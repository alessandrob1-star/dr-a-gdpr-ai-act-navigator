"""Citation-grade legal references for scored regulatory events.

A compliance officer's first two questions about any risk line are "says who?"
and "is it current?". This module answers both by mapping each deterministic
topic label to the specific EU AI Act / GDPR article(s) it derives from, with a
stable EUR-Lex link and a last-verified date.

The registry is deterministic data (no network, no model) so it is auditable and
testable. It is intentionally decoupled from ``models`` to avoid import cycles.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

# Date on which the article mappings and EUR-Lex links below were last checked
# against the official consolidated texts. Bump this when the mappings are
# reviewed.
LAST_VERIFIED = "2026-07-13"

# Stable EUR-Lex CELEX identifiers for the two instruments.
AI_ACT_CELEX = "32024R1689"  # Regulation (EU) 2024/1689 (AI Act)
GDPR_CELEX = "32016R0679"  # Regulation (EU) 2016/679 (GDPR)

_AI_ACT = "EU AI Act"
_GDPR = "GDPR"


def _eurlex_url(celex: str, article_anchor: str | None = None) -> str:
    base = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}"
    return f"{base}#{article_anchor}" if article_anchor else base


@dataclass(frozen=True)
class LegalCitation:
    """A single, stable citation to a specific provision."""

    instrument: str
    celex: str
    articles: str
    title: str
    url: str
    last_verified: str = LAST_VERIFIED

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ai_act(articles: str, title: str, anchor: str) -> LegalCitation:
    return LegalCitation(
        instrument=_AI_ACT,
        celex=AI_ACT_CELEX,
        articles=articles,
        title=title,
        url=_eurlex_url(AI_ACT_CELEX, anchor),
    )


def _gdpr(articles: str, title: str, anchor: str) -> LegalCitation:
    return LegalCitation(
        instrument=_GDPR,
        celex=GDPR_CELEX,
        articles=articles,
        title=title,
        url=_eurlex_url(GDPR_CELEX, anchor),
    )


# Topic labels come from module_web_scraping.scoring.REGULATORY_IMPACT_BY_TOPIC.
# Each maps to the provision(s) that make that topic legally relevant.
TOPIC_LEGAL_CITATIONS: dict[str, list[LegalCitation]] = {
    "AI_ACT_PROHIBITED_PRACTICES": [
        _ai_act("Article 5", "Prohibited AI practices", "art_5"),
    ],
    "AI_ACT_HIGH_RISK": [
        _ai_act("Article 6", "Classification rules for high-risk AI systems", "art_6"),
        _ai_act("Annex III", "High-risk AI systems referred to in Article 6(2)", "anx_III"),
    ],
    "AI_ACT_GPAI": [
        _ai_act(
            "Articles 51-55",
            "General-purpose AI models: classification and obligations",
            "art_51",
        ),
    ],
    "AI_ACT_TRANSPARENCY": [
        _ai_act(
            "Article 50",
            "Transparency obligations for providers and deployers of certain AI systems",
            "art_50",
        ),
    ],
    "AI_ACT_GENERAL": [
        _ai_act("Article 1", "Subject matter of the AI Act", "art_1"),
    ],
    "GDPR_DATA_BREACH": [
        _gdpr(
            "Article 33",
            "Notification of a personal data breach to the supervisory authority",
            "art_33",
        ),
        _gdpr(
            "Article 34", "Communication of a personal data breach to the data subject", "art_34"
        ),
    ],
    "GDPR_DPIA": [
        _gdpr("Article 35", "Data protection impact assessment", "art_35"),
    ],
    "GDPR_INTERNATIONAL_TRANSFERS": [
        _gdpr("Articles 44-49", "Transfers of personal data to third countries", "art_44"),
    ],
    "GDPR_AUTOMATED_DECISION_MAKING": [
        _gdpr(
            "Article 22",
            "Automated individual decision-making, including profiling",
            "art_22",
        ),
    ],
    "GDPR_GENERAL": [
        _gdpr("Article 5", "Principles relating to processing of personal data", "art_5"),
    ],
}


def citations_for_topics(topic_labels: list[str]) -> list[dict[str, Any]]:
    """Return de-duplicated, order-preserving citations for the given topics.

    Unknown labels are skipped so a new topic never fabricates a citation.
    """
    seen: set[tuple[str, str]] = set()
    citations: list[dict[str, Any]] = []
    for label in topic_labels:
        for citation in TOPIC_LEGAL_CITATIONS.get(label, ()):
            key = (citation.celex, citation.articles)
            if key in seen:
                continue
            seen.add(key)
            citations.append(citation.to_dict())
    return citations
