#!/usr/bin/env python3
"""Tests for inertial transitions. Run from v2/:  python tests/test_inertial.py"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.character import CharacterSpec, Pose  # noqa: E402
from studio.inertial import (  # noqa: E402
    CHANNELS,
    InertialCut,
    spring_offset,
    wrap_deg,
    omega_of,
)
from studio.motion import ease_in_out_cubic  # noqa: E402

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


def zero_rate(**over):
    vals = {f: 0.0 for f in CHANNELS}
    vals.update(over)
    return Pose(**vals)


# 1. critical spring does not overshoot and starts on the offset
resting_x, resting_v = spring_offset(10, 0, 0, 4, 1)
check(resting_x == 10 and resting_v == 0, "spring at t=0 must return the offset")

critical_overshoot = False
omega = math.log(2) / 0.1
for i in range(1, 41):
    x, _v = spring_offset(40, 0, i * 0.05, omega, 1)
    if x < -0.05 or x > 40.05:
        critical_overshoot = True
check(not critical_overshoot, "critical knee spring overshot")

# 2. underdamped arm settles
sx, sv = spring_offset(80, 40, 2.0, math.log(2) / (0.55 * 0.12), 0.55)
check(abs(sx) < 0.5 and abs(sv) < 0.5, f"spring did not settle ({sx}, {sv})")

# 3. a 240 deg/s shoulder and the position both survive the cut
prev = Pose(x=0.42, r_shoulder=20, r_knee=12)
prev_v = zero_rate(r_shoulder=240, x=0.3)
target = Pose(x=0.50, r_shoulder=80, r_knee=4)
target_v = zero_rate()
cut = InertialCut.capture(prev, prev_v, target, target_v)
pose0, vel0 = cut.apply(target, target_v, 0.0)
check(abs(pose0.r_shoulder - prev.r_shoulder) < 1e-9, "shoulder position popped at the cut")
check(abs(pose0.x - prev.x) < 1e-9, "root position popped at the cut")
check(abs(pose0.r_knee - prev.r_knee) < 1e-9, "knee position popped at the cut")
check(abs(vel0.r_shoulder - 240) < 1e-9, f"240 deg/s shoulder was lost ({vel0.r_shoulder})")
check(abs(vel0.x - 0.3) < 1e-9, "root velocity was lost")

# one frame later the shoulder is still clearly moving; the offset has not flipped sign
pose1, vel1 = cut.apply(target, target_v, 1.0 / 60.0)
check(abs(vel1.r_shoulder) > 100, f"shoulder stalled within one frame ({vel1.r_shoulder:.1f})")
check(pose1.r_knee * prev.r_knee >= 0 or abs(pose1.r_knee) < abs(prev.r_knee),
      "critical knee crossed through the incoming pose immediately")

# 4. cubic ease-in-out throws that same rate away
dur = 0.36
u = (1.0 / 60.0) / dur
eased = ease_in_out_cubic(u)
cubic_rate = (target.r_shoulder - prev.r_shoulder) * eased / (1.0 / 60.0)
check(abs(cubic_rate) < 5.0, f"cubic ease did not drop the rate below 5 deg/s ({cubic_rate:.2f})")
check(abs(cubic_rate) < abs(vel1.r_shoulder) / 10, "cubic was not much slower than inertialization")

# 5. short arc: 170 -> -170 is a 20 degree error, not 340
arc = InertialCut.capture(Pose(r_shoulder=170), zero_rate(), Pose(r_shoulder=-170), zero_rate())
check(abs(arc.err["r_shoulder"] - wrap_deg(170 - (-170))) < 1e-9, "short-arc helper disagreed")
check(abs(arc.err["r_shoulder"]) < 21, f"angle error took the long way ({arc.err['r_shoulder']})")
# a fast rate near the wrap must keep its sign
fast = InertialCut.capture(Pose(), zero_rate(r_shoulder=240), Pose(), zero_rate(r_shoulder=-10))
check(abs(fast.err_v["r_shoulder"] - 250) < 1e-9, "velocity was wrapped and flipped sign")

# 6. deterministic
again = InertialCut.capture(prev, prev_v, target, target_v)
check(again.apply(target, target_v, 0.2) == cut.apply(target, target_v, 0.2),
      "inertial output differs between runs")

# 7. identity is never an input
spec = CharacterSpec("hero", "Sami")
h = spec.identity_hash()
_ = cut.apply(target, target_v, 0.2)
check(spec.identity_hash() == h, "transition changed the character identity")

# 8. omega matches the half-life definition
check(abs(omega_of(0.13, 0.55) - math.log(2) / (0.55 * 0.13)) < 1e-12, "omega formula drifted")

print("inertial tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
sys.exit(1 if failures else 0)
