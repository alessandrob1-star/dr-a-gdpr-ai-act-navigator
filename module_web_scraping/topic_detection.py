"""Deterministic topic detection for GDPR and EU AI Act monitoring."""

from __future__ import annotations

import re

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "AI_ACT_GENERAL": (
        "ai act",
        "artificial intelligence act",
        "regulation eu 2024 1689",
        "eu ai regulation",
        "ai office",
    ),
    "AI_ACT_PROHIBITED_PRACTICES": (
        "prohibited ai practices",
        "unacceptable risk",
        "banned ai systems",
        "social scoring",
        "manipulative ai",
        "biometric categorisation",
        "emotion recognition",
        "real time remote biometric identification",
    ),
    "AI_ACT_HIGH_RISK": (
        "high risk ai",
        "high-risk ai",
        "annex iii",
        "annex i",
        "conformity assessment",
        "risk management system",
        "human oversight",
        "technical documentation",
        "quality management system",
        "post market monitoring",
    ),
    "AI_ACT_TRANSPARENCY": (
        "transparency obligations",
        "article 50",
        "ai generated content",
        "chatbot disclosure",
        "deep fake disclosure",
        "synthetic content",
        "users must be informed",
        "deployer transparency",
    ),
    "AI_ACT_GPAI": (
        "general purpose ai",
        "general-purpose ai",
        "gpai",
        "systemic risk",
        "model provider",
        "code of practice",
        "model documentation",
        "copyright policy",
        "safety and security chapter",
    ),
    "GDPR_GENERAL": (
        "gdpr",
        "general data protection regulation",
        "regulation eu 2016 679",
        "personal data",
        "data protection",
        "lawful basis",
        "consent",
        "legitimate interest",
    ),
    "GDPR_DPIA": (
        "dpia",
        "data protection impact assessment",
        "high risk processing",
        "article 35",
        "likely to result in a high risk",
        "risk to rights and freedoms",
    ),
    "GDPR_DATA_BREACH": (
        "personal data breach",
        "data breach notification",
        "article 33",
        "article 34",
        "supervisory authority notification",
        "breach communication to data subjects",
    ),
    "GDPR_INTERNATIONAL_TRANSFERS": (
        "international transfers",
        "third country transfer",
        "standard contractual clauses",
        "sccs",
        "supplementary measures",
        "adequacy decision",
        "transfer impact assessment",
    ),
    "GDPR_AUTOMATED_DECISION_MAKING": (
        "automated decision making",
        "automated decision-making",
        "profiling",
        "article 22",
        "solely automated processing",
        "meaningful information about logic",
        "significant effects",
    ),
    "GDPR_CONTROLLER_PROCESSOR": (
        "controller",
        "processor",
        "joint controller",
        "processing agreement",
        "article 28",
        "controller processor relationship",
    ),
    "GDPR_DATA_SUBJECT_RIGHTS": (
        "right of access",
        "data subject rights",
        "right to erasure",
        "right to rectification",
        "right to object",
        "right to portability",
        "access request",
    ),
}


def normalize_text(value: str) -> str:
    value = value.lower()
    value = value.replace("general-purpose", "general purpose")
    value = value.replace("high-risk", "high risk")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def detect_topic_labels(title: str, summary: str = "", raw_text: str = "") -> list[str]:
    haystack = normalize_text(" ".join([title, summary, raw_text]))
    labels = [
        label
        for label, keywords in TOPIC_KEYWORDS.items()
        if any(normalize_text(keyword) in haystack for keyword in keywords)
    ]
    return labels


def detect_regulation_area(topic_labels: list[str]) -> str:
    has_ai_act = any(label.startswith("AI_ACT") for label in topic_labels)
    has_gdpr = any(label.startswith("GDPR") for label in topic_labels)
    if has_ai_act and has_gdpr:
        return "GDPR_AI_ACT_INTERPLAY"
    if has_ai_act:
        return "AI_ACT"
    if has_gdpr:
        return "GDPR"
    return "OUT_OF_SCOPE"
