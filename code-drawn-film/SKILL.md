---
name: code-drawn-film
description: |
  Make a narrated, animated short film where every frame is drawn by code (cut paper + ink on
  canvas, a pure function of time), voiced in Hebrew or English with a DESIGNED Gemini 3.8 voice,
  scored with Lyria, foley synthesized in code, rendered headless in parallel and gated by checks
  on the finished file. The genre of "made entirely in code by a team of Claude agents" films
  (PDoomVideo, Claude-Pop, INNER WEATHER). Covers the engine, the cast rig, the window/portal
  transition, narration with the audio iron gate, music, mix, multi-agent chapter building, and
  the craft rules that separate it from slop. Also works for music videos (keep the song, draw to it).

  TRIGGERS: an animated or narrated film drawn in code ("code-drawn film",
  "narrated animation", "סרטון מונפש", "סרט מצויר בקוד", "סרטון עם הקראה והנפשה"); a film like the
  Claude-made ones ("make a film like PDoom", "כמו הסרטונים של אופוס"); a music video drawn to a
  song ("music video in code", "קליפ לשיר"); a tribute or memorial film ("tribute film",
  "סרטון לזכרו").
  ENTRY POINT: if you also use the film-director agent (published alongside this skill), a new film
  request goes to it first; the director runs this pipeline when the film is drawn in code.
---

# Code-drawn film

A film here is a **program**: `frame(t)` paints the whole picture for any time t; audio is a
timeline of real files; the mp4 is only a render of both. Everything that makes it beautiful is
craft decided before the code; everything that makes it reliable is a gate that reads the output.

Reference build: the method and the lessons below come from real builds. The first was a memorial
film for a real person (2026-09-25); its project held DESIGN.md, STORYBOARD.md, src/ and research/,
the layout in section 2.

## 0. Before anything: the three questions that decide the film

1. **Source and rights.** What text/music does it use, and may we reproduce it? Copyrighted poems or
   lyrics found in a file or on the web are NOT read aloud or put on screen; the film tells their
   stories in new words (at most one short quote, attributed). A song the user supplies is kept and
   never replaced. If a source the user meant to send is missing, ask and wait for it; never build
   on a substitute.
2. **Real people.** Facts about a real person go through a find-then-adversarially-verify pass
   (only CONFIRMED facts reach the film). A voice is DESIGNED from a description, never cloned from
   someone without their consent; a narrator never speaks as the real person; credits say the voice
   is synthetic. Google refuses to design child voices: plan the film without one.
3. **The spine.** One visual idea that carries the whole film and escalates (PDoom: a P(doom) meter;
   the memorial reference build: a building whose visited windows stay lit). Without it the film is
   a slideshow.

## 1. Pipeline (and who does what)

| Step | Output | Tool | Gate |
|---|---|---|---|
| Research | `research/*.md` | workflow: method, landscape, voice, source reading, bio + verify | every fact has a URL; bio claims verdicted |
| Design bible | `DESIGN.md` | you | thesis in one sentence; palette; cast; world rules; slop list |
| Storyboard | `STORYBOARD.md` | you | every section: picture, narration id, exit motive |
| Narration text | `script/narration_vN.md` | you draft, `writer` agent polishes (it leaves the machine) | no copyrighted lines; facts only from the verified list |
| Voice | a designed voice id | `audio-producer` `design_voice` | listener panel on REAL lines + voiced-fraction (see §4) |
| Narration audio | `work/voice/*.wav` + manifest | `scripts/narrate.py` | iron gate per take, listener >= 4 |
| Timing | `src/timing.js`, `work/timeline.json` | a small build script | shots cover [0, dur] with no gap |
| Engine + cast + world | `src/core.js`, `cast.js`, world module | vendored from `engine/` | model sheet rendered and looked at |
| Chapters | `src/ch/*.js` | workflow: one Opus agent per chapter, pipeline + reviewer | per-chapter contact sheets, >= 3 fix rounds |
| Music | `music/*.mp3` | `scripts/score.py` (Lyria 3.5) then `scripts/fit_music.py` | two-model voice screen; envelope correlation per section |
| Foley | `work/sfx/*.wav` | `scripts/sfx.py` (15 sounds incl. water, purr, pencil) | placed 8-18 dB under |
| Subtitles | `work/subs.ass`, `out/final_subs.mp4` | `scripts/subs.py --burn` | RTL checked on a still |
| Mix | `work/mix.wav` | `scripts/mix.py` | -16 LUFS, TP < -1.5, music ducked under voice |
| Render | `work/frames/`, `out/final.mp4` | `engine/render.py frames` then `encode` | all frames present |
| Continuity | PASS/FAIL per cut | `scripts/check_cuts.py` on work/frames | no pop > 3x local motion and > 6 grey levels |
| Final gates | PASS/FAIL table | `scripts/check_film.py` | container, dead seconds, black frames, loudness, narration placement |
| Review | notes, fixes | a fresh reviewer agent that sees only the film's contact sheets + DESIGN.md | fix the worst three, re-render those chapters only |

Price it before you start, and tell the user the cost before paying it: a 5-minute film is several
hours of agent time.

## 2. Project layout

```
DESIGN.md  STORYBOARD.md  PROJECT_TIMELINE.md  MAKE_REPORT.md
script/    narration drafts, lines.json
research/  reports
voices/    voice-design rounds and their results
music/     cues.json, cues, report
src/       studio.html core.js config.js timing.js cast.js <world>.js ch/*.js ANIMATION_GUIDE.md
work/      voice/ sfx/ frames/ check/ timeline.json mix.wav   (git-ignored)
out/       final.mp4, final_subs.mp4, final_sheet.jpg
```
Copy `engine/core.js`, `engine/cast.js`, `engine/studio.html`, `engine/ANIMATION_GUIDE.md` into `src/`,
and `engine/config.example.js` as `src/config.js` (fps, dur, palette, fonts, the script list, audio).
Run every script from the project root.

## 3. The engine (engine/core.js) — rules that make it work

- **Pure function of t.** `E.addShot({name, t0, t1, fn(ctx, t, lt, dur)})`; a shot paints the
  entire frame and ends with `E.finish`. No `Math.random`, no state. `E.boil(key, t)` reseeds 12x/s
  (the hand-drawn "boil"); per-object keys keep one moving object from re-boiling everything else.
- **Cut paper beats flat vector.** A flat Flash-puppet look was the first result and it read as
  cheap. `E.paperShape` (colour + fibre texture + soft cast shadow + faint lit edge) turned the same
  geometry into handmade. Architecture uses `sharp: true` (Catmull-Rom smoothing makes 4-point
  rectangles into pills). Canvas shadows ignore the transform: pass `sh` = on-screen scale.
- **Depth:** back-to-front layers with parallax; near objects in `E.plate(..., {blur})`.
- **Hebrew in canvas:** `ctx.direction='rtl'` works for plain Hebrew; digit runs must be isolated
  (`E.ltrIsolate`, applied inside `inkText`) or "1950–2020" renders as "2020–1950". FrankRuehl has no
  Latin glyphs; use David for dates. Guttman Yad / Yad-Brush are good handwriting faces (if installed).
- **Portal transitions:** fly the camera into a window and show the next shot inside it, scaled so
  that it becomes exactly the screen when the aperture fills it (blend from cover-scale to exact
  scale; the reference build did this in its own world module, `facade.js` `throughWindow`, which is
  not shipped here). Shots seen through a portal are drawn at `lt < 0` or `lt > dur`: every shot
  must clamp and draw its opening/closing state.
- **Render:** `engine/render.py` (Playwright + Chromium, one process per worker, `--disable-gpu`,
  JPEG frames, resumable). `sheet` prints ms/frame on the image. Typical: 40-250 ms/frame.

## 4. Voice (Gemini 3.8) — what was learned designing an old storyteller in Hebrew

- `gemini_tts.design_voice(description, name, gender, "he-IL")` → a persistent voice id. The API
  takes no sample text and the audition sample may come back in English: judge only Hebrew takes.
- "Close to the microphone", "intimate", "quiet room" in a description produce a near-WHISPER on
  every take. Ask for "a full voice at natural storytelling volume, never whispering" and put the
  age into the timbre ("gravelly, a little rough and cracked with age").
- Style annotations are fragile: "warm, gentle" made one voice sound ominous to a listener. Default
  to NO style; the persona lives in the design.
- Listener models disagree about age and change their answer with the question. Use a panel (two
  models) on 2-3 REAL lines of the film (a funny one and a sad one), ask for warmth, ominousness,
  "fits a grandfather telling a story", and whispering; add the objective voiced-fraction measure
  (autocorrelation in 70-300 Hz; a whisper has no pitch). Pick the voice with the best panel.
- Elderly designed voices speak at 4.5-7 characters/second: lower the gate's rate floor to 4.0.
- The gate miscounts spelling variants (הכול/הכל) and number words (the transcriber writes digits):
  `narrate.py` normalises both.
- `narrate.py` gates Hebrew or English lines (it reads both alphabets; spelling variants are Hebrew
  only). Pass `--voice-desc "an elderly man"` (any description) and the listener also deducts for a
  take that does not sound like that voice.

## 5. Music (Lyria 3.5)

**Which tool:** a song with HEBREW lyrics -> Suno (in a browser, on your own account); instrumental
cues or English lyrics -> Lyria is fine. Lyria's prompt filter blocks some words with no reason given
("content_blocked" / "sensitive words": a cue about a swarm "breaking free of its cage" with a beat that "drops" was
refused twice); rewrite neutrally rather than retrying.

**If you have a Gemini app subscription,** generating the music in the app through a browser (driven by Playwright)
can replace metered API calls; this section's API call (`scripts/score.py`) is then the paid fallback. In the app,
write the prompt positively ("a calm, warm instrumental score: felt piano..."): a list of negations ("no vocals, no
choir, no humming") failed 3 of 3 times with error replies, and the positive version worked first time.

`POST v1beta/interactions {"model": "lyria-3.5", "input": prompt}` returns MP3 44.1 kHz stereo,
"a couple of minutes", length steered in the prompt; `lyria-3-clip-preview` gives 30 s clips. Write
"Instrumental only, no vocals", tempo, instruments, and a timestamped structure. One theme, varied
per section, beats five unrelated cues. Check each cue with a listener (vocals? fits the brief?).
Trim cues to phrase boundaries and crossfade in `mix.py`; never time-stretch a user's song.

## 6. Building chapters with agents

- One agent per chapter (Opus), each editing only `src/ch/<name>.js`; shared files are read-only to
  them. Give each: DESIGN.md, ANIMATION_GUIDE.md, its STORYBOARD block, its `TIMING` shot and lines,
  what the previous chapter ends on and what the next starts on.
- The agent's own loop is the quality gate: contact sheets every 0.5 s, looked at with the Read
  tool, three or more fix rounds, a 0.25 s sheet through the busiest part, ms/frame under budget.
- Then a reviewer that did NOT build it sees only the rendered sheets + DESIGN.md and names the
  three weakest moments; fix only those. Cap review loops at two rounds.
- Cap parallel agents at 5.

## 7. Craft rules (the difference from slop)

- One focal action per moment, a big readable silhouette; the viewer must understand in time.
- Something moves every second (camera drift at minimum); holds are deliberate and rare.
- Every cut has a motive: a window, a door, a match cut, a look, a page.
- Faces never snap; mood changes ride a blink or a head move.
- Narration frames, the picture plays. Wordless comedy beats narrated comedy.
- Palette discipline; no pure black or white; no neon/purple grade.
- Text on screen only when it is the point (a title, a quote, a dedication).
- Credits tell the truth: what is synthetic, what is inspired by whom.

## 8. Lessons from the first build (a memorial film, 2026-09-25) — read before the next one

- **Hand-offs break where two agents assume opposite things.** c04 skipped its own grain/vignette
  when seen through a window ("the connector finishes the frame"); the connector faded ITS grain to 0
  as the window filled ("the chapter finishes itself"). Result: a 26-grey-level pop at both cuts.
  Rule: every shot ALWAYS calls its own finish; the world module's portal finish (`FAC.finish` in the
  reference build, not shipped) fades the outer grain as the window fills.
  `scripts/check_cuts.py` on the rendered frames catches this in seconds - run it after every render.
- **A door that opens in one shot must be the same door, in the same state, in the next.** Cuts are
  fine; state jumps are not. Decide in the storyboard who opens it.
- **The printed ms/frame is not the cost.** Chrome rasterizes inside `toDataURL`, outside the timer.
  Real costs: 100-700 ms. Budget by wall-clock: 7,734 frames rendered with 5 workers in ~20 min.
  Full-screen `E.plate` blur and drawing a whole shot through a portal are the expensive parts;
  quarter-resolution scratch canvases for soft light and for distant portals fix most of it.
- **Rig gaps the agents hit (fix in cast.js before the next film):** arms are drawn before the head
  (no hand at the face without a clipped redraw), no seated/kneeling pose, `blend` snaps clothes at
  u=0.5, `stoop` ignores `flip`, gaze moves pupils only 7% of the head, mitten hands only.
- **`paperShape` sets globalAlpha absolutely**: characters cannot be faded with `ctx.globalAlpha`;
  draw them into a layer and composite. `inkText` reveal clips glow with a hard edge.
- **Lyria ignores timestamped structure** (correlations -0.24..0.46 against requested curves) while
  a listener model calls every take "a perfect match" and even invents timestamps past the end of
  the file. Generate 2-3 takes per section, then let `scripts/fit_music.py` pick (file, offset) by
  envelope correlation with the section's intensity curve (got 0.43-0.71).
- **Screen every cue for human voice with TWO listener models** (wordless choir/vocalise slipped in on
  "instrumental only" prompts); discard a take either model flags if it would sit under narration.
- **libass needs RLE/PDF + LRI/PDI** for Hebrew (`scripts/subs.py` does it); canvas needs LRI/PDI
  for digit runs (`E.ltrIsolate`).
- **The writer agent caught three narration lines that tracked the copyrighted source too closely**
  (checked against a scan of the source, which the research notes could not show). Always run the
  narration through it.
- **A synthesized noise sound heard ALONE is a buzz** (feedback on a previous film: a buzzing sound at the start, too
  loud and unpleasant). Measured on the mix: 0.5-3.5 s, the `pencil` scratch (band-passed noise, -13 dB)
  was 70-80% of all the energy (2-9 kHz share), because the music was still near-silent and the narration
  started at 8.5 s. Rules: (1) before the mix, list what plays in any stretch with no voice and quiet music,
  and put noise-based effects there at -22 dB or lower; (2) sustained or pulsed noise anywhere (pencil, purr,
  water, crickets, whoosh beds) at -20 dB or lower with 0.5 s fades; prefer sparse short strokes or soft tonal
  synthesis over continuous noise; one-shots (clang, click) may stay at -12. (3) Gate it in code: in each 0.5 s
  window, if the 2-9 kHz share of the mix exceeds 0.5 for more than 1 s, flag it - that single number found
  this; no listening needed.
- Parallel work that paid off while chapter agents ran: rendering finished ranges early, fitting
  music, building the mix plan, fixing cross-chapter hand-offs as each pair landed.

## 8b. Lessons from the second build (an idea explainer, 2026-10-04, 16:9, 2:42, 5 parallel chapter agents)

The later builds (8b, 12, 12b) ran project-local versions of the scripts. These names belong to those
versions and are not in this repo's `scripts/`: `build_timing.py mix` (and a build_timing.py that read the
slot map from the narration script), `GAP_OVERRIDE`, `MUSIC_SPLIT`, `record --force`, `RETAKE_SALT`,
`work/voice/words.json`, `mg.js`, `KIT_GUIDE.md`. With the shipped scripts: lengthen a shot or a pause with
`min`, `tail` or an `after:<id>+<gap>` offset in plan.json; force new takes for a line by deleting
`work/voice/<id>.wav` and `work/voice/cache/<id>_*`; the transcript of each chosen take is in
`work/voice/manifest.json` under `gate.transcript`.

- **Per-frame grain breaks two things.** (1) `render.py encode` at CRF 16 made a 2.9 GB file (143 Mbps): grain is
  incompressible. Deliver with a bitrate cap (~14 Mbps for Facebook) and a light `hqdn3d` for a <50 MB copy for
  messaging apps. (2) `check_film.py`'s dead-window test compares consecutive frames, so grain makes it unable to fail
  on the master and makes a denoised copy fail falsely. Measure change over 1.5 s after a blur instead (that build used
  its own `motion_check.py`, not shipped here).
- **check_film.py hard-coded 24 fps**: pass `--fps 30` (fixed 2026-10-04).
- **A chat bot that parses captions as Markdown** (Telegram's sendDocument with a Markdown parse mode): an underscore in
  a file path ("film_2026-10-04") made the send fail with "can't parse entities". Keep paths and underscores out of
  captions.
- **What worked:** a kit agent first (mg.js + KIT_GUIDE.md + an approved 12 s style test), then one agent per chapter
  with a shared CHAPTER_BRIEF.md and TIMING word times; builders matched hand-offs by rendering both sides of each cut.
  One blind reviewer (contact sheets one frame per second, DESIGN.md, the spoken lines) found the three real weaknesses
  (a payoff that did not read as people, a key finding with a caption-size credit, the best fact in tiny type); the same
  builders fixed them in one round by SendMessage, with their context intact.
- **v3 (2026-10-05, built overnight in two Workflows: story -> narration, then build -> render -> review -> fix):**
  (1) Let the clock READ the slot map from the script (chapter id in every `### NXX — <chapter>` heading, `## NXX` = a
  silent beat) so a rewritten script cannot drift from build_timing.py. (2) Route each review note by its time range to
  EVERY chapter it touches: a note covering c2 and c3 went only to c2, and the c3 half was fixed by hand afterwards.
  (3) Ask the reviewer to check the author's own structure point by point; it caught a direction arrow that read
  backwards and a caption that had dropped its "לא". (4) Judge text size on a full frame, not on a thumbnail sheet, and
  give the closing questions phone-readable type (62 px at 1080p). (5) The project's narration script wrote its report
  to `voices/`: create the folder in a new project, or the step fails after everything else is written.
  (6) **A cloned voice can INSERT a word** (one take added a word to an approved line). Both
  listeners named it under `extra_words`, and the take still passed because the panel never read that field. The fix:
  fail a word both listeners name as inserted, and re-judge a cached take by today's rules (a `--force` re-record had
  silently reused the cached take). An audit of the earlier films found no other agreed insertion. `scripts/narrate.py`
  here gates on missing words and a listener score, not on inserted words: add this check to any narration script you use.
  (7) **A crashed mix-plan step mixed the STALE timeline with every gate green** (v3.1): a chapter grew to 85 s, longer
  than any take of its music cue, fit_music returned NO CANDIDATE, the project's `build_timing.py mix` step crashed, and
  mix.py happily mixed the previous version's timeline.json (overlapping voices, picture out of sync, the old music
  level). check_film's "narration placement" passed because it compared that timeline to itself. Now: the build stops on
  any failing mix step; an audit compares every voice clip to the PICTURE clock and fails on overlap; a balance check
  measures the voice above the ducked music while it speaks (aim for >= 15 dB; at 6 dB a viewer found the music too loud);
  a duration check compares every mp4 to the clock (that build's `audit_mix.py`, `mix_balance.py` and
  `check_duration.py`, not shipped here). Split a long chapter into two music sections at a slot. And the <50 MB copy's
  bitrate must shrink as the film grows: 1750k fit 3:21, 1350k is needed for 4:03 under 49 MB.
  (8) The viewer opens the high-quality file the moment its path appears: do not name a file's path before its checks
  have finished.

## 8c. Taste notes for an IDEA film (a viewer's notes on the second build's v2, 2026-10-04)

- More serious, explanatory, smart and interesting: explain the mechanism; no gags or self-referential jokes in the voice.
- Not papers or people: tell the principle, not who said it; names and papers go to the credits only.
- Modest in pretension: modest in CLAIMS (hedged, a thought offered), not in visuals.
- End on a genuine open question to the viewer, not a slogan.
- A key term known in English (e.g. The Bitter Lesson) is said and written in English first, then in the film's language.
- A serious recording style runs ~20% slower than an enthusiastic one: budget words for it before recording
  (v2: 288 words -> 3:25; cut to 258 + tempo 1.18 -> 2:59).
- Develop the idea before building when the user asks for it: a treatment first (with the strongest model available),
  then narration (writer), then the build.

## 9. Final gates (check_film.py) and delivery

Run `check_film.py --film out/final.mp4 --timeline work/timeline.json --allow-still <deliberate holds>`.
It names the file it read. Then deliver `out/final.mp4` (and a subtitled copy for muted feeds via
ASS + libass, which handles Hebrew bidi when the text is not pre-reversed) with MAKE_REPORT.md.

**Publishing a film on a website (only when the user asks):** make a two-pass web copy under 50 MB, a
poster, a teaser and one VTT caption file per language (a translated caption is one string per subtitle
cue, written by the writer agent). Pick the poster from a frame with no text: a title card under a play
button reads as dirt (the reviewer's first finding).

## 10. A vertical film (a hero-adventure, 2026-09-29) - early lessons
- **The engine is hard-coded landscape** (`engine/core.js` W = 1920, H = 1080; `studio.html` canvas). A vertical film needs
  W/H made config first, 30 fps, and `boil` re-derived (10 or 15 reseeds/s). The ANIMATION_GUIDE "never neon / never pure
  black-white" rule was written for the memorial film; a film's DESIGN.md may override it explicitly.
- **Research as find-then-adversarially-verify paid off**: 3 Sonnet finders + 3 Opus refuters over 20 papers produced 74
  verdicts (59 confirmed, 14 corrected, 1 unverifiable, 0 refuted). The corrections were the valuable part: causal wording on
  correlational data, a "100%" that was a vignette-level strict count, a benchmark that was published norms not tested humans.
  Verifier ids carry claim suffixes (".F1", "#2"): strip them before joining verdicts to papers.
- **Real people as heroes**: the user supplied photos of real people (with their consent); `rembg` with the local
  `u2net_human_seg` model (it runs locally from `~/.u2net`) cut them out in seconds; review a contact sheet on the film's
  paper colour (one of 12 kept background fringe). Hero "power lines" are facts (roles, first authorship, counts taken
  from a source document), never personality claims. Photos stay out of git.
- **Images a user sends while a turn is running are not saved to disk** (only images in their own message land in the session's
  images folder). Ask for photos as separate messages after the turn ends, and verify each file exists before relying on it.
- **A cloned voice (only of a consenting speaker): match the speaker's natural energy, and search for the style in
  code** (an earlier rule, "record calm and speed up", was an over-generalisation). What
  drops words is a SPEED instruction ("fast"), not enthusiasm. Run a style search first (4-5 styles x the 3-4 hardest
  lines x 2 takes; gate + a two-model listener panel for enthusiasm and person-vs-announcer + F0 std in code). In one
  build the winner was "excited and upbeat, genuinely thrilled, but speaking at a medium pace and
  finishing every word clearly": 16 of 16 slots passed on the first take, F0 std 3.7 st vs 2.3 for calm. Gate fixes that
  matter: measure the rate over speaking time (not the raw file), and count a word missing only when BOTH transcribers
  (Gemini + local Whisper) miss it.
- **Foley that reads as a buzz** (feedback on the same film): a SYNTHESISED record scratch (harmonic tone dragged back and
  forth) and band-noise whooshes/zips were each heard as a buzz at the exact seconds they played, even at -18..-26 dB and
  with a low 2-9 kHz share (the share gate did NOT catch them). Use short dry hits only (<= 0.25 s) and let the music carry
  transitions.
- **Palette taste**: fluo pink was rejected as not beautiful; a wider riso set without pink (sunflower, blue, green, violet,
  prussian, aqua, red, orange) replaced it. Show a palette in a short style test before building chapters.
- **Posture in generated art**: two figures where one sits on the floor and the other bends over him read as a servant.
  Brief every people-image as EQUALS (same height, face to face), and audit every image for posture.
- Downloading fonts is a file download: ask first; the Windows-installed Aharoni/Impact/Arial Narrow render correctly as a
  fallback.

## 11. A third form: painted plates animated in code (2026-10-05)

Not a canvas-drawn film: the pictures are AI oil paintings (generated in ChatGPT through a browser, on a subscription) and
everything that moves is code (a Python/OpenCV engine, not the Chromium canvas engine above; that engine and its detailed
lessons are not included in this repo). The audio-side lessons are
in the audio-producer skill (items 24-31). Use this form when the film is about PEOPLE and a painterly, serious look
fits; use the cut-paper engine above when the idea needs drawn motion. What carried over from this skill unchanged: a
designed Gemini 3.8 voice (never a clone), Lyria from the subscription screened by a listener model, the audio gate, and
gating the delivered file. What differs: the music is extended by repeating a phrase found by spectral similarity (never
stretched), and sentence timing is confirmed by content, not read from pauses.

Changing the film after it is finished (the same evening): re-render only the part that changed (render from a chunk
onward, and prove with a frame comparison that the unchanged prefix is identical), and run ONE round of independent
reviewers on the new text and screens before paying for a voice - it caught a chart drawn on the wrong scale range, a
one-sided before/after panel, "they wrote" over invented quotes, and a label that means "real excerpt" to an academic.

## 12. Fourth build: a system explainer (2026-10-07, 2:59, a DESIGNED narrator voice)

Base copied from the second build's v3 project; only chapter ids, the script path and the voice changed.
- **A narrator who is not a real, consenting speaker gets a designed voice, and the credits say so.** Three he-IL
  designs, two real lines each, two listeners and the voiced fraction in code (a small voice-design script); the winner
  (A_chief, "a calm chief of staff") ran at about 2.6 words/s at tempo 1.0, much faster than a cloned voice in an earlier
  build (1.73): budget words for it, and give the densest pictures a held beat (a larger gap in plan.json: an
  `after:<id>+<gap>` offset or a longer `tail`) instead of slowing the voice.
- **A homograph passes every word gate.** עבודות said as ovdot ('facts', spelled עובדות) has the same letters once niqqud
  is gone, so the transcript gate, the whole-file match and a panel without a check for that word all passed it. It was
  caught only because a blind reviewer saw the local transcript's spelling differ from the script. Do this on purpose:
  diff each line's transcript (`gate.transcript` in work/voice/manifest.json) against the script, and settle every word whose spelling differs with two listeners asked
  about that one word (a small script; read the question from a UTF-8 file: Hebrew passed as a .bat argument is
  mangled). Then point the word and re-take.
- **Route review notes by TIME, not by text.** The fix round assigned notes by looking for a chapter id in the
  reviewer's free-text time field; notes written as "74.0-79.3 s" fell to UNASSIGNED and no chapter fixed them (two of
  six). Map each note's t0 to `TIMING.shots` in the workflow script.
- **A camera move that ends on a cut must arrive at rest.** c1's push into the swarm used easeIn, full speed on the last
  frame, and check_cuts failed the boundary (jump 41.6); easeInOut on the push plus a pull-back that starts from rest
  brought it to 4.7, PASS.
- Facts for a film about a real system: readers -> one skeptic who opens every cited line -> only its verified file
  reaches the story; numbers only from a counting script. The skeptic caught a count that measured headings, not items.

### 12b. Version 2 of the same film (2026-10-07, 9:17, six technical chapters) - what the longer build taught
- **One shared world module, built and judged BEFORE the chapter builders.** `src/<film>_world.js` held the one accurate
  system diagram (every box and arrow with its file:line), the hand-off frame, the drill into a box, terminals, documents,
  glosses and callouts. Six builders then drew one machine, and all five cuts passed check_cuts on the first render.
  Builders still reported module gaps (per-part focus, segment lighting, a digit inside a right-to-left label reversing
  "SHA256" to "256SHA"): fix those in the module after the film, not in six chapter files.
- **A long film is three bottlenecks, each with a cheap fix.** (1) CPU Whisper took ~1.5 min per slot: cache word times
  per slot by the wav's sha256, so a re-take costs two slots, not the whole film. (2) The review does not need every
  frame: render one frame per second (that build's renderer had a `--step 30` option; the shipped `engine/render.py` does
  not) plus the half second before each boundary for check_cuts (~1 minute), then render the full film ONCE after the
  fix round; re-render only chapters whose source is newer than their frames, and stop the build if anything is still
  stale. (3) A chapter longer than every music take gives fit_music NO CANDIDATE: split it at a slot into two sections
  in sections.json (c1 at its methods, N07).
- **`--force` re-scores nothing.** After fixing the transcript normaliser (Latin words such as "Markdown"/"Git", digits
  such as "31", a name the transcriber split into two words), `record --force` reused the cached takes with their old
  FAIL verdicts. A per-slot salt in the take hash (`RETAKE_SALT`) forces new takes for those slots only. Before
  re-taking, re-score the cached transcripts with the new normaliser: if they pass, the voice was right and only the
  gate was wrong.
- **A 9-minute film does not fit a chat-bot upload** (a Telegram bot takes 50 MB per file; ~120 MB at the v1 quality).
  Deliver it through a cloud folder the user names: copy, compare sha256, then share the link once. A Dropbox web link
  of the form `dropbox.com/home/<path>?preview=<file>` opens in the owner's signed-in Dropbox, with no public share link.
- **The blind review earned its place again:** it found the matching rules taught by an unexplained regex, the
  punchline spoken over a picture that did not show it, and grey bars where the claim was "the output is concrete". The
  fix agents asked for real tool output (79242 chars, 566 rows) and the numbers were added to the constants file with
  their evidence.
