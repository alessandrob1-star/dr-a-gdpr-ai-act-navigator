"""Deterministic policy definitions based on keywords and regex patterns."""

from __future__ import annotations

import re

ITALIAN_LANGUAGE_MARKERS = [
    "come",
    "quale",
    "quali",
    "posso",
    "possiamo",
    "nostra",
    "nostro",
    "azienda",
    "società",
    "conformità",
    "conforme",
    "legge",
    "obblighi",
    "controlli",
    "rischi",
    "documentazione",
    "consulenza",
    "garantire",
    "aggirare",
    "nascondere",
    "falsificare",
    "dimmi",
    "dimme",
    "devo",
    "dobbiamo",
    "prima",
    "prime",
    "dopo",
    "poi",
    "faccio",
    "facciamo",
    "farle",
    "farli",
    "fatte",
    "fatti",
    "regola",
    "norma",
    "posto",
    "assicuri",
    "saremo",
    "conformi",
    "seguiamo",
    "passaggi",
    "perfettamente",
]

PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "developer mode",
    "system prompt",
    "reveal prompt",
    "jailbreak",
    "dan",
    "do anything now",
    "ignora le istruzioni precedenti",
    "ignora tutte le istruzioni precedenti",
    "modalità sviluppatore",
    "prompt di sistema",
    "rivela il prompt",
]

PROMPT_INJECTION_REGEX = [
    re.compile(
        r"\b(ignore|disregard)\b.{0,40}\b(instruction|system|policy|guard)\b", re.IGNORECASE
    ),
    re.compile(
        r"\b(show|reveal|print|leak)\b.{0,40}\b(system prompt|prompt|internal instruction)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(jailbreak|developer\s*mode|dan)\b", re.IGNORECASE),
    re.compile(
        r"\b(act as|roleplay as)\b.{0,60}\b(ignore|bypass|unrestricted|without rules|no rules)\b",
        re.IGNORECASE,
    ),
]

REGULATORY_EVASION_KEYWORDS = [
    "bypass ai act",
    "bypass gdpr",
    "evade ai act",
    "evade gdpr",
    "circumvent compliance",
    "skip controls",
    "avoid regulatory checks",
    "elude audit",
    "break the law",
    "violate the law",
    "defraud the law",
    "ignore the law",
    "appear compliant",
    "appearing compliant",
    "appear regular",
    "appearing regular",
    "look compliant before",
    "appear compliant before",
    "look compliant",
    "seem compliant",
    "stay under the radar",
    "without disclosing the gaps",
    "hide gaps from an auditor",
    "conceal gaps from an auditor",
    "aggirare l'ai act",
    "aggirare il gdpr",
    "eludere i controlli",
    "saltare i controlli",
    "violare la legge",
    "ignorare la legge",
    "sembrare conforme",
    "apparire conforme",
    "sembrare a norma",
    "apparire a norma",
    "apparire in regola",
    "sembrare in regola",
    "risultare conforme",
    "risultare a norma",
    "farlo risultare conforme",
    "nascondere le lacune a un revisore",
]

REGULATORY_EVASION_REGEX = [
    re.compile(
        r"\b(bypass|evade|circumvent|elude|skip)\b.{0,40}\b(ai\s*act|gdpr|audit|regulat|compliance|control)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bavoid\s+(?:(?:an?|the)\s+audit|being\s+audited|regulatory\s+checks?)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bavoid\s+audit\b(?!\s+(?:findings?|issues?|problems?)\b)", re.IGNORECASE),
    re.compile(
        r"\b(how\s+(?:can|do|to)|help\s+me)\b.{0,50}\b(break|violate|defraud|ignore|evade)\b.{0,30}\b(law|regulat|ai\s*act|gdpr)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(slowly|delay|postpone|stall|buy\s+time)\b.{0,100}"
        r"\b(appear(?:ing)?|look(?:ing)?|seem(?:ing)?|present(?:ing)?)\b.{0,30}"
        r"\b(regular|compliant|lawful|legal)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(appear(?:ing)?|look(?:ing)?|seem(?:ing)?|present(?:ing)?)\b.{0,45}"
        r"\b(regular|compliant|lawful|legal)\b.{0,80}"
        r"\b(before|without|while\s+not)\b.{0,60}\b(implement|do(?:ing)?|fix|complete|control|gap)\w*",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(appear(?:ing)?|look(?:ing)?|seem(?:ing)?)\b.{0,35}"
        r"\b(regular|compliant|lawful|legal)\b.{0,80}\b(later|afterwards|then)\b.{0,50}"
        r"\b(fix|regulari[sz]e|implement|complete)\w*",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(delay|postpone|defer|skip)\b.{0,70}\b(without|avoid)\b.{0,30}"
        r"\b(disclos|tell|inform|report)\w*\b.{0,50}\b(auditor|regulator|authority)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(hide|conceal|withhold)\w*\b.{0,40}\b(gap|control|evidence|issue)\w*"
        r"\b.{0,40}\b(auditor|regulator|authority)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(aggirare|eludere|saltare)\b.{0,50}\b(ai\s*act|gdpr|audit|controll|conformit|normativ)",
        re.IGNORECASE,
    ),
    re.compile(r"\bevitare\s+(?:(?:un |l['’])audit|(?:i\s+)?controlli normativi)\b", re.IGNORECASE),
    re.compile(
        r"\b(sembrare|apparire|risultare)\b.{0,35}"
        r"\b(conforme|regolare|in\s+regola|a\s+norma)\b.{0,90}"
        r"\b(prima|senza)\b.{0,70}\b(implement|fare|complet|sistem|regolarizz|controll)\w*",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(prima)\b.{0,70}\b(poi|dopo)\b.{0,50}\b(regolarizz|sistem|implement|complet)\w*"
        r"|"
        r"\b(poi|dopo)\b.{0,50}\b(regolarizz|sistem|implement|complet)\w*.{0,70}\b(prima)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(rallentare|ritardare|rinviare|prendere\s+tempo)\b.{0,100}\b(sembrare|apparire|risultare)\b.{0,35}\b(conforme|regolare|a\s+norma)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(nascondere|occultare|omettere)\b.{0,50}\b(lacun|problem|controll|prov)\w*.{0,50}\b(revisore|autorità|regolatore|audit)",
        re.IGNORECASE,
    ),
]

FRAUD_KEYWORDS = [
    "fake certification",
    "fake audit",
    "forge compliance",
    "falsify documentation",
    "invent evidence",
    "fabricate proof",
    "counterfeit certificate",
    "falsa certificazione",
    "falsificare documenti",
    "inventare prove",
    "fabbricare prove",
    "simulare un audit",
]

FRAUD_REGEX = [
    re.compile(
        r"\b(fake|forg\w*|falsif\w*|fabricat\w*|invent\w*|counterfeit\w*)\b.{0,50}\b(audit|certificate|certification|document|evidence|proof|compliance)\w*",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(falsific|invent|fabbric|contraff|simul)\w*\b.{0,45}\b(audit|certificat|document|prov|conformit)\w*",
        re.IGNORECASE,
    ),
]

LEGAL_ADVICE_BLOCK_REGEX = [
    re.compile(r"\b(am i compliant|are we compliant|is my company compliant)\b", re.IGNORECASE),
    re.compile(
        r"\b(guarantee|certify|confirm|assure)\b.{0,60}\b(comply|complies|compliant|compliance|lawful|legal)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(does|will|would)\b.{0,40}\b(guarantee|ensure)\b.{0,40}\b(compliance|compliant)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(write|draft|provide)\b.{0,40}\b(legal advice|legal opinion|formal legal opinion)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(sono|siamo|la mia azienda è|la nostra azienda è)\b.{0,30}\b(conforme|a norma)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(garant|certific|conferm|assicur)\w*\b.{0,70}\b(conform\w*|legal\w*|a norma)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(scrivere|redigere|fornire)\b.{0,40}\b(consulenza legale|parere legale)", re.IGNORECASE
    ),
]

OUTPUT_UNSAFE_REGEX = [
    re.compile(
        r"\b(how to|steps to|way to)\b.{0,60}\b(bypass|evade|circumvent)\b.{0,40}\b(ai\s*act|gdpr|audit|compliance)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(fake|forg\w*|falsif\w*|fabricat\w*|invent\w*)\b.{0,50}\b(audit|certificate|evidence|proof|documentation)\w*",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(come|passaggi per|modo per)\b.{0,60}\b(aggirare|eludere)\b.{0,40}\b(ai\s*act|gdpr|audit|conformit)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(falsific|invent|fabbric)\w*\b.{0,40}\b(audit|certificat|prov|documentazion)",
        re.IGNORECASE,
    ),
]
