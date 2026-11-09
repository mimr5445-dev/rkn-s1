# Lessons from the workflow

Each lesson is a rule for the next model or contributor. Each one comes from a real event, linked to an incident.

## L-001: Verify the remote after every push
- **What happened:** I first reported a merge as complete while it had not reached GitHub (push failed for lack of credentials).
- **Rule:** after every push, run `git ls-remote origin refs/heads/main` and compare the hash with local `main`. Report what the remote shows, not what was attempted. (INC-017)

## L-002: Numeric tests must cover what the eye checks
- **What happened:** the stride bug (INC-010) and the high knee bend (INC-011) were found by looking at contact sheets, not by tests. The walk tests passed on a 12-frame sample while the full 48-frame cycle bent the knee past 55 degrees.
- **Rule:** if a visual check finds a problem, add a numeric guard for it before the fix is merged. Measure over a full cycle at the test frame rate, not over a few frames.

## L-003: A negative test must use a realistic defect
- **What happened:** the first injected skin defect was 3 units, below the tolerance, so the test did not fail. (INC-015)
- **Rule:** when injecting a defect, make it large enough to matter, then check the test fails. Then check the real code passes.

## L-004: Remove the defect itself, not only the symptom
- **What happened:** the old stride bug was no longer caught after the pelvis bob fix. That is correct, because the bob removed its harmful effect. The guard that fails is the one that tests the real cause (missing pelvis bob).
- **Rule:** when fixing a defect, check that the new guard fails when the root cause is put back.

## L-005: Test code must fail with a message, not a crash
- **What happened:** a `max()` on an empty list crashed the test runner instead of reporting a failure. (INC-014)
- **Rule:** guard every aggregate (`max`, `min`) on possibly empty data, and use `default=` or an explicit check.

## L-006: Ask when an answer is ambiguous
- **What happened:** the owner answered "1 2" to a two-option question. I chose one reading and built a record on it. The owner then clarified. (INC-020)
- **Rule:** when a reply can mean more than one thing, ask one short question before writing a decision record.

## L-007: Shell portability
- **What happened:** `${PIPESTATUS[0]}` fails under `/bin/sh` with "Bad substitution". (INC-018)
- **Rule:** use `bash -c` for pipeline status, or read exit codes directly.
- **Recurrence (INC-021):** the rule was written down and still broke the next time. Before running any command, check that it works in `/bin/sh`. Prefer plain commands that need no bashisms.

## L-008: Keep secrets out of chat and files
- **What happened:** access tokens were pasted into the conversation. (INC-009)
- **Rule:** never write a token into a file, a commit, or a message. Use the owner's own credential setup. A sandbox credential store, outside the repository, is the only exception, and it must be disclosed.
