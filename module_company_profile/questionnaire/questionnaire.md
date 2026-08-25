# Company Onboarding Questionnaire Design

This document records the questionnaire design implemented in the integrated
dashboard and used to create a structured company profile.
It is a triage instrument, not legal advice.

## ISSUE-010: Questionnaire Sections

The questionnaire is organized into the required sections:

1. **Company basics**
2. **AI usage**
3. **AI use cases**
4. **Personal data processing**
5. **Data transfers and security**
6. **Governance readiness**

## MVP Reduced Questionnaire (15-20 Questions)

Proposed MVP set (18 questions):

1. Company name (short text)  
2. Industry (multiple choice)  
3. Company size (multiple choice)  
4. Operates in EU (yes/no)  
5. Has EU customers/users (yes/no)  
6. Uses AI systems (yes/no)  
7. Develops AI in-house (yes/no)  
8. Provides AI systems to clients (yes/no)  
9. Provides GPAI/foundation model (yes/no)  
10. Uses AI in high-risk domains: HR, credit, education, healthcare, law enforcement, critical infrastructure (multi-select)  
11. Uses biometric identification or emotion recognition (multi-select)  
12. Processes personal data (yes/no)  
13. Processes sensitive data or children data (multi-select)  
14. Uses profiling or automated decision-making (yes/no)  
15. Transfers data outside EU/EEA (yes/no)  
16. Uses non-EU cloud/AI providers (yes/no)  
17. Informs users when AI is used (yes/no)  
18. Has documented controls: DPIA, breach process, human oversight, vendor review, model documentation (multi-select)

## Checked Against Official PDFs (Targeted Review)

The questionnaire options below were verified and refined using these official sources:

- `commission_guidelines_ai_system_definition_AI_Act.pdf` (AI system definition: autonomy/adaptiveness/inference)
- `Guidelines_on_prohibited_artificial_intelligence_practices_AI_Act.pdf` (Article 5 prohibited practices)
- `Draft_Guidelines_high_risk_AI_Annex_III.pdf` (Annex III high-risk use cases)
- `OJ_L_202401689_EN_TXT.pdf` (AI Act core text, Annex III, transparency and emotion-recognition references)
- `CELEX_32016R0679_EN_TXT.pdf` (GDPR personal data, children data, DPIA context)
- `EDPB_guidelines_202007_controllerprocessor_final_en.pdf` (controller/processor/joint controller)
- `edpb_guidelines_202401_legitimateinterest_en.pdf` (legal basis detail)
- `edpb_recommendations_202001vo.2.0_supplementarymeasurestransferstools_en.pdf` (extra-EEA transfers and supplementary measures)
- `Code_of_Practice_GPAI_Transparency_Chapter.pdf` (GPAI transparency-related indicators)

## Recommended UI Fields (Checkboxes and Dropdowns)

### 1) Company and Scope (dropdowns)

- `industry` (dropdown): `saas`, `hr_tech`, `fintech`, `healthcare`, `education`, `manufacturing`, `public_sector`, `other`
- `company_size` (dropdown): `micro`, `small`, `medium`, `large`, `enterprise`
- `ai_role` (dropdown): `provider`, `deployer`, `importer_distributor`, `mixed_role`, `unknown`
- `gdpr_role` (dropdown): `controller`, `processor`, `joint_controller`, `mixed_role`, `unknown`
- `legal_basis_primary` (dropdown): `consent`, `contract`, `legal_obligation`, `vital_interest`, `public_task`, `legitimate_interest`, `unknown`

### 2) AI System Definition Signals (checkboxes)

Use checkboxes to support initial AI Act scope triage:

- `system_generates_predictions_recommendations_decisions_or_content`
- `system_operates_with_some_autonomy`
- `system_can_adapt_after_deployment`
- `uses_ml_logic_or_knowledge_based_inference`

### 3) High-Risk Annex III Signals (multi-checkbox)

Expand high-risk options to include all major Annex III areas:

- `employment_and_worker_management` (includes HR/recruitment)
- `education_and_vocational_training`
- `credit_scoring_or_access_to_essential_services`
- `healthcare_or_medical_triage`
- `law_enforcement`
- `migration_asylum_border_management`
- `justice_and_democratic_processes`
- `critical_infrastructure`

### 4) Prohibited-Practice Signals (multi-checkbox)

Add explicit Article 5-oriented indicators:

- `social_scoring`
- `subliminal_or_manipulative_techniques`
- `exploit_vulnerabilities_due_to_age_disability_or_social_economic_situation`
- `emotion_recognition_in_workplace_or_education`
- `remote_biometric_identification_in_public_spaces_for_law_enforcement`
- `sensitive_biometric_categorisation`

### 5) Transparency and GPAI Signals (checkboxes)

- `interacts_with_users_as_chatbot_or_virtual_agent`
- `generates_or_edits_synthetic_content`
- `possible_deepfake_or_simulated_media_output`
- `users_are_informed_ai_is_used`
- `provides_general_purpose_model`
- `fine_tunes_foundation_or_general_purpose_models`

### 6) GDPR/DPIA/Transfer Signals (checkboxes + dropdown)

- `processes_personal_data`
- `processes_special_categories_of_data`
- `processes_children_data`
- `uses_profiling_or_automated_decision_making`
- `large_scale_processing`
- `tracks_user_behavior`
- `transfers_data_outside_eea`
- `uses_non_eea_cloud_or_ai_provider`
- `transfer_mechanism` (dropdown): `adequacy_decision`, `sccs`, `bcrs`, `derogation`, `unknown`
- `supplementary_transfer_measures_in_place` (dropdown): `yes`, `partially`, `no`, `unknown`

### 7) Governance Readiness (multi-checkbox)

- `has_dpia_process`
- `has_data_breach_process`
- `has_data_subject_rights_process`
- `has_human_oversight_process`
- `has_model_documentation`
- `has_vendor_review_process`
- `has_ai_governance_policy`
- `has_staff_ai_literacy_training`

## ISSUE-011: Company Profile Database Fields (Initial List)

### Company basics
- `company_name`
- `industry`
- `company_size`
- `operates_in_eu`
- `has_eu_customers`

### AI profile
- `uses_ai_systems`
- `develops_ai_systems`
- `provides_ai_systems_to_clients`
- `provides_general_purpose_ai_model`
- `uses_third_party_ai_tools`

### AI use-case indicators
- `uses_ai_for_hr_or_recruitment`
- `uses_ai_for_credit_or_finance`
- `uses_ai_for_education`
- `uses_ai_for_healthcare`
- `uses_ai_for_law_enforcement`
- `uses_ai_for_critical_infrastructure`
- `uses_biometric_identification`
- `uses_emotion_recognition`
- `uses_automated_decision_making`

### GDPR/data processing indicators
- `processes_personal_data`
- `processes_sensitive_personal_data`
- `processes_children_data`
- `performs_large_scale_processing`
- `tracks_user_behavior`
- `transfers_data_outside_eu`
- `uses_non_eu_cloud_or_ai_provider`

### Governance readiness
- `has_dpo`
- `has_dpia_process`
- `has_data_breach_process`
- `has_ai_governance_policy`
- `has_model_documentation`
- `has_human_oversight_process`
- `has_vendor_review_process`
- `has_user_transparency_notice`

### Metadata
- `created_at`
- `updated_at`

### Suggested extension fields (after PDF review)
- `ai_role`
- `gdpr_role`
- `legal_basis_primary`
- `transfer_mechanism`
- `supplementary_transfer_measures_in_place`
- `has_data_subject_rights_process`
- `has_staff_ai_literacy_training`

## ISSUE-012: Mapping Answers to Regulatory Relevance

Core mapping rules:

- **GDPR active** if EU operation/customers or personal data processing is present.
- **AI Act active** if AI is used, developed, provided, or GPAI is provided.
- **High-risk AI candidate** if AI is used in HR/credit/education/healthcare/law enforcement/critical infrastructure.
- **DPIA candidate** if sensitive data, children data, large-scale processing, behavior tracking, or automated decision-making is present.
- **Data breach relevance** if personal data is processed and breach process is missing.
- **Transparency obligation candidate** if AI is used and user transparency notice is missing.
- **GPAI candidate** if the company provides general-purpose models.
- **International transfer candidate** if data leaves EU/EEA or non-EU providers are used.

Additional mapping notes from reviewed sources:

- `gdpr_role = processor/joint_controller` should trigger role-specific obligation review.
- `legal_basis_primary = legitimate_interest` should trigger balancing-test evidence check.
- `transfer_mechanism = unknown` or `supplementary_transfer_measures_in_place in {no, unknown}` should raise transfer-risk attention.
- `emotion_recognition_in_workplace_or_education = true` should raise prohibited-practice candidate with review-needed status.
- `migration_asylum_border_management` and `justice_and_democratic_processes` should feed high-risk candidate flags.

## ISSUE-013: Demo Company Profiles (Documentation)

### 1) Low-risk SaaS profile (demo)
- AI chatbot for support, no high-risk domain use.
- Processes personal data.
- No biometric/emotion recognition.
- Expected: GDPR active, AI Act active, medium exposure.

### 2) Higher-risk HR AI profile (demo)
- AI-based CV screening and candidate evaluation.
- Automated decision-making and sensitive data processing.
- Uses non-EU AI/cloud providers.
- Missing transparency notice.
- Expected: GDPR active, AI Act active, high-risk candidate, DPIA candidate, transparency candidate.

## Boundaries

The questionnaire and mapping layer:

- collects and normalizes inputs;
- identifies possible regulatory relevance and missing information.

It does not:

- provide definitive legal conclusions;
- replace legal counsel;
- run source monitoring, validation, or scraping.
