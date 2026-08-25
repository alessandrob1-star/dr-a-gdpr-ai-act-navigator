"""Shared models for deterministic policy checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(str, Enum):
    """Policy outcome for a guard check."""

    ALLOW = "allow"
    BLOCK = "block"


class ViolationCategory(str, Enum):
    """High-level policy violation categories."""

    PROMPT_INJECTION = "prompt_injection"
    REGULATORY_EVASION = "regulatory_evasion"
    FRAUD = "fraud"
    LEGAL_ADVICE = "legal_advice"
    OFF_TOPIC = "off_topic"
    UNSAFE_OUTPUT = "unsafe_output"
    UNSUPPORTED_CLAIM = "unsupported_claim"


@dataclass(frozen=True)
class Violation:
    """Single deterministic violation record."""

    category: ViolationCategory
    reason_code: str
    evidence: str


@dataclass
class GuardResult:
    """Normalized return object for input and output guards."""

    decision: Decision
    message: str
    violations: list[Violation] = field(default_factory=list)
    reply: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_blocked(self) -> bool:
        return self.decision == Decision.BLOCK

    @classmethod
    def allow(cls, reply: str | None = None, metadata: dict[str, Any] | None = None) -> GuardResult:
        return cls(decision=Decision.ALLOW, message="", reply=reply, metadata=metadata or {})

    @classmethod
    def block(
        cls,
        message: str,
        violation: Violation,
        metadata: dict[str, Any] | None = None,
    ) -> GuardResult:
        return cls(
            decision=Decision.BLOCK,
            message=message,
            violations=[violation],
            metadata=metadata or {},
        )
