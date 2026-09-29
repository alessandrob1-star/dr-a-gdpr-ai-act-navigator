# Final Validation Report

**Project:** Dr. G.D.P.R. & AI Act navigator
**Candidate release:** release candidate
**Validation scope:** browser dashboard, deterministic assessment pipeline,
Dr. A, Policy Agent, localization, reports, Progress, Compliance Action
Workspace, Help, source refresh, and Docker configuration

## 1. Environment

- Windows desktop validation host
- Dashboard: `http://localhost:8771`
- OpenAI model: `gpt-5.6-sol`
- Local validation interpreter: Python `3.14.5`
- CI target and Docker base: Python `3.12`
- Docker Compose passes `OPENAI_API_KEY` only at runtime

The submitted assistant runtime is fixed to the official OpenAI endpoint and
the exact `gpt-5.6-sol` model. Deterministic scoring, policy, and grounding
checks remain independent from model-generated explanations.

## 2. Automated validation

The following checks were run against the complete release candidate:

| Check | Result |
|---|---|
| Python test suite | **136 passed** |
| Deterministic Policy Agent evaluation | **52/52 passed**; 32/32 adversarial cases blocked; 20/20 benign cases allowed |
| Ruff format check | Passed |
| Ruff lint check | Passed |
| Mypy static type check | Passed |
| JavaScript syntax check | Passed across 33 files |
| Shell launcher syntax | Passed |
| Docker Compose configuration | Valid |
| Dockerfile runtime alignment | All seven Python Dockerfiles use `python:3.12-slim` |
| Diff whitespace validation | Passed |

The Python suite covers Policy Agent decisions, adversarial guardrail cases,
assessment explanations, agent boundaries, regulatory citations, regulatory
diffs, source monitoring, EUR-Lex integration, dashboard APIs, report export,
frontend security, action-plan workflow gates, and the complete 25-language
dictionary contracts.

## 3. Manual end-to-end validation

All manual scenarios below passed for the release candidate.

| Scenario | Expected behavior | Result |
|---|---|---|
| High-risk HR AI demo | Acme HR AI, score 100/100, six tags, six matched events | Passed |
| Progress overview | 100/100, two existing controls, eight missing/to-check controls, three milestones, 20% coverage, one high and three medium priorities | Passed |
| Compliance Action Workspace | Eight tasks sync from trusted findings; owner and human approval gate active work; evidence gates completion; revision persists | Passed |
| Italian localization | Questionnaire, Dashboard, Progress, Help, warnings, controls, charts, and snapshot placeholders localize without technical keys | Passed |
| Contextual Help | Questionnaire, Dashboard, and Progress show page-specific content; modal scrolling, close control, Escape behavior, and floating access remain usable | Passed |
| Localized reports | PDF and DOCX export in Italian with readable headings, score, warnings, controls, timeline, disclaimer, accents, and layout | Passed |
| Dr. A profile grounding | Priority and DPIA follow-up answers use Acme HR AI assessment facts and the relevant GDPR/AI Act context | Passed |
| Policy Agent | Explicit request to appear compliant before implementing controls is blocked | Passed |
| Transfer evidence boundary | Confirmed and unresolved transfer facts are separated; unsupported transfer mechanisms are not invented | Passed |
| Low-risk SaaS profile | CalmDesk SaaS produces 44/100, medium attention, and two relevant tags without retaining Acme HR AI state | Passed |
| JSON questionnaire loading | Loaded JSON populates the form and clears the visual selection state of demo buttons | Passed |
| Live source refresh | Refresh gives visual feedback, updates the timestamp, and preserves official/early-warning separation and source links | Passed |
| Snapshot persistence | Assessment snapshot saves, appears in history, reloads, and preserves the profile and score | Passed |
| Dutch localization | Questionnaire, Dashboard, Progress, Help, chart labels, timeline, controls, and snapshot actions remain localized | Passed |

## 4. Release evidence

- New README screenshots were captured after the manual validation and replace
  the previous image set.
- The screenshots show English, Italian, and Dutch questionnaire states;
  contextual Help for all three main views; the Progress overview; and a
  grounded Dr. A conversation.
- Screenshots showing a disconnected model or an empty frame were excluded.

## 5. Known boundaries

- The product provides decision support and general compliance information; it
  does not certify legal compliance or replace qualified legal advice.
- Live source refresh depends on the availability and structure of curated
  external sources.
- File-based history is appropriate for the local single-user demo, not a
  concurrent production deployment.
- The Compliance Action Workspace is currently English-only.
- Dr. A output still requires human review despite independent policy and
  grounding validation.

## 6. Approval status

The candidate is ready for pull-request review. The release tag must be created
from the merged `main` commit so that the published release exactly matches the
reviewed code and documentation.
