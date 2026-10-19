"""Local runtime resolution for sandboxed / offline environments.

Some environments (cloud sandboxes, CI, air-gapped machines) block the
browser downloads and CDNs that the render runtimes assume by default.
This module resolves *local* substitutes so tools keep working there:

  - a Chromium binary for Remotion and HyperFrames (instead of letting
    them download chrome-headless-shell),
  - a local copy of GSAP (instead of cdn.jsdelivr.net),
  - an absolute path to a Piper voice model (instead of a bare model name
    that only resolves relative to the current working directory).

Every resolver returns ``None`` when nothing local is found, so callers
fall back to the upstream default behavior unchanged.

Environment variables (all optional; see scripts/setup_cloud_env.sh):
  OPENMONTAGE_BROWSER_EXECUTABLE  Chromium/Chrome binary for headless renders
  REMOTION_BROWSER_EXECUTABLE     read by remotion-composer/remotion.config.ts
  HYPERFRAMES_BROWSER_PATH        read natively by the hyperframes CLI
  OPENMONTAGE_GSAP_PATH           path to gsap.min.js
  OPENMONTAGE_VENDOR_DIR          npm prefix holding vendored JS (default: <repo>/.vendor)
  PIPER_MODEL_DIR                 directory holding Piper *.onnx voices
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

GSAP_VERSION = "3.14.2"
GSAP_CDN_URL = f"https://cdn.jsdelivr.net/npm/gsap@{GSAP_VERSION}/dist/gsap.min.js"

_BROWSER_ENV_VARS = (
    "OPENMONTAGE_BROWSER_EXECUTABLE",
    "REMOTION_BROWSER_EXECUTABLE",
    "HYPERFRAMES_BROWSER_PATH",
)


def _is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def resolve_browser_executable() -> Optional[str]:
    """Return a local Chromium binary suitable for headless rendering."""
    for var in _BROWSER_ENV_VARS:
        value = os.environ.get(var)
        if value and _is_executable(Path(value)):
            return str(Path(value).resolve())

    # Playwright-managed browsers (pre-installed in Claude Code cloud sessions).
    # Prefer chrome-headless-shell: it is what Remotion and HyperFrames
    # download by default, so it needs no chrome-mode override.
    pw_root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    candidates = sorted(
        pw_root.glob("chromium_headless_shell-*/chrome-linux*/headless_shell"), reverse=True
    )
    candidates.append(pw_root / "chromium")
    candidates += sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True)
    for candidate in candidates:
        if _is_executable(candidate):
            return str(candidate.resolve())

    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    return None


def browser_env(base: Optional[dict[str, str]] = None) -> dict[str, str]:
    """Return an environment with the local browser exported for Node renderers."""
    env = dict(os.environ if base is None else base)
    browser = resolve_browser_executable()
    if browser:
        env.setdefault("HYPERFRAMES_BROWSER_PATH", browser)
        env.setdefault("REMOTION_BROWSER_EXECUTABLE", browser)
    return env


def resolve_gsap_path() -> Optional[Path]:
    """Return a local gsap.min.js, or None to fall back to the CDN."""
    override = os.environ.get("OPENMONTAGE_GSAP_PATH")
    if override and Path(override).is_file():
        return Path(override).resolve()

    vendor_dir = Path(os.environ.get("OPENMONTAGE_VENDOR_DIR", REPO_ROOT / ".vendor"))
    for root in (vendor_dir, REPO_ROOT / "remotion-composer"):
        candidate = root / "node_modules" / "gsap" / "dist" / "gsap.min.js"
        if candidate.is_file():
            return candidate.resolve()
    return None


def stage_gsap(workspace: Path, rel_dir: str = "assets/vendor") -> str:
    """Copy local GSAP into ``workspace/rel_dir`` and return the script src.

    The returned src is relative to ``workspace``. When no local copy is
    available, the CDN URL is returned instead (upstream default).
    """
    local = resolve_gsap_path()
    if local is None:
        return GSAP_CDN_URL
    dest_dir = Path(workspace) / rel_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(local, dest_dir / "gsap.min.js")
    return f"{rel_dir.strip('/')}/gsap.min.js"


def piper_model_dirs() -> list[Path]:
    dirs: list[Path] = []
    if os.environ.get("PIPER_MODEL_DIR"):
        dirs.append(Path(os.environ["PIPER_MODEL_DIR"]).expanduser())
    dirs += [
        Path.home() / ".piper" / "models",
        Path.home() / ".local" / "share" / "piper",
        REPO_ROOT / "models" / "piper",
    ]
    return dirs


def resolve_piper_model(model: str) -> Optional[Path]:
    """Resolve a Piper model name or path to an absolute ``.onnx`` file.

    Accepts an explicit path (with or without the ``.onnx`` suffix) or a
    bare voice name such as ``en_US-lessac-medium``. The matching
    ``.onnx.json`` config must sit next to the model, as Piper requires.
    """
    as_path = Path(model).expanduser()
    names = [as_path] if as_path.suffix == ".onnx" else [as_path.with_name(as_path.name + ".onnx")]
    candidates = [n for n in names if n.is_absolute() or n.parent != Path(".")]
    candidates += [d / n.name for d in piper_model_dirs() for n in names]
    candidates += [Path.cwd() / n for n in names]
    for candidate in candidates:
        if candidate.is_file() and Path(str(candidate) + ".json").is_file():
            return candidate.resolve()
    return None
