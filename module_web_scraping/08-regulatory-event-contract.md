# 08 - Regulatory Event Contract

## Purpose

This document defines the structure of a regulatory event.

A regulatory event is a grouped and validated regulatory development created from one or more monitored items.

The dashboard should display regulatory events, not raw source items.

## Core Principle

Many monitored items can describe one regulatory event.

Example:

```text
IAPP article
Euractiv article
European Commission draft page
EUR-Lex publication
```

should become:

```text
One regulatory event with multiple evidence sources.
```

## Minimum Fields

Each regulatory event should include:

- `event_title`
- `regulation_area`
- `topic_labels`
- `event_status`
- `summary`
- `first_detected_at`
- `last_updated_at`
- `official_publication_date`
- `effective_date`
- `application_date`
- `compliance_deadline`
- `consultation_deadline`
- `primary_official_source_url`
- `evidence_count`
- `has_official_evidence`
- `has_warning_sources`
- `validation_explanation`
- `recommended_attention`

## Event Status

Suggested values:

```text
C_UNCONFIRMED_NEWS
B_OFFICIAL_DRAFT
A_OFFICIALLY_PUBLISHED
ARCHIVED
```

## Status Meaning

### C_UNCONFIRMED_NEWS

The event is based only on trusted news, expert commentary, or other non-binding sources.

Dashboard label:

```text
Warning
```

### B_OFFICIAL_DRAFT

The event is supported by an official draft, consultation, proposal, or guidance page.

Dashboard label:

```text
Official Draft / Upcoming
```

### A_OFFICIALLY_PUBLISHED

The event is confirmed by an official legal source such as EUR-Lex or the Official Journal.

Dashboard label:

```text
Official Alert
```

## Regulation Area

Suggested values:

```text
GDPR
AI_ACT
GDPR_AI_ACT_INTERPLAY
```

## Topic Labels

Initial topic labels:

```text
AI_ACT_GENERAL
AI_ACT_PROHIBITED_PRACTICES
AI_ACT_HIGH_RISK
AI_ACT_TRANSPARENCY
AI_ACT_GPAI
GDPR_GENERAL
GDPR_DPIA
GDPR_DATA_BREACH
GDPR_INTERNATIONAL_TRANSFERS
GDPR_AUTOMATED_DECISION_MAKING
GDPR_CONTROLLER_PROCESSOR
GDPR_DATA_SUBJECT_RIGHTS
```

## Date Fields

Regulatory events should distinguish between different date types.

Important dates:

- `first_detected_at`: when the system first detected the event;
- `last_updated_at`: when new evidence or scoring changed the event;
- `official_publication_date`: date of official publication;
- `effective_date`: when the act enters into force;
- `application_date`: when obligations start applying;
- `compliance_deadline`: deadline for affected organizations;
- `consultation_deadline`: deadline for public feedback.

Only official or clearly supported dates should appear as hard deadlines.

Dates mentioned only by news sources should remain tentative until validated.

## Evidence Fields

Each event should keep a link to the strongest official source when available.

Suggested fields:

- `primary_official_source_url`
- `evidence_count`
- `has_official_evidence`
- `has_warning_sources`

This allows the dashboard to show the difference between official evidence and warning signals.

## Explanation Fields

Each event should include a short explanation.

### validation_explanation

Explains why the event has its current status.

Example:

```text
The event is classified as an official draft because it is supported by a European Commission draft guidance page, but no final Official Journal publication has been found yet.
```

### recommended_attention

Suggested dashboard text:

```text
Monitor
Review
Action recommended
Immediate attention
```

## Example

```json
{
  "event_title": "Draft guidance on high-risk AI classification",
  "regulation_area": "AI_ACT",
  "topic_labels": [
    "AI_ACT_HIGH_RISK"
  ],
  "event_status": "B_OFFICIAL_DRAFT",
  "summary": "The European Commission has published draft guidance related to the classification of high-risk AI systems under the AI Act.",
  "first_detected_at": "2026-06-18",
  "last_updated_at": "2026-06-22",
  "official_publication_date": null,
  "effective_date": null,
  "application_date": null,
  "compliance_deadline": null,
  "consultation_deadline": null,
  "primary_official_source_url": "https://digital-strategy.ec.europa.eu/",
  "evidence_count": 3,
  "has_official_evidence": true,
  "has_warning_sources": true,
  "validation_explanation": "The event is supported by official draft guidance but has not been confirmed as a final binding publication.",
  "recommended_attention": "Monitor closely"
}
```

## MVP Success Criteria

The regulatory event contract is successful if it allows the system to:

- represent one grouped event from multiple sources;
- separate warnings, official drafts, and official alerts;
- preserve official evidence and warning evidence;
- track relevant dates and deadlines;
- provide a clean object for dashboard display.

