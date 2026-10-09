"""Hebrew (or any) subtitles from the narration timing, as an ASS file, and an optional burned-in copy.

  py subs.py --timing src/timing.js --out work/subs.ass [--burn out/final.mp4 --to out/final_subs.mp4]

MEASURED 2026-09-25: libass on the build machine laid a Hebrew line out LEFT-to-right unless told otherwise:
the final period lands on the right and "1950–2020" reads "2020–1950". Each line is therefore wrapped in
RLE...PDF (U+202B/U+202C) and every digit run in LRI...PDI (U+2066/U+2069). Tags <...> are removed.
"""
import argparse, json, pathlib, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def rtl(line):
    line = re.sub(r"[0-9][0-9–\-.:/,]*[0-9]|[0-9]", lambda m: "⁦" + m.group(0) + "⁩", line)
    return "‫" + line + "‬"


def wrap(text, width=38):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return "\\N".join(rtl(x) for x in lines)


ap = argparse.ArgumentParser(); ap.add_argument("--timing", default="src/timing.js"); ap.add_argument("--out", default="work/subs.ass")
ap.add_argument("--font", default="David"); ap.add_argument("--size", type=int, default=56)
ap.add_argument("--burn"); ap.add_argument("--to"); a = ap.parse_args()
js = pathlib.Path(a.timing).read_text(encoding="utf-8")
T = json.loads(js[js.index("=") + 1:].rstrip().rstrip(";"))
ev = []
for lid, L in sorted(T["lines"].items(), key=lambda kv: kv[1]["t0"]):
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", L["text"])).strip()
    text = re.sub(r"[֑-ׇ]", "", text).replace("...", "…")
    # one subtitle per sentence, timed in proportion to its length inside the spoken line
    parts = [x.strip() for x in re.split(r"(?<=[.?!…])\s+", text) if x.strip()]
    tot, t = sum(len(x) for x in parts), L["t0"]
    for i, x in enumerate(parts):
        d = (L["t1"] - L["t0"]) * len(x) / tot
        ev.append("Dialogue: 0,%s,%s,Sub,,0,0,0,,%s" % (ts(t), ts(t + d + (0.3 if i == len(parts) - 1 else 0.05)), wrap(x)))
        t += d
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,%s,%d,&H00F4EEE6,&H000000FF,&H00182028,&H64000000,0,0,0,0,100,100,0,0,1,3,1,2,160,160,64,177

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (a.font, a.size)
pathlib.Path(a.out).write_text(head + "\n".join(ev) + "\n", encoding="utf-8-sig")
print("subs: %s | %d lines from %s" % (a.out, len(ev), a.timing))
if a.burn:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.burn, "-vf", "ass=" + a.out.replace("\\", "/"), "-c:v", "libx264",
                    "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", a.to], check=True)
    print("burned:", a.to)
