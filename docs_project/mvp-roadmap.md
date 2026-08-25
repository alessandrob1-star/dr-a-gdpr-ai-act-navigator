# MVP Roadmap

> **Status:** original 11-week planning baseline retained for project history.
> It is not the current architecture or an implementation-status checklist. See
> [`architecture.md`](architecture.md), [`agents.md`](agents.md), and the root
> [`README.md`](../README.md) for the implemented system.

## Original Timeline Assumption

This roadmap assumes an 11-week solo delivery window.

## Delivery Philosophy

The MVP should prove the regulatory intelligence workflow with a narrow, high-quality demo.

The 11-week version should demonstrate:

- one realistic company profile;
- GDPR and EU AI Act only;
- a curated set of official sources;
- a curated set of trusted news or specialist sources;
- warning creation from pseudo-reliable news;
- official verification through selected APIs or publication pages;
- validation states for unconfirmed news, official drafts, and official publications;
- simple reliability, urgency, and company-specific priority scoring;
- one dashboard and one chat assistant.

The 11-week version should not attempt:

- complete coverage of every EU and national source;
- real-time production monitoring;
- full legal compliance automation;
- a legal-advisor-grade system;
- DORA, NIS2, Cyber Resilience Act, or national implementation mapping.

## Week 1: Scope and Product Definition

Goals:

- finalize the platform scope around GDPR and the EU AI Act;
- define the target user as a European SME or AI startup founder, product lead, or compliance owner;
- define the main demo scenario;
- define the difference between official alerts and news warnings;
- prepare reviewer questions.

Deliverables:

- updated README;
- problem statement;
- MVP scope;
- initial architecture draft.

## Week 2: Data Model and User Flows

Goals:

- design the company onboarding questionnaire;
- define the company profile schema;
- define long-term memory objects;
- define alert, warning, validation, and risk-score schemas;
- choose official and news data sources for the MVP.

Deliverables:

- onboarding questionnaire draft;
- company profile model;
- alert and validation status model;
- source list.

## Week 3: Project Setup and Regulatory Knowledge Base

Goals:

- create the codebase structure;
- implement document ingestion for selected official GDPR and AI Act sources;
- chunk legal texts by article, recital, annex, or guidance section where possible;
- create the first vector and keyword indexes.

Deliverables:

- local document store;
- ingestion pipeline prototype;
- metadata schema;
- first RAG retrieval tests.

## Week 4: Company Profiling and Memory

Goals:

- implement the company onboarding flow;
- persist company profile, questionnaire answers, alert history, risk-score history, and completed actions;
- expose the memory layer to downstream analysis.

Deliverables:

- working onboarding flow;
- persistent company profile;
- company memory service.

## Week 5: Official Regulatory Monitoring

Goals:

- implement scheduled or manual checks for a curated set of official sources;
- normalize official matches into confirmation objects;
- assign source, title, date, link, update type, publication status, effective date, and reliability;
- connect official confirmations to company relevance checks.

Deliverables:

- official-source verification prototype;
- official confirmation feed;
- relevance scoring draft.

## Week 6: News Monitoring and Validation

Goals:

- collect news or specialist compliance updates from a curated set of trusted sources;
- label these items as warnings rather than official alerts;
- implement validation against selected official sources;
- classify each item as official publication, official draft, or unconfirmed news.

Deliverables:

- news monitoring prototype;
- validation agent;
- validation status labels.

## Week 7: Risk Assessment Engine

Goals:

- implement the company-specific priority scoring model;
- combine source reliability, regulatory applicability, penalty impact, urgency, business criticality, and readiness gap;
- produce Critical, High, Medium, and Low risk levels;
- store risk-score history in company memory.

Deliverables:

- risk scoring service;
- reliability and urgency scoring;
- score history;
- top-risk output.

## Week 8: AI Compliance Assistant

Goals:

- implement chat over regulatory RAG, company memory, and alert history;
- require citations for regulatory claims;
- support company-specific questions such as urgent GDPR or AI Act risks;
- add guardrails against unsupported legal conclusions.

Deliverables:

- chat assistant prototype;
- cited answers;
- fallback behavior for unsupported questions.

## Week 9: Dashboard Integration

Goals:

- integrate onboarding, memory, monitoring, validation, scoring, and chat;
- build dashboard sections for company overview, risk dashboard, regulatory alerts, compliance timeline, and AI chat;
- prepare realistic demo data.

Deliverables:

- end-to-end dashboard;
- demo scenario data;
- integrated workflow.

## Week 10: Reliability and Evaluation

Goals:

- test several company scenarios;
- improve citation reliability;
- test validation status outputs;
- document known limitations;
- polish the dashboard.

Deliverables:

- scenario tests;
- known limitations document;
- demo-ready application.

## Week 11: Final Submission and Pitch

Goals:

- finalize documentation;
- record a working demo;
- prepare a 5-minute pitch;
- prepare backup screenshots and Q&A answers.

Deliverables:

- final code;
- final report;
- pitch deck;
- final demo script.

## Success Criteria

The MVP is successful if it can:

- create and persist a realistic company profile;
- retrieve GDPR and AI Act evidence from official sources;
- create warnings from trusted but non-binding news sources;
- validate warnings against selected official sources;
- distinguish unconfirmed news, official drafts, and official publications;
- calculate reliability, urgency, and company-specific priority scores;
- prioritize alerts and timeline items;
- answer company-specific regulatory questions with citations;
- show a polished end-to-end dashboard demo.
