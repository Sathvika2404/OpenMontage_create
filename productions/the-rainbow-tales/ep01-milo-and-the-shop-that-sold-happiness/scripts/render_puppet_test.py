"""Render a Milo puppet/acting test timeline through OpenMontage's video_compose.

Merges the rig + explicit action timeline into a Remotion props file under the
pipeline workspace (projects/rainbow-tales-ep01/, gitignored), then renders the
atelier composition in remotion/rainbow-tales-ep01/ with local Chromium (see
remotion-composer/remotion.config.ts).

Usage (from the repo root):
    python3 productions/the-rainbow-tales/ep01-milo-and-the-shop-that-sold-happiness/scripts/render_puppet_test.py \
        [--timeline timelines/milo_acting_test_15s.json] [--output PATH] [--scale 0.5]

The output defaults to projects/rainbow-tales-ep01/renders/<timeline id>.mp4 and
the composition to the timeline's "composition_id" (default MiloPuppetTest).

Static files are served from a public dir assembled per render under the
workspace (gitignored): Milo's layers at layers/, plus any timeline "assets"
(source files are never modified; "clamp_alpha_trim" writes a cleaned copy).
A timeline with "strip_audio": true gets its silent track removed so the MP4
duration is exactly the timeline duration.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

EP_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = EP_DIR.parents[2]
PROJECT_ID = "rainbow-tales-ep01"
WORKSPACE = REPO_ROOT / "projects" / PROJECT_ID

sys.path.insert(0, str(REPO_ROOT))


def clamp_alpha_trim(src: Path, dst: Path) -> float:
    """Make a lossy-alpha cut-out solid inside, trim to content; return h/w."""
    import numpy as np
    from PIL import Image

    im = np.asarray(Image.open(src).convert("RGBA")).copy()
    a = im[:, :, 3]
    a[a >= 240] = 255  # lossy WebP leaves the interior at ~253
    ys, xs = np.nonzero(a > 8)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(im).save(dst)
    return im.shape[0] / im.shape[1]


def assemble_public_dir(timeline: dict) -> Path:
    public = WORKSPACE / "public"
    if public.exists():
        shutil.rmtree(public)
    shutil.copytree(EP_DIR / "characters" / "milo" / "layers", public / "layers")
    for name, asset in (timeline.get("assets") or {}).items():
        src, dst = EP_DIR / asset["src"], public / asset["out"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if asset.get("prep") == "clamp_alpha_trim":
            aspect = clamp_alpha_trim(src, dst)
            if name in timeline.get("layout", {}):
                timeline["layout"][name]["aspect"] = round(aspect, 5)
        else:
            shutil.copyfile(src, dst)
    return public


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default="timelines/milo_puppet_test_15s.json")
    ap.add_argument("--output", help="default: projects/rainbow-tales-ep01/renders/<timeline id>.mp4")
    ap.add_argument("--scale", type=float, help="draft scale, e.g. 0.5")
    args = ap.parse_args()

    from lib.checkpoint import init_project
    from tools.video.video_compose import VideoCompose

    init_project(PROJECT_ID, title="Milo and the Shop That Sold Happiness",
                 pipeline_type="character-animation")

    timeline = json.loads((EP_DIR / args.timeline).read_text(encoding="utf-8"))
    output = args.output or str(WORKSPACE / "renders" / f"{timeline['id']}.mp4")
    rig = json.loads((EP_DIR / timeline["rig"]).read_text(encoding="utf-8"))
    props_path = WORKSPACE / "artifacts" / f"{timeline['id']}_props.json"
    props_path.parent.mkdir(parents=True, exist_ok=True)
    public_dir = assemble_public_dir(timeline)
    props_path.write_text(json.dumps({"rig": rig, "timeline": timeline}), encoding="utf-8")

    bespoke = {
        "entry": str(EP_DIR / "remotion" / "rainbow-tales-ep01" / "index.tsx"),
        "composition_id": timeline.get("composition_id", "MiloPuppetTest"),
        "props_path": str(props_path),
        "public_dir": str(public_dir),
        "crf": 16,
    }
    if args.scale:
        bespoke["scale"] = args.scale

    result = VideoCompose().execute({
        "operation": "render",
        "output_path": output,
        "edit_decisions": {
            "version": "1.0",
            "composition_mode": "atelier",
            "render_runtime": "remotion",
            "bespoke": bespoke,
            "cuts": [],
        },
    })
    if result.success and timeline.get("strip_audio"):
        tmp = Path(output).with_suffix(".tmp.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", output, "-map", "0:v:0", "-c", "copy",
                        "-movflags", "+faststart", str(tmp)], check=True)
        tmp.replace(output)
    print(json.dumps({"success": result.success, "error": result.error,
                      "output": output, "data": result.data}, indent=2, default=str)[:3000])
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
