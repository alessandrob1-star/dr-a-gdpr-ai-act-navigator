# Contributing

Thanks for your interest in Dr. G.D.P.R. & AI Act navigator. This project is an
educational and research prototype for European AI startups and SMEs. This
guide covers the local development workflow and the quality gates your change
must pass.

> Reminder: this project supports regulatory triage and prioritization. It does
> not provide legal advice. Please keep contributions consistent with that
> scope.

## Prerequisites

- Python 3.12
- (Optional) Docker, for the containerized dashboard and package smoke checks

## Getting set up

```bash
# 1. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2. Install the code-quality and test tooling (pinned to match CI)
python -m pip install ruff==0.15.21 mypy==2.2.0 pytest==8.4.2 pre-commit

# 3. Install the integrated application dependencies
python -m pip install -r module_company_profile/requirements.txt

# 4. Enable the local pre-commit hooks (runs the same checks as CI)
pre-commit install
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `policy_agent/` | Guardrails for evasion, fraud, prompt injection, legal-guarantee requests |
| `module_web_scraping/` | Regulatory source monitoring pipeline and connector packages |
| `module_company_profile/` | Questionnaire, risk scoring, dashboard, and report export |
| `module_agents/` | Runtime Company Profile, Regulatory Monitoring, Regulatory Matching, and Dr. A agents, plus the auditable trace demo |
| `docs/` | Architecture and module documentation |

## Quality gates

Every change must pass the same checks CI runs. Run them locally before pushing:

```bash
# Format check + lint
ruff format --check .
ruff check .

# Static type checking (configuration lives in pyproject.toml)
mypy policy_agent module_web_scraping module_agents \
  module_company_profile/memory_agent/company_memory_agent.py \
  module_company_profile/memory_agent/run_demo_profiles.py \
  module_company_profile/dashboard/dashboard_server.py \
  module_company_profile/dashboard/profile_store.py \
  module_company_profile/dashboard/report_exporter.py \
  module_company_profile/dashboard/report_localizer.py \
  module_company_profile/tests

# Tests (auto-discovered; see [tool.pytest.ini_options] in pyproject.toml)
python -m pytest
```

`ruff format .` and `ruff check . --fix` apply the safe auto-fixes.

If you install the pre-commit hooks (step 4 above), formatting, linting, type
checking, and secret scanning run automatically on every commit. To run them
against the whole repository on demand:

```bash
pre-commit run --all-files
```

## Adding tests

Tests use `unittest.TestCase` and are discovered automatically. To add a new
suite, create a `test_*.py` file under one of the existing test directories:

- `policy_agent/tests/`
- `module_company_profile/tests/`
- `module_web_scraping/tests/`

No CI edits are needed — `python -m pytest` will pick it up.

## Security

- Never commit real credentials. `config/eurlex_credentials.json` is
  git-ignored; commit only the placeholder `config/eurlex_credentials.example.json`.
- Dependency CVE scanning (`pip-audit`) and secret scanning (`gitleaks`) run
  in CI and are fail-closed. Pin any new dependency to an exact version.
- To report a vulnerability, follow [SECURITY.md](.github/SECURITY.md).

## Commit and pull request guidelines

- Use clear, imperative commit subjects (e.g. "Add EUR-Lex retry backoff").
- Keep dependency versions pinned; Dependabot manages upgrades via PRs.
- Fill out the pull request template. Ensure all CI checks are green before
  requesting review.
- A code owner review is required to merge (see [CODEOWNERS](.github/CODEOWNERS)).
