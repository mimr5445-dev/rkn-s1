# DEC-002: New product scope (revised)

- **Date:** 2026-11-09
- **Decided by:** project owner
- **Revision:** the first version of this record read the owner's reply as "new version of the same studio". The owner clarified that the choice is option 2: a new product built from scratch. Only the principle of character and style consistency carries over. Nothing in the old library is reused as a base.

## What the product is
A video production product whose main strength is **consistency of characters and visual style across every scene**. The team builds its own library, which is large and not minimal:

- Characters, with their poses and movements.
- Locations and backgrounds.
- Visual styles.
- Cinematic motion with physics-based movement.
- Professional sound: music and effects that are polished, not harsh or annoying.
- Icons and graphic elements.

Skills extend the library over time. A new character, location, style, sound pack or effect is added as a self-contained skill, without changing the core.

## Principles
1. **Consistency first.** A character keeps the same look, proportions and style in every shot. This is tested, not assumed.
2. **Original library.** All assets are built by the team. Nothing from the old project is reused as an asset.
3. **Continuous development.** Every change is tested. Every problem is an incident with a root cause. Every release has a changelog entry.

## Decisions still needed (not assumed)
1. **Rendering method.** The old product rendered every frame by code. Should the new one keep that, or use another method? This affects the consistency approach directly, so it must be decided before design.
2. **Visual form of characters.** Stick figures or a richer character style?
3. **First milestone.** Which part to build first: the character system, the sound library, or the motion system.
4. **Language and stack.** The old code is a mix of JavaScript and Python.
5. **License:** decided, proprietary (DEC-005).

## Success criteria for the first milestone (M1)
- One character is defined once and renders consistently across at least three shots with different poses and backgrounds, as proven by a test.
- A new skill can be added without changing core code, and a test proves it.
- All tests pass, and the change is documented.

## Non-goals for now
- Reusing the old library as a base.
- Packaging beyond what is needed to run the core.
