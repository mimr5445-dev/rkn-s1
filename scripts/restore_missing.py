#!/usr/bin/env python3
"""Validate, and optionally restore, kit files from base64 parts in _restore/.

Safe by default:
  python scripts/restore_missing.py          # validate only, writes nothing
  python scripts/restore_missing.py --apply  # extract, and only into paths that do not exist yet

It refuses to extract a payload that does not decode and fully parse as a gzip tar,
and it never overwrites an existing file. Path traversal is blocked with the 'data' filter.
"""
import argparse, base64, io, sys, tarfile, tempfile, shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parts_dir = root / "_restore"
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true", help="extract files that do not already exist")
args = ap.parse_args()

parts = sorted(parts_dir.glob("missing_*.b64"))
if not parts:
    print("No missing_*.b64 parts found in _restore/")
    sys.exit(1)

data = "".join(p.read_text().strip() for p in parts)
try:
    raw = base64.b64decode(data, validate=True)
except Exception as e:
    print(f"FAILED: payload is not valid base64 ({e}).")
    sys.exit(1)

try:
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        members = [m for m in tf.getmembers() if m.isfile()]
        for m in members:  # full read forces the gzip stream to be checked to its end
            tf.extractfile(m).read()
except (EOFError, tarfile.TarError, OSError) as e:
    print(f"FAILED: archive is truncated or corrupt ({type(e).__name__}: {e}).")
    print("Nothing was written. See project-memory/INCIDENTS/INCIDENT_INDEX.md (INC-004).")
    sys.exit(1)

print(f"archive OK: {len(members)} files, {len(raw)} bytes")
for m in members:
    dest = root / m.name
    state = "exists (kept)" if dest.exists() else ("would restore" if not args.apply else "restoring")
    print(f"  {state}: {m.name}")

if args.apply:
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
            tf.extractall(tmp, filter="data")
        for m in members:
            dest = root / m.name
            if dest.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(tmp) / m.name, dest)
    print("done: only missing files were written")
