/**
 * Progress view derived exclusively from the current deterministic assessment.
 * It visualises existing results and never recalculates legal risk or compliance.
 */
const progressEmpty = document.getElementById("progressEmpty");
const progressContent = document.getElementById("progressContent");
const progressMetrics = document.getElementById("progressMetrics");
const controlCoverageChart = document.getElementById("controlCoverageChart");
const priorityDistributionChart = document.getElementById("priorityDistributionChart");
const deadlineOutlook = document.getElementById("deadlineOutlook");
const actionPlanSummary = document.getElementById("actionPlanSummary");
const actionPlanFeedback = document.getElementById("actionPlanFeedback");
const actionPlanList = document.getElementById("actionPlanList");
let currentActionPlan = null;
let actionPlanRequestVersion = 0;

const actionStatuses = [
  ["proposed", "Proposed"],
  ["approved", "Approved"],
  ["in_progress", "In progress"],
  ["completed", "Completed"]
];

const progressControlLabels = {
  privacy_policy: "Privacy policy",
  records_processing: "Records of processing",
  dpo_privacy_owner: "DPO or privacy owner",
  dpia_process: "DPIA process",
  breach_process: "Data breach process",
  data_subject_rights: "Data subject rights process",
  vendor_review: "Vendor review",
  ai_documentation: "AI system documentation",
  human_oversight: "Human oversight",
  ai_policy: "Internal AI policy",
  training: "AI or privacy training"
};

function progressNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function isUpcomingMilestone(item) {
  const daysRemaining = progressNumber(item?.days_remaining);
  return daysRemaining !== null && daysRemaining >= 0;
}

function renderProgressMetric(label, value, detail, level = "") {
  return `
    <article class="progress-metric ${escapeHtml(level)}">
      <span class="progress-metric-label">${escapeHtml(label)}</span>
      <strong class="progress-metric-value">${escapeHtml(value)}</strong>
      <span class="status">${escapeHtml(detail)}</span>
    </article>
  `;
}

function renderProgressList(items, emptyText = "-") {
  if (!items.length) return `<p class="status">${escapeHtml(emptyText)}</p>`;
  return `<ul class="progress-detail-list">
    ${items.map((item) => {
      const label = progressControlLabels[item] || item;
      return `<li>${escapeHtml(trResult(label))}</li>`;
    }).join("")}
  </ul>`;
}

function renderDonut(segments, centerLabel, ariaLabel) {
  let offset = 0;
  const circles = segments.map((segment) => {
    const length = Math.max(0, Math.min(100, segment.percentage));
    const circle = `<circle class="donut-segment ${escapeHtml(segment.className)}"
      cx="21" cy="21" r="15.9155"
      stroke-dasharray="${length} ${100 - length}"
      stroke-dashoffset="${-offset}"
      transform="rotate(-90 21 21)"></circle>`;
    offset += length;
    return circle;
  }).join("");

  return `<svg class="progress-donut" viewBox="0 0 42 42"
    role="img" aria-label="${escapeHtml(ariaLabel)}">
    <circle class="donut-track" cx="21" cy="21" r="15.9155"></circle>
    ${circles}
    <circle class="donut-center" cx="21" cy="21" r="11.6"></circle>
    <text class="donut-label" x="21" y="22.3">${escapeHtml(centerLabel)}</text>
  </svg>`;
}

function renderControlCoverage(memory) {
  const existingControls = Array.isArray(memory.controls?.existing) ? memory.controls.existing : [];
  const missingControls = Array.isArray(memory.controls?.missing_or_to_verify)
    ? memory.controls.missing_or_to_verify
    : [];
  const total = existingControls.length + missingControls.length;
  const percentage = total ? Math.round((existingControls.length / total) * 100) : 100;

  controlCoverageChart.innerHTML = `
    <div class="coverage-layout">
      ${renderDonut(
        [{ className: "coverage", percentage }],
        `${percentage}%`,
        `${t("control_coverage")}: ${percentage}%`
      )}
      <div class="coverage-legend">
        <div class="coverage-legend-row">
          <span><i class="legend-dot"></i>${escapeHtml(t("existing_controls"))}</span>
          <strong>${existingControls.length}</strong>
        </div>
        <div class="coverage-legend-row">
          <span><i class="legend-dot missing"></i>${escapeHtml(t("missing_controls"))}</span>
          <strong>${missingControls.length}</strong>
        </div>
        <p class="status">${escapeHtml(t("progress_disclaimer"))}</p>
      </div>
    </div>
    <div class="control-details-grid">
      <section class="progress-detail-group existing">
        <h3><i class="legend-dot"></i>${escapeHtml(t("existing_controls"))}</h3>
        ${renderProgressList(existingControls)}
      </section>
      <section class="progress-detail-group missing">
        <h3><i class="legend-dot missing"></i>${escapeHtml(t("missing_controls"))}</h3>
        ${renderProgressList(missingControls, t("no_missing_controls"))}
      </section>
    </div>
  `;
}

function renderPriorityDistribution(context) {
  const priorities = { high: [], medium: [], low: [] };
  (context.risk_warnings || []).forEach((warning) => {
    const level = String(warning.level || "low").toLowerCase();
    (priorities[level] || priorities.low).push(warning);
  });

  const levels = ["high", "medium", "low"];
  const total = levels.reduce((sum, level) => sum + priorities[level].length, 0);
  const ariaLabel = levels
    .map((level) => `${trResult(level)}: ${priorities[level].length}`)
    .join(", ");
  const segments = total
    ? levels.map((level) => ({
      className: level,
      percentage: (priorities[level].length / total) * 100
    }))
    : [];

  priorityDistributionChart.innerHTML = `
    <div class="priority-pie-layout">
      ${renderDonut(segments, total, ariaLabel)}
      <div class="priority-legend">
        ${levels.map((level) => `
          <section class="priority-legend-group ${level}">
            <div class="priority-legend-heading">
              <span><i class="legend-dot ${level}"></i>${escapeHtml(trResult(level))}</span>
              <strong>${priorities[level].length}</strong>
            </div>
            ${priorities[level].length
              ? `<ul class="progress-detail-list">${priorities[level]
                .map((warning) => `<li>${escapeHtml(trResult(warning.title || ""))}</li>`)
                .join("")}</ul>`
              : `<p class="status">-</p>`}
          </section>
        `).join("")}
      </div>
    </div>
  `;
}

function renderDeadlineOutlook(context) {
  const milestones = (context.compliance_timeline || [])
    .filter(isUpcomingMilestone)
    .sort((left, right) => String(left.date).localeCompare(String(right.date)))
    .slice(0, 4);
  if (!milestones.length) {
    deadlineOutlook.innerHTML = `<p class="status">${escapeHtml(t("no_match"))}</p>`;
    return;
  }
  deadlineOutlook.innerHTML = `<div class="deadline-list">${milestones.map((item) => {
    const date = new Date(`${item.date}T00:00:00`).toLocaleDateString(currentLanguage, {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
    return `<article class="deadline-row">
      <div>
        <span class="deadline-date">${escapeHtml(date)}</span>
        <h3>${escapeHtml(t(item.translation_key) || item.title)}</h3>
      </div>
      <span class="badge medium">${escapeHtml(t(item.status_code) || item.status)}</span>
    </article>`;
  }).join("")}</div>`;
}

function actionPlanCounts(plan) {
  const counts = Object.fromEntries(actionStatuses.map(([status]) => [status, 0]));
  (plan?.tasks || []).forEach((task) => {
    if (Object.hasOwn(counts, task.status)) counts[task.status] += 1;
  });
  return counts;
}

function renderActionPlan(plan) {
  currentActionPlan = plan;
  const tasks = Array.isArray(plan?.tasks) ? plan.tasks : [];
  const counts = actionPlanCounts(plan);
  actionPlanSummary.innerHTML = `
    <span><strong>${tasks.length}</strong> active</span>
    <span><strong>${counts.approved + counts.in_progress + counts.completed}</strong> approved</span>
    <span><strong>${counts.completed}</strong> completed</span>
  `;
  if (!tasks.length) {
    actionPlanList.innerHTML = "<p class=\"status\">No missing controls require an action plan.</p>";
    return;
  }
  actionPlanList.innerHTML = tasks.map((task) => {
    const isApproved = Boolean(task.approved_at);
    const references = (task.legal_references || [])
      .map((reference) => `<li>${escapeHtml(reference)}</li>`)
      .join("");
    const statusOptions = actionStatuses.map(([value, label]) => `
      <option value="${value}" ${task.status === value ? "selected" : ""}>${label}</option>
    `).join("");
    return `
      <article class="action-task" data-action-task="${escapeHtml(task.id)}">
        <div class="action-task-heading">
          <div>
            <span class="badge ${escapeHtml(task.priority)}">${escapeHtml(trResult(task.priority))}</span>
            <h3>${escapeHtml(trResult(task.title))}</h3>
          </div>
          <span class="action-revision">Revision ${escapeHtml(task.revision)}</span>
        </div>
        <p>${escapeHtml(trResult(task.recommended_action) || "Assign an owner and document the implementation evidence.")}</p>
        ${references ? `<details><summary>Legal basis</summary><ul class="action-reference-list">${references}</ul></details>` : ""}
        <div class="action-fields">
          <label>Status
            <select class="form-select" data-action-field="status">${statusOptions}</select>
          </label>
          <label>Owner
            <input class="form-control" data-action-field="owner" maxlength="4000" value="${escapeHtml(task.owner || "")}" placeholder="e.g. Compliance lead">
          </label>
          <label>Due date
            <input class="form-control" data-action-field="due_date" type="date" value="${escapeHtml(task.due_date || "")}">
          </label>
          <label>Human approver
            <input class="form-control" data-action-field="approved_by" maxlength="4000" value="${escapeHtml(task.approved_by || "")}" ${isApproved ? "disabled" : ""} placeholder="Required when approving">
          </label>
          <label class="action-evidence">Evidence note
            <textarea class="form-control" data-action-field="evidence" maxlength="4000" rows="2" placeholder="Required before completion">${escapeHtml(task.evidence || "")}</textarea>
          </label>
        </div>
        <div class="action-task-footer">
          <span class="status">${isApproved
            ? `Approved by ${escapeHtml(task.approved_by)} · ${escapeHtml(new Date(task.approved_at).toLocaleString(currentLanguage))}`
            : "Human approval pending"}</span>
          <button class="btn btn-primary" type="button" data-save-action="${escapeHtml(task.id)}">Save action</button>
        </div>
      </article>
    `;
  }).join("");
}

async function syncActionPlan(payload) {
  const requestVersion = ++actionPlanRequestVersion;
  actionPlanFeedback.textContent = "Loading action plan...";
  actionPlanList.innerHTML = "";
  try {
    const response = await fetch("/api/action-plan/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionnaire_payload: payload.questionnaire_payload })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to load the action plan.");
    if (requestVersion !== actionPlanRequestVersion) return;
    actionPlanFeedback.textContent = "";
    renderActionPlan(result.action_plan);
  } catch (error) {
    if (requestVersion !== actionPlanRequestVersion) return;
    currentActionPlan = null;
    actionPlanFeedback.textContent = error.message;
    actionPlanList.innerHTML = "";
  }
}

actionPlanList?.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-save-action]");
  if (!button || !currentActionPlan) return;
  const taskElement = button.closest("[data-action-task]");
  if (!taskElement) return;
  const fieldValue = (name) => taskElement.querySelector(`[data-action-field="${name}"]`)?.value || "";
  button.disabled = true;
  actionPlanFeedback.textContent = "Saving action...";
  try {
    const response = await fetch("/api/action-plan/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        plan_id: currentActionPlan.plan_id,
        task_id: button.dataset.saveAction,
        patch: {
          status: fieldValue("status"),
          owner: fieldValue("owner"),
          due_date: fieldValue("due_date"),
          approved_by: fieldValue("approved_by"),
          evidence: fieldValue("evidence")
        }
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to save the action.");
    actionPlanFeedback.textContent = "Action saved with an auditable revision.";
    renderActionPlan(result.action_plan);
  } catch (error) {
    actionPlanFeedback.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

function renderProgress(payload) {
  if (!payload?.dashboard_context || !payload?.company_memory) {
    progressEmpty.hidden = false;
    progressContent.hidden = true;
    currentActionPlan = null;
    actionPlanList.innerHTML = "";
    return;
  }
  const context = payload.dashboard_context;
  const memory = payload.company_memory;
  const score = context.compliance_score || { score: 0, band: "low" };
  const existing = Array.isArray(memory.controls?.existing) ? memory.controls.existing.length : 0;
  const missing = Array.isArray(memory.controls?.missing_or_to_verify)
    ? memory.controls.missing_or_to_verify.length
    : 0;
  const upcoming = (context.compliance_timeline || [])
    .filter(isUpcomingMilestone).length;

  progressEmpty.hidden = true;
  progressContent.hidden = false;
  progressMetrics.innerHTML = [
    renderProgressMetric(t("compliance_score"), `${score.score}/100`, trResult(score.label), score.band),
    renderProgressMetric(t("existing_controls"), existing, t("control_coverage"), "low"),
    renderProgressMetric(t("missing_controls"), missing, t("recommended_action"), missing ? "medium" : "low"),
    renderProgressMetric(t("upcoming_milestones"), upcoming, t("compliance_timeline"), "")
  ].join("");
  renderControlCoverage(memory);
  renderPriorityDistribution(context);
  renderDeadlineOutlook(context);
  syncActionPlan(payload);
}

document.getElementById("progressTab")?.addEventListener("click", () => {
  if (currentContext) renderProgress(currentContext);
});
