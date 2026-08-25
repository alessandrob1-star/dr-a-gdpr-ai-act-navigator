# Source Monitoring Module Architecture

> **Status:** data-pipeline design contract. Named stages such as validation and
> scoring describe deterministic processing components; the current runtime
> agent boundary is documented in `docs_project/agents.md`.

## Purpose

This document summarizes the architecture of the Source Monitoring and Validation module.

The module turns official sources and trusted news into validated, grouped, scored regulatory events that can be displayed in the dashboard.

## Architecture Flow

```text
Curated Sources
      |
      v
Source Monitoring Agent
      |
      v
Monitored Items Database
      |
      v
Event Grouping and Deduplication
      |
      v
Regulatory Events
      |
      v
Validation Agent
      |
      v
Reliability and Risk Scoring
      |
      v
Dashboard Output
```

## Component Responsibilities

### Curated Sources

Stores the official and trusted sources monitored by the system.

Examples:

- EUR-Lex Official Journal;
- EUR-Lex ELI stable links;
- European Commission AI Office;
- EDPB Guidelines;
- IAPP News;
- Euractiv Tech.

Purpose:

- avoid random broad scraping;
- keep source quality controlled;
- make monitoring explainable.

### Source Monitoring Agent

Collects items from configured sources.

Responsibilities:

- fetch source content;
- extract title, URL, date, and summary;
- classify the source type;
- filter by GDPR and AI Act relevance;
- save structured items to the database.

Output:

```text
monitored_items
```

### Monitored Items Database

Stores every collected source item.

This layer preserves traceability.

Examples:

- news article;
- official draft page;
- EDPB guideline;
- Official Journal publication;
- RSS entry.

### Event Grouping and Deduplication

Groups related monitored items into one regulatory event.

Responsibilities:

- detect exact duplicates;
- compare titles, topics, dates, legal references, and sources;
- link related items to an existing event;
- create a new event when no match exists.

Output:

```text
regulatory_events
event_sources
```

### Regulatory Events

Represents the dashboard-ready regulatory development.

One event can be supported by multiple monitored items.

Example:

```text
Draft high-risk AI classification guidance
```

Supported by:

- trusted news article;
- European Commission draft;
- later official publication.

### Validation Agent

Checks whether a regulatory event is supported by official evidence.

Validation statuses:

```text
C_UNCONFIRMED_NEWS
B_OFFICIAL_DRAFT
A_OFFICIALLY_PUBLISHED
```

Purpose:

- separate warnings from official alerts;
- prevent news from being treated as law;
- keep a clear evidence trail.

### Reliability and Risk Scoring

Assigns explainable scores.

Score dimensions:

- reliability;
- urgency;
- regulatory impact;
- business impact;
- overall priority.

Reliability is based on source authority.

Risk and priority depend on urgency, legal impact, and later company profile relevance.

### Dashboard Output

Provides clean data to the frontend.

Dashboard sections supported:

- official alerts;
- official drafts;
- news warnings;
- priority list;
- source evidence;
- compliance timeline.

## MVP Data Flow Example

1. IAPP publishes a news article about upcoming AI Act guidance.
2. The Source Monitoring Agent saves it as a monitored item.
3. Grouping creates a new regulatory event.
4. Validation classifies it as `C_UNCONFIRMED_NEWS`.
5. The dashboard shows it as a warning.
6. Later, the European Commission publishes a draft.
7. The event is updated to `B_OFFICIAL_DRAFT`.
8. Reliability increases.
9. If the final act appears in EUR-Lex, the event becomes `A_OFFICIALLY_PUBLISHED`.

## MVP Boundaries

The MVP should not attempt to solve every compliance problem.

It should prove that the system can:

- monitor selected sources;
- capture relevant regulatory signals;
- group duplicated items;
- validate signals against official sources;
- assign transparent status and scores;
- produce dashboard-ready outputs.

## Future Extensions

Possible later improvements:

- EUR-Lex webservice integration;
- RSS automation;
- semantic similarity;
- scheduled monitoring;
- manual review workflow;
- company-specific scoring;
- LLM-generated summaries;
- SQL stored procedures for compaction;
- PostgreSQL or SQL Server migration.

