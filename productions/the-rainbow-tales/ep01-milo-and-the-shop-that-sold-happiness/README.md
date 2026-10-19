# The Rainbow Tales — Milo's Little Adventures, Ep. 1

**Milo and the Shop That Sold Happiness** · target 9:30 · 1920x1080 · 16:9 · 30 fps · $0 budget

Status: **tests only**: puppet test and character acting test (15 s each).
The full episode has not been started.

Pipeline: `character-animation` (beta), proposal → *sample* sub-stage.
Pipeline workspace (gitignored, regenerable): `projects/rainbow-tales-ep01/`.

## Layout

| Path | What | In Git |
|---|---|---|
| `reference/milo_character_sheet_official.webp` | Official Milo character sheet — visual source of truth | yes |
| `characters/milo/layers/*.png` | 2.5D front-view puppet layers (2x, shared canvas, RGBA) | yes |
| `characters/milo/rig/milo_front_rig.json` | Pivots, draw order, parenting, eye geometry, limits | yes |
| `timelines/milo_puppet_test_15s.json` | Puppet test timeline (subtle idle motion) | yes |
| `timelines/milo_acting_test_15s.json` | Character acting test: notice → excited → surprised → joy | yes |
| `scripts/extract_milo_layers.py` | Rebuilds layers + rig from the sheet (OpenCV, local) | yes |
| `scripts/render_puppet_test.py` | Renders any timeline via `video_compose` atelier mode (Remotion) | yes |
| `remotion/rainbow-tales-ep01/` | Remotion source: `MiloPuppet`, timeline evaluator, test scene | yes |
| `sets/grandpa-theo-workshop/source/` | Workshop background(s), as supplied | yes |
| `props/slipper/source/` | Slipper image(s), as supplied | yes |
| `characters/milo/source/stage2/` | Stage 2 Milo artwork (standing / walking / interaction), as supplied | yes |
| `scenes/sc01-workshop-slipper/` | Scene 01 shot plan, Stage 2 art spec, timelines | yes |
| `assets_manifest.json` | Provenance, checksums and inspection notes for every source asset | yes |
| `projects/rainbow-tales-ep01/renders/` | Rendered MP4s + QC stills | **no** |

## Reproduce

```bash
make cloud-setup && source .env.local-runtime          # once per container
pip install opencv-python-headless                      # free, local
EP=productions/the-rainbow-tales/ep01-milo-and-the-shop-that-sold-happiness
python3 $EP/scripts/extract_milo_layers.py              # layers + rig
python3 $EP/scripts/render_puppet_test.py               # -> projects/rainbow-tales-ep01/renders/milo_puppet_test_15s.mp4
python3 $EP/scripts/render_puppet_test.py --timeline timelines/milo_acting_test_15s.json   # -> .../milo_acting_test_15s.mp4
python3 $EP/scripts/render_puppet_test.py --scale 0.5 --output /tmp/draft.mp4   # fast draft
```

## Puppet

Draw order (back → front): `tail`, `body` (incl. chest patch), `head`, `mouth`,
eye states, `bandana`, `ear_left`, `ear_right`. `head` parents mouth, eyes and
ears; `body` breathing lifts head and bandana at their pivot heights.

| Layer | Pivot | Motion |
|---|---|---|
| body + chest patch | paws on floor | breathing, volume-preserving squash/stretch, hop (whole puppet) |
| head | neck under chin | tilt (±11° limit), lean/raise offsets (±30 px) |
| ear_left / ear_right | ear roots | spring follow-through on head tilt and bounce; outward swing capped (left +7°, right −6.5°) so the hidden cheek fill is never exceeded |
| tail | behind back paw | idle sway, wag (±28°) |
| bandana | knot line | slight lag on head / wag (±2°) |
| mouth (lower jaw + tongue) | upper lip line | panting, gasp (jaw drop) |
| eyes | — | blink / half-blink / wink / happy squeeze / wide via the sheet's official **Half Blink**, **Blink (Closed)** and **Wide** tiles, scaled and colour-matched per eye |

### What is synthesized (approved for this test only)

- `head`: 16 px cheek strip mirrored under each ear's inner edge (hidden at rest).
- `body`: 24 px jaw-fur band above the head cut line (hidden at rest).
- Eye-state tiles are used unmirrored for both eyes so catch-lights match the front view.

### Evaluated and rejected (needs new artwork)

- **Eye direction (iris glance):** the painted iris blends into the rim shadow,
  so a cut-out iris leaves fragments and bright edges when moved.
- **Mouth shapes (closed / small open / round):** the sheet's mouth tiles have a
  closed jaw, while the front view's jaw hangs open down to the bandana; the
  missing chin made the swap read as a pasted patch.
- **Real head turn:** only a front-view head exists as layers; a turn needs a
  layered 3/4 head. The acting test uses tilt + lean instead.

### Needs new artwork for production quality

1. Higher-resolution source (front view is only ~250x365 px on the sheet).
2. Layered front-view parts: head without ears, ears with roots, body with neck.
3. A fully visible tail in the front view (only a small tuft shows).
4. Brows / expression overlays at front-view scale (sad, determined, surprised).
5. Mouth shapes at front-view scale and angle for lip sync (incl. the chin for a closed jaw).
6. Separate iris + eye-white layers for eye direction.
7. A layered 3/4 head (and body) for real head turns.
8. Separated legs for walk/run; side, 3/4 and back views as parts.

See `QUALITY_REPORT.md` for the test render's QC results.
