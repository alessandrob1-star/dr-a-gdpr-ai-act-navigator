"""Smoke run for the scoring engine package container."""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
for parent in Path(__file__).resolve().parents:
    if (parent / "module_web_scraping").is_dir():
        sys.path.insert(0, str(parent))
        PROJECT_ROOT = parent
        break

from module_web_scraping.models import AuthorityLevel, ValidationStatus
from module_web_scraping.scoring import (
    priority_from_scores,
    recommended_attention,
    regulatory_impact,
    reliability_from_authorities,
    urgency_score,
)


def main() -> None:
    labels = ["AI_ACT_HIGH_RISK", "AI_ACT_TRANSPARENCY"]
    reliability = reliability_from_authorities(
        [AuthorityLevel.OFFICIAL_GUIDANCE, AuthorityLevel.TRUSTED_WARNING]
    )
    urgency = urgency_score(
        ValidationStatus.OFFICIAL_DRAFT,
        compliance_deadline=date.today() + timedelta(days=90),
    )
    impact = regulatory_impact(labels)
    priority = priority_from_scores(reliability, urgency, impact, business_impact_score=70)
    print(
        json.dumps(
            {
                "package": "scoring_engine",
                "labels": labels,
                "reliability_score": reliability,
                "urgency_score": urgency,
                "regulatory_impact_score": impact,
                "business_impact_score": 70,
                "overall_priority": priority.value,
                "recommended_attention": recommended_attention(priority),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
