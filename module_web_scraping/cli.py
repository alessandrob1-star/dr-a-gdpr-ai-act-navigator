"""Command line entry point for the source monitoring MVP."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .demo_monitor_static import STATIC_HTML
from .demo_report import build_demo_report, write_json_report, write_markdown_report
from .eurlex_webservice import (
    EurLexCredentials,
    build_query_envelope,
    celex_query,
    keyword_query,
    run_query,
    summarize_response,
)
from .pipeline import group_items_into_events, monitored_items_from_event_seed
from .regulatory_diff import diff_regulatory_events, render_diff_markdown
from .repository import load_sources
from .source_monitor import (
    deduplicate_against_existing,
    deduplicate_items,
    monitor_source,
    monitor_source_from_html,
)
from .storage import (
    known_urls_and_hashes,
    load_monitored_items,
    save_monitored_items,
    save_regulatory_events,
)
from .web_scraping_outputs import generate_web_scraping_outputs

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REGISTRY = ROOT / "data" / "source-registry-seed.csv"
EVENT_SEED = ROOT / "data" / "demo-regulatory-events-seed.csv"
CREDENTIALS_FILE = ROOT / "config" / "eurlex_credentials.json"
DEFAULT_ITEMS_STORE = ROOT / "storage" / "monitored_items.jsonl"
DEFAULT_EVENTS_STORE = ROOT / "storage" / "regulatory_events.jsonl"
DEFAULT_DEMO_REPORT = ROOT / "storage" / "demo_report.md"
DEFAULT_DEMO_REPORT_JSON = ROOT / "storage" / "demo_report.json"
DEFAULT_WEB_SCRAPING_OUTPUT_DIR = ROOT / "storage" / "web_scraping_outputs"
DEFAULT_DASHBOARD_EVENTS = DEFAULT_WEB_SCRAPING_OUTPUT_DIR / "regulatory_events.json"


def dumps(value: object) -> str:
    return json.dumps(value, indent=2, default=str)


def cmd_sources(args: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    if args.active:
        sources = [source for source in sources if source.active]
    print(dumps([asdict(source) for source in sources]))


def cmd_seed_dashboard(_: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    items = monitored_items_from_event_seed(EVENT_SEED, sources)
    events = group_items_into_events(items)
    print(dumps([event.to_dashboard_dict() for event in events]))


def cmd_monitor_static(_: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next(source for source in sources if source.name == "European Commission AI Office")
    items = deduplicate_items(monitor_source_from_html(source, STATIC_HTML))
    print(dumps([asdict(item) for item in items]))


def cmd_monitor_static_dashboard(_: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next(source for source in sources if source.name == "European Commission AI Office")
    items = deduplicate_items(monitor_source_from_html(source, STATIC_HTML))
    events = group_items_into_events(items)
    print(dumps([event.to_dashboard_dict() for event in events]))


def cmd_monitor_live(args: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next((source for source in sources if source.name == args.source_name), None)
    if source is None:
        available = ", ".join(source.name for source in sources)
        raise SystemExit(f"Unknown source '{args.source_name}'. Available sources: {available}")
    items = deduplicate_items(monitor_source(source, limit=args.limit))
    print(dumps([asdict(item) for item in items]))


def cmd_monitor_live_dashboard(args: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next((source for source in sources if source.name == args.source_name), None)
    if source is None:
        available = ", ".join(source.name for source in sources)
        raise SystemExit(f"Unknown source '{args.source_name}'. Available sources: {available}")
    items = deduplicate_items(monitor_source(source, limit=args.limit))
    events = group_items_into_events(items)
    print(dumps([event.to_dashboard_dict() for event in events]))


def cmd_monitor_static_persist(args: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next(source for source in sources if source.name == "European Commission AI Office")
    existing = load_monitored_items(args.items_store)
    existing_urls, existing_hashes = known_urls_and_hashes(existing)
    items = deduplicate_against_existing(
        deduplicate_items(monitor_source_from_html(source, STATIC_HTML)),
        existing_urls,
        existing_hashes,
    )
    events = group_items_into_events(items)
    save_monitored_items(args.items_store, items)
    save_regulatory_events(args.events_store, events)
    print(
        dumps(
            {
                "new_items": len(items),
                "new_events": len(events),
                "items_store": str(args.items_store),
                "events_store": str(args.events_store),
            }
        )
    )


def cmd_monitor_live_persist(args: argparse.Namespace) -> None:
    sources = load_sources(SOURCE_REGISTRY)
    source = next((source for source in sources if source.name == args.source_name), None)
    if source is None:
        available = ", ".join(source.name for source in sources)
        raise SystemExit(f"Unknown source '{args.source_name}'. Available sources: {available}")
    existing = load_monitored_items(args.items_store)
    existing_urls, existing_hashes = known_urls_and_hashes(existing)
    items = deduplicate_against_existing(
        deduplicate_items(monitor_source(source, limit=args.limit)),
        existing_urls,
        existing_hashes,
    )
    events = group_items_into_events(items)
    save_monitored_items(args.items_store, items)
    save_regulatory_events(args.events_store, events)
    print(
        dumps(
            {
                "source": source.name,
                "new_items": len(items),
                "new_events": len(events),
                "items_store": str(args.items_store),
                "events_store": str(args.events_store),
            }
        )
    )


def cmd_eurlex_celex_envelope(args: argparse.Namespace) -> None:
    credentials = EurLexCredentials.load(CREDENTIALS_FILE)
    envelope = build_query_envelope(
        credentials=credentials,
        expert_query=celex_query(args.celex_id),
        page=args.page,
        page_size=args.page_size,
        search_language=args.search_language,
    )
    print(envelope)


def cmd_eurlex_keyword_envelope(args: argparse.Namespace) -> None:
    credentials = EurLexCredentials.load(CREDENTIALS_FILE)
    envelope = build_query_envelope(
        credentials=credentials,
        expert_query=keyword_query(*args.terms),
        page=args.page,
        page_size=args.page_size,
        search_language=args.search_language,
    )
    print(envelope)


def cmd_eurlex_celex_query(args: argparse.Namespace) -> None:
    credentials = EurLexCredentials.load(CREDENTIALS_FILE)
    response = run_query(
        credentials=credentials,
        expert_query=celex_query(args.celex_id),
        page=args.page,
        page_size=args.page_size,
        search_language=args.search_language,
        timeout_seconds=args.timeout,
    )
    if args.summary:
        print(dumps(summarize_response(response).to_dict()))
    else:
        print(response)


def cmd_demo_report(args: argparse.Namespace) -> None:
    report = build_demo_report(SOURCE_REGISTRY, EVENT_SEED)
    write_markdown_report(report, args.output)
    write_json_report(report, args.json_output)
    print(
        dumps(
            {
                "report": str(args.output),
                "json_report": str(args.json_output),
                **report["summary"],
            }
        )
    )


def cmd_demo_outputs(args: argparse.Namespace) -> None:
    summary = generate_web_scraping_outputs(SOURCE_REGISTRY, EVENT_SEED, args.output_dir)
    print(dumps(summary))


def _load_event_list(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected a JSON array of events in {path}.")
    return data


def cmd_regulatory_diff(args: argparse.Namespace) -> None:
    old_events = _load_event_list(args.old)
    new_events = _load_event_list(args.new)
    report = diff_regulatory_events(old_events, new_events)
    markdown = render_diff_markdown(report)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(dumps(report) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    print(markdown)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Source monitoring MVP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sources_parser = subparsers.add_parser("sources", help="Print source registry")
    sources_parser.add_argument("--active", action="store_true", help="Show only active sources")
    sources_parser.set_defaults(func=cmd_sources)

    seed_parser = subparsers.add_parser(
        "seed-dashboard", help="Build dashboard events from local seed data"
    )
    seed_parser.set_defaults(func=cmd_seed_dashboard)

    static_parser = subparsers.add_parser(
        "monitor-static", help="Run source monitor against deterministic static HTML"
    )
    static_parser.set_defaults(func=cmd_monitor_static)

    static_dashboard_parser = subparsers.add_parser(
        "monitor-static-dashboard",
        help="Run static source monitor and output dashboard-ready events",
    )
    static_dashboard_parser.set_defaults(func=cmd_monitor_static_dashboard)

    live_parser = subparsers.add_parser(
        "monitor-live", help="Fetch one configured source and extract monitored items"
    )
    live_parser.add_argument("source_name", help="Exact source name from the registry")
    live_parser.add_argument("--limit", type=int, default=25, help="Maximum candidate links")
    live_parser.set_defaults(func=cmd_monitor_live)

    live_dashboard_parser = subparsers.add_parser(
        "monitor-live-dashboard",
        help="Fetch one configured source and output dashboard-ready events",
    )
    live_dashboard_parser.add_argument("source_name", help="Exact source name from the registry")
    live_dashboard_parser.add_argument(
        "--limit", type=int, default=25, help="Maximum candidate links"
    )
    live_dashboard_parser.set_defaults(func=cmd_monitor_live_dashboard)

    persist_static_parser = subparsers.add_parser(
        "monitor-static-persist",
        help="Run static monitor and append new items/events to JSONL storage",
    )
    persist_static_parser.add_argument("--items-store", type=Path, default=DEFAULT_ITEMS_STORE)
    persist_static_parser.add_argument("--events-store", type=Path, default=DEFAULT_EVENTS_STORE)
    persist_static_parser.set_defaults(func=cmd_monitor_static_persist)

    persist_live_parser = subparsers.add_parser(
        "monitor-live-persist",
        help="Fetch one source and append new items/events to JSONL storage",
    )
    persist_live_parser.add_argument("source_name", help="Exact source name from the registry")
    persist_live_parser.add_argument("--limit", type=int, default=25)
    persist_live_parser.add_argument("--items-store", type=Path, default=DEFAULT_ITEMS_STORE)
    persist_live_parser.add_argument("--events-store", type=Path, default=DEFAULT_EVENTS_STORE)
    persist_live_parser.set_defaults(func=cmd_monitor_live_persist)

    eurlex_celex_envelope_parser = subparsers.add_parser(
        "eurlex-celex-envelope",
        help="Print the EUR-Lex SOAP envelope for a CELEX identifier",
    )
    eurlex_celex_envelope_parser.add_argument("celex_id", help="CELEX identifier, e.g. 32024R1689")
    eurlex_celex_envelope_parser.add_argument("--page", type=int, default=1)
    eurlex_celex_envelope_parser.add_argument("--page-size", type=int, default=10)
    eurlex_celex_envelope_parser.add_argument("--search-language", default="en")
    eurlex_celex_envelope_parser.set_defaults(func=cmd_eurlex_celex_envelope)

    eurlex_keyword_envelope_parser = subparsers.add_parser(
        "eurlex-keyword-envelope",
        help="Print the EUR-Lex SOAP envelope for keyword search terms",
    )
    eurlex_keyword_envelope_parser.add_argument("terms", nargs="+")
    eurlex_keyword_envelope_parser.add_argument("--page", type=int, default=1)
    eurlex_keyword_envelope_parser.add_argument("--page-size", type=int, default=10)
    eurlex_keyword_envelope_parser.add_argument("--search-language", default="en")
    eurlex_keyword_envelope_parser.set_defaults(func=cmd_eurlex_keyword_envelope)

    eurlex_celex_query_parser = subparsers.add_parser(
        "eurlex-celex-query",
        help="Run one live EUR-Lex SOAP query for a CELEX identifier",
    )
    eurlex_celex_query_parser.add_argument("celex_id", help="CELEX identifier, e.g. 32024R1689")
    eurlex_celex_query_parser.add_argument("--page", type=int, default=1)
    eurlex_celex_query_parser.add_argument("--page-size", type=int, default=10)
    eurlex_celex_query_parser.add_argument("--search-language", default="en")
    eurlex_celex_query_parser.add_argument("--timeout", type=int, default=30)
    eurlex_celex_query_parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact JSON summary instead of the raw XML response",
    )
    eurlex_celex_query_parser.set_defaults(func=cmd_eurlex_celex_query)

    demo_report_parser = subparsers.add_parser(
        "demo-report",
        help="Generate a readable Markdown and JSON report from deterministic demo data",
    )
    demo_report_parser.add_argument("--output", type=Path, default=DEFAULT_DEMO_REPORT)
    demo_report_parser.add_argument("--json-output", type=Path, default=DEFAULT_DEMO_REPORT_JSON)
    demo_report_parser.set_defaults(func=cmd_demo_report)

    demo_outputs_parser = subparsers.add_parser(
        "demo-outputs",
        help="Generate concrete JSON and Markdown outputs for the web scraping MVP",
    )
    demo_outputs_parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_WEB_SCRAPING_OUTPUT_DIR
    )
    demo_outputs_parser.set_defaults(func=cmd_demo_outputs)

    regulatory_diff_parser = subparsers.add_parser(
        "regulatory-diff",
        help="Diff two regulatory-event snapshots into a dated 'what changed' changelog",
    )
    regulatory_diff_parser.add_argument(
        "--old",
        type=Path,
        required=True,
        help="Path to the previous regulatory_events.json snapshot",
    )
    regulatory_diff_parser.add_argument(
        "--new",
        type=Path,
        default=DEFAULT_DASHBOARD_EVENTS,
        help="Path to the current snapshot (defaults to the bundled dashboard events)",
    )
    regulatory_diff_parser.add_argument("--markdown-output", type=Path)
    regulatory_diff_parser.add_argument("--json-output", type=Path)
    regulatory_diff_parser.set_defaults(func=cmd_regulatory_diff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
