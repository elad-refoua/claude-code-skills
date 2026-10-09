# -*- coding: utf-8 -*-
"""
Strip trailing artefacts from generated narration.

Gemini TTS sometimes appends a fragment AFTER the sentence has finished and
after a stretch of silence — a half-word, a breath, the start of a re-take. It
is short, so the duration gate accepts the file, and the listen-QC scores it 5/5
because the scripted words are all present and correct. It is only audible in
the cut, where it lands like a word beginning and being chopped off.

The rule: find the last silence of at least MIN_GAP. If what follows it is
shorter than MAX_TAIL, that tail is not speech we asked for — cut the file at
the start of that silence plus a short natural decay.

Picks up the per-beat narration files in this folder, named like s1.mp3, s4a.mp3
or b1.mp3, and stops with an error if it finds none (a check that reads nothing
must not report success).

Run with --check to report without writing.
"""
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
NOISE_DB = '-45dB'
MIN_GAP = 0.45      # a pause this long has ended the sentence
MAX_TAIL = 0.90     # anything shorter after that pause is an artefact
DECAY = 0.30        # keep this much after the last word


def silences(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af',
                        f'silencedetect=noise={NOISE_DB}:d={MIN_GAP}', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out, cur = [], None
    for line in (r.stderr or '').splitlines():
        m = re.search(r'silence_start:\s*([\d.]+)', line)
        if m:
            cur = float(m.group(1))
        m = re.search(r'silence_end:\s*([\d.]+)', line)
        if m and cur is not None:
            out.append((cur, float(m.group(1))))
            cur = None
    if cur is not None:
        out.append((cur, None))          # silence runs to the end of the file
    return out


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=nw=1:nk=1', path],
                                capture_output=True, text=True).stdout.strip())


check = '--check' in sys.argv
files = sorted(f for f in os.listdir(HERE)
               if re.fullmatch(r'[a-z]+\d+[a-z]?\.mp3', f))
if not files:
    raise SystemExit('no narration files found in ' + HERE)
fixed = 0
for f in files:
    p = os.path.join(HERE, f)
    total = dur(p)
    gaps = [g for g in silences(p) if g[1] is not None]      # gaps with audio after
    if not gaps:
        print(f'  {f}: clean')
        continue
    start, end = gaps[-1]
    tail = total - end
    if tail >= MAX_TAIL:
        print(f'  {f}: clean (tail after last pause is {tail:.2f}s of real speech)')
        continue
    cut = round(start + DECAY, 2)
    print(f'  {f}: ARTEFACT — {tail:.2f}s of audio at {end:.2f}s, after a '
          f'{end-start:.2f}s pause. Trimming {total:.2f}s -> {cut:.2f}s')
    fixed += 1
    if check:
        continue
    shutil.copy2(p, p + '.orig')
    tmp = p + '.tmp.mp3'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', p, '-t', str(cut),
                    '-af', f'afade=t=out:st={max(cut-0.12,0):.2f}:d=0.12',
                    '-codec:a', 'libmp3lame', '-qscale:a', '2', tmp],
                   capture_output=True)
    os.replace(tmp, p)

print(f'\n{fixed} of {len(files)} narration files had a trailing artefact'
      + (' (check only, nothing written)' if check else ''))
