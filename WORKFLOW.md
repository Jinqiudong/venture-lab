# Shared Project Workflow

This document defines the default delivery workflow for projects managed through Venture Lab.

## Delivery Flow

Idea / problem
→ GitHub Issue
→ working branch
→ implementation
→ local validation
→ Pull Request
→ CI
→ review
→ human approval
→ merge to main
→ deploy
→ monitor
→ follow-up issue if needed

## Repository Responsibilities

Each product repository should own its own:

- `AGENTS.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`
- tests
- product documentation
- deployment configuration

The exact CI differs by technology stack; the workflow principle stays the same.

## Branch Policy

Do not develop directly on `main`.

Use scoped branches such as:

- `feature/...`
- `fix/...`
- `refactor/...`
- `chore/...`
- `experiment/...`

## Issue Requirements

Before implementation, a task should state:

1. Problem / goal
2. Desired outcome
3. Acceptance criteria
4. Important constraints
5. Validation plan

## Pull Request Requirements

A PR should explain:

- what changed
- why it changed
- what was intentionally not changed
- how it was tested
- important risks or assumptions

## AI Agent Policy

AI agents may implement, test, refactor, review, and investigate.

Agents should not bypass CI or push directly to `main`.

When multiple agents disagree on an implementation, prefer objective evidence: tests, benchmarks, user outcomes, maintainability, and production behavior.

Human approval remains the default gate for merging to `main`, production deployment, database migrations, billing changes, and other consequential actions until the workflow is proven reliable.
