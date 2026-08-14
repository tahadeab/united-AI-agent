"""Small, dependency-light web search helper for agent tool calls."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from urllib.parse import quote_plus, unquote, urlparse
from urllib.request import Request, urlopen


class _SearchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._in_title = False
        self._in_snippet = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag == "a" and "result__a" in classes:
            href = attributes.get("href") or ""
            self._current = {"title": "", "url": self._clean_url(href), "snippet": ""}
            self._in_title = True
        elif self._current and tag in {"a", "div", "span"} and "result__snippet" in classes:
            self._in_snippet = True

    def handle_data(self, data: str) -> None:
        if not self._current:
            return
        text = " ".join(data.split())
        if self._in_title:
            self._current["title"] += text
        elif self._in_snippet:
            self._current["snippet"] += text

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_title:
            self._in_title = False
            if self._current.get("url") and self._current.get("title"):
                self.results.append(self._current)
                self._current = None
        if tag in {"a", "div", "span"}:
            self._in_snippet = False

    @staticmethod
    def _clean_url(href: str) -> str:
        parsed = urlparse(href)
        if parsed.path.startswith("/l/") and "uddg=" in parsed.query:
            from urllib.parse import parse_qs

            return unquote(parse_qs(parsed.query).get("uddg", [href])[0])
        return href


def _instant_answer_results(query: str, max_results: int) -> list[dict[str, str]]:
    """Use DuckDuckGo's JSON endpoint when HTML search is challenged or empty."""
    url = (
        "https://api.duckduckgo.com/?q=" + quote_plus(query)
        + "&format=json&no_html=1&skip_disambig=1"
    )
    request = Request(url, headers={"User-Agent": "UnitedAI-Agent/1.0"})
    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read(2_000_000).decode("utf-8", errors="replace"))
    results: list[dict[str, str]] = []
    abstract = payload.get("Abstract", "").strip()
    abstract_url = payload.get("AbstractURL", "").strip()
    heading = payload.get("Heading", "").strip() or query
    if abstract and abstract_url:
        results.append({"title": heading, "url": abstract_url, "snippet": abstract})
    for topic in payload.get("RelatedTopics", []):
        if len(results) >= max_results:
            break
        if "Topics" in topic:
            for nested in topic["Topics"]:
                if len(results) >= max_results:
                    break
                if nested.get("Text") and nested.get("FirstURL"):
                    results.append({
                        "title": nested["Text"].split(" - ", 1)[0],
                        "url": nested["FirstURL"],
                        "snippet": nested["Text"],
                    })
        elif topic.get("Text") and topic.get("FirstURL"):
            results.append({
                "title": topic["Text"].split(" - ", 1)[0],
                "url": topic["FirstURL"],
                "snippet": topic["Text"],
            })
    return results[:max_results]


def search_web(query: str, max_results: int = 5) -> str:
    """Search the public web and return titles, URLs, and short snippets."""
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    max_results = max(1, min(max_results, 10))
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (UnitedAI-Agent/1.0)"})
    with urlopen(request, timeout=10) as response:
        html = response.read(2_000_000).decode("utf-8", errors="replace")
    parser = _SearchParser()
    parser.feed(html)
    results = parser.results[:max_results]
    if not results:
        results = _instant_answer_results(query, max_results)
    if not results:
        return f"No public web results found for: {query}"
    lines = [f"Search results for: {query}"]
    for index, result in enumerate(results, 1):
        lines.append(
            f"{index}. {result['title']}\nURL: {result['url']}\n"
            f"Snippet: {result['snippet'] or 'No snippet available.'}"
        )
    return "\n\n".join(lines)
