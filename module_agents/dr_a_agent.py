"""Dr. A: model transport, grounding, policy, and chat orchestration."""

from __future__ import annotations

import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from policy_agent import PolicyAgent

DEFAULT_ASSISTANT_NAME = "Dr. A"
DEFAULT_OPENAI_MODEL = "gpt-5.6-sol"
DEFAULT_LOCAL_MODEL = "qwen2.5:14b-instruct"
OPENAI_CHAT_COMPLETIONS_ENDPOINT = "https://api.openai.com/v1/chat/completions"
POLICY_AGENT = PolicyAgent()


def configured_model_provider() -> str:
    """Return the selected model provider without guessing silently."""
    provider = os.getenv("MODEL_PROVIDER", "openai").strip().lower()
    if provider in {"local", "ollama", "qwen"}:
        return "local"
    return "openai"


def openai_model_config() -> tuple[str, str, str | None]:
    """Return the fixed OpenAI runtime and its process-scoped API key."""
    return (
        OPENAI_CHAT_COMPLETIONS_ENDPOINT,
        DEFAULT_OPENAI_MODEL,
        os.getenv("OPENAI_API_KEY"),
    )


def _chat_request_body(
    model: str, messages: list[dict[str, str]], *, stream: bool = False
) -> dict[str, Any]:
    """Build a GPT-5.6 Sol Chat Completions request."""
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 1200,
    }
    if stream:
        body["stream"] = True
    return body


def local_model_config() -> tuple[str | None, str, str | None]:
    """Read provider-neutral settings while preserving legacy QWEN_* names."""
    endpoint = os.getenv("LOCAL_MODEL_ENDPOINT") or os.getenv("QWEN_ENDPOINT")
    if endpoint:
        parsed = urllib.parse.urlparse(endpoint)
        if parsed.hostname == "localhost":
            port = f":{parsed.port}" if parsed.port else ""
            endpoint = urllib.parse.urlunparse(
                (
                    parsed.scheme,
                    f"127.0.0.1{port}",
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )
    model = os.getenv("LOCAL_MODEL_NAME") or os.getenv("QWEN_MODEL") or DEFAULT_LOCAL_MODEL
    api_key = os.getenv("LOCAL_MODEL_API_KEY") or os.getenv("QWEN_API_KEY")
    return endpoint, model, api_key


def openai_model_runtime_status() -> dict[str, Any]:
    """Return a fast, truthful health signal for the configured model endpoint."""
    endpoint, model, api_key = openai_model_config()
    status = {
        "model_configured": bool(api_key),
        "model_reachable": False,
        "model_available": None,
        "model_name": model,
    }
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return status
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((parsed.hostname, port), timeout=0.75):
            status["model_reachable"] = True
    except OSError:
        return status
    return status


def local_model_runtime_status() -> dict[str, Any]:
    """Return a fast, truthful health signal for the configured local endpoint."""
    endpoint, model, _ = local_model_config()
    status = {
        "model_configured": bool(endpoint),
        "model_reachable": False,
        "model_available": None,
        "model_name": model,
        "model_provider": "local",
    }
    if not endpoint:
        return status
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return status
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((parsed.hostname, port), timeout=0.75):
            status["model_reachable"] = True
    except OSError:
        return status

    if parsed.path.endswith("/v1/chat/completions"):
        tags_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/api/tags", "", "", ""))
        try:
            with urllib.request.urlopen(tags_url, timeout=1.5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            names = {
                str(item.get("name") or item.get("model") or "")
                for item in payload.get("models", [])
                if isinstance(item, dict)
            }
            status["model_available"] = model in names
        except (OSError, TimeoutError, ValueError, TypeError, json.JSONDecodeError):
            pass
    return status


def configured_model_runtime_status() -> dict[str, Any]:
    """Return health for the provider selected by MODEL_PROVIDER."""
    if configured_model_provider() == "local":
        return local_model_runtime_status()
    status = openai_model_runtime_status()
    status["model_provider"] = "openai"
    return status


class OpenAIModelError(RuntimeError):
    """Raised when the configured model cannot produce a usable response."""


class LocalModelError(OpenAIModelError):
    """Raised when the configured local model cannot produce a usable response."""


class GroundingValidationError(RuntimeError):
    """Raised when model output remains unsupported after one correction attempt."""


def call_openai_model(messages: list[dict[str, str]]) -> str:
    endpoint, model, api_key = openai_model_config()
    if not api_key:
        raise OpenAIModelError("OpenAI is not configured. Set OPENAI_API_KEY.")

    body = _chat_request_body(model, messages)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
    except (
        urllib.error.URLError,
        TimeoutError,
        KeyError,
        IndexError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        raise OpenAIModelError(f"OpenAI request failed: {exc}") from exc
    if not isinstance(content, str) or not content.strip():
        raise OpenAIModelError("OpenAI returned an empty response.")
    return content.strip()


def call_local_model(messages: list[dict[str, str]]) -> str:
    endpoint, model, api_key = local_model_config()
    if not endpoint:
        raise LocalModelError("The local model is not configured. Set LOCAL_MODEL_ENDPOINT.")

    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 650,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
    except (
        urllib.error.URLError,
        TimeoutError,
        KeyError,
        IndexError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        raise LocalModelError(f"Local model request failed: {exc}") from exc
    if not isinstance(content, str) or not content.strip():
        raise LocalModelError("The local model returned an empty response.")
    return content.strip()


def call_configured_model(messages: list[dict[str, str]]) -> str:
    """Call the provider selected by MODEL_PROVIDER."""
    if configured_model_provider() == "local":
        return call_local_model(messages)
    return call_openai_model(messages)


def stream_openai_model(messages: list[dict[str, str]]) -> Iterator[str]:
    """Yield text from the OpenAI Chat Completions streaming endpoint."""
    endpoint, model, api_key = openai_model_config()
    if not api_key:
        raise OpenAIModelError("OpenAI is not configured. Set OPENAI_API_KEY.")

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(_chat_request_body(model, messages, stream=True)).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")

    received_content = False
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                event = json.loads(data)
                if event.get("error"):
                    raise OpenAIModelError(str(event["error"]))
                choices = event.get("choices") or []
                if not choices:
                    continue
                content = choices[0].get("delta", {}).get("content")
                if content:
                    received_content = True
                    yield content
    except OpenAIModelError:
        raise
    except (
        urllib.error.URLError,
        TimeoutError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise OpenAIModelError(f"OpenAI streaming request failed: {exc}") from exc
    if not received_content:
        raise OpenAIModelError("OpenAI returned an empty streaming response.")


def stream_local_model(messages: list[dict[str, str]]) -> Iterator[str]:
    """Yield text from any OpenAI-compatible local streaming chat endpoint."""
    endpoint, model, api_key = local_model_config()
    if not endpoint:
        raise LocalModelError("The local model is not configured. Set LOCAL_MODEL_ENDPOINT.")

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 650,
                "stream": True,
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")

    received_content = False
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                event = json.loads(data)
                if event.get("error"):
                    raise LocalModelError(str(event["error"]))
                choices = event.get("choices") or []
                if not choices:
                    continue
                content = choices[0].get("delta", {}).get("content")
                if content:
                    received_content = True
                    yield content
    except LocalModelError:
        raise
    except (
        urllib.error.URLError,
        TimeoutError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise LocalModelError(f"Local model streaming request failed: {exc}") from exc
    if not received_content:
        raise LocalModelError("The local model returned an empty streaming response.")


def stream_configured_model(messages: list[dict[str, str]]) -> Iterator[str]:
    """Stream from the provider selected by MODEL_PROVIDER."""
    if configured_model_provider() == "local":
        return stream_local_model(messages)
    return stream_openai_model(messages)


ARTICLE_EXPRESSION = r"\d+(?:\s*[-–]\s*\d+)?(?:\s*(?:,|and)\s*\d+(?:\s*[-–]\s*\d+)?)*"


LEGAL_REFERENCE_PATTERNS = {
    "AI Act": (
        re.compile(rf"\bAI Act\s+Articles?\s+({ARTICLE_EXPRESSION})", re.IGNORECASE),
        re.compile(
            rf"\bArticles?\s+({ARTICLE_EXPRESSION})"
            rf"(?:\s+and\s+Annex\s+[IVXLCDM]+)?\s+of\s+(?:the\s+)?AI Act\b",
            re.IGNORECASE,
        ),
    ),
    "GDPR": (
        re.compile(rf"\bGDPR\s+Articles?\s+({ARTICLE_EXPRESSION})", re.IGNORECASE),
        re.compile(
            rf"\bArticles?\s+({ARTICLE_EXPRESSION})\s+of\s+(?:the\s+)?GDPR\b",
            re.IGNORECASE,
        ),
    ),
}


def _article_numbers(expression: str) -> set[int]:
    numbers: set[int] = set()
    for start_text, end_text in re.findall(r"(\d+)(?:\s*[-–]\s*(\d+))?", expression):
        start = int(start_text)
        end = int(end_text or start_text)
        if end >= start and end - start <= 100:
            numbers.update(range(start, end + 1))
    return numbers


def allowed_legal_articles(context: dict[str, Any]) -> dict[str, set[int]]:
    """Return article numbers explicitly present in trusted assessment context."""
    serialized = json.dumps(context, ensure_ascii=False)
    allowed: dict[str, set[int]] = {"AI Act": set(), "GDPR": set()}
    for regulation, patterns in LEGAL_REFERENCE_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(serialized):
                allowed[regulation].update(_article_numbers(match.group(1)))
    return allowed


def _target_warning_for_question(context: dict[str, Any], question: str) -> dict[str, Any] | None:
    """Select the warning explicitly named by a control-linkage question."""
    normalized = question.casefold()
    if "control" not in normalized or not any(
        term in normalized for term in ("connected", "specifically", "collegat", "specific")
    ):
        return None
    ignored = {
        "candidate",
        "connected",
        "controls",
        "missing",
        "possible",
        "specifically",
        "warning",
    }
    question_terms = {
        token
        for token in re.findall(r"[a-z0-9]+", normalized)
        if len(token) > 2 and token not in ignored
    }
    warnings = (context.get("dashboard_context") or {}).get("risk_warnings") or []
    ranked: list[tuple[int, dict[str, Any]]] = []
    for warning in warnings:
        title_terms = {
            token
            for token in re.findall(r"[a-z0-9]+", str(warning.get("title", "")).casefold())
            if len(token) > 2 and token not in ignored
        }
        score = len(question_terms & title_terms)
        if score:
            ranked.append((score, warning))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1] if ranked else None


TRANSFER_MECHANISMS = {
    "Standard Contractual Clauses": ("standard contractual clauses", "scc", "sccs"),
    "Binding Corporate Rules": ("binding corporate rules", "bcr", "bcrs"),
    "adequacy decision": ("adequacy decision", "adequacy decisions"),
    "approved code of conduct": ("approved code of conduct", "codes of conduct"),
    "certification mechanism": ("certification mechanism", "certification mechanisms"),
    "Article 49 derogation": ("article 49 derogation", "article 49 derogations"),
}

INTERNAL_IMPLEMENTATION_TERMS = (
    "context json",
    "citation catalog",
    "evidence focus",
    "supported_mechanisms",
    "supported_named_transfer_mechanisms",
    "question_scope",
    "linked_missing_controls",
    "risk_warnings",
    "triggered_by",
    "recommended_action",
    "transfer_status",
)

MOJIBAKE_MARKERS = (
    "Ãˆ",
    "Ã‰",
    "Ã ",
    "Ã¨",
    "Ã©",
    "Ã¬",
    "Ã²",
    "Ã¹",
    "Ã§",
    "â€™",
    "â€œ",
    "â€",
    "å",
    "è§",
    "æœ",
    "çš",
    "ï¼",
    "ã€",
    "æ‰",
    "é˜",
    "å›",
    "ä¸",
)


def _grounding_validation_issues(reply: str, context: dict[str, Any]) -> list[str]:
    """Validate objective grounding boundaries without enforcing canned wording."""
    issues: list[str] = []
    question = str(context.get("active_user_message") or "")
    normalized_question = question.casefold()
    normalized_reply = reply.casefold()

    warning = _target_warning_for_question(context, question)
    if warning is not None:
        allowed_controls = {
            str(control) for control in warning.get("linked_missing_controls") or []
        }
        all_controls = {
            str(control)
            for control in ((context.get("company_memory") or {}).get("controls") or {}).get(
                "missing_or_to_verify", []
            )
        }
        unexpected = sorted(
            control
            for control in all_controls - allowed_controls
            if control.casefold() in normalized_reply
        )
        if unexpected:
            issues.append(
                "Controls not linked to the requested warning were included: "
                + ", ".join(unexpected)
                + "."
            )

    transfer_claim = any(
        term in normalized_question or term in normalized_reply
        for term in ("transfer", "trasferiment")
    )
    if transfer_claim:
        evidence = json.dumps(
            context.get("selected_chat_sources") or [], ensure_ascii=False
        ).casefold()
        for mechanism, aliases in TRANSFER_MECHANISMS.items():
            if any(alias in normalized_reply for alias in aliases) and not any(
                alias in evidence for alias in aliases
            ):
                issues.append(f"Unsupported international-transfer mechanism: {mechanism}.")

        transfer_status = ((context.get("company_memory") or {}).get("privacy_profile") or {}).get(
            "extra_eea_transfers"
        )
        if transfer_status == "unknown" and any(
            phrase in normalized_reply
            for phrase in (
                "has indicated the presence of extra-eu",
                "has international transfers",
                "transfers are taking place",
                "transfers are occurring",
                "there are extra-eu/eea transfers",
                "data will be transferred",
                "data is transferred outside",
                "these international transfers",
            )
        ):
            issues.append(
                "Unknown transfer information was presented as confirmed transfer activity."
            )
        if re.search(r"\b(?:eu|eea|eu/eea) citizens(?:'|’)? data\b", normalized_reply):
            issues.append(
                "GDPR transfer scope was incorrectly described in terms of EU/EEA citizenship."
            )

    # Reject only a direct attribution of residual-risk assessment to the
    # screening stage.  A wider proximity check produced false positives when
    # a correct answer contrasted screening with the *completed* DPIA later in
    # the same paragraph.
    if "dpia" in normalized_reply and re.search(
        r"(?:screening|screening dpia)\s+"
        r"(?:identifies|indicates|shows|finds|reveals|determines|"
        r"identifica|indica|mostra|rileva|determina)"
        r"[^.;:\n]{0,60}(?:high residual risk|rischio residuo elevato)",
        normalized_reply,
    ):
        issues.append(
            "DPIA screening was incorrectly described as identifying residual risk; "
            "residual risk is assessed by the completed DPIA."
        )

    if any(term in normalized_reply for term in INTERNAL_IMPLEMENTATION_TERMS) or re.search(
        r"(?im)^\s*(?:title|message|recommended action)\s*:",
        reply,
    ):
        issues.append("The response exposed internal prompt or data-structure terminology.")

    if any(marker in reply for marker in MOJIBAKE_MARKERS) or (
        not re.search(r"[\u3400-\u9fff]", question) and re.search(r"[\u3400-\u9fff]", reply)
    ):
        issues.append("The response contains corrupted text or an unsupported language switch.")

    return issues


def model_reply_validation_issues(reply: str, context: dict[str, Any]) -> list[str]:
    """Validate a complete model draft without rewriting its meaning."""
    issues: list[str] = []
    output_check = POLICY_AGENT.check_output(model_reply=reply, context=context)
    if output_check.is_blocked:
        reason = (
            output_check.violations[0].reason_code if output_check.violations else "output.policy"
        )
        issues.append(f"Policy validation failed: {reason}.")

    issues.extend(_grounding_validation_issues(reply, context))

    allowed = allowed_legal_articles(context)
    seen: set[tuple[str, str]] = set()
    for regulation, patterns in LEGAL_REFERENCE_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(reply):
                cited = _article_numbers(match.group(1))
                unsupported = cited - allowed[regulation]
                key = (regulation, match.group(0))
                if unsupported and key not in seen:
                    seen.add(key)
                    numbers = ", ".join(str(value) for value in sorted(unsupported))
                    issues.append(f"Unsupported {regulation} article reference(s): {numbers}.")
    return issues


def safe_validation_feedback(issues: list[str] | tuple[str, ...] | str) -> str:
    """Describe validation categories without echoing rejected claims to the model."""
    text = " ".join(issues) if not isinstance(issues, str) else issues
    categories: list[str] = []
    checks = (
        (
            "international-transfer mechanism",
            "Remove named international-transfer mechanisms that are not explicitly supported "
            "by the supplied sources.",
        ),
        (
            "article reference",
            "Remove legal article references that are not present in the supplied evidence.",
        ),
        (
            "not linked to the requested warning",
            "Remove controls that are not linked to the warning being discussed.",
        ),
        (
            "confirmed transfer activity",
            "Keep confirmed provider use separate from unresolved personal-data transfers.",
        ),
        (
            "citizenship",
            "Describe GDPR scope using people, data subjects, or personal data rather than "
            "citizenship.",
        ),
        (
            "DPIA screening",
            "Keep DPIA screening, the full DPIA, and residual-risk assessment as separate stages.",
        ),
        (
            "internal prompt",
            "Remove internal prompt, field, and data-structure terminology.",
        ),
        (
            "corrupted text",
            "Use clean text in the language of the question.",
        ),
        (
            "Policy validation failed",
            "Remove definitive legal guarantees or other policy-violating claims.",
        ),
    )
    for marker, guidance in checks:
        if marker.casefold() in text.casefold() and guidance not in categories:
            categories.append(guidance)
    return " ".join(categories) or "Correct the factual or policy grounding of the draft."


def regenerate_after_validation_failure(
    messages: list[dict[str, str]],
    context: dict[str, Any],
    failure: GroundingValidationError,
) -> str:
    """Make one evidence-focused correction without prescribing the answer text."""
    correction_messages = [
        *messages,
        {
            "role": "user",
            "content": (
                "Generate a corrected answer once. "
                + safe_validation_feedback(str(failure))
                + "\nUse only the supplied company and regulatory information. Preserve useful "
                "detail, answer only the question asked, do not expose internal fields, and do "
                "not mention this validation exchange."
            ),
        },
    ]
    reply = call_configured_model(correction_messages)
    issues = model_reply_validation_issues(reply, context)
    if issues:
        raise GroundingValidationError(
            "Dr. A could not correct the response after grounding validation. " + " ".join(issues)
        )
    return reply


def generate_grounded_reply(messages: list[dict[str, str]], context: dict[str, Any]) -> str:
    """Generate with the configured model, retry once, then fail visibly."""
    working_messages = list(messages)
    last_issues: list[str] = []
    for attempt in range(2):
        reply = call_configured_model(working_messages)
        last_issues = model_reply_validation_issues(reply, context)
        if not last_issues:
            return reply
        if attempt == 0:
            working_messages = [
                *messages,
                {
                    "role": "user",
                    "content": (
                        safe_validation_feedback(last_issues)
                        + " Generate a new answer from the supplied evidence. "
                        "Do not repeat unsupported claims or references. "
                        "Do not describe this validation exchange to the user."
                    ),
                },
            ]
    raise GroundingValidationError(
        "Dr. A could not produce a response that passed grounding validation. "
        + " ".join(last_issues)
    )


STREAM_DISPLAY_BOUNDARY = re.compile(r"(?:\n{2,}|[.!?](?:[ \t]+|\n+))")


def validated_stream_segments(chunks: Iterator[str], context: dict[str, Any]) -> Iterator[str]:
    """Buffer short readable segments and validate cumulative text before display."""
    pending = ""
    accepted = ""
    received = False

    def validate(segment: str) -> str:
        candidate = accepted + segment
        issues = model_reply_validation_issues(candidate, context)
        if issues:
            raise GroundingValidationError(
                "Dr. A stopped before displaying a segment that failed validation. "
                + " ".join(issues)
            )
        return candidate

    for chunk in chunks:
        if not chunk:
            continue
        received = True
        pending += chunk
        while True:
            boundary = STREAM_DISPLAY_BOUNDARY.search(pending)
            if not boundary:
                break
            # Avoid flashing tiny fragments such as a heading on its own, unless
            # the model has completed a full paragraph.
            if boundary.end() < 60 and "\n\n" not in boundary.group(0):
                next_boundary = STREAM_DISPLAY_BOUNDARY.search(pending, boundary.end())
                if not next_boundary:
                    break
                boundary = next_boundary
            segment = pending[: boundary.end()]
            candidate = validate(segment)
            accepted = candidate
            pending = pending[boundary.end() :]
            yield segment

    if not received:
        raise OpenAIModelError("The configured model returned an empty streaming response.")
    if pending:
        candidate = validate(pending)
        accepted = candidate
        yield pending


def build_chat_sources(context: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """Build a stable, deduplicated citation catalog from matched dashboard evidence."""
    dashboard = context.get("dashboard_context") or {}
    groups = (
        dashboard.get("matched_regulatory_events") or [],
        dashboard.get("matched_news_feed") or [],
        dashboard.get("matched_early_warnings") or [],
    )
    sources: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for items in groups:
        for item in items:
            candidates = [item, *(item.get("related_sources") or [])]
            for candidate in candidates:
                evidence_url = next(
                    (
                        str(entry.get("url", "")).strip()
                        for entry in (candidate.get("evidence") or [])
                        if entry.get("url")
                    ),
                    "",
                )
                url = str(
                    candidate.get("url")
                    or candidate.get("primary_official_source_url")
                    or evidence_url
                    or ""
                ).strip()
                parsed_url = urllib.parse.urlparse(url)
                if (
                    not url
                    or parsed_url.scheme not in {"http", "https"}
                    or not parsed_url.netloc
                    or url in seen_urls
                ):
                    continue
                seen_urls.add(url)
                sources.append(
                    {
                        "id": f"S{len(sources) + 1}",
                        "title": candidate.get("title") or "Regulatory source",
                        "url": url,
                        "source": candidate.get("source") or candidate.get("source_name") or "",
                        "is_official": candidate.get("is_official") is True,
                        "legal_status": candidate.get("legal_status") or "",
                        "support": (
                            candidate.get("summary")
                            or candidate.get("message")
                            or candidate.get("description")
                            or ""
                        ),
                        "legal_references": candidate.get("legal_references") or [],
                    }
                )
                if len(sources) >= limit:
                    return sources
    return sources


def select_supported_sources(
    sources: list[dict[str, Any]], user_message: str, limit: int = 3
) -> list[dict[str, Any]]:
    """Offer evidence only when the question names a topic covered by its support text."""
    ignored = {
        "about",
        "after",
        "cosa",
        "cose",
        "devo",
        "della",
        "delle",
        "fare",
        "first",
        "meglio",
        "point",
        "prima",
        "prime",
        "primo",
        "quali",
        "should",
        "spiegami",
        "what",
        "with",
    }
    query_terms = {
        token.lower()
        for token in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]{2,}", user_message)
        if len(token) >= 4 and token.lower() not in ignored
    }
    if not query_terms:
        return []
    normalized_query = user_message.lower()
    topic_aliases = (
        ("ai act", ("ai act",)),
        ("gdpr", ("gdpr",)),
        ("transparency", ("transparency", "trasparenza")),
        ("prohibited", ("prohibited", "vietate", "proibite")),
        ("dpia", ("dpia", "valutazione d'impatto", "valutazione di impatto")),
        ("breach", ("breach", "violazione dei dati", "violazioni dei dati")),
        ("transfer", ("transfer", "trasferimento", "trasferimenti")),
    )
    requested_topics = {
        canonical
        for canonical, aliases in topic_aliases
        if any(alias in normalized_query for alias in aliases)
    }
    ranked: list[tuple[int, dict[str, Any]]] = []
    for source in sources:
        evidence = " ".join(
            str(value)
            for value in (
                source.get("title", ""),
                source.get("support", ""),
                " ".join(source.get("legal_references", [])),
            )
        ).lower()
        score = sum(term in evidence for term in query_terms)
        score += 2 * sum(topic in evidence for topic in requested_topics)
        if score:
            ranked.append((score, source))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [source for _, source in ranked[:limit]]


def compact_warning(item: dict[str, Any]) -> dict[str, Any]:
    """Keep only auditable warning fields needed by Dr. A."""
    return {
        key: item.get(key)
        for key in (
            "level",
            "title",
            "message",
            "triggered_by",
            "linked_missing_controls",
            "legal_references",
            "recommended_action",
        )
        if item.get(key)
    }


def compact_chat_context(context: dict[str, Any]) -> dict[str, Any]:
    """Return the compact generic assessment used when no narrower focus applies."""
    memory = context.get("company_memory") or {}
    dashboard = context.get("dashboard_context") or {}
    company_profile = memory.get("company_profile") or {}
    company = {
        key: company_profile.get(key)
        for key in ("company_name", "industry", "company_size", "eu_presence", "dashboard_priority")
        if company_profile.get(key) not in (None, "", [])
    }
    return {
        "company": company,
        "relevance_tags": memory.get("relevance_tags") or [],
        "compliance_score": memory.get("compliance_score") or {},
        "controls": memory.get("controls") or {},
        "risk_warnings": [compact_warning(item) for item in (dashboard.get("risk_warnings") or [])],
    }


def build_question_context(
    context: dict[str, Any],
    user_message: str,
    source_catalog: list[dict[str, Any]],
) -> dict[str, Any]:
    """Select the smallest truthful evidence set that can answer the current question."""
    memory = context.get("company_memory") or {}
    dashboard = context.get("dashboard_context") or {}
    generic = compact_chat_context(context)
    normalized = user_message.casefold()
    warnings = [compact_warning(item) for item in (dashboard.get("risk_warnings") or [])]

    def warning_named(fragment: str) -> dict[str, Any] | None:
        return next(
            (
                warning
                for warning in warnings
                if fragment in str(warning.get("title", "")).casefold()
            ),
            None,
        )

    if any(term in normalized for term in ("transfer", "trasferiment")):
        privacy = memory.get("privacy_profile") or {}
        providers = [
            value
            for value in privacy.get("extra_eea_providers") or []
            if value not in {"unknown", "no"}
        ]
        transfer_status = privacy.get("extra_eea_transfers")
        confirmed: dict[str, Any] = {}
        if providers:
            confirmed["extra_eu_eea_provider_types"] = providers
        if transfer_status == "yes":
            confirmed["personal_data_transfers_outside_eu_eea"] = True
        elif transfer_status == "no":
            confirmed["personal_data_transfers_outside_eu_eea"] = False

        unresolved: list[str] = []
        if transfer_status == "unknown":
            unresolved.extend(
                [
                    "whether personal-data transfers outside the EU/EEA actually occur",
                    "transfer destinations and recipients",
                    "the applicable transfer mechanism and supplementary measures",
                ]
            )

        evidence_text = json.dumps(source_catalog, ensure_ascii=False).casefold()
        supported_mechanisms = [
            mechanism
            for mechanism, aliases in TRANSFER_MECHANISMS.items()
            if any(alias in evidence_text for alias in aliases)
        ]
        if supported_mechanisms:
            confirmed["transfer_mechanisms_explicitly_named_by_sources"] = supported_mechanisms
        else:
            unresolved.append(
                "which transfer mechanism applies; the supplied sources do not name one"
            )
        guidance = [
            "Keep confirmed facts separate from unresolved information.",
            "Do not imply that personal-data transfers occur when their status is unknown.",
            "Name a transfer mechanism only when the supplied sources explicitly name it.",
        ]
        if any(
            term in normalized
            for term in ("violating", "violation", "non-compliance", "noncompliance")
        ):
            guidance.append(
                "Answer the yes-or-no question directly: unknown status alone does not "
                "establish a GDPR violation."
            )
        return {
            "topic": "international_transfers",
            "company": generic["company"],
            "confirmed": confirmed,
            "unresolved": unresolved,
            "warning": warning_named("international transfer"),
            "guidance": guidance,
        }

    if "dpia" in normalized or "prior consultation" in normalized:
        return {
            "topic": "dpia",
            "company": generic["company"],
            "warning": warning_named("dpia candidate"),
            "profile_factors": (warning_named("dpia candidate") or {}).get("triggered_by", []),
            "guidance": [
                "The questionnaire signals screening factors; it does not prove a full DPIA "
                "is mandatory.",
                "Screening asks whether planned processing is likely to result in high risk.",
                "A full DPIA follows when that threshold is met.",
                "Prior consultation follows only if the completed DPIA identifies high residual "
                "risk without adequate mitigation.",
                "Do not introduce hypothetical profile facts that were not selected.",
            ],
        }

    if any(term in normalized for term in ("high-risk", "high risk", "annex iii", "recruit")):
        return {
            "topic": "high_risk_ai_classification",
            "company": generic["company"],
            "ai_profile": memory.get("ai_profile") or {},
            "warning": warning_named("possible high-risk"),
            "guidance": [
                "Recruitment is a candidate Annex III intended use because AI used for "
                "recruitment or selection can affect access to employment; this does not depend "
                "on describing applicant data as sensitive.",
                "A recruitment use is not automatically high-risk.",
                "Final classification depends on intended purpose and the applicable Article 6 "
                "conditions and exceptions.",
                "Answer only the classification or control question asked; do not append other "
                "dashboard priorities.",
            ],
        }

    if any(term in normalized for term in ("first three", "three things", "priorit")):
        return {
            "topic": "ordered_priorities",
            "company": generic["company"],
            "priorities": warnings[:3],
            "guidance": [
                "Preserve this order.",
                "Explain naturally without printing internal field labels.",
                "For the international-transfer priority, extra-EU/EEA provider use is "
                "confirmed but personal-data transfers remain unresolved; do not describe "
                "transfers as already occurring.",
            ],
        }

    warning = _target_warning_for_question(context, user_message)
    if warning is not None:
        return {
            "topic": "warning_controls",
            "company": generic["company"],
            "warning": compact_warning(warning),
            "guidance": [
                "Use only linked_missing_controls for the requested warning.",
                "Explain each control once and avoid repetition.",
            ],
        }

    return {
        "topic": "general_assessment",
        **generic,
        "guidance": ["Answer only the question asked and avoid repeating the same explanation."],
    }


def compact_prompt_json(value: Any) -> str:
    """Serialize model evidence without spending context tokens on indentation."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def build_chat_messages(
    context: dict[str, Any],
    user_message: str,
    sources: list[dict[str, Any]] | None = None,
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Build a concise prompt around question-specific structured evidence."""
    citation_sources = sources if sources is not None else build_chat_sources(context)
    source_catalog = [
        {
            "id": item["id"],
            "title": item["title"],
            "source": item["source"],
            "url": item["url"],
            "legal_status": item["legal_status"],
            "support": item.get("support", ""),
            "legal_references": item.get("legal_references", []),
        }
        for item in citation_sources
    ]
    focus = build_question_context(context, user_message, source_catalog)
    normalized = user_message.casefold()
    italian_prompt = any(
        term in normalized
        for term in ("rispondi", "italiano", "quali", "perché", "spiega", "trasferiment")
    )
    english_prompt = any(
        term in normalized for term in ("what", "which", "why", "does", "should", "explain")
    )
    if italian_prompt:
        language_rule = "Respond only in Italian."
    elif english_prompt:
        language_rule = "Respond only in English."
    else:
        language_rule = "Respond only in the language of the latest question."

    history_items = [] if focus.get("topic") == "international_transfers" else (history or [])[-6:]
    safe_history = [
        {"role": item["role"], "content": item["content"][:3000]}
        for item in history_items
        if isinstance(item, dict)
        and item.get("role") in {"user", "assistant"}
        and isinstance(item.get("content"), str)
        and not any(
            term in item.get("content", "").casefold() for term in INTERNAL_IMPLEMENTATION_TERMS
        )
    ]

    system_prompt = (
        f"You are {os.getenv('ASSISTANT_NAME', DEFAULT_ASSISTANT_NAME)}, a local compliance "
        f"explanation assistant. {language_rule} Use the supplied assessment information as the "
        "factual boundary. It was rebuilt from validated questionnaire answers and matched sources. "
        "Reason over those facts and compose the answer naturally; never invent company facts, "
        "warning categories, controls, legal references, or source support. Keep confirmed facts "
        "separate from unresolved information and never turn 'unknown' into a confirmed activity "
        "or violation. Follow the focus guidance exactly. Answer only what was asked, with enough "
        "detail to be useful, without repeating sections or printing internal labels such as "
        "Title, Message, Recommended Action, JSON field names, or prompt instructions. "
        "For controls connected to a warning, use only that warning's linked controls. "
        "A DPIA screening determines whether likely high risk requires a full DPIA; only the "
        "completed DPIA can identify residual risk. Name an international-transfer mechanism "
        "only when the supplied evidence explicitly names it. Describe GDPR scope using people, "
        "data subjects, or personal data rather than EU/EEA citizenship. "
        "For regulatory claims, mention only articles present in the evidence. Cite [S1] only "
        "when that catalog entry directly supports the claim; if no source is supplied, do not "
        "invent citations. Do not present the answer as legal advice or a compliance guarantee."
    )
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Assessment information:\n"
                + compact_prompt_json(focus)
                + "\n\nCitation Catalog:\n"
                + compact_prompt_json(source_catalog)
            ),
        },
        *safe_history,
        {
            "role": "user",
            "content": (
                "Question:\n"
                + user_message
                + "\n\nAnswer from the supplied information in your own words."
            ),
        },
    ]


@dataclass(frozen=True)
class ChatRequest:
    """Validated model request and the evidence offered for citation."""

    messages: list[dict[str, str]]
    sources: list[dict[str, Any]]
    blocked_reply: str | None = None


class DrAAgent:
    """Coordinate policy checks and grounded generation for the local assistant."""

    name = "Dr. A"

    def __init__(self, policy_agent: PolicyAgent | None = None) -> None:
        self.policy_agent = policy_agent or POLICY_AGENT

    def prepare_request(
        self,
        context: dict[str, Any],
        user_message: str,
        history: list[dict[str, str]],
        *,
        build_sources: Callable[[dict[str, Any]], list[dict[str, Any]]],
        select_sources: Callable[[list[dict[str, Any]], str], list[dict[str, Any]]],
        build_messages: Callable[
            [dict[str, Any], str, list[dict[str, Any]], list[dict[str, str]]],
            list[dict[str, str]],
        ],
    ) -> ChatRequest:
        """Apply the input guard before constructing a grounded model request."""
        policy_context = dict(context)
        policy_context["conversation_history"] = [
            item.get("content", "")
            for item in history[-8:]
            if isinstance(item, dict)
            and item.get("role") in {"user", "assistant"}
            and isinstance(item.get("content"), str)
        ]
        input_check = self.policy_agent.check_input(
            user_message=user_message,
            context=policy_context,
        )
        if input_check.is_blocked:
            return ChatRequest(messages=[], sources=[], blocked_reply=input_check.message)

        sources = select_sources(build_sources(context), user_message)
        messages = build_messages(context, user_message, sources, history)
        return ChatRequest(messages=messages, sources=sources)

    def validate_output(self, model_reply: str, context: dict[str, Any]):
        """Expose the same output Policy Agent used by the grounding validator."""
        return self.policy_agent.check_output(model_reply=model_reply, context=context)

    @staticmethod
    def cited_sources(sources: list[dict[str, Any]], model_reply: str) -> list[dict[str, Any]]:
        """Return only sources whose identifiers appear in the generated answer."""
        return [source for source in sources if f"[{source['id']}]" in model_reply]
