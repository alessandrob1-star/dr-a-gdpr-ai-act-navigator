# Regulatory Data Sources

## Source Selection Principles

The project should prioritize official, stable, and citable sources.

Preferred sources:

- official EU legal texts;
- European Commission implementation pages;
- European AI Office guidance;
- European Data Protection Board guidance;
- official regulatory authority materials;
- selected news sources only as lower-confidence monitoring inputs.

Avoid relying on:

- law firm summaries as primary sources;
- blog posts as legal evidence;
- uncited online explainers;
- LLM-generated summaries without source verification.

## Primary Official Sources for MVP

### 1. EUR-Lex

Purpose:

- official EU legal texts;
- regulations;
- consolidated versions;
- recitals;
- annexes.

Use for:

- EU AI Act;
- GDPR.

Important metadata:

- CELEX identifier;
- regulation number;
- article number;
- recital number;
- annex number;
- language;
- source URL;
- retrieval date.

### 2. European Commission AI Act Pages

Purpose:

- AI Act implementation guidance;
- risk-based approach summaries;
- application timelines;
- links to official tools and guidance;
- AI Office updates.

Use for:

- application timeline;
- prohibited practices;
- high-risk examples;
- transparency obligations;
- GPAI obligations;
- implementation updates.

### 3. European AI Office

Purpose:

- AI Act implementation support;
- GPAI guidance;
- codes of practice;
- policy updates.

Use for:

- official AI Act implementation monitoring;
- guidance-related retrieval;
- validation of AI Act news.

### 4. GDPR Official Text

Purpose:

- data protection obligations;
- controller and processor concepts;
- lawful basis;
- transparency;
- data subject rights;
- DPIA provisions;
- automated decision-making and profiling.

Use for:

- GDPR impact flags;
- privacy-related risk notes;
- chat assistant answers.

### 5. European Data Protection Board

Purpose:

- GDPR guidelines, recommendations, and best practices.

Use for:

- interpreting GDPR risk areas;
- validating privacy-related news;
- supporting privacy recommendations.

### 6. ENISA

Purpose:

- cybersecurity guidance and EU security context.

Use for:

- secondary context where AI Act or GDPR risk intersects with cybersecurity;
- future extension toward NIS2 or security-related obligations.

## News and Secondary Monitoring Sources

News and commentary sources can be useful for early detection, but they should not be treated as official regulatory evidence.

Use cases:

- detect upcoming consultations or guidance;
- identify emerging compliance debates;
- create early warnings for the dashboard;
- trigger validation checks against official sources.

Output label:

- `WARNING`.

Required validation status:

- `A_OFFICIALLY_PUBLISHED`;
- `B_OFFICIAL_DRAFT`;
- `C_UNCONFIRMED_NEWS`.

## Data Model Draft

### Source Chunk

Each official source chunk should include:

- `source_id`;
- `source_type`;
- `title`;
- `regulation`;
- `article`;
- `recital`;
- `annex`;
- `section`;
- `text`;
- `url`;
- `publication_date`;
- `retrieved_at`;
- `language`;
- `version`.

### Company Profile

Each company profile should include:

- `company_id`;
- `sector`;
- `employee_count`;
- `eu_market_exposure`;
- `ai_use_cases`;
- `personal_data_processed`;
- `special_category_data_processed`;
- `high_risk_ai_indicators`;
- `business_critical_processes`;
- `created_at`;
- `updated_at`.

### Alert or Warning

Each monitored item should include:

- `item_id`;
- `item_type`;
- `source`;
- `title`;
- `date`;
- `url`;
- `regulatory_area`;
- `summary`;
- `source_confidence`;
- `validation_status`;
- `retrieved_at`.

### Risk Score

Each risk score should include:

- `score_id`;
- `company_id`;
- `item_id`;
- `applicability`;
- `penalty_impact`;
- `urgency`;
- `business_criticality`;
- `risk_score`;
- `risk_level`;
- `explanation`;
- `created_at`.

## Citation Format

The product should cite sources in a human-readable way.

Example:

`EU AI Act, Article X, source: EUR-Lex`

or:

`GDPR, Article 35, Data Protection Impact Assessment, source: EUR-Lex`

For the MVP, citations can link to source documents and identify article-level references. Fine-grained paragraph citation can be added later.

## Future Expansion Sources

These sources are not part of the first MVP, but may support later modules:

- national supervisory authority materials;
- European Commission NIS2 pages;
- EBA, ESMA, and EIOPA materials for DORA;
- Cyber Resilience Act official pages and implementing guidance.
