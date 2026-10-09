"""Mix narration, music and effects on one timeline, duck the music under the voice, master to a target loudness.

  py mix.py --timeline work/timeline.json --out work/mix.wav [--lufs -16]

timeline.json:
{ "dur": 300.0,
  "narration": [{"file": "work/voice/s01.wav", "t": 4.2, "gain_db": 0}],
  "music":     [{"file": "music/theme.mp3", "t": 0, "in": 0, "dur": 60, "gain_db": -4, "fade_in": 1.5, "fade_out": 3}],
  "sfx":       [{"file": "work/sfx/clang.wav", "t": 31.4, "gain_db": -6, "pan": 0.2}],
  "duck": {"db": -9, "attack": 0.25, "release": 0.9} }
Deterministic: same timeline in, same file out. Prints what it read and the measured loudness.
"""
import argparse, json, pathlib, subprocess, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def place(bus, x, t, gain_db=0.0, pan=0.0):
    i = int(round(t * SR)); g = 10 ** (gain_db / 20)
    if pan:
        x = x * np.array([min(1, 1 - pan), min(1, 1 + pan)], np.float32)
    j = min(len(bus), i + len(x))
    if j > i >= 0:
        bus[i:j] += x[:j - i] * g


def fades(x, fi, fo):
    n = len(x)
    if fi > 0:
        k = min(n, int(fi * SR)); x[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None]
    if fo > 0:
        k = min(n, int(fo * SR)); x[n - k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
    return x


def smooth_env(active, attack, release):
    """0/1 activity -> smooth 0..1 envelope that rises `attack` s BEFORE speech and falls over `release` s after."""
    a = active.astype(np.float32); n = len(a); hop = 480; m = n // hop + 1
    blk = np.array([a[i * hop:(i + 1) * hop].max() if i * hop < n else 0 for i in range(m)], np.float32)
    ka, kr = max(1, int(attack * SR / hop)), max(1, int(release * SR / hop))
    fwd = blk.copy()
    for i in range(1, m):
        fwd[i] = max(blk[i], fwd[i - 1] - 1.0 / kr)
    bwd = fwd.copy()
    for i in range(m - 2, -1, -1):
        bwd[i] = max(fwd[i], bwd[i + 1] - 1.0 / ka)
    env = np.repeat(bwd, hop)[:n]
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(env, 0, 1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--timeline", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--lufs", type=float, default=-16.0); a = ap.parse_args()
    tl = json.loads(pathlib.Path(a.timeline).read_text(encoding="utf-8")); n = int(tl["dur"] * SR)
    voice, music, sfx = (np.zeros((n, 2), np.float32) for _ in range(3))
    for c in tl.get("narration", []):
        place(voice, load(c["file"]), c["t"], c.get("gain_db", 0))
    for c in tl.get("music", []):
        x = load(c["file"]); i0 = int(c.get("in", 0) * SR); x = x[i0:i0 + int(c.get("dur", len(x) / SR) * SR)]
        place(music, fades(x, c.get("fade_in", 0), c.get("fade_out", 0)), c["t"], c.get("gain_db", 0))
    for c in tl.get("sfx", []):
        place(sfx, load(c["file"]), c["t"], c.get("gain_db", 0), c.get("pan", 0))
    d = tl.get("duck", {"db": -9, "attack": .25, "release": .9})
    env = smooth_env(np.abs(voice).max(axis=1) > 0.01, d["attack"], d["release"])
    music *= (10 ** (d["db"] * env / 20)).astype(np.float32)[:, None]
    mix = voice + music + sfx
    tmp = pathlib.Path(a.out).with_suffix(".raw.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_f32le", str(tmp)],
                   input=mix.astype(np.float32).tobytes(), check=True)
    # two-pass loudnorm to the target
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=%s:TP=-1.5:LRA=11:print_format=json" % a.lufs, "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
    af = ("loudnorm=I=%s:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
          % (a.lufs, j["input_i"], j["input_tp"], j["input_lra"], j["input_thresh"], j["target_offset"]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", a.out], check=True)
    tmp.unlink()
    print("mix: %s | read %s | %d narration, %d music, %d sfx | %.1fs | input %.1f LUFS -> target %s"
          % (a.out, a.timeline, len(tl.get("narration", [])), len(tl.get("music", [])), len(tl.get("sfx", [])), tl["dur"], float(j["input_i"]), a.lufs))


if __name__ == "__main__":
    main()
