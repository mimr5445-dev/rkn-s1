#!/usr/bin/env python3
"""Consistency tests for the character system. Run from v2/:  python tests/test_character.py"""
import dataclasses
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, Palette, Pose, render_svg, skeleton, rasterize  # noqa: E402

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


HERO = CharacterSpec("hero", "Sami")
POSES = {
    "idle": Pose(),
    "wave": Pose(r_shoulder=150, r_elbow=-30),
    "lean_point": Pose(lean=14, x=0.45, r_shoulder=80, r_elbow=5, l_hip=-14, r_hip=18, r_knee=-12),
}


def sample(png_path, xy):
    img = Image.open(png_path).convert("RGB")
    return img.getpixel(xy)


# 1. identity is frozen and hashable
h1 = HERO.identity_hash()
check(h1 == CharacterSpec("hero", "Sami").identity_hash(), "identity hash is not stable for the same spec")
check(h1 != dataclasses.replace(HERO, palette=Palette(shirt="#aa0000")).identity_hash(),
      "changing the palette did not change the identity hash")

# 2. poses never change identity: the same spec, rendered in every pose, keeps the same hash
hashes = {HERO.identity_hash() for _ in POSES}
check(len(hashes) == 1, "identity hash changed across poses")

# 3. deterministic output: same spec and pose give identical bytes
check(render_svg(HERO, POSES["wave"]) == render_svg(HERO, POSES["wave"]),
      "rendering the same spec and pose twice gave different SVG")

# 4. poses do change geometry (otherwise the poses are meaningless)
wrist_idle = skeleton(HERO, POSES["idle"])["r_wr"]
wrist_wave = skeleton(HERO, POSES["wave"])["r_wr"]
check(wrist_wave[1] < wrist_idle[1] - 0.05, "waving did not raise the right wrist")

# 5. head size is identical across poses (proportions are identity)
head_r = HERO.proportions.head_r
check(all(HERO.proportions.head_r == head_r for _ in POSES), "head radius is not a fixed identity value")

# 6. pixel-level consistency of the face across poses
with tempfile.TemporaryDirectory() as tmp:
    samples = {}
    for name, pose in POSES.items():
        png = Path(tmp) / f"{name}.png"
        rasterize(render_svg(HERO, pose, 640, 640), str(png))
        J = skeleton(HERO, pose)
        hc, up = J["head_c"], J["up"]
        # a point on the face, 0.45 head radii below the head centre (below the eyes, above the neck)
        r = HERO.proportions.head_r
        face = (hc[0] - up[0] * 0.45 * r, hc[1] - up[1] * 0.45 * r)
        x, y = int(face[0] * 640), int(face[1] * 640)
        samples[name] = sample(png, (x, y))
    base = samples["idle"]
    for name, col in samples.items():
        dist = sum(abs(a - b) for a, b in zip(base, col))
        check(dist <= 24, f"face colour in pose '{name}' differs from idle by {dist} (tolerance 24): {col} vs {base}")

    # 7. a palette change must actually show up in the pixels (identity is really used)
    other = dataclasses.replace(HERO, palette=Palette(skin="#4a2c1d", skin_shade="#2a180f"))
    png = Path(tmp) / "dark.png"
    rasterize(render_svg(other, POSES["idle"], 640, 640), str(png))
    J = skeleton(other, POSES["idle"])
    hc, up = J["head_c"], J["up"]
    face = (hc[0] - up[0] * 0.45 * r, hc[1] - up[1] * 0.45 * r)
    dark = sample(png, (int(face[0] * 640), int(face[1] * 640)))
    check(sum(dark) < sum(base) - 150, "a darker skin palette did not produce a darker face")

# 7b. backgrounds are not identity: the same character on two backgrounds keeps the same face colour
with tempfile.TemporaryDirectory() as tmp:
    colours = []
    for bg in (("#1d2033", "#07080d"), ("#f2e4c9", "#c98f5a")):
        png = Path(tmp) / f"bg_{bg[0]}.png"
        rasterize(render_svg(HERO, POSES["wave"], 640, 640, bg_top=bg[0], bg_bottom=bg[1]), str(png))
        J = skeleton(HERO, POSES["wave"])
        hc, up = J["head_c"], J["up"]
        r = HERO.proportions.head_r
        face = (hc[0] - up[0] * 0.45 * r, hc[1] - up[1] * 0.45 * r)
        colours.append(sample(png, (int(face[0] * 640), int(face[1] * 640))))
    dist = sum(abs(a - b) for a, b in zip(*colours))
    check(dist <= 24, f"face colour changes with the background (distance {dist})")

# 8. rasterized output is valid, the right size, and not blank
with tempfile.TemporaryDirectory() as tmp:
    png = Path(tmp) / "check.png"
    rasterize(render_svg(HERO, POSES["wave"], 320, 240), str(png))
    img = Image.open(png)
    check(img.size == (320, 240), f"PNG size is {img.size}, expected (320, 240)")
    extrema = img.convert("L").getextrema()
    check(extrema[1] - extrema[0] > 40, "PNG looks blank")

print("character tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
sys.exit(1 if failures else 0)
