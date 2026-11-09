#!/usr/bin/env python3
"""Render one walk cycle and a contact sheet of frames.

Run from v2/:  python examples/render_walk_clip.py -> examples/out/walk_sheet.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, render_svg, rasterize  # noqa: E402
from studio.gait import walk_poses  # noqa: E402

hero = CharacterSpec("hero", "Sami")
FPS, FRAMES = 12, 12  # one cycle at 12 fps
poses = walk_poses(hero, FRAMES, FPS, cycle_s=1.0)
out = HERE / "out" / "walk"
out.mkdir(parents=True, exist_ok=True)
tiles = []
for i, pose in enumerate(poses):
    png = out / f"walk_{i:02d}.png"
    rasterize(render_svg(hero, pose, 320, 320, bg_top="#f2e4c9", bg_bottom="#c98f5a"), str(png))
    tiles.append(Image.open(png).convert("RGB"))
sheet = Image.new("RGB", (320 * len(tiles), 320))
for i, t in enumerate(tiles):
    sheet.paste(t, (320 * i, 0))
sheet.save(HERE / "out" / "walk_sheet.png")
print(f"wrote {len(tiles)} walk frames")
