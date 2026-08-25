/**
 * Local i18n runtime. Dictionaries live in ./locales/<language>.js.
 * No translation service is called: all text is bundled and works offline.
 */
const localeBundles = window.ComplianceLocales || {};
const euOfficialLanguageCodes = Object.keys(localeBundles);
const translations = Object.fromEntries(
  Object.entries(localeBundles).map(([code, bundle]) => [code, bundle.ui || {}])
);
const questionnaireTranslations = Object.fromEntries(
  Object.entries(localeBundles)
    .filter(([code]) => code !== "it")
    .map(([code, bundle]) => [code, bundle.questionnaire || {}])
);
const localeResultTranslations = Object.fromEntries(
  Object.entries(localeBundles)
    .filter(([, bundle]) => bundle.results)
    .map(([code, bundle]) => [code, bundle.results])
);

// Deterministic assessment results are produced in English by the server so
// scoring remains language-neutral. Translate the known result vocabulary at
// render time without changing any score, tag, or legal reference.
const resultTranslations = localeResultTranslations;

let currentLanguage = "en";
const questionnaireUiKeys = new Set([
  "questionnaire_title",
  "questionnaire_intro",
  "questionnaire_language_warning",
  "load_questionnaire",
  "demo_saas",
  "demo_hr",
  "demo_gpai",
  "evaluate_questionnaire",
  "download_questionnaire",
  "go_dashboard"
]);

function t(key) {
  return translations[currentLanguage][key] || translations.en[key] || translations.it[key] || key;
}

function trResult(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  const dictionary = resultTranslations[currentLanguage] || {};
  const direct = dictionary[text];
  if (direct) return direct;
  const missingPrefix = "Some expected controls are missing or unclear: ";
  const translatedMissingPrefix = dictionary[missingPrefix];
  if (translatedMissingPrefix && text.startsWith(missingPrefix)) {
    const controls = text.slice(missingPrefix.length).replace(/\.$/, "").split(", ");
    return `${translatedMissingPrefix}${controls.map((item) => dictionary[item] || item).join(", ")}.`;
  }
  return text;
}

// Italian is the schema source language. Every other enabled language must
// provide a complete local dictionary instead of silently copying English.
const questionnaireLanguageCodes = new Set([
  "it",
  ...Object.keys(questionnaireTranslations)
]);

function tq(text) {
  if (currentLanguage === "it") return text;
  const direct = questionnaireTranslations[currentLanguage]?.[text];
  if (direct) return direct;
  return text;
}

function applyLanguage(languageCode) {
  currentLanguage = translations[languageCode] ? languageCode : "it";
  document.documentElement.lang = currentLanguage;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    const questionnaireFallback = node.closest("#questionnairePage")
      && questionnaireUiKeys.has(key)
      && !questionnaireLanguageCodes.has(currentLanguage);
    node.textContent = questionnaireFallback
      ? (translations.it[key] || t(key))
      : t(key);
  });
  if (typeof updateQuestionnaireFileLabel === "function") {
    updateQuestionnaireFileLabel();
  }
  chatInput.placeholder = t("chat_placeholder");
  const modelUnavailable = serverStatus.dataset.modelAvailable === "false";
  serverStatus.textContent = modelUnavailable ? t("model_missing") : "";
  serverStatus.hidden = !modelUnavailable;
  if (currentContext) {
    renderDashboard(currentContext, false);
  }
  const questionnaireLanguageWarning = document.getElementById("questionnaireLanguageWarning");
  if (questionnaireLanguageWarning) {
    questionnaireLanguageWarning.classList.toggle(
      "visible",
      !questionnaireLanguageCodes.has(currentLanguage)
    );
  }
  const savedPayload = questionnaireForm.children.length
    ? collectQuestionnairePayload()
    : currentQuestionnairePayload;
  renderQuestionnaireForm();
  if (savedPayload) {
    populateQuestionnaire(savedPayload);
  }
}
