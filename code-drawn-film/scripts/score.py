"""Music cues with Lyria 3.5 (Gemini API key from audio-producer), each checked by a listener model.

  py score.py --cues music/cues.json --out music [--only theme]

cues.json: [{"id": "theme", "prompt": "Instrumental only, no vocals. ...", "takes": 2}, ...]
Write prompts in English; say "Instrumental only, no vocals"; give length, tempo (BPM), key, instruments,
and a timestamped structure ("[0:00-0:12] ..."). Lyria cannot imitate named artists or copyrighted songs.
Every output carries a SynthID watermark. Results vary per call, so take 2 and keep the better one.
The listener returns vocals yes/no, instruments, tempo, mood, glitches and a 1-5 fit score.
"""
import argparse, base64, json, pathlib, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
_SK = pathlib.Path(__file__).resolve().parents[2]   # ~/.claude/skills: the voice module is "audio-producer"
for _d in ("audio-producer", "gemini-voice"):     # or "gemini-voice", a standalone build of audio-producer, if installed instead
    if (_SK / _d / "scripts" / "gemini_tts.py").exists():
        sys.path.insert(0, str(_SK / _d / "scripts")); break
import gemini_tts as gt

ASK = ("You are a film music supervisor. The brief for this cue was:\n{brief}\nListen and answer JSON only: "
       "{{\"has_vocals\": bool (ANY human voice: singing, humming, a wordless aah/ooh vocalise, choir; instruments that "
       "merely sound voice-like do not count), \"instruments\": [..], \"tempo_bpm\": int, \"mood\": \"...\", \"glitches\": [..], "
       "\"fits_brief_1to5\": int, \"note\": \"one sentence\"}}")


def envelope(p, hop_s=0.5):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", "8000", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32); h = int(8000 * hop_s)
    return np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-6 for i in range(0, len(x) - h, h)])


def match(p, target, dur):
    """Pearson correlation between the cue's loudness (dB per 0.5 s) over [0, dur] and a target intensity curve
    [[t, level 0..1], ...]. Listener models invent timestamps (one described a 104 s cue up to 145 s); this cannot."""
    import numpy as np
    e = 20 * np.log10(envelope(p)); n = min(len(e), int(dur / .5)); e = e[:n]
    tt = np.arange(n) * .5; ts, vs = zip(*target); goal = np.interp(tt, ts, vs)
    return float(np.corrcoef(e, goal)[0, 1]) if n > 4 else 0.0


def generate(prompt):
    r = gt._post("interactions", {"model": "lyria-3.5", "input": prompt}, timeout=600)
    audio = b"".join(base64.b64decode(c["data"]) for s in r.get("steps", []) for c in s.get("content", []) if c.get("type") == "audio" and c.get("data"))
    if not audio:
        raise RuntimeError("no audio: " + json.dumps(r)[:400])
    return audio


def listen(mp3, brief):
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mpeg", "data": base64.b64encode(mp3).decode()}},
                                    {"text": ASK.format(brief=brief)}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4000, "responseMimeType": "application/json"}}
    for _ in range(3):
        try:
            r = gt._post("models/gemini-3.5-flash:generateContent", body)
            return json.loads(re.search(r"\{.*\}", "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"]), re.S).group(0))
        except Exception as e:
            err = str(e); time.sleep(4)
    return {"fits_brief_1to5": 0, "note": "listener failed: " + err}


def seconds(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cues", required=True); ap.add_argument("--out", default="music")
    ap.add_argument("--only", nargs="*"); a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    cues = json.loads(pathlib.Path(a.cues).read_text(encoding="utf-8")); rep_p = out / "cues_report.json"
    rep = json.loads(rep_p.read_text(encoding="utf-8")) if rep_p.exists() else {}
    for c in cues:
        if a.only and c["id"] not in a.only:
            continue
        best = None
        for k in range(1, c.get("takes", 2) + 1):
            p = out / ("%s_t%d.mp3" % (c["id"], k))
            if not p.exists():
                try:
                    p.write_bytes(generate(c["prompt"])); time.sleep(3)
                except Exception as e:                         # a refused prompt is not transient: report, move on
                    body = e.read().decode("utf-8", "replace")[:300] if hasattr(e, "read") else str(e)
                    print("  %-12s take %d  REFUSED/FAILED: %s" % (c["id"], k, body), flush=True); continue
            L = listen(p.read_bytes(), c["prompt"]); s = (L.get("fits_brief_1to5") or 0) - (3 if L.get("has_vocals") else 0)
            if c.get("target"):
                L["target_corr"] = round(match(p, c["target"], c.get("dur", seconds(p))), 3); s = L["target_corr"] * 5 - (3 if L.get("has_vocals") else 0)
            print("  %-12s take %d  %.1fs  fit=%s vocals=%s corr=%s  %s" % (c["id"], k, seconds(p), L.get("fits_brief_1to5"), L.get("has_vocals"), L.get("target_corr"), L.get("note", "")[:80]), flush=True)
            if best is None or s > best[0]:
                best = (s, p, L)
        if best is None:
            print("  %-12s NO CUE - rewrite the prompt" % c["id"]); continue
        final = out / (c["id"] + ".mp3"); final.write_bytes(best[1].read_bytes())
        rep[c["id"]] = {"chosen": best[1].name, "seconds": round(seconds(final), 2), "listen": best[2]}
        rep_p.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print("cues read from", a.cues, "->", rep_p)


if __name__ == "__main__":
    main()
