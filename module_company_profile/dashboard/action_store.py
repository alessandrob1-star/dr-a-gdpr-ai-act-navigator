"""Persistent, human-approved action plans derived from trusted assessments."""

from __future__ import annotations

import json
import re
import threading
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

ALLOWED_STATUSES = {"proposed", "approved", "in_progress", "completed"}
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
MAX_TEXT_LENGTH = 4000
_STORE_LOCK = threading.RLock()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "company"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _validated_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[a-z0-9-]+", value):
        raise ValueError(f"Invalid {label} identifier.")
    return value


def _clean_text(value: Any, label: str, *, required: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    cleaned = value.strip()
    if required and not cleaned:
        raise ValueError(f"{label} is required.")
    if len(cleaned) > MAX_TEXT_LENGTH:
        raise ValueError(f"{label} must be {MAX_TEXT_LENGTH} characters or fewer.")
    return cleaned


def _clean_due_date(value: Any) -> str:
    cleaned = _clean_text(value, "Due date")
    if not cleaned:
        return ""
    try:
        date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError("Due date must use YYYY-MM-DD format.") from exc
    return cleaned


def _priority_for_control(control: str, warnings: list[dict[str, Any]]) -> str:
    levels = [
        str(warning.get("level") or "low").lower()
        for warning in warnings
        if control in (warning.get("linked_missing_controls") or [])
    ]
    return max(levels, key=lambda level: PRIORITY_RANK.get(level, 0), default="medium")


def _warnings_for_control(control: str, warnings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    linked = [
        warning for warning in warnings if control in (warning.get("linked_missing_controls") or [])
    ]
    return sorted(
        linked,
        key=lambda warning: PRIORITY_RANK.get(str(warning.get("level") or "low").lower(), 0),
        reverse=True,
    )


def derive_action_plan(evaluation: dict[str, Any]) -> dict[str, Any]:
    """Create an auditable task plan without changing the legal assessment."""
    context = evaluation.get("dashboard_context") or {}
    memory = evaluation.get("company_memory") or {}
    company_name = str(context.get("company_name") or "").strip()
    if not company_name:
        raise ValueError("A company name is required to create an action plan.")
    missing_controls = (memory.get("controls") or {}).get("missing_or_to_verify") or []
    if not isinstance(missing_controls, list) or not all(
        isinstance(control, str) and control.strip() for control in missing_controls
    ):
        raise ValueError("The assessment contains invalid missing controls.")
    warnings = context.get("risk_warnings") or []
    if not isinstance(warnings, list):
        raise ValueError("The assessment contains invalid warnings.")

    generated_at = _now()
    tasks = []
    for control in missing_controls:
        linked = _warnings_for_control(control, warnings)
        specific = next(
            (
                warning
                for warning in linked
                if str(warning.get("title") or "") != "Missing controls"
            ),
            linked[0] if linked else {},
        )
        references = sorted(
            {
                str(reference)
                for warning in linked
                for reference in (warning.get("legal_references") or [])
                if str(reference).strip()
            }
        )
        tasks.append(
            {
                "id": f"control-{_slug(control)}",
                "title": control,
                "priority": _priority_for_control(control, warnings),
                "status": "proposed",
                "owner": "",
                "due_date": "",
                "evidence": "",
                "approved_by": "",
                "approved_at": "",
                "warning_titles": [str(item.get("title") or "") for item in linked],
                "legal_references": references,
                "recommended_action": str(specific.get("recommended_action") or ""),
                "created_at": generated_at,
                "updated_at": generated_at,
                "revision": 1,
            }
        )
    tasks.sort(key=lambda task: (-PRIORITY_RANK.get(str(task["priority"]), 0), str(task["title"])))
    return {
        "plan_id": _slug(company_name),
        "company_name": company_name,
        "generated_at": generated_at,
        "updated_at": generated_at,
        "tasks": tasks,
        "archived_tasks": [],
    }


def _plan_path(root: Path, plan_id: str) -> Path:
    return root / f"{_validated_identifier(plan_id, 'action plan')}.json"


def _write_plan(root: Path, plan: dict[str, Any]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    path = _plan_path(root, str(plan["plan_id"]))
    temporary = root / f".{path.stem}.{uuid4().hex}.tmp"
    try:
        temporary.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_action_plan(root: Path, plan_id: str) -> dict[str, Any]:
    path = _plan_path(root, plan_id)
    if not path.exists():
        raise ValueError("Action plan not found.")
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Stored action plan is invalid.") from exc
    if not isinstance(plan, dict) or plan.get("plan_id") != plan_id:
        raise ValueError("Stored action plan is invalid.")
    return plan


def sync_action_plan(root: Path, evaluation: dict[str, Any]) -> dict[str, Any]:
    """Merge fresh deterministic findings with user-managed task state."""
    derived = derive_action_plan(evaluation)
    with _STORE_LOCK:
        try:
            stored = load_action_plan(root, str(derived["plan_id"]))
        except ValueError as exc:
            if str(exc) != "Action plan not found.":
                raise
            stored = None
        if not stored:
            _write_plan(root, derived)
            return derived

        stored_tasks = {
            str(task.get("id")): task
            for task in stored.get("tasks") or []
            if isinstance(task, dict) and isinstance(task.get("id"), str)
        }
        merged_tasks = []
        active_ids = set()
        for task in derived["tasks"]:
            task_id = str(task["id"])
            active_ids.add(task_id)
            previous = stored_tasks.get(task_id)
            if previous:
                for field in (
                    "status",
                    "owner",
                    "due_date",
                    "evidence",
                    "approved_by",
                    "approved_at",
                    "created_at",
                    "updated_at",
                    "revision",
                ):
                    task[field] = previous.get(field, task[field])
            merged_tasks.append(task)

        archived = [
            task
            for task in (stored.get("archived_tasks") or [])
            if isinstance(task, dict) and task.get("id") not in active_ids
        ]
        for task_id, task in stored_tasks.items():
            if task_id not in active_ids:
                retired = dict(task)
                retired["archived_at"] = _now()
                archived.append(retired)

        derived["generated_at"] = stored.get("generated_at") or derived["generated_at"]
        derived["updated_at"] = _now()
        derived["tasks"] = merged_tasks
        derived["archived_tasks"] = archived
        _write_plan(root, derived)
        return derived


def update_action_task(
    root: Path,
    plan_id: str,
    task_id: str,
    patch: dict[str, Any],
) -> dict[str, Any]:
    """Apply a validated human workflow update to one persisted task."""
    _validated_identifier(plan_id, "action plan")
    _validated_identifier(task_id, "action task")
    if not isinstance(patch, dict):
        raise ValueError("Action task update must be an object.")
    allowed_fields = {"status", "owner", "due_date", "evidence", "approved_by"}
    unexpected = set(patch) - allowed_fields
    if unexpected:
        raise ValueError(f"Unsupported action task fields: {', '.join(sorted(unexpected))}.")

    with _STORE_LOCK:
        plan = load_action_plan(root, plan_id)
        task = next(
            (item for item in plan.get("tasks") or [] if item.get("id") == task_id),
            None,
        )
        if not isinstance(task, dict):
            raise ValueError("Action task not found.")

        owner = _clean_text(patch.get("owner", task.get("owner", "")), "Owner")
        due_date = _clean_due_date(patch.get("due_date", task.get("due_date", "")))
        evidence = _clean_text(patch.get("evidence", task.get("evidence", "")), "Evidence note")
        requested_status = str(patch.get("status", task.get("status", "proposed")))
        if requested_status not in ALLOWED_STATUSES:
            raise ValueError("Invalid action task status.")

        approved_by = str(task.get("approved_by") or "")
        approved_at = str(task.get("approved_at") or "")
        if requested_status == "proposed":
            approved_by = ""
            approved_at = ""
        elif requested_status == "approved":
            if not owner:
                raise ValueError("An owner is required for approved or active work.")
            if not approved_at:
                approved_by = _clean_text(patch.get("approved_by", ""), "Approver", required=True)
                approved_at = _now()
        elif requested_status in {"in_progress", "completed"}:
            if not approved_at:
                raise ValueError("Human approval is required before work can start or complete.")
            if not owner:
                raise ValueError("An owner is required for approved or active work.")
        if requested_status == "completed" and not evidence:
            raise ValueError("Add an evidence note before completing an action.")

        task.update(
            {
                "status": requested_status,
                "owner": owner,
                "due_date": due_date,
                "evidence": evidence,
                "approved_by": approved_by,
                "approved_at": approved_at,
                "updated_at": _now(),
                "revision": int(task.get("revision") or 0) + 1,
            }
        )
        plan["updated_at"] = task["updated_at"]
        _write_plan(root, plan)
        return plan
