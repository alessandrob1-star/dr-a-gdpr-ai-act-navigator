"""Small EUR-Lex webservice client helpers.

This module prepares the official EUR-Lex SOAP request. Credentials can be read
from a local JSON file for the private team repository or from environment
variables for safer deployments later.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

DEFAULT_ENDPOINT = "https://eur-lex.europa.eu/EURLexWebService"
DEFAULT_CREDENTIALS_PATH = Path("config") / "eurlex_credentials.json"
SOAP_ENVELOPE_NS = "http://www.w3.org/2003/05/soap-envelope"
WSSE_NS = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
EURLEX_NS = "http://eur-lex.europa.eu/search"
SOAP_ACTION = "https://eur-lex.europa.eu/ws/doQuery"


class EurLexConfigError(RuntimeError):
    """Raised when local EUR-Lex webservice configuration is incomplete."""


@dataclass(frozen=True)
class EurLexCredentials:
    username: str
    password: str

    @classmethod
    def from_environment(
        cls,
        env: Mapping[str, str] | None = None,
        username_key: str = "EURLEX_USERNAME",
        password_key: str = "EURLEX_PASSWORD",
    ) -> EurLexCredentials:
        env = env or os.environ
        username = env.get(username_key, "").strip()
        password = env.get(password_key, "").strip()
        if not username or not password:
            raise EurLexConfigError(
                f"Missing {username_key} or {password_key}. "
                "Set environment variables or use config/eurlex_credentials.json."
            )
        return cls(username=username, password=password)

    @classmethod
    def from_json_file(cls, path: str | Path = DEFAULT_CREDENTIALS_PATH) -> EurLexCredentials:
        path = Path(path)
        if not path.exists():
            raise EurLexConfigError(f"EUR-Lex credentials file not found: {path}")
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", "")).strip()
        if not username or not password:
            raise EurLexConfigError(
                f"EUR-Lex credentials file must include username and password: {path}"
            )
        return cls(username=username, password=password)

    @classmethod
    def load(
        cls,
        path: str | Path = DEFAULT_CREDENTIALS_PATH,
        env: Mapping[str, str] | None = None,
    ) -> EurLexCredentials:
        """Load credentials from JSON first, then fall back to environment."""
        path = Path(path)
        if path.exists():
            return cls.from_json_file(path)
        return cls.from_environment(env)


@dataclass(frozen=True)
class EurLexResponseSummary:
    celex_ids: list[str]
    likely_result_count: int
    response_size_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "celex_ids": self.celex_ids,
            "likely_result_count": self.likely_result_count,
            "response_size_bytes": self.response_size_bytes,
        }


def celex_query(celex_id: str) -> str:
    """Build a simple expert-search query for a CELEX document identifier."""
    clean_id = celex_id.strip()
    if not clean_id:
        raise ValueError("CELEX identifier cannot be empty")
    return f"DN = {clean_id}"


def keyword_query(*terms: str) -> str:
    """Build a conservative expert-search full-text query."""
    cleaned = [term.strip().replace('"', "") for term in terms if term.strip()]
    if not cleaned:
        raise ValueError("At least one search term is required")
    return " AND ".join(f'TEXT = "{term}"' for term in cleaned)


def build_query_envelope(
    credentials: EurLexCredentials,
    expert_query: str,
    page: int = 1,
    page_size: int = 10,
    search_language: str = "en",
) -> str:
    """Return the SOAP envelope used by the EUR-Lex webservice."""
    if page < 1:
        raise ValueError("page must be greater than zero")
    if page_size < 1:
        raise ValueError("page_size must be greater than zero")
    if not expert_query.strip():
        raise ValueError("expert_query cannot be empty")

    username = escape(credentials.username)
    password = escape(credentials.password)
    query = escape(expert_query.strip())
    language = escape(search_language.strip() or "en")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{SOAP_ENVELOPE_NS}" xmlns:wsse="{WSSE_NS}" xmlns:eur="{EURLEX_NS}">
  <soap:Header>
    <wsse:Security>
      <wsse:UsernameToken>
        <wsse:Username>{username}</wsse:Username>
        <wsse:Password>{password}</wsse:Password>
      </wsse:UsernameToken>
    </wsse:Security>
  </soap:Header>
  <soap:Body>
    <eur:searchRequest>
      <eur:expertQuery>{query}</eur:expertQuery>
      <eur:page>{page}</eur:page>
      <eur:pageSize>{page_size}</eur:pageSize>
      <eur:searchLanguage>{language}</eur:searchLanguage>
    </eur:searchRequest>
  </soap:Body>
</soap:Envelope>"""


def run_query(
    credentials: EurLexCredentials,
    expert_query: str,
    endpoint: str = DEFAULT_ENDPOINT,
    page: int = 1,
    page_size: int = 10,
    search_language: str = "en",
    timeout_seconds: int = 30,
) -> str:
    """Execute one EUR-Lex SOAP query and return the XML response text."""
    envelope = build_query_envelope(
        credentials=credentials,
        expert_query=expert_query,
        page=page,
        page_size=page_size,
        search_language=search_language,
    )
    request = Request(
        endpoint,
        data=envelope.encode("utf-8"),
        headers={
            "Content-Type": (f'application/soap+xml; charset=utf-8; action="{SOAP_ACTION}"'),
            "User-Agent": "AI-Regulatory-Intelligence-MVP/0.1",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8", errors="replace")


def summarize_response(xml_text: str) -> EurLexResponseSummary:
    """Extract a compact summary from a EUR-Lex XML response.

    The webservice response can include different XML wrappers depending on the
    query. For the MVP we keep parsing conservative: extract CELEX-like document
    identifiers and infer a result count from unique identifiers.
    """
    celex_ids = sorted(set(re.findall(r"\b[0-9][0-9]{4}[A-Z][0-9]{4}\b", xml_text)))
    return EurLexResponseSummary(
        celex_ids=celex_ids,
        likely_result_count=len(celex_ids),
        response_size_bytes=len(xml_text.encode("utf-8")),
    )
