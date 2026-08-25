# 04 - Implementation Roadmap

## Purpose

This document defines the implementation roadmap for the Web Scraping and Source Monitoring module.

The goal is to move from documentation to a simple working MVP without trying to automate everything at once.

## Guiding Principles

- Start with curated sources, not broad web scraping.
- Store source items before applying complex reasoning.
- Separate warning sources from official sources.
- Keep validation explainable.
- Use simple deterministic rules before semantic matching or LLM reasoning.
- Keep source links traceable for every dashboard event.

## Phase 1 - Source Registry

Objective:

Create the first structured source registry.

Deliverables:

- official source list;
- trusted warning source list;
- source categories;
- source priority;
- source access method.

Initial source categories:

- official binding sources;
- official guidance sources;
- official draft and consultation sources;
- trusted warning sources;
- expert context sources.

Expected outcome:

The module has a controlled list of sources to monitor.

## Phase 2 - Monitored Items

Objective:

Define and store the first source items collected from curated sources.

Deliverables:

- monitored item data structure;
- topic labels;
- collection status;
- basic duplicate checks by URL.

Expected outcome:

The system can store source records consistently before validation.

## Phase 3 - Topic Detection

Objective:

Classify collected items into AI Act and GDPR topics.

Initial topics:

- AI Act general updates;
- prohibited AI practices;
- high-risk AI systems;
- transparency obligations;
- general-purpose AI models;
- GDPR DPIA;
- GDPR data breach;
- GDPR international transfers;
- GDPR automated decision-making and profiling.

Expected outcome:

Collected items can be filtered and routed to the correct validation logic.

## Phase 4 - Event Grouping

Objective:

Group similar monitored items into one regulatory event.

Initial matching signals:

- same regulation area;
- shared topic labels;
- similar normalized title;
- shared legal references;
- close publication dates;
- same official institution.

Expected outcome:

The dashboard does not show duplicated alerts for the same regulatory development.

## Phase 5 - Validation

Objective:

Validate grouped events against official sources.

Validation statuses:

```text
C_UNCONFIRMED_NEWS
B_OFFICIAL_DRAFT
A_OFFICIALLY_PUBLISHED
```

Expected outcome:

The system clearly separates news warnings, official drafts, and official publications.

## Phase 6 - Scoring

Objective:

Assign explainable scores to validated regulatory events.

Score dimensions:

- reliability;
- urgency;
- regulatory impact;
- business impact;
- overall priority.

Expected outcome:

The dashboard can prioritize alerts and explain why they matter.

## Phase 7 - Dashboard Output

Objective:

Prepare clean regulatory event objects for the frontend.

Dashboard-ready fields:

- event title;
- regulation area;
- status;
- scores;
- official evidence;
- warning sources;
- key dates;
- recommended attention.

Expected outcome:

The frontend receives grouped, validated, traceable regulatory intelligence.

## Phase 8 - Automation Improvements

Possible improvements after the first MVP:

- RSS-based monitoring;
- EUR-Lex webservice integration;
- scheduled jobs;
- semantic similarity;
- LLM-assisted summaries;
- manual review workflow;
- SQL stored procedures for compaction;
- company-specific business impact scoring.

## MVP Success Criteria

The module is successful if it can:

- monitor a small curated source list;
- collect relevant AI Act and GDPR items;
- classify source items by topic;
- group duplicated signals into one event;
- validate events against official evidence;
- assign reliability and urgency scores;
- provide dashboard-ready output.

