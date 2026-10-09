# -*- coding: utf-8 -*-
"""
Assemble an editorial short film (the worked example: a film about one AI model
orchestrating others - image, voice and video models driven by a coding agent).

Follows the ai-live-action-video skill: audio measured first, picture cut to fit,
`-frames:v` (never `-t`) on zoompan, the 3:2 pillarbox cropped out of the Veo
clip, and nothing sped up anywhere.

Subtitles are burned in because Facebook autoplays muted, and their timings come
from transcribing each narration file rather than from dividing the text evenly -
the latter drifts badly on a beat with an uneven sentence.
"""
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD, SLIDE, CLIPS, REF = (os.path.join(ROOT, d) for d in
                          ('05_audio', '06_slide', '03_clips', '02_reference'))
OUT = os.path.join(ROOT, '07_final')
WORK = os.path.join(OUT, 'seg')
W, H, FPS, XFADE = 1920, 1080, 24, 0.45
PAPER = '0xF6F3EE'
# The dark footage sits as a photo plate on the page, the way a magazine sets a
# picture in a column of type. That turns the light/dark contrast into rhythm
# instead of a jarring cut, and leaves the foot of the frame as paper so the
# burned-in subtitles always land on a light ground.
PW, PH, PX, PY = 1424, 800, 248, 118   # even dims: h264 rejects odd height
# A Python interpreter that has faster-whisper installed (it can be a separate venv).
WHISPER = os.environ.get('WHISPER_PYTHON', sys.executable)

UNPAD = ("crop=ih*3/2:ih:(iw-ih*3/2)/2:0,crop=iw:iw*9/16:0:(ih-iw*9/16)*0.5,"
         f"scale={W}:{H}:flags=lanczos,setsar=1")


def run(a, label=''):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        print('FFMPEG FAILED', label); print((r.stderr or '')[-1400:]); raise SystemExit(1)
    return r


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=nw=1:nk=1', p],
                                capture_output=True, text=True).stdout.strip())


def still(name, src, length, z0=1.0, z1=1.07, px=.5, py=.5):
    o = os.path.join(WORK, name + '.mp4')
    n = int(round(length * FPS))
    ww = int(W * max(z0, z1) * 1.06)
    vf = (f"scale={ww}:-1:flags=lanczos,crop=iw:iw*9/16:0:(ih-iw*9/16)*0.5,"
          f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw*{px}-(iw/zoom)*{px}'"
          f":y='ih*{py}-(ih/zoom)*{py}':d={n}:s={W}x{H}:fps={FPS},setsar=1")
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', src, '-vf', vf,
         '-frames:v', str(n), '-r', str(FPS), '-an', '-c:v', 'libx264',
         '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', o], name)
    return o


def clip(name, src, start, length, zoom=1.0):
    o = os.path.join(WORK, name + '.mp4')
    vf = UNPAD + (f",scale={int(W*zoom)}:{int(H*zoom)}:flags=lanczos,crop={W}:{H}"
                  if zoom > 1 else '')
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(start), '-t', str(length), '-i', src,
         '-vf', vf, '-r', str(FPS), '-an', '-c:v', 'libx264', '-preset', 'veryfast',
         '-crf', '19', '-pix_fmt', 'yuv420p', o], name)
    got = dur(o)
    if abs(got - length) > .15:                     # slices truncate silently
        print(f'  ! {name}: asked {length}s, got {got:.2f}s')
    return o


def passthru(name, src):
    o = os.path.join(WORK, name + '.mp4')
    run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf',
         f'scale={W}:{H}:flags=lanczos,setsar=1', '-r', str(FPS), '-an',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
         '-pix_fmt', 'yuv420p', o], name)
    return o



def plate(name, src, length, is_video, caption='', unpad=False, start=0.0, zoom=1.0):
    """Inset a dark asset on the paper page, with an editorial caption.

    `zoom` punches in, turning one 8s generation into several distinct shots.
    """
    o = os.path.join(WORK, name + '.mp4')
    inp = (['-ss', str(start), '-t', str(length), '-i', src] if is_video
           else ['-loop', '1', '-t', str(length), '-i', src])
    # `unpad` only for an asset a video model returned as 3:2 inside 16:9.
    # Everything else scales to COVER the plate: scale-to-width-then-crop fails
    # whenever the source is already 16:9 and lands a few pixels short.
    pad = (UNPAD if unpad else
           f'scale={PW}:{PH}:force_original_aspect_ratio=increase:flags=lanczos,'
           f'crop={PW}:{PH}')
    if zoom > 1.0:
        pad += (f',scale={int(PW*zoom)}:{int(PH*zoom)}:flags=lanczos,'
                f'crop={PW}:{PH}')
    fc = (f"color=c={PAPER}:s={W}x{H}:r={FPS}[bg];"
          f"[0:v]{pad},scale={PW}:{PH}:flags=lanczos,setsar=1[a];"
          f"[bg][a]overlay={PX}:{PY}:shortest=1[v0];"
          f"[v0]drawbox=x={PX-1}:y={PY-1}:w={PW+2}:h={PH+2}:color=0xDED8CE@1:t=2[v1]")
    last = 'v1'
    if caption:
        # A comma inside a filtergraph chains filters, so an unescaped one in the
        # caption text silently breaks the whole graph. ':' and '%' likewise.
        cap = (caption.replace(':', r'\:').replace(',', r'\,')
                      .replace("'", '').replace('%', ' percent'))
        fc += (f";[{last}]drawtext=text='{cap}':fontcolor=0x80887F:fontsize=26:"
               f"x={PX}:y={PY-42}:fontfile='C\:/Windows/Fonts/consola.ttf'[vo]")
        last = 'vo'
    else:
        fc += f";[{last}]null[vo]"
    run(['ffmpeg', '-y', '-v', 'error'] + inp + ['-filter_complex', fc, '-map', '[vo]',
         '-t', str(length), '-r', str(FPS), '-an', '-c:v', 'libx264',
         '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', o], name)
    got = dur(o)
    # A slice longer than what is left in the source truncates in silence. That
    # is how b4's narration came to overrun its picture by 2.3s while every gate
    # still passed: asking an 8s clip for 10.7s simply returns 8s.
    if abs(got - length) > 0.15:
        print(f'  ! {name}: asked {length:.2f}s, got {got:.2f}s '
              f'- source is too short for this slice')
    return o


# ---- picture, sized to the measured narration -----------------------------
os.makedirs(WORK, exist_ok=True)
nd = {b: dur(os.path.join(AUD, f'{b}.mp3')) for b in
      ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']}
print('narration:', {k: round(v, 2) for k, v in nd.items()},
      '=', round(sum(nd.values()), 1), 's')

S = lambda n: os.path.join(SLIDE, f'slide_{n}.png')
segs = [
    ('b1',  [still('s1', S(1), nd['b1'] + 1.8, 1.0, 1.06)]),
    ('b2',  [plate('s2', os.path.join(SLIDE, 'waveform_b2.png'), nd['b2'] + 1.8, False,
                   'GEMINI  -  the waveform of this very sentence')]),
    ('b3',  [plate('s3', os.path.join(REF, 'machine_operating_machine.png'),
                   nd['b3'] + 1.8, False,
                   'GPT IMAGE 2  -  prompt written and sent by Claude')]),
    # b4 carries the longest line (16.9s) and the only clip is 8s, so it is cut
    # as three shots from that one generation - wide, then two punch-ins - rather
    # than asking for a slice the source cannot supply.
    ('b4',  [plate('s4a', os.path.join(CLIPS, 'robot_arm.mp4'), 6.0, True,
                   'VEO 3.1  -  driven through a browser  |  no API', unpad=True),
             plate('s4b', os.path.join(CLIPS, 'robot_arm.mp4'), 5.6, True,
                   'VEO 3.1  -  first-frame conditioned', unpad=True,
                   start=1.2, zoom=1.35),
             plate('s4c', os.path.join(CLIPS, 'robot_arm.mp4'), 5.2, True,
                   'VEO 3.1  -  eight seconds of generated footage', unpad=True,
                   start=2.0, zoom=1.7)]),
    ('b5',  [still('s5', S(5), nd['b5'] + 1.8, 1.0, 1.03)]),
    ('b6',  [still('s6', S(6), nd['b6'] + 1.8, 1.0, 1.03)]),
    ('b7',  [still('s7', S(7), nd['b7'] + 1.8, 1.0, 1.03)]),
    # The closing shot is the whole thesis in one frame: Gemini drew the still,
    # then Veo was handed that same still as its first frame and moved the camera
    # into it. One model's output became another model's input, and Claude was
    # the only thing in between.
    ('b8',  [plate('s8a', os.path.join(CLIPS, 'recursion_push.mp4'), 4.8, True,
                   'GEMINI DREW IT  |  VEO MOVED THE CAMERA INTO IT'),
             still('s8b', S(8), nd['b8'] - 3.0, 1.0, 1.04)]),
]

paths, starts, acc, i = [], {}, 0.0, 0
for beat, parts in segs:
    starts[beat] = acc - i * XFADE
    for p in parts:
        paths.append(p); acc += dur(p); i += 1
total_raw = acc - (len(paths) - 1) * XFADE
print('picture:', round(total_raw, 2), 's')

args = ['ffmpeg', '-y', '-v', 'error']
for p in paths:
    args += ['-i', p]
fc, prev, off = [], '0:v', 0.0
for k in range(1, len(paths)):
    off += dur(paths[k - 1]) - XFADE
    fc.append(f'[{prev}][{k}:v]xfade=transition=fade:duration={XFADE}:offset={off:.3f}[x{k}]')
    prev = f'x{k}'
video = os.path.join(WORK, '_v.mp4')
args += ['-filter_complex', ';'.join(fc), '-map', f'[{prev}]', '-r', str(FPS),
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', video]
run(args, 'concat')
TOTAL = dur(video)
print('video track:', round(TOTAL, 2), 's')

# ---- subtitles, timed by transcribing each beat ---------------------------
tr = os.path.join(WORK, '_tr.py')
open(tr, 'w', encoding='utf-8').write(
    "import sys,io,json\n"
    "sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')\n"
    "from faster_whisper import WhisperModel\n"
    "m=WhisperModel('base.en',device='cpu',compute_type='int8')\n"
    "segs,_=m.transcribe(sys.argv[1],language='en')\n"
    "print(json.dumps([{'s':s.start,'e':s.end,'t':s.text.strip()} for s in segs]))\n")


def ts(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f'{h:d}:{m:02d}:{t%60:05.2f}'


lines = []
for beat in nd:
    r = subprocess.run([WHISPER, tr, os.path.join(AUD, f'{beat}.mp3')],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    m = re.search(r'\[.*\]', r.stdout or '', re.S)
    if not m:
        print('  ! no transcript for', beat); continue
    base = starts[beat] + 0.55                      # narration offset within its beat
    for c in json.loads(m.group(0)):
        lines.append((base + c['s'], base + c['e'], c['t']))

ass = os.path.join(WORK, 'subs.ass')
with open(ass, 'w', encoding='utf-8') as f:
    f.write('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n'
            'WrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n'
            'Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,'
            'Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,'
            'Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n'
            # Ink on paper: ASS colours are &HAABBGGRR, so #14161A -> &H001A1614.
            # No box and no outline, because it sits on the page rather than on
            # a plate. MarginV clears the plate caption above it.
            'Style: S,Public Sans,50,&H001A1614,&H00FFFFFF,&H00FFFFFF,0,0,0,0,'
            '100,100,0,0,1,0,0,2,220,220,34,1\n\n[Events]\n'
            'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n')
    for s, e, t in lines:
        t = t.replace('{', '(').replace('}', ')')
        f.write(f'Dialogue: 0,{ts(s)},{ts(e)},S,,0,0,0,,{t}\n')
print('subtitles:', len(lines), 'cues')

# ---- bed, mix, burn -------------------------------------------------------
# No room tone here: the only clip's audio is keyboard clatter, which loops
# as an irritating tic rather than atmosphere. Pad only, and quieter.
env = dict(os.environ, ROOMTONE_CLIP='robot_arm.mp4',
           ROOMTONE_GAIN='0.0', PAD_GAIN='0.105')
r = subprocess.run([sys.executable, os.path.join(AUD, 'build_bed.py'), f'{TOTAL:.3f}'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print((r.stdout or '').strip() or '(bed produced no output)')
if r.returncode:
    print('BED BUILD FAILED:'); print((r.stderr or '')[-800:]); raise SystemExit(1)

final = os.path.join(OUT, 'editorial_film.mp4')
a = ['ffmpeg', '-y', '-v', 'error', '-i', video]
fc, mix, n = [], [], 1
bed = os.path.join(AUD, 'bed.wav')
if os.path.exists(bed):
    a += ['-i', bed]; fc.append(f'[{n}:a]volume=1.0[bed]'); mix.append('[bed]'); n += 1
for beat in nd:
    a += ['-i', os.path.join(AUD, f'{beat}.mp3')]
    d = int((starts[beat] + 0.55) * 1000)
    fc.append(f'[{n}:a]adelay={d}|{d}[n{n}]'); mix.append(f'[n{n}]'); n += 1
fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:dropout_transition=0,"
          f"alimiter=limit=0.95,aresample=48000[ao]")
subs = ass.replace('\\', '/').replace(':', r'\:')
a += ['-filter_complex', ';'.join(fc) + f";[0:v]ass='{subs}'[vo]",
      '-map', '[vo]', '-map', '[ao]', '-t', f'{TOTAL:.3f}',
      '-r', str(FPS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
      '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
      '-movflags', '+faststart', final]
run(a, 'mux')
print('wrote', final, f'{dur(final):.2f}s')
json.dump({'total': round(TOTAL, 3), 'starts': {k: round(v, 3) for k, v in starts.items()}},
          open(os.path.join(OUT, 'timeline.json'), 'w'), indent=2)
