# Design: inertial transitions (v2)

## Problem
`Timeline.sample` eases between keys with ease-in-out cubic. That curve has zero slope, and zero second derivative, at both ends. A limb that was swinging at 240°/s has its angular velocity set to 0 on the first frame of the next clip. The eye reads that as a hitch. The existing spring in `follow_through` does not fix it: that spring is a semi-implicit Euler step inside one timeline, it is timestep-sensitive, and it is not a cut.

## Choice
Inertialization (David Bollo, GDC 2018). It is the default blend in Unreal Engine 5, including motion matching. Motion matching itself needs a clip database this studio does not have. The transition technique is the part that removes the hitch, and it works on two poses.

At the cut, store:

- pose error, angles on the short arc (−180°, 180°]
- velocity error, subtracted raw (do not wrap a rate; 240°/s must not become −120°/s)

The incoming clip then plays at full weight. Only the error is added back, and it decays as the closed form of `x'' + 2 ζ ω x' + ω² x = 0`. Half-life sets the speed: `ω = ln(2) / (ζ · t½)`. No substeps, so two frame rates give the same pose at the same time.

## Channels
Legs, root (`x`, `y`) and the face are critically damped (`ζ = 1`). A foot must not bounce through the floor. Shoulders, elbows and lean are slightly underdamped (`ζ ≈ 0.52–0.70`, half-life about 0.13–0.15 s) so the arm follows through and then stops.

## Rules
- Motion still only produces `Pose`. `CharacterSpec` is not an argument.
- `studio/motion.py` is unchanged. This is a layer above the sampler: capture at the cut, apply every frame.
- Same inputs, same output.

## Tests
- Position and a 240°/s shoulder both survive the cut. Cubic easing of the same pair drops that rate below 5°/s.
- A critically damped offset does not overshoot. An underdamped offset settles.
- 170° to −170° is a 20° error. A 240°/s rate is not wrapped.
- Deterministic. Identity hash unchanged.
