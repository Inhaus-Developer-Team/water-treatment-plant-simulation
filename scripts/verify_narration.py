#!/usr/bin/env python3
"""
Verification script for Guided Tour British Male Voice Narration
in Municipal WRRF (index.html) and Mobile Treatment System (mobile.html).
"""

import functools
import http.server
import os
import socketserver
import subprocess
import threading
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8089

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=PROJECT_ROOT)
    httpd = ReuseTCPServer(("", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port

def test_audio_files():
    print("=== 1. Checking Narration MP3 Files on Disk ===")
    narration_dir = os.path.join(PROJECT_ROOT, "assets", "audio", "narration")
    expected_files = [
        "muni_stage_01.mp3",
        "muni_stage_02.mp3",
        "muni_stage_03.mp3",
        "muni_stage_04.mp3",
        "muni_stage_05.mp3",
        "muni_stage_06.mp3",
        "mobile_stage_01.mp3",
        "mobile_stage_02.mp3",
        "mobile_stage_03.mp3",
        "mobile_stage_04.mp3"
    ]
    all_ok = True
    for fn in expected_files:
        fp = os.path.join(narration_dir, fn)
        assert os.path.exists(fp), f"Missing audio file: {fn}"
        size = os.path.getsize(fp)
        assert size > 50000, f"File too small ({size} bytes): {fn}"
        # Check duration via afinfo
        afinfo_res = subprocess.check_output(["afinfo", fp]).decode()
        duration_line = [l for l in afinfo_res.splitlines() if "estimated duration" in l][0]
        print(f"  ✓ {fn} ({size:,} bytes) - {duration_line.strip()}")
    print("All 10 narration audio files verified on disk.\n")

def test_pages_in_playwright(port):
    print("=== 2. Testing index.html (Municipal WRRF) in Playwright ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        context = browser.new_context()
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(f"http://localhost:{port}/index.html", wait_until="networkidle")
        time.sleep(2)

        # Check tourStages definition
        stage_0_spoken = page.evaluate("() => window.tourStages[0].spokenText")
        print(f"  Stage 01 spokenText: '{stage_0_spoken[:65]}...'")
        assert "six hundred millimetre" in stage_0_spoken, "Missing 'six hundred millimetre' in stage 0"

        stage_1_spoken = page.evaluate("() => window.tourStages[1].spokenText")
        assert "four hundred and fifty cubic metres per minute" in stage_1_spoken, "Missing cubic metres per min"

        stage_2_spoken = page.evaluate("() => window.tourStages[2].spokenText")
        assert "sixteen metre" in stage_2_spoken, "Missing 'sixteen metre'"
        assert "R A S" in stage_2_spoken, "Missing 'R A S'"

        stage_3_spoken = page.evaluate("() => window.tourStages[3].spokenText")
        assert "ninety-nine point nine percent" in stage_3_spoken, "Missing 'ninety-nine point nine percent'"

        stage_4_spoken = page.evaluate("() => window.tourStages[4].spokenText")
        assert "ninety-nine point four percent" in stage_4_spoken, "Missing 'ninety-nine point four percent'"

        stage_5_spoken = page.evaluate("() => window.tourStages[5].spokenText")
        assert "Stage six" in stage_5_spoken, "Missing 'Stage six'"

        # Click Start Tour
        page.click("#btn-start-tour")
        time.sleep(1.5)

        # Check tour drawer is visible
        drawer_display = page.evaluate("() => document.getElementById('tour-drawer').style.display")
        assert drawer_display == "block", f"Drawer display is {drawer_display}, expected block"
        print("  ✓ Tour drawer opened successfully")

        # Check audio playback
        audio_src = page.evaluate("() => window.getNarrationAudio() ? window.getNarrationAudio().src : null")
        print(f"  ✓ Active Narration Audio Src: {audio_src}")
        assert audio_src and "muni_stage_01.mp3" in audio_src, "Audio src not playing muni_stage_01.mp3"

        playback_rate = page.evaluate("() => window.getNarrationAudio() ? window.getNarrationAudio().playbackRate : null")
        assert playback_rate == 1.0, f"Expected playbackRate 1.0, got {playback_rate}"
        print(f"  ✓ Audio playbackRate: {playback_rate}")

        # Check voice indicator status
        voice_badge_text = page.evaluate("() => document.getElementById('tour-voice-label').textContent")
        print(f"  ✓ Voice Badge Status: {voice_badge_text}")

        # Test Next Tour Stage
        page.click("#btn-tour-next")
        time.sleep(1)
        stage_badge = page.evaluate("() => document.getElementById('tour-badge-stage').textContent")
        assert "02" in stage_badge, f"Expected STAGE 02 in badge, got {stage_badge}"
        audio_src_2 = page.evaluate("() => window.getNarrationAudio() ? window.getNarrationAudio().src : null")
        assert audio_src_2 and "muni_stage_02.mp3" in audio_src_2, "Stage 2 audio not set"
        print(f"  ✓ Stage 2 Active Narration Audio Src: {audio_src_2}")

        print("  ✓ index.html guided tour narration verified.\n")

        print("=== 3. Testing mobile.html (Mobile Wastewater System) in Playwright ===")
        page.goto(f"http://localhost:{port}/mobile.html", wait_until="networkidle")
        time.sleep(2)

        # Check mobile tourStages
        m_stage_0_spoken = page.evaluate("() => window.tourStages[0].spokenText")
        print(f"  Mobile Stage 01 spokenText: '{m_stage_0_spoken[:65]}...'")
        assert "forty-five cubic metre" in m_stage_0_spoken, "Missing 'forty-five cubic metre'"
        assert "P C ten" in m_stage_0_spoken, "Missing 'P C ten'"

        m_stage_1_spoken = page.evaluate("() => window.tourStages[1].spokenText")
        assert "A O P Reactor, Pod One" in m_stage_1_spoken, "Missing 'A O P Reactor, Pod One'"

        m_stage_2_spoken = page.evaluate("() => window.tourStages[2].spokenText")
        assert "twenty to forty micrometre" in m_stage_2_spoken, "Missing 'twenty to forty micrometre'"

        m_stage_3_spoken = page.evaluate("() => window.tourStages[3].spokenText")
        assert "less than zero point six N T U" in m_stage_3_spoken, "Missing 'less than zero point six N T U'"

        # Click Start Tour
        page.click("#btn-start-tour")
        time.sleep(1.5)

        m_drawer_display = page.evaluate("() => document.getElementById('tour-drawer').style.display")
        assert m_drawer_display == "block", f"Mobile drawer display is {m_drawer_display}"
        print("  ✓ Mobile Tour drawer opened successfully")

        m_audio_src = page.evaluate("() => window.getNarrationAudio() ? window.getNarrationAudio().src : null")
        print(f"  ✓ Mobile Active Narration Audio Src: {m_audio_src}")
        assert m_audio_src and "mobile_stage_01.mp3" in m_audio_src, "Mobile audio src not mobile_stage_01.mp3"

        m_playback_rate = page.evaluate("() => window.getNarrationAudio() ? window.getNarrationAudio().playbackRate : null")
        assert m_playback_rate == 1.0, f"Expected playbackRate 1.0, got {m_playback_rate}"
        print(f"  ✓ Mobile Audio playbackRate: {m_playback_rate}")

        # Test Next Tour Stage
        page.click("#btn-tour-next")
        time.sleep(1)
        m_stage_badge = page.evaluate("() => document.getElementById('tour-badge-stage').textContent")
        assert "02" in m_stage_badge, f"Expected STAGE 02 in mobile badge, got {m_stage_badge}"
        m_audio_src_2 = page.evaluate("() => window.getNarrationAudio() ? window.getNarrationAudio().src : null")
        assert m_audio_src_2 and "mobile_stage_02.mp3" in m_audio_src_2, "Mobile stage 2 audio not set"
        print(f"  ✓ Mobile Stage 2 Active Narration Audio Src: {m_audio_src_2}")

        print("  ✓ mobile.html guided tour narration verified.\n")

        browser.close()

def main():
    test_audio_files()
    httpd, port = start_server()
    print(f"Local static server running on http://localhost:{port}")
    try:
        test_pages_in_playwright(port)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    finally:
        httpd.shutdown()

if __name__ == "__main__":
    main()
