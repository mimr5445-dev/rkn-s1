# Current state (as of 2026-11-09, after S4)

## Working
- Rendering (`render.mjs`): the example project renders 14 stills and a contact sheet, inspected by eye (INC-007).
- Audio layer (v1): imports, and generates all 35 sound effects and 11 music moods with no silence or clipping (`tests/test_audio.py`).
- JS modules: every named import resolves to an export (`tests/check_js_imports.py`).
- Python and JS syntax checks pass for all kit files.
- Dependencies: Node 22, ffmpeg 6.1, numpy, scipy and faster-whisper are installed. npm packages are installed.

## Studio v2 character, motion, body, gait, skills (M1–M3a)
- Character system with identity separated from pose. Consistency tests pass.
- Motion: keyframes, easing, spring follow-through.
- Body detail and expression: hands, feet, five expressions.
- Ground contact and walk: two-bone IK, walk cycle with pelvis bob.
- Skill loader: validates and loads character and location skills from folders; external skills load without core change.
- Known limits (unchanged): simple limbs in places, knees can read slightly bow-legged from front, only character + location skill kinds so far, no lip sync, no eye direction, no full pipeline yet.

## S4 Sound design spec (design only)
- `docs/design/sound-system.md` defines measurable limits:
  - Final mix: −14.0 LUFS ± 1.0 LU integrated, true peak ≤ −1.0 dBTP.
  - Relative levels and ducking rules for music (−9 to −12 dB under voice), ambience (−18 to −28 dB), SFX.
  - High-frequency energy limits above 6 kHz to reduce harshness on phone speakers.
  - Determinism, sample rate (48 kHz), silence and clipping rules.
- No generation code yet. Next work is M4 (sound library built against these numbers).

## Not verified
- Whether the v1 audio output sounds the same as the original author's version (INC-001 fix was rebuilt from call sites).

## Broken or open
- Eight kit files differ from the recorded "tested version" hashes (INC-005).
- `_restore/` payloads are truncated (INC-004).
- License: proprietary, all rights reserved (DEC-005). Owner to confirm v1 origin rights.
- INC-009: tokens exposed in chat — owner must revoke them.
- INC-016: hair layering had no numeric guard (open gap).

## Branch
- Work for S4 is on `docs/sound-system-spec` (to be merged after review).
