import json
import tempfile
import unittest
from pathlib import Path

from module_agents import CompanyProfileAgent, RegulatoryMatchingAgent, RegulatoryMonitoringAgent
from module_company_profile.dashboard.action_store import (
    derive_action_plan,
    sync_action_plan,
    update_action_task,
)

ROOT = Path(__file__).resolve().parents[2]


def hr_evaluation() -> dict:
    payload = json.loads(
        (
            ROOT
            / "module_company_profile"
            / "memory_agent"
            / "demo_profiles"
            / "02_hr_ai_high_risk.json"
        ).read_text(encoding="utf-8")
    )
    memory = CompanyProfileAgent().evaluate(payload)
    feed, metadata = RegulatoryMonitoringAgent(
        ROOT,
        ROOT / "module_web_scraping" / "source_registry_seed.csv",
        ROOT / "storage" / "web_scraping_outputs" / "live_articles_and_news_feed.json",
    ).load_active_feed()
    context = RegulatoryMatchingAgent(ROOT).evaluate(memory, feed)
    return {
        "questionnaire_payload": payload,
        "company_memory": memory,
        "dashboard_context": context,
        "feed_meta": metadata,
    }


class ActionStoreTests(unittest.TestCase):
    def test_plan_derives_prioritized_tasks_from_trusted_missing_controls(self):
        plan = derive_action_plan(hr_evaluation())
        self.assertEqual("acme-hr-ai", plan["plan_id"])
        self.assertEqual(8, len(plan["tasks"]))
        documentation = next(
            task for task in plan["tasks"] if task["title"] == "AI system documentation"
        )
        self.assertEqual("high", documentation["priority"])
        self.assertIn("Possible high-risk AI use case", documentation["warning_titles"])
        self.assertIn("AI Act Article 6 and Annex III", documentation["legal_references"])

    def test_human_approval_and_evidence_gate_task_progress(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = sync_action_plan(root, hr_evaluation())
            task_id = plan["tasks"][0]["id"]

            with self.assertRaisesRegex(ValueError, "Human approval"):
                update_action_task(root, plan["plan_id"], task_id, {"status": "in_progress"})
            with self.assertRaisesRegex(ValueError, "owner is required"):
                update_action_task(
                    root,
                    plan["plan_id"],
                    task_id,
                    {"status": "approved", "approved_by": "Founder"},
                )

            approved = update_action_task(
                root,
                plan["plan_id"],
                task_id,
                {"status": "approved", "owner": "Compliance Lead", "approved_by": "Founder"},
            )
            task = next(item for item in approved["tasks"] if item["id"] == task_id)
            self.assertEqual("approved", task["status"])
            self.assertEqual("Founder", task["approved_by"])
            self.assertTrue(task["approved_at"])

            with self.assertRaisesRegex(ValueError, "owner is required"):
                update_action_task(
                    root,
                    plan["plan_id"],
                    task_id,
                    {"status": "approved", "owner": ""},
                )

            with self.assertRaisesRegex(ValueError, "evidence note"):
                update_action_task(
                    root,
                    plan["plan_id"],
                    task_id,
                    {"status": "completed"},
                )
            completed = update_action_task(
                root,
                plan["plan_id"],
                task_id,
                {"status": "completed", "evidence": "Policy approved in governance review."},
            )
            task = next(item for item in completed["tasks"] if item["id"] == task_id)
            self.assertEqual("completed", task["status"])
            self.assertEqual(3, task["revision"])

    def test_sync_preserves_managed_state_and_archives_resolved_controls(self):
        evaluation = hr_evaluation()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = sync_action_plan(root, evaluation)
            task_id = plan["tasks"][0]["id"]
            update_action_task(
                root,
                plan["plan_id"],
                task_id,
                {"owner": "Product Lead", "due_date": "2026-08-01"},
            )

            refreshed = sync_action_plan(root, evaluation)
            task = next(item for item in refreshed["tasks"] if item["id"] == task_id)
            self.assertEqual("Product Lead", task["owner"])
            self.assertEqual("2026-08-01", task["due_date"])

            resolved = json.loads(json.dumps(evaluation))
            resolved["company_memory"]["controls"]["missing_or_to_verify"] = [
                control
                for control in resolved["company_memory"]["controls"]["missing_or_to_verify"]
                if f"control-{control.lower().replace(' ', '-')}" != task_id
            ]
            synced = sync_action_plan(root, resolved)
            self.assertNotIn(task_id, {item["id"] for item in synced["tasks"]})
            self.assertIn(task_id, {item["id"] for item in synced["archived_tasks"]})


if __name__ == "__main__":
    unittest.main()
