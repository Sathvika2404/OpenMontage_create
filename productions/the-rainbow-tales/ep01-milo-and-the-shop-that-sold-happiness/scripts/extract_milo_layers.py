"""Extract Milo's front-view 2.5D puppet layers from the official reference sheet.

Source of truth: reference/milo_character_sheet_official.webp (1536x1024).
Only the FRONT VIEW figure is used. Every layer is cut from the official
artwork; the only synthesized pixels are small copied-fur fills in regions the
sheet hides (approved for the test):

  - head: a strip under each ear, mirrored from the adjacent cheek fur, so a
    swinging ear never reveals a hole;
  - body: a band above the head cut line, copied from the head's own jaw fur,
    so a tilting head never reveals a hole at the neck;
  - eyelids: none synthesized; blinks use the sheet's official Half Blink and
    Blink (Closed) eye-state tiles, scaled and colour-matched onto each eye.

All layers share one canvas (crop of the sheet, upscaled SCALE x with
Lanczos), so the renderer only needs per-layer transforms around pivots.
Coordinates below are in CROP pixels (origin = sheet (270, 5)), measured on
zoomed grid overlays of the sheet.

Usage:
    python3 scripts/extract_milo_layers.py [--debug-dir DIR]

Writes characters/milo/layers/*.png and characters/milo/rig/milo_front_rig.json.
Requires: opencv-python-headless, numpy (free, local).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

EP_DIR = Path(__file__).resolve().parent.parent
SHEET = EP_DIR / "reference" / "milo_character_sheet_official.webp"
LAYER_DIR = EP_DIR / "characters" / "milo" / "layers"
RIG_PATH = EP_DIR / "characters" / "milo" / "rig" / "milo_front_rig.json"

# Front-view figure crop on the sheet. Right edge stops before the 3/4 view.
CROP_X, CROP_Y, CROP_W, CROP_H = 270, 5, 282, 387
SCALE = 2

# --- Part polygons (crop px) ------------------------------------------------
# Viewer's left ear. Inner edge follows the dark crease between ear and cheek.
EAR_L = [(78, 58), (72, 50), (60, 47), (45, 55), (32, 70), (20, 88), (10, 108),
         (3, 130), (2, 160), (10, 186), (27, 206), (45, 218), (63, 218),
         (72, 206), (75, 185), (74, 160), (72, 130), (71, 105), (70, 85), (74, 68)]
# Viewer's right ear.
EAR_R = [(203, 36), (215, 30), (233, 43), (251, 60), (265, 84), (275, 108),
         (279, 135), (275, 161), (266, 181), (251, 195), (232, 198), (222, 191),
         (217, 170), (215, 145), (213, 120), (211, 95), (208, 70), (205, 50)]
# Head (face + crown), bounded below by the bandana's top edge.
HEAD_CUT = [(217, 172), (212, 182), (200, 184), (185, 190), (150, 197),
            (110, 192), (88, 188), (80, 180), (74, 160)]
HEAD_TOP = [(74, 68), (70, 40), (78, 10), (110, -5), (150, -8), (190, -5),
            (207, 15), (205, 50), (208, 70), (211, 95), (213, 120), (215, 145)]
HEAD_OVERLAP_PX = 8   # head extends under the bandana by this much
NECK_FILL_PX = 24     # body band copied from the jaw above the cut line
EAR_FILL_PX = 16      # cheek strip mirrored under each ear's inner edge
# Lower jaw + tongue, for subtle mouth movement.
MOUTH = [(103, 153), (115, 160), (130, 158), (150, 156), (165, 158), (178, 152),
         (177, 165), (169, 180), (150, 193), (128, 191), (112, 181)]
# Bandana bounding polygon (refined by teal/gold colour inside it).
BANDANA = [(84, 184), (100, 186), (150, 192), (200, 180), (206, 186), (204, 210),
           (185, 235), (160, 258), (150, 266), (138, 258), (110, 232), (88, 210)]
# Golden star emblem on the bandana (fur shares the star's hue range).
STAR_BOX = [(126, 210), (166, 210), (166, 250), (126, 250)]
# Tail tuft peeking out behind the viewer's-left back paw (low contrast).
TAIL = [(52, 331), (40, 327), (28, 331), (19, 341), (21, 351), (31, 358),
        (43, 358), (50, 350)]
# Central face features protected from backdrop removal: (cx, cy), (rx, ry).
FEATURES_ELLIPSE = ((142, 128), (72, 72))
# Official "Eye States" tiles (SHEET px): eye centre of each tile. The tiles
# are close-ups at ~1.47x the front-view eye size. They are NOT mirrored for
# the second eye: unmirrored, the catch-light sits upper-right like both eyes
# in the front view.
EYE_TILE_CENTERS = {"open": (631, 946), "half": (724, 946), "closed": (818, 946), "wide": (913, 946)}
EYE_TILE_RIM = (28.5, 27.0)   # half-size of the open tile's dark rim (sheet px)
EYE_TILE_Y_LIMIT = (899, 979)  # stay inside the rounded tile
# Eyes: (cx, cy, rx, ry) of the dark outer rim.
EYE_L = (103.5, 103.5, 19.5, 18.5)
EYE_R = (178.0, 94.0, 18.0, 19.0)

# NOTE: separating the irises for eye direction ("glance") was evaluated and
# rejected: in the painted art the iris blends softly into the rim shadow, so
# a hard-edged iris cut leaves fragments and bright edges when shifted. Needs
# separate iris + eye-white artwork.
# NOTE: the sheet's "Mouth Shapes" tiles were evaluated and rejected for the
# front view: they show a closed/near-closed jaw, while the front view's jaw
# hangs open down to the bandana, so swapping them in requires chin artwork
# that does not exist (it read as a pasted patch). Needs new front-view art.

PIVOTS = {
    "body": (141, 387),     # paws on the floor; breathing scales from here
    "head": (145, 205),     # neck, just below the chin
    "ear_left": (68, 60),   # ear roots
    "ear_right": (210, 44),
    "bandana": (145, 192),  # knot line under the chin
    "tail": (54, 346),      # hidden behind the back paw
    "mouth": (141, 154),    # upper lip line
}


def poly_mask(points, shape, offset=(0, 0)) -> np.ndarray:
    m = np.zeros(shape, np.uint8)
    pts = np.array([(x + offset[0], y + offset[1]) for x, y in points], np.int32)
    cv2.fillPoly(m, [pts], 255)
    return m


def fill_holes(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    flood = mask.copy()
    ff = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(flood, ff, (0, 0), 255)
    return mask | cv2.bitwise_not(flood)


def foreground_mask(crop: np.ndarray) -> np.ndarray:
    """GrabCut silhouette, with eye whites restored and the tail added."""
    mask = np.zeros(crop.shape[:2], np.uint8)
    rect = (6, 4, CROP_W - 8, CROP_H - 6)
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(crop, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
    # Second pass: pin parts we know are character (incl. faint tail).
    sure_fg = np.zeros_like(mask)
    for poly in (TAIL, MOUTH, BANDANA):
        sure_fg |= cv2.erode(poly_mask(poly, mask.shape), np.ones((5, 5), np.uint8))
    for cx, cy, rx, ry in (EYE_L, EYE_R):
        cv2.ellipse(sure_fg, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, 255, -1)
    mask[sure_fg > 0] = cv2.GC_FGD
    cv2.grabCut(crop, mask, None, bgd, fgd, 4, cv2.GC_INIT_WITH_MASK)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    # Keep the largest component plus the tail.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    if n > 1:
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg = np.where(labels == largest, 255, 0).astype(np.uint8)
    tail = poly_mask(TAIL, fg.shape)
    fg |= cv2.bitwise_and(tail, cv2.GaussianBlur(tail, (0, 0), 1.5))
    fg = fill_holes(fg)
    # Drop desaturated grey-brown backdrop pockets (e.g. between ear and
    # shoulder). Fur is saturated orange (S > 100); dark creases/paw lines are
    # kept by the V floor. The face is excluded: nose and eye rims are grey.
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    backdrop = cv2.inRange(hsv, (0, 0, 100), (180, 96, 178))
    backdrop = cv2.morphologyEx(backdrop, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    features = np.zeros_like(backdrop)  # eyes, nose, mouth: legitimately grey/dark
    cv2.ellipse(features, FEATURES_ELLIPSE[0], FEATURES_ELLIPSE[1], 0, 0, 360, 255, -1)
    backdrop &= ~features
    fg &= ~backdrop
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    keep = np.zeros_like(fg)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 40:
            keep[labels == i] = 255
    return keep


def decontaminate(img: np.ndarray, fg: np.ndarray) -> np.ndarray:
    """Replace edge colours with interior fur colours to kill background halos."""
    core = cv2.erode(fg, np.ones((5, 5), np.uint8))
    hole = cv2.bitwise_and(cv2.dilate(fg, np.ones((7, 7), np.uint8)), cv2.bitwise_not(core))
    filled = cv2.inpaint(img, hole, 4, cv2.INPAINT_TELEA)
    edge = cv2.bitwise_and(fg, cv2.bitwise_not(core)) > 0
    out = img.copy()
    # Blend: keep 35% of the original at the edge for texture, 65% interior colour.
    out[edge] = (0.35 * img[edge] + 0.65 * filled[edge]).astype(np.uint8)
    out[~(fg > 0)] = filled[~(fg > 0)]
    return out


def mirror_fill_horizontal(img, region, boundary_x, direction):
    """Fill region pixels by mirroring across a per-row boundary x.

    direction=-1 fills to the left of the boundary from pixels on its right.
    """
    out = img.copy()
    ys, xs = np.nonzero(region)
    for y, x in zip(ys, xs):
        bx = boundary_x(y)
        sx = int(round(2 * bx - x))
        if 0 <= sx < img.shape[1] and (sx - bx) * direction < 0:
            out[y, x] = img[y, sx]
    return out


def interp_x(points, y):
    pts = sorted(points, key=lambda p: p[1])
    ys = [p[1] for p in pts]
    xs = [p[0] for p in pts]
    return float(np.interp(y, ys, xs))


def soft_alpha(mask: np.ndarray, sigma: float) -> np.ndarray:
    """Anti-aliased alpha at output scale.

    The GrabCut mask is pixel-stepped; smoothing and re-thresholding it at
    source resolution removes the staircase, then a blur at SCALE x gives a
    soft but crisp edge. `sigma` is in source px.
    """
    smooth = cv2.GaussianBlur(mask, (0, 0), 1.0)
    smooth = np.where(smooth >= 128, 255, 0).astype(np.uint8) | (mask & cv2.erode(mask, np.ones((3, 3), np.uint8)))
    big = cv2.resize(smooth, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(big, (0, 0), sigma * SCALE)


def up(a: np.ndarray, interp=cv2.INTER_LANCZOS4) -> np.ndarray:
    return cv2.resize(a, None, fx=SCALE, fy=SCALE, interpolation=interp)


def save_layer(name, color, alpha, layers):
    color = color.copy()
    color[alpha == 0] = 0  # keeps PNGs small; fully transparent anyway
    rgba = np.dstack([color, alpha])
    path = LAYER_DIR / f"{name}.png"
    cv2.imwrite(str(path), rgba, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    ys, xs = np.nonzero(alpha > 8)
    layers[name] = {
        "file": f"layers/{name}.png",
        "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None,
    }


def fit_eye_tiles(sheet: np.ndarray, face: np.ndarray) -> dict:
    """Scale the official eye-state tiles onto each front-view eye.

    Returns {(side, state): (bgr, alpha)} at output scale. Each tile is
    colour-matched to the face fur in a ring around the eye (per-channel gain)
    and blended through a feathered ellipse so no tile edge shows.
    """
    out = {}
    trx, try_ = EYE_TILE_RIM
    H, W = CROP_H * SCALE, CROP_W * SCALE
    face_big = up(face)
    for side, (cx, cy, rx, ry) in (("left", EYE_L), ("right", EYE_R)):
        sx, sy = rx / trx, ry / try_  # sheet-tile px -> crop px
        ring = np.zeros((H, W), np.uint8)
        cv2.ellipse(ring, (int(cx * SCALE), int(cy * SCALE)), (int((rx + 8) * SCALE), int((ry + 8) * SCALE)), 0, 0, 360, 255, -1)
        cv2.ellipse(ring, (int(cx * SCALE), int(cy * SCALE)), (int((rx + 3) * SCALE), int((ry + 3) * SCALE)), 0, 0, 360, 0, -1)
        alpha = np.zeros((H, W), np.uint8)
        # Raised 1px and shortened: the tiles end ~23px below the eye centre,
        # so a taller fade would show the tile's bottom edge as a line.
        cv2.ellipse(alpha, (int(cx * SCALE), int((cy - 1) * SCALE)), (int((rx + 3) * SCALE), int((ry + 2) * SCALE)), 0, 0, 360, 255, -1)
        alpha = cv2.GaussianBlur(alpha, (0, 0), 2.2 * SCALE)
        alpha = np.clip(alpha.astype(np.float32) * 1.5, 0, 255).astype(np.uint8)
        wide_alpha = np.zeros((H, W), np.uint8)
        # Raised slightly: the Wide tile paints a bright lower lid that would
        # glow against the front view's darker cheek fur.
        cv2.ellipse(wide_alpha, (int(cx * SCALE), int((cy - 1.5) * SCALE)), (int((rx + 2.5) * SCALE), int((ry + 1.5) * SCALE)), 0, 0, 360, 255, -1)
        wide_alpha = np.clip(cv2.GaussianBlur(wide_alpha, (0, 0), 1.6 * SCALE).astype(np.float32) * 1.5, 0, 255).astype(np.uint8)
        for state in ("half", "closed", "wide"):
            tcx, tcy = EYE_TILE_CENTERS[state]
            hw, hh = int((rx + 9) / sx), int((ry + 9) / sy)
            y0, y1 = max(tcy - hh, EYE_TILE_Y_LIMIT[0]), min(tcy + hh, EYE_TILE_Y_LIMIT[1])
            tile = sheet[y0:y1, tcx - hw:tcx + hw]
            scale = SCALE * sx
            tw, th = int(round(tile.shape[1] * scale)), int(round(tile.shape[0] * SCALE * sy))
            # INTER_AREA: this is a downscale of higher-detail official art.
            small = cv2.resize(tile, (tw, th), interpolation=cv2.INTER_AREA)
            canvas = np.zeros((H, W, 3), np.uint8)
            ox = int(round(cx * SCALE - tw / 2))
            oy = int(round(cy * SCALE - (tcy - y0) * SCALE * sy))
            canvas[oy:oy + th, ox:ox + tw] = small
            covered = np.zeros((H, W), np.uint8)
            covered[oy:oy + th, ox:ox + tw] = 255
            r = (ring > 0) & (covered > 0)
            # Feather where the tile ends so its rectangle never shows.
            covered = cv2.GaussianBlur(cv2.erode(covered, np.ones((5, 5), np.uint8)), (0, 0), 1.2 * SCALE)
            gain = face_big[r].reshape(-1, 3).mean(0) / np.maximum(canvas[r].reshape(-1, 3).mean(0), 1)
            canvas = np.clip(canvas.astype(np.float32) * gain, 0, 255).astype(np.uint8)
            a = wide_alpha if state == "wide" else alpha
            out[(side, state)] = (canvas, np.minimum(a, covered))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug-dir", type=Path)
    args = ap.parse_args()

    sheet = cv2.imread(str(SHEET), cv2.IMREAD_COLOR)
    if sheet is None or sheet.shape[:2] != (1024, 1536):
        raise SystemExit(f"Unexpected reference sheet: {SHEET}")
    crop = sheet[CROP_Y:CROP_Y + CROP_H, CROP_X:CROP_X + CROP_W].copy()
    shape = crop.shape[:2]

    fg = foreground_mask(crop)
    color = decontaminate(crop, fg)

    # Ears may extend outward (away from the face) to catch wispy edge fur.
    face_hull = poly_mask(HEAD_TOP + HEAD_CUT, shape)
    grow = np.ones((13, 13), np.uint8)
    ear_l = (poly_mask(EAR_L, shape) | (cv2.dilate(poly_mask(EAR_L, shape), grow) & ~face_hull)) & fg
    ear_r = (poly_mask(EAR_R, shape) | (cv2.dilate(poly_mask(EAR_R, shape), grow) & ~face_hull)) & fg
    ear_r &= ~ear_l
    ears = ear_l | ear_r
    tail = poly_mask(TAIL, shape) & fg
    head_poly = HEAD_TOP + [(x, y + HEAD_OVERLAP_PX) for x, y in HEAD_CUT]
    head_region = poly_mask(head_poly, shape) & fg & ~ears
    head_visible = poly_mask(HEAD_TOP + HEAD_CUT, shape) & fg & ~ears
    bandana_box = poly_mask(BANDANA, shape)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    teal = cv2.inRange(hsv, (78, 60, 50), (105, 255, 255))
    gold = cv2.inRange(hsv, (12, 90, 120), (35, 255, 255))
    bandana = fill_holes(cv2.morphologyEx((teal | (gold & poly_mask(STAR_BOX, shape))) & bandana_box,
                                          cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
    mouth = poly_mask(MOUTH, shape)

    # --- Head colour: mirrored cheek fur under each ear's inner edge. -------
    head_color = color.copy()
    for ear_mask, inner, direction in (
        (ear_l, EAR_L[-11:], -1),  # inner edge points of left ear (x grows to the right)
        (ear_r, EAR_R[-8:] + EAR_R[:1], +1),
    ):
        band = cv2.dilate(face_hull, np.ones((1, 2 * EAR_FILL_PX + 1), np.uint8)) & ear_mask
        head_color = mirror_fill_horizontal(head_color, band, lambda y, pts=inner: interp_x(pts, y), direction)
        head_region |= band
    head_alpha = soft_alpha(head_region, 0.7)

    # --- Body: everything except head/ears/tail, plus a neck band of jaw fur.
    body_region = fg & ~head_visible & ~ears & ~tail
    neck_band = cv2.dilate(body_region, np.ones((NECK_FILL_PX * 2 + 1, 1), np.uint8)) & head_visible
    body_region |= neck_band
    body_alpha = soft_alpha(body_region, 0.7)

    # --- Eyelids: official Half Blink / Blink tiles fitted into each eye. ---
    eye_states = fit_eye_tiles(sheet, color)

    layers: dict[str, dict] = {}
    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    save_layer("tail", up(color), soft_alpha(tail, 1.4), layers)
    save_layer("body", up(color), body_alpha, layers)
    save_layer("head", up(head_color), head_alpha, layers)
    save_layer("mouth", up(color), soft_alpha(mouth & fg, 1.2), layers)
    for (side, state), (rgb, alpha) in eye_states.items():
        save_layer(f"eye_{side}_{state}", rgb, alpha, layers)
    save_layer("bandana", up(color), soft_alpha(bandana, 0.6), layers)
    save_layer("ear_left", up(color), soft_alpha(ear_l, 0.7), layers)
    save_layer("ear_right", up(color), soft_alpha(ear_r, 0.7), layers)
    # Full composite for comparison against the sheet.
    save_layer("_reference_cutout", up(color), soft_alpha(fg, 0.7), layers)

    s = SCALE
    rig = {
        "character_id": "milo",
        "view": "front",
        "source": {
            "file": "reference/milo_character_sheet_official.webp",
            "crop": [CROP_X, CROP_Y, CROP_W, CROP_H],
            "scale": SCALE,
        },
        "canvas": {"width": CROP_W * s, "height": CROP_H * s},
        "draw_order": ["tail", "body", "head", "mouth", "eye_states",
                       "bandana", "ear_left", "ear_right"],
        "parenting": {
            "head": ["mouth", "eye_states", "ear_left", "ear_right"],
            "body": ["head", "bandana"],
        },
        "pivots": {k: [x * s, y * s] for k, (x, y) in PIVOTS.items()},
        "eyes": {
            name: {"cx": cx * s, "cy": cy * s, "rx": (rx + 2) * s, "ry": (ry + 2) * s}
            for name, (cx, cy, rx, ry) in (("left", EYE_L), ("right", EYE_R))
        },
        "eyelid": {"mode": "official_tile_swap", "half_full_at": 0.4, "closed_from": 0.55, "closed_full_at": 0.9},
        # Limits keep every rotation inside the artwork that actually exists:
        # ears swing outward only as far as the mirrored cheek strip reaches,
        # and the head never tilts far enough to expose the neck cut.
        "limits_deg": {"head": [-11, 11], "ear_left": [-6, 7], "ear_right": [-6.5, 6],
                       "tail": [-28, 28], "bandana": [-2, 2]},
        "limits_px": {"head_offset": 30},
        "layers": layers,
        "synthesized_fills": {
            "head": f"{EAR_FILL_PX}px cheek strip mirrored under each ear (hidden at rest)",
            "body": f"{NECK_FILL_PX}px jaw-fur band above the head cut line (hidden at rest)",
            "eye_states": "official Half Blink / Blink (Closed) / Wide tiles scaled onto each eye, colour-matched to the surrounding fur (not mirrored, so catch-lights match the front view)",
        },
    }
    RIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    RIG_PATH.write_text(json.dumps(rig, indent=2) + "\n", encoding="utf-8")

    if args.debug_dir:
        args.debug_dir.mkdir(parents=True, exist_ok=True)
        dbg = crop.copy()
        for poly, col in ((EAR_L, (255, 0, 0)), (EAR_R, (255, 0, 0)), (head_poly, (0, 255, 0)),
                          (MOUTH, (0, 0, 255)), (BANDANA, (255, 255, 0)), (TAIL, (255, 0, 255))):
            cv2.polylines(dbg, [np.array(poly, np.int32)], True, col, 1)
        for x, y in PIVOTS.values():
            cv2.circle(dbg, (x, y), 3, (0, 0, 255), -1)
        cv2.imwrite(str(args.debug_dir / "milo_rig_overlay.png"), up(dbg, cv2.INTER_NEAREST))
    print(f"Wrote {len(layers)} layers to {LAYER_DIR} and rig to {RIG_PATH}")


if __name__ == "__main__":
    main()
