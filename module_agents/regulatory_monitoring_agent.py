"""Regulatory-monitoring agent for live and cached source feeds."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from module_company_profile.memory_agent.company_memory_agent import (
    DEFAULT_ARTICLE_FEED,
    load_json_list,
)
from module_web_scraping.live_feed import refresh_live_feed


class RegulatoryMonitoringAgent:
    """Refresh regulatory sources and expose a truthful active-feed status."""

    name = "Regulatory Monitoring Agent"

    def __init__(
        self,
        root: Path,
        source_registry: Path,
        live_feed_file: Path,
        freshness: timedelta = timedelta(minutes=30),
    ) -> None:
        self.root = root
        self.source_registry = source_registry
        self.live_feed_file = live_feed_file
        self.freshness = freshness

    def refresh(self) -> None:
        """Collect the configured sources and persist the normalized live feed."""
        refresh_live_feed(self.source_registry, self.live_feed_file)

    def load_active_feed(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prefer fresh monitored data and disclose cached/demo fallback status."""
        if self.live_feed_file.exists():
            try:
                payload = json.loads(self.live_feed_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                payload = {}
            feed_items = (
                [item for item in payload.get("items", []) if isinstance(item, dict)]
                if isinstance(payload, dict) and isinstance(payload.get("items"), list)
                else []
            )
            if feed_items:
                updated_at = payload.get("updated_at")
                effective_mode = str(payload.get("mode") or "cached")
                if effective_mode == "live":
                    try:
                        updated = datetime.fromisoformat(str(updated_at).replace("Z", "+00:00"))
                        if updated.tzinfo is None:
                            updated = updated.replace(tzinfo=UTC)
                        age = datetime.now(UTC) - updated
                        if age > self.freshness or age < -timedelta(minutes=5):
                            effective_mode = "cached"
                    except (TypeError, ValueError):
                        effective_mode = "cached"
                return feed_items, {
                    "mode": effective_mode,
                    "updated_at": updated_at,
                    "refresh_attempted_at": payload.get("refresh_attempted_at"),
                    "sources": payload.get("sources", []),
                    "errors": payload.get("errors", []),
                }
        return load_json_list(self.root / DEFAULT_ARTICLE_FEED), {
            "mode": "demo",
            "updated_at": None,
            "sources": [],
            "errors": ["Live feed unavailable or empty; using bundled demo data."],
        }
