# 07 - Source Evidence Contract

## Purpose

This document defines how source evidence should be represented for each regulatory event.

Source evidence explains why an event exists, how it was validated, and which sources support it.

The dashboard should make evidence visible so users can distinguish between:

- official legal confirmation;
- official drafts or guidance;
- trusted warning sources;
- expert commentary.

## Core Principle

Every regulatory event must be traceable.

The system should never show a status or score without being able to point back to source evidence.

## Evidence Relationship

One regulatory event can have multiple evidence records.

Example:

```text
Regulatory Event:
Draft guidance on high-risk AI classification

Evidence:
- European Commission draft guidance
- IAPP article
- Euractiv article
```

## Minimum Fields

Each evidence record should include:

- `event_id`
- `monitored_item_id`
- `source_name`
- `source_url`
- `source_type`
- `authority_level`
- `evidence_role`
- `title`
- `published_date`
- `retrieved_at`
- `evidence_summary`
- `confidence_contribution`

## Source Type

Suggested values:

```text
official_journal
official_api
official_reference
official_guidance
official_news
trusted_news
expert_source
vendor_content
```

## Authority Level

Suggested values:

```text
official_binding
official_guidance
official_draft
trusted_warning
low_priority
```

## Evidence Role

Suggested values:

```text
initial_signal
supporting_warning
official_draft_evidence
official_confirmation
related_guidance
background_context
```

## Role Definitions

### initial_signal

The first source that caused the event to be created.

This is often a trusted warning source.

### supporting_warning

A non-official source that supports the existence of a topic but does not confirm legal status.

### official_draft_evidence

An official proposal, consultation, draft, or guidance page.

This can move an event to:

```text
B_OFFICIAL_DRAFT
```

### official_confirmation

An official binding or strongly authoritative source.

This can move an event to:

```text
A_OFFICIALLY_PUBLISHED
```

### related_guidance

Guidance that helps interpret an already existing legal obligation.

### background_context

Useful context that should not directly drive validation status.

## Evidence Priority

When displaying evidence, the strongest sources should appear first.

Suggested priority order:

1. Official Journal / EUR-Lex legal act.
2. ELI stable legal link.
3. European Commission official publication.
4. European AI Office official guidance.
5. EDPB final guideline or recommendation.
6. Official draft or public consultation.
7. Trusted news.
8. Expert commentary.
9. Vendor content.

## Confidence Contribution

Each evidence source can contribute to the reliability score.

Suggested examples:

```text
Official Journal / EUR-Lex legal act: 95
European Commission official publication: 80
European AI Office official guidance: 75
EDPB final guideline: 75
Official draft or consultation: 65
Trusted news source: 35
Expert commentary: 30
Vendor content: 15
```

Repeated news coverage can support an event, but it should not replace official confirmation.

## Dashboard Display

The dashboard should separate evidence into groups:

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

This makes the system transparent and avoids treating news as binding law.

## MVP Success Criteria

The source evidence layer is successful if it can:

- link each event to its supporting sources;
- distinguish official evidence from warning sources;
- explain why the validation status was assigned;
- support reliability scoring;
- provide clear evidence links for the dashboard.

