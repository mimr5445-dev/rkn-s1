# Current state (as of 2026-11-09)

## Working
- Rendering (`render.mjs`): the example project renders 14 stills and a contact sheet, inspected by eye (INC-007).
- Audio layer: imports, and generates all 35 sound effects and 11 music moods with no silence or clipping (`tests/test_audio.py`).
- JS modules: every named import resolves to an export (`tests/check_js_imports.py`).
- Python and JS syntax checks pass for all kit files.
- Dependencies: Node 22, ffmpeg 6.1, numpy, scipy and faster-whisper are installed. npm packages are installed.

## Studio v2 (M1, in progress)
- Character system with identity separated from pose. Consistency tests pass, including a defect injected in a temporary copy that the tests caught.
- Visual check: three shots of one character with different poses and backgrounds, inspected by eye.
- Known limits: simple limbs, no hands or feet detail, one hero character, no motion over time yet.

## Studio v2 motion (M2a)
- Keyframe timelines with eased interpolation and spring follow-through. Tests cover exact keys, settling, continuity, determinism, and identity safety. A deliberately overdamped defect was caught.
- Visual check: a wave clip (37 frames) rendered and inspected by eye. The arm rises, holds and returns, and the character keeps its look.
- Known limits: no ground contact, no inverse kinematics, no expression.

## Studio v2 body and expression (M2b)
- Hands and feet drawn as shapes. Expressions: neutral, happy, sad, surprised, blink, driven by pose fields so the motion system can animate them.
- Tests: all expressions differ and are deterministic, cheek skin colour is the same in every expression, hand and foot have the right colour, identity unchanged. A defect that changes skin with expression was caught.
- Visual check: five-expression sheet inspected by eye.
- Known limits: small face at 320 px, no finger or toe detail, no lip sync, no eye direction.

## Studio v2 ground contact and walk (M2c)
- Two-bone IK for each leg. Walk cycle with planted stance feet and arcing swing feet, arms swinging beside the body.
- Tests: IK exact on reachable targets, clamped on unreachable, no foot below the ground, planted feet do not slide, no ankle jumps, deterministic, identity unchanged. A defect that sinks the feet into the ground was caught.
- Visual check: one walk cycle inspected by eye. Legs are near straight, feet step on the ground.
- Known limits: knees bend outward, which reads as slightly bow-legged from the front view. A side view would read better. Hip height is fixed. No balance or body dynamics.

## Not verified
- Whether the audio output sounds the same as the original author's version (INC-001 fix was rebuilt from call sites).

## Broken or open
- Eight kit files differ from the recorded "tested version" hashes (INC-005).
- `_restore/` payloads are truncated (INC-004).
- License: proprietary, all rights reserved (DEC-005). Owner to confirm v1 origin rights.

## Branch
- `fix/repo-health` was merged into `main` (commit `38236f4`) and pushed.
- Owner action pending: revoke the tokens exposed in chat (INC-009).
