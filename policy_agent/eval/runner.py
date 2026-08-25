"""Runner that scores the guardrail golden set against the live Policy Agent.

Design goals:
  * Deterministic and LLM-free, so it runs in CI and produces a reproducible,
    falsifiable safety number for the README.
  * Uses the exact `PolicyAgent` entry points the dashboard chat endpoint uses,
    so the measured behaviour matches production behaviour.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from policy_agent import PolicyAgent

GOLDEN_SET_PATH = Path(__file__).resolve().parent / "golden_set.json"


@dataclass
class CaseResult:
    """Outcome of running a single golden-set case."""

    case_id: str
    channel: str
    language: str
    category: str
    expected: str
    actual: str
    passed: bool
    reason_code: str | None


@dataclass
class EvalReport:
    """Aggregated, JSON-serialisable evaluation report."""

    total: int
    passed: int
    failed: int
    adversarial_total: int
    adversarial_blocked: int
    benign_total: int
    benign_allowed: int
    by_category: dict[str, dict[str, int]]
    by_language: dict[str, dict[str, int]]
    failures: list[CaseResult] = field(default_factory=list)
    results: list[CaseResult] = field(default_factory=list)

    @property
    def block_rate(self) -> float:
        """Share of adversarial cases correctly blocked (recall of blocking)."""
        if self.adversarial_total == 0:
            return 0.0
        return self.adversarial_blocked / self.adversarial_total

    @property
    def false_block_rate(self) -> float:
        """Share of benign cases incorrectly blocked (lower is better)."""
        if self.benign_total == 0:
            return 0.0
        return (self.benign_total - self.benign_allowed) / self.benign_total

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "adversarial_total": self.adversarial_total,
            "adversarial_blocked": self.adversarial_blocked,
            "benign_total": self.benign_total,
            "benign_allowed": self.benign_allowed,
            "block_rate": round(self.block_rate, 4),
            "false_block_rate": round(self.false_block_rate, 4),
            "by_category": self.by_category,
            "by_language": self.by_language,
            "failures": [vars(result) for result in self.failures],
        }


def load_golden_set(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and lightly validate the committed golden-set cases."""
    source = path or GOLDEN_SET_PATH
    data = json.loads(source.read_text(encoding="utf-8"))
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"Golden set at {source} has no cases.")
    return cases


def _run_case(agent: PolicyAgent, case: Mapping[str, Any]) -> CaseResult:
    channel = str(case.get("channel", "input"))
    text = str(case.get("text", ""))
    context = case.get("context") if isinstance(case.get("context"), Mapping) else None
    expected = str(case.get("expected", "allow"))

    if channel == "output":
        result = agent.check_output(text, context)
    else:
        result = agent.check_input(text, context)

    actual = "block" if result.is_blocked else "allow"
    reason_code = result.violations[0].reason_code if result.violations else None
    return CaseResult(
        case_id=str(case.get("id", "")),
        channel=channel,
        language=str(case.get("language", "")),
        category=str(case.get("category", "")),
        expected=expected,
        actual=actual,
        passed=actual == expected,
        reason_code=reason_code,
    )


def evaluate_golden_set(path: Path | None = None) -> EvalReport:
    """Run every golden-set case and aggregate the results."""
    agent = PolicyAgent()
    cases = load_golden_set(path)
    results = [_run_case(agent, case) for case in cases]

    by_category: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    by_language: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    adversarial_total = adversarial_blocked = 0
    benign_total = benign_allowed = 0

    for result in results:
        by_category[result.category]["total"] += 1
        by_language[result.language]["total"] += 1
        if result.passed:
            by_category[result.category]["passed"] += 1
            by_language[result.language]["passed"] += 1
        if result.expected == "block":
            adversarial_total += 1
            if result.actual == "block":
                adversarial_blocked += 1
        else:
            benign_total += 1
            if result.actual == "allow":
                benign_allowed += 1

    passed = sum(1 for result in results if result.passed)
    return EvalReport(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        adversarial_total=adversarial_total,
        adversarial_blocked=adversarial_blocked,
        benign_total=benign_total,
        benign_allowed=benign_allowed,
        by_category=dict(by_category),
        by_language=dict(by_language),
        failures=[result for result in results if not result.passed],
        results=results,
    )


def render_markdown(report: EvalReport) -> str:
    """Render a human-readable Markdown summary of the report."""
    lines = [
        "# Dr A Guardrail Evaluation",
        "",
        "Deterministic evaluation of the Policy Agent guardrails that protect the "
        "Dr A assistant. No language model is involved, so these numbers are "
        "reproducible in CI.",
        "",
        f"- **Cases:** {report.total} ({report.passed} passed, {report.failed} failed)",
        f"- **Adversarial blocked:** {report.adversarial_blocked} / "
        f"{report.adversarial_total} ({report.block_rate:.0%})",
        f"- **Benign allowed:** {report.benign_allowed} / {report.benign_total} "
        f"(false-block rate {report.false_block_rate:.0%})",
        "",
        "## By category",
        "",
        "| Category | Passed | Total |",
        "| --- | --- | --- |",
    ]
    for category in sorted(report.by_category):
        stats = report.by_category[category]
        lines.append(f"| {category} | {stats['passed']} | {stats['total']} |")
    lines += ["", "## By language", "", "| Language | Passed | Total |", "| --- | --- | --- |"]
    for language in sorted(report.by_language):
        stats = report.by_language[language]
        lines.append(f"| {language} | {stats['passed']} | {stats['total']} |")
    if report.failures:
        lines += [
            "",
            "## Failures",
            "",
            "| Case | Channel | Expected | Actual |",
            "| --- | --- | --- | --- |",
        ]
        for failure in report.failures:
            lines.append(
                f"| {failure.case_id} | {failure.channel} | {failure.expected} | {failure.actual} |"
            )
    lines.append("")
    return "\n".join(lines)
