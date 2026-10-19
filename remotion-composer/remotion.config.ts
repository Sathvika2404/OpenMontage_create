import fs from "node:fs";
import path from "node:path";
import { Config } from "@remotion/cli/config";

// Local browser override for sandboxed / offline environments.
//
// By default Remotion downloads chrome-headless-shell on first render. Where
// that download is blocked (e.g. Claude Code cloud sessions), use a
// pre-installed binary instead. Resolution order:
//
//   1. REMOTION_BROWSER_EXECUTABLE (written to .env.local-runtime by
//      scripts/setup_cloud_env.sh)
//   2. Playwright's chrome-headless-shell under PLAYWRIGHT_BROWSERS_PATH
//
// When neither exists, Remotion's default download behavior is unchanged.
// Keep in sync with lib/local_runtime.py:resolve_browser_executable().
const findPlaywrightHeadlessShell = (): string | null => {
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH;
  if (!root || !fs.existsSync(root)) {
    return null;
  }
  const builds = fs
    .readdirSync(root)
    .filter((name) => name.startsWith("chromium_headless_shell-"))
    .sort()
    .reverse();
  for (const build of builds) {
    for (const platformDir of ["chrome-linux", "chrome-linux64"]) {
      const candidate = path.join(root, build, platformDir, "headless_shell");
      if (fs.existsSync(candidate)) {
        return candidate;
      }
    }
  }
  return null;
};

const browserExecutable =
  process.env.REMOTION_BROWSER_EXECUTABLE || findPlaywrightHeadlessShell();
if (browserExecutable) {
  Config.setBrowserExecutable(browserExecutable);
}

// "headless-shell" (default) for chrome-headless-shell binaries;
// "chrome-for-testing" when the executable is a full Chrome/Chromium build.
const chromeMode = process.env.REMOTION_CHROME_MODE;
if (chromeMode === "headless-shell" || chromeMode === "chrome-for-testing") {
  Config.setChromeMode(chromeMode);
}
