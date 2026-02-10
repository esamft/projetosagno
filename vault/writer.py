"""Escritor do vault: operações de criação e modificação de notas."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import frontmatter


class VaultWriter:
    """Operações de escrita no vault Obsidian."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

    def create_note(
        self,
        path: str,
        content: str,
        title: Optional[str] = None,
        tags: Optional[list[str]] = None,
        extra_frontmatter: Optional[dict] = None,
    ) -> str:
        """Cria uma nova nota no vault.

        Returns:
            Caminho relativo da nota criada.
        """
        full_path = self.vault_path / path
        if not full_path.suffix:
            full_path = full_path.with_suffix(".md")
        if full_path.exists():
            raise FileExistsError(f"Nota já existe: {path}")

        full_path.parent.mkdir(parents=True, exist_ok=True)

        fm: dict = {}
        if title:
            fm["title"] = title
        if tags:
            fm["tags"] = tags
        if extra_frontmatter:
            fm.update(extra_frontmatter)

        fm["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        post = frontmatter.Post(content, **fm)
        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return str(full_path.relative_to(self.vault_path))

    def append_to_note(self, path: str, content: str) -> str:
        """Adiciona conteúdo ao final de uma nota existente."""
        full_path = self._resolve(path)
        existing = full_path.read_text(encoding="utf-8")
        full_path.write_text(existing.rstrip() + "\n\n" + content + "\n", encoding="utf-8")
        return str(full_path.relative_to(self.vault_path))

    def prepend_to_note(self, path: str, content: str) -> str:
        """Adiciona conteúdo após o frontmatter de uma nota."""
        full_path = self._resolve(path)
        post = frontmatter.load(str(full_path))
        post.content = content + "\n\n" + post.content
        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return str(full_path.relative_to(self.vault_path))

    def add_tags(self, path: str, new_tags: list[str]) -> list[str]:
        """Adiciona tags ao frontmatter de uma nota.

        Returns:
            Lista completa de tags após a adição.
        """
        full_path = self._resolve(path)
        post = frontmatter.load(str(full_path))

        existing = post.metadata.get("tags", [])
        if isinstance(existing, str):
            existing = [t.strip() for t in existing.split(",")]
        existing_set = set(existing)

        for tag in new_tags:
            tag = tag.lstrip("#").strip()
            if tag and tag not in existing_set:
                existing.append(tag)
                existing_set.add(tag)

        post.metadata["tags"] = existing
        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return existing

    def remove_tags(self, path: str, tags_to_remove: list[str]) -> list[str]:
        """Remove tags do frontmatter de uma nota."""
        full_path = self._resolve(path)
        post = frontmatter.load(str(full_path))

        existing = post.metadata.get("tags", [])
        if isinstance(existing, str):
            existing = [t.strip() for t in existing.split(",")]

        remove_set = {t.lstrip("#").strip() for t in tags_to_remove}
        remaining = [t for t in existing if t not in remove_set]

        post.metadata["tags"] = remaining
        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return remaining

    def insert_link(self, path: str, target: str, context_heading: Optional[str] = None) -> str:
        """Insere um [[wiki-link]] em uma nota.

        Se context_heading for fornecido, insere após o heading.
        Caso contrário, insere na seção 'Relacionados' no final.
        """
        full_path = self._resolve(path)
        post = frontmatter.load(str(full_path))
        link = f"[[{target}]]"

        if link in post.content:
            return f"Link {link} já existe na nota"

        if context_heading:
            pattern = re.compile(
                rf"^(#{{{1,6}}}\s+{re.escape(context_heading)}.*)$",
                re.MULTILINE,
            )
            match = pattern.search(post.content)
            if match:
                insert_pos = match.end()
                post.content = (
                    post.content[:insert_pos]
                    + f"\n- {link}"
                    + post.content[insert_pos:]
                )
            else:
                post.content = post.content.rstrip() + f"\n\n## Relacionados\n- {link}\n"
        else:
            related_match = re.search(r"^##\s+Relacionados", post.content, re.MULTILINE)
            if related_match:
                section_end = post.content.find("\n## ", related_match.end())
                if section_end == -1:
                    post.content = post.content.rstrip() + f"\n- {link}\n"
                else:
                    post.content = (
                        post.content[:section_end]
                        + f"- {link}\n"
                        + post.content[section_end:]
                    )
            else:
                post.content = post.content.rstrip() + f"\n\n## Relacionados\n- {link}\n"

        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return f"Link {link} inserido em {path}"

    def update_frontmatter(self, path: str, fields: dict) -> dict:
        """Atualiza campos do frontmatter de uma nota."""
        full_path = self._resolve(path)
        post = frontmatter.load(str(full_path))
        post.metadata.update(fields)
        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return dict(post.metadata)

    def replace_content(self, path: str, new_content: str) -> str:
        """Substitui o conteúdo inteiro de uma nota (mantém frontmatter)."""
        full_path = self._resolve(path)
        post = frontmatter.load(str(full_path))
        post.content = new_content
        full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return str(full_path.relative_to(self.vault_path))

    def _resolve(self, path: str) -> Path:
        full_path = self.vault_path / path
        if not full_path.exists():
            if not full_path.suffix:
                full_path = full_path.with_suffix(".md")
            if not full_path.exists():
                raise FileNotFoundError(f"Nota não encontrada: {path}")
        return full_path
