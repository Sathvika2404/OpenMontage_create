# Quality reports

- [Scene 01: shots 1–2, revision 2 (10 s)](#scene-01--shots-12-revision-2-10-s) (latest)
- [Scene 01: shots 1–2 (10 s)](#scene-01--shots-12-10-s)
- [Character acting test (15 s)](#character-acting-test-15-s)
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


## Scene 01 — shots 1–2 (10 s)

Render: `projects/rainbow-tales-ep01/renders/sc01_shots01-02.mp4` (gitignored;
superseded by revision 2 at the same path).

### Technical checks

| Check | Result |
|---|---|
| Decodes end-to-end | PASS |
| Video | H.264 1920x1080, 16:9, 30 fps, **300 frames, 10.000 s**, no audio track |
| Camera continuity | PASS. The only discontinuity is the planned cut at frame 150 (5.0 s). The largest change elsewhere is at the push-in's peak speed (2.5 s); it's spread evenly across the frame, not a pop. |
| Slipper opacity | PASS. Interior fully opaque after import cleanup (98.7%); only the anti-aliased edge (1.3%) is partial |

### Milo placement (computed from layout + camera)

| Time | Milo paws (frame px) | Milo height | Slipper heel to toe (x) |
|---|---|---|---|
| 0 s (wide) | (822, 939) | 250 px | 924–1281 |
| 4.98 s (end of push-in) | (869, 910) | 273 px | 981–1371 |
| 5.0 s (medium) | (771, 850) | 567 px | 1003–1813 |
| 10 s | (792, 884) | 588 px | 1033–1873 |

Milo's floor point never moves in the world; only the camera moves, so there is no sliding. Scale changes only at the cut, never during a shot.

### Visual checks (0, 2, 4, 6, 8, 9 s)

| Check | Result |
|---|---|
| Both front paws visible, on the floor | PASS in all six frames |
| Floor shadows | PASS. Contact shadow under the paws and the sole, plus soft cast shadows running away from the window |
| Milo identity (fur, eyes, ears, chest patch, teal bandana and star) | PASS. Approved rig; only a mild warm grade to sit in the window light |
| Slipper heel faces Milo, toe right | PASS |
| Transparency artefacts on the slipper | None seen |

### Known defects and limitations

1. **The eyes don't shift toward the slipper.** The iris glance was rejected in the acting test, because the painted irises can't be cut cleanly. Attention reads through the ear twitch, wide-eyed pop, and tilt and lean toward the slipper. Real eye direction needs separate iris and eye-white art.
2. **The background is soft.** The 1672×941 plate is enlarged 1.19–1.30× in the wide shot and 2.7–2.8× in the medium shot. The medium shot hides it with a deliberate background blur.
3. **The slipper is slightly crisper and more photo-real** than the painted set, even after grading. Its toe curves up from the floor as drawn in the source art.
4. **Milo's cast shadow is a static silhouette.** It doesn't follow the small head and ear moves; with blur and 45% opacity this is hard to spot.
5. **A faint warm glow** shows under the viewer's-right eye during the wide-eyed pop (6 s), and earlier puppet-test edge softness still applies.


## Scene 01 — shots 1–2, revision 2 (10 s)

Review feedback: curiosity not clear enough; Milo stayed front-facing and
stationary. Revised in place: same workshop, slipper, layout, camera and cut.

Render: `projects/rainbow-tales-ep01/renders/sc01_shots01-02.mp4` (gitignored).
QC: `projects/rainbow-tales-ep01/renders/qc_sc01_r2/` (frames at 1, 1.4, 3, 4.5, 5, 5.5, 7, 8, 9, 9.9 s; contact sheet; face close-ups).

### What changed

| | Revision 1 | Revision 2 |
|---|---|---|
| Attention cue | none | A warm sun glint sweeps across the slipper (1.0–1.8 s) |
| Eyes | Always facing the viewer | Dart to screen-right at 1.45–1.62 s and stay on the slipper |
| Shot 1 head | Idle drift | Pause, then a turn and tilt toward the slipper (+6.5°, 2.3–3.1 s), ears following |
| Shot 2 | Tilt and hold | Tilt to 11°, curious blink (6.9–7.3 s), re-tilt, then a lean toward the slipper with paws planted (8.2–9.5 s) |
| Wide-eye pop | Used | Removed; that tile has a centred iris and would fight the gaze |

### How the gaze works (no new artwork)

The whole eye interior (iris, pupil, catch-light and white) slides under the
fixed dark rim. The side it uncovers is filled with that eye's own eye-white
colour, shaded under the lid. Nothing is cut around the iris, which is why
the earlier iris glance failed. There are 10 pre-rendered steps up to 4.5
source px, under 1 screen px apart.

### Checks

| Check | Result |
|---|---|
| Video | H.264 1920x1080, 16:9, 30 fps, 300 frames, **10.000 s**, no audio track; decodes cleanly |
| Camera continuity | The only discontinuity is the planned cut at frame 150; the largest change elsewhere is 6.8/255 at the push-in's peak speed |
| Gaze visible at normal speed | **Yes.** Eye-white clearly shows on the left of both irises from 1.6 s, in the wide shot (eyes about 25 px) and plainly in the medium shot (about 55 px) |
| Head movement visible at normal speed | **Yes.** About 6.5° tilt plus an 8 px lean in shot 1; 11° plus a lean in shot 2, then a forward lean toward the slipper |
| Paws, floor contact, shadows | Both front paws visible and planted in every inspected frame; the lean shears the body about the paw line |
| Bandana, identity | Unchanged approved layers; no layer other than the new gaze frames was modified |

### Known defects and limitations

1. **The gaze only goes to screen-right**, up to 4.5 source px. Left, up and down need separate iris and eye-white art, or another build of this technique.
2. **A faint inner band** sometimes shows in the viewer's-left eye's white during the gaze. It's the original eye-white edge riding along, about 1–2 screen px in the medium shot.
3. **Blinks while gazing pass briefly through the official Half Blink tile,** whose iris is centred (about 0.1 s, e.g. 7.0 s).
4. **The head turn is a tilt plus lean, not a true 3/4 turn.** As requested, the flat head isn't rotated into a side view.
5. **The bandana's screen-right corner has a slightly ragged edge,** visible in the medium shot (from the original cut-out).
6. Previous scene-01 limitations still apply: a soft enlarged background, a slightly photo-real slipper, and a static cast shadow.
