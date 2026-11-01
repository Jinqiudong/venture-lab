# Venture Lab Autonomous Delivery Flow

> Current autonomous engineering control plane. GitHub Issues are the work contract; product repositories own product code and platform CI; Venture Lab owns orchestration, independent review, QA, risk gates, and human escalation.

## 1. Mental model

Venture Lab is a **control plane**, not a product repository.

```text
BUILD-ready plan → GitHub milestone of Issues → Agent Orchestrator (woken by the Heartbeat)
                                   ├─ ready Issue → Builder → task PR into milestone/<slug>
                                   └─ existing PR → Review Cycle
task PR → product-repo CI → Reviewer
                         ├─ changes → Fixer → new HEAD → CI/Review again
                         └─ approve → QA → Risk Gate
                                           ├─ routine → Auto-merge into the milestone branch → next Issue at once
                                           └─ sensitive/ambiguous → Product Owner → resume
milestone has no open Issues → acceptance checklist on the milestone PR → Product Owner tries it
                         ├─ accept (merge or /accept) → default branch
                         └─ feedback → new Issues in the same milestone → loop
```

The Product Owner reviews **milestones, not PRs**. Inside a milestone the AI team does not stop, except for the risk categories below.

The key separation is **coordination vs evidence**. Venture Lab decides what happens next. The target repository and its CI provide platform-specific evidence. For example, AniDream's macOS/Xcode workflow is authoritative for iOS tests; a Linux Reviewer/Fixer should not pretend it ran Xcode locally.

## 2. Canonical inputs

### GitHub Issue = implementation contract
Builder works from a dependency-ready Issue and its acceptance criteria. It implements the smallest change satisfying that contract and must not silently expand product scope.

### Pull Request = review unit
Reviewer and QA evaluate the exact PR HEAD. If Fixer pushes a new commit, previous evidence is stale and the new HEAD must be reviewed again.

### Product repository CI = platform evidence
Builds, tests, linting, simulator/device checks, and other platform-specific validation belong in the product repository. Venture Lab reads those results as evidence.

### Agent contracts = role boundaries
- `agents/builder.md`: implement the Issue.
- `agents/reviewer.md`: independently inspect correctness and scope; never edit.
- `agents/fixer.md`: repair only supplied blocking findings.
- `agents/qa.md`: independently validate acceptance criteria and tests.
- `agents/handoff.md`: translate a true human decision into a concise Product Owner handoff.

## 3. How the Actions interact

### Agent Orchestrator — `.github/workflows/orchestrator.yml`
The Orchestrator refreshes portfolio state and asks `scripts/orchestrate.py` for the next action. It can build a dependency-ready Issue, wake Review Cycle for an existing managed PR, auto-stop repeated Builder failures, or remain idle.

**Auto-stop and `/retry`.** After two Builder failures on an Issue, the Orchestrator posts an auto-stop and skips it. A Claude usage limit is not counted as a failure. When the cause is fixed, the owner comments `/retry` (or `重试`) on the Issue (`orchestrator/retry.py`). Failures and auto-stops before that comment are then ignored by the Orchestrator and the dashboard, so nobody has to delete comments.

**Scheduling.** The AI Team Heartbeat wakes the Orchestrator (see below). Product-repo CI events also wake it through `portfolio-refresh`, and every auto-merge dispatches it so the next ready Issue starts at once. Up to `MAX_PARALLEL_BUILDERS` (default 2) ready Issues are built at once as a job matrix; Issues already in review do not use Builder capacity.

For a build it checks out the target repo and picks the base branch with `scripts/milestones.py base`. That is `milestone/<slug>` when the Issue belongs to an open GitHub milestone, created from the default branch and synced with it on each build, and the default branch otherwise. It then creates `agent/issue-<n>`, runs Builder, checkpoints work, commits, opens a PR against that base, and dispatches Review Cycle.

**Only a `hold` label stops the AI team.** Draft PRs are reviewed like any other PR, and an approved draft is marked ready automatically right before merge. To keep the AI team away from a PR, add the `hold` label; its Issue then gets the `hold` stage, which neither blocks new Builder dispatches nor gets reset to `ready` by dependency resolution. Removing the label resumes automation. Stacked PRs (based on another feature branch) are skipped until their base merges. Deleting a merged branch would make GitHub close PRs stacked on it, so the merge step merges without deleting, retargets those PRs to the default branch, and only then deletes the branch.

### Product repository CI
Opening/updating the PR triggers the product repository's own workflows. Results are attached to the exact commit SHA and become evidence for Reviewer/QA.

### Agent Review Cycle — `.github/workflows/review-cycle.yml`

**Reviewer** reads Issue, PR, diff, architecture, and current-HEAD CI evidence. It returns `approve` or `request_changes`, escalating only genuine product ambiguity.

**Fixer loop** runs for actionable blockers that do not need a product decision. It fixes only those findings and pushes a new commit. New HEAD means CI/review must run again. Platform-only execution requirements belong in platform CI, not an impossible Linux retry loop. If the Reviewer still requests changes on the same HEAD after the Fixer's one attempt, the PR is handed to the owner once (`venture-human-ready`) instead of being reviewed again every heartbeat. A PR whose CI jobs GitHub never started (Actions minutes or billing) is skipped without spending an agent run until CI can run.

**QA** runs after Reviewer approval, validates acceptance criteria and relevant tests, and may treat successful platform CI on the exact HEAD as authoritative evidence. QA's `needs_human` / `human_validation` does not block the merge. It is a "try this" note, such as visual feel or behavior on a real device, that is added to the milestone PR and lands in the milestone's acceptance checklist. Anything actually broken or unverified is a `fail`.

**Risk gate** follows Reviewer approval + QA pass. Routine low-risk changes may auto-merge. Human-gated categories include workflow/control-plane changes, secrets, payments/billing, production release, database/schema migrations, entitlements, privacy, and legal/terms changes.

**Product Owner handoff** is the exception path. It asks for product/UX/risk judgment, not routine code approval. A decision resolves the gate and allows automation to resume.

**Venture Lab reviews itself.** Venture Lab is registered in `dashboard/projects.json` (hidden from the page with `"dashboard": false`), so its own PRs that contain `Closes #<n>` go through the same Reviewer → QA → risk gate. Any change under `.github/`, `agents/`, `orchestrator/`, or the scheduling/guard scripts is control-plane work and always goes to the Product Owner; dashboard, docs and incubation records may auto-merge.

**Auto-merge** re-checks the exact HEAD before squash-merging and deleting the branch. PRs stacked on it are retargeted to the merged PR's base. After a merge into a milestone branch, `scripts/milestones.py after-merge` closes the Issue, because `Closes #n` only fires on the default branch and dependent Issues would otherwise never become ready. It also opens the milestone PR if needed and adds QA's try note. Every merge then dispatches the Orchestrator.

### Milestones — `scripts/milestones.py`
A milestone is the Product Owner's unit of review. Its task PRs merge into `milestone/<slug>`, and one milestone PR (draft until finished) carries the branch to the default branch. Review Cycle never selects a milestone PR. When the GitHub milestone has no open Issues, the heartbeat posts an acceptance checklist on the milestone PR (`<!-- venture-acceptance-ready:<HEAD SHA> -->`) with what shipped and every QA try note, and marks it ready. The dashboard shows it under "Needs you". The owner merges it, or comments `/accept` (or `验收通过`) and the heartbeat merges it and closes the milestone. Feedback becomes new Issues in the same milestone; once they merge, the HEAD changes and a fresh checklist is posted. Keep milestones small, about ten Issues or a few days, so the branch does not drift.

### AI Team Heartbeat — `.github/workflows/heartbeat.yml`
GitHub cron is not reliable enough to drive the team. On 2026-10-31 the hourly Orchestrator schedule ran twice in twelve hours, and the pipeline sat idle for hours after each PR. The heartbeat is one long job (`scripts/heartbeat.py`) that re-arms itself before the Actions time limit. It dispatches workflows and writes the `metrics` branch with the workflow's own `GITHUB_TOKEN`, because `AGENT_GITHUB_TOKEN` is a fine-grained PAT without Actions write on Venture Lab. It uses the agent token only for product-repo milestone work. A failed dispatch is recorded as an `error` sample, so it shows on the Operations page instead of failing silently. A sparse cron only restarts it if a run is ever lost. Every ten minutes it:
1. pauses while the newest finished agent run failed on a Claude usage limit, until the reset time in that message (30 minutes when no time is given);
2. advances milestones (acceptance checklist, `/accept` merges);
3. stops starting agent work while fewer than 500 core GitHub API calls remain in the shared token's hour, so the owner's own tools keep working;
4. dispatches the Orchestrator when no Orchestrator or Review Cycle run is queued or running;
5. refreshes the dashboard;
6. appends a sample to `metrics/heartbeat.jsonl` on the `metrics` branch, keeping 7 days: the state (`working`, `idle_with_work`, `idle`, `paused`, `api_guard`), work waiting, and the API budget. The dashboard's Operations page (`ops.html`) reads it to show where the last 24 hours went, hourly API peaks against an 80% warning line, Claude limit hits and paused time, and Actions runs per merged PR. Claude subscriptions expose no usage percentage that automation can read, so Claude usage is shown as limit hits and pauses.

### Idea intake — `.github/workflows/idea-brain.yml`
The dashboard's "new idea" button opens the `idea.yml` issue form, which labels the issue `idea`. When the repository owner opens such an issue, or comments on it, the Product Brain (`agents/product-incubator.md` plus `product-incubator/PLAYBOOK.md`) runs one turn: desk research, an updated incubation record, and a reply with at most three questions. The record is embedded in that reply as an `idea-cauldron-record` HTML comment, so the issue alone holds the state; `scripts/generate_dashboard.py` reads the latest one to draw the idea card, and a file in `product-incubator/records/` still wins when both exist. Comments from anyone other than the owner never start a turn and are left out of the prompt. The Product Brain cannot move an idea to BUILD; that happens only when the owner's latest comment contains `/approve-build` (or `批准开发`).

### Agent runtime — `.github/actions/run-agent`
Every role (Builder, Reviewer, Fixer, QA, Handoff) runs through one composite action, so the model provider is a configuration choice rather than a workflow rewrite.

- **Claude Code (default).** Uses the `CLAUDE_CODE_OAUTH_TOKEN` secret (created with `claude setup-token`, billed to the owner's Claude subscription) or, failing that, `ANTHROPIC_API_KEY`. Read-only roles may only read files and run read-only git commands; editing roles may change the working tree but cannot `git push` or call `gh`, because publishing stays with the workflow. Schema-bound roles return validated JSON through `--json-schema`.
- **Research profile.** `:research` is the read-only profile plus `WebSearch` and `WebFetch`. Only the Product Brain uses it, and it always runs on Claude.
- **Codex (fallback).** Set the repository variable `AGENT_PROVIDER=codex` to route every role through `openai/codex-action` with `OPENAI_API_KEY`.

## 4. Supporting Actions

- **Agent Guardrails** cancels stalled agent runs and records a failure checkpoint on the Issue/PR. A failure caused by a usage limit (a Claude limit, `Quota exceeded`, or a GitHub API rate limit) is not recorded, because two of them would auto-stop a healthy Issue; the heartbeat retries after the reset instead.
- **Agent Runtime Guard** caps unhealthy automatic-fix behavior and protects against runaway loops. It counts Fixer attempts from the `<!-- venture-fixer-attempt:<HEAD SHA> -->` marker that Review Cycle posts, so the guard and the workflow must share that exact marker format.
- **Scope Gate Shadow** analyzes whether ready Issues are sufficiently bounded; currently observational.
- **Portfolio Dashboard** exposes state. The heartbeat refreshes it every ten minutes, plus a 6-hourly schedule and pushes to its own files. It no longer refreshes on every agent run or product-repo event, which was most of the GitHub API spend. Dashboards are observability, not canonical truth.

## 5. Safety invariants

1. GitHub is the system of record.
2. Issue defines scope; agents cannot invent product requirements.
3. Reviewer is independent from Builder.
4. QA follows Reviewer approval.
5. Evidence is tied to the exact commit SHA.
6. A changed HEAD invalidates prior approval/evidence.
7. Failed required CI is a blocker; missing platform tooling on Linux is not proof of failure.
8. Fixer repairs findings without broadening scope.
9. Human escalation is for judgment, risk, or irreducible external validation—not routine approvals.
10. Auto-merge requires evidence plus risk-policy approval.
11. Repeated automation failure must stop rather than loop forever.

## 6. Typical lifecycle

```text
Issue ready → Orchestrator → Builder → task PR (into milestone/<slug>) → product CI → Reviewer
→ [Fixer → new HEAD → CI → Reviewer] as needed
→ Reviewer approve → QA (try notes to the milestone) → Risk Gate
→ Auto-merge (Issue closed, Orchestrator dispatched) OR Product Owner decision → merge
→ dependency graph exposes next ready Issue → Orchestrator continues
→ milestone finished → acceptance checklist → Product Owner accepts → default branch
```

## 7. Keeping this document synchronized

This document is English-only, like all code and documentation in Venture Lab and its product repositories.

A **Documentation Guard** requires every change to a core orchestration workflow, `orchestrator/` module, or agent contract to update this document in the same change. CI fails rather than allowing architecture docs to silently become stale.

The guard does not ask AI to guess documentation after the fact. The engineer/agent changing the process updates the relevant section in the same change, so intended behavior and documentation are reviewed together.

## 8. Source-of-truth map

| Concern | Canonical source |
|---|---|
| Product/implementation requirement | Target repo GitHub Issue |
| Current implementation | PR exact HEAD |
| Platform build/test evidence | Target repo Actions/checks |
| Scheduling/build orchestration | `.github/workflows/orchestrator.yml` + `scripts/orchestrate.py`, woken by `.github/workflows/heartbeat.yml` + `scripts/heartbeat.py` |
| Milestone branches and acceptance | `scripts/milestones.py` |
| Review/Fix/QA/merge state machine | `.github/workflows/review-cycle.yml` |
| Agent behavior | `agents/*.md` |
| Portfolio visibility | Generated dashboard |
| Architecture explanation | `docs/AUTONOMOUS_FLOW.md` |
