# Source Monitoring Package

## Responsibility

This package monitors curated official and trusted-warning sources and prepares
raw monitored items for the rest of the regulatory intelligence pipeline.

## Scope

Initial sources include:

- EUR-Lex Official Journal pages
- European Commission AI Office pages
- EDPB guidance and news pages
- selected trusted privacy and EU policy news sources

## Expected Inputs

- source registry
- monitoring configuration
- optional RSS or webpage endpoints

## Expected Outputs

- monitored item records
- source metadata
- retrieval timestamp
- normalized title and URL
- detected regulation area
- detected topic labels

## Docker

Build from the repository root:

```powershell
docker build -f module_web_scraping/packages/source_monitoring/Dockerfile -t ai-regulatory-source-monitoring:local .
```

Run smoke check:

```powershell
docker run --rm ai-regulatory-source-monitoring:local
```

The container prints a sample monitored-item payload from deterministic static
HTML so the package can be checked without live network access.
