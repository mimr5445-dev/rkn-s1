#!/usr/bin/env python3
"""Tests for ground contact and walk. Run from v2/:  python tests/test_gait.py"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.character import CharacterSpec, Pose, skeleton  # noqa: E402
from studio.gait import GROUND_Y, ik_two_bone, walk_poses  # noqa: E402

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


HERO = CharacterSpec("hero", "Sami")
P = HERO.proportions
FOOT_DROP = P.limb_w * 0.7
TOL = 0.002

# 1. IK reaches reachable targets exactly
rng = random.Random(7)
worst = 0.0
for _ in range(300):
    hip = (0.5, 0.5)
    ang = rng.uniform(0, 2 * math.pi)
    dist = rng.uniform(abs(P.thigh - P.shin) + 0.01, P.thigh + P.shin - 0.01)
    target = (hip[0] + dist * math.sin(ang) * 0.5, hip[1] + dist * math.cos(ang))
    thigh, knee, ok = ik_two_bone(hip, target, P.thigh, P.shin)
    if not ok:
        continue
    pose = Pose(x=0.0, y=0.0, l_hip=thigh, l_knee=knee)
    # rebuild the leg from the solved angles, starting at the same hip
    kx = hip[0] + math.sin(math.radians(thigh)) * P.thigh
    ky = hip[1] + math.cos(math.radians(thigh)) * P.thigh
    ax = kx + math.sin(math.radians(thigh + knee)) * P.shin
    ay = ky + math.cos(math.radians(thigh + knee)) * P.shin
    worst = max(worst, math.hypot(ax - target[0], ay - target[1]))
check(worst < 1e-6, f"IK missed a reachable target by {worst:.2e}")

# 2. IK clamps unreachable targets and returns finite values
thigh, knee, ok = ik_two_bone((0.5, 0.5), (0.5, 0.5 + 10.0), P.thigh, P.shin)
check(not ok and math.isfinite(thigh) and math.isfinite(knee), "far target not flagged as unreachable or not finite")

# 3. walk: no foot bottom goes below the ground
poses = walk_poses(HERO, n_frames=48, fps=24)
lowest = -1.0
for pose in poses:
    J = skeleton(HERO, pose)
    for an in ("l_an", "r_an"):
        lowest = max(lowest, J[an][1] + FOOT_DROP)  # y grows downward; the bottom is the largest y
check(lowest <= GROUND_Y + TOL, f"a foot sank into the ground: bottom {lowest:.4f} vs ground {GROUND_Y}")

# 4. stance foot does not slide: while a foot is planted, its world x barely changes
slides = []
for side_key in ("l_an", "r_an"):
    xs = [skeleton(HERO, p)[side_key][0] for p in poses]
    ys = [skeleton(HERO, p)[side_key][1] for p in poses]
    planted = [i for i in range(len(poses)) if abs(ys[i] - (GROUND_Y - FOOT_DROP)) < 1e-3]
    for i, j in zip(planted, planted[1:]):
        if j == i + 1:
            slides.append(abs(xs[j] - xs[i]))
check(len(slides) > 0, "no planted frames found for the stance check")
check(bool(slides) and max(slides) < 0.004, f"a planted foot slid (max {max(slides, default=float('nan')):.4f})")

# 5. continuity: ankles never jump between frames
max_jump = 0.0
prev = None
for pose in poses:
    J = skeleton(HERO, pose)
    cur = (J["l_an"], J["r_an"])
    if prev is not None:
        for a, b in zip(prev, cur):
            max_jump = max(max_jump, math.hypot(a[0] - b[0], a[1] - b[1]))
    prev = cur
check(max_jump < 0.03, f"ankle jumped {max_jump:.4f} between frames")

# 6. deterministic and identity-safe
check(walk_poses(HERO, 48, 24) == poses, "walk output differs between runs")
h = HERO.identity_hash()
_ = walk_poses(HERO, 10, 24)
check(HERO.identity_hash() == h, "walk changed the identity")

# 6b. legs stay near straight: the knee never bends more than 40 degrees (interior angle above 140)
import math as _m
min_knee = 180.0
for pose in poses:
    J = skeleton(HERO, pose)
    for side in ("l", "r"):
        hip, kn, an = J[side + "_hip"], J[side + "_kn"], J[side + "_an"]
        d1 = _m.dist(hip, kn)
        d2 = _m.dist(kn, an)
        dh = _m.dist(hip, an)
        c = (d1 * d1 + d2 * d2 - dh * dh) / (2 * d1 * d2)
        min_knee = min(min_knee, _m.degrees(_m.acos(max(-1.0, min(1.0, c)))))
check(min_knee > 140.0, f"knee bends too far during the walk (interior angle {min_knee:.1f}, need > 140)")

# 6c. arms swing beside the body: no wrist crosses the torso centre line
for pose in poses:
    J = skeleton(HERO, pose)
    centre_x = (J["l_sh"][0] + J["r_sh"][0]) / 2
    if not (J["l_wr"][0] < centre_x and J["r_wr"][0] > centre_x):
        check(False, "a wrist crossed the body centre line during the walk")
        break

# 7. invalid input is rejected
try:
    walk_poses(HERO, 0, 24)
    check(False, "zero frames was accepted")
except ValueError:
    pass

print("gait tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
sys.exit(1 if failures else 0)
