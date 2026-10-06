# Venture Lab Autonomous Delivery Flow

[中文](AUTONOMOUS_FLOW.zh-CN.md) | **English**

> Current autonomous engineering control plane. GitHub Issues are the work contract; product repositories own product code and platform CI; Venture Lab owns orchestration, independent review, QA, risk gates, and human escalation.

## 1. Mental model

Venture Lab is a **control plane**, not a product repository.

```text
BUILD-ready plan → GitHub Issue → Agent Orchestrator
                                   ├─ ready Issue → Builder → PR
                                   └─ existing PR → Review Cycle
PR → product-repo CI → Reviewer
                         ├─ changes → Fixer → new HEAD → CI/Review again
                         └─ approve → QA → Risk Gate
                                           ├─ routine → Auto-merge
                                           └─ sensitive/ambiguous → Product Owner → resume
```

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

For a build it checks out the target repo, creates `agent/issue-<n>`, runs Builder, checkpoints work, commits, opens a PR, then dispatches Review Cycle and Dashboard refresh.

### Product repository CI
Opening/updating the PR triggers the product repository's own workflows. Results are attached to the exact commit SHA and become evidence for Reviewer/QA.

### Agent Review Cycle — `.github/workflows/review-cycle.yml`

**Reviewer** reads Issue, PR, diff, architecture, and current-HEAD CI evidence. It returns `approve` or `request_changes`, escalating only genuine product ambiguity.

**Fixer loop** runs for actionable blockers that do not need a product decision. It fixes only those findings and pushes a new commit. New HEAD means CI/review must run again. Platform-only execution requirements belong in platform CI, not an impossible Linux retry loop.

**QA** runs after Reviewer approval, validates acceptance criteria and relevant tests, and may treat successful platform CI on the exact HEAD as authoritative evidence.

**Risk gate** follows Reviewer approval + QA pass. Routine low-risk changes may auto-merge. Human-gated categories include workflow/control-plane changes, secrets, payments/billing, production release, database/schema migrations, entitlements, privacy, and legal/terms changes.

**Product Owner handoff** is the exception path. It asks for product/UX/risk judgment, not routine code approval. A decision resolves the gate and allows automation to resume.

**Auto-merge** re-checks the exact HEAD before squash-merging and deleting the branch.

## 4. Supporting Actions

- **Agent Runtime Guard** caps unhealthy automatic-fix behavior and protects against runaway loops.
- **Scope Gate Shadow** analyzes whether ready Issues are sufficiently bounded; currently observational.
- **Portfolio Dashboard / Checkpoint Dashboard Refresh** expose state/checkpoints; dashboards are observability, not canonical truth.

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
Issue ready → Orchestrator → Builder → PR → product CI → Reviewer
→ [Fixer → new HEAD → CI → Reviewer] as needed
→ Reviewer approve → QA → Risk Gate
→ Auto-merge OR Product Owner decision → merge
→ dependency graph exposes next ready Issue → Orchestrator continues
```

## 7. Keeping this document synchronized

These files are a synchronized pair:
- `docs/AUTONOMOUS_FLOW.md` — English
- `docs/AUTONOMOUS_FLOW.zh-CN.md` — Simplified Chinese

A **Documentation Guard** requires changes to core orchestration workflows or agent contracts to update **both** documents in the same change. CI fails rather than allowing architecture docs to silently become stale.

The guard does not ask AI to guess documentation after the fact. The engineer/agent changing the process updates the relevant section in the same change, so intended behavior and documentation are reviewed together.

## 8. Source-of-truth map

| Concern | Canonical source |
|---|---|
| Product/implementation requirement | Target repo GitHub Issue |
| Current implementation | PR exact HEAD |
| Platform build/test evidence | Target repo Actions/checks |
| Scheduling/build orchestration | `.github/workflows/orchestrator.yml` + `scripts/orchestrate.py` |
| Review/Fix/QA/merge state machine | `.github/workflows/review-cycle.yml` |
| Agent behavior | `agents/*.md` |
| Portfolio visibility | Generated dashboard |
| Architecture explanation | `docs/AUTONOMOUS_FLOW*.md` |
