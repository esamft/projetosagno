"""Bot Telegram para o ObsidianAI — interface conversacional com o Zettelkasten."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Optional

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config.settings import settings
from vault.reader import VaultReader
from vault.writer import VaultWriter
from tools.toolkit import VaultToolkit

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Constantes                                                          #
# ------------------------------------------------------------------ #

MAX_MSG_LEN = 4096  # limite Telegram
EXECUTOR = ThreadPoolExecutor(max_workers=4)

AGENT_DESCRIPTIONS = {
    "retriever": "Busca e responde perguntas",
    "zettel": "Processa inbox e mantém o Zettelkasten",
    "capture": "Captura rápida de pensamentos",
    "ingest": "Ingere dados brutos em notas",
    "scout": "Busca novidades na web",
    "organizer": "Sugere melhorias na organização",
    "linker": "Descobre conexões faltantes",
    "tagger": "Normaliza tags",
    "summarizer": "Cria Structure Notes / MOCs",
    "reviewer": "Auditoria de saúde do vault",
}


# ------------------------------------------------------------------ #
#  Estado por usuário                                                  #
# ------------------------------------------------------------------ #

class UserSession:
    """Estado de conversa de um usuário."""

    def __init__(self):
        self.agent_name: str = "retriever"
        self.agent_instance = None
        self.pending_agent = None  # agente com proposta pendente de aprovação

    def reset_agent(self):
        self.agent_instance = None
        self.pending_agent = None


_sessions: dict[int, UserSession] = {}


def _get_session(user_id: int) -> UserSession:
    if user_id not in _sessions:
        _sessions[user_id] = UserSession()
    return _sessions[user_id]


# ------------------------------------------------------------------ #
#  Vault e toolkit                                                     #
# ------------------------------------------------------------------ #

_reader: Optional[VaultReader] = None
_writer: Optional[VaultWriter] = None
_toolkit: Optional[VaultToolkit] = None


def _init_vault():
    global _reader, _writer, _toolkit
    vault_path = settings.VAULT_PATH
    if not vault_path or not vault_path.exists():
        raise RuntimeError(f"Vault não encontrado: {vault_path}")

    _reader = VaultReader(vault_path, excluded_folders=settings.EXCLUDED_FOLDERS)
    _reader.load()
    _writer = VaultWriter(vault_path)
    _toolkit = VaultToolkit(_reader, writer=_writer)


def _reload_vault():
    global _reader, _writer, _toolkit
    _reader = None
    _writer = None
    _toolkit = None
    _init_vault()
    # Resetar agentes de todas as sessões
    for session in _sessions.values():
        session.reset_agent()


def _get_toolkit() -> VaultToolkit:
    if _toolkit is None:
        _init_vault()
    return _toolkit


# ------------------------------------------------------------------ #
#  Criação de agentes                                                  #
# ------------------------------------------------------------------ #

def _create_agent(name: str):
    """Cria instância de agente pelo nome."""
    toolkit = _get_toolkit()

    from agents.retriever import RetrieverAgent
    from agents.organizer import OrganizerAgent
    from agents.linker import LinkerAgent
    from agents.tagger import TaggerAgent
    from agents.summarizer import SummarizerAgent
    from agents.reviewer import ReviewerAgent
    from agents.zettel import ZettelAgent
    from agents.capture import CaptureAgent
    from agents.ingest import IngestAgent
    from agents.scout import ScoutAgent

    agent_classes = {
        "retriever": RetrieverAgent,
        "zettel": ZettelAgent,
        "capture": CaptureAgent,
        "ingest": IngestAgent,
        "scout": ScoutAgent,
        "organizer": OrganizerAgent,
        "linker": LinkerAgent,
        "tagger": TaggerAgent,
        "summarizer": SummarizerAgent,
        "reviewer": ReviewerAgent,
    }

    cls = agent_classes.get(name)
    if cls is None:
        raise ValueError(f"Agente desconhecido: {name}")
    return cls(toolkit)


# ------------------------------------------------------------------ #
#  Autorização                                                         #
# ------------------------------------------------------------------ #

def _is_authorized(user_id: int) -> bool:
    """Verifica se o usuário está na lista de autorizados."""
    allowed = settings.TELEGRAM_ALLOWED_USERS
    if not allowed:
        return True  # sem restrição configurada
    allowed_ids = {int(uid.strip()) for uid in allowed.split(",") if uid.strip()}
    return user_id in allowed_ids


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

async def _send_long(update: Update, text: str, **kwargs):
    """Envia mensagem longa, dividindo se necessário."""
    if not text.strip():
        text = "(sem resposta)"

    chunks = _split_message(text)
    for chunk in chunks:
        try:
            await update.effective_message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN, **kwargs)
        except Exception:
            # Fallback sem markdown se der erro de parse
            await update.effective_message.reply_text(chunk, **kwargs)


def _split_message(text: str) -> list[str]:
    """Divide mensagem respeitando o limite do Telegram."""
    if len(text) <= MAX_MSG_LEN:
        return [text]

    chunks = []
    while text:
        if len(text) <= MAX_MSG_LEN:
            chunks.append(text)
            break

        # Tentar quebrar em parágrafo
        cut = text.rfind("\n\n", 0, MAX_MSG_LEN)
        if cut == -1:
            cut = text.rfind("\n", 0, MAX_MSG_LEN)
        if cut == -1:
            cut = MAX_MSG_LEN

        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")

    return chunks


def _run_agent_sync(agent, prompt: str) -> str:
    """Executa agente de forma síncrona (para rodar no executor)."""
    return agent.run(prompt)


def _continue_agent_sync(agent, prompt: str) -> str:
    """Continua agente preservando contexto."""
    return agent.continue_run(prompt)


# ------------------------------------------------------------------ #
#  Handlers de comando                                                 #
# ------------------------------------------------------------------ #

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /start."""
    if not _is_authorized(update.effective_user.id):
        await update.message.reply_text("Acesso não autorizado.")
        return

    await update.message.reply_text(
        "*ObsidianAI — Zettelkasten Inteligente*\n\n"
        "Seu assistente de gestão de conhecimento no Telegram.\n\n"
        "*Comandos:*\n"
        "/ask `pergunta` — perguntar sobre suas notas\n"
        "/scout `tema` — buscar novidades na web\n"
        "/capture `texto` — captura rápida\n"
        "/ingest — envie um arquivo para ingerir\n"
        "/inbox — processar fleeting notes\n"
        "/review — auditoria do vault\n"
        "/stats — estatísticas (sem IA)\n"
        "/agente `nome` — trocar agente ativo\n"
        "/agentes — listar agentes\n"
        "/reload — recarregar vault\n"
        "/ajuda — esta mensagem\n\n"
        "Ou simplesmente _envie uma mensagem_ e o agente ativo responde.\n"
        "_Envie um PDF ou foto_ para ingerir automaticamente.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /ajuda."""
    await cmd_start(update, context)


async def cmd_agentes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /agentes — lista agentes disponíveis."""
    if not _is_authorized(update.effective_user.id):
        return

    session = _get_session(update.effective_user.id)
    lines = []
    for name, desc in AGENT_DESCRIPTIONS.items():
        marker = " ← ativo" if name == session.agent_name else ""
        lines.append(f"• *{name}* — {desc}{marker}")

    await update.message.reply_text(
        "*Agentes disponíveis:*\n\n" + "\n".join(lines) + "\n\nUse /agente `nome` para trocar.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_agente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /agente <nome> — troca agente ativo."""
    if not _is_authorized(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Use: /agente `nome`\nEx: /agente scout")
        return

    name = context.args[0].lower()
    if name not in AGENT_DESCRIPTIONS:
        await update.message.reply_text(
            f"Agente '{name}' não existe.\nDisponíveis: {', '.join(AGENT_DESCRIPTIONS.keys())}"
        )
        return

    session = _get_session(update.effective_user.id)
    session.agent_name = name
    session.reset_agent()
    await update.message.reply_text(f"Agente trocado para *{name}* — {AGENT_DESCRIPTIONS[name]}", parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /stats — estatísticas sem IA."""
    if not _is_authorized(update.effective_user.id):
        return

    try:
        _init_vault() if _reader is None else None
        s = _reader.get_stats()
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
        return

    text = (
        f"*Estatísticas do Vault*\n\n"
        f"📝 Notas: {s.total_notes}\n"
        f"📁 Pastas: {s.folders}\n"
        f"🏷 Tags únicas: {s.unique_tags}\n"
        f"🔗 Links: {s.total_links}\n"
        f"🔴 Órfãs: {s.orphan_notes}\n"
        f"⚪ Sem tags: {s.notes_without_tags}\n"
        f"📭 Vazias: {s.empty_notes}\n"
        f"📏 Curtas (<30 palavras): {s.short_notes}\n"
        f"📊 Média palavras/nota: {s.avg_note_length}\n"
    )

    if s.top_tags:
        text += "\n*Top Tags:*\n"
        for tag, count in s.top_tags[:8]:
            text += f"  #{tag} ({count})\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /reload — recarrega vault."""
    if not _is_authorized(update.effective_user.id):
        return

    try:
        _reload_vault()
        await update.message.reply_text(f"Vault recarregado: {len(_reader.notes)} notas")
    except Exception as e:
        await update.message.reply_text(f"Erro ao recarregar: {e}")


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /ask — pergunta sobre notas."""
    if not _is_authorized(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Use: /ask `sua pergunta aqui`")
        return

    question = " ".join(context.args)
    await _run_agent_command(update, "retriever", question)


async def cmd_scout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /scout — busca novidades na web."""
    if not _is_authorized(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Use: /scout `tema`\nEx: /scout inteligência artificial")
        return

    topic = " ".join(context.args)
    prompt = (
        f"Busque novidades e conteúdo relevante sobre '{topic}'. "
        "Verifique o que já tenho no vault, busque na web, extraia os melhores artigos, "
        "e proponha notas Zettelkasten para minha aprovação."
    )
    await _run_agent_command(update, "scout", prompt, with_approval=True)


async def cmd_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /capture — captura rápida."""
    if not _is_authorized(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Use: /capture `seu pensamento aqui`")
        return

    thought = " ".join(context.args)
    prompt = (
        f"Capture isso no meu Zettelkasten como fleeting note: \"{thought}\". "
        "Gere a nota completa com frontmatter, tags, e links. "
        "Use create_note para salvar diretamente em inbox/."
    )
    await _run_agent_command(update, "capture", prompt)


async def cmd_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /inbox — processa fleeting notes."""
    if not _is_authorized(update.effective_user.id):
        return

    prompt = (
        "Processe minha inbox Zettelkasten. Liste as fleeting notes em inbox/, "
        "leia cada uma, classifique e proponha transformações. "
        "Apresente o plano para minha aprovação."
    )
    await _run_agent_command(update, "zettel", prompt, with_approval=True)


async def cmd_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /review — auditoria."""
    if not _is_authorized(update.effective_user.id):
        return

    prompt = (
        "Faça uma auditoria Zettelkasten completa do meu vault. "
        "Analise fluxo, atomicidade, conectividade e cobertura. "
        "Dê pontuação e plano de ação."
    )
    await _run_agent_command(update, "reviewer", prompt)


# ------------------------------------------------------------------ #
#  Handler de mensagens de texto livre                                 #
# ------------------------------------------------------------------ #

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensagem de texto livre → agente ativo."""
    if not _is_authorized(update.effective_user.id):
        return

    text = update.message.text.strip()
    if not text:
        return

    session = _get_session(update.effective_user.id)
    await _run_agent_command(update, session.agent_name, text)


# ------------------------------------------------------------------ #
#  Handler de arquivos (PDF, imagens, documentos)                      #
# ------------------------------------------------------------------ #

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Documento enviado → IngestAgent."""
    if not _is_authorized(update.effective_user.id):
        return

    doc = update.message.document
    if not doc:
        return

    await update.message.reply_text(f"Recebendo arquivo: {doc.file_name}...")
    await update.effective_chat.send_action(ChatAction.TYPING)

    # Baixar arquivo para temp
    try:
        tg_file = await doc.get_file()
        suffix = Path(doc.file_name).suffix if doc.file_name else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            await tg_file.download_to_drive(tmp.name)
            tmp_path = tmp.name
    except Exception as e:
        await update.message.reply_text(f"Erro ao baixar arquivo: {e}")
        return

    # Extrair conteúdo
    try:
        from vault.ingest import extract_from_file
        extracted = extract_from_file(tmp_path)
    except Exception as e:
        await update.message.reply_text(f"Erro ao processar arquivo: {e}")
        return
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    content = extracted.get("content", "")
    content_type = extracted.get("type", "unknown")
    metadata = extracted.get("metadata", {})

    if content_type == "image":
        prompt = (
            f"Recebi uma imagem ({doc.file_name}). "
            "O usuário enviou pelo Telegram. "
            "Descreva que tipo de notas podem ser criadas e pergunte detalhes."
        )
    elif not content.strip():
        await update.message.reply_text(
            "Não consegui extrair conteúdo textual deste arquivo. "
            "Se é um PDF escaneado, considere usar OCR antes."
        )
        return
    else:
        display = content[:5000] + "\n\n[... truncado ...]" if len(content) > 5000 else content
        prompt = (
            f"Recebi o seguinte conteúdo para ingestão no meu Zettelkasten.\n\n"
            f"**Fonte:** {doc.file_name}\n"
            f"**Tipo:** {content_type}\n\n"
            f"**Conteúdo:**\n\n{display}\n\n"
            "Analise e proponha um plano de ingestão em notas atômicas. "
            "Busque conexões com o vault existente."
        )

    await _run_agent_command(update, "ingest", prompt, with_approval=True)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foto enviada → IngestAgent."""
    if not _is_authorized(update.effective_user.id):
        return

    photo = update.message.photo[-1]  # maior resolução
    caption = update.message.caption or ""

    await update.message.reply_text("Recebendo imagem...")
    await update.effective_chat.send_action(ChatAction.TYPING)

    prompt = (
        f"O usuário enviou uma foto pelo Telegram."
    )
    if caption:
        prompt += f"\nDescrição do usuário: \"{caption}\""
    prompt += (
        "\n\nComo não consigo ver imagens diretamente, preciso que o usuário descreva o conteúdo. "
        "Pergunte o que a imagem contém para que eu possa criar notas."
    )

    await _run_agent_command(update, "ingest", prompt)


# ------------------------------------------------------------------ #
#  Handler de callbacks (botões inline)                                #
# ------------------------------------------------------------------ #

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa cliques em botões inline (aprovar/rejeitar)."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    session = _get_session(user_id)

    if query.data == "approve":
        if session.pending_agent is None:
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("Nenhuma proposta pendente.")
            return

        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Aprovado! Criando as notas...")
        await update.effective_chat.send_action(ChatAction.TYPING)

        agent = session.pending_agent
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                EXECUTOR,
                partial(
                    _continue_agent_sync,
                    agent,
                    "APROVADO. Crie todas as notas do plano proposto usando a tool create_note. "
                    "Para cada nota, use os caminhos, títulos, tags e conteúdos exatamente como propostos. "
                    "Após criar, insira os links entre elas com insert_link_in_note.",
                ),
            )
            await _send_long(update, response)
            # Recarregar vault para refletir notas criadas
            _reload_vault()
        except Exception as e:
            await query.message.reply_text(f"Erro ao criar notas: {e}")
        finally:
            session.pending_agent = None

    elif query.data == "reject":
        session.pending_agent = None
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Proposta rejeitada.")

    elif query.data == "modify":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "Diga o que deseja alterar no plano. "
            "Vou ajustar e reapresentar para sua aprovação."
        )
        # Manter o pending_agent para continuar a conversa


# ------------------------------------------------------------------ #
#  Motor principal de execução de agentes                              #
# ------------------------------------------------------------------ #

async def _run_agent_command(
    update: Update,
    agent_name: str,
    prompt: str,
    with_approval: bool = False,
):
    """Executa um agente e envia o resultado."""
    await update.effective_chat.send_action(ChatAction.TYPING)

    session = _get_session(update.effective_user.id)

    # Se há um agente pendente e o usuário responde (sem callback), tratar como modificação
    if session.pending_agent and agent_name == session.agent_name:
        agent = session.pending_agent
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                EXECUTOR,
                partial(_continue_agent_sync, agent, prompt),
            )
        except Exception as e:
            await update.message.reply_text(f"Erro: {e}")
            session.pending_agent = None
            return

        await _send_long(update, response)
        # Re-mostrar botões de aprovação
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Aprovar", callback_data="approve"),
                InlineKeyboardButton("Alterar", callback_data="modify"),
                InlineKeyboardButton("Rejeitar", callback_data="reject"),
            ]
        ])
        await update.message.reply_text("O que deseja fazer com o plano atualizado?", reply_markup=keyboard)
        return

    # Criar novo agente
    try:
        agent = _create_agent(agent_name)
    except Exception as e:
        await update.message.reply_text(f"Erro ao criar agente {agent_name}: {e}")
        return

    # Rodar em thread separada (agente é síncrono)
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            EXECUTOR, partial(_run_agent_sync, agent, prompt)
        )
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
        return

    # Enviar resposta
    await _send_long(update, response)

    # Se requer aprovação, mostrar botões e guardar agente
    if with_approval:
        session.pending_agent = agent
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Aprovar", callback_data="approve"),
                InlineKeyboardButton("Alterar", callback_data="modify"),
                InlineKeyboardButton("Rejeitar", callback_data="reject"),
            ]
        ])
        await update.effective_message.reply_text(
            "O que deseja fazer com este plano?",
            reply_markup=keyboard,
        )


# ------------------------------------------------------------------ #
#  Inicialização do bot                                                #
# ------------------------------------------------------------------ #

def run_bot(token: str | None = None):
    """Inicia o bot Telegram."""
    token = token or settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN não configurado. "
            "Adicione ao .env ou passe como argumento."
        )

    # Inicializar vault
    _init_vault()
    logger.info("Vault carregado: %d notas", len(_reader.notes))

    # Criar aplicação
    app = Application.builder().token(token).build()

    # Registrar handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ajuda", cmd_ajuda))
    app.add_handler(CommandHandler("help", cmd_ajuda))
    app.add_handler(CommandHandler("agentes", cmd_agentes))
    app.add_handler(CommandHandler("agente", cmd_agente))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reload", cmd_reload))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(CommandHandler("scout", cmd_scout))
    app.add_handler(CommandHandler("capture", cmd_capture))
    app.add_handler(CommandHandler("inbox", cmd_inbox))
    app.add_handler(CommandHandler("review", cmd_review))

    # Callbacks (botões inline)
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Documentos e fotos
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Texto livre (deve ser o último)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot Telegram iniciado. Aguardando mensagens...")
    print("Bot Telegram ObsidianAI iniciado. Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
