"""Gates on the FINISHED film file (not on the code): a check that reads the artifact it names.

  py check_film.py --film out/final.mp4 [--timeline work/timeline.json] [--dead 1.5] [--allow-still 0-3.5,290-300] [--fps 30]

Checks, each printed PASS/FAIL with the number behind it:
  1. the file opens; duration, fps, resolution, an audio stream (and duration matches the timeline)
  2. no dead picture: every window of `--dead` seconds has motion (mean abs frame difference on a 96x54
     grey proxy) above a floor, except the ranges passed in --allow-still (deliberate holds)
  3. no black or blown frames (mean luma outside 12..245)
  4. loudness: integrated -18..-13 LUFS, true peak below -1.0 dBTP
  5. narration placement (with --timeline): clips do not overlap and all end inside the film
Also writes a whole-film contact sheet (one frame per 4 s) next to the film for a human look.
"""
import argparse, json, pathlib, re, subprocess, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")


def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = [s for s in j["streams"] if s["codec_type"] == "audio"]
    num, den = v["r_frame_rate"].split("/")
    return float(j["format"]["duration"]), float(num) / float(den), int(v["width"]), int(v["height"]), bool(a)


def ranges(s):
    out = []
    for part in (s or "").split(","):
        if part.strip():
            a, b = part.split("-"); out.append((float(a), float(b)))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--film", required=True); ap.add_argument("--timeline")
    ap.add_argument("--dead", type=float, default=1.5); ap.add_argument("--floor", type=float, default=0.35)
    ap.add_argument("--allow-still", default=""); ap.add_argument("--fps", type=float, default=24)
    a = ap.parse_args()
    film = pathlib.Path(a.film); results = []
    dur, fps, w, h, has_audio = probe(film)
    print("checking", film.resolve(), "| %.2fs %sfps %dx%d audio=%s" % (dur, fps, w, h, has_audio))
    ok = has_audio and w == 1920 and h == 1080 and abs(fps - a.fps) < .01
    if a.timeline:
        tl = json.loads(pathlib.Path(a.timeline).read_text(encoding="utf-8")); ok = ok and abs(tl["dur"] - dur) < 0.25
    results.append(("container", ok, "%.2fs, %gfps, %dx%d, audio=%s" % (dur, fps, w, h, has_audio)))

    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(film), "-vf", "scale=96:54,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 54, 96).astype(np.float32)
    luma = fr.mean(axis=(1, 2)); diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    allow = ranges(a.allow_still); win = max(1, int(a.dead * fps)); dead = []
    for i in range(0, len(diff) - win):
        t0 = i / fps
        if any(x <= t0 and t0 + a.dead <= y for x, y in allow):
            continue
        if diff[i:i + win].max() < a.floor:
            dead.append(round(t0, 2))
    results.append(("no dead %.1fs windows" % a.dead, not dead, "%d dead windows%s" % (len(dead), (", first at %.2fs" % dead[0]) if dead else "")))
    bad = [round(i / fps, 2) for i, v in enumerate(luma) if v < 12 or v > 245]
    bad = [x for x in bad if not any(p <= x <= q for p, q in allow)]
    results.append(("no black/blown frames", not bad, "%d frames%s" % (len(bad), (", first at %.2fs" % bad[0]) if bad else "")))

    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(film), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", m)[-1]); TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", m)[-1])
    results.append(("loudness", -18 <= I <= -13 and TP < -1.0, "I=%.1f LUFS, true peak=%.1f dBTP" % (I, TP)))

    # hiss/buzz: a synthesized noise effect heard alone (a previous build, 2026-09-26: the opening pencil scratch was
    # 70-80% of the mix's energy in 2-9 kHz for 3 s and read as an unpleasant buzz). Flag > 1 s above a 0.5 share.
    au = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(film), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"],
                                      capture_output=True, check=True).stdout, np.float32)
    h = 12000; share = []
    for i in range(0, len(au) - h, h):
        X = np.abs(np.fft.rfft(au[i:i + h])); f = np.fft.rfftfreq(h, 1 / 24000)
        loud = np.sqrt(np.mean(au[i:i + h] ** 2)) > 10 ** (-45 / 20)
        share.append(float(X[(f > 2000) & (f < 9000)].sum() / (X.sum() + 1e-9)) if loud else 0.0)
    buzz = [i * .5 for i in range(len(share) - 2) if min(share[i:i + 3]) > .5]
    results.append(("no hiss/buzz stretch", not buzz, "%d windows over 0.5 hiss share%s" % (len(buzz), (", first at %.1fs" % buzz[0]) if buzz else "")))

    if a.timeline:
        nar = sorted(tl.get("narration", []), key=lambda c: c["t"]); over = []
        for c in nar:
            c["end"] = c["t"] + float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", c["file"]],
                                                    capture_output=True, text=True).stdout.strip())
        for x, y in zip(nar, nar[1:]):
            if y["t"] < x["end"]:
                over.append(pathlib.Path(x["file"]).stem)
        late = [pathlib.Path(c["file"]).stem for c in nar if c["end"] > dur]
        results.append(("narration placement", not over and not late, "%d clips, overlaps=%s, past end=%s" % (len(nar), over or "none", late or "none")))

    sheet = film.with_name(film.stem + "_sheet.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(film), "-vf", "fps=1/4,scale=320:-1,tile=8x%d" % max(1, int(dur / 4 / 8) + 1), "-frames:v", "1", str(sheet)])
    for name, passed, detail in results:
        print("%-24s %s  %s" % (name, "PASS" if passed else "FAIL", detail))
    print("contact sheet:", sheet)
    sys.exit(0 if all(p for _, p, _ in results) else 1)


if __name__ == "__main__":
    main()
