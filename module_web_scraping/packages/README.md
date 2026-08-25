# Modular Package Workspace

This folder contains the independent package structure for the regulatory
intelligence platform.

The packages are intentionally small and independently containerizable. Each
package owns one responsibility and can later expose a CLI, API, worker, or
library interface without forcing the rest of the system to change.

## Web Scraping Area Packages

The current package split for the web scraping and regulatory monitoring area is:

1. `source_monitoring`
   - reads curated sources
   - collects official and trusted-warning source items
   - prepares raw monitored items

2. `eurlex_connector`
   - connects to the official EUR-Lex webservice
   - prepares SOAP requests
   - converts XML responses into internal JSON-ready objects

3. `validation_engine`
   - classifies evidence as warning, official draft, or official publication
   - compares trusted news against official EU sources
   - prepares validation status for dashboard alerts

4. `scoring_engine`
   - calculates reliability, urgency, and regulatory impact
   - produces priority levels for dashboard review

5. `regulatory_data_storage`
   - stores sources, monitored items, evidence, and regulatory events
   - uses DuckDB as the lightweight MVP database
   - provides query-ready data for the dashboard and assistant

## Container Strategy

Each package has its own Dockerfile. The package-level `docker-compose.yml`
defines one service per package so the team can run or test modules
independently.

The current containers are draft smoke targets. They document the intended
package boundaries and run a small deterministic check against the MVP code.

Each package folder includes:

- `Dockerfile`
- `requirements.txt`
- `package_manifest.yml`
- `smoke.py`
- package-specific notes in `README.md`
