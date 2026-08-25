"""Local, file-based profile snapshot storage for the single-user dashboard."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "company"


def save_profile_snapshot(root: Path, evaluation: dict[str, Any]) -> dict[str, Any]:
    questionnaire = evaluation.get("questionnaire_payload") or {}
    company_name = str(
        (evaluation.get("dashboard_context") or {}).get("company_name")
        or (questionnaire.get("answers") or {}).get("company_name")
        or "Company"
    )
    saved_at = datetime.now(UTC).isoformat()
    snapshot_id = f"{_slug(company_name)}-{saved_at[:10]}-{uuid4().hex[:8]}"
    payload = {
        "id": snapshot_id,
        "company_name": company_name,
        "saved_at": saved_at,
        "score": (evaluation.get("dashboard_context") or {})
        .get("compliance_score", {})
        .get("score"),
        "evaluation": evaluation,
    }
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{snapshot_id}.json"
    temporary_path = root / f".{snapshot_id}.{uuid4().hex}.tmp"
    try:
        temporary_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return {key: payload[key] for key in ("id", "company_name", "saved_at", "score")}


def list_profile_snapshots(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    snapshots = []
    for path in root.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("id"), str)
            or not re.fullmatch(r"[a-z0-9-]+", payload["id"])
            or not isinstance(payload.get("evaluation"), dict)
        ):
            continue
        snapshots.append(
            {key: payload.get(key) for key in ("id", "company_name", "saved_at", "score")}
        )
    return sorted(snapshots, key=lambda item: item.get("saved_at") or "", reverse=True)


def load_profile_snapshot(root: Path, snapshot_id: str) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9-]+", snapshot_id):
        raise ValueError("Invalid profile snapshot identifier.")
    path = root / f"{snapshot_id}.json"
    if not path.exists():
        raise ValueError("Profile snapshot not found.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    evaluation = payload.get("evaluation")
    if not isinstance(evaluation, dict):
        raise ValueError("Stored profile snapshot is invalid.")
    return evaluation


def delete_profile_snapshot(root: Path, snapshot_id: str) -> None:
    if not re.fullmatch(r"[a-z0-9-]+", snapshot_id):
        raise ValueError("Invalid profile snapshot identifier.")
    path = root / f"{snapshot_id}.json"
    if not path.exists():
        raise ValueError("Profile snapshot not found.")
    path.unlink()


def compare_profile_snapshots(
    root: Path,
    older_id: str,
    newer_id: str,
) -> dict[str, Any]:
    older = load_profile_snapshot(root, older_id)
    newer = load_profile_snapshot(root, newer_id)
    return compare_evaluations(older, newer, older_id, newer_id)


def compare_evaluations(
    older: dict[str, Any],
    newer: dict[str, Any],
    older_id: str = "older",
    newer_id: str = "newer",
) -> dict[str, Any]:
    """Compare two already validated evaluations."""
    older_context = older.get("dashboard_context") or {}
    newer_context = newer.get("dashboard_context") or {}
    older_company = str(older_context.get("company_name") or "").strip()
    newer_company = str(newer_context.get("company_name") or "").strip()
    if older_company and newer_company and older_company.casefold() != newer_company.casefold():
        raise ValueError("Only snapshots of the same company can be compared.")
    older_memory = older.get("company_memory") or {}
    newer_memory = newer.get("company_memory") or {}
    old_score = int((older_context.get("compliance_score") or {}).get("score") or 0)
    new_score = int((newer_context.get("compliance_score") or {}).get("score") or 0)
    old_tags = set(older_context.get("relevance_tags") or [])
    new_tags = set(newer_context.get("relevance_tags") or [])
    old_controls = set((older_memory.get("controls") or {}).get("missing_or_to_verify") or [])
    new_controls = set((newer_memory.get("controls") or {}).get("missing_or_to_verify") or [])
    return {
        "company_name": newer_company or older_company,
        "older_id": older_id,
        "newer_id": newer_id,
        "older_score": old_score,
        "newer_score": new_score,
        "score_delta": new_score - old_score,
        "added_tags": sorted(new_tags - old_tags),
        "removed_tags": sorted(old_tags - new_tags),
        "new_missing_controls": sorted(new_controls - old_controls),
        "resolved_controls": sorted(old_controls - new_controls),
    }
