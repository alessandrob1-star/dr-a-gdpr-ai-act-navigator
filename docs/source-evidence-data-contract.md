# Source Evidence Data Contract

## Purpose

This document defines how source evidence should be represented for each regulatory event.

Source evidence explains why an event exists, how it was validated, and which sources support it.

The dashboard should make the evidence visible so users can distinguish between:

- official legal confirmation;
- official draft or guidance;
- trusted warning sources;
- expert commentary.

## Core Principle

Every regulatory event should be traceable.

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

## Required Fields

### evidence_id

Unique identifier of the evidence record.

### event_id

Reference to the related regulatory event.

### monitored_item_id

Reference to the original monitored item.

### source_name

Human-readable name of the source.

Examples:

```text
EUR-Lex Official Journal
European Commission AI Office
EDPB
IAPP News
Euractiv Tech
```

### source_url

URL of the source item.

If a stable or official link is available, use that as the preferred URL.

### source_type

Type of source.

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

### authority_level

Authority level of the source.

Suggested values:

```text
official_binding
official_guidance
official_draft
trusted_warning
low_priority
```

### evidence_role

Role played by the source in the event.

Suggested values:

```text
initial_signal
supporting_warning
official_draft_evidence
official_confirmation
related_guidance
background_context
```

## Optional Fields

### title

Title of the source item.

### published_date

Publication date stated by the source.

### retrieved_at

Date and time when the system collected the evidence.

### evidence_summary

Short explanation of what the source contributes.

### quoted_reference

Short reference text or excerpt.

For the MVP, use this carefully and avoid storing long copyrighted text.

### confidence_contribution

How much this source contributes to event reliability.

Suggested scale:

```text
0-100
```

Example:

```text
Official Journal: 95
European Commission draft: 65
IAPP article: 35
Vendor blog: 15
```

## Evidence Role Definitions

### initial_signal

The first source that caused the event to be created.

This is often a trusted news source.

### supporting_warning

A non-official source that supports the existence of the topic but does not confirm legal status.

### official_draft_evidence

An official proposal, draft, consultation, or guidance page.

This can move an event to:

```text
B_OFFICIAL_DRAFT
```

### official_confirmation

An official binding source.

This can move an event to:

```text
A_OFFICIALLY_PUBLISHED
```

### related_guidance

Guidance that helps interpret an already existing legal obligation.

### background_context

Useful context, but not enough to influence validation status directly.

## Evidence Priority

When displaying evidence, show strongest sources first.

Suggested order:

1. Official Journal / EUR-Lex legal act.
2. ELI stable legal link.
3. European Commission official publication.
4. European AI Office official guidance.
5. EDPB final guideline or recommendation.
6. Official draft or public consultation.
7. Trusted news.
8. Expert commentary.
9. Vendor content.

## Example JSON

```json
{
  "evidence_id": 44,
  "event_id": 12,
  "monitored_item_id": 83,
  "source_name": "European Commission Digital Strategy",
  "source_url": "https://digital-strategy.ec.europa.eu/",
  "source_type": "official_guidance",
  "authority_level": "official_draft",
  "evidence_role": "official_draft_evidence",
  "title": "Draft guidance on high-risk AI classification",
  "published_date": "2026-06-18",
  "retrieved_at": "2026-06-21T20:00:00",
  "evidence_summary": "The source provides official draft guidance related to high-risk AI classification under the AI Act.",
  "quoted_reference": null,
  "confidence_contribution": 65
}
```

## Dashboard Display

The dashboard should separate evidence visually.

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

## MVP Boundary

The first version should prioritize source links and short summaries.

Avoid:

- long copied source text;
- unsupported legal conclusions;
- treating commentary as official evidence.

The evidence layer should make the system transparent and auditable.

