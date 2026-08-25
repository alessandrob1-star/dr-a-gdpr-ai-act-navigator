"""Diff two regulatory-event snapshots into a dated 'what changed' changelog.

A compliance tool is only as trustworthy as its data currency. This turns two
snapshots of the dashboard event list (the JSON emitted by
``RegulatoryEvent.to_dashboard_dict``) into an explicit, dated record of what
was added, removed, or changed since the last run — so freshness is provable,
not merely claimed.

Pure functions, no network, deterministic given its inputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from typing import Any

# Fields whose changes are meaningful for a freshness changelog. Timestamps like
# first_detected_at are deliberately excluded so trivial re-detections do not
# create noise; last_updated_at IS tracked because it signals a real update.
TRACKED_FIELDS: tuple[str, ...] = (
    "event_status",
    "overall_priority",
    "recommended_attention",
    "reliability_score",
    "urgency_score",
    "regulatory_impact_score",
    "business_impact_score",
    "effective_date",
    "compliance_deadline",
    "last_updated_at",
)


def _index_by_id(events: Iterable[Mapping[str, Any]]) -> dict[Any, Mapping[str, Any]]:
    index: dict[Any, Mapping[str, Any]] = {}
    for event in events:
        event_id = event.get("event_id")
        if event_id is not None:
            index[event_id] = event
    return index


def _summarize(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id"),
        "event_title": event.get("event_title"),
        "event_status": event.get("event_status"),
        "overall_priority": event.get("overall_priority"),
    }


def diff_regulatory_events(
    old_events: Iterable[Mapping[str, Any]],
    new_events: Iterable[Mapping[str, Any]],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Compare two event snapshots keyed on ``event_id``.

    Returns a JSON-serialisable report with added, removed, and changed events.
    """
    old_index = _index_by_id(old_events)
    new_index = _index_by_id(new_events)

    added = [_summarize(new_index[k]) for k in new_index if k not in old_index]
    removed = [_summarize(old_index[k]) for k in old_index if k not in new_index]

    changed: list[dict[str, Any]] = []
    for event_id in new_index:
        if event_id not in old_index:
            continue
        old_event, new_event = old_index[event_id], new_index[event_id]
        field_changes = {
            field: {"from": old_event.get(field), "to": new_event.get(field)}
            for field in TRACKED_FIELDS
            if old_event.get(field) != new_event.get(field)
        }
        if field_changes:
            changed.append(
                {
                    "event_id": event_id,
                    "event_title": new_event.get("event_title"),
                    "changes": field_changes,
                }
            )

    added.sort(key=lambda item: (item["event_id"] is None, item["event_id"]))
    removed.sort(key=lambda item: (item["event_id"] is None, item["event_id"]))
    changed.sort(key=lambda item: (item["event_id"] is None, item["event_id"]))

    return {
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "summary": {
            "old_count": len(old_index),
            "new_count": len(new_index),
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
        "added": added,
        "removed": removed,
        "changed": changed,
    }


def render_diff_markdown(report: Mapping[str, Any]) -> str:
    """Render the diff report as a dated Markdown changelog."""
    summary = report.get("summary", {})
    lines = [
        "# Regulatory Updates — What Changed",
        "",
        f"_Generated: {report.get('generated_at', 'unknown')}_",
        "",
        f"- Previous snapshot: {summary.get('old_count', 0)} events",
        f"- Current snapshot: {summary.get('new_count', 0)} events",
        f"- **Added: {summary.get('added', 0)} · "
        f"Removed: {summary.get('removed', 0)} · "
        f"Changed: {summary.get('changed', 0)}**",
        "",
    ]

    added = report.get("added", [])
    if added:
        lines += ["## New events", ""]
        for item in added:
            lines.append(
                f"- **[{item.get('overall_priority', '?')}]** "
                f"{item.get('event_title', '(untitled)')} "
                f"(#{item.get('event_id')}, {item.get('event_status', '?')})"
            )
        lines.append("")

    changed = report.get("changed", [])
    if changed:
        lines += ["## Updated events", ""]
        for item in changed:
            lines.append(f"- **{item.get('event_title', '(untitled)')}** (#{item.get('event_id')})")
            for field, delta in item.get("changes", {}).items():
                lines.append(f"  - `{field}`: {delta.get('from')} → {delta.get('to')}")
        lines.append("")

    removed = report.get("removed", [])
    if removed:
        lines += ["## Removed events", ""]
        for item in removed:
            lines.append(f"- {item.get('event_title', '(untitled)')} (#{item.get('event_id')})")
        lines.append("")

    if not (added or changed or removed):
        lines += ["_No changes since the previous snapshot._", ""]

    return "\n".join(lines)
