---
name: ai-live-action-video
description: |
  Produce a short film whose footage is AI-GENERATED LIVE ACTION - people, rooms, dialogue -
  cut together with narration, slides and real screen captures, and gated by checks that
  measure the finished file. Covers the two things that actually break: keeping the same
  faces across separate clips, and getting past safety filters on sensitive subject matter.

  TRIGGERS: a film with AI-generated actors or scenes, e.g. Veo or Google Flow
  ("video with AI actors", "סרטון עם דמויות", "סרטון AI"); faces or characters that change
  between clips ("character consistency", "הדמויות משתנות"); a submission or project video
  ("submission video", "סרטון הגשה"); screen recordings cut into the film
  ("record the app for the video", "הקלטת מסך לסרטון").

  NOT for: illustrated/animated explainers (use the video-producer agent), or audio-only
  narration (use audio-producer).
---

# AI live-action video

## Where this sits — do not reinvent

| Need | Use |
|---|---|
| Narration TTS + listen-QC gate | `audio-producer` skill (Gemini TTS, mandatory QC gate before any audio ships) |
| Illustrated/animated explainer frames | `video-producer` agent |
| Reference stills, slide backgrounds | an image-generation skill: GPT Image 2 (no watermark), or `nano-banana-poster` for Gemini images |
| Subtitles, ASS templates, promo formats | `video-producer` agent |

This skill owns only what those do not: **generated live-action footage**, **screen capture
as video**, and **gates that measure the output file**.

Reusable scripts live in `scripts/`. They are working code from a real production, not
sketches — read them before writing your own. They assume one project folder per film with
`01_script/ 02_reference/ 03_clips/ 04_screencap/ 05_audio/ 06_slide/ 07_final/`, and each
script is copied into the folder it works on: `generate_narration.py`, `trim_tails.py` and
`build_bed.py` into `05_audio/`; the slide renderers into `06_slide/`; `record_demo.py` into
`04_screencap/`; `verify.py` into `07_final/`; `build_video.py`, `build_audio.py` and
`build_editorial_film.py` into any one subfolder (they treat its parent as the project
root). Settings come from the environment: `GEMINI_API_KEY` (TTS, listen-QC, images),
`WHISPER_PYTHON` (a Python with `faster-whisper` installed; defaults to the current one),
`DEMO_APP_URL` (the app `record_demo.py` captures).

---

## 1. The order that works: audio first, then picture

Narration length is fixed by the words; picture length is infinitely adjustable. So measure
the narration FIRST, then size the picture to it. Doing it the other way produces a cut where
every scene is a second or two too short and the voice runs over the next shot.

1. Write the script. Count words: English narration lands at **11-13 characters/second**.
2. Generate narration as **one file per beat**, not one long file. Discrete files are what
   make exact placement — and therefore ducking — possible.
3. Measure each file. Now build picture to fit, with ~0.5s of air at each end.

**Crossfades shrink the timeline.** N segments joined by an `xfade` of duration `d` finish
`(N-1)·d` shorter than the sum of their parts. Any offset arithmetic that ignores this drifts
badly by the end. See `scripts/build_audio.py:starts()`.

**Trim the narration files before you time anything against them.** Gemini TTS pads the end
of a file with silence — 1.5 to 3 seconds, varying per file — and *sometimes appends a stray
fragment after that silence*: a half-word, a breath, the start of a re-take. Both gates miss
it. The duration gate passes because the file length is plausible; listen-QC scores it 5/5
because every scripted word really is present and correct. It is only audible in the cut,
where it lands like a word beginning and being chopped off.

`scripts/trim_tails.py` finds the last pause of ≥0.45s and, if what follows is shorter than
0.9s, cuts the file there with a short fade. Run it with `--check` first. On one film it
flagged 4 of 8 files.

**Measure timing from the last spoken WORD, not from file duration.** This is the reason the
trim matters beyond the audible glitch: with 1.5–3s of trailing silence baked in, "tail =
next_cut − (start + lead + file_duration)" is not the gap a viewer hears. It read as a
comfortable 0.8s while the real gap after the last word was completely different. After
building, transcribe the finished audio with word timestamps and report, for each cut, the
gap from the last word that ends before it:

```python
gap = cut_time - last_word_end_before(cut_time)
assert gap > XFADE, f'a word lands on the dissolve at {cut_time:.2f}s'
```

**Give every beat a tail longer than the crossfade.** A beat sized `voice + 1.0` with a 0.55s
lead-in leaves 0.45s of picture after the last word — and a 0.45s dissolve consumes exactly
that, so the final syllable lands on the transition and the cut reads as clipped. Budget
`0.55 lead + ~1.25 hold`, and assert it:

```python
tail = next_beat_start - (beat_start + LEAD + narration_duration)
assert tail > XFADE, f'{beat}: {tail:.2f}s tail is inside the {XFADE}s dissolve'
```

Print the tail for every beat at build time. It is three lines of arithmetic and it catches
both the clipped-transition case and the far worse one below.

**A slice longer than the source truncates in silence — in *every* helper, not just one.**
`plate()` was asked for a 10.7s window of an 8s clip and returned 8s without a word, so one
beat's narration overran its picture by 2.3 seconds. Every gate still passed, because none of
them compares audio placement to picture length. Put the same `abs(got - asked) > 0.15` check
in each helper that slices, and derive slice lengths from the source duration rather than from
narration arithmetic.

---

## 2. Generated footage: keeping the same faces

This is the hard part and everything else is downstream of it.

**Generate one reference still first.** A single image (GPT Image 2) of your cast in the set.
Every clip then starts from that image. Without it, each clip invents new people.

**Use the reference as the FIXED FIRST FRAME, not as a "style reference".**
A style/ingredient reference still lets the model redraw faces. First-frame conditioning
pins them. Say it explicitly: *"use the attached photograph as the FIXED FIRST FRAME"*.

**Model choice matters more than prompt quality.** Measured on the same reference and prompt:

| Model | Result |
|---|---|
| Omni Flash | faces drifted mid-clip, a sixth person appeared |
| **Veo 3.1 - Lite** (first-frame) | **faces identical across the full 8s** |
| Veo 3.1 - Quality | does not accept reference images at all |

**Ask for less motion than you want.** Morphing is caused by motion. A prompt listing five
actions in eight seconds will drift; one listing a head turn and a blink will not. Include
these constraints verbatim:

> exactly five people, nobody enters or leaves the frame, nobody swaps places, every face
> stays identical to the first frame for the whole eight seconds. Minimal motion only:
> [one small action]. Nothing else moves.

**One 8-second clip is two shots.** Take a wide slice and a punched-in slice of a different
moment (`scale` then `crop`). Free footage, no extra credits, and it cuts like coverage.
See `scripts/build_video.py:clip_seg(zoom=…)`.

**Dialogue works.** Veo 3.1 lip-syncs quoted speech accurately. Verify it landed by
transcribing the clip rather than trusting it — `faster-whisper` on the clip's audio returns
the lines with timings, which you then need anyway for ducking.

**One Flow project per film.** Reusing a previous film's project mixes unrelated assets into
the picker and makes the per-project "approve, don't ask again" state confusing. A new project
is one click.

**Clip length.** Generations are ~8s. To fill a longer beat, either use **Extend** (adds 8s
holding the scene — click the clip in the asset grid, not via the chat agent), or intercut
Ken Burns moves over stills. Stills are free and often better than a longer clip.

---

## 3. Safety filters on sensitive subjects

Medical, forensic, clinical and historical subjects trip filters in ways that look
arbitrary. Two rules recover most rejections:

**Name adults as adults.** "medical students" around a draped figure was refused as
*"content related to minors"*. `"adult women aged twenty-six to thirty-two"` passed with the
same composition. The filter reads "student" as "child".

**Describe the frame, not the subject matter.** Say "a draped tray, covered by a white
cloth". Do not say cadaver, dissection, specimen, body, corpse. Keep the sensitive object
covered or out of shot — which is usually the more dignified choice anyway, and reads better.

A rejection costs nothing. A *silent* rejection does not exist: you always get a reason, so
read it before rewriting.

---

## 4. Screen capture as video

For a product demo you need moving capture, not screenshots.

**Playwright's `record_video_dir` is the right tool.** Real Chromium, real interaction, real
network calls, 1080p, headless — so nothing appears on the user's desktop. See
`scripts/record_demo.py`.

```python
ctx = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    record_video_dir='out/',
    record_video_size={'width': 1920, 'height': 1080})
```

**It records video only — no page audio.** Anything the app speaks is not captured. Do not
write narration that implies the viewer will hear the app.

**Type at human speed** (`locator.type(text, delay=55)`). Instant text-fill looks fake.

**Long waits: cut, never speed up.** If the backend takes 40s, cut it — and state the real
elapsed time on screen so the cut cannot mislead. Speeding up is a lie about performance and
is explicitly banned by most submission briefs.

**Inset the capture on your slide background.** Cutting from a dark slide to a full-bleed
white web app is jarring. Scale to ~85% inside a bordered panel on the same background and
the whole film reads as one piece. See `scripts/build_video.py:demo_seg()`.

---

## 5. ffmpeg traps that cost real hours

**`zoompan` with `-loop 1`: bound by `-frames:v`, never `-t`.**
`-t` before `-i` limits *input* duration. With `-loop 1` that still feeds ~200 frames, and
zoompan expands each into `d` output frames. An "8 second" Ken Burns segment came out
**1600 seconds** and 95 MB. Always:

```bash
ffmpeg -loop 1 -i still.png -vf "…,zoompan=…:d=$FRAMES:s=1920x1080:fps=24" \
       -frames:v $FRAMES out.mp4
```

**Do not pre-scale stills to 4K.** zoompan renders at the working resolution. Scale to just
above your maximum zoom (`W * max_zoom * 1.06`). 4K made segments take minutes for no gain.

**Aspect: image generators are 3:2, video is 16:9.** GPT Image 2 landscape is 1536×1024.
Feed that to a video model and you get 3:2 content pillarboxed inside a 16:9 frame, with
black bars baked in. Detect with `cropdetect`, then undo:

```
crop=ih*3/2:ih:(iw-ih*3/2)/2:0, crop=iw:iw*9/16:0:(ih-iw*9/16)*0.30, scale=1920:1080
```

The `0.30` biases the re-frame upward so heads keep their headroom.

**Clip slices silently truncate.** `-ss 4.0 -t 6.5` on an 8-second source yields 4.0s, not
6.5s, and nothing warns you. Always assert the segment came out the length you asked for.

**`drawtext` eats `%` and commas.** `%` is a strftime specifier and silently drops the label
*in full*; a comma chains filters and breaks the whole graph. Escape `:` `,` and quotes, or
simply keep captions comma-free. On Windows use `fontfile='C\:/Windows/Fonts/consola.ttf'` —
family names need fontconfig.

**h264 refuses odd dimensions.** A plate sized 1424×**801** (the exact 16:9 height) fails with
"height not divisible by 2". Round to 800 and take the 0.1% error.

**Mask polarity on `showwavespic`.** It draws the trace in the colour you ask for on a *black*
field. Key on brightness to extract it. Keying on darkness — the intuitive reading — produces
a perfectly empty, perfectly silent plate that looks like a layout bug.

---

## 6. Audio: ducking by construction, and no dead air

**Ducking.** Briefs ask that narration stop when a character speaks. Do not reach for a
compressor. Place narration as discrete files at explicit offsets and simply schedule
nothing inside the dialogue window — then a collision is *impossible*, and one line of
arithmetic proves it:

```python
if item.start < dialogue_end and item.end > dialogue_start:
    fail('DUCKING VIOLATION')
```

Get the dialogue window by transcribing the clip, not by estimating.

**Gemini TTS refuses some lines, and the refusal looks like a crash.** A blocked prompt returns
`promptFeedback` with **no** `candidates`, so code that indexes straight into `candidates` raises
a bare `KeyError: 'candidates'` three times and gives up — telling you nothing. Through the
audio-producer module, a refused line raises an error that says BLOCKED (with the `blockReason` on
the 3.1 endpoint, as "no audio ... possibly BLOCKED" on 3.8), and the listen-QC call in
`generate_narration.py` reports the `blockReason` too.

What gets blocked is not obvious. `PROHIBITED_CONTENT` fired on:

> "Start with this voice. **Nobody recorded it.** Claude sent the text to Gemini and asked it to speak."

The same sentence *without* the voice-direction preamble passed, and so did this rewrite:

> "Take this voice. Claude wrote the line, handed it to Gemini, and Gemini read it out."

Narration that draws attention to a voice being synthetic, next to detailed voice-styling
instructions, reads as voice-cloning intent. Frame it around the handoff rather than the
authenticity of the voice. **A block is deterministic — retrying is wasted; rewrite.**

**No part of a film should sit in silence.** Slides and diagrams have no audio of their own,
so they read as dead. Lay a bed under everything: room tone lifted from the generated clips
(free, and genuinely the scene's own ambience) plus a low sustained pad. Target **~20 dB
below narration** — measure it, don't guess. See `scripts/build_bed.py`.

`tremolo` will not go below `f=0.1`. Use `apulsator` if you need slower.

---

## 7. Gates that measure the OUTPUT

Every check must run against the finished file. A check that reads your own source can pass
while the film is broken — one grep for speed filters matched its own docstring and reported
"x1 confirmed" without touching the video.

`scripts/verify.py` runs four:

| Gate | How |
|---|---|
| Runtime inside the limit | `ffprobe` duration |
| Playback is x1 | frame count == `duration × fps`, exactly |
| No dead air | `silencedetect=noise=-50dB:d=1.5`, expect zero hits |
| Narration all present | `faster-whisper` the finished audio, diff against script, expect ≥0.80 |

**`astats` needs info-level stderr.** With `-v error` it returns nothing and any parser
built on it silently reports `?` forever. Use `volumedetect` and do not suppress stderr.

Expect the transcript diff to flag spelled-out abbreviations ("g p t five point four" vs
"GPT-5.4"). That is the check working, not failing.

---

## 8. Never let the narration contradict the footage

The failure mode is writing the script before the footage exists and never revisiting it.
Every one of these was caught only by watching the output:

- "an answer in seconds" — the capture's own timeline showed **31 seconds**. Corrected to
  "about thirty seconds instead of ten minutes", which is a stronger line anyway.
- "eighty-eight percent" — the real run returned **94%**, visible on screen.
- Narration promising a spoken answer the capture has no audio for.
- A claimed feature the app does not have (segmentation, on-image labels).

**Before locking:** list every factual claim the narration makes, and point at the frame that
proves it. Regenerating one TTS line is cheap; a video that contradicts itself is not.

If the software being demonstrated has a known flaw, say so in a closing card and in an
accompanying note. Disclosure costs thirty seconds of runtime and converts a liability into
evidence of judgement — which is what a reviewer is grading.

---

## 8b. Chaining models — the shot that makes the point

The strongest single image in a film about orchestration is **one model's output used as
another model's input**. Have an image model draw a still, then hand that exact file to the
video model as its first frame. Caption it plainly ("X drew it | Y moved the camera into it")
and the claim needs no argument — the frame is the argument.

It is also just good practice: first-frame conditioning is what holds a shot together
(§2), so the chain costs nothing you were not already doing.

## 8c. Design direction: ask the design skill, do not hand-roll

Do not invent a palette and a font pairing. Run the `ui-ux-pro-max` design skill (a
separate public skill, not included in this repo) with `--design-system` and take its
recommendation:

```bash
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "<mood> <medium>" --design-system
```

For an editorial film it returned Swiss Modernism 2.0 with **Libre Bodoni + Public Sans**,
which was markedly better than the pairing chosen by eye.

**When the film mixes light slides with dark footage**, do not cut between them. Inset the
footage as a **photo plate on the page**, the way a magazine sets a picture in a column of
type, and reserve the foot of every frame as paper. Two things fall out of that one decision:
the light/dark contrast becomes rhythm rather than a flash, and burned-in subtitles always
land on a consistent light band instead of fighting whatever is behind them.

**Subtitles for social video.** Facebook and Instagram autoplay muted, so burn them in. Time
them by transcribing each narration file with `faster-whisper` and offsetting by that beat's
start — dividing the text evenly drifts badly on any beat with uneven sentences. ASS colours
are `&HAABBGGRR`, so ink `#14161A` is `&H001A1614`; get that backwards and the text renders
near-white and invisible on paper.

## 8d. Verify the file, not the tool's success message

Twice in one session a patch script printed its own success line and had changed nothing —
once leaving a function without the parameter its body used, once leaving the subtitle style
light-on-light. Both surfaced only in the rendered frames.

**After any scripted edit, grep the target file for the thing you just wrote.** The same rule
as §7, one level up: a tool reporting success is not evidence that the file changed.

## 8e. Room tone is only an asset when the clip's audio is neutral

§6 says to lift room tone from the footage. That holds when the clip's own audio is ambience.
When the footage contains **percussive** sound — a keyboard, footsteps, a door — looping it
under the whole film reads as an irritating tic, not atmosphere, and it is the first thing a
viewer complains about. Make the layer switchable (`ROOMTONE_GAIN=0`) and run on the pad
alone, a little quieter. `scripts/build_bed.py` takes `ROOMTONE_GAIN` and `PAD_GAIN`.

## 8f. Google Flow in October 2026 - driving it from Claude in Chrome (measured 2026-10-07)

- Flow moved to **flow.google.com**. Video models: Omni 1.1 Flash (12 credits), **Veo 3.1 Lite / Fast (20 credits in Frames
  mode) / Quality (100)**; Frames mode (start and end frame) works on all three. The Pro tier came with 1,050 credits a
  month at the time of measurement. Visible watermarking is a toggle under the avatar (off).
- **Upload without a native dialog:** patch `HTMLInputElement.prototype.click` to capture the file input instead of opening the
  picker, open the Start slot's frame picker, click its "Upload media", then `file_upload` to the captured input (max 10 MB per
  call: three 1536x864 PNGs). The "Add media > Upload" menu item may call `showOpenFilePicker` - avoid it.
- **Selecting a start frame:** in the frame picker, focus the "Search assets" input and `document.execCommand('insertText')` the
  name (a value setter does not filter); clicking the one result row sets the start frame directly. Verify by comparing the row's
  thumbnail URL key with the start slot's image URL key before spending credits.
- **When the user's Chrome window is minimised the page is hidden and throttled**: screenshots time out and long scripts hit
  the 45 s CDP limit (they may still finish afterwards). Work in one short JS call per step, read state back each time, never
  resize the user's window.
- Generations run concurrently; the prompt box empties when a submission is accepted (that is the check).
- Downloading a clip is a file download: ask the user before downloading.

## 9. Slides

**Look at every slide before you assemble.** All four gates in §7 passed on a build whose
central slide had collapsed to one word per line and was completely unreadable. The gates
measure runtime, frame count, silence and transcript — **none of them can see the picture**.
Render each slide, open it, then build.

The specific trap that caused it: **CSS grid treats `<b>Wrote</b>` and the text node after it
as two separate grid items**, so `li{display:grid;grid-template-columns:56px 1fr}` puts the
bold word in one column and pushes the rest into an implicit row a few pixels wide. Use a
relative `li` with an absolutely-positioned `::before` counter and leave the content as one
inline flow.


Render slides from **HTML → PNG via Playwright**, never from an image model. Text accuracy is
the whole point of a slide and image models garble it. Build reveal states with a
`?reveal=N` query param and cross-dissolve them, so bullets appear as the narration reaches
them. See `scripts/render_slides.py`.

---

## Build checklist

1. Script written; every claim traceable to something that will exist on screen.
2. Narration generated per beat, listen-QC'd, durations measured.
3. Reference still generated; cast and set locked.
4. Clips generated first-frame-conditioned, minimal motion; faces checked on first vs last frame.
5. Dialogue clips transcribed; dialogue window recorded.
6. Screen captures recorded; long waits cut and the real elapsed time labelled.
7. Slides rendered from HTML.
8. Picture assembled to fit the measured narration; segment durations asserted.
9. Bed built to the final runtime, measured ~20 dB under narration.
10. `verify.py` green: runtime, x1, no dead air, transcript ≥0.80.
11. Watch it end to end. The gates cannot see a bad take, a wrong crop or a missing label.
