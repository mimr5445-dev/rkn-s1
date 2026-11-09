"""Ground contact and walk cycle. Uses two-bone IK for legs. Only Pose changes; identity is never touched."""
from __future__ import annotations

import math
from typing import List, Tuple

from .character import CharacterSpec, Pose, skeleton

GROUND_Y = 0.96   # floor line, fraction of canvas height (y points down)
HIP_Y = 0.564     # fixed hip height for a walk: legs are nearly straight (about 15 degrees of knee bend)


def _deg(rad: float) -> float:
    return math.degrees(rad)


def _wrap(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


def ik_two_bone(hip: Tuple[float, float], target: Tuple[float, float],
                l1: float, l2: float, bend: float = 1.0) -> Tuple[float, float, bool]:
    """Solve thigh angle (absolute, from down) and knee angle (relative to thigh) so the ankle reaches target.

    Returns (thigh_deg, knee_rel_deg, reachable). Out of reach, the target is clamped to the closest reachable point.
    """
    vx, vy = target[0] - hip[0], target[1] - hip[1]
    d = math.hypot(vx, vy)
    lo, hi = abs(l1 - l2) + 1e-9, l1 + l2 - 1e-9
    reachable = lo <= d <= hi
    d = min(max(d, lo), hi)
    theta_t = math.atan2(vx, vy)  # direction hip -> target, from down toward +x
    cos_a = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    a = math.acos(min(1.0, max(-1.0, cos_a)))
    thigh = theta_t + bend * a  # bend = +1 or -1 chooses which side the knee points to
    knee = (hip[0] + math.sin(thigh) * l1, hip[1] + math.cos(thigh) * l1)
    shin = math.atan2(target[0] - knee[0], target[1] - knee[1])
    return _wrap(_deg(thigh)), _wrap(_deg(shin - thigh)), reachable


def _leg_local(phase: float, stride: float, lift: float) -> Tuple[float, float]:
    """Foot offset (x relative to root, lift above ground) for phase in [0, 1). Continuous over the cycle."""
    p = phase % 1.0
    if p < 0.5:  # stance: foot moves from +stride to -stride on the ground
        u = p / 0.5
        return stride * (1 - 2 * u), 0.0
    u = (p - 0.5) / 0.5  # swing: foot moves from -stride to +stride in the air
    return -stride + 2 * stride * u, lift * math.sin(math.pi * u)


def walk_poses(spec: CharacterSpec, n_frames: int, fps: int, cycle_s: float = 1.0,
               stride: float = 0.045, lift: float = 0.035, arm_swing: float = 6.0,
               start_x: float = 0.30) -> List[Pose]:
    """A walk cycle, one Pose per frame. Stance feet stay still in world space; swing feet arc forward."""
    if n_frames <= 0 or fps <= 0 or cycle_s <= 0:
        raise ValueError("n_frames, fps and cycle_s must be positive")
    P = spec.proportions
    ankle_drop = P.limb_w * 0.7  # foot ellipse half height, so the foot's bottom sits on the ground
    root_speed = 4 * stride / cycle_s  # keeps the stance foot still in world space
    poses: List[Pose] = []
    for i in range(n_frames):
        t = i / fps
        cyc = (t / cycle_s) % 1.0
        root_x = start_x + root_speed * t
        root = Pose(x=root_x, y=HIP_Y)
        J = skeleton(spec, root)
        legs = {}
        for side, offset, bend in (("l", 0.0, -1.0), ("r", 0.5, 1.0)):  # knees bend outward
            dx, lift_y = _leg_local(cyc + offset, stride, lift)
            hip = J[f"{side}_hip"]
            target = (hip[0] + dx, GROUND_Y - ankle_drop - lift_y)  # stride is measured from each hip
            thigh, knee, _ = ik_two_bone(hip, target, P.thigh, P.shin, bend)
            legs[f"{side}_hip"] = thigh
            legs[f"{side}_knee"] = knee
        swing = math.sin(2 * math.pi * cyc) * arm_swing  # arms swing beside the body, not across it
        poses.append(Pose(
            x=root_x, y=HIP_Y,
            l_shoulder=8.0 + swing, r_shoulder=-8.0 - swing,
            l_hip=legs["l_hip"], l_knee=legs["l_knee"],
            r_hip=legs["r_hip"], r_knee=legs["r_knee"],
        ))
    return poses
