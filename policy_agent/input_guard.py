"""Input guard enforcing deterministic policy checks on user messages."""

from __future__ import annotations

from collections.abc import Mapping

from . import classifier, policies, prompts
from .models import GuardResult, Violation, ViolationCategory


class InputGuard:
    """Runs ordered rule checks and blocks on first violation."""

    def check(self, user_message: str, context: Mapping[str, object] | None = None) -> GuardResult:
        message = user_message or ""
        language = classifier.detect_language(message)
        conversation_history = []
        if isinstance(context, dict):
            raw_history = context.get("conversation_history")
            if isinstance(raw_history, list):
                conversation_history = [item for item in raw_history if isinstance(item, str)]

        if classifier.contains_keyword(
            message, policies.PROMPT_INJECTION_KEYWORDS
        ) or classifier.matches_pattern(message, policies.PROMPT_INJECTION_REGEX):
            return GuardResult.block(
                prompts.INPUT_BLOCK_MESSAGES[language]["prompt_injection"],
                Violation(
                    category=ViolationCategory.PROMPT_INJECTION,
                    reason_code="input.prompt_injection",
                    evidence=message,
                ),
            )

        if (
            classifier.contains_keyword(message, policies.REGULATORY_EVASION_KEYWORDS)
            or classifier.matches_pattern(message, policies.REGULATORY_EVASION_REGEX)
            or classifier.detects_compliance_washing_intent(message)
            or classifier.detects_pass_controls_anyway_intent(message)
            or classifier.detects_deferred_compliance_washing_followup(
                message, conversation_history
            )
        ):
            return GuardResult.block(
                prompts.INPUT_BLOCK_MESSAGES[language]["regulatory_evasion"],
                Violation(
                    category=ViolationCategory.REGULATORY_EVASION,
                    reason_code="input.regulatory_evasion",
                    evidence=message,
                ),
            )

        if classifier.contains_keyword(
            message, policies.FRAUD_KEYWORDS
        ) or classifier.matches_pattern(message, policies.FRAUD_REGEX):
            return GuardResult.block(
                prompts.INPUT_BLOCK_MESSAGES[language]["fraud"],
                Violation(
                    category=ViolationCategory.FRAUD,
                    reason_code="input.fraud",
                    evidence=message,
                ),
            )

        if classifier.matches_pattern(message, policies.LEGAL_ADVICE_BLOCK_REGEX):
            return GuardResult.block(
                prompts.INPUT_BLOCK_MESSAGES[language]["legal_advice"],
                Violation(
                    category=ViolationCategory.LEGAL_ADVICE,
                    reason_code="input.legal_advice",
                    evidence=message,
                ),
            )

        return GuardResult.allow()
