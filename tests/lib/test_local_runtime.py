"""Tests for lib.local_runtime — local browser / GSAP / Piper resolution.

Filesystem-only: no browsers are launched and nothing is downloaded.
"""

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib import local_runtime
from lib.local_runtime import (
    GSAP_CDN_URL,
    browser_env,
    resolve_browser_executable,
    resolve_gsap_path,
    resolve_piper_model,
    stage_gsap,
)


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    for var in (
        "OPENMONTAGE_BROWSER_EXECUTABLE",
        "REMOTION_BROWSER_EXECUTABLE",
        "HYPERFRAMES_BROWSER_PATH",
        "OPENMONTAGE_GSAP_PATH",
        "PIPER_MODEL_DIR",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path / "no-browsers"))
    monkeypatch.setenv("OPENMONTAGE_VENDOR_DIR", str(tmp_path / "no-vendor"))
    monkeypatch.setattr(local_runtime, "REPO_ROOT", tmp_path / "repo")
    monkeypatch.setattr(local_runtime.shutil, "which", lambda name: None)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return tmp_path


def _make_exe(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n")
    path.chmod(0o755)
    return path


def test_browser_none_when_nothing_installed(clean_env):
    assert resolve_browser_executable() is None
    assert "HYPERFRAMES_BROWSER_PATH" not in browser_env({})


def test_browser_env_var_wins(clean_env, monkeypatch):
    exe = _make_exe(clean_env / "bin" / "chrome")
    monkeypatch.setenv("REMOTION_BROWSER_EXECUTABLE", str(exe))
    assert resolve_browser_executable() == str(exe.resolve())


def test_browser_prefers_playwright_headless_shell(clean_env, monkeypatch):
    root = clean_env / "pw"
    _make_exe(root / "chromium-1194" / "chrome-linux" / "chrome")
    shell = _make_exe(root / "chromium_headless_shell-1194" / "chrome-linux" / "headless_shell")
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(root))
    assert resolve_browser_executable() == str(shell.resolve())
    env = browser_env({})
    assert env["HYPERFRAMES_BROWSER_PATH"] == str(shell.resolve())
    assert env["REMOTION_BROWSER_EXECUTABLE"] == str(shell.resolve())


def test_gsap_falls_back_to_cdn(clean_env):
    assert resolve_gsap_path() is None
    assert stage_gsap(clean_env / "ws") == GSAP_CDN_URL
    assert not (clean_env / "ws").exists()


def test_gsap_vendored_copy_is_staged(clean_env, monkeypatch):
    vendor = clean_env / "vendor"
    gsap = vendor / "node_modules" / "gsap" / "dist" / "gsap.min.js"
    gsap.parent.mkdir(parents=True)
    gsap.write_text("/* gsap */")
    monkeypatch.setenv("OPENMONTAGE_VENDOR_DIR", str(vendor))
    src = stage_gsap(clean_env / "ws")
    assert src == "assets/vendor/gsap.min.js"
    assert (clean_env / "ws" / src).read_text() == "/* gsap */"


def _make_voice(directory: Path, name: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    model = directory / f"{name}.onnx"
    model.write_bytes(b"onnx")
    Path(str(model) + ".json").write_text("{}")
    return model


def test_piper_model_resolved_from_model_dir(clean_env, monkeypatch):
    model = _make_voice(clean_env / "voices", "en_US-lessac-medium")
    monkeypatch.setenv("PIPER_MODEL_DIR", str(clean_env / "voices"))
    assert resolve_piper_model("en_US-lessac-medium") == model.resolve()
    assert resolve_piper_model(str(model)) == model.resolve()


def test_piper_model_requires_config(clean_env, monkeypatch):
    voices = clean_env / "voices"
    voices.mkdir()
    (voices / "en_US-lessac-medium.onnx").write_bytes(b"onnx")
    monkeypatch.setenv("PIPER_MODEL_DIR", str(voices))
    assert resolve_piper_model("en_US-lessac-medium") is None


def test_piper_model_missing_returns_none(clean_env):
    assert resolve_piper_model("en_US-lessac-medium") is None
