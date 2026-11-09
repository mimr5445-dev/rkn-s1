# Design: ground contact and walk (v2, M2c)

## Goal
Feet touch the floor and do not sink into it. A simple walk cycle is generated from a few parameters.

## Components
1. **Two-bone IK** (`studio/gait.py`): given a hip joint and a target ankle, solve thigh and knee so the ankle reaches the target exactly when it is within reach. Out of reach, the target is clamped to the maximum reach and the function reports it.
2. **Ground**: a horizontal line at `GROUND_Y` (a fraction of canvas height). A foot's bottom edge must not go below it.
3. **Walk cycle** (`walk_poses`): stance (foot on the ground, moving backward relative to the body at the body's speed) and swing (foot lifted in a half-sine arc, moving forward). The two legs are half a cycle apart. Arms swing opposite to the legs.

## Rules
- Identity is untouched. Only `Pose` changes.
- Hip joints come from the skeleton, so IK always uses the real hip positions.
- Knee angle in `Pose` is relative to the thigh, which matches the existing skeleton convention.
- Deterministic: no randomness, fixed parameters.

## Tests (must pass)
- IK reaches reachable targets (error below 1e-6).
- IK clamps unreachable targets and returns finite values.
- During the walk, no foot bottom is below the ground by more than a small tolerance.
- During stance, the planted foot does not slide (world x speed close to zero).
- Motion stays continuous: no ankle jumps between frames.
- Output is deterministic. Identity hash is unchanged.

## Out of scope
- Physics-based balance, body dynamics, and stairs or uneven ground.
- Pelvis height from foot-contact solving (the hip height is fixed for each walk).
