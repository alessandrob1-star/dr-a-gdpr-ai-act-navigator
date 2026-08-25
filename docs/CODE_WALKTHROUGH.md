# Code Walkthrough

This guide maps the running application to its current source files. It is
intended for a technical presentation and describes implemented behavior, not a
future architecture.

## End-to-end assessment flow

1. `module_company_profile/dashboard/index.html` loads the application shell.
2. `assets/js/core.js` renders the questionnaire from a data-driven schema and
   applies the selected dictionary from `assets/js/i18n/locales/`.
3. `assets/js/events.js` sends questionnaire JSON to `POST /api/evaluate`.
4. `dashboard_server.py` validates the request and passes it to the Company
   Profile Agent.
5. The Company Profile Agent builds deterministic company memory.
6. The Regulatory Monitoring Agent selects the current live, cached, or
   disclosed demo feed.
7. The Regulatory Matching Agent calculates the personalized score, warnings,
   missing controls, timeline, and matched evidence.
8. The browser renders the structured result. No language model participates in
   scoring or classification.

## Runtime agents

### Company Profile Agent

- File: `module_agents/company_profile_agent.py`
- Service logic:
  `module_company_profile/memory_agent/company_memory_agent.py`
- Input: validated questionnaire JSON.
- Output: normalized company, AI, privacy, governance, relevance-tag, control,
  and assessment-trace data.

The boundary is intentionally small. `build_company_memory()` contains the
auditable deterministic rules, while the agent exposes a clear runtime role.

### Regulatory Monitoring Agent

- File: `module_agents/regulatory_monitoring_agent.py`
- Collection pipeline: `module_web_scraping/`
- Input: curated source registry and stored live-feed file.
- Output: feed records plus truthful `live`, `cached`, or `demo` metadata.

The agent never presents cached or bundled data as a successful live refresh.

### Regulatory Matching Agent

- File: `module_agents/regulatory_matching_agent.py`
- Matching services:
  `module_company_profile/memory_agent/company_memory_agent.py`
- Input: company memory, regulatory-event catalog, and active feed.
- Output: risk score, warnings, linked missing controls, timeline, official
  updates, early warnings, and explanations of triggering answers.

Matching and scoring are deterministic and inspectable.

### Dr. A Agent

- File: `module_agents/dr_a_agent.py`
- Input: server-rebuilt assessment context, current question, recent history,
  and matched sources.
- Output: a progressively streamed GPT-5.6 Sol explanation and cited sources.

The agent selects a compact evidence scope for the current topic, including
dedicated handling for DPIA, possible high-risk classification, international
transfers, warning controls, and ordered priorities. It validates legal
references, linked controls, supported transfer mechanisms, language integrity,
and internal-field leakage. A failed draft gets one sanitized model-generated
correction attempt; the application does not substitute canned answers.

### Policy Agent

- Package: `policy_agent/`
- Input guard: `input_guard.py`
- Output guard: `output_guard.py`
- Intent classification and policies: `classifier.py` and `policies.py`

The Policy Agent is deterministic and separate from Dr. A. It blocks explicit
regulatory evasion, fraud, prompt injection, and requests for guaranteed legal
conclusions in English and Italian. Legitimate compliance questions continue to
the OpenAI model.

## HTTP adapter

`module_company_profile/dashboard/dashboard_server.py` is deliberately thin. It
does not contain agent intelligence or hardcoded chat answers. Its main routes
are:

| Route | Responsibility |
|---|---|
| `GET /api/health` | Dashboard and OpenAI status |
| `GET /api/profiles` | List local assessment snapshots |
| `POST /api/evaluate` | Run the three deterministic assessment-agent handoffs |
| `POST /api/demo-profile` | Load and evaluate a bundled profile |
| `POST /api/refresh-news` | Refresh sources and recalculate the assessment |
| `POST /api/chat` | Run Policy Agent, Dr. A, model streaming, and validation |
| `POST /api/profile/*` | Save, load, compare, and delete snapshots |
| `POST /api/export-report` | Rebuild trusted data and export PDF or DOCX |

The server rebuilds derived data from questionnaire answers for chat, snapshots,
and reports instead of trusting browser-supplied scores or warnings.

## Frontend structure

The browser has no build step and no external translation service:

- `index.html`: semantic application shell and asset loading;
- `assets/css/`: base, layout, component, and responsive styles;
- `assets/js/core.js`: questionnaire schema, state, rendering, and localization;
- `assets/js/events.js`: user actions and API calls;
- `assets/js/progress.js`: derived Progress metrics, CSP-safe SVG charts, control lists, and milestones;
- `assets/js/help.js`: page-specific contextual Help for Questionnaire, Dashboard, and Progress;
- `assets/js/i18n/core.js`: translation lookup and coverage checks;
- `assets/js/i18n/locales/<code>.js`: one complete dictionary per language;
- `assets/flags/`: locally served language flags;
- `assets/fonts/`: locally served UI fonts.

The application supports all 25 configured languages through separate local dictionary files.

## Persistence and reports

- Snapshot logic: `module_company_profile/dashboard/profile_store.py`
- Local history: `storage/company_profile/history/`
- Report generation: `module_company_profile/dashboard/report_exporter.py`
- Local report translation adapter: `module_company_profile/dashboard/report_localizer.py`
- Formats: PDF and DOCX, generated in the dashboard language by reusing the same 25 offline locale dictionaries.

## Suggested technical presentation

1. Show `evaluate_payload()` to explain the three deterministic agent handoffs.
2. Show `build_company_memory()` and the assessment trace.
3. Show the Regulatory Matching Agent and compare two demo profiles.
4. Show the separate locale files and switch the dashboard language.
5. Show `build_question_context()` in Dr. A and ask a grounded follow-up.
6. Show the Policy Agent blocking an explicit compliance-evasion request.
7. Show the Progress page and explain that it visualizes deterministic assessment data without creating a second score.
8. Close with the automated tests, Docker configuration, and localized reports.
