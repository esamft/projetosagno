"""Busca web e extração de conteúdo de artigos/notícias."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchResult:
    """Um resultado de busca web."""

    title: str
    url: str
    snippet: str
    source: str = ""
    date: str = ""


@dataclass
class Article:
    """Artigo extraído de uma URL."""

    url: str
    title: str
    content: str
    author: str = ""
    date: str = ""
    source: str = ""
    word_count: int = 0
    excerpt: str = ""


def search_web(query: str, max_results: int = 10, region: str = "pt-br") -> list[SearchResult]:
    """Busca na web usando DuckDuckGo (sem API key necessária).

    Args:
        query: Termo de busca.
        max_results: Máximo de resultados (padrão 10).
        region: Região para resultados (padrão pt-br).

    Returns:
        Lista de SearchResult.
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        raise ImportError(
            "duckduckgo-search não está instalado. Instale com: pip install duckduckgo-search"
        )

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, region=region, max_results=max_results):
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", r.get("link", "")),
                    snippet=r.get("body", r.get("snippet", "")),
                    source=_extract_domain(r.get("href", r.get("link", ""))),
                )
            )

    return results


def search_news(query: str, max_results: int = 10, region: str = "pt-br") -> list[SearchResult]:
    """Busca notícias recentes usando DuckDuckGo News.

    Args:
        query: Termo de busca.
        max_results: Máximo de resultados.
        region: Região para resultados.

    Returns:
        Lista de SearchResult com data de publicação.
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        raise ImportError(
            "duckduckgo-search não está instalado. Instale com: pip install duckduckgo-search"
        )

    results = []
    with DDGS() as ddgs:
        for r in ddgs.news(query, region=region, max_results=max_results):
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", r.get("link", "")),
                    snippet=r.get("body", r.get("snippet", "")),
                    source=r.get("source", _extract_domain(r.get("url", ""))),
                    date=r.get("date", ""),
                )
            )

    return results


def fetch_article(url: str) -> Article:
    """Extrai o conteúdo principal de uma URL (artigo/notícia).

    Usa trafilatura para extração limpa do conteúdo principal,
    com fallback para BeautifulSoup.

    Args:
        url: URL do artigo.

    Returns:
        Article com conteúdo extraído.
    """
    # Tentar trafilatura primeiro (melhor para artigos)
    content = _fetch_with_trafilatura(url)

    if not content or len(content.strip()) < 100:
        # Fallback para BeautifulSoup
        content = _fetch_with_bs4(url)

    if not content:
        content = "[Não foi possível extrair conteúdo desta URL]"

    title = _extract_title_from_content(content) or _extract_domain(url)
    word_count = len(content.split())

    return Article(
        url=url,
        title=title,
        content=content,
        source=_extract_domain(url),
        word_count=word_count,
        excerpt=content[:300].strip() + "..." if len(content) > 300 else content,
    )


def _fetch_with_trafilatura(url: str) -> str:
    """Extrai conteúdo usando trafilatura."""
    try:
        import trafilatura
    except ImportError:
        return ""

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        result = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
            output_format="txt",
        )
        return result or ""
    except Exception:
        return ""


def _fetch_with_bs4(url: str) -> str:
    """Fallback: extrai conteúdo usando requests + BeautifulSoup."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return ""

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ObsidianAI/1.0; Knowledge Management Bot)"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remover scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        # Tentar encontrar o conteúdo principal
        main = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=re.compile(r"(content|article|post|entry)", re.I))
            or soup.find("body")
        )

        if not main:
            return ""

        # Extrair texto limpo
        paragraphs = main.find_all(["p", "h1", "h2", "h3", "h4", "li"])
        text_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 20:  # Ignorar parágrafos muito curtos
                if p.name and p.name.startswith("h"):
                    level = int(p.name[1])
                    text_parts.append(f"{'#' * level} {text}")
                else:
                    text_parts.append(text)

        return "\n\n".join(text_parts)

    except Exception:
        return ""


def _extract_domain(url: str) -> str:
    """Extrai o domínio de uma URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url


def _extract_title_from_content(content: str) -> str:
    """Tenta extrair o título do conteúdo (primeira linha de heading)."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line and len(line) > 10 and len(line) < 200:
            return line
    return ""


def format_search_results(results: list[SearchResult]) -> str:
    """Formata resultados de busca como texto legível."""
    if not results:
        return "Nenhum resultado encontrado."

    parts = []
    for i, r in enumerate(results, 1):
        entry = f"**{i}. {r.title}**\n"
        entry += f"   URL: {r.url}\n"
        entry += f"   Fonte: {r.source}"
        if r.date:
            entry += f" | Data: {r.date}"
        entry += f"\n   {r.snippet}"
        parts.append(entry)

    return "\n\n".join(parts)


def format_article(article: Article) -> str:
    """Formata um artigo extraído como texto para o agente."""
    parts = [
        f"# {article.title}",
        f"**URL:** {article.url}",
        f"**Fonte:** {article.source}",
    ]
    if article.author:
        parts.append(f"**Autor:** {article.author}")
    if article.date:
        parts.append(f"**Data:** {article.date}")
    parts.append(f"**Palavras:** {article.word_count}")
    parts.append("")
    parts.append(article.content)

    return "\n".join(parts)
