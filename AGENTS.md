# Instructions for any model working in this repository

1. Read `PROJECT_CONTEXT.md`, then `project-memory/CURRENT_STATE.md`, then `project-memory/INCIDENTS/INCIDENT_INDEX.md`.
2. Do not work on `main`. Use a branch and open a merge request. Do not merge to `main` without explicit owner approval.
3. Every claim of success needs evidence: a test you ran, its output, and the commit.
4. Every problem you find gets an incident entry with its root cause, or with the explicit note "root cause unknown".
5. Do not overwrite files in `_restore/` or delete history. Use `scripts/restore_missing.py` only in validation mode first.
6. Run `python tests/test_audio.py` and `python tests/check_js_imports.py` before committing changes under `kit/`.
