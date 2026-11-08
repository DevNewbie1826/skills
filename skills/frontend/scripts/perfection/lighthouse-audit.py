# Run with: python3 lighthouse-audit.py https://example.com
# Install runtime dependencies with any compatible Python dependency runner, for example:
#   python3 -m pip install playwright
#   python3 -m playwright install chromium
# Node dependencies: lighthouse and chrome-launcher.
# Any compatible dependency runner may be used; python3 is the portable invocation.

"""Lighthouse audit via real Playwright Chrome.

The audit launches Chrome through Playwright and invokes the Lighthouse Node API against
Chrome's CDP port. It intentionally avoids the Lighthouse CLI's headless-shell path.
"""

from __future__ import annotations

import argparse
import importlib
import json
import socket
from statistics import median
import subprocess
import sys
import tempfile
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol, cast


class _Browser(Protocol):
    def close(self) -> None: ...


class _Chromium(Protocol):
    def launch(self, *, channel: str, headless: bool, args: list[str]) -> _Browser: ...


class _Playwright(Protocol):
    chromium: _Chromium


class _PlaywrightModule(Protocol):
    def sync_playwright(self) -> AbstractContextManager[_Playwright]: ...


LIGHTHOUSE_RUNNER_JS = """\
const lighthouse = require('lighthouse');

const url = process.argv[2];
const port = parseInt(process.argv[3], 10);
const preset = process.argv[4];

const config = {
  extends: 'lighthouse:default',
  settings: {
    formFactor: preset === 'desktop' ? 'desktop' : 'mobile',
    throttling: preset === 'desktop'
      ? { rttMs: 40, throughputKbps: 10240, cpuSlowdownMultiplier: 1 }
      : undefined,
    screenEmulation: preset === 'desktop'
      ? { mobile: false, width: 1350, height: 940, deviceScaleFactor: 1 }
      : undefined,
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
  },
};

(async () => {
  const result = await lighthouse(url, { port, logLevel: 'error' }, config);
  const output = {};
  for (const [key, category] of Object.entries(result.lhr.categories)) {
    output[key] = Math.round(category.score * 100);
  }
  console.log(JSON.stringify(output));
})();
"""


def _check_node_deps() -> bool:
    """Return whether the required Node modules are available."""
    result = subprocess.run(
        ["node", "-e", "require('lighthouse'); require('chrome-launcher')"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _node_dependency_hint() -> str:
    return "Install Lighthouse dependencies with your Node package manager: lighthouse and chrome-launcher."


def _playwright_sync() -> Callable[[], AbstractContextManager[_Playwright]]:
    """Load Playwright only when an audit is requested, keeping --help self-contained."""
    try:
        module = importlib.import_module("playwright.sync_api")
    except ModuleNotFoundError as error:
        message = (
            "Playwright is unavailable. Install it with your preferred Python dependency runner, "
            + "then run `python3 -m playwright install chromium`."
        )
        raise RuntimeError(message) from error
    return cast(_PlaywrightModule, cast(object, module)).sync_playwright


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return cast(int, listener.getsockname()[1])


def _run_lighthouse_via_cdp(url: str, cdp_port: int, preset: str) -> dict[str, int]:
    """Run Lighthouse through Chrome's CDP endpoint."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as file:
        _ = file.write(LIGHTHOUSE_RUNNER_JS)
        runner_path = Path(file.name)

    try:
        result = subprocess.run(
            ["node", str(runner_path), url, str(cdp_port), preset],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Lighthouse failed: {result.stderr.strip()}")
        payload = cast(object, json.loads(result.stdout.strip()))
        if not isinstance(payload, dict):
            raise RuntimeError("Lighthouse returned an invalid score payload.")
        scores: dict[str, int] = {}
        for category, score in cast(dict[object, object], payload).items():
            if not isinstance(category, str) or not isinstance(score, int):
                raise RuntimeError("Lighthouse returned non-numeric category scores.")
            scores[category] = score
        return scores
    finally:
        runner_path.unlink(missing_ok=True)


def _run_with_playwright(url: str, preset: str) -> dict[str, int]:
    """Launch real Chrome with Playwright and audit it over CDP."""
    sync_playwright = _playwright_sync()
    cdp_port = _free_local_port()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=True,
            args=[f"--remote-debugging-port={cdp_port}"],
        )
        try:
            return _run_lighthouse_via_cdp(url, cdp_port, preset)
        finally:
            browser.close()


def _median_scores(score_runs: list[dict[str, int]]) -> dict[str, float]:
    """Return per-category medians from Lighthouse JSON score payloads."""
    if not score_runs:
        raise RuntimeError("Lighthouse did not return any score payloads.")

    categories = set(score_runs[0])
    if any(set(scores) != categories for scores in score_runs[1:]):
        raise RuntimeError("Lighthouse returned inconsistent categories across runs.")

    return {
        category: float(median([scores[category] for scores in score_runs]))
        for category in score_runs[0]
    }


def _run_preset(url: str, preset: str, runs: int) -> dict[str, float]:
    """Run one preset repeatedly and return its per-category medians."""
    print(f"Auditing {preset}: {url} ({runs} runs)")
    score_runs: list[dict[str, int]] = []
    for run_number in range(1, runs + 1):
        print(f"  Run {run_number}/{runs}")
        score_runs.append(_run_with_playwright(url, preset))
    return _median_scores(score_runs)


def _print_scores(scores: dict[str, float], preset: str, threshold: int, runs: int) -> bool:
    """Print per-category medians and return whether they meet the threshold."""
    label = f"{preset} median ({runs} runs)"
    if threshold != 100:
        label += f"; diagnostic threshold {threshold}"
    print(f"\nLighthouse - {label}")

    all_at_threshold = True
    for category, score in scores.items():
        at_threshold = score >= threshold
        all_at_threshold = all_at_threshold and at_threshold
        if threshold == 100:
            status = "PASS" if at_threshold else "FAIL"
        else:
            status = "AT/ABOVE" if at_threshold else "BELOW"
        print(f"  {category:16} {score:5g} {status}")
    return all_at_threshold


def run_audit(
    url: str, threshold: int, desktop_only: bool, mobile_only: bool, runs: int = 3
) -> int:
    if not _check_node_deps():
        print(_node_dependency_hint(), file=sys.stderr)
        return 2

    all_at_threshold = True
    try:
        if not desktop_only:
            mobile_scores = _run_preset(url, "mobile", runs)
            all_at_threshold = _print_scores(mobile_scores, "Mobile", threshold, runs) and all_at_threshold

        if not mobile_only:
            desktop_scores = _run_preset(url, "desktop", runs)
            all_at_threshold = _print_scores(desktop_scores, "Desktop", threshold, runs) and all_at_threshold
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        print(f"Audit could not run: {error}", file=sys.stderr)
        return 2

    if all_at_threshold:
        if threshold == 100:
            print("\nAll categories passed.")
        else:
            print(
                f"\nAll categories met the diagnostic threshold of {threshold}; this is not a passing audit."
            )
        return 0

    if threshold == 100:
        message = "Some categories are below 100. Not done yet."
    else:
        message = f"Some categories are below diagnostic threshold {threshold}. Not done yet."
    print(f"\n{message}", file=sys.stderr)
    return 1


def _positive_int(value: str) -> int:
    runs = int(value)
    if runs < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return runs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a real-browser Lighthouse audit.")
    _ = parser.add_argument("url", help="URL to audit")
    _ = parser.add_argument(
        "--threshold",
        "-t",
        type=int,
        default=100,
        help="Diagnostic score threshold; only 100 establishes a passing audit",
    )
    _ = parser.add_argument(
        "--runs",
        type=_positive_int,
        default=3,
        metavar="N",
        help="Audits per preset; report per-category medians (default: 3)",
    )
    _ = parser.add_argument("--desktop-only", action="store_true", help="Skip the mobile audit")
    _ = parser.add_argument("--mobile-only", action="store_true", help="Skip the desktop audit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    desktop_only = cast(bool, args.desktop_only)
    mobile_only = cast(bool, args.mobile_only)
    if desktop_only and mobile_only:
        print("Choose at most one of --desktop-only and --mobile-only.", file=sys.stderr)
        return 2
    return run_audit(
        cast(str, args.url),
        cast(int, args.threshold),
        desktop_only,
        mobile_only,
        cast(int, args.runs),
    )


if __name__ == "__main__":
    raise SystemExit(main())
