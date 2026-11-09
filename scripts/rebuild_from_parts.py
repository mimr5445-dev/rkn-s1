#!/usr/bin/env python3
"""Rebuild full source files from _parts/ if present.
Run from repo root: python scripts/rebuild_from_parts.py
"""
from pathlib import Path
import json, sys

root = Path(__file__).resolve().parents[1]
manifest = root / '_parts' / 'manifest.json'
if not manifest.exists():
    print('No _parts/manifest.json — nothing to rebuild.')
    sys.exit(0)

data = json.loads(manifest.read_text())
for entry in data:
    path = entry['path']
    parts = []
    for i in range(entry['parts']):
        p = root / '_parts' / f'{path}.{i:02d}.part'
        if not p.exists():
            print(f'MISSING {p}')
            sys.exit(1)
        parts.append(p.read_text())
    out = root / path
    out.parent.mkdir(parents=True, exist_ok=True)
    content = ''.join(parts)
    out.write_text(content)
    print(f'wrote {path} ({len(content)} bytes)')
print('done')
