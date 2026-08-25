# 02 - Validation and Event Grouping

## Purpose

This document defines how collected source items are grouped into regulatory events and validated against official evidence.

The goal is to avoid duplicated alerts and prevent news articles from being treated as official legal updates.

## Core Principle

The system stores every collected source item, but the dashboard should display grouped regulatory events.

Example:

```text
IAPP article
Euractiv article
European Commission draft
EUR-Lex publication
```

should become:

```text
One regulatory event with multiple supporting evidence sources.
```

## Data Flow

```text
Monitored Items
      |
      v
Event Grouping and Deduplication
      |
      v
Regulatory Events
      |
      v
Validation Agent
      |
      v
Validated Events
```

## Event Grouping

Event grouping identifies whether a new monitored item belongs to an existing regulatory event or should create a new event.

Initial matching signals:

- same regulation area;
- similar normalized title;
- shared topic labels;
- same legal reference;
- same official institution;
- close publication date;
- similar summary.

## Exact Duplicate Detection

An item is an exact duplicate if:

- the URL already exists; or
- the extracted text hash already exists.

Exact duplicates should not create new events.

## Rule-Based Matching

The MVP can use a simple rule-based score.

Suggested matching signals:

```text
Same regulation area: +25
Shared legal reference: +30
Similar normalized title: +20
Shared key topics: +15
Publication date within 14 days: +10
Same official institution: +10
```

Suggested thresholds:

```text
0-39: create a new event
40-69: needs review or cautious linking
70-100: link to existing event
```

The first version should prioritize traceability over aggressive automatic merging.

## Regulatory Event

A regulatory event is the dashboard-ready representation of a regulatory development.

Minimum fields:

- `event_title`
- `regulation_area`
- `topic_labels`
- `event_status`
- `summary`
- `first_detected_at`
- `last_updated_at`
- `primary_official_source_url`
- `evidence_count`
- `validation_explanation`

## Validation Agent

The Validation Agent checks whether a regulatory event is supported by official evidence.

It answers:

```text
Is this regulatory signal confirmed by an official source?
```

## Validation Statuses

### C_UNCONFIRMED_NEWS

The signal exists only in news, expert commentary, or other non-binding sources.

Dashboard treatment:

```text
Warning
```

### B_OFFICIAL_DRAFT

The signal is supported by an official draft, proposal, consultation, or guidance page.

Dashboard treatment:

```text
Official Draft / Upcoming
```

### A_OFFICIALLY_PUBLISHED

The signal is confirmed by a binding or official legal source such as EUR-Lex or the Official Journal.

Dashboard treatment:

```text
Official Alert
```

## Evidence Priority

The strongest source should drive validation.

Priority order:

1. Official Journal / EUR-Lex legal act.
2. ELI stable legal link.
3. European Commission official publication.
4. European AI Office official guidance.
5. EDPB final guideline or recommendation.
6. Official draft or public consultation.
7. Trusted news.
8. Expert commentary.
9. Vendor content.

Repeated news coverage can support an event, but it should not make the event official.

## Source Evidence

Each event should keep links to supporting evidence.

Evidence roles:

- `initial_signal`
- `supporting_warning`
- `official_draft_evidence`
- `official_confirmation`
- `related_guidance`
- `background_context`

The dashboard should clearly separate:

- official evidence;
- warning sources;
- background context.

## Event Status Progression

An event can move upward when stronger evidence appears:

```text
C_UNCONFIRMED_NEWS -> B_OFFICIAL_DRAFT -> A_OFFICIALLY_PUBLISHED
```

Example:

1. A trusted news source reports possible AI Act guidance.
2. The event starts as `C_UNCONFIRMED_NEWS`.
3. The European Commission publishes draft guidance.
4. The event becomes `B_OFFICIAL_DRAFT`.
5. A final legal act or official publication appears.
6. The event becomes `A_OFFICIALLY_PUBLISHED`.

## MVP Success Criteria

The grouping and validation layer is successful if it can:

- avoid duplicated dashboard alerts;
- group related items into one regulatory event;
- preserve source evidence;
- distinguish warning sources from official sources;
- assign a clear validation status;
- explain why the status was assigned.

