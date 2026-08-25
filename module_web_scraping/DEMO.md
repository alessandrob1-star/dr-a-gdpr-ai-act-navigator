# Web Scraping Docker Demo

This demo shows the first dockerized version of the regulatory monitoring
module. It is intentionally small, deterministic, and easy to run during a
project review.

## Prerequisites

- Docker Desktop installed
- Docker Desktop running before commands are executed
- PowerShell opened from the repository root

Open PowerShell in the folder where the repository was cloned:

```powershell
cd "path\to\AI-Act-Compliance-Navigator"
```

Quick Docker check:

```powershell
docker ps
```

An empty container table is fine.

## Run The Full Demo

From the repository root:

```powershell
.\module_web_scraping\run_demo.ps1
```

The script builds the package images and runs each service one at a time so the
output remains readable. It also generates:

- `storage/demo_report.md`
- `storage/demo_report.json`
- `storage/web_scraping_outputs/run_summary.md`
- `storage/web_scraping_outputs/regulatory_events.json`
- `storage/web_scraping_outputs/scraped_monitored_items.json`
- `storage/web_scraping_outputs/articles_and_news_feed.html`

## Run Everything With Compose

This runs all services together:

```powershell
docker compose -f module_web_scraping\packages\docker-compose.yml up --build
```

The output is more crowded because all containers write logs at the same time.

## Run Individual Services

Source monitoring:

```powershell
docker compose -f module_web_scraping\packages\docker-compose.yml run --rm source-monitoring
```

EUR-Lex connector:

```powershell
docker compose -f module_web_scraping\packages\docker-compose.yml run --rm eurlex-connector
```

Validation engine:

```powershell
docker compose -f module_web_scraping\packages\docker-compose.yml run --rm validation-engine
```

Scoring engine:

```powershell
docker compose -f module_web_scraping\packages\docker-compose.yml run --rm scoring-engine
```

Regulatory data storage:

```powershell
docker compose -f module_web_scraping\packages\docker-compose.yml run --rm regulatory-data-storage
```

## What Each Service Demonstrates

`source-monitoring` extracts deterministic monitored items from a demo official
source page and labels them by regulatory area.

`eurlex-connector` builds demo EUR-Lex SOAP query envelopes for CELEX and keyword
searches. The smoke run does not call the live EUR-Lex service.

`validation-engine` groups seeded regulatory signals into dashboard-ready events
and classifies them as official publication, official draft, or unconfirmed news.

`scoring-engine` calculates reliability, urgency, regulatory impact, business
impact, final priority, and recommended attention.

`regulatory-data-storage` writes a small JSONL sample to the mounted `storage`
folder so persistence can be inspected.

`demo-report` generates a consolidated Markdown and JSON report from the
deterministic MVP data. This gives the demo a final artifact that can be opened
after the terminal run.

`demo-outputs` generates concrete JSON and Markdown output files from the
deterministic web scraping flow. These files are useful for review, handoff, and
future dashboard integration.

It also creates `articles_and_news_feed.html`, a static browser-friendly feed of
monitored articles, official updates, draft guidance, and trusted news warnings.

## Short Explanation

This is not the final product. It is a working MVP demonstration of a modular
regulatory monitoring pipeline. Each responsibility is isolated in its own
Docker container, and each container has a smoke script that proves the module
can start, import the project code, read demo inputs, and produce structured
output. The report command turns those structured outputs into a concise review
artifact.
