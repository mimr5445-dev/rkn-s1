"""Character system: identity (spec), pose, skeleton geometry, and deterministic SVG rendering.

Units: lengths are fractions of canvas height. Positions: x is a fraction of width, y a fraction of height (down).
Angles: degrees. Limb angles are measured from straight down; positive swings toward +x.
Identity (CharacterSpec) never changes between shots. Pose, including expression, changes per shot.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field, replace
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
    hand_len: float = 0.060
    foot_len: float = 0.085


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
    mouth: str = "#5a2222"


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
    """Per-shot pose, including expression. Changing a pose never changes the character's identity."""

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
    # expression (animatable floats)
    brow: float = 0.0        # +1 raised, -1 furrowed
    smile: float = 0.0       # +1 happy, -1 sad
    mouth_open: float = 0.0  # 0 closed, 1 open
    blink: float = 0.0       # 0 open, 1 closed


EXPRESSIONS: Dict[str, dict] = {
    "neutral": {},
    "happy": {"smile": 1.0, "brow": 0.2},
    "sad": {"smile": -0.8, "brow": -0.4},
    "surprised": {"brow": 1.0, "mouth_open": 0.9},
    "blink": {"blink": 1.0},
}


def expression(name: str, base: Pose = Pose()) -> Pose:
    """A pose with the named expression applied on top of `base`."""
    if name not in EXPRESSIONS:
        raise ValueError(f"unknown expression: {name}")
    return replace(base, **EXPRESSIONS[name])


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
    l_fdir = _dir(pose.l_shoulder + pose.l_elbow)
    r_fdir = _dir(pose.r_shoulder + pose.r_elbow)
    l_el = _add(l_sh, _mul(_dir(pose.l_shoulder), P.upper_arm))
    l_wr = _add(l_el, _mul(l_fdir, P.forearm))
    r_el = _add(r_sh, _mul(_dir(pose.r_shoulder), P.upper_arm))
    r_wr = _add(r_el, _mul(r_fdir, P.forearm))

    l_hip = _add(hip, _mul(across, -P.hip_w / 2))
    r_hip = _add(hip, _mul(across, P.hip_w / 2))
    l_kn = _add(l_hip, _mul(_dir(pose.l_hip), P.thigh))
    l_an = _add(l_kn, _mul(_dir(pose.l_hip + pose.l_knee), P.shin))
    r_kn = _add(r_hip, _mul(_dir(pose.r_hip), P.thigh))
    r_an = _add(r_kn, _mul(_dir(pose.r_hip + pose.r_knee), P.shin))

    return {
        "hip": hip, "shoulder_c": shoulder_c, "head_c": head_c, "up": up, "across": across,
        "l_sh": l_sh, "r_sh": r_sh, "l_el": l_el, "r_el": r_el, "l_wr": l_wr, "r_wr": r_wr,
        "l_fdir": l_fdir, "r_fdir": r_fdir,
        "l_hip": l_hip, "r_hip": r_hip, "l_kn": l_kn, "r_kn": r_kn, "l_an": l_an, "r_an": r_an,
    }


def _f(v: float) -> str:
    return f"{v:.3f}"


def _px(p: Point, W: int, H: int) -> Tuple[str, str]:
    return _f(p[0] * W), _f(p[1] * H)


def _polyline(points, W, H, color, width, extra="") -> str:
    d = " ".join(("M" if i == 0 else "L") + " ".join(_px(p, W, H)) for i, p in enumerate(points))
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{_f(width * H)}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _circle(c: Point, r: float, W, H, fill, extra="") -> str:
    cx, cy = _px(c, W, H)
    return f'<circle cx="{cx}" cy="{cy}" r="{_f(r * H)}" fill="{fill}" {extra}/>'


def _ellipse(c: Point, rx: float, ry: float, angle_deg: float, W, H, fill, stroke="", sw=0.0) -> str:
    cx, cy = _px(c, W, H)
    st = f' stroke="{stroke}" stroke-width="{_f(sw * H)}"' if stroke else ""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{_f(rx * H)}" ry="{_f(ry * H)}" '
            f'transform="rotate({_f(angle_deg)} {cx} {cy})" fill="{fill}"{st}/>')


def _quad(p0: Point, ctrl: Point, p1: Point, W, H, color, width) -> str:
    a, b, c = _px(p0, W, H), _px(ctrl, W, H), _px(p1, W, H)
    return (f'<path d="M{a[0]} {a[1]} Q{b[0]} {b[1]} {c[0]} {c[1]}" fill="none" stroke="{color}" '
            f'stroke-width="{_f(width * H)}" stroke-linecap="round"/>')


def render_svg(spec: CharacterSpec, pose: Pose, width: int = 640, height: int = 640,
               bg_top: str = "#1d2033", bg_bottom: str = "#07080d") -> str:
    """Deterministic SVG for one character in one pose and expression."""
    P, C = spec.proportions, spec.palette
    J = skeleton(spec, pose)
    W, H = width, height
    up, across = J["up"], J["across"]
    ow = P.outline_w
    sid = spec.id.replace(" ", "_")
    down = (-up[0], -up[1])

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

    # 1. Legs (pants), then feet (ellipses pointing image-right)
    for hip_k, kn_k, an_k in (("l_hip", "l_kn", "l_an"), ("r_hip", "r_kn", "r_an")):
        pts = [J[hip_k], J[kn_k], J[an_k]]
        parts.append(_polyline(pts, W, H, C.outline, P.limb_w + 2 * ow))
        parts.append(_polyline(pts, W, H, C.pants, P.limb_w))
    for an_k in ("l_an", "r_an"):
        foot_c = _add(J[an_k], (P.foot_len * 0.25, 0.0))
        parts.append(_ellipse(foot_c, P.foot_len * 0.55, P.limb_w * 0.7, 0, W, H,
                              C.shoe, stroke=C.outline, sw=2 * ow))

    # 2. Torso (shirt) with outline and a right-edge rim light
    torso = [J["l_sh"], J["r_sh"], J["r_hip"], J["l_hip"]]
    d = "M" + " L".join(" ".join(_px(p, W, H)) for p in torso) + " Z"
    parts.append(f'<path d="{d}" fill="{C.outline}" stroke="{C.outline}" '
                 f'stroke-width="{_f(2 * ow * H)}" stroke-linejoin="round"/>')
    parts.append(f'<path d="{d}" fill="url(#shirt-{sid})"/>')
    parts.append(_polyline([J["r_sh"], J["r_hip"]], W, H, C.rim, P.limb_w * 0.22,
                           'stroke-opacity="0.85"'))

    # 3. Arms: sleeve upper arm, skin forearm, hand ellipse along the forearm
    for sh, el, wr, fd in (("l_sh", "l_el", "l_wr", "l_fdir"), ("r_sh", "r_el", "r_wr", "r_fdir")):
        parts.append(_polyline([J[sh], J[el], J[wr]], W, H, C.outline, P.limb_w + 2 * ow))
        parts.append(_polyline([J[sh], J[el]], W, H, C.shirt, P.limb_w))
        parts.append(_polyline([J[el], J[wr]], W, H, C.skin, P.limb_w * 0.92))
        fdir = J[fd]
        hand_c = _add(J[wr], _mul(fdir, P.hand_len * 0.5))
        # angle in pixel space so the hand lines up with the forearm on non-square canvases
        ang = math.degrees(math.atan2(fdir[1] * H, fdir[0] * W))
        parts.append(_ellipse(hand_c, P.hand_len * 0.5, P.limb_w * 0.55, ang, W, H,
                              C.skin, stroke=C.outline, sw=ow))

    # 4. Head: outline, hair cap, rim crescent, skin, face
    hc, r = J["head_c"], P.head_r
    hair_c = _add(hc, _mul(up, 0.22 * r))
    parts.append(_circle(hc, r + ow, W, H, C.outline))
    parts.append(_circle(hair_c, r * 1.02 + ow, W, H, C.outline))
    parts.append(_circle(hair_c, r * 1.02, W, H, C.hair))
    parts.append(_circle(_add(hc, _mul(across, 0.07 * r)), r * 0.98, W, H, C.rim))
    parts.append(_circle(hc, r * 0.88, W, H, f"url(#skin-{sid})"))

    def face_pt(ax: float, dy: float) -> Point:
        """Point in head units: ax along across, dy along down (both in head radii)."""
        return _add(hc, _add(_mul(across, ax * r), _mul(down, dy * r)))

    for side in (-1, 1):
        eye = face_pt(side * 0.36, 0.05)
        ry = max(0.015, 0.11 * (1 - pose.blink)) * r
        parts.append(_ellipse(eye, 0.11 * r, ry, 0, W, H, C.eye))
        brow_c = face_pt(side * 0.36, -0.26 + pose.brow * 0.07)
        parts.append(_polyline([_add(brow_c, _mul(across, -0.16 * r)), _add(brow_c, _mul(across, 0.16 * r))],
                               W, H, C.hair, 0.035 * r))

    mouth_c = face_pt(0.0, 0.42)
    if pose.mouth_open > 0.05:
        parts.append(_ellipse(mouth_c, 0.16 * r, pose.mouth_open * 0.13 * r, 0, W, H, C.mouth))
    else:
        start = face_pt(-0.20, 0.42 - pose.smile * 0.05)
        end = face_pt(0.20, 0.42 - pose.smile * 0.05)
        ctrl = face_pt(0.0, 0.42 + pose.smile * 0.14)
        parts.append(_quad(start, ctrl, end, W, H, C.mouth, 0.035 * r))

    parts.append("</svg>")
    return "\n".join(parts)


def rasterize(svg: str, out_path: str) -> None:
    """Write a PNG from an SVG string using cairosvg. Output is deterministic for the same SVG."""
    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out_path)
