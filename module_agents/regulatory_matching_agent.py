"""Regulatory-matching agent for company-specific dashboard context."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from module_company_profile.memory_agent.company_memory_agent import (
    DEFAULT_REGULATORY_EVENTS,
    build_dashboard_context,
    load_json_list,
)


class RegulatoryMatchingAgent:
    """Match validated company memory with regulatory events and monitored items."""

    name = "Regulatory Matching Agent"

    def __init__(self, root: Path) -> None:
        self.root = root

    def load_regulatory_events(self) -> list[dict[str, Any]]:
        """Load usable regulatory evidence, excluding obsolete placeholder URLs."""
        events = load_json_list(self.root / DEFAULT_REGULATORY_EVENTS)
        return [
            event
            for event in events
            if event.get("primary_official_source_url")
            and "/en/policies/ai-office" not in event["primary_official_source_url"]
            and "/oj/direct-access.html" not in event["primary_official_source_url"]
        ]

    def evaluate(
        self,
        company_memory: dict[str, Any],
        article_feed: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build the personalized warnings, evidence feed, score, and timeline."""
        return build_dashboard_context(
            company_memory,
            self.load_regulatory_events(),
            article_feed,
        )
