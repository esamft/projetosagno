"""Extrator de conteúdo: lê PDFs, imagens, URLs e arquivos de texto para ingestão."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Optional


def extract_from_file(file_path: str) -> dict:
    """Detecta o tipo de arquivo e extrai conteúdo.

    Returns:
        {"type": "text|pdf|image", "content": str, "metadata": dict}
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or ""

    if mime == "application/pdf" or path.suffix.lower() == ".pdf":
        return extract_pdf(path)
    elif mime.startswith("image/"):
        return extract_image(path)
    elif _is_text_file(path, mime):
        return extract_text(path)
    else:
        return extract_text(path)


def extract_pdf(path: Path) -> dict:
    """Extrai texto de um PDF."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber não está instalado. Instale com: pip install pdfplumber"
        )

    pages_text = []
    metadata = {"file": str(path), "type": "pdf"}

    with pdfplumber.open(str(path)) as pdf:
        metadata["pages"] = len(pdf.pages)
        metadata["pdf_metadata"] = pdf.metadata or {}

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- Página {i + 1} ---\n{text}")

    content = "\n\n".join(pages_text)
    if not content.strip():
        metadata["warning"] = "PDF sem texto extraível (pode ser escaneado/imagem)"

    return {"type": "pdf", "content": content, "metadata": metadata}


def extract_image(path: Path) -> dict:
    """Prepara uma imagem para envio ao LLM (base64).

    O conteúdo da imagem será interpretado pelo agente via vision.
    """
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")

    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "image/png"

    return {
        "type": "image",
        "content": f"[Imagem: {path.name}]",
        "image_data": {"base64": b64, "media_type": mime},
        "metadata": {
            "file": str(path),
            "type": "image",
            "media_type": mime,
            "size_bytes": len(data),
        },
    }


def extract_text(path: Path) -> dict:
    """Lê um arquivo de texto."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    content = ""
    used_encoding = ""

    for enc in encodings:
        try:
            content = path.read_text(encoding=enc)
            used_encoding = enc
            break
        except UnicodeDecodeError:
            continue

    return {
        "type": "text",
        "content": content,
        "metadata": {
            "file": str(path),
            "type": "text",
            "extension": path.suffix,
            "encoding": used_encoding,
            "lines": content.count("\n") + 1,
            "chars": len(content),
        },
    }


def extract_from_raw_text(text: str, source: str = "") -> dict:
    """Empacota texto bruto para ingestão."""
    return {
        "type": "text",
        "content": text,
        "metadata": {
            "type": "raw_text",
            "source": source,
            "chars": len(text),
        },
    }


def _is_text_file(path: Path, mime: str) -> bool:
    text_extensions = {
        ".txt", ".md", ".markdown", ".rst", ".csv", ".tsv", ".json",
        ".yaml", ".yml", ".xml", ".html", ".htm", ".log", ".py", ".js",
        ".ts", ".css", ".sql", ".sh", ".bat", ".ini", ".cfg", ".conf",
        ".tex", ".bib", ".org", ".adoc",
    }
    if path.suffix.lower() in text_extensions:
        return True
    if mime and mime.startswith("text/"):
        return True
    return False
