# Design: motion system (v2, M2a + physics fix)

## Goal
Characters move over time with smooth, cinematic motion: keyframes, eased transitions, and secondary physics (spring follow-through and overshoot) on limbs. The character identity is never touched by motion.

## Components
1. **Timeline**: keyframes of poses at times in seconds. Sampling at time t interpolates between the two surrounding keys with an easing curve (ease in/out cubic by default).
2. **Spring follower** (secondary motion): each pose field is driven by a damped spring toward the timeline's target. This creates follow-through: a limb lags, overshoots slightly, and settles.
3. **Clip rendering**: sample every frame at a fixed fps, render each frame with the existing `render_svg`, and write numbered PNG frames.

## Spring parameters (physics fix)
Angle fields and position fields use **separate** springs. A single shared k/c made limbs bounce too hard and body translation wobble.

| Kind | Fields | Stiffness | Damping ratio | Intent |
|------|--------|-----------|---------------|--------|
| Angle | shoulders, elbows, hips, knees, lean, expression… | 200 | 0.65 | Light overshoot (~5°) for secondary action |
| Position | `x`, `y` | 90 | 0.92 | Near-critical; body does not bobble |

- Critical damping = `2 * sqrt(k)` (mass = 1).
- Integration: semi-implicit Euler with fixed sub-steps (default 10 per frame).
- Legacy `stiffness` / `damping` kwargs still accepted; they override the angle pair only.

## Rules
- Motion only changes `Pose`. `CharacterSpec` is never passed to a motion function for modification.
- Simulation is deterministic: fixed timestep, no randomness. The same timeline gives the same frames.
- The spring uses a fixed sub-step so the result does not depend on frame rate.
- Overshoot on a typical arm swing stays under ~10°.
- Frame-to-frame angle change stays under ~32° at 24 fps for normal keys.

## Tests (must pass)
- Interpolation hits keyframe values exactly at the keys.
- Spring output is finite everywhere, and settles to the target within a bounded time.
- Per-frame change is bounded: no sudden jumps (continuity).
- Deterministic output across runs.
- Identity is unchanged by motion (same hash before and after).
- Controlled overshoot on angles; position fields stay near-critical.
- Negative: very low damping ratio produces large overshoot (proves the upper bound is meaningful).

## Out of scope
- Contact with the ground or collisions (handled by the gait system).
- Inverse kinematics (handled by the gait system).
- Expression and lip sync driven by audio.
