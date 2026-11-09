#!/usr/bin/env python3
"""Render a short wave clip with keyframes and spring follow-through, then a contact sheet of frames.

Run from v2/:  python examples/render_wave_clip.py  -> examples/out/clip/ and wave_clip_sheet.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, Pose, render_svg, rasterize  # noqa: E402
from studio.motion import Keyframe, Timeline, follow_through  # noqa: E402

hero = CharacterSpec("hero", "Sami")
idle = Pose()
wave_up = Pose(r_shoulder=150, r_elbow=-30)
wave_hi = Pose(r_shoulder=160, r_elbow=-60)
timeline = Timeline([
    Keyframe(0.0, idle),
    Keyframe(0.6, wave_up),
    Keyframe(1.2, wave_hi),
    Keyframe(1.8, wave_up),
    Keyframe(2.4, idle),
])
frames = follow_through(timeline, fps=12)

out = HERE / "out" / "clip"
out.mkdir(parents=True, exist_ok=True)
for i, pose in enumerate(frames):
    rasterize(render_svg(hero, pose, 320, 320, bg_top="#f2e4c9", bg_bottom="#c98f5a"),
              str(out / f"frame_{i:03d}.png"))

pick = list(range(0, len(frames), max(1, len(frames) // 8)))[:8]
sheet = Image.new("RGB", (320 * len(pick), 320))
for k, i in enumerate(pick):
    sheet.paste(Image.open(out / f"frame_{i:03d}.png").convert("RGB"), (320 * k, 0))
sheet.save(HERE / "out" / "wave_clip_sheet.png")
print(f"wrote {len(frames)} frames; sheet uses frames {pick}")
