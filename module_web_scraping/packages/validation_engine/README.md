# Validation Engine Package

## Responsibility

This package validates regulatory signals by comparing warning sources against
official EU sources.

## Validation States

- `C_UNCONFIRMED_NEWS`
- `B_OFFICIAL_DRAFT`
- `A_OFFICIALLY_PUBLISHED`

## Expected Inputs

- monitored items
- official source evidence
- trusted-warning evidence
- grouped regulatory events

## Expected Outputs

- validation status
- validation explanation
- official evidence links
- confidence indicators for the dashboard

## Docker

Build from the repository root:

```powershell
docker build -f module_web_scraping/packages/validation_engine/Dockerfile -t ai-regulatory-validation-engine:local .
```

Run smoke check:

```powershell
docker run --rm ai-regulatory-validation-engine:local
```

The container validates seeded regulatory events and prints status counts plus
a small dashboard-ready sample.
