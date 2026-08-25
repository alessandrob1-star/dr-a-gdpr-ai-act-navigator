"""Smoke run for the validation engine package container."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
for parent in Path(__file__).resolve().parents:
    if (parent / "module_web_scraping").is_dir():
        sys.path.insert(0, str(parent))
        PROJECT_ROOT = parent
        break

from module_web_scraping.pipeline import group_items_into_events, monitored_items_from_event_seed
from module_web_scraping.repository import load_sources

SOURCE_REGISTRY = PROJECT_ROOT / "data" / "source-registry-seed.csv"
EVENT_SEED = PROJECT_ROOT / "data" / "demo-regulatory-events-seed.csv"


def main() -> None:
    sources = load_sources(SOURCE_REGISTRY)
    items = monitored_items_from_event_seed(EVENT_SEED, sources)
    events = group_items_into_events(items)
    print(
        json.dumps(
            {
                "package": "validation_engine",
                "events_validated": len(events),
                "status_counts": {
                    status: sum(1 for event in events if event.event_status.value == status)
                    for status in sorted({event.event_status.value for event in events})
                },
                "sample": [event.to_dashboard_dict() for event in events[:2]],
            },
            default=str,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
