const checkpointTime = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(date);
};

function ensureCheckpointStyles() {
  if (document.querySelector('link[data-checkpoint-styles]')) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = './checkpoints.css';
  link.dataset.checkpointStyles = 'true';
  document.head.appendChild(link);
}

function findCard(project, issue) {
  const cards = [...document.querySelectorAll(".workflow-card, .attention-card")];
  return cards.find((card) => {
    const heading = card.querySelector("h3")?.textContent || "";
    const meta = card.querySelector(".workflow-meta, .attention-meta")?.textContent || "";
    return heading.trim().startsWith(`#${issue} `) && meta.includes(project);
  });
}

function checkpointMarkup(checkpoints) {
  if (!checkpoints?.length) return "";
  const latest = checkpoints[0];
  const history = checkpoints.slice(1);
  return `
    <div class="checkpoint-note">
      <div class="checkpoint-kicker"><span class="checkpoint-dot checkpoint-${latest.kind}"></span>Latest checkpoint <span>${checkpointTime(latest.at)}</span></div>
      <strong>${latest.title}</strong>
      <p>${latest.note}</p>
      ${latest.url ? `<a href="${latest.url}" target="_blank" rel="noreferrer">Source ↗</a>` : ""}
      ${history.length ? `<details><summary>History (${history.length})</summary><div class="checkpoint-history">${history.map((item) => `
        <div class="checkpoint-history-item">
          <span>${checkpointTime(item.at)}</span>
          <div><strong>${item.title}</strong><p>${item.note}</p></div>
        </div>`).join("")}</div></details>` : ""}
    </div>
  `;
}

async function loadCheckpoints() {
  ensureCheckpointStyles();
  try {
    const response = await fetch("./checkpoints.json", { cache: "no-store" });
    if (!response.ok) return;
    const data = await response.json();
    const items = data.items || [];

    // app.js renders cards asynchronously; wait briefly until they exist.
    for (let attempt = 0; attempt < 20; attempt += 1) {
      let inserted = 0;
      for (const item of items) {
        if (!item.checkpoints?.length) continue;
        const card = findCard(item.project, item.issue);
        if (!card || card.querySelector(".checkpoint-note")) continue;
        const foot = card.querySelector(".workflow-foot");
        const wrapper = document.createElement("div");
        wrapper.innerHTML = checkpointMarkup(item.checkpoints);
        const note = wrapper.firstElementChild;
        if (foot) card.insertBefore(note, foot);
        else card.appendChild(note);
        inserted += 1;
      }
      if (inserted || document.querySelector(".workflow-card, .attention-card")) break;
      await new Promise((resolve) => setTimeout(resolve, 150));
    }
  } catch (_) {}
}

loadCheckpoints();
