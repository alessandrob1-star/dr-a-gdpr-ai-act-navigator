# EUR-Lex Connector Package

## Responsibility

This package isolates access to the official EUR-Lex webservice and stable legal
links.

## Scope

The connector is responsible for:

- building EUR-Lex expert-search queries
- calling the SOAP webservice
- receiving XML responses
- extracting useful legal identifiers such as CELEX IDs
- converting official API responses into JSON-ready internal records

## Expected Inputs

- CELEX identifiers
- keyword queries
- EUR-Lex credentials
- page and page size parameters

## Expected Outputs

- official source evidence
- CELEX IDs
- official document links
- response summaries
- XML-to-JSON transformed records

## Docker

Build from the repository root:

```powershell
docker build -f module_web_scraping/packages/eurlex_connector/Dockerfile -t ai-regulatory-eurlex-connector:local .
```

Run smoke check:

```powershell
docker run --rm ai-regulatory-eurlex-connector:local
```

The container builds demo EUR-Lex SOAP envelopes only. It does not call the
live EUR-Lex service.
