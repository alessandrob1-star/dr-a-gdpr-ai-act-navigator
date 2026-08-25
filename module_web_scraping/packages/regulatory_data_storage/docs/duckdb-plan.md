# DuckDB Plan

## Purpose

DuckDB will provide lightweight local persistence for the MVP. It avoids the
need for a separate database server while still giving the team SQL-based data
management.

## Planned Database File

```text
storage/regulatory_intelligence.duckdb
```

## Planned Tables

- `sources`
- `monitoring_runs`
- `monitored_items`
- `source_evidence`
- `regulatory_events`
- `event_sources`
- `validation_results`
- `score_history`

## Initial Data Flow

```text
source_monitoring
      |
      v
monitored_items
      |
      v
validation_engine
      |
      v
regulatory_events
      |
      v
scoring_engine
      |
      v
dashboard-ready query views
```

## MVP Rationale

DuckDB is suitable for the bootcamp MVP because:

- it is easy to run locally;
- it works inside Docker;
- it can persist data in a single file;
- it supports SQL queries for dashboard aggregation;
- it can later be replaced by a server database if needed.
