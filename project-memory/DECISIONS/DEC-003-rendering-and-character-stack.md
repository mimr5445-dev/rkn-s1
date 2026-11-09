# DEC-003: rendering method and first stack

- **Date:** 2026-11-09
- **Decided by:** project owner (rendering by code; richer professional characters; start with the character system). Technical choices delegated to the architect.

## Decisions
1. **Rendering by code.** Every frame is produced by code, not by generative models. This keeps identity exact and results reproducible.
2. **Language: Python 3.12.** Geometry, SVG generation and tests are written in Python.
3. **Vector output:** characters are built as SVG paths, then rasterized with cairosvg. Reason: output is deterministic, testable by pixel, and needs no browser. The v1 browser pipeline is not reused for v2.
4. **Identity separated from pose** (see docs/design/character-system.md).

## Why not the other options
- Canvas in a headless browser (v1): heavier to run, and harder to test deterministically.
- Pillow drawing only: fewer options for gradients and smooth outlines than SVG.

## Reversibility
Rendering is behind a single function (`render_svg`). The rasterizer can be swapped without changing the character model.
