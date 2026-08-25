import json
import os
import sys
import tempfile
import threading
import unittest
import zipfile
from http.client import HTTPConnection
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from module_agents import RegulatoryMonitoringAgent  # noqa: E402
from module_agents.dr_a_agent import (  # noqa: E402
    GroundingValidationError,
    _chat_request_body,
    allowed_legal_articles,
    build_chat_messages,
    build_chat_sources,
    compact_chat_context,
    generate_grounded_reply,
    local_model_config,
    model_reply_validation_issues,
    openai_model_config,
    regenerate_after_validation_failure,
    safe_validation_feedback,
    validated_stream_segments,
)
from module_company_profile.dashboard.dashboard_server import (  # noqa: E402
    MAX_REQUEST_BYTES,
    DashboardHandler,
    DashboardHTTPServer,
    RequestTooLarge,
    build_export_evaluation,
    dashboard_bind_address,
    evaluate_payload,
    load_demo_profile,
    read_request_json,
)
from module_company_profile.dashboard.profile_store import (  # noqa: E402
    compare_profile_snapshots,
    delete_profile_snapshot,
    list_profile_snapshots,
    load_profile_snapshot,
    save_profile_snapshot,
)
from module_company_profile.dashboard.report_exporter import (  # noqa: E402
    _register_pdf_fonts,
    build_docx_report,
    build_pdf_report,
)
from module_company_profile.dashboard.report_localizer import (  # noqa: E402
    load_report_locale,
    localize_result,
    localize_timeline_item,
    localize_ui,
)
from module_company_profile.memory_agent.company_memory_agent import (  # noqa: E402
    build_compliance_timeline,
)


class DashboardFeatureTests(unittest.TestCase):
    def setUp(self):
        self.evaluation = {
            "questionnaire_payload": {"answers": {"company_name": "Test AI"}},
            "company_memory": {
                "company_profile": {"company_name": "Test AI"},
                "controls": {"missing_or_to_verify": ["AI documentation"]},
            },
            "dashboard_context": {
                "company_name": "Test AI",
                "compliance_score": {"score": 72, "band": "high"},
                "relevance_tags": ["ai_act_relevant"],
                "risk_warnings": [],
                "compliance_timeline": build_compliance_timeline(["ai_act_relevant"]),
                "matched_regulatory_events": [],
            },
        }

    def test_profile_snapshot_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata = save_profile_snapshot(root, self.evaluation)
            self.assertEqual("Test AI", metadata["company_name"])
            self.assertEqual(1, len(list_profile_snapshots(root)))
            self.assertEqual(self.evaluation, load_profile_snapshot(root, metadata["id"]))

    def test_progress_contract_for_all_demo_profiles(self):
        expected = {
            "low-risk-saas": {
                "score": 44,
                "existing": 4,
                "missing": 4,
                "priorities": {"high": 0, "medium": 1, "low": 0},
            },
            "hr-ai": {
                "score": 100,
                "existing": 2,
                "missing": 8,
                "priorities": {"high": 1, "medium": 3, "low": 0},
            },
            "gpai-provider": {
                "score": 92,
                "existing": 4,
                "missing": 5,
                "priorities": {"high": 0, "medium": 3, "low": 0},
            },
        }

        for profile_id, contract in expected.items():
            with self.subTest(profile_id=profile_id):
                evaluation = evaluate_payload(load_demo_profile(profile_id))
                dashboard = evaluation["dashboard_context"]
                controls = evaluation["company_memory"]["controls"]
                priority_counts = {"high": 0, "medium": 0, "low": 0}
                for warning in dashboard["risk_warnings"]:
                    priority_counts[warning["level"]] += 1

                self.assertEqual(contract["score"], dashboard["compliance_score"]["score"])
                self.assertEqual(contract["existing"], len(controls["existing"]))
                self.assertEqual(contract["missing"], len(controls["missing_or_to_verify"]))
                self.assertEqual(contract["priorities"], priority_counts)
                self.assertTrue(dashboard["compliance_timeline"])
                for item in dashboard["compliance_timeline"]:
                    self.assertIsInstance(item["days_remaining"], int)
                    self.assertRegex(item["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_profile_snapshots_can_be_compared_and_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            older = save_profile_snapshot(root, self.evaluation)
            updated = json.loads(json.dumps(self.evaluation))
            updated["dashboard_context"]["compliance_score"]["score"] = 60
            updated["company_memory"]["controls"]["missing_or_to_verify"] = []
            newer = save_profile_snapshot(root, updated)
            comparison = compare_profile_snapshots(root, older["id"], newer["id"])
            self.assertEqual(-12, comparison["score_delta"])
            self.assertEqual(["AI documentation"], comparison["resolved_controls"])
            delete_profile_snapshot(root, older["id"])
            self.assertEqual(1, len(list_profile_snapshots(root)))

    def test_snapshots_from_different_companies_cannot_be_compared(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            older = save_profile_snapshot(root, self.evaluation)
            different = json.loads(json.dumps(self.evaluation))
            different["dashboard_context"]["company_name"] = "Other Company"
            newer = save_profile_snapshot(root, different)
            with self.assertRaisesRegex(ValueError, "same company"):
                compare_profile_snapshots(root, older["id"], newer["id"])

    def test_timeline_is_personalised_by_tags(self):
        self.assertEqual([], build_compliance_timeline(["gdpr_relevant"]))
        high_risk = build_compliance_timeline(["ai_act_relevant", "high_risk_ai_candidate"])
        self.assertTrue(any(item["date"] == "2027-12-02" for item in high_risk))
        self.assertTrue(any(item["date"] == "2028-08-02" for item in high_risk))
        self.assertTrue(
            all(
                item["basis"] == "political_agreement"
                for item in high_risk
                if item["date"] in {"2027-12-02", "2028-08-02"}
            )
        )

    def test_report_exports_are_valid_file_containers(self):
        pdf = build_pdf_report(self.evaluation)
        docx = build_docx_report(self.evaluation)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertTrue(docx.startswith(b"PK"))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.docx"
            path.write_bytes(docx)
            with zipfile.ZipFile(path) as archive:
                self.assertIn("word/document.xml", archive.namelist())

    def test_report_exports_follow_the_selected_local_language(self):
        italian_docx = build_docx_report(self.evaluation, language="it")
        dutch_docx = build_docx_report(self.evaluation, language="nl")
        with zipfile.ZipFile(BytesIO(italian_docx)) as archive:
            italian_xml = archive.read("word/document.xml").decode("utf-8")
        with zipfile.ZipFile(BytesIO(dutch_docx)) as archive:
            dutch_xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("ESPORTA REPORT DI CONFORMITÀ", italian_xml)
        self.assertIn("Punteggio di attenzione al rischio", italian_xml)
        self.assertIn("RAPPORT EXPORTEREN", dutch_xml)
        self.assertIn("Risico-aandachtsscore", dutch_xml)

    def test_all_local_report_dictionaries_are_available_offline(self):
        locale_codes = {
            "bg",
            "cs",
            "da",
            "de",
            "el",
            "en",
            "es",
            "et",
            "fi",
            "fr",
            "ga",
            "hr",
            "hu",
            "it",
            "lt",
            "lv",
            "mt",
            "nl",
            "pl",
            "pt",
            "ro",
            "sk",
            "sl",
            "sq",
            "sv",
        }
        locales_dir = (
            ROOT / "module_company_profile" / "dashboard" / "assets" / "js" / "i18n" / "locales"
        )
        self.assertEqual(locale_codes, {path.stem for path in locales_dir.glob("*.js")})
        evaluation = evaluate_payload(load_demo_profile("hr-ai"))
        for code in locale_codes:
            with self.subTest(language=code):
                self.assertTrue(load_report_locale(code)["ui"])
                self.assertTrue(localize_ui(code, "export_report"))
                self.assertTrue(localize_result(code, "high"))
                status, title = localize_timeline_item(
                    code,
                    {
                        "status_code": "timeline_status_upcoming",
                        "translation_key": "timeline_general",
                    },
                )
                self.assertTrue(status)
                self.assertTrue(title)

                self.assertTrue(build_docx_report(evaluation, language=code).startswith(b"PK"))
                self.assertTrue(build_pdf_report(evaluation, language=code).startswith(b"%PDF-"))

    def test_report_localizer_rejects_unknown_or_malformed_languages(self):
        for language in ("xx", "../en", "english", "", "it-IT"):
            with (
                self.subTest(language=language),
                self.assertRaisesRegex(ValueError, "Unsupported report language"),
            ):
                load_report_locale(language)

    def test_export_ignores_forged_derived_results(self):
        forged = {
            "evaluation": {
                "dashboard_context": {
                    "company_name": "Fabricated",
                    "compliance_score": {"score": 1, "band": "low"},
                }
            }
        }
        with self.assertRaisesRegex(ValueError, "completed questionnaire"):
            build_export_evaluation(forged)

        trusted = build_export_evaluation({"questionnaire_payload": load_demo_profile("hr-ai")})
        self.assertEqual("Acme HR AI", trusted["dashboard_context"]["company_name"])
        self.assertEqual(100, trusted["dashboard_context"]["compliance_score"]["score"])

    def test_pdf_report_embeds_a_unicode_font(self):
        evaluation = json.loads(json.dumps(self.evaluation))
        evaluation["dashboard_context"]["company_name"] = "Δοκιμή Éireann България"
        evaluation["company_memory"]["controls"]["missing_or_to_verify"] = [
            "Τεκμηρίωση συστήματος ΤΝ",
            "Документация на ИИ система",
        ]
        regular_font, bold_font = _register_pdf_fonts()
        pdf = build_pdf_report(evaluation)
        self.assertEqual(("NavigatorSans", "NavigatorSans-Bold"), (regular_font, bold_font))
        self.assertIn(b"/ToUnicode", pdf)

    def test_api_json_reader_rejects_non_objects_and_oversized_requests(self):
        array_body = b"[]"
        array_request = SimpleNamespace(
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Content-Length": str(len(array_body)),
            },
            rfile=BytesIO(array_body),
        )
        with self.assertRaisesRegex(ValueError, "must be an object"):
            read_request_json(array_request)  # type: ignore[arg-type]  # duck-typed request stub

        oversized_request = SimpleNamespace(
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(MAX_REQUEST_BYTES + 1),
            },
            rfile=BytesIO(),
        )
        with self.assertRaises(RequestTooLarge):
            read_request_json(oversized_request)  # type: ignore[arg-type]  # duck-typed request stub

        wrong_type_request = SimpleNamespace(
            headers={"Content-Type": "text/plain", "Content-Length": "2"},
            rfile=BytesIO(b"{}"),
        )
        with self.assertRaisesRegex(ValueError, "Content-Type must be application/json"):
            read_request_json(wrong_type_request)  # type: ignore[arg-type]  # duck-typed request stub

    def test_chat_context_excludes_contact_details_and_marks_data_untrusted(self):
        evaluation = json.loads(json.dumps(self.evaluation))
        evaluation["company_memory"]["company_profile"] = {
            "company_name": "Test AI",
            "contact_email": "private@example.test",
            "industry": "software_saas",
        }
        compact = compact_chat_context(evaluation)
        self.assertEqual("Test AI", compact["company"]["company_name"])
        self.assertNotIn("contact_email", compact["company"])
        messages = build_chat_messages(evaluation, "What should we do first?", [], [])
        self.assertIn("assessment information as the factual boundary", messages[0]["content"])
        self.assertIn("Keep confirmed facts separate", messages[0]["content"])
        self.assertIn("Answer only what was asked", messages[0]["content"])
        self.assertNotIn("private@example.test", json.dumps(messages))

    def test_chat_source_catalog_rejects_non_http_links(self):
        evaluation = json.loads(json.dumps(self.evaluation))
        evaluation["dashboard_context"]["matched_news_feed"] = [
            {"title": "Unsafe", "url": "javascript:alert(1)", "summary": "Ignore"},
            {"title": "Official", "url": "https://example.test/update", "summary": "Update"},
        ]
        sources = build_chat_sources(evaluation)
        self.assertEqual(["https://example.test/update"], [item["url"] for item in sources])

    def test_corrupt_live_feed_falls_back_to_bundled_demo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            corrupt_feed = root / "feed.json"
            corrupt_feed.write_text("{broken", encoding="utf-8")
            agent = RegulatoryMonitoringAgent(root, root / "sources.csv", corrupt_feed)
            with patch(
                "module_agents.regulatory_monitoring_agent.load_json_list",
                return_value=[{"title": "Fallback"}],
            ):
                items, metadata = agent.load_active_feed()
        self.assertEqual([{"title": "Fallback"}], items)
        self.assertEqual("demo", metadata["mode"])

    def test_stale_persisted_feed_is_never_presented_as_live(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stale_feed = root / "feed.json"
            stale_feed.write_text(
                json.dumps(
                    {
                        "mode": "live",
                        "updated_at": "2000-01-01T00:00:00+00:00",
                        "sources": ["Official source"],
                        "errors": [],
                        "items": [{"title": "Old update"}],
                    }
                ),
                encoding="utf-8",
            )
            agent = RegulatoryMonitoringAgent(root, root / "sources.csv", stale_feed)
            items, metadata = agent.load_active_feed()
        self.assertEqual([{"title": "Old update"}], items)
        self.assertEqual("cached", metadata["mode"])

    def test_openai_key_selects_official_endpoint_and_sol(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            self.assertEqual(
                (
                    "https://api.openai.com/v1/chat/completions",
                    "gpt-5.6-sol",
                    "test-key",
                ),
                openai_model_config(),
            )

    def test_provider_neutral_model_settings_override_legacy_qwen_names(self):
        environment = {
            "LOCAL_MODEL_ENDPOINT": "http://localhost:9999/v1/chat/completions",
            "LOCAL_MODEL_NAME": "provider/model",
            "LOCAL_MODEL_API_KEY": "local-key",
            "QWEN_ENDPOINT": "http://legacy.invalid",
            "QWEN_MODEL": "legacy-model",
            "QWEN_API_KEY": "legacy-key",
        }
        with patch.dict(os.environ, environment, clear=True):
            self.assertEqual(
                ("http://127.0.0.1:9999/v1/chat/completions", "provider/model", "local-key"),
                local_model_config(),
            )

    def test_qwen_web_launchers_select_local_provider(self):
        windows = (ROOT / "Start web page with Qwen.bat").read_text(encoding="utf-8")
        shell = (ROOT / "Start-Web-Page-Qwen.sh").read_text(encoding="utf-8")

        self.assertIn("MODEL_PROVIDER=local", windows)
        self.assertIn('MODEL_PROVIDER="local"', shell)
        self.assertIn("qwen2.5:14b-instruct", windows)
        self.assertIn("qwen2.5:14b-instruct", shell)
        self.assertIn("Start dashboard.bat", windows)
        self.assertIn("Start-Dashboard.sh", shell)

    def test_openai_runtime_uses_exact_sol_model_and_supported_token_parameter(self):
        messages = [{"role": "user", "content": "What should we prioritize?"}]
        body = _chat_request_body(
            "gpt-5.6-sol",
            messages,
            stream=True,
        )
        self.assertEqual("gpt-5.6-sol", body["model"])
        self.assertEqual(1200, body["max_completion_tokens"])
        self.assertTrue(body["stream"])
        self.assertNotIn("temperature", body)
        self.assertNotIn("max_tokens", body)

    def test_dashboard_bind_address_validates_the_configured_port(self):
        with patch.dict(
            os.environ,
            {"DASHBOARD_HOST": "127.0.0.1", "DASHBOARD_PORT": "8772"},
            clear=False,
        ):
            self.assertEqual(("127.0.0.1", 8772), dashboard_bind_address())
        for invalid in ("0", "65536", "not-a-port"):
            with (
                self.subTest(port=invalid),
                patch.dict(os.environ, {"DASHBOARD_PORT": invalid}, clear=False),
                self.assertRaisesRegex(ValueError, "between 1 and 65535"),
            ):
                dashboard_bind_address()

    def test_dashboard_server_rejects_concurrent_bind_and_does_not_hold_worker_threads(self):
        self.assertFalse(DashboardHTTPServer.allow_reuse_address)
        self.assertTrue(DashboardHTTPServer.daemon_threads)

    def test_dashboard_http_smoke_flow_and_security_headers(self):
        server = DashboardHTTPServer(("127.0.0.1", 0), DashboardHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def request(
            method: str,
            path: str,
            payload: dict | None = None,
            content_type: str = "application/json",
        ):
            body = json.dumps(payload).encode("utf-8") if payload is not None else None
            headers = {"Content-Type": content_type} if body is not None else {}
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            response_body = response.read()
            response_headers = dict(response.getheaders())
            connection.close()
            return response.status, response_headers, response_body

        model_status = {
            "model_configured": True,
            "model_reachable": True,
            "model_available": True,
        }
        try:
            with patch(
                "module_company_profile.dashboard.dashboard_server.openai_model_runtime_status",
                return_value=model_status,
            ):
                status, headers, body = request("GET", "/api/health")
            self.assertEqual(200, status)
            self.assertTrue(json.loads(body)["ok"])
            self.assertIn("application/json", headers["Content-Type"])

            status, headers, body = request("GET", "/")
            self.assertEqual(200, status)
            self.assertIn(b"Dr. G.D.P.R. &amp; AI Act navigator", body)
            self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
            self.assertEqual("nosniff", headers["X-Content-Type-Options"])

            status, _, body = request("POST", "/api/demo-profile", {"profile_id": "hr-ai"})
            self.assertEqual(200, status)
            self.assertEqual(
                100, json.loads(body)["dashboard_context"]["compliance_score"]["score"]
            )

            with (
                tempfile.TemporaryDirectory() as temp_dir,
                patch(
                    "module_company_profile.dashboard.dashboard_server.ACTION_PLAN_DIR",
                    Path(temp_dir),
                ),
            ):
                status, _, body = request(
                    "POST",
                    "/api/action-plan/sync",
                    {"questionnaire_payload": load_demo_profile("hr-ai")},
                )
                self.assertEqual(200, status)
                action_plan = json.loads(body)["action_plan"]
                self.assertEqual("acme-hr-ai", action_plan["plan_id"])
                self.assertEqual(8, len(action_plan["tasks"]))

                first_task = action_plan["tasks"][0]
                status, _, body = request(
                    "POST",
                    "/api/action-plan/update",
                    {
                        "plan_id": action_plan["plan_id"],
                        "task_id": first_task["id"],
                        "patch": {"status": "in_progress"},
                    },
                )
                self.assertEqual(400, status)
                self.assertIn("Human approval", json.loads(body)["error"])

            status, _, body = request(
                "POST",
                "/api/export-report",
                {
                    "format": "pdf",
                    "language": "../en",
                    "questionnaire_payload": load_demo_profile("hr-ai"),
                },
            )
            self.assertEqual(400, status)
            self.assertIn("Unsupported report language", json.loads(body)["error"])

            status, _, body = request(
                "POST", "/api/demo-profile", {"profile_id": "hr-ai"}, "text/plain"
            )
            self.assertEqual(400, status)
            self.assertIn("Content-Type must be application/json", json.loads(body)["error"])

            status, _, _ = request("GET", "/../../pyproject.toml")
            self.assertEqual(404, status)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        self.assertFalse(thread.is_alive())

    def test_launchers_validate_dashboard_identity_and_preserve_model_configuration(self):
        windows = (ROOT / "Start dashboard.bat").read_text(encoding="utf-8")
        shell = (ROOT / "Start-Dashboard.sh").read_text(encoding="utf-8")
        docker_windows = (ROOT / "Start with Docker.bat").read_text(encoding="utf-8")
        docker_shell = (ROOT / "start-demo.sh").read_text(encoding="utf-8")

        self.assertIn("$h.ok -ne $true", windows)
        self.assertIn("$h.model_configured -ne $true", windows)
        self.assertIn("%ROOT%module_company_profile\\dashboard\\dashboard_server.py", windows)
        self.assertIn('"ok"[[:space:]]*:[[:space:]]*true', shell)
        self.assertIn('"model_configured"[[:space:]]*:[[:space:]]*true', shell)
        self.assertIn("$h.ok -eq $true", docker_windows)
        self.assertIn('"ok"[[:space:]]*:[[:space:]]*true', docker_shell)

    def test_docker_runtime_matches_ci_and_keeps_the_dashboard_local(self):
        dockerfile = (ROOT / "module_company_profile" / "Dockerfile").read_text(encoding="utf-8")
        compose = (ROOT / "module_company_profile" / "docker-compose.yml").read_text(
            encoding="utf-8"
        )
        workflow = (ROOT / ".github" / "workflows" / "web-scraping-demo.yml").read_text(
            encoding="utf-8"
        )

        self.assertTrue(dockerfile.startswith("FROM python:3.12-slim\n"))
        self.assertIn('python-version: "3.12"', workflow)
        self.assertIn("COPY module_company_profile ./module_company_profile", dockerfile)
        self.assertIn("/app/module_company_profile/dashboard/dashboard_server.py", compose)
        self.assertIn('DASHBOARD_HOST: "0.0.0.0"', compose)
        self.assertIn('"127.0.0.1:8771:8771"', compose)

        dockerfiles = sorted(ROOT.rglob("Dockerfile"))
        self.assertGreaterEqual(len(dockerfiles), 7)
        for path in dockerfiles:
            with self.subTest(dockerfile=path.relative_to(ROOT)):
                self.assertTrue(
                    path.read_text(encoding="utf-8").startswith("FROM python:3.12-slim\n")
                )

    def test_model_output_validation_rejects_unsupported_claims_without_rewriting(self):
        context = {
            "legal_references": [
                "AI Act Article 6 and Annex III",
                "AI Act Articles 9-15",
                "GDPR Articles 35-36",
            ]
        }
        allowed = allowed_legal_articles(context)
        self.assertIn(6, allowed["AI Act"])
        self.assertNotIn(8, allowed["AI Act"])
        self.assertEqual(
            [],
            model_reply_validation_issues(
                "Review AI Act Articles 9-15 and GDPR Articles 35-36.", context
            ),
        )
        unsupported = model_reply_validation_issues("Review AI Act Articles 6-8.", context)
        self.assertTrue(any("7, 8" in issue for issue in unsupported))
        general_compliance = model_reply_validation_issues(
            "These steps ensure legal compliance.", context
        )
        self.assertFalse(any("Policy validation failed" in issue for issue in general_compliance))

    def test_question_scoped_validation_rejects_unlinked_controls(self):
        context = evaluate_payload(load_demo_profile("hr-ai"))
        context["active_user_message"] = (
            "Which missing controls are connected specifically to the DPIA candidate warning?"
        )
        issues = model_reply_validation_issues(
            "The connected controls are DPIA process and Records of processing.",
            context,
        )
        self.assertTrue(any("not linked" in issue for issue in issues))

        valid_issues = model_reply_validation_issues(
            "The connected missing control is the DPIA process.",
            context,
        )
        self.assertFalse(any("not linked" in issue for issue in valid_issues))

    def test_validation_rejects_dpia_stage_confusion(self):
        context = evaluate_payload(load_demo_profile("hr-ai"))
        context["active_user_message"] = "Does the questionnaire prove a DPIA is mandatory?"
        issues = model_reply_validation_issues(
            "If screening indicates high residual risk, a full DPIA is required.",
            context,
        )
        self.assertTrue(any("residual risk" in issue for issue in issues))

        context["active_user_message"] = (
            "What are the first three things this company should review?"
        )
        overview_issues = model_reply_validation_issues(
            "Run a DPIA screening. If the screening indicates high residual risk, "
            "prior consultation may be needed.",
            context,
        )
        self.assertTrue(any("residual risk" in issue for issue in overview_issues))

        supported_distinction = model_reply_validation_issues(
            "Run a DPIA screening to determine whether the planned processing is likely to "
            "result in high risk. Prior consultation applies only if the completed DPIA "
            "identifies high residual risk that cannot be adequately mitigated.",
            context,
        )
        self.assertFalse(any("residual risk" in issue for issue in supported_distinction))

    def test_validation_rejects_unsupported_transfer_mechanisms_and_corrupt_text(self):
        context = evaluate_payload(load_demo_profile("hr-ai"))
        context["active_user_message"] = "Which international transfer mechanisms should we use?"
        context["selected_chat_sources"] = []
        mechanism_issues = model_reply_validation_issues(
            "Use Standard Contractual Clauses (SCCs).",
            context,
        )
        self.assertTrue(any("transfer mechanism" in issue for issue in mechanism_issues))

        context["active_user_message"] = (
            "Why is the international transfer review relevant when information is unknown?"
        )
        general_transfer_issues = model_reply_validation_issues(
            "Use Standard Contractual Clauses. The company has international transfers.",
            context,
        )
        self.assertTrue(any("transfer mechanism" in issue for issue in general_transfer_issues))
        self.assertTrue(any("confirmed transfer" in issue for issue in general_transfer_issues))

        context["active_user_message"] = (
            "What are the first three things this company should review?"
        )
        overview_mechanism_issues = model_reply_validation_issues(
            "Review international transfers and use Standard Contractual Clauses.",
            context,
        )
        self.assertTrue(any("transfer mechanism" in issue for issue in overview_mechanism_issues))

        confirmed_transfer_issues = model_reply_validation_issues(
            "Map the providers and safeguards for these international transfers.",
            context,
        )
        self.assertTrue(any("confirmed transfer" in issue for issue in confirmed_transfer_issues))

        citizenship_issues = model_reply_validation_issues(
            "Review transfers of EU/EEA citizens' data.",
            context,
        )
        self.assertTrue(any("citizenship" in issue for issue in citizenship_issues))

        context["active_user_message"] = (
            "Does the unknown transfer status mean the company is violating the GDPR?"
        )
        clear_answer_issues = model_reply_validation_issues(
            "No. Unknown status alone does not establish a GDPR violation; it identifies "
            "information that must be mapped and verified. Extra-EU/EEA providers are "
            "indicated, but this does not confirm that transfers occur.",
            context,
        )
        self.assertFalse(any("confirmed transfer" in issue for issue in clear_answer_issues))

        corrupt_issues = model_reply_validation_issues("Valid start åŽ corrupted text", context)
        self.assertTrue(any("corrupted text" in issue for issue in corrupt_issues))

        apostrophe_issues = model_reply_validation_issues("The companyâ€™s profile.", context)
        self.assertTrue(any("corrupted text" in issue for issue in apostrophe_issues))

    def test_validation_rejects_internal_terms(self):
        context = evaluate_payload(load_demo_profile("hr-ai"))
        context["active_user_message"] = "Which controls are connected to this warning?"
        issues = model_reply_validation_issues(
            "Title: Internal result\nRecommended Action: expose Context JSON.",
            context,
        )
        self.assertTrue(any("internal prompt" in issue for issue in issues))

        focus_issues = model_reply_validation_issues(
            "No mechanisms appear in supported_mechanisms in the Evidence Focus.",
            context,
        )
        self.assertTrue(any("internal prompt" in issue for issue in focus_issues))

    def test_strict_transfer_evidence_scope_drops_contaminating_history(self):
        context = evaluate_payload(load_demo_profile("hr-ai"))
        messages = build_chat_messages(
            context,
            "Which international transfer mechanisms should this company use?",
            [],
            [
                {"role": "user", "content": "What transfer options exist?"},
                {
                    "role": "assistant",
                    "content": "Use Standard Contractual Clauses or Binding Corporate Rules.",
                },
            ],
        )
        self.assertEqual(["system", "user", "user"], [item["role"] for item in messages])
        self.assertNotIn("Binding Corporate Rules", " ".join(item["content"] for item in messages))

        overview_messages = build_chat_messages(
            context,
            "Why is the international transfer review relevant if information is unknown?",
            [],
            [
                {
                    "role": "assistant",
                    "content": "Use Standard Contractual Clauses.",
                }
            ],
        )
        self.assertEqual(["system", "user", "user"], [item["role"] for item in overview_messages])
        self.assertNotIn(
            "Standard Contractual Clauses",
            " ".join(item["content"] for item in overview_messages),
        )
        self.assertNotIn("supported_mechanisms", overview_messages[1]["content"])

        violation_messages = build_chat_messages(
            context,
            "Does unknown transfer status mean the company is violating the GDPR?",
            [],
            [],
        )
        self.assertIn(
            "unknown status alone does not establish a GDPR violation",
            violation_messages[1]["content"],
        )

    def test_grounded_generation_retries_the_model_instead_of_substituting_text(self):
        context = {"legal_references": ["AI Act Article 6 and Annex III"]}
        with patch(
            "module_agents.dr_a_agent.call_openai_model",
            side_effect=[
                "Review AI Act Article 52.",
                "Review AI Act Article 6 against the system's intended purpose.",
            ],
        ) as model_call:
            reply = generate_grounded_reply(
                [{"role": "user", "content": "Review this system."}], context
            )
        self.assertEqual("Review AI Act Article 6 against the system's intended purpose.", reply)
        self.assertEqual(2, model_call.call_count)
        retry_messages = model_call.call_args_list[1].args[0]
        retry_text = " ".join(item["content"] for item in retry_messages)
        self.assertNotIn("Article 52", retry_text)

    def test_validation_feedback_does_not_echo_unsupported_mechanism_names(self):
        feedback = safe_validation_feedback(
            [
                "Unsupported international-transfer mechanism: Standard Contractual Clauses.",
                "Unsupported international-transfer mechanism: Binding Corporate Rules.",
            ]
        )
        self.assertIn("not explicitly supported", feedback)
        self.assertNotIn("Standard Contractual Clauses", feedback)
        self.assertNotIn("Binding Corporate Rules", feedback)

    def test_correction_prompt_does_not_repeat_internal_evidence_label(self):
        context = evaluate_payload(load_demo_profile("hr-ai"))
        context["active_user_message"] = (
            "What transfer facts are confirmed, and what remains unresolved?"
        )
        context["selected_chat_sources"] = []
        messages = build_chat_messages(context, context["active_user_message"], [], [])
        failure = GroundingValidationError(
            "Unsupported international-transfer mechanism: Standard Contractual Clauses."
        )
        with patch(
            "module_agents.dr_a_agent.call_openai_model",
            return_value=(
                "Provider use is confirmed, while personal-data transfers and the applicable "
                "mechanism remain unresolved."
            ),
        ) as model_call:
            regenerate_after_validation_failure(messages, context, failure)
        correction = model_call.call_args.args[0][-1]["content"]
        self.assertNotIn("Evidence Focus", correction)
        self.assertNotIn("Standard Contractual Clauses", correction)

    def test_streaming_validates_each_complete_segment_before_display(self):
        context = {"legal_references": ["AI Act Article 6 and Annex III"]}
        segments = list(
            validated_stream_segments(
                iter(
                    [
                        "Review the intended purpose under AI Act Article ",
                        "6. Then document the classification decision.",
                    ]
                ),
                context,
            )
        )
        self.assertEqual(
            "Review the intended purpose under AI Act Article 6. "
            "Then document the classification decision.",
            "".join(segments),
        )

    def test_streaming_never_displays_a_segment_with_an_unsupported_article(self):
        context = {"legal_references": ["AI Act Article 6 and Annex III"]}
        first_segment = (
            "Start with the documented intended purpose and the actual company use case. "
        )
        stream = validated_stream_segments(
            iter([first_segment, "Then apply AI Act Article 52."]),
            context,
        )
        self.assertEqual(first_segment, next(stream))
        with self.assertRaisesRegex(GroundingValidationError, "article reference"):
            next(stream)

    def test_priority_workflow_is_grounded_but_generated_by_the_model(self):
        evaluation = evaluate_payload(load_demo_profile("hr-ai"))
        messages = build_chat_messages(
            evaluation,
            "What are the first three things this company should review?",
            [],
            [],
        )
        self.assertEqual("system", messages[0]["role"])
        self.assertIn(
            "Question:\nWhat are the first three things this company should review?",
            messages[-1]["content"],
        )
        self.assertNotIn("Authoritative assessment evidence", messages[-1]["content"])
        self.assertIn('"topic":"ordered_priorities"', messages[1]["content"])
        context_message = messages[1]["content"]
        self.assertIn("Possible high-risk AI use case", context_message)
        self.assertIn("DPIA candidate", context_message)
        self.assertIn("International transfer review", context_message)
        self.assertIn("AI system documentation", context_message)
        high_risk_warning = evaluation["dashboard_context"]["risk_warnings"][0]
        self.assertEqual(
            ["AI system documentation", "Internal AI policy", "Human oversight"],
            high_risk_warning["linked_missing_controls"],
        )
        self.assertIn("linked_missing_controls", context_message)
        self.assertNotIn("Article 52", context_message)
        self.assertIn("Answer only what was asked", messages[0]["content"])
        self.assertIn("without printing internal field labels", context_message)
        self.assertIn("personal-data transfers remain unresolved", context_message)
        self.assertLess(sum(len(item["content"]) for item in messages), 13_000)

    def test_public_evaluation_rejects_an_incomplete_questionnaire(self):
        with self.assertRaisesRegex(ValueError, "Questionnaire incomplete"):
            evaluate_payload({"answers": {"company_name": "Incomplete"}})


if __name__ == "__main__":
    unittest.main()
