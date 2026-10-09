# -*- coding: utf-8 -*-
"""Generate a still with Google's Gemini image model (Nano Banana 2).

Writes a `<file>.prompt.json` sidecar next to the image: in a film about AI
models, the sidecar IS the evidence that a model was called and what it was told.

Needs GEMINI_API_KEY in the environment.

Usage:  gen_gemini_image.py "<prompt>" <out.png>
"""
import base64
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

MODEL = 'gemini-3.1-flash-image-preview'
API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    raise SystemExit('Set GEMINI_API_KEY in the environment.')

prompt, out = sys.argv[1], sys.argv[2]
url = (f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}'
       f':generateContent')
payload = {'contents': [{'parts': [{'text': prompt}]}],
           'generationConfig': {'responseModalities': ['IMAGE']}}

# The key goes in a header, never in the URL, so it stays out of proxy logs and tracebacks.
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                             headers={'Content-Type': 'application/json',
                                      'x-goog-api-key': API_KEY})
with urllib.request.urlopen(req, timeout=300) as r:
    d = json.loads(r.read().decode())

if 'candidates' not in d:
    fb = d.get('promptFeedback', {})
    raise SystemExit('BLOCKED: ' + str(fb.get('blockReason', fb or d.keys())))

data = None
for part in d['candidates'][0]['content']['parts']:
    if 'inlineData' in part:
        data = base64.b64decode(part['inlineData']['data'])
        break
if not data:
    raise SystemExit('no image in response')

open(out, 'wb').write(data)
json.dump({'prompt': prompt, 'model': MODEL,
           'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
           'generated_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
          open(out + '.prompt.json', 'w', encoding='utf-8'), indent=2)
print(f'{out}  {len(data)//1024} KB  ({MODEL})')
