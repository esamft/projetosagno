"""Parser de notas Obsidian: frontmatter YAML, wiki-links, tags e headings."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import frontmatter

from .models import Note, NoteMeta


_WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")
_INLINE_TAG_RE = re.compile(
    r"(?:^|\s)#([a-zA-Z\u00C0-\u024F][a-zA-Z0-9\u00C0-\u024F_/-]*)", re.MULTILINE
)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_DATAVIEW_FIELD_RE = re.compile(r"^(\w+)::\s*(.+)$", re.MULTILINE)


def extract_wiki_links(content: str) -> list[str]:
    return list(set(_WIKI_LINK_RE.findall(content)))


def extract_tags(content: str, fm: dict) -> list[str]:
    tags: set[str] = set()

    fm_tags = fm.get("tags", [])
    if isinstance(fm_tags, list):
        tags.update(str(t).strip() for t in fm_tags if t)
    elif isinstance(fm_tags, str):
        tags.update(t.strip() for t in fm_tags.split(",") if t.strip())

    tags.update(_INLINE_TAG_RE.findall(content))
    return sorted(tags)


def extract_headings(content: str) -> list[str]:
    return [
        f"{'#' * len(level)} {text.strip()}"
        for level, text in _HEADING_RE.findall(content)
    ]


def extract_dataview_fields(content: str) -> dict[str, str]:
    return dict(_DATAVIEW_FIELD_RE.findall(content))


def parse_note(file_path: Path, vault_root: Path) -> Optional[Note]:
    try:
        post = frontmatter.load(str(file_path))
    except Exception:
        try:
            raw = file_path.read_text(encoding="utf-8")
            post = frontmatter.Post(raw)
        except Exception:
            return None

    fm = dict(post.metadata) if post.metadata else {}
    body = post.content

    stat = file_path.stat()
    rel_path = str(file_path.relative_to(vault_root))

    aliases_raw = fm.get("aliases", [])
    if isinstance(aliases_raw, str):
        aliases_raw = [a.strip() for a in aliases_raw.split(",")]
    aliases = aliases_raw if isinstance(aliases_raw, list) else []

    meta = NoteMeta(
        path=rel_path,
        title=fm.get("title", file_path.stem),
        tags=extract_tags(body, fm),
        aliases=[str(a) for a in aliases if a],
        created=datetime.fromtimestamp(stat.st_ctime),
        modified=datetime.fromtimestamp(stat.st_mtime),
        frontmatter=fm,
    )

    dataview = extract_dataview_fields(body)
    if dataview:
        meta.frontmatter["_dataview"] = dataview

    return Note(
        meta=meta,
        content=body,
        outgoing_links=extract_wiki_links(body),
        headings=extract_headings(body),
    )
