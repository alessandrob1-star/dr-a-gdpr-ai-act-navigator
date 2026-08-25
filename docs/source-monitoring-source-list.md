# Source Monitoring Operational List

Local working document.
Do not publish to GitHub without explicit approval.

This document lists the first operational sources for the Source Monitoring and Validation Agent.

## Source Categories

- `official_law`: final legal text or official publication.
- `official_api`: official API or webservice.
- `official_guidance`: official guidance or implementation page.
- `official_draft`: official draft, proposal, consultation, or political agreement.
- `trusted_news`: trusted but non-official news source.
- `legal_analysis`: expert legal commentary or academic/professional analysis.

## Operational Source List

| Source | URL / File | Category | Access Type | Agent Use | Validation Role | Priority | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EUR-Lex Official Journal | https://eur-lex.europa.eu/oj/direct-access.html | official_law | Website | Check official publication of EU legal acts | Strongest confirmation source | High | Final publication source for EU legal acts. |
| EUR-Lex Webservice | https://eur-lex.europa.eu/content/help/data-reuse/webservice.html | official_api | SOAP webservice, registration required | Query EUR-Lex directly for acts and metadata | Official verification source | High | Registration submitted; access pending administrator approval. |
| EUR-Lex stable links | https://eur-lex.europa.eu/content/help/data-reuse/linking.html | official_guidance | Public webpage | Store permanent links to official legal documents | Stable reference support | High | Useful fallback while API access is pending. |
| GDPR official text | official-documents/CELEX_32016R0679_EN_TXT.pdf | official_law | Local PDF / EUR-Lex | Core GDPR knowledge base | Official legal source | High | Main GDPR legal text. |
| EU AI Act official text | official-documents/OJ_L_202401689_EN_TXT.pdf | official_law | Local PDF / Official Journal | Core AI Act knowledge base | Official legal source | High | Main AI Act legal text. |
| EU AI Act ELI link | https://eur-lex.europa.eu/eli/reg/2024/1689/oj | official_law | Stable ELI URL | Permanent reference to AI Act | Official publication confirmation | High | CELEX: 32024R1689. |
| European AI Office | https://digital-strategy.ec.europa.eu/en/policies/ai-office | official_guidance | Public webpage | Monitor AI Act implementation, GPAI, guidance and compliance updates | Official institutional source | High | Important for AI Act implementation and GPAI. |
| European Commission AI Act page | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai | official_guidance | Public webpage | Monitor AI Act timeline, risk approach and implementation updates | Official policy source | High | Useful for deadlines and implementation context. |
| Digital Omnibus AI Regulation Proposal | https://digital-strategy.ec.europa.eu/en/library/digital-omnibus-ai-regulation-proposal | official_draft | Public webpage | Track proposed amendments to AI regulation | Draft/proposal validation | High | Treat as official proposal, not final law. |
| EU agreement to simplify AI rules | https://digital-strategy.ec.europa.eu/en/news/eu-agrees-simplify-ai-rules-boost-innovation-and-ban-nudification-apps-protect-citizens | official_draft | Public webpage | Track political agreement about AI rule changes | Political agreement validation | High | Useful example of official non-final regulatory progress. |
| EDPB Guidelines page | https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en | official_guidance | Public webpage | Monitor GDPR guidance and recommendations | Official GDPR guidance source | High | Main EDPB guidance index. |
| EDPB automated decision-making and profiling | https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/automated-decision-making-and-profiling_en | official_guidance | Public webpage | Support profiling and automated decision-making detection | Official GDPR interpretation | High | Important for AI systems evaluating people. |
| EDPB DPIA guidance | https://ec.europa.eu/newsroom/article29/items/611236/en | official_guidance | Public webpage / PDF | Support DPIA risk detection | Official GDPR guidance | High | Useful for high-risk processing. |
| EDPB personal data breach guidance | Guidelines 9/2022 on personal data breach notification under GDPR | official_guidance | Public webpage / PDF | Support breach and incident-response risk flags | Official GDPR guidance | High | Useful for security and data breach obligations. |
| EDPB international transfer recommendations | official-documents/edpb_recommendations_202001vo.2.0_supplementarymeasurestransferstools_en.pdf | official_guidance | Local PDF | Detect cloud, LLM provider and third-country transfer risks | Official GDPR recommendation | High | Important for non-EU providers and AI APIs. |
| Commission AI system definition guidelines | official-documents/commission_guidelines_ai_system_definition_AI_Act.pdf | official_guidance | Local PDF | Determine whether the product qualifies as an AI system | Official AI Act guidance | High | First filter for AI Act applicability. |
| Commission prohibited AI practices guidelines | official-documents/Guidelines_on_prohibited_artificial_intelligence_practices_AI_Act.pdf | official_guidance | Local PDF | Detect prohibited AI practice indicators | Official AI Act guidance | High | Critical for highest-risk alerts. |
| Draft high-risk AI general principles | official-documents/Draft_Guidelines_high_risk_AI_general_principles.pdf | official_draft | Local PDF | Support high-risk AI classification logic | Official draft guidance | High | Treat as draft, not final guidance. |
| Draft high-risk AI Annex I | official-documents/Draft_Guidelines_high_risk_AI_Annex_I.pdf | official_draft | Local PDF | Support high-risk AI classification logic | Official draft guidance | High | Treat as draft, not final guidance. |
| Draft high-risk AI Annex III | official-documents/Draft_Guidelines_high_risk_AI_Annex_III.pdf | official_draft | Local PDF | Support high-risk AI use-case detection | Official draft guidance | High | Relevant to employment, education, credit, justice and other high-risk domains. |
| AI Act transparency obligations guidance | official-documents/Guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_AI_systems_under_Article_50_of_the_AI_Act_lz68oNH813eIDWoquXwCo7eEUc_128275.pdf | official_guidance | Local PDF | Detect transparency obligations | Official AI Act guidance | High | Relevant for chatbots, deepfakes and AI-generated content. |
| GPAI Code of Practice - Transparency | official-documents/Code_of_Practice_GPAI_Transparency_Chapter.pdf | official_guidance | Local PDF | Support GPAI transparency checks | Official implementation guidance | High | Useful for LLM/foundation model cases. |
| GPAI Code of Practice - Safety and Security | official-documents/Code_of_Practice_GPAI_Safety_and_Security_Chapter.pdf | official_guidance | Local PDF | Support GPAI safety/security checks | Official implementation guidance | High | Useful for model providers and advanced AI use cases. |
| GPAI Code of Practice - Copyright | official-documents/Code_of_Practice_GPAI_Copyright_Chapter.pdf | official_guidance | Local PDF | Support copyright and training data concerns | Official implementation guidance | Medium-High | Relevant for GPAI providers and training data governance. |
| IAPP News / AI Governance | https://iapp.org/news/ | trusted_news | Monitored webpage | Create early warnings for privacy and AI governance developments | Warning source only | High | Must be validated against official sources. |
| Euractiv Tech | https://www.euractiv.com/section/tech/ | trusted_news | Monitored webpage / RSS candidate | Create early warnings for EU tech and AI policy | Warning source only | Medium-High | Useful for EU policy developments. |
| Future of Privacy Forum AI | https://fpf.org/fpf-ai/ | trusted_news | Monitored webpage | Create early warnings and policy context | Warning source only | Medium | Broader/global perspective, not EU-only. |
| European Law Blog AI section | https://europeanlawblog.eu/category/artificial-intelligence/ | legal_analysis | Monitored webpage / RSS likely | Create legal analysis signals | Analysis source only | Medium | Useful for expert interpretation, not official validation. |

## MVP Monitoring Rule

The first MVP should not monitor every source automatically.

Recommended MVP subset:

1. EUR-Lex / Official Journal;
2. European AI Office;
3. EDPB Guidelines page;
4. IAPP News;
5. Euractiv Tech.

This is enough to demonstrate the workflow:

- trusted news creates a warning;
- official sources are checked for confirmation;
- draft/proposal sources increase reliability but do not become final law;
- Official Journal / EUR-Lex publication provides the strongest confirmation.
