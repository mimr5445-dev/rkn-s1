#!/usr/bin/env python3
"""Render the same character in each expression preset, with hands and feet visible.

Run from v2/:  python examples/render_expression_sheet.py -> examples/out/expression_sheet.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, EXPRESSIONS, Pose, expression, render_svg, rasterize  # noqa: E402

hero = CharacterSpec("hero", "Sami")
base = Pose(r_shoulder=150, r_elbow=-30)  # one hand raised, so the hand is visible
out = HERE / "out"
out.mkdir(exist_ok=True)
tiles = []
for name in EXPRESSIONS:
    png = out / f"expr_{name}.png"
    rasterize(render_svg(hero, expression(name, base), 320, 320, bg_top="#f2e4c9", bg_bottom="#c98f5a"), str(png))
    tiles.append(Image.open(png).convert("RGB"))
sheet = Image.new("RGB", (320 * len(tiles), 320))
for i, t in enumerate(tiles):
    sheet.paste(t, (320 * i, 0))
sheet.save(out / "expression_sheet.png")
print("wrote", list(EXPRESSIONS), "to", out)
