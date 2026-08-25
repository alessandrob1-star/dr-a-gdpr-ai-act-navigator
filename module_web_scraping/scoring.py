"""Explainable MVP scoring rules for regulatory events."""

from __future__ import annotations

from datetime import date

from .models import AuthorityLevel, Priority, ValidationStatus

RELIABILITY_BY_AUTHORITY = {
    AuthorityLevel.OFFICIAL_BINDING: 95,
    AuthorityLevel.OFFICIAL_GUIDANCE: 75,
    AuthorityLevel.OFFICIAL_DRAFT: 65,
    AuthorityLevel.TRUSTED_WARNING: 35,
    AuthorityLevel.LOW_PRIORITY: 15,
}


REGULATORY_IMPACT_BY_TOPIC = {
    "AI_ACT_PROHIBITED_PRACTICES": 95,
    "AI_ACT_HIGH_RISK": 85,
    "AI_ACT_GPAI": 80,
    "GDPR_DATA_BREACH": 80,
    "GDPR_DPIA": 75,
    "GDPR_INTERNATIONAL_TRANSFERS": 75,
    "GDPR_AUTOMATED_DECISION_MAKING": 75,
    "AI_ACT_TRANSPARENCY": 65,
    "GDPR_GENERAL": 55,
    "AI_ACT_GENERAL": 55,
}


def status_from_authority(authority: AuthorityLevel) -> ValidationStatus:
    if authority == AuthorityLevel.OFFICIAL_BINDING:
        return ValidationStatus.OFFICIALLY_PUBLISHED
    if authority in {AuthorityLevel.OFFICIAL_GUIDANCE, AuthorityLevel.OFFICIAL_DRAFT}:
        return ValidationStatus.OFFICIAL_DRAFT
    return ValidationStatus.UNCONFIRMED_NEWS


def reliability_from_authorities(authorities: list[AuthorityLevel]) -> int:
    if not authorities:
        return 0
    base = max(RELIABILITY_BY_AUTHORITY.get(authority, 15) for authority in authorities)
    trusted_count = sum(
        1 for authority in authorities if authority == AuthorityLevel.TRUSTED_WARNING
    )
    if base < 55 and trusted_count > 1:
        base = min(45, base + (trusted_count - 1) * 5)
    return base


def regulatory_impact(topic_labels: list[str]) -> int:
    if not topic_labels:
        return 25
    return max(REGULATORY_IMPACT_BY_TOPIC.get(label, 50) for label in topic_labels)


def urgency_score(
    status: ValidationStatus,
    effective_date: date | None = None,
    compliance_deadline: date | None = None,
    today: date | None = None,
) -> int:
    today = today or date.today()
    target = compliance_deadline or effective_date
    if target is None:
        if status == ValidationStatus.OFFICIALLY_PUBLISHED:
            return 50
        if status == ValidationStatus.OFFICIAL_DRAFT:
            return 30
        return 20

    days = (target - today).days
    if days <= 0:
        return 90
    if days <= 30:
        return 85
    if days <= 90:
        return 70
    if days <= 183:
        return 55
    if days <= 365:
        return 40
    return 25


def priority_from_scores(
    reliability_score: int,
    urgency_score_value: int,
    regulatory_impact_score: int,
    business_impact_score: int | None,
) -> Priority:
    business = business_impact_score if business_impact_score is not None else 50
    weighted = round(
        (reliability_score + urgency_score_value + regulatory_impact_score + business) / 4
    )
    if weighted >= 75:
        return Priority.CRITICAL
    if weighted >= 50:
        return Priority.HIGH
    if weighted >= 25:
        return Priority.MEDIUM
    return Priority.LOW


def recommended_attention(priority: Priority) -> str:
    return {
        Priority.LOW: "Monitor",
        Priority.MEDIUM: "Review",
        Priority.HIGH: "Action recommended",
        Priority.CRITICAL: "Immediate attention",
    }[priority]
