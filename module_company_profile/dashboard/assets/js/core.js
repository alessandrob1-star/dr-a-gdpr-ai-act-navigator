let currentContext = null;
const chatHistory = [];

// -----------------------------------------------------------------------
// Application state and stable DOM references
// -----------------------------------------------------------------------
const summary = document.getElementById("summary");
const warnings = document.getElementById("warnings");
const events = document.getElementById("events");
const news = document.getElementById("news");
const earlyWarnings = document.getElementById("earlyWarnings");
const timeline = document.getElementById("timeline");
const feedNotice = document.getElementById("feedNotice");
const chatLog = document.getElementById("chatLog");
const chatInput = document.getElementById("chatInput");
const serverStatus = document.getElementById("serverStatus");
const questionnaireForm = document.getElementById("questionnaireForm");
const questionnaireFile = document.getElementById("questionnaireFile");
const questionnaireFileName = document.getElementById("questionnaireFileName");
const languageFlag = document.getElementById("languageFlag");
let currentQuestionnairePayload = null;

const languageFlagCodes = {
  sq: "al", bg: "bg", cs: "cz", da: "dk", de: "de",
  et: "ee", el: "gr", en: "gb", es: "es", fr: "fr",
  ga: "ie", hr: "hr", it: "it", lv: "lv", lt: "lt",
  hu: "hu", mt: "mt", nl: "nl", pl: "pl", pt: "pt",
  ro: "ro", sk: "sk", sl: "si", fi: "fi", sv: "se"
};

function updateLanguageFlag(languageCode) {
  const option = document.querySelector(`#languageSelect option[value="${languageCode}"]`);
  const languageName = option?.textContent || languageCode;
  const countryCode = languageFlagCodes[languageCode] || "gb";
  languageFlag.style.backgroundImage = `url("assets/flags/${countryCode}.svg")`;
  languageFlag.setAttribute("aria-label", `${languageName} flag`);
  languageFlag.title = languageName;
}

function updateQuestionnaireFileLabel() {
  const selectedFile = questionnaireFile.files[0];
  questionnaireFileName.textContent = selectedFile ? selectedFile.name : t("no_file_selected");
}

questionnaireFile.addEventListener("change", updateQuestionnaireFileLabel);

// -----------------------------------------------------------------------
// Questionnaire schema
// Questions are data-driven so flags can be rendered, loaded, and exported
// through the same structure without duplicating form logic.
// -----------------------------------------------------------------------
const questionnaireSchema = [
  {
    title: "1. Dati azienda",
    questions: [
      { name: "company_name", label: "Nome azienda", type: "text" },
      { name: "contact_email", label: "Email di riferimento", type: "text" },
      {
        name: "industry", label: "Settore principale", type: "radio", options: [
          ["software_saas", "Software / SaaS"],
          ["hr_recruiting", "HR / recruiting / gestione dipendenti"],
          ["fintech", "Fintech / credito / assicurazioni"],
          ["healthcare", "Sanita' / medtech"],
          ["education", "Educazione / formazione"],
          ["manufacturing", "Industria / manifattura"],
          ["public_sector", "PA o fornitori della PA"],
          ["other", "Altro"]
        ]
      },
      {
        name: "company_size", label: "Dimensione aziendale", type: "radio", options: [
          ["micro", "1-9 persone"],
          ["small", "10-49 persone"],
          ["medium", "50-249 persone"],
          ["large", "250+ persone"]
        ]
      },
      {
        name: "eu_presence", label: "L'azienda opera o vende nell'Unione Europea?", type: "checkbox", options: [
          ["eu_company", "Ha sede nell'UE"],
          ["eu_customers", "Ha clienti o utenti nell'UE"],
          ["eu_market", "Offre servizi o prodotti al mercato UE"],
          ["no_eu_presence", "Non opera nel mercato UE"],
          ["unknown", "Non lo so"]
        ]
      }
    ]
  },
  {
    title: "2. Uso dell'intelligenza artificiale",
    questions: [
      {
        name: "ai_usage", label: "L'azienda usa o fornisce AI?", type: "checkbox", options: [
          ["internal_ai", "Usa AI solo internamente"],
          ["customer_product_ai", "Integra AI in prodotti o servizi per clienti"],
          ["in_house_ai", "Sviluppa sistemi AI propri"],
          ["ai_provider", "Fornisce sistemi AI ad altre aziende"],
          ["gpai", "Usa, modifica o fornisce modelli generativi/foundation model"],
          ["no_ai", "Non usa AI"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "ai_functions", label: "Che cosa fa il sistema AI?", type: "checkbox", options: [
          ["content_generation", "Produce testi, immagini, audio, video o codice"],
          ["recommendations", "Fa raccomandazioni o suggerimenti"],
          ["classification", "Classifica persone, documenti, clienti o rischi"],
          ["scoring", "Assegna punteggi o priorita'"],
          ["decision_support", "Supporta decisioni su persone fisiche"],
          ["automated_decision", "Prende decisioni automatiche senza revisione umana"],
          ["not_applicable", "Non applicabile"]
        ]
      },
      {
        name: "ai_notice", label: "Gli utenti sanno quando stanno interagendo con AI?", type: "radio", options: [
          ["clear", "Si, e' indicato chiaramente"],
          ["not_prominent", "Si, ma l'informazione non e' molto visibile"],
          ["no_notice", "No, non e' indicato chiaramente"],
          ["not_applicable", "Non applicabile"],
          ["unknown", "Non lo so"]
        ]
      }
    ]
  },
  {
    title: "3. Ambiti sensibili",
    questions: [
      {
        name: "sensitive_domains", label: "L'AI viene usata in uno di questi ambiti?", type: "checkbox", options: [
          ["recruiting", "Selezione personale, CV screening, candidati"],
          ["workers", "Gestione dipendenti o valutazione performance"],
          ["education", "Educazione, esami, ammissioni, valutazioni studenti"],
          ["credit", "Credito, assicurazioni o accesso a servizi essenziali"],
          ["healthcare", "Sanita', diagnosi, triage o decisioni mediche"],
          ["critical_infrastructure", "Infrastrutture critiche o sicurezza operativa"],
          ["law_migration_justice", "Forze dell'ordine, migrazione, giustizia o processi democratici"],
          ["none", "Nessuno di questi"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "delicate_ai_practices", label: "Il prodotto include pratiche AI particolarmente delicate?", type: "checkbox", options: [
          ["biometric_recognition", "Riconoscimento biometrico"],
          ["emotion_recognition", "Riconoscimento delle emozioni"],
          ["social_scoring", "Valutazione sociale o ranking delle persone"],
          ["manipulative_techniques", "Tecniche manipolative o persuasive non trasparenti"],
          ["sensitive_traits", "Analisi di caratteristiche sensibili delle persone"],
          ["none", "Nessuna di queste"],
          ["unknown", "Non lo so"]
        ]
      }
    ]
  },
  {
    title: "4. Dati personali",
    questions: [
      {
        name: "personal_data", label: "L'azienda tratta dati personali?", type: "checkbox", options: [
          ["customers_users", "Dati di clienti o utenti"],
          ["employees_candidates", "Dati di dipendenti o candidati"],
          ["contact_account", "Dati di contatto o account"],
          ["tracking_analytics", "Dati di utilizzo, tracciamento o analytics"],
          ["sensitive_data", "Dati sanitari, biometrici o altri dati sensibili"],
          ["children_data", "Dati di minori"],
          ["no_personal_data", "No, non tratta dati personali"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "profiling_decisions", label: "L'azienda usa dati personali per profilazione o decisioni automatiche?", type: "checkbox", options: [
          ["profiling", "Profilazione o segmentazione utenti/clienti"],
          ["personalized_recommendations", "Raccomandazioni personalizzate"],
          ["significant_automated_decisions", "Decisioni automatiche con effetti importanti sulle persone"],
          ["human_review_decision_support", "Supporto decisionale con revisione umana"],
          ["no", "No"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "privacy_role", label: "Qual e' il ruolo privacy principale dell'azienda?", type: "radio", options: [
          ["controller", "Titolare del trattamento"],
          ["processor", "Responsabile del trattamento per conto di clienti"],
          ["joint_controller", "Contitolare con altri soggetti"],
          ["mixed", "Ruolo misto"],
          ["unknown", "Non lo so"]
        ]
      }
    ]
  },
  {
    title: "5. Cloud, fornitori e controlli",
    questions: [
      {
        name: "extra_eea_transfers", label: "I dati personali vengono trasferiti fuori da UE/SEE?", type: "radio", options: [
          ["yes", "Si"],
          ["no", "No"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "extra_eea_providers", label: "L'azienda usa fornitori cloud o AI extra UE/SEE?", type: "checkbox", options: [
          ["cloud_hosting", "Cloud hosting"],
          ["ai_api_models", "API o modelli AI"],
          ["internal_saas", "Strumenti SaaS usati internamente"],
          ["no", "No"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "controls", label: "Quali controlli o documenti esistono gia'?", type: "checkbox", options: [
          ["privacy_policy", "Privacy policy aggiornata"],
          ["records_processing", "Registro dei trattamenti"],
          ["dpo_privacy_owner", "DPO o referente privacy nominato"],
          ["dpia_process", "Processo DPIA / valutazione impatto privacy"],
          ["breach_process", "Processo gestione data breach"],
          ["data_subject_rights", "Processo gestione diritti degli interessati"],
          ["vendor_review", "Revisione fornitori e subfornitori"],
          ["ai_documentation", "Documentazione del sistema AI"],
          ["human_oversight", "Controllo umano sugli output AI"],
          ["ai_policy", "Policy interna sull'uso dell'AI"],
          ["training", "Formazione interna su AI o privacy"],
          ["none", "Nessuno di questi"],
          ["unknown", "Non lo so"]
        ]
      },
      {
        name: "dashboard_priority", label: "Cosa vuoi ottenere per primo dalla valutazione?", type: "radio", options: [
          ["applicable_rules", "Capire quali norme si applicano all'azienda"],
          ["main_risks", "Capire quali sono i rischi principali"],
          ["missing_controls", "Sapere quali documenti o controlli mancano"],
          ["external_evidence", "Preparare materiale per clienti, investitori o partner"],
          ["gdpr_ai_act_review", "Prepararsi a una revisione GDPR o AI Act"],
          ["action_plan", "Costruire un piano operativo con prossime azioni"]
        ]
      },
      { name: "notes", label: "Note libere opzionali", type: "textarea" }
    ]
  }
];

const exclusiveCheckboxValues = {
  eu_presence: new Set(["no_eu_presence", "unknown"]),
  ai_usage: new Set(["no_ai", "unknown"]),
  ai_functions: new Set(["not_applicable"]),
  sensitive_domains: new Set(["none", "unknown"]),
  delicate_ai_practices: new Set(["none", "unknown"]),
  personal_data: new Set(["no_personal_data", "unknown"]),
  profiling_decisions: new Set(["no", "unknown"]),
  extra_eea_providers: new Set(["no", "unknown"]),
  controls: new Set(["none", "unknown"])
};

function setSingleAnswer(name, value) {
  document.querySelectorAll(`input[name="${name}"]`).forEach((item) => {
    item.checked = item.value === value;
  });
}

function clearAnswers(name, values) {
  document.querySelectorAll(`input[name="${name}"]`).forEach((item) => {
    if (values.has(item.value)) item.checked = false;
  });
}

questionnaireForm.addEventListener("change", (event) => {
  const field = event.target;
  document.querySelectorAll("[data-demo-questionnaire]").forEach((button) => {
    button.classList.remove("active-demo");
    button.setAttribute("aria-pressed", "false");
  });
  if (!(field instanceof HTMLInputElement)) return;

  if (field.type === "checkbox") {
    const exclusiveValues = exclusiveCheckboxValues[field.name];
    if (exclusiveValues) {
      const group = Array.from(document.querySelectorAll(`input[type="checkbox"][name="${field.name}"]`));
      if (field.checked && exclusiveValues.has(field.value)) {
        group.forEach((item) => { if (item !== field) item.checked = false; });
      } else if (field.checked) {
        group.forEach((item) => {
          if (exclusiveValues.has(item.value)) item.checked = false;
        });
      }
    }
  }

  if (field.name === "ai_usage" && field.checked && field.value === "no_ai") {
    setSingleAnswer("ai_functions", "not_applicable");
    setSingleAnswer("sensitive_domains", "none");
    setSingleAnswer("delicate_ai_practices", "none");
    setSingleAnswer("ai_notice", "not_applicable");
  } else if (field.name === "ai_usage" && field.checked && !["no_ai", "unknown"].includes(field.value)) {
    clearAnswers("ai_functions", new Set(["not_applicable"]));
    clearAnswers("sensitive_domains", new Set(["none"]));
    clearAnswers("delicate_ai_practices", new Set(["none"]));
    clearAnswers("ai_notice", new Set(["not_applicable"]));
  }

  if (field.name === "personal_data" && field.checked && field.value === "no_personal_data") {
    setSingleAnswer("profiling_decisions", "no");
    setSingleAnswer("extra_eea_transfers", "no");
    setSingleAnswer("extra_eea_providers", "no");
  } else if (field.name === "personal_data" && field.checked && !["no_personal_data", "unknown"].includes(field.value)) {
    clearAnswers("profiling_decisions", new Set(["no"]));
    clearAnswers("extra_eea_transfers", new Set(["no"]));
    clearAnswers("extra_eea_providers", new Set(["no"]));
  }
});

fetch("/api/health")
  .then((response) => response.json())
  .then((health) => {
    serverStatus.dataset.modelConfigured = health.model_configured ? "true" : "false";
    const modelUnavailable = !health.model_configured
      || !health.model_reachable
      || health.model_available === false;
    serverStatus.dataset.modelAvailable = modelUnavailable ? "false" : "true";
    serverStatus.textContent = modelUnavailable ? t("model_missing") : "";
    serverStatus.hidden = !modelUnavailable;
  })
  .catch(() => {
    serverStatus.dataset.modelAvailable = "false";
    serverStatus.textContent = t("model_missing");
    serverStatus.hidden = false;
  });

document.getElementById("languageSelect").addEventListener("change", (event) => {
  updateLanguageFlag(event.target.value);
  applyLanguage(event.target.value);
});

function switchPage(pageId) {
  document.querySelectorAll(".page").forEach((page) => {
    const isActive = page.id === pageId;
    page.classList.toggle("active", isActive);
    page.hidden = !isActive;
  });
  document.querySelectorAll("[data-page-target]").forEach((button) => {
    const isActive = button.dataset.pageTarget === pageId;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });
}

document.querySelectorAll("[data-page-target]").forEach((button) => {
  button.addEventListener("click", () => switchPage(button.dataset.pageTarget));
  button.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
    const tabs = Array.from(document.querySelectorAll("[data-page-target]"));
    const offset = event.key === "ArrowRight" ? 1 : -1;
    const next = tabs[(tabs.indexOf(button) + offset + tabs.length) % tabs.length];
    switchPage(next.dataset.pageTarget);
    next.focus();
    event.preventDefault();
  });
});

// Render the schema into mouse-friendly radio and checkbox controls.
function renderQuestionnaireForm() {
  questionnaireForm.innerHTML = questionnaireSchema.map((section) => `
        <div class="questionnaire-section">
          <h2>${escapeHtml(tq(section.title))}</h2>
          ${section.questions.map(renderQuestion).join("")}
        </div>
      `).join("");
}

function renderQuestion(question) {
  if (question.type === "text") {
    return `
          <div class="question">
            <label class="title" for="q_${question.name}">${escapeHtml(tq(question.label))}</label>
            <input type="text" id="q_${question.name}" name="${question.name}">
          </div>
        `;
  }
  if (question.type === "textarea") {
    return `
          <div class="question">
            <label class="title" for="q_${question.name}">${escapeHtml(tq(question.label))}</label>
            <textarea id="q_${question.name}" name="${question.name}"></textarea>
          </div>
        `;
  }
  return `
        <div class="question">
          <label class="title">${escapeHtml(tq(question.label))}</label>
          <div class="question-options">
            ${question.options.map(([value, label]) => `
              <label class="choice">
                <input type="${question.type}" name="${question.name}" value="${escapeHtml(value)}">
                <span>${escapeHtml(tq(label))}</span>
              </label>
            `).join("")}
          </div>
        </div>
      `;
}

function collectQuestionnairePayload() {
  const answers = {};
  for (const section of questionnaireSchema) {
    for (const question of section.questions) {
      const fields = Array.from(document.querySelectorAll(`[name="${question.name}"]`));
      if (question.type === "checkbox") {
        answers[question.name] = fields.filter((field) => field.checked).map((field) => field.value);
      } else if (question.type === "radio") {
        const selected = fields.find((field) => field.checked);
        answers[question.name] = selected ? selected.value : "";
      } else {
        answers[question.name] = fields[0] ? fields[0].value.trim() : "";
      }
    }
  }
  currentQuestionnairePayload = {
    questionnaire: "company_gdpr_ai_act_initial_assessment",
    version: "1.0",
    completed_at: new Date().toISOString(),
    answers
  };
  return currentQuestionnairePayload;
}

function populateQuestionnaire(payload) {
  currentQuestionnairePayload = payload;
  const answers = payload.answers || {};
  for (const section of questionnaireSchema) {
    for (const question of section.questions) {
      const value = answers[question.name];
      const fields = Array.from(document.querySelectorAll(`[name="${question.name}"]`));
      if (question.type === "checkbox") {
        const values = Array.isArray(value) ? value : [];
        fields.forEach((field) => { field.checked = values.includes(field.value); });
      } else if (question.type === "radio") {
        fields.forEach((field) => { field.checked = field.value === value; });
      } else if (fields[0]) {
        fields[0].value = value || "";
      }
    }
  }
}

async function evaluateQuestionnairePayload(payload, goToDashboard = true) {
  const response = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Errore valutazione");
  currentQuestionnairePayload = result.questionnaire_payload || payload;
  resetChatConversation();
  renderDashboard(result);
  if (goToDashboard) switchPage("dashboardPage");
  return result;
}

const languageSelect = document.getElementById("languageSelect");
Array.from(languageSelect.options).forEach((option) => {
  option.disabled = !questionnaireLanguageCodes.has(option.value);
});
languageSelect.value = "en";
updateLanguageFlag("en");
renderQuestionnaireForm();
applyLanguage("en");

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function safeExternalUrl(value) {
  try {
    const parsed = new URL(String(value || ""));
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : "";
  } catch (_) {
    return "";
  }
}

function badgeClass(level) {
  const value = String(level || "").toLowerCase();
  if (value.includes("critical")) return "critical";
  if (value.includes("high")) return "high";
  if (value.includes("medium")) return "medium";
  return "low";
}

function readableValue(value) {
  return String(value || "").replaceAll("_", " ");
}

function renderEvidence(items) {
  if (!items || items.length === 0) return "-";
  return items.map((item) => {
    const values = item.selected_values || item.missing_values || [];
    return readableValue(item.question_key) + ": " + values.map(readableValue).join(", ");
  }).join("; ");
}

function renderExplanation(item) {
  return '<details class="explanation"><summary>' + escapeHtml(t("why_triggered")) +
    '</summary><p>' + escapeHtml(renderEvidence(item.triggered_by)) +
    '</p><p><strong>' + escapeHtml(t("legal_references")) + ':</strong> ' +
    escapeHtml((item.legal_references || []).join("; ") || "-") +
    '</p><p><strong>' + escapeHtml(t("recommended_action")) + ':</strong> ' +
    escapeHtml(trResult(item.recommended_action) || "-") + '</p></details>';
}

// Render only server-produced facts. The browser never recalculates risk.
function renderDashboard(payload, announce = true) {
  currentContext = payload;
  const ctx = payload.dashboard_context;
  const feedMeta = payload.feed_meta || { mode: "demo" };
  const memory = payload.company_memory;
  const score = ctx.compliance_score;

  summary.className = "summary-grid";
  summary.innerHTML = `
        <div class="metric">
          <strong>${escapeHtml(t("company"))}</strong>
          <div class="value">${escapeHtml(ctx.company_name || "Profilo")}</div>
          <span class="badge ${badgeClass(score.band)}">${escapeHtml(trResult(score.label))}</span>
        </div>
        <div class="metric">
          <strong>${escapeHtml(t("compliance_score"))}</strong>
          <div class="value">${escapeHtml(score.score)}/100</div>
          <span class="badge ${badgeClass(score.band)}">${escapeHtml(trResult(score.band))}</span>
        </div>
        <div class="metric">
          <strong>${escapeHtml(t("relevant_tags"))}</strong>
          <div class="value">${ctx.relevance_tags.length}</div>
          <span class="status">${escapeHtml(ctx.relevance_tags.join(", "))}</span>
        </div>
        <div class="metric">
          <strong>${escapeHtml(t("matched_events"))}</strong>
          <div class="value">${ctx.matched_regulatory_events.length}</div>
          <span class="status">${escapeHtml(t("personalized_feed"))}</span>
        </div>
      `;

  warnings.className = "lists";
  warnings.innerHTML = `
        <div>
          <h3>${escapeHtml(t("warnings"))}</h3>
          <ul>
            ${ctx.risk_warnings.map((item) => `<li><span class="badge ${badgeClass(item.level)}">${escapeHtml(trResult(item.level))}</span> <strong>${escapeHtml(trResult(item.title))}</strong><br>${escapeHtml(trResult(item.message))}${renderExplanation(item)}</li>`).join("")}
          </ul>
        </div>
        <div>
          <h3>${escapeHtml(t("missing_controls"))}</h3>
          <ul>
            ${(memory.controls.missing_or_to_verify || []).map((item) => `<li>${escapeHtml(trResult(item))}</li>`).join("") || `<li>${escapeHtml(t("no_missing_controls"))}</li>`}
          </ul>
          <h3>${escapeHtml(t("score_breakdown"))}</h3>
          <ul>
            ${(score.breakdown || []).map((item) => `<li><strong>+${escapeHtml(item.points)}</strong> ${escapeHtml(trResult(item.label))}${renderExplanation(item)}</li>`).join("")}
          </ul>
        </div>
      `;

  renderFeed(events, ctx.matched_regulatory_events);
  renderFeed(news, ctx.matched_news_feed);
  renderFeed(earlyWarnings, ctx.matched_early_warnings || []);
  renderTimeline(ctx.compliance_timeline || []);
  if (typeof renderProgress === "function") {
    renderProgress(payload);
  }
  if (feedMeta.mode === "live") {
    const updatedAt = new Date(feedMeta.updated_at);
    const formattedDate = Number.isNaN(updatedAt.getTime())
      ? ""
      : updatedAt.toLocaleString(currentLanguage);
    const warningCount = Array.isArray(feedMeta.errors) ? feedMeta.errors.length : 0;
    feedNotice.textContent = `${t("live_notice")} ${formattedDate}${feedMeta.mode === "cached" || warningCount ? `  ⚠ ${warningCount || 1}` : ""}`.trim();
    feedNotice.dataset.feedMode = feedMeta.mode;
  } else if (feedMeta.mode === "cached") {
    const updatedAt = new Date(feedMeta.updated_at);
    const formattedDate = Number.isNaN(updatedAt.getTime())
      ? "unknown"
      : updatedAt.toLocaleString(currentLanguage);
    const warningCount = Array.isArray(feedMeta.errors) ? feedMeta.errors.length : 0;
    feedNotice.textContent = `${t("demo_notice")}  CACHED SNAPSHOT: ${formattedDate}  ⚠ ${warningCount || 1}`;
    feedNotice.dataset.feedMode = "cached";
  } else {
    feedNotice.textContent = t("demo_notice");
    feedNotice.dataset.feedMode = "demo";
  }
  if (announce) {
    appendChat(t("assistant_name"), t("dashboard_loaded"));
  }
}

function renderFeed(container, items) {
  container.className = "feed";
  if (!items || items.length === 0) {
    container.className = "feed empty";
    container.textContent = t("no_match");
    return;
  }
  container.innerHTML = items.map((item) => {
    const sourceUrl = safeExternalUrl(
      item.url || item.primary_official_source_url || item.evidence?.find((entry) => entry.url)?.url
    );
    return `
        <article class="event">
          <div class="event-top">
            <span>${escapeHtml(t("match"))} ${escapeHtml(item.match_score)}/100 · ${escapeHtml(item.regulation_area)}</span>
            <span>${escapeHtml(item.priority || item.status || "")}${item.priority_score !== undefined ? ` · ${escapeHtml(item.priority_score)}/100` : ""}</span>
          </div>
          <h3>${escapeHtml(item.title)}</h3>
          ${item.duplicate_count > 1 ? `<p><strong>${escapeHtml(t("source_label"))}:</strong> ${escapeHtml(item.duplicate_count)}</p>` : ""}
          ${item.source ? `<p><strong>${escapeHtml(t("source_label"))}:</strong> ${escapeHtml(item.source)}</p>` : ""}
          ${item.legal_status ? `<p class="signal-status"><strong>${escapeHtml(t("source_status"))}:</strong> ${escapeHtml(item.legal_status)}</p>` : ""}
          <p>${escapeHtml(item.summary)}</p>
          ${item.priority_reasons?.length ? `<details class="explanation"><summary>${escapeHtml(t("why_triggered"))}</summary><p>${escapeHtml(item.priority_reasons.join("; "))}</p></details>` : ""}
          <p><strong>${escapeHtml(t("topics"))}:</strong> ${escapeHtml((item.matched_topics || []).join(", ") || "general")}</p>
          ${sourceUrl ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(t("open_source"))}</a>` : `<span class="status">${escapeHtml(t("no_source"))}</span>`}
        </article>
      `;
  }).join("");
}

function renderTimeline(items) {
  timeline.className = "timeline";
  if (!items.length) {
    timeline.className = "timeline empty";
    timeline.textContent = t("no_match");
    return;
  }
  timeline.innerHTML = items.map((item) => {
    const date = new Date(`${item.date}T00:00:00Z`).toLocaleDateString(currentLanguage, {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
    const className = item.basis === "political_agreement" ? "timeline-item political-agreement" : "timeline-item";
    const sourceUrl = safeExternalUrl(item.source_url);
    return `
          <article class="${className}">
            <div>
              <div class="timeline-date">${escapeHtml(date)}</div>
              <span class="badge ${item.status_code === "timeline_status_applicable" ? "low" : "medium"}">${escapeHtml(t(item.status_code) || item.status)}</span>
            </div>
            <div>
              <h3>${escapeHtml(t(item.translation_key) || item.title)}</h3>
              <p>${escapeHtml(item.legal_reference || "")}</p>
              ${sourceUrl ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(t("open_source"))}</a>` : ""}
            </div>
          </article>
        `;
  }).join("");
}

function appendChat(author, text, isUser = false) {
  const message = document.createElement("div");
  message.className = `message${isUser ? " user" : ""}`;

  if (isUser) {
    message.textContent = `${author}: ${text}`;
  } else {
    message.innerHTML = `
      <strong>${author}:</strong>
      <div class="markdown-content">
        ${text ? renderSafeMarkdown(text) : ""}
      </div>
    `;
  }

  chatLog.appendChild(message);
  chatLog.scrollTop = chatLog.scrollHeight;

  return message;
}

function resetChatConversation() {
  chatHistory.length = 0;
  chatLog.replaceChildren();
}

// -----------------------------------------------------------------------
