"""Generate a readable end-to-end demo report from deterministic seed data."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .pipeline import group_items_into_events, monitored_items_from_event_seed
from .repository import load_sources


def build_demo_report(source_registry: Path, event_seed: Path) -> dict[str, Any]:
    sources = load_sources(source_registry)
    items = monitored_items_from_event_seed(event_seed, sources)
    events = [event.to_dashboard_dict() for event in group_items_into_events(items)]
    status_counts = Counter(event["event_status"] for event in events)
    priority_counts = Counter(event["overall_priority"] for event in events)
    official_events = [
        event for event in events if event.get("event_status") == "A_OFFICIALLY_PUBLISHED"
    ]
    high_attention_events = [
        event for event in events if event.get("overall_priority") in {"High", "Critical"}
    ]
    return {
        "summary": {
            "sources_loaded": len(sources),
            "monitored_items": len(items),
            "regulatory_events": len(events),
            "official_events": len(official_events),
            "high_attention_events": len(high_attention_events),
            "status_counts": dict(sorted(status_counts.items())),
            "priority_counts": dict(sorted(priority_counts.items())),
        },
        "sources": [
            {
                "name": source.name,
                "authority_level": source.authority_level.value,
                "source_type": source.source_type,
                "topic_area": source.topic_area,
                "access_method": source.access_method,
                "priority": source.priority,
                "active": source.active,
                "url": source.url,
            }
            for source in sources
        ],
        "events": events,
    }


def write_json_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    events = report["events"]
    lines = [
        "# Dr. G.D.P.R. & AI Act navigator - Demo Report",
        "",
        "This report is generated from deterministic MVP seed data. It shows how",
        "the regulatory monitoring module converts sources and monitored items into",
        "validated, scored, dashboard-ready regulatory events.",
        "",
        "## Demo Narrative",
        "",
        "The demo starts from a curated source registry and deterministic seed",
        "signals. The pipeline normalizes those inputs into monitored items, groups",
        "related items into regulatory events, separates official evidence from",
        "early warning signals, and calculates explainable priority scores.",
        "",
        "The key point is that the platform does not treat every news item or source",
        "as equally reliable. Official evidence increases validation confidence,",
        "while draft or unconfirmed signals remain visible but clearly labelled.",
        "",
        "The generated events are ready to feed a dashboard, a company-specific risk",
        "engine, or an assistant module once the company profile is available.",
        "",
        "## Summary",
        "",
        f"- Sources loaded: {summary['sources_loaded']}",
        f"- Monitored items: {summary['monitored_items']}",
        f"- Regulatory events: {summary['regulatory_events']}",
        f"- Officially published events: {summary['official_events']}",
        f"- High-attention events: {summary['high_attention_events']}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in summary["status_counts"].items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Priority Counts", ""])
    for priority, count in summary["priority_counts"].items():
        lines.append(f"- {priority}: {count}")

    lines.extend(
        [
            "",
            "## Source Registry Snapshot",
            "",
            "| Source | Authority | Type | Access | Priority | Active |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for source in report["sources"]:
        lines.append(
            "| "
            f"{source['name']} | "
            f"{source['authority_level']} | "
            f"{source['source_type']} | "
            f"{source['access_method']} | "
            f"{source['priority']} | "
            f"{source['active']} |"
        )

    lines.extend(
        [
            "",
            "## Validation Logic Summary",
            "",
            "- A_OFFICIALLY_PUBLISHED means the event is supported by official binding evidence or an authoritative official legal source.",
            "- B_OFFICIAL_DRAFT means the event is supported by official guidance, draft material, consultation, or institutional evidence.",
            "- C_UNCONFIRMED_NEWS means the event is currently supported only by trusted warning or expert sources.",
            "- Official evidence increases reliability and makes an alert stronger for dashboard prioritization.",
            "- Warning sources remain visible, but the report labels them separately so the platform does not treat news as law.",
        ]
    )

    lines.extend(["", "## Top Demo Events", ""])
    for event in events[:5]:
        lines.extend(
            [
                f"### {event['event_title']}",
                "",
                f"- Status: {event['event_status']}",
                f"- Priority: {event['overall_priority']}",
                f"- Regulation area: {event['regulation_area']}",
                f"- Reliability score: {event['reliability_score']}",
                f"- Urgency score: {event['urgency_score']}",
                f"- Regulatory impact score: {event['regulatory_impact_score']}",
                f"- Evidence count: {event['evidence_count']}",
                f"- Primary official source: {event.get('primary_official_source_url') or 'not available'}",
                f"- Recommended attention: {event['recommended_attention']}",
                "",
                event["summary"],
                "",
            ]
        )

    lines.extend(
        [
            "## Demo Boundaries",
            "",
            "This is not legal advice and not a final compliance product. It is an MVP",
            "technical demonstration of source monitoring, validation, scoring, and",
            "structured output generation.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
