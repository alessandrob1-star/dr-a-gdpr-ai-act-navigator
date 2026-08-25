"""Deterministic classification helpers shared by guards."""

from __future__ import annotations

import re
import unicodedata
from re import Pattern

from . import policies


def normalize_text(value: str) -> str:
    return " ".join((value or "").lower().split())


def detect_language(text: str) -> str:
    """Distinguish the two languages supported by the deterministic guard."""
    normalized = normalize_text(text)
    italian_score = sum(
        bool(re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", normalized))
        for marker in policies.ITALIAN_LANGUAGE_MARKERS
    )
    return "it" if italian_score >= 1 else "en"


def contains_keyword(text: str, keywords: list[str]) -> bool:
    normalized = normalize_text(text)
    # Match complete words or phrases. Substring checks caused false positives
    # such as "guidance" matching the jailbreak acronym "dan".
    return any(
        re.search(rf"(?<!\w){re.escape(normalize_text(keyword))}(?!\w)", normalized)
        for keyword in keywords
    )


def matches_pattern(text: str, patterns: list[Pattern[str]]) -> bool:
    return any(pattern.search(text or "") for pattern in patterns)


def _normalize_for_intent(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", without_accents.lower()).strip()


def _edit_distance_at_most_one(left: str, right: str) -> bool:
    if left == right:
        return True
    if abs(len(left) - len(right)) > 1:
        return False
    if len(left) > len(right):
        left, right = right, left

    edits = 0
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(left) == len(right):
            i += 1
        j += 1
    return True


def _token_matches_any(token: str, terms: set[str]) -> bool:
    if token in terms:
        return True
    # Allow one typo for meaningful words so "apparie" still matches "apparire".
    return len(token) >= 5 and any(_edit_distance_at_most_one(token, term) for term in terms)


def _has_token_match(tokens: list[str], terms: set[str]) -> bool:
    return any(_token_matches_any(token, terms) for token in tokens)


def _has_phrase(normalized: str, phrases: set[str]) -> bool:
    return any(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized) for phrase in phrases)


def detects_compliance_washing_intent(text: str) -> bool:
    """Detect colloquial requests to look compliant before doing real controls.

    This intentionally stays deterministic and lightweight. It does not replace
    the model; it catches an unsafe intent pattern before the model is called.
    """

    normalized = _normalize_for_intent(text)
    if not normalized:
        return False
    tokens = normalized.split()

    appearance_terms = {
        "appear",
        "appearing",
        "look",
        "looking",
        "seem",
        "seeming",
        "present",
        "presenting",
        "apparire",
        "apparie",
        "appare",
        "appari",
        "appaio",
        "sembrare",
        "sembra",
        "sembri",
        "sembro",
        "risultare",
        "risulta",
        "risulti",
        "risulto",
        "passare",
        "passa",
        "passi",
    }
    appearance_phrases = {
        "far vedere",
        "fare vedere",
        "far passare",
        "fare passare",
        "farlo passare",
        "farla passare",
        "farci passare",
        "facciamo passare",
        "far risultare",
        "make it look",
        "make us look",
        "make it seem",
        "make us seem",
    }

    compliance_state_terms = {
        "compliant",
        "compliance",
        "regular",
        "lawful",
        "legal",
        "clean",
        "ok",
        "okay",
        "conforme",
        "conformi",
        "conformita",
        "regola",
        "norma",
        "regolare",
        "posto",
    }
    compliance_state_phrases = {
        "in regola",
        "a norma",
        "a posto",
        "in ordine",
        "allineati alla norma",
        "appear compliant",
        "look compliant",
        "seem compliant",
        "look regular",
    }

    timing_terms = {
        "before",
        "without",
        "later",
        "afterwards",
        "then",
        "eventually",
        "temporarily",
        "now",
        "prima",
        "senza",
        "poi",
        "dopo",
        "intanto",
        "temporaneamente",
        "momentaneamente",
        "ora",
    }
    timing_phrases = {
        "for now",
        "not yet",
        "while not",
        "prima e poi",
        "prima poi",
        "per ora",
        "per adesso",
        "nel frattempo",
        "non ancora",
    }

    deferred_action_terms = {
        "implement",
        "implemented",
        "complete",
        "completed",
        "fix",
        "fixed",
        "regularize",
        "regularise",
        "do",
        "doing",
        "control",
        "controls",
        "gap",
        "gaps",
        "fare",
        "faccio",
        "facciamo",
        "fanno",
        "farle",
        "farli",
        "farlo",
        "sistemare",
        "sistemo",
        "sistemiamo",
        "regolarizzare",
        "regolarizzo",
        "regolarizziamo",
        "implementare",
        "implemento",
        "implementiamo",
        "completare",
        "completo",
        "completiamo",
        "controlli",
        "lacune",
    }
    deferred_action_phrases = {
        "do it later",
        "fix it later",
        "implement later",
        "complete later",
        "le faccio",
        "li faccio",
        "lo faccio",
        "la faccio",
        "le faccio dopo",
        "li faccio dopo",
        "lo faccio dopo",
        "la faccio dopo",
    }

    has_appearance = _has_token_match(tokens, appearance_terms) or _has_phrase(
        normalized, appearance_phrases
    )
    has_compliance_state = _has_token_match(tokens, compliance_state_terms) or _has_phrase(
        normalized, compliance_state_phrases
    )
    has_timing = _has_token_match(tokens, timing_terms) or _has_phrase(normalized, timing_phrases)
    has_deferred_action = _has_token_match(tokens, deferred_action_terms) or _has_phrase(
        normalized, deferred_action_phrases
    )

    return has_appearance and has_compliance_state and (has_timing or has_deferred_action)


def detects_pass_controls_anyway_intent(text: str) -> bool:
    """Detect requests to pass checks despite not completing required work."""

    normalized = _normalize_for_intent(text)
    if not normalized:
        return False
    tokens = normalized.split()

    pass_terms = {
        "pass",
        "passing",
        "passare",
        "passo",
        "passi",
        "passiamo",
        "clear",
        "clearing",
        "satisfy",
        "satisfying",
        "survive",
        "surviving",
        "get",
        "superare",
        "supero",
        "superi",
        "superiamo",
    }
    check_terms = {
        "control",
        "controls",
        "check",
        "checks",
        "audit",
        "review",
        "inspection",
        "controllo",
        "controlli",
        "verifica",
        "verifiche",
        "revisione",
    }
    incomplete_terms = {
        "without",
        "anyway",
        "regardless",
        "not",
        "incomplete",
        "missing",
        "later",
        "some",
        "partial",
        "partially",
        "shortcut",
        "shortcuts",
        "time",
        "non",
        "senza",
        "comunque",
        "tutto",
        "tutte",
        "tutti",
        "tempo",
        "dopo",
        "mancanti",
        "incompleto",
        "incompleti",
    }
    pressure_phrases = {
        "non ho tempo",
        "non abbiamo tempo",
        "non riesco a fare tutto",
        "non riusciamo a fare tutto",
        "senza fare tutto",
        "comunque i controlli",
        "passare comunque",
        "superare comunque",
        "pass controls anyway",
        "pass the checks anyway",
        "pass the audit anyway",
        "without doing everything",
        "not enough time",
        "do not have time",
        "dont have time",
        "no time",
        "get through the checks",
        "get through the audit",
        "get through controls",
        "clear the checks",
        "clear the audit",
        "satisfy the checks",
        "pass with only some",
        "pass by doing only some",
        "fix the rest later",
        "complete the rest later",
        "do the rest later",
        "only do some controls",
    }

    has_pass = any(token in pass_terms for token in tokens) or _has_phrase(
        normalized,
        {
            "get through",
            "clear the",
            "satisfy the",
        },
    )
    has_check = any(token in check_terms for token in tokens)
    has_incomplete = any(token in incomplete_terms for token in tokens) or _has_phrase(
        normalized, pressure_phrases
    )
    return has_pass and has_check and has_incomplete


def detects_deferred_compliance_washing_followup(text: str, previous_messages: list[str]) -> bool:
    """Detect short follow-ups that continue a prior compliance-washing request."""

    normalized = _normalize_for_intent(text)
    if not normalized or not previous_messages:
        return False
    tokens = normalized.split()

    followup_terms = {
        "dopo",
        "poi",
        "prima",
        "intanto",
        "temporaneamente",
        "momentaneamente",
        "later",
        "then",
        "afterwards",
        "temporarily",
        "eventually",
        "now",
        "only",
    }
    action_terms = {
        "fare",
        "faccio",
        "facciamo",
        "farle",
        "farli",
        "farlo",
        "farla",
        "fatte",
        "fatti",
        "alcune",
        "qualcuna",
        "tutte",
        "tutti",
        "sistemare",
        "sistemo",
        "sistemiamo",
        "regolarizzare",
        "regolarizzo",
        "implementare",
        "implemento",
        "completare",
        "completo",
        "controlli",
        "do",
        "doing",
        "fix",
        "complete",
        "implement",
        "controls",
        "some",
        "all",
    }
    followup_phrases = {
        "le faccio dopo",
        "li faccio dopo",
        "lo faccio dopo",
        "la faccio dopo",
        "farne solo alcune",
        "non tutte",
        "non tutti",
        "if i do them later",
        "do them later",
        "fix them later",
        "only some",
    }

    is_deferred_followup = (
        _has_token_match(tokens, followup_terms) and _has_token_match(tokens, action_terms)
    ) or _has_phrase(normalized, followup_phrases)
    if not is_deferred_followup:
        return False

    recent_previous = previous_messages[-6:]
    return any(
        detects_compliance_washing_intent(message)
        or detects_pass_controls_anyway_intent(message)
        or _has_phrase(
            _normalize_for_intent(message), {"blocco del policy agent", "policy agent block"}
        )
        for message in recent_previous
    )
