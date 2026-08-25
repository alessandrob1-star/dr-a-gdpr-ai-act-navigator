"""Standardized user-facing policy messages."""

INPUT_BLOCK_MESSAGES = {
    "en": {
        "prompt_injection": (
            "Policy Agent block: I cannot follow requests to bypass system instructions "
            "or reveal internal prompts. Ask a question about AI Act "
            "or GDPR compliance instead."
        ),
        "regulatory_evasion": (
            "Policy Agent block: I cannot help evade the AI Act, GDPR, audits, or "
            "regulatory controls. I can help build a lawful phased compliance plan instead."
        ),
        "fraud": (
            "Policy Agent block: I cannot help fabricate evidence, falsify documentation, "
            "or fake an audit or certification. I can help prepare legitimate compliance evidence."
        ),
        "legal_advice": (
            "Legal-information boundary: this application provides general compliance "
            "information, not legal advice, and cannot guarantee that an organization is "
            "legally compliant. A legal determination requires qualified legal counsel."
        ),
        "off_topic": (
            "This Policy Agent evaluates English or Italian questions about "
            "AI Act, GDPR, governance, risks, controls, and compliance documentation."
        ),
    },
    "it": {
        "prompt_injection": (
            "Blocco del Policy Agent: non posso seguire richieste per aggirare le istruzioni "
            "di sistema o rivelare prompt interni. Puoi invece fare una domanda sull'AI Act "
            "o sulla conformità al GDPR."
        ),
        "regulatory_evasion": (
            "Blocco del Policy Agent: non posso aiutarti ad aggirare l'AI Act, il GDPR, "
            "gli audit o i controlli normativi. Posso invece aiutarti a preparare un piano "
            "graduale e conforme alla legge."
        ),
        "fraud": (
            "Blocco del Policy Agent: non posso aiutarti a inventare prove, falsificare "
            "documenti o simulare audit o certificazioni. Posso aiutarti a preparare prove "
            "di conformità autentiche."
        ),
        "legal_advice": (
            "Limite delle informazioni legali: questa applicazione fornisce informazioni "
            "generali sulla conformità, non consulenza legale, e non può garantire che "
            "un'organizzazione sia legalmente conforme. La valutazione richiede un legale qualificato."
        ),
        "off_topic": (
            "Questo Policy Agent valuta domande in inglese o italiano su AI Act, GDPR, "
            "governance, rischi, controlli e documentazione di conformità."
        ),
    },
}

OUTPUT_BLOCK_MESSAGES = {
    "en": (
        "I cannot provide that response. I can only provide general AI compliance information, "
        "not legal advice, and I cannot assist with regulatory evasion, fraud, or unsupported claims."
    ),
    "it": (
        "Non posso fornire questa risposta. Posso offrire solo informazioni generali sulla "
        "conformità dell'IA, non consulenza legale, e non posso aiutare con elusione normativa, "
        "frode o affermazioni non supportate."
    ),
}
