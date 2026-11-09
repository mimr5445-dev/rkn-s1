"""Body coordination for walk: pelvis bob, trunk lean, shoulder–hip counter-rotation, arms."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Coordination:
    lean: float
    l_shoulder: float
    r_shoulder: float
    l_hip_bias: float
    r_hip_bias: float
    pelvis_bob: float


def coordinate(phase: float, arm_swing: float = 5.0, lean_amp: float = 2.5,
               counter_amp: float = 5.0, bob_amp: float = 0.012) -> Coordination:
    """Phase-driven coordination. phase in [0, 1)."""
    p = phase % 1.0
    lean = -lean_amp * math.sin(2.0 * math.pi * p)
    shoulder_wave = math.sin(2.0 * math.pi * p)
    l_sh = 6.0 + arm_swing * shoulder_wave
    r_sh = -6.0 - arm_swing * shoulder_wave
    l_hip_bias = -counter_amp * shoulder_wave
    r_hip_bias = counter_amp * shoulder_wave
    pelvis_bob = bob_amp * (0.5 - 0.5 * math.cos(4.0 * math.pi * p))
    return Coordination(
        lean=lean,
        l_shoulder=l_sh,
        r_shoulder=r_sh,
        l_hip_bias=l_hip_bias,
        r_hip_bias=r_hip_bias,
        pelvis_bob=pelvis_bob,
    )
