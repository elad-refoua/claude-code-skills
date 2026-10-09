# -*- coding: utf-8 -*-
"""gemini_tts.py - the ONE place that knows how to call Gemini TTS. Every script imports this.

Why it exists (2026-09-24). Gemini 3.8 Flash TTS changed three things at once, and each one breaks
the old copy-pasted TTS code in its own way:
  1. It returns a finished WAV file (RIFF header, 24 kHz). The old code wrapped the bytes in a
     second WAV header, so the first 44 bytes of every clip were a header played as audio.
  2. Google's docs say 3.8 treats input text as a VERBATIM transcript: delivery instructions go in a
     separate `speech_metadata.style` field (Interactions API), not in the text. On the legacy
     endpoint the old "directions --- text" prompt was not read aloud when tested on 2026-09-24,
     but that is undocumented behaviour, so this module uses the documented path for 3.8.
  3. Inline vocal tags are angle brackets: <laugh> <sigh> <short pause> ... (3.1 used [laughs]).
So: one function, `synthesize()`, that takes the text and the style separately and always returns
WAV bytes with exactly one header - for 3.8 and for 3.1 alike.

Usage as a module:
    sys.path.insert(0, os.path.expanduser("~/.claude/skills/audio-producer/scripts"))
    from gemini_tts import synthesize, wav_to_mp3, DEFAULT_MODEL
    wav, seconds = synthesize("שלום לכולם", voice="Kore", style="warm, calm narrator")
    wav_to_mp3(wav, "out.mp3")

CLI:
    python -X utf8 gemini_tts.py --text "..." --voice Kore --style "..." --out clip.mp3 [--model ...]
    python -X utf8 gemini_tts.py --voices [--lang en-GB]      # the extended voice library
    python -X utf8 gemini_tts.py --check                       # real calls; exit 0 = PASS, 1 = FAIL

The API key: $GEMINI_VOICE_API_KEY, else $GEMINI_API_KEY (environment variables only).
Custom voices live in the project of the key that made them - see api_key(). Never printed.
"""
import argparse
import base64
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import wave

DEFAULT_MODEL = "gemini-3.8-flash-tts"          # GA, 30 prebuilt voices, 130 languages incl. Hebrew
LITE_MODEL = "gemini-3.8-flash-lite-tts"        # cheaper/faster, 101 languages incl. Hebrew
FALLBACK_MODEL = "gemini-3.1-flash-tts-preview"  # the previous default; legacy request shape
QC_MODEL = "gemini-3.5-flash"                    # audio in -> transcript out, for --check
BASE = "https://generativelanguage.googleapis.com/v1beta/"
RATE = 24000


def api_key():
    """Custom voices (cloned and designed) belong to ONE Google project and are invisible to a key from any
    other project (measured 2026-09-25: a key from another project got 404 on existing custom voices). So the
    voice project's key wins: $GEMINI_VOICE_API_KEY first, and only then a general $GEMINI_API_KEY (which may
    belong to another project)."""
    k = os.environ.get("GEMINI_VOICE_API_KEY")
    if k:
        return k
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    raise RuntimeError("no Gemini key: set the environment variable GEMINI_API_KEY (or GEMINI_VOICE_API_KEY "
                       "for the Google project that holds your custom voices). Get a key at "
                       "https://aistudio.google.com/apikey")


def _post(path, body, timeout=180):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode("utf-8"),
                                 headers={"x-goog-api-key": api_key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(path, timeout=60):
    req = urllib.request.Request(BASE + path, headers={"x-goog-api-key": api_key()})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def as_wav(raw, rate=RATE):
    """Exactly one WAV header, whatever the model sent: 3.8 sends WAV, 3.1 sends raw 16-bit PCM."""
    if raw[:4] == b"RIFF":
        return raw
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(raw)
    return bio.getvalue()


def wav_seconds(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes)) as w:
        return w.getnframes() / float(w.getframerate())


def synthesize(text, voice="Kore", style=None, model=DEFAULT_MODEL, timeout=180):
    """Return (wav_bytes, seconds). `text` is spoken verbatim; `style` is HOW it is spoken.

    Never put delivery instructions inside `text` - pass them as `style`.
    `voice` is a prebuilt name (Kore, Sulafat, ...) or a library / designed voice id.
    """
    if model.startswith("gemini-3.8"):
        item = {"type": "text", "text": text}
        if style:
            item["annotations"] = [{"type": "speech_metadata", "style": style}]
        body = {"model": model,
                "input": [{"type": "user_input", "content": [item]}],
                "response_format": {"type": "audio"},
                "generation_config": {"speech_config": [{"voice": voice}]}}
        r = _post("interactions", body, timeout)
        raw = b""
        for step in r.get("steps", []):
            for c in step.get("content", []):
                if c.get("type") == "audio" and c.get("data"):
                    raw += base64.b64decode(c["data"])
        if not raw:  # the documented top-level field, in case the response shape moves
            oa = r.get("output_audio") or {}
            raw = base64.b64decode(oa.get("data", "")) if oa.get("data") else b""
    else:
        prompt = (style.strip() + "\n---\n" + text) if style else text
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        r = _post("models/%s:generateContent" % model, body, timeout)
        if "candidates" not in r:  # a blocked prompt: promptFeedback and no candidates
            fb = r.get("promptFeedback", {})
            raise RuntimeError("BLOCKED by Gemini: %s - rephrase the text, it is not transient"
                               % fb.get("blockReason", fb or "no candidates"))
        raw, rate = b"", RATE
        for p in r["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                raw += base64.b64decode(p["inlineData"]["data"])
                mt = p["inlineData"].get("mimeType", "")
                if "rate=" in mt:
                    rate = int(mt.split("rate=")[1].split(";")[0])
        if raw[:4] != b"RIFF":
            raw = as_wav(raw, rate)
    if not raw:
        raise RuntimeError("no audio in the %s response (status %s) - possibly BLOCKED; rephrase"
                           % (model, r.get("status", "?")))
    wav = as_wav(raw)
    return wav, wav_seconds(wav)


def wav_to_mp3(wav_bytes, mp3_path, qscale="2"):
    """Write an MP3 via ffmpeg. Returns the path."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        t.write(wav_bytes)
        tmp = t.name
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame",
                        "-qscale:a", qscale, str(mp3_path)], check=True, capture_output=True)
    finally:
        os.remove(tmp)
    return str(mp3_path)


def list_voices(lang=None, gender=None, pitch=None, persona=None, context=None, voice_type=None,
                search=None, page_size=1000, all_pages=True):
    """The Extended Voice Library (+ your own designed/replicated voices, newest first).

    Params are the documented snake_case ones; a list means OR, different params mean AND.
    2,089 prebuilt voices on 2026-09-24 over 3 pages - none in Hebrew. Pass all_pages=False for one page.
    """
    import urllib.parse
    params = {"page_size": page_size}
    for k, v in (("language_code", lang), ("gender", gender), ("pitch", pitch), ("persona", persona),
                 ("context", context), ("type", voice_type), ("search", search)):
        if v:
            params[k] = v
    out, tok = [], None
    while True:
        p = dict(params, **({"page_token": tok} if tok else {}))
        d = _get("voices?" + urllib.parse.urlencode(p, doseq=True))
        out += d.get("voices", [])
        tok = d.get("next_page_token") or d.get("nextPageToken")
        if not tok or not all_pages:
            return out


def design_voice(description, display_name, gender=None, language_code="he-IL", model=DEFAULT_MODEL):
    """Voice design: a persistent custom voice from a 1-2 sentence description.

    Returns (voice_id, sample_wav_bytes). Tested in Hebrew on 2026-09-24 (he-IL accepted; the
    60 s sample was natural Hebrew). Lives 1 year; 200 custom voices per project. Put permanent
    traits (age, gender, timbre, accent) HERE, never in `style`.
    """
    voice = {"model": model, "type": "prompted", "display_name": display_name,
             "language_code": language_code, "prompted": {"input": description}}
    if gender:
        voice["gender"] = gender
    r = _post("voices", {"store": True, "voice": voice}, timeout=300)
    sa = r.get("sample_audio") or {}
    return r.get("id"), (base64.b64decode(sa["data"]) if sa.get("data") else b"")


def _to_wav24(path):
    """Any recording (m4a, mp3, ogg, wav...) -> 24 kHz mono 16-bit WAV bytes, via ffmpeg."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        tmp = t.name
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "24000",
                        "-sample_fmt", "s16", tmp], check=True, capture_output=True)
        return pathlib.Path(tmp).read_bytes()
    finally:
        os.remove(tmp)


def replicate_voice(reference_audio, consent_audio, display_name, store=True, model=DEFAULT_MODEL):
    """Voice replication (cloning) - ONLY the speaker's own voice, with their own recorded consent.

    reference_audio: 10-30 s of clean natural speech (any format; converted to 24 kHz mono WAV).
    consent_audio: the SAME speaker, same mic and room, reciting Google's consent sentence
    verbatim in one of its 30 locales - Hebrew is NOT one of them, so use English:
      "I am the owner of this voice and I consent to Google using this voice to create a
       synthetic voice model."
    Returns the voice id (voice_..., store=True, 1 year) or key (voicekey_..., store=False, 7 days).
    Body exactly as documented (voices.create, type "replicated", source_audio + consent_audio).
    """
    def b64(p):
        return base64.b64encode(_to_wav24(p)).decode()
    voice = {"model": model, "type": "replicated", "display_name": display_name,
             "replicated": {"source_audio": {"mime_type": "audio/wav", "data": b64(reference_audio)},
                            "consent_audio": {"mime_type": "audio/wav", "data": b64(consent_audio)}}}
    r = _post("voices", {"store": store, "voice": voice}, timeout=300)
    return r.get("id") or r.get("key") or r


def delete_voice(voice_id):
    req = urllib.request.Request(BASE + "voices/" + voice_id, headers={"x-goog-api-key": api_key()},
                                 method="DELETE")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status


def transcribe(wav_bytes):
    body = {"contents": [{"parts": [
        {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(wav_bytes).decode()}},
        {"text": "Transcribe this audio exactly, word for word, in the language spoken. Output only the transcript."}]}]}
    r = _post("models/%s:generateContent" % QC_MODEL, body)
    return r["candidates"][0]["content"]["parts"][0]["text"].strip()


def gate(wav_bytes, text, names=(), min_hit=0.9, cps=(6, 26)):
    """The IRON audio gate for one take: speaking rate plausible, >= min_hit of the content words heard, and
    EVERY name heard as often as it is written. A name gets its own test because a 90% word match lets a
    swapped name through (2026-09-24: a sentence-initial name was spoken as another name and the take passed).
    Niqqud and <tags> are for the voice, so they are stripped before comparing. Returns (ok, report)."""
    # niqqud off, and doubled yod/vav collapsed: "עניין" and "ענין" are one word in two spellings, not a miss
    plain = lambda s: re.sub(r"(י)י+|(ו)ו+", r"\1\2", re.sub(r"[֑-ׇ]", "", s))  # noqa: E731
    spoken = plain(re.sub(r"<[^>]+>", " ", text))
    # letter-spelled acronyms (אף-אם-אר-איי, איי-איי) come back from the transcriber in Latin (fMRI, AI), so they
    # can never match; they are left out of the word count and judged by the listen-QC on the whole file instead
    words = [w for w in re.findall(r"[֐-׿]+", re.sub(r"\S+(?:-\S+)+", " ", spoken)) if len(w) > 2]
    secs = wav_seconds(wav_bytes)
    rate = len(re.sub(r"\s+", "", spoken)) / secs
    heard = plain(transcribe(wav_bytes))
    missing = [w for w in words if w not in heard]
    hit = 1 - len(missing) / max(1, len(words))
    short_names = [n for n in names if heard.count(plain(n)) < spoken.count(plain(n))]
    ok = cps[0] <= rate <= cps[1] and hit >= min_hit and not short_names
    return ok, {"seconds": round(secs, 2), "chars_per_sec": round(rate, 1), "words_heard": round(hit, 3),
                "missing": missing, "names_not_heard": short_names, "transcript": heard}


def _check():
    """Real calls. PASS only if every model returns one-header WAV of plausible length, and the
    transcript of each clip contains the words that were sent (so a style leak would FAIL)."""
    text = "שלום, זו בדיקה של המודל הקולי. <short pause> הכל עובד."
    words = ["שלום", "בדיקה", "המודל", "עובד"]
    style = "warm, calm, clear"
    ok = True
    for model in (DEFAULT_MODEL, LITE_MODEL, FALLBACK_MODEL):
        try:
            wav, secs = synthesize(text, "Kore", style, model)
            one_header = wav[:4] == b"RIFF" and wav.find(b"RIFF", 4) == -1
            tr = transcribe(wav)
            has = all(w in tr for w in words)
            leak = any(w in tr.lower() for w in ("warm", "calm", "clear"))
            good = one_header and 2.0 < secs < 15.0 and has and not leak
            print("%-30s %s  one_header=%s  %.2fs  words=%s  style_leak=%s" %
                  (model, "PASS" if good else "FAIL", one_header, secs, has, leak))
            ok &= good
        except Exception as e:  # noqa: BLE001 - report and fail, never hide
            print("%-30s FAIL  %s" % (model, str(e)[:200]))
            ok = False
    try:
        n = len(list_voices(page_size=50, all_pages=False))
        print("voice library: %d voices returned for page_size=50 -> %s" % (n, "PASS" if n else "FAIL"))
        ok &= n > 0
    except Exception as e:  # noqa: BLE001
        print("voice library FAIL %s" % str(e)[:200])
        ok = False
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Gemini TTS, one module for every script")
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--voice", default="Kore")
    ap.add_argument("--style")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", default="tts_out.mp3")
    ap.add_argument("--voices", action="store_true")
    ap.add_argument("--lang")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--design", metavar="DESCRIPTION", help="voice design: 1-2 sentence description")
    ap.add_argument("--clone", nargs=2, metavar=("REFERENCE", "CONSENT"), help="voice replication (own voice only)")
    ap.add_argument("--name", default="My voice", help="display name for --design / --clone")
    ap.add_argument("--gender", help="for --design: female / male / neutral")
    ap.add_argument("--delete", metavar="VOICE_ID")
    a = ap.parse_args()
    if a.check:
        sys.exit(_check())
    if a.design:
        vid, sample = design_voice(a.design, a.name, gender=a.gender, language_code=a.lang or "he-IL", model=a.model)
        if sample:
            pathlib.Path("designed_voice_sample.wav").write_bytes(sample)
        print("designed voice id: %s  (sample: designed_voice_sample.wav) - keep this id" % vid)
        return
    if a.clone:
        vid = replicate_voice(a.clone[0], a.clone[1], a.name, model=a.model)
        print("replicated voice id: %s - keep this id" % vid)
        return
    if a.delete:
        print("deleted, status", delete_voice(a.delete))
        return
    if a.voices:
        vs = list_voices(a.lang)
        print("%d voices%s" % (len(vs), " for " + a.lang if a.lang else ""))
        for v in vs:
            print("  %-28s %-6s %-8s %-10s %s" % (v.get("id"), v.get("gender"), v.get("pitch"),
                                                 v.get("language_code"), (v.get("description") or "")[:70]))
        return
    text = a.text or pathlib.Path(a.file).read_text(encoding="utf-8")
    wav, secs = synthesize(text, a.voice, a.style, a.model)
    if a.out.lower().endswith(".wav"):
        pathlib.Path(a.out).write_bytes(wav)
    else:
        wav_to_mp3(wav, a.out)
    print("wrote %s (%.2f s, %s, voice %s)" % (a.out, secs, a.model, a.voice))


if __name__ == "__main__":
    main()
