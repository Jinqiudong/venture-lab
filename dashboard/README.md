# Venture Lab Dashboard

The dashboard is a read-only portfolio view. Product repositories remain the source of truth for engineering work.

## What it shows

The overview page (`index.html`):
- **Needs you**: only product judgment. Open PRs whose current HEAD has a Review Cycle Product Owner handoff with no later decision, plus work items configured with `needs_human`. A `hold` is the owner's own pause and an auto-stopped Builder is an engineering failure, so neither appears here.
- one card per project with a status light (`needs_you`, `stuck`, `stalled`, `moving`, `quiet`), the lifecycle stage, planned-task progress, and the next open milestone
- what the team shipped, filterable by project and by 3, 7 or 30 days

Each repo card opens `project.html?p=<slug>`, which shows:
- the project's open asks and a board: waiting on you, AI stuck, AI working, queued, done
- the plan: GitHub milestones with their due dates and a projected finish from the last four weeks of throughput
- delivery: PRs merged per week over eight weeks, the four-week pace, and the median time from PR to merge
- recently shipped work and, for projects that grew out of an idea, how it started

Planned timelines come from GitHub milestones in the product repository. Give a milestone a due date and assign its issues to it; the dashboard does the rest.

## Add or edit a project

Edit `dashboard/projects.json` and add an entry with:

```json
{
  "name": "Project Name",
  "repo": "owner/repository",
  "stage": "MVP",
  "health": "green",
  "current_focus": "Current milestone",
  "attention": "Next decision or action"
}
```

Supported health values are `green`, `yellow`, and `red`.

## Private repositories

The default `GITHUB_TOKEN` of the public `venture-lab` repository cannot read unrelated private repositories.

To show live data for private project repositories, create a fine-grained GitHub personal access token with read-only access to the repositories you want to monitor, then add it to Venture Lab as an Actions repository secret named:

`PORTFOLIO_GITHUB_TOKEN`

Minimum permissions should be read-only and scoped as narrowly as possible. Do not commit the token.

Without this secret, the dashboard still renders manual portfolio metadata and labels private live data as unavailable.

## GitHub Pages

The workflow `.github/workflows/dashboard.yml` generates `dashboard/data.json`, validates it, uploads the `dashboard/` directory as the Pages artifact, and deploys it.

After merging the dashboard PR, set the repository Pages source to **GitHub Actions** if GitHub does not enable it automatically.

The workflow runs:
- on relevant pull requests (build/validation only)
- after relevant pushes to `main`
- every 6 hours
- on manual `workflow_dispatch`

## Source-of-truth rule

Do not manually copy detailed task status into Venture Lab. Issues, pull requests, CI, releases, and deployments stay in each product repository. Venture Lab stores only lightweight portfolio metadata and aggregates the rest.
