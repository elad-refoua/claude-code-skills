# -*- coding: utf-8 -*-
"""
Build the underscore bed: nothing in the film should sit in dead silence.

Two layers, both deliberately quiet enough to disappear under narration:

1. **Room tone**, lifted from the Veo clips themselves. This is the honest layer
   - it is the actual ambience of the generated lab - and it keeps the acted
   scenes from sounding vacuum-sealed.
2. **A low sustained pad**, a root/fifth/octave drone with a very slow tremolo.
   The convention for clinical documentary, and it carries the sections that
   have no footage of their own: the pipeline diagram, the ethics slide and the
   closing note, which are otherwise silent for long stretches.

Levels are set so the bed measures roughly 20 dB below the narration. Verified
by measurement at the end of this script rather than by ear.
"""
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, '03_clips')
OUT = os.path.join(ROOT, '05_audio')

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 161.125
SR = 48000

# Room tone is only an asset when the clip's own audio is neutral ambience.
# When the footage has percussive sound in it - the robotic-arm clip is full of
# key presses - looping it reads as an irritating tic rather than atmosphere.
# Set ROOMTONE_GAIN=0 to drop the layer and run on the pad alone.
ROOMTONE_GAIN = float(os.environ.get('ROOMTONE_GAIN', '0.50'))
PAD_GAIN = float(os.environ.get('PAD_GAIN', '0.175'))

ROOMTONE = os.path.join(OUT, '_roomtone.wav')
BED = os.path.join(OUT, 'bed.wav')


def run(args, label):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f'FAILED: {label}')
        print((r.stderr or '')[-1200:])
        raise SystemExit(1)


# --- 1. room tone -----------------------------------------------------------
# A clip with no speech in it: its whole run is usable ambience. Set
# ROOMTONE_CLIP to name the file; it differs per project.
# Loop it for the full runtime, high-pass out the rumble, and sit it low.
run(['ffmpeg', '-y', '-v', 'error', '-stream_loop', '-1', '-i', os.path.join(CLIPS, os.environ.get('ROOMTONE_CLIP', 'scene1.mp4')),
     '-t', f'{DURATION:.3f}', '-vn',
     '-af', f'highpass=f=120,lowpass=f=6000,volume={ROOMTONE_GAIN},afade=t=in:st=0:d=2,'
            f'afade=t=out:st={DURATION-3:.2f}:d=3,aresample={SR}',
     '-ac', '2', ROOMTONE], 'room tone')

# --- 2. pad + bed -----------------------------------------------------------
# A2 / E3 / A5 drone. The octave-and-a-bit on top gives it air without
# becoming a melody that would compete with the voice.
d = f'{DURATION:.3f}'
run(['ffmpeg', '-y', '-v', 'error',
     '-f', 'lavfi', '-i', f'sine=frequency=110:sample_rate={SR}:duration={d}',
     '-f', 'lavfi', '-i', f'sine=frequency=164.81:sample_rate={SR}:duration={d}',
     '-f', 'lavfi', '-i', f'sine=frequency=220:sample_rate={SR}:duration={d}',
     '-f', 'lavfi', '-i', f'anoisesrc=color=brown:sample_rate={SR}:duration={d}:amplitude=0.5',
     '-i', ROOMTONE,
     '-filter_complex',
     '[0:a]volume=0.50[r];'
     '[1:a]volume=0.26[f];'
     '[2:a]volume=0.14[o];'
     '[3:a]lowpass=f=380,volume=0.30[air];'
     '[r][f][o][air]amix=inputs=4:normalize=0[pad0];'
     # slow breathing, warmth, and a gentle lift so the last third opens up
     '[pad0]tremolo=f=0.1:d=0.30,lowpass=f=1100,'
     f'volume={PAD_GAIN},afade=t=in:st=0:d=4,afade=t=out:st={DURATION-5:.2f}:d=5[pad];'
     '[pad][4:a]amix=inputs=2:normalize=0,'
     'alimiter=limit=0.7,aresample=' + str(SR) + '[out]',
     '-map', '[out]', '-t', d, '-ac', '2', '-c:a', 'pcm_s16le', BED], 'bed')

os.remove(ROOMTONE)

# --- 3. measure, do not assume ---------------------------------------------
def measure(path):
    # volumedetect reports at info level, so stderr must NOT be suppressed.
    # An earlier version passed -v error and silently printed '?' forever.
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect',
                        '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    for line in (r.stderr or '').splitlines():
        if 'mean_volume' in line:
            return line.split('mean_volume:')[-1].strip()
    return 'UNMEASURED'

dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'default=nw=1:nk=1', BED], capture_output=True, text=True).stdout.strip()
print(f'bed.wav  {float(dur):.2f}s  RMS {measure(BED)} dB')
# Compare against the first per-beat narration file, whatever the naming
# (s1.mp3, s4a.mp3, b1.mp3 ...), so the check runs on every pipeline.
narr_files = sorted(f for f in os.listdir(OUT) if re.fullmatch(r'[a-z]+\d+[a-z]?\.mp3', f))
if narr_files:
    narr = os.path.join(OUT, narr_files[0])
    print(f'narration {narr_files[0]} RMS {measure(narr)} dB  (bed should sit well below this)')
else:
    print('no narration file to compare against')
