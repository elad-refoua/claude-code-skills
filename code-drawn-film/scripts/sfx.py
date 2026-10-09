"""A small foley library synthesized in code (numpy only), deterministic by seed.

  py sfx.py --out work/sfx            -> clang, creak, click, whoosh, rustle, typewriter, crickets, steps, tick, pop, thud, chime .wav

Each sound is 48 kHz mono, peak-normalised to -3 dBFS. They are meant to sit UNDER music and voice.
Levels in mix.py: one-shots (clang, click, pop, thud, tick, chime) about -12 dB; anything SUSTAINED or PULSED
(pencil, purr, water, crickets, whoosh, rustle beds) at -20 dB or lower, and -22 dB where nothing else plays.
In a previous build the 3 s `pencil` scratch at -13 dB, alone in the opening, was 70-80% of the mix's energy and
read as an unpleasant buzz (viewer feedback, 2026-09-26). `purr` is pulsed noise and just as risky.
"""
import argparse, pathlib, subprocess, sys
import numpy as np
SR = 48000


def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def norm(x, db=-3):
    return (x / (np.abs(x).max() + 1e-9) * 10 ** (db / 20)).astype(np.float32)


def clang(r):
    n = int(1.4 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f, d, a in [(523, .5, 1), (1187, .35, .7), (1960, .22, .5), (2771, .15, .35), (3690, .08, .25)]:
        x += a * np.sin(2 * np.pi * f * t * (1 + .002 * np.sin(2 * np.pi * 7 * t))) * np.exp(-t / d)
    x += band(r.standard_normal(n), 1500, 9000) * env(n, .001, .02) * 1.5
    b = int(.28 * SR); x[b:] += .35 * x[:n - b]                      # a second, smaller bounce
    return x


def creak(r):
    n = int(.9 * SR); t = np.arange(n) / SR
    f = 230 + 140 * np.sin(2 * np.pi * .9 * t) + 30 * np.cumsum(r.standard_normal(n)) / np.sqrt(SR) * 8
    ph = 2 * np.pi * np.cumsum(f) / SR; saw = ((ph / (2 * np.pi)) % 1) * 2 - 1
    x = band(saw * (1 + .6 * (r.random(n) < .02)), 200, 2600)
    return x * np.sin(np.pi * np.clip(t / .9, 0, 1)) ** .7


def click(r):
    n = int(.25 * SR); x = np.zeros(n)
    for k, off in enumerate([0, .06]):
        i = int(off * SR); m = int(.03 * SR)
        x[i:i + m] += band(r.standard_normal(m), 900, 7000) * env(m, .0005, .006) * (1 - .4 * k)
    return x


def whoosh(r):
    n = int(1.6 * SR); t = np.arange(n) / SR; x = r.standard_normal(n); out = np.zeros(n); seg = 2048
    for i in range(0, n - seg, seg // 2):                             # a band that sweeps upward
        c = 300 + 2800 * (i / n) ** 1.5; w = np.hanning(seg)
        out[i:i + seg] += band(x[i:i + seg] * w, c * .6, c * 1.6)
    return out * np.sin(np.pi * t / 1.6) ** 1.5


def rustle(r):
    n = int(.7 * SR); t = np.arange(n) / SR
    am = np.repeat(r.random(int(n / 400) + 1), 400)[:n] ** 3
    return band(r.standard_normal(n), 2500, 12000) * am * np.sin(np.pi * t / .7)


def typewriter(r):
    n = int(3.2 * SR); x = np.zeros(n); tt = 0.1
    while tt < 2.7:
        i = int(tt * SR); m = int(.05 * SR)
        x[i:i + m] += (band(r.standard_normal(m), 700, 5000) + .5 * np.sin(2 * np.pi * 1800 * np.arange(m) / SR)) * env(m, .0005, .008)
        tt += .09 + r.random() * .14
    i = int(2.85 * SR); t = np.arange(int(.35 * SR)) / SR
    x[i:i + len(t)] += .6 * np.sin(2 * np.pi * 2350 * t) * np.exp(-t / .12)   # the carriage bell
    return x


def crickets(r):
    n = int(8 * SR); x = np.zeros(n); t = np.arange(int(.018 * SR)) / SR
    for voice in range(3):
        f = 4300 + voice * 380; tt = r.random() * .5
        while tt < 7.6:
            for k in range(3):
                i = int((tt + k * .035) * SR)
                if i + len(t) < n:
                    x[i:i + len(t)] += np.sin(2 * np.pi * f * t) * np.hanning(len(t)) * (.5 + .5 * r.random())
            tt += .45 + r.random() * .5
    return x * .6


def steps(r):
    n = int(4 * SR); x = np.zeros(n)
    for k in range(8):
        i = int((.2 + k * .48 + r.random() * .03) * SR); m = int(.12 * SR)
        x[i:i + m] += band(r.standard_normal(m), 60, 900) * env(m, .002, .025) * (.8 + .2 * r.random())
    return x


def tick(r):
    n = int(2 * SR); x = np.zeros(n)
    for k in range(2):
        i = int((.05 + k) * SR); m = int(.02 * SR)
        x[i:i + m] += band(r.standard_normal(m), 2000, 8000) * env(m, .0003, .003)
    return x


def pop(r):
    n = int(.3 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 - 1800 * t) * t) * np.exp(-t / .03) + band(r.standard_normal(n), 800, 6000) * env(n, .0005, .01)


def thud(r):
    n = int(.5 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 70 * t) * np.exp(-t / .09) + band(r.standard_normal(n), 40, 400) * env(n, .001, .03)


def chime(r):
    n = int(3 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f, a in [(1568, 1), (2093, .6), (2637, .4)]:
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t / 1.1)
    return x


def water(r):
    """A trickle of water: 11 s of band-limited noise with slow swells and droplet plinks."""
    n = int(11 * SR); t = np.arange(n) / SR
    x = band(r.standard_normal(n), 250, 5200) * (0.75 + 0.25 * np.sin(2 * np.pi * .23 * t) * np.sin(2 * np.pi * .11 * t + 1))
    for k in range(40):
        i = int(r.random() * (n - SR // 4)); m = int(.08 * SR); f = 900 + r.random() * 1800
        x[i:i + m] += .5 * np.sin(2 * np.pi * f * np.arange(m) / SR * (1 + np.arange(m) / m * .6)) * env(m, .001, .02)
    return x * np.minimum(1, t / .6) * np.minimum(1, (11 - t) / 1.5)


def purr(r):
    """A cat-like purr: low noise pulsed at ~25 Hz, breathing in and out."""
    n = int(2.2 * SR); t = np.arange(n) / SR
    x = band(r.standard_normal(n), 60, 700) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 25 * t)) * .8)
    breath = np.abs(np.sin(np.pi * t / 1.1)) ** .6
    return x * breath * np.sin(np.pi * t / 2.2)


def pencil(r):
    """Graphite on paper for a 3 s scrawl: scratchy bursts in looping strokes."""
    n = int(3.1 * SR); t = np.arange(n) / SR
    am = (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 2.6 * t + np.sin(2 * np.pi * .7 * t) * 2))) * (0.7 + 0.3 * r.random(n))
    return band(r.standard_normal(n), 1800, 9000) * am * np.minimum(1, t / .05) * np.minimum(1, (3.1 - t) / .2)


SOUNDS = dict(clang=clang, creak=creak, click=click, whoosh=whoosh, rustle=rustle, typewriter=typewriter,
              crickets=crickets, steps=steps, tick=tick, pop=pop, thud=thud, chime=chime, water=water, purr=purr, pencil=pencil)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="work/sfx"); a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for i, (name, fn) in enumerate(SOUNDS.items()):
        x = norm(fn(np.random.default_rng(1000 + i)))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(out / (name + ".wav"))],
                       input=x.tobytes(), check=True)
    print("wrote %d sounds to %s" % (len(SOUNDS), out.resolve()))
