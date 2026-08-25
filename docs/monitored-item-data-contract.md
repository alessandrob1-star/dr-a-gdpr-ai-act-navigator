# Monitored Item Data Contract

## Purpose

This document defines the structure of a monitored item.

A monitored item is a single record collected from a source before deduplication, validation, scoring, or dashboard grouping.

Examples:

- one news article;
- one official Commission page;
- one EDPB guideline page;
- one EUR-Lex item;
- one RSS entry;
- one downloaded official document reference.

## Core Principle

The Source Monitoring Agent should save structured records before reasoning on them.

This makes the pipeline easier to debug:

```text
source -> monitored item -> regulatory event -> validation -> scoring -> dashboard
```

## Required Fields

### source_id

Reference to the source registry.

Example:

```text
IAPP News
EUR-Lex Official Journal
European Commission AI Office
```

### title

Original title extracted from the source.

The title should be saved as close as possible to the source version.

### url

Canonical URL of the item.

If the source provides a stable or permanent link, prefer that over a temporary page URL.

### retrieved_at

Timestamp when the system collected the item.

This is not the same as the publication date.

### item_type

Classification of the collected item.

Suggested values:

```text
official_publication
official_guidance
official_draft
public_consultation
news_article
expert_commentary
rss_entry
document_reference
```

### source_authority_level

Authority inherited from the source registry.

Suggested values:

```text
official_binding
official_guidance
official_draft
trusted_warning
low_priority
```

### regulation_area

High-level regulatory area detected by the monitoring agent.

Suggested values:

```text
GDPR
AI_ACT
GDPR_AI_ACT_INTERPLAY
```

### topic_labels

Specific topic tags detected in the item.

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

## Optional Fields

### published_date

The date the source says the item was published.

Only fill this field when the date is clearly available.

### summary

Short factual summary of the item.

For the first MVP, this can be simple and deterministic. LLM-generated summaries can be added later.

### raw_text

Extracted text from the item.

This may be stored directly in early development, but in production it may be preferable to store only cleaned text, a hash, or a reference to object storage.

### raw_text_hash

Hash of the raw or cleaned text.

Used for duplicate detection.

### normalized_title

Lowercased and cleaned version of the title.

Used for grouping and deduplication.

### detected_dates

Important dates extracted from the item.

Examples:

```text
publication_date
entry_into_force_date
application_date
compliance_deadline
consultation_deadline
```

### detected_legal_references

Legal references found in the item.

Examples:

```text
Regulation (EU) 2024/1689
Regulation (EU) 2016/679
Article 50 AI Act
Article 35 GDPR
Article 33 GDPR
```

### detected_institutions

Institutions mentioned in the item.

Examples:

```text
European Commission
European AI Office
EDPB
EUR-Lex
Official Journal
```

### collection_status

Status of the collection process.

Suggested values:

```text
new
already_seen
failed_fetch
needs_review
ignored_out_of_scope
```

## Example JSON

```json
{
  "source_id": 9,
  "title": "A view from Brussels: upcoming guidelines on GDPR, AI Act interplay",
  "url": "https://iapp.org/news/example",
  "published_date": "2026-06-18",
  "retrieved_at": "2026-06-21T19:30:00",
  "item_type": "news_article",
  "source_authority_level": "trusted_warning",
  "regulation_area": "GDPR_AI_ACT_INTERPLAY",
  "topic_labels": [
    "AI_ACT_GENERAL",
    "GDPR_GENERAL"
  ],
  "summary": "A trusted privacy news source reports possible upcoming guidance on the interaction between GDPR and AI Act obligations.",
  "raw_text_hash": "example_hash",
  "normalized_title": "view brussels upcoming guidelines gdpr ai act interplay",
  "detected_dates": [],
  "detected_legal_references": [
    "GDPR",
    "AI Act"
  ],
  "detected_institutions": [],
  "collection_status": "new"
}
```

## MVP Boundary

The first version should focus on collecting reliable metadata.

It is better to store fewer fields correctly than many fields inconsistently.

Minimum viable fields:

- source;
- title;
- URL;
- retrieved date;
- item type;
- authority level;
- regulation area;
- topic labels;
- collection status.

