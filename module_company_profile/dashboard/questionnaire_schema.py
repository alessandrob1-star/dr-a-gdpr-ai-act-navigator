"""Shared questionnaire schema for dashboard adapters."""

from __future__ import annotations

from typing import Literal, NamedTuple

QuestionType = Literal["text", "textarea", "radio", "checkbox"]


class Question(NamedTuple):
    name: str
    label: str
    type: QuestionType
    options: tuple[tuple[str, str], ...] = ()


class Section(NamedTuple):
    title: str
    questions: tuple[Question, ...]


QUESTIONNAIRE_NAME = "company_gdpr_ai_act_initial_assessment"
QUESTIONNAIRE_VERSION = "1.0"

QUESTIONNAIRE_SCHEMA: tuple[Section, ...] = (
    Section(
        "1. Dati azienda",
        (
            Question("company_name", "Nome azienda", "text"),
            Question("contact_email", "Email di riferimento", "text"),
            Question(
                "industry",
                "Settore principale",
                "radio",
                (
                    ("software_saas", "Software / SaaS"),
                    ("hr_recruiting", "HR / recruiting / gestione dipendenti"),
                    ("fintech", "Fintech / credito / assicurazioni"),
                    ("healthcare", "Sanita' / medtech"),
                    ("education", "Educazione / formazione"),
                    ("manufacturing", "Industria / manifattura"),
                    ("public_sector", "PA o fornitori della PA"),
                    ("other", "Altro"),
                ),
            ),
            Question(
                "company_size",
                "Dimensione aziendale",
                "radio",
                (
                    ("micro", "1-9 persone"),
                    ("small", "10-49 persone"),
                    ("medium", "50-249 persone"),
                    ("large", "250+ persone"),
                ),
            ),
            Question(
                "eu_presence",
                "L'azienda opera o vende nell'Unione Europea?",
                "checkbox",
                (
                    ("eu_company", "Ha sede nell'UE"),
                    ("eu_customers", "Ha clienti o utenti nell'UE"),
                    ("eu_market", "Offre servizi o prodotti al mercato UE"),
                    ("no_eu_presence", "Non opera nel mercato UE"),
                    ("unknown", "Non lo so"),
                ),
            ),
        ),
    ),
    Section(
        "2. Uso dell'intelligenza artificiale",
        (
            Question(
                "ai_usage",
                "L'azienda usa o fornisce AI?",
                "checkbox",
                (
                    ("internal_ai", "Usa AI solo internamente"),
                    ("customer_product_ai", "Integra AI in prodotti o servizi per clienti"),
                    ("in_house_ai", "Sviluppa sistemi AI propri"),
                    ("ai_provider", "Fornisce sistemi AI ad altre aziende"),
                    ("gpai", "Usa, modifica o fornisce modelli generativi/foundation model"),
                    ("no_ai", "Non usa AI"),
                    ("unknown", "Non lo so"),
                ),
            ),
            Question(
                "ai_functions",
                "Che cosa fa il sistema AI?",
                "checkbox",
                (
                    ("content_generation", "Produce testi, immagini, audio, video o codice"),
                    ("recommendations", "Fa raccomandazioni o suggerimenti"),
                    ("classification", "Classifica persone, documenti, clienti o rischi"),
                    ("scoring", "Assegna punteggi o priorita'"),
                    ("decision_support", "Supporta decisioni su persone fisiche"),
                    ("automated_decision", "Prende decisioni automatiche senza revisione umana"),
                    ("not_applicable", "Non applicabile"),
                ),
            ),
            Question(
                "ai_notice",
                "Gli utenti sanno quando stanno interagendo con AI?",
                "radio",
                (
                    ("clear", "Si, e' indicato chiaramente"),
                    ("not_prominent", "Si, ma l'informazione non e' molto visibile"),
                    ("no_notice", "No, non e' indicato chiaramente"),
                    ("not_applicable", "Non applicabile"),
                    ("unknown", "Non lo so"),
                ),
            ),
        ),
    ),
    Section(
        "3. Ambiti sensibili",
        (
            Question(
                "sensitive_domains",
                "L'AI viene usata in uno di questi ambiti?",
                "checkbox",
                (
                    ("recruiting", "Selezione personale, CV screening, candidati"),
                    ("workers", "Gestione dipendenti o valutazione performance"),
                    ("education", "Educazione, esami, ammissioni, valutazioni studenti"),
                    ("credit", "Credito, assicurazioni o accesso a servizi essenziali"),
                    ("healthcare", "Sanita', diagnosi, triage o decisioni mediche"),
                    ("critical_infrastructure", "Infrastrutture critiche o sicurezza operativa"),
                    (
                        "law_migration_justice",
                        "Forze dell'ordine, migrazione, giustizia o processi democratici",
                    ),
                    ("none", "Nessuno di questi"),
                    ("unknown", "Non lo so"),
                ),
            ),
            Question(
                "delicate_ai_practices",
                "Il prodotto include pratiche AI particolarmente delicate?",
                "checkbox",
                (
                    ("biometric_recognition", "Riconoscimento biometrico"),
                    ("emotion_recognition", "Riconoscimento delle emozioni"),
                    ("social_scoring", "Valutazione sociale o ranking delle persone"),
                    (
                        "manipulative_techniques",
                        "Tecniche manipolative o persuasive non trasparenti",
                    ),
                    ("sensitive_traits", "Analisi di caratteristiche sensibili delle persone"),
                    ("none", "Nessuna di queste"),
                    ("unknown", "Non lo so"),
                ),
            ),
        ),
    ),
    Section(
        "4. Dati personali",
        (
            Question(
                "personal_data",
                "L'azienda tratta dati personali?",
                "checkbox",
                (
                    ("customers_users", "Dati di clienti o utenti"),
                    ("employees_candidates", "Dati di dipendenti o candidati"),
                    ("contact_account", "Dati di contatto o account"),
                    ("tracking_analytics", "Dati di utilizzo, tracciamento o analytics"),
                    ("sensitive_data", "Dati sanitari, biometrici o altri dati sensibili"),
                    ("children_data", "Dati di minori"),
                    ("no_personal_data", "No, non tratta dati personali"),
                    ("unknown", "Non lo so"),
                ),
            ),
            Question(
                "profiling_decisions",
                "L'azienda usa dati personali per profilazione o decisioni automatiche?",
                "checkbox",
                (
                    ("profiling", "Profilazione o segmentazione utenti/clienti"),
                    ("personalized_recommendations", "Raccomandazioni personalizzate"),
                    (
                        "significant_automated_decisions",
                        "Decisioni automatiche con effetti importanti sulle persone",
                    ),
                    ("human_review_decision_support", "Supporto decisionale con revisione umana"),
                    ("no", "No"),
                    ("unknown", "Non lo so"),
                ),
            ),
            Question(
                "privacy_role",
                "Qual e' il ruolo privacy principale dell'azienda?",
                "radio",
                (
                    ("controller", "Titolare del trattamento"),
                    ("processor", "Responsabile del trattamento per conto di clienti"),
                    ("joint_controller", "Contitolare con altri soggetti"),
                    ("mixed", "Ruolo misto"),
                    ("unknown", "Non lo so"),
                ),
            ),
        ),
    ),
    Section(
        "5. Cloud, fornitori e controlli",
        (
            Question(
                "extra_eea_transfers",
                "I dati personali vengono trasferiti fuori da UE/SEE?",
                "radio",
                (("yes", "Si"), ("no", "No"), ("unknown", "Non lo so")),
            ),
            Question(
                "extra_eea_providers",
                "L'azienda usa fornitori cloud o AI extra UE/SEE?",
                "checkbox",
                (
                    ("cloud_hosting", "Cloud hosting"),
                    ("ai_api_models", "API o modelli AI"),
                    ("internal_saas", "Strumenti SaaS usati internamente"),
                    ("no", "No"),
                    ("unknown", "Non lo so"),
                ),
            ),
            Question(
                "controls",
                "Quali controlli o documenti esistono gia'?",
                "checkbox",
                (
                    ("privacy_policy", "Privacy policy aggiornata"),
                    ("records_processing", "Registro dei trattamenti"),
                    ("dpo_privacy_owner", "DPO o referente privacy nominato"),
                    ("dpia_process", "Processo DPIA / valutazione impatto privacy"),
                    ("breach_process", "Processo gestione data breach"),
                    ("data_subject_rights", "Processo gestione diritti degli interessati"),
                    ("vendor_review", "Revisione fornitori e subfornitori"),
                    ("ai_documentation", "Documentazione del sistema AI"),
                    ("human_oversight", "Controllo umano sugli output AI"),
                    ("ai_policy", "Policy interna sull'uso dell'AI"),
                    ("training", "Formazione interna su AI o privacy"),
                    ("none", "Nessuno di questi"),
                    ("unknown", "Non lo so"),
                ),
            ),
            Question(
                "dashboard_priority",
                "Cosa vuoi ottenere per primo dalla valutazione?",
                "radio",
                (
                    ("applicable_rules", "Capire quali norme si applicano all'azienda"),
                    ("main_risks", "Capire quali sono i rischi principali"),
                    ("missing_controls", "Sapere quali documenti o controlli mancano"),
                    ("external_evidence", "Preparare materiale per clienti, investitori o partner"),
                    ("gdpr_ai_act_review", "Prepararsi a una revisione GDPR o AI Act"),
                    ("action_plan", "Costruire un piano operativo con prossime azioni"),
                ),
            ),
            Question("notes", "Note libere opzionali", "textarea"),
        ),
    ),
)

EXCLUSIVE_CHECKBOX_VALUES: dict[str, frozenset[str]] = {
    "eu_presence": frozenset({"no_eu_presence", "unknown"}),
    "ai_usage": frozenset({"no_ai", "unknown"}),
    "ai_functions": frozenset({"not_applicable"}),
    "sensitive_domains": frozenset({"none", "unknown"}),
    "delicate_ai_practices": frozenset({"none", "unknown"}),
    "personal_data": frozenset({"no_personal_data", "unknown"}),
    "profiling_decisions": frozenset({"no", "unknown"}),
    "extra_eea_providers": frozenset({"no", "unknown"}),
    "controls": frozenset({"none", "unknown"}),
}
