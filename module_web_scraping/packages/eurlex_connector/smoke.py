"""Smoke run for the EUR-Lex connector package container."""

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

from module_web_scraping.eurlex_webservice import (
    EurLexCredentials,
    build_query_envelope,
    celex_query,
    keyword_query,
)


def main() -> None:
    credentials = EurLexCredentials(username="demo-user", password="demo-password")
    celex_envelope = build_query_envelope(
        credentials=credentials,
        expert_query=celex_query("32024R1689"),
        page=1,
        page_size=5,
        search_language="en",
    )
    keyword_envelope = build_query_envelope(
        credentials=credentials,
        expert_query=keyword_query("artificial intelligence", "high-risk"),
        page=1,
        page_size=5,
        search_language="en",
    )
    print(
        json.dumps(
            {
                "package": "eurlex_connector",
                "celex_query_ready": "32024R1689" in celex_envelope,
                "keyword_query_ready": "artificial intelligence" in keyword_envelope,
                "note": "This smoke run builds envelopes only and does not call EUR-Lex.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
