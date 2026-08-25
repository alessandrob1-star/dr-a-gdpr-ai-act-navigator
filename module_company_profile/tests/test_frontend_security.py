from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "module_company_profile" / "dashboard"


def test_chat_markdown_always_uses_the_restricted_renderer():
    index = (DASHBOARD / "index.html").read_text(encoding="utf-8")
    core = (DASHBOARD / "assets" / "js" / "core.js").read_text(encoding="utf-8")
    events = (DASHBOARD / "assets" / "js" / "events.js").read_text(encoding="utf-8")
    renderer = (DASHBOARD / "assets" / "js" / "safe-markdown.js").read_text(encoding="utf-8")

    assert index.index("marked.min.js") < index.index("safe-markdown.js") < index.index("core.js")
    assert "marked.parse(" not in core
    assert "marked.parse(" not in events
    assert "renderSafeMarkdown(text)" in core
    assert "renderSafeMarkdown(streamedReply)" in events
    assert "renderer.html" in renderer
    assert "renderer.link" in renderer
    assert "renderer.image" in renderer
    assert '["http:", "https:"]' in renderer


def test_contextual_help_uses_csp_safe_dom_rendering():
    index = (DASHBOARD / "index.html").read_text(encoding="utf-8")
    help_script = (DASHBOARD / "assets" / "js" / "help.js").read_text(encoding="utf-8")

    assert 'src="assets/js/help.js"' in index
    assert "style=" not in index
    assert ".innerHTML" not in help_script
    assert ".style." not in help_script
    assert "replaceChildren()" in help_script
    assert 'return "progress"' in help_script
    assert "progress_title" in help_script


def test_progress_view_uses_assessment_data_and_safe_script_order():
    index = (DASHBOARD / "index.html").read_text(encoding="utf-8")
    progress = (DASHBOARD / "assets" / "js" / "progress.js").read_text(encoding="utf-8")

    assert 'id="progressPage"' in index
    assert index.index("core.js") < index.index("progress.js") < index.index("events.js")
    assert "payload.dashboard_context" in progress
    assert "payload.company_memory" in progress
    assert 'fetch("/api/profiles")' not in progress
    assert "memory.controls?.existing" in progress
    assert "memory.controls?.missing_or_to_verify" in progress
    assert "priority-pie" in progress
    assert "warning.title" in progress
    assert "function renderDonut" in progress
    assert "function isUpcomingMilestone" in progress
    assert "daysRemaining !== null" in progress
    assert '<svg class="progress-donut"' in progress
    assert "style=" not in progress
    assert "Math.random" not in progress
    assert "eval(" not in progress


def test_ci_checks_dashboard_javascript_and_report_localizer_types():
    workflow = (ROOT / ".github" / "workflows" / "web-scraping-demo.yml").read_text(
        encoding="utf-8"
    )
    assert "actions/setup-node@v6" in workflow
    assert "node --check" in workflow
    assert "module_company_profile/dashboard/report_localizer.py" in workflow


def test_shell_launchers_are_forced_to_lf_checkouts():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "*.sh text eol=lf" in attributes
