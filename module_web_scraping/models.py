"""Data models for the source monitoring MVP.

The module intentionally uses dataclasses and standard-library types so the
first MVP can run locally without framework dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from .citations import citations_for_topics


class AuthorityLevel(StrEnum):
    OFFICIAL_BINDING = "official_binding"
    OFFICIAL_GUIDANCE = "official_guidance"
    OFFICIAL_DRAFT = "official_draft"
    TRUSTED_WARNING = "trusted_warning"
    LOW_PRIORITY = "low_priority"


class ItemType(StrEnum):
    OFFICIAL_PUBLICATION = "official_publication"
    OFFICIAL_GUIDANCE = "official_guidance"
    OFFICIAL_DRAFT = "official_draft"
    PUBLIC_CONSULTATION = "public_consultation"
    NEWS_ARTICLE = "news_article"
    EXPERT_COMMENTARY = "expert_commentary"
    RSS_ENTRY = "rss_entry"
    DOCUMENT_REFERENCE = "document_reference"


class CollectionStatus(StrEnum):
    NEW = "new"
    ALREADY_SEEN = "already_seen"
    FAILED_FETCH = "failed_fetch"
    NEEDS_REVIEW = "needs_review"
    IGNORED_OUT_OF_SCOPE = "ignored_out_of_scope"


class ValidationStatus(StrEnum):
    UNCONFIRMED_NEWS = "C_UNCONFIRMED_NEWS"
    OFFICIAL_DRAFT = "B_OFFICIAL_DRAFT"
    OFFICIALLY_PUBLISHED = "A_OFFICIALLY_PUBLISHED"
    ARCHIVED = "ARCHIVED"


class Priority(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass(frozen=True)
class Source:
    id: int
    name: str
    url: str
    source_type: str
    authority_level: AuthorityLevel
    topic_area: str
    access_method: str
    priority: int
    active: bool
    notes: str = ""


@dataclass
class MonitoredItem:
    id: int
    source_id: int
    source_name: str
    title: str
    url: str
    retrieved_at: datetime
    item_type: ItemType
    source_authority_level: AuthorityLevel
    regulation_area: str
    topic_labels: list[str]
    collection_status: CollectionStatus
    published_date: date | None = None
    summary: str = ""
    raw_text_hash: str = ""
    normalized_title: str = ""
    detected_legal_references: list[str] = field(default_factory=list)
    detected_institutions: list[str] = field(default_factory=list)


@dataclass
class SourceEvidence:
    source_name: str
    source_type: str
    authority_level: AuthorityLevel
    title: str
    url: str
    relationship_type: str
    published_date: date | None = None


@dataclass
class RegulatoryEvent:
    event_id: int
    event_title: str
    regulation_area: str
    topic_labels: list[str]
    event_status: ValidationStatus
    summary: str
    first_detected_at: datetime
    last_updated_at: datetime
    reliability_score: int
    urgency_score: int
    regulatory_impact_score: int
    business_impact_score: int | None
    overall_priority: Priority
    recommended_attention: str
    evidence: list[SourceEvidence] = field(default_factory=list)
    effective_date: date | None = None
    compliance_deadline: date | None = None
    validation_explanation: str = ""
    scoring_explanation: str = ""

    def to_dashboard_dict(self) -> dict[str, Any]:
        """Return the compact object expected by the dashboard contract."""
        data = asdict(self)
        data["event_status"] = self.event_status.value
        data["overall_priority"] = self.overall_priority.value
        data["has_official_evidence"] = any(
            ev.authority_level
            in {
                AuthorityLevel.OFFICIAL_BINDING,
                AuthorityLevel.OFFICIAL_GUIDANCE,
                AuthorityLevel.OFFICIAL_DRAFT,
            }
            for ev in self.evidence
        )
        data["has_warning_sources"] = any(
            ev.authority_level == AuthorityLevel.TRUSTED_WARNING for ev in self.evidence
        )
        data["evidence_count"] = len(self.evidence)
        official = [
            ev.url
            for ev in self.evidence
            if ev.authority_level
            in {
                AuthorityLevel.OFFICIAL_BINDING,
                AuthorityLevel.OFFICIAL_GUIDANCE,
                AuthorityLevel.OFFICIAL_DRAFT,
            }
        ]
        data["primary_official_source_url"] = official[0] if official else None
        data["legal_citations"] = citations_for_topics(self.topic_labels)
        return data
