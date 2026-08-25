"""CSV-backed repository helpers for the local MVP."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import AuthorityLevel, Source


def load_sources(path: str | Path) -> list[Source]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {
            "name",
            "url",
            "source_type",
            "authority_level",
            "topic_area",
            "access_method",
            "priority",
            "active",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Source registry {Path(path)} is missing required "
                f"column(s): {', '.join(sorted(missing))}."
            )
        sources: list[Source] = []
        for index, row in enumerate(reader, start=1):
            try:
                priority = int(row["priority"])
            except ValueError as exc:
                raise ValueError(
                    f"Source registry row {index} ({row.get('name', '?')}) has a "
                    f"non-numeric priority: {row['priority']!r}."
                ) from exc
            try:
                authority_level = AuthorityLevel(row["authority_level"])
            except ValueError as exc:
                raise ValueError(
                    f"Source registry row {index} ({row.get('name', '?')}) has an "
                    f"unknown authority_level: {row['authority_level']!r}."
                ) from exc
            sources.append(
                Source(
                    id=index,
                    name=row["name"],
                    url=row["url"],
                    source_type=row["source_type"],
                    authority_level=authority_level,
                    topic_area=row["topic_area"],
                    access_method=row["access_method"],
                    priority=priority,
                    active=row["active"].lower() == "true",
                    notes=row.get("notes", ""),
                )
            )
    return sources
