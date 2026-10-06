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
  ready: "Ready for Builder",
  decision: "Decision needed",
  human_handoff: "Experience review",
  blocked_on_human: "Waiting on you",
  blocked: "Blocked",
  review: "AI review",
  reviewing: "AI review",
  merged: "Merged",
  done: "Done",
  coding: "Coding",
  building: "Building",
  ci: "CI running",
  qa: "QA",
  changes_requested: "Fixing review findings",
}[status] || status || "Unknown");

const projectSlug = (name = "project") => name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const stageState = (item, stage) => {
  const status = item.workflow_stage;
  if (["merged", "done"].includes(status)) return "done";
  if (stage === "Issue") return "done";
  if (["blocked", "decision", "blocked_on_human"].includes(status)) return "todo";
  if (status === "ready") return stage === "Branch" ? "current" : "todo";
  if (stage === "Branch") return ["coding", "building", "ci", "review", "reviewing", "qa", "human_handoff"].includes(status) ? "done" : "todo";
  if (stage === "PR") return item.pr ? "done" : (["coding", "building"].includes(status) ? "current" : "todo");
  if (stage === "CI") return status === "ci" || status === "qa" ? "current" : (["review", "reviewing", "human_handoff"].includes(status) ? "done" : "todo");
  if (stage === "Review") return ["review", "reviewing"].includes(status) ? "current" : (status === "human_handoff" ? "done" : "todo");
  return "todo";
};

const pipeline = (item) => `
  <div class="pipeline" aria-label="Issue to merge workflow">
    ${stageOrder.map((stage) => {
      const state = stageState(item, stage);
      const mark = state === "done" ? "✓" : "";
      return `<div class="pipeline-step ${state}"><span class="dot">${mark}</span><small>${stage}</small></div>`;
    }).join("")}
  </div>
`;

const issueHref = (item) => {
  if (item.issue_url) return item.issue_url;
  if (item.repo && item.issue) return `https://github.com/${item.repo}/issues/${item.issue}`;
  if (item.repo) return `https://github.com/${item.repo}`;
  return "#";
};

const attentionCard = (item) => {
  const link = item.pr_url || issueHref(item);
  const slug = projectSlug(item.project_name);
  const handoff = item.human_handoff || {};
  const questions = Array.isArray(handoff.questions) && handoff.questions.length
    ? `<ul>${handoff.questions.map((question) => `<li>${question}</li>`).join("")}</ul>`
    : "";
  return `
    <article class="attention-card searchable project-${slug}" data-search="${[item.project_name, item.title, item.next_action, statusLabel(item.workflow_stage)].join(" ").toLowerCase()}">
      <div>
        <div class="attention-meta"><span class="project-dot"></span>${item.project_name} / ${statusLabel(item.workflow_stage)}</div>
        <h3>${handoff.title || item.title || "Work item"}</h3>
        <p>${handoff.what_you_need_to_do || item.next_action || "A product decision is needed."}</p>
        ${handoff.where_to_look ? `<p><strong>Where to look:</strong> ${handoff.where_to_look}</p>` : ""}
        ${questions}
        ${handoff.approve_action ? `<p><strong>If approved:</strong> ${handoff.approve_action}</p>` : ""}
      </div>
      <a href="${link}" target="_blank" rel="noreferrer">Open ↗</a>
    </article>
  `;
};

const workflowCard = (item) => {
  const blocked = item.blocked_by?.length ? `Blocked by ${item.blocked_by.map((n) => `#${n}`).join(", ")}` : "";
  const issueLink = issueHref(item);
  const slug = projectSlug(item.project_name);
  const search = [item.project_name, item.project_stage, item.issue ? `#${item.issue}` : "", item.title, item.next_action, statusLabel(item.workflow_stage), blocked].join(" ").toLowerCase();
  return `
    <article class="workflow-card searchable project-${slug} ${item.workflow_stage === "blocked" ? "is-blocked" : ""} ${["merged", "done"].includes(item.workflow_stage) ? "is-complete" : ""}" data-search="${search}">
      <div class="workflow-head">
        <div><div class="workflow-meta"><span class="project-dot"></span>${item.project_name} / ${item.project_stage}</div><h3>${item.issue ? `#${item.issue} ` : ""}${item.title || "Work item"}</h3></div>
        <span class="status status-${item.workflow_stage}">${["merged", "done"].includes(item.workflow_stage) ? "✓ " : ""}${statusLabel(item.workflow_stage)}</span>
      </div>
      ${pipeline(item)}
      <div class="workflow-foot">
        <div><strong>${["merged", "done"].includes(item.workflow_stage) ? "Completed" : (item.next_action || "AI team owns the next move")}</strong>${blocked ? `<span>${blocked}</span>` : ""}</div>
        <div class="workflow-links"><a href="${issueLink}" target="_blank" rel="noreferrer">Issue ↗</a>${item.pr_url ? `<a href="${item.pr_url}" target="_blank" rel="noreferrer">PR #${item.pr} ↗</a>` : ""}</div>
      </div>
    </article>
  `;
};

const workflowGroups = (items) => {
  const groups = new Map();
  for (const item of items) {
    const name = item.project_name || "Other";
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push(item);
  }
  return [...groups.entries()].map(([name, groupItems]) => {
    const slug = projectSlug(name);
    return `<section class="project-workflow-group project-${slug}"><div class="project-group-head"><div><span class="project-dot"></span><strong>${name}</strong></div><span>${groupItems.length} item${groupItems.length === 1 ? "" : "s"}</span></div><div class="project-workflow-cards">${groupItems.map(workflowCard).join("")}</div></section>`;
  }).join("");
};

const projectCard = (project) => {
  const slug = projectSlug(project.name);
  const search = [project.name, project.repo, project.stage, project.current_focus, project.health].join(" ").toLowerCase();
  return `
    <article class="portfolio-card searchable project-${slug}" data-search="${search}">
      <div class="portfolio-topline"><div><div class="repo"><span class="project-dot"></span>${project.repo}</div><h3>${project.name}</h3></div><span class="health health-${project.health}">${healthLabel[project.health] || project.health}</span></div>
      <div class="stage">${project.stage}</div><p>${project.current_focus}</p>
      <div class="portfolio-stats"><span>${project.open_issues ?? "—"} issues</span><span>${project.open_prs ?? "—"} PRs</span><span>${project.live ? "synced" : "fallback"}</span></div>
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
  document.querySelectorAll(".project-workflow-group").forEach((group) => {
    const visibleCards = [...group.querySelectorAll(".workflow-card")].some((card) => !card.classList.contains("filtered-out"));
    group.classList.toggle("filtered-out", normalized && !visibleCards);
  });
}

function wireSearch() {
  const input = document.querySelector("#command-search");
  if (!input) return;
  input.addEventListener("input", (event) => applyFilter(event.target.value));
  document.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => {
    input.value = button.dataset.filter || "";
    applyFilter(input.value);
    input.focus();
  }));
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== input) {
      event.preventDefault();
      input.focus();
    }
  });
}

async function loadDashboard() {
  const attentionNode = document.querySelector("#attention-list");
  const aiTeamNode = document.querySelector("#ai-team-list");
  const queueNode = document.querySelector("#queue-list");
  const projectsNode = document.querySelector("#projects-grid");
  const updatedNode = document.querySelector("#updated");

  try {
    const response = await fetch("./data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    dashboardData = await response.json();

    const needsYou = dashboardData.needs_you || [];
    const aiTeam = dashboardData.ai_team || [];
    const queue = dashboardData.queue || [];

    attentionNode.innerHTML = needsYou.length ? needsYou.map(attentionCard).join("") : `<div class="empty-state">Nothing needs you right now. The AI team owns the next move.</div>`;
    aiTeamNode.innerHTML = aiTeam.length ? workflowGroups(aiTeam) : `<div class="empty-state">No AI work is active or ready.</div>`;
    queueNode.innerHTML = queue.length ? workflowGroups(queue) : `<div class="empty-state">Queue is clear.</div>`;
    projectsNode.innerHTML = (dashboardData.projects || []).map(projectCard).join("");

    const attentionCount = document.querySelector('#attention-count');
    const aiCount = document.querySelector('#ai-team-count');
    const queueCount = document.querySelector('#queue-count');
    if (attentionCount) attentionCount.textContent = needsYou.length;
    if (aiCount) aiCount.textContent = aiTeam.length;
    if (queueCount) queueCount.textContent = queue.length;

    updatedNode.textContent = `Synced ${formatDate(dashboardData.generated_at)}`;
    wireSearch();
  } catch (error) {
    updatedNode.textContent = "Sync failed";
    attentionNode.innerHTML = `<div class="empty-state">Could not load dashboard data.</div>`;
    aiTeamNode.innerHTML = `<div class="empty-state">AI Team data is unavailable.</div>`;
    queueNode.innerHTML = `<div class="empty-state">Queue data is unavailable.</div>`;
    projectsNode.innerHTML = `<div class="empty-state">Project data is unavailable.</div>`;
    wireSearch();
  }
}

async function loadHeroCat() {
  const img = document.querySelector('.mascot-hero img');
  if (!img) return;
  const fallback = () => {
    img.dataset.removeEdgeWhite = 'true';
    img.src = 'assets/cat-hero.webp';
    setTimeout(() => {
      if (typeof removeEdgeWhite === 'function') removeEdgeWhite(img);
    }, 0);
  };
  try {
    const response = await fetch('./assets/cat-hero-gpt-fixed-small.b64', { cache: 'no-store' });
    if (!response.ok) return fallback();
    const b64 = (await response.text()).replace(/\s+/g, '');
    if (!b64.startsWith('UklG')) return fallback();
    img.onerror = fallback;
    img.src = `data:image/webp;base64,${b64}`;
  } catch (_) {
    fallback();
  }
}

loadHeroCat();
loadDashboard();

const incubationStages = ["SPARK", "EXPLORE", "VALIDATE", "INCUBATE", "BUILD"];

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
}[char]));

const incubationIdeaCard = (idea) => {
  const decision = idea.decision || {};
  const title = idea.title || `Idea #${idea.idea_issue}`;
  const url = `https://github.com/Jinqiudong/venture-lab/issues/${idea.idea_issue}`;
  const guidance = idea.guidance || {};
  const completed = Array.isArray(guidance.completed) ? guidance.completed : [];
  const prompt = guidance.chat_prompt || `Use the Idea Cauldron Product Incubator on Idea #${idea.idea_issue}.`;
  return `<article class="incubation-idea">
    <span class="incubation-idea-meta">#${idea.idea_issue} · ${escapeHtml(idea.stage || "—")} · Step ${escapeHtml(guidance.step || "—")} of ${escapeHtml(guidance.total_steps || 6)}</span>
    <strong>${escapeHtml(title)}</strong>
    <small><b>${escapeHtml(guidance.phase || "Next")}</b> · ${escapeHtml(guidance.current || decision.next_action || "No next action recorded.")}</small>
    ${completed.length ? `<small>✓ ${completed.map(escapeHtml).join(" · ✓ ")}</small>` : ""}
    <div class="workflow-links"><a href="${url}" target="_blank" rel="noreferrer">Idea ↗</a><button type="button" class="copy-incubation-prompt" data-prompt="${escapeHtml(prompt)}">Copy ChatGPT prompt</button></div>
  </article>`;
};

const renderIncubationBoard = (ideas = []) => {
  const board = document.getElementById("incubation-board");
  if (!board) return;
  const active = incubationStages.map((stage) => {
    const stageIdeas = ideas.filter((idea) => idea.stage === stage);
    return `<section class="incubation-column ${stageIdeas.length ? "has-ideas" : ""}">
      <div class="incubation-column-head"><span>${stage}</span><b>${stageIdeas.length}</b></div>
      <div class="incubation-column-body">${stageIdeas.length ? stageIdeas.map(incubationIdeaCard).join("") : '<span class="incubation-empty">—</span>'}</div>
    </section>`;
  }).join("");
  const exits = ["PARK", "REJECT"].map((stage) => {
    const stageIdeas = ideas.filter((idea) => idea.stage === stage);
    return `<section class="incubation-exit"><span>${stage}</span><b>${stageIdeas.length}</b>${stageIdeas.map(incubationIdeaCard).join("")}</section>`;
  }).join("");
  board.innerHTML = `<div class="incubation-lanes">${active}</div><div class="incubation-exit-row">${exits}</div>`;
};

async function loadIncubationBoard() {
  try {
    const response = await fetch("./incubation.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    renderIncubationBoard(Array.isArray(payload.ideas) ? payload.ideas : []);
  } catch (_) {
    const board = document.getElementById("incubation-board");
    if (board) board.innerHTML = '<div class="incubation-loading">Incubation data is unavailable.</div>';
  }
}

loadIncubationBoard();

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-incubation-prompt");
  if (!button) return;
  try {
    await navigator.clipboard.writeText(button.dataset.prompt || "");
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = original; }, 1200);
  } catch (_) {
    button.textContent = "Copy failed";
  }
});
