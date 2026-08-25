# Source Monitoring Implementation Roadmap

> **Status:** original implementation plan retained for traceability. Current
> runtime behavior is documented in `docs_project/architecture.md` and
> `docs/CODE_WALKTHROUGH.md`.

## Purpose

This roadmap defines the implementation path for the Source Monitoring and Validation module.

The goal is to build the module gradually, starting from a simple, explainable MVP and leaving space for more advanced automation later.

## Guiding Principles

- Start with curated sources, not broad web scraping.
- Store raw monitoring results before applying complex reasoning.
- Separate news warnings from official evidence.
- Keep the LLM layer optional and replaceable.
- Prefer explainable rules first, then add semantic matching or machine learning later.
- Make every dashboard alert traceable back to source links.

## Phase 1: Data Foundation

Objective:

Create the basic data structure needed by the monitoring and validation agents.

Deliverables:

- database schema;
- source list table;
- official documents table;
- monitored items table;
- regulatory events table;
- validation results table.

Expected outcome:

The project can store sources, documents, collected items, and grouped regulatory events in a consistent format.

## Phase 2: Curated Source Registry

Objective:

Load the first official and trusted sources into the database.

Initial source categories:

- official binding sources;
- official guidance sources;
- official draft/proposal sources;
- trusted warning sources.

Initial priority sources:

- EUR-Lex Official Journal;
- EUR-Lex stable links / ELI;
- European Commission AI Office;
- European Commission Digital Strategy;
- EDPB guidelines and recommendations;
- IAPP News;
- Euractiv Tech.

Expected outcome:

The monitoring agent has a controlled set of sources to process.

## Phase 3: Basic Source Monitoring Agent

Objective:

Build the first deterministic version of the Source Monitoring Agent.

Initial behavior:

- read active sources from the database;
- fetch source content;
- extract title, URL, date, and text summary when available;
- filter items by GDPR and AI Act keywords;
- save new items to `monitored_items`;
- avoid duplicates using URL and text hash.

Expected outcome:

The system can collect structured monitoring records from a small number of sources.

## Phase 4: Event Grouping

Objective:

Group similar monitored items into one regulatory event.

Initial behavior:

- normalize titles;
- compare regulation area;
- compare keywords;
- compare dates within a short window;
- attach related items to an existing event when possible;
- create a new event when no match exists.

Expected outcome:

The dashboard can show one event supported by multiple sources instead of duplicated alerts.

## Phase 5: Validation Agent

Objective:

Classify each regulatory event according to the strength of official evidence.

Validation statuses:

- `C_UNCONFIRMED_NEWS`;
- `B_OFFICIAL_DRAFT`;
- `A_OFFICIALLY_PUBLISHED`.

Initial behavior:

- check whether the event is supported only by news;
- check whether an official draft or guidance exists;
- check whether a binding official publication exists;
- store validation evidence and explanation.

Expected outcome:

The system can clearly separate warning signals from official regulatory alerts.

## Phase 6: Reliability and Risk Scoring

Objective:

Add explainable scoring to validated regulatory events.

Initial score dimensions:

- reliability;
- urgency;
- regulatory impact;
- business impact;
- overall priority.

Expected outcome:

The dashboard can prioritize events and explain why an item is low, medium, high, or critical.

## Phase 7: Dashboard Integration

Objective:

Expose clean event data to the frontend.

Initial dashboard views:

- official alerts;
- official drafts;
- news warnings;
- priority list;
- source evidence panel;
- timeline of deadlines and application dates.

Expected outcome:

The frontend can display useful regulatory intelligence without needing to parse raw source data.

## Phase 8: Improvements After MVP

Possible later improvements:

- EUR-Lex webservice integration when access is approved;
- RSS-based monitoring;
- semantic similarity for event grouping;
- LLM-assisted summaries;
- scheduled monitoring jobs;
- PostgreSQL or SQL Server migration;
- stored procedures for compaction and scoring;
- manual review workflow;
- company-specific risk explanation.

## MVP Success Criteria

The module is successful if it can:

- monitor a small curated set of sources;
- collect relevant GDPR and AI Act items;
- group duplicated signals into one event;
- distinguish news from official sources;
- assign a transparent validation status;
- expose dashboard-ready regulatory events.

