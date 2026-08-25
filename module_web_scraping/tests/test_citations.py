"""Tests for the citation-grade legal reference registry."""

import unittest

from module_web_scraping.citations import (
    LAST_VERIFIED,
    TOPIC_LEGAL_CITATIONS,
    citations_for_topics,
)
from module_web_scraping.scoring import REGULATORY_IMPACT_BY_TOPIC


class CitationRegistryTests(unittest.TestCase):
    def test_every_scored_topic_has_a_citation(self) -> None:
        # Guarantees a scored risk line can always answer "says who?".
        for topic in REGULATORY_IMPACT_BY_TOPIC:
            with self.subTest(topic=topic):
                self.assertIn(topic, TOPIC_LEGAL_CITATIONS)
                self.assertTrue(TOPIC_LEGAL_CITATIONS[topic])

    def test_citations_are_well_formed(self) -> None:
        for citations in TOPIC_LEGAL_CITATIONS.values():
            for citation in citations:
                self.assertIn(citation.instrument, {"EU AI Act", "GDPR"})
                self.assertTrue(citation.articles)
                self.assertTrue(citation.title)
                self.assertTrue(citation.url.startswith("https://eur-lex.europa.eu/"))
                self.assertEqual(citation.last_verified, LAST_VERIFIED)

    def test_lookup_deduplicates_and_preserves_order(self) -> None:
        result = citations_for_topics(["AI_ACT_HIGH_RISK", "AI_ACT_HIGH_RISK", "GDPR_DPIA"])
        signatures = [(c["celex"], c["articles"]) for c in result]
        self.assertEqual(len(signatures), len(set(signatures)))
        # High-risk (2 provisions) comes before the DPIA citation.
        self.assertEqual(result[0]["articles"], "Article 6")
        self.assertEqual(result[-1]["articles"], "Article 35")

    def test_unknown_topic_yields_no_citation(self) -> None:
        self.assertEqual(citations_for_topics(["NOT_A_REAL_TOPIC"]), [])

    def test_each_citation_is_json_serialisable_dict(self) -> None:
        result = citations_for_topics(["AI_ACT_TRANSPARENCY"])
        self.assertEqual(len(result), 1)
        self.assertEqual(
            set(result[0]),
            {"instrument", "celex", "articles", "title", "url", "last_verified"},
        )


if __name__ == "__main__":
    unittest.main()
