# Incident index

Format: one entry per problem. Status is one of: fixed (on branch), open, or environmental.

| ID | Date | Title | Status |
|----|------|-------|--------|
| INC-001 | 2026-11-09 | Audio modules cannot import from dsp.py | fixed on branch |
| INC-002 | 2026-11-09 | sine() argument order differs from all callers | fixed on branch |
| INC-003 | 2026-11-09 | Waveform name "tri" not supported | fixed on branch |
| INC-004 | 2026-11-09 | Restore payloads truncated | superseded by DEC-001 |
| INC-005 | 2026-11-09 | Eight kit files do not match recorded hashes | superseded by DEC-001; checker removed in DEC-004 |
| INC-006 | 2026-11-09 | INCOMPLETE.md declared "complete" without evidence | fixed on branch |
| INC-007 | 2026-11-09 | Chromium cannot be installed here, so rendering is unverified | resolved (workaround, environment only) |
| INC-008 | 2026-11-09 | No LICENSE file | fixed: proprietary license (DEC-005) |
| INC-009 | 2026-11-09 | Access tokens pasted into the chat | open, needs owner action |
| INC-010 | 2026-11-09 | Walk stride measured from body centre, not from each hip | fixed (M2c) |
| INC-011 | 2026-11-09 | Knee bent over 55 degrees mid-swing (lifted foot too close to hip) | fixed by pelvis bob (M2c) |
| INC-012 | 2026-11-09 | Arms swung across the torso during the walk | fixed (M2c), guarded by test |
| INC-013 | 2026-11-09 | Hip too low, figure looked crouched | fixed (M2c), guarded by knee test |
| INC-014 | 2026-11-09 | Gait test crashed on empty max() instead of reporting a failure | fixed |
| INC-015 | 2026-11-09 | Negative test used a defect below tolerance and did not fail | fixed |
| INC-016 | 2026-11-09 | Hair cap invisible after the first render (layer order) | fixed, no numeric guard yet (open gap) |
| INC-017 | 2026-11-09 | Merge reported complete before the push reached the remote | fixed, rule L-001 |
| INC-018 | 2026-11-09 | PIPESTATUS[0] unsupported in /bin/sh | fixed, rule L-007 |
| INC-019 | 2026-11-09 | Walk checked on 12 frames only; full-cycle problems were missed | fixed, rule L-002 |
| INC-020 | 2026-11-09 | Owner's ambiguous reply "1 2" was read as one option and recorded | corrected in DEC-002, rule L-006 |

---

## INC-001: audio modules cannot import from dsp.py
- **Symptom:** `ImportError: cannot import name 'expdec'`. sfx.py, music.py and mix.py all failed to import.
- **Evidence:** `dsp.py` on `main` defines no `expdec`, `osc` or `midi_hz`, while all three modules import them.
- **Root cause (confirmed):** the audio modules were written against a different version of `dsp.py` than the one committed. No test imported the modules, so the mismatch was never caught.
- **Fix:** added `osc`, `expdec` and `midi_hz` to `dsp.py`, derived from how the callers use them. Because they were rebuilt from call sites, the exact behaviour may differ from the original author's version.
- **Prevention:** `tests/test_audio.py` imports every module and renders every effect and mood.

## INC-002: sine() argument order differs from all callers
- **Symptom:** none at import time. This is the dangerous one: with the old `sine(n, f)` signature, a call `sine(f, n)` silently produced a wrong-length, wrong-pitch wave.
- **Root cause (confirmed):** same version drift as INC-001. Every caller uses `sine(frequency, n)`, and frequency may be an array for glides.
- **Fix:** changed `sine` to `(f, n, phase)` and made it accept per-sample frequency arrays with phase continuity. Verified: `sine(440)` peaks at 440 Hz.
- **Prevention:** the frequency assertion in `tests/test_audio.py`.

## INC-003: waveform name "tri" not supported
- **Symptom:** `ValueError: unknown wave: tri` in four music moods (wonder, hopeful, triumph, epic).
- **Root cause (confirmed):** `music.py` uses the alias `tri`; `osc` accepted only `triangle`.
- **Fix:** `osc` accepts both names.

## INC-004: restore payloads truncated
- **Symptom:** `EOFError: Compressed file ended before the end-of-stream marker`, for both `missing_00.b64` and `music.py.tar.gz.b64`.
- **Evidence:** both files are exactly 2500 characters and decode to 1875 bytes, which ends mid-stream.
- **Root cause:** unconfirmed. Truncation during upload is the likely cause, given that both are the same size. This should not be stated as fact until the upload is checked.
- **Impact:** `scripts/restore_missing.py` could not restore anything. It now validates first and writes nothing on failure.
- **Next step:** re-upload complete payloads, then run `python scripts/restore_missing.py` to validate. Do not run with `--apply` before validation passes.

## INC-005: eight kit files do not match recorded hashes
- **Symptom:** `verify_kit.py` reports `dsp.py, music.py, sfx.py, fx2d.js, rig2d.js, three-kit.js, ui2d.js, render.mjs` as MISMATCH. 21 of 29 pass.
- **Root cause:** unknown. The recorded hashes come from a "tested version" that is not in this repository. Six of these files were meant to come from the broken restore payloads (INC-004), but `dsp.py` and `render.mjs` were not.
- **Impact:** this is not proof that the files are wrong. The audio files now work (INC-001 to INC-003). The visual files have not been run.
- **Next step:** obtain the tested source and compare. Or re-record the hashes once the owner confirms the current files are correct.

## INC-006: INCOMPLETE.md declared "complete" without evidence
- **Symptom:** the file was named "incomplete" and its content said "complete". The audio layer could not run, which contradicted the claim.
- **Root cause (confirmed):** the status was written from file presence, not from running the code.
- **Fix:** renamed to `STATUS.md` and rewritten from evidence.
- **Prevention:** AGENTS.md rule 3 requires evidence for every claim of success.

## INC-007: Chromium cannot be installed here
- **Symptom:** `playwright install chromium` fails with `Download failure`. No local browser exists.
- **Resolution:** a Chromium 131 binary was taken from the npm package `@sparticuz/chromium` and linked to the paths Playwright expects (`/opt/pw-browsers/...`). This is a workaround for this sandbox only and is not part of the repository.
- **Verified:** `doctor.py` reports Chromium OK. `render.mjs --project examples/reaction-time --sheet --scale 0.3` exits 0 and writes 14 stills and a contact sheet. The contact sheet was inspected by eye and shows the stick-figure scenes, sets, charts and captions as intended.
- **Still open:** the render was checked on this sandbox only, and not on the target machine.

## INC-009: Access tokens pasted into the chat
- **Symptom:** three GitHub personal access tokens were typed into the conversation. One was rejected with 403. A second one was used once for a single push of `main` (to `38236f4`) and was not stored anywhere.
- **Impact:** both tokens are exposed in the conversation transcript and must be treated as compromised.
- **Required action (owner):** revoke both tokens on GitHub immediately, and check the account's recent activity. Create a new token only if needed, with access limited to this repository.
- **Prevention:** never paste credentials into chat. Use `git credential` or SSH on the owner's machine.

## INC-008: no LICENSE file
- **Symptom:** the README says "license to be decided".
- **Impact:** without a license, others have no right to use or modify the code.
- **Status:** needs an owner decision. This was not decided here.

## INC-010 to INC-020 (details)

- **INC-010 (stride reference):** legs reached too far because each foot's stride was measured from the body centre rather than from its own hip. Root cause: wrong reference point in the design. Found by measuring knee angles. Fix: stride measured from each hip. Guard: knee-angle test (test_gait 6b).
- **INC-011 (knee bend mid-swing):** when a foot lifts, its distance to the hip shrinks and the knee bends sharply (worst 125 degrees over a full cycle). Root cause: a fixed hip height. Found by the new guard on the full 48-frame cycle. Fix: pelvis bob, so the hip rises just enough to keep both legs within reach. Guard: knee interior angle above 140 degrees. Negative check: removing the bob makes the guard fail.
- **INC-012 (arms across the torso):** a positive swing angle moved the left arm inward. Found by eye. Fix: arms swing around a rest pose of plus or minus 8 degrees, with amplitude 6. Guard: wrists stay on their own side of the body centre (test_gait 6c).
- **INC-013 (crouched look):** the hip height was too low, so the knee bend was large. Found by eye. Fix: hip height 0.564. Guard: knee test.
- **INC-014 (test crash):** a max() on an empty list raised an exception instead of a failure message. Found when injecting a defect. Fix: default value and an explicit check.
- **INC-015 (weak negative test):** the first injected skin defect was 3 units, below the 24-unit tolerance. Found on the first injection. Fix: a lean-dependent defect of 28 units, which the test catches.
- **INC-016 (hair layering):** the hair cap was hidden by the skin circle. Found by eye and fixed by changing the layer order. There is no numeric guard for the hair yet. Open gap for M3.
- **INC-017 (premature report):** a merge was reported as done before the push succeeded. Found and corrected when the remote was checked. Rule L-001.
- **INC-018 (shell):** PIPESTATUS[0] is not valid in /bin/sh. Found on first use. Rule L-007.
- **INC-019 (sampling):** the walk was checked on 12 frames, and the knee problem appeared only on the full 48-frame cycle. Rule L-002.
- **INC-020 (ambiguous answer):** the owner's "1 2" reply was read as one option, and DEC-002 was written on that reading. The owner clarified the choice. Rule L-006.
