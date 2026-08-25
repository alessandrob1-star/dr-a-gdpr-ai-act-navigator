# 11 - Urgency and Deadline Logic

## Purpose

This document defines how the module should detect and use regulatory dates and deadlines.

Deadline handling is important because regulatory intelligence is only useful if the user understands when an obligation becomes relevant.

## Core Principle

Urgency should be based on validated dates, not on speculation.

Dates found in official sources can drive urgency scoring.

Dates mentioned only in news or commentary should remain tentative until confirmed by official evidence.

## Date Types

The module should distinguish between different date types.

### first_detected_at

Date when the system first detected the regulatory event.

### last_updated_at

Date when the event was last updated by new evidence, validation, or scoring.

### official_publication_date

Date when an official source published the act, guidance, draft, or notice.

### effective_date

Date when a legal act enters into force.

### application_date

Date when obligations start applying.

This can be different from the effective date.

### compliance_deadline

Date by which affected organizations should comply.

### consultation_deadline

Date by which feedback must be submitted for a public consultation or draft guidance.

## Official vs Tentative Dates

The system should classify dates by evidence strength.

### Official Dates

Dates from sources such as:

- EUR-Lex;
- Official Journal;
- European Commission;
- European AI Office;
- EDPB.

These can be used for urgency scoring and timeline display.

### Tentative Dates

Dates from:

- news articles;
- expert commentary;
- vendor content;
- informal summaries.

These should be stored as notes or warnings, but they should not drive high urgency until validated.

## Urgency Score

Urgency measures how soon the company may need to act.

Suggested scale:

```text
0-25   No clear deadline or long-term monitoring
26-50  Future deadline, not immediate
51-75  Deadline approaching
76-100 Immediate or already applicable
```

## Initial Scoring Rules

Suggested rules:

```text
Already applicable: 90
Deadline within 30 days: 85
Deadline within 90 days: 70
Deadline within 6 months: 55
Deadline within 12 months: 40
No official deadline found: 20
Official draft with uncertain timing: 30
Tentative news-only deadline: 25
```

These values can be refined after the first MVP.

## Timeline Display

The dashboard should show a timeline using validated dates.

Recommended timeline order:

1. First detected.
2. Official publication.
3. Entry into force.
4. Application date.
5. Compliance deadline.
6. Consultation deadline.

Hard deadlines should be visually separated from tentative dates.

## Examples

### Official Publication Already Applicable

```text
Source: EUR-Lex
Status: A_OFFICIALLY_PUBLISHED
Application date: already passed
Urgency score: 90
```

### Official Draft With Consultation Deadline

```text
Source: European Commission
Status: B_OFFICIAL_DRAFT
Consultation deadline: within 60 days
Urgency score: 70
```

### News Warning With Unconfirmed Date

```text
Source: trusted news
Status: C_UNCONFIRMED_NEWS
Date mentioned: next month
Urgency score: 25
```

The date is useful context, but not a confirmed compliance deadline.

## MVP Success Criteria

The urgency and deadline logic is successful if the system can:

- extract important dates from source items;
- distinguish official dates from tentative dates;
- calculate a simple urgency score;
- support a dashboard timeline;
- avoid treating news-only dates as confirmed deadlines.

