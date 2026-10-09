# -*- coding: utf-8 -*-
"""Render slides.html to 1920x1080 PNGs.

Gate values are substituted into slide 7 at render time from argv, so the film
shows the numbers its own verify run actually produced rather than a guess.
Usage:  render_slides_with_gates.py [states...] [--gates G1 G2 G3 G4]
"""
import os
import re
import shutil
import sys
import tempfile
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

argv = sys.argv[1:]
gates = ['—'] * 4
if '--gates' in argv:
    i = argv.index('--gates')
    gates = (argv[i + 1:i + 5] + gates)[:4]
    argv = argv[:i]
states = argv or ['1', '5', '6', '7', '8']

src = open(os.path.join(HERE, 'slides.html'), encoding='utf-8').read()
for n, v in enumerate(gates, 1):
    src = src.replace(f'__G{n}__', v)

tmp = os.path.join(tempfile.gettempdir(), '_slides_render.html')
open(tmp, 'w', encoding='utf-8').write(src)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    url = 'file:///' + tmp.replace(os.sep, '/')
    for s in states:
        pg.goto(f'{url}?s={s}', wait_until='networkidle')
        pg.wait_for_timeout(1200)
        out = os.path.join(HERE, f'slide_{s}.png')
        pg.screenshot(path=out)
        print(f'slide_{s}.png  {os.path.getsize(out)//1024} KB')
    b.close()
os.remove(tmp)
