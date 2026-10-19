# Quality report — Milo puppet test (15 s)

Render: `projects/rainbow-tales-ep01/renders/milo_puppet_test_15s.mp4` (gitignored)
Renderer: Remotion 4.0.484 via `video_compose` atelier mode, local
chrome-headless-shell (Playwright build 1194). No paid services used.

## Technical checks

| Check | Result |
|---|---|
| Container decodes end-to-end (`ffmpeg -f null`) | PASS, no errors |
| Video | H.264, 1920x1080, DAR 16:9, 30/1 fps, 450 frames |
| Duration | 15.0 s video (container 15.06 s due to the silent AAC track) |
| Audio | Silent AAC track (expected: the test has no audio) |
| Pixel format | `yuvj420p` (full range, Remotion default) |
| Frame-to-frame scan | Max mean change 0.74/255 (during the head tilt); no pops at eye-state swaps |

## Visual checks (frames 0, 3, 6, 9, 12, 14 s + 4.1, 7.3, 10.3 s close-ups)

| Check | Result |
|---|---|
| Matches the character sheet | PASS. Face, eyes, nose, tongue, ears, chest patch and teal bandana with gold star are all taken directly from the official front view. |
| Detached ears | PASS. The ears stay attached through the tilt and follow-through. |
| Distorted paws | PASS. Breathing pivots at the paws, so they stay planted. |
| Inconsistent faces | PASS. No full-head swaps were used. Blink and wink use the official eye-state art. |
| Background | PASS. Clean warm cream backdrop with a soft contact shadow. |
| Seams | MINOR. A small bluish-grey sliver (painted background from the sheet) is visible between the jaw and the root of the viewer's-right ear, most noticeable at the 4 s tilt. |

## Known defects (honest list)

1. **Soft, slightly stair-stepped silhouette edges.** The source figure is about 250x365 px and was upscaled 2x with Lanczos. Fine fur wisps were lost in the cut-out, and edges look a little soft or serrated at 1080p, especially around the ears.
2. **Faint light fringe** in places along the ear edges, left over from the sheet's painted background.
3. **Grey sliver** next to the right ear root (see above).
4. **Tail wag is subtle.** Only a small tuft of the tail is visible in the front view.
5. **The half-blink frames are a different eye drawing.** They're the official Half Blink tile, whose iris shape differs slightly from the open front-view eye. They're only on screen for about 0.4 s around 4.7 s.
6. **A soft ring is just visible around the closed eyes** where the tile is feathered into the face.
7. **Surprised expression not used.** A full-head swap from the expression row would have caused a jump in scale and lighting, so a wink was used instead, as the brief allowed.

All of these improve most with higher-resolution, layered source art (see README).
