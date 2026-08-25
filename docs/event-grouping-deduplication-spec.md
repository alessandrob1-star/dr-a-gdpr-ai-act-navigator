# Event Grouping and Deduplication Specification

## Purpose

This document defines how the system groups multiple monitored items into one regulatory event.

The goal is to avoid duplicated dashboard alerts when different sources report the same regulatory development.

Example:

- one IAPP article reports upcoming AI Act guidance;
- one Euractiv article reports the same development;
- the European Commission later publishes a draft page;
- EUR-Lex later publishes the final legal act.

The dashboard should show one regulatory event with multiple supporting sources, not four separate alerts.

## Core Principle

The system stores every collected item, but displays grouped regulatory events.

Raw source records:

```text
monitored_items
```

Dashboard-ready grouped records:

```text
regulatory_events
```

Relationship table:

```text
event_sources
```

## Grouping Inputs

For each monitored item, the grouping logic should use:

- normalized title;
- source type;
- regulation area;
- detected topics;
- publication date;
- extracted legal references;
- extracted institutions;
- URL;
- text hash;
- summary.

## Normalization Rules

Before comparing items, the system should normalize text.

Suggested rules:

- lowercase text;
- remove punctuation;
- remove common stop words;
- normalize common terms;
- trim extra whitespace;
- convert known aliases to standard labels.

Example aliases:

```text
Artificial Intelligence Act -> AI Act
Regulation (EU) 2024/1689 -> AI Act
General-purpose AI -> GPAI
Data Protection Impact Assessment -> DPIA
Regulation (EU) 2016/679 -> GDPR
```

## Exact Duplicate Detection

An item is an exact duplicate if:

- the URL already exists; or
- the raw text hash already exists.

Action:

```text
Do not create a new monitored item.
Mark as already seen.
```

## Same Event Detection

An item should be linked to an existing regulatory event when several signals match.

Suggested matching criteria:

- same regulation area;
- similar normalized title;
- overlapping keywords;
- same official institution;
- close publication date;
- same legal act reference;
- same guidance or proposal name.

The MVP should use a simple rule-based score.

## Rule-Based Matching Score

Suggested score:

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

For the MVP, uncertain matches can be stored as `needs_review` instead of being automatically merged.

## Key Topics

Initial topic labels:

- `AI_ACT_GENERAL`
- `AI_ACT_PROHIBITED_PRACTICES`
- `AI_ACT_HIGH_RISK`
- `AI_ACT_TRANSPARENCY`
- `AI_ACT_GPAI`
- `GDPR_GENERAL`
- `GDPR_DPIA`
- `GDPR_DATA_BREACH`
- `GDPR_INTERNATIONAL_TRANSFERS`
- `GDPR_AUTOMATED_DECISION_MAKING`
- `GDPR_CONTROLLER_PROCESSOR`
- `GDPR_DATA_SUBJECT_RIGHTS`

Each monitored item can have one or more topic labels.

## Event Creation Rules

Create a new `regulatory_events` record when:

- no existing event has a strong match;
- the item concerns a clearly different topic;
- the item concerns a different legal act;
- the item concerns a different compliance deadline;
- the item is from an official source and introduces a new regulatory development.

Initial event status depends on the source:

```text
Trusted news only -> C_UNCONFIRMED_NEWS
Official draft/guidance -> B_OFFICIAL_DRAFT
Official binding publication -> A_OFFICIALLY_PUBLISHED
```

## Event Update Rules

When a monitored item is linked to an existing event, the system should update:

- `last_updated_at`;
- `event_status` if the new item provides stronger evidence;
- `reliability_score`;
- `effective_date` or `compliance_deadline` if official dates are found;
- source evidence list.

Event status can move upward:

```text
C_UNCONFIRMED_NEWS -> B_OFFICIAL_DRAFT -> A_OFFICIALLY_PUBLISHED
```

Event status should not move upward based only on repeated news coverage.

## Evidence Priority

When multiple items support one event, the strongest evidence should drive validation.

Priority order:

1. Official Journal / EUR-Lex legal act.
2. ELI stable legal act link.
3. European Commission official publication.
4. European AI Office official guidance.
5. EDPB final guideline or recommendation.
6. Official draft or consultation.
7. Trusted news.
8. Expert commentary.
9. Vendor content.

## Example

### Item 1

```text
Source: IAPP
Title: A view from Brussels: Upcoming guidelines on GDPR and AI Act interplay
Type: trusted_news
```

Result:

```text
Create event.
Status: C_UNCONFIRMED_NEWS
Reliability: 35
```

### Item 2

```text
Source: Euractiv
Title: EU officials prepare guidance on AI Act and GDPR overlap
Type: trusted_news
```

Result:

```text
Link to existing event.
Status remains: C_UNCONFIRMED_NEWS
Reliability may increase slightly.
```

### Item 3

```text
Source: European Commission
Title: Draft guidance on the interaction between the AI Act and GDPR
Type: official_draft
```

Result:

```text
Link to existing event.
Status becomes: B_OFFICIAL_DRAFT
Reliability increases significantly.
```

### Item 4

```text
Source: EUR-Lex
Title: Official publication of related legal act
Type: official_publication
```

Result:

```text
Link to existing event.
Status becomes: A_OFFICIALLY_PUBLISHED
Reliability becomes high.
```

## MVP Boundary

The first version should use deterministic matching.

Later improvements can include:

- embedding similarity;
- clustering;
- human review queue;
- stored procedures for periodic compaction;
- confidence explanation generated by an LLM;
- manual merge and split controls.

The MVP should prioritize traceability over aggressive automatic merging.

