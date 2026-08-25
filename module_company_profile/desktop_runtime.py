"""Shared runtime services for the native PySide6 desktop application."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REGISTRY = ROOT / "module_web_scraping" / "source_registry_seed.csv"
LIVE_FEED_FILE = ROOT / "storage" / "web_scraping_outputs" / "live_articles_and_news_feed.json"
PROFILE_HISTORY_DIR = ROOT / "storage" / "company_profile" / "history"

sys.path.insert(0, str(ROOT))
from module_agents import (  # noqa: E402
    CompanyProfileAgent,
    DrAAgent,
    RegulatoryMatchingAgent,
    RegulatoryMonitoringAgent,
)

COMPANY_PROFILE_AGENT = CompanyProfileAgent()
REGULATORY_MATCHING_AGENT = RegulatoryMatchingAgent(ROOT)
REGULATORY_MONITORING_AGENT = RegulatoryMonitoringAgent(
    ROOT,
    SOURCE_REGISTRY,
    LIVE_FEED_FILE,
)
DR_A_AGENT = DrAAgent()


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Run the explicit company, monitoring, and matching agent handoffs."""
    memory = COMPANY_PROFILE_AGENT.evaluate(payload)
    article_feed, feed_meta = REGULATORY_MONITORING_AGENT.load_active_feed()
    dashboard_context = REGULATORY_MATCHING_AGENT.evaluate(memory, article_feed)
    return {
        "questionnaire_payload": payload,
        "company_memory": memory,
        "dashboard_context": dashboard_context,
        "feed_meta": feed_meta,
    }


def build_export_evaluation(payload: dict[str, Any]) -> dict[str, Any]:
    """Rebuild report input from questionnaire answers, ignoring derived UI data."""
    questionnaire = payload.get("questionnaire_payload")
    if not isinstance(questionnaire, dict):
        raise ValueError("A completed questionnaire is required for report export.")
    return evaluate_payload(questionnaire)


def load_demo_profile(profile_id: str) -> dict[str, Any]:
    demo_profiles = {
        "low-risk-saas": ROOT
        / "module_company_profile"
        / "memory_agent"
        / "demo_profiles"
        / "01_low_risk_saas.json",
        "hr-ai": ROOT
        / "module_company_profile"
        / "memory_agent"
        / "demo_profiles"
        / "02_hr_ai_high_risk.json",
        "gpai-provider": ROOT
        / "module_company_profile"
        / "memory_agent"
        / "demo_profiles"
        / "03_gpai_provider.json",
    }
    path = demo_profiles.get(profile_id)
    if not path:
        raise ValueError(f"Unknown demo profile: {profile_id}")
    return json.loads(path.read_text(encoding="utf-8"))
