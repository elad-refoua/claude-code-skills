"""Deterministic music editor: for each film section, find the (cue file, start offset) whose loudness curve best
matches the section's target intensity curve. Lyria does not reliably honour timestamped structure (measured
2026-09-25: correlations of -0.24..0.46 against the requested curves while a listener model called every take
"a perfect match"), so we search inside everything we generated instead of trusting the brief.

  py fit_music.py --sections music/sections.json --out music/fit.json

sections.json: [{"id": "s04", "dur": 40.4, "target": [[t, level], ...], "candidates": ["music/m2_s04_t1.mp3", ...],
                 "must_start_at_zero": false}, ...]
Score = Pearson correlation between the candidate's dB envelope (0.5 s) over [off, off+dur] and the target, with a
small penalty for starting mid-phrase (a loud onset right at `off`) unless the section fades in.
"""
import argparse, json, pathlib, subprocess, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
HOP = 0.5


def env_db(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", "8000", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); h = int(8000 * HOP)
    return 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-6 for i in range(0, len(x) - h, h)]))


ap = argparse.ArgumentParser(); ap.add_argument("--sections", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
secs = json.loads(pathlib.Path(a.sections).read_text(encoding="utf-8")); cache, out = {}, {}
for s in secs:
    n = int(round(s["dur"] / HOP)); tt = np.arange(n) * HOP; ts, vs = zip(*s["target"]); goal = np.interp(tt, ts, vs)
    best = None
    for c in s["candidates"]:
        if not pathlib.Path(c).exists():
            continue
        e = cache.setdefault(c, env_db(c))
        offs = [0] if s.get("must_start_at_zero") else range(0, max(1, len(e) - n + 1))
        for k in offs:
            seg = e[k:k + n]
            if len(seg) < n or np.std(seg) < 1e-6:
                continue
            r = float(np.corrcoef(seg, goal)[0, 1])
            if k > 0 and seg[0] - np.median(seg) > 4:             # a hard onset right at the cut point
                r -= 0.08
            if best is None or r > best[0]:
                best = (r, c, k * HOP)
    out[s["id"]] = {"file": best[1], "in": best[2], "corr": round(best[0], 3), "dur": s["dur"]} if best else None
    print("%-14s %s" % (s["id"], ("%s @ %.1fs  corr %.3f" % (best[1], best[2], best[0])) if best else "NO CANDIDATE"))
pathlib.Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("read", a.sections, "->", a.out)
