#!/usr/bin/env python3
"""ObsidianAI — Agentes inteligentes para gestão de conhecimento no Obsidian."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config.settings import settings
from vault.reader import VaultReader
from tools.toolkit import VaultToolkit

app = typer.Typer(
    name="obsidian-ai",
    help="Agentes inteligentes para gestão de conhecimento no Obsidian",
    add_completion=False,
)
console = Console()


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #


def _get_vault(vault_path: Optional[str] = None) -> VaultReader:
    path = Path(vault_path) if vault_path else settings.VAULT_PATH
    if not path or not path.exists():
        console.print(
            Panel(
                "[bold red]Vault não encontrado![/]\n\n"
                "Configure OBSIDIAN_VAULT_PATH no arquivo .env\n"
                "ou passe --vault /caminho/do/vault",
                title="Erro",
            )
        )
        raise typer.Exit(1)

    console.print(f"[dim]Carregando vault: {path}[/]")
    reader = VaultReader(path, excluded_folders=settings.EXCLUDED_FOLDERS)
    reader.load()
    console.print(f"[dim]{len(reader.notes)} notas carregadas[/]\n")
    return reader


def _get_toolkit(vault: VaultReader) -> VaultToolkit:
    return VaultToolkit(vault)


def _validate_api_key() -> None:
    errors = settings.validate()
    if errors:
        for err in errors:
            console.print(f"[bold red]Erro:[/] {err}")
        raise typer.Exit(1)


def _run_agent(agent, prompt: str) -> None:
    """Executa um agente e exibe resultado com rich."""
    console.print(
        Panel(
            f"[bold]{agent.description}[/]",
            title=f"Agente: {agent.name}",
            border_style="cyan",
        )
    )

    tool_count = 0

    def on_tool(name: str, inputs: dict, result: str) -> None:
        nonlocal tool_count
        tool_count += 1
        args = ", ".join(f"{k}={v!r}" for k, v in inputs.items()) if inputs else ""
        console.print(f"  [dim]tool [{tool_count}]: {name}({args})[/]")

    console.print(f"[dim]Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}[/]\n")
    console.print("[yellow]Processando...[/]\n")

    try:
        response = agent.run(prompt, on_tool_call=on_tool)
    except Exception as e:
        console.print(f"\n[bold red]Erro ao executar agente:[/] {e}")
        raise typer.Exit(1)

    console.print()
    console.print(Panel(Markdown(response), title="Resultado", border_style="green"))
    console.print(f"\n[dim]Tools chamadas: {tool_count}[/]")


# ------------------------------------------------------------------ #
#  Comandos                                                           #
# ------------------------------------------------------------------ #


@app.command()
def stats(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
):
    """Mostra estatísticas do vault (sem usar LLM)."""
    reader = _get_vault(vault)
    s = reader.get_stats()

    table = Table(title="Estatísticas do Vault", border_style="cyan")
    table.add_column("Métrica", style="bold")
    table.add_column("Valor", justify="right")
    table.add_row("Total de notas", str(s.total_notes))
    table.add_row("Pastas", str(s.folders))
    table.add_row("Tags únicas", str(s.unique_tags))
    table.add_row("Total de links", str(s.total_links))
    table.add_row("Notas órfãs", str(s.orphan_notes))
    table.add_row("Notas sem tags", str(s.notes_without_tags))
    table.add_row("Notas vazias", str(s.empty_notes))
    table.add_row("Notas curtas (<30 palavras)", str(s.short_notes))
    table.add_row("Média de palavras/nota", str(s.avg_note_length))
    console.print(table)

    if s.top_tags:
        console.print()
        tag_table = Table(title="Top Tags", border_style="yellow")
        tag_table.add_column("Tag", style="bold")
        tag_table.add_column("Usos", justify="right")
        for tag, count in s.top_tags[:10]:
            tag_table.add_row(f"#{tag}", str(count))
        console.print(tag_table)

    if s.most_linked:
        console.print()
        link_table = Table(title="Notas Mais Linkadas", border_style="green")
        link_table.add_column("Nota", style="bold")
        link_table.add_column("Backlinks", justify="right")
        for title, count in s.most_linked[:10]:
            link_table.add_row(title, str(count))
        console.print(link_table)


@app.command()
def review(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
):
    """Auditoria Zettelkasten completa do vault."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.reviewer import ReviewerAgent

    agent = ReviewerAgent(toolkit)
    _run_agent(
        agent,
        "Faça uma auditoria Zettelkasten completa do meu vault. Analise fluxo de "
        "processamento (inbox), atomicidade das permanent notes, conectividade "
        "e cobertura de structure notes. Dê pontuação e plano de ação.",
    )


@app.command()
def organize(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    focus: Optional[str] = typer.Option(None, "--focus", "-f", help="Foco da análise (pasta ou tema)"),
):
    """Sugere melhorias na organização do vault."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.organizer import OrganizerAgent

    agent = OrganizerAgent(toolkit)
    prompt = "Analise a estrutura do meu vault e sugira melhorias na organização."
    if focus:
        prompt += f" Foque especialmente em: {focus}"
    _run_agent(agent, prompt)


@app.command()
def links(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    note: Optional[str] = typer.Option(None, "--note", "-n", help="Nota específica para analisar"),
):
    """Descobre conexões faltantes entre notas."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.linker import LinkerAgent

    agent = LinkerAgent(toolkit)
    prompt = "Analise meu vault e encontre conexões faltantes entre notas."
    if note:
        prompt += f" Comece pela nota: {note}"
    _run_agent(agent, prompt)


@app.command()
def tags(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
):
    """Analisa e sugere melhorias no sistema de tags."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.tagger import TaggerAgent

    agent = TaggerAgent(toolkit)
    _run_agent(
        agent,
        "Analise o sistema de tags do meu vault. Identifique problemas e sugira tags "
        "para notas que não têm. Proponha uma taxonomia organizada.",
    )


@app.command()
def summarize(
    topic: str = typer.Argument(help="Tema ou pasta para resumir"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    moc: bool = typer.Option(False, "--moc", help="Gerar como Map of Content"),
):
    """Cria Structure Notes (MOCs) sobre um tema."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.summarizer import SummarizerAgent

    agent = SummarizerAgent(toolkit)
    if moc:
        prompt = (
            f"Crie uma Structure Note sobre '{topic}' para meu Zettelkasten. "
            "Busque todas as permanent notes e literature notes relevantes. "
            "Organize com frontmatter type: structure. Identifique lacunas."
        )
    else:
        prompt = (
            f"Sintetize o conhecimento que tenho sobre '{topic}'. "
            "Busque notas relevantes e crie um resumo com referências [[wiki-links]]."
        )
    _run_agent(agent, prompt)


@app.command()
def ask(
    question: str = typer.Argument(help="Pergunta sobre suas notas"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
):
    """Pergunta algo e busca a resposta nas suas notas."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.retriever import RetrieverAgent

    agent = RetrieverAgent(toolkit)
    _run_agent(agent, question)


@app.command()
def inbox(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
):
    """Processa fleeting notes da inbox pelo método Zettelkasten."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.zettel import ZettelAgent

    agent = ZettelAgent(toolkit)
    _run_agent(
        agent,
        "Processe minha inbox Zettelkasten. Liste as fleeting notes em inbox/, "
        "leia cada uma, classifique (ideia → permanent note, fonte → literature note, "
        "ação → project note, lixo → deletar) e gere as notas transformadas prontas "
        "para salvar, com frontmatter, tags e links.",
    )


@app.command()
def capture(
    thought: str = typer.Argument(help="Pensamento, ideia ou informação para capturar"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    note_type: str = typer.Option("fleeting", "--type", "-t", help="Tipo: fleeting, zettel, literature, project"),
):
    """Captura rápida de um pensamento no Zettelkasten."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.capture import CaptureAgent

    agent = CaptureAgent(toolkit)
    prompt = (
        f"Capture isso no meu Zettelkasten como {note_type} note: \"{thought}\". "
        "Gere a nota completa com frontmatter, tags, e links para notas existentes. "
        "Sugira o caminho e nome do arquivo."
    )
    _run_agent(agent, prompt)


@app.command()
def ingest(
    source: str = typer.Argument(help="Caminho do arquivo (PDF, texto, imagem) OU texto entre aspas para ingerir"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Tratar source como texto bruto em vez de caminho de arquivo"),
    source_name: str = typer.Option("", "--source-name", "-s", help="Nome da fonte (para texto bruto)"),
):
    """Ingere dados brutos (PDF, imagem, texto) e propõe notas Zettelkasten para aprovação."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from vault.ingest import extract_from_file, extract_from_raw_text
    from agents.ingest import IngestAgent

    # Extrair conteúdo da fonte
    if raw:
        extracted = extract_from_raw_text(source, source_name)
    else:
        source_path = Path(source).expanduser().resolve()
        if not source_path.exists():
            console.print(f"[bold red]Arquivo não encontrado:[/] {source}")
            raise typer.Exit(1)
        console.print(f"[dim]Lendo arquivo: {source_path}[/]")
        try:
            extracted = extract_from_file(str(source_path))
        except ImportError as e:
            console.print(f"[bold red]Dependência faltando:[/] {e}")
            raise typer.Exit(1)

    content_type = extracted["type"]
    content = extracted["content"]
    metadata = extracted.get("metadata", {})

    console.print(f"[dim]Tipo detectado: {content_type}[/]")
    if content_type == "pdf":
        console.print(f"[dim]Páginas: {metadata.get('pages', '?')}[/]")
    elif content_type == "image":
        console.print(f"[dim]Imagem: {metadata.get('media_type', '?')} ({metadata.get('size_bytes', 0)} bytes)[/]")
    console.print(f"[dim]Conteúdo: {len(content)} caracteres[/]\n")

    if content_type == "image":
        prompt = (
            f"Recebi uma imagem ({metadata.get('file', 'desconhecido')}). "
            "Não consigo ver a imagem diretamente, mas o usuário pode descrevê-la. "
            "Com base no nome e contexto, sugira que tipo de notas podem ser criadas. "
            "Pergunte ao usuário para descrever o conteúdo da imagem."
        )
    elif not content.strip():
        console.print("[yellow]Aviso: Nenhum conteúdo textual extraído do arquivo.[/]")
        console.print("[dim]Se é um PDF escaneado, considere usar OCR primeiro.[/]")
        raise typer.Exit(0)
    else:
        # Truncar se muito longo para o prompt
        display_content = content[:5000] + "\n\n[... truncado ...]" if len(content) > 5000 else content
        prompt = (
            f"Recebi o seguinte conteúdo para ingestão no meu Zettelkasten.\n\n"
            f"**Fonte:** {metadata.get('file', metadata.get('source', 'texto direto'))}\n"
            f"**Tipo:** {content_type}\n\n"
            f"**Conteúdo:**\n\n{display_content}\n\n"
            "Analise este conteúdo e crie um plano de ingestão completo. "
            "Decomponha em notas atômicas, classifique cada uma, busque conexões "
            "com o vault existente e apresente o plano para minha aprovação."
        )

    agent = IngestAgent(toolkit)
    _run_agent(agent, prompt)


@app.command()
def scout(
    topic: str = typer.Argument(help="Tema para buscar novidades na web"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    news_only: bool = typer.Option(False, "--news", "-n", help="Buscar apenas notícias (mais recentes)"),
):
    """Busca novidades na web sobre um tema e propõe notas Zettelkasten."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.scout import ScoutAgent

    agent = ScoutAgent(toolkit)

    if news_only:
        prompt = (
            f"Busque as NOTÍCIAS mais recentes sobre '{topic}'. "
            "Foque apenas em novidades das últimas semanas. "
            "Verifique o que já tenho no vault, busque na web, extraia os melhores artigos, "
            "e proponha notas Zettelkasten para minha aprovação."
        )
    else:
        prompt = (
            f"Busque novidades e conteúdo relevante sobre '{topic}'. "
            "Verifique o que já tenho no vault sobre esse tema, "
            "busque notícias E artigos de fundo na web, "
            "extraia os mais relevantes, e proponha notas Zettelkasten para minha aprovação."
        )

    _run_agent(agent, prompt)


@app.command()
def zettel(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
    action: str = typer.Option("review", "--action", "-a", help="Ação: review, atomicity, setup"),
):
    """Manutenção do sistema Zettelkasten."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

    from agents.zettel import ZettelAgent

    agent = ZettelAgent(toolkit)

    prompts = {
        "review": (
            "Faça uma revisão completa do meu sistema Zettelkasten. "
            "Verifique inbox, atomicidade, conexões, structure notes e tags."
        ),
        "atomicity": (
            "Verifique a atomicidade das minhas permanent notes em zettel/. "
            "Encontre notas longas ou com múltiplos assuntos e sugira divisões."
        ),
        "setup": (
            "Analise meu vault e verifique se a estrutura Zettelkasten está correta. "
            "As pastas inbox/, zettel/, references/, structure/, projects/ e archive/ existem? "
            "Há notas fora do lugar? Sugira a reorganização necessária."
        ),
    }

    prompt = prompts.get(action, prompts["review"])
    _run_agent(agent, prompt)


@app.command()
def chat(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Caminho do vault"),
):
    """Modo interativo: converse com seus agentes."""
    _validate_api_key()
    reader = _get_vault(vault)
    toolkit = _get_toolkit(reader)

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

    agents_map = {
        "retriever": RetrieverAgent(toolkit),
        "zettel": ZettelAgent(toolkit),
        "capture": CaptureAgent(toolkit),
        "ingest": IngestAgent(toolkit),
        "scout": ScoutAgent(toolkit),
        "organizer": OrganizerAgent(toolkit),
        "linker": LinkerAgent(toolkit),
        "tagger": TaggerAgent(toolkit),
        "summarizer": SummarizerAgent(toolkit),
        "reviewer": ReviewerAgent(toolkit),
    }
    current_agent = agents_map["retriever"]

    console.print(
        Panel(
            "[bold]Modo Chat Zettelkasten[/]\n\n"
            "Comandos especiais:\n"
            "  [cyan]/agente <nome>[/]  — trocar agente\n"
            "  [cyan]/agentes[/]        — listar agentes disponíveis\n"
            "  [cyan]/sair[/]           — encerrar\n",
            title="ObsidianAI Chat",
            border_style="cyan",
        )
    )
    console.print(f"[dim]Agente ativo: {current_agent.name}[/]\n")

    while True:
        try:
            user_input = console.input("[bold green]Você:[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Até logo![/]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/sair", "/quit", "/exit"):
            console.print("[dim]Até logo![/]")
            break

        if user_input.lower() == "/agentes":
            for name, ag in agents_map.items():
                marker = " [cyan]<- ativo[/]" if name == current_agent.name else ""
                console.print(f"  [bold]{name}[/] — {ag.description}{marker}")
            console.print()
            continue

        if user_input.lower().startswith("/agente "):
            agent_name = user_input.split(" ", 1)[1].strip().lower()
            if agent_name in agents_map:
                current_agent = agents_map[agent_name]
                console.print(f"[green]Agente trocado para: {current_agent.name}[/]\n")
            else:
                console.print(f"[red]Agente '{agent_name}' não encontrado.[/]")
                console.print(f"[dim]Disponíveis: {', '.join(agents_map.keys())}[/]\n")
            continue

        tool_count = 0

        def on_tool(name: str, inputs: dict, result: str) -> None:
            nonlocal tool_count
            tool_count += 1
            console.print(f"  [dim]tool: {name}[/]")

        console.print(f"[dim]({current_agent.name}) pensando...[/]")

        try:
            response = current_agent.run(user_input, on_tool_call=on_tool)
            console.print()
            console.print(Markdown(response))
            console.print()
        except Exception as e:
            console.print(f"[bold red]Erro:[/] {e}\n")


if __name__ == "__main__":
    app()
