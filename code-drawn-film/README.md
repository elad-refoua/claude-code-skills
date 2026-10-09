# code-drawn-film

Make a narrated, animated short film in which every frame is drawn by code (cut paper and ink on a canvas), voiced with a designed Gemini voice, scored with Lyria, and checked by gates that read the finished file.

## What It Does

- Ships a deterministic canvas engine (`engine/core.js`): every frame is a pure function of time, with a cut-paper look, hand-drawn "boil", parallax depth, portal transitions through windows, and Hebrew/RTL text that keeps digit runs in the right order.
- Ships a parametric paper-puppet rig (`engine/cast.js`) so characters stay identical across chapters built by different agents, plus a contract file (`engine/ANIMATION_GUIDE.md`) that each chapter agent reads first.
- Renders headless in parallel with Playwright and Chromium (`engine/render.py`), with contact sheets, resumable frame rendering and ffmpeg encoding.
- Covers the audio chain in scripts: gated narration takes, Lyria music cues screened by a listener model, music fitted to each section by envelope correlation, foley synthesized in numpy, a ducked mix mastered to -16 LUFS, and RTL-safe burned-in subtitles.
- Gates the result on the rendered output: continuity at every cut (`check_cuts.py`) and a final PASS/FAIL table on the mp4 (`check_film.py`: container, dead seconds, black frames, loudness, hiss/buzz, narration placement). SKILL.md carries the craft rules and the lessons from several real builds.

## Requirements

- Python 3 with `pip install playwright numpy pillow`, then `playwright install chromium`
- `ffmpeg` and `ffprobe` on your PATH
- A Gemini API key as an environment variable: `GEMINI_VOICE_API_KEY` (preferred: use the key of the project that holds your designed voices) or `GEMINI_API_KEY`. Used by `scripts/narrate.py` and `scripts/score.py`.
- The **audio-producer** skill from this repo, installed at `~/.claude/skills/audio-producer/`. `narrate.py` and `score.py` import its `scripts/gemini_tts.py` (voice design, synthesis, transcription, API calls).
- Optional, from this repo: the **writer** agent (polishes narration and catches lines too close to a copyrighted source) and the **film-director** agent (the entry point for a new film).
- For Hebrew on canvas and in subtitles: the FrankRuehl and David fonts (Windows ships them); a handwriting face such as Guttman Yad is optional.

## Usage

In Claude Code, say:

- "Make a code-drawn film about ..."
- "A narrated animation of ..."
- "Make a film like PDoom" / "a music video in code for this song" / "a tribute film for ..."
- "סרטון מונפש", "סרט מצויר בקוד", "סרטון עם הקראה והנפשה", "כמו הסרטונים של אופוס", "קליפ לשיר", "סרטון לזכרו"

## How It Works

A film is a program. `src/studio.html` loads the engine, a timing file, a `config.js` (FILM: fps, dur, palette, fonts, script list, audio; start from `engine/config.example.js`) and one script per chapter; each chapter registers shots with `E.addShot`, and a shot paints the whole frame for any time t without state or `Math.random`, so frames can render in parallel and out of order. Narration lines are synthesized with a designed voice and must pass an iron gate (speaking rate, words heard in a transcript, names heard, a listener score) before they are used; `build_timing.py` turns the real line durations into `src/timing.js` and the mix timeline. Music cues come from Lyria, are screened for vocals, and are cut to each section by `fit_music.py`; `sfx.py` synthesizes foley; `mix.py` ducks the music under the voice and normalises loudness in two passes. `render.py` renders frames with one Chromium per worker and encodes them with the mix. Gates then read the rendered frames and the finished mp4, and each one names the file it read. Chapters are usually built by one agent each, with a blind reviewer at the end; SKILL.md describes that workflow, the project layout and the lessons learned.
