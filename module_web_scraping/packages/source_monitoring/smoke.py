"""Smoke run for the source monitoring package container."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
for parent in Path(__file__).resolve().parents:
    if (parent / "module_web_scraping").is_dir():
        sys.path.insert(0, str(parent))
        PROJECT_ROOT = parent
        break

from module_web_scraping.demo_monitor_static import STATIC_HTML
from module_web_scraping.repository import load_sources
from module_web_scraping.source_monitor import deduplicate_items, monitor_source_from_html

SOURCE_REGISTRY = PROJECT_ROOT / "data" / "source-registry-seed.csv"


def main() -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next(source for source in sources if source.name == "European Commission AI Office")
    items = deduplicate_items(monitor_source_from_html(source, STATIC_HTML, limit=10))
    print(
        json.dumps(
            {
                "package": "source_monitoring",
                "source": source.name,
                "items_found": len(items),
                "sample_items": [asdict(item) for item in items[:2]],
            },
            default=str,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
