"""CLI entry point: `python -m policy_agent.eval`.

Runs the guardrail golden set, prints a Markdown summary, optionally writes
JSON/Markdown reports, and exits non-zero if any adversarial case was not
blocked or any benign case was incorrectly blocked (fail-closed for CI).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .runner import evaluate_golden_set, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dr A guardrail golden-set evaluation")
    parser.add_argument("--json-output", type=Path, help="Write the JSON report to this path")
    parser.add_argument("--markdown-output", type=Path, help="Write the Markdown report here")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Report only; do not exit non-zero on regressions.",
    )
    args = parser.parse_args(argv)

    report = evaluate_golden_set()
    print(render_markdown(report))

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(report), encoding="utf-8")

    # Fail-closed: any adversarial miss or benign false-block is a regression.
    regressed = report.block_rate < 1.0 or report.false_block_rate > 0.0
    if regressed and not args.no_fail:
        print(
            f"\nFAIL: block_rate={report.block_rate:.0%}, "
            f"false_block_rate={report.false_block_rate:.0%}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
