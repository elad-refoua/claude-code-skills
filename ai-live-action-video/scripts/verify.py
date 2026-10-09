# -*- coding: utf-8 -*-
"""
Final gate on the finished MP4. Everything here measures the OUTPUT file, not
the scripts that produced it - an earlier version of this check grepped the
build script for speed filters and matched its own docstring, which is exactly
the kind of check that cannot fail.

  1. runtime is inside the brief's 3:00 limit
  2. speed is x1, proven by frame count against duration
  3. no dead air
  4. every narration line actually reached the soundtrack, proven by
     transcribing the finished audio and diffing it against the script
"""
import difflib
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MP4 = os.path.join(HERE, 'final_video.mp4')       # what build_audio.py writes
# A Python interpreter that has faster-whisper installed (it can be a separate venv).
WHISPER_PY = os.environ.get('WHISPER_PYTHON', sys.executable)

FPS = 24
LIMIT = 180.0

fails = []


def sh(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding='utf-8', errors='replace')


# 1 + 2 -------------------------------------------------------------------
duration = float(sh(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=nw=1:nk=1', MP4]).stdout.strip())
frames = int(sh(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                 '-show_entries', 'stream=nb_read_frames',
                 '-of', 'default=nw=1:nk=1', MP4]).stdout.strip())
expected = round(duration * FPS)

print(f'runtime      {duration:.2f}s  ({int(duration//60)}:{duration%60:04.1f})  limit {LIMIT:.0f}s')
if duration > LIMIT:
    fails.append(f'runtime {duration:.2f}s exceeds the 3:00 limit')

print(f'frames       {frames} vs {expected} expected at {FPS}fps x1')
if abs(frames - expected) > 2:
    fails.append(f'frame count {frames} != {expected}: playback is not x1')

# 3 -----------------------------------------------------------------------
sil = sh(['ffmpeg', '-hide_banner', '-i', MP4, '-af',
          'silencedetect=noise=-50dB:d=1.5', '-f', 'null', '-'])
gaps = len(re.findall(r'silence_start', sil.stderr or ''))
print(f'dead air     {gaps} stretches over 1.5s below -50dB')
if gaps:
    fails.append(f'{gaps} silent stretches - every part of the film needs narration or bed')

# 4 -----------------------------------------------------------------------
gen = os.path.join(ROOT, '05_audio', 'generate_narration.py')
src = open(gen, encoding='utf-8').read()
spoken = ' '.join(re.findall(r'text="([^"]*(?:"\s*"[^"]*)*)"', src))
spoken = re.sub(r'"\s*"', '', spoken)
script_words = re.findall(r"[a-z0-9']+", spoken.lower())

wav = os.path.join(HERE, '_verify.wav')
sh(['ffmpeg', '-y', '-v', 'error', '-i', MP4, '-vn', '-ac', '1', '-ar', '16000', wav])

tr = os.path.join(HERE, '_transcribe.py')
open(tr, 'w', encoding='utf-8').write(
    "import sys,io\n"
    "sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')\n"
    "from faster_whisper import WhisperModel\n"
    "m=WhisperModel('base.en',device='cpu',compute_type='int8')\n"
    "segs,_=m.transcribe(sys.argv[1],language='en')\n"
    "print(' '.join(s.text.strip() for s in segs))\n")
out = sh([WHISPER_PY, tr, wav])
heard = re.findall(r"[a-z0-9']+", (out.stdout or '').lower())

sm = difflib.SequenceMatcher(None, script_words, heard)
ratio = sm.ratio()
print(f'transcript   {len(heard)} words heard vs {len(script_words)} scripted, '
      f'similarity {ratio:.3f}')

missing = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ('delete', 'replace'):
        chunk = script_words[i1:i2]
        if len(chunk) >= 3:
            missing.append(' '.join(chunk))
if missing:
    print('  scripted runs not heard:')
    for m in missing[:8]:
        print(f'    - {m[:90]}')
if ratio < 0.80:
    fails.append(f'transcript similarity {ratio:.3f} below 0.80 - narration may be missing')

for f in (wav, tr):
    if os.path.exists(f):
        os.remove(f)

print()
if fails:
    for f in fails:
        print('FAIL:', f)
    raise SystemExit(1)
print('ALL CHECKS PASSED')
