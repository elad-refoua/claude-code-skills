# ai-live-action-video

Produce a short film from AI-generated live-action footage (Veo / Google Flow), cut together with narration, HTML slides and real screen captures, and gated by checks that measure the finished file.

## What It Does

- Keeps the same faces across separate generated clips: a reference still used as the **fixed first frame**, a model that holds identity (Veo 3.1 Lite), and minimal-motion prompts.
- Gets sensitive subjects (medical, forensic, historical) past safety filters with two rules: name adults as adults, and describe the frame rather than the subject.
- Builds the film audio-first: one narration file per beat, trailing TTS artefacts trimmed, picture sized to the measured voice. Narration is never scheduled over on-screen dialogue, so it cannot collide with it.
- Records real app demos as video with Playwright (headless, 1080p, human-speed typing). Long waits are cut and labelled, never sped up.
- Runs final gates on the output MP4: runtime limit, x1 playback (frame count == duration x fps), no dead air, and a transcript diff showing that every narration line made it in.

## Requirements

- Python 3.8+ with `pip install playwright faster-whisper`, then `playwright install chromium`
- `ffmpeg` and `ffprobe` on your PATH
- `GEMINI_API_KEY` environment variable (Gemini TTS, listen-QC, Gemini image generation)
- Optional environment variables: `WHISPER_PYTHON` (a separate Python that has `faster-whisper`; defaults to the current interpreter), `DEMO_APP_URL` (the app `record_demo.py` captures), `ROOMTONE_CLIP`, `ROOMTONE_GAIN`, `PAD_GAIN` (bed mix)
- Access to Google Flow / Veo 3.1 for the generated clips (a Google AI plan with Flow credits)
- The **audio-producer** skill from this repo, installed at `~/.claude/skills/audio-producer/`. `generate_narration.py` imports its `scripts/gemini_tts.py`.
- Optional: the **video-producer** agent and **nano-banana-poster** skill from this repo, for subtitles/promo formats and reference stills
- On macOS/Linux, change the `fontfile='C\:/Windows/Fonts/consola.ttf'` in the `drawtext` captions to a font on your system

## Usage

In Claude Code, say:

- "make a video with AI actors" / "סרטון עם דמויות" / "סרטון AI"
- "the characters change between clips" / "character consistency" / "הדמויות משתנות"
- "make a submission video" / "סרטון הגשה"
- "record the app for the video" / "הקלטת מסך לסרטון"

## How It Works

`SKILL.md` holds the method and the lessons: ordering, face consistency, safety-filter phrasing, ffmpeg traps (bound `zoompan` with `-frames:v` rather than `-t`, undo the 3:2 pillarbox, assert every slice's length), and the build checklist. The scripts are working code from two real productions. Copy them into a per-film folder (`01_script/` ... `07_final/`; SKILL.md says which script goes where) and edit the scene lists:

| Script | Role |
|---|---|
| `generate_narration.py` | One TTS take per beat, with a duration gate (characters per second) and a Gemini listen-QC score. It reports the real block reason when TTS refuses a line. |
| `trim_tails.py` | Finds the short fragment Gemini TTS sometimes appends after the closing silence and cuts it (`--check` to report only). |
| `gen_gemini_image.py` | Generates a still and writes a `.prompt.json` sidecar recording the prompt, model and SHA-256. |
| `render_slides.py`, `render_slides_with_gates.py` | Render HTML slides to 1920x1080 PNGs through Playwright, one per reveal state. The second injects the verify gate's real numbers into a slide. |
| `record_demo.py` | Records a real Playwright screen capture of the app. |
| `build_video.py` | Cuts Veo clips (with punch-ins), Ken Burns stills, slides and inset screen captures into per-segment files, crossfades them, and writes `timeline.json`. |
| `build_audio.py` | Places narration files at explicit offsets on that timeline and checks arithmetically that nothing overlaps the dialogue window, then mixes and muxes. |
| `build_bed.py` | Builds a room-tone + drone bed and measures it against the narration (about 20 dB below). |
| `build_editorial_film.py` | A second, editorial-style assembly: footage set as photo plates on a paper page, with burned-in subtitles timed by transcribing each beat. |
| `verify.py` | Final gates, all measured on the output MP4 rather than on the scripts. |
