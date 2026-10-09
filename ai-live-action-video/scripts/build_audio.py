# -*- coding: utf-8 -*-
"""
Build the audio track and mux it onto the video.

The brief requires "audio ducking": when a character speaks on screen, the
narration must stop rather than talk over them. This is enforced structurally
rather than with a compressor - narration lives in eight separate files placed
at explicit offsets, and the Scene 3 window where the two characters speak
(measured by transcription at 0.0-7.0s into that clip) simply has no narration
scheduled in it. A collision is therefore impossible, not merely unlikely, and
`--check` proves it arithmetically.
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, '05_audio')
CLIPS = os.path.join(ROOT, '03_clips')
OUT = os.path.join(ROOT, '07_final')
WORK = os.path.join(OUT, 'segments')

XFADE = 0.45
MIN_GAP = 0.35        # breathing room between narration segments
DIALOGUE_START, DIALOGUE_END = 0.0, 7.0     # measured, not assumed

# Which segment each narration file hangs off, and how far into it.
PLACEMENT = [
    ('s1',  's1a',     0.6),
    ('s2',  's2a',     0.15),
    ('s3',  's3a',     7.5),   # starts only after the dialogue has finished
    ('s4a', 's4pipe0', 0.4),
    ('s4b', 's4demohi', 2.5),
    ('s4c', 's4demolo', 3.5),
    ('s5',  's5a',     0.3),
    ('s6',  's6eth0',  0.4),
]


def dur(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True)
    return float(r.stdout.strip())


def starts(timeline):
    """Start time of each segment on the finished timeline. Each crossfade
    junction pulls everything after it earlier by XFADE."""
    out, acc = {}, 0.0
    for i, seg in enumerate(timeline['segments']):
        out[seg['label']] = acc - i * XFADE
        acc += seg['dur']
    return out


def plan():
    timeline = json.load(open(os.path.join(OUT, 'timeline.json')))
    st = starts(timeline)
    items = []
    for narr, anchor, offset in PLACEMENT:
        if anchor not in st:
            print(f'  skip {narr}: anchor {anchor} not in this cut')
            continue
        f = os.path.join(AUDIO, f'{narr}.mp3')
        if not os.path.exists(f):
            print(f'  skip {narr}: {f} missing')
            continue
        t = st[anchor] + offset
        # Never let a segment start before the previous one has finished. The
        # anchor gives the intended position; this keeps it honest if a picture
        # segment turns out shorter than the narration it has to carry.
        if items:
            t = max(t, items[-1]['end'] + MIN_GAP)
        items.append(dict(id=narr, path=f, start=t, dur=dur(f), end=t + dur(f)))
    return timeline, st, items


def check(timeline, st, items):
    """Deterministic gate. Returns list of problems; empty means clean."""
    problems = []

    # 1. narration must never overlap another narration segment
    for a, b in zip(items, items[1:]):
        if b['start'] < a['end'] - 0.01:
            problems.append(f"narration overlap: {a['id']} ends {a['end']:.2f} "
                            f"but {b['id']} starts {b['start']:.2f}")

    # 2. narration must never overlap the on-screen dialogue (the ducking rule)
    if 's3a' in st:
        d0, d1 = st['s3a'] + DIALOGUE_START, st['s3a'] + DIALOGUE_END
        for it in items:
            if it['start'] < d1 and it['end'] > d0:
                problems.append(f"DUCKING VIOLATION: {it['id']} "
                                f"({it['start']:.2f}-{it['end']:.2f}) overlaps "
                                f"character dialogue ({d0:.2f}-{d1:.2f})")

    # 3. nothing may run past the end of picture
    total = timeline['video_duration']
    for it in items:
        if it['end'] > total + 0.01:
            problems.append(f"{it['id']} ends at {it['end']:.2f}, past picture end {total:.2f}")

    # 4. the whole thing must fit the brief's hard limit
    if total > 180.0:
        problems.append(f"runtime {total:.2f}s exceeds the 3:00 limit")

    return problems


def build(timeline, st, items):
    video = os.path.join(WORK, '_video.mp4')
    total = timeline['video_duration']
    out = os.path.join(OUT, 'final_video.mp4')

    args = ['ffmpeg', '-y', '-v', 'error', '-i', video]
    inputs, fc, mixes = 1, [], []

    # Underscore bed first, so no part of the film sits in dead silence.
    bed = os.path.join(AUDIO, 'bed.wav')
    if os.path.exists(bed):
        args += ['-i', bed]
        fc.append(f'[{inputs}:a]volume=1.0[bed]')
        mixes.append('[bed]')
        inputs += 1

    for it in items:
        args += ['-i', it['path']]
        fc.append(f"[{inputs}:a]adelay={int(it['start']*1000)}|{int(it['start']*1000)},"
                  f"volume=1.0[n{inputs}]")
        mixes.append(f'[n{inputs}]')
        inputs += 1

    # Scene 3's own audio carries the two spoken lines. Take only the dialogue
    # window, and place it exactly where that clip sits on the timeline.
    if 's3a' in st:
        args += ['-i', os.path.join(CLIPS, 'scene3.mp4')]
        d0 = int(max(st['s3a'], 0) * 1000)
        fc.append(f"[{inputs}:a]atrim=0:{DIALOGUE_END},asetpts=PTS-STARTPTS,"
                  f"adelay={d0}|{d0},volume=1.6[dlg]")
        mixes.append('[dlg]')
        inputs += 1

    fc.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0:dropout_transition=0,"
              f"alimiter=limit=0.95,aresample=48000[aout]")

    args += ['-filter_complex', ';'.join(fc),
             '-map', '0:v', '-map', '[aout]',
             '-t', f'{total:.3f}',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
             '-movflags', '+faststart', out]
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print((r.stderr or '')[-2000:])
        raise SystemExit(1)
    return out


def main():
    timeline, st, items = plan()
    print('\nNarration placement:')
    for it in items:
        print(f"  {it['id']:5s} {it['start']:7.2f} -> {it['end']:7.2f}  ({it['dur']:.2f}s)")
    if 's3a' in st:
        print(f"\n  dialogue window: {st['s3a']:.2f} -> {st['s3a']+DIALOGUE_END:.2f}")

    problems = check(timeline, st, items)
    print('\n--- CHECK ---')
    if problems:
        for p in problems:
            print('  FAIL:', p)
    else:
        print('  PASS: no narration overlaps, no ducking violation, fits 3:00')

    if '--check' in sys.argv:
        raise SystemExit(1 if problems else 0)

    out = build(timeline, st, items)
    print(f'\nwrote {out}  ({dur(out):.2f}s)')


if __name__ == '__main__':
    main()
