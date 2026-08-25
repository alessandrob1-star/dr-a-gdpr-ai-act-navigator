# 16 - End-to-End Demo Script

## Purpose

This document defines a practical end-to-end demo script for presenting the Web Scraping and Source Monitoring module.

The script is designed to explain the module clearly to a jury or technical reviewer, even if some integrations are still in progress.

## Demo Goal

Show that the platform can:

- monitor curated regulatory sources;
- separate news warnings from official evidence;
- group related source items into one regulatory event;
- validate events against official sources;
- score reliability and urgency;
- prepare clean dashboard-ready output.

## Opening Message

Suggested wording:

```text
This module is designed to help companies monitor AI Act and GDPR updates from official EU sources and selected trusted warning sources.

The key idea is that the platform does not treat every news article as law. It validates signals against official sources, groups duplicated information into one regulatory event, and assigns explainable scores before showing the result in the dashboard.
```

## Step 1 - Show Source Registry

Show:

```text
module_web_scraping/source_registry_seed.csv
```

Explain:

```text
We start from a curated source registry instead of broad uncontrolled scraping.
Sources are classified by authority level: official binding, official guidance, official draft, trusted warning, or expert context.
```

Highlight:

- EUR-Lex;
- European Commission AI Office;
- EDPB;
- IAPP;
- Euractiv.

## Step 2 - Explain Source Ingestion

Show:

```text
module_web_scraping/01-source-ingestion.md
module_web_scraping/05-monitored-item-contract.md
```

Explain:

```text
Each collected page or article becomes a monitored item with structured fields such as source, title, URL, authority level, item type, regulation area, topic labels, and collection status.
```

## Step 3 - Explain Topic Detection

Show:

```text
module_web_scraping/09-topic-detection-rules.md
```

Explain:

```text
The first MVP uses deterministic topic detection rules. This keeps the system explainable and helps route each source item to AI Act, GDPR, or GDPR/AI Act interplay topics.
```

Example topics:

- high-risk AI;
- prohibited AI practices;
- transparency obligations;
- GPAI;
- DPIA;
- data breach;
- international transfers.

## Step 4 - Show Event Grouping

Show:

```text
module_web_scraping/02-validation-and-grouping.md
module_web_scraping/08-regulatory-event-contract.md
```

Explain:

```text
Multiple source items can discuss the same regulatory development. Instead of showing duplicated alerts, the platform groups them into one regulatory event with multiple evidence sources.
```

Example:

```text
IAPP article + Euractiv article + Commission draft + EUR-Lex publication
= one regulatory event
```

## Step 5 - Show Validation Status

Explain the three validation levels:

```text
C_UNCONFIRMED_NEWS -> Warning
B_OFFICIAL_DRAFT -> Official Draft / Upcoming
A_OFFICIALLY_PUBLISHED -> Official Alert
```

Suggested wording:

```text
This is one of the most important parts of the project. A news article can create a warning, but only official evidence can move the event to official draft or official alert.
```

## Step 6 - Show EUR-Lex Official Source Strategy

Show:

```text
module_web_scraping/06-source-access-and-eurlex-webservice.md
```

Explain:

```text
EUR-Lex webservice access has been approved. The service uses SOAP and can support structured official queries. For the MVP, this is used as an official validation source, while stable links and official documents remain available as fallback.
```

Do not show credentials during the demo.

## Step 7 - Show Evidence Contract

Show:

```text
module_web_scraping/07-source-evidence-contract.md
```

Explain:

```text
Every event keeps evidence records. The dashboard can show official evidence separately from warning sources, so users understand why a status was assigned.
```

## Step 8 - Show Scoring

Show:

```text
module_web_scraping/11-urgency-and-deadline-logic.md
module_web_scraping/12-reliability-scoring-logic.md
module_web_scraping/13-scoring-model-summary.md
```

Explain:

```text
Reliability measures how official and well-supported an event is.
Urgency measures how soon it may require attention.
Regulatory impact measures how serious the topic is.
Business impact will later use the company profile module.
```

Key phrase:

```text
Reliability is not the same as business risk.
```

## Step 9 - Show Demo Events

Show:

```text
module_web_scraping/demo_regulatory_events_seed.csv
```

Explain:

```text
The seed data allows us to demonstrate the full flow before every live integration is complete. It follows the same structure expected from the automated pipeline.
```

Example events:

- AI Act official publication;
- prohibited practices guidance;
- high-risk AI draft guidance;
- GDPR data breach guidance;
- GDPR DPIA guidance;
- GDPR/AI Act interplay warning.

## Step 10 - Show Dashboard Output

Show:

```text
module_web_scraping/10-dashboard-output-contract.md
```

Explain:

```text
The dashboard receives grouped, validated, scored events. It can display official alerts, official drafts, news warnings, timeline dates, and evidence links.
```

## Step 11 - Explain Fallback Plan

Show:

```text
module_web_scraping/15-fallback-plan.md
```

Explain:

```text
The demo does not depend entirely on live external systems. If APIs or scraping are unavailable, the same data contracts can be demonstrated using prepared seed data and official documents.
```

## Closing Message

Suggested wording:

```text
The MVP proves the intelligence flow: collect regulatory signals, classify them, group duplicates, validate against official sources, score reliability and urgency, and prepare dashboard-ready events.

The architecture remains modular, so each part can be improved independently: source monitoring, validation, scoring, dashboard integration, and company-specific impact from the Company Profile module.
```

## Demo Checklist

Before presenting:

- confirm source registry is visible;
- confirm demo regulatory events are available;
- avoid showing credentials;
- show warning vs official draft vs official alert;
- show reliability and urgency separately;
- show deadline/timeline logic;
- show fallback plan if live integration is not ready.

