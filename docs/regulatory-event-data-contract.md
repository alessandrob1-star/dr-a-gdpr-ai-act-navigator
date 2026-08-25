# Regulatory Event Data Contract

## Purpose

This document defines the structure of a regulatory event.

A regulatory event is a grouped and validated regulatory development created from one or more monitored items.

The dashboard should display regulatory events, not raw monitored items.

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

## Required Fields

### event_id

Unique identifier of the regulatory event.

### event_title

Human-readable title of the event.

The title should describe the regulatory development, not the source article.

Example:

```text
Draft guidance on high-risk AI classification
```

### regulation_area

Main regulatory area.

Suggested values:

```text
GDPR
AI_ACT
GDPR_AI_ACT_INTERPLAY
```

### topic_labels

Specific topic labels connected to the event.

Suggested values:

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

### event_status

Validation status of the event.

Suggested values:

```text
C_UNCONFIRMED_NEWS
B_OFFICIAL_DRAFT
A_OFFICIALLY_PUBLISHED
ARCHIVED
```

### summary

Short explanation of what happened and why it matters.

The summary should be factual and should not overstate legal certainty.

### first_detected_at

When the event was first detected by the system.

### last_updated_at

When the event was last updated by a new source, validation result, score update, or date extraction.

## Scoring Fields

### reliability_score

How strongly the event is supported by official evidence.

Scale:

```text
0-100
```

### urgency_score

How soon the event may require attention.

Scale:

```text
0-100
```

### regulatory_impact_score

How legally significant the regulatory development is.

Scale:

```text
0-100
```

### business_impact_score

How relevant the event is to the company profile.

Scale:

```text
0-100
```

This score may be empty before the Company Profile module is connected.

### overall_priority

Dashboard-friendly priority label.

Suggested values:

```text
Low
Medium
High
Critical
```

## Date Fields

### official_publication_date

Date of official publication, if confirmed.

### effective_date

Date when the legal act enters into force, if available.

### application_date

Date when obligations start applying, if different from the effective date.

### compliance_deadline

Deadline for companies to comply, if clearly stated.

### consultation_deadline

Deadline for public consultation or feedback, if relevant.

## Evidence Fields

### primary_official_source_url

The strongest official source supporting the event.

Examples:

- EUR-Lex legal act;
- Official Journal publication;
- European Commission official page;
- EDPB final guideline.

### evidence_count

Number of monitored items linked to the event.

### has_official_evidence

Boolean field.

True if at least one official source supports the event.

### has_warning_sources

Boolean field.

True if at least one trusted news or expert commentary source supports the event.

## Explanation Fields

### validation_explanation

Short explanation of the validation status.

Example:

```text
The event is classified as an official draft because it is supported by a European Commission draft guideline, but no final Official Journal publication has been found.
```

### scoring_explanation

Short explanation of the scores.

Example:

```text
Reliability is medium-high due to official draft evidence. Regulatory impact is high because the event concerns high-risk AI classification.
```

### recommended_attention

Dashboard text describing what the user should do next.

Examples:

```text
Monitor
Review
Action recommended
Immediate attention
```

## Example JSON

```json
{
  "event_id": 12,
  "event_title": "Draft guidance on high-risk AI classification",
  "regulation_area": "AI_ACT",
  "topic_labels": [
    "AI_ACT_HIGH_RISK"
  ],
  "event_status": "B_OFFICIAL_DRAFT",
  "summary": "The European Commission has published draft guidance related to the classification of high-risk AI systems under the AI Act.",
  "first_detected_at": "2026-06-18",
  "last_updated_at": "2026-06-21",
  "reliability_score": 65,
  "urgency_score": 55,
  "regulatory_impact_score": 85,
  "business_impact_score": null,
  "overall_priority": "High",
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
  "scoring_explanation": "Reliability is based on official draft evidence. Regulatory impact is high because the topic concerns high-risk AI systems.",
  "recommended_attention": "Monitor closely"
}
```

## MVP Boundary

The first version should keep regulatory events simple.

The most important fields are:

- title;
- status;
- regulation area;
- topic labels;
- source evidence;
- reliability score;
- urgency score;
- summary;
- recommended attention.

The system can add richer legal interpretation later.

