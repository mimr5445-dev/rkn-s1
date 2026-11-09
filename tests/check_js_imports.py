#!/usr/bin/env python3
"""Verify every named import between the kit's JS modules is exported by its source. Run from repo root."""
import re, os, sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1] / "skills" / "make-2d-video" / "kit"
files = [p for p in KIT.rglob("*.js") if "node_modules" not in p.parts]

exports = {}
for f in files:
    s = f.read_text()
    names = set(re.findall(r"export\s+(?:const|let|var|function\*?|class)\s+([A-Za-z_$][\w$]*)", s))
    for block in re.findall(r"export\s*\{([^}]*)\}", s):
        for part in block.split(","):
            if part.strip():
                names.add(part.strip().split(" as ")[-1].strip())
    if re.search(r"export\s+default", s):
        names.add("default")
    exports[os.path.normpath(str(f))] = names

problems = []
for f in files:
    for names, rel in re.findall(r"import\s*\{([^}]*)\}\s*from\s*['\"](\.[^'\"]+)['\"]", f.read_text()):
        target = os.path.normpath(os.path.join(os.path.dirname(str(f)), rel))
        key = target if target in exports else target + ".js"
        if key not in exports:
            problems.append(f"{f.relative_to(KIT)}: cannot resolve '{rel}'")
            continue
        for part in names.split(","):
            name = part.strip().split(" as ")[0].strip()
            if name and name not in exports[key]:
                problems.append(f"{f.relative_to(KIT)}: imports '{name}' from '{rel}' but it is not exported")

print(f"JS modules scanned: {len(files)}")
for p in problems:
    print("FAIL:", p)
print("js import check:", "PASS" if not problems else f"{len(problems)} FAILURE(S)")
sys.exit(1 if problems else 0)
