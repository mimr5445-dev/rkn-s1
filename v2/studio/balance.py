"""Balance helpers: lateral shift of the root toward the supporting foot."""
from __future__ import annotations

from .locomotion import SupportState


def lateral_shift(support: SupportState, hip_w: float, amount: float = 0.35) -> float:
    """Signed offset added to root x, toward the weighted support.

    amount is a fraction of hip width. Positive shifts toward +x (character's right).
    When weight is on the left, shift is negative.
    """
    if hip_w < 0:
        raise ValueError("hip_w must be non-negative")
    return (0.5 - support.w_left) * 2.0 * amount * hip_w


def closer_to(root_x: float, a_x: float, b_x: float) -> str:
    """Return 'a' if root is closer to a_x, else 'b'. Ties → 'a'."""
    return "a" if abs(root_x - a_x) <= abs(root_x - b_x) else "b"
