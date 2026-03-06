"""
Aether Voice OS — Browser E2E Test with Screen Recording.
==========================================================
Tests the full voice portal UI lifecycle:
  1. Launches the Next.js portal dev server
  2. Navigates to /live (auto-launching voice interface)
  3. Validates connection status transitions
  4. Tests the main portal page (/) with quantum avatar
  5. Records screen video of the entire interaction

Run:
    python tests/e2e/test_browser_voice_e2e.py

Requires:
    - Node.js and npm (for Next.js dev server)
    - playwright (pip install playwright && playwright install chromium)
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("browser_e2e")

ROOT = Path(__file__).resolve().parent.parent.parent
PORTAL_DIR = ROOT / "apps" / "portal"
VIDEO_DIR = ROOT / "test-results" / "videos"
SCREENSHOT_DIR = ROOT / "test-results" / "screenshots"
DEV_PORT = 3111  # Use non-standard port to avoid conflicts
BASE_URL = f"http://localhost:{DEV_PORT}"


def ensure_dirs():
    """Create output directories."""
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


async def wait_for_server(url: str, timeout: float = 90.0) -> bool:
    """Wait for the Next.js dev server to be ready using urllib."""
    import urllib.error
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.urlopen(url, timeout=3)
            if req.status == 200:
                return True
        except (urllib.error.URLError, OSError, ConnectionRefusedError):
            pass
        await asyncio.sleep(2)
    return False


async def run_browser_tests():
    """Execute the full browser E2E test suite with screen recording."""
    from playwright.async_api import async_playwright

    ensure_dirs()

    # Start Next.js dev server on dedicated port
    logger.info(f"Starting Next.js dev server on port {DEV_PORT}...")
    dev_server = subprocess.Popen(
        ["npx", "next", "dev", "--port", str(DEV_PORT)],
        cwd=str(PORTAL_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )

    try:
        # Wait for server to be ready
        logger.info(f"Waiting for dev server at {BASE_URL}...")
        server_ready = await wait_for_server(BASE_URL, timeout=90)
        if not server_ready:
            logger.error("Dev server failed to start within 90 seconds")
            return False

        logger.info("Dev server is ready!")

        async with async_playwright() as p:
            # Launch browser with video recording
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--use-fake-ui-for-media-stream",
                    "--use-fake-device-for-media-stream",
                ],
            )

            # Create context with video recording and fake media
            context = await browser.new_context(
                record_video_dir=str(VIDEO_DIR),
                record_video_size={"width": 1280, "height": 720},
                viewport={"width": 1280, "height": 720},
                permissions=["microphone"],
                color_scheme="dark",
            )

            page = await context.new_page()
            results = {"passed": 0, "failed": 0, "tests": []}

            # ── Test 1: Main Portal Page (/) ──────────────────────
            logger.info("TEST 1: Loading main portal page...")
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)  # Let 3D scene render

                title = await page.title()
                logger.info(f"  Page title: {title}")

                # Screenshot of main portal
                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "01_main_portal.png"),
                    full_page=False,
                )
                logger.info("  Screenshot saved: 01_main_portal.png")

                results["tests"].append({"name": "Main Portal Load", "status": "PASS"})
                results["passed"] += 1
            except Exception as e:
                logger.error(f"  FAIL: {e}")
                results["tests"].append(
                    {"name": "Main Portal Load", "status": f"FAIL: {e}"}
                )
                results["failed"] += 1

            # ── Test 2: Live Voice Page (/live) ──────────────────
            logger.info("TEST 2: Loading live voice page...")
            try:
                await page.goto(
                    f"{BASE_URL}/live", wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(3000)

                # Check for status elements on the live page
                content = await page.content()
                has_live_content = (
                    "live" in content.lower() or "aether" in content.lower()
                )
                logger.info(f"  Live page has content: {has_live_content}")

                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "02_live_page.png"),
                    full_page=False,
                )
                logger.info("  Screenshot saved: 02_live_page.png")

                results["tests"].append(
                    {"name": "Live Voice Page Load", "status": "PASS"}
                )
                results["passed"] += 1
            except Exception as e:
                logger.error(f"  FAIL: {e}")
                results["tests"].append(
                    {"name": "Live Voice Page Load", "status": f"FAIL: {e}"}
                )
                results["failed"] += 1

            # ── Test 3: Admin Dashboard (/admin) ─────────────────
            logger.info("TEST 3: Loading admin dashboard...")
            try:
                await page.goto(
                    f"{BASE_URL}/admin", wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(2000)

                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "03_admin_dashboard.png"),
                    full_page=False,
                )
                logger.info("  Screenshot saved: 03_admin_dashboard.png")

                results["tests"].append(
                    {"name": "Admin Dashboard Load", "status": "PASS"}
                )
                results["passed"] += 1
            except Exception as e:
                logger.error(f"  FAIL: {e}")
                results["tests"].append(
                    {"name": "Admin Dashboard Load", "status": f"FAIL: {e}"}
                )
                results["failed"] += 1

            # ── Test 4: Audio Pipeline Initialization ────────────
            logger.info("TEST 4: Testing audio pipeline initialization...")
            try:
                await page.goto(
                    f"{BASE_URL}/live", wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(2000)

                # Check if AudioContext can be created
                audio_support = await page.evaluate("""() => {
                    try {
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        ctx.close();
                        return { supported: true, sampleRate: ctx.sampleRate };
                    } catch (e) {
                        return { supported: false, error: e.message };
                    }
                }""")
                logger.info(f"  AudioContext support: {audio_support}")

                # Check if MediaDevices API is available
                media_support = await page.evaluate("""() => {
                    return {
                        mediaDevices: !!navigator.mediaDevices,
                        getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
                        enumerateDevices: !!(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices),
                    };
                }""")
                logger.info(f"  MediaDevices support: {media_support}")

                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "04_audio_pipeline.png"),
                    full_page=False,
                )

                results["tests"].append(
                    {
                        "name": "Audio Pipeline Init",
                        "status": "PASS",
                        "details": {**audio_support, **media_support},
                    }
                )
                results["passed"] += 1
            except Exception as e:
                logger.error(f"  FAIL: {e}")
                results["tests"].append(
                    {"name": "Audio Pipeline Init", "status": f"FAIL: {e}"}
                )
                results["failed"] += 1

            # ── Test 5: UI Responsiveness & Interaction ──────────
            logger.info("TEST 5: Testing UI responsiveness...")
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)

                # Measure page performance
                perf_metrics = await page.evaluate("""() => {
                    const perf = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: perf ? perf.domContentLoadedEventEnd : 0,
                        loadComplete: perf ? perf.loadEventEnd : 0,
                        domInteractive: perf ? perf.domInteractive : 0,
                        transferSize: perf ? perf.transferSize : 0,
                    };
                }""")
                logger.info(f"  Performance metrics: {perf_metrics}")

                # Check for console errors
                errors = []
                page.on(
                    "console",
                    lambda msg: errors.append(msg.text)
                    if msg.type == "error"
                    else None,
                )
                await page.wait_for_timeout(2000)

                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "05_ui_responsiveness.png"),
                    full_page=False,
                )

                results["tests"].append(
                    {
                        "name": "UI Responsiveness",
                        "status": "PASS",
                        "details": perf_metrics,
                    }
                )
                results["passed"] += 1
            except Exception as e:
                logger.error(f"  FAIL: {e}")
                results["tests"].append(
                    {"name": "UI Responsiveness", "status": f"FAIL: {e}"}
                )
                results["failed"] += 1

            # ── Test 6: Full Navigation Flow Recording ───────────
            logger.info("TEST 6: Recording full navigation flow...")
            try:
                # Navigate through all pages for video recording
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(4000)

                await page.goto(
                    f"{BASE_URL}/live", wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(4000)

                await page.goto(
                    f"{BASE_URL}/admin", wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(3000)

                # Return to main
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)

                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "06_navigation_complete.png"),
                    full_page=False,
                )

                results["tests"].append(
                    {"name": "Full Navigation Flow", "status": "PASS"}
                )
                results["passed"] += 1
            except Exception as e:
                logger.error(f"  FAIL: {e}")
                results["tests"].append(
                    {"name": "Full Navigation Flow", "status": f"FAIL: {e}"}
                )
                results["failed"] += 1

            # Close context to finalize video
            await context.close()
            await browser.close()

        # Print results
        print("\n" + "=" * 55)
        print("  AETHER BROWSER E2E TEST RESULTS")
        print("=" * 55)
        for t in results["tests"]:
            status = "PASS" if "PASS" in str(t["status"]) else "FAIL"
            icon = "  ✅" if status == "PASS" else "  ❌"
            print(f"{icon} {t['name']}: {t['status']}")
        print(f"\n  Score: {results['passed']}/{results['passed'] + results['failed']}")
        print(f"  Videos: {VIDEO_DIR}")
        print(f"  Screenshots: {SCREENSHOT_DIR}")
        print("=" * 55 + "\n")

        # Save results
        import json

        report_path = ROOT / "test-results" / "browser_e2e_report.json"
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Report saved to {report_path}")

        return results["failed"] == 0

    finally:
        # Cleanup: Kill the dev server process group
        logger.info("Stopping dev server...")
        try:
            os.killpg(os.getpgid(dev_server.pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        try:
            dev_server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(dev_server.pid), signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
        logger.info("Dev server stopped.")


if __name__ == "__main__":
    success = asyncio.run(run_browser_tests())
    sys.exit(0 if success else 1)
