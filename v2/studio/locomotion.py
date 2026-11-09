"""Locomotion planning: phase, foot targets, support schedule. No Pose assembly here."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SupportState:
    """Weight on left foot in [0, 1]; right is 1 - w_left."""
    w_left: float
    phase: float

    @property
    def w_right(self) -> float:
        return 1.0 - self.w_left

    @property
    def stance_side(self) -> str:
        """Dominant support for single-support tests: 'l', 'r', or 'both'."""
        if self.w_left >= 0.75:
            return "l"
        if self.w_right >= 0.75:
            return "r"
        return "both"


def walk_phase(t: float, cycle_s: float) -> float:
    """Phase in [0, 1)."""
    if cycle_s <= 0:
        raise ValueError("cycle_s must be positive")
    return (t / cycle_s) % 1.0


def support_at(phase: float) -> SupportState:
    """Smooth weight transfer. See docs/design/locomotion.md."""
    p = phase % 1.0

    def smooth(u: float) -> float:
        u = min(max(u, 0.0), 1.0)
        return u * u * (3.0 - 2.0 * u)

    if p < 0.1:
        w = 0.5 + 0.5 * smooth(p / 0.1)
    elif p < 0.4:
        w = 1.0
    elif p < 0.6:
        w = 1.0 - smooth((p - 0.4) / 0.2)
    elif p < 0.9:
        w = 0.0
    else:
        w = 0.5 * smooth((p - 0.9) / 0.1)
    return SupportState(w_left=w, phase=p)


def foot_local(phase: float, stride: float, lift: float) -> Tuple[float, float]:
    """Foot offset relative to its hip line: (dx, lift_above_ground). Continuous over the cycle."""
    p = phase % 1.0
    if p < 0.5:
        u = p / 0.5
        return stride * (1.0 - 2.0 * u), 0.0
    u = (p - 0.5) / 0.5
    return -stride + 2.0 * stride * u, lift * math.sin(math.pi * u)


def root_speed(stride: float, cycle_s: float) -> float:
    """Horizontal speed so a stance foot stays planted in world space (two steps per cycle)."""
    if cycle_s <= 0:
        raise ValueError("cycle_s must be positive")
    return 4.0 * stride / cycle_s
