import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from module_web_scraping.live_feed import LIVE_SOURCE_NAMES, refresh_live_feed
from module_web_scraping.models import (
    AuthorityLevel,
    CollectionStatus,
    ItemType,
    MonitoredItem,
    Source,
)


class LiveFeedResilienceTests(unittest.TestCase):
    def test_failed_refresh_preserves_last_non_empty_feed(self):
        cached_item = {
            "title": "Last known official update",
            "source": "European Commission Digital Strategy News",
            "url": "https://example.test/update",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "feed.json"
            output_path.write_text(
                json.dumps(
                    {
                        "mode": "live",
                        "updated_at": "2026-07-03T10:00:00+00:00",
                        "sources": ["European Commission Digital Strategy News"],
                        "errors": [],
                        "items": [cached_item],
                    }
                ),
                encoding="utf-8",
            )

            with patch("module_web_scraping.live_feed.load_sources", return_value=[]):
                payload = refresh_live_feed(Path("unused.csv"), output_path)

            self.assertEqual("cached", payload["mode"])
            self.assertEqual([cached_item], payload["items"])
            self.assertEqual("2026-07-03T10:00:00+00:00", payload["updated_at"])
            self.assertIn("refresh_attempted_at", payload)
            self.assertTrue(payload["errors"])
            self.assertEqual(payload, json.loads(output_path.read_text(encoding="utf-8")))

    def test_empty_refresh_without_cache_stays_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "feed.json"

            with patch("module_web_scraping.live_feed.load_sources", return_value=[]):
                payload = refresh_live_feed(Path("unused.csv"), output_path)

            self.assertEqual("failed", payload["mode"])
            self.assertEqual([], payload["items"])
            self.assertTrue(payload["errors"])

    def test_navigation_titles_are_removed_and_output_is_atomic(self):
        sources = [
            Source(
                id=index,
                name=name,
                url=f"https://example.test/{index}",
                source_type="official_news",
                authority_level=AuthorityLevel.OFFICIAL_GUIDANCE,
                topic_area="AI_ACT",
                access_method="html",
                priority=1,
                active=True,
            )
            for index, name in enumerate(LIVE_SOURCE_NAMES, start=1)
        ]

        def monitored(source, limit):
            title = "data protection" if source.id == 1 else f"Regulatory update {source.id}"
            return [
                MonitoredItem(
                    id=source.id,
                    source_id=source.id,
                    source_name=source.name,
                    title=title,
                    url=f"https://example.test/item/{source.id}",
                    retrieved_at=datetime.now(UTC),
                    item_type=ItemType.NEWS_ARTICLE,
                    source_authority_level=source.authority_level,
                    regulation_area="AI_ACT",
                    topic_labels=["AI_ACT_GENERAL"],
                    collection_status=CollectionStatus.NEW,
                )
            ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "feed.json"
            with (
                patch("module_web_scraping.live_feed.load_sources", return_value=sources),
                patch("module_web_scraping.live_feed.monitor_source", side_effect=monitored),
            ):
                payload = refresh_live_feed(Path("unused.csv"), output_path)

            self.assertNotIn(
                "data protection", [item["title"].lower() for item in payload["items"]]
            )
            self.assertFalse(list(output_path.parent.glob("*.tmp")))
            self.assertEqual(payload, json.loads(output_path.read_text(encoding="utf-8")))

    def test_css_contaminated_titles_are_removed_from_live_feed(self):
        sources = [
            Source(
                id=index,
                name=name,
                url=f"https://example.test/{index}",
                source_type="official_news",
                authority_level=AuthorityLevel.OFFICIAL_GUIDANCE,
                topic_area="AI_ACT",
                access_method="html",
                priority=1,
                active=True,
            )
            for index, name in enumerate(LIVE_SOURCE_NAMES, start=1)
        ]

        def monitored(source, limit):
            title = (
                ".css-card{display:block;font-size:18px;} AI Act update"
                if source.id == 1
                else f"Regulatory AI Act update {source.id}"
            )
            return [
                MonitoredItem(
                    id=source.id,
                    source_id=source.id,
                    source_name=source.name,
                    title=title,
                    url=f"https://example.test/item/{source.id}",
                    retrieved_at=datetime.now(UTC),
                    item_type=ItemType.NEWS_ARTICLE,
                    source_authority_level=source.authority_level,
                    regulation_area="AI_ACT",
                    topic_labels=["AI_ACT_GENERAL"],
                    collection_status=CollectionStatus.NEW,
                    raw_text_hash=f"hash-{source.id}",
                )
            ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "feed.json"
            with (
                patch("module_web_scraping.live_feed.load_sources", return_value=sources),
                patch("module_web_scraping.live_feed.monitor_source", side_effect=monitored),
            ):
                payload = refresh_live_feed(Path("unused.csv"), output_path)

        titles = [item["title"] for item in payload["items"]]
        self.assertEqual(5, len(titles))
        self.assertFalse(any(title.startswith(".css-") for title in titles))


if __name__ == "__main__":
    unittest.main()
