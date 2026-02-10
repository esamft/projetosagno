"""Toolkit: expõe operações do vault como tools para os agentes LLM."""

from __future__ import annotations

import json
from typing import Any, Callable

from vault.reader import VaultReader


class VaultToolkit:
    """Registro central de tools. Cada agente seleciona as que precisa."""

    def __init__(self, vault: VaultReader):
        self.vault = vault
        self._registry: dict[str, dict[str, Any]] = {}
        self._register_all()

    def get(self, *names: str) -> tuple[list[dict], dict[str, Callable]]:
        schemas = []
        handlers: dict[str, Callable] = {}
        for name in names:
            entry = self._registry[name]
            schemas.append(entry["schema"])
            handlers[name] = entry["handler"]
        return schemas, handlers

    def all_names(self) -> list[str]:
        return list(self._registry.keys())

    # ------------------------------------------------------------------ #
    #  Registro de tools                                                  #
    # ------------------------------------------------------------------ #

    def _register_all(self) -> None:
        self._register(
            "get_vault_stats",
            "Retorna estatísticas gerais do vault Obsidian: total de notas, tags, "
            "links, notas órfãs, notas vazias, tags mais usadas e notas mais linkadas.",
            {},
            [],
            self._get_vault_stats,
        )
        self._register(
            "search_notes",
            "Busca notas pelo conteúdo ou título. Retorna lista resumida das notas encontradas.",
            {"query": {"type": "string", "description": "Termo de busca"}},
            ["query"],
            self._search_notes,
        )
        self._register(
            "get_note_content",
            "Retorna o conteúdo completo de uma nota dado seu caminho relativo no vault.",
            {"path": {"type": "string", "description": "Caminho relativo da nota (ex: pasta/nota.md)"}},
            ["path"],
            self._get_note_content,
        )
        self._register(
            "list_all_notes",
            "Lista todas as notas do vault com título, tags, contagem de palavras e links.",
            {},
            [],
            self._list_all_notes,
        )
        self._register(
            "get_orphan_notes",
            "Retorna notas órfãs (sem links de entrada nem de saída).",
            {},
            [],
            self._get_orphan_notes,
        )
        self._register(
            "get_notes_without_tags",
            "Retorna notas que não possuem nenhuma tag.",
            {},
            [],
            self._get_notes_without_tags,
        )
        self._register(
            "get_all_tags",
            "Retorna todas as tags do vault com contagem de uso.",
            {},
            [],
            self._get_all_tags,
        )
        self._register(
            "get_notes_by_tag",
            "Retorna todas as notas que possuem uma tag específica.",
            {"tag": {"type": "string", "description": "Nome da tag (sem #)"}},
            ["tag"],
            self._get_notes_by_tag,
        )
        self._register(
            "get_empty_notes",
            "Retorna notas vazias ou quase vazias (menos de 3 palavras).",
            {},
            [],
            self._get_empty_notes,
        )
        self._register(
            "get_short_notes",
            "Retorna notas curtas (menos de 30 palavras).",
            {},
            [],
            self._get_short_notes,
        )
        self._register(
            "get_folder_structure",
            "Retorna a estrutura de pastas do vault com contagem de notas por pasta.",
            {},
            [],
            self._get_folder_structure,
        )
        self._register(
            "get_note_links",
            "Retorna os links de saída e de entrada (backlinks) de uma nota específica.",
            {"path": {"type": "string", "description": "Caminho relativo da nota"}},
            ["path"],
            self._get_note_links,
        )
        self._register(
            "find_similar_titles",
            "Encontra notas com títulos similares que podem ser duplicatas.",
            {},
            [],
            self._find_similar_titles,
        )
        self._register(
            "get_all_note_titles",
            "Retorna lista com todos os títulos de notas existentes no vault.",
            {},
            [],
            self._get_all_note_titles,
        )
        self._register(
            "get_most_linked_notes",
            "Retorna as notas mais referenciadas (com mais backlinks) no vault.",
            {},
            [],
            self._get_most_linked_notes,
        )
        self._register(
            "get_notes_by_type",
            "Retorna notas filtradas por tipo Zettelkasten (fleeting, zettel, literature, structure, project).",
            {"note_type": {"type": "string", "description": "Tipo: fleeting, zettel, literature, structure ou project"}},
            ["note_type"],
            self._get_notes_by_type,
        )
        self._register(
            "get_inbox_notes",
            "Retorna notas na pasta inbox/ (fleeting notes a processar).",
            {},
            [],
            self._get_inbox_notes,
        )
        self._register(
            "get_notes_by_folder",
            "Retorna notas de uma pasta específica do vault.",
            {"folder": {"type": "string", "description": "Nome da pasta (ex: zettel, references, projects)"}},
            ["folder"],
            self._get_notes_by_folder,
        )
        self._register(
            "get_long_notes",
            "Retorna permanent notes longas (>500 palavras) que podem violar atomicidade.",
            {},
            [],
            self._get_long_notes,
        )

    def _register(
        self,
        name: str,
        description: str,
        properties: dict,
        required: list[str],
        handler: Callable,
    ) -> None:
        self._registry[name] = {
            "schema": {
                "name": name,
                "description": description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
            "handler": handler,
        }

    # ------------------------------------------------------------------ #
    #  Implementações                                                     #
    # ------------------------------------------------------------------ #

    def _get_vault_stats(self) -> str:
        stats = self.vault.get_stats()
        data = stats.model_dump()
        data["top_tags"] = [{"tag": t, "count": c} for t, c in stats.top_tags]
        data["most_linked"] = [{"title": t, "backlinks": c} for t, c in stats.most_linked]
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _search_notes(self, query: str) -> str:
        results = self.vault.search(query)
        if not results:
            return json.dumps({"results": [], "message": f"Nenhuma nota encontrada para '{query}'"})
        return json.dumps(
            {"results": [_note_summary(n) for n in results]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_note_content(self, path: str) -> str:
        note = self.vault.get_note(path)
        if not note:
            note = self.vault.get_note_by_title(path)
        if not note:
            return json.dumps({"error": f"Nota não encontrada: {path}"})
        return json.dumps(
            {
                "path": note.meta.path,
                "title": note.meta.title,
                "tags": note.meta.tags,
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

    def _list_all_notes(self) -> str:
        notes = sorted(self.vault.notes.values(), key=lambda n: n.meta.path)
        return json.dumps(
            {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_orphan_notes(self) -> str:
        orphans = self.vault.get_orphans()
        return json.dumps(
            {"total": len(orphans), "notes": [_note_summary(n) for n in orphans]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_notes_without_tags(self) -> str:
        notes = self.vault.get_notes_without_tags()
        return json.dumps(
            {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_all_tags(self) -> str:
        tags = self.vault.get_all_tags()
        return json.dumps(
            {"total_unique": len(tags), "tags": [{"tag": t, "count": c} for t, c in tags.items()]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_notes_by_tag(self, tag: str) -> str:
        notes = self.vault.get_notes_by_tag(tag)
        return json.dumps(
            {"tag": tag, "total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_empty_notes(self) -> str:
        notes = self.vault.get_empty_notes()
        return json.dumps(
            {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_short_notes(self) -> str:
        notes = self.vault.get_short_notes()
        return json.dumps(
            {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_folder_structure(self) -> str:
        folders = self.vault.get_folders()
        return json.dumps(
            {"total_folders": len(folders), "folders": folders},
            ensure_ascii=False,
            indent=2,
        )

    def _get_note_links(self, path: str) -> str:
        note = self.vault.get_note(path)
        if not note:
            note = self.vault.get_note_by_title(path)
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

    def _find_similar_titles(self) -> str:
        similar = self.vault.find_similar_titles()
        return json.dumps(
            {"total_pairs": len(similar), "pairs": [{"a": a, "b": b} for a, b in similar]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_all_note_titles(self) -> str:
        titles = self.vault.get_all_titles()
        return json.dumps({"total": len(titles), "titles": titles}, ensure_ascii=False, indent=2)

    def _get_most_linked_notes(self) -> str:
        most = self.vault.get_most_linked(15)
        return json.dumps(
            {"notes": [{"title": t, "backlinks": c} for t, c in most]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_notes_by_type(self, note_type: str) -> str:
        notes = [
            n for n in self.vault.notes.values()
            if n.meta.frontmatter.get("type", "").lower() == note_type.lower()
        ]
        return json.dumps(
            {"type": note_type, "total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_inbox_notes(self) -> str:
        notes = [
            n for n in self.vault.notes.values()
            if n.meta.path.startswith("inbox/") or n.meta.path.startswith("inbox\\")
        ]
        notes.sort(key=lambda n: n.meta.modified or n.meta.created, reverse=True)
        return json.dumps(
            {"total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_notes_by_folder(self, folder: str) -> str:
        folder_clean = folder.strip("/").strip("\\")
        notes = [
            n for n in self.vault.notes.values()
            if n.meta.path.startswith(folder_clean + "/") or n.meta.path.startswith(folder_clean + "\\")
        ]
        notes.sort(key=lambda n: n.meta.path)
        return json.dumps(
            {"folder": folder, "total": len(notes), "notes": [_note_summary(n) for n in notes]},
            ensure_ascii=False,
            indent=2,
        )

    def _get_long_notes(self) -> str:
        notes = [
            n for n in self.vault.notes.values()
            if n.word_count > 500
            and (n.meta.path.startswith("zettel/") or n.meta.frontmatter.get("type") == "zettel")
        ]
        notes.sort(key=lambda n: n.word_count, reverse=True)
        items = [
            {**_note_summary(n), "headings_count": len(n.headings)}
            for n in notes
        ]
        return json.dumps(
            {"total": len(items), "notes": items},
            ensure_ascii=False,
            indent=2,
        )


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
