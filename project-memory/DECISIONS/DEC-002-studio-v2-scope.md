# DEC-002: Studio v2 scope

- **Date:** 2026-11-09
- **Decided by:** project owner (chose: new version of the studio, with skills added and continuous development)
- **Open for confirmation:** the owner's reply was "1 2". This record reads it as option 1, with option 2's idea of reusing only parts of the old work allowed where useful. Confirm or correct.

## What v2 is
A studio that turns a voiceover into a stick-figure video. Every frame is drawn by code (no image or video generation models). Same concept as v1, rebuilt as a new version. Original files are a reference for ideas only (DEC-001).

## Core requirements
1. Input: a voiceover, optionally with a script. Output: a finished video with music and sound effects.
2. Frames are rendered by code and are reproducible: the same input gives the same output.
3. Skills: new capabilities (a visual style, a scene type, a sound pack, a character, an effect) are added as self-contained skills, without editing the core. Each skill declares what it provides and what it needs.
4. Continuous development: every change is tested, every problem is an incident with a root cause, and every release has a changelog entry.

## Non-goals (for now)
- Real-time or interactive editing.
- Generative image or video models.
- Any new packaging beyond the existing Claude plugin format, until the core works.

## Success criteria for v2 core (milestone M1)
- A reference project renders end-to-end from a voiceover to an MP4, from a single command.
- The render is deterministic: two runs produce identical frames (checked by hash).
- A new skill can be added without changing core code, and a test proves it.
- All tests pass on `main`, and every release has a changelog entry.

## Milestones
- **M0 (done):** diagnosis, memory, audio fixes, render verified on v1.
- **M1:** core v2: skill loader, deterministic renderer, end-to-end test on a reference project.
- **M2:** first skill set (styles and sound packs), migrated from v1 ideas.
- **M3:** continuous improvement loop: quality checks per release, and an incident log in use.

## Decisions still needed
1. Which skill to build first in M2.
2. Language of the new code (current code is JavaScript and Python, which is a mixed stack).
3. License (INC-008), which still needs an owner decision.
