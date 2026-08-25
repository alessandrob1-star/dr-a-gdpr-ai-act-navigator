# Source Monitoring Agent Specification

> **Implementation note:** source collection and normalization are deterministic
> services in `module_web_scraping/`. Their runtime boundary is the
> `RegulatoryMonitoringAgent` in `module_agents/regulatory_monitoring_agent.py`.

## Purpose

The Source Monitoring Agent is responsible for collecting regulatory signals from official sources and trusted warning sources.

Its role is not to decide final compliance risk by itself. Instead, it creates structured records that can later be validated, grouped, scored, and displayed in the dashboard.

## MVP Scope

The first version should focus on a small number of high-value sources:

- EUR-Lex and Official Journal for binding EU legal publications;
- European Commission AI Office and Digital Strategy pages for AI Act guidance and updates;
- EDPB pages for GDPR guidance and recommendations;
- selected trusted news or expert sources such as IAPP and Euractiv for early warning signals.

The MVP should avoid broad web scraping across random websites. It should monitor a curated source list first.

## Input

The agent receives one source configuration from the database.

Expected source fields:

- `name`
- `url`
- `source_type`
- `authority_level`
- `topic_area`
- `access_method`
- `is_active`
- `notes`

Example:

```text
name: EUR-Lex Official Journal
url: https://eur-lex.europa.eu/oj/direct-access.html
source_type: official_journal
authority_level: official_binding
topic_area: EU law
access_method: webpage / RSS / API later
```

## Output

For each relevant item found, the agent creates a `monitored_items` record.

Expected extracted fields:

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
- `collection_status`

## Source Categories

### Official Binding Sources

These are the strongest sources.

Examples:

- EUR-Lex Official Journal;
- EUR-Lex ELI stable links;
- EUR-Lex webservice when access is approved.

Expected item status:

- `official_publication`

Typical validation effect:

- can confirm a regulatory event as `A_OFFICIALLY_PUBLISHED`;
- should strongly increase reliability.

### Official Guidance Sources

These sources clarify how laws should be interpreted or applied.

Examples:

- European AI Office;
- European Commission Digital Strategy pages;
- EDPB Guidelines and Recommendations.

Expected item status:

- `official_guidance`
- `official_draft`

Typical validation effect:

- can confirm that an update is official;
- can classify a regulatory event as `B_OFFICIAL_DRAFT` or strengthen an already published event.

### Trusted Warning Sources

These are useful for early signals but should not be treated as law.

Examples:

- IAPP News;
- Euractiv Tech;
- Future of Privacy Forum;
- European Law Blog.

Expected item status:

- `news_article`
- `expert_commentary`

Typical validation effect:

- creates or supports `C_UNCONFIRMED_NEWS`;
- must be checked against official sources before becoming an official alert.

## Basic Workflow

1. Load active sources from the database.
2. Fetch the source content using the configured access method.
3. Extract candidate items.
4. Filter items by project scope:
   - GDPR;
   - EU AI Act;
   - AI Act high-risk systems;
   - AI Act prohibited practices;
   - AI Act transparency obligations;
   - General-purpose AI models;
   - GDPR data breach;
   - GDPR DPIA;
   - GDPR international transfers.
5. Normalize title and text.
6. Check if the item already exists using URL and content hash.
7. Save new items to `monitored_items`.
8. Send new items to the Validation Agent.

## Filtering Rules

The MVP should keep filtering simple.

An item is relevant if it contains one or more core terms:

- `AI Act`
- `Artificial Intelligence Act`
- `Regulation (EU) 2024/1689`
- `high-risk AI`
- `prohibited AI practices`
- `transparency obligations`
- `general-purpose AI`
- `GPAI`
- `GDPR`
- `Regulation (EU) 2016/679`
- `data breach`
- `DPIA`
- `legitimate interest`
- `international transfers`
- `processor`
- `controller`
- `data subject rights`

The first version should prefer false positives over missing important items. Irrelevant items can be filtered later.

## Collection Status

Suggested `collection_status` values:

- `new`
- `already_seen`
- `failed_fetch`
- `needs_review`
- `ignored_out_of_scope`

## MVP Design Choice

The agent should be deterministic first.

This means the first version should rely on:

- source configuration;
- structured parsing where possible;
- keyword filtering;
- URL and hash deduplication;
- short summaries generated only after the item is stored.

LLM reasoning can be added later for classification and summarization, but the source monitoring layer should remain explainable and easy to debug.

## Handoff to Validation Agent

After saving a new monitored item, the Source Monitoring Agent should pass the item to the Validation Agent.

The Validation Agent will decide whether the item:

- creates a new regulatory event;
- supports an existing event;
- confirms an event through an official source;
- should remain only a low-confidence warning.

## Example Scenario

A trusted news source publishes:

```text
New AI Act high-risk guidance expected next month
```

The Source Monitoring Agent stores it as:

```text
item_type: news_article
regulation_area: AI_ACT_HIGH_RISK
collection_status: new
```

The Validation Agent then checks official sources.

If no official source exists yet:

```text
event_status: C_UNCONFIRMED_NEWS
```

If a Commission draft page exists:

```text
event_status: B_OFFICIAL_DRAFT
```

If the document is published in EUR-Lex or the Official Journal:

```text
event_status: A_OFFICIALLY_PUBLISHED
```

## Next Step

After this specification, the next design document should define the Validation Agent in the same style:

- validation statuses;
- evidence rules;
- reliability scoring;
- relationship with official sources;
- dashboard-ready output.

