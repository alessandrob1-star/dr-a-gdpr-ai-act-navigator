# Historical Architecture Proposal: Python Multi-Agent MVP

> **Status:** early planning document retained for design history. It proposes
> FastAPI, vector retrieval, and additional agents that are not part of the
> current executable MVP. For the implemented architecture, use
> [`architecture.md`](architecture.md), [`agents.md`](agents.md), and
> [`../docs/CODE_WALKTHROUGH.md`](../docs/CODE_WALKTHROUGH.md).

## Project Overview

This project is an AI-powered regulatory intelligence platform for European SMEs and AI startups.

It helps companies understand, monitor, and prioritize relevant obligations under:

- GDPR
- EU AI Act

The platform does not provide legal advice. Its goal is regulatory triage and prioritization: it helps a company understand which regulatory signals are relevant, whether they are official, and what should be handled first.

The core idea is to combine:

- company-specific memory;
- Python-based agents;
- news and regulatory signal monitoring;
- official source verification;
- validation status tracking;
- explainable risk scoring;
- RAG-based assistance with citations.

## Core Concept

The key differentiator is the validation pipeline:

```text
News Signal -> Official Verification -> Validation Status -> Risk Scoring -> Company Impact
```

The platform does not treat news as law. A news item is only an early warning until it is checked against official regulatory sources.

This makes the system different from a generic legal chatbot. It is designed to answer a more practical question:

```text
Which regulatory updates actually matter for this specific company, and why?
```

## Python-First Technical Direction

The project is intentionally Python-first because the main intelligence layer involves tasks where Python is a strong fit:

- data processing;
- document ingestion;
- scraping and source monitoring;
- embeddings and retrieval;
- agent orchestration;
- risk scoring;
- LLM integration;
- compliance-oriented reasoning.

The frontend can be implemented separately, but the core product logic should live in Python.

## Recommended MVP Stack

### Backend and Agents

- Python
- FastAPI
- Pydantic
- SQLite for MVP storage
- PostgreSQL as a future production upgrade

### Agent and Data Processing Layer

- requests / httpx
- BeautifulSoup
- Playwright only when dynamic pages require it
- pandas where useful for data inspection and exports

### RAG and AI Layer

- local regulatory document folder;
- chunking and indexing pipeline;
- sentence-transformers or another embedding model;
- ChromaDB or FAISS for local vector search;
- OpenAI GPT-5.6 Sol for grounded explanations;
- optional API-based LLM adapter as a future extension.

### User Interface

For the MVP, two options are realistic:

- Streamlit for a fast Python-native demo;
- React dashboard if a more modern web interface is required.

The recommended interview-friendly version is:

```text
Streamlit or React UI
        |
FastAPI backend
        |
Python multi-agent pipeline
        |
SQLite + local vector index
        |
Local documents + AI assistant API
```

## Multi-Agent Architecture

The project should include agents, but each agent must have a clear responsibility. The agents are not decorative; they represent separate steps in the regulatory intelligence workflow.

```text
Company Profile Agent
        |
News Monitoring Agent
        |
Official Verification Agent
        |
Validation Agent
        |
Risk Scoring Agent
        |
RAG Assistant Agent
        |
Dashboard Output
```

## Agent Responsibilities

### 1. Company Profile Agent

Collects and normalizes company information:

- industry;
- country;
- company size;
- AI use cases;
- personal data processed;
- sensitive data processed;
- GDPR relevance;
- EU AI Act relevance;
- current compliance readiness.

This creates the long-term company memory used by the rest of the system.

### 2. News Monitoring Agent

Detects regulatory signals from curated sources.

For the MVP, this can use:

- curated RSS feeds;
- selected trusted websites;
- static demo data;
- manually seeded news items.

The output is a warning event, not a confirmed legal obligation.

### 3. Official Verification Agent

Checks whether the same regulatory signal appears in official sources such as:

- EUR-Lex;
- European Commission;
- AI Office;
- EDPB;
- official guidance pages.

This agent is responsible for separating unofficial information from official evidence.

### 4. Validation Agent

Assigns a validation status to each regulatory event:

```text
UNCONFIRMED_NEWS
OFFICIAL_DRAFT
OFFICIAL_PUBLICATION
```

This status must be visible in the dashboard so the user understands the reliability of each alert.

### 5. Risk Scoring Agent

Calculates a company-specific priority score.

Example scoring model:

```text
Risk Score = Reliability x Applicability x Urgency x Impact x Readiness Gap
```

The score should be explainable. The system should show why an alert is critical, high, medium, or low priority.

### 6. RAG Assistant Agent

Answers questions using:

- local GDPR documents;
- local EU AI Act documents;
- EDPB or Commission guidance;
- company profile memory;
- validated alerts.

The assistant should provide grounded answers with citations where possible. It should not invent legal conclusions.

### 7. Orchestrator Agent

Coordinates the full workflow:

```text
load company profile
detect regulatory signal
verify official evidence
assign validation status
calculate risk score
save alert
prepare dashboard output
```

The orchestrator makes the system feel like a coherent multi-agent application rather than a collection of unrelated scripts.

## Suggested Python Project Structure

```text
README.md
.env
requirements.txt

app/
  main.py
  api/
    routes_company.py
    routes_alerts.py
    routes_chat.py
  agents/
    orchestrator_agent.py
    company_profile_agent.py
    news_monitoring_agent.py
    official_verification_agent.py
    validation_agent.py
    risk_scoring_agent.py
    rag_assistant_agent.py
  services/
    source_fetcher.py
    document_ingestion.py
    chunking.py
    embeddings.py
    vector_store.py
    openai_client.py
  models/
    company.py
    regulatory_event.py
    source_evidence.py
    risk_score.py
  storage/
    database.py
    repositories.py
  utils/
    logging.py
    scoring.py

documents/
  gdpr/
  eu-ai-act/
  edpb/
  commission/

data/
  demo_news/
  vector_index/
  app.db

docs_project/
  architecture.md
  agents.md
  scoring-model.md
  data-sources.md
```

## Core MVP Workflow

### 1. Company Onboarding

The user enters company information through a questionnaire.

The Company Profile Agent transforms the answers into a structured profile.

### 2. Regulatory Signal Detection

The News Monitoring Agent detects a possible regulatory update from a trusted but non-binding source.

The platform marks this as a warning, not as an official obligation.

### 3. Official Verification

The Official Verification Agent searches official sources for matching evidence.

The event becomes more reliable only when official evidence is found.

### 4. Validation Status

The Validation Agent assigns one of the official statuses:

- unconfirmed news;
- official draft;
- official publication.

### 5. Company-Specific Risk Scoring

The Risk Scoring Agent checks whether the update matters for the company.

It considers:

- source reliability;
- relevance to the company's sector;
- GDPR or AI Act applicability;
- urgency and deadlines;
- potential impact;
- readiness gap.

### 6. RAG-Based Assistant

The user can ask questions about obligations, alerts, and regulatory documents.

The RAG Assistant Agent retrieves relevant chunks from local documents and combines them with company memory.

### 7. Dashboard

The dashboard shows:

- company profile summary;
- validated alerts;
- source reliability;
- validation status;
- risk score;
- explanation;
- recommended priority actions;
- timeline of regulatory events.

## MVP Scope

The MVP should focus on a narrow but complete demonstration.

Included:

- GDPR and EU AI Act only;
- one company onboarding flow;
- persistent company profile;
- curated regulatory/news signals;
- limited official source verification;
- validation status;
- explainable risk scoring;
- local RAG over regulatory documents;
- dashboard output;
- chat assistant with citations.

Not included:

- full EU and national law coverage;
- real-time monitoring of every source;
- enterprise governance workflows;
- legal compliance automation;
- replacement of legal professionals;
- production-grade monitoring infrastructure.

## Strong Demo Scenario

A European SME uses AI to screen job applicants and processes customer data.

The platform should:

1. create a company profile;
2. detect GDPR and EU AI Act relevance;
3. receive a regulatory news signal;
4. classify it as unconfirmed until official evidence is found;
5. verify whether the topic appears in official sources;
6. assign a validation status;
7. calculate risk based on company context;
8. show the alert in a dashboard;
9. explain why the alert matters;
10. answer follow-up questions using local regulatory documents.

## Interview Positioning

This project can be described as:

> A Python-based multi-agent regulatory intelligence MVP for European SMEs. The system monitors regulatory signals, verifies them against official sources, assigns validation status, calculates company-specific risk, and provides a RAG assistant grounded in GDPR and EU AI Act documents.

The strongest technical points to highlight are:

- Python-first architecture;
- multi-agent workflow;
- FastAPI backend;
- source validation pipeline;
- local document ingestion;
- RAG with citations;
- deterministic and explainable risk scoring;
- company-specific memory;
- clear distinction between news, draft, and official law.

## Key Differentiator

Most legal AI tools answer questions using documents.

This project tracks regulatory signals, validates them, and decides what matters for a specific company.

That distinction makes the project more practical, more explainable, and more suitable as a serious portfolio project.

## Disclaimer

This project is an educational and research prototype. It does not provide legal advice and should not be used as a substitute for professional legal review.
