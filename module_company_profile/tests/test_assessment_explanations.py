import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from module_company_profile.memory_agent.company_memory_agent import (  # noqa: E402
    build_company_memory,
    build_dashboard_context,
)


class AssessmentExplanationTests(unittest.TestCase):
    def test_no_ai_and_no_personal_data_produces_no_regulatory_score(self):
        memory = build_company_memory(
            {
                "answers": {
                    "company_name": "No AI Company",
                    "eu_presence": ["eu_company"],
                    "ai_usage": ["no_ai"],
                    "sensitive_domains": ["none"],
                    "delicate_ai_practices": ["none"],
                    "personal_data": ["no_personal_data"],
                    "profiling_decisions": ["no"],
                    "extra_eea_transfers": "no",
                    "extra_eea_providers": ["no"],
                    "controls": ["none"],
                }
            }
        )
        self.assertEqual([], memory["relevance_tags"])
        self.assertEqual([], memory["controls"]["missing_or_to_verify"])
        self.assertEqual(0, memory["compliance_score"]["score"])

    def test_sensitive_domain_without_ai_is_not_high_risk_ai(self):
        memory = build_company_memory(
            {
                "answers": {
                    "eu_presence": ["eu_company"],
                    "sensitive_domains": ["recruiting"],
                    "personal_data": ["no_personal_data"],
                    "controls": ["none"],
                }
            }
        )
        self.assertNotIn("high_risk_ai_candidate", memory["relevance_tags"])

    def test_rejects_contradictory_checkbox_answers(self):
        with self.assertRaisesRegex(ValueError, "exclusive answer"):
            build_company_memory(
                {
                    "answers": {
                        "ai_usage": ["no_ai", "ai_provider"],
                    }
                }
            )

    def test_rejects_cross_question_no_ai_conflicts(self):
        with self.assertRaisesRegex(ValueError, "no_ai"):
            build_company_memory(
                {
                    "answers": {
                        "ai_usage": ["no_ai"],
                        "ai_functions": ["automated_decision"],
                    }
                }
            )

    def test_rejects_cross_question_no_personal_data_conflicts(self):
        with self.assertRaisesRegex(ValueError, "no_personal_data"):
            build_company_memory(
                {
                    "answers": {
                        "personal_data": ["no_personal_data"],
                        "profiling_decisions": ["profiling"],
                    }
                }
            )

    def test_high_risk_profile_explains_score_and_warning(self):
        payload = {
            "answers": {
                "company_name": "Example HR AI",
                "eu_presence": ["eu_company"],
                "ai_usage": ["customer_product_ai"],
                "sensitive_domains": ["recruiting"],
                "personal_data": ["employees_candidates"],
                "profiling_decisions": ["significant_automated_decisions"],
                "controls": [],
            }
        }
        memory = build_company_memory(payload)
        self.assertEqual("high", memory["compliance_score"]["band"])
        warning = next(
            item
            for item in memory["risk_warnings"]
            if item["title"] == "Possible high-risk AI use case"
        )
        selected_values = {
            value for evidence in warning["triggered_by"] for value in evidence["selected_values"]
        }
        self.assertIn("customer_product_ai", selected_values)
        self.assertIn("recruiting", selected_values)
        self.assertIn("AI Act Article 6 and Annex III", warning["legal_references"])
        rules = {item["rule_id"] for item in memory["compliance_score"]["breakdown"]}
        self.assertIn("high_risk_ai_candidate", rules)

    def test_profiles_produce_different_explainable_scores(self):
        low = build_company_memory({"answers": {"company_name": "Low", "controls": []}})
        gpai = build_company_memory(
            {
                "answers": {
                    "company_name": "GPAI",
                    "eu_presence": ["eu_market"],
                    "ai_usage": ["gpai"],
                    "controls": [
                        "privacy_policy",
                        "records_processing",
                        "breach_process",
                        "vendor_review",
                    ],
                }
            }
        )
        self.assertNotEqual(low["compliance_score"]["score"], gpai["compliance_score"]["score"])
        self.assertTrue(all(item["recommended_action"] for item in gpai["assessment_trace"]))

    def test_dpia_warning_exposes_only_the_answers_that_triggered_it(self):
        memory = build_company_memory(
            {
                "answers": {
                    "eu_presence": ["eu_company"],
                    "personal_data": ["tracking_analytics"],
                    "profiling_decisions": ["profiling", "human_review_decision_support"],
                    "controls": [],
                }
            }
        )
        warning = next(
            item for item in memory["risk_warnings"] if item["title"] == "DPIA candidate"
        )
        selected_values = {
            value for evidence in warning["triggered_by"] for value in evidence["selected_values"]
        }
        self.assertEqual(
            {"tracking_analytics", "profiling", "human_review_decision_support"},
            selected_values,
        )
        self.assertNotIn("sensitive data", warning["message"])
        self.assertNotIn("minors data", warning["message"])
        self.assertIn("DPIA is required", warning["message"])
        self.assertIn("does not establish that a full DPIA is mandatory", warning["message"])
        self.assertIn("prior consultation follows only", warning["message"])
        self.assertIn("high residual risk", warning["recommended_action"])

    def test_missing_controls_are_personalised_to_the_actual_profile(self):
        low_risk = build_company_memory(
            {
                "answers": {
                    "eu_presence": ["eu_company"],
                    "ai_usage": ["internal_ai"],
                    "ai_functions": ["content_generation"],
                    "personal_data": ["contact_account"],
                    "extra_eea_transfers": "no",
                    "extra_eea_providers": ["no"],
                    "controls": [],
                }
            }
        )
        missing = low_risk["controls"]["missing_or_to_verify"]
        self.assertIn("AI or privacy training", missing)
        self.assertIn("Data subject rights process", missing)
        self.assertNotIn("Human oversight", missing)
        self.assertNotIn("Vendor review", missing)
        control_trace = next(
            item for item in low_risk["assessment_trace"] if item["rule_id"] == "missing_controls"
        )
        self.assertNotIn("AI Act Articles 9-17", control_trace["legal_references"])

    def test_dashboard_separates_official_updates_from_early_warnings(self):
        memory = build_company_memory(
            {
                "answers": {
                    "company_name": "AI company",
                    "eu_presence": ["eu_market"],
                    "ai_usage": ["customer_product_ai"],
                    "controls": [],
                }
            }
        )
        common = {
            "regulation_area": "AI_ACT",
            "topic_labels": ["AI_ACT_GENERAL"],
            "priority": "Review",
            "summary": "Relevant update",
        }
        feed = [
            {
                **common,
                "title": "Official Commission update",
                "url": "https://example.test/official",
                "source_category": "official_update",
                "is_official": True,
            },
            {
                **common,
                "title": "Trusted expert analysis",
                "url": "https://example.test/commentary",
                "source_category": "early_warning",
                "is_official": False,
                "legal_status": "Non-binding commentary",
            },
        ]

        context = build_dashboard_context(memory, article_feed=feed)

        self.assertEqual(
            ["Official Commission update"],
            [item["title"] for item in context["matched_news_feed"]],
        )
        self.assertEqual(
            ["Trusted expert analysis"],
            [item["title"] for item in context["matched_early_warnings"]],
        )
        self.assertEqual(
            "Non-binding commentary",
            context["matched_early_warnings"][0]["legal_status"],
        )


if __name__ == "__main__":
    unittest.main()
