# 09 - Topic Detection Rules

## Purpose

This document defines the first rule-based topic detection logic for the Web Scraping and Source Monitoring module.

Topic detection is used to classify collected source items before grouping, validation, scoring, and dashboard display.

The MVP should start with simple deterministic rules. Semantic classification or LLM-assisted classification can be added later.

## Core Question

For each monitored item, the system should answer:

```text
Which regulatory area and topic labels does this source item belong to?
```

## Main Regulation Areas

### AI_ACT

Use when an item refers to the EU Artificial Intelligence Act or related implementation material.

Typical signals:

- AI Act;
- Artificial Intelligence Act;
- Regulation (EU) 2024/1689;
- EU AI regulation;
- European AI Office;
- high-risk AI;
- prohibited AI practices;
- general-purpose AI;
- GPAI;
- transparency obligations.

### GDPR

Use when an item refers to EU data protection obligations.

Typical signals:

- GDPR;
- General Data Protection Regulation;
- Regulation (EU) 2016/679;
- personal data;
- data protection;
- data subject rights;
- controller;
- processor;
- DPIA;
- data breach;
- international transfers.

### GDPR_AI_ACT_INTERPLAY

Use when an item discusses both AI Act and GDPR together.

Examples:

- interaction between AI Act and GDPR;
- automated decision-making and AI governance;
- privacy impact of AI systems;
- data protection implications of AI Act obligations.

## Topic Labels

Each monitored item can receive one or more topic labels.

### AI_ACT_GENERAL

Keywords:

- AI Act;
- Artificial Intelligence Act;
- Regulation (EU) 2024/1689;
- EU AI regulation;
- AI Office.

### AI_ACT_PROHIBITED_PRACTICES

Keywords:

- prohibited AI practices;
- unacceptable risk;
- banned AI systems;
- social scoring;
- manipulative AI;
- biometric categorisation;
- emotion recognition;
- real-time remote biometric identification.

### AI_ACT_HIGH_RISK

Keywords:

- high-risk AI;
- high risk AI;
- Annex III;
- Annex I;
- conformity assessment;
- risk management system;
- human oversight;
- technical documentation;
- quality management system;
- post-market monitoring.

### AI_ACT_TRANSPARENCY

Keywords:

- transparency obligations;
- Article 50;
- AI-generated content;
- chatbot disclosure;
- deepfake disclosure;
- synthetic content;
- users must be informed;
- deployer transparency.

### AI_ACT_GPAI

Keywords:

- general-purpose AI;
- GPAI;
- general purpose AI model;
- systemic risk;
- model provider;
- Code of Practice;
- model documentation;
- copyright policy;
- safety and security chapter.

### GDPR_GENERAL

Keywords:

- GDPR;
- General Data Protection Regulation;
- Regulation (EU) 2016/679;
- personal data;
- data protection;
- lawful basis;
- consent;
- legitimate interest.

### GDPR_DPIA

Keywords:

- DPIA;
- Data Protection Impact Assessment;
- high risk processing;
- Article 35;
- likely to result in a high risk;
- risk to rights and freedoms.

### GDPR_DATA_BREACH

Keywords:

- personal data breach;
- data breach notification;
- Article 33;
- Article 34;
- supervisory authority notification;
- breach communication to data subjects.

### GDPR_INTERNATIONAL_TRANSFERS

Keywords:

- international transfers;
- third country transfer;
- Standard Contractual Clauses;
- SCCs;
- supplementary measures;
- adequacy decision;
- transfer impact assessment.

### GDPR_AUTOMATED_DECISION_MAKING

Keywords:

- automated decision-making;
- profiling;
- Article 22;
- solely automated processing;
- meaningful information about logic;
- significant effects.

### GDPR_CONTROLLER_PROCESSOR

Keywords:

- controller;
- processor;
- joint controller;
- processing agreement;
- Article 28;
- controller processor relationship.

### GDPR_DATA_SUBJECT_RIGHTS

Keywords:

- right of access;
- data subject rights;
- right to erasure;
- right to rectification;
- right to object;
- right to portability;
- access request.

## Detection Flow

For each monitored item:

1. Combine title, summary, and available extracted text.
2. Normalize the text:
   - lowercase;
   - remove punctuation;
   - collapse extra whitespace.
3. Search for topic keywords.
4. Assign all matching topic labels.
5. Assign the main regulation area.
6. Mark irrelevant items as out of scope.

## Interplay Rule

If both AI Act and GDPR topic labels are detected, use:

```text
GDPR_AI_ACT_INTERPLAY
```

as the main regulation area when the item clearly discusses both frameworks.

Example:

```text
An article about AI recruitment tools and automated decision-making may receive:

AI_ACT_HIGH_RISK
GDPR_AUTOMATED_DECISION_MAKING
GDPR_DPIA
```

## Out-of-Scope Rule

If no AI Act or GDPR keyword is found, the item should be marked as:

```text
ignored_out_of_scope
```

The item can be logged for debugging, but it should not create a regulatory event.

## MVP Success Criteria

Topic detection is successful if it can:

- identify whether an item belongs to AI Act, GDPR, or both;
- assign one or more useful topic labels;
- filter clearly irrelevant items;
- support event grouping and validation;
- remain explainable during the demo.

