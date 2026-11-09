# DEC-001: Original kit files are not a binding reference

- **Date:** 2026-11-09
- **Decided by:** project owner
- **Decision:** the original kit files and their recorded hashes are no longer the reference. The team will build something new and will not try to restore or match the original versions.
- **Consequences:**
  - INC-004 (truncated restore payloads) and INC-005 (hash mismatches) are closed as superseded. They are not bugs to fix.
  - Original files stay in git history. They are not deleted.
  - `tools/verify_kit.py` hashes are obsolete and should be removed or replaced when the new build defines its own reference.
  - INC-001 to INC-003 (audio fixes) stay as history. The reconstructed audio functions may be replaced by the new build.
- **Open:** the scope of the new build is not yet defined. It needs a separate decision record (DEC-002).
