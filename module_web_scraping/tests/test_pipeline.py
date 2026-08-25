import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from module_web_scraping.cli import build_parser
from module_web_scraping.models import ValidationStatus
from module_web_scraping.pipeline import group_items_into_events, monitored_items_from_event_seed
from module_web_scraping.repository import load_sources
from module_web_scraping.source_monitor import (
    CandidateLink,
    deduplicate_items,
    is_low_value_link,
    monitor_source_from_html,
)
from module_web_scraping.storage import load_monitored_items, save_monitored_items
from module_web_scraping.topic_detection import detect_regulation_area, detect_topic_labels

ROOT = Path(__file__).resolve().parents[2]


class TopicDetectionTests(unittest.TestCase):
    def test_detects_ai_act_high_risk(self):
        labels = detect_topic_labels(
            "Draft high-risk AI classification guidance",
            "Draft guidance explains high-risk AI systems under Annex III.",
        )
        self.assertIn("AI_ACT_HIGH_RISK", labels)
        self.assertEqual(detect_regulation_area(labels), "AI_ACT")

    def test_detects_gdpr_ai_act_interplay(self):
        labels = detect_topic_labels(
            "GDPR and AI Act interplay",
            "Automated decision-making under GDPR and AI Act obligations.",
        )
        self.assertIn("GDPR_AUTOMATED_DECISION_MAKING", labels)
        self.assertIn("AI_ACT_GENERAL", labels)
        self.assertEqual(detect_regulation_area(labels), "GDPR_AI_ACT_INTERPLAY")


class PipelineTests(unittest.TestCase):
    def test_seed_pipeline_creates_dashboard_events(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        items = monitored_items_from_event_seed(
            ROOT / "data" / "demo-regulatory-events-seed.csv", sources
        )
        events = group_items_into_events(items)
        self.assertGreaterEqual(len(events), 5)
        statuses = {event.event_status for event in events}
        self.assertIn(ValidationStatus.OFFICIALLY_PUBLISHED, statuses)
        self.assertIn(ValidationStatus.OFFICIAL_DRAFT, statuses)
        self.assertIn(ValidationStatus.UNCONFIRMED_NEWS, statuses)

    def test_dashboard_output_contains_evidence_flags(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        items = monitored_items_from_event_seed(
            ROOT / "data" / "demo-regulatory-events-seed.csv", sources
        )
        event = group_items_into_events(items)[0]
        output = event.to_dashboard_dict()
        self.assertIn("has_official_evidence", output)
        self.assertIn("has_warning_sources", output)
        self.assertIn("evidence_count", output)

    def test_seed_status_cannot_promote_a_warning_source_to_official(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        with TemporaryDirectory() as tmpdir:
            seed = Path(tmpdir) / "events.csv"
            seed.write_text(
                "event_title,summary,regulation_area,event_status,source_name,source_url\n"
                '"AI Act warning","AI Act warning from news","AI_ACT",'
                '"A_OFFICIALLY_PUBLISHED","IAPP News","https://iapp.org/news/"\n',
                encoding="utf-8",
            )
            items = monitored_items_from_event_seed(seed, sources)
        event = group_items_into_events(items)[0]
        self.assertEqual(ValidationStatus.UNCONFIRMED_NEWS, event.event_status)


class SourceMonitorTests(unittest.TestCase):
    def test_static_html_monitor_extracts_relevant_links(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        source = next(src for src in sources if src.name == "European Commission AI Office")
        html = """
        <html><body>
          <a href="/ai-act/high-risk">Draft high-risk AI classification guidance under the AI Act</a>
          <a href="/unrelated">Football result</a>
        </body></html>
        """
        items = monitor_source_from_html(source, html)
        self.assertEqual(len(items), 1)
        self.assertIn("AI_ACT_HIGH_RISK", items[0].topic_labels)

    def test_deduplicate_items_uses_url_and_hash(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        source = next(src for src in sources if src.name == "European Commission AI Office")
        html = """
        <html><body>
          <a href="/ai-act/high-risk">Draft high-risk AI classification guidance under the AI Act</a>
          <a href="/ai-act/high-risk">Draft high-risk AI classification guidance under the AI Act</a>
        </body></html>
        """
        items = deduplicate_items(monitor_source_from_html(source, html))
        self.assertEqual(len(items), 1)

    def test_low_value_same_page_anchor_is_filtered(self):
        link = CandidateLink(
            title="The Structure of the AI Office",
            url="https://example.test/ai-office#structure",
        )
        self.assertTrue(is_low_value_link(link, "https://example.test/ai-office"))

    def test_embedded_style_and_script_are_not_included_in_link_title(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        source = next(src for src in sources if src.name == "European Commission AI Office")
        html = """
        <html><body>
          <a href="/news/ai-act-deadline">
            <style>.css-card{display:block;font-size:18px;}</style>
            <script>window.tracking = "AI Act";</script>
            The EU AI Act deadline moved, vendor questionnaires will not
          </a>
        </body></html>
        """

        items = monitor_source_from_html(source, html)

        self.assertEqual(len(items), 1)
        self.assertEqual(
            "The EU AI Act deadline moved, vendor questionnaires will not",
            items[0].title,
        )

    def test_css_contaminated_title_is_filtered(self):
        link = CandidateLink(
            title=(".css-card{overflow:hidden;font-size:18px;} The EU AI Act deadline moved"),
            url="https://example.test/news/ai-act-deadline",
        )

        self.assertTrue(is_low_value_link(link, "https://example.test/news"))


class CliTests(unittest.TestCase):
    def test_cli_parses_seed_dashboard_command(self):
        parser = build_parser()
        args = parser.parse_args(["seed-dashboard"])
        self.assertEqual(args.command, "seed-dashboard")

    def test_cli_parses_monitor_static_dashboard_command(self):
        parser = build_parser()
        args = parser.parse_args(["monitor-static-dashboard"])
        self.assertEqual(args.command, "monitor-static-dashboard")

    def test_cli_parses_eurlex_celex_envelope_command(self):
        parser = build_parser()
        args = parser.parse_args(["eurlex-celex-envelope", "32024R1689"])
        self.assertEqual(args.command, "eurlex-celex-envelope")
        self.assertEqual(args.celex_id, "32024R1689")

    def test_cli_parses_eurlex_keyword_envelope_command(self):
        parser = build_parser()
        args = parser.parse_args(["eurlex-keyword-envelope", "AI Act", "high-risk"])
        self.assertEqual(args.command, "eurlex-keyword-envelope")
        self.assertEqual(args.terms, ["AI Act", "high-risk"])

    def test_cli_parses_eurlex_celex_query_summary_flag(self):
        parser = build_parser()
        args = parser.parse_args(["eurlex-celex-query", "32024R1689", "--summary"])
        self.assertEqual(args.command, "eurlex-celex-query")
        self.assertTrue(args.summary)


class StorageTests(unittest.TestCase):
    def test_save_and_load_monitored_items_jsonl(self):
        sources = load_sources(ROOT / "data" / "source-registry-seed.csv")
        source = next(src for src in sources if src.name == "European Commission AI Office")
        html = """
        <html><body>
          <a href="/ai-act/high-risk">Draft high-risk AI classification guidance under the AI Act</a>
        </body></html>
        """
        items = monitor_source_from_html(source, html)
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "items.jsonl"
            save_monitored_items(path, items)
            loaded = load_monitored_items(path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, items[0].title)


if __name__ == "__main__":
    unittest.main()
