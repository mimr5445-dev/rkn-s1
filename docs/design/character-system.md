# Design: character system (v2, M1)

## Goal
A character looks identical in every shot. Only its pose and position change. Characters are richer and more professional than the v1 stick figure: outlined shapes, shading, rim light, and distinct clothing.

## Core idea: identity is separate from pose
- **CharacterSpec** (identity): proportions and palette. It is frozen and hashed. Any change to it changes the hash, and the hash is stored with every render.
- **Pose** (per shot): root position, torso lean, and joint angles. Poses never change identity.
- **Skeleton**: forward kinematics turns a spec and a pose into joint positions. It is pure geometry and can be tested without drawing.
- **Render**: skeleton to SVG, with deterministic formatting. SVG to PNG with cairosvg.

## Units
- Lengths are fractions of the canvas height. Positions are fractions of width (x) and height (y), with y pointing down.
- Angles are degrees. An arm or leg angle is measured from straight down, and positive values swing toward +x (image right). An elbow or knee value is added to the parent angle.
- The torso leans with `lean` (0 is upright). Arms and legs are measured in world space, not relative to the torso. This is a v2 simplification to be revisited in M2.

## Layers (back to front)
1. Legs: pants color, with thigh and shin as one outlined stroke each.
2. Shoes.
3. Torso: shirt color, trapezoid with a vertical gradient and a right-edge rim light.
4. Arms: upper arm in sleeve color, forearm in skin color.
5. Head: hair cap, rim-light crescent, skin with radial gradient, two eyes.

Every part has an outline stroke drawn before its fill. This gives a clean, cartoon-like edge that reads as professional at small sizes.

## Consistency guarantees (tested)
- The identity hash is the same across all poses of one character.
- The skin color sampled at a fixed point relative to the head is the same across poses, within a small tolerance.
- Different palettes produce different skin colors (the test checks that identity is actually being used).
- Rendering the same spec and pose twice gives identical SVG bytes.

## Out of scope for M1
- Facial expressions beyond fixed eyes.
- Hands and feet detail.
- Motion over time (physics, easing). This is the next milestone.
- Clothing patterns and accessories beyond solid colors and gradients.
