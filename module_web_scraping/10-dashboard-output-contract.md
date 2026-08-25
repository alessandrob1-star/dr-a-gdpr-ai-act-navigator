# 10 - Dashboard Output Contract

## Purpose

This document defines the dashboard-ready output produced by the Web Scraping and Source Monitoring module.

The dashboard should not consume raw scraped items directly. It should receive grouped, validated, scored, and traceable regulatory events.

## Core Principle

The frontend should display regulatory intelligence, not raw monitoring noise.

The backend module should transform:

```text
sources -> monitored items -> grouped events -> validation -> scoring -> dashboard output
```

into clean event objects that are easy to understand and explain.

## Dashboard Event Object

Each dashboard event should represent one regulatory development.

Minimum fields:

- `event_title`
- `regulation_area`
- `topic_labels`
- `event_status`
- `dashboard_label`
- `summary`
- `reliability_score`
- `urgency_score`
- `regulatory_impact_score`
- `business_impact_score`
- `overall_priority`
- `recommended_attention`
- `primary_official_source_url`
- `evidence_count`
- `has_official_evidence`
- `has_warning_sources`
- `first_detected_at`
- `last_updated_at`
- `official_publication_date`
- `effective_date`
- `application_date`
- `compliance_deadline`
- `consultation_deadline`
- `validation_explanation`
- `scoring_explanation`

## Status Labels

Internal validation statuses should be translated into user-friendly dashboard labels.

```text
C_UNCONFIRMED_NEWS -> Warning
B_OFFICIAL_DRAFT -> Official Draft / Upcoming
A_OFFICIALLY_PUBLISHED -> Official Alert
ARCHIVED -> Archived
```

## Priority Labels

Suggested dashboard priority bands:

```text
0-24    Low
25-49   Medium
50-74   High
75-100  Critical
```

Suggested attention labels:

```text
Low -> Monitor
Medium -> Review
High -> Action recommended
Critical -> Immediate attention
```

## Evidence Output

Each event should expose evidence in a way that the dashboard can display clearly.

Suggested evidence groups:

- official evidence;
- warning sources;
- background context.

Example:

```text
Official evidence:
- EUR-Lex legal act
- European Commission guidance

Warning sources:
- IAPP News article
- Euractiv Tech article
```

This makes it clear whether an event is supported by binding legal sources or only by early warning signals.

## Timeline Output

The dashboard should support timeline and deadline views.

Important date types:

- first detected;
- official publication date;
- entry into force date;
- application date;
- compliance deadline;
- consultation deadline.

Only official or clearly supported dates should appear as hard deadlines.

Dates mentioned only by news sources should remain tentative until validated against official sources.

## Suggested Dashboard Sections

### Official Alerts

Events with:

```text
A_OFFICIALLY_PUBLISHED
```

These should be shown as the highest-confidence legal alerts.

### Official Drafts / Upcoming

Events with:

```text
B_OFFICIAL_DRAFT
```

These should be monitored closely because they are official but may not yet be binding.

### News Warnings

Events with:

```text
C_UNCONFIRMED_NEWS
```

These should be clearly marked as warning signals.

### Compliance Timeline

Displays validated dates and deadlines.

The timeline should prioritize:

- already applicable obligations;
- deadlines within 30 days;
- deadlines within 90 days;
- upcoming application dates;
- consultation deadlines.

### Source Evidence Panel

Shows why the system assigned a status and score.

The panel should include:

- source name;
- source type;
- authority level;
- evidence role;
- source link;
- publication date;
- short evidence summary.

## Example Output

```json
{
  "event_title": "Draft guidance on high-risk AI classification",
  "regulation_area": "AI_ACT",
  "topic_labels": ["AI_ACT_HIGH_RISK"],
  "event_status": "B_OFFICIAL_DRAFT",
  "dashboard_label": "Official Draft / Upcoming",
  "summary": "The European Commission has published draft guidance related to high-risk AI classification under the AI Act.",
  "reliability_score": 65,
  "urgency_score": 55,
  "regulatory_impact_score": 85,
  "business_impact_score": 80,
  "overall_priority": "High",
  "recommended_attention": "Monitor closely",
  "primary_official_source_url": "https://digital-strategy.ec.europa.eu/",
  "evidence_count": 3,
  "has_official_evidence": true,
  "has_warning_sources": true,
  "first_detected_at": "2026-06-18",
  "last_updated_at": "2026-06-22",
  "official_publication_date": null,
  "effective_date": null,
  "application_date": null,
  "compliance_deadline": null,
  "consultation_deadline": null,
  "validation_explanation": "The event is supported by official draft guidance but has not been confirmed as a final binding publication.",
  "scoring_explanation": "Reliability is based on official draft evidence. Regulatory impact is high because the topic concerns high-risk AI systems."
}
```

## MVP Success Criteria

The dashboard output contract is successful if it allows the frontend to:

- show official alerts, official drafts, and warnings separately;
- display reliability and urgency clearly;
- expose official evidence and warning sources;
- show validated deadlines and timeline dates;
- explain why an event is relevant and how it was scored;
- avoid showing duplicate raw source items.

