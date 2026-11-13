"""Inertialization: clip-to-clip transitions that keep angular velocity.

David Bollo, GDC 2018. This is the default transition in Unreal Engine 5 and
in motion matching. There is no clip database here, so motion matching itself
is the wrong tool. The cut still needs this layer.

At a cut, store the pose error and the velocity error. The incoming pose plays
at full weight; only the error decays. The decay is the closed-form damped
harmonic oscillator, not a semi-implicit Euler step, so the result does not
depend on the frame rate and cannot explode.

Angles take the short arc. Rates are not wrapped: wrapping 240 deg/s flips
the sign and the limb kicks the wrong way.

Legs, root position and the face are critically damped (zeta = 1) so a foot
cannot bounce through the floor. Arms and lean are slightly underdamped so
they follow through.

This module does not sample timelines. `motion.py` stays the keyframe sampler.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass
from typing import Dict, Tuple

from .character import Pose

POSE_FIELDS: Tuple[str, ...] = tuple(f.name for f in dataclasses.fields(Pose))
ANGLE_FIELDS = frozenset({
    "lean",
    "l_shoulder", "l_elbow", "r_shoulder", "r_elbow",
    "l_hip", "l_knee", "r_hip", "r_knee",
})

# half-life in seconds, damping ratio
CHANNELS: Dict[str, Tuple[float, float]] = {
    "x": (0.16, 1.0),
    "y": (0.11, 1.0),
    "lean": (0.14, 0.7),
    "l_shoulder": (0.13, 0.55),
    "l_elbow": (0.15, 0.52),
    "r_shoulder": (0.13, 0.55),
    "r_elbow": (0.15, 0.52),
    "l_hip": (0.10, 1.0),
    "l_knee": (0.10, 1.0),
    "r_hip": (0.10, 1.0),
    "r_knee": (0.10, 1.0),
    "brow": (0.08, 1.0),
    "smile": (0.10, 1.0),
    "mouth_open": (0.07, 1.0),
    "blink": (0.05, 1.0),
}

assert set(CHANNELS) == set(POSE_FIELDS), "every pose field needs a transition channel"


def wrap_deg(delta: float) -> float:
    """Shortest signed delta, in degrees, wrapped to (-180, 180]."""
    return ((delta + 180.0) % 360.0 + 360.0) % 360.0 - 180.0


def omega_of(half_life: float, zeta: float) -> float:
    """omega so the envelope decays by half in `half_life` seconds: omega = ln(2) / (zeta * t_half)."""
    return math.log(2.0) / (max(zeta, 0.05) * half_life)


def spring_offset(x0: float, v0: float, t: float, omega: float, zeta: float) -> Tuple[float, float]:
    """Position and velocity of x'' + 2 zeta omega x' + omega^2 x = 0 at time t."""
    if t <= 0.0:
        return x0, v0
    z = max(zeta, 0.0)
    if z >= 0.999:
        e = math.exp(-omega * t)
        b = v0 + omega * x0
        return (x0 + b * t) * e, (v0 - omega * t * b) * e
    wd = omega * math.sqrt(max(0.0, 1.0 - z * z))
    e = math.exp(-z * omega * t)
    cos = math.cos(wd * t)
    sin = math.sin(wd * t)
    a = x0
    b = (v0 + z * omega * x0) / wd
    x = e * (a * cos + b * sin)
    v = -z * omega * x + e * wd * (-a * sin + b * cos)
    return x, v


def _delta(field: str, left: float, right: float, wrap: bool) -> float:
    d = left - right
    if wrap and field in ANGLE_FIELDS:
        return wrap_deg(d)
    return d


@dataclass(frozen=True)
class InertialCut:
    """Error captured at the frame a new clip takes over."""

    err: Dict[str, float]
    err_v: Dict[str, float]

    @staticmethod
    def capture(prev: Pose, prev_v: Pose, target: Pose, target_v: Pose) -> "InertialCut":
        """prev/target are poses. prev_v/target_v are rates, carried in a Pose for convenience.

        Angular *positions* use the short arc. Angular *rates* are subtracted raw.
        """
        err = {
            f: _delta(f, getattr(prev, f), getattr(target, f), True)
            for f in POSE_FIELDS
        }
        err_v = {
            f: _delta(f, getattr(prev_v, f), getattr(target_v, f), False)
            for f in POSE_FIELDS
        }
        return InertialCut(err, err_v)

    def apply(self, target: Pose, target_v: Pose, elapsed: float) -> Tuple[Pose, Pose]:
        """Incoming clip plus the decaying error. Returns (pose, velocity)."""
        pose: Dict[str, float] = {}
        vel: Dict[str, float] = {}
        for field, (half_life, zeta) in CHANNELS.items():
            off_x, off_v = spring_offset(
                self.err[field], self.err_v[field], elapsed, omega_of(half_life, zeta), zeta,
            )
            pose[field] = getattr(target, field) + off_x
            vel[field] = getattr(target_v, field) + off_v
        return Pose(**pose), Pose(**vel)
