# Database Schema Draft

> **Status:** future production design. The current local single-user MVP uses
> JSON snapshots and feed files; it does not claim that this database schema is
> deployed.

## Purpose

This document defines the first database model for the Source Monitoring and Validation module.

The goal is not to build the final production database immediately, but to clarify what the agents need to store, compare, validate, and expose to the dashboard.

For the MVP, the database should support four core needs:

- store official and non-official sources;
- store every collected item from those sources;
- group similar items into one regulatory event;
- track validation status, reliability, urgency, and evidence.

## Recommended MVP Database

For the first implementation, SQLite is enough.

It is simple, local, easy to version during development, and does not require server setup. The application should access it through an ORM layer such as SQLAlchemy, so the project can later move to PostgreSQL, SQL Server, or another relational database without rewriting the whole system.

Future options:

- SQLite for local MVP and demo;
- PostgreSQL for cloud deployment;
- SQL Server if the team wants to use a Microsoft-based stack later.

## Core Concept

The system should not create a separate dashboard alert for every article or document found online.

Instead:

- `monitored_items` stores each collected source item;
- `regulatory_events` stores the compacted event shown to the user;
- multiple items can support the same event.

Example:

Three news articles mention upcoming AI Act guidance. Later, the European Commission publishes an official page. The system should represent this as one regulatory event with several supporting sources, not as four unrelated alerts.

## Tables

### sources

Stores the sources monitored by the system.

Suggested fields:

- `id`
- `name`
- `url`
- `source_type`
- `authority_level`
- `topic_area`
- `access_method`
- `is_active`
- `notes`

Example `source_type` values:

- `official`
- `official_guidance`
- `official_journal`
- `trusted_news`
- `expert_blog`
- `vendor_content`

Example `authority_level` values:

- `official_binding`
- `official_guidance`
- `official_draft`
- `trusted_warning`
- `low_priority`

### official_documents

Stores official documents already collected for the knowledge base.

Suggested fields:

- `id`
- `title`
- `file_name`
- `source_url`
- `regulation_area`
- `document_type`
- `publication_date`
- `status`
- `priority`
- `description`

Example `regulation_area` values:

- `GDPR`
- `AI_ACT`
- `AI_ACT_GPAI`
- `AI_ACT_HIGH_RISK`
- `AI_ACT_TRANSPARENCY`
- `GDPR_DATA_BREACH`
- `GDPR_INTERNATIONAL_TRANSFERS`

### monitored_items

Stores each item collected from monitoring sources.

This can be a news article, an official page, an RSS entry, an Official Journal item, a draft guidance page, or a newly discovered PDF.

Suggested fields:

- `id`
- `source_id`
- `title`
- `url`
- `published_date`
- `retrieved_at`
- `item_type`
- `regulation_area`
- `summary`
- `raw_text_hash`
- `normalized_title`
- `event_id`
- `collection_status`

Example `item_type` values:

- `official_publication`
- `official_guidance`
- `official_draft`
- `news_article`
- `expert_commentary`
- `rss_entry`

### regulatory_events

Stores the compacted event that the dashboard should display.

Suggested fields:

- `id`
- `event_title`
- `regulation_area`
- `event_status`
- `first_detected_at`
- `last_updated_at`
- `effective_date`
- `compliance_deadline`
- `summary`
- `reliability_score`
- `urgency_score`
- `impact_score`
- `overall_priority`

Example `event_status` values:

- `C_UNCONFIRMED_NEWS`
- `B_OFFICIAL_DRAFT`
- `A_OFFICIALLY_PUBLISHED`
- `ARCHIVED`

Example `overall_priority` values:

- `low`
- `medium`
- `high`
- `critical`

### validation_results

Stores the validation evidence produced by the validation agent.

Suggested fields:

- `id`
- `event_id`
- `validated_at`
- `validation_status`
- `official_evidence_url`
- `official_evidence_title`
- `official_publication_date`
- `confidence_score`
- `reasoning_summary`

This table should explain why an item is considered only a warning, an official draft, or an official publication.

### event_sources

Links monitored items to regulatory events.

Suggested fields:

- `id`
- `event_id`
- `monitored_item_id`
- `relationship_type`
- `created_at`

Example `relationship_type` values:

- `initial_signal`
- `supporting_news`
- `official_confirmation`
- `related_guidance`

### reliability_score_history

Tracks how the reliability of an event changes over time.

Suggested fields:

- `id`
- `event_id`
- `scored_at`
- `previous_score`
- `new_score`
- `reason`

Example:

A news article creates an event with reliability 35/100. An official draft later raises it to 70/100. Publication in the Official Journal raises it to 95/100.

## Deduplication Strategy

The MVP should start with simple deduplication rules before introducing machine learning or semantic similarity.

Initial rules:

- normalize titles by lowercasing and removing punctuation;
- compare regulation area;
- compare publication dates within a short time window;
- compare repeated keywords such as "AI Act", "GDPR", "high-risk AI", "data breach", "GPAI", "transparency";
- link similar monitored items to an existing regulatory event when the match is strong enough.

Later improvements:

- embedding similarity between article summaries;
- clustering similar articles;
- stored procedures or scheduled database jobs for periodic compaction;
- manual review flags for uncertain matches.

## Stored Procedures and Database Jobs

Stored procedures are useful later, especially for compacting duplicate or similar records.

For the MVP, this logic can live in the application layer because SQLite does not support stored procedures in the same way as SQL Server or PostgreSQL.

Future stored procedure candidates:

- merge duplicate monitored items;
- recalculate event reliability scores;
- recalculate urgency based on approaching deadlines;
- archive old low-confidence warnings;
- generate dashboard-ready priority lists.

## MVP Implementation Path

Recommended order:

1. Create the database schema.
2. Insert the curated source list.
3. Insert the official documents already collected.
4. Build a simple source monitoring agent that saves monitored items.
5. Build the validation logic that updates regulatory events.
6. Add scoring after the event model is stable.

This keeps the project modular and shows a professional progression: data model first, agent behavior second, scoring and dashboard output third.

