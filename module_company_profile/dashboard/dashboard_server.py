"""Local interactive dashboard server for company compliance profiles."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_DIR = Path(__file__).resolve().parent
SOURCE_REGISTRY = ROOT / "module_web_scraping" / "source_registry_seed.csv"
LIVE_FEED_FILE = ROOT / "storage" / "web_scraping_outputs" / "live_articles_and_news_feed.json"
PROFILE_HISTORY_DIR = ROOT / "storage" / "company_profile" / "history"
ACTION_PLAN_DIR = ROOT / "storage" / "company_profile" / "action_plans"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8771
MAX_REQUEST_BYTES = 2 * 1024 * 1024

sys.path.insert(0, str(ROOT))
from module_agents import (  # noqa: E402
    CompanyProfileAgent,
    DrAAgent,
    RegulatoryMatchingAgent,
    RegulatoryMonitoringAgent,
)
from module_agents.dr_a_agent import (  # noqa: E402
    DEFAULT_ASSISTANT_NAME,
    GroundingValidationError,
    OpenAIModelError,
    build_chat_messages,
    build_chat_sources,
    configured_model_runtime_status,
    generate_grounded_reply,
    regenerate_after_validation_failure,
    select_supported_sources,
    stream_configured_model,
    validated_stream_segments,
)
from module_company_profile.dashboard.action_store import (  # noqa: E402
    sync_action_plan,
    update_action_task,
)
from module_company_profile.dashboard.profile_store import (  # noqa: E402
    compare_evaluations,
    delete_profile_snapshot,
    list_profile_snapshots,
    load_profile_snapshot,
    save_profile_snapshot,
)
from module_company_profile.dashboard.report_exporter import (  # noqa: E402
    build_docx_report,
    build_pdf_report,
)

COMPANY_PROFILE_AGENT = CompanyProfileAgent()
REGULATORY_MATCHING_AGENT = RegulatoryMatchingAgent(ROOT)
REGULATORY_MONITORING_AGENT = RegulatoryMonitoringAgent(
    ROOT,
    SOURCE_REGISTRY,
    LIVE_FEED_FILE,
)
DR_A_AGENT = DrAAgent()
openai_model_runtime_status = configured_model_runtime_status
stream_openai_model = stream_configured_model


class DashboardHTTPServer(ThreadingHTTPServer):
    """Threaded local server that rejects concurrent binds cleanly."""

    # On Windows SO_REUSEADDR can permit overlapping server processes. Keep
    # the exclusive bind while allowing request threads to close with the app.
    allow_reuse_address = False
    daemon_threads = True


def dashboard_bind_address() -> tuple[str, int]:
    """Return a validated host and TCP port from the local configuration."""
    host = os.getenv("DASHBOARD_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
    raw_port = os.getenv("DASHBOARD_PORT", str(DEFAULT_PORT)).strip()
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("DASHBOARD_PORT must be an integer between 1 and 65535.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("DASHBOARD_PORT must be an integer between 1 and 65535.")
    return host, port


class RequestTooLarge(ValueError):
    """Raised when an API request exceeds the local server safety limit."""


def json_response(
    handler: BaseHTTPRequestHandler, payload: dict[str, Any], status: int = 200
) -> None:
    body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def file_response(
    handler: BaseHTTPRequestHandler,
    body: bytes,
    content_type: str,
    filename: str,
) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_request_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    content_type = handler.headers.get("Content-Type", "")
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type != "application/json":
        raise ValueError("Content-Type must be application/json.")
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError as exc:
        raise ValueError("Invalid Content-Length header.") from exc
    if length < 0 or length > MAX_REQUEST_BYTES:
        raise RequestTooLarge("JSON request body is too large.")
    raw = handler.rfile.read(length)
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON request body must be an object.")
    return payload


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Run the explicit company, monitoring, and matching agent handoffs."""
    memory = COMPANY_PROFILE_AGENT.evaluate(payload)
    article_feed, feed_meta = REGULATORY_MONITORING_AGENT.load_active_feed()
    dashboard_context = REGULATORY_MATCHING_AGENT.evaluate(memory, article_feed)
    return {
        "questionnaire_payload": payload,
        "company_memory": memory,
        "dashboard_context": dashboard_context,
        "feed_meta": feed_meta,
    }


def build_export_evaluation(payload: dict[str, Any]) -> dict[str, Any]:
    """Rebuild report input from questionnaire answers, ignoring derived client data."""
    questionnaire = payload.get("questionnaire_payload")
    if not isinstance(questionnaire, dict):
        raise ValueError("A completed questionnaire is required for report export.")
    return evaluate_payload(questionnaire)


def load_demo_profile(profile_id: str) -> dict[str, Any]:
    demo_profiles = {
        "low-risk-saas": ROOT
        / "module_company_profile"
        / "memory_agent"
        / "demo_profiles"
        / "01_low_risk_saas.json",
        "hr-ai": ROOT
        / "module_company_profile"
        / "memory_agent"
        / "demo_profiles"
        / "02_hr_ai_high_risk.json",
        "gpai-provider": ROOT
        / "module_company_profile"
        / "memory_agent"
        / "demo_profiles"
        / "03_gpai_provider.json",
    }
    path = demo_profiles.get(profile_id)
    if not path:
        raise ValueError(f"Unknown demo profile: {profile_id}")
    return json.loads(path.read_text(encoding="utf-8"))


class DashboardHandler(BaseHTTPRequestHandler):
    """Thin HTTP adapter connecting the browser UI to the local agents."""

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[dashboard] {self.address_string()} - {format % args}")

    def do_GET(self) -> None:
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path in {"/", "/dashboard"}:
            self.serve_file(DASHBOARD_DIR / "index.html")
            return
        if parsed_path.path == "/api/health":
            model_status = openai_model_runtime_status()
            json_response(
                self,
                {
                    "ok": True,
                    **model_status,
                    "assistant_name": os.getenv("ASSISTANT_NAME", DEFAULT_ASSISTANT_NAME),
                },
            )
            return
        if parsed_path.path == "/api/profiles":
            json_response(self, {"profiles": list_profile_snapshots(PROFILE_HISTORY_DIR)})
            return
        requested = (DASHBOARD_DIR / parsed_path.path.lstrip("/")).resolve()
        if DASHBOARD_DIR in requested.parents and requested.exists() and requested.is_file():
            self.serve_file(requested)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        # API routes only orchestrate work; assessment logic stays in the agents.
        try:
            if self.path == "/api/evaluate":
                payload = read_request_json(self)
                json_response(self, evaluate_payload(payload))
                return
            if self.path == "/api/demo-profile":
                payload = read_request_json(self)
                profile = load_demo_profile(str(payload.get("profile_id", "")))
                json_response(self, evaluate_payload(profile))
                return
            if self.path == "/api/refresh-news":
                payload = read_request_json(self)
                REGULATORY_MONITORING_AGENT.refresh()
                json_response(self, evaluate_payload(payload))
                return
            if self.path == "/api/profile/save":
                payload = read_request_json(self)
                evaluation = payload.get("evaluation")
                if not isinstance(evaluation, dict):
                    raise ValueError("A completed assessment is required.")
                questionnaire = evaluation.get("questionnaire_payload")
                if not isinstance(questionnaire, dict):
                    raise ValueError("The assessment questionnaire is missing.")
                snapshot = save_profile_snapshot(
                    PROFILE_HISTORY_DIR,
                    evaluate_payload(questionnaire),
                )
                json_response(self, {"snapshot": snapshot})
                return
            if self.path == "/api/profile/load":
                payload = read_request_json(self)
                stored_evaluation = load_profile_snapshot(
                    PROFILE_HISTORY_DIR,
                    str(payload.get("profile_id") or ""),
                )
                questionnaire = stored_evaluation.get("questionnaire_payload")
                if not isinstance(questionnaire, dict):
                    raise ValueError("Stored profile questionnaire is missing.")
                evaluation = evaluate_payload(questionnaire)
                json_response(self, evaluation)
                return
            if self.path == "/api/profile/delete":
                payload = read_request_json(self)
                delete_profile_snapshot(
                    PROFILE_HISTORY_DIR,
                    str(payload.get("profile_id") or ""),
                )
                json_response(self, {"deleted": True})
                return
            if self.path == "/api/profile/compare":
                payload = read_request_json(self)
                older_id = str(payload.get("older_id") or "")
                newer_id = str(payload.get("newer_id") or "")
                older_stored = load_profile_snapshot(PROFILE_HISTORY_DIR, older_id)
                newer_stored = load_profile_snapshot(PROFILE_HISTORY_DIR, newer_id)
                older_questionnaire = older_stored.get("questionnaire_payload")
                newer_questionnaire = newer_stored.get("questionnaire_payload")
                if not isinstance(older_questionnaire, dict) or not isinstance(
                    newer_questionnaire, dict
                ):
                    raise ValueError("Stored profile questionnaire is missing.")
                comparison = compare_evaluations(
                    evaluate_payload(older_questionnaire),
                    evaluate_payload(newer_questionnaire),
                    older_id,
                    newer_id,
                )
                json_response(self, {"comparison": comparison})
                return
            if self.path == "/api/action-plan/sync":
                payload = read_request_json(self)
                questionnaire = payload.get("questionnaire_payload")
                if not isinstance(questionnaire, dict):
                    raise ValueError("A completed questionnaire is required for the action plan.")
                # Rebuild the assessment server-side. The browser cannot supply
                # warning levels, missing controls, legal references, or tasks.
                plan = sync_action_plan(ACTION_PLAN_DIR, evaluate_payload(questionnaire))
                json_response(self, {"action_plan": plan})
                return
            if self.path == "/api/action-plan/update":
                payload = read_request_json(self)
                patch = payload.get("patch")
                if not isinstance(patch, dict):
                    raise ValueError("An action task update is required.")
                plan = update_action_task(
                    ACTION_PLAN_DIR,
                    str(payload.get("plan_id") or ""),
                    str(payload.get("task_id") or ""),
                    patch,
                )
                json_response(self, {"action_plan": plan})
                return
            if self.path == "/api/export-report":
                payload = read_request_json(self)
                report_format = str(payload.get("format") or "").lower()
                language = str(payload.get("language") or "en").lower()
                # Never trust browser-supplied scores, warnings, controls, or company
                # metadata. Rebuild the complete report input from validated answers.
                evaluation = build_export_evaluation(payload)
                company_name = str(
                    (evaluation.get("dashboard_context") or {}).get("company_name") or "company"
                )
                slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-") or "company"
                if report_format == "pdf":
                    file_response(
                        self,
                        build_pdf_report(evaluation, language=language),
                        "application/pdf",
                        f"compliance-report-{slug}.pdf",
                    )
                    return
                if report_format == "docx":
                    file_response(
                        self,
                        build_docx_report(evaluation, language=language),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        f"compliance-report-{slug}.docx",
                    )
                    return
                raise ValueError("Unsupported report format.")
            if self.path == "/api/chat":
                payload = read_request_json(self)
                questionnaire = payload.get("questionnaire_payload")
                if not isinstance(questionnaire, dict):
                    # Compatibility with browser sessions opened before the lean
                    # request format was introduced. Derived client data is ignored.
                    client_context = payload.get("context")
                    questionnaire = (
                        client_context.get("questionnaire_payload")
                        if isinstance(client_context, dict)
                        else None
                    )
                if not isinstance(questionnaire, dict):
                    raise ValueError("The assessment questionnaire is missing.")
                # Rebuild all model context from validated answers. The browser
                # never gets to supply scores, warnings, sources, or citations.
                context = evaluate_payload(questionnaire)
                user_message = payload.get("message", "")
                if not isinstance(user_message, str) or not user_message.strip():
                    raise ValueError("A question is required.")
                if len(user_message) > 4000:
                    raise ValueError("The question must be 4000 characters or fewer.")
                history = payload.get("history", [])
                if not isinstance(history, list):
                    raise ValueError("Conversation history must be a list.")
                validation_context = dict(context)
                validation_context["active_user_message"] = user_message
                chat_request = DR_A_AGENT.prepare_request(
                    validation_context,
                    user_message,
                    history,
                    build_sources=build_chat_sources,
                    select_sources=select_supported_sources,
                    build_messages=build_chat_messages,
                )
                if chat_request.blocked_reply:
                    json_response(self, {"reply": chat_request.blocked_reply})
                    return
                sources = chat_request.sources
                messages = chat_request.messages
                validation_context["selected_chat_sources"] = sources
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Connection", "close")
                self.end_headers()
                model_reply = ""
                try:
                    try:
                        for segment in validated_stream_segments(
                            stream_openai_model(messages), validation_context
                        ):
                            event = {"type": "delta", "text": segment}
                            self.wfile.write((json.dumps(event) + "\n").encode("utf-8"))
                            self.wfile.flush()
                            model_reply += segment
                    except GroundingValidationError as exc:
                        try:
                            corrected_reply = regenerate_after_validation_failure(
                                messages,
                                validation_context,
                                exc,
                            )
                        except (OpenAIModelError, GroundingValidationError) as correction_error:
                            print(
                                "[dashboard] grounded correction failed: "
                                f"{type(correction_error).__name__}: {correction_error}"
                            )
                            error_event = {
                                "type": "error",
                                "text": (
                                    "Dr. A could not produce a fully supported answer. "
                                    "Please rephrase the question or verify the available sources."
                                ),
                            }
                            self.wfile.write((json.dumps(error_event) + "\n").encode("utf-8"))
                            self.wfile.flush()
                            return
                        event_type = "replace" if model_reply else "delta"
                        event = {"type": event_type, "text": corrected_reply}
                        self.wfile.write((json.dumps(event) + "\n").encode("utf-8"))
                        self.wfile.flush()
                        model_reply = corrected_reply
                    except OpenAIModelError as exc:
                        if not model_reply:
                            # Preserve compatibility with endpoints that do not
                            # implement SSE, and retain full-response correction
                            # when the first buffered segment fails validation.
                            model_reply = generate_grounded_reply(messages, validation_context)
                            event = {"type": "delta", "text": model_reply}
                            self.wfile.write((json.dumps(event) + "\n").encode("utf-8"))
                            self.wfile.flush()
                        else:
                            error_event = {"type": "error", "text": str(exc)}
                            self.wfile.write((json.dumps(error_event) + "\n").encode("utf-8"))
                            self.wfile.flush()
                            return
                    cited_sources = DR_A_AGENT.cited_sources(sources, model_reply)
                    source_event = {"type": "sources", "items": cited_sources}
                    self.wfile.write((json.dumps(source_event) + "\n").encode("utf-8"))
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            self.send_error(404)
        except RequestTooLarge as exc:
            json_response(self, {"error": str(exc)}, status=413)
        except OpenAIModelError as exc:
            json_response(self, {"error": str(exc)}, status=503)
        except GroundingValidationError as exc:
            json_response(self, {"error": str(exc)}, status=422)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            json_response(self, {"error": str(exc)}, status=400)
        except OSError as exc:
            print(f"[dashboard] storage or network error: {exc}")
            json_response(
                self, {"error": "The requested operation could not be completed."}, status=500
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[dashboard] unexpected error: {type(exc).__name__}: {exc}")
            json_response(self, {"error": "Internal server error."}, status=500)

    def serve_file(self, path: Path) -> None:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
        }:
            content_type += "; charset=utf-8"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if path.name == "index.html":
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data:; style-src 'self'; "
                "script-src 'self'; connect-src 'self'; base-uri 'none'; "
                "form-action 'self'; frame-ancestors 'none'",
            )
            self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    try:
        host, port = dashboard_bind_address()
    except ValueError as exc:
        print(f"Could not start the dashboard: {exc}", file=sys.stderr)
        return 2
    try:
        server = DashboardHTTPServer((host, port), DashboardHandler)
    except OSError as exc:
        print(
            f"Could not start the dashboard on {host}:{port}: {exc}\n"
            "The port may already be in use. Set DASHBOARD_PORT to pick another "
            "one, for example DASHBOARD_PORT=8772.",
            file=sys.stderr,
        )
        return 1
    print(f"Dashboard available at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the dashboard.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
