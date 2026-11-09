# Roadmap: Studio v2

Last updated: 2026-11-09. Owner: project owner. Architect of record: see HANDOFF.md.

## Where we are
| Stage | Status | Evidence |
|---|---|---|
| M0: diagnosis, memory, v1 audio fixes, v1 render verified | done | INC-001 to INC-009, DEC-001 |
| M1: character system (identity separate from pose, deterministic SVG to PNG) | done | `v2/tests/test_character.py`, hero contact sheet |
| M2a: keyframes, easing, spring follow-through | done | `v2/tests/test_motion.py`, wave clip |

## Principles that do not change
1. Consistency first: a character never changes between shots. Identity is hashed and tested.
2. Everything is rendered by code. The output is deterministic.
3. The library is original. v1 assets are not reused.
4. Every new capability is a skill that can be added without changing the core.
5. Every claim of success is backed by a test or a visual check. Every problem gets an incident entry.

---

## Short term (next 3 to 4 milestones)

### S1. M2b: body detail and expression
- **Goal:** hands, feet, and a face that can express emotion.
- **Deliverables:** hand and foot shapes that attach to the wrist and ankle. Eyes that blink. Brows and mouth shapes (neutral, smile, frown, open).
- **Acceptance:** identity hash unchanged. Expression changes do not change the face colour. A test checks that each expression renders differently and deterministically. Visual check of a 4-expression sheet.
- **Risk:** detail can break identity. Keep all new features in the identity spec, not in the pose.

### S2. M2c: ground contact and simple foot IK
- **Goal:** feet stay on the floor during walks and turns.
- **Deliverables:** two-bone IK for each leg, a ground plane, and a walk cycle.
- **Acceptance:** foot height is never below the floor by more than a set tolerance. Stride length is constant across cycles. Visual check of a walk clip.

### S3. M3a: skill loader (design first)
- **Goal:** new characters, locations, styles, and sound packs are added as separate skills, without changing core code.
- **Deliverables:** a skill manifest (name, version, provides, requires), a loader that validates it, and a registry. Two sample skills: one character, one location.
- **Acceptance:** adding a skill requires no edit to `studio/`. A test proves this by loading a skill from outside the core. A broken manifest is rejected with a clear error.
- **Why now:** every later item in the library depends on this.

### S4. Sound design spec (design only, no code yet)
- **Goal:** decide what "professional, not harsh" means in numbers before building sounds.
- **Deliverables:** `docs/design/sound-system.md` with loudness target (for example integrated loudness around -16 LUFS for web), peak ceiling, maximum allowed energy above 6 kHz for effects, and a rule for music ducking under voice.
- **Acceptance:** the spec gives measurable limits that a test can check later.

---

## Long term

### L1. Sound library (M4)
- Music beds, effects, and ambience built to the spec in S4.
- Tests: loudness, peak, harshness band, silence check, and clipping check on every asset.
- Note: v1 `audio/` code exists in git history only. Use it as an idea source, not a dependency.

### L2. Character library (M5)
- Multiple characters, body types, outfits, and hair, each as a skill.
- Acceptance: each character passes the consistency test suite.

### L3. Locations, backgrounds, and icons (M5)
- Scene sets with depth layers, lighting, and parallax.
- An icon library (for charts, labels, and callouts) with one shared style rule.

### L4. Cinematic camera (M6)
- Dolly, zoom, pan, and handheld shake, driven by the same spring physics as the motion system.
- Acceptance: camera paths are continuous and deterministic.

### L5. Voiceover to video pipeline (M7)
- Script to shots to timeline to render to mix to MP4.
- Word timestamps from faster-whisper (installed, not yet tested on v2).
- MP4 assembly with ffmpeg (installed, version 6.1).
- Acceptance: one command turns a voiceover into a finished MP4. The output is checked for duration, frame count, audio loudness, and visual non-blank frames.

### L6. Quality gates and releases (ongoing from M3)
- Visual regression: hash the reference frames on every release and flag changes.
- Audio gates from S4.
- Versioning with a changelog entry for every release. Tag each release.
- Incident process: every failure gets an entry with a root cause or the note "unknown".

### L7. Packaging (after M7)
- Decide whether v2 ships as a Claude plugin, a standalone CLI, or both.

---

## Open decisions (owner)
1. **License** (INC-008). Blocks any public release.
2. ~~Retire or keep v1.~~ **Decided (DEC-004):** archived as read-only history.
3. ~~Remove `verify_kit.py`.~~ **Decided and done (DEC-004).**
4. **Token rotation** (INC-009). Owner action.

## Risks
- **Identity drift as the library grows.** Mitigation: the consistency suite runs on every character.
- **Sound sounds harsh.** Mitigation: the S4 limits, enforced by tests.
- **Render time on a CPU-only machine.** Mitigation: measure early (M7) and set a budget.
- **Scope creep.** Mitigation: each milestone has written acceptance criteria before code starts.
