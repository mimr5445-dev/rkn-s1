#!/usr/bin/env python3
"""Rebuild missing kit files from base64 parts. Run from repo root:
  python scripts/restore_missing.py
"""
from pathlib import Path
import base64, tarfile, io

root = Path(__file__).resolve().parents[1]
parts_dir = root / "_restore"
parts = sorted(parts_dir.glob("missing_*.b64"))
if not parts:
    print("No parts found in _restore/")
    raise SystemExit(1)
data = "".join(p.read_text().strip() for p in parts)
raw = base64.b64decode(data)
print(f"decoded {len(raw)} bytes from {len(parts)} parts")
with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
    tf.extractall(root)
    for m in tf.getmembers():
        if m.isfile():
            print("extracted", m.name)
print("done — missing kit files restored")
