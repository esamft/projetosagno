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
        "Servidor MCP para gestão de conhecimento no Obsidian. "
        "Permite ler, buscar, analisar e modificar notas do vault. "
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
    """Auditoria completa da saúde do vault Obsidian."""
    return (
        "Faça uma auditoria completa do meu vault Obsidian. "
        "Comece coletando as estatísticas, depois analise notas órfãs, "
        "notas sem tags, notas vazias, possíveis duplicatas, e a estrutura de pastas. "
        "Apresente um relatório com pontuação de saúde (0-100), problemas encontrados "
        "organizados por severidade, e um plano de ação priorizado. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def suggest_links() -> str:
    """Encontra conexões faltantes entre notas."""
    return (
        "Analise meu vault Obsidian e encontre conexões faltantes entre notas. "
        "Busque notas órfãs, leia seu conteúdo, e sugira [[wiki-links]] para conectá-las "
        "ao restante do vault. Para cada sugestão, explique o motivo da conexão. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def organize_tags() -> str:
    """Analisa e melhora o sistema de tags."""
    return (
        "Analise o sistema de tags do meu vault Obsidian. "
        "Identifique tags duplicadas, inconsistentes ou mal utilizadas. "
        "Sugira tags para notas sem tags. Proponha uma taxonomia organizada. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def create_moc(topic: str) -> str:
    """Cria um Map of Content (MOC) sobre um tema."""
    return (
        f"Crie um Map of Content (MOC) sobre '{topic}'. "
        "Busque todas as notas relevantes no vault, leia as principais, e crie "
        "um MOC estruturado pronto para ser salvo como nota no Obsidian. "
        "Use [[wiki-links]] para referenciar as notas existentes. "
        "Inclua frontmatter YAML sugerido. "
        "Responda em português brasileiro."
    )


@mcp.prompt()
def daily_review() -> str:
    """Revisão diária do vault com sugestões de ação."""
    return (
        "Faça uma revisão rápida do meu vault Obsidian. "
        "Identifique: notas recentemente modificadas, notas que precisam de atenção "
        "(sem tags, sem links, muito curtas), e sugira 3-5 ações concretas que eu "
        "posso fazer hoje para melhorar meu vault. Seja breve e prático. "
        "Responda em português brasileiro."
    )


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    mcp.run()
