---
name: studio-workflow
description: >
  How to work on the RKN-S1 studio (v2) the way the previous architect did: design before code, tests that can fail,
  visual checks backed by numbers, incident and achievement logs, and verified pushes. Use this skill for any task in
  this repository: a new milestone, a fix, a visual change, a refactor, or a handoff. Read it before the first edit.
---

# Studio workflow (RKN-S1)

This skill describes how work gets done in this repository. Follow it in order. Skip nothing, because each step
exists because something went wrong without it (see `project-memory/LESSONS.md`).

## 0. Before you touch anything
1. Read `HANDOFF.md`, then `project-memory/ROADMAP.md`, `project-memory/CURRENT_STATE.md`,
   `project-memory/LESSONS.md`, and the latest entries in `project-memory/ACHIEVEMENTS.md`.
2. Check the open items in `project-memory/INCIDENTS/INCIDENT_INDEX.md`. If your task touches one, read its entry.
3. Run the test suites (see section 6). If anything fails before you start, record it as an incident first.
4. Check the owner's decisions in `project-memory/DECISIONS/`. Do not reopen a decided item without the owner.

## 1. Clarify, then decide
- If the owner's reply can mean two things, ask one short question. Do not pick a reading and build on it (L-006).
- If the decision is technical and the owner has delegated it, decide yourself and record the reason in a DEC file.
- Destructive or irreversible actions (deleting history, rewriting `main`, publishing) need explicit owner approval.

## 2. Design before code
- Write `docs/design/<system>.md` first. It must state: the goal, the decisions, the units and conventions,
  the rules (for example "identity never changes between shots"), the tests that must pass, and what is out of scope.
- Record each non-obvious choice in a `DEC-xxx` file under `project-memory/DECISIONS/`.
- Keep identity (what a thing is) separate from state (what it does at a moment). This split is the core of v2.

## 3. Tests first, and tests that can fail
- Write the test file before the implementation when you can. Each test checks one claim.
- Every test prints `FAIL: <reason>` and exits non-zero. Guard every `min()` and `max()` on possibly empty data.
- **Numeric guards before visual fixes.** If you find a problem by looking at an image, write a numeric check for it
  before you fix it (L-002). Measure over a full cycle at the real frame rate, not a sample.
- **Negative check.** After writing a test, inject a realistic defect into a temporary copy (`/tmp/...`, never in
  the repository) and confirm the test fails. Use a defect that is large enough to matter (L-003). Then confirm the
  real code still passes. Fix the root cause, then confirm the guard fails when the root cause is put back (L-004).

## 4. Implement small, then verify visually
- Keep functions small and pure where possible. Give each module one job.
- Make output deterministic: no randomness without a fixed seed, fixed rounding in SVG, same bytes for the same input.
- After the numeric tests pass, render an example and look at it. Save the image under `examples/out/`, which is git-ignored.
- Record what you saw in the state file. The eye finds problems the numbers miss, so look at every new visual feature.

## 5. Log the work
- **Achievement:** after each milestone, add a row to `project-memory/ACHIEVEMENTS.md` with the commit and the evidence.
- **Incident:** every defect, whether found by a test, by the eye, or by a mistake in the process, gets an entry in
  `INCIDENT_INDEX.md` with: symptom, evidence, root cause (or "unknown"), fix, and the guard that prevents a repeat.
- **Lesson:** if a mistake teaches a rule, add it to `LESSONS.md` with a number.
- **State:** update `CURRENT_STATE.md` with what works, what is verified, and what is still open.
- Do not write "done" without evidence. Write the test name, the number, or the image you checked.

## 6. Commands
From the repository root:
    python3 tests/check_js_imports.py
    cd v2
    python3 tests/test_character.py
    python3 tests/test_motion.py
    python3 tests/test_body_expression.py
    python3 tests/test_gait.py
Each must print PASS. Add your new suite to this list and to `HANDOFF.md`.

## 7. Git flow
- Never work on `main`. Use a branch: `feat/<name>` for features, `fix/<name>` for fixes, `docs/<name>` for records.
- Commit in logical units. Use a message that says what changed and why, with the incident numbers.
- Before merging: run every test suite on the branch. Merge with `--no-ff` so the history shows the feature.
- After merging into `main`, run the test suites again on `main`.
- Push, then **verify the remote**: `git ls-remote origin refs/heads/main` must equal `git rev-parse main` (L-001).
  Report the remote hash, not "pushed".

## 8. Credentials
- Never write a token into a file, a commit, a log, or a message (L-008). Never ask the owner to paste one in chat.
- Use the credential setup the owner provides for the environment. If a token was pasted in chat, use it only for the
  task at hand, do not store it in the repository, and remind the owner to revoke it.
- Sandbox credential stores outside the repository are the only exception, and you must disclose them in the state file.

## 9. Hand off cleanly
- Leave the repository so the next model can start from `HANDOFF.md` alone.
- Make sure the roadmap lists the next milestone with acceptance criteria, and that open questions for the owner are written down.
- Tell the owner in plain language: what was done, what was verified and how, what is not verified, and the one decision needed next.

## 10. How to talk to the owner
- Write in the owner's language (Arabic, in this project). Be direct. Lead with the result.
- Separate verified facts from guesses. Say "I did not check X" when that is true.
- Do not overclaim. Do not hide a failed step. If a push failed, say so first.
- Keep the reply short. Offer one recommended next step and ask one question at most.

## Templates
See `references/templates.md` for the design doc, test file, incident entry and achievement row.
