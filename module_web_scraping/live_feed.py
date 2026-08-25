"""Collect a small live regulatory news feed from configured official sources."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from .repository import load_sources
from .source_monitor import deduplicate_items, has_embedded_stylesheet, monitor_source

OFFICIAL_SOURCE_NAMES = (
    "European Commission Digital Strategy News",
    "EDPB News",
    "European Commission AI Office",
)

EARLY_WARNING_SOURCE_NAMES = (
    "IAPP News",
    "Inside Privacy AI",
    "Future of Privacy Forum AI",
)

LIVE_SOURCE_NAMES = OFFICIAL_SOURCE_NAMES + EARLY_WARNING_SOURCE_NAMES
IGNORED_NAVIGATION_TITLES = {
    "ai office",
    "data protection",
    "general data protection notice",
    "general-purpose ai (gpai)",
}


def refresh_live_feed(
    source_registry: Path, output_path: Path, limit_per_source: int = 12
) -> dict[str, Any]:
    sources_by_name = {source.name: source for source in load_sources(source_registry)}
    items = []
    errors: list[str] = []

    def collect_source(source_name: str) -> tuple[str, list[Any], str | None]:
        source = sources_by_name.get(source_name)
        if source is None:
            return source_name, [], f"Source not configured: {source_name}"
        try:
            return source_name, monitor_source(source, limit=limit_per_source), None
        except Exception as exc:  # noqa: BLE001
            return source_name, [], f"{source_name}: {exc}"

    with ThreadPoolExecutor(max_workers=len(LIVE_SOURCE_NAMES)) as executor:
        results = list(executor.map(collect_source, LIVE_SOURCE_NAMES))
    for _, source_items, error in results:
        items.extend(source_items)
        if error:
            errors.append(error)

    unique_items = [
        item
        for item in deduplicate_items(items)
        if item.title.strip().lower() not in IGNORED_NAVIGATION_TITLES
        and not item.title.strip().lower().startswith("continue reading")
        and not has_embedded_stylesheet(item.title)
        and "#more-" not in item.url
    ]
    retrieved_at = datetime.now(UTC).isoformat()
    feed = []
    for item in unique_items:
        source = sources_by_name.get(item.source_name)
        parsed_url = urlparse(item.url)
        if source is None or parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            continue
        is_early_warning = source.name in EARLY_WARNING_SOURCE_NAMES
        feed.append(
            {
                "title": item.title,
                "source": item.source_name,
                "url": item.url,
                "kind": "live_monitored_item",
                "status": "EARLY_WARNING" if is_early_warning else "OFFICIAL_UPDATE",
                "status_label": (
                    "Early warning - not law" if is_early_warning else "Official update"
                ),
                "source_category": ("early_warning" if is_early_warning else "official_update"),
                "source_type": source.source_type,
                "authority_level": source.authority_level.value,
                "is_official": not is_early_warning,
                "legal_status": (
                    "Non-binding commentary; verify against official sources"
                    if is_early_warning
                    else "Official source; check whether the item is binding law or guidance"
                ),
                "priority": "Review",
                "regulation_area": item.regulation_area,
                "topic_labels": list(item.topic_labels),
                "summary": item.summary
                or (
                    "Early signal detected from a trusted professional source. "
                    "It is not law and requires verification against official sources."
                    if is_early_warning
                    else "Update detected from an official source. Open the source to read the complete content."
                ),
                "recommended_attention": "Review the impact on this company profile",
                "retrieved_at": item.retrieved_at.isoformat(),
            }
        )
    payload = {
        "mode": "live" if feed else "failed",
        "updated_at": retrieved_at,
        "sources": list(LIVE_SOURCE_NAMES),
        "errors": errors,
        "items": feed,
    }

    # A live refresh is optional enrichment, not a reason to break the demo.
    # If every source is unavailable, retain the last non-empty snapshot and
    # expose the failed attempt through metadata instead of replacing it with
    # an empty feed.
    if not feed and output_path.exists():
        try:
            cached_payload = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            cached_payload = {}
        if cached_payload.get("items"):
            payload = {
                **cached_payload,
                "mode": "cached",
                "refresh_attempted_at": retrieved_at,
                "errors": errors,
            }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.{uuid4().hex}.tmp")
    try:
        temporary_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return payload
