const STRINGS = {
  en: {
    "nav.projects": "Projects",
    "nav.shipped": "Shipped",
    "hero.line1": "Ideas in,",
    "hero.line2": "products out.",
    "hero.lede": "Your AI team builds, reviews, and ships on its own. Here is where every project stands.",
    "stat.projects": "projects",
    "stat.shipped": "shipped in 7 days",
    "stat.active": "being worked on now",
    "projects.eyebrow": "Portfolio",
    "projects.title": "Every project at a glance",
    "shipped.eyebrow": "Shipped",
    "shipped.title": "What the team finished",
    "range.3": "3 days",
    "range.7": "7 days",
    "kind.idea": "Incubating",
    "progress": "{done} of {total} done",
    "chip.active": "{n} in progress",
    "chip.shipped": "{n} shipped this week",
    "chip.hold": "{n} on hold",
    "pipeline.ok": "AI team is running",
    "pipeline.failing": "AI team is stuck: runs keep failing",
    "pipeline.unknown": "AI team status unknown",
    "shipped.empty": "Nothing shipped in this window yet.",
    "updated": "Updated {when}",
    "stage.idea": "Idea",
    "stage.explore": "Explore",
    "stage.validate": "Validate",
    "stage.build": "Build",
    "stage.beta": "Beta",
    "stage.launch": "Launch",
  },
  zh: {
    "nav.projects": "项目",
    "nav.shipped": "已完成",
    "hero.line1": "想法丢进去，",
    "hero.line2": "产品端出来。",
    "hero.lede": "AI 团队自己写代码、审查、上线。每个项目走到哪一步，这里一眼就能看到。",
    "stat.projects": "个项目",
    "stat.shipped": "7 天内完成",
    "stat.active": "正在进行",
    "projects.eyebrow": "项目总览",
    "projects.title": "所有项目，一眼看清",
    "shipped.eyebrow": "已完成",
    "shipped.title": "团队最近做完了什么",
    "range.3": "3 天",
    "range.7": "7 天",
    "kind.idea": "孵化中",
    "progress": "已完成 {done} / {total}",
    "chip.active": "{n} 项进行中",
    "chip.shipped": "本周完成 {n} 项",
    "chip.hold": "{n} 项暂停",
    "pipeline.ok": "AI 团队运转正常",
    "pipeline.failing": "AI 团队卡住了：连续运行失败",
    "pipeline.unknown": "AI 团队状态未知",
    "shipped.empty": "这段时间还没有完成的内容。",
    "updated": "更新于 {when}",
    "stage.idea": "想法",
    "stage.explore": "探索",
    "stage.validate": "验证",
    "stage.build": "开发",
    "stage.beta": "内测",
    "stage.launch": "上线",
  },
};

const LIFECYCLE = ["idea", "explore", "validate", "build", "beta", "launch"];
const ACTIVE_STAGES = ["coding", "building", "ci", "review", "reviewing", "qa", "changes_requested"];

const store = {
  get(key) { try { return localStorage.getItem(key); } catch { return null; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch { /* storage unavailable */ } },
};

let lang = store.get("lang") || ((navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en");
let range = Number(store.get("range")) || 7;
let data = null;

const t = (key, vars = {}) =>
  (STRINGS[lang][key] ?? STRINGS.en[key] ?? key).replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");

const escapeHtml = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);

const relative = (iso) => {
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "";
  const seconds = (then.getTime() - Date.now()) / 1000;
  const rtf = new Intl.RelativeTimeFormat(lang === "zh" ? "zh-CN" : "en", { numeric: "auto" });
  const units = [["day", 86400], ["hour", 3600], ["minute", 60]];
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size || unit === "minute") return rtf.format(Math.round(seconds / size), unit);
  }
  return "";
};

const allProjects = () => [...(data?.projects || []).filter((p) => p.dashboard !== false), ...(data?.ideas || [])];

const shippedWithin = (days) => {
  const since = Date.now() - days * 86400 * 1000;
  return (data?.projects || [])
    .flatMap((project) => (project.recent_merged || []).map((pr) => ({ ...pr, project: project.name, repo: project.repo })))
    .filter((pr) => new Date(pr.merged_at).getTime() >= since)
    .sort((a, b) => b.merged_at.localeCompare(a.merged_at));
};

const activeItems = (project) => (project.work_items || []).filter((item) => ACTIVE_STAGES.includes(item.workflow_stage));

function renderStatic() {
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-lang]").forEach((el) => el.classList.toggle("on", el.dataset.lang === lang));
  document.querySelectorAll("[data-range]").forEach((el) => el.classList.toggle("on", Number(el.dataset.range) === range));
}

function renderPipeline() {
  const status = data?.pipeline?.status || "unknown";
  const pill = document.getElementById("pipeline-pill");
  pill.className = `pill ${status}`;
  document.getElementById("pipeline-text").textContent = t(`pipeline.${status}`);
}

function renderStats() {
  const projects = allProjects();
  document.getElementById("stat-projects").textContent = projects.length;
  document.getElementById("stat-shipped").textContent = shippedWithin(7).length;
  document.getElementById("stat-active").textContent = projects.reduce((sum, p) => sum + activeItems(p).length, 0);
}

function timeline(current) {
  const index = LIFECYCLE.indexOf(current);
  return `<div class="timeline">${LIFECYCLE.map((stage, i) => {
    const state = i < index ? "done" : i === index ? "now" : "";
    return `<div class="step ${state}"><i></i><small>${t(`stage.${stage}`)}</small></div>`;
  }).join("")}</div>`;
}

function projectCard(project) {
  const progress = project.progress || { done: 0, total: 0 };
  const percent = progress.total ? Math.round((progress.done / progress.total) * 100) : 0;
  const focus = (lang === "zh" && project.current_focus_zh) || project.current_focus || "";
  const active = activeItems(project).length;
  const shipped = (project.recent_merged || []).length;
  const held = (project.work_items || []).filter((item) => item.workflow_stage === "hold").length;
  const href = project.repo ? `https://github.com/${project.repo}` : project.issue_url || "#";
  const chips = [
    active ? `<span class="chip live">${t("chip.active", { n: active })}</span>` : "",
    shipped ? `<span class="chip">${t("chip.shipped", { n: shipped })}</span>` : "",
    held ? `<span class="chip">${t("chip.hold", { n: held })}</span>` : "",
  ].join("");
  return `
    <article class="card">
      <a class="card-link" href="${escapeHtml(href)}" target="_blank" rel="noopener" aria-label="${escapeHtml(project.name)}"></a>
      <div class="card-top">
        <h3>${escapeHtml(project.name)}</h3>
        ${project.kind === "idea" ? `<span class="tag idea">${t("kind.idea")}</span>` : ""}
      </div>
      <p class="focus">${escapeHtml(focus)}</p>
      ${timeline(project.lifecycle || "idea")}
      ${progress.total ? `<div class="meter"><div class="bar"><b style="width:${percent}%"></b></div><span>${t("progress", progress)}</span></div>` : ""}
      ${chips ? `<div class="card-foot">${chips}</div>` : ""}
    </article>`;
}

function renderProjects() {
  const order = (p) => -LIFECYCLE.indexOf(p.lifecycle || "idea");
  const projects = allProjects().sort((a, b) => order(a) - order(b));
  document.getElementById("project-grid").innerHTML = projects.map(projectCard).join("");
}

function renderShipped() {
  const items = shippedWithin(range);
  document.getElementById("shipped-list").innerHTML = items.length
    ? items.map((pr) => `
        <li><a href="${escapeHtml(pr.url)}" target="_blank" rel="noopener">
          <span class="check">✓</span>
          <span class="title">${escapeHtml(pr.title)}</span>
          <span class="chip">${escapeHtml(pr.project)}</span>
          <span class="when">${relative(pr.merged_at)}</span>
        </a></li>`).join("")
    : `<li class="empty">${t("shipped.empty")}</li>`;
}

function render() {
  renderStatic();
  if (!data) return;
  renderPipeline();
  renderStats();
  renderProjects();
  renderShipped();
  document.getElementById("updated").textContent = t("updated", { when: relative(data.generated_at) });
}

document.querySelectorAll("[data-lang]").forEach((button) => button.addEventListener("click", () => {
  lang = button.dataset.lang;
  store.set("lang", lang);
  render();
}));
document.querySelectorAll("[data-range]").forEach((button) => button.addEventListener("click", () => {
  range = Number(button.dataset.range);
  store.set("range", String(range));
  render();
}));

render();
fetch("data.json", { cache: "no-store" })
  .then((response) => response.json())
  .then((json) => { data = json; render(); })
  .catch(() => { document.getElementById("updated").textContent = "data.json unavailable"; });
