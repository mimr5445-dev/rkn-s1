#!/usr/bin/env python3
"""Tests for the motion system. Run from v2/:  python tests/test_motion.py"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.character import CharacterSpec, Pose  # noqa: E402
from studio.motion import (  # noqa: E402
    ANGLE_FIELDS,
    Keyframe,
    POSE_FIELDS,
    POSITION_FIELDS,
    Timeline,
    ease_in_out_cubic,
    follow_through,
)

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


A = Pose(r_shoulder=-8, r_elbow=0)
B = Pose(r_shoulder=150, r_elbow=-30, lean=10)
TL = Timeline([Keyframe(0.0, A), Keyframe(1.0, B), Keyframe(2.0, A)])

# 1. interpolation hits the keys exactly
check(TL.sample(0.0) == A, "timeline does not return the first key at t=0")
check(TL.sample(1.0) == B, "timeline does not return the middle key at t=1")
check(TL.sample(2.0) == A, "timeline does not return the last key at t=2")
check(TL.sample(-5.0) == A and TL.sample(99.0) == A, "timeline does not clamp outside its range")

# 2. easing is monotonic on [0,1] and starts/ends at 0/1
vals = [ease_in_out_cubic(i / 100) for i in range(101)]
check(abs(vals[0]) < 1e-12 and abs(vals[-1] - 1) < 1e-12, "easing does not start at 0 or end at 1")
check(all(b >= a - 1e-12 for a, b in zip(vals, vals[1:])), "easing is not monotonic")

# 3. spring follow-through: finite, bounded, settles on the target
frames = follow_through(TL, fps=24)
check(all(math.isfinite(getattr(p, f)) for p in frames for f in POSE_FIELDS), "spring produced non-finite values")
check(max(abs(getattr(p, "r_shoulder")) for p in frames) < 250, "spring diverged (r_shoulder too large)")
end = frames[-1]
check(abs(end.r_shoulder - A.r_shoulder) < 0.5 and abs(end.lean - A.lean) < 0.5,
      f"spring did not settle to the final key (r_shoulder {end.r_shoulder:.2f})")

# 4. follow-through is real: the spring overshoots the target a little on the way
# Use a faster key so secondary motion is visible under the default damping ratio.
TL_fast = Timeline([Keyframe(0.0, A), Keyframe(0.5, B), Keyframe(1.2, A)])
fast_frames = follow_through(TL_fast, fps=24)
peak = max(p.r_shoulder for p in fast_frames)
check(peak > B.r_shoulder + 2.0, f"no useful overshoot: peak {peak:.1f} vs target {B.r_shoulder}")
# but overshoot must stay modest (old physics overshot ~15°; new limit ~10°)
check(peak < B.r_shoulder + 10.0, f"overshoot too large: {peak - B.r_shoulder:.1f}°")

# 5. continuity: no sudden jumps between frames (stricter than before)
max_step = 0.0
for p, q in zip(fast_frames, fast_frames[1:]):
    for f in ANGLE_FIELDS:
        max_step = max(max_step, abs(getattr(q, f) - getattr(p, f)))
check(max_step < 32.0, f"a frame-to-frame jump of {max_step:.1f} degrees is too large")

# 6. determinism: same timeline gives identical frames
check(follow_through(TL, fps=24) == frames, "motion output differs between runs")

# 7. motion never touches identity
spec = CharacterSpec("hero", "Sami")
h = spec.identity_hash()
_ = follow_through(TL, fps=24)
check(spec.identity_hash() == h, "motion changed the character identity")

# 8. invalid input is rejected
try:
    Timeline([])
    check(False, "empty timeline was accepted")
except ValueError:
    pass

# 9. position fields settle without large overshoot (body should not bobble)
TL_pos = Timeline([
    Keyframe(0.0, Pose(x=0.3, y=0.60)),
    Keyframe(0.5, Pose(x=0.7, y=0.55)),
    Keyframe(1.0, Pose(x=0.3, y=0.60)),
])
pos_frames = follow_through(TL_pos, fps=24)
x_vals = [p.x for p in pos_frames]
x_peak = max(x_vals)
x_target = 0.7
check(x_peak < x_target + 0.04, f"position overshoot too large: {x_peak - x_target:.3f}")
check(abs(pos_frames[-1].x - 0.3) < 0.01, "position did not settle")

# 10. field classification is complete
check(set(ANGLE_FIELDS) | POSITION_FIELDS == set(POSE_FIELDS), "field classification misses a Pose field")
check(not (set(ANGLE_FIELDS) & POSITION_FIELDS), "a field is both angle and position")

# 11. negative: extreme under-damping on angles produces large overshoot
# (proves the overshoot upper-bound guard is meaningful)
bad = follow_through(TL_fast, fps=24, angle_damping_ratio=0.30)
bad_peak = max(p.r_shoulder for p in bad)
check(bad_peak > B.r_shoulder + 12.0,
      f"negative check: low damping should overshoot a lot (got {bad_peak - B.r_shoulder:.1f}°)")

print("motion tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
sys.exit(1 if failures else 0)
