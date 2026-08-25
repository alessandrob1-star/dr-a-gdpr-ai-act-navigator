# 14 - Demo Flow Notes

## Purpose

This document defines a stable demo flow for the Web Scraping and Source Monitoring module.

The goal is to show the project clearly to the jury even if some integrations are still incomplete.

## Demo Principle

The demo should focus on the value of the system, not on the completeness of every technical integration.

The core story is:

```text
The platform separates early warning signals from official regulatory evidence, groups duplicated sources into one event, scores the event, and prepares it for dashboard display.
```

## Demo Inputs

The demo can use:

- curated source registry;
- demo regulatory events seed;
- official AI Act and GDPR documents;
- EUR-Lex webservice access notes;
- source evidence examples;
- scoring and dashboard output contracts.

This allows a stable walkthrough even before full scheduled automation is implemented.

## Suggested Demo Scenario

### Step 1 - Show Curated Sources

Explain that the system monitors selected source categories:

- official binding sources;
- official guidance and draft sources;
- trusted warning sources;
- expert context sources.

Example sources:

- EUR-Lex;
- European Commission AI Office;
- EDPB;
- IAPP;
- Euractiv.

### Step 2 - Show Source Ingestion

Show that the system collects structured source items rather than uncontrolled web pages.

Example monitored item fields:

- source;
- title;
- URL;
- authority level;
- item type;
- regulation area;
- topic labels;
- collection status.

### Step 3 - Show Warning Signal

Use an example event based only on trusted news.

Expected status:

```text
C_UNCONFIRMED_NEWS
```

Dashboard label:

```text
Warning
```

Message:

```text
This is useful as an early signal, but it is not treated as official law.
```

### Step 4 - Show Official Draft

Show the same or similar regulatory topic supported by an official Commission or EDPB draft.

Expected status:

```text
B_OFFICIAL_DRAFT
```

Dashboard label:

```text
Official Draft / Upcoming
```

Message:

```text
The event is now supported by official evidence, but may not be binding yet.
```

### Step 5 - Show Official Publication

Show an event confirmed by EUR-Lex or the Official Journal.

Expected status:

```text
A_OFFICIALLY_PUBLISHED
```

Dashboard label:

```text
Official Alert
```

Message:

```text
This can be treated as official regulatory evidence.
```

### Step 6 - Show Scoring

Explain the separate score dimensions:

- reliability;
- urgency;
- regulatory impact;
- business impact;
- overall priority.

Important message:

```text
Reliability is not the same as business risk.
```

### Step 7 - Show Timeline and Deadlines

Show how official dates affect urgency.

Important date types:

- publication date;
- entry into force;
- application date;
- compliance deadline;
- consultation deadline.

Message:

```text
Only validated official dates should drive high urgency and hard deadlines.
```

### Step 8 - Show Evidence Panel

Show that each dashboard event is traceable.

Evidence groups:

- official evidence;
- warning sources;
- background context.

Message:

```text
The user can see why the system assigned a status and score.
```

## Fallback Plan

If live scraping or API calls are not ready during the presentation, use seed data.

Fallback data:

- `source_registry_seed.csv`;
- `demo_regulatory_events_seed.csv`;
- official documents already stored in the repository;
- manually prepared evidence examples.

This keeps the demo stable and avoids depending on network conditions or external APIs.

## Demo Success Criteria

The demo is successful if the jury understands that the module can:

- monitor curated official and trusted sources;
- collect structured regulatory signals;
- avoid treating news as law;
- validate signals against official evidence;
- group duplicated sources into one event;
- score reliability and urgency;
- prepare clean dashboard output;
- remain useful even with partial automation.

