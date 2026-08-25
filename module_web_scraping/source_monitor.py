"""Basic deterministic source monitoring.

This module intentionally keeps live access small and replaceable. It supports
webpage fetching with the Python standard library plus pure functions that can
be tested using static HTML fixtures.
"""

from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .models import CollectionStatus, MonitoredItem, Source
from .pipeline import item_type_from_source
from .topic_detection import detect_regulation_area, detect_topic_labels, normalize_text


@dataclass(frozen=True)
class CandidateLink:
    title: str
    url: str
    summary: str = ""


LOW_VALUE_TITLE_PATTERNS = (
    "the structure of",
    "tasks of",
    "any question",
    "join the",
    "contact",
    "subscribe",
    "newsletter",
    "press corner",
    "share this",
)

IGNORED_CONTENT_TAGS = frozenset({"script", "style", "noscript", "svg"})


def has_embedded_stylesheet(value: str) -> bool:
    """Return whether a supposed title contains serialized CSS rather than prose."""

    compact = clean_text(value).lower()
    if compact.startswith((".css-", "@layer ", "<style")):
        return True
    prefix = compact[:500]
    return (
        "{" in prefix
        and "}" in prefix
        and any(
            marker in prefix
            for marker in ("font-size:", "font-family:", "display:", "overflow:", "--chakra-")
        )
    )


class LinkExtractor(HTMLParser):
    """Extract readable anchor text and absolute links from an HTML page."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self._current_href: str | None = None
        self._text_parts: list[str] = []
        self.links: list[CandidateLink] = []
        self.page_title = ""
        self._in_title = False
        self._title_parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in IGNORED_CONTENT_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self._current_href = urljoin(self.base_url, href)
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        if self._current_href:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in IGNORED_CONTENT_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._in_title = False
            self.page_title = clean_text(" ".join(self._title_parts))
        if tag != "a" or not self._current_href:
            return
        title = clean_text(" ".join(self._text_parts))
        if title:
            self.links.append(CandidateLink(title=title, url=self._current_href))
        self._current_href = None
        self._text_parts = []


def clean_text(value: str) -> str:
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def fetch_webpage(
    url: str,
    timeout_seconds: int = 20,
    max_bytes: int = 5 * 1024 * 1024,
) -> str:
    # Only fetch over HTTP(S). urllib would otherwise honour schemes such as
    # file://, ftp://, or data://, so an unexpected or crafted registry entry
    # like "file:///etc/passwd" could be read from disk. Curated sources are
    # always web pages, so restricting the scheme removes that SSRF/local-file
    # surface without limiting legitimate use.
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Unsupported or non-HTTP(S) source URL: {url!r}")

    request = Request(
        url,
        headers={
            "User-Agent": ("AI-Regulatory-Intelligence-MVP/0.1 (educational research prototype)")
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        content_type = response.headers.get("Content-Type", "")
        encoding = "utf-8"
        match = re.search(r"charset=([\w-]+)", content_type)
        if match:
            encoding = match.group(1)
        # Cap the body so a very large or malicious response cannot exhaust
        # memory. One extra byte is requested only to detect truncation.
        raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError(f"Source response exceeded the {max_bytes}-byte safety limit: {url!r}")
        return raw.decode(encoding, errors="replace")


def extract_candidate_links(html_text: str, base_url: str, limit: int = 25) -> list[CandidateLink]:
    parser = LinkExtractor(base_url)
    parser.feed(html_text)

    candidates: list[CandidateLink] = []
    seen_urls: set[str] = set()
    for link in parser.links:
        if link.url in seen_urls:
            continue
        if is_low_value_link(link, base_url):
            continue
        seen_urls.add(link.url)
        labels = detect_topic_labels(link.title, link.summary)
        if labels:
            candidates.append(link)
        if len(candidates) >= limit:
            break

    if not candidates and parser.page_title:
        candidates.append(CandidateLink(title=parser.page_title, url=base_url))
    return candidates


def is_low_value_link(link: CandidateLink, base_url: str) -> bool:
    normalized_title = normalize_text(link.title)
    normalized_base = base_url.split("#", 1)[0].rstrip("/")
    normalized_url = link.url.split("#", 1)[0].rstrip("/")

    if link.url.endswith("undefined"):
        return True
    if "#" in link.url and normalized_url == normalized_base:
        return True
    if len(normalized_title) < 8:
        return True
    if has_embedded_stylesheet(link.title):
        return True
    return any(pattern in normalized_title for pattern in LOW_VALUE_TITLE_PATTERNS)


def candidate_to_monitored_item(
    candidate: CandidateLink,
    source: Source,
    item_id: int,
    retrieved_at: datetime | None = None,
) -> MonitoredItem:
    retrieved_at = retrieved_at or datetime.now()
    topic_labels = detect_topic_labels(candidate.title, candidate.summary)
    regulation_area = detect_regulation_area(topic_labels)
    collection_status = (
        CollectionStatus.NEW if topic_labels else CollectionStatus.IGNORED_OUT_OF_SCOPE
    )
    raw_hash = hashlib.sha256(
        f"{candidate.title}|{candidate.summary}|{candidate.url}".encode()
    ).hexdigest()
    return MonitoredItem(
        id=item_id,
        source_id=source.id,
        source_name=source.name,
        title=candidate.title,
        url=candidate.url,
        retrieved_at=retrieved_at,
        item_type=item_type_from_source(source),
        source_authority_level=source.authority_level,
        regulation_area=regulation_area,
        topic_labels=topic_labels,
        collection_status=collection_status,
        summary=candidate.summary,
        raw_text_hash=raw_hash,
        normalized_title=normalize_text(candidate.title),
    )


def monitor_source_from_html(
    source: Source,
    html_text: str,
    starting_item_id: int = 1,
    limit: int = 25,
) -> list[MonitoredItem]:
    candidates = extract_candidate_links(html_text, source.url, limit=limit)
    return [
        candidate_to_monitored_item(candidate, source, item_id)
        for item_id, candidate in enumerate(candidates, start=starting_item_id)
    ]


def monitor_source(
    source: Source, starting_item_id: int = 1, limit: int = 25
) -> list[MonitoredItem]:
    """Fetch and monitor one source.

    Network failures are intentionally surfaced to the caller so CLI or scheduled
    jobs can log the exact failing source.
    """
    html_text = fetch_webpage(source.url)
    return monitor_source_from_html(source, html_text, starting_item_id, limit)


def deduplicate_items(items: list[MonitoredItem]) -> list[MonitoredItem]:
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    deduped: list[MonitoredItem] = []
    for item in items:
        if item.url in seen_urls or item.raw_text_hash in seen_hashes:
            item.collection_status = CollectionStatus.ALREADY_SEEN
            continue
        seen_urls.add(item.url)
        seen_hashes.add(item.raw_text_hash)
        deduped.append(item)
    return deduped


def deduplicate_against_existing(
    items: list[MonitoredItem],
    existing_urls: set[str],
    existing_hashes: set[str],
) -> list[MonitoredItem]:
    """Remove items already seen in previous persisted runs."""
    fresh: list[MonitoredItem] = []
    seen_urls = set(existing_urls)
    seen_hashes = set(existing_hashes)
    for item in items:
        if item.url in seen_urls or item.raw_text_hash in seen_hashes:
            item.collection_status = CollectionStatus.ALREADY_SEEN
            continue
        seen_urls.add(item.url)
        seen_hashes.add(item.raw_text_hash)
        fresh.append(item)
    return fresh
