"""Local source monitoring vertical slice.

This pipeline deliberately builds reproducible regulatory-event examples from
curated seed records with explicit provenance. The dashboard's live update
collector is a separate path and is labelled separately in the interface.
"""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime
from pathlib import Path

from .models import (
    AuthorityLevel,
    CollectionStatus,
    ItemType,
    MonitoredItem,
    RegulatoryEvent,
    Source,
    SourceEvidence,
    ValidationStatus,
)
from .scoring import (
    priority_from_scores,
    recommended_attention,
    regulatory_impact,
    reliability_from_authorities,
    status_from_authority,
    urgency_score,
)
from .topic_detection import detect_regulation_area, detect_topic_labels, normalize_text


def item_type_from_source(source: Source, status_hint: str | None = None) -> ItemType:
    if source.authority_level == AuthorityLevel.OFFICIAL_BINDING:
        return ItemType.OFFICIAL_PUBLICATION
    if status_hint == ValidationStatus.OFFICIAL_DRAFT.value:
        return ItemType.OFFICIAL_DRAFT
    if source.authority_level == AuthorityLevel.OFFICIAL_GUIDANCE:
        return ItemType.OFFICIAL_GUIDANCE
    if source.source_type == "expert_source":
        return ItemType.EXPERT_COMMENTARY
    return ItemType.NEWS_ARTICLE


def source_for_seed_row(sources: list[Source], row: dict[str, str]) -> Source:
    """Resolve explicit seed provenance; never infer a source from desired status."""
    source_name = str(row.get("source_name") or "").strip()
    if not source_name:
        raise ValueError("Regulatory event seed row is missing source_name.")
    try:
        return next(source for source in sources if source.name == source_name)
    except StopIteration as exc:
        raise ValueError(f"Unknown regulatory event source: {source_name}") from exc


def monitored_items_from_event_seed(
    event_seed_path: str | Path, sources: list[Source]
) -> list[MonitoredItem]:
    """Convert demo regulatory event rows into monitored items.

    The seed file represents dashboard-level examples. For the local MVP we
    convert each row into one traceable monitored item so topic detection,
    validation status, and dashboard export can be tested end-to-end.
    """
    items: list[MonitoredItem] = []
    now = datetime.now()
    with Path(event_seed_path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"event_title", "summary", "regulation_area", "source_name"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Regulatory event seed {Path(event_seed_path)} is missing required "
                f"column(s): {', '.join(sorted(missing))}."
            )
        for index, row in enumerate(reader, start=1):
            source = source_for_seed_row(sources, row)
            topic_labels = detect_topic_labels(row["event_title"], row["summary"])
            regulation_area = detect_regulation_area(topic_labels)
            if regulation_area == "OUT_OF_SCOPE":
                regulation_area = row["regulation_area"]
            title = row["event_title"]
            raw_hash = hashlib.sha256(f"{title}|{row['summary']}|{source.url}".encode()).hexdigest()
            items.append(
                MonitoredItem(
                    id=index,
                    source_id=source.id,
                    source_name=source.name,
                    title=title,
                    url=str(row.get("source_url") or "").strip() or source.url,
                    retrieved_at=now,
                    item_type=item_type_from_source(source),
                    source_authority_level=source.authority_level,
                    regulation_area=regulation_area,
                    topic_labels=topic_labels,
                    collection_status=CollectionStatus.NEW
                    if topic_labels
                    else CollectionStatus.NEEDS_REVIEW,
                    summary=row["summary"],
                    raw_text_hash=raw_hash,
                    normalized_title=normalize_text(title),
                )
            )
    return items


def group_items_into_events(items: list[MonitoredItem]) -> list[RegulatoryEvent]:
    """Create one event per normalized title for the MVP.

    Later versions can replace this with the scoring algorithm from
    event-grouping-deduplication-spec.md.
    """
    events: list[RegulatoryEvent] = []
    grouped: dict[str, list[MonitoredItem]] = {}
    for item in items:
        if item.collection_status == CollectionStatus.IGNORED_OUT_OF_SCOPE:
            continue
        grouped.setdefault(item.normalized_title, []).append(item)

    for event_id, group in enumerate(grouped.values(), start=1):
        authorities = [item.source_authority_level for item in group]
        strongest_status = max(
            (status_from_authority(authority) for authority in authorities),
            key=lambda status: {
                ValidationStatus.UNCONFIRMED_NEWS: 1,
                ValidationStatus.OFFICIAL_DRAFT: 2,
                ValidationStatus.OFFICIALLY_PUBLISHED: 3,
                ValidationStatus.ARCHIVED: 0,
            }[status],
        )
        labels = sorted({label for item in group for label in item.topic_labels})
        reliability = reliability_from_authorities(authorities)
        urgency = urgency_score(strongest_status)
        impact = regulatory_impact(labels)
        priority = priority_from_scores(reliability, urgency, impact, None)
        first = min(item.retrieved_at for item in group)
        last = max(item.retrieved_at for item in group)
        evidence = [
            SourceEvidence(
                source_name=item.source_name,
                source_type=item.item_type.value,
                authority_level=item.source_authority_level,
                title=item.title,
                url=item.url,
                relationship_type="official_confirmation"
                if item.source_authority_level
                in {
                    AuthorityLevel.OFFICIAL_BINDING,
                    AuthorityLevel.OFFICIAL_GUIDANCE,
                    AuthorityLevel.OFFICIAL_DRAFT,
                }
                else "initial_signal",
                published_date=item.published_date,
            )
            for item in group
        ]
        events.append(
            RegulatoryEvent(
                event_id=event_id,
                event_title=group[0].title,
                regulation_area=group[0].regulation_area,
                topic_labels=labels,
                event_status=strongest_status,
                summary=group[0].summary,
                first_detected_at=first,
                last_updated_at=last,
                reliability_score=reliability,
                urgency_score=urgency,
                regulatory_impact_score=impact,
                business_impact_score=None,
                overall_priority=priority,
                recommended_attention=recommended_attention(priority),
                evidence=evidence,
                validation_explanation=validation_explanation(strongest_status),
                scoring_explanation=(
                    "Scores are based on source authority, validation status, "
                    "topic severity, and missing company-specific impact."
                ),
            )
        )
    return events


def validation_explanation(status: ValidationStatus) -> str:
    if status == ValidationStatus.OFFICIALLY_PUBLISHED:
        return "The event is supported by official binding evidence or an authoritative official legal source."
    if status == ValidationStatus.OFFICIAL_DRAFT:
        return "The event is supported by official guidance, draft, consultation, or institutional evidence."
    if status == ValidationStatus.UNCONFIRMED_NEWS:
        return "The event is currently supported only by trusted warning or expert sources."
    return "The event is archived."
