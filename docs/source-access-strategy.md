# Source Access Strategy

## Purpose

This document defines how the system should access each source in the MVP and how access can improve later.

The goal is to avoid blocking the project on complex integrations before the monitoring logic is proven.

## Access Methods

Suggested access method labels:

```text
manual_seed
webpage
rss
api
stable_link
download_reference
pending_access
```

## Strategy Principle

Start simple.

For the MVP, the system can begin with:

- curated URLs;
- stable legal links;
- official web pages;
- RSS feeds where available;
- manually collected official PDFs.

More advanced APIs can be added after the pipeline works.

## Source Access Table

| Source | Initial Access | Later Access | Priority | Notes |
|---|---|---|---:|---|
| EUR-Lex Official Journal | webpage | RSS / webservice | 1 | Primary official publication source. Use website and stable links first. |
| EUR-Lex ELI Stable Links | stable_link | stable_link | 1 | Best way to reference known legal acts. |
| EUR-Lex Webservice | pending_access | api | 1 | SOAP service, access pending administrator approval. Useful later for structured queries. |
| European Commission AI Office | webpage | webpage / RSS if available | 1 | Official source for AI Office and AI Act implementation updates. |
| European Commission AI Act Policy Page | webpage | webpage / RSS if available | 1 | Official AI Act policy and regulatory framework source. |
| European Commission Digital Strategy News | webpage | RSS if available | 2 | Useful for official announcements and policy updates. |
| EDPB Guidelines and Recommendations | webpage | webpage | 1 | Official GDPR guidance source. |
| EDPB News | webpage | RSS if available | 2 | Useful for recent GDPR-related updates and consultations. |
| IAPP News | webpage | newsletter / RSS if available | 3 | Trusted warning source, not official evidence. |
| IAPP AI Governance Resources | webpage | webpage | 3 | Useful for AI governance context and early warning. |
| Euractiv Tech | webpage | RSS | 3 | Trusted EU policy news warning source. |
| Future of Privacy Forum AI | webpage | webpage / newsletter | 4 | Expert context source, not official evidence. |
| European Law Blog AI | webpage | RSS if available | 4 | Expert legal commentary source. |

## MVP Access Plan

### Step 1: Manual Seed

Start with known official sources and documents already collected.

Purpose:

- validate database structure;
- test event grouping;
- test validation statuses;
- prepare dashboard examples.

### Step 2: Webpage Fetching

Fetch selected pages from curated sources.

Purpose:

- extract titles, dates, and links;
- detect new items;
- classify items by topic.

### Step 3: RSS Where Available

Use RSS feeds for sources that support them.

Purpose:

- simplify monitoring;
- avoid brittle scraping;
- detect updates more reliably.

### Step 4: EUR-Lex Webservice Later

Use the EUR-Lex webservice once access is approved and the team is ready for SOAP/XML integration.

Purpose:

- structured official queries;
- more robust official source monitoring.

This should not block the MVP.

## Source Priority

### Priority 1

Must support the MVP.

Sources:

- EUR-Lex / Official Journal;
- ELI stable links;
- European Commission AI Office;
- European Commission AI Act Policy;
- EDPB Guidelines.

### Priority 2

Important but not required for first prototype.

Sources:

- European Commission Digital Strategy News;
- EDPB News.

### Priority 3

Useful warning sources.

Sources:

- IAPP;
- Euractiv Tech.

### Priority 4

Context and expert commentary.

Sources:

- Future of Privacy Forum;
- European Law Blog.

## Fallback Strategy

If APIs are not available:

- use stable official links;
- use official web pages;
- use manually collected documents;
- use RSS where possible;
- store source metadata clearly.

If scraping is unreliable:

- reduce source list;
- monitor fewer pages;
- prefer RSS;
- use manual seed data for demo continuity.

## MVP Boundary

The first implementation should prove the monitoring pipeline, not perfect every data integration.

Success means:

- each source has a known access method;
- official sources are clearly separated from warning sources;
- the system can ingest at least a small curated set of source items;
- validation can be demonstrated even before full automation.

