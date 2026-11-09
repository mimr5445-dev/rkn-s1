# DEC-004: archive v1 and remove verify_kit.py

- **Date:** 2026-11-09
- **Decided by:** project owner ("agreed to the decisions").

## Decisions
1. **v1 is archived.** `skills/make-2d-video/` is read-only history. A notice is in `ARCHIVED.md`. Nothing is deleted, and the git history is kept.
2. **`tools/verify_kit.py` is removed.** It compared files against hashes of a reference version that is not in the repository (INC-005). With DEC-001 there is no such reference, so the check was misleading.
3. **v1 regression tests stay** (`tests/test_audio.py`, `tests/check_js_imports.py`).

## Not decided
- **License (INC-008):** the owner must choose it. It blocks public release. Options for the owner to choose from: MIT, Apache-2.0, a proprietary "all rights reserved" notice, or another license.
