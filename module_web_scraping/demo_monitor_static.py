"""Run source monitoring against a static HTML sample.

This gives a deterministic demo without relying on live network access.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .repository import load_sources
from .source_monitor import deduplicate_items, monitor_source_from_html

ROOT = Path(__file__).resolve().parents[1]

STATIC_HTML = """
<html>
  <head><title>Example regulatory source</title></head>
  <body>
    <a href="/ai-act/high-risk-guidance">Draft high-risk AI classification guidance under the AI Act</a>
    <a href="/privacy/dpia">EDPB guidance on DPIA and high risk processing under GDPR Article 35</a>
    <a href="/sports">Unrelated sports update</a>
    <a href="/ai-act/high-risk-guidance">Draft high-risk AI classification guidance under the AI Act</a>
  </body>
</html>
"""


def main() -> None:
    sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
    source = next(src for src in sources if src.name == "European Commission AI Office")
    items = deduplicate_items(monitor_source_from_html(source, STATIC_HTML))
    print(json.dumps([asdict(item) for item in items], indent=2, default=str))


if __name__ == "__main__":
    main()
