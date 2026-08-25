"""Main Policy Agent orchestrating input and output checks."""

from __future__ import annotations

from collections.abc import Mapping

from .input_guard import InputGuard
from .models import GuardResult
from .output_guard import OutputGuard


class PolicyAgent:
    """Single entry point used by the dashboard chat endpoint."""

    def __init__(self) -> None:
        self._input_guard = InputGuard()
        self._output_guard = OutputGuard()

    def check_input(
        self, user_message: str, context: Mapping[str, object] | None = None
    ) -> GuardResult:
        return self._input_guard.check(user_message=user_message, context=context)

    def check_output(
        self, model_reply: str, context: Mapping[str, object] | None = None
    ) -> GuardResult:
        return self._output_guard.check(model_reply=model_reply, context=context)
