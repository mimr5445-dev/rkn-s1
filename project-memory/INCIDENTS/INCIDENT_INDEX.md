# Incident index

Format: one entry per problem. Status is one of: fixed (on branch), open, or environmental.

| ID | Date | Title | Status |
|----|------|-------|--------|
| INC-001 | 2026-11-09 | Audio modules cannot import from dsp.py | fixed on branch |
| INC-002 | 2026-11-09 | sine() argument order differs from all callers | fixed on branch |
| INC-003 | 2026-11-09 | Waveform name "tri" not supported | fixed on branch |
| INC-004 | 2026-11-09 | Restore payloads truncated | superseded by DEC-001 |
| INC-005 | 2026-11-09 | Eight kit files do not match recorded hashes | superseded by DEC-001 |
| INC-006 | 2026-11-09 | INCOMPLETE.md declared "complete" without evidence | fixed on branch |
| INC-007 | 2026-11-09 | Chromium cannot be installed here, so rendering is unverified | resolved (workaround, environment only) |
| INC-008 | 2026-11-09 | No LICENSE file | open, needs owner decision |
| INC-009 | 2026-11-09 | Access tokens pasted into the chat | open, needs owner action |

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
