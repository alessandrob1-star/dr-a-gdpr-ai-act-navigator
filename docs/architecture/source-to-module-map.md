# Source-to-Module Map

This map links regulatory inputs to the current executable modules.

## Company questionnaire and profile

Primary references:

- EU AI Act official text and implementation guidance;
- GDPR official text;
- EDPB guidance on DPIA, roles, rights, breaches, and transfers.

Implementation:

- questionnaire schema: `module_company_profile/dashboard/assets/js/core.js`;
- Company Profile Agent: `module_agents/company_profile_agent.py`;
- deterministic rules:
  `module_company_profile/memory_agent/company_memory_agent.py`.

Result: normalized company memory, relevance tags, controls, and an assessment
trace linked to questionnaire answers.

## Official and trusted source monitoring

Source categories:

- EUR-Lex and Official Journal material;
- European Commission and European AI Office pages;
- EDPB publications;
- selected trusted professional sources used only for early warning.

Implementation:

- source registry: `module_web_scraping/source_registry_seed.csv`;
- ingestion and normalization: `module_web_scraping/`;
- runtime feed boundary: `module_agents/regulatory_monitoring_agent.py`;
- normalized storage: `storage/web_scraping_outputs/`.

Result: source-linked records with official, guidance, or non-binding status and
truthful live/cached/demo feed metadata.

## Company-specific matching and prioritization

Primary references:

- AI Act risk classification, prohibited-practice, transparency, and GPAI
  material;
- GDPR DPIA, international-transfer, breach, and rights guidance.

Implementation:

- Regulatory Matching Agent: `module_agents/regulatory_matching_agent.py`;
- deterministic matching, warning, grouping, score, and timeline services:
  `company_memory_agent.py`;
- curated events: `storage/web_scraping_outputs/regulatory_events.json`.

Result: personalized warnings, missing controls, score contributions, timeline,
official updates, and early-warning cards.

## Dr. A explanations

Inputs:

- server-rebuilt company memory;
- personalized dashboard context;
- topic-matched regulatory sources;
- current question and limited conversation history.

Implementation:

- Dr. A Agent: `module_agents/dr_a_agent.py`;
- Policy Agent: `policy_agent/`;
- HTTP streaming: `module_company_profile/dashboard/dashboard_server.py`.

Result: model-generated explanations constrained by question-specific evidence,
policy checks, citation validation, and objective grounding checks. Dr. A does
not use a vector database or unrestricted RAG in the current MVP.

## Dashboard and reports

Implementation:

- frontend: `module_company_profile/dashboard/`;
- locale dictionaries: `dashboard/assets/js/i18n/locales/`;
- snapshots: `dashboard/profile_store.py`;
- reports: `dashboard/report_exporter.py`.

Result: multilingual score and warning views, source links, chat, timeline,
snapshot comparison, and PDF/DOCX export.
