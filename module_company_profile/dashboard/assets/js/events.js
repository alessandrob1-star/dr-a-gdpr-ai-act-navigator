// User actions and API orchestration
// -----------------------------------------------------------------------
function clearDemoSelection() {
  document.querySelectorAll("[data-demo-questionnaire]").forEach((button) => {
    button.classList.remove("active-demo");
    button.setAttribute("aria-pressed", "false");
  });
}

const assistantPanel = document.getElementById("assistantPanel");
const chatbotLauncher = document.getElementById("chatbotLauncher");
const chatbotClose = document.getElementById("chatbotClose");
const chatbotBreakpoint = window.matchMedia("(max-width: 1180px)");

function setChatbotPanelOpen(isOpen) {
  if (!assistantPanel || !chatbotLauncher) return;
  assistantPanel.classList.toggle("chatbot-open", isOpen);
  document.body.classList.toggle("chatbot-panel-open", isOpen);
  chatbotLauncher.setAttribute("aria-expanded", String(isOpen));
  if (isOpen) {
    chatInput.focus();
  } else {
    chatbotLauncher.focus();
  }
}

if (assistantPanel && chatbotLauncher) {
  chatbotLauncher.addEventListener("click", () => setChatbotPanelOpen(true));
  chatbotClose?.addEventListener("click", () => setChatbotPanelOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && assistantPanel.classList.contains("chatbot-open")) {
      setChatbotPanelOpen(false);
    }
  });
  document.addEventListener("click", (event) => {
    if (!chatbotBreakpoint.matches || !assistantPanel.classList.contains("chatbot-open")) return;
    if (assistantPanel.contains(event.target) || chatbotLauncher.contains(event.target)) return;
    setChatbotPanelOpen(false);
  });
  chatbotBreakpoint.addEventListener("change", (event) => {
    if (!event.matches) setChatbotPanelOpen(false);
  });
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") || "";
  let result = {};
  if (contentType.includes("application/json")) {
    result = await response.json();
  }
  if (!response.ok) {
    throw new Error(result.error || `Request failed (${response.status}).`);
  }
  return result;
}

document.getElementById("loadQuestionnaireFile").addEventListener("click", async () => {
  const file = questionnaireFile.files[0];
  if (!file) {
    alert(t("load_json_alert"));
    return;
  }
  try {
    const content = await file.text();
    const payload = JSON.parse(content);
    clearDemoSelection();
    populateQuestionnaire(payload);
    await evaluateQuestionnairePayload(payload, false);
  } catch (error) {
    alert(`${t("load_error")}: ${error.message}`);
  }
});

document.getElementById("evaluateQuestionnaire").addEventListener("click", async () => {
  try {
    await evaluateQuestionnairePayload(collectQuestionnairePayload(), true);
  } catch (error) {
    alert(`${t("load_error")}: ${error.message}`);
  }
});

document.getElementById("downloadQuestionnaire").addEventListener("click", () => {
  const payload = collectQuestionnairePayload();
  const company = (payload.answers.company_name || "azienda").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "azienda";
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `questionario-${company}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});

document.getElementById("goDashboard").addEventListener("click", () => {
  switchPage("dashboardPage");
});

document.querySelectorAll("[data-demo-questionnaire]").forEach((button) => {
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      const result = await requestJson("/api/demo-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile_id: button.dataset.demoQuestionnaire })
      });
      document.querySelectorAll("[data-demo-questionnaire]").forEach((item) => {
        const isSelected = item === button;
        item.classList.toggle("active-demo", isSelected);
        item.setAttribute("aria-pressed", String(isSelected));
      });
      populateQuestionnaire(result.questionnaire_payload);
      resetChatConversation();
      renderDashboard(result, false);
    } catch (error) {
      alert(`${t("load_error")}: ${error.message}`);
    } finally {
      button.disabled = false;
    }
  });
});

const sendChatButton = document.getElementById("sendChat");
let chatRequestInFlight = false;

sendChatButton.addEventListener("click", async () => {
  const message = chatInput.value.trim();
  if (!message || chatRequestInFlight) return;
  if (!currentContext) {
    appendChat(t("assistant_name"), t("load_profile_first"));
    return;
  }
  appendChat(t("you"), message, true);
  chatInput.value = "";
  chatRequestInFlight = true;
  sendChatButton.disabled = true;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        questionnaire_payload: currentContext.questionnaire_payload,
        history: chatHistory.slice(-8)
      })
    });
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const result = await response.json();
      const reply = result.reply || result.error || t("load_error");
      appendChat(t("assistant_name"), reply);
      chatHistory.push({ role: "user", content: message }, { role: "assistant", content: reply });
      return;
    }
    if (!response.ok || !response.body) {
      throw new Error(`Chat request failed (${response.status}).`);
    }

    const messageNode = appendChat(t("assistant_name"), "");
    const markdownContainer = messageNode.querySelector(".markdown-content");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let streamedReply = "";
    let streamBuffer = "";
    let streamFailed = false;
    while (true) {
      const { value, done } = await reader.read();
      streamBuffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const lines = streamBuffer.split("\n");
      streamBuffer = done ? "" : lines.pop();
      for (const line of lines) {
        if (!line.trim()) continue;
        const event = JSON.parse(line);
        if (event.type === "delta") {
          streamedReply += event.text || "";

          markdownContainer.innerHTML = renderSafeMarkdown(streamedReply);
        } else if (event.type === "replace") {
          streamedReply = event.text || "";
          markdownContainer.innerHTML = renderSafeMarkdown(streamedReply);
        } else if (event.type === "error") {
          streamedReply = event.text || "Dr. A could not complete the response.";
          markdownContainer.innerHTML = renderSafeMarkdown(streamedReply);
          streamFailed = true;
        } else if (event.type === "sources" && event.items?.length) {
          appendChatSources(messageNode, event.items);
        }
        chatLog.scrollTop = chatLog.scrollHeight;
      }
      if (done) break;
    }
    if (!streamFailed) {
      chatHistory.push(
        { role: "user", content: message },
        { role: "assistant", content: streamedReply }
      );
    }
  } catch (error) {
    appendChat(t("assistant_name"), `${t("load_error")}: ${error.message}`);
  } finally {
    chatRequestInFlight = false;
    sendChatButton.disabled = false;
    chatInput.focus();
  }
});

function appendChatSources(messageNode, sources) {
  const block = document.createElement("div");
  block.className = "message-sources";
  const heading = document.createElement("strong");
  heading.textContent = `${t("source_label")}:`;
  block.appendChild(heading);
  const list = document.createElement("ul");
  sources.forEach((source) => {
    let parsedUrl;
    try {
      parsedUrl = new URL(source.url);
    } catch (_) {
      return;
    }
    if (!["http:", "https:"].includes(parsedUrl.protocol)) return;
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = parsedUrl.href;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = `[${source.id}] ${source.title}`;
    item.appendChild(link);
    if (source.legal_status) {
      const status = document.createElement("span");
      status.textContent = ` — ${source.legal_status}`;
      item.appendChild(status);
    }
    list.appendChild(item);
  });
  block.appendChild(list);
  messageNode.appendChild(block);
}

document.getElementById("refreshNews").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = t("refreshing_news");
  try {
    const response = await fetch("/api/refresh-news", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectQuestionnairePayload())
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "News refresh failed");
    resetChatConversation();
    renderDashboard(result, false);
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
});

const savedProfiles = document.getElementById("savedProfiles");
const compareProfile = document.getElementById("compareProfile");
const profileComparison = document.getElementById("profileComparison");
const appFeedback = document.getElementById("appFeedback");
let feedbackTimer = null;

function showFeedback(message, isError = false) {
  window.clearTimeout(feedbackTimer);
  appFeedback.textContent = message;
  appFeedback.classList.toggle("error", isError);
  appFeedback.hidden = false;
  feedbackTimer = window.setTimeout(() => {
    appFeedback.hidden = true;
  }, 3500);
}

async function refreshSavedProfiles() {
  const result = await requestJson("/api/profiles");
  savedProfiles.innerHTML = `<option value="" data-i18n="saved_profiles">${t("saved_profiles")}</option>`;
  compareProfile.innerHTML = `<option value="" data-i18n="compare_with">${t("compare_with")}</option>`;
  (result.profiles || []).forEach((profile) => {
    const savedAt = profile.saved_at ? new Date(profile.saved_at).toLocaleString(currentLanguage) : "";
    const label = `${profile.company_name} · ${profile.score ?? "-"}/100 · ${savedAt}`;
    [savedProfiles, compareProfile].forEach((select) => {
      const option = document.createElement("option");
      option.value = profile.id;
      option.textContent = label;
      select.appendChild(option);
    });
  });
}

document.getElementById("saveProfile").addEventListener("click", async () => {
  if (!currentContext) {
    alert(t("load_profile_first"));
    return;
  }
  try {
    const result = await requestJson("/api/profile/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ evaluation: currentContext })
    });
    await refreshSavedProfiles();
    savedProfiles.value = result.snapshot.id;
    showFeedback(`${t("save_profile")} ✓`);
  } catch (error) {
    showFeedback(error.message, true);
  }
});

document.getElementById("loadSavedProfile").addEventListener("click", async () => {
  if (!savedProfiles.value) return;
  try {
    const result = await requestJson("/api/profile/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_id: savedProfiles.value })
    });
    clearDemoSelection();
    resetChatConversation();
    populateQuestionnaire(result.questionnaire_payload);
    renderDashboard(result, false);
    switchPage("dashboardPage");
    showFeedback(`${t("load_saved_profile")} ✓`);
  } catch (error) {
    showFeedback(error.message, true);
  }
});

document.getElementById("deleteSavedProfile").addEventListener("click", async () => {
  if (!savedProfiles.value) return;
  if (!window.confirm(`${t("delete_profile")}?`)) return;
  try {
    await requestJson("/api/profile/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_id: savedProfiles.value })
    });
    profileComparison.hidden = true;
    await refreshSavedProfiles();
    showFeedback(`${t("delete_profile")} ✓`);
  } catch (error) {
    showFeedback(error.message, true);
  }
});

document.getElementById("compareProfiles").addEventListener("click", async () => {
  if (!savedProfiles.value || !compareProfile.value || savedProfiles.value === compareProfile.value) {
    showFeedback(`${t("compare_profiles")}: 2`, true);
    return;
  }
  try {
    const result = await requestJson("/api/profile/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ older_id: compareProfile.value, newer_id: savedProfiles.value })
    });
    const comparison = result.comparison;
    const list = (items) => escapeHtml((items || []).join(", ") || "-");
    const delta = comparison.score_delta > 0 ? `+${comparison.score_delta}` : comparison.score_delta;
    profileComparison.innerHTML = `
          <h3>${escapeHtml(comparison.company_name || "")}</h3>
          <p><strong>${escapeHtml(t("compliance_score"))}:</strong> ${escapeHtml(comparison.older_score)} → ${escapeHtml(comparison.newer_score)} (${escapeHtml(delta)})</p>
          <p><strong>+ ${escapeHtml(t("relevant_tags"))}:</strong> ${list(comparison.added_tags)}</p>
          <p><strong>− ${escapeHtml(t("relevant_tags"))}:</strong> ${list(comparison.removed_tags)}</p>
          <p><strong>✓ ${escapeHtml(t("missing_controls"))}:</strong> ${list(comparison.resolved_controls)}</p>
          <p><strong>+ ${escapeHtml(t("missing_controls"))}:</strong> ${list(comparison.new_missing_controls)}</p>
        `;
    profileComparison.hidden = false;
    showFeedback(`${t("compare_profiles")} ✓`);
  } catch (error) {
    showFeedback(error.message, true);
  }
});

document.querySelectorAll("[data-report-format]").forEach((button) => {
  button.addEventListener("click", async () => {
    if (!currentContext) {
      alert(t("load_profile_first"));
      return;
    }
    button.disabled = true;
    try {
      const response = await fetch("/api/export-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          format: button.dataset.reportFormat,
          language: currentLanguage,
          questionnaire_payload: currentContext.questionnaire_payload
        })
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Report export failed.");
      }
      const disposition = response.headers.get("content-disposition") || "";
      const filenameMatch = disposition.match(/filename="([^"]+)"/i);
      const filename = filenameMatch?.[1]
        || `compliance-report.${button.dataset.reportFormat === "docx" ? "docx" : "pdf"}`;
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      document.querySelectorAll("[data-report-format]").forEach((item) => {
        item.classList.toggle("active-export", item === button);
      });
      showFeedback(`${t("export_report")} ✓`);
    } catch (error) {
      showFeedback(error.message, true);
    } finally {
      button.disabled = false;
    }
  });
});

refreshSavedProfiles().catch(() => {
  savedProfiles.innerHTML = `<option value="" data-i18n="saved_profiles">${t("saved_profiles")}</option>`;
  compareProfile.innerHTML = `<option value="" data-i18n="compare_with">${t("compare_with")}</option>`;
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    document.getElementById("sendChat").click();
  }
});
