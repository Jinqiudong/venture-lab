const healthLabel = { green: "Healthy", yellow: "Watch", red: "At risk" };
const stageOrder = ["Issue", "Branch", "PR", "CI", "Review", "Merge"];

const formatDate = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(date);
};

const statusLabel = (status) => ({
  ready: "Ready",
  decision: "Decision needed",
  blocked: "Blocked",
  review: "In review",
  merged: "Merged",
  done: "Done",
  coding: "Coding",
  ci: "CI running",
}[status] || status || "Unknown");

const stageState = (item, stage) => {
  const status = item.workflow_stage;
  if (stage === "Issue") return item.issue_state === "closed" ? "done" : "done";
  if (status === "blocked" || status === "ready" || status === "decision") return "todo";
  if (stage === "Branch") return ["coding", "ci", "review", "merged", "done"].includes(status) ? "done" : "todo";
  if (stage === "PR") return item.pr ? "done" : (["coding"].includes(status) ? "current" : "todo");
  if (stage === "CI") return status === "ci" ? "current" : (["review", "merged", "done"].includes(status) ? "done" : "todo");
  if (stage === "Review") return status === "review" ? "current" : (["merged", "done"].includes(status) ? "done" : "todo");
  if (stage === "Merge") return ["merged", "done"].includes(status) ? "done" : "todo";
  return "todo";
};

const pipeline = (item) => `
  <div class="pipeline">
    ${stageOrder.map((stage) => {
      const state = stageState(item, stage);
      return `<div class="pipeline-step ${state}"><span class="dot"></span><small>${stage}</small></div>`;
    }).join("")}
  </div>
`;

const attentionCard = (item) => {
  const link = item.issue_url || (item.repo ? `https://github.com/${item.repo}` : "#");
  return `
    <article class="attention-card">
      <div>
        <div class="attention-meta">${item.project_name} · ${statusLabel(item.workflow_stage)}</div>
        <h3>${item.title || "Work item"}</h3>
        <p>${item.next_action || "Review next action"}</p>
      </div>
      <a href="${link}" target="_blank" rel="noreferrer">Open →</a>
    </article>
  `;
};

const workflowCard = (item) => {
  const blocked = item.blocked_by?.length ? `Blocked by ${item.blocked_by.map((n) => `#${n}`).join(", ")}` : "";
  const issueLink = item.issue_url || (item.issue ? `https://github.com/${item.repo}/issues/${item.issue}` : `https://github.com/${item.repo}`);
  return `
    <article class="workflow-card ${item.workflow_stage === "blocked" ? "is-blocked" : ""}">
      <div class="workflow-head">
        <div>
          <div class="workflow-meta">${item.project_name} · ${item.project_stage}</div>
          <h3>${item.issue ? `#${item.issue} ` : ""}${item.title || "Work item"}</h3>
        </div>
        <span class="status status-${item.workflow_stage}">${statusLabel(item.workflow_stage)}</span>
      </div>
      ${pipeline(item)}
      <div class="workflow-foot">
        <div>
          <strong>${item.next_action || "No next action set"}</strong>
          ${blocked ? `<span>${blocked}</span>` : ""}
        </div>
        <div class="workflow-links">
          <a href="${issueLink}" target="_blank" rel="noreferrer">Issue</a>
          ${item.pr_url ? `<a href="${item.pr_url}" target="_blank" rel="noreferrer">PR #${item.pr}</a>` : ""}
        </div>
      </div>
    </article>
  `;
};

const projectCard = (project) => `
  <article class="portfolio-card">
    <div class="portfolio-topline">
      <div>
        <div class="repo">${project.repo}</div>
        <h3>${project.name}</h3>
      </div>
      <span class="health health-${project.health}">${healthLabel[project.health] || project.health}</span>
    </div>
    <div class="stage">${project.stage}</div>
    <p>${project.current_focus}</p>
    <div class="portfolio-stats">
      <span>${project.open_issues ?? "—"} issues</span>
      <span>${project.open_prs ?? "—"} PRs</span>
      <span>${project.live ? "Live" : "Fallback"}</span>
    </div>
    <a class="repo-link" href="https://github.com/${project.repo}" target="_blank" rel="noreferrer">Open repo →</a>
  </article>
`;

async function loadDashboard() {
  const attentionNode = document.querySelector("#attention");
  const workflowsNode = document.querySelector("#workflows");
  const projectsNode = document.querySelector("#projects");
  const updatedNode = document.querySelector("#updated");

  try {
    const response = await fetch("data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    const needsYou = data.needs_you || [];
    const workItems = data.work_items || data.projects.flatMap((p) => p.work_items || []);

    attentionNode.innerHTML = needsYou.length
      ? needsYou.map(attentionCard).join("")
      : `<div class="empty-state">Nothing needs your attention right now.</div>`;

    workflowsNode.innerHTML = workItems.length
      ? workItems.map(workflowCard).join("")
      : `<div class="empty-state">No active work items configured.</div>`;

    projectsNode.innerHTML = data.projects.map(projectCard).join("");
    updatedNode.textContent = `Updated ${formatDate(data.generated_at)}`;
  } catch (error) {
    updatedNode.textContent = "Dashboard data unavailable";
    workflowsNode.innerHTML = `<div class="empty-state">Could not load workflow data.</div>`;
  }
}

loadDashboard();
