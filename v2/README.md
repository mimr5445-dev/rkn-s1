# Studio v2

A new production system (DEC-002, DEC-003). Its strength is consistency: a character keeps the same identity in every shot.

## Status: M1 in progress
- Character system: identity (spec), pose, skeleton geometry, deterministic SVG rendering, PNG output.
- Tests: `python tests/test_character.py`, `python tests/test_motion.py`, `python tests/test_body_expression.py`, `python tests/test_gait.py`, `python tests/test_registry.py`.
- Examples: `python examples/render_hero_shots.py`, `python examples/render_wave_clip.py`, `python examples/render_expression_sheet.py`, `python examples/render_walk_clip.py` (output in `examples/out/`).

## Design
See `docs/design/character-system.md` (at repository root).

## Known limits (M1)
- Hands and feet are simple shapes. Fingers and toes are not drawn.
- Only one hero character is defined.
- No motion over time yet. That is the next milestone.
