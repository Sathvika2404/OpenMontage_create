# Quality reports

- [Character acting test (15 s)](#character-acting-test-15-s) (latest)
- [Puppet test (15 s)](#puppet-test-15-s)

## Puppet test (15 s)

Render: `projects/rainbow-tales-ep01/renders/milo_puppet_test_15s.mp4` (gitignored)
Renderer: Remotion 4.0.484 via `video_compose` atelier mode, local
chrome-headless-shell (Playwright build 1194). No paid services used.

### Technical checks

| Check | Result |
|---|---|
| Container decodes end-to-end (`ffmpeg -f null`) | PASS, no errors |
| Video | H.264, 1920x1080, DAR 16:9, 30/1 fps, 450 frames |
| Duration | 15.0 s video (container 15.06 s due to the silent AAC track) |
| Audio | Silent AAC track (expected: the test has no audio) |
| Pixel format | `yuvj420p` (full range, Remotion default) |
| Frame-to-frame scan | Max mean change 0.74/255 (during the head tilt); no pops at eye-state swaps |

### Visual checks (frames 0, 3, 6, 9, 12, 14 s + 4.1, 7.3, 10.3 s close-ups)

| Check | Result |
|---|---|
| Matches the character sheet | PASS. Face, eyes, nose, tongue, ears, chest patch and teal bandana with gold star are all taken directly from the official front view. |
| Detached ears | PASS. The ears stay attached through the tilt and follow-through. |
| Distorted paws | PASS. Breathing pivots at the paws, so they stay planted. |
| Inconsistent faces | PASS. No full-head swaps were used. Blink and wink use the official eye-state art. |
| Background | PASS. Clean warm cream backdrop with a soft contact shadow. |
| Seams | MINOR. A small bluish-grey sliver (painted background from the sheet) is visible between the jaw and the root of the viewer's-right ear, most noticeable at the 4 s tilt. |

### Known defects (honest list)

1. **Soft, slightly stair-stepped silhouette edges.** The source figure is about 250x365 px and was upscaled 2x with Lanczos. Fine fur wisps were lost in the cut-out, and edges look a little soft or serrated at 1080p, especially around the ears.
2. **Faint light fringe** in places along the ear edges, left over from the sheet's painted background.
3. **Grey sliver** next to the right ear root (see above).
4. **Tail wag is subtle.** Only a small tuft of the tail is visible in the front view.
5. **The half-blink frames are a different eye drawing.** They're the official Half Blink tile, whose iris shape differs slightly from the open front-view eye. They're only on screen for about 0.4 s around 4.7 s.
6. **A soft ring is just visible around the closed eyes** where the tile is feathered into the face.
7. **Surprised expression not used.** A full-head swap from the expression row would have caused a jump in scale and lighting, so a wink was used instead, as the brief allowed.

All of these improve most with higher-resolution, layered source art (see README).


## Character acting test (15 s)

Render: `projects/rainbow-tales-ep01/renders/milo_acting_test_15s.mp4` (gitignored)
Timeline: `timelines/milo_acting_test_15s.json`. Composition: `MiloActingTest`.

### What changed from the puppet test

| | Puppet test | Acting test |
|---|---|---|
| Framing | Milo about 770 px tall | 1.25x, about 970 px tall, full body, paws on a floor line at y=1046 |
| Motion (mean frame-to-frame change) | 0.14 | 0.96 (about 7x) |
| Frames with visible motion (>0.3) | 48 of 449 | 292 of 449 |
| Head | ±6° tilt | 10–11° tilt toward Milo's left, plus a lean (16 px) and raise, with an anticipation dip first |
| Body | 1.1% breathing | Hops with volume-preserving squash/stretch; anticipation squash before each big move |
| Tail | ±12° | ±24° fast wag |
| Ears | Gentle follow | Spring follow on tilt and on every bounce, a twitch at the sound, a flare on surprise |
| Eyes | Blink, wink | Official Wide eyes (notice, surprise), double-take blink, happy closed-eye squeeze |
| Mouth | Subtle | Panting during excitement, jaw-drop gasp on surprise |

### Technical checks

| Check | Result |
|---|---|
| Decodes end-to-end | PASS |
| Video | H.264 1920x1080, 16:9, 30 fps, 450 frames, 15.0 s (silent AAC) |
| Head never clipped at frame top | PASS (highest fur row 60) |
| Both front paws visible in every frame | PASS (lowest fur row 1020 of 1080, including during hops) |
| Largest frame-to-frame change | 5.8/255 at frame 372, the joyful hop; motion, not a pop |

### Visual checks

| Check | Result |
|---|---|
| Notice (0–5 s) readable | PASS. Ear twitch, wide-eyed pop, then a clear tilt and lean toward Milo's left |
| Excited (5–10 s) readable | PASS. Bounce, wag, panting and ear flaps |
| Surprised (10–12.3 s) readable | PASS. Wide eyes, gasp, pull-back, freeze, double-take blink |
| Joy (12.3–15 s) readable | PASS. Hop, happy closed-eye squeeze, wag |
| Proportions / face preserved | PASS. No warping; every face change is official sheet art |
| Missing artwork exposed | PASS after fixes. The ear swing is capped inside the hidden cheek fill (a 9° flare exposed a grey pocket and was reduced) |

### Known defects and limitations

1. **The head "turn" is a tilt plus lean.** A real turn needs a layered 3/4 head; I didn't fake it with skewing.
2. **No eye direction.** The iris glance was tried and rejected (fragments and bright edges). Curiosity is shown with a wide-eye pop instead.
3. **The mouth never closes.** Mouth tiles were tried and rejected (pasted look, missing chin). Surprise is a jaw drop on the open mouth.
4. **A faint warm glow** remains below the viewer's-right Wide eye (the tile's bright lower lid).
5. **The tail is still a small tuft.** The wag is bigger but limited by the visible artwork.
6. **The hop lifts the whole sitting body.** This reads as a joyful bounce, but a real puppy would push off with its front legs, and that needs separate leg artwork.
7. Defects 1–3 from the puppet test still apply: soft edges, a light ear fringe, and the grey sliver at the right ear root.
