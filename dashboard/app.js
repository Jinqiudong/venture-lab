const healthLabel = { green: "Stable", yellow: "Watch", red: "At risk" };
const stageOrder = ["Issue", "Branch", "PR", "CI", "Review", "Merge"];
let dashboardData = null;

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
  if (stage === "Issue") return "done";
  if (status === "blocked" || status === "ready" || status === "decision") return "todo";
  if (stage === "Branch") return ["coding", "ci", "review", "merged", "done"].includes(status) ? "done" : "todo";
  if (stage === "PR") return item.pr ? "done" : (status === "coding" ? "current" : "todo");
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

const itemIssueLink = (item) => {
  if (item.issue_url) return item.issue_url;
  if (item.repo && item.issue) return `https://github.com/${item.repo}/issues/${item.issue}`;
  if (item.repo) return `https://github.com/${item.repo}`;
  return "#";
};

const attentionCard = (item) => {
  const link = itemIssueLink(item);
  return `
    <article class="attention-card searchable" data-search="${[item.project_name, item.title, item.next_action, statusLabel(item.workflow_stage)].join(" ").toLowerCase()}">
      <div>
        <div class="attention-meta">${item.project_name} / ${statusLabel(item.workflow_stage)}</div>
        <h3>${item.title || "Work item"}</h3>
        <p>${item.next_action || "Pick the next move"}</p>
      </div>
      <a href="${link}" target="_blank" rel="noreferrer">Open ↗</a>
    </article>
  `;
};

const workflowCard = (item) => {
  const blocked = item.blocked_by?.length ? `Blocked by ${item.blocked_by.map((n) => `#${n}`).join(", ")}` : "";
  const issueLink = itemIssueLink(item);
  const search = [item.project_name, item.project_stage, item.issue ? `#${item.issue}` : "", item.title, item.next_action, statusLabel(item.workflow_stage), blocked].join(" ").toLowerCase();
  return `
    <article class="workflow-card searchable ${item.workflow_stage === "blocked" ? "is-blocked" : ""}" data-search="${search}">
      <div class="workflow-head">
        <div>
          <div class="workflow-meta">${item.project_name} / ${item.project_stage}</div>
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
          <a href="${issueLink}" target="_blank" rel="noreferrer">Issue ↗</a>
          ${item.pr_url ? `<a href="${item.pr_url}" target="_blank" rel="noreferrer">PR #${item.pr} ↗</a>` : ""}
        </div>
      </div>
    </article>
  `;
};

const projectCard = (project) => {
  const search = [project.name, project.repo, project.stage, project.current_focus, project.health].join(" ").toLowerCase();
  return `
    <article class="portfolio-card searchable" data-search="${search}">
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
        <span>${project.live ? "synced" : "fallback"}</span>
      </div>
      <a class="repo-link" href="https://github.com/${project.repo}" target="_blank" rel="noreferrer">Open repo ↗</a>
    </article>
  `;
};

function applyFilter(query) {
  const normalized = (query || "").trim().toLowerCase();
  document.querySelectorAll(".searchable").forEach((node) => {
    const haystack = node.dataset.search || "";
    node.classList.toggle("filtered-out", normalized && !haystack.includes(normalized));
  });
}

function wireSearch() {
  const input = document.querySelector("#command-search");
  if (!input) return;
  input.addEventListener("input", (event) => applyFilter(event.target.value));
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      input.value = button.dataset.filter || "";
      applyFilter(input.value);
      input.focus();
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== input) {
      event.preventDefault();
      input.focus();
    }
  });
}

async function loadDashboard() {
  const attentionNode = document.querySelector("#attention-list");
  const workflowsNode = document.querySelector("#workflows");
  const projectsNode = document.querySelector("#projects-grid");
  const updatedNode = document.querySelector("#updated");

  try {
    const response = await fetch("./data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    dashboardData = await response.json();

    const needsYou = dashboardData.needs_you || [];
    const workItems = dashboardData.work_items || (dashboardData.projects || []).flatMap((p) => p.work_items || []);

    attentionNode.innerHTML = needsYou.length
      ? needsYou.map(attentionCard).join("")
      : `<div class="empty-state">Nothing needs you right now.</div>`;

    workflowsNode.innerHTML = workItems.length
      ? workItems.map(workflowCard).join("")
      : `<div class="empty-state">Nothing is on the burner yet.</div>`;

    projectsNode.innerHTML = (dashboardData.projects || []).map(projectCard).join("");
    updatedNode.textContent = `Synced ${formatDate(dashboardData.generated_at)}`;
    wireSearch();
  } catch (error) {
    updatedNode.textContent = "Sync failed";
    attentionNode.innerHTML = `<div class="empty-state">Could not load dashboard data.</div>`;
    workflowsNode.innerHTML = `<div class="empty-state">Workflow data is unavailable.</div>`;
    projectsNode.innerHTML = `<div class="empty-state">Project data is unavailable.</div>`;
    wireSearch();
  }
}

loadDashboard();
