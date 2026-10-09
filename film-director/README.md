# film-director

A director agent that owns a film from brief to delivery: it writes the treatment, prices the build, routes production to the right skill or agent, gates the result in code, delivers once, and remembers every lesson for the next film.

## What It Does

- **Takes the brief and settles it first.** It looks up what files can answer and asks only what they cannot, one question at a time. It never builds on a substitute for a source that did not arrive.
- **Writes one `TREATMENT.md` per film** (thesis, audience, one visual "spine", beats, look, voice, music, length, delivery), gets the go on structure, and prices the build in time and agents before spending it.
- **Routes production by form.** Code-drawn animation goes to the `code-drawn-film` pipeline, illustrated explainers to `video-producer`, testimonies to `story-to-video`, live action and screen capture to `ai-live-action-video`, and every spoken or on-screen word to `writer`.
- **Gates the film in code before anyone sees it.** Voice takes (two transcribers, inserted-word check, rate), mix (voice at least 15 dB over music, -16 LUFS), cuts, frozen frames, subtitles, and duration against the clock. Then one blind reviewer, one fix round, and its own look at the contact sheets.
- **Learns across films.** It keeps a per-film dossier, the commissioner's verdicts verbatim, cross-film lessons and measured pipeline times in its own memory (`~/.claude/agent-memory/film-director/`).

## Requirements

- Claude Code with subagents (the Agent tool) and skills (the Skill tool).
- `ffmpeg` on PATH.
- Python 3 with `numpy` and `Pillow`, plus `playwright` with Chromium for the code-drawn renderer:
  `pip install numpy pillow playwright && playwright install chromium`
- A Gemini API key as an environment variable for narration and music (used by `audio-producer` and `code-drawn-film`): `GEMINI_API_KEY`. If your designed voices live in a different Google project, set `GEMINI_VOICE_API_KEY` to that project's key; it takes precedence.
- Other items from this repo that it routes to: `code-drawn-film`, `audio-producer`, `ai-live-action-video`, `video-producer`, `story-to-video`, `writer`, `data-storytelling`, `nano-banana-poster`, `gemini-consult`, `ffmpeg-motion-only`, `hebrew-docx`, `suno-instrumental-prompt`, `gh-pages-deploy`.
- Optional, not included in this repo: browser-driven routes that use a subscription you already pay for (images through ChatGPT, music through Lyria in the Gemini app), a GPT image skill, an explainer-video skill, and, on Windows, a hidden-launcher script (`run_hidden.vbs`; a minimal version is in `AGENT.md` section 2.3).
- Fill in the `<SET_YOUR_PATH>` placeholders in `AGENT.md`: your studio folder, your film project folders, and any toolkit from a past film you reuse.

## Usage

In Claude Code, say:

- "make a video about ...", "direct a film", "explainer video", "promo", "trailer", "music video", "edit this video"
- Notes on a film it made: "notes on the film: ..."
- Hebrew: "תכין סרטון", "סרטון הסבר", "תביים", "פרומו", "טריילר", "קליפ", "סרטון ברכה", "סרטון לזכרו", "תערוך את הסרטון", "גרסה חדשה לסרטון", "הערות על הסרטון"

## How It Works

The agent works in three steps. **Step 0** is recall: it reads its memory catalog and the closest past films' dossiers, so "good" is defined by what worked before. **Step 1** is the brief. **Step 2** is the treatment and a one-line price. Then it chooses a form from a table that maps the kind of film to a pipeline and a builder. It briefs builders with their full stack (their own files, the treatment, the verified facts, exact outputs, the gates to pass), never with a one-liner, and caps parallel agents at five. Model checks are budgeted (one blind reviewer, one fix round). Deterministic checks run freely, and each one names the file it read. Delivery is once, signed, to an identifier, with copies sized to each channel's limit. After every film it updates the dossier, `taste.md`, `lessons.md`, `pipelines.md` and the film's own `PROJECT_TIMELINE.md`. A bug found in a shared tool gets fixed directly; a change to a shared rule is proposed first.

Hard boundaries are built in: no participant or clinical data, no fabricated facts or quotes, no cloned voice without a fresh yes for that film, no downloads, purchases or publishing without a yes, and no secrets in chat or files.

The memory folder starts empty. The agent creates its files on the first film, and until then the recorded numbers and lessons in `AGENT.md` are its baseline.

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/film-director ~/.claude/agents/
cp -r claude-code-skills/{code-drawn-film,audio-producer,ai-live-action-video,data-storytelling,nano-banana-poster,gemini-consult,ffmpeg-motion-only,hebrew-docx,suno-instrumental-prompt,gh-pages-deploy} ~/.claude/skills/
cp -r claude-code-skills/{video-producer,story-to-video,writer} ~/.claude/agents/
```

`AGENT.md` and the `code-drawn-film` scripts expect skills under `~/.claude/skills/` and agents under `~/.claude/agents/`; `audio-producer` must sit at `~/.claude/skills/audio-producer/`, because `narrate.py` and `score.py` look for `gemini_tts.py` there.
