"""Run the memory agent on three distinct demo companies."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from module_company_profile.memory_agent.company_memory_agent import run  # noqa: E402

ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT


def main() -> None:
    demo_dir = ROOT / "demo_profiles"
    output_root = ROOT / "demo_outputs"
    regulatory_events = REPO_ROOT / "storage" / "web_scraping_outputs" / "regulatory_events.json"
    article_feed = REPO_ROOT / "storage" / "web_scraping_outputs" / "articles_and_news_feed.json"

    for profile in sorted(demo_dir.glob("*.json")):
        out_dir = output_root / profile.stem
        run(profile, out_dir, regulatory_events, article_feed)
        print(f"Wrote {out_dir}")


if __name__ == "__main__":
    main()
