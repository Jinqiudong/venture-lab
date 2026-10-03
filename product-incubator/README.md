# Idea Cauldron Product Incubator

This layer sits before engineering. It turns a raw Idea into a product direction that is ready for validation and, later, a bounded engineering plan.

## Flow

```text
Raw Idea
  ↓
SPARK
  ↓
EXPLORE
  ↓
VALIDATE
  ↓
INCUBATE
  ↓
BUILD
  ↓
Repo bootstrap → Epic → Scope Gate → Builder
```

Ideas may also move to `PARK` or `REJECT` with rationale preserved.

## Separation of responsibilities

- Product Incubator: what should be built and why.
- Scope Gate: whether engineering work is bounded enough for one autonomous PR.
- Builder: implementation.
- Reviewer / QA: verification.
- Product Owner: strategic, subjective, and final product decisions.

## Canonical incubation record

Each idea may maintain a structured record using `product-incubator/idea.schema.json` semantics. The record captures:

- stage
- product thesis
- evidence
- validation plan
- MVP / non-goals
- success metrics
- risks / unknowns
- open Product Owner decisions
- recommendation + confidence
- build handoff when applicable

The canonical source remains GitHub: the Idea Issue plus any linked incubation artifact. Chat conversations are working sessions, not the system of record.

## Promotion rules

### SPARK → EXPLORE
Raw idea is understandable enough to articulate a user and possible problem.

### EXPLORE → VALIDATE
The product thesis is coherent and the riskiest assumptions are explicit.

### VALIDATE → INCUBATE
There is enough signal to justify defining an MVP. Validation may be lightweight; the standard is decision usefulness, not statistical certainty.

### INCUBATE → BUILD
Requires a human Product Owner gate. Before promotion, the idea should have:

- clear target user and problem
- differentiated product hypothesis
- explicit MVP and non-goals
- core user journey
- retention / repeat-use hypothesis
- success metrics
- major risks and open decisions documented
- cheapest validation completed or consciously waived

Promotion to BUILD authorizes repo bootstrap and engineering planning. It does not bypass Scope Gate.

## Suggested chat usage

In a product-specific chat, use language such as:

> Use the Idea Cauldron Product Incubator on Idea #9. Treat GitHub as canonical truth. Help me move it from its current stage toward a validated MVP; do routine PM work autonomously and bring me only strategic product decisions.

The chat should write important decisions back to the Idea Issue or incubation artifact so other chats and the control plane can recover state.
