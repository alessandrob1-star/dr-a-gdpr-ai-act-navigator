# Company Profile Questionnaire Schema

## Purpose

This document defines a structured questionnaire for the Company Profiling module.

The goal is to avoid open-ended answers in the MVP. The company should answer through predefined options, checkboxes, and simple yes/no fields. This makes the company profile easier to store, query, and connect to regulatory alerts.

The questionnaire should produce a structured company profile that can be used by:

- the Regulatory Knowledge Base;
- the Source Monitoring and Validation module;
- the Risk Scoring Engine;
- the Dashboard;
- the AI Compliance Assistant.

## Design Principle

Each answer should influence at least one of the following:

- GDPR relevance;
- AI Act relevance;
- high-risk AI relevance;
- prohibited AI practice relevance;
- transparency obligation relevance;
- general-purpose AI relevance;
- data breach relevance;
- DPIA relevance;
- international transfer relevance;
- urgency or business impact scoring.

If an answer does not influence any downstream logic, it should not be included in the MVP questionnaire.

## Recommended Input Types

Use controlled fields only:

- single-choice dropdown;
- multi-choice checkbox;
- yes/no toggle;
- numeric range;
- date field where necessary.

Avoid free-text fields in the MVP, except for optional company name or internal notes.

## Suggested Database Model

For the MVP, the company profile can be stored as columns with boolean flags and selected categories.

Suggested table:

```text
company_profiles
```

Suggested fields:

- `id`
- `company_name`
- `industry`
- `company_size`
- `operates_in_eu`
- `has_eu_customers`
- `uses_ai_systems`
- `develops_ai_systems`
- `provides_ai_systems_to_clients`
- `provides_general_purpose_ai_model`
- `uses_third_party_ai_tools`
- `uses_biometric_identification`
- `uses_emotion_recognition`
- `uses_automated_decision_making`
- `uses_ai_for_hr_or_recruitment`
- `uses_ai_for_credit_or_finance`
- `uses_ai_for_education`
- `uses_ai_for_healthcare`
- `uses_ai_for_law_enforcement`
- `uses_ai_for_critical_infrastructure`
- `processes_personal_data`
- `processes_sensitive_personal_data`
- `processes_children_data`
- `performs_large_scale_processing`
- `tracks_user_behavior`
- `transfers_data_outside_eu`
- `has_dpo`
- `has_dpia_process`
- `has_data_breach_process`
- `has_ai_governance_policy`
- `created_at`
- `updated_at`

This structure is intentionally simple. It can later be normalized into multiple tables if needed.

## Questionnaire Sections

### 1. Company Basics

Purpose:

Understand the business context and company size.

Fields:

```text
company_name: text
industry: single choice
company_size: single choice
operates_in_eu: yes/no
has_eu_customers: yes/no
```

Suggested `industry` options:

- Technology / SaaS
- Healthcare
- Finance / Insurance
- Education
- HR / Recruitment
- Retail / E-commerce
- Marketing / Advertising
- Manufacturing
- Legal / Professional services
- Public sector
- Other

Suggested `company_size` options:

- 1-9 employees
- 10-49 employees
- 50-249 employees
- 250+ employees

Regulatory relevance:

- EU customers or EU operations activate GDPR and AI Act monitoring.
- Certain industries increase business impact for high-risk AI categories.

### 2. AI Usage

Purpose:

Understand whether the company uses or develops AI.

Fields:

```text
uses_ai_systems: yes/no
develops_ai_systems: yes/no
provides_ai_systems_to_clients: yes/no
uses_third_party_ai_tools: yes/no
provides_general_purpose_ai_model: yes/no
```

Regulatory relevance:

- AI use activates AI Act relevance.
- AI development or provision increases regulatory impact.
- General-purpose AI model provision activates GPAI obligations.

### 3. AI Use Cases

Purpose:

Identify possible high-risk AI areas.

Fields:

```text
uses_ai_for_hr_or_recruitment: yes/no
uses_ai_for_credit_or_finance: yes/no
uses_ai_for_education: yes/no
uses_ai_for_healthcare: yes/no
uses_ai_for_law_enforcement: yes/no
uses_ai_for_critical_infrastructure: yes/no
uses_ai_for_biometric_identification: yes/no
uses_ai_for_emotion_recognition: yes/no
```

Regulatory relevance:

- HR, education, credit, healthcare, law enforcement, and critical infrastructure can trigger high-risk AI assessment.
- Biometric identification and emotion recognition require special attention because they may involve high-risk or prohibited practices depending on context.

### 4. Personal Data Processing

Purpose:

Understand GDPR exposure.

Fields:

```text
processes_personal_data: yes/no
processes_sensitive_personal_data: yes/no
processes_children_data: yes/no
performs_large_scale_processing: yes/no
tracks_user_behavior: yes/no
uses_automated_decision_making: yes/no
```

Regulatory relevance:

- Personal data activates GDPR relevance.
- Sensitive data, children data, large-scale processing, tracking, and automated decision-making increase DPIA relevance.
- Automated decision-making connects GDPR and AI Act monitoring.

### 5. Data Transfers and Security

Purpose:

Identify international transfer and breach readiness issues.

Fields:

```text
transfers_data_outside_eu: yes/no
uses_non_eu_cloud_or_ai_provider: yes/no
has_data_breach_process: yes/no
has_dpia_process: yes/no
has_dpo: yes/no
```

Regulatory relevance:

- Non-EU data transfers activate international transfer guidance.
- Missing breach process increases business impact for GDPR breach alerts.
- Missing DPIA process increases business impact for high-risk processing.

### 6. Governance Readiness

Purpose:

Estimate whether the company has basic compliance processes.

Fields:

```text
has_ai_governance_policy: yes/no
has_model_documentation: yes/no
has_human_oversight_process: yes/no
has_vendor_review_process: yes/no
has_user_transparency_notice: yes/no
```

Regulatory relevance:

- Missing governance controls increase business impact.
- Transparency notices connect to AI Act Article 50 monitoring.
- Human oversight and documentation are relevant for high-risk AI systems.

## Example Mapping Rules

### GDPR Active

Condition:

```text
operates_in_eu = true
OR has_eu_customers = true
OR processes_personal_data = true
```

Result:

```text
Enable GDPR monitoring.
```

### AI Act Active

Condition:

```text
uses_ai_systems = true
OR develops_ai_systems = true
OR provides_ai_systems_to_clients = true
```

Result:

```text
Enable AI Act monitoring.
```

### High-Risk AI Candidate

Condition:

```text
uses_ai_for_hr_or_recruitment = true
OR uses_ai_for_credit_or_finance = true
OR uses_ai_for_education = true
OR uses_ai_for_healthcare = true
OR uses_ai_for_law_enforcement = true
OR uses_ai_for_critical_infrastructure = true
```

Result:

```text
Increase business impact for AI Act high-risk guidance and alerts.
```

### DPIA Candidate

Condition:

```text
processes_sensitive_personal_data = true
OR processes_children_data = true
OR performs_large_scale_processing = true
OR tracks_user_behavior = true
OR uses_automated_decision_making = true
```

Result:

```text
Increase relevance of GDPR DPIA guidance.
```

### International Transfers Candidate

Condition:

```text
transfers_data_outside_eu = true
OR uses_non_eu_cloud_or_ai_provider = true
```

Result:

```text
Increase relevance of EDPB international transfer guidance.
```

### Transparency Obligation Candidate

Condition:

```text
uses_ai_systems = true
AND has_user_transparency_notice = false
```

Result:

```text
Increase relevance of AI Act transparency obligation alerts.
```

## MVP Output

The questionnaire should produce a structured object like this:

```json
{
  "company_name": "Example AI Startup",
  "industry": "Technology / SaaS",
  "company_size": "10-49 employees",
  "gdpr_active": true,
  "ai_act_active": true,
  "high_risk_ai_candidate": true,
  "dpia_candidate": true,
  "international_transfers_candidate": false,
  "gpai_candidate": false,
  "transparency_obligation_candidate": true
}
```

## Demo Scenario

For the final demo, the questionnaire should make the dashboard visibly change.

Example:

Company A:

- SaaS startup;
- uses AI chatbot;
- processes personal data;
- no high-risk AI use case.

Expected result:

- GDPR alerts active;
- AI Act transparency alerts active;
- high-risk AI alerts lower priority.

Company B:

- HR tech startup;
- develops AI recruitment screening;
- processes candidate personal data;
- uses automated decision-making.

Expected result:

- GDPR alerts active;
- DPIA alerts high priority;
- AI Act high-risk alerts high priority;
- transparency and human oversight alerts relevant.

## Implementation Note

The first version can be implemented with simple rules and boolean columns.

Later, the module can evolve into:

- normalized questionnaire answer tables;
- versioned company profiles;
- profile history;
- memory agent;
- company-specific risk explanations.

For the MVP, the most important objective is to make questionnaire answers directly influence regulatory relevance and dashboard priorities.

