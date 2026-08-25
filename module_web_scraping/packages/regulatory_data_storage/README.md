# Regulatory Data Storage Package

## Responsibility

This package owns local persistence for regulatory intelligence data.

DuckDB is the selected MVP database because it runs as an embedded database
file, supports SQL, works well in Docker, and does not require a separate
database server.

## Expected Stored Data

- curated sources
- monitoring runs
- monitored items
- source evidence
- regulatory events
- validation status history
- scoring history

## Expected Consumers

- web dashboard
- AI compliance assistant
- validation engine
- scoring engine

## Docker

Build from the repository root:

```powershell
docker build -f module_web_scraping/packages/regulatory_data_storage/Dockerfile -t ai-regulatory-data-storage:local .
```

Run smoke check:

```powershell
docker run --rm ai-regulatory-data-storage:local
```

The container writes a small deterministic JSONL sample to `/app/storage`.

## Notes

See [docs/duckdb-plan.md](docs/duckdb-plan.md) for the initial DuckDB plan.
