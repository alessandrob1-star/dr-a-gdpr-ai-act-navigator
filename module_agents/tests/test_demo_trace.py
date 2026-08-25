import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, ClassVar

from module_agents.demo_trace import build_agent_trace, write_json_trace, write_markdown_trace

EXPECTED_AGENT_NAMES = [
    "Source Monitoring Agent",
    "Official Source Verification Agent",
    "Regulatory Validation Agent",
    "Risk Scoring Agent",
    "Demo Report Agent",
]


class AgentTraceTests(unittest.TestCase):
    trace: ClassVar[dict[str, Any]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.trace = build_agent_trace()

    def test_trace_contains_the_five_declared_service_agents_in_order(self) -> None:
        names = [step["agent_name"] for step in self.trace["steps"]]

        self.assertEqual(EXPECTED_AGENT_NAMES, names)

    def test_each_agent_has_an_auditable_structured_handoff(self) -> None:
        steps = self.trace["steps"]

        for index, step in enumerate(steps):
            with self.subTest(agent=step["agent_name"]):
                self.assertTrue(step["responsibility"].strip())
                self.assertTrue(step["input_summary"].strip())
                self.assertTrue(step["output_summary"].strip())
                self.assertTrue(step["evidence"])
                self.assertTrue(all(item.strip() for item in step["evidence"]))
                self.assertTrue(step["next_handoff"].strip())

                if index < len(steps) - 1:
                    self.assertEqual(steps[index + 1]["agent_name"], step["next_handoff"])

        self.assertEqual(
            "Dashboard, company-specific scoring, or assistant module.",
            steps[-1]["next_handoff"],
        )

    def test_trace_summary_matches_the_underlying_report(self) -> None:
        summary = self.trace["summary"]

        self.assertGreater(summary["sources_loaded"], 0)
        self.assertGreater(summary["monitored_items"], 0)
        self.assertGreater(summary["regulatory_events"], 0)
        self.assertEqual(summary["regulatory_events"], sum(summary["status_counts"].values()))
        self.assertEqual(summary["regulatory_events"], sum(summary["priority_counts"].values()))
        self.assertLessEqual(summary["official_events"], summary["regulatory_events"])
        self.assertLessEqual(summary["high_attention_events"], summary["regulatory_events"])

    def test_trace_writers_preserve_structure_and_boundary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "agent_trace.json"
            markdown_path = Path(tmpdir) / "agent_trace.md"

            write_json_trace(self.trace, json_path)
            write_markdown_trace(self.trace, markdown_path)

            saved_trace = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = markdown_path.read_text(encoding="utf-8")

        self.assertEqual(self.trace, saved_trace)
        self.assertIn("# Dr. G.D.P.R. & AI Act navigator - Agent Trace", markdown)
        self.assertIn("## Agent Steps", markdown)
        self.assertIn("## Boundary", markdown)
        for name in EXPECTED_AGENT_NAMES:
            self.assertIn(name, markdown)


if __name__ == "__main__":
    unittest.main()
