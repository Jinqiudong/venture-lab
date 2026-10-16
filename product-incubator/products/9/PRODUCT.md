# 猫猫美容中心 — PRODUCT.md

> Idea #9 · Stage: **EXPLORE** · Build readiness: **NOT READY**
>
> This document distinguishes hypotheses from evidence. It is expected to change as the Product Owner and Product Brain learn.

## Product snapshot
**Hypothesis:** A playful cat-grooming companion can make recurring care easier to remember and more emotionally engaging, while preserving a useful grooming history.

## Problem
- **Target user — Owner decision (2026-10-15):** experienced cat owners (several years of ownership) with busy daily schedules. **Hypothesis:** they know the basics but may struggle to consistently remember or record routine care.
- **Problem — Hypothesis:** recurring grooming/hygiene tasks are easy to forget or inconsistently track.
- **Job to be done — Hypothesis:** “Help me know what care my cat needs, remember when to do it, and feel good about keeping up.”
- **Frequency/context — TBD:** we do not yet know whether grooming events occur often enough to support a dedicated product.
- **Current alternatives — Desk research:** memory, calendars, notes, and dedicated pet-care apps. 11pets already supports hygiene logs and reminders for bathing, teeth brushing, nail clipping, and ear care; PetDesk offers reminders/to-dos; PawTrack offers grooming routines and tracking. These establish competitive functionality, not proof of demand for our product.

### Competitor / problem desk research (2026-10-15)
- **Evidence — 11pets:** https://www.11pets.com/en/feature — hygiene care logs and configurable reminders.
- **Evidence — PetDesk:** https://apps.apple.com/us/app/petdesk/id631377773 — reminders and to-dos.
- **Evidence — PawTrack:** https://play.google.com/store/apps/details?id=com.zeppelinapps.pawtrack — routine grooming and hygiene tracking.
- **Inference:** reminders/checklists are commoditized; personalized virtual-cat progression may differentiate, but its retention value remains unvalidated.
- **Safety constraint — Evidence:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10845437/ — routine ear cleaning is not indicated without discomfort/disease; the product must not incentivize unnecessary or distressing care.


## Product hypothesis
- **Decision (2026-10-15):** Product direction C — real-world grooming check-ins drive progression of a personalized digital cat. Utility and playful companionship are intentionally linked, not separate modes.
- **Core loop — Decision:** complete appropriate real cat care → record a check-in → digital cat responds/grows → see history and upcoming care.
- **Core value — Hypothesis:** turn cat-care maintenance into a simple ritual: know → do → record → see progress.
- **Differentiation — Hypothesis:** practical grooming records plus a personalized digital-cat progression layer rather than a conventional clinical pet tracker.
- **Why now — TBD:** no validated timing thesis yet.

## Core experience
- **Entry — Hypothesis:** add cat profile (photo optional), select appropriate care activities and cadence; generate a lightweight digital-cat companion.
- **First value — Hypothesis:** log one real grooming activity in seconds and see the digital cat respond.
- **Aha moment — Hypothesis:** see real-life care history visibly change the personalized digital cat.
- **Repeat-use / retention loop — Decision/Hypothesis:** appropriate recurring real-world care → simple check-in → gentle digital-cat progression → useful care history and configurable reminders. Avoid pressure/streak penalties or rewards for excessive grooming.

### Gentle Care Companion — reminder experience (Owner proposal, 2026-10-15)
- **Product direction — Proposed for validation:** friendly, opt-in reminders in the voice of the personalized digital cat, supporting care continuity without guilt or pressure.
- **Care reminder:** when a user-configured care plan suggests checking an appropriate task, ask whether care is needed or already completed; never presume it must be performed.
- **Re-engagement reminder:** after a user-configured period of app inactivity, invite them to catch up on records; inactivity does **not** imply the real cat was neglected.
- **Post-check-in response:** affectionate acknowledgement when real care is logged, without rewarding unnecessary grooming.
- **Controls / safeguards:** explicit opt-in, configurable per-task schedule and quiet hours, snooze/disable, frequency cap, no shame or streak penalties, no universal medical/grooming intervals; guidance should account for the individual cat and veterinary advice.
- **Validation question:** do busy, experienced cat owners prefer task-based reminders, a gentle digital-cat check-in, both, or neither? Test perceived helpfulness versus notification fatigue.
- **Scope gate:** candidate core experience; notification delivery is not automatically committed to MVP before validation.

### Pocket Kitty — ambient virtual-cat companion (Owner direction, 2026-10-15)
- **Decision:** the product should feel like caring for an adorable electronic pet, not a high-pressure streak app. Inspiration: a memorable mascot and small home-screen widget, explicitly *not* guilt-driven Duolingo-style nudges.
- **Small home-screen widget — Experience hypothesis:** personalized cat rests, stretches, peeks, grooms itself, or waves; tapping opens the cat or relevant care log. Widget is ambient companionship, not a persistent task alarm.
- **Affection / progression — Experience hypothesis:** logging appropriate real-world care unlocks gentle animations, expressions, keepsakes, and optional accessories. No neglect simulation, deterioration, sadness, lost streak, or punishment for inactivity.
- **Gentle messaging:** playful invitations rather than urgency or guilt; silence is an acceptable state. The companion is happy when the owner returns, not distressed when absent.
- **Notifications:** optional, quiet-hours-aware, rate-limited, independently configurable for care reminders vs. friendly check-ins. Widget behavior must not imply that an inactive app means an uncared-for real cat.
- **Validation:** compare static tracker, tracker + mascot, and widget mockups with busy experienced cat owners. Measure delight *and* willingness to keep logging; distinguish novelty from durable value.
- **Scope gate:** concept approved for Core Experience; native iOS widget, animation system, and personalization depth remain candidate MVP features pending validation and feasibility review.

### My Kitty, My Companion — onboarding and multi-cat (Owner direction, 2026-10-16)
- **Decision:** offer two entry paths: (1) "I have a cat" with optional photo upload to create a stylized digital likeness; (2) "Adopt a virtual kitty" without owning a real cat. Photo upload is skippable; a preset avatar is always available.
- **Decision:** support multi-cat households with separate profiles, avatars, schedules, and care histories; allow adding or switching cats later.
- **Real Kitty:** associate a real cat profile with an optional photo-derived digital companion. Keep care check-ins tied to the correct real cat; allow correcting or replacing generated appearance.
- **Virtual Kitty:** playful companionship, expressions and customization without pretending virtual actions are real grooming or generating fake care history.
- **Onboarding hypothesis:** choose path → name cat → optionally upload photo / select preset → see companion immediately → optionally set up a care routine. Keep first session short and avoid mandatory account/photo upload before showing value where feasible.
- **Safety/privacy constraints:** photo upload must be consensual, explain image processing/storage and deletion; minimize photo retention, avoid implying generated avatars are exact matches; keep each cat's records separate.
- **Validation:** test the two-path onboarding with busy experienced owners, including multi-cat owners; measure setup completion, time to first companion, photo-upload opt-in, and confusion between real and virtual care.
- **Scope gate:** this is approved product direction, not approval to build image-generation, multiple cat accounts, or an entire virtual-pet game before MVP validation.

## MVP
### Capabilities
**TBD.** Do not freeze features until the problem/frequency assumption is better understood.

### Non-goals
- **Decision:** no commerce/toolkit marketplace in the first validation scope.
- **Decision:** do not build the full long-term virtual-pet vision before validating recurring care value.

### Product acceptance criteria
TBD during MVP phase.

## Validation
- **Riskiest assumption:** cat owners have enough recurring grooming pain or forgetfulness to return to a dedicated grooming app.
- **Existing evidence:** desk research confirms competitor functionality, but there is **no direct user-interview or retention evidence** for our concept.
- **Cheapest next validation:** 5–8 short interviews with experienced, busy cat owners; ask about the last 30 days of actual grooming, missed care, current workarounds, and reaction to two simple prototype screens (plain tracker vs tracker + digital-cat feedback).
- **Positive threshold — Proposed, not yet approved:** at least 4 of 8 interviewees describe a concrete recent care-tracking problem; at least 4 of 8 opt into a 2-week prototype trial after seeing both concepts.
- **Negative threshold — Proposed:** fewer than 2 of 8 have concrete tracking friction, or fewer than 2 of 8 opt into a trial; revisit problem or park.

## Success metrics
TBD after the core experience and validation method are defined.

## Risks and unknowns
- Grooming may be too infrequent for a strong retention loop.
- The digital-cat layer may create delight without changing care behavior.
- Commerce/toolkit demand is unvalidated and outside the immediate problem test.

## Open Product Owner decisions
- **Resolved:** C — real care check-ins drive digital-cat progression.
- **Resolved (2026-10-15):** first validation cohort = experienced, busy cat owners; new owners are not the initial focus.
- **Pending:** MVP scope and BUILD approval; no engineering issues before owner gate.

## Build readiness
- **Status:** NOT READY
- **Missing before BUILD:** problem-frequency evidence, alternatives/competitor evidence, core journey, MVP/non-goals, validation result or explicit waiver, success metrics, and Product Owner BUILD approval.

## First-cohort research plan (2026-10-15)
- **Owner decision:** recruit experienced cat owners with demanding work or family schedules; do not assume they have a problem simply because they are busy.
- **Recruitment screener:** cat ownership for 2+ years (operational proxy, not a validated segment boundary); self-described busy schedule; personally responsible for at least one care routine.
- **Interview (10–15 min):** (1) What grooming did you actually do in the last 30 days? (2) What did you postpone or forget, if anything? (3) How do you remember and record it today? (4) What is inconvenient about that approach? (5) Would a care log alone be useful? (6) Does seeing a personalized digital cat respond to completed *appropriate* care change your willingness to return? (7) Would you try a two-week prototype? Why/why not?
- **Analysis:** separate concrete past behavior from hypothetical enthusiasm; record task frequency, current workaround, pain intensity, prototype preference, and trial opt-in per participant. Avoid leading questions before eliciting recent behavior.
- **Guardrail:** rewards must never encourage unnecessary grooming, over-cleaning, or animal distress.
- **Next gate:** review findings and decide STAY / VALIDATE / PARK; no BUILD without owner approval.
