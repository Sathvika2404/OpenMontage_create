# The Rainbow Tales — Milo's Little Adventures, Ep. 1

**Milo and the Shop That Sold Happiness** · target 9:30 · 1920x1080 · 16:9 · 30 fps · $0 budget

Status: **puppet test only** (15 s). The full episode has not been started.

Pipeline: `character-animation` (beta), proposal → *sample* sub-stage.
Pipeline workspace (gitignored, regenerable): `projects/rainbow-tales-ep01/`.

## Layout

| Path | What | In Git |
|---|---|---|
| `reference/milo_character_sheet_official.webp` | Official Milo character sheet — visual source of truth | yes |
| `characters/milo/layers/*.png` | 2.5D front-view puppet layers (2x, shared canvas, RGBA) | yes |
| `characters/milo/rig/milo_front_rig.json` | Pivots, draw order, parenting, eye geometry, limits | yes |
| `timelines/milo_puppet_test_15s.json` | Explicit hand-authored action timeline | yes |
| `scripts/extract_milo_layers.py` | Rebuilds layers + rig from the sheet (OpenCV, local) | yes |
| `scripts/render_puppet_test.py` | Renders via `video_compose` atelier mode (Remotion) | yes |
| `remotion/rainbow-tales-ep01/` | Remotion source: `MiloPuppet`, timeline evaluator, test scene | yes |
| `projects/rainbow-tales-ep01/renders/` | Rendered MP4s + QC stills | **no** |

## Reproduce

```bash
make cloud-setup && source .env.local-runtime          # once per container
pip install opencv-python-headless                      # free, local
EP=productions/the-rainbow-tales/ep01-milo-and-the-shop-that-sold-happiness
python3 $EP/scripts/extract_milo_layers.py              # layers + rig
python3 $EP/scripts/render_puppet_test.py               # -> projects/rainbow-tales-ep01/renders/milo_puppet_test_15s.mp4
python3 $EP/scripts/render_puppet_test.py --scale 0.5 --output /tmp/draft.mp4   # fast draft
```

## Puppet

Draw order (back → front): `tail`, `body` (incl. chest patch), `head`, `mouth`,
eye states, `bandana`, `ear_left`, `ear_right`. `head` parents mouth, eyes and
ears; `body` breathing lifts head and bandana at their pivot heights.

| Layer | Pivot | Motion |
|---|---|---|
| body + chest patch | paws on floor | breathing (≈1.1 % vertical stretch) |
| head | neck under chin | tilt (±8° limit), small offsets |
| ear_left / ear_right | ear roots | spring follow-through on head tilt (±7°) |
| tail | behind back paw | idle sway, wag (±14°) |
| bandana | knot line | slight lag on head / wag (±1.5°) |
| mouth (lower jaw + tongue) | upper lip line | subtle open/close |
| eyes | — | blink / half-blink / wink via the sheet's official **Half Blink** and **Blink (Closed)** tiles, scaled and colour-matched per eye |

### What is synthesized (approved for this test only)

- `head`: 16 px cheek strip mirrored under each ear's inner edge (hidden at rest).
- `body`: 24 px jaw-fur band above the head cut line (hidden at rest).
- Eye-state tiles are mirrored for Milo's left eye (viewer's right).

### Needs new artwork for production quality

1. Higher-resolution source (front view is only ~250x365 px on the sheet).
2. Layered front-view parts: head without ears, ears with roots, body with neck.
3. A fully visible tail in the front view (only a small tuft shows).
4. Brows / expression overlays at front-view scale (sad, determined, surprised).
5. Mouth shapes at front-view scale and angle for lip sync.
6. Separated legs for walk/run; side, 3/4 and back views as parts.

See `QUALITY_REPORT.md` for the test render's QC results.
