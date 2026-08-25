"""Generate an auditable agent trace for the regulatory monitoring MVP."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from module_web_scraping.demo_report import build_demo_report

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REGISTRY = ROOT / "data" / "source-registry-seed.csv"
EVENT_SEED = ROOT / "data" / "demo-regulatory-events-seed.csv"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "storage" / "agent_trace.md"
DEFAULT_JSON_OUTPUT = ROOT / "storage" / "agent_trace.json"


@dataclass(frozen=True)
class AgentStep:
    agent_name: str
    responsibility: str
    input_summary: str
    output_summary: str
    evidence: list[str]
    next_handoff: str


def build_agent_trace() -> dict[str, Any]:
    report = build_demo_report(SOURCE_REGISTRY, EVENT_SEED)
    summary = report["summary"]
    sources = report["sources"]
    events = report["events"]

    authority_counts = Counter(source["authority_level"] for source in sources)
    status_counts = Counter(event["event_status"] for event in events)
    priority_counts = Counter(event["overall_priority"] for event in events)
    top_events = events[:3]

    steps = [
        AgentStep(
            agent_name="Source Monitoring Agent",
            responsibility="Load curated sources and normalize candidate regulatory signals.",
            input_summary=f"{len(sources)} configured sources from the source registry.",
            output_summary=(
                f"{summary['monitored_items']} monitored items prepared for validation."
            ),
            evidence=[
                f"{level}: {count} source(s)" for level, count in sorted(authority_counts.items())
            ],
            next_handoff="Official Source Verification Agent",
        ),
        AgentStep(
            agent_name="Official Source Verification Agent",
            responsibility="Separate official sources from lower-confidence warning sources.",
            input_summary="Source registry entries with authority levels and access methods.",
            output_summary=(
                f"{summary['official_events']} event(s) have official publication evidence."
            ),
            evidence=[
                "Official binding sources increase reliability.",
                "Official guidance and draft sources remain visible as draft-stage signals.",
                "Trusted warning sources are not treated as binding law.",
            ],
            next_handoff="Regulatory Validation Agent",
        ),
        AgentStep(
            agent_name="Regulatory Validation Agent",
            responsibility="Classify events by evidence level.",
            input_summary=f"{summary['regulatory_events']} grouped regulatory events.",
            output_summary=", ".join(
                f"{status}: {count}" for status, count in sorted(status_counts.items())
            ),
            evidence=[
                "A_OFFICIALLY_PUBLISHED = official legal or binding evidence.",
                "B_OFFICIAL_DRAFT = official guidance, proposal, draft, or consultation.",
                "C_UNCONFIRMED_NEWS = trusted warning without official confirmation.",
            ],
            next_handoff="Risk Scoring Agent",
        ),
        AgentStep(
            agent_name="Risk Scoring Agent",
            responsibility="Calculate explainable priority from reliability, urgency, and impact.",
            input_summary="Validated events with topic labels, authority level, and scoring inputs.",
            output_summary=", ".join(
                f"{priority}: {count}" for priority, count in sorted(priority_counts.items())
            ),
            evidence=[
                f"{event['event_title']} -> {event['overall_priority']}" for event in top_events
            ],
            next_handoff="Demo Report Agent",
        ),
        AgentStep(
            agent_name="Demo Report Agent",
            responsibility="Produce review-ready artifacts for the project demo.",
            input_summary="Source registry, validated events, scores, and explanation traces.",
            output_summary="Markdown and JSON reports ready for dashboard or presentation use.",
            evidence=[
                "storage/demo_report.md",
                "storage/demo_report.json",
                "storage/agent_trace.md",
                "storage/agent_trace.json",
            ],
            next_handoff="Dashboard, company-specific scoring, or assistant module.",
        ),
    ]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "steps": [asdict(step) for step in steps],
    }


def write_json_trace(trace: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")


def write_markdown_trace(trace: dict[str, Any], output_path: Path) -> None:
    summary = trace["summary"]
    lines = [
        "# Dr. G.D.P.R. & AI Act navigator - Agent Trace",
        "",
        "This trace shows the MVP as a chain of constrained, auditable agents.",
        "Each agent has a narrow responsibility and hands structured output to",
        "the next step.",
        "",
        "## Run Summary",
        "",
        f"- Generated at: {trace['generated_at']}",
        f"- Sources loaded: {summary['sources_loaded']}",
        f"- Monitored items: {summary['monitored_items']}",
        f"- Regulatory events: {summary['regulatory_events']}",
        f"- Official events: {summary['official_events']}",
        f"- High-attention events: {summary['high_attention_events']}",
        "",
        "## Agent Steps",
        "",
    ]

    for index, step in enumerate(trace["steps"], start=1):
        lines.extend(
            [
                f"### {index}. {step['agent_name']}",
                "",
                f"Responsibility: {step['responsibility']}",
                "",
                f"Input: {step['input_summary']}",
                "",
                f"Output: {step['output_summary']}",
                "",
                "Evidence:",
            ]
        )
        lines.extend(f"- {item}" for item in step["evidence"])
        lines.extend(["", f"Next handoff: {step['next_handoff']}", ""])

    lines.extend(
        [
            "## Boundary",
            "",
            "This is a deterministic MVP trace. It does not provide legal advice and",
            "does not make final compliance determinations.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate MVP agent trace artifacts")
    parser.add_argument("--output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    trace = build_agent_trace()
    write_markdown_trace(trace, args.output)
    write_json_trace(trace, args.json_output)
    print(
        json.dumps(
            {
                "agent_trace": str(args.output),
                "json_trace": str(args.json_output),
                "steps": len(trace["steps"]),
                **trace["summary"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
