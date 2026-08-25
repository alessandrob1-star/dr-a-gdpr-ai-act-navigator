# Company Memory Design Contract

This folder documents the **Company Memory contract** implemented by
`../memory_agent/company_memory_agent.py`.

## Purpose

The memory object stores normalized company context so other modules can determine:

- whether a regulatory item is relevant for the company;
- whether existing actions already reduce risk.

## Memory Object Contract

The implemented memory object includes:

- `memory_version`
- `created_at`
- `source_questionnaire`
- `source_completed_at`
- `company_profile`
- `ai_profile`
- `privacy_profile`
- `controls`
- `relevance_tags`
- `assessment_trace`
- `compliance_score`
- `risk_warnings`
- `notes`

## Implemented MVP Persistence

The dashboard stores local JSON assessment snapshots under
`storage/company_profile/history/`. SQLite or PostgreSQL remains a possible
future production migration, not a current dependency.

## Integration Targets

This memory contract is used by:

- the Regulatory Matching Agent;
- dashboard score, warning, and control panels;
- local assessment snapshots;
- server-rebuilt Dr. A context;
- PDF and DOCX report generation.

## Boundaries

This contract does not:

- provide a final legal classification;
- validate sources;
- perform scraping;
- provide legal advice.
