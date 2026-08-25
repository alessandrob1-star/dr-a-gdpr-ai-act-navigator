"""Run the local source monitoring MVP pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from .pipeline import group_items_into_events, monitored_items_from_event_seed
from .repository import load_sources

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
    items = monitored_items_from_event_seed(
        ROOT / "data" / "demo-regulatory-events-seed.csv", sources
    )
    events = group_items_into_events(items)
    dashboard_output = [event.to_dashboard_dict() for event in events]
    print(json.dumps(dashboard_output, indent=2, default=str))


if __name__ == "__main__":
    main()
