"""Skill loader: discovers skill folders, validates manifests and data, and resolves ids.

A skill is a folder with skill.json and a data file. Broken skills are rejected with a message that names them,
and the other skills still load. Loading never changes core code.
"""
from __future__ import annotations

import dataclasses
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .character import CharacterSpec, Palette, Proportions

STUDIO_MAJOR = "2"
KINDS = ("character", "location")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class SkillError(Exception):
    """A skill could not be loaded. The message names the skill and the reason."""


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    top: str
    bottom: str


@dataclass(frozen=True)
class Skill:
    name: str
    version: str
    kind: str
    provides: Tuple[str, ...]
    path: Path
    obj: object  # CharacterSpec or Location


@dataclass
class Registry:
    skills: Dict[str, Skill] = field(default_factory=dict)  # name -> Skill
    by_id: Dict[str, Skill] = field(default_factory=dict)   # "kind:id" -> Skill
    errors: List[str] = field(default_factory=list)

    def get(self, ref: str):
        """Resolve 'kind:id' to its object. Undeclared or unknown ids fail."""
        if ref not in self.by_id:
            raise SkillError(f"no skill provides '{ref}'")
        return self.by_id[ref].obj


def _hex_ok(name: str, value, skill: str) -> None:
    if not isinstance(value, str) or not HEX_RE.match(value):
        raise SkillError(f"{skill}: colour '{name}' must be #rrggbb, got {value!r}")


def _build_character(data: dict, skill: str) -> CharacterSpec:
    allowed = {"id", "name", "proportions", "palette"}
    unknown = set(data) - allowed
    if unknown:
        raise SkillError(f"{skill}: unknown character keys {sorted(unknown)}")
    for key in ("id", "name", "proportions", "palette"):
        if key not in data:
            raise SkillError(f"{skill}: character data is missing '{key}'")
    if not NAME_RE.match(str(data["id"])):
        raise SkillError(f"{skill}: character id '{data['id']}' must be a slug")

    p_fields = {f.name for f in dataclasses.fields(Proportions)}
    bad_p = set(data["proportions"]) - p_fields
    if bad_p:
        raise SkillError(f"{skill}: unknown proportion keys {sorted(bad_p)}")
    c_fields = {f.name for f in dataclasses.fields(Palette)}
    bad_c = set(data["palette"]) - c_fields
    if bad_c:
        raise SkillError(f"{skill}: unknown palette keys {sorted(bad_c)}")
    for k, v in data["palette"].items():
        _hex_ok(k, v, skill)
    for k, v in data["proportions"].items():
        if not isinstance(v, (int, float)) or v <= 0:
            raise SkillError(f"{skill}: proportion '{k}' must be a positive number")

    return CharacterSpec(
        id=data["id"],
        name=data["name"],
        proportions=Proportions(**data["proportions"]),
        palette=Palette(**data["palette"]),
    )


def _build_location(data: dict, skill: str) -> Location:
    for key in ("id", "name", "top", "bottom"):
        if key not in data:
            raise SkillError(f"{skill}: location data is missing '{key}'")
    unknown = set(data) - {"id", "name", "top", "bottom"}
    if unknown:
        raise SkillError(f"{skill}: unknown location keys {sorted(unknown)}")
    if not NAME_RE.match(str(data["id"])):
        raise SkillError(f"{skill}: location id '{data['id']}' must be a slug")
    _hex_ok("top", data["top"], skill)
    _hex_ok("bottom", data["bottom"], skill)
    return Location(id=data["id"], name=data["name"], top=data["top"], bottom=data["bottom"])


def load_skill(folder: Path) -> Skill:
    """Load and validate one skill folder. Raises SkillError with the skill name in the message."""
    manifest_path = folder / "skill.json"
    label = folder.name
    if not manifest_path.exists():
        raise SkillError(f"{label}: missing skill.json")
    try:
        m = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        raise SkillError(f"{label}: skill.json is not valid JSON ({e})")

    for key in ("name", "version", "kind", "provides", "data", "studio"):
        if key not in m:
            raise SkillError(f"{label}: manifest is missing '{key}'")
    name = m["name"]
    if name != folder.name:
        raise SkillError(f"{label}: manifest name '{name}' must equal the folder name")
    if not NAME_RE.match(str(name)):
        raise SkillError(f"{label}: name '{name}' must be a slug")
    if not VERSION_RE.match(str(m["version"])):
        raise SkillError(f"{name}: version '{m['version']}' must be x.y.z")
    if m["kind"] not in KINDS:
        raise SkillError(f"{name}: kind '{m['kind']}' must be one of {KINDS}")
    if m["studio"] != STUDIO_MAJOR:
        raise SkillError(f"{name}: needs studio major version {m['studio']}, this is {STUDIO_MAJOR}")
    provides = m["provides"]
    if not isinstance(provides, list) or not provides:
        raise SkillError(f"{name}: 'provides' must be a non-empty list")

    data_path = folder / str(m["data"])
    if not data_path.exists():
        raise SkillError(f"{name}: data file '{m['data']}' not found")
    try:
        data = json.loads(data_path.read_text())
    except json.JSONDecodeError as e:
        raise SkillError(f"{name}: data file is not valid JSON ({e})")

    if m["kind"] == "character":
        obj = _build_character(data, name)
    else:
        obj = _build_location(data, name)
    expected = f"{m['kind']}:{data['id']}"
    if expected not in provides:
        raise SkillError(f"{name}: provides must include '{expected}' (the id in its data file)")
    for ref in provides:
        if not isinstance(ref, str) or ref.count(":") != 1 or not ref.startswith(m["kind"] + ":"):
            raise SkillError(f"{name}: provides entry '{ref}' must be '{m['kind']}:<id>'")
    return Skill(name=name, version=m["version"], kind=m["kind"], provides=tuple(provides),
                 path=folder, obj=obj)


def discover(library: Path) -> Registry:
    """Load every skill folder under `library`, in sorted order. Broken skills are reported, not fatal."""
    reg = Registry()
    if not library.exists():
        reg.errors.append(f"library folder not found: {library}")
        return reg
    for folder in sorted(p for p in library.iterdir() if p.is_dir()):
        try:
            skill = load_skill(folder)
        except SkillError as e:
            reg.errors.append(str(e))
            continue
        if skill.name in reg.skills:
            reg.errors.append(f"{skill.name}: duplicate skill name")
            continue
        clash = [r for r in skill.provides if r in reg.by_id]
        if clash:
            reg.errors.append(f"{skill.name}: id(s) already provided by another skill: {clash}")
            continue
        reg.skills[skill.name] = skill
        for ref in skill.provides:
            reg.by_id[ref] = skill
    return reg
