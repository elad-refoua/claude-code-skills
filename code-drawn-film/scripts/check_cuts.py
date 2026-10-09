"""Continuity at every shot boundary, measured on the rendered frames (work/frames/f%06d.jpg).

  py check_cuts.py [--timing src/timing.js] [--frames work/frames] [--allow c07_a>c08_b ...]

For each boundary, the jump from the last frame of shot A to the first frame of shot B (mean absolute grey
difference on a 192x108 proxy) is compared with the ordinary frame-to-frame motion just before it (median of the
previous 12 differences). A boundary FAILs when the jump is > 3x that motion AND > 6 grey levels, i.e. a pop the
eye will see. Prints the file range it read; deliberate cuts can be allowed by name.
"""
import argparse, json, pathlib, sys
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser(); ap.add_argument("--timing", default="src/timing.js"); ap.add_argument("--frames", default="work/frames")
ap.add_argument("--fps", type=int, default=24); ap.add_argument("--allow", nargs="*", default=[]); a = ap.parse_args()
js = pathlib.Path(a.timing).read_text(encoding="utf-8"); T = json.loads(js[js.index("=") + 1:].rstrip().rstrip(";"))
F = pathlib.Path(a.frames)


def g(i):
    p = F / ("f%06d.jpg" % i)
    return np.asarray(Image.open(p).convert("L").resize((192, 108), Image.BILINEAR), np.float32) if p.exists() else None


shots = sorted(T["shots"].items(), key=lambda kv: kv[1]["t0"]); bad = 0; checked = 0
print("frames from", F.resolve())
for (na, A), (nb, B) in zip(shots, shots[1:]):
    i = int(round(B["t0"] * a.fps))
    frames = [g(k) for k in range(i - 13, i + 1)]
    if any(f is None for f in frames):
        print("%-30s  (frames missing, not checked)" % (na + " > " + nb)); continue
    d = [float(np.abs(frames[k + 1] - frames[k]).mean()) for k in range(13)]
    motion, jump = float(np.median(d[:-1])), d[-1]
    ok = not (jump > 3 * max(motion, .5) and jump > 6) or (na + ">" + nb) in a.allow
    checked += 1; bad += not ok
    print("%-30s jump %5.2f  motion %5.2f  %s" % (na + " > " + nb, jump, motion, "PASS" if ok else "FAIL"))
print("%d boundaries checked, %d failed" % (checked, bad))
sys.exit(1 if bad else 0)
