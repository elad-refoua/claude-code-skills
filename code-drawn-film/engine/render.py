"""Headless renderer for a code-drawn film (Playwright + Chromium + ffmpeg).

Every frame is window.renderFrame(t) in src/studio.html, a pure function of t, so frames render in
parallel, out of order, resumably. Each worker is its own Chromium process (file:// pages can share a
renderer process, which would serialise them).

  py render.py stills  --t 3.5 12 40.2                 -> work/check/still_<t>.jpg
  py render.py sheet   --t 10 10.5 11 11.5 --cols 4    -> work/check/sheet.jpg (ms/frame printed on it)
  py render.py sheet   --from 30 --to 45 --every 0.5   -> a contact sheet of one chapter
  py render.py frames  --from 0 --to 300 --workers 6   -> work/frames/f000000.jpg ... (skips existing)
  py render.py frames  --from 30 --to 45 --force        -> re-render one chapter
  py render.py encode  --audio work/mix.wav --out out/final.mp4
  py render.py clip    --from 30 --to 45 --audio work/mix.wav --out work/check/clip.mp4

Run from the film project root (the folder that has src/studio.html). Prints which studio it read.
"""
import argparse, base64, io, math, multiprocessing as mp, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path.cwd()
STUDIO = ROOT / "src" / "studio.html"
FRAMES = ROOT / "work" / "frames"
CHECK = ROOT / "work" / "check"
ARGS = ["--allow-file-access-from-files", "--disable-gpu", "--disable-renderer-backgrounding",
        "--disable-background-timer-throttling", "--force-color-profile=srgb", "--font-render-hinting=none"]


def open_studio(pw):
    b = pw.chromium.launch(headless=True, args=ARGS)
    pg = b.new_page(viewport={"width": 1920, "height": 1200}, device_scale_factor=1)
    pg.goto(STUDIO.as_uri() + "?headless=1")
    pg.wait_for_function("window.__ready === true || !!window.__error", timeout=120000)
    err = pg.evaluate("window.__error || null")
    if err:
        raise RuntimeError("studio failed to load: " + err)
    return b, pg


def grab(pg, t, q=0.95):
    r = pg.evaluate("([t,q]) => window.renderFrame(t, q)", [t, q])
    return base64.b64decode(r["data"].split(",", 1)[1]), r["shot"], r["ms"]


def fps_dur(pg):
    return pg.evaluate("[FILM.fps, FILM.dur]")


def _worker(k, n, idx, fps, force, q, report):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b, pg = open_studio(pw)
        done = 0
        for i in idx[k::n]:
            f = FRAMES / ("f%06d.jpg" % i)
            if f.exists() and not force:
                continue
            data, shot, ms = grab(pg, i / fps, q)
            tmp = f.with_suffix(".tmp")
            tmp.write_bytes(data); os.replace(tmp, f)
            done += 1
            if done % 48 == 0:
                report.put((k, i, ms))
        b.close()
    report.put((k, -1, 0))


def cmd_frames(a):
    from playwright.sync_api import sync_playwright
    FRAMES.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b, pg = open_studio(pw); fps, dur = fps_dur(pg); b.close()
    t1 = dur if a.to is None else min(a.to, dur)
    idx = list(range(int(round(a.frm * fps)), int(math.ceil(t1 * fps))))
    print("studio:", STUDIO, "| fps", fps, "| frames", idx[0], "..", idx[-1], "(%d)" % len(idx), "| workers", a.workers)
    q = mp.Queue(); ps = [mp.Process(target=_worker, args=(k, a.workers, idx, fps, a.force, a.q, q)) for k in range(a.workers)]
    t0 = time.time(); [p.start() for p in ps]; alive = a.workers
    while alive:
        k, i, ms = q.get()
        if i < 0:
            alive -= 1
        else:
            print("  worker %d at frame %d (%.2fs)  %.0f ms/frame  elapsed %.0fs" % (k, i, i / fps, ms, time.time() - t0), flush=True)
    [p.join() for p in ps]
    missing = [i for i in idx if not (FRAMES / ("f%06d.jpg" % i)).exists()]
    print("frames present: %d/%d, missing %d, %.0fs" % (len(idx) - len(missing), len(idx), len(missing), time.time() - t0))
    if missing:
        sys.exit(1)


def times_from(a):
    if a.t:
        return [float(x) for x in a.t]
    n = int(round((a.to - a.frm) / a.every)) + 1
    return [round(a.frm + i * a.every, 3) for i in range(n)]


def cmd_stills(a):
    from playwright.sync_api import sync_playwright
    CHECK.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b, pg = open_studio(pw)
        for t in times_from(a):
            data, shot, ms = grab(pg, t, 0.95)
            p = CHECK / ("still_%07.2f.jpg" % t); p.write_bytes(data)
            print("%s  t=%.2f  shot=%s  %.0f ms" % (p, t, shot, ms))
        b.close()


def cmd_sheet(a):
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw
    CHECK.mkdir(parents=True, exist_ok=True)
    ts = times_from(a); cols = a.cols; w = a.w; h = int(w * 9 / 16)
    rows = math.ceil(len(ts) / cols)
    sheet = Image.new("RGB", (cols * w, rows * (h + 22)), (20, 18, 16)); d = ImageDraw.Draw(sheet)
    with sync_playwright() as pw:
        b, pg = open_studio(pw)
        for n, t in enumerate(ts):
            data, shot, ms = grab(pg, t, 0.9)
            im = Image.open(io.BytesIO(data)).convert("RGB").resize((w, h), Image.LANCZOS)
            x, y = (n % cols) * w, (n // cols) * (h + 22)
            sheet.paste(im, (x, y)); d.text((x + 6, y + h + 4), "%.2fs  %s  %.0fms" % (t, shot, ms), fill=(230, 220, 200))
        b.close()
    out = pathlib.Path(a.out) if a.out else CHECK / "sheet.jpg"
    sheet.save(out, quality=88); print("sheet:", out, "| %d frames from %s" % (len(ts), STUDIO))


def cmd_encode(a):
    n = len(list(FRAMES.glob("f*.jpg")))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats", "-framerate", str(a.fps), "-i", str(FRAMES / "f%06d.jpg")]
    if a.audio:
        cmd += ["-i", a.audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "256k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out]
    print("encoding %d frames from %s + audio %s -> %s" % (n, FRAMES, a.audio, a.out))
    subprocess.run(cmd, check=True)


def cmd_clip(a):
    from playwright.sync_api import sync_playwright
    CHECK.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b, pg = open_studio(pw); fps, dur = fps_dur(pg)
        ff = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-"]
        if a.audio:
            ff += ["-ss", str(a.frm), "-t", str(a.to - a.frm), "-i", a.audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-shortest"]
        ff += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", a.out]
        p = subprocess.Popen(ff, stdin=subprocess.PIPE)
        for i in range(int(round(a.frm * fps)), int(round(a.to * fps))):
            data, _, _ = grab(pg, i / fps, 0.9); p.stdin.write(data)
        p.stdin.close(); p.wait(); b.close()
    print("clip:", a.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["frames", "stills", "sheet", "encode", "clip"])
    ap.add_argument("--t", nargs="*"); ap.add_argument("--from", dest="frm", type=float, default=0.0)
    ap.add_argument("--to", type=float); ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--cols", type=int, default=4); ap.add_argument("--w", type=int, default=480)
    ap.add_argument("--workers", type=int, default=6); ap.add_argument("--force", action="store_true")
    ap.add_argument("--q", type=float, default=0.95); ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--crf", type=int, default=16); ap.add_argument("--audio"); ap.add_argument("--out")
    a = ap.parse_args()
    {"frames": cmd_frames, "stills": cmd_stills, "sheet": cmd_sheet, "encode": cmd_encode, "clip": cmd_clip}[a.cmd](a)
