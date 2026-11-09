# Handoff: how to continue this project

Read this first if you are a new model or a new contributor.

## 1. Read in this order
1. `project-memory/ROADMAP.md`: what to build next and why.
2. `project-memory/CURRENT_STATE.md`: what works and what is open.
3. `project-memory/DECISIONS/`: DEC-001 (originals not binding), DEC-002 (scope), DEC-003 (stack).
4. `project-memory/INCIDENTS/INCIDENT_INDEX.md`: known problems and their status.
5. `docs/design/`: the design for each system. Read the design before changing code.
6. `AGENTS.md`: working rules.

## 2. Working rules (short)
- Design before code. Write the design doc, then the tests, then the code.
- Do not work on `main` directly. Create a branch named `feat/...`, `fix/...`, or `docs/...`.
- Every change must pass the tests below before merging.
- Every problem becomes an incident in `INCIDENT_INDEX.md`, with a root cause or "unknown".
- Do not delete history. Do not rewrite `main`.

## 3. Commands
Run from the repository root unless noted.

    python3 tests/check_js_imports.py              # v1 JS import check
    python3 tests/test_audio.py                    # v1 audio smoke test (takes a few minutes)
    cd v2 && python3 tests/test_character.py       # v2 identity and rendering
    cd v2 && python3 tests/test_motion.py          # v2 motion and physics
    cd v2 && python3 examples/render_hero_shots.py # visual check: hero in 3 shots
    cd v2 && python3 examples/render_wave_clip.py  # visual check: wave clip

## 4. Environment notes
- Python 3.12, numpy, scipy, Pillow, cairosvg (needs system `libcairo2`), faster-whisper.
- Node 22 and ffmpeg 6.1 are installed for v1.
- Chromium for v1 rendering was provided by a workaround that is not in the repo (see INC-007). If it is missing, v1 rendering must be re-verified.
- Shell note: `/bin/sh` does not support `${PIPESTATUS[0]}`. Use `bash -c` or check exit codes directly.

## 5. Things to know before changing code
- Character identity lives in `CharacterSpec`. Pose and motion must never modify it. The consistency tests exist to catch this.
- `render_svg` is the single rendering function. Replacing the rasterizer should not change the character model.
- The motion spring is tuned with stiffness 180 and damping 14. Raising damping too far makes the simulation diverge, and the motion tests catch it.
- v1 audio functions were rebuilt from call sites (INC-001). Do not assume they match the original sound.

## 6. Credentials
- No secrets are stored in this repository. Do not commit tokens or keys.
- Pushing requires the owner's credentials. Use the owner's own git setup. Do not paste tokens into chat or files.
