# Design: hands, feet and expressions (v2, M2b)

## Goal
Make the character readable at close range: hands and feet with shape, and a face that can show emotion.

## Decisions
1. **Hand and foot size are identity.** They live in `Proportions` (`hand_len`, `foot_len`). They never change between shots.
2. **Mouth colour is identity.** It lives in `Palette` (`mouth`).
3. **Expressions are pose fields, not identity.** `brow`, `smile`, `mouth_open` and `blink` are floats in `Pose`. This means:
   - they are animatable with the existing motion system (no new code path),
   - a character's face colour and shape never change, only its expression.
4. **Expression presets** are partial pose updates: `neutral`, `happy`, `sad`, `surprised`, `blink`.
5. **Hands** are ellipses along the forearm direction at the wrist. **Feet** are ellipses at the ankle pointing toward image right.

## Layout (in units of head radius r, measured from head centre)
- Eyes: 0.36 r either side, 0.05 r below centre. Blink closes the eye ellipse toward a line.
- Brows: 0.26 r above the eyes. `brow` raises (positive) or lowers (negative) them.
- Mouth: 0.42 r below centre, half width 0.20 r. `smile` bends it, `mouth_open` shows an open mouth.

## Tests (must pass)
- Expression presets render differently from each other.
- Rendering the same expression twice gives identical bytes.
- Skin colour on a cheek point is the same across all expressions and poses.
- A hand and a foot have the expected colour at their centre (proves they are drawn).
- Identity hash is unchanged by pose and expression changes.
- Motion tests still pass with the new pose fields.

## Out of scope
- Finger detail, toe detail, lip sync, and eye direction.
