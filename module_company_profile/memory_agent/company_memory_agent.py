"""Build company memory and dashboard matching context from questionnaire JSON.

The deterministic output is the source of truth. The OpenAI call only
creates a human-readable explanation from the already derived memory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_REGULATORY_EVENTS = Path("storage/web_scraping_outputs/regulatory_events.json")
DEFAULT_ARTICLE_FEED = Path("storage/web_scraping_outputs/articles_and_news_feed.json")
AI_ACT_TIMELINE_SOURCE = "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai"
AI_ACT_SIMPLIFICATION_AGREEMENT_SOURCE = (
    "https://www.consilium.europa.eu/en/press/press-releases/2026/05/07/"
    "artificial-intelligence-council-and-parliament-agree-to-simplify-and-streamline-rules/"
)


# ---------------------------------------------------------------------------
# Assessment knowledge base
#
# These dictionaries are the deterministic core of the Company Profile Agent.
# Rules, references, and weights stay as data so every score contribution can
# be traced back to a questionnaire answer during a review or presentation.
# ---------------------------------------------------------------------------

TAG_EXPLANATIONS = {
    "gdpr_relevant": {
        "legal_references": ["GDPR Articles 2-3, 5, 24 and 30"],
        "recommended_action": "Confirm the processing inventory, lawful bases, notices, roles, and records of processing.",
    },
    "ai_act_relevant": {
        "legal_references": ["AI Act Articles 2-4 and 16-27"],
        "recommended_action": "Document the AI value-chain role and classify each AI system before deployment.",
    },
    "high_risk_ai_candidate": {
        "legal_references": ["AI Act Article 6 and Annex III", "AI Act Articles 9-15"],
        "recommended_action": "Perform a documented high-risk classification review and map the applicable provider or deployer duties.",
    },
    "prohibited_practice_review": {
        "legal_references": ["AI Act Article 5"],
        "recommended_action": "Pause deployment until the selected practice has been reviewed against the prohibited-practices rules.",
    },
    "dpia_candidate": {
        "legal_references": ["GDPR Articles 35-36"],
        "recommended_action": (
            "Run and document a DPIA screening. The questionnaire signals do not by "
            "themselves establish that a full DPIA is mandatory. Complete a DPIA before "
            "processing if the screening shows likely high risk; consult the supervisory "
            "authority under Article 36 only if the DPIA shows high residual risk without "
            "adequate mitigation."
        ),
    },
    "international_transfer_review": {
        "legal_references": ["GDPR Articles 44-49"],
        "recommended_action": "Map destinations and vendors, then verify the transfer mechanism and supplementary measures.",
    },
    "transparency_gap": {
        "legal_references": ["AI Act Article 50", "GDPR Articles 12-14"],
        "recommended_action": "Add a clear and prominent notice explaining when and how users interact with AI.",
    },
    "gpai_relevant": {
        "legal_references": ["AI Act Articles 51-56"],
        "recommended_action": "Determine whether the company is a GPAI provider or downstream deployer and document the applicable duties.",
    },
}

TAG_RULES: dict[str, dict[str, Any]] = {
    "gdpr_relevant": {
        "answer_keys": {
            "eu_presence": {"eu_company", "eu_customers", "eu_market"},
            "personal_data": {
                "customers_users",
                "employees_candidates",
                "contact_account",
                "tracking_analytics",
                "sensitive_data",
                "children_data",
            },
        },
        "match_mode": "all",
        "label": "GDPR relevance likely",
        "dashboard_text": "The company likely needs a GDPR relevance review.",
    },
    "ai_act_relevant": {
        "answer_keys": {
            "eu_presence": {"eu_company", "eu_customers", "eu_market"},
            "ai_usage": {
                "internal_ai",
                "customer_product_ai",
                "in_house_ai",
                "ai_provider",
                "gpai",
            },
        },
        "match_mode": "all",
        "label": "AI Act relevance likely",
        "dashboard_text": "The company likely needs an AI Act relevance review.",
    },
    "high_risk_ai_candidate": {
        "answer_keys": {
            "ai_usage": {
                "internal_ai",
                "customer_product_ai",
                "in_house_ai",
                "ai_provider",
                "gpai",
            },
            "sensitive_domains": {
                "recruiting",
                "workers",
                "education",
                "credit",
                "healthcare",
                "critical_infrastructure",
                "law_migration_justice",
            },
        },
        "match_mode": "all",
        "requires_tags": {"ai_act_relevant"},
        "label": "High-risk AI candidate",
        "dashboard_text": "One or more AI use cases may fall into high-risk AI areas.",
    },
    "prohibited_practice_review": {
        "answer_keys": {
            "ai_usage": {
                "internal_ai",
                "customer_product_ai",
                "in_house_ai",
                "ai_provider",
                "gpai",
            },
            "delicate_ai_practices": {
                "biometric_recognition",
                "emotion_recognition",
                "social_scoring",
                "manipulative_techniques",
                "sensitive_traits",
            },
        },
        "match_mode": "all",
        "requires_tags": {"ai_act_relevant"},
        "label": "Sensitive AI practice review",
        "dashboard_text": "Sensitive AI practices require specific review before use or sale.",
    },
    "dpia_candidate": {
        "answer_keys": {
            "personal_data": {"sensitive_data", "children_data", "tracking_analytics"},
            "profiling_decisions": {
                "profiling",
                "personalized_recommendations",
                "significant_automated_decisions",
                "human_review_decision_support",
            },
        },
        "requires_tags": {"gdpr_relevant"},
        "label": "DPIA candidate",
        "dashboard_text": "The company may need a DPIA or similar impact assessment.",
    },
    "international_transfer_review": {
        "answer_keys": {
            "extra_eea_transfers": {"yes", "unknown"},
            "extra_eea_providers": {"cloud_hosting", "ai_api_models", "internal_saas", "unknown"},
        },
        "requires_tags": {"gdpr_relevant"},
        "label": "International transfer review",
        "dashboard_text": "Cloud, AI providers, or data transfers outside the EU/EEA should be reviewed.",
    },
    "transparency_gap": {
        "answer_keys": {
            "ai_notice": {"no_notice", "not_prominent"},
        },
        "requires_tags": {"ai_act_relevant"},
        "label": "AI transparency gap",
        "dashboard_text": "The company may need clearer user-facing AI notices.",
    },
    "gpai_relevant": {
        "answer_keys": {
            "ai_usage": {"gpai"},
        },
        "requires_tags": {"ai_act_relevant"},
        "label": "GPAI relevance likely",
        "dashboard_text": "The company may need to track general-purpose AI model obligations and Code of Practice updates.",
    },
}


TAG_TO_TOPIC_LABELS = {
    "gdpr_relevant": {"GDPR_GENERAL"},
    "ai_act_relevant": {"AI_ACT_GENERAL"},
    "high_risk_ai_candidate": {"AI_ACT_HIGH_RISK"},
    "prohibited_practice_review": {"AI_ACT_PROHIBITED_PRACTICES"},
    "dpia_candidate": {"GDPR_DPIA"},
    "international_transfer_review": {"GDPR_INTERNATIONAL_TRANSFERS"},
    "transparency_gap": {"AI_ACT_TRANSPARENCY"},
    "gpai_relevant": {"AI_ACT_GPAI"},
}


TAG_SCORE_WEIGHTS = {
    "gdpr_relevant": 14,
    "ai_act_relevant": 14,
    "high_risk_ai_candidate": 22,
    "prohibited_practice_review": 26,
    "dpia_candidate": 16,
    "international_transfer_review": 10,
    "transparency_gap": 8,
    "gpai_relevant": 18,
}


CONTROL_LABELS = {
    "privacy_policy": "Privacy policy",
    "records_processing": "Records of processing",
    "dpo_privacy_owner": "DPO or privacy owner",
    "dpia_process": "DPIA process",
    "breach_process": "Data breach process",
    "data_subject_rights": "Data subject rights process",
    "vendor_review": "Vendor review",
    "ai_documentation": "AI system documentation",
    "human_oversight": "Human oversight",
    "ai_policy": "Internal AI policy",
    "training": "AI or privacy training",
}

# Explicit warning-to-control relationships keep downstream explanations
# precise. They expose which derived missing controls belong to each warning.
WARNING_CONTROL_LINKS = {
    "prohibited_practice_review": {
        "AI system documentation",
        "Human oversight",
        "Internal AI policy",
    },
    "high_risk_ai_candidate": {
        "AI system documentation",
        "Human oversight",
        "Internal AI policy",
    },
    "dpia_candidate": {"DPIA process"},
    "international_transfer_review": {"Vendor review"},
}

CHECKBOX_OPTIONS = {
    "eu_presence": {"eu_company", "eu_customers", "eu_market", "no_eu_presence", "unknown"},
    "ai_usage": {
        "internal_ai",
        "customer_product_ai",
        "in_house_ai",
        "ai_provider",
        "gpai",
        "no_ai",
        "unknown",
    },
    "ai_functions": {
        "content_generation",
        "recommendations",
        "classification",
        "scoring",
        "decision_support",
        "automated_decision",
        "not_applicable",
    },
    "sensitive_domains": {
        "recruiting",
        "workers",
        "education",
        "credit",
        "healthcare",
        "critical_infrastructure",
        "law_migration_justice",
        "none",
        "unknown",
    },
    "delicate_ai_practices": {
        "biometric_recognition",
        "emotion_recognition",
        "social_scoring",
        "manipulative_techniques",
        "sensitive_traits",
        "none",
        "unknown",
    },
    "personal_data": {
        "customers_users",
        "employees_candidates",
        "contact_account",
        "tracking_analytics",
        "sensitive_data",
        "children_data",
        "no_personal_data",
        "unknown",
    },
    "profiling_decisions": {
        "profiling",
        "personalized_recommendations",
        "significant_automated_decisions",
        "human_review_decision_support",
        "no",
        "unknown",
    },
    "extra_eea_providers": {"cloud_hosting", "ai_api_models", "internal_saas", "no", "unknown"},
    "controls": set(CONTROL_LABELS) | {"none", "unknown"},
}

RADIO_OPTIONS = {
    "industry": {
        "software_saas",
        "hr_recruiting",
        "fintech",
        "healthcare",
        "education",
        "manufacturing",
        "public_sector",
        "other",
    },
    "company_size": {"micro", "small", "medium", "large"},
    "ai_notice": {"clear", "not_prominent", "no_notice", "not_applicable", "unknown"},
    "privacy_role": {"controller", "processor", "joint_controller", "mixed", "unknown"},
    "extra_eea_transfers": {"yes", "no", "unknown"},
    "dashboard_priority": {
        "applicable_rules",
        "main_risks",
        "missing_controls",
        "external_evidence",
        "gdpr_ai_act_review",
        "action_plan",
    },
}

TEXT_FIELDS = {"company_name", "contact_email", "notes"}
REQUIRED_ASSESSMENT_FIELDS = (
    "company_name",
    "industry",
    "company_size",
    "eu_presence",
    "ai_usage",
    "ai_functions",
    "ai_notice",
    "sensitive_domains",
    "delicate_ai_practices",
    "personal_data",
    "profiling_decisions",
    "privacy_role",
    "extra_eea_transfers",
    "extra_eea_providers",
    "controls",
    "dashboard_priority",
)

EXCLUSIVE_CHECKBOX_VALUES = {
    "eu_presence": {"no_eu_presence", "unknown"},
    "ai_usage": {"no_ai", "unknown"},
    "ai_functions": {"not_applicable"},
    "sensitive_domains": {"none", "unknown"},
    "delicate_ai_practices": {"none", "unknown"},
    "personal_data": {"no_personal_data", "unknown"},
    "profiling_decisions": {"no", "unknown"},
    "extra_eea_providers": {"no", "unknown"},
    "controls": {"none", "unknown"},
}


def validate_questionnaire_payload(
    payload: dict[str, Any], *, require_complete: bool = False
) -> dict[str, Any]:
    """Validate the public questionnaire contract before deriving any score."""
    if not isinstance(payload, dict):
        raise ValueError("Questionnaire payload must be a JSON object.")
    answers = payload.get("answers", {})
    if not isinstance(answers, dict):
        raise ValueError("Questionnaire answers must be a JSON object.")

    known_fields = set(CHECKBOX_OPTIONS) | set(RADIO_OPTIONS) | TEXT_FIELDS
    unknown_fields = sorted(set(answers) - known_fields)
    if unknown_fields:
        raise ValueError("Unknown questionnaire fields: " + ", ".join(unknown_fields))

    for field, allowed_values in CHECKBOX_OPTIONS.items():
        if field not in answers:
            continue
        values = answers[field]
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError(f"Questionnaire field '{field}' must be a list of values.")
        invalid_values = sorted(set(values) - allowed_values)
        if invalid_values:
            raise ValueError(
                f"Questionnaire field '{field}' contains invalid values: "
                + ", ".join(invalid_values)
            )
        if len(values) != len(set(values)):
            raise ValueError(f"Questionnaire field '{field}' contains duplicate values.")
        exclusive_selected = set(values) & EXCLUSIVE_CHECKBOX_VALUES.get(field, set())
        if exclusive_selected and len(set(values)) > 1:
            raise ValueError(
                f"Questionnaire field '{field}' combines an exclusive answer with other values."
            )

    for field, allowed_values in RADIO_OPTIONS.items():
        if field not in answers:
            continue
        value = answers[field]
        if value != "" and (not isinstance(value, str) or value not in allowed_values):
            raise ValueError(f"Questionnaire field '{field}' contains an invalid value.")

    for field in TEXT_FIELDS:
        if field in answers and not isinstance(answers[field], str):
            raise ValueError(f"Questionnaire field '{field}' must be text.")
    if len(answers.get("company_name", "")) > 200:
        raise ValueError("Company name must be 200 characters or fewer.")
    if len(answers.get("contact_email", "")) > 320:
        raise ValueError("Contact email must be 320 characters or fewer.")
    if len(answers.get("notes", "")) > 5000:
        raise ValueError("Notes must be 5000 characters or fewer.")

    if require_complete:
        missing_fields = [
            field for field in REQUIRED_ASSESSMENT_FIELDS if answers.get(field) in (None, "", [])
        ]
        if missing_fields:
            raise ValueError(
                "Questionnaire incomplete. Answer every assessment question; "
                "select 'I do not know' where necessary. Missing fields: "
                + ", ".join(missing_fields)
            )

    # Imported JSON can bypass the browser's mutually-exclusive controls, so
    # also reject contradictions that span separate questions.
    if "no_ai" in as_set(answers.get("ai_usage")):
        ai_conflicts = {
            "ai_functions": as_set(answers.get("ai_functions")) - {"not_applicable"},
            "sensitive_domains": as_set(answers.get("sensitive_domains")) - {"none"},
            "delicate_ai_practices": as_set(answers.get("delicate_ai_practices")) - {"none"},
        }
        conflicts = sorted(field for field, values in ai_conflicts.items() if values)
        if answers.get("ai_notice") not in {None, "", "not_applicable"}:
            conflicts.append("ai_notice")
        if conflicts:
            raise ValueError(
                "The 'no_ai' answer conflicts with AI-specific fields: " + ", ".join(conflicts)
            )
    if "no_personal_data" in as_set(answers.get("personal_data")):
        conflicts = []
        if as_set(answers.get("profiling_decisions")) - {"no"}:
            conflicts.append("profiling_decisions")
        if answers.get("extra_eea_transfers") not in {None, "", "no"}:
            conflicts.append("extra_eea_transfers")
        if as_set(answers.get("extra_eea_providers")) - {"no"}:
            conflicts.append("extra_eea_providers")
        if conflicts:
            raise ValueError(
                "The 'no_personal_data' answer conflicts with privacy-specific fields: "
                + ", ".join(conflicts)
            )
    return answers


# ---------------------------------------------------------------------------
# Answer normalization and rule evidence
# ---------------------------------------------------------------------------
def as_set(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(item) for item in value}
    if value in (None, ""):
        return set()
    return {str(value)}


def rule_matches(answers: dict[str, Any], rule: dict[str, Any]) -> bool:
    matches = [
        bool(as_set(answers.get(key)) & expected_values)
        for key, expected_values in rule["answer_keys"].items()
    ]
    if rule.get("match_mode") == "all":
        return bool(matches) and all(matches)
    return any(matches)


def triggered_answers(answers: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    evidence = []
    for question_key, expected_values in TAG_RULES[tag]["answer_keys"].items():
        selected = sorted(as_set(answers.get(question_key)) & expected_values)
        if selected:
            evidence.append({"question_key": question_key, "selected_values": selected})
    return evidence


def build_assessment_trace(
    answers: dict[str, Any], tags: list[str], missing_controls: list[str]
) -> list[dict[str, Any]]:
    trace = []
    for tag in tags:
        trace.append(
            {
                "type": "relevance_rule",
                "rule_id": tag,
                "label": TAG_RULES[tag]["label"],
                "points": TAG_SCORE_WEIGHTS[tag],
                "triggered_by": triggered_answers(answers, tag),
                **TAG_EXPLANATIONS[tag],
            }
        )
    if missing_controls:
        control_references = []
        if "gdpr_relevant" in tags:
            control_references.append("GDPR Articles 12-22, 24, 30 and 32")
        if "ai_act_relevant" in tags:
            control_references.append("AI Act Article 4")
        if "high_risk_ai_candidate" in tags:
            control_references.append("AI Act Articles 9-17")
        trace.append(
            {
                "type": "missing_controls",
                "rule_id": "missing_controls",
                "label": "Missing or unverified controls",
                "points": min(len(missing_controls) * 4, 24),
                "triggered_by": [{"question_key": "controls", "missing_values": missing_controls}],
                "legal_references": control_references,
                "recommended_action": "Assign owners and evidence for each missing or unverified control.",
            }
        )
    return trace


# ---------------------------------------------------------------------------
# Company Profile Agent: questionnaire answers -> persistent company memory
# ---------------------------------------------------------------------------
def derive_tags(answers: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for tag, rule in TAG_RULES.items():
        required_tags = set(rule.get("requires_tags", set()))
        if required_tags and not required_tags.issubset(tags):
            continue
        if rule_matches(answers, rule):
            tags.append(tag)
    return tags


def derive_missing_controls(answers: dict[str, Any], tags: list[str]) -> list[str]:
    controls = as_set(answers.get("controls"))
    needed: set[str] = set()

    if "gdpr_relevant" in tags:
        needed.update(
            {"privacy_policy", "records_processing", "breach_process", "data_subject_rights"}
        )
        if answers.get("extra_eea_transfers") in {"yes", "unknown"} or as_set(
            answers.get("extra_eea_providers")
        ) & {"cloud_hosting", "ai_api_models", "internal_saas", "unknown"}:
            needed.add("vendor_review")
    if "dpia_candidate" in tags:
        needed.add("dpia_process")
    if "ai_act_relevant" in tags:
        needed.update({"ai_documentation", "ai_policy", "training"})
    if "high_risk_ai_candidate" in tags:
        needed.update({"human_oversight", "ai_documentation"})
    elif as_set(answers.get("ai_functions")) & {"decision_support", "automated_decision"}:
        needed.add("human_oversight")

    return [CONTROL_LABELS[key] for key in sorted(needed) if key not in controls]


def build_company_memory(
    payload: dict[str, Any], *, require_complete: bool = False
) -> dict[str, Any]:
    """Create the deterministic, reusable company profile from questionnaire data."""
    answers = validate_questionnaire_payload(payload, require_complete=require_complete)
    tags = derive_tags(answers)
    missing_controls = derive_missing_controls(answers, tags)

    return {
        "memory_version": "0.1.0",
        "created_at": datetime.now(UTC).isoformat(),
        "source_questionnaire": payload.get("questionnaire"),
        "source_completed_at": payload.get("completed_at"),
        "company_profile": {
            "company_name": answers.get("company_name", ""),
            "contact_email": answers.get("contact_email", ""),
            "industry": answers.get("industry", ""),
            "company_size": answers.get("company_size", ""),
            "eu_presence": answers.get("eu_presence", []),
            "dashboard_priority": answers.get("dashboard_priority", ""),
        },
        "ai_profile": {
            "ai_usage": answers.get("ai_usage", []),
            "ai_functions": answers.get("ai_functions", []),
            "ai_notice": answers.get("ai_notice", ""),
            "sensitive_domains": answers.get("sensitive_domains", []),
            "delicate_ai_practices": answers.get("delicate_ai_practices", []),
        },
        "privacy_profile": {
            "personal_data": answers.get("personal_data", []),
            "profiling_decisions": answers.get("profiling_decisions", []),
            "privacy_role": answers.get("privacy_role", ""),
            "extra_eea_transfers": answers.get("extra_eea_transfers", ""),
            "extra_eea_providers": answers.get("extra_eea_providers", []),
        },
        "controls": {
            "existing": answers.get("controls", []),
            "missing_or_to_verify": missing_controls,
        },
        "relevance_tags": tags,
        "assessment_trace": build_assessment_trace(answers, tags, missing_controls),
        "compliance_score": calculate_compliance_score(answers, tags, missing_controls),
        "risk_warnings": build_warnings(answers, tags, missing_controls),
        "notes": answers.get("notes", ""),
    }


def calculate_compliance_score(
    answers: dict[str, Any], tags: list[str], missing_controls: list[str]
) -> dict[str, Any]:
    # This is an attention score for prioritization, not a legal classification.
    breakdown = build_assessment_trace(answers, tags, missing_controls)
    raw_score = sum(item["points"] for item in breakdown)
    score = min(raw_score, 100)
    if score >= 70:
        band = "high"
        label = "High attention"
    elif score >= 35:
        band = "medium"
        label = "Medium attention"
    else:
        band = "low"
        label = "Low attention"
    return {
        "score": score,
        "band": band,
        "label": label,
        "explanation": "Score combines relevance tags and missing controls. It is for prioritization, not legal classification.",
        "raw_score": raw_score,
        "breakdown": breakdown,
    }


def build_warnings(
    answers: dict[str, Any], tags: list[str], missing_controls: list[str]
) -> list[dict[str, Any]]:
    def linked_controls(tag: str) -> list[str]:
        allowed = WARNING_CONTROL_LINKS.get(tag, set())
        return [control for control in missing_controls if control in allowed]

    warnings = []
    if "prohibited_practice_review" in tags:
        warnings.append(
            {
                "level": "critical",
                "title": "Sensitive AI practice review required",
                "message": "Potential prohibited or sensitive AI practices were selected. Review before deployment or sale.",
                "triggered_by": triggered_answers(answers, "prohibited_practice_review"),
                "linked_missing_controls": linked_controls("prohibited_practice_review"),
                **TAG_EXPLANATIONS["prohibited_practice_review"],
            }
        )
    if "high_risk_ai_candidate" in tags:
        warnings.append(
            {
                "level": "high",
                "title": "Possible high-risk AI use case",
                "message": "The AI use case may fall into AI Act high-risk areas such as HR, education, credit, healthcare, or critical infrastructure.",
                "triggered_by": triggered_answers(answers, "high_risk_ai_candidate"),
                "linked_missing_controls": linked_controls("high_risk_ai_candidate"),
                **TAG_EXPLANATIONS["high_risk_ai_candidate"],
            }
        )
    if "dpia_candidate" in tags:
        warnings.append(
            {
                "level": "medium",
                "title": "DPIA candidate",
                "message": (
                    "The selected answers indicate DPIA screening factors, but the "
                    "questionnaire alone does not establish that a full DPIA is mandatory. "
                    "A DPIA is required when the planned processing is likely to result in "
                    "high risk; prior consultation follows only when the DPIA identifies "
                    "high residual risk without adequate mitigation."
                ),
                "triggered_by": triggered_answers(answers, "dpia_candidate"),
                "linked_missing_controls": linked_controls("dpia_candidate"),
                **TAG_EXPLANATIONS["dpia_candidate"],
            }
        )
    if "international_transfer_review" in tags:
        warnings.append(
            {
                "level": "medium",
                "title": "International transfer review",
                "message": "Extra EU/EEA providers or transfers should be mapped and verified.",
                "triggered_by": triggered_answers(answers, "international_transfer_review"),
                "linked_missing_controls": linked_controls("international_transfer_review"),
                **TAG_EXPLANATIONS["international_transfer_review"],
            }
        )
    if missing_controls:
        warnings.append(
            {
                "level": "medium",
                "title": "Missing controls",
                "message": "Some expected controls are missing or unclear: "
                + ", ".join(missing_controls[:5])
                + ".",
                "triggered_by": [{"question_key": "controls", "missing_values": missing_controls}],
                "linked_missing_controls": list(missing_controls),
                "legal_references": ["GDPR Article 24", "AI Act Articles 9 and 17"],
                "recommended_action": "Assign owners and evidence for each missing or unverified control.",
            }
        )
    if not warnings:
        warnings.append(
            {
                "level": "low",
                "title": "No major warning from current answers",
                "message": "No major risk signal was detected from the current questionnaire answers.",
                "triggered_by": [],
                "legal_references": [],
                "recommended_action": "Keep the profile current and repeat the assessment when processing or AI use changes.",
            }
        )
    return warnings


# ---------------------------------------------------------------------------
# Regulatory Matching Agent: company tags -> relevant events and news
# ---------------------------------------------------------------------------
def load_json_list(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    # A corrupt or hand-edited data file should degrade to "no data" like a
    # missing file, not abort the whole assessment with a decode error.
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    return value if isinstance(value, list) else []


def topic_labels_for_tags(tags: list[str]) -> set[str]:
    labels: set[str] = set()
    for tag in tags:
        labels.update(TAG_TO_TOPIC_LABELS.get(tag, set()))
    return labels


TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
    "ai",
    "eu",
    "new",
    "update",
    "updates",
}


def title_tokens(value: Any) -> set[str]:
    """Return stable title tokens used for conservative alert grouping."""
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(token) > 2 and token not in TITLE_STOPWORDS
    }


def titles_are_similar(left: Any, right: Any) -> bool:
    left_tokens = title_tokens(left)
    right_tokens = title_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    return overlap >= 0.72


def alert_priority(item: dict[str, Any], match_score: int) -> tuple[int, str, list[str]]:
    """Calculate an explainable review priority from relevance and evidence quality."""
    score = min(match_score, 70)
    reasons = [f"Company-profile relevance: {match_score}/100"]
    declared = str(item.get("overall_priority") or item.get("priority") or "").lower()
    if declared in {"high", "critical"}:
        score += 10
        reasons.append("Source pipeline marked the item as high priority")
    status = str(item.get("status", ""))
    is_official = bool(
        item.get("has_official_evidence")
        or item.get("is_official") is True
        or status.startswith("A_")
    )
    if is_official:
        score += 10
        reasons.append("Official or officially evidenced source")
    else:
        score -= 8
        reasons.append("Non-binding early-warning source")
    if status.startswith("A_"):
        score += 5
        reasons.append("Validated publication status")

    deadline_value = item.get("compliance_deadline") or item.get("effective_date")
    if deadline_value:
        try:
            deadline = datetime.fromisoformat(str(deadline_value).replace("Z", "+00:00"))
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=UTC)
            days = (deadline - datetime.now(UTC)).days
            if days < 0:
                score += 15
                reasons.append("Effective date or deadline has passed")
            elif days <= 30:
                score += 15
                reasons.append("Deadline within 30 days")
            elif days <= 90:
                score += 10
                reasons.append("Deadline within 90 days")
        except ValueError:
            pass

    score = max(0, min(score, 100))
    if score >= 85:
        label = "Critical"
    elif score >= 65:
        label = "High"
    elif score >= 40:
        label = "Medium"
    else:
        label = "Low"
    return score, label, reasons


def group_similar_alerts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group duplicate URLs and conservatively similar titles into one alert."""
    groups: list[dict[str, Any]] = []
    for item in items:
        item_url = str(item.get("url") or "").split("#", 1)[0].rstrip("/")
        match = next(
            (
                existing
                for existing in groups
                if (
                    item_url
                    and item_url == str(existing.get("url") or "").split("#", 1)[0].rstrip("/")
                )
                or (
                    item.get("regulation_area") == existing.get("regulation_area")
                    and titles_are_similar(item.get("title"), existing.get("title"))
                )
            ),
            None,
        )
        if match is None:
            item["duplicate_count"] = 1
            item["related_sources"] = []
            groups.append(item)
            continue
        match["duplicate_count"] += 1
        match["related_sources"].append(
            {
                "title": item.get("title"),
                "source": item.get("source"),
                "url": item.get("url"),
                "is_official": item.get("is_official"),
                "legal_status": item.get("legal_status"),
            }
        )
        match["matched_topics"] = sorted(
            set(match.get("matched_topics") or []) | set(item.get("matched_topics") or [])
        )
    return groups


def match_items_to_company(
    items: list[dict[str, Any]],
    tags: list[str],
    limit: int = 6,
) -> list[dict[str, Any]]:
    """Rank regulatory items against the company profile using transparent rules."""
    expected_topics = topic_labels_for_tags(tags)
    matched = []
    for item in items:
        item_topics = set(item.get("topic_labels") or [])
        regulation_area = str(item.get("regulation_area", ""))
        score = len(expected_topics & item_topics) * 20
        if "gdpr_relevant" in tags and regulation_area.startswith("GDPR"):
            score += 8
        if "ai_act_relevant" in tags and regulation_area.startswith("AI_ACT"):
            score += 8
        if "gpai_relevant" in tags and "AI_ACT_GPAI" in item_topics:
            score += 20
        if score <= 0:
            continue
        priority = str(item.get("overall_priority") or item.get("priority") or "")
        if priority.lower() == "high":
            score += 8
        if item.get("has_official_evidence") or str(item.get("status", "")).startswith("A_"):
            score += 6
        match_score = min(score, 100)
        priority_score, priority_label, priority_reasons = alert_priority(item, match_score)
        status = str(item.get("status", ""))
        is_official = bool(
            item.get("has_official_evidence")
            or item.get("is_official") is True
            or status.startswith("A_")
        )
        matched.append(
            {
                "match_score": match_score,
                "matched_topics": sorted(expected_topics & item_topics),
                "title": item.get("event_title") or item.get("title"),
                "regulation_area": item.get("regulation_area"),
                "topic_labels": item.get("topic_labels", []),
                "status": item.get("event_status") or item.get("status"),
                "priority": priority_label,
                "priority_score": priority_score,
                "priority_reasons": priority_reasons,
                "declared_priority": item.get("overall_priority") or item.get("priority"),
                "summary": item.get("summary"),
                "source": item.get("source") or item.get("source_name"),
                "retrieved_at": item.get("retrieved_at") or item.get("last_updated_at"),
                "recommended_attention": item.get("recommended_attention"),
                "source_category": item.get("source_category", "official_update"),
                "source_type": item.get("source_type"),
                "authority_level": item.get("authority_level"),
                "is_official": is_official,
                "legal_status": item.get("legal_status"),
                "effective_date": item.get("effective_date"),
                "compliance_deadline": item.get("compliance_deadline"),
                "url": (
                    item.get("primary_official_source_url")
                    or item.get("url")
                    or next(
                        (
                            evidence.get("url")
                            for evidence in item.get("evidence", [])
                            if evidence.get("url")
                        ),
                        None,
                    )
                ),
            }
        )
    ranked = sorted(
        matched,
        key=lambda item: (item["priority_score"], item["match_score"]),
        reverse=True,
    )
    return group_similar_alerts(ranked)[:limit]


def build_dashboard_context(
    memory: dict[str, Any],
    regulatory_events: list[dict[str, Any]] | None = None,
    article_feed: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    cards = []
    for tag in memory["relevance_tags"]:
        rule = TAG_RULES[tag]
        cards.append(
            {
                "tag": tag,
                "title": rule["label"],
                "summary": rule["dashboard_text"],
                "priority": priority_for_tag(tag),
            }
        )

    if memory["controls"]["missing_or_to_verify"]:
        cards.append(
            {
                "tag": "missing_controls",
                "title": "Controls to verify",
                "summary": "Missing or unclear controls: "
                + ", ".join(memory["controls"]["missing_or_to_verify"]),
                "priority": "medium",
            }
        )

    feed_items = article_feed or []
    official_feed = [
        item
        for item in feed_items
        if item.get("source_category", "official_update") != "early_warning"
    ]
    early_warning_feed = [
        item for item in feed_items if item.get("source_category") == "early_warning"
    ]
    matched_official_news = match_items_to_company(official_feed, memory["relevance_tags"], limit=6)
    matched_early_warnings = match_items_to_company(
        early_warning_feed, memory["relevance_tags"], limit=9
    )

    return {
        "company_name": memory["company_profile"]["company_name"],
        "compliance_score": memory["compliance_score"],
        "assessment_trace": memory["assessment_trace"],
        "risk_warnings": memory["risk_warnings"],
        "relevance_tags": memory["relevance_tags"],
        "dashboard_cards": cards,
        "matched_regulatory_events": match_items_to_company(
            regulatory_events or [], memory["relevance_tags"]
        ),
        "matched_news_feed": matched_official_news,
        "matched_early_warnings": matched_early_warnings,
        "compliance_timeline": build_compliance_timeline(memory["relevance_tags"]),
        "match_query_tags": memory["relevance_tags"],
        "match_query_topic_labels": sorted(topic_labels_for_tags(memory["relevance_tags"])),
        "next_matching_targets": [
            "module_web_scraping regulatory events",
            "source evidence records",
            "risk scoring rules",
            "dashboard output contract",
        ],
    }


def priority_for_tag(tag: str) -> str:
    if tag in {"prohibited_practice_review", "high_risk_ai_candidate"}:
        return "high"
    if tag in {"gdpr_relevant", "ai_act_relevant", "dpia_candidate"}:
        return "medium"
    return "low"


def build_compliance_timeline(tags: list[str]) -> list[dict[str, Any]]:
    """Return official AI Act milestones relevant to the active company profile."""
    if "ai_act_relevant" not in tags and "gpai_relevant" not in tags:
        return []
    milestones: list[dict[str, Any]] = [
        {
            "date": "2025-02-02",
            "title": "Prohibited-practice and AI-literacy provisions apply",
            "translation_key": "timeline_literacy",
            "applies_when": {"ai_act_relevant", "prohibited_practice_review"},
            "legal_reference": "AI Act Article 4 and Article 5",
            "basis": "applicable_law",
        },
        {
            "date": "2025-08-02",
            "title": "Governance rules and GPAI obligations apply",
            "translation_key": "timeline_gpai",
            "applies_when": {"gpai_relevant"},
            "legal_reference": "AI Act Chapters V and VII",
            "basis": "applicable_law",
        },
        {
            "date": "2026-08-02",
            "title": "General AI Act rules and Article 50 transparency obligations apply",
            "translation_key": "timeline_general",
            "applies_when": {"ai_act_relevant", "transparency_gap"},
            "legal_reference": "AI Act Article 113 and Article 50",
            "basis": "applicable_law",
        },
        {
            "date": "2026-08-02",
            "title": "Commission enforcement powers for GPAI obligations apply",
            "translation_key": "timeline_enforcement",
            "applies_when": {"gpai_relevant"},
            "legal_reference": "AI Act GPAI enforcement timeline",
            "basis": "applicable_law",
        },
        {
            "date": "2027-08-02",
            "title": "Transition deadline for GPAI models placed on the market before 2 August 2025",
            "translation_key": "timeline_legacy_gpai",
            "applies_when": {"gpai_relevant"},
            "legal_reference": "AI Act Article 111(3)",
            "basis": "applicable_law",
        },
        {
            "date": "2027-12-02",
            "title": "Standalone high-risk system rules under the 2026 simplification agreement",
            "translation_key": "timeline_high_risk",
            "applies_when": {"high_risk_ai_candidate"},
            "legal_reference": "Commission political agreement of 7 May 2026",
            "basis": "political_agreement",
            "source_url": AI_ACT_SIMPLIFICATION_AGREEMENT_SOURCE,
        },
        {
            "date": "2028-08-02",
            "title": "Product-embedded high-risk system rules under the 2026 simplification agreement",
            "translation_key": "timeline_embedded_high_risk",
            "applies_when": {"high_risk_ai_candidate"},
            "legal_reference": "Council and Parliament political agreement of 7 May 2026",
            "basis": "political_agreement",
            "source_url": AI_ACT_SIMPLIFICATION_AGREEMENT_SOURCE,
        },
    ]
    today = datetime.now(UTC).date()
    result = []
    active_tags = set(tags)
    for milestone in milestones:
        if not (active_tags & milestone["applies_when"]):
            continue
        date_value = datetime.fromisoformat(milestone["date"]).date()
        days_remaining = (date_value - today).days
        if milestone["basis"] == "political_agreement":
            status = "Political agreement - verify final legal text"
            status_code = "timeline_status_agreement"
        elif days_remaining < 0:
            status = "Applicable"
            status_code = "timeline_status_applicable"
        elif days_remaining == 0:
            status = "Due today"
            status_code = "timeline_status_today"
        else:
            status = "Upcoming"
            status_code = "timeline_status_upcoming"
        result.append(
            {
                "date": milestone["date"],
                "title": milestone["title"],
                "translation_key": milestone["translation_key"],
                "status": status,
                "status_code": status_code,
                "days_remaining": days_remaining,
                "legal_reference": milestone["legal_reference"],
                "basis": milestone["basis"],
                "source_url": milestone.get("source_url", AI_ACT_TIMELINE_SOURCE),
            }
        )
    return result


# ---------------------------------------------------------------------------
# Explanation Agent: deterministic context -> OpenAI narrative
#
# OpenAI never creates the score. It explains the already calculated memory and
# dashboard context, which remain the source of truth if the model is offline.
# ---------------------------------------------------------------------------
def build_model_prompt(memory: dict[str, Any], dashboard_context: dict[str, Any]) -> str:
    return (
        "You are an EU AI Act and GDPR compliance assistant. "
        "Use only the structured company memory and dashboard context below. "
        "Do not invent facts. Do not provide legal advice. "
        "Explain the initial relevance assessment in clear business language.\n\n"
        "Required output:\n"
        "1. Short company-specific summary\n"
        "2. Why GDPR may or may not be relevant\n"
        "3. Why AI Act may or may not be relevant\n"
        "4. Top 3 action priorities\n"
        "5. Missing information to ask the company\n\n"
        "COMPANY_MEMORY_JSON:\n"
        f"{json.dumps(memory, indent=2, ensure_ascii=False)}\n\n"
        "DASHBOARD_CONTEXT_JSON:\n"
        f"{json.dumps(dashboard_context, indent=2, ensure_ascii=False)}\n"
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Orchestration and command-line entry point
# ---------------------------------------------------------------------------
def run(
    input_path: Path,
    out_dir: Path,
    regulatory_events_path: Path | None = DEFAULT_REGULATORY_EVENTS,
    article_feed_path: Path | None = DEFAULT_ARTICLE_FEED,
) -> None:
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Questionnaire input file not found: {input_path}") from exc
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not read questionnaire JSON from {input_path}: {exc}") from exc
    memory = build_company_memory(payload, require_complete=True)
    regulatory_events = load_json_list(regulatory_events_path)
    article_feed = load_json_list(article_feed_path)
    dashboard_context = build_dashboard_context(memory, regulatory_events, article_feed)
    model_prompt = build_model_prompt(memory, dashboard_context)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "company_memory.json", memory)
    write_json(out_dir / "dashboard_context.json", dashboard_context)
    (out_dir / "model_prompt.txt").write_text(model_prompt, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build company memory from questionnaire answers.")
    parser.add_argument(
        "input_json", type=Path, help="JSON downloaded from the questionnaire form."
    )
    parser.add_argument(
        "--out", type=Path, default=Path("company_memory_output"), help="Output folder."
    )
    parser.add_argument(
        "--regulatory-events",
        type=Path,
        default=DEFAULT_REGULATORY_EVENTS,
        help="Regulatory events JSON generated by the web scraping module.",
    )
    parser.add_argument(
        "--article-feed",
        type=Path,
        default=DEFAULT_ARTICLE_FEED,
        help="Articles/news feed JSON generated by the web scraping module.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        run(args.input_json, args.out, args.regulatory_events, args.article_feed)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
