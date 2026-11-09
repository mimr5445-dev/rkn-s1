# Studio v2

A new production system (DEC-002, DEC-003). Its strength is consistency: a character keeps the same identity in every shot.

## Status: M1 in progress
- Character system: identity (spec), pose, skeleton geometry, deterministic SVG rendering, PNG output.
- Tests: `python tests/test_character.py` checks identity, determinism, pose-independence, pixel-level face consistency and background independence.
- Example: `python examples/render_hero_shots.py` writes three shots and a contact sheet to `examples/out/`.

## Design
See `docs/design/character-system.md` (at repository root).

## Known limits (M1)
- Limbs are simple strokes. Hands and feet are not detailed.
- Only one hero character is defined.
- No motion over time yet. That is the next milestone.
