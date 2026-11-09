# Design: skill loader (v2, M3a)

## Goal
New characters and locations are added as self-contained skill folders. The core (`v2/studio/`) is not edited to add them.

## Skill layout
    v2/library/<skill-name>/
        skill.json     manifest
        <data>.json    the content (character or location)

## Manifest (`skill.json`)
| field | rule |
|---|---|
| `name` | slug: lowercase letters, digits, hyphens; must equal the folder name |
| `version` | semantic version `x.y.z` |
| `kind` | `character` or `location` |
| `provides` | non-empty list of `kind:id`; must include the id declared in the data file |
| `data` | relative path to the data file, which must exist |
| `studio` | required studio major version, for example `"2"` |

## Data files
- **character**: keys `id`, `name`, `proportions`, `palette`. Proportions and palette keys must match the dataclass fields exactly. Colours are `#rrggbb`. Unknown keys are rejected.
- **location**: keys `id`, `name`, `top`, `bottom` (background gradient colours, `#rrggbb`).

## Rules
1. A broken skill is rejected with an error that names the skill and the reason. Other skills still load.
2. Duplicate ids across skills are rejected, and both skills are reported.
3. Load order is sorted by folder name, so results are deterministic.
4. A skill can only provide what it declares. Looking up an undeclared id fails.
5. Loading never changes core code or other skills.

## Tests (must pass)
- The two sample skills load and resolve.
- A skill copied in from outside the library loads with no core change (extensibility).
- Each broken case is rejected with a message that names the skill (missing field, bad version, bad kind, provides mismatch, unknown key, bad colour, missing data file, duplicate id).
- One broken skill does not stop the others from loading.
- Same character from a skill renders with the same identity as one built in code.
- Same character in two locations keeps the same face colour; the backgrounds differ.

## Out of scope
- Sounds, icons, effects and styles (later milestones, same mechanism).
- Remote skill installation and signing.
