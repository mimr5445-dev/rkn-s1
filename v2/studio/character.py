"""Character system: identity (spec), pose, skeleton geometry, and deterministic SVG rendering.

Units: lengths are fractions of canvas height. Positions: x is a fraction of width, y a fraction of height (down).
Angles: degrees. Limb angles are measured from straight down; positive swings toward +x.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from typing import Dict, Tuple

Point = Tuple[float, float]


@dataclass(frozen=True)
class Proportions:
    head_r: float = 0.080
    neck: float = 0.025
    torso: float = 0.260
    shoulder_w: float = 0.150
    hip_w: float = 0.110
    upper_arm: float = 0.150
    forearm: float = 0.140
    thigh: float = 0.190
    shin: float = 0.190
    limb_w: float = 0.034
    outline_w: float = 0.007


@dataclass(frozen=True)
class Palette:
    skin: str = "#e2b391"
    skin_shade: str = "#b87f5f"
    hair: str = "#2a1c14"
    shirt: str = "#2f6a8f"
    shirt_shade: str = "#1c3f57"
    pants: str = "#2b2f3d"
    pants_shade: str = "#171a24"
    shoe: str = "#101116"
    outline: str = "#08080c"
    rim: str = "#ffcf8a"
    eye: str = "#0b0b0f"


@dataclass(frozen=True)
class CharacterSpec:
    """Identity of a character. Frozen: it never changes between shots."""

    id: str
    name: str
    proportions: Proportions = field(default_factory=Proportions)
    palette: Palette = field(default_factory=Palette)

    def identity_hash(self) -> str:
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:16]


@dataclass(frozen=True)
class Pose:
    """Per-shot pose. Changing a pose never changes the character's identity."""

    x: float = 0.5
    y: float = 0.60
    lean: float = 0.0
    l_shoulder: float = 8.0
    l_elbow: float = 0.0
    r_shoulder: float = -8.0
    r_elbow: float = 0.0
    l_hip: float = -3.0
    l_knee: float = 0.0
    r_hip: float = 3.0
    r_knee: float = 0.0


def _add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def _mul(a: Point, k: float) -> Point:
    return (a[0] * k, a[1] * k)


def _dir(deg: float) -> Point:
    r = math.radians(deg)
    return (math.sin(r), math.cos(r))


def skeleton(spec: CharacterSpec, pose: Pose) -> Dict[str, Point]:
    """Forward kinematics. Returns joint positions in canvas-height fractions."""
    P = spec.proportions
    lean = math.radians(pose.lean)
    up: Point = (math.sin(lean), -math.cos(lean))
    across: Point = (math.cos(lean), math.sin(lean))  # image-right when upright

    hip: Point = (pose.x, pose.y)
    shoulder_c = _add(hip, _mul(up, P.torso))
    neck_top = _add(shoulder_c, _mul(up, P.neck))
    head_c = _add(neck_top, _mul(up, P.head_r))

    l_sh = _add(shoulder_c, _mul(across, -P.shoulder_w / 2))
    r_sh = _add(shoulder_c, _mul(across, P.shoulder_w / 2))
    l_el = _add(l_sh, _mul(_dir(pose.l_shoulder), P.upper_arm))
    l_wr = _add(l_el, _mul(_dir(pose.l_shoulder + pose.l_elbow), P.forearm))
    r_el = _add(r_sh, _mul(_dir(pose.r_shoulder), P.upper_arm))
    r_wr = _add(r_el, _mul(_dir(pose.r_shoulder + pose.r_elbow), P.forearm))

    l_hip = _add(hip, _mul(across, -P.hip_w / 2))
    r_hip = _add(hip, _mul(across, P.hip_w / 2))
    l_kn = _add(l_hip, _mul(_dir(pose.l_hip), P.thigh))
    l_an = _add(l_kn, _mul(_dir(pose.l_hip + pose.l_knee), P.shin))
    r_kn = _add(r_hip, _mul(_dir(pose.r_hip), P.thigh))
    r_an = _add(r_kn, _mul(_dir(pose.r_hip + pose.r_knee), P.shin))

    return {
        "hip": hip, "shoulder_c": shoulder_c, "head_c": head_c, "up": up, "across": across,
        "l_sh": l_sh, "r_sh": r_sh, "l_el": l_el, "r_el": r_el, "l_wr": l_wr, "r_wr": r_wr,
        "l_hip": l_hip, "r_hip": r_hip, "l_kn": l_kn, "r_kn": r_kn, "l_an": l_an, "r_an": r_an,
    }


def _f(v: float) -> str:
    return f"{v:.3f}"


def _px(p: Point, W: int, H: int) -> Tuple[str, str]:
    return _f(p[0] * W), _f(p[1] * H)


def _polyline(points, W, H, color, width, extra="") -> str:
    d = " ".join(("M" if i == 0 else "L") + f"{_px(p, W, H)[0]} {_px(p, W, H)[1]}" for i, p in enumerate(points))
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{_f(width * H)}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _poly_fill(points, W, H, fill) -> str:
    d = "M" + " L".join(f"{_px(p, W, H)[0]} {_px(p, W, H)[1]}" for p in points) + " Z"
    return f'<path d="{d}" fill="{fill}"/>'


def _circle(c: Point, r: float, W, H, fill, extra="") -> str:
    cx, cy = _px(c, W, H)
    return f'<circle cx="{cx}" cy="{cy}" r="{_f(r * H)}" fill="{fill}" {extra}/>'


def render_svg(spec: CharacterSpec, pose: Pose, width: int = 640, height: int = 640,
               bg_top: str = "#1d2033", bg_bottom: str = "#07080d") -> str:
    """Deterministic SVG for one character in one pose."""
    P, C = spec.proportions, spec.palette
    J = skeleton(spec, pose)
    W, H = width, height
    up, across = J["up"], J["across"]
    ow = P.outline_w
    sid = spec.id.replace(" ", "_")  # gradient ids unique per character

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        "<defs>",
        f'<linearGradient id="bg-{sid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{bg_top}"/><stop offset="1" stop-color="{bg_bottom}"/></linearGradient>',
        f'<linearGradient id="shirt-{sid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{C.shirt}"/><stop offset="1" stop-color="{C.shirt_shade}"/></linearGradient>',
        f'<radialGradient id="skin-{sid}" cx="0.42" cy="0.38" r="0.7">'
        f'<stop offset="0" stop-color="{C.skin}"/><stop offset="1" stop-color="{C.skin_shade}"/></radialGradient>',
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="url(#bg-{sid})"/>',
    ]

    # 1. Legs (pants), then shoes
    for hip_k, kn_k, an_k in (("l_hip", "l_kn", "l_an"), ("r_hip", "r_kn", "r_an")):
        pts = [J[hip_k], J[kn_k], J[an_k]]
        parts.append(_polyline(pts, W, H, C.outline, P.limb_w + 2 * ow))
        parts.append(_polyline(pts, W, H, C.pants, P.limb_w))
    for an_k in ("l_an", "r_an"):
        parts.append(_circle(J[an_k], P.limb_w * 0.75, W, H, C.shoe))

    # 2. Torso (shirt) with outline and a right-edge rim light
    torso = [J["l_sh"], J["r_sh"], _add(J["r_hip"], (0, 0)), J["l_hip"]]
    parts.append(f'<path d="M{_px(torso[0], W, H)[0]} {_px(torso[0], W, H)[1]} '
                 + " ".join(f"L{_px(p, W, H)[0]} {_px(p, W, H)[1]}" for p in torso[1:])
                 + f' Z" fill="{C.outline}" stroke="{C.outline}" stroke-width="{_f(2 * ow * H)}" '
                   f'stroke-linejoin="round"/>')
    parts.append(f'<path d="M{_px(torso[0], W, H)[0]} {_px(torso[0], W, H)[1]} '
                 + " ".join(f"L{_px(p, W, H)[0]} {_px(p, W, H)[1]}" for p in torso[1:])
                 + f' Z" fill="url(#shirt-{sid})"/>')
    parts.append(_polyline([J["r_sh"], J["r_hip"]], W, H, C.rim, P.limb_w * 0.22,
                           'stroke-opacity="0.85"'))

    # 3. Arms: upper arm in shirt color (sleeve), forearm in skin color
    for sh, el, wr in (("l_sh", "l_el", "l_wr"), ("r_sh", "r_el", "r_wr")):
        parts.append(_polyline([J[sh], J[el], J[wr]], W, H, C.outline, P.limb_w + 2 * ow))
        parts.append(_polyline([J[sh], J[el]], W, H, C.shirt, P.limb_w))
        parts.append(_polyline([J[el], J[wr]], W, H, C.skin, P.limb_w * 0.92))
        parts.append(_circle(J[wr], P.limb_w * 0.5, W, H, C.skin))

    # 4. Head: outline, hair cap, rim crescent, skin, eyes
    hc, r = J["head_c"], P.head_r
    hair_c = _add(hc, _mul(up, 0.22 * r))
    parts.append(_circle(hc, r + ow, W, H, C.outline))
    parts.append(_circle(hair_c, r * 1.02 + ow, W, H, C.outline))
    parts.append(_circle(hair_c, r * 1.02, W, H, C.hair))
    parts.append(_circle(_add(hc, _mul(across, 0.07 * r)), r * 0.98, W, H, C.rim))
    parts.append(_circle(hc, r * 0.88, W, H, f"url(#skin-{sid})"))
    for side in (-1, 1):
        eye = _add(_add(hc, _mul(across, side * 0.36 * r)), _mul(up, -0.05 * r))
        parts.append(_circle(eye, 0.11 * r, W, H, C.eye))

    parts.append("</svg>")
    return "\n".join(parts)


def rasterize(svg: str, out_path: str) -> None:
    """Write a PNG from an SVG string using cairosvg. Output is deterministic for the same SVG."""
    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out_path)
