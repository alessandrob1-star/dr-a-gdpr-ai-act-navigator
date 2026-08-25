# 15 - Fallback Plan

## Purpose

This document defines the fallback plan for the Web Scraping and Source Monitoring module.

The goal is to ensure that the project demo remains stable even if external integrations, APIs, or live scraping are incomplete or unavailable during presentation.

## Core Principle

The demo should not depend entirely on live external systems.

The platform should be able to demonstrate its value using prepared seed data and documented source evidence.

## Main Risks

### EUR-Lex Webservice Issues

Possible problems:

- authentication fails;
- SOAP request format needs more work;
- service is temporarily unavailable;
- query syntax needs refinement;
- rate limit or access issue occurs during demo.

Fallback:

- use known EUR-Lex stable links;
- use already collected official documents;
- use manually prepared official evidence examples;
- show the webservice integration plan and approved access notes.

### Web Scraping Issues

Possible problems:

- page structure changes;
- source blocks automated requests;
- network connection fails;
- source content is inconsistent;
- parsing extracts incomplete data.

Fallback:

- use the curated source registry seed;
- use manually collected source items;
- use demo regulatory events seed;
- avoid live scraping during the main presentation.

### News Source Issues

Possible problems:

- article pages change;
- paywall or login appears;
- source removes old content;
- RSS feed is unavailable.

Fallback:

- use stored warning examples;
- use source metadata only;
- keep warning events clearly marked as non-official.

### Company Profile Module Delay

Possible problems:

- company questionnaire is incomplete;
- company memory is not fully implemented;
- business impact score cannot be calculated dynamically.

Fallback:

- use sample company profiles;
- keep `business_impact_score` as a prepared demo value;
- explain that the scoring interface is ready for Company Profile integration.

### Dashboard Integration Delay

Possible problems:

- frontend is incomplete;
- API endpoint is not ready;
- data contract integration is delayed.

Fallback:

- show dashboard-ready JSON/CSV data;
- show grouped regulatory events in a table;
- explain the frontend contract and visual flow.

## Prepared Fallback Assets

The module should maintain:

- `source_registry_seed.csv`;
- `demo_regulatory_events_seed.csv`;
- official AI Act and GDPR documents;
- source evidence examples;
- scoring model documents;
- dashboard output contract.

These assets allow a stable walkthrough without depending on live network calls.

## Fallback Demo Flow

If live integration is not ready, use this flow:

1. Show curated sources.
2. Show source registry seed.
3. Show demo regulatory events seed.
4. Explain event statuses:
   - warning;
   - official draft;
   - official alert.
5. Show reliability and urgency scoring.
6. Show timeline/deadline logic.
7. Show dashboard-ready event structure.
8. Explain where live automation will connect.

## Communication During Demo

Recommended wording:

```text
The MVP is designed to work with live official sources, but the demo also includes seed data to keep the presentation stable and reproducible.
```

and:

```text
The fallback data follows the same structure expected from the automated monitoring pipeline, so it is not a separate demo-only shortcut.
```

## MVP Success Criteria

The fallback plan is successful if:

- the demo can run without live external APIs;
- the data structure remains the same as the real pipeline;
- official and non-official sources remain clearly separated;
- scoring and dashboard output can still be demonstrated;
- the jury can understand the full product value even with partial automation.

