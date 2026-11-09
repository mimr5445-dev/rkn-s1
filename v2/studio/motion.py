"""Motion: keyframe timelines, eased interpolation, and spring follow-through.

Motion only produces Poses. It never changes a CharacterSpec (identity).
Times are in seconds. Simulation uses a fixed sub-step so results do not depend on the frame rate.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .character import Pose

POSE_FIELDS: Tuple[str, ...] = tuple(f.name for f in dataclasses.fields(Pose))


def ease_in_out_cubic(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return 4 * u ** 3 if u < 0.5 else 1 - ((-2 * u + 2) ** 3) / 2


def lerp_pose(a: Pose, b: Pose, u: float) -> Pose:
    """Linear blend of two poses, with u in [0, 1]."""
    vals = {f: getattr(a, f) + (getattr(b, f) - getattr(a, f)) * u for f in POSE_FIELDS}
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


def _spring_step(s: SpringState, target: float, dt: float, stiffness: float, damping: float) -> None:
    """Semi-implicit Euler for a damped spring: x'' = k(target - x) - c x'."""
    accel = stiffness * (target - s.value) - damping * s.velocity
    s.velocity += accel * dt
    s.value += s.velocity * dt


def follow_through(timeline: Timeline, fps: int = 24, stiffness: float = 180.0,
                   damping: float = 14.0, tail: float = 0.6, substeps: int = 8) -> List[Pose]:
    """Drive every pose field with a damped spring toward the timeline. Returns one Pose per frame.

    The spring lags behind fast changes and overshoots a little, then settles. `tail` extra seconds
    are simulated after the last key so the motion finishes instead of stopping abruptly.
    """
    if fps <= 0 or substeps <= 0:
        raise ValueError("fps and substeps must be positive")
    dt = 1.0 / (fps * substeps)
    frames = int(math.ceil((timeline.duration + tail) * fps)) + 1
    first = timeline.sample(0.0)
    states = {f: SpringState(getattr(first, f)) for f in POSE_FIELDS}
    out: List[Pose] = []
    t = 0.0
    for i in range(frames):
        for _ in range(substeps):
            tgt = timeline.sample(t)
            for f in POSE_FIELDS:
                _spring_step(states[f], getattr(tgt, f), dt, stiffness, damping)
            t += dt
        out.append(Pose(**{f: states[f].value for f in POSE_FIELDS}))
    return out
