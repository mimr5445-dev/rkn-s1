"""Motion: keyframe timelines, eased interpolation, and spring follow-through.

Motion only produces Poses. It never changes a CharacterSpec (identity).
Times are in seconds. Simulation uses a fixed sub-step so results do not depend on the frame rate.

Spring parameters are separated by field kind:
- angle fields (degrees) use a lightly under-damped rotational spring
- position fields (normalised 0–1) use a near-critical translational spring
This avoids the old shared k/c which made limbs bounce too hard and body translation wobble.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .character import Pose

POSE_FIELDS: Tuple[str, ...] = tuple(f.name for f in dataclasses.fields(Pose))

# Fields that live in normalised canvas units (not degrees).
POSITION_FIELDS: frozenset = frozenset({"x", "y"})

# Joint angles in degrees. These must interpolate along the shortest arc
# (otherwise 179 → -179 spins almost a full turn instead of 2 degrees).
JOINT_ANGLE_FIELDS: frozenset = frozenset({
    "lean",
    "l_shoulder", "l_elbow", "r_shoulder", "r_elbow",
    "l_hip", "l_knee", "r_hip", "r_knee",
})

# Expression scalars (typically small ranges like 0–1). Linear blend only.
EXPRESSION_FIELDS: frozenset = frozenset({"brow", "smile", "mouth_open", "blink"})

# Legacy alias used by tests and callers that mean "not a position".
ANGLE_FIELDS: Tuple[str, ...] = tuple(f for f in POSE_FIELDS if f not in POSITION_FIELDS)


def ease_in_out_cubic(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return 4 * u ** 3 if u < 0.5 else 1 - ((-2 * u + 2) ** 3) / 2


def shortest_angle_delta(a: float, b: float) -> float:
    """Signed shortest rotation from a to b in degrees, in (-180, 180]."""
    return (b - a + 180.0) % 360.0 - 180.0


def lerp_pose(a: Pose, b: Pose, u: float) -> Pose:
    """Blend two poses. Joint angles take the shortest arc; positions and expressions are linear."""
    vals = {}
    for f in POSE_FIELDS:
        av, bv = getattr(a, f), getattr(b, f)
        if f in JOINT_ANGLE_FIELDS:
            vals[f] = av + shortest_angle_delta(av, bv) * u
        else:
            vals[f] = av + (bv - av) * u
    return Pose(**vals)


@dataclass(frozen=True)
class Keyframe:
    time: float
    pose: Pose


class Timeline:
    """Keyframes in time order. Sampling eases between the two keys around t."""

    def __init__(self, keys: Sequence[Keyframe]):
        if not keys:
            raise ValueError("a timeline needs at least one keyframe")
        self.keys: List[Keyframe] = sorted(keys, key=lambda k: k.time)

    @property
    def duration(self) -> float:
        return self.keys[-1].time

    def sample(self, t: float) -> Pose:
        if t <= self.keys[0].time:
            return self.keys[0].pose
        if t >= self.keys[-1].time:
            return self.keys[-1].pose
        for a, b in zip(self.keys, self.keys[1:]):
            if a.time <= t <= b.time:
                span = b.time - a.time
                u = 0.0 if span == 0 else (t - a.time) / span
                return lerp_pose(a.pose, b.pose, ease_in_out_cubic(u))
        raise AssertionError("unreachable")


@dataclass
class SpringState:
    value: float
    velocity: float = 0.0


def _critical_damping(stiffness: float) -> float:
    """c_crit = 2 * sqrt(k) for mass = 1."""
    return 2.0 * math.sqrt(max(stiffness, 0.0))


def _spring_step(s: SpringState, target: float, dt: float, stiffness: float, damping: float) -> None:
    """Semi-implicit Euler for a damped spring: x'' = k(target - x) - c x'."""
    accel = stiffness * (target - s.value) - damping * s.velocity
    s.velocity += accel * dt
    s.value += s.velocity * dt


# Default physical parameters (mass = 1).
# Angles: light overshoot for secondary action (damping ratio ~0.65).
# Positions: near-critical so the body does not bobble (damping ratio ~0.92).
DEFAULT_ANGLE_STIFFNESS = 200.0
DEFAULT_ANGLE_DAMPING_RATIO = 0.65   # light overshoot (~5°) for secondary action
DEFAULT_POS_STIFFNESS = 90.0
DEFAULT_POS_DAMPING_RATIO = 0.92    # near-critical so body translation does not bobble


def _field_params(
    field: str,
    angle_stiffness: float,
    angle_damping_ratio: float,
    pos_stiffness: float,
    pos_damping_ratio: float,
) -> Tuple[float, float]:
    if field in POSITION_FIELDS:
        k = pos_stiffness
        c = pos_damping_ratio * _critical_damping(k)
    else:
        k = angle_stiffness
        c = angle_damping_ratio * _critical_damping(k)
    return k, c


def follow_through(
    timeline: Timeline,
    fps: int = 24,
    *,
    angle_stiffness: float = DEFAULT_ANGLE_STIFFNESS,
    angle_damping_ratio: float = DEFAULT_ANGLE_DAMPING_RATIO,
    pos_stiffness: float = DEFAULT_POS_STIFFNESS,
    pos_damping_ratio: float = DEFAULT_POS_DAMPING_RATIO,
    tail: float = 0.5,
    substeps: int = 10,
    # Legacy aliases kept so old call sites still work.
    stiffness: float | None = None,
    damping: float | None = None,
) -> List[Pose]:
    """Drive every pose field with a damped spring toward the timeline. Returns one Pose per frame.

    Angle fields and position fields use separate stiffness / damping-ratio pairs so the
    secondary motion feels cinematic without the body translation wobbling.

    If the legacy `stiffness` / `damping` kwargs are given they override the angle pair
    (kept for backward compatibility with earlier tests and call sites).
    """
    if fps <= 0 or substeps <= 0:
        raise ValueError("fps and substeps must be positive")
    if angle_stiffness <= 0 or pos_stiffness <= 0:
        raise ValueError("stiffness must be positive")
    if angle_damping_ratio < 0 or pos_damping_ratio < 0:
        raise ValueError("damping ratio must be non-negative")

    if stiffness is not None:
        angle_stiffness = stiffness
    if damping is not None:
        # Convert absolute damping to a ratio against the (possibly overridden) angle stiffness.
        angle_damping_ratio = damping / max(_critical_damping(angle_stiffness), 1e-9)

    params: Dict[str, Tuple[float, float]] = {
        f: _field_params(f, angle_stiffness, angle_damping_ratio, pos_stiffness, pos_damping_ratio)
        for f in POSE_FIELDS
    }

    dt = 1.0 / (fps * substeps)
    frames = int(math.ceil((timeline.duration + tail) * fps)) + 1
    first = timeline.sample(0.0)
    states = {f: SpringState(getattr(first, f)) for f in POSE_FIELDS}
    out: List[Pose] = []
    t = 0.0
    for _ in range(frames):
        for _ in range(substeps):
            tgt = timeline.sample(t)
            for f in POSE_FIELDS:
                k, c = params[f]
                _spring_step(states[f], getattr(tgt, f), dt, k, c)
            t += dt
        out.append(Pose(**{f: states[f].value for f in POSE_FIELDS}))
    return out
