# DEC-006: rename to RKN-S1 and v1 status

- **Date:** 2026-11-09
- **Decided by:** project owner.

## Decisions
1. **v1 is a free starting point.** It is not licensed by a third party and does not carry any licence rights to be preserved. The owner holds the licence for everything in this repository under DEC-005.
2. **All current files use the new name RKN-S1.** The old name is removed from current files. The git history is not rewritten, and past decision and incident records keep their original wording.
3. **Stale instructions are fixed.** References to the removed `verify_kit.py` are deleted from install and skill instructions.

## Scope of the rename
- Product name: RKN-S1 Studio. Folder name for installed kits: `rkn-s1-studio/`.
- Package name in `kit/package.json` and `package-lock.json`: `rkn-s1-studio`. Dependency licences are unchanged.
