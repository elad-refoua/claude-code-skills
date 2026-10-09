"""Narration for a film: one designed Gemini 3.8 voice, every line gated, cached, trimmed.

  py narrate.py --lines script/lines.json --voice voice_xxx --out work/voice [--cps-min 4.0] [--only id1 id2]
                [--voice-desc "an elderly man"]

lines.json: [{"id": "s03_can", "text": "...<short pause>...", "style": null, "names": ["ירושלים"]}, ...]
Lines may be Hebrew or English. --voice-desc (optional) makes the listener deduct for a take that does not
sound like that voice.
Writes work/voice/<id>.wav (24 kHz mono, edge silence trimmed to 60 ms) and work/voice/manifest.json
with the duration, chosen take, gate report and listener score of every line.

The IRON gate from audio-producer, per take: (1) speaking rate plausible, (2) >= 90% of the words heard in
a transcript (with Hebrew spelling variants and number words normalised), (3) every name heard, and
(4) a listener model scores the take 1-5 against the exact script. Up to 3 takes; the best passing take
wins; a line with no passing take is reported as FAILED and the script exits non-zero.
"""
import argparse, base64, hashlib, json, pathlib, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
_SK = pathlib.Path(__file__).resolve().parents[2]   # ~/.claude/skills: the voice module is "audio-producer"
for _d in ("audio-producer", "gemini-voice"):     # or "gemini-voice", a standalone build of audio-producer, if installed instead
    if (_SK / _d / "scripts" / "gemini_tts.py").exists():
        sys.path.insert(0, str(_SK / _d / "scripts")); break
import gemini_tts as gt

NIQQUD = re.compile(r"[\u0591-\u05C7]")
VARIANTS = {"הכול": "הכל", "מאוד": "מאד", "כול": "כל", "אמא": "אמא"}
NUMBER_WORDS = set("אחד אחת שתיים שניים שלוש שלושה ארבע ארבעה חמש חמישה שש שישה שבע שבעה שמונה תשע תשעה עשר עשרים "
                   "שלושים ארבעים חמישים שישים שבעים שמונים תשעים מאה מאות אלף ותשע ושבע ושמונה ושש וחמש וארבע ושלוש ושתיים ואחת "
                   "ותשעה ושבעה "
                   "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
                   "seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand".split())
LISTEN = ("You are a strict audio QC listener. The audio should say EXACTLY this script (angle-bracket tags are "
          "performance cues, not words):\n{script}\nListen and answer JSON only: {{\"score\": 1-5, \"problems\": [\"...\"]}}. "
          "Score 5 = every word right, natural, no glitches. Deduct for: garbled or invented words, a wrong or missing word, "
          "a tag read aloud as a word, stutters or loops, clipped endings, wrong language, robotic delivery{voice}.")


def norm(s):
    s = NIQQUD.sub("", re.sub(r"<[^>]+>", " ", s)).lower()     # Latin is lower-cased; Hebrew has no case
    words = re.findall(r"[\u05D0-\u05EAa-z]+", s)        # Hebrew and Latin letters
    return [VARIANTS.get(w, w) for w in words]


def gate(wav, text, names, cps_min):
    secs = gt.wav_seconds(wav)
    spoken = NIQQUD.sub("", re.sub(r"<[^>]+>", " ", text))
    rate = len(re.sub(r"\s+", "", spoken)) / secs
    heard_raw = gt.transcribe(wav)
    heard = " ".join(norm(heard_raw))
    has_digits = bool(re.search(r"\d", heard_raw))
    words = [w for w in norm(text) if len(w) > 2]
    skel = lambda x: re.sub("[יו]", "", x)   # defective vs plene spelling: niqqud-stripped "לטוף" is "ליטוף"
    missing = [w for w in words if w not in heard and skel(w) not in skel(heard) and not (has_digits and w in NUMBER_WORDS)]
    hit = 1 - len(missing) / max(1, len(words))
    names_missing = [n for n in names if VARIANTS.get(n, n).lower() not in heard]
    ok = cps_min <= rate <= 26 and hit >= 0.9 and not names_missing
    return ok, {"seconds": round(secs, 2), "cps": round(rate, 1), "hit": round(hit, 3), "missing": missing,
                "names_missing": names_missing, "transcript": heard_raw}


def listen(wav, text, voice_desc=None):
    voice = (", a voice that does not sound like this description: " + voice_desc) if voice_desc else ""
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(wav).decode()}},
                                    {"text": LISTEN.format(script=text, voice=voice)}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4000, "responseMimeType": "application/json"}}
    for attempt in range(3):
        try:
            r = gt._post("models/gemini-3.5-flash:generateContent", body)
            txt = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
            return json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
        except Exception as e:
            err = str(e); time.sleep(4)
    return {"score": 0, "problems": ["listener failed: " + err]}


def trim(wav_bytes, out_path, pad=0.06):
    """Cut leading/trailing silence (below -45 dB) and leave `pad` seconds each side."""
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=%.2f,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=%.2f,areverse" % (pad, pad))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "-", "-af", af, "-ar", "24000", "-ac", "1", str(out_path)],
                   input=wav_bytes, check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)],
                       capture_output=True, text=True, check=True).stdout.strip()
    return float(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True); ap.add_argument("--voice", required=True)
    ap.add_argument("--out", default="work/voice"); ap.add_argument("--cps-min", type=float, default=4.0)
    ap.add_argument("--takes", type=int, default=3); ap.add_argument("--only", nargs="*")
    ap.add_argument("--voice-desc", help='optional, e.g. "an elderly man": the listener deducts for a take that does not match it')
    a = ap.parse_args()
    out = pathlib.Path(a.out); cache = out / "cache"; cache.mkdir(parents=True, exist_ok=True)
    lines = json.loads(pathlib.Path(a.lines).read_text(encoding="utf-8"))
    man_p = out / "manifest.json"
    man = json.loads(man_p.read_text(encoding="utf-8")) if man_p.exists() else {}
    print("lines from", a.lines, "| voice", a.voice, "|", len(lines), "lines")
    failed = []
    for ln in lines:
        if a.only and ln["id"] not in a.only:
            continue
        style = ln.get("style"); text = ln["text"]
        h = hashlib.sha1(json.dumps([a.voice, style, text, gt.DEFAULT_MODEL], ensure_ascii=False).encode()).hexdigest()[:16]
        if man.get(ln["id"], {}).get("hash") == h and (out / (ln["id"] + ".wav")).exists():
            print("  %-16s cached  %.2fs" % (ln["id"], man[ln["id"]]["duration"])); continue
        best = None
        for take in range(1, a.takes + 1):
            cp = cache / ("%s_%s_t%d.wav" % (ln["id"], h, take))
            if cp.exists():
                wav = cp.read_bytes()
            else:
                for attempt in range(4):                      # 429/5xx are transient: back off and retry
                    try:
                        wav, _ = gt.synthesize(text, voice=a.voice, style=style); break
                    except Exception as e:
                        if attempt == 3 or not any(c in str(e) for c in ("429", "500", "502", "503", "504", "timed out")):
                            raise
                        time.sleep(10 * (attempt + 1))
                cp.write_bytes(wav); time.sleep(2)
            ok, rep = gate(wav, text, ln.get("names", []), a.cps_min)
            ls = listen(wav, text, a.voice_desc) if ok else {"score": 0, "problems": ["gate failed"]}
            score = ls.get("score", 0) or 0
            print("  %-16s take %d  gate=%s  cps=%.1f hit=%.2f  listen=%s  %s" % (ln["id"], take, ok, rep["cps"], rep["hit"], score,
                  (rep["missing"] + rep["names_missing"] + ls.get("problems", []))[:3]), flush=True)
            cand = {"take": take, "ok": ok, "score": score, "gate": rep, "listen": ls, "path": cp}
            if ok and (best is None or score > best["score"]):
                best = cand
            if ok and score >= 5:
                break
        if not best or best["score"] < 4:
            failed.append(ln["id"])
            print("  %-16s FAILED (best listener score %s)" % (ln["id"], best["score"] if best else "none"))
            if not best:
                continue
        dur = trim(best["path"].read_bytes(), out / (ln["id"] + ".wav"))
        man[ln["id"]] = {"hash": h, "duration": round(dur, 3), "take": best["take"], "score": best["score"],
                         "gate": best["gate"], "problems": best["listen"].get("problems", []), "text": text}
        man_p.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(v["duration"] for v in man.values())
    print("manifest: %s | %d lines | %.1fs of narration | failed: %s" % (man_p, len(man), total, failed or "none"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
