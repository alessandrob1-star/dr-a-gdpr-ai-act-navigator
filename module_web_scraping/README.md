# Web Scraping and Source Monitoring Module

## Purpose

This module is responsible for collecting regulatory signals from official EU sources and selected trusted news sources.

Its goal is to support the platform in distinguishing between:

- early warning signals from news or expert commentary;
- official drafts, consultations, or guidance;
- officially published legal acts.

The module does not provide legal advice. It prepares structured, traceable regulatory intelligence for validation, scoring, and dashboard display.

## High-Level Flow

```text
Curated Sources
      |
      v
Source Monitoring Agent
      |
      v
Collected Source Items
      |
      v
Event Grouping and Deduplication
      |
      v
Validation Against Official Sources
      |
      v
Reliability and Urgency Scoring
      |
      v
Dashboard-Ready Regulatory Events
```

## Source Categories

### Official Binding Sources

Used to confirm whether a legal act has been officially published.

Examples:

- EUR-Lex Official Journal;
- EUR-Lex ELI stable legal links;
- EUR-Lex webservice, once access is approved.

Expected validation role:

```text
A_OFFICIALLY_PUBLISHED
```

### Official Guidance and Draft Sources

Used to identify official guidance, proposals, consultations, or draft implementation material.

Examples:

- European Commission AI Office;
- European Commission Digital Strategy pages;
- EDPB Guidelines and Recommendations.

Expected validation role:

```text
B_OFFICIAL_DRAFT
```

or official guidance supporting an already published legal act.

### Trusted Warning Sources

Used as early warning signals only.

Examples:

- IAPP News;
- Euractiv Tech;
- Future of Privacy Forum;
- European Law Blog.

Expected validation role:

```text
C_UNCONFIRMED_NEWS
```

These sources can trigger monitoring, but they cannot confirm that a rule is legally binding.

## Core Validation Statuses

```text
C_UNCONFIRMED_NEWS
```

The signal exists only in news or commentary.

```text
B_OFFICIAL_DRAFT
```

The signal is supported by an official draft, consultation, proposal, or guidance page.

```text
A_OFFICIALLY_PUBLISHED
```

The signal is confirmed by an official legal source such as EUR-Lex or the Official Journal.

## Deduplication Concept

The system should store every collected item but avoid showing duplicated alerts.

Multiple articles or official pages about the same topic should be grouped into one regulatory event.

Example:

```text
IAPP article
Euractiv article
European Commission draft
EUR-Lex publication
```

becomes:

```text
One regulatory event with multiple evidence sources.
```

## MVP Database Objects

Suggested core objects:

- `sources`
- `monitored_items`
- `regulatory_events`
- `event_sources`
- `validation_results`
- `reliability_score_history`

## MVP Goal

The first version should prove that the module can:

- monitor a curated set of sources;
- collect relevant AI Act and GDPR signals;
- separate warning sources from official sources;
- group duplicated signals into one event;
- assign a clear validation status;
- prepare clean data for dashboard display.

## Published Documentation

The module is currently documented through small, ordered planning files. This
keeps the work easy to review and allows each Jira item to map to a clear
deliverable before implementation starts.

1. [Source Ingestion Plan](01-source-ingestion.md)
2. [Validation and Event Grouping Plan](02-validation-and-grouping.md)
3. [Scoring and Dashboard Output Plan](03-scoring-and-dashboard-output.md)
4. [Implementation Roadmap](04-implementation-roadmap.md)
5. [Monitored Item Contract](05-monitored-item-contract.md)
6. [Source Access and EUR-Lex Webservice Notes](06-source-access-and-eurlex-webservice.md)
7. [Source Evidence Contract](07-source-evidence-contract.md)
8. [Regulatory Event Contract](08-regulatory-event-contract.md)
9. [Topic Detection Rules](09-topic-detection-rules.md)
10. [Dashboard Output Contract](10-dashboard-output-contract.md)
11. [Urgency and Deadline Logic](11-urgency-and-deadline-logic.md)
12. [Reliability Scoring Logic](12-reliability-scoring-logic.md)
13. [Scoring Model Summary](13-scoring-model-summary.md)
14. [Demo Flow Notes](14-demo-flow-notes.md)
15. [Fallback Plan](15-fallback-plan.md)
16. [End-to-End Demo Script](16-end-to-end-demo-script.md)

## Seed Data

The following CSV files are available as lightweight demo and configuration
inputs. They are not secrets and do not contain credentials.

- [Source Registry Seed](source_registry_seed.csv)
- [Demo Regulatory Events Seed](demo_regulatory_events_seed.csv)

## Containerized Package

The web scraping module can run as an independent Docker package. Build it from
the repository root:

```powershell
docker build -f module_web_scraping/Dockerfile -t ai-regulatory-web-scraping:local .
```

Run the default dashboard seed command:

```powershell
docker run --rm ai-regulatory-web-scraping:local
```

Run a specific CLI command:

```powershell
docker run --rm ai-regulatory-web-scraping:local sources --active
docker run --rm ai-regulatory-web-scraping:local monitor-static-dashboard
docker run --rm ai-regulatory-web-scraping:local eurlex-celex-envelope 32024R1689 --page-size 3
```

Run the module with Docker Compose:

```powershell
docker compose -f module_web_scraping/docker-compose.yml run --rm web-scraping sources --active
```

Run tests inside the container:

```powershell
docker run --rm --entrypoint python ai-regulatory-web-scraping:local -m unittest discover -s module_web_scraping/tests
```

The image copies the module, seed data, and local EUR-Lex configuration file.
Generated JSONL output can be written to `/app/storage` and mounted to the host
through the Compose volume.

## Future Extensions

Possible later improvements:

- EUR-Lex webservice integration;
- RSS-based monitoring;
- semantic similarity for event grouping;
- scheduled monitoring jobs;
- stored procedures for event compaction;
- LLM-assisted summaries;
- manual review workflow.
