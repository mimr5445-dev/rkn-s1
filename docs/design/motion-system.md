# Design: motion system (v2, M2a)

## Goal
Characters move over time with smooth, cinematic motion: keyframes, eased transitions, and secondary physics (spring follow-through and overshoot) on limbs. The character identity is never touched by motion.

## Components
1. **Timeline**: keyframes of poses at times in seconds. Sampling at time t interpolates between the two surrounding keys with an easing curve (ease in/out cubic by default).
2. **Spring follower** (secondary motion): each pose field is driven by a damped spring toward the timeline's target. This creates follow-through: a limb lags, overshoots slightly, and settles. Damping controls how much it overshoots.
3. **Clip rendering**: sample every frame at a fixed fps, render each frame with the existing `render_svg`, and write numbered PNG frames.

## Rules
- Motion only changes `Pose`. `CharacterSpec` is never passed to a motion function for modification.
- Simulation is deterministic: fixed timestep, no randomness. The same timeline gives the same frames.
- The spring uses a fixed sub-step so the result does not depend on frame rate.

## Tests (must pass)
- Interpolation hits keyframe values exactly at the keys.
- Spring output is finite everywhere, and settles to the target within a bounded time.
- Per-frame change is bounded: no sudden jumps (continuity).
- Deterministic output across runs.
- Identity is unchanged by motion (same hash before and after).

## Out of scope for M2a
- Contact with the ground or collisions (feet do not touch the floor physically).
- Inverse kinematics (reaching a target point).
- Expression and lip sync.
