#!/usr/bin/env python3
"""ObsidianAI MCP Server — expõe o vault Obsidian como tools para Claude Desktop e outros MCP clients."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Garante imports do projeto
sys.path.insert(0, str(Path(__file__).resolve().parent))
load_dotenv()

from vault.reader import VaultReader
from vault.writer import VaultWriter

# ------------------------------------------------------------------ #
#  Inicialização                                                       #
# ------------------------------------------------------------------ #

VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", ""))
EXCLUDED = os.getenv("EXCLUDED_FOLDERS", ".obsidian,.trash,.git,_templates").split(",")

mcp = FastMCP(
    "obsidian-ai",
    instructions=(
        "Servidor MCP para gestão de conhecimento Zettelkasten no Obsidian. "
        "O vault segue o método Zettelkasten com pastas: inbox/ (fleeting notes), "
        "zettel/ (permanent notes atômicas), references/ (literature notes), "
        "structure/ (MOCs/índices), projects/ (ações ativas), archive/ (concluídos). "
        "Permite ler, buscar, analisar, criar e modificar notas. "
        "Sempre responda em português brasileiro."
    ),
)

_reader: Optional[VaultReader] = None
_writer: Optional[VaultWriter] = None


def _get_reader() -> VaultReader:
    global _reader
    if _reader is None:
        if not VAULT_PATH.exists():
            raise RuntimeError(
                f"Vault não encontrado: {VAULT_PATH}. "
                "Configure OBSIDIAN_VAULT_PATH no .env ou como variável de ambiente."
            )
        _reader = VaultReader(VAULT_PATH, excluded_folders=EXCLUDED)
        _reader.load()
    return _reader


def _get_writer() -> VaultWriter:
    global _writer
    if _writer is None:
        if not VAULT_PATH.exists():
            raise RuntimeError(f"Vault não encontrado: {VAULT_PATH}")
        _writer = VaultWriter(VAULT_PATH)
    return _writer


def _note_summary(note) -> dict:
    return {
        "path": note.meta.path,
        "title": note.meta.title,
        "tags": note.meta.tags,
        "type": note.meta.frontmatter.get("type", ""),
        "word_count": note.word_count,
        "links_out": len(note.outgoing_links),
        "links_in": len(note.backlinks),
    }


# ------------------------------------------------------------------ #
#  Tools de leitura                                                    #
# ------------------------------------------------------------------ #


@mcp.tool()
def vault_stats() -> str:
    """Retorna estatísticas gerais do vault: total de notas, tags, links, notas órfãs, vazias, tags mais usadas e notas mais linkadas."""
    reader = _get_reader()
    stats = reader.get_stats()
    data = stats.model_dump()
    data["top_tags"] = [{"tag": t, "count": c} for t, c in stats.top_tags]
    data["most_linked"] = [{"title": t, "backlinks": c} for t, c in stats.most_linked]
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def search_notes(query: str) -> str:
    """Busca notas pelo conteúdo ou título. Retorna lista resumida das notas encontradas."""
    reader = _get_reader()
    results = reader.search(query)
    if not results:
        return json.dumps({"results": [], "message": f"Nenhuma nota encontrada para '{query}'"})
    return json.dumps(
        {"results": [_note_summary(n) for n in results]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def read_note(path: str) -> str:
    """Retorna o conteúdo completo de uma nota dado seu caminho relativo (ex: pasta/nota.md) ou título."""
    reader = _get_reader()
    note = reader.get_note(path)
    if not note:
        note = reader.get_note_by_title(path)
    if not note:
        return json.dumps({"error": f"Nota não encontrada: {path}"})
    return json.dumps(
        {
            "path": note.meta.path,
            "title": note.meta.title,
            "tags": note.meta.tags,
            "aliases": note.meta.aliases,
            "frontmatter": note.meta.frontmatter,
            "outgoing_links": note.outgoing_links,
            "backlinks": note.backlinks,
            "headings": note.headings,
            "word_count": note.word_count,
            "content": note.content,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def list_notes() -> str:
    """Lista todas as notas do vault com título, tags, contagem de palavras e links."""
    reader = _get_reader()
    notes = sorted(reader.notes.values(), key=lambda n: n.meta.path)
    return json.dumps(
        {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_orphan_notes() -> str:
    """Retorna notas órfãs — sem nenhum link de entrada nem de saída."""
    reader = _get_reader()
    orphans = reader.get_orphans()
    return json.dumps(
        {"total": len(orphans), "notes": [_note_summary(n) for n in orphans]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_notes_without_tags() -> str:
    """Retorna notas que não possuem nenhuma tag."""
    reader = _get_reader()
    notes = reader.get_notes_without_tags()
    return json.dumps(
        {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def list_all_tags() -> str:
    """Retorna todas as tags do vault com contagem de uso, ordenadas por frequência."""
    reader = _get_reader()
    tags = reader.get_all_tags()
    return json.dumps(
        {"total_unique": len(tags), "tags": [{"tag": t, "count": c} for t, c in tags.items()]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_notes_by_tag(tag: str) -> str:
    """Retorna todas as notas que possuem uma tag específica (sem o #)."""
    reader = _get_reader()
    notes = reader.get_notes_by_tag(tag)
    return json.dumps(
        {"tag": tag, "total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_empty_notes() -> str:
    """Retorna notas vazias ou quase vazias (menos de 3 palavras)."""
    reader = _get_reader()
    notes = reader.get_empty_notes()
    return json.dumps(
        {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_short_notes() -> str:
    """Retorna notas curtas (menos de 30 palavras) que podem precisar ser expandidas."""
    reader = _get_reader()
    notes = reader.get_short_notes()
    return json.dumps(
        {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def folder_structure() -> str:
    """Retorna a estrutura de pastas do vault com contagem de notas por pasta."""
    reader = _get_reader()
    folders = reader.get_folders()
    return json.dumps(
        {"total_folders": len(folders), "folders": folders},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def note_links(path: str) -> str:
    """Retorna os links de saída e backlinks de uma nota específica."""
    reader = _get_reader()
    note = reader.get_note(path) or reader.get_note_by_title(path)
    if not note:
        return json.dumps({"error": f"Nota não encontrada: {path}"})
    return json.dumps(
        {
            "path": note.meta.path,
            "title": note.meta.title,
            "outgoing_links": note.outgoing_links,
            "backlinks": note.backlinks,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_similar_titles() -> str:
    """Encontra notas com títulos similares que podem ser duplicatas."""
    reader = _get_reader()
    similar = reader.find_similar_titles()
    return json.dumps(
        {"total_pairs": len(similar), "pairs": [{"a": a, "b": b} for a, b in similar]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def most_linked_notes() -> str:
    """Retorna as notas mais referenciadas (com mais backlinks) — os hubs de conhecimento."""
    reader = _get_reader()
    most = reader.get_most_linked(15)
    return json.dumps(
        {"notes": [{"title": t, "backlinks": c} for t, c in most]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def reload_vault() -> str:
    """Recarrega o vault do disco. Use após fazer alterações externas no Obsidian."""
    global _reader
    _reader = None
    reader = _get_reader()
    stats = reader.get_stats()
    return json.dumps(
        {"status": "ok", "message": f"Vault recarregado: {stats.total_notes} notas"},
        ensure_ascii=False,
    )


# ------------------------------------------------------------------ #
#  Tools Zettelkasten                                                  #
# ------------------------------------------------------------------ #


@mcp.tool()
def inbox_notes() -> str:
    """Retorna fleeting notes na pasta inbox/ que precisam ser processadas."""
    reader = _get_reader()
    notes = [
        n for n in reader.notes.values()
        if n.meta.path.startswith("inbox/") or n.meta.path.startswith("inbox\\")
    ]
    notes.sort(key=lambda n: n.meta.modified or n.meta.created, reverse=True)
    return json.dumps(
        {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def notes_by_type(note_type: str) -> str:
    """Retorna notas filtradas por tipo Zettelkasten.

    Args:
        note_type: Um de: fleeting, zettel, literature, structure, project
    """
    reader = _get_reader()
    notes = [
        n for n in reader.notes.values()
        if n.meta.frontmatter.get("type", "").lower() == note_type.lower()
    ]
    return json.dumps(
        {"type": note_type, "total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def notes_by_folder(folder: str) -> str:
    """Retorna notas de uma pasta específica (ex: zettel, references, projects).

    Args:
        folder: Nome da pasta.
    """
    reader = _get_reader()
    folder_clean = folder.strip("/")
    notes = [
        n for n in reader.notes.values()
        if n.meta.path.startswith(folder_clean + "/")
    ]
    notes.sort(key=lambda n: n.meta.path)
    return json.dumps(
        {"folder": folder, "total": len(notes), "notes": [_note_summary(n) for n in notes]},
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def find_non_atomic_notes() -> str:
    """Encontra permanent notes longas (>500 palavras) que podem violar o princípio de atomicidade Zettelkasten."""
    reader = _get_reader()
    notes = [
        n for n in reader.notes.values()
        if n.word_count > 500
        and (n.meta.path.startswith("zettel/") or n.meta.frontmatter.get("type") == "zettel")
    ]
    notes.sort(key=lambda n: n.word_count, reverse=True)
    items = [{**_note_summary(n), "headings_count": len(n.headings)} for n in notes]
    return json.dumps({"total": len(items), "notes": items}, ensure_ascii=False, indent=2)


@mcp.tool()
def setup_zettelkasten() -> str:
    """Cria a estrutura de pastas Zettelkasten no vault (inbox, zettel, references, structure, projects, archive, templates)."""
    writer = _get_writer()
    created = writer.ensure_zettel_folders()
    if created:
        return json.dumps(
            {"status": "ok", "created_folders": created, "message": f"Pastas criadas: {', '.join(created)}"},
            ensure_ascii=False,
        )
    return json.dumps({"status": "ok", "message": "Estrutura Zettelkasten já existe"})


@mcp.tool()
def move_note(path: str, new_path: str) -> str:
    """Move uma nota para outro caminho/pasta no vault.

    Args:
        path: Caminho atual da nota.
        new_path: Novo caminho (ex: zettel/minha-ideia.md).
    """
    writer = _get_writer()
    try:
        result = writer.move_note(path, new_path)
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "old_path": path, "new_path": result, "message": f"Nota movida para {result}"},
            ensure_ascii=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})
    except FileExistsError:
        return json.dumps({"error": f"Destino já existe: {new_path}"})


# ------------------------------------------------------------------ #
#  Tools de escrita                                                    #
# ------------------------------------------------------------------ #


@mcp.tool()
def create_note(
    path: str,
    content: str,
    title: str = "",
    tags: str = "",
) -> str:
    """Cria uma nova nota no vault.

    Args:
        path: Caminho relativo (ex: projetos/meu-projeto.md). Cria pastas se necessário.
        content: Conteúdo markdown da nota.
        title: Título (opcional, usa nome do arquivo se vazio).
        tags: Tags separadas por vírgula (ex: "projeto,python,ia").
    """
    writer = _get_writer()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    try:
        created_path = writer.create_note(
            path=path,
            content=content,
            title=title or None,
            tags=tag_list,
        )
        # Recarrega vault para refletir a nova nota
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "path": created_path, "message": f"Nota criada: {created_path}"},
            ensure_ascii=False,
        )
    except FileExistsError:
        return json.dumps({"error": f"Nota já existe: {path}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def append_to_note(path: str, content: str) -> str:
    """Adiciona conteúdo ao final de uma nota existente.

    Args:
        path: Caminho relativo da nota.
        content: Conteúdo markdown a adicionar.
    """
    writer = _get_writer()
    try:
        updated = writer.append_to_note(path, content)
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "path": updated, "message": "Conteúdo adicionado ao final da nota"},
            ensure_ascii=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})


@mcp.tool()
def add_tags_to_note(path: str, tags: str) -> str:
    """Adiciona tags ao frontmatter de uma nota existente.

    Args:
        path: Caminho relativo da nota.
        tags: Tags separadas por vírgula (ex: "python,backend,api").
    """
    writer = _get_writer()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    try:
        all_tags = writer.add_tags(path, tag_list)
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "path": path, "all_tags": all_tags},
            ensure_ascii=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})


@mcp.tool()
def remove_tags_from_note(path: str, tags: str) -> str:
    """Remove tags do frontmatter de uma nota.

    Args:
        path: Caminho relativo da nota.
        tags: Tags a remover separadas por vírgula.
    """
    writer = _get_writer()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    try:
        remaining = writer.remove_tags(path, tag_list)
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "path": path, "remaining_tags": remaining},
            ensure_ascii=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})


@mcp.tool()
def insert_link_in_note(path: str, target: str, heading: str = "") -> str:
    """Insere um [[wiki-link]] em uma nota.

    Args:
        path: Caminho da nota onde inserir o link.
        target: Nome da nota alvo (será inserido como [[target]]).
        heading: Se fornecido, insere o link após esse heading. Senão, cria/usa seção "Relacionados".
    """
    writer = _get_writer()
    try:
        result = writer.insert_link(path, target, context_heading=heading or None)
        global _reader
        _reader = None
        return json.dumps({"status": "ok", "message": result}, ensure_ascii=False)
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})


@mcp.tool()
def update_note_content(path: str, content: str) -> str:
    """Substitui o conteúdo inteiro de uma nota (mantém frontmatter).

    Args:
        path: Caminho relativo da nota.
        content: Novo conteúdo markdown completo.
    """
    writer = _get_writer()
    try:
        updated = writer.replace_content(path, content)
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "path": updated, "message": "Conteúdo atualizado"},
            ensure_ascii=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})


@mcp.tool()
def update_frontmatter(path: str, fields_json: str) -> str:
    """Atualiza campos do frontmatter de uma nota.

    Args:
        path: Caminho relativo da nota.
        fields_json: JSON com os campos a atualizar (ex: '{"status": "concluido", "priority": 1}').
    """
    writer = _get_writer()
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"JSON inválido: {e}"})
    try:
        updated = writer.update_frontmatter(path, fields)
        global _reader
        _reader = None
        return json.dumps(
            {"status": "ok", "path": path, "frontmatter": updated},
            ensure_ascii=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": f"Nota não encontrada: {path}"})


# ------------------------------------------------------------------ #
#  Resources                                                           #
# ------------------------------------------------------------------ #


@mcp.resource("obsidian://vault/stats")
def resource_vault_stats() -> str:
    """Estatísticas atuais do vault."""
    return vault_stats()


@mcp.resource("obsidian://vault/tags")
def resource_all_tags() -> str:
    """Todas as tags do vault."""
    return list_all_tags()


@mcp.resource("obsidian://vault/structure")
def resource_structure() -> str:
    """Estrutura de pastas do vault."""
    return folder_structure()


# ------------------------------------------------------------------ #
#  Prompts pré-definidos                                               #
# ------------------------------------------------------------------ #


@mcp.prompt()
def review_vault() -> str:
    """Auditoria Zettelkasten completa do vault."""
    return (
        "Faça uma auditoria Zettelkasten completa do meu vault. Analise: "
        "1) Fluxo de processamento: quantas fleeting notes na inbox? Estão acumulando? "
        "2) Atomicidade: há permanent notes longas demais ou com múltiplos assuntos? "
        "3) Conectividade: quantas notas estão órfãs? Média de links por nota? "
        "4) Estrutura: os temas principais têm structure notes? "
        "5) Tags: o sistema de tags está consistente? "
        "Dê uma pontuação de 0 a 100 com breakdown por critério e um plano de ação. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def process_inbox() -> str:
    """Processa fleeting notes da inbox seguindo o método Zettelkasten."""
    return (
        "Processe minha inbox Zettelkasten. Para cada fleeting note em inbox/: "
        "1) Leia o conteúdo "
        "2) Classifique: é uma IDEIA (→ permanent note), FONTE (→ literature note), "
        "AÇÃO (→ project note), ou LIXO (→ deletar)? "
        "3) Para cada transformação, gere a nota completa com frontmatter, "
        "tags, e links para notas existentes relacionadas "
        "4) Sugira o caminho de destino e nome do arquivo "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def suggest_links() -> str:
    """Tece conexões faltantes entre notas do Zettelkasten."""
    return (
        "Analise meu Zettelkasten e encontre conexões intelectuais faltantes. "
        "Foque em: permanent notes (zettel/) com menos de 2 links, notas órfãs, "
        "e literature notes que deveriam linkar para permanent notes. "
        "Para cada sugestão, explique a RELAÇÃO intelectual entre as notas. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def organize_tags() -> str:
    """Analisa e normaliza o sistema de tags Zettelkasten."""
    return (
        "Analise o sistema de tags do meu Zettelkasten. Verifique: "
        "1) Toda permanent note tem ao menos 1 tag de tema? "
        "2) Há tags duplicadas ou inconsistentes? "
        "3) As tags seguem o padrão: tema, tema/subtema, status/X, fonte/X? "
        "4) Há notas com tags demais (>6, possível violação de atomicidade)? "
        "Proponha uma taxonomia consolidada. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def create_structure_note(topic: str) -> str:
    """Cria uma Structure Note (MOC) Zettelkasten sobre um tema."""
    return (
        f"Crie uma Structure Note sobre '{topic}' para meu Zettelkasten. "
        "Busque todas as permanent notes e literature notes relevantes. "
        "Organize em subtemas com breves descrições ao lado de cada [[link]]. "
        "Inclua frontmatter com type: structure. "
        "Identifique lacunas (temas que deveriam ter notas mas não têm). "
        "Gere a nota completa pronta para salvar em structure/. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def daily_review() -> str:
    """Revisão diária do Zettelkasten com foco em processamento e manutenção."""
    return (
        "Revisão diária do meu Zettelkasten. Verifique: "
        "1) Inbox: quantas fleeting notes para processar? "
        "2) Notas recentes: o que foi adicionado/modificado? "
        "3) Saúde rápida: notas sem tags, sem links, vazias? "
        "4) Sugira 3-5 ações concretas para hoje, priorizando processar inbox. "
        "Seja breve e prático. Responda em português brasileiro."
    )


@mcp.prompt()
def capture_thought(thought: str) -> str:
    """Captura rápida de um pensamento como fleeting note."""
    return (
        f"Capture este pensamento no meu Zettelkasten: \"{thought}\". "
        "Crie uma fleeting note em inbox/ com: "
        "1) Frontmatter apropriado (title, type: fleeting, tags inferidos) "
        "2) Conteúdo limpo e organizado "
        "3) Sugestão de notas existentes que podem se relacionar "
        "Use a tool create_note para salvar. "
        "Responda em português brasileiro."
    )


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    mcp.run()
