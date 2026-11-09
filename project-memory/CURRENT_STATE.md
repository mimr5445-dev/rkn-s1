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

## Not verified
- Whether the audio output sounds the same as the original author's version (INC-001 fix was rebuilt from call sites).

## Broken or open
- Eight kit files differ from the recorded "tested version" hashes (INC-005).
- `_restore/` payloads are truncated (INC-004).
- No LICENSE (INC-008).

## Branch
- `fix/repo-health` was merged into `main` (commit `38236f4`) and pushed.
- Owner action pending: revoke the tokens exposed in chat (INC-009).
