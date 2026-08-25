# 05 - Monitored Item Contract

## Purpose

This document defines the structure of a monitored item.

A monitored item is a single source record collected by the Source Monitoring Agent before grouping, validation, scoring, or dashboard display.

Examples:

- one news article;
- one official Commission page;
- one EDPB guideline page;
- one EUR-Lex item;
- one RSS entry;
- one official document reference.

## Core Principle

The module should store structured source records before applying reasoning.

This keeps the pipeline traceable:

```text
source -> monitored item -> regulatory event -> validation -> scoring -> dashboard
```

## Minimum Fields

Each monitored item should include:

- `source_name`
- `source_url`
- `source_type`
- `authority_level`
- `title`
- `url`
- `published_date`
- `retrieved_at`
- `item_type`
- `regulation_area`
- `topic_labels`
- `summary`
- `collection_status`

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

The authority level is important because it affects validation and reliability scoring.

## Item Type

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

Each monitored item can have more than one topic label.

## Collection Status

Suggested values:

```text
new
already_seen
failed_fetch
needs_review
ignored_out_of_scope
```

## Date Fields

The ingestion layer should distinguish between:

- `published_date`: date stated by the source;
- `retrieved_at`: date and time when the system collected the item.

Later validation may extract additional dates such as:

- entry into force date;
- application date;
- compliance deadline;
- consultation deadline.

Only dates from official sources should drive high urgency scoring.

## Duplicate Support Fields

The MVP should support basic duplicate detection with:

- canonical URL;
- normalized title;
- raw or cleaned text hash.

This allows the system to avoid storing exact duplicates and supports later event grouping.

## Example

```json
{
  "source_name": "IAPP News",
  "source_url": "https://iapp.org/news/",
  "source_type": "trusted_news",
  "authority_level": "trusted_warning",
  "title": "A view from Brussels: upcoming guidelines on GDPR, AI Act interplay",
  "url": "https://iapp.org/news/example",
  "published_date": "2026-06-18",
  "retrieved_at": "2026-06-22T10:30:00",
  "item_type": "news_article",
  "regulation_area": "GDPR_AI_ACT_INTERPLAY",
  "topic_labels": [
    "AI_ACT_GENERAL",
    "GDPR_GENERAL"
  ],
  "summary": "A trusted privacy news source reports possible upcoming guidance on the interaction between GDPR and AI Act obligations.",
  "collection_status": "new"
}
```

## MVP Success Criteria

The monitored item contract is successful if it allows the system to:

- store collected source records consistently;
- distinguish official and non-official sources;
- classify items by regulatory area and topic;
- support duplicate detection;
- provide traceable input for validation and scoring.

