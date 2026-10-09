# -*- coding: utf-8 -*-
"""
Assemble a project submission video (the worked example: a 3-minute video about
an AI study aid used in a hands-on lab class).

Design notes that matter:

* **x1 speed only.** No `atempo`, no `setpts`, anywhere. The brief forbids speed
  changes, so extra seconds come from Ken Burns moves over stills, never from
  slowing footage down.
* **Ducking by construction.** Narration is a set of discrete per-segment files
  placed at explicit offsets. Nothing is scheduled over Scene 3's dialogue
  window, so character audio can never collide with the voiceover.
* **Pillarbox removal.** Veo returned 3:2 content padded into a 16:9 frame,
  because the reference stills were 1536x1024. Every clip is cropped back to its
  real content and then re-framed to 16:9, biased upward to keep headroom.
* Each segment is rendered to its own intermediate file. One giant filtergraph
  would be shorter to write and far harder to debug.
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, '03_clips')
REF = os.path.join(ROOT, '02_reference')
AUDIO = os.path.join(ROOT, '05_audio')
SLIDE = os.path.join(ROOT, '06_slide')
OUT = os.path.join(ROOT, '07_final')
WORK = os.path.join(OUT, 'segments')

W, H, FPS = 1920, 1080, 24

# (start, length) windows taken from each screen capture
# (start, length) windows read off the captures' own contact sheets.
# The ~38s the model spends thinking is cut, not sped up - the brief forbids
# speed changes - and the second label states the real elapsed time so the cut
# cannot mislead.
DEMO_HI_A = (5.0, 9.0)      # image loaded, question typed, submitted
DEMO_HI_B = (51.0, 15.0)    # the 94% answer arrives
DEMO_LO = (60.0, 18.0)      # the 64% refusal

# A Veo clip carries 3:2 content inside a 16:9 frame. Undo the pad, then take a
# 16:9 window biased to the upper third so faces keep their headroom.
UNPAD = ("crop=ih*3/2:ih:(iw-ih*3/2)/2:0,"
         "crop=iw:iw*9/16:0:(ih-iw*9/16)*0.30,"
         f"scale={W}:{H}:flags=lanczos,setsar=1")


FORCE = '--force' in sys.argv


def run(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print('FFMPEG FAILED:', ' '.join(args[:9]), '...')
        print((r.stderr or '')[-1500:])
        raise SystemExit(1)
    return r


def cached(out, src):
    """Segment rendering is the slow part, so skip anything already newer than
    its source. Pass --force to rebuild everything."""
    return (not FORCE and os.path.exists(out) and os.path.getsize(out) > 0
            and os.path.getmtime(out) >= os.path.getmtime(src))


def dur(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=nw=1:nk=1', path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def clip_seg(name, src, start, length, zoom=1.0):
    """A slice of a Veo clip. zoom>1 punches in, which turns one 8s generation
    into two distinct-looking shots without spending another credit."""
    out = os.path.join(WORK, f'{name}.mp4')
    if cached(out, src):
        return out
    vf = UNPAD
    if zoom > 1.0:
        vf += f",scale={int(W*zoom)}:{int(H*zoom)}:flags=lanczos,crop={W}:{H}"
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(start), '-t', str(length), '-i', src,
         '-vf', vf, '-r', str(FPS), '-an',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out])
    return out


def still_seg(name, src, length, z0=1.0, z1=1.12, px=0.5, py=0.5):
    """Ken Burns move over a still. Slow push from z0 to z1 toward (px,py).

    zoompan renders at the *working* resolution, so the pre-scale only needs to
    cover the largest zoom actually requested plus a small margin. Scaling to
    4K first (the obvious-looking choice) made 8-second segments take minutes
    and weigh 95 MB apiece for no visible gain.
    """
    out = os.path.join(WORK, f'{name}.mp4')
    if cached(out, src):
        return out
    frames = int(round(length * FPS))
    work_w = int(W * max(z0, z1) * 1.06)
    vf = (f"scale={work_w}:-1:flags=lanczos,"
          f"crop=iw:iw*9/16:0:(ih-iw*9/16)*0.5,"
          f"zoompan=z='{z0}+({z1}-{z0})*on/{frames}'"
          f":x='iw*{px}-(iw/zoom)*{px}':y='ih*{py}-(ih/zoom)*{py}'"
          f":d={frames}:s={W}x{H}:fps={FPS},setsar=1")
    # Bound the output by FRAME COUNT, not by -t. With `-loop 1` the input is
    # infinite and zoompan expands every input frame into `d` output frames, so
    # a duration cap still lets it queue enormous amounts of work: a 20-second
    # segment ran for four minutes and passed 50 MB before being killed.
    # `-frames:v` stops it at exactly the frames we asked for.
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', src,
         '-vf', vf, '-frames:v', str(frames), '-r', str(FPS), '-an',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21',
         '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', out])
    return out


def demo_seg(name, src, start, length, label=None):
    """A slice of the real screen capture, seated in a device frame on the same
    dark ground as the slides.

    Cutting straight from a navy slide to a full-bleed white web app is jarring;
    insetting the capture keeps one visual world across the whole film and reads
    as deliberate rather than pasted in.
    """
    out = os.path.join(WORK, f'{name}.mp4')
    if cached(out, src):
        return out
    inner_w, inner_h = 1616, 909            # 16:9, leaves a generous margin
    x, y = (W - inner_w) // 2, (H - inner_h) // 2
    fc = (
        f"color=c=0x0B0F14:s={W}x{H}:r={FPS}[bg];"
        # a faint halo so the panel lifts off the background
        f"[bg]drawbox=x={x-14}:y={y-14}:w={inner_w+28}:h={inner_h+28}:"
        f"color=0x3B82F6@0.10:t=fill[bg2];"
        f"[0:v]scale={inner_w}:{inner_h}:flags=lanczos,setsar=1[app];"
        f"[bg2][app]overlay={x}:{y}:shortest=1[withapp];"
        f"[withapp]drawbox=x={x-1}:y={y-1}:w={inner_w+2}:h={inner_h+2}:"
        f"color=0x3B82F6@0.55:t=2[framed]"
    )
    last = 'framed'
    if label:
        # drawtext treats % as a strftime specifier and silently drops the
        # whole string; ':' and quotes also need escaping.
        safe = (label.replace('%', ' PERCENT')
                     .replace(':', r'\:')
                     .replace("'", ''))
        fc += (f";[{last}]drawtext=text='{safe}':fontcolor=0x8FA1B3:fontsize=30:"
               f"x=(w-text_w)/2:y={y+inner_h+26}:"
               f"fontfile='C\:/Windows/Fonts/consola.ttf'[out]")
        last = 'out'
    else:
        fc += f";[{last}]null[out]"
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(start), '-t', str(length), '-i', src,
         '-filter_complex', fc, '-map', '[out]', '-t', str(length),
         '-r', str(FPS), '-an',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
         '-pix_fmt', 'yuv420p', out])
    return out


def slide_seg(name, pngs, per):
    """Slide reveal states, cross-dissolved, with a barely-there drift."""
    parts = []
    for i, png in enumerate(pngs):
        p = still_seg(f'{name}_{i}', png, per, z0=1.0, z1=1.03)
        parts.append(p)
    return parts


def concat(paths, out, xfade=0.45):
    """Concatenate with crossfades. Durations shorten by xfade per junction."""
    if len(paths) == 1:
        run(['ffmpeg', '-y', '-v', 'error', '-i', paths[0], '-c', 'copy', out])
        return dur(out)
    args = ['ffmpeg', '-y', '-v', 'error']
    for p in paths:
        args += ['-i', p]
    fc, prev, offset = [], '0:v', 0.0
    for i in range(1, len(paths)):
        offset += dur(paths[i - 1]) - xfade
        lab = f'x{i}'
        fc.append(f'[{prev}][{i}:v]xfade=transition=fade:duration={xfade}:offset={offset:.3f}[{lab}]')
        prev = lab
    args += ['-filter_complex', ';'.join(fc), '-map', f'[{prev}]',
             '-r', str(FPS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
             '-pix_fmt', 'yuv420p', out]
    run(args)
    return dur(out)


def main():
    os.makedirs(WORK, exist_ok=True)
    print('demo captures present:',
          os.path.exists(os.path.join(ROOT, '04_screencap', 'demo_hi.webm')),
          os.path.exists(os.path.join(ROOT, '04_screencap', 'demo_lo.webm')))

    s1c = os.path.join(CLIPS, 'scene1.mp4')
    s2c = os.path.join(CLIPS, 'scene2.mp4')
    s3c = os.path.join(CLIPS, 'scene3.mp4')
    s5c = os.path.join(CLIPS, 'scene5.mp4')

    atlas = os.path.join(REF, 'still_atlas_vs_tray.png')
    tabpov = os.path.join(REF, 'still_tablet_pov.png')
    lab = os.path.join(REF, 'ref_lab_tablet.png')

    segments = []          # (label, path)

    # ---- Scene 1 : the problem ---------------------------------------------
    segments.append(('s1a', clip_seg('s1a', s1c, 0.0, 8.0)))
    segments.append(('s1b', still_seg('s1b', atlas, 10.5, 1.0, 1.16, px=0.35, py=0.55)))
    segments.append(('s1c', clip_seg('s1c', s1c, 1.4, 6.5, zoom=1.45)))

    # ---- Scene 2 : nobody comes -------------------------------------------
    segments.append(('s2a', clip_seg('s2a', s2c, 0.0, 8.0)))
    segments.append(('s2b', clip_seg('s2b', s2c, 1.0, 7.0, zoom=1.5)))

    # ---- Scene 3 : the solution (dialogue clip carries its own audio) ------
    if os.path.exists(s3c):
        segments.append(('s3a', clip_seg('s3a', s3c, 0.0, 8.0)))
    segments.append(('s3b', still_seg('s3b', tabpov, 10.5, 1.0, 1.18, px=0.55, py=0.35)))
    segments.append(('s3c', still_seg('s3c', lab, 9.5, 1.14, 1.0, px=0.5, py=0.45)))

    # ---- Scene 4 : the demo ------------------------------------------------
    pipe = [os.path.join(SLIDE, f'pipeline_{i}.png') for i in (1, 2, 3, 4)]
    for i, p in enumerate(slide_seg('s4pipe', pipe, 5.6)):
        segments.append((f's4pipe{i}', p))
    hi = os.path.join(ROOT, '04_screencap', 'demo_hi.webm')
    lo = os.path.join(ROOT, '04_screencap', 'demo_lo.webm')
    if os.path.exists(hi) and os.path.exists(lo):
        # Real screen captures of the running app, inset on the dark ground.
        segments.append(('s4demoq', demo_seg('s4demoq', hi, DEMO_HI_A[0], DEMO_HI_A[1],
                                             'LIVE CAPTURE - THE QUESTION')))
        segments.append(('s4demohi', demo_seg('s4demohi', hi, DEMO_HI_B[0], DEMO_HI_B[1],
                                              'LIVE CAPTURE - ANSWER RETURNED AFTER ~30 SECONDS')))
        segments.append(('s4demolo', demo_seg('s4demolo', lo, DEMO_LO[0], DEMO_LO[1],
                                              'LIVE CAPTURE - BELOW THE 85% THRESHOLD')))
    else:
        # Placeholder so the rough cut still times out correctly.
        segments.append(('s4hold', still_seg('s4hold', pipe[3], 27.0, 1.02, 1.12)))

    # ---- Scene 5 : resolution ---------------------------------------------
    segments.append(('s5a', clip_seg('s5a', s5c, 0.0, 8.0)))
    segments.append(('s5b', clip_seg('s5b', s5c, 3.4, 4.5, zoom=1.4)))

    # ---- Scene 6 : honest limits ------------------------------------------
    eth = [os.path.join(SLIDE, f'ethics_{i}.png') for i in (0, 1, 2, 3)]
    for i, p in enumerate(slide_seg('s6eth', eth, 7.2)):
        segments.append((f's6eth{i}', p))

    # ---- Closing note : what is real, what is demonstration only ----------
    note = os.path.join(SLIDE, 'prototype_note.png')
    if os.path.exists(note):
        segments.append(('note', still_seg('note', note, 11.0, 1.0, 1.03)))

    paths = [p for _, p in segments]
    for lab_, p in segments:
        print(f'  {lab_:10s} {dur(p):6.2f}s')

    video = os.path.join(WORK, '_video.mp4')
    total = concat(paths, video)
    print(f'\nvideo track: {total:.2f}s ({int(total//60)}:{total%60:04.1f})')

    json.dump({'segments': [{'label': l, 'dur': round(dur(p), 3)} for l, p in segments],
               'video_duration': round(total, 3)},
              open(os.path.join(OUT, 'timeline.json'), 'w'), indent=2)
    print('wrote timeline.json')


if __name__ == '__main__':
    main()
