from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class NoteMeta(BaseModel):
    """Metadata de uma nota do Obsidian."""

    path: str
    title: str
    tags: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    frontmatter: dict = Field(default_factory=dict)

    @property
    def stem(self) -> str:
        return Path(self.path).stem


class Note(BaseModel):
    """Representação completa de uma nota do Obsidian."""

    meta: NoteMeta
    content: str = ""
    outgoing_links: list[str] = Field(default_factory=list)
    backlinks: list[str] = Field(default_factory=list)
    headings: list[str] = Field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def is_empty(self) -> bool:
        return self.word_count < 3

    @property
    def is_short(self) -> bool:
        return self.word_count < 30

    @property
    def is_orphan(self) -> bool:
        return not self.outgoing_links and not self.backlinks

    def summary_line(self) -> str:
        tags = ", ".join(f"#{t}" for t in self.meta.tags) if self.meta.tags else "sem tags"
        links_out = len(self.outgoing_links)
        links_in = len(self.backlinks)
        return (
            f"{self.meta.path} | {self.word_count} palavras | "
            f"{tags} | links: {links_out} saindo, {links_in} entrando"
        )


class VaultStats(BaseModel):
    """Estatísticas gerais do vault."""

    total_notes: int = 0
    total_tags: int = 0
    unique_tags: int = 0
    total_links: int = 0
    orphan_notes: int = 0
    notes_without_tags: int = 0
    empty_notes: int = 0
    short_notes: int = 0
    avg_note_length: float = 0.0
    folders: int = 0
    top_tags: list[tuple[str, int]] = Field(default_factory=list)
    most_linked: list[tuple[str, int]] = Field(default_factory=list)
