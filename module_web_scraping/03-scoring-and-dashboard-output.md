# 03 - Scoring and Dashboard Output

## Purpose

This document defines how validated regulatory events are scored and prepared for dashboard display.

The goal is to help users understand:

- how reliable an event is;
- how urgent it is;
- how significant it may be;
- which evidence supports it;
- whether it should be shown as a warning, draft, or official alert.

## Core Principle

Reliability and risk are different concepts.

Reliability answers:

```text
How official and well-supported is this regulatory event?
```

Risk answers:

```text
How important or urgent could this event be for a company?
```

A news article may describe a serious possible change, but if it is not confirmed by official sources, reliability remains limited.

## Score Dimensions

### Reliability Score

Reliability measures the strength of the evidence supporting an event.

Suggested scale:

```text
0-30   Low reliability
31-55  Warning signal
56-80  Official draft or official guidance
81-100 Officially published or strongly confirmed
```

Example source weights:

```text
Official Journal / EUR-Lex legal act: 95
ELI stable legal act link: 95
European Commission official publication: 80
European AI Office official guidance: 75
EDPB final guideline: 75
Official draft / public consultation: 65
Trusted news source: 35
Expert legal blog: 30
Vendor content: 15
```

Repeated news coverage can support an event, but it should not replace official confirmation.

### Urgency Score

Urgency measures how soon the event may require attention.

Suggested scale:

```text
0-25   No clear deadline or long-term monitoring
26-50  Future deadline, not immediate
51-75  Deadline approaching
76-100 Immediate or already applicable
```

Important date types:

- publication date;
- entry into force date;
- application date;
- compliance deadline;
- consultation deadline.

Only dates from official sources should drive high urgency.

If a date appears only in a news article, it should be treated as tentative until validated.

### Regulatory Impact Score

Regulatory impact measures the legal significance of the event.

Examples:

```text
AI Act prohibited practice: very high
AI Act high-risk system obligation: high
AI Act transparency obligation: medium-high
GDPR personal data breach notification: high
GDPR DPIA guidance: medium-high
General policy commentary: low-medium
```

### Business Impact Score

Business impact depends on the company profile.

This module can prepare the field, but the final value should be calculated when the Company Profile module is connected.

Examples:

- high-risk AI guidance matters more to companies using AI in HR, education, credit, healthcare, or critical infrastructure;
- GDPR breach guidance matters more to companies processing personal data;
- GPAI obligations matter more to model providers than to simple deployers.

## Priority Bands

Suggested dashboard priority:

```text
0-24    Low
25-49   Medium
50-74   High
75-100  Critical
```

Suggested labels:

```text
Low: Monitor
Medium: Review
High: Action recommended
Critical: Immediate attention
```

## Dashboard Event Output

The dashboard should receive grouped regulatory events, not raw scraped items.

Minimum event fields:

- `event_title`
- `regulation_area`
- `topic_labels`
- `event_status`
- `summary`
- `reliability_score`
- `urgency_score`
- `regulatory_impact_score`
- `business_impact_score`
- `overall_priority`
- `primary_official_source_url`
- `evidence_count`
- `validation_explanation`
- `recommended_attention`

## Dashboard Status Labels

Internal validation statuses should be translated into user-friendly labels.

```text
C_UNCONFIRMED_NEWS -> Warning
B_OFFICIAL_DRAFT -> Official Draft / Upcoming
A_OFFICIALLY_PUBLISHED -> Official Alert
ARCHIVED -> Archived
```

## Evidence Display

Each event should show the sources that support it.

Suggested groups:

```text
Official evidence
Warning sources
Background context
```

Example:

```text
Official evidence:
- European Commission draft guidance

Warning sources:
- IAPP News article
- Euractiv Tech article
```

This makes the system traceable and prevents non-official news from being confused with binding law.

## Timeline Output

The dashboard should support a timeline of relevant dates.

Timeline date types:

- first detected;
- official publication;
- entry into force;
- application date;
- compliance deadline;
- consultation deadline.

Only official or clearly supported dates should appear as hard deadlines.

Tentative dates can be shown as notes or warnings, but should not be treated as confirmed compliance deadlines.

## MVP Success Criteria

The scoring and dashboard output layer is successful if it can:

- show whether an event is a warning, draft, or official alert;
- explain why an event has a given reliability score;
- highlight urgency based on validated dates;
- separate official evidence from news evidence;
- provide clean event objects for the dashboard;
- support a compliance timeline.

