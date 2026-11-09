#!/usr/bin/env python3
"""Tests for the skill loader. Run from v2/:  python tests/test_registry.py"""
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image  # noqa: E402
from studio.character import CharacterSpec, Palette, Pose, Proportions, render_svg, rasterize, skeleton  # noqa: E402
from studio.registry import SkillError, discover, load_skill  # noqa: E402

LIB = ROOT / "library"
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL:", msg)


def safe_discover(path: Path):
    """discover() must never raise; if it does, report a failure instead of crashing the test run."""
    try:
        return discover(path)
    except Exception as e:  # noqa: BLE001
        check(False, f"discover() raised {type(e).__name__}: {e}")
        from studio.registry import Registry
        return Registry()


def write_skill(lib: Path, name: str, manifest: dict, data: dict) -> None:
    d = lib / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "skill.json").write_text(json.dumps(manifest))
    (d / manifest.get("data", "data.json")).write_text(json.dumps(data))


GOOD_CHAR = {"id": "tester", "name": "Tester", "proportions": {}, "palette": {}}
GOOD_MANIFEST = {"name": "character-tester", "version": "1.0.0", "kind": "character",
                 "provides": ["character:tester"], "data": "character.json", "studio": "2"}

# 1. the sample skills load and resolve
reg = safe_discover(LIB)
check(not reg.errors, f"sample library has errors: {reg.errors}")
sami = reg.get("character:sami")
dusk = reg.get("location:dusk-street")
check(isinstance(sami, CharacterSpec), "character:sami did not resolve to a CharacterSpec")
check(dusk.top == "#1d2033" and dusk.bottom == "#07080d", "location:dusk-street has the wrong colours")

# 2. a skill loaded from data equals the same character built in code (identity is preserved)
check(sami.proportions == Proportions() and sami.palette == Palette(),
      "loaded character differs from the built-in defaults")
check(sami.identity_hash() == CharacterSpec("sami", "Sami").identity_hash(),
      "loaded identity hash differs from the code-built spec")

# 3. undeclared or unknown ids fail
try:
    reg.get("character:nobody")
    check(False, "unknown id was resolved")
except SkillError:
    pass

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # 4. extensibility: a skill added from outside the core loads with no core change
    outside = tmp / "external"
    write_skill(outside, "character-tester", GOOD_MANIFEST, GOOD_CHAR)
    ext = safe_discover(outside)
    check(not ext.errors and isinstance(ext.get("character:tester"), CharacterSpec),
          f"external skill did not load: {ext.errors}")

    # 5. each broken case is rejected, names the skill, and the good skill still loads
    cases = {
        "missing field": (dict(GOOD_MANIFEST, **{}), None),
        "bad version": (dict(GOOD_MANIFEST, version="1.0"), None),
        "bad kind": (dict(GOOD_MANIFEST, kind="weather"), None),
        "provides mismatch": (dict(GOOD_MANIFEST, provides=["character:other"]), None),
        "wrong studio major": (dict(GOOD_MANIFEST, studio="1"), None),
        "name not folder": (dict(GOOD_MANIFEST, name="someone-else"), None),
        "unknown character key": (GOOD_MANIFEST, dict(GOOD_CHAR, speed=3)),
        "unknown palette key": (GOOD_MANIFEST, dict(GOOD_CHAR, palette={"sparkle": "#ffffff"})),
        "bad colour": (GOOD_MANIFEST, dict(GOOD_CHAR, palette={"skin": "red"})),
        "negative proportion": (GOOD_MANIFEST, dict(GOOD_CHAR, proportions={"head_r": -1})),
    }
    for label, (manifest, data) in cases.items():
        lib = tmp / ("broken-" + label.replace(" ", "-"))
        if label == "missing field":
            bad = {k: v for k, v in GOOD_MANIFEST.items() if k != "studio"}
            write_skill(lib, "character-tester", bad, GOOD_CHAR)
        else:
            write_skill(lib, "character-tester", manifest, data if data is not None else GOOD_CHAR)
        write_skill(lib, "location-good", {"name": "location-good", "version": "1.0.0", "kind": "location",
                                           "provides": ["location:good"], "data": "location.json", "studio": "2"},
                    {"id": "good", "name": "Good", "top": "#000000", "bottom": "#ffffff"})
        r = safe_discover(lib)
        named = any("character-tester" in e or "tester" in e for e in r.errors)
        check(named, f"{label}: error does not name the skill: {r.errors}")
        check("location:good" in r.by_id, f"{label}: a broken skill stopped the good one from loading")
        check("character:tester" not in r.by_id, f"{label}: a broken skill was accepted")

    # 6. duplicate ids across two skills are rejected, and the first one is kept
    dup = tmp / "dup"
    write_skill(dup, "character-a", dict(GOOD_MANIFEST, name="character-a"), GOOD_CHAR)
    write_skill(dup, "character-b", dict(GOOD_MANIFEST, name="character-b"), GOOD_CHAR)
    r = safe_discover(dup)
    check(any("already provided" in e for e in r.errors), f"duplicate id not reported: {r.errors}")
    check(len([s for s in r.skills.values()]) == 1, "duplicate id loaded twice")

    # 7. loading order is deterministic
    check(list(discover(LIB).skills) == list(discover(LIB).skills), "load order changed between runs")

# 8. same character, two locations: face colour is unchanged, backgrounds differ
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    loc2 = reg.get("location:dusk-street")
    from studio.registry import Location
    day = Location(id="day", name="Day", top="#f2e4c9", bottom="#c98f5a")
    cols = {}
    for loc in (loc2, day):
        png = tmp / f"{loc.id}.png"
        rasterize(render_svg(sami, Pose(), 640, 640, bg_top=loc.top, bg_bottom=loc.bottom), str(png))
        J = skeleton(sami, Pose())
        hc, up, across = J["head_c"], J["up"], J["across"]
        r0 = sami.proportions.head_r
        down = (-up[0], -up[1])
        p = (hc[0] + (across[0] * 0.6 + down[0] * 0.1) * r0, hc[1] + (across[1] * 0.6 + down[1] * 0.1) * r0)
        cols[loc.id] = Image.open(png).convert("RGB").getpixel((int(p[0] * 640), int(p[1] * 640)))
    check(sum(abs(a - b) for a, b in zip(cols["dusk-street"], cols["day"])) <= 24,
          f"face colour changed with the location: {cols}")
    bg_a = Image.open(tmp / "dusk-street.png").convert("RGB").getpixel((5, 5))
    bg_b = Image.open(tmp / "day.png").convert("RGB").getpixel((5, 5))
    check(sum(abs(a - b) for a, b in zip(bg_a, bg_b)) > 100, "the two locations look the same")

print("registry tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
sys.exit(1 if failures else 0)
