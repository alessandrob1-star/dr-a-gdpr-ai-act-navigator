"""Output guard for deterministic checks on model answers."""

from __future__ import annotations

import re
from collections.abc import Mapping

from . import classifier, policies, prompts
from .models import GuardResult, Violation, ViolationCategory

NEGATED_UNSAFE_PREFIX = re.compile(
    r"(?:do not|don't|never|cannot|can't|must not|non posso|non bisogna|"
    r"non si deve|non devi|mai)\b[^.;:!?]{0,35}$",
    re.IGNORECASE,
)


def _contains_unsafe_instruction(reply: str) -> bool:
    """Match unsafe instructions without blocking a short refusal or warning."""
    for pattern in policies.OUTPUT_UNSAFE_REGEX:
        for match in pattern.finditer(reply):
            prefix = reply[max(0, match.start() - 50) : match.start()]
            if not NEGATED_UNSAFE_PREFIX.search(prefix):
                return True
    return False


class OutputGuard:
    """Validates model output and blocks unsafe responses."""

    def check(self, model_reply: str, context: Mapping[str, object] | None = None) -> GuardResult:
        reply = model_reply or ""
        block_message = prompts.OUTPUT_BLOCK_MESSAGES[classifier.detect_language(reply)]

        if _contains_unsafe_instruction(reply):
            return GuardResult.block(
                block_message,
                Violation(
                    category=ViolationCategory.UNSAFE_OUTPUT,
                    reason_code="output.unsafe_instruction",
                    evidence=reply,
                ),
            )

        return GuardResult.allow(reply=reply)
