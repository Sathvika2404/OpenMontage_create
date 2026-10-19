"""Render the 15-second Milo puppet test through OpenMontage's video_compose.

Merges the rig + explicit action timeline into a Remotion props file under the
pipeline workspace (projects/rainbow-tales-ep01/, gitignored), then renders the
atelier composition in remotion/rainbow-tales-ep01/ with local Chromium (see
remotion-composer/remotion.config.ts).

Usage (from the repo root):
    python3 productions/the-rainbow-tales/ep01-milo-and-the-shop-that-sold-happiness/scripts/render_puppet_test.py \
        [--timeline timelines/milo_puppet_test_15s.json] [--output PATH] [--scale 0.5]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EP_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = EP_DIR.parents[2]
PROJECT_ID = "rainbow-tales-ep01"
WORKSPACE = REPO_ROOT / "projects" / PROJECT_ID

sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default="timelines/milo_puppet_test_15s.json")
    ap.add_argument("--output", default=str(WORKSPACE / "renders" / "milo_puppet_test_15s.mp4"))
    ap.add_argument("--scale", type=float, help="draft scale, e.g. 0.5")
    args = ap.parse_args()

    from lib.checkpoint import init_project
    from tools.video.video_compose import VideoCompose

    init_project(PROJECT_ID, title="Milo and the Shop That Sold Happiness",
                 pipeline_type="character-animation")

    timeline = json.loads((EP_DIR / args.timeline).read_text(encoding="utf-8"))
    rig = json.loads((EP_DIR / timeline["rig"]).read_text(encoding="utf-8"))
    props_path = WORKSPACE / "artifacts" / f"{timeline['id']}_props.json"
    props_path.parent.mkdir(parents=True, exist_ok=True)
    props_path.write_text(json.dumps({"rig": rig, "timeline": timeline}), encoding="utf-8")

    bespoke = {
        "entry": str(EP_DIR / "remotion" / "rainbow-tales-ep01" / "index.tsx"),
        "composition_id": "MiloPuppetTest",
        "props_path": str(props_path),
        "public_dir": str(EP_DIR / "characters" / "milo"),
        "crf": 16,
    }
    if args.scale:
        bespoke["scale"] = args.scale

    result = VideoCompose().execute({
        "operation": "render",
        "output_path": args.output,
        "edit_decisions": {
            "version": "1.0",
            "composition_mode": "atelier",
            "render_runtime": "remotion",
            "bespoke": bespoke,
            "cuts": [],
        },
    })
    print(json.dumps({"success": result.success, "error": result.error,
                      "output": args.output, "data": result.data}, indent=2, default=str)[:3000])
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
