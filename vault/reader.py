"""Leitor do Obsidian Vault: carrega, indexa e consulta notas."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .models import Note, VaultStats
from .parser import parse_note


class VaultReader:
    def __init__(self, vault_path: Path, excluded_folders: list[str] | None = None):
        self.vault_path = vault_path
        self.excluded = set(excluded_folders or [])
        self._notes: dict[str, Note] = {}
        self._title_index: dict[str, str] = {}
        self._tag_index: dict[str, list[str]] = {}
        self._loaded = False

    def load(self) -> "VaultReader":
        self._notes.clear()
        self._title_index.clear()
        self._tag_index.clear()

        for file_path in self.vault_path.rglob("*.md"):
            if self._is_excluded(file_path):
                continue
            note = parse_note(file_path, self.vault_path)
            if note:
                self._notes[note.meta.path] = note

        self._build_indices()
        self._loaded = True
        return self

    def _is_excluded(self, path: Path) -> bool:
        parts = path.relative_to(self.vault_path).parts
        return any(part.strip() in self.excluded for part in parts)

    def _build_indices(self) -> None:
        self._title_index.clear()
        self._tag_index.clear()

        for path, note in self._notes.items():
            self._title_index[note.meta.title.lower()] = path
            self._title_index[note.meta.stem.lower()] = path
            for alias in note.meta.aliases:
                self._title_index[alias.lower()] = path

        for path, note in self._notes.items():
            for link_target in note.outgoing_links:
                target_path = self._title_index.get(link_target.lower())
                if target_path and target_path in self._notes:
                    target_note = self._notes[target_path]
                    if path not in target_note.backlinks:
                        target_note.backlinks.append(path)

        for path, note in self._notes.items():
            for tag in note.meta.tags:
                self._tag_index.setdefault(tag, []).append(path)

    @property
    def notes(self) -> dict[str, Note]:
        if not self._loaded:
            self.load()
        return self._notes

    def get_note(self, path: str) -> Note | None:
        return self.notes.get(path)

    def get_note_by_title(self, title: str) -> Note | None:
        path = self._title_index.get(title.lower())
        return self._notes.get(path) if path else None

    def search(self, query: str, max_results: int = 20) -> list[Note]:
        q = query.lower()
        scored: list[tuple[int, Note]] = []
        for note in self.notes.values():
            score = 0
            if q in note.meta.title.lower():
                score += 10
            if any(q in tag.lower() for tag in note.meta.tags):
                score += 5
            if q in note.content.lower():
                score += note.content.lower().count(q)
            if score > 0:
                scored.append((score, note))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [note for _, note in scored[:max_results]]

    def get_orphans(self) -> list[Note]:
        return [n for n in self.notes.values() if n.is_orphan]

    def get_notes_without_tags(self) -> list[Note]:
        return [n for n in self.notes.values() if not n.meta.tags]

    def get_notes_by_tag(self, tag: str) -> list[Note]:
        paths = self._tag_index.get(tag, [])
        return [self._notes[p] for p in paths if p in self._notes]

    def get_empty_notes(self) -> list[Note]:
        return [n for n in self.notes.values() if n.is_empty]

    def get_short_notes(self, threshold: int = 30) -> list[Note]:
        return [n for n in self.notes.values() if n.word_count < threshold]

    def get_all_tags(self) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for note in self.notes.values():
            counter.update(note.meta.tags)
        return dict(counter.most_common())

    def get_all_titles(self) -> list[str]:
        return sorted(n.meta.title for n in self.notes.values())

    def get_folders(self) -> dict[str, int]:
        folders: Counter[str] = Counter()
        for path in self.notes:
            parent = str(Path(path).parent)
            if parent != ".":
                folders[parent] += 1
            else:
                folders["(raiz)"] += 1
        return dict(folders.most_common())

    def get_most_linked(self, top: int = 10) -> list[tuple[str, int]]:
        counts = [
            (n.meta.title, len(n.backlinks))
            for n in self.notes.values()
            if n.backlinks
        ]
        counts.sort(key=lambda x: x[1], reverse=True)
        return counts[:top]

    def find_similar_titles(self, threshold: float = 0.6) -> list[tuple[str, str]]:
        titles = list(self._title_index.keys())
        similar = []
        for i, t1 in enumerate(titles):
            for t2 in titles[i + 1 :]:
                if t1 == t2:
                    continue
                common = set(t1.split()) & set(t2.split())
                total = set(t1.split()) | set(t2.split())
                if total and len(common) / len(total) >= threshold:
                    similar.append((t1, t2))
        return similar

    def get_stats(self) -> VaultStats:
        notes = list(self.notes.values())
        if not notes:
            return VaultStats()

        all_tags: Counter[str] = Counter()
        total_links = 0
        for note in notes:
            all_tags.update(note.meta.tags)
            total_links += len(note.outgoing_links)

        orphans = [n for n in notes if n.is_orphan]
        no_tags = [n for n in notes if not n.meta.tags]
        empty = [n for n in notes if n.is_empty]
        short = [n for n in notes if n.is_short]
        avg_len = sum(n.word_count for n in notes) / len(notes)

        return VaultStats(
            total_notes=len(notes),
            total_tags=sum(all_tags.values()),
            unique_tags=len(all_tags),
            total_links=total_links,
            orphan_notes=len(orphans),
            notes_without_tags=len(no_tags),
            empty_notes=len(empty),
            short_notes=len(short),
            avg_note_length=round(avg_len, 1),
            folders=len(self.get_folders()),
            top_tags=all_tags.most_common(15),
            most_linked=self.get_most_linked(10),
        )
