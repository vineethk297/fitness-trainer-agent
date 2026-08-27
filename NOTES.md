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
- [ ] Full plan review for all 4 test profiles (in progress)
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

### User_2, User_3, User_4 — plan review in progress
(Intake stage completed for all; follow-up answers sent; awaiting/reviewing final plans.)

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

## Design notes / open questions
- All four profiles get an almost identical opening line ("Welcome aboard — I'm genuinely
  excited to work with you!"). This is the First Response Directive working as written,
  but worth deciding: is a consistent opening a feature (brand voice) or does it read as
  templated across very different users? No fix yet — just flagged.
- The "Iterate Based on Feedback" rule (tracking energy/sleep/recovery over time) can't be
  properly tested yet since there's no persistent memory across sessions. This is expected
  — it's the next phase of the project, not a current bug.

## Next steps
1. Finish plan review for User_2, User_3, User_4 against their Test Focus criteria.
2. Add persistent memory (start with a simple JSON file per user) so returning users don't
   re-answer intake every session.
3. Formalize the 4 test profiles into an actual eval script — write explicit pass/fail
   criteria per profile, automate running them, and use an LLM-as-judge to score
   responses against the criteria rather than reading transcripts by hand.
4. Add tool-calling (e.g. logging a completed workout, looking up an exercise
   substitution) once memory is in place.
