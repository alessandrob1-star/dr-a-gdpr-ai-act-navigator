# Dashboard Output Contract

## Purpose

This document defines what the backend agents should provide to the dashboard.

The dashboard should not need to understand raw scraping results, duplicated articles, or internal validation steps. It should receive clean, grouped, explainable regulatory events.

## Main Dashboard Objects

The MVP dashboard should be built around three main objects:

- company overview;
- regulatory events;
- source evidence.

## Company Overview

The company overview comes from the Company Profile module.

Expected fields:

- `company_name`
- `industry`
- `company_size`
- `operates_in_eu`
- `uses_ai`
- `develops_ai`
- `processes_personal_data`
- `processes_sensitive_data`
- `uses_automated_decision_making`
- `possible_high_risk_ai_area`
- `overall_compliance_exposure`

This section helps explain why a regulatory event may or may not matter to a specific company.

## Regulatory Event Card

Each card in the dashboard should represent one grouped regulatory event, not one raw article.

Expected fields:

- `event_id`
- `event_title`
- `regulation_area`
- `event_status`
- `summary`
- `reliability_score`
- `urgency_score`
- `regulatory_impact_score`
- `business_impact_score`
- `overall_priority`
- `first_detected_at`
- `last_updated_at`
- `effective_date`
- `compliance_deadline`
- `recommended_attention`

Example:

```json
{
  "event_id": 12,
  "event_title": "Draft guidance on high-risk AI classification",
  "regulation_area": "AI_ACT_HIGH_RISK",
  "event_status": "B_OFFICIAL_DRAFT",
  "summary": "The European Commission has published draft guidance related to high-risk AI classification under the AI Act.",
  "reliability_score": 65,
  "urgency_score": 45,
  "regulatory_impact_score": 85,
  "business_impact_score": 70,
  "overall_priority": "High",
  "first_detected_at": "2026-06-18",
  "last_updated_at": "2026-06-21",
  "effective_date": null,
  "compliance_deadline": null,
  "recommended_attention": "Monitor closely"
}
```

## Event Status Labels

The dashboard should translate internal statuses into user-friendly labels.

Suggested mapping:

```text
C_UNCONFIRMED_NEWS -> Warning
B_OFFICIAL_DRAFT -> Official Draft / Upcoming
A_OFFICIALLY_PUBLISHED -> Official Alert
ARCHIVED -> Archived
```

## Priority Labels

Suggested mapping:

```text
Low -> Monitor
Medium -> Review
High -> Action recommended
Critical -> Immediate attention
```

## Source Evidence Panel

Each regulatory event should include evidence links.

Expected fields:

- `source_name`
- `source_type`
- `authority_level`
- `title`
- `url`
- `published_date`
- `relationship_type`

Example relationship types:

- `initial_signal`
- `supporting_news`
- `official_confirmation`
- `related_guidance`

The dashboard should make the difference between news and official evidence visible.

Example:

```text
Official evidence:
- European Commission draft guideline

Supporting warning sources:
- IAPP article
- Euractiv Tech article
```

## Timeline View

The timeline should show important dates connected to each event.

Expected date types:

- first detected;
- official publication;
- entry into force;
- application date;
- compliance deadline;
- consultation deadline.

If a date is not officially confirmed, it should be marked as tentative or kept out of the legal deadline field.

## Dashboard Sections

### Progress view

The Progress page consumes the same active `company_memory` and
`dashboard_context` objects as the dashboard. It displays:

- the current risk-attention score;
- existing and missing-or-to-check control counts and labels;
- the distribution and titles of high, medium, and low warnings;
- upcoming personalized compliance milestones.

This is a derived visualization contract. It does not modify assessment data,
infer completed work from snapshots, or introduce an alternative compliance
score.

### Company Overview

Shows the company profile and general exposure.

### Risk Dashboard

Shows the highest priority events for the company.

Recommended sorting:

```text
Critical first, then High, then Medium, then Low.
Within each band, sort by urgency score.
```

### Regulatory Alerts

Separates official alerts from warnings.

Suggested groups:

- Official Alerts;
- Official Drafts;
- News Warnings;
- Archived / Low confidence.

### Compliance Timeline

Shows future deadlines and application dates.

Only official or clearly supported dates should appear as hard deadlines.

### AI Compliance Assistant

The assistant should be able to answer questions using:

- company profile;
- official documents;
- regulatory events;
- evidence links;
- scoring explanations.

## Explainability Requirement

Every dashboard score should have an explanation.

The user should be able to understand:

- why the event was detected;
- which sources support it;
- whether it is official or only a warning;
- why the priority is high or low;
- what company profile data made it relevant.

## MVP Boundary

The dashboard should avoid presenting the system as a legal decision maker.

Recommended language:

```text
This alert is decision-support information based on monitored sources. Final compliance decisions should be reviewed by qualified professionals.
```

The MVP should focus on clarity, traceability, and prioritization.



## Legal Citation Field (`legal_citations`)

Every regulatory event emitted by `RegulatoryEvent.to_dashboard_dict()` now
includes a `legal_citations` array. This answers a compliance officer's first
two questions about any risk line — "says who?" and "is it current?" — by
tracing the event's topic labels to the specific provisions they derive from.

The mapping is deterministic and lives in `module_web_scraping/citations.py`
(keyed by the same topic labels used for scoring). Each citation object has:

| Field | Meaning | Example |
| --- | --- | --- |
| `instrument` | The legal instrument | `"EU AI Act"` / `"GDPR"` |
| `celex` | Stable EUR-Lex CELEX identifier | `"32024R1689"` |
| `articles` | Specific provision(s) | `"Article 6"`, `"Annex III"`, `"Articles 44-49"` |
| `title` | Short provision title | `"Classification rules for high-risk AI systems"` |
| `url` | Stable EUR-Lex link (article anchor) | `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689#art_6` |
| `last_verified` | Date the mapping was last checked | `"2026-07-13"` |

Example:

```json
"legal_citations": [
  {
    "instrument": "EU AI Act",
    "celex": "32024R1689",
    "articles": "Article 6",
    "title": "Classification rules for high-risk AI systems",
    "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689#art_6",
    "last_verified": "2026-07-13"
  }
]
```

Unknown topic labels yield no citation (the registry never fabricates a
reference). Coverage is enforced by `module_web_scraping/tests/test_citations.py`,
which asserts that every scored topic has at least one citation.
