"""Tests for the regulatory freshness diff."""

import unittest

from module_web_scraping.regulatory_diff import diff_regulatory_events, render_diff_markdown


def _event(event_id: int, **overrides: object) -> dict:
    base = {
        "event_id": event_id,
        "event_title": f"Event {event_id}",
        "event_status": "A_OFFICIALLY_PUBLISHED",
        "overall_priority": "High",
        "reliability_score": 90,
        "urgency_score": 50,
        "regulatory_impact_score": 80,
        "business_impact_score": None,
        "recommended_attention": "Action recommended",
        "effective_date": None,
        "compliance_deadline": None,
        "last_updated_at": "2026-07-01T00:00:00+00:00",
    }
    base.update(overrides)
    return base


class RegulatoryDiffTests(unittest.TestCase):
    def test_detects_added_and_removed(self) -> None:
        old = [_event(1), _event(2)]
        new = [_event(1), _event(3)]
        report = diff_regulatory_events(old, new)
        self.assertEqual(report["summary"]["added"], 1)
        self.assertEqual(report["summary"]["removed"], 1)
        self.assertEqual(report["added"][0]["event_id"], 3)
        self.assertEqual(report["removed"][0]["event_id"], 2)

    def test_detects_field_changes(self) -> None:
        old = [_event(1, overall_priority="Medium", urgency_score=40)]
        new = [_event(1, overall_priority="Critical", urgency_score=85)]
        report = diff_regulatory_events(old, new)
        self.assertEqual(report["summary"]["changed"], 1)
        changes = report["changed"][0]["changes"]
        self.assertEqual(changes["overall_priority"], {"from": "Medium", "to": "Critical"})
        self.assertEqual(changes["urgency_score"], {"from": 40, "to": 85})

    def test_identical_snapshots_report_no_changes(self) -> None:
        events = [_event(1), _event(2)]
        report = diff_regulatory_events(events, list(events))
        self.assertEqual(report["summary"]["added"], 0)
        self.assertEqual(report["summary"]["removed"], 0)
        self.assertEqual(report["summary"]["changed"], 0)
        self.assertIn("No changes", render_diff_markdown(report))

    def test_deterministic_generated_at_passthrough(self) -> None:
        report = diff_regulatory_events([], [], generated_at="2026-07-13T00:00:00+00:00")
        self.assertEqual(report["generated_at"], "2026-07-13T00:00:00+00:00")

    def test_markdown_lists_changes(self) -> None:
        old = [_event(1, overall_priority="Medium")]
        new = [_event(1, overall_priority="Critical"), _event(9)]
        markdown = render_diff_markdown(diff_regulatory_events(old, new))
        self.assertIn("What Changed", markdown)
        self.assertIn("Medium → Critical", markdown)
        self.assertIn("Event 9", markdown)


if __name__ == "__main__":
    unittest.main()
