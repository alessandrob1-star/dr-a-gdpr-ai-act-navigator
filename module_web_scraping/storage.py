"""JSONL storage for monitored items and regulatory events.

This is a lightweight MVP persistence layer. It keeps records inspectable and
can later be replaced by SQLite using the same model boundaries.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .models import (
    AuthorityLevel,
    CollectionStatus,
    ItemType,
    MonitoredItem,
    Priority,
    RegulatoryEvent,
    SourceEvidence,
    ValidationStatus,
)


def encode_value(value: Any) -> Any:
    if isinstance(value, datetime | date):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    return value


def append_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, default=encode_value, ensure_ascii=True))
            file.write("\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def save_monitored_items(path: str | Path, items: list[MonitoredItem]) -> None:
    append_jsonl(path, (asdict(item) for item in items))


def save_regulatory_events(path: str | Path, events: list[RegulatoryEvent]) -> None:
    append_jsonl(path, (event.to_dashboard_dict() for event in events))


def load_monitored_items(path: str | Path) -> list[MonitoredItem]:
    return [monitored_item_from_dict(record) for record in read_jsonl(path)]


def monitored_item_from_dict(record: dict[str, Any]) -> MonitoredItem:
    return MonitoredItem(
        id=int(record["id"]),
        source_id=int(record["source_id"]),
        source_name=record["source_name"],
        title=record["title"],
        url=record["url"],
        retrieved_at=datetime.fromisoformat(record["retrieved_at"]),
        item_type=ItemType(record["item_type"]),
        source_authority_level=AuthorityLevel(record["source_authority_level"]),
        regulation_area=record["regulation_area"],
        topic_labels=list(record["topic_labels"]),
        collection_status=CollectionStatus(record["collection_status"]),
        published_date=date.fromisoformat(record["published_date"])
        if record.get("published_date")
        else None,
        summary=record.get("summary", ""),
        raw_text_hash=record.get("raw_text_hash", ""),
        normalized_title=record.get("normalized_title", ""),
        detected_legal_references=list(record.get("detected_legal_references", [])),
        detected_institutions=list(record.get("detected_institutions", [])),
    )


def regulatory_event_from_dict(record: dict[str, Any]) -> RegulatoryEvent:
    evidence = [
        SourceEvidence(
            source_name=item["source_name"],
            source_type=item["source_type"],
            authority_level=AuthorityLevel(item["authority_level"]),
            title=item["title"],
            url=item["url"],
            relationship_type=item["relationship_type"],
            published_date=date.fromisoformat(item["published_date"])
            if item.get("published_date")
            else None,
        )
        for item in record.get("evidence", [])
    ]
    return RegulatoryEvent(
        event_id=int(record["event_id"]),
        event_title=record["event_title"],
        regulation_area=record["regulation_area"],
        topic_labels=list(record["topic_labels"]),
        event_status=ValidationStatus(record["event_status"]),
        summary=record.get("summary", ""),
        first_detected_at=datetime.fromisoformat(record["first_detected_at"]),
        last_updated_at=datetime.fromisoformat(record["last_updated_at"]),
        reliability_score=int(record["reliability_score"]),
        urgency_score=int(record["urgency_score"]),
        regulatory_impact_score=int(record["regulatory_impact_score"]),
        business_impact_score=record.get("business_impact_score"),
        overall_priority=Priority(record["overall_priority"]),
        recommended_attention=record["recommended_attention"],
        evidence=evidence,
        effective_date=date.fromisoformat(record["effective_date"])
        if record.get("effective_date")
        else None,
        compliance_deadline=date.fromisoformat(record["compliance_deadline"])
        if record.get("compliance_deadline")
        else None,
        validation_explanation=record.get("validation_explanation", ""),
        scoring_explanation=record.get("scoring_explanation", ""),
    )


def known_urls_and_hashes(items: list[MonitoredItem]) -> tuple[set[str], set[str]]:
    return {item.url for item in items}, {item.raw_text_hash for item in items}
