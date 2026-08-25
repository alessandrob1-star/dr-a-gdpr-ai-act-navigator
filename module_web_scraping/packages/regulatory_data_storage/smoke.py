"""Smoke run for the regulatory data storage package container."""

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
from module_web_scraping.storage import (
    read_jsonl,
    save_monitored_items,
    save_regulatory_events,
)

SOURCE_REGISTRY = PROJECT_ROOT / "data" / "source-registry-seed.csv"
EVENT_SEED = PROJECT_ROOT / "data" / "demo-regulatory-events-seed.csv"
STORAGE = PROJECT_ROOT / "storage"


def main() -> None:
    sources = load_sources(SOURCE_REGISTRY)
    items = monitored_items_from_event_seed(EVENT_SEED, sources)
    events = group_items_into_events(items)
    item_store = STORAGE / "monitored_items.jsonl"
    event_store = STORAGE / "regulatory_events.jsonl"
    save_monitored_items(item_store, items[:3])
    save_regulatory_events(event_store, events[:3])
    print(
        json.dumps(
            {
                "package": "regulatory_data_storage",
                "item_store": str(item_store),
                "event_store": str(event_store),
                "items_written_this_run": 3,
                "events_written_this_run": 3,
                "stored_item_rows": len(read_jsonl(item_store)),
                "stored_event_rows": len(read_jsonl(event_store)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
