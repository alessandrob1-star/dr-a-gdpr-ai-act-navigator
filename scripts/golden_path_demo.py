#!/usr/bin/env python3
"""One-command demo: seed a sample SME assessment, then launch the dashboard.

Judges have minutes, not hours. This script removes the "empty dashboard"
first-run friction: it loads a bundled questionnaire, runs the deterministic
evaluation pipeline (no language model required), saves the result as a profile
snapshot, and then starts the dashboard so a reviewer lands on a populated risk
dashboard immediately.

Usage:
    python scripts/golden_path_demo.py              # seed, then launch the server
    python scripts/golden_path_demo.py --seed-only  # seed only (used by CI/tests)

The Dr A chat assistant still needs `OPENAI_API_KEY`, but the
seeded assessment, scores, warnings, and matched regulatory events render
without it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "module_company_profile" / "dashboard"
DEFAULT_SAMPLE = (
    ROOT / "module_company_profile" / "memory_agent" / "sample_questionnaire_answers.json"
)

# dashboard_server imports sibling modules (profile_store, report_exporter) by
# bare name, mirroring how it is launched. The dashboard directory must be on
# sys.path before importing it.
sys.path.insert(0, str(DASHBOARD_DIR))

import dashboard_server  # noqa: E402
from profile_store import save_profile_snapshot  # noqa: E402


def seed_sample_assessment(sample_path: Path = DEFAULT_SAMPLE) -> dict:
    """Run the deterministic evaluation for a sample company and persist it."""
    if not sample_path.exists():
        raise SystemExit(f"Sample questionnaire not found: {sample_path}")
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    evaluation = dashboard_server.evaluate_payload(payload)
    return save_profile_snapshot(dashboard_server.PROFILE_HISTORY_DIR, evaluation)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Seed a sample assessment and launch the dashboard"
    )
    parser.add_argument(
        "--sample",
        type=Path,
        default=DEFAULT_SAMPLE,
        help="Questionnaire JSON to seed (defaults to the bundled Acme HR AI sample)",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Seed the assessment and exit without starting the server.",
    )
    args = parser.parse_args(argv)

    meta = seed_sample_assessment(args.sample)
    print(
        f"Seeded assessment: {meta.get('company_name')} "
        f"(score {meta.get('score')}) -> snapshot {meta.get('id')}"
    )

    if args.seed_only:
        print("Seed-only mode: skipping server launch.")
        return 0

    print("Launching dashboard. Open http://localhost:8771 and pick the saved assessment.")
    return dashboard_server.main()


if __name__ == "__main__":
    raise SystemExit(main())
