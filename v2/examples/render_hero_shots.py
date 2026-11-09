#!/usr/bin/env python3
"""Render one character in three shots with different poses and backgrounds, then a contact sheet.

Run from v2/:  python examples/render_hero_shots.py   -> writes examples/out/
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, Pose, render_svg, rasterize  # noqa: E402

hero = CharacterSpec("hero", "Sami")
shots = [
    ("shot_idle_dusk", Pose(), ("#1d2033", "#07080d")),
    ("shot_wave_day", Pose(r_shoulder=150, r_elbow=-30), ("#f2e4c9", "#c98f5a")),
    ("shot_point_night", Pose(lean=14, x=0.45, r_shoulder=80, r_elbow=5, l_hip=-14, r_hip=18, r_knee=-12),
     ("#0b1a2e", "#2b0f3a")),
]
out = HERE / "out"
out.mkdir(exist_ok=True)
tiles = []
for name, pose, (top, bottom) in shots:
    png = out / f"{name}.png"
    rasterize(render_svg(hero, pose, 480, 480, bg_top=top, bg_bottom=bottom), str(png))
    tiles.append(Image.open(png).convert("RGB"))
sheet = Image.new("RGB", (480 * len(tiles), 480))
for i, t in enumerate(tiles):
    sheet.paste(t, (480 * i, 0))
sheet.save(out / "hero_contact_sheet.png")
print("wrote", [s[0] for s in shots], "and hero_contact_sheet.png to", out)
