/**
 * Contextual Help UI.
 *
 * Help remains a presentation-layer feature: it does not alter questionnaire
 * answers, assessment results, agent prompts, or model configuration.
 */
const contextHelp = document.getElementById("contextHelp");
const contextHelpBody = document.getElementById("contextHelpBody");
const contextHelpClose = document.getElementById("contextHelpClose");
const helpButton = document.getElementById("helpButton");
const floatingHelpButton = document.getElementById("floatingHelpButton");
const helpTriggers = [helpButton, floatingHelpButton].filter(Boolean);

const helpSections = {
  questionnaire: [
    {
      titleKey: "loading_title",
      textKey: "loading_text",
      itemKeys: ["loading_1", "loading_2", "loading_3"]
    },
    {
      titleKey: "questionnaire_overview_title",
      textKey: "questionnaire_overview_text",
      itemKeys: [
        "questionnaire_answer_1",
        "questionnaire_answer_2",
        "questionnaire_answer_3",
        "questionnaire_answer_4"
      ]
    },
    {
      titleKey: "evaluate_questionnaire",
      textKey: "assessment_1"
    },
    {
      titleKey: "snapshots_title",
      textKey: "snapshots_text",
      itemKeys: ["snapshot_save", "snapshot_load", "snapshot_compare", "snapshot_delete"]
    },
    {
      titleKey: "go_dashboard",
      textKey: "assessment_3"
    }
  ],
  dashboard: [
    {
      titleKey: "dashboard_score_title",
      textKey: "dashboard_score_text"
    },
    {
      titleKey: "dashboard_warnings_title",
      textKey: "dashboard_warnings_text"
    },
    {
      titleKey: "dashboard_timeline_title",
      textKey: "dashboard_timeline_text"
    },
    {
      titleKey: "dashboard_news_title",
      itemKeys: ["dashboard_news_events", "dashboard_news_updates", "dashboard_news_refresh"]
    },
    {
      titleKey: "dashboard_assistant_title",
      textKey: "dashboard_assistant_text",
      exampleKey: "chat_placeholder"
    }
  ],
  progress: [
    {
      titleKey: "progress_title",
      textKey: "progress_intro"
    },
    {
      titleKey: "control_coverage",
      itemKeys: ["existing_controls", "missing_controls"]
    },
    {
      titleKey: "priority_distribution",
      textKey: "dashboard_warnings_text"
    },
    {
      titleKey: "upcoming_milestones",
      textKey: "timeline_notice"
    },
    {
      titleKey: "progress_eyebrow",
      textKey: "progress_disclaimer"
    }
  ]
};

let previousHelpFocus = null;

function activeHelpPage() {
  if (document.getElementById("progressPage")?.classList.contains("active")) return "progress";
  if (document.getElementById("dashboardPage")?.classList.contains("active")) return "dashboard";
  return "questionnaire";
}

function appendLocalizedElement(parent, tagName, key) {
  const element = document.createElement(tagName);
  element.dataset.i18n = key;
  element.textContent = t(key);
  parent.appendChild(element);
}

function appendLocalizedList(parent, keys) {
  const list = document.createElement("ul");
  keys.forEach((key) => appendLocalizedElement(list, "li", key));
  parent.appendChild(list);
}

function renderContextHelp() {
  contextHelpBody.replaceChildren();
  helpSections[activeHelpPage()].forEach((definition) => {
    const section = document.createElement("section");
    section.className = "context-help-section";
    appendLocalizedElement(section, "h3", definition.titleKey);
    if (definition.textKey) appendLocalizedElement(section, "p", definition.textKey);
    if (definition.itemKeys) appendLocalizedList(section, definition.itemKeys);
    if (definition.exampleKey) {
      const example = document.createElement("p");
      example.className = "context-help-example";
      example.dataset.i18n = definition.exampleKey;
      example.textContent = t(definition.exampleKey);
      section.appendChild(example);
    }
    contextHelpBody.appendChild(section);
  });
}

function openContextHelp() {
  previousHelpFocus = document.activeElement;
  renderContextHelp();
  contextHelp.hidden = false;
  document.body.classList.add("context-help-open");
  helpTriggers.forEach((trigger) => trigger.setAttribute("aria-expanded", "true"));
  updateFloatingHelpVisibility();
  contextHelpClose.focus();
}

function closeContextHelp() {
  contextHelp.hidden = true;
  document.body.classList.remove("context-help-open");
  helpTriggers.forEach((trigger) => trigger.setAttribute("aria-expanded", "false"));
  updateFloatingHelpVisibility();
  if (previousHelpFocus instanceof HTMLElement) previousHelpFocus.focus();
}

function updateFloatingHelpVisibility() {
  floatingHelpButton.hidden = window.scrollY < 260 || !contextHelp.hidden;
}

function trapContextHelpFocus(event) {
  if (event.key === "Escape") {
    closeContextHelp();
    return;
  }
  if (event.key !== "Tab") return;

  const focusable = Array.from(
    contextHelp.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])')
  ).filter((element) => !element.disabled);
  if (!focusable.length) return;

  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    last.focus();
    event.preventDefault();
  } else if (!event.shiftKey && document.activeElement === last) {
    first.focus();
    event.preventDefault();
  }
}

helpTriggers.forEach((trigger) => {
  trigger.setAttribute("aria-expanded", "false");
  trigger.addEventListener("click", openContextHelp);
});
contextHelp.querySelectorAll("[data-help-close]").forEach((button) => {
  button.addEventListener("click", closeContextHelp);
});
contextHelp.addEventListener("keydown", trapContextHelpFocus);
window.addEventListener("scroll", updateFloatingHelpVisibility, { passive: true });
updateFloatingHelpVisibility();
