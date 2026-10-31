const STRINGS = {
  en: {
    "nav.needs": "Needs you",
    "nav.projects": "Projects",
    "nav.shipped": "Shipped",
    "hero.line1": "Ideas in,",
    "hero.line2": "products out.",
    "hero.lede": "Your AI team builds, reviews, and ships on its own. Here is where every project stands.",
    "stat.projects": "projects",
    "stat.shipped": "shipped in 7 days",
    "stat.active": "being worked on now",
    "needs.eyebrow": "Your inbox",
    "needs.title": "Only what needs you",
    "needs.empty": "Nothing needs you right now. The AI team is moving on its own.",
    "needs.handoff": "Review",
    "needs.accept": "Accept",
    "needs.accept.ask": "The milestone is finished. Try it, then merge it or comment /accept.",
    "needs.decision": "Decide",
    "needs.open": "Open",
    "projects.eyebrow": "Portfolio",
    "projects.title": "Every project at a glance",
    "shipped.eyebrow": "Shipped",
    "shipped.title": "What the team finished",
    "range.3": "3 days",
    "range.7": "7 days",
    "range.30": "30 days",
    "filter.all": "All projects",
    "kind.idea": "Incubating",
    "idea.new": "+ Drop in a new idea",
    "idea.new.short": "+ Idea",
    "idea.hint": "The Product Brain researches it and replies on GitHub with findings and a few questions.",
    "progress": "Planned tasks {done} of {total}",
    "chip.active": "{n} in progress",
    "chip.shipped": "{n} shipped this week",
    "chip.hold": "{n} paused by you",
    "chip.idea": "Idea #{n}",
    "status.needs_you": "Needs you",
    "status.stuck": "AI is stuck",
    "status.stalled": "No activity for 3+ days",
    "status.moving": "Moving",
    "status.quiet": "Nothing queued",
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
    "detail.back": "← All projects",
    "detail.missing": "This project is not in the dashboard data.",
    "detail.links.repo": "GitHub repository",
    "detail.links.idea": "Idea #{n}",
    "detail.board": "Right now",
    "board.you": "Waiting on you",
    "board.stuck": "AI is stuck",
    "board.ai": "AI working",
    "board.queue": "Queued",
    "board.done": "Done",
    "detail.milestones": "Plan",
    "milestones.error": "Milestones could not be loaded from GitHub just now.",
    "milestones.empty": "No milestones with target dates yet, so there is no planned timeline to compare against.",
    "milestone.tasks": "{closed} of {total} tasks",
    "milestone.due": "target {date}",
    "milestone.projected": "at the current pace ≈ {date}",
    "milestone.late": "behind plan",
    "milestone.done": "done",
    "detail.delivery": "Delivery",
    "delivery.chart": "Changes shipped per week, last 8 weeks",
    "delivery.tooltip": "Week of {week}: {n} shipped",
    "delivery.none": "Nothing shipped in the last 8 weeks yet.",
    "tile.shipped30": "shipped in 30 days",
    "tile.pace": "per week, last 4 weeks",
    "tile.cycle": "median time from PR to merge",
    "tile.minutes": "{n} min",
    "tile.hours": "{n} h",
    "tile.days": "{n} d",
    "detail.shipped": "Recently shipped",
    "detail.idea": "How it started",
    "nav.ops": "Operations",
    "ops.title": "How the AI team runs",
    "ops.lede": "Where the last 24 hours went, and how close we are to GitHub and Claude limits.",
    "ops.empty": "The heartbeat started recently. Samples arrive every 10 minutes, so this fills in over the next few hours.",
    "ops.now": "Right now",
    "ops.state.working": "Working",
    "ops.state.idle_with_work": "Idle with work waiting",
    "ops.state.idle": "Nothing to do",
    "ops.state.paused": "Waiting for Claude limit reset",
    "ops.state.api_guard": "Saving GitHub API budget",
    "ops.state.error": "Heartbeat error",
    "ops.resume": "resumes {when}",
    "ops.waiting": "{n} tasks ready",
    "ops.day": "The last 24 hours",
    "ops.day.note": "One cell per 10-minute heartbeat check. Red cells are time lost: work was ready but nothing ran.",
    "ops.share": "{p}%",
    "ops.api": "GitHub API budget",
    "ops.api.note": "All automation and your own tools share one token: {limit} calls per hour. Above 80% this turns red. Below 500 left, the heartbeat stops starting agent work until the hourly reset.",
    "ops.api.now": "This hour: {used} of {limit} used, resets {when}",
    "ops.api.chart": "Peak use per hourly window, last 24 hours",
    "ops.api.tooltip": "Window ending {when}: {used} of {limit}",
    "ops.api.threshold": "80%",
    "ops.claude": "Claude usage",
    "ops.claude.note": "Claude subscriptions don't report a usage percentage that automation can read. When a 5-hour or weekly limit is hit, the heartbeat pauses until the reset time Claude reports and then continues by itself.",
    "ops.claude.hits24": "limit hits, 24 hours",
    "ops.claude.hits7": "limit hits, 7 days",
    "ops.claude.paused": "minutes paused, 24 hours",
    "ops.actions": "GitHub Actions",
    "ops.actions.runs": "workflow runs, 24 hours",
    "ops.actions.perMerge": "runs per merged PR",
    "ops.actions.merged": "PRs merged, 24 hours",
    "ops.actions.minutes": "runner minutes, 24 hours",
    "ops.warn.api_now": "GitHub API use is above 80% this hour.",
    "ops.warn.api_day": "At least one hour in the last day went above 80% of the GitHub API budget.",
    "ops.warn.idle_with_work": "The team sat idle while work was ready. See the red cells.",
    "ops.warn.claude_limit": "A Claude usage limit was hit in the last 24 hours.",
  },
  zh: {
    "nav.needs": "等你处理",
    "nav.projects": "项目",
    "nav.shipped": "已完成",
    "hero.line1": "想法丢进去，",
    "hero.line2": "产品端出来。",
    "hero.lede": "AI 团队自己写代码、审查、上线。每个项目走到哪一步，这里一眼就能看到。",
    "stat.projects": "个项目",
    "stat.shipped": "7 天内完成",
    "stat.active": "正在进行",
    "needs.eyebrow": "你的待办",
    "needs.title": "只放真正需要你的事",
    "needs.empty": "现在没有需要你处理的事，AI 团队在自己推进。",
    "needs.handoff": "需要你看",
    "needs.accept": "待验收",
    "needs.accept.ask": "这个里程碑做完了。试用一下，满意就合并，或者评论 /accept。",
    "needs.decision": "需要你决定",
    "needs.open": "打开",
    "projects.eyebrow": "项目总览",
    "projects.title": "所有项目，一眼看清",
    "shipped.eyebrow": "已完成",
    "shipped.title": "团队最近做完了什么",
    "range.3": "3 天",
    "range.7": "7 天",
    "range.30": "30 天",
    "filter.all": "全部项目",
    "kind.idea": "孵化中",
    "idea.new": "+ 记录一个新想法",
    "idea.new.short": "+ 想法",
    "idea.hint": "AI 产品经理会去做市场调研，然后在 GitHub 上回复你调研结果和几个问题。",
    "progress": "计划任务 {done} / {total}",
    "chip.active": "{n} 项进行中",
    "chip.shipped": "本周完成 {n} 项",
    "chip.hold": "{n} 项被你暂停",
    "chip.idea": "想法 #{n}",
    "status.needs_you": "等你处理",
    "status.stuck": "AI 卡住了",
    "status.stalled": "3 天以上没动静",
    "status.moving": "在推进",
    "status.quiet": "暂无排期",
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
    "detail.back": "← 所有项目",
    "detail.missing": "dashboard 数据里没有这个项目。",
    "detail.links.repo": "GitHub 仓库",
    "detail.links.idea": "想法 #{n}",
    "detail.board": "现在的状态",
    "board.you": "等你",
    "board.stuck": "AI 卡住",
    "board.ai": "AI 在做",
    "board.queue": "排队中",
    "board.done": "已完成",
    "detail.milestones": "计划",
    "milestones.error": "暂时无法从 GitHub 加载里程碑。",
    "milestones.empty": "还没有设定带目标日期的里程碑，所以暂时没有计划时间线可以对照。",
    "milestone.tasks": "{closed} / {total} 项任务",
    "milestone.due": "目标 {date}",
    "milestone.projected": "按当前速度预计 {date}",
    "milestone.late": "落后于计划",
    "milestone.done": "已完成",
    "detail.delivery": "交付",
    "delivery.chart": "每周完成的改动，近 8 周",
    "delivery.tooltip": "{week} 这周：完成 {n} 项",
    "delivery.none": "近 8 周还没有完成的改动。",
    "tile.shipped30": "30 天内完成",
    "tile.pace": "每周，近 4 周平均",
    "tile.cycle": "从提交到合并（中位数）",
    "tile.minutes": "{n} 分钟",
    "tile.hours": "{n} 小时",
    "tile.days": "{n} 天",
    "detail.shipped": "最近完成",
    "detail.idea": "这个项目的由来",
    "nav.ops": "流程监控",
    "ops.title": "AI 团队运转得怎么样",
    "ops.lede": "过去 24 小时时间花在了哪里，以及离 GitHub 和 Claude 的用量上限还有多远。",
    "ops.empty": "心跳刚上线，每 10 分钟记录一次，接下来几个小时数据会慢慢填满。",
    "ops.now": "现在",
    "ops.state.working": "工作中",
    "ops.state.idle_with_work": "有活但没人干",
    "ops.state.idle": "没有可做的",
    "ops.state.paused": "等 Claude 额度恢复",
    "ops.state.api_guard": "节省 GitHub API 额度",
    "ops.state.error": "心跳出错",
    "ops.resume": "{when}恢复",
    "ops.waiting": "{n} 个任务待做",
    "ops.day": "过去 24 小时",
    "ops.day.note": "每格代表一次 10 分钟的心跳检查。红色格子是浪费的时间：有活可干，却没有在跑。",
    "ops.share": "{p}%",
    "ops.api": "GitHub API 额度",
    "ops.api.note": "所有自动化和你自己的工具共用一个 token，每小时 {limit} 次。超过 80% 会变红；剩余不到 500 次时，心跳会暂停启动新的 AI 工作，等到整点额度重置。",
    "ops.api.now": "本小时已用 {used} / {limit}，{when}重置",
    "ops.api.chart": "近 24 小时，每个小时窗口的用量峰值",
    "ops.api.tooltip": "{when}结束的窗口：{used} / {limit}",
    "ops.api.threshold": "80%",
    "ops.claude": "Claude 用量",
    "ops.claude.note": "Claude 订阅没有提供自动化可以读取的用量百分比。触发 5 小时或每周上限时，心跳会暂停到 Claude 报告的恢复时间，然后自动继续。",
    "ops.claude.hits24": "24 小时内触发上限次数",
    "ops.claude.hits7": "7 天内触发上限次数",
    "ops.claude.paused": "24 小时内暂停的分钟数",
    "ops.actions": "GitHub Actions",
    "ops.actions.runs": "24 小时内的工作流运行次数",
    "ops.actions.perMerge": "每合并一个 PR 的运行次数",
    "ops.actions.merged": "24 小时内合并的 PR",
    "ops.actions.minutes": "24 小时内的运行分钟数",
    "ops.warn.api_now": "本小时 GitHub API 用量超过了 80%。",
    "ops.warn.api_day": "过去一天里至少有一个小时，GitHub API 用量超过了 80%。",
    "ops.warn.idle_with_work": "有活可干时团队却闲着，见红色格子。",
    "ops.warn.claude_limit": "过去 24 小时触发过 Claude 用量上限。",
  },
};

const LIFECYCLE = ["idea", "explore", "validate", "build", "beta", "launch"];
const ACTIVE_STAGES = ["coding", "building", "ci", "review", "reviewing", "qa", "changes_requested"];
const DONE_STAGES = ["done", "merged"];
const PAGE = document.body.dataset.page || "home";

const store = {
  get(key) { try { return localStorage.getItem(key); } catch { return null; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch { /* storage unavailable */ } },
};

let lang = new URLSearchParams(location.search).get("lang") || store.get("lang") || ((navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en");
let range = Number(store.get("range")) || 7;
let projectFilter = "all";
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

const shortDate = (iso) => {
  const date = new Date(`${iso}T00:00:00`);
  return Number.isNaN(date.getTime()) ? iso : date.toLocaleDateString(lang === "zh" ? "zh-CN" : "en", { month: "short", day: "numeric" });
};

const projectName = (project) => (lang === "zh" && project.name_zh) || project.name;
const visibleProjects = () => (data?.projects || []).filter((p) => p.dashboard !== false);
const allProjects = () => [...visibleProjects(), ...(data?.ideas || [])];
const projectHref = (project) => project.kind === "idea" ? project.issue_url || "#" : `project.html?p=${encodeURIComponent(project.slug)}`;

const shippedWithin = (days, projects = visibleProjects()) => {
  const since = Date.now() - days * 86400 * 1000;
  return projects
    .flatMap((project) => (project.recent_merged || []).map((pr) => ({ ...pr, project: projectName(project), slug: project.slug })))
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
  const pill = document.getElementById("pipeline-pill");
  if (!pill) return;
  const status = data?.pipeline?.status || "unknown";
  pill.className = `pill ${status}`;
  document.getElementById("pipeline-text").textContent = t(`pipeline.${status}`);
}

function renderStats() {
  const projects = allProjects();
  document.getElementById("stat-projects").textContent = projects.length;
  document.getElementById("stat-shipped").textContent = shippedWithin(7).length;
  document.getElementById("stat-active").textContent = projects.reduce((sum, p) => sum + activeItems(p).length, 0);
}

const statusBadge = (status) => status ? `<span class="status ${status}"><i></i>${t(`status.${status}`)}</span>` : "";

function timeline(current) {
  const index = LIFECYCLE.indexOf(current);
  return `<div class="timeline">${LIFECYCLE.map((stage, i) => {
    const state = i < index ? "done" : i === index ? "now" : "";
    return `<div class="step ${state}"><i></i><small>${t(`stage.${stage}`)}</small></div>`;
  }).join("")}</div>`;
}

const meter = (done, total, label) => {
  const percent = total ? Math.round((done / total) * 100) : 0;
  return `<div class="meter"><div class="bar"><b style="width:${percent}%"></b></div><span>${label}</span></div>`;
};

// The milestone that is still open and due first; the plan line on a card.
const currentMilestone = (project) => (project.milestones || []).find((m) => m.state === "open");

function milestoneLine(milestone) {
  if (!milestone) return "";
  const parts = [escapeHtml(milestone.title)];
  if (milestone.due_on) parts.push(t("milestone.due", { date: shortDate(milestone.due_on) }));
  if (milestone.projected_on) parts.push(t("milestone.projected", { date: shortDate(milestone.projected_on) }));
  const late = milestone.due_on && milestone.projected_on && milestone.projected_on > milestone.due_on;
  return `<p class="plan-line${late ? " late" : ""}">${parts.join(" · ")}${late ? ` · ${t("milestone.late")}` : ""}</p>`;
}

function projectCard(project) {
  const progress = project.progress || { done: 0, total: 0 };
  const focus = (lang === "zh" && project.current_focus_zh) || project.current_focus || "";
  const name = projectName(project);
  const active = activeItems(project).length;
  const shipped = shippedWithin(7, [project]).length;
  const held = (project.work_items || []).filter((item) => item.workflow_stage === "hold").length;
  const external = project.kind === "idea";
  const chips = [
    active ? `<span class="chip live">${t("chip.active", { n: active })}</span>` : "",
    shipped ? `<span class="chip">${t("chip.shipped", { n: shipped })}</span>` : "",
    held ? `<span class="chip">${t("chip.hold", { n: held })}</span>` : "",
    project.idea ? `<a class="chip chip-link" href="${escapeHtml(project.idea.issue_url)}" target="_blank" rel="noopener">${t("chip.idea", { n: project.idea.issue })}</a>` : "",
  ].join("");
  return `
    <article class="card">
      <a class="card-link" href="${escapeHtml(projectHref(project))}"${external ? ' target="_blank" rel="noopener"' : ""} aria-label="${escapeHtml(name)}"></a>
      <div class="card-top">
        <h3>${escapeHtml(name)}</h3>
        ${external ? `<span class="tag idea">${t("kind.idea")}</span>` : statusBadge(project.status)}
      </div>
      <p class="focus">${escapeHtml(focus)}</p>
      ${timeline(project.lifecycle || "idea")}
      ${progress.total ? meter(progress.done, progress.total, t("progress", progress)) : ""}
      ${milestoneLine(currentMilestone(project))}
      ${chips ? `<div class="card-foot">${chips}</div>` : ""}
    </article>`;
}

function needsYouItems(slug) {
  return (data?.needs_you || []).filter((item) => !slug || item.project_slug === slug);
}

function needsYouList(items, withProject = true) {
  if (!items.length) return `<li class="empty">${t("needs.empty")}</li>`;
  return items.map((item) => {
    const url = item.url || item.pr_url || item.issue_url || "#";
    const ask = item.acceptance ? t("needs.accept.ask") : item.kind === "handoff" ? item.ask : item.next_action;
    const label = item.kind === "handoff" ? `PR #${item.pr}` : item.issue ? `#${item.issue}` : "";
    return `
      <li><a href="${escapeHtml(url)}" target="_blank" rel="noopener">
        <span class="ask-kind">${t(item.acceptance ? "needs.accept" : item.kind === "handoff" ? "needs.handoff" : "needs.decision")}</span>
        <span class="ask-body">
          <strong>${escapeHtml(item.title)}</strong>
          ${ask ? `<small>${escapeHtml(ask)}</small>` : ""}
        </span>
        ${withProject ? `<span class="chip">${escapeHtml(item.project_name)}</span>` : ""}
        <span class="when">${escapeHtml(label)}</span>
      </a></li>`;
  }).join("");
}

function renderNeeds() {
  document.getElementById("needs-list").innerHTML = needsYouList(needsYouItems());
  const count = needsYouItems().length;
  document.getElementById("needs-count").textContent = count ? String(count) : "";
}

function renderProjects() {
  const order = (p) => -LIFECYCLE.indexOf(p.lifecycle || "idea");
  const projects = allProjects().sort((a, b) => order(a) - order(b));
  document.getElementById("project-grid").innerHTML = projects.map(projectCard).join("");
}

function shippedItems(items, withProject = true) {
  return items.length
    ? items.map((pr) => `
        <li><a href="${escapeHtml(pr.url)}" target="_blank" rel="noopener">
          <span class="check">✓</span>
          <span class="title">${escapeHtml(pr.title)}</span>
          ${withProject ? `<span class="chip">${escapeHtml(pr.project)}</span>` : ""}
          <span class="when">${relative(pr.merged_at)}</span>
        </a></li>`).join("")
    : `<li class="empty">${t("shipped.empty")}</li>`;
}

function renderShipped() {
  const withWork = visibleProjects().filter((p) => (p.recent_merged || []).length);
  if (projectFilter !== "all" && !withWork.some((p) => p.slug === projectFilter)) projectFilter = "all";
  document.getElementById("project-filter").innerHTML = [
    `<button type="button" data-project="all" class="${projectFilter === "all" ? "on" : ""}">${t("filter.all")}</button>`,
    ...withWork.map((p) => `<button type="button" data-project="${escapeHtml(p.slug)}" class="${projectFilter === p.slug ? "on" : ""}">${escapeHtml(projectName(p))}</button>`),
  ].join("");
  const scope = projectFilter === "all" ? visibleProjects() : visibleProjects().filter((p) => p.slug === projectFilter);
  document.getElementById("shipped-list").innerHTML = shippedItems(shippedWithin(range, scope), projectFilter === "all");
}

/* Project detail page */

function boardColumn(key, items) {
  const list = items.slice(0, 6).map((item) => {
    const url = item.pr_url || item.issue_url || "#";
    return `<li><a href="${escapeHtml(url)}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a></li>`;
  }).join("");
  const more = items.length > 6 ? `<li class="more">+${items.length - 6}</li>` : "";
  return `<div class="col ${key}"><h4><span>${t(`board.${key}`)}</span><strong>${items.length}</strong></h4><ul>${list}${more}</ul></div>`;
}

function board(project) {
  const items = project.work_items || [];
  const stage = (item) => item.workflow_stage;
  const you = [...(project.handoffs || []).map((h) => ({ title: h.title, pr_url: h.url })), ...items.filter((i) => i.needs_human && !["hold", "blocked_on_human", ...DONE_STAGES].includes(stage(i)))];
  return `<div class="board">
    ${boardColumn("you", you)}
    ${boardColumn("stuck", items.filter((i) => stage(i) === "blocked_on_human"))}
    ${boardColumn("ai", items.filter((i) => ACTIVE_STAGES.includes(stage(i)) && !i.needs_human))}
    ${boardColumn("queue", items.filter((i) => ["ready", "blocked"].includes(stage(i)) && !i.needs_human))}
    ${boardColumn("done", items.filter((i) => DONE_STAGES.includes(stage(i))))}
  </div>`;
}

function milestones(project) {
  const list = project.milestones || [];
  if (project.milestones_error) return `<p class="note">${t("milestones.error")}</p>`;
  if (!list.length) return `<p class="note">${t("milestones.empty")}</p>`;
  return `<div class="milestones">${list.map((m) => {
    const total = m.open + m.closed;
    const late = m.due_on && m.projected_on && m.projected_on > m.due_on;
    const when = m.state === "closed" ? t("milestone.done") : [
      m.due_on ? t("milestone.due", { date: shortDate(m.due_on) }) : "",
      m.projected_on ? t("milestone.projected", { date: shortDate(m.projected_on) }) : "",
    ].filter(Boolean).join(" · ");
    return `<div class="milestone${late ? " late" : ""}">
      <div class="milestone-head"><a href="${escapeHtml(m.url)}" target="_blank" rel="noopener">${escapeHtml(m.title)}</a><span>${when}${late ? ` · ${t("milestone.late")}` : ""}</span></div>
      ${meter(m.closed, total, t("milestone.tasks", { closed: m.closed, total }))}
    </div>`;
  }).join("")}</div>`;
}

function weeklyChart(weekly) {
  if (!weekly.some((w) => w.merged)) return weekly.length ? `<p class="note">${t("delivery.none")}</p>` : "";
  const max = Math.max(1, ...weekly.map((w) => w.merged));
  const ticks = [0, Math.ceil(max / 2), max].filter((v, i, all) => all.indexOf(v) === i);
  const bars = weekly.map((w) => {
    const height = (w.merged / max) * 100;
    const tip = t("delivery.tooltip", { week: shortDate(w.week), n: w.merged });
    return `<div class="col-bar" tabindex="0" data-tip="${escapeHtml(tip)}">
      <span class="value">${w.merged || ""}</span>
      <b style="height:${height}%"></b>
      <small>${shortDate(w.week)}</small>
    </div>`;
  }).join("");
  return `<figure class="chart">
    <figcaption>${t("delivery.chart")}</figcaption>
    <div class="plot">
      <div class="grid">${ticks.map((v) => `<span style="bottom:${(v / max) * 100}%"><em>${v}</em></span>`).join("")}</div>
      <div class="bars">${bars}</div>
    </div>
    <div class="tooltip" role="status" hidden></div>
  </figure>`;
}

function deliveryTiles(project) {
  const delivery = project.delivery || {};
  const hours = delivery.median_hours_to_merge;
  const cycle = hours == null ? "–"
    : hours < 1 ? t("tile.minutes", { n: Math.max(1, Math.round(hours * 60)) })
    : hours < 48 ? t("tile.hours", { n: Math.round(hours) })
    : t("tile.days", { n: Math.round(hours / 24) });
  return `<div class="tiles">
    <div class="stat"><strong>${(project.recent_merged || []).length}</strong><span>${t("tile.shipped30")}</span></div>
    <div class="stat"><strong>${delivery.per_week ?? "–"}</strong><span>${t("tile.pace")}</span></div>
    <div class="stat"><strong>${cycle}</strong><span>${t("tile.cycle")}</span></div>
  </div>`;
}

function ideaOrigin(project) {
  if (!project.idea) return "";
  const done = (project.idea.done_steps || []).slice(-5).map((step) => `<li>${escapeHtml(step)}</li>`).join("");
  return `<section class="panel"><h3>${t("detail.idea")}</h3><ul class="steps">${done}</ul></section>`;
}

function renderDetail() {
  const slug = new URLSearchParams(location.search).get("p");
  const project = visibleProjects().find((p) => p.slug === slug);
  const root = document.getElementById("detail");
  if (!project) {
    root.innerHTML = `<p class="note">${t("detail.missing")}</p>`;
    return;
  }
  document.title = `${projectName(project)} · Idea Cauldron`;
  const focus = (lang === "zh" && project.current_focus_zh) || project.current_focus || "";
  const progress = project.progress || { done: 0, total: 0 };
  const links = [
    `<a class="chip chip-link" href="https://github.com/${escapeHtml(project.repo)}" target="_blank" rel="noopener">${t("detail.links.repo")}</a>`,
    project.idea ? `<a class="chip chip-link" href="${escapeHtml(project.idea.issue_url)}" target="_blank" rel="noopener">${t("detail.links.idea", { n: project.idea.issue })}</a>` : "",
  ].join("");
  const needs = needsYouItems(project.slug);
  root.innerHTML = `
    <section class="detail-head">
      <div class="card-top"><h1 class="detail-title">${escapeHtml(projectName(project))}</h1>${statusBadge(project.status)}</div>
      <p class="focus">${escapeHtml(focus)}</p>
      ${timeline(project.lifecycle || "idea")}
      ${progress.total ? meter(progress.done, progress.total, t("progress", progress)) : ""}
      <div class="card-foot">${links}</div>
    </section>
    ${needs.length ? `<section class="panel"><h3>${t("needs.title")}</h3><ol class="needs-list">${needsYouList(needs, false)}</ol></section>` : ""}
    <section class="panel"><h3>${t("detail.board")}</h3>${board(project)}</section>
    <section class="panel"><h3>${t("detail.milestones")}</h3>${milestones(project)}</section>
    <section class="panel"><h3>${t("detail.delivery")}</h3>${deliveryTiles(project)}${weeklyChart((project.delivery || {}).weekly || [])}</section>
    <section class="panel">
      <div class="panel-head"><h3>${t("detail.shipped")}</h3>
        <div class="range" role="group" aria-label="Range">${[7, 30].map((d) => `<button type="button" data-range="${d}" class="${range === d ? "on" : ""}">${t(`range.${d}`)}</button>`).join("")}</div>
      </div>
      <ol class="shipped-list">${shippedItems(shippedWithin(range, [project]), false)}</ol>
    </section>
    ${ideaOrigin(project)}`;
  bindRange(root);
  bindTooltips(root);
}

/* Operations page */

const OPS_ORDER = ["working", "idle_with_work", "idle", "paused", "api_guard", "error"];
const clock = (iso) => new Date(iso).toLocaleTimeString(lang === "zh" ? "zh-CN" : "en-GB", { hour: "2-digit", minute: "2-digit", hour12: false });

function opsTimeline(ops) {
  const cells = ops.timeline.map((s) => {
    const tip = `${clock(s.t)} · ${t(`ops.state.${s.state}`)}${s.waiting ? ` · ${t("ops.waiting", { n: s.waiting })}` : ""}`;
    return `<i class="cell ${escapeHtml(s.state)}" tabindex="0" data-tip="${escapeHtml(tip)}"></i>`;
  }).join("");
  const total = Math.max(1, ops.samples_24h);
  const legend = OPS_ORDER.filter((state) => ops.shares[state]).map((state) =>
    `<span class="legend-item"><i class="cell ${state}"></i>${t(`ops.state.${state}`)} <strong>${t("ops.share", { p: Math.round((ops.shares[state] / total) * 100) })}</strong></span>`).join("");
  return `<figure class="chart strip-chart">
    <div class="strip" style="grid-template-columns:repeat(${ops.timeline.length},1fr)">${cells}</div>
    <div class="legend">${legend}</div>
    <div class="tooltip" role="status" hidden></div>
  </figure>`;
}

function apiChart(ops) {
  const hours = ops.api_hourly || [];
  if (!hours.length) return "";
  const limit = Math.max(...hours.map((h) => h.limit));
  const every = Math.ceil(hours.length / 8);
  const bars = hours.map((h, i) => {
    const tip = t("ops.api.tooltip", { when: clock(h.reset), used: h.used, limit: h.limit });
    const hot = h.used >= 0.8 * h.limit;
    return `<div class="col-bar${hot ? " hot" : ""}" tabindex="0" data-tip="${escapeHtml(tip)}"><b style="height:${(h.used / limit) * 100}%"></b>${i % every === 0 ? `<small>${clock(h.reset)}</small>` : ""}</div>`;
  }).join("");
  return `<figure class="chart">
    <figcaption>${t("ops.api.chart")}</figcaption>
    <div class="plot">
      <div class="grid"><span style="bottom:0"><em>0</em></span><span class="threshold" style="bottom:80%"><em>${t("ops.api.threshold")}</em></span><span style="bottom:100%"><em>${limit}</em></span></div>
      <div class="bars" style="grid-template-columns:repeat(${hours.length},1fr)">${bars}</div>
    </div>
    <div class="tooltip" role="status" hidden></div>
  </figure>`;
}

function renderOps() {
  const root = document.getElementById("ops");
  const ops = data.ops;
  document.title = `${t("nav.ops")} · Idea Cauldron`;
  if (!ops) { root.innerHTML = `<p class="note">${t("ops.empty")}</p>`; return; }
  const now = ops.now;
  const api = now?.api;
  const state = now?.state;
  const resume = now?.resume ? ` · ${t("ops.resume", { when: clock(now.resume) })}` : "";
  const warnings = (ops.warnings || []).map((w) => `<li>${t(`ops.warn.${w}`)}</li>`).join("");
  const a = ops.actions || {};
  const c = ops.claude || {};
  root.innerHTML = `
    <section class="detail-head">
      <div class="card-top"><h1 class="detail-title">${t("ops.title")}</h1>${state ? `<span class="status ops-${escapeHtml(state)}"><i></i>${t(`ops.state.${state}`)}${resume}</span>` : ""}</div>
      <p class="focus">${t("ops.lede")}</p>
      ${warnings ? `<ul class="warnings">${warnings}</ul>` : ""}
    </section>
    <section class="panel"><h3>${t("ops.day")}</h3>
      ${ops.samples_24h ? `<p class="note">${t("ops.day.note")}</p>${opsTimeline(ops)}` : `<p class="note">${t("ops.empty")}</p>`}
    </section>
    <section class="panel"><h3>${t("ops.api")}</h3>
      <p class="note">${t("ops.api.note", { limit: api?.limit ?? 5000 })}</p>
      ${api ? `<div class="api-now${api.used >= 0.8 * api.limit ? " hot" : ""}">${meter(api.used, api.limit, t("ops.api.now", { used: api.used, limit: api.limit, when: clock(api.reset) }))}</div>` : ""}
      ${apiChart(ops)}
    </section>
    <section class="panel"><h3>${t("ops.claude")}</h3>
      <div class="tiles">
        <div class="stat"><strong>${c.limit_hits_24h ?? "–"}</strong><span>${t("ops.claude.hits24")}</span></div>
        <div class="stat"><strong>${c.limit_hits_7d ?? "–"}</strong><span>${t("ops.claude.hits7")}</span></div>
        <div class="stat"><strong>${c.paused_minutes_24h ?? "–"}</strong><span>${t("ops.claude.paused")}</span></div>
      </div>
      <p class="note">${t("ops.claude.note")}</p>
    </section>
    <section class="panel"><h3>${t("ops.actions")}</h3>
      <div class="tiles">
        <div class="stat"><strong>${a.runs_24h ?? "–"}${a.runs_capped ? "+" : ""}</strong><span>${t("ops.actions.runs")}</span></div>
        <div class="stat"><strong>${a.merged_24h ?? "–"}</strong><span>${t("ops.actions.merged")}</span></div>
        <div class="stat"><strong>${a.runs_per_merge ?? "–"}</strong><span>${t("ops.actions.perMerge")}</span></div>
      </div>
      <ul class="workflow-list">${Object.entries(a.by_workflow || {}).map(([name, n]) => `<li><span>${escapeHtml(name)}</span><strong>${n}</strong></li>`).join("")}</ul>
    </section>`;
  bindTooltips(root);
}

function bindTooltips(root) {
  root.querySelectorAll(".chart").forEach((chart) => {
    const tip = chart.querySelector(".tooltip");
    const show = (bar) => {
      tip.textContent = bar.dataset.tip;
      tip.hidden = false;
      const box = bar.getBoundingClientRect();
      const host = chart.getBoundingClientRect();
      tip.style.left = `${box.left - host.left + box.width / 2}px`;
    };
    chart.querySelectorAll(".col-bar, .strip .cell").forEach((bar) => {
      bar.addEventListener("mouseenter", () => show(bar));
      bar.addEventListener("focus", () => show(bar));
      bar.addEventListener("mouseleave", () => { tip.hidden = true; });
      bar.addEventListener("blur", () => { tip.hidden = true; });
    });
  });
}

function bindRange(root = document) {
  root.querySelectorAll("[data-range]").forEach((button) => button.addEventListener("click", () => {
    range = Number(button.dataset.range);
    store.set("range", String(range));
    render();
  }));
}

function render() {
  renderStatic();
  if (!data) return;
  if (data.new_idea_url) document.querySelectorAll("[data-new-idea]").forEach((el) => { el.href = data.new_idea_url; });
  renderPipeline();
  if (PAGE === "project") {
    renderDetail();
  } else if (PAGE === "ops") {
    renderOps();
  } else {
    renderStats();
    renderNeeds();
    renderProjects();
    renderShipped();
  }
  document.getElementById("updated").textContent = t("updated", { when: relative(data.generated_at) });
}

document.querySelectorAll("[data-lang]").forEach((button) => button.addEventListener("click", () => {
  lang = button.dataset.lang;
  store.set("lang", lang);
  render();
}));
if (PAGE === "home") {
  bindRange();
  document.getElementById("project-filter").addEventListener("click", (event) => {
    const button = event.target.closest("[data-project]");
    if (!button) return;
    projectFilter = button.dataset.project;
    renderShipped();
  });
}

render();
fetch("data.json", { cache: "no-store" })
  .then((response) => response.json())
  .then((json) => { data = json; render(); })
  .catch(() => { document.getElementById("updated").textContent = "data.json unavailable"; });
