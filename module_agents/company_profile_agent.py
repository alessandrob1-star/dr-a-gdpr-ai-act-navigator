"""Company-profile agent: validate questionnaire answers and build company memory."""

from __future__ import annotations

from typing import Any

from module_company_profile.memory_agent.company_memory_agent import build_company_memory


class CompanyProfileAgent:
    """Turn a completed questionnaire into the deterministic company profile."""

    name = "Company Profile Agent"

    def evaluate(self, questionnaire: dict[str, Any]) -> dict[str, Any]:
        """Validate the public questionnaire contract and derive company memory."""
        return build_company_memory(questionnaire, require_complete=True)
