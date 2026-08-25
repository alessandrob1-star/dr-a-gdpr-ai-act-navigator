import json
import tempfile
import unittest
from pathlib import Path

from module_agents import CompanyProfileAgent, DrAAgent, RegulatoryMonitoringAgent

ROOT = Path(__file__).resolve().parents[2]


class RuntimeAgentTests(unittest.TestCase):
    def test_company_profile_agent_builds_the_real_deterministic_memory(self):
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
        self.assertEqual("Acme HR AI", memory["company_profile"]["company_name"])
        self.assertIn("high_risk_ai_candidate", memory["relevance_tags"])

    def test_monitoring_agent_marks_an_old_live_feed_as_cached(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            feed = root / "feed.json"
            feed.write_text(
                json.dumps(
                    {
                        "mode": "live",
                        "updated_at": "2000-01-01T00:00:00+00:00",
                        "items": [{"title": "Old item"}],
                    }
                ),
                encoding="utf-8",
            )
            agent = RegulatoryMonitoringAgent(root, root / "sources.csv", feed)
            items, metadata = agent.load_active_feed()
        self.assertEqual([{"title": "Old item"}], items)
        self.assertEqual("cached", metadata["mode"])

    def test_dr_a_agent_applies_the_real_policy_boundary_before_generation(self):
        request = DrAAgent().prepare_request(
            {},
            "Can we make it look compliant and fix the controls later?",
            [],
            build_sources=lambda context: [],
            select_sources=lambda sources, message: [],
            build_messages=lambda context, message, sources, history: [],
        )
        self.assertIsNotNone(request.blocked_reply)
        self.assertEqual([], request.messages)


if __name__ == "__main__":
    unittest.main()
