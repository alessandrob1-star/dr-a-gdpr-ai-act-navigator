# Topic Detection Rules

## Purpose

This document defines the first rule-based topic detection logic for monitored items.

The goal is to classify collected source items into relevant AI Act and GDPR topics before validation, grouping, and scoring.

The MVP should start with deterministic keyword rules. More advanced semantic classification can be added later.

## Core Principle

Topic detection should answer:

```text
Which regulatory area does this source item belong to?
```

and:

```text
Which specific topic labels should be attached to it?
```

## Main Regulation Areas

### AI_ACT

Use when the item mentions:

- AI Act;
- Artificial Intelligence Act;
- Regulation (EU) 2024/1689;
- EU AI regulation;
- AI Office;
- high-risk AI;
- prohibited AI practices;
- general-purpose AI;
- GPAI;
- transparency obligations under the AI Act.

### GDPR

Use when the item mentions:

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

Use when the item discusses both AI Act and GDPR together.

Examples:

- AI Act and GDPR interaction;
- AI governance and data protection;
- automated decision-making under GDPR and AI Act;
- privacy implications of AI Act obligations.

## Topic Labels

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
- deep fake disclosure;
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

## Detection Logic

For each monitored item:

1. Combine title, summary, and available text.
2. Normalize text:
   - lowercase;
   - remove punctuation;
   - collapse extra whitespace.
3. Search for topic keywords.
4. Assign all matching topic labels.
5. Assign the main regulation area.

If both AI Act and GDPR terms are found, use:

```text
GDPR_AI_ACT_INTERPLAY
```

while keeping both AI Act and GDPR topic labels.

## Priority Rule

If an item matches several topic labels, keep all labels.

Example:

```text
An article about AI recruitment tools and automated decision-making may receive:

AI_ACT_HIGH_RISK
GDPR_AUTOMATED_DECISION_MAKING
GDPR_DPIA
```

## Out-of-Scope Rule

If no relevant AI Act or GDPR keyword is found, the item should be marked as:

```text
ignored_out_of_scope
```

The item can still be logged for debugging, but it should not create a regulatory event.

## MVP Boundary

The first implementation should prefer simple and explainable matching.

Later improvements:

- synonym dictionaries;
- multilingual keyword support;
- semantic classification;
- LLM-assisted classification;
- confidence score per topic;
- manual correction workflow.

