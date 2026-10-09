# Gemini TTS — Voice Catalog & Prompting Reference

**Model (default since 2026-09-24)**: `gemini-3.8-flash-tts` · lighter: `gemini-3.8-flash-lite-tts`
**Fallback**: `gemini-3.1-flash-tts-preview` (April 2026) · **Do not use**: the 2.5 TTS models
**Call it through** `scripts/gemini_tts.py` — never with an inline copy of the request code.

This file is the source of truth for voice selection and expressive prompting
across ALL audio work: audio-producer skill, video-producer agent, story-to-video agent.

---

## Gemini 3.8 — what is different (read first; verified 2026-09-24)

- **Same 30 studio voices, same names and descriptors** as the catalog below. All speak Hebrew
  (3.8 Flash: 130 languages; Lite: 101; Hebrew is in both). The language is detected automatically.
- **Style is a separate field.** The text is a verbatim transcript; delivery goes in
  `speech_metadata.style` — `synthesize(text, voice, style=...)`. The "Director's Notes" section
  below still describes WHAT to say in a style; on 3.8 you pass it as `style`, not before `---`.
- **Vocal tags are angle brackets**, in the text, at the point they happen:
  `<argh>` `<breath>` `<heavy breath>` `<exhales>` `<cackle>` `<cheer>` `<chuckle>` `<cough>`
  `<cry>` `<gasp>` `<giggle>` `<groan>` `<growl>` `<grunt>` `<grr>` `<hiss>` `<laugh>` `<moan>`
  `<pant>` `<pff>` `<phew>` `<scream>` `<shout>` `<shriek>` `<sigh>` `<sneeze>` `<snicker>`
  `<snort>` `<sob>` `<throat-clearing>` `<tsk>` `<whimper>` `<whispers>` `<yawn>`
  `<short pause>` `<long pause>`. Emotions that last ("excitedly", "sadly") go in `style`.
  The square-bracket tags in the "Audio Tags" section below are 3.1 syntax.
- **Output is a WAV file** (RIFF, 24 kHz mono) — do not wrap it again.
- **Two speakers max** per request, each text item tagged with its speaker and its own style.
- **Extended library (measured 2026-09-24): 2,089 prebuilt voices, 3 pages, NO Hebrew.** Largest
  locales: en-US 215, en-IN 120, en-GB 117, ko-KR 117, ja-JP 115, hi-IN 114, pt-BR 107, ar-EG 92,
  de-DE 87, es-419 86, fr-FR 81, en-CA/en-IE/en-ZA 80 each, fr-CA 68, pl-PL 63, pt-PT 56, it-IT 53,
  sw-KE 44 … Gender: 1,066 female, 966 male, 57 neutral. Pitch: low 1,119, medium 524, high 446.
  Each voice carries an `id` (e.g. `en-gb-storyteller-3`), accent, persona, context and a
  one-line description. **Personas** include High-Trust Advisor (Lawyer, Financial Advisor,
  Researcher), Customer Support (incl. Social Worker), Tech Support, Video/Training Voiceover,
  Storyteller & Narrator (Nature Documentary, Philosopher), Educational Tutor (Professor),
  Companion & Peer (Parent, Sibling, Podcast Interviewer), News & Podcast Host, Concierge.
  **Contexts:** Enterprise Agent, Content & Media, Conversational / Edu, Growth & Marketing,
  Wellness & Culture, Entertainment & Gaming. Query: `list_voices(lang="en-GB", gender="female",
  persona=..., context=..., search="warm")` or `gemini_tts.py --voices --lang en-GB`; pass the
  `id` as `voice`.
- **Voice design — the answer for "many Hebrew voices".** `design_voice(description, name,
  gender=..., language_code="he-IL")` returns a persistent `voice_...` and a WAV sample.
  **Tested 2026-09-24:** "A warm, calm Israeli woman in her forties, a clinical psychologist,
  speaking native Hebrew with a soft, reassuring voice" → a 60 s sample in natural spoken Hebrew
  (hesitations included), and a Hebrew sentence synthesised with it was transcribed exactly. (The
  test voice was deleted.) Describe permanent traits in 1–2 sentences — age, gender, timbre,
  accent; keep `style` for the moment's emotion. 200 custom voices per project, 1-year life;
  `delete_voice(id)` removes one. Ideal for a recurring cast (e.g. simulation characters): design
  each once, reuse the id.
- **⚠ A custom voice belongs to ONE Google project and is invisible to every other project's key**
  (measured 2026-09-25: a key from a different Google project got **404** on existing custom voices).
  So: `api_key()` prefers `$GEMINI_VOICE_API_KEY` (set it to a key from the project that holds your
  custom voices) and only then `$GEMINI_API_KEY`. **Never revoke that key or switch the audio module to
  another project** unless every custom voice is re-created there first (a clone needs the speaker's
  reference + consent recordings again). Checked the same day: a designed test voice PASS 100% (then
  deleted), `--check` PASS on 3 models.
- **Voice replication (cloning).** Needs two recordings of the same adult, same mic and room:
  10–30 s of natural speech, and the consent sentence recited verbatim in one of 30 locales —
  **Hebrew is not one**, so use the English: *"I am the owner of this voice and I consent to Google
  using this voice to create a synthetic voice model."* `replicate_voice(reference, consent, name)`
  converts any format to 24 kHz mono WAV. `store=True` → `voice_...` for a year; `store=False` →
  `voicekey_...` kept locally, 7 days. **Only a speaker's own voice with their own consent; never
  a participant's or patient's; and a clone never produces anything that reaches another person as
  if that speaker said it without the speaker's per-use approval.** Keep the recordings out of
  version control (git-ignore them) — they are biometric data.
  **Recordings:** compressed voice-note audio (opus, 48 kHz) is accepted for both the reference and
  the consent clip; `replicate_voice()` converts it. Trim the reference to 10–30 s of clean speech.
  A clone can add natural fillers ("אממ") that are not in the text.
  **`style` cannot invent a register the reference never had.** Mild styles (none, "calm and warm",
  "excited") carry over to a clone; a projected register such as "confident lecturer addressing a
  large audience" does not, if the reference is a quiet phone note. Record the reference in the
  target register (for a lecture voice, while actually lecturing) and clone that.
- **A script for a cloned voice should be written from a transcript of that person's real speech**,
  so the wording sounds like them. Weave any requested line into the flow rather than appending it.
- **Long pieces in a clone sound mechanical through an even pace.** One style for every paragraph
  gives the clone away on anything longer than a short note. Vary `style` per paragraph to follow the
  content (faster and excited for the exciting idea, slower for the caution), use CAPITALISED
  emphasis words and short bursts, and keep long pieces rare. The lasting fix is a better reference:
  the speaker talking animatedly in a real conversation, not a calm voice note.
- **A transcriber "corrects" rare terms.** QC transcripts read "CBT" where the audio said C-P-T,
  and "בדיונית" for "בדויה"; a targeted question to two listener models
  ("which letters do you hear, C-P-T or C-B-T?") confirmed the audio was right. When a QC
  transcript disagrees on a domain term, ask the listener about that word before re-rendering.
- **Limits:** 2 speakers per request (prebuilt voices only); for designed/cloned voices in a
  dialogue, synthesise each turn separately and concatenate.

## Model Capabilities (3.1 reference — 3.8 differences above)

- **30 prebuilt voices** (up from single-Kore default)
- **70+ languages** including Hebrew (`he`) in preview
- **Audio tags** in brackets `[laughs]`, `[whispers]`, `[sighs]` for granular emotion control
- **Director's notes** via natural-language style prompts
- **Multi-speaker mode** — up to 2 speakers in one synthesis call
- **Output**: PCM, 24 kHz, mono, 16-bit (same as 2.5 — wrap in WAV)
- **Input limit**: 8,192 tokens text
- **Output limit**: 16,384 tokens audio (~10 min; quality drifts past ~few minutes)
- **Pricing (standard)**: $1/M input, $20/M output. Batch: $0.50 / $10.
- **Audio token rate**: 25 tokens per second of audio

---

## Complete Voice Catalog (30 Voices)

Each voice has an officially documented characteristic. Pick by character, not gender alone.

### Female Voices (14)

| Voice | Characteristic | Best For |
|-------|---------------|----------|
| **Kore** | Firm | Default female — authoritative narration, instructional, professional |
| **Sulafat** | Warm | Therapeutic content, guided meditations, supportive friend tone |
| **Vindemiatrix** | Gentle | Breathing exercises, children's content, soft bedtime narration |
| **Achernar** | Soft | Very gentle / pediatric / whispered intimate narration |
| **Autonoe** | Bright | Upbeat marketing, promo videos, energetic explainer |
| **Zephyr** | Bright | Same family as Autonoe — bright/cheerful, alternate energetic female |
| **Despina** | Smooth | Narrative storytelling, long-form documentary |
| **Erinome** | Clear | Educational content, e-learning, crisp delivery |
| **Aoede** | Breezy | Casual conversation, light/social content |
| **Callirrhoe** | Easy-going | Relaxed podcast-style narration |
| **Leda** | Youthful | Young character voices, upbeat/teen content |
| **Laomedeia** | Upbeat | High-energy announcements, celebration content |
| **Pulcherrima** | Forward | Direct/assertive delivery, strong personality |
| **Gacrux** | Mature | Older/wiser female voice, gravitas |

### Male Voices (16)

| Voice | Characteristic | Best For |
|-------|---------------|----------|
| **Charon** | Informative | Default male — explainer, documentary, calm authority |
| **Orus** | Firm | Authoritative male — news, training, corporate |
| **Algieba** | Smooth | Narrator, storyteller, long-form listening |
| **Iapetus** | Clear | News-style, education, crisp male delivery |
| **Achird** | Friendly | Casual conversation, warm approachable host |
| **Puck** | Upbeat | Energetic male, game shows, marketing |
| **Fenrir** | Excitable | High-energy, dramatic, action content |
| **Zubenelgenubi** | Casual | Relaxed hangout podcast tone |
| **Alnilam** | Firm | Alternate firm male, rugged authoritative |
| **Rasalgethi** | Informative | Alternate to Charon — teacher/explainer |
| **Enceladus** | Breathy | Intimate, ASMR-adjacent, mysterious |
| **Algenib** | Gravelly | Aged/weathered character, noir narrator |
| **Umbriel** | Easy-going | Laid-back, friendly mentor |
| **Sadachbia** | Lively | Energetic host, engaging presenter |
| **Sadaltager** | Knowledgeable | Professor/expert tone |
| **Schedar** | Even | Neutral balanced delivery, neither hot nor cold |

---

## Voice Selection Cheatsheet (Hebrew Content)

**Default female** (matches historical Kore identity — use when no preference specified):
→ **Kore** (firm, professional)

**By content type:**

| Content | Primary | Alternate |
|---------|---------|-----------|
| Therapeutic / psychoeducation (breathing exercises, trauma-support sites) | Sulafat (warm) | Vindemiatrix (gentle) |
| Guided breathing / meditation | Vindemiatrix (gentle) | Achernar (soft) |
| Academic lecture / training | Kore (firm) | Erinome (clear) |
| Marketing / promo / landing page | Autonoe (bright) | Laomedeia (upbeat) |
| Storytelling / narrative video (story-to-video) | Despina (smooth) | Sulafat (warm) |
| Children's content | Leda (youthful) | Achernar (soft) |
| News / explainer voiceover | Erinome (clear) | Kore (firm) |
| Casual podcast / conversation | Aoede (breezy) | Callirrhoe (easy-going) |
| Male narrator (when needed) | Charon (informative) | Algieba (smooth) |
| Male authoritative (training video) | Orus (firm) | Iapetus (clear) |

**When content requires self-reference**, match feminine/masculine Hebrew grammar to the chosen voice.

---

## Audio Tags (Emotion & Non-Speech Sounds) — 3.1 syntax; on 3.8 use the angle-bracket tags at the top

Place in brackets `[tag]` INSIDE the text. They apply to the following phrase.

### Emotion tags (verified)
`[amazed]` `[amused]` `[bored]` `[crying]` `[curious]` `[excited]` `[excitedly]`
`[mischievously]` `[panicked]` `[reluctantly]` `[sarcastic]` `[sarcastically]`
`[serious]` `[tired]` `[trembling]`

### Non-speech sounds
`[sigh]` `[sighs]` `[gasp]` `[laughs]` `[giggles]` `[cough]` `[snorts]` `[uhm]`

### Delivery style
`[whispering]` `[whispers]` `[shouting]` `[robotic]` `[singing]` `[asmr]`

### Pacing
`[short pause]` `[medium pause]` `[long pause]` `[extremely fast]`

### Creative / character
`[like a dog]` `[like dracula]` — free-form allowed, model interprets

### Example

```
[excitedly] באמת? זה מדהים! [short pause] [whispering] אבל אל תספר לאף אחד.
```

**Rule**: keep emotion consistent with surrounding text. `[crying]` on cheerful text = confused output. Align **what is said** with **how it is said**.

---

## Director's Notes (Style Prompt Structure)

The model accepts a natural-language style prompt BEFORE the text (separated by `---` or newlines).
Recommended three-part structure for complex narrations:

```
AUDIO PROFILE: <who is speaking — identity/persona>
SCENE: <environment, mood, context>
DIRECTOR'S NOTES: <style, accent, pacing, emotion>
---
<transcript>
```

### Example

```
AUDIO PROFILE: Warm Israeli therapist, mid-30s, speaks to clients with calm authority.
SCENE: Quiet clinic room, end of session, final guided exercise of the day.
DIRECTOR'S NOTES: Conversational pace with natural breath pauses. Gentle falling
intonation at end of each phrase. No sing-song cadence. Treat the listener as
an intelligent adult, not a child.
---
נסגור יחד את השיחה בנשימה אחת עמוקה...
```

### Director's Notes components

- **Style**: specific and layered ("warm Israeli therapist" beats "nice female voice"). Phrases like "vocal smile" or "clinical calm" work well.
- **Accent**: geographic precision wins. For Hebrew, the model handles Israeli Hebrew natively — don't specify unless you want a specific regional feel.
- **Pacing**: describe tempo variation, not just speed. "Slightly faster for lists, slower on key points" > "medium pace".
- **Avoid over-specification**: let the model fill gaps. Don't describe every phrase.

---

## Multi-Speaker Mode (3.1 SDK example; on 3.8 see the top section and audio-producer SKILL.md)

Up to 2 named speakers in one synthesis call. Good for dialogue, interviews, Q&A, skits.

### Python example

```python
from google import genai
from google.genai import types
import wave

client = genai.Client()

prompt = """TTS the following conversation between Therapist and Client:
Therapist: איך ההרגשה אחרי התרגיל?
Client: [sighs] יותר רגוע, תודה.
Therapist: יופי. נחזור על זה מחר."""

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker='Therapist',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Sulafat'))),
                    types.SpeakerVoiceConfig(
                        speaker='Client',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Charon'))),
                ]
            )
        )
    )
)

pcm = response.candidates[0].content.parts[0].inline_data.data
with wave.open('dialogue.wav', 'wb') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
    wf.writeframes(pcm)
```

**Limit**: 2 named speakers per request. For 3+, split into separate calls.

---

## Single-Speaker Python Example (3.1 legacy — new code uses scripts/gemini_tts.py)

```python
from google import genai
from google.genai import types
import wave

client = genai.Client()

style = ("AUDIO PROFILE: Warm, clear Hebrew female narrator.\n"
         "DIRECTOR'S NOTES: Conversational pace, gentle falling intonation. "
         "Micro-pauses between sentences.")
text  = "שלום, אני שמחה שהצטרפתם היום לתרגיל."
prompt = style + "\n---\n" + text

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Sulafat')
            )
        ),
    )
)

pcm = response.candidates[0].content.parts[0].inline_data.data
with wave.open('out.wav', 'wb') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
    wf.writeframes(pcm)
```

---

## REST API (3.1 legacy urllib pattern — new code uses scripts/gemini_tts.py)

```python
MODEL = 'gemini-3.1-flash-tts-preview'
VOICE = 'Kore'  # or any from catalog above

url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}'
payload = {
    'contents': [{'parts': [{'text': prompt}]}],
    'generationConfig': {
        'responseModalities': ['AUDIO'],
        'speechConfig': {
            'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': VOICE}}
        }
    }
}
```

Output unchanged from 2.5: base64 PCM in `candidates[0].content.parts[*].inlineData.data`.
Wrap in WAV header (24 kHz, 16-bit, mono) before saving or converting to MP3.

---

## Hebrew-Specific Notes

1. **Hebrew language code**: `he` (some endpoints also accept `he-IL`)
2. **Nikkud still ignored** — the 3.1 model, like 2.5, does not respond to Hebrew vowel marks. Use transliteration in PRON hints. (On 3.8, niqqud on a name did fix it; see audio-producer SKILL.md, IRON GATE item 5.)
3. **Still stochastic** — same text → different pronunciation each run. QC + re-roll workflow still required.
4. **Proper names**: Hebrew proper names and coined product or project names often mispronounce. Transliterate aggressively in PRON.
5. **New in 3.1**: audio tags work in Hebrew. `[excitedly]` before a Hebrew phrase produces excited Hebrew delivery.
6. **Feminine forms required** when voice is female AND content has self-reference verbs ("אני שמחה" with Sulafat/Kore, not "אני שמח").

---

## Migration from 2.5 → 3.1

1. Change `MODEL` constant from `gemini-2.5-pro-preview-tts` or `gemini-2.5-flash-preview-tts` → `gemini-3.1-flash-tts-preview`
2. Voice names are **unchanged** — same 30 voice catalog. Existing `Kore` code keeps working.
3. Output format unchanged (PCM 24 kHz mono 16-bit). Existing WAV/MP3 code keeps working.
4. Rate limits improved — Flash 3.1 is faster than Pro 2.5. Start with 3-second delay, increase if 429.
5. Quality is more expressive — may want to re-QC existing tracks; some will improve, some may shift character.
6. Audio tags `[laughs]` etc. are a net-new capability — exploit them in emotional content.

## Voice design lessons from an old-storyteller narrator (2026-09-25, an animated film)

- "Close to the microphone", "intimate", "quiet room" in a description gave a near-whisper on every Hebrew
  take. What worked (voice F of the audition set): "a full, deep and resonant but clearly
  aged voice: gravelly, a little rough and cracked with age. He never whispers; he speaks at a natural
  storytelling volume". Default to NO style; "warm, gentle" made one voice sound ominous to a listener.
- Designing a child's voice is refused by the safety filter ("Voice prompt was blocked"); the catalogue has
  no child voices. Do not reword around it; plan the film without one.
- The audition sample can come back in English even with `he-IL`; judge only Hebrew takes.
- Listener models disagree about age and change it with the wording. Judge on REAL lines of the script (a
  funny and a sad one) with two models, ask about warmth, ominousness and whispering, and add the objective
  voiced fraction (autocorrelation 70-300 Hz; a whisper has no pitch).
- Gate traps fixed in `code-drawn-film/scripts/narrate.py`: plene/defective spelling after niqqud is
  stripped (לִטּוּף -> "לטוף" vs heard "ליטוף"), spelling variants (הכול/הכל), number words the transcriber
  writes as digits, and elderly voices at 4.5-7 chars/s (rate floor 4.0).
