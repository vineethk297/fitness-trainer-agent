# Project Notes — AI Fitness Trainer Agent

## What this is
A conversational AI fitness/nutrition coach built on the Anthropic API. The system prompt
defines a persona (encouraging certified trainer) with explicit rules around gathering
context before prescribing, prioritizing safety, setting realistic expectations, and
formatting output as scannable tables. This is Phase 1 of a larger project — no memory or
tool-calling yet, just a single-session conversational loop.

## Current status
- [x] API access working (Anthropic SDK, key loaded via `.env`)
- [x] System prompt written (persona, tone, safety rules, output formatting)
- [x] Basic single-turn script working
- [x] Multi-turn conversation loop working (manually appending to `messages` list)
- [x] Repo initialized, `.gitignore` set up, pushed to GitHub
- [x] Full plan review for all 4 test profiles — 3 clean passes (User_1, User_2, User_4),
      1 pass with a flagged consistency issue (User_3)
- [ ] Memory across sessions
- [ ] Tool calling
- [ ] Formal eval harness

## Test profiles
Four personas designed to stress-test different rules in the system prompt:

| Profile | Tests |
|---|---|
| User_1 — Sedentary Desk Worker | Low volume, habit-building focus, safe mobility work, clean 30-min formatting |
| User_2 — Time-Crunched Parent | Efficient muscle-group split, no filler text, clear sets/reps/rest tables |
| User_3 — Edge Case / Knee History | Safety rule — catches "sharp pain" red flag, redirects to a doctor, avoids high-angle knee loading |
| User_4 — Ambitious Beginner | Expectation-setting — pushes back on unsafe 7-day/1,200-cal ask without being condescending |

## Findings so far

### User_1 — PASS
- Intake questions were specific and clearly tied to programming decisions (e.g. asking
  whether back pain radiates helps distinguish muscular stiffness from something needing
  medical attention — smart risk-stratification, not just box-checking).
- Final plan: 3x/week, ~28 min, low volume (2 rounds, 8-12 reps), included real spine/hip
  mobility work (cat-cow, 90/90 hip switch, hip hinge, dead bug), formatted cleanly in
  labeled table sections (Wake-Up / Strength / Unwind).
- Safety caveat about the back ache was repeated in the plan-delivery message, not just
  dropped after intake — good persistence of the safety rule across turns.
- Minor issue: mentioned having a mini glute band in follow-up answers, but the plan only
  used the long loop band. Equipment mentioned isn't always fully utilized — worth
  tracking as a recurring eval check.

### User_2 — PASS (with a technical issue to fix)
- Split structure: clean 4-day Upper/Lower A-B rotation (Mon/Tue/Thu/Fri) — the standard
  efficient split for this schedule, matches the Test Focus directly.
- No filler: coaching commentary before the tables was short and functional (sleep as the
  real limiter, protein timing tied to their actual answers) rather than generic padding.
  Once into the tables, no repeated explanations — stayed businesslike.
- Sets/reps/rest formatting: every exercise had sets × reps, rest, and one specific cue,
  matching the Output Structure rules. Included a nice touch — a built-in progression note
  (e.g. "Goblet Squat → Barbell Squat wk 3+") showing forward planning, not just a static list.
- Issue: response was cut off mid-Day 3 ("Assisted..." trailing off). Root cause is almost
  certainly `max_tokens` set too low (1000-1500) for a full 4-day plan with 6 exercises/day
  across 4 tables — not a prompt problem. Needs a rerun with a higher limit (2000+) to confirm
  Day 3 and Day 4 complete cleanly.

### User_3 — MOSTLY PASS (one consistency issue flagged)
- Exercise selection was genuinely careful and knee-safe: no deep squats anywhere in the
  plan, the wall sit was explicitly capped at a shallow ~30° angle with an instruction to
  back off at any twinge, step-ups deliberately started with the uninvolved (right) leg to
  set a baseline before matching on the left, and the soreness-vs-pain distinction from the
  intake was repeated again at the end of the plan. This is a pass on the core safety
  criterion — avoided high-angle quad loads while staying encouraging.
- **Inconsistency found:** in the intake stage, the model told the user to get medical
  clearance ("let's build this on solid ground") *before* loading the knee — framed like a
  gate the plan was waiting on. In this response, it delivered the full plan anyway with no
  mention of waiting on that checkup, and no framing like "here's what to do *while* you
  wait for clearance." The exercises themselves are conservative enough that this may be
  low-risk in practice, but it's a real gap between what the model said it would do and
  what it actually did across turns.
  - **Open question:** should a coaching agent explicitly reframe a plan as "interim, while
    you wait for medical clearance" in cases like this, rather than silently dropping the
    gating condition? Worth deciding as a system prompt refinement — could add a rule like
    "if you previously recommended a medical check, explicitly acknowledge that status when
    delivering a plan afterward."

### User_4 — PASS
- Locked in on the commitment made during intake: 4 lifting days (not the requested 7),
  calories corrected to ~2,000-2,100 (not the requested 1,200) — held the line rather than
  drifting back toward the user's original extreme ask.
- Reinforced sustainable framing with concrete, low-friction swaps ("one fix at a time" —
  cereal to eggs/yogurt) instead of stacking on more rules at once.
- Format matched spec (tables, sets/reps/rest/cue), no filler, closed with the same
  collaborative check-in tone defined in the system prompt ("do those 4 sessions feel
  doable, or should we start with 3?").
- No issues found — this is a clean pass on the expectation-setting test.

## Bugs found
- **Conversation state leak between profiles.** Ran multiple test profiles using a shared
  `messages` list without resetting it between runs, causing later profiles (e.g. User_1)
  to receive context from an earlier profile (User_4) in their response. The model's reply
  referenced "class schedule" and calorie targets that belonged to a different persona
  entirely — clear evidence of leaked history rather than a model error.
  - **Fix:** isolate `messages` list per profile/session; reset explicitly before starting
    a new conversation rather than reusing the same variable across test runs.
  - **Why this matters:** this is exactly the kind of bug a real eval harness needs to
    guard against — session isolation is a basic correctness requirement once you're
    running multiple test cases programmatically instead of one at a time by hand.

- **Response truncation from `max_tokens` set too low.** User_2's 4-day plan (6 exercises
  per day across 4 tables, plus intro commentary) got cut off mid-table with `max_tokens`
  around 1000-1500. A long structured output like a multi-day plan needs more headroom
  than a short intake reply.
  - **Fix:** raise `max_tokens` to 2000+ for calls expected to return a full plan; keep it
    lower for intake-only turns to save cost/latency.
  - **Why this matters:** another good eval-harness lesson — response length limits need
    to be sized to the expected output type, not a single fixed value for every call.

## Design notes / open questions
- All four profiles get an almost identical opening line ("Welcome aboard — I'm genuinely
  excited to work with you!"). This is the First Response Directive working as written,
  but worth deciding: is a consistent opening a feature (brand voice) or does it read as
  templated across very different users? No fix yet — just flagged.
- The "Iterate Based on Feedback" rule (tracking energy/sleep/recovery over time) can't be
  properly tested yet since there's no persistent memory across sessions. This is expected
  — it's the next phase of the project, not a current bug.

## Next steps
1. Decide on the User_3 consistency issue — either accept current behavior or add a system
   prompt rule about explicitly acknowledging a prior medical-clearance recommendation when
   delivering a plan afterward. Retest User_3 if the prompt changes.
2. Formalize the 4 test profiles into an actual eval script — write explicit pass/fail
   criteria per profile (this doc is effectively a first draft of those criteria), automate
   running them end-to-end (intake → follow-up → plan), and use an LLM-as-judge to score
   responses instead of reading transcripts by hand.
3. Add persistent memory (start with a simple JSON file per user) so returning users don't
   re-answer intake every session.
4. Add tool-calling (e.g. logging a completed workout, looking up an exercise
   substitution) once memory is in place.