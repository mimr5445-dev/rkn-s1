# Achievements log (chronological)

One entry per milestone or verified deliverable. Each entry names the commit or merge and the evidence.
Add a new entry for every milestone before the work is merged.

| Date | Milestone | What was delivered | Commit / merge | Evidence |
|---|---|---|---|---|
| 2026-11-09 | Baseline | v1 repository as received | 66fa992 | git history |
| 2026-11-09 | M0: diagnosis | Diagnosis report, memory structure, incident index | 38236f4, 16516d5 | project-memory/, INC-001 to INC-009 |
| 2026-11-09 | v1 audio fixes | Audio layer imports and renders (35 effects, 11 moods) | 2a8a729 (merged in 38236f4) | tests/test_audio.py passes |
| 2026-11-09 | v1 safe restore | Restore script validates before writing | 7b56293 (merged in 38236f4) | restore refuses truncated payload |
| 2026-11-09 | v1 render verified | Example project renders 14 stills and a contact sheet | abe6f2a (merged in 16516d5) | render exit 0, contact sheet inspected by eye |
| 2026-11-09 | DEC-001 | Originals no longer binding | 21a9a22 | DEC-001 |
| 2026-11-09 | DEC-002 | Scope of the new product (revised after owner clarification) | 2d67ab0, 50398b4 | DEC-002 |
| 2026-11-09 | M1: character system | Identity separate from pose, deterministic SVG to PNG | b86dd9f (merged in 36ad9d2) | tests/test_character.py, hero sheet |
| 2026-11-09 | M2a: motion | Keyframes, easing, spring follow-through | 30e8bfe (merged in dc04c3a) | tests/test_motion.py, wave clip |
| 2026-11-09 | Roadmap and handoff | ROADMAP.md, HANDOFF.md | b3da006 | files in repository |
| 2026-11-09 | DEC-004 | v1 archived, verify_kit.py removed | 57da346 | DEC-004 |
| 2026-11-09 | DEC-005 | Proprietary licence | 4c56638 | LICENSE, DEC-005 |
| 2026-11-09 | DEC-006 | Rename to RKN-S1, stale instructions fixed | 11138eb | DEC-006 |
| 2026-11-09 | M2b: body and expression | Hands, feet, five expressions | c290b51 | tests/test_body_expression.py, expression sheet |
| 2026-11-09 | M2c: ground and walk | Two-bone IK, walk with pelvis bob, guards on knee and arms | 2b0c76f (plus the guards and pelvis bob in the next commit) | tests/test_gait.py, walk sheet |
| 2026-11-09 | M3a: skill loader | Skills validated and loaded from folders; two sample skills (character, location); a skill added from outside the core loads with no core change | (merge of feat/v2-skill-loader) | tests/test_registry.py, skills_sheet.png |
| 2026-11-09 | S4: sound design spec | Measurable limits for loudness (−14 LUFS), true peak (−1 dBTP), high-band energy, relative levels and ducking | (this branch) | docs/design/sound-system.md |
