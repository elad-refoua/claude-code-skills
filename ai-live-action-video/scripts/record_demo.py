# -*- coding: utf-8 -*-
"""
Record a genuine screen capture of the web app being demonstrated.

Playwright drives a real Chromium at 1920x1080 and records video of the page,
so every frame is the actual application doing actual work - a real upload, a
real GPT-5.4 call, a real confidence score. Nothing is mocked or re-created.

The selectors and placeholder text below belong to the worked example (an image
question-answering prototype); adapt them to your own app. Set DEMO_APP_URL.

Two deliberate constraints. Read the app's own code before filming:

* **Never click navigation links the app has not implemented.** A 404 on camera
  undoes the demo.
* **Never rest on a panel whose numbers are placeholders** (for example, values
  from `Math.random()`). Scroll past it at reading speed and say so in the
  closing card. Below, the capture scrolls from the confidence badge past such
  a panel to the full analysis, which is genuine model output.

Usage:  py record_demo.py <image> <out-stem> "<question>"
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.environ.get('DEMO_APP_URL', '<YOUR_APP_URL>')
if APP.startswith('<'):
    raise SystemExit('Set DEMO_APP_URL to the address of the app to record.')

image = sys.argv[1]
stem = sys.argv[2]
question = sys.argv[3] if len(sys.argv) > 3 else \
    'Identify this muscle and mention its primary clinical function.'

raw = os.path.join(HERE, '_raw_' + stem)
os.makedirs(raw, exist_ok=True)


def settle(page, ms):
    page.wait_for_timeout(ms)


with sync_playwright() as p:
    browser = p.chromium.launch(args=['--hide-scrollbars', '--force-device-scale-factor=1'])
    ctx = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        device_scale_factor=1,
        record_video_dir=raw,
        record_video_size={'width': 1920, 'height': 1080},
    )
    page = ctx.new_page()

    page.goto(APP, wait_until='networkidle')
    settle(page, 2200)                                   # let the empty state read

    # --- upload ------------------------------------------------------------
    page.locator('input[type=file]').first.set_input_files(image)
    settle(page, 2600)                                   # "IMAGE LOADED"

    # --- ask ---------------------------------------------------------------
    box = page.get_by_placeholder('Ask about the anatomical structure shown…')
    box.click()
    box.type(question, delay=55)                         # typed at human speed
    settle(page, 1200)

    page.get_by_role('button', name='Submit Query').click()
    settle(page, 1800)                                   # the ANALYZING state

    # --- wait for the real answer -----------------------------------------
    page.wait_for_selector('text=OVERALL CONFIDENCE', timeout=120000)
    for _ in range(120):
        txt = page.inner_text('body')
        if 'CALCULATING' not in txt and 'GENERATING ANALYSIS' not in txt:
            break
        page.wait_for_timeout(1000)
    settle(page, 2500)                                   # hold on the score

    # --- the tour -----------------------------------------------------------
    # Nothing is hidden or removed: the capture shows the page as it really is.
    # A panel that shows placeholder numbers is passed at natural reading speed,
    # the way a user scrolling would, rather than held on, and the closing card
    # discloses it.
    page.evaluate("""() => {
      const el = [...document.querySelectorAll('*')]
        .find(e => e.textContent.trim().startsWith('OVERALL CONFIDENCE'));
      if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
    }""")
    settle(page, 3000)

    # continuous glide down through the placeholder panel to the genuine analysis
    for _ in range(9):
        page.mouse.wheel(0, 200)
        settle(page, 260)

    page.evaluate("""() => {
      const el = [...document.querySelectorAll('*')]
        .find(e => e.children.length === 0 && e.textContent.trim() === 'FULL ANALYSIS');
      if (el) el.scrollIntoView({behavior:'smooth', block:'start'});
    }""")
    settle(page, 3500)

    # slow read down the genuine analysis text
    for _ in range(6):
        page.mouse.wheel(0, 260)
        settle(page, 1100)

    # --- speak it ----------------------------------------------------------
    try:
        page.get_by_role('button', name='Speak Response').click()
        settle(page, 4000)
    except Exception as e:
        print('speak button not clicked:', e)

    settle(page, 1200)
    ctx.close()
    browser.close()

# Playwright names the file by an internal id; there is exactly one.
webm = [f for f in os.listdir(raw) if f.endswith('.webm')]
if not webm:
    print('NO VIDEO PRODUCED')
    raise SystemExit(1)
src = os.path.join(raw, webm[0])
print('raw capture:', src, os.path.getsize(src) // 1024, 'KB')
print('OK')
