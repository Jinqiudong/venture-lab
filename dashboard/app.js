const healthLabel = {
  green: "Healthy",
  yellow: "Watch",
  red: "At risk",
};

const ciLabel = (ci) => {
  if (!ci) return "Unknown";
  const normalized = ci.toLowerCase();
  if (normalized === "success") return "Passing";
  if (["failure", "cancelled", "timed_out", "action_required"].includes(normalized)) return "Failing";
  if (["queued", "in_progress", "waiting", "requested", "pending"].includes(normalized)) return "Running";
  if (normalized === "no-runs") return "No runs";
  return ci;
};

const formatDate = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
};

const metric = (label, value) => `
  <div class="metric">
    <span>${label}</span>
    <strong>${value ?? "—"}</strong>
  </div>
`;

const projectCard = (project) => {
  const liveClass = project.live ? "live" : "offline";
  const liveText = project.live ? "Live GitHub data" : "Manual fallback";
  return `
    <article class="project-card">
      <div class="project-topline">
        <div>
          <p class="repo">${project.repo}</p>
          <h3>${project.name}</h3>
        </div>
        <span class="health health-${project.health}">${healthLabel[project.health] ?? project.health}</span>
      </div>

      <div class="stage">${project.stage}</div>
      <p class="focus">${project.current_focus}</p>

      <div class="metrics">
        ${metric("Open issues", project.open_issues)}
        ${metric("Open PRs", project.open_prs)}
        ${metric("CI", ciLabel(project.ci))}
        ${metric("Last push", formatDate(project.latest_activity))}
      </div>

      <div class="source-row">
        <span class="source ${liveClass}">${liveText}</span>
        ${project.error ? `<span class="error-note">${project.error}</span>` : ""}
      </div>

      <a class="repo-link" href="https://github.com/${project.repo}" target="_blank" rel="noreferrer">Open repository →</a>
    </article>
  `;
};

const attentionCard = (project) => `
  <article class="attention-card">
    <div>
      <span class="attention-project">${project.name}</span>
      <p>${project.attention}</p>
    </div>
    <a href="https://github.com/${project.repo}/issues" target="_blank" rel="noreferrer">View issues</a>
  </article>
`;

async function loadDashboard() {
  const projectsNode = document.querySelector("#projects");
  const attentionNode = document.querySelector("#attention");
  const updatedNode = document.querySelector("#updated");

  try {
    const response = await fetch("data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    projectsNode.innerHTML = data.projects.map(projectCard).join("");
    attentionNode.innerHTML = data.projects.filter((p) => p.attention).map(attentionCard).join("");
    updatedNode.textContent = `Updated ${formatDate(data.generated_at)}`;
  } catch (error) {
    updatedNode.textContent = "Dashboard data unavailable";
    projectsNode.innerHTML = `
      <div class="empty-state">
        Could not load portfolio data. Run the dashboard workflow or check the generated data file.
      </div>
    `;
  }
}

loadDashboard();
