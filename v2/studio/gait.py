"""Walk cycle orchestrator. Composes locomotion, balance, coordination, and leg IK.

Only Pose changes; CharacterSpec identity is never touched.
"""
from __future__ import annotations

import math
from typing import List, Tuple

from .balance import lateral_shift
from .body_coordination import coordinate
from .character import CharacterSpec, Pose, skeleton
from .locomotion import foot_local, root_speed, support_at, walk_phase

GROUND_Y = 0.96
HIP_Y = 0.564


def _deg(rad: float) -> float:
    return math.degrees(rad)


def _wrap(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


def ik_two_bone(hip: Tuple[float, float], target: Tuple[float, float],
                l1: float, l2: float, bend: float = 1.0) -> Tuple[float, float, bool]:
    """Two-bone IK. Returns (thigh_deg, knee_rel_deg, reachable)."""
    vx, vy = target[0] - hip[0], target[1] - hip[1]
    d = math.hypot(vx, vy)
    lo, hi = abs(l1 - l2) + 1e-9, l1 + l2 - 1e-9
    reachable = lo <= d <= hi
    d = min(max(d, lo), hi)
    theta_t = math.atan2(vx, vy)
    cos_a = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    a = math.acos(min(1.0, max(-1.0, cos_a)))
    thigh = theta_t + bend * a
    knee = (hip[0] + math.sin(thigh) * l1, hip[1] + math.cos(thigh) * l1)
    shin = math.atan2(target[0] - knee[0], target[1] - knee[1])
    return _wrap(_deg(thigh)), _wrap(_deg(shin - thigh)), reachable


def walk_poses(spec: CharacterSpec, n_frames: int, fps: int, cycle_s: float = 1.0,
               stride: float = 0.045, lift: float = 0.035, arm_swing: float = 5.0,
               start_x: float = 0.30, lateral_amount: float = 0.35,
               lean_amp: float = 2.5, counter_amp: float = 5.0) -> List[Pose]:
    """One Pose per frame. Stance feet stay planted in world space; body shifts over support."""
    if n_frames <= 0 or fps <= 0 or cycle_s <= 0:
        raise ValueError("n_frames, fps and cycle_s must be positive")

    P = spec.proportions
    ankle_drop = P.limb_w * 0.7
    speed = root_speed(stride, cycle_s)
    reach = 0.97 * (P.thigh + P.shin)
    poses: List[Pose] = []

    for i in range(n_frames):
        t = i / fps
        phase = walk_phase(t, cycle_s)
        support = support_at(phase)
        coord = coordinate(phase, arm_swing=arm_swing, lean_amp=lean_amp, counter_amp=counter_amp)

        base_x = start_x + speed * t
        shift = lateral_shift(support, P.hip_w, amount=lateral_amount)
        root_x = base_x + shift

        world_targets = {}
        for side, hip_off, offset, bend in (
            ("l", -P.hip_w / 2, 0.0, -1.0),
            ("r", P.hip_w / 2, 0.5, 1.0),
        ):
            dx, lift_y = foot_local(phase + offset, stride, lift)
            tx = base_x + hip_off + dx
            ty = GROUND_Y - ankle_drop - lift_y
            world_targets[side] = (tx, ty, bend, dx)

        bob_y = HIP_Y + coord.pelvis_bob
        root_y = min([bob_y] + [
            ty - math.sqrt(max(reach * reach - dx * dx, 0.0))
            for _, (_, ty, _, dx) in world_targets.items()
        ])

        root = Pose(x=root_x, y=root_y, lean=coord.lean)
        J = skeleton(spec, root)
        legs = {}
        for side, (tx, ty, bend, _) in world_targets.items():
            hip = J[f"{side}_hip"]
            thigh, knee, _ = ik_two_bone(hip, (tx, ty), P.thigh, P.shin, bend)
            legs[f"{side}_hip"] = thigh
            legs[f"{side}_knee"] = knee

        poses.append(Pose(
            x=root_x, y=root_y, lean=coord.lean,
            l_shoulder=coord.l_shoulder, r_shoulder=coord.r_shoulder,
            l_hip=legs["l_hip"], l_knee=legs["l_knee"],
            r_hip=legs["r_hip"], r_knee=legs["r_knee"],
        ))
    return poses
