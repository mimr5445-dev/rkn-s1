#!/usr/bin/env python3
"""Tests for hands, feet and expressions. Run from v2/:  python tests/test_body_expression.py"""
import dataclasses
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, EXPRESSIONS, Palette, Pose, expression, rasterize, render_svg, skeleton  # noqa: E402
from studio.motion import Keyframe, Timeline, follow_through  # noqa: E402

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


HERO = CharacterSpec("hero", "Sami")
SIZE = 640


def px_at(png, p):
    img = Image.open(png).convert("RGB")
    return img.getpixel((int(p[0] * SIZE), int(p[1] * SIZE)))


def near(a, b, tol=24):
    return sum(abs(x - y) for x, y in zip(a, b)) <= tol


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # 1. each expression renders differently, and deterministically
    svgs = {name: render_svg(HERO, expression(name), SIZE, SIZE) for name in EXPRESSIONS}
    names = list(svgs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            check(svgs[names[i]] != svgs[names[j]], f"expressions '{names[i]}' and '{names[j]}' render the same")
    check(render_svg(HERO, expression("happy"), SIZE, SIZE) == svgs["happy"], "expression output is not deterministic")

    # 2. skin colour on a cheek point is the same in every expression (expressions must not change identity)
    cheek_rel = (0.6, 0.1)  # head units: 0.6 across, 0.1 down (right cheek, clear of eyes and mouth)
    cheek_colours = {}
    for name in EXPRESSIONS:
        png = tmp / f"{name}.png"
        rasterize(svgs[name], str(png))
        J = skeleton(HERO, expression(name))
        r = HERO.proportions.head_r
        hc, up, across = J["head_c"], J["up"], J["across"]
        down = (-up[0], -up[1])
        ax, dy = cheek_rel  # head units along across and along down
        p = (hc[0] + (across[0] * ax + down[0] * dy) * r, hc[1] + (across[1] * ax + down[1] * dy) * r)
        cheek_colours[name] = px_at(png, p)
    base = cheek_colours["neutral"]
    for name, col in cheek_colours.items():
        check(near(col, base), f"cheek colour changes in expression '{name}': {col} vs {base}")

    # 3. hands and feet are actually drawn with the right colour at their centres
    pose = Pose(r_shoulder=150, r_elbow=-30)
    J = skeleton(HERO, pose)
    png = tmp / "body.png"
    rasterize(render_svg(HERO, pose, SIZE, SIZE), str(png))
    P = HERO.proportions
    fd = J["r_fdir"]
    hand_c = (J["r_wr"][0] + fd[0] * P.hand_len * 0.5, J["r_wr"][1] + fd[1] * P.hand_len * 0.5)
    hand_px = px_at(png, hand_c)
    check(near(hand_px, (0xe2, 0xb3, 0x91), 60), f"right hand centre is not skin-coloured: {hand_px}")
    foot_c = (J["l_an"][0] + P.foot_len * 0.25, J["l_an"][1])
    foot_px = px_at(png, foot_c)
    check(near(foot_px, (0x10, 0x11, 0x16), 60), f"left foot centre is not shoe-coloured: {foot_px}")

    # 4. identity is unchanged by pose and expression
    h = HERO.identity_hash()
    _ = [expression(n) for n in EXPRESSIONS]
    check(HERO.identity_hash() == h, "expression changed the identity hash")

    # 5. expression fields are animatable: a motion timeline blends them without error
    tl = Timeline([Keyframe(0.0, expression("neutral")), Keyframe(1.0, expression("happy")),
                   Keyframe(2.0, expression("sad"))])
    frames = follow_through(tl, fps=12)
    check(any(abs(f.smile) > 0.5 for f in frames), "motion did not drive the smile field")

    # 6. invalid expression name is rejected
    try:
        expression("furious")
        check(False, "unknown expression was accepted")
    except ValueError:
        pass

print("body and expression tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
sys.exit(1 if failures else 0)
