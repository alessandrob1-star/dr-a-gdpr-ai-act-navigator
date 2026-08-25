import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from module_web_scraping.eurlex_webservice import (
    EurLexConfigError,
    EurLexCredentials,
    build_query_envelope,
    celex_query,
    keyword_query,
    run_query,
    summarize_response,
)


class EurLexWebserviceTests(unittest.TestCase):
    def test_credentials_are_loaded_from_environment_mapping(self):
        credentials = EurLexCredentials.from_environment(
            {
                "EURLEX_USERNAME": "demo-user",
                "EURLEX_PASSWORD": "demo-password",
            }
        )
        self.assertEqual(credentials.username, "demo-user")
        self.assertEqual(credentials.password, "demo-password")

    def test_missing_credentials_raise_clear_error(self):
        with self.assertRaises(EurLexConfigError):
            EurLexCredentials.from_environment({})

    def test_credentials_are_loaded_from_json_file(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "eurlex_credentials.json"
            path.write_text(
                '{"username": "json-user", "password": "json-password"}',
                encoding="utf-8",
            )

            credentials = EurLexCredentials.from_json_file(path)

        self.assertEqual(credentials.username, "json-user")
        self.assertEqual(credentials.password, "json-password")

    def test_load_prefers_json_file_over_environment(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "eurlex_credentials.json"
            path.write_text(
                '{"username": "json-user", "password": "json-password"}',
                encoding="utf-8",
            )

            credentials = EurLexCredentials.load(
                path=path,
                env={
                    "EURLEX_USERNAME": "env-user",
                    "EURLEX_PASSWORD": "env-password",
                },
            )

        self.assertEqual(credentials.username, "json-user")
        self.assertEqual(credentials.password, "json-password")

    def test_celex_query_builds_document_identifier_query(self):
        self.assertEqual(celex_query("32024R1689"), "DN = 32024R1689")

    def test_keyword_query_uses_expert_search_text_clauses(self):
        query = keyword_query("AI Act", "high-risk")
        self.assertEqual(query, 'TEXT = "AI Act" AND TEXT = "high-risk"')

    def test_query_envelope_escapes_xml_values(self):
        envelope = build_query_envelope(
            credentials=EurLexCredentials(
                username="demo-user",
                password="secret<&>",
            ),
            expert_query='TEXT = "AI & GDPR"',
            page=2,
            page_size=5,
            search_language="en",
        )

        self.assertIn("<wsse:Username>demo-user</wsse:Username>", envelope)
        self.assertIn("<wsse:Password>secret&lt;&amp;&gt;</wsse:Password>", envelope)
        self.assertIn("<eur:searchRequest>", envelope)
        self.assertNotIn("<eur:doQuery>", envelope)
        self.assertIn('<eur:expertQuery>TEXT = "AI &amp; GDPR"</eur:expertQuery>', envelope)
        self.assertIn("<eur:page>2</eur:page>", envelope)
        self.assertIn("<eur:pageSize>5</eur:pageSize>", envelope)
        self.assertIn("<eur:searchLanguage>en</eur:searchLanguage>", envelope)

    @patch("module_web_scraping.eurlex_webservice.urlopen")
    def test_run_query_uses_current_soap_action(self, mocked_urlopen):
        response = MagicMock()
        response.read.return_value = b"<searchResults />"
        mocked_urlopen.return_value.__enter__.return_value = response

        result = run_query(
            credentials=EurLexCredentials("demo-user", "demo-password"),
            expert_query="DN = 32024R1689",
        )

        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(result, "<searchResults />")
        self.assertEqual(
            request.get_header("Content-type"),
            'application/soap+xml; charset=utf-8; action="https://eur-lex.europa.eu/ws/doQuery"',
        )
        self.assertIn(b"<eur:searchRequest>", request.data)

    def test_query_envelope_rejects_invalid_page_size(self):
        with self.assertRaises(ValueError):
            build_query_envelope(
                credentials=EurLexCredentials("demo-user", "demo-password"),
                expert_query="DN = 32024R1689",
                page_size=0,
            )

    def test_summarize_response_extracts_unique_celex_ids(self):
        summary = summarize_response(
            """
            <response>
              <doc>32024R1689</doc>
              <doc>32016R0679</doc>
              <duplicate>32024R1689</duplicate>
            </response>
            """
        )

        self.assertEqual(summary.celex_ids, ["32016R0679", "32024R1689"])
        self.assertEqual(summary.likely_result_count, 2)
        self.assertGreater(summary.response_size_bytes, 0)


if __name__ == "__main__":
    unittest.main()
