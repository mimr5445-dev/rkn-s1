# Templates

## Design doc (`docs/design/<system>.md`)
    # Design: <name> (v2, <milestone>)
    ## Goal
    ## Decisions (numbered; identity vs state; units; conventions)
    ## Rules (must always hold)
    ## Tests (must pass)
    ## Out of scope

## Test file (`v2/tests/test_<name>.py`)
    #!/usr/bin/env python3
    """Tests for <name>. Run from v2/:  python tests/test_<name>.py"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    failures = []
    def check(cond, msg):
        if not cond:
            failures.append(msg); print("FAIL:", msg)

    # one claim per check; numeric where possible; guard max()/min() on empty data

    print("<name> tests:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
    sys.exit(1 if failures else 0)

## Incident entry (add a row to the index, then a details line)
    | INC-0NN | <date> | <short title> | fixed / open / superseded |
    - **INC-0NN (<short title>):** <symptom>. Evidence: <test name, number or image>.
      Root cause: <cause, or "unknown">. Fix: <what changed>. Guard: <test that prevents a repeat>.

## Achievement row (`project-memory/ACHIEVEMENTS.md`)
    | <date> | <milestone> | <what was delivered> | <commit / merge> | <test name or image> |

## Lesson (`project-memory/LESSONS.md`)
    ## L-0NN: <rule in one line>
    - **What happened:** <event, linked to an incident>
    - **Rule:** <what to do next time>
