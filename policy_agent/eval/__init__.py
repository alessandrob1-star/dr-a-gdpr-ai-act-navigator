"""Deterministic guardrail evaluation harness for the Dr A Policy Agent.

The harness runs a committed, labelled golden set of adversarial and benign
cases through the same `PolicyAgent` the dashboard uses and reports measurable,
falsifiable safety metrics (block rate on adversarial cases, false-block rate on
benign cases). It requires no language model, so it runs in CI.
"""

from .runner import EvalReport, evaluate_golden_set, load_golden_set

__all__ = ["EvalReport", "evaluate_golden_set", "load_golden_set"]
