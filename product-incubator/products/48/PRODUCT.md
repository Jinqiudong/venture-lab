# PRODUCT.md — 雪场预滑 · Ski Pre-Run

> Canonical product contract for Idea [#48](https://github.com/Jinqiudong/venture-lab/issues/48). Claims are marked **Evidence**, **Hypothesis**, **Decision** or **TBD**.

## Product snapshot
- Idea: #48. Repo: [Jinqiudong/ski-prerun](https://github.com/Jinqiudong/ski-prerun). Live prototype: https://jinqiudong.github.io/ski-prerun/
- Stage: EXPLORE, with a playable validation prototype (v2, 2026-11-01). BUILD needs the owner's `/approve-build` on #48.
- One-line promise: the night before a ski day, plan your route and ride it in a game version of the real resort, so you know the way tomorrow.

## Problem
- Target user: **Hypothesis** — intermediate skiers and snowboarders visiting an unfamiliar resort a few times a season. The owner is user zero.
- Problem: **Evidence (owner)** — flat trail maps are hard to read; on the mountain you lose time finding the way and can end up on runs that are too hard.
- Job to be done: build a mental picture of lifts, runs and junctions, and a route for tomorrow.
- Frequency/context: the evening before, and on the lift during the day. **Hypothesis**: a few times a season per resort, more for a multi-day trip.
- Current alternatives: **Evidence** — resort trail maps; 3D map apps (FATMAP, Ski Resort 3D, Ski Copilot, PistePal); videos and posts; asking staff. None found that let you ride a real resort with game feel (shallow desk search, Product Brain 2026-11-01).

## Product hypothesis
- Core value: plan a route, then ride it — on the chair with the runs below named, and down each run with turn-by-turn cues — until it is familiar.
- Differentiation: playable first-person route rehearsal on real terrain, not a map viewer or a fly-over.
- Why now: free OpenStreetMap piste/lift data and open terrain tiles make a real resort buildable in days (**Evidence**: Copper Mountain, 155 runs and 23 lifts, built from them).

## Core experience
- Entry: open the link, pick ski or snowboard and your level.
- First value: plan "village → lunch spot" and see the lifts and runs it takes.
- Aha moment: **Hypothesis** — after one auto ride-through, the owner recognises the junctions on the mountain.
- Repeat-use loop: **TBD** — each trip / each new resort; possibly sharing a planned day with friends.

## MVP
### Capabilities (built in the prototype)
- Real resort: terrain, runs by difficulty, lifts, villages and restaurants (Copper Mountain).
- Route planner across lifts and runs, capped at the rider's level, with time estimates.
- Lift rides that show the runs below; runs with trail signs, turn-by-turn cues, a heading-up minimap and an overview pause.
- Auto mode that rides the planned route for you.
- Ski or snowboard rider; stylized-realistic look.
### Non-goals (for now)
- Snow Memories (shared photos, follow-cam edits, memory map) — **Decision (owner, 2026-11-01)**: not in the MVP; later it can pin trip photos onto this map (#49).
- Native app, accounts, multiplayer, live lift status, grooming reports.
- Resorts other than Copper until the core loop is validated.
### Product acceptance criteria
- The owner plans a route for a real ski day, rides it through the night before, and on the day finds the route without opening the official trail map.

## Validation
- Riskiest assumption: riding the route in the game makes people remember it better than looking at a 3D map.
- Existing evidence: owner feedback on v1 — "riding one run did not help me plan or know where I am"; v2 adds planning and orientation.
- Cheapest next validation: the owner's next Copper day; then 5–8 skier friends try one planned route on the link.
- Positive threshold: the owner navigates the planned route from memory; most friends say they would open it before a new resort.
- Negative threshold: the owner still needs the trail map at every junction, or friends prefer a plain 3D map.

## Success metrics
- Planned routes ridden through per session; return visits before a trip; "found my way" self-reports.

## Risks and unknowns
- OpenStreetMap gaps: some lift-to-run connections are missing (9 lift tops unreachable on blue at Copper); Chinese resort coverage unverified.
- Phone performance on older devices; heavy 3D on mobile browsers.
- Game feel vs. accuracy: terrain is ~14 m resolution; no small features.

## Open Product Owner decisions
- Approve BUILD (`/approve-build` on #48) to make this a managed project with milestones.
- Next resort(s) after Copper, and whether to target Chinese resorts.
- How far to push realism vs. a light, fast map.

## Build readiness
- Status: NOT READY — prototype validation in progress.
- Missing before BUILD: the owner's real-day test; repeat-use hypothesis.
