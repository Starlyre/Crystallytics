"""
record_showcase.py

Automated 1080p/720p Screen Recording of Crystallytics using Playwright + Chrome.
Records the ACTUAL web application with real Chart.js animations, realistic cursor,
tab switching, and 1-click data cleaning in action.
"""

import sys
import os
import time
import shutil
import threading
import http.server
import socketserver
import subprocess

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

PORT = 8765
DOC_ROOT = os.path.dirname(os.path.abspath(__file__))
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_MP4 = os.path.join(DOC_ROOT, "crystallytics_showcase.mp4")
RAW_DIR = os.path.join(DOC_ROOT, "raw_recording")


class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOC_ROOT, **kwargs)

    def log_message(self, format, *args):
        pass


def inject_virtual_cursor(page):
    """Injects a sleek glowing virtual cursor overlay that tracks mouse events."""
    js = """
    (() => {
        if (document.getElementById('virtual-cursor')) return;
        const cursor = document.createElement('div');
        cursor.id = 'virtual-cursor';
        cursor.style.cssText = `
            position: fixed;
            top: 0; left: 0;
            width: 20px; height: 20px;
            background: rgba(14, 165, 233, 0.9);
            border: 2px solid #ffffff;
            border-radius: 50%;
            pointer-events: none;
            z-index: 2147483647;
            box-shadow: 0 0 14px rgba(56, 189, 248, 0.9), 0 0 2px rgba(0,0,0,0.5);
            transition: transform 0.1s cubic-bezier(0.2, 0.9, 0.3, 1), background 0.15s ease;
            transform: translate(-50%, -50%);
        `;
        document.body.appendChild(cursor);

        window.addEventListener('mousemove', e => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        window.addEventListener('mousedown', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(0.65)';
            cursor.style.background = 'rgba(16, 185, 129, 0.95)';
            cursor.style.boxShadow = '0 0 20px rgba(16, 185, 129, 1)';
        });

        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.background = 'rgba(14, 165, 233, 0.9)';
            cursor.style.boxShadow = '0 0 14px rgba(56, 189, 248, 0.9)';
        });
    })();
    """
    page.evaluate(js)


def switch_tab(page, tab_id, steps=20, wait_after=0.8):
    """Smoothly moves virtual cursor to tab button, clicks it, and ensures tab pane activates."""
    # Ensure tab navigation bar is visible
    page.evaluate("window.scrollTo({top: 220, behavior: 'smooth'})")
    time.sleep(0.4)

    btn = page.locator(f"button[data-tab='{tab_id}']")
    box = btn.bounding_box()
    if box:
        cx = box['x'] + box['width'] / 2
        cy = box['y'] + box['height'] / 2
        page.mouse.move(cx, cy, steps=steps)
        time.sleep(0.15)
    btn.click()
    page.wait_for_selector(f"#{tab_id}.active", timeout=5000)
    time.sleep(wait_after)


def click_action(page, selector, steps=18, wait_after=1.0):
    """Smoothly moves virtual cursor to an element, ensures it is in view, and clicks it."""
    loc = page.locator(selector)
    loc.scroll_into_view_if_needed()
    time.sleep(0.3)
    box = loc.bounding_box()
    if box:
        cx = box['x'] + box['width'] / 2
        cy = box['y'] + box['height'] / 2
        page.mouse.move(cx, cy, steps=steps)
        time.sleep(0.15)
    loc.click()
    time.sleep(wait_after)


def smooth_scroll(page, delta_y, steps=18, delay=0.035):
    """Performs a human-like smooth scroll."""
    step = delta_y / steps
    for _ in range(steps):
        page.evaluate(f"window.scrollBy(0, {step})")
        time.sleep(delay)


def run_recording():
    print("[1/5] Starting local HTTP server on port", PORT)
    server = socketserver.TCPServer(('127.0.0.1', PORT), SilentHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    os.makedirs(RAW_DIR, exist_ok=True)
    for f in os.listdir(RAW_DIR):
        try:
            os.remove(os.path.join(RAW_DIR, f))
        except Exception:
            pass

    print("[2/5] Launching Chrome via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--enable-font-antialiasing", "--disable-gpu-vsync"]
        )

        context = browser.new_context(
            record_video_dir=RAW_DIR,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1.0,
        )

        page = context.new_page()

        # ── SCENE 1: Modern Animated Intro (3.5s) ──
        print("  -> Recording Scene 1: Modern Branded Intro...")
        page.goto(f"http://127.0.0.1:{PORT}/showcase_intro.html")
        page.wait_for_timeout(3500)

        # ── SCENE 2: Real App Landing & Ingestion (5s) ──
        print("  -> Recording Scene 2: Live App Landing & Dataset Ingestion...")
        page.goto(f"http://127.0.0.1:{PORT}/index.html")
        page.wait_for_load_state("networkidle")
        inject_virtual_cursor(page)
        page.mouse.move(640, 360, steps=15)
        page.wait_for_timeout(1000)

        # Move to 'Load Sample Sales Data' button and click
        click_action(page, "#btn-demo", steps=24, wait_after=1.8)

        # ── SCENE 3: Top Health Metrics & Inferred Domain (4s) ──
        print("  -> Recording Scene 3: Top Health Metrics & Context Inference...")
        # Hover over Health Metrics
        metric_box = page.query_selector(".metrics-grid").bounding_box()
        if metric_box:
            page.mouse.move(metric_box['x'] + 100, metric_box['y'] + 40, steps=18)
            page.wait_for_timeout(600)
            page.mouse.move(metric_box['x'] + 300, metric_box['y'] + 40, steps=18)
            page.wait_for_timeout(600)
            page.mouse.move(metric_box['x'] + 600, metric_box['y'] + 40, steps=18)
            page.wait_for_timeout(1000)

        # ── SCENE 4: Tab 1 — AI Executive Narrative (6s) ──
        print("  -> Recording Scene 4: Tab 1 AI Executive Narrative...")
        smooth_scroll(page, 320, steps=16, delay=0.03)
        page.wait_for_timeout(1800)
        smooth_scroll(page, 280, steps=16, delay=0.03)
        page.wait_for_timeout(1800)
        smooth_scroll(page, -600, steps=16, delay=0.02)
        page.wait_for_timeout(600)

        # ── SCENE 5: Tab 2 — Automated Visualizations with Chart.js (8s) ──
        print("  -> Recording Scene 5: Tab 2 Context-Aware Visualizations...")
        switch_tab(page, "tab-viz", steps=20, wait_after=2.0)
        # Hover over line chart to show tooltip
        canvas1 = page.query_selector("#charts-container canvas")
        if canvas1:
            cbox = canvas1.bounding_box()
            if cbox:
                page.mouse.move(cbox['x'] + cbox['width'] * 0.35, cbox['y'] + cbox['height'] * 0.45, steps=18)
                page.wait_for_timeout(700)
                page.mouse.move(cbox['x'] + cbox['width'] * 0.65, cbox['y'] + cbox['height'] * 0.35, steps=18)
                page.wait_for_timeout(700)
                page.mouse.move(cbox['x'] + cbox['width'] * 0.85, cbox['y'] + cbox['height'] * 0.25, steps=18)
                page.wait_for_timeout(900)

        smooth_scroll(page, 420, steps=18, delay=0.03)
        page.wait_for_timeout(2000)
        smooth_scroll(page, -420, steps=16, delay=0.02)
        page.wait_for_timeout(600)

        # ── SCENE 6: Tab 4 — 1-Click Data Cleaning Engine (7s) ──
        print("  -> Recording Scene 6: Tab 4 1-Click Data Cleaning Engine...")
        switch_tab(page, "tab-cleaner", steps=20, wait_after=1.2)
        smooth_scroll(page, 150, steps=12, delay=0.03)
        page.wait_for_timeout(800)

        # Click Apply Cleaning Recipe
        click_action(page, "#btn-apply-cleaning", steps=18, wait_after=1.8)
        # Highlight the green audit results card
        smooth_scroll(page, 200, steps=14, delay=0.03)
        page.wait_for_timeout(2200)
        smooth_scroll(page, -350, steps=16, delay=0.02)
        page.wait_for_timeout(600)

        # ── SCENE 7: Tab 3 — Data Health & Profiling Table (5s) ──
        print("  -> Recording Scene 7: Tab 3 Data Health & Profiling Table...")
        switch_tab(page, "tab-profile", steps=20, wait_after=1.2)
        smooth_scroll(page, 300, steps=15, delay=0.03)
        page.wait_for_timeout(1800)
        smooth_scroll(page, -300, steps=15, delay=0.02)
        page.wait_for_timeout(600)

        # ── SCENE 8: Tab 5 — Custom Explorer (4s) ──
        print("  -> Recording Scene 8: Tab 5 Custom Distribution Explorer...")
        switch_tab(page, "tab-explorer", steps=20, wait_after=1.0)
        # Select customer rating from dropdown
        page.select_option("#select-custom-col", "Customer Rating")
        page.wait_for_timeout(1600)
        page.select_option("#select-custom-col", "Units Sold")
        page.wait_for_timeout(2000)

        # ── SCENE 9: Modern Outro & Call to Action (4.5s) ──
        print("  -> Recording Scene 9: Outro & Call to Action...")
        page.goto(f"http://127.0.0.1:{PORT}/showcase_outro.html")
        page.wait_for_timeout(4500)

        print("[3/5] Finalizing video recording session...")
        context.close()
        browser.close()

    server.shutdown()

    # Convert .webm to MP4 using ffmpeg
    print("[4/5] Converting raw webm recording to crisp MP4...")
    webm_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".webm")]
    if not webm_files:
        raise RuntimeError("No recorded video found in " + RAW_DIR)

    raw_video = os.path.join(RAW_DIR, webm_files[0])
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # ffmpeg conversion with high quality H.264
    cmd = [
        ffmpeg_exe, "-y",
        "-i", raw_video,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        OUTPUT_MP4
    ]

    subprocess.run(cmd, check=True)

    size_mb = os.path.getsize(OUTPUT_MP4) / (1024 * 1024)
    print(f"[5/5] SUCCESS! Showcase video ready at: {OUTPUT_MP4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    run_recording()
