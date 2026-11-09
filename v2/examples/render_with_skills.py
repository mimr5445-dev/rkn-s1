#!/usr/bin/env python3
"""Compose skills: one character from its skill, two locations from their skills, one contact sheet.

Run from v2/:  python examples/render_with_skills.py -> examples/out/skills_sheet.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from PIL import Image  # noqa: E402
from studio.character import Pose, expression, render_svg, rasterize  # noqa: E402
from studio.registry import Location, discover  # noqa: E402

reg = discover(HERE.parent / "library")
if reg.errors:
    raise SystemExit("library has errors: " + "; ".join(reg.errors))
hero = reg.get("character:sami")
locations = [reg.get("location:dusk-street"), Location(id="day", name="Day", top="#f2e4c9", bottom="#c98f5a")]
poses = [Pose(), expression("happy", Pose(r_shoulder=150, r_elbow=-30))]

out = HERE / "out"
out.mkdir(exist_ok=True)
tiles = []
for loc in locations:
    for pose in poses:
        png = out / f"skills_{loc.id}_{'happy' if pose.smile else 'idle'}.png"
        rasterize(render_svg(hero, pose, 320, 320, bg_top=loc.top, bg_bottom=loc.bottom), str(png))
        tiles.append(Image.open(png).convert("RGB"))
sheet = Image.new("RGB", (320 * len(tiles), 320))
for i, t in enumerate(tiles):
    sheet.paste(t, (320 * i, 0))
sheet.save(out / "skills_sheet.png")
print(f"loaded {len(reg.skills)} skills; wrote {len(tiles)} tiles")
