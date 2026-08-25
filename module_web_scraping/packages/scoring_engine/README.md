# Scoring Engine Package

## Responsibility

This package calculates alert priority from regulatory evidence and business
impact inputs.

## Scoring Dimensions

- reliability
- urgency
- regulatory impact
- business impact

## Expected Inputs

- validation status
- authority level of evidence
- topic labels
- compliance deadlines
- company relevance signals from the company profile module

## Expected Outputs

- reliability score
- urgency score
- regulatory impact score
- final priority
- scoring explanation

## Docker

Build from the repository root:

```powershell
docker build -f module_web_scraping/packages/scoring_engine/Dockerfile -t ai-regulatory-scoring-engine:local .
```

Run smoke check:

```powershell
docker run --rm ai-regulatory-scoring-engine:local
```

The container calculates one deterministic draft score using the current MVP
scoring rules.
