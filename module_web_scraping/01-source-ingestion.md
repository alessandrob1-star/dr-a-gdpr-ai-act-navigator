# 01 - Source Ingestion

## Purpose

This document defines the first ingestion layer for the Web Scraping and Source Monitoring module.

The goal is to collect structured regulatory signals from a curated set of official and trusted sources, without relying on broad or uncontrolled web scraping.

## MVP Principle

The MVP should start with a small, controlled source registry.

This keeps the system:

- easier to test;
- easier to explain;
- less fragile;
- more transparent for validation.

The first version should prove that the platform can collect reliable source items before adding more advanced automation.

## Source Categories

### Official Binding Sources

These sources can confirm that a legal act has been officially published.

Examples:

- EUR-Lex Official Journal;
- EUR-Lex ELI stable legal links;
- EUR-Lex webservice, once access is approved.

Validation role:

```text
A_OFFICIALLY_PUBLISHED
```

### Official Guidance and Draft Sources

These sources provide official guidance, policy pages, proposals, consultations, or draft implementation material.

Examples:

- European Commission AI Office;
- European Commission Digital Strategy pages;
- EDPB Guidelines and Recommendations.

Validation role:

```text
B_OFFICIAL_DRAFT
```

or official guidance supporting an already published legal obligation.

### Trusted Warning Sources

These sources are useful for early signals but cannot confirm legal status.

Examples:

- IAPP News;
- Euractiv Tech;
- Future of Privacy Forum;
- European Law Blog.

Validation role:

```text
C_UNCONFIRMED_NEWS
```

## Initial Source Registry

| Source | Category | Priority | MVP Access |
|---|---|---:|---|
| EUR-Lex Official Journal | Official binding | 1 | Webpage / stable links |
| EUR-Lex ELI Stable Links | Official binding | 1 | Stable links |
| EUR-Lex Webservice | Official binding | 1 | Pending access |
| European Commission AI Office | Official guidance | 1 | Webpage |
| European Commission AI Act Policy Page | Official guidance | 1 | Webpage |
| EDPB Guidelines and Recommendations | Official guidance | 1 | Webpage |
| European Commission Digital Strategy News | Official news | 2 | Webpage / RSS later |
| EDPB News | Official news | 2 | Webpage / RSS later |
| IAPP News | Trusted warning | 3 | Webpage / newsletter |
| Euractiv Tech | Trusted warning | 3 | Webpage / RSS |
| Future of Privacy Forum AI | Expert context | 4 | Webpage |
| European Law Blog AI | Expert context | 4 | Webpage / RSS later |

## Access Strategy

The first implementation should not be blocked by complex APIs.

Recommended order:

1. Start from manually curated official URLs and documents.
2. Fetch selected official web pages.
3. Use stable legal links where available.
4. Add RSS feeds when available.
5. Add EUR-Lex webservice integration after access is approved and the rest of the pipeline works.

EUR-Lex webservice remains important, but it should not block the MVP.

## Monitored Item

A monitored item is a single record collected from a source before deduplication, validation, scoring, or dashboard grouping.

Examples:

- one news article;
- one official Commission page;
- one EDPB guideline page;
- one EUR-Lex item;
- one RSS entry;
- one official document reference.

## Minimum Data Fields

Each collected item should include:

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

Suggested `item_type` values:

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

Suggested `collection_status` values:

```text
new
already_seen
failed_fetch
needs_review
ignored_out_of_scope
```

## Topic Detection

The ingestion layer should apply simple rule-based topic detection.

Initial topics:

- AI Act general updates;
- prohibited AI practices;
- high-risk AI systems;
- transparency obligations;
- general-purpose AI models;
- GDPR general updates;
- DPIA;
- data breach;
- international transfers;
- automated decision-making and profiling;
- controller and processor obligations;
- data subject rights.

The first version should prefer explainable keyword matching. Semantic matching or LLM-assisted classification can be added later.

## Output of the Ingestion Layer

The ingestion layer should produce structured `monitored_items`.

These items will then be used by:

- event grouping and deduplication;
- validation against official sources;
- reliability scoring;
- dashboard output.

## MVP Success Criteria

The ingestion layer is successful if it can:

- monitor a small curated set of sources;
- collect relevant AI Act and GDPR items;
- separate official sources from warning sources;
- store clean metadata;
- provide traceable source links for later validation.

