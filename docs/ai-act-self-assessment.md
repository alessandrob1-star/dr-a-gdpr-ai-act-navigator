# AI Act Self-Assessment of Dr. G.D.P.R. & AI Act navigator

This tool helps SMEs triage their obligations under the EU AI Act (Regulation
(EU) 2024/1689) and the GDPR (Regulation (EU) 2016/679). Because it is itself an
AI-enabled system, we apply the AI Act's own methodology to it. This document is
a good-faith engineering self-assessment, not a legal conclusion or a conformity
declaration.

> Scope note: this assessment covers the prototype as shipped in this
> repository (a local, single-user demo). A production deployment would require
> re-assessment against its actual context of use.

## 1. System description

| Attribute | Value |
| --- | --- |
| System | Dr. G.D.P.R. & AI Act navigator (questionnaire → deterministic risk profile + "Dr. A" assistant) |
| AI component | "Dr. A", powered by `gpt-5.6-sol` through the official OpenAI API |
| Role of the AI | Explains an already-computed compliance context in natural language |
| Runtime boundaries | Company Profile, Regulatory Monitoring, Regulatory Matching, and Dr. A agents plus a separate deterministic Policy Agent |
| Source of truth | Deterministic Python rules (`module_company_profile/memory_agent` and `module_web_scraping`), not the model |
| Users | An SME's own staff, reviewing their own company profile |
| Autonomy | None. The system produces information; humans make all decisions |
| Data location | Local by default; company answers stay on the user's machine |

## 2. Risk classification under the AI Act

The AI Act assigns systems to tiers. We walk each tier and record why it does or
does not apply.

### Prohibited practices — Article 5: **Not applicable**
The system performs none of the prohibited practices (no social scoring, no
untargeted facial scraping, no biometric categorisation, no manipulation or
exploitation of vulnerabilities). It only presents regulatory information about
the user's own company.

### High-risk — Article 6 and Annex III: **Not classified as high-risk**
Annex III lists specific high-risk purposes (biometrics, critical
infrastructure, education scoring, employment decisions about individuals,
essential services eligibility, law enforcement, migration, justice). Dr. A does
**not** make or support decisions about individual people in any of these
domains. It is an informational aid about *regulation*, used by a company about
*itself*. Under Article 6(3), a system is not high-risk where it performs a
narrow procedural or purely preparatory/informational task and does not
materially influence the outcome of decision-making — which matches an
explain-the-context assistant sitting on top of deterministic rules.

### Limited-risk / transparency — Article 50: **Applicable**
Dr. A is an AI system that interacts with natural persons, so the Article 50
transparency obligation applies: users must be informed they are interacting
with an AI system. We meet this (see §3).

### Minimal-risk: **Baseline**
Absent the above, the system sits in the minimal-risk tier, for which the AI Act
imposes no mandatory obligations but encourages voluntary codes of conduct
(Article 95). We nonetheless adopt several high-risk-style controls voluntarily
(see §4).

**Conclusion:** limited-risk (transparency obligations apply), not high-risk,
not prohibited.

## 3. Article 50 transparency obligations — how we meet them

| Obligation | Implementation in this repository |
| --- | --- |
| Inform users they interact with an AI | The assistant is presented as "Dr. A", an OpenAI-powered AI assistant, in the dashboard UI and README |
| Do not present AI output as legal fact | A persistent disclaimer states the tool supports triage and does not provide legal advice (README top banner; dashboard) |
| Distinguish AI explanation from authoritative source | The deterministic layer computes applicability and scores; Dr. A only explains that context and cites supplied evidence, it does not create classifications |

## 4. Voluntary controls (beyond what limited-risk requires)

We adopt several practices drawn from the high-risk obligation set (Articles
9–15) as good responsible-AI hygiene, even though they are not mandatory for a
limited-risk system.

| AI Act theme | Article(s) | Voluntary control in this project |
| --- | --- | --- |
| Human oversight | Art. 14 | Human-in-the-loop by design: the tool never acts, only informs; all decisions remain with the user |
| Accuracy & robustness | Art. 15 | Deterministic rules are the source of truth and are unit-tested; the model cannot override the classification |
| Risk management | Art. 9 | An input **and** output guardrail (`policy_agent`) blocks evasion, fraud, prompt injection, and requests for guaranteed legal conclusions, in English and Italian |
| Testing & validation | Art. 9 | A deterministic guardrail golden set is evaluated in CI (see below) |
| Transparency to users | Art. 13, 50 | Evidence links point to specific official EUR-Lex/EDPB/Commission sources; see the citation registry (`module_web_scraping/citations.py`) |
| Record-keeping | Art. 12 | Assessment snapshots are persisted locally and are comparable across time |
| Data governance | Art. 10 | Local-by-default processing keeps company answers on the user's machine |

### Measured guardrail performance

The guardrail controls are not just claimed, they are measured. The committed
golden set (`policy_agent/eval/golden_set.json`) is scored on every CI run by
`policy_agent/tests/test_guardrail_eval.py`:

- **32 / 32 adversarial cases blocked (100%)** — regulatory evasion, fraud,
  prompt injection, legal-guarantee requests, and unsafe output.
- **0 / 20 benign compliance questions incorrectly blocked (0% false-block).**
- Coverage spans **English and Italian**.

Reproduce locally:

```bash
python -m policy_agent.eval
```

## 5. Residual limitations (honest disclosure)

- The model is probabilistic. Segments receive automated policy, citation, and
  objective grounding checks, but the complete legal meaning of free text still
  requires human review.
- The guardrail golden set is a curated sample, not exhaustive adversarial
  coverage.
- Live regulatory collection covers a curated source list, not every EU or
  national authority.
- This assessment is an engineering exercise; it is not legal advice and does
  not constitute an AI Act conformity assessment.

## 6. Re-assessment triggers

Re-run this assessment if any of the following change: the system starts
supporting decisions about individuals (possible Annex III relevance); it is
deployed as a multi-tenant hosted service; the model is given tools that take
actions; or new obligations under the AI Act implementation timeline take
effect.

---

_Last reviewed: 2026-07-16. Legal instruments referenced: Regulation (EU)
2024/1689 (AI Act); Regulation (EU) 2016/679 (GDPR)._
