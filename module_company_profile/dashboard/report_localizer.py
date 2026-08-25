"""Local-only translations used by the deterministic report exporters.

The dashboard locale modules are the single source of truth for all 25
languages.  They contain JSON assigned to ``window.ComplianceLocales``;
this module extracts that JSON without evaluating JavaScript or calling an
external translation service.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

LOCALES_DIR = Path(__file__).resolve().parent / "assets" / "js" / "i18n" / "locales"
LOCALE_PATTERN = re.compile(
    r'window\.ComplianceLocales\["([a-z]{2})"\]\s*=\s*(\{.*\});\s*$',
    flags=re.DOTALL,
)
MISSING_CONTROLS_PREFIX = "Some expected controls are missing or unclear: "


@lru_cache(maxsize=32)
def load_report_locale(language: str) -> dict[str, Any]:
    """Load a validated local dashboard dictionary for report generation."""
    code = language.strip().lower()
    if not re.fullmatch(r"[a-z]{2}", code):
        raise ValueError("Unsupported report language.")
    path = LOCALES_DIR / f"{code}.js"
    if not path.is_file():
        raise ValueError("Unsupported report language.")
    match = LOCALE_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match or match.group(1) != code:
        raise ValueError(f"Invalid local report dictionary: {code}.")
    bundle = json.loads(match.group(2))
    if not isinstance(bundle.get("ui"), dict) or not isinstance(bundle.get("results"), dict):
        raise ValueError(f"Incomplete local report dictionary: {code}.")
    return bundle


def localize_ui(language: str, key: str) -> str:
    """Translate a known report label without a silent cross-language fallback."""
    bundle = load_report_locale(language)
    value = bundle["ui"].get(key)
    if value:
        return str(value)
    raise ValueError(f"Missing local report translation: {language}.{key}.")


def localize_result(language: str, value: Any) -> str:
    """Translate deterministic assessment output exactly as the dashboard does."""
    if value is None:
        return ""
    text = str(value)
    dictionary = load_report_locale(language)["results"]
    direct = dictionary.get(text)
    if direct:
        return str(direct)
    translated_prefix = dictionary.get(MISSING_CONTROLS_PREFIX)
    if translated_prefix and text.startswith(MISSING_CONTROLS_PREFIX):
        controls = text[len(MISSING_CONTROLS_PREFIX) :].removesuffix(".").split(", ")
        translated_controls = [str(dictionary.get(control) or control) for control in controls]
        return f"{translated_prefix}{', '.join(translated_controls)}."
    return text


def localize_timeline_item(language: str, item: dict[str, Any]) -> tuple[str, str]:
    """Return the localized status and milestone while preserving legal references."""
    status_key = str(item.get("status_code") or "")
    title_key = str(item.get("translation_key") or "")
    status = localize_ui(language, status_key) if status_key else str(item.get("status") or "")
    title = localize_ui(language, title_key) if title_key else str(item.get("title") or "")
    return status, title
