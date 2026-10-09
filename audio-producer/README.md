# audio-producer

Speech and narration with Gemini TTS (Hebrew and English) through one tested Python module, with a quality gate that every take must pass before it is delivered.

## What It Does

- Generates speech with Gemini 3.8 Flash TTS (Lite and the 3.1 model as fallbacks) through a single module, `scripts/gemini_tts.py`. It returns a WAV with exactly one header and keeps delivery instructions (`style`) separate from the spoken text, so directions are never read aloud.
- Covers every voice source: the 30 studio voices (all speak Hebrew), the extended library of about 2,000 voices (no Hebrew), voice design for new custom Hebrew voices from a one-line description, and consent-based cloning of a speaker's own voice.
- Gates every take: a speaking-rate check, a transcription word match, and a per-name check (`gemini_tts.gate()`), followed by a final listen on the whole delivered file. Weak takes are re-rolled, never shipped.
- Documents the batch pipeline: script sections, Hebrew pronunciation hints filtered per section, selective re-rolls, and a simple team review page.
- Ships `voices.md`, a voice catalog and prompting reference, plus lessons from narrated films: confirming sentence timing by content, extending music without time-stretching it, and padding the mix to the film's full length.

## Requirements

- Python 3. The module uses only the standard library, so there is nothing to `pip install`. The legacy 3.1 SDK examples in `voices.md` need `pip install google-genai`; you only need that if you run those examples.
- `ffmpeg` on your PATH (MP3 output, and converting cloning recordings to 24 kHz mono WAV).
- `GEMINI_API_KEY` environment variable (get one at https://aistudio.google.com/apikey).
- Optional: `GEMINI_VOICE_API_KEY`, a key from the Google project that holds your designed or cloned voices. A custom voice is invisible to keys from any other project, so when this variable is set it takes precedence.
- No other skills are required. Several items in this repo build on this one: the `ai-live-action-video` and `code-drawn-film` skills and the `film-director`, `video-producer` and `story-to-video` agents. Install it at `~/.claude/skills/audio-producer/` so their imports resolve.

## Usage

In Claude Code, say:

- "create audio" / "generate audio" / "narration" / "record this"
- "text to speech batch" / "batch TTS" / "audio pipeline" / "produce audio files"
- "voice message" / "send me audio" / "generate speech"
- "הקלטה" / "צור הקלטה" / "שלח הודעה קולית"

The skill produces the audio file; sending it is up to your own messaging tool.

Or call the module directly:

```bash
python -X utf8 scripts/gemini_tts.py --check                      # real calls; prints RESULT: PASS or FAIL
python -X utf8 scripts/gemini_tts.py --text "..." --voice Kore --style "warm, calm" --out clip.mp3
python -X utf8 scripts/gemini_tts.py --voices --lang en-GB        # browse the extended library
python -X utf8 scripts/gemini_tts.py --design "A calm Israeli man in his thirties, low warm voice" --name Narrator --gender male --lang he-IL
```

## How It Works

`SKILL.md` holds the method: what changed in Gemini 3.8 and why older TTS snippets break on it, the quality gate, voice selection, the five-step pipeline (script, generate, QC, re-roll, review), and numbered lessons from real projects. `voices.md` is the voice catalog and prompting reference that the video skills and agents also read.

`scripts/gemini_tts.py` is the one place that calls the API. Its main functions:

| Function | Role |
|---|---|
| `synthesize(text, voice, style, model)` | Returns `(wav_bytes, seconds)`. On 3.8 it uses the Interactions endpoint with `style` as a `speech_metadata` annotation; on 3.1 it uses the legacy `generateContent` shape. |
| `gate(wav, text, names=...)` | Checks one take: speaking rate in range, at least 90% of the Hebrew content words heard in a transcript, and every listed name heard as often as it is written. Returns `(ok, report)`. |
| `transcribe(wav)` | Transcribes a take with a Gemini audio model, for the gate and the `--check` self-test. |
| `list_voices(...)`, `design_voice(...)`, `replicate_voice(...)`, `delete_voice(id)` | The extended voice library, voice design, voice cloning (own voice and recorded consent only) and cleanup. |
| `as_wav`, `wav_to_mp3` | Exactly one WAV header whatever the model returned, and MP3 output through ffmpeg. |

`--check` synthesizes a short Hebrew line on all three models, transcribes each result, and fails if a clip has a doubled header, an implausible length, missing words, or style words that leaked into the speech.
