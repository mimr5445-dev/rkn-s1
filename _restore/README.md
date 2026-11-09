# _restore — status: NOT usable as a restore source

The two payloads in this folder are truncated. Each `.b64` file is exactly 2500 characters,
and the decoded archive ends before the gzip end-of-stream marker, so extraction fails with
`EOFError`. Running the old restore script would fail and write nothing.

Kept on purpose: the files are history and are not deleted. The source of truth for the kit is
`skills/make-2d-video/kit/` on `main`.

Check the state:

    python scripts/restore_missing.py          # validation only, writes nothing

Tracked as INC-004 in `project-memory/INCIDENTS/INCIDENT_INDEX.md`. To restore these files,
re-upload complete payloads (the full base64 must be intact) and re-run the validation.
