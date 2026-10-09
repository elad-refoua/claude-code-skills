---
name: audio-producer
description: |
  Primary audio/voice skill. Generates speech and audio files with Gemini TTS through ONE module,
  scripts/gemini_tts.py: Hebrew-capable studio voices, voice design for custom Hebrew voices,
  voice cloning (own voice + consent only), style control, vocal tags and 2-speaker dialogue.
  Use for any audio generation need, from a quick voice message to batch production with QC
  listening and team review sites. The current model, voice defaults and voices.md (read it
  before choosing a voice) are in the body.

  TRIGGERS: "create audio", "generate audio", "make recording", "TTS project",
  "audio production", "generate recordings", "narration", "guided audio",
  "text to speech batch", "produce audio files", "record content",
  "create voice files", "batch TTS", "audio pipeline",
  "send voice", "send audio message", "create voice", "generate speech",
  "say something", "voice message", "send me audio", "record this",
  "הקלטה", "צור הקלטה", "שלח הודעה קולית"
---

# Audio Producer

End-to-end audio production: script writing, TTS generation, QC, and team review.
This skill produces the audio file; sending it is up to your own messaging tool.

**Model**: `gemini-3.8-flash-tts` (GA, Sep 2026; 130 languages incl. Hebrew). Cheaper/faster:
`gemini-3.8-flash-lite-tts` (101 languages incl. Hebrew). Fallback: `gemini-3.1-flash-tts-preview`.
**Voices**: the same 30 prebuilt names (see [voices.md](voices.md)), plus an extended library.
**Call it ONLY through `scripts/gemini_tts.py`** — `synthesize(text, voice, style, model)` returns
WAV bytes with exactly one header; `python -X utf8 scripts/gemini_tts.py --check` is the gate.

## ⚠ What changed in 3.8, and why every old TTS snippet was wrong (verified 2026-09-24)

1. **It returns a finished WAV** (`audio/wav`, RIFF header, 24 kHz). 3.1 returned headerless PCM,
   and every script here wrapped it in `wave.open(...)`. On 3.8 that writes the header TWICE —
   the first 44 bytes of every clip become a click. `gemini_tts.as_wav()` handles both.
2. **The text is a verbatim transcript.** Google's docs: delivery instructions go in a separate
   `speech_metadata.style` annotation, not in the text, or they are read aloud. (Tested: the old
   "directions `---` text" prompt was NOT read aloud on the legacy endpoint — but that is
   undocumented, so the module uses the documented path.) **Pass directions as `style`, never in
   `text`.**
3. **New endpoint for style:** `POST /v1beta/interactions` with
   `input[].content[].annotations[{type: speech_metadata, style}]`,
   `generation_config.speech_config: [{voice}]`; audio comes back at `steps[].content[]` with
   `type: audio`. The legacy `models/...:generateContent` still accepts 3.8 (no style field).
4. **Vocal tags are angle brackets** inside the text: `<laugh>` `<chuckle>` `<sigh>` `<breath>`
   `<whispers>` `<gasp>` `<cry>` `<sob>` `<yawn>` `<cough>` `<short pause>` `<long pause>` and
   ~25 more (full list in voices.md). The 3.1 square-bracket tags (`[laughs]`) are old syntax.
5. **Multi-speaker: up to 2 speakers** per request (`speech_config.mode: conversational`).
6. **Four sources of voices** (full detail and numbers in voices.md):
   - **30 studio voices** — all speak Hebrew.
   - **Extended library** — **2,089 prebuilt voices** (3 pages; `list_voices()` paginates), dozens
     of locales, filterable by gender, pitch, accent, persona, context, free-text search. **None
     Hebrew.** Use for English, Arabic, Korean, Japanese, Hindi, Portuguese, German, French, etc.
   - **Voice design — THE way to get many Hebrew voices.** `design_voice(description, name,
     language_code="he-IL")` → a persistent `voice_...` + a 60 s sample. **Tested 2026-09-24: a
     "warm Israeli clinical psychologist in her forties" came out as natural spoken Hebrew**, and
     synthesis with it was transcribed exactly. 200 custom voices per project, 1-year life.
   - **Voice replication (cloning)** — `replicate_voice(reference, consent, name)`: 10–30 s of
     natural speech + the speaker reciting Google's consent sentence (no Hebrew locale; use the
     English one), same mic and room. **The speaker's own voice only, with their own recorded
     consent, and a clone is never used to produce anything that reaches another person as if that
     speaker said it** — identity cannot be retracted once someone has heard it. Each such use needs
     the speaker's explicit per-use approval.
7. **Prompting on 3.8 (Google's guide):** try an EMPTY style first — most text needs none. Keep
   style short ("warm, calm") and reuse the same string; long Director's-Notes blocks are "the most
   common cause of voice drift" — put a lasting persona into a designed voice instead. Never put
   age, gender, name or accent in `style`. CAPITALISE a word for emphasis. In Hebrew text, keep the
   inline tags in English (`<sigh>`, not Hebrew). Two-speaker dialogue: listener reactions in pipes
   inside a turn (`|oh really?|`) give natural backchannels.
8. **Flash vs Lite:** Flash for studio-grade acting, dialogue, many tags, long narration; Lite is
   Google's recommended cheap high-volume replacement for 3.1. **Output formats:** WAV (default),
   `audio/l16` raw PCM, `audio/mulaw`, `audio/alaw`, with `sample_rate`; streaming returns raw PCM.

Migrated to the module on 2026-09-24, each tested through its own QC on 3.8: a recurring
spoken-briefing script (QC 5/5), an explainer-video narration script (QC 5/5), and the `ai-live-action-video`
skill's `scripts/generate_narration.py` (QC 4/5).

## ⛔ IRON GATE — NEVER DELIVER UN-QC'D AUDIO (learned 2026-07-10 from a broken delivery)

Gemini TTS is STOCHASTIC: the same text can render perfectly on one run and as garbled
babble on the next. On 2026-07-10 a multi-section briefing recording was generated,
concatenated, and delivered WITHOUT the QC step — several sections were gibberish and the
user got a broken recording. This must never recur. Therefore, for EVERY audio artifact,
no matter how small or urgent:

1. **Deterministic duration gate (free, always):** Hebrew speech runs ~9-20 chars/sec
   (accept 6-26). A section whose audio duration implies a rate outside that band is a
   truncation or babble-loop — REJECT and re-roll without listening.
2. **Listen-QC every section (mandatory, not optional):** send each generated section to a
   Gemini audio-understanding model (`gemini-2.5-flash` family — SEPARATE quota from TTS)
   together with the exact expected script; require JSON {score 1-5, problems}; score
   specifically hunts gibberish/garble/loops/wrong-language/stage-directions-read-aloud.
   Accept only >=4. Re-roll <4 up to 3 takes, keep the best.
3. **Final whole-file listen** on the concatenated output against the full script before
   declaring done. If QC infrastructure is down (404s), the artifact is delivered ONLY with
   an explicit warning to the user that it is unverified — never silently.
4. **Never hand-deliver a path around the gate.** If you write a new TTS script, the gate
   goes INSIDE it. `gemini_tts.gate()` in this skill's `scripts/` is the per-take check (rate,
   transcript word match, names); add the final whole-file listen (layer 3) in your own script.
5. **Names are gated one by one: `ok, report = gemini_tts.gate(wav, text, names=(...))`.** It checks
   the rate, the 90% word match, and that EVERY listed name is heard as often as it is written
   (niqqud and tags are stripped first). **Why (2026-09-24):** a voice note passed at 96% while the
   voice had said a different name in place of the intended one at the start of a sentence; two
   listener models each heard yet another name. Adding niqqud to the name fixed the pronunciation.
   Transcribers also guess grammatical gender from a name (they heard "שואלת" for a man), so gender
   is judged by a listener prompt that asks for gender as heard, never by the plain transcript.
6. **How much checking (feedback, 2026-09-24: use online transcription, but do not overdo it).**
   Online transcription, not local Whisper, but no more calls than the job needs: one transcription per take, at most 3 takes per
   paragraph, a per-paragraph cache (sha of voice+style+text) so a fix re-renders only what changed, and
   ONE listener model on the final file; a second listener only if the first raises a doubt. Cost is
   small (about 0.1-1 cent per check at 3.5 Flash prices), so the reason to hold back is sprawl, not money.
7. **What fails in Hebrew with a custom voice, learned on a two-minute Hebrew narration:** a
   name that OPENS a sentence or follows a short word ("אז <name>", "<name> חושב") comes out soft (its
   first sound dropped, or heard as a similar name) - put a lead-in before it ("אז ככה, <name>", "ועוד
   נקודה: <name>"); a name fused to vav ("ו<name>") - write "ואז <name>";
   and choose verbs whose masculine and feminine SOUND different (מבקש/מבקשת, חושב/חושבת), never
   מציע/מציעה or רוצה (the voice said רוצָה despite niqqud). The word check is substring-based, so give the
   render script a list of the wrong forms to reject (it caught "מציעה" and "שמנהל" before the listener did).
   Letter-spelled acronyms are left out of the word count; transcribers return them in Latin.

Skipping this gate is the one known way this skill produces a broken deliverable.

## Voice Selection (read voices.md for full guide)

Always pick voice intentionally based on content:
- Default female: **Kore** (firm) | Warm: **Sulafat** | Gentle: **Vindemiatrix** | Bright: **Autonoe** | Narrative: **Despina**
- Default male: **Charon** (informative) | Firm: **Orus** | Smooth: **Algieba** | Friendly: **Achird**

When content requires self-reference, match Hebrew feminine/masculine to the chosen voice.

## Pipeline Overview

```
1. Script    →  2. Generate  →  3. QC (Gemini LLM)  →  4. Re-roll  →  5. Review site
   text+tone     Gemini TTS      listen & rate           fix 4/5s       deploy+notify
```

## Step 1: Write the Script

Structure content as **sections** — each section becomes one audio file.

### Section Format

```python
{
    "id": "section-name",        # kebab-case → filename
    "tone": "English tone...",   # emotion/delivery direction
    "text": "Hebrew text...",    # actual spoken content
    "skip_speech_dir": False,    # optional: skip SPEECH_DIR for this track
    "skip_pron": False,          # optional: skip PRON for this track
}
```

### Tone Direction Examples

```
"Serious then warmly reassuring."
"Calm, instructional, gentle authority."
"Gentle guiding, warm invitation to breathe together."
"Clear, steady, guiding through each sense. Smooth connected flow."
"Warm, reassuring, like a supportive friend. Each phrase with conviction."
"Calm, patient, poetic for the wave metaphor. Gentle imagery."
"Soft, dreamy, guiding imagery. Slow and peaceful."
"Empathetic, acknowledging, normalizing."
"Practical, caring, each tip clearly."
"Conversational pace, varied intonation — like explaining to a friend."
"Caring, direct, informative. Deliver the opening line as a declarative title with falling intonation."
```

**Tone pitfalls:**
- "Soothing/bedtime voice" → too slow for informational content. Use "conversational" instead
- Question-mark sentences get rising intonation even when meant as titles → add "declarative, falling intonation"
- Always add "clear falling intonation at end, no clipping" for final tracks

### Speech Directions (CRITICAL — Add to ALL Tracks)

```python
SPEECH_DIR = (
    'Add micro-pauses (0.3-0.5s) between sentences. '
    'Add audible breath sounds between paragraphs. '
    'Vary pace naturally — slightly faster for lists, slower for key points. '
    'When counting or listing numbers, pause clearly between each number. '
    'When breathing instructions appear, slow down and add real pauses to let the listener follow along. '
)
```

Without SPEECH_DIR, TTS sounds flat and robotic. **Always include it.**

**Exception:** Tracks that need raw delivery (e.g., breathing demonstrations with actual sounds) should set `skip_speech_dir: True` — SPEECH_DIR interferes with breath sound generation.

### Pronunciation Corrections (Hebrew)

```python
PRON = (
    'מלאו="mal-OO". שאפו="sha-FOO". נשפו="nish-FOO". שחררו="sha-khar-ROO". '
    'בימים="ba-ya-MIM" with kamatz on bet. '
    'להרגע="le-he-ra-GE-a" not "le-har-GA". '
    'מערכת="ma-a-RE-khet" not "ma-al-KET". '
    'פיזיולוגית="fi-zyo-LO-git" with f not p. '
    'תרגלו="tir-ge-LU" not "ti-rag-LU". '
    'לרווחה="lir-va-CHA". '
    'בבת אחת="be-VAT a-CHAT". '
    'שינה="shei-NA". '
    'פתיל="ptil" — shva on פ, NOT "pa-til". '
    'אגרפו="ig-re-FU" not "ei-gar-FU". '
    '1201="e-lef ma-ta-YIM ve-e-KHAD". '
    'תנו="tnu" short and clear.'
)
```

### CRITICAL: filter_pron() — Never Send Full PRON

**Sending the full PRON string (945+ chars) + SPEECH_DIR to every track causes Gemini to switch to text mode** — it reads the pronunciation hints aloud instead of applying them.

**Always filter PRON to only include words that appear in the current section's text:**

```python
def filter_pron(text, pron):
    """Return only PRON entries for words that appear in the text."""
    entries = pron.split('. ')
    relevant = []
    for entry in entries:
        for word in entry.split():
            if any('\u0590' <= c <= '\u05FF' for c in word):
                clean = word.strip('="\'')
                if clean in text:
                    relevant.append(entry)
                    break
    return '. '.join(relevant) + '.' if relevant else ''
```

This is the single most important lesson from a six-version breathing-exercise audio project. Without filtering, audio quality degrades catastrophically.

### What DOESN'T Fix Hebrew Pronunciation

Tried and failed across 6 versions:

1. **Nikkud (vowel marks)** (3.1-era) — Gemini 3.1 ignored Hebrew diacritics entirely: adding זַהֵה instead of זהה had zero effect. (On 3.8, niqqud on a name did fix its pronunciation; see IRON GATE item 5.)
2. **Transliteration in PRON** — Works for some words, not others. Stochastic.
3. **MiniMax TTS** — every voice has a strong non-native accent in Hebrew; no Hebrew-native voices exist. Not viable.

**The truth: Gemini TTS is stochastic.** Same text → different pronunciation each run. No text-based fix guarantees correct pronunciation. The best strategy is:
1. Apply PRON hints (helps ~70% of the time)
2. Generate multiple takes
3. QC with Gemini LLM (see Step 3)
4. Re-roll tracks that scored below 5/5
5. Accept 4/5 as the floor — some tracks may never reach 5/5

## Step 2: Generate Audio

### Gemini 3.8 Flash TTS (Current Default) — use `scripts/gemini_tts.py`

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("~/.claude/skills/audio-producer/scripts").expanduser()))
from gemini_tts import synthesize, wav_to_mp3

wav, seconds = synthesize("שלום לכולם. <short pause> היום נדבר על...",   # spoken verbatim
                          voice="Kore",
                          style="warm, calm, clear; micro-pauses between sentences")  # HOW, not WHAT
wav_to_mp3(wav, "section_01.mp3")
```

The block below is the OLD 3.1-era inline pattern, kept for reference only. Do not copy it into a
new script: on 3.8 it double-writes the WAV header and puts directions inside the text.

```python
def generate_tts(section_id, tone, text, outdir, skip_speech_dir=False, skip_pron=False, retries=2):
    """Generate TTS for one section."""
    parts = []
    if not skip_speech_dir:
        parts.append(SPEECH_DIR)
    parts.append(tone)
    if not skip_pron:
        filtered_pron = filter_pron(text, PRON)
        if filtered_pron:
            parts.append(filtered_pron)
    prompt = ' '.join(parts) + '\n---\n' + text

    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}'
    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'responseModalities': ['AUDIO'],
            'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': VOICE}}}
        }
    }

    for attempt in range(retries + 1):
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=180) as response:
                result = json.loads(response.read().decode('utf-8'))
                all_audio = b''
                mime_type = ''
                for part in result['candidates'][0]['content']['parts']:
                    if 'inlineData' in part:
                        all_audio += base64.b64decode(part['inlineData']['data'])
                        mime_type = part['inlineData'].get('mimeType', '')
                if all_audio:
                    rate = 24000
                    if 'rate=' in mime_type:
                        rate = int(mime_type.split('rate=')[1].split(';')[0])
                    wav_path = os.path.join(outdir, f'{section_id}.wav')
                    mp3_path = os.path.join(outdir, f'{section_id}.mp3')
                    with wave.open(wav_path, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(rate)
                        wf.writeframes(all_audio)
                    subprocess.run(['ffmpeg', '-y', '-i', wav_path,
                                    '-codec:a', 'libmp3lame', '-qscale:a', '2',
                                    mp3_path], capture_output=True)
                    os.remove(wav_path)
                    return mp3_path, len(all_audio) / (rate * 2)
        except Exception as e:
            print(f'  Attempt {attempt+1} failed: {e}')
            if attempt < retries:
                time.sleep(5)
    return None, 0
```

### Rate Limits

| Model | Delay Between Calls | Daily Limit (Free) | Quota Reset |
|-------|--------------------|--------------------|-------------|
| Pro TTS | 8 seconds | ~9-15 tracks/run | Midnight Pacific (~9-10 AM Israel) |
| Flash TTS | 3 seconds | More generous | Same |
| LLM (non-TTS) | 2 seconds | Separate quota | Same |

**429 errors = quota exhausted.** Don't retry — wait for reset or use Flash model.

### Special Tracks: Breathing Demonstrations

For tracks that need actual audible breathing sounds (e.g., physiological sigh):

```python
{
    "id": "step3b-sigh",
    "tone": "Gentle guiding, warm invitation to breathe together.",
    "text": "...",
    "skip_speech_dir": True,  # SPEECH_DIR interferes with breath sounds
    "skip_pron": True,        # PRON adds noise to the prompt
}
```

**Sigh demo prompts that produce actual breathing sounds:**

```python
SIGH_DEMO_PROMPT = (
    'Gently guide a physiological sigh breathing exercise. '
    'Make a LONG audible inhale sound (3-4 seconds) when you say "שאיפה ארוכה". '
    'Make a SHORT audible inhale sound (1 second) when you say "לגימה קצרה". '
    'Make a LONG audible exhale sound (4-5 seconds) when you say "נשיפה ארוכה". '
    'Warm, calm voice.\n---\n' + TEXT
)
```

Generate 3+ takes and let the team pick — breathing quality varies per run.

### Post-Processing: Adding Silence

Add pauses before/after a track (e.g., breath moment before a breathing exercise):

```python
def post_process_add_silence(mp3_path, seconds=2):
    """Add silence before and after a track."""
    outdir = os.path.dirname(mp3_path)
    silence = os.path.join(outdir, '_silence.mp3')
    original = os.path.join(outdir, '_original.mp3')
    subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=24000:cl=mono',
                    '-t', str(seconds), '-codec:a', 'libmp3lame', '-qscale:a', '2', silence],
                   capture_output=True)
    os.rename(mp3_path, original)
    list_path = os.path.join(outdir, '_concat.txt')
    with open(list_path, 'w') as f:
        f.write(f"file '{os.path.basename(silence)}'\nfile '{os.path.basename(original)}'\nfile '{os.path.basename(silence)}'\n")
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_path,
                    '-codec:a', 'libmp3lame', '-qscale:a', '2', mp3_path],
                   capture_output=True, cwd=outdir)
    for f in [silence, original, list_path]:
        if os.path.exists(f): os.remove(f)
```

## Step 3: QC with Gemini LLM (Audio Understanding)

**Use Gemini's multimodal LLM to listen to generated audio and check pronunciation.**
This uses a SEPARATE quota from TTS — you can QC even when TTS quota is exhausted.

```python
def qc_track(track_id, audio_path, problem_words=None):
    """Send audio to Gemini LLM for pronunciation QC."""
    with open(audio_path, 'rb') as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    prompt = f'''Listen to this Hebrew audio. Rate pronunciation quality 1-5.
List any mispronounced or unclear words. Note rhythm issues. Be brief.
Track: {track_id}'''

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}'
    payload = {
        'contents': [{'parts': [
            {'inlineData': {'mimeType': 'audio/mp3', 'data': audio_b64}},
            {'text': prompt}
        ]}],
        # maxOutputTokens must be HIGH (>=2000): thinking-capable QC models spend tokens on
        # internal reasoning BEFORE the visible reply; a 300-400 cap yields an empty reply that
        # masquerades as QC infrastructure failure (lesson 2026-07-10, synthetic-voice task).
        'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 4000}
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
        return result['candidates'][0]['content']['parts'][0]['text']
```

**Valid QC model names** (verified 2026-07-10): `gemini-3.5-flash`, `gemini-2.5-flash`,
`gemini-3-flash-preview`. **`gemini-3.1-flash` does NOT exist** (returns 404) — never use it
as a fallback. Preview endpoints also throw transient 404s under load — retry before concluding
QC is down, and join multi-part replies (`''.join(p.get('text','') for p in parts)`).

### QC Workflow

1. Generate all tracks
2. Run QC on ALL tracks (2-second delay between calls)
3. Separate into 5/5 (keep) and <5 (re-roll candidates)
4. Re-generate only the <5 tracks
5. QC again on re-generated tracks
6. Accept 4/5 as floor — Gemini's stochastic nature means some tracks may never reach 5/5

**For sigh/breathing tracks, add specific QC:**

```python
sigh_prompt = '''Listen to this Hebrew audio of a physiological sigh exercise.
Does it include ACTUAL audible breathing sounds (inhale/exhale)?
Rate breath sounds quality 1-5 and Hebrew pronunciation 1-5.'''
```

## Step 4: Review Site

Build a team review page with:
- Audio players with transcripts per track
- Shared comments (Google Apps Script backend)
- Deploy to GitHub Pages

### Fresh Comments Per Version

Use a **version prefix** on trackIds to namespace comments:

```javascript
var VERSION_PREFIX = 'final-';
// In HTML: data-comments="final-panic-intro"
// When loading: filter to only show comments with VERSION_PREFIX
allComments = data.comments.filter(c => c.trackId.startsWith(VERSION_PREFIX));
```

This lets you reuse the same Apps Script backend while keeping each version's comments separate.

### Safari/iOS Compatibility

**Never use JavaScript Audio probe objects** (canplaythrough/error events) to test file existence. Safari blocks Audio creation before user interaction. Use `preload="none"` directly:

```html
<!-- CORRECT -->
<audio controls preload="none" src="audio/track.mp3"></audio>

<!-- WRONG — breaks on Safari/iOS -->
<script>var a = new Audio('track.mp3'); a.oncanplaythrough = ...</script>
```

## Step 5: Batch Script Pattern

```python
def main():
    os.makedirs(OUTDIR, exist_ok=True)

    # --only flag for selective regeneration
    only = None
    if '--only' in sys.argv:
        idx = sys.argv.index('--only')
        only = sys.argv[idx + 1:]

    sections = SECTIONS
    if only:
        sections = [s for s in SECTIONS if s['id'] in only]

    results = []
    for i, sec in enumerate(sections):
        sid = sec['id']
        skip_sd = sec.get('skip_speech_dir', False)
        skip_pr = sec.get('skip_pron', False)
        print(f'[{i+1}/{len(sections)}] {sid}...', end=' ', flush=True)
        path, dur = generate_tts(sid, sec['tone'], sec['text'], OUTDIR,
                                 skip_speech_dir=skip_sd, skip_pron=skip_pr)
        if path:
            print(f'OK - {dur:.0f}s, {os.path.getsize(path)//1024}KB')
        else:
            print('FAILED')
        time.sleep(8)  # 8s for Pro, 3s for Flash
```

## Versioning & Iteration Workflow

### Feedback → Fix Cycle

1. **Categorize fixes**: text, pronunciation, tone, structural
2. **Fork the script** (e.g., `generate_v2.py`) — keep old scripts for reference
3. **Back up audio** before regenerating
4. **Regenerate ALL** for global changes (voice, SPEECH_DIR). Use `--only` for isolated fixes
5. **Deploy new review site** per version — don't overwrite old one

### Content Guidelines

- **Remove phone numbers** — say "מספרי הטלפון מופיעים באתר" instead
- **Add "שניות"** after numbers in breathing instructions
- **Check grammar** before generating — re-generation is expensive
- **Keep sections under ~200 words** for best quality

### Don't Fix What Works

If a track sounded great in v2, **don't change it in v3** by adding global settings. Use `skip_speech_dir` and `skip_pron` flags to preserve tracks that already work.

## Engine Comparison

| Feature | Gemini TTS | ElevenLabs | MiniMax |
|---------|-----------|------------|---------|
| Hebrew quality | Excellent | Good | Bad (accented) |
| English quality | Good | Excellent | Good |
| Free tier | Generous | Limited | 100K chars/mo ($5) |
| Voice cloning | Yes (3.8 replication; own voice + recorded consent only) | Yes | No |
| Breathing sounds | Yes (with prompting) | No | No |
| Stochastic | Yes (big issue) | Minimal | Minimal |
| Rate limits | ~9-15 tracks/day (free) | Character-based | Credit-based |

**Bottom line: Gemini is the only viable option for Hebrew TTS. Accept its stochastic nature and use QC + re-rolls.**

## Lessons Learned (A Breathing-Exercise Audio Project — 6 Versions)

1. **filter_pron() is CRITICAL** — full PRON + SPEECH_DIR causes Gemini to read hints aloud. Always filter to only relevant words per section.
2. **Nikkud didn't work** (3.1-era) — Gemini 3.1 ignored Hebrew vowel marks entirely. (On 3.8, niqqud on a name did fix it; see IRON GATE item 5.)
3. **Gemini is stochastic** — same text → different pronunciation each run. No text fix is 100% reliable.
4. **QC with Gemini LLM** — use multimodal API (audio input) to listen and rate. Separate quota from TTS.
5. **Don't fix what works** — if a track was excellent in v2, protect it with skip flags in later versions.
6. **Sigh/breathing demos** — use specific prompts for actual breathing sounds. Skip SPEECH_DIR and PRON. Generate 3+ takes.
7. **8-second delay for Pro** — 3s causes 429 errors. Free tier quota resets midnight Pacific (~9-10 AM Israel).
8. **MiniMax is NOT viable for Hebrew** — all voices sound accented. Don't waste subscription money.
9. **Safari/iOS audio** — never use Audio probe objects. Use `preload="none"` directly.
10. **Fresh comments per version** — use version prefix on trackIds (e.g., `final-panic-intro`).
11. **Selective regeneration** — QC first, then re-roll only tracks scored <5/5. Don't blindly regenerate all.
12. **22 tracks at 8s delay = ~6 min** — run generation in background while building review site.
13. **Tone directions in English** work well even for Hebrew content.
14. **Post-processing** — add silence before/after breathing tracks with ffmpeg concat.
15. **"Soothing/bedtime" tone is a trap** — makes practical content sleepy. Use "conversational" instead.
16. **4/5 is acceptable** — some tracks will never reach 5/5 due to stochastic nature. Don't chase perfection endlessly.
17. **Falling intonation** — explicitly request for last track's ending to prevent clipping.
18. **Test quota before batch run** — send one test request to check for 429 before committing to a full run.

## Lessons from narrated films (2026-10-05)

The reference implementation was a project-local `build_audio.py` (+ `final_listen.py`). It is not
included in this repo; the items below describe what it does so you can rebuild it.

19. **Budget characters, not seconds.** Sulafat with "unhurried" ran 7-9 characters a second in Hebrew and 10-13 in
    English. The first script for a "one minute" video came out at 87 s (Hebrew) and 79 s (English). A style of
    "brisk and energetic" plus a modest `atempo=1.08` brought a ~470-character Hebrew / ~600-character English script to 51 s.
20. **Do not have the voice say a name you cannot afford to get wrong.** The voice and the transcriber both turned
    a coined product name (in English and in Hebrew) into the nearest common word, and a sentence that OPENS with
    "<Name> arrives" was spoken as "Thank you, <Name>." The gate caught all of them across three takes each. What held: leave the name out of the
    narration and let an on-screen label carry it.
21. **English needs its own gate.** `gemini_tts.gate` counts only Hebrew words, so on English it checks the rate and
    nothing else. A `gate_en` in the project's build_audio.py does the same three tests; transcribers write "seventy-two" as "72", so digits
    in the transcript are turned back into words first. The Hebrew gate gets one tolerance for the same reason, limited to
    number words and only when the transcript really contains digits.
22. **Gate the DELIVERED file, music included.** The narration alone passing says nothing about whether the voice is still
    intelligible over a music bed. `final_listen.py` reads the audio track of the finished .mp4.
23. **A failed run must not leave the last good mix behind.** The gate failed, mix.wav was not rewritten, and the old one
    (for the old timing) sat there waiting to be muxed. Delete stale mixes before regenerating; render only after the gate passed.
24. **Sentence timing in a narrated film must be CONFIRMED BY CONTENT** (v2 of the same film, 2026-10-05). Placing picture changes on
    "the longest pauses" or on a character-proportional estimate was a second or two wrong in places: a breath at a comma looks like
    a full stop. What worked (a `verified_starts` step in the project's build script): list every pause, take the candidates nearest the text's own
    estimate, cut two seconds of audio after each, have a listener model write down what it hears, accept the first pause after which
    the take really begins with the sentence's first words. Cache the result beside the take.
25. **Before paying for any voice, check that the spoken text equals the text the gates read** (`check_spoken_equals_gated`: same
    paragraphs after normalising number words, maqaf and spacing). It exists because the number and quote gates read a file and the
    voice reads a string in code, and the two had silently drifted. It fired on its first run.
26. **A very short sentence fails the audio gate for no reason**: three words, one mis-transcribed, is 67%. Reword it ("כך הם
    מתארים את זה" for "ככה המתאמנים מתארים את זה:"), do not loosen the gate.
27. **Do not write "Dr." in narration you split into sentences**: the period splits the sentence. Write "Doctor" in the spoken text and
    keep "Dr." for the screen - except in an on-screen QUOTE card, which the film's own splitter also cuts at ". ", so a quote that
    is read aloud and shown says "Doctor" too. English also needs its own gate (item 21) and, for a film timed by sentence number, a
    translation with the SAME number of sentences per paragraph. This was written down on 2026-10-05 and then repeated the same evening
    in a new English quote, caught only by a reviewer; `check_spoken_equals_gated` in the project's build script now fails on any
    "Dr./Mr./Prof." in the spoken text. A lesson that is not a gate gets repeated.
28. **A designed voice speaks slowly** (Hebrew about 8 characters a second, English about 126 words a minute), so budget a film at that
    pace, not at a TTS estimate. A mild speed-up is fine when measured: x1.07 with `atempo` on the English takes was not audible as an
    effect; the first video's forced "brisk" style plus 1.08 was what made it sound like a news bulletin. Re-wrap the WAV header after a
    piped ffmpeg step (a streaming header has no length).
29. **Never time-stretch music to fit a film.** Slowing a Lyria track to 0.8x scored 2/5 on a listener model (phasiness, metallic strings,
    smeared piano attacks). Extend by repeating one phrase: find the pair of points (start, start + L, L of 24-44 s) whose spectral
    surroundings are most alike (a project-local `make_music_bed.py`, not included), crossfade 2.5 s, keep the track's own final chord, absorb the rest with at most 4%
    tempo. **Match the RHYTHM as well as the sound** (compare the pattern of note onsets over the same window): a 24.3 s loop chosen on
    spectrum alone was heard as "abrupt cuts" by one listener run and as seamless by the next, and a listener model also invents
    timestamps. So do not ask about the whole piece: cut each JOINT out (4 s either side) and judge it alone, twice; the 38.9 s loop that
    matched on rhythm passed every joint 0 of 2.
30. **Pad the mix to the film's full length.** The mix ended with the last word, `ffmpeg -shortest` cut the picture to match, and the
    end card with the QR code was gone (235.5 s expected, 229.5 s delivered). Only the delivered-file gate (item 22) saw it. Use
    `apad=whole_dur=<film>` and take loudness in two measured steps (single-pass `loudnorm` gave -14.8 LUFS and a true peak of -0.4).
31. **Lyria through the Gemini app (a browser-automation path that drives the Gemini web app; not included in this repo) fails when the machine is busy** ("no download control appeared within 420 s", three times while a
    render ran); it succeeded once on a quiet machine. Run it alone, and keep one good take.
