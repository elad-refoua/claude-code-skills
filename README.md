# Claude Code — Skills & Agents

A curated, privacy-scrubbed collection of **60** Claude Code **skills** (52) and **agents** (8), built and
used in real academic, clinical and research work, then stripped of personal data so they drop into
your own setup.

Shared by [Elad Refoua](https://eladrefoua.com).

> **⚠️ Most items need a small adjustment before they run.** Names, paths, contacts and project
> specifics were replaced with placeholders such as `<SET_YOUR_PATH>`, `<YOUR_API_KEY>`, `<USER>` and
> `<YOUR_NAME>`. Anything carrying a placeholder will not work untouched. Open the item's own file
> and fill them in. API keys are always read from environment variables, never from a file in the repo.

**Browse by topic:** [Writing & references](#writing--references) ·
[Research data & statistics](#research-data--statistics) ·
[Figures, dashboards & data stories](#figures-dashboards--data-stories) ·
[Presentations & documents](#presentations--documents) · [Film, audio & media](#film-audio--media) ·
[Privacy & security](#privacy--security) · [Claude Code workflow](#claude-code-workflow) ·
[Dev & publishing utilities](#dev--publishing-utilities)

## Skill or agent, what is the difference?

| | **Skill** | **Agent** |
|---|---|---|
| What it is | Knowledge or a procedure loaded **into** your current chat | A **separate** Claude you hand a whole job to |
| Lives in | `~/.claude/skills/<name>/SKILL.md` | `~/.claude/agents/<name>/AGENT.md` |
| Own context window? | No, it runs in your conversation | Yes, isolated context and scoped tools |
| Use it when | You want Claude to do a thing a certain way | You want to hand off a self-contained task |

In short: **a skill is something you read and apply; an agent is someone you hand the job to.**

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git

# a skill goes to ~/.claude/skills/
cp -r claude-code-skills/ref-verify ~/.claude/skills/

# an agent goes to ~/.claude/agents/
cp -r claude-code-skills/writer ~/.claude/agents/
```

Then open the file you copied and replace any `<PLACEHOLDER>` it contains. Some items build on others
(for example the film agents call the film and audio skills); their own README lists what to install
with them.

**Quality:** an honest self-assessment of how polished and broadly useful each item is —
★★★★★ flagship · ★★★★☆ strong · ★★★☆☆ solid but niche · ★★☆☆☆ thin.

---

## 🎬 Featured: the film director and its studio

**[film-director](film-director/)** is an agent that directs a whole film for you, from the brief to the delivered file.
You tell it what the film is for; it decides how the film gets made, hands each part to the right builder, checks the
result in code, and remembers what it learned for the next film.

**What it does, step by step**
1. **Recall.** Before anything else it reads its own memory of past films, so "good" means what worked before.
2. **Brief.** It settles the brief from your files first and asks only what they cannot answer, one question at a time.
   If a source you meant to send did not arrive, it stops and asks instead of building on a substitute.
3. **Treatment.** It writes one `TREATMENT.md` per film (thesis, audience, one visual "spine", beats, look, voice,
   music, length, delivery), gets your go on the structure, and tells you the price in time and agents before spending it.
4. **Production, routed by form.** It picks the pipeline that fits the film and briefs the builder with everything it needs:

| Form of the film | Built by | Type |
|---|---|---|
| Animation drawn entirely in code (cut paper, motion graphics, explainers, tributes, music videos) | [code-drawn-film](code-drawn-film/) | Skill |
| A narrated video of illustrated frames or screenshots, from a script | [video-producer](video-producer/) | Agent |
| A personal testimony or story, illustrated and narrated | [story-to-video](story-to-video/) | Agent |
| AI live-action footage (Veo) and screen recordings | [ai-live-action-video](ai-live-action-video/) | Skill |
| Every narration line, with a quality gate per take | [audio-producer](audio-producer/) | Skill |
| Every word that is spoken or shown on screen | [writer](writer/) | Agent |
| A data scene inside a film | [data-storytelling](data-storytelling/) | Skill |

5. **Gates in code, before anyone watches it.** Each voice take is transcribed twice and checked for inserted words and
   speaking rate; the mix keeps the voice at least 15 dB over the music at -16 LUFS; cuts, frozen frames, subtitles and
   the total duration are measured. Then one blind reviewer, one fix round, and its own look at the contact sheets.
6. **Delivery and memory.** It delivers once, and after every film it updates a per-film dossier and its own lessons,
   taste notes and measured pipeline times, so the next film starts from what this one taught.

**Built-in limits:** no fabricated facts or quotes, no cloned voice without a fresh yes for that film, no downloads,
purchases or publishing without a yes, and no secrets in chat or files.

**Install the whole studio**

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/film-director ~/.claude/agents/
cp -r claude-code-skills/{code-drawn-film,audio-producer,ai-live-action-video,data-storytelling,nano-banana-poster,gemini-consult,ffmpeg-motion-only,hebrew-docx,suno-instrumental-prompt,gh-pages-deploy} ~/.claude/skills/
cp -r claude-code-skills/{video-producer,story-to-video,writer} ~/.claude/agents/
```

It needs `ffmpeg`, Python 3 (`pip install numpy pillow playwright && playwright install chromium`) and a
`GEMINI_API_KEY` environment variable for narration and music. Full details: [film-director/README.md](film-director/README.md).
Then say "make a video about ..." or "direct a film" in Claude Code.

---

### Writing & references

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[writer](writer/)** | Agent | ★★★★★ | Academic writing agent for manuscripts, revisions, grants, reviewer responses, op-eds, social posts and slide blueprints, with anti-AI style rules, a story-first method, a reviewer sub-agent and reference checks. *Scaffold: the personal voice corpus is removed.* Use for any publication-quality text. |
| **[apa-manuscript](apa-manuscript/)** | Skill | ★★★★★ | Generates an APA manuscript in Markdown and Word from R analysis tables, with every statistic and citation pulled from code. Use to write a paper whose numbers must come straight from the analysis. |
| **[ref-check](ref-check/)** | Skill | ★★★★★ | Cross-references every in-text citation in a .docx against its reference list and returns a colour-coded Word file. Use to find citations missing from the list and references never cited. |
| **[ref-verify](ref-verify/)** | Skill | ★★★★★ | Verifies every reference (authors, year, title, journal, pages, DOI) with two independent rounds of web-search sub-agents; exports an Excel audit and a Zotero-ready RIS file. Use before submission. |
| **[ref-context](ref-context/)** | Skill | ★★★★☆ | Checks that each citation actually supports the sentence it is attached to. Use to catch wrong or irrelevant references after the list already matches. |
| **[manuscript-submit](manuscript-submit/)** | Skill | ★★★★☆ | Walks a manuscript from journal selection through reference verification, APA 7 formatting and an automated Elsevier portal upload. Use when a paper is ready to submit. |
| **[gemini-consult](gemini-consult/)** | Skill | ★★★★☆ | Gets a second opinion from Gemini on a draft (writing, style, academic or Hebrew text), optionally as Word comments. Use for a non-Claude review. |
| **[lit-synthesis](lit-synthesis/)** | Skill | ★★★☆☆ | Merges several AI-generated literature-review PDFs into a deduplicated papers database and a funnel-structured APA introduction. Use to draft a literature section. |
| **[jcr-lookup](jcr-lookup/)** | Skill | ★★★☆☆ | Documents how to look up a journal's Impact Factor, rank and quartile through the Clarivate JCR APIs. *Interface only: you supply `jcr_lookup.py`.* Use to report journal metrics. |
| **[web-research](web-research/)** | Skill | ★★★☆☆ | Token-efficient research across the web and academic databases, saved to a dated markdown file. Use to research a topic across sources. |

### Research data & statistics

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[r-coder](r-coder/)** | Agent | ★★★★★ | Writes R as linear, commented, step-saved scripts with a checks checklist, a review packet and a deterministic style linter (`r_lint.py`). *Scaffold: personal style examples removed.* Use for R code a human will review line by line. |
| **[mlm-prepost-design](mlm-prepost-design/)** | Skill | ★★★★★ | Field-standard defaults for multilevel pre-post designs: random effects, effect sizes, multiple comparisons, power by simulation, missing data. Use to plan or analyse within-subjects mixed models. |
| **[diary-numbering-check](diary-numbering-check/)** | Skill | ★★★★★ | R checker for ESM/diary day and slot numbering: duplicates, wraparounds, calendar mismatches, long gaps. Use before any day-level or lagged analysis. |
| **[qualtrics-survey-builder](qualtrics-survey-builder/)** | Skill | ★★★★★ | Builds and changes Qualtrics surveys through API v3: safe updates, blocks, flow, skip logic, Hebrew RTL templates, pre-publish checks. Use to create surveys programmatically without losing data. |
| **[qualtrics-cleaning](qualtrics-cleaning/)** | Skill | ★★★★☆ | R workflow to pull, merge and clean Qualtrics exports and build scales. Use to import and clean survey data in R. |
| **[r-analysis](r-analysis/)** | Skill | ★★★★☆ | R analysis conventions: headers, no-loop style, ASCII-safe comments on Hebrew Windows, multilevel models, sjPlot tables, provenance checks. Use for readable, auditable analysis scripts. |
| **[r-results-narrative](r-results-narrative/)** | Skill | ★★★★☆ | R scripts that write a `Results.md` with tables and paper-ready prose, statistics embedded via `glue()`. Use when finishing an R analysis. |

### Figures, dashboards & data stories

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[dashboard-expert](dashboard-expert/)** | Agent | ★★★☆☆ | Builds interactive research data explorers: precompute to JSON, a single-file HTML, a client-side stats engine, a QA matrix and verified deploys. Use to build a dashboard for a research dataset. |
| **[academic-figures](academic-figures/)** | Skill | ★★★★★ | Publication figures: exact layout in HTML/CSS, a Playwright screenshot, a Gemini polish and self-review. Use for a diagram, flow or architecture figure in a paper. |
| **[dashboard-style](dashboard-style/)** | Skill | ★★★★★ | A dark, data-dense dashboard design system plus a file of UX lessons from real feedback. Use to style any dashboard or data explorer. |
| **[data-storytelling](data-storytelling/)** | Skill | ★★★★☆ | Explorable scroll data stories for a general reader: one mark per real thing, each scroll step changes one encoding, the caveat at the moment it matters, the method open at every depth; a 180k-mark canvas engine and gates. Use to make a dataset or findings accessible to the public. |
| **[scientific-figures](scientific-figures/)** | Skill | ★★★★☆ | Evidence-based rules for data figures (channel ranking, colour accessibility, layout, distortions), after Franconeri et al. 2021. Use to choose or review a chart. |
| **[nano-banana-poster](nano-banana-poster/)** | Skill | ★★★★☆ | Generates images and posters with Gemini image models, with aspect-ratio control and Hebrew/RTL guidance. Use for a poster, a social image or a polished diagram. |

### Presentations & documents

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[presentation-journey-architect](presentation-journey-architect/)** | Agent | ★★★★☆ | Turns a slide deck into a finished online 3D journey by running the four `presentation-3d-*` skills in order and checking the result in a real browser. Use to take a deck end to end. |
| **[presentation-3d-story](presentation-3d-story/)** | Skill | ★★★★☆ | Deck to stops, each with an audience question, its evidence and a reason to move on. Use first when planning a 3D journey. |
| **[presentation-3d-design](presentation-3d-design/)** | Skill | ★★★★☆ | Visual direction for an immersive presentation: composition, readable charts, RTL, motion as meaning. Use after the story plan. |
| **[presentation-3d-build](presentation-3d-build/)** | Skill | ★★★★☆ | Three.js build with readable HTML/SVG panels, camera routes, fallbacks and measured performance. Use to implement the journey. |
| **[presentation-3d-review](presentation-3d-review/)** | Skill | ★★★★☆ | Traces every number to its source, runs a real browser pass and publishes. Use before calling a 3D presentation done. |
| **[nano-deck](nano-deck/)** | Skill | ★★★★☆ | Builds a whole deck as AI-generated slide images assembled into PPTX. Use when designed image slides are wanted and editable text is not. |
| **[html-to-pptx](html-to-pptx/)** | Skill | ★★★★☆ | HTML to PowerPoint, as editable text or pixel-exact images, with RTL. Use to turn HTML slides into a .pptx. |
| **[html-to-pdf](html-to-pdf/)** | Skill | ★★★★★ | Pixel-accurate HTML to PDF with Puppeteer and automatic Hebrew/RTL. Use to export a page or report. |
| **[hebrew-docx](hebrew-docx/)** | Skill | ★★★★★ | Correct RTL Hebrew Word documents with python-docx (bidi at document, paragraph and run level). Use when generating a Hebrew .docx. |
| **[read-docx](read-docx/)** | Skill | ★★★★☆ | Extracts text, tables and tracked changes from .docx files, with Hebrew support. Use to read a Word file. |

### Film, audio & media

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[film-director](film-director/)** | Agent | ★★★★☆ | Owns a film from brief to delivery: writes the treatment, prices the build, routes production to the right skill or agent, gates voice, mix, cuts and subtitles in code, delivers once and records each lesson. Use to make or revise a narrated, animated or promo film. |
| **[video-producer](video-producer/)** | Agent | ★★★★☆ | A narrated MP4 end to end: TTS, illustrated frames, annotated screenshots, Ken Burns motion, subtitles, ffmpeg assembly, with QC. Use for training, explainer or promo videos. |
| **[story-to-video](story-to-video/)** | Agent | ★★★★☆ | Turns a testimony, transcript or written story into an illustrated, narrated video with consistent watercolour characters. Use for a memorial, family or children's story video. |
| **[code-drawn-film](code-drawn-film/)** | Skill | ★★★★☆ | Narrated, animated short films drawn entirely in code (cut-paper canvas engine, puppet rig, parallel render) with a designed voice, generated music, foley and PASS/FAIL gates on the finished mp4. Use for a code-drawn explainer, tribute or music video. |
| **[ai-live-action-video](ai-live-action-video/)** | Skill | ★★★★☆ | Short films from AI live-action footage (Veo): faces held across clips, safe prompts for sensitive subjects, audio-first assembly, screen captures and output gates. Use for a demo or explainer with AI actors. |
| **[audio-producer](audio-producer/)** | Skill | ★★★★☆ | Gemini TTS through one tested module: Hebrew-capable voices, voice design, consent-only cloning, style tags and a per-take quality gate. Use for any narration or batch TTS job. |
| **[ffmpeg-motion-only](ffmpeg-motion-only/)** | Skill | ★★★★☆ | Cuts a long screen recording down to its moving frames (mpdecimate plus re-timing). Use to shorten a demo or lecture recording. |
| **[synth-typing-sounds](synth-typing-sounds/)** | Skill | ★★★★☆ | Synthesises keyboard-typing audio in pure-stdlib Python and muxes it under a video. Use for demo-video sound design. |
| **[suno-instrumental-prompt](suno-instrumental-prompt/)** | Skill | ★★★☆☆ | Writes Suno prompts for purely instrumental music. Use for backing tracks without Suno singing your directions. |

### Privacy & security

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[privacy-compliance](privacy-compliance/)** | Agent | ★★★★☆ | Audits systems and code, writes DPIAs, policies and incident plans under HIPAA, GDPR and Israeli privacy law. Use when a system handles personal or health data. |
| **[anonymize-hebrew](anonymize-hebrew/)** | Skill | ★★★★★ | Hebrew-aware PII scrubbing for text, Word and PDF, word-boundary-safe, with a leak check. Use before Hebrew data goes to a cloud service or an outside reader. |
| **[block-files](block-files/)** | Skill | ★★★★★ | Adds `permissions.deny` rules so Claude's Read tool cannot open sensitive files. Use to keep data files out of a session (it does not stop shell commands; see its notes). |
| **[privacy-gdpr](privacy-gdpr/)** | Skill | ★★★★☆ | GDPR requirements and checklists: lawful basis, rights, breach timelines, DPIA, transfers. Use for EU data subjects. |
| **[privacy-hipaa](privacy-hipaa/)** | Skill | ★★★★☆ | HIPAA checklists plus a guide to HIPAA-ready AI infrastructure on Google Cloud. Use for health-data systems. |
| **[privacy-check](privacy-check/)** | Skill | ★★★☆☆ | Routes a compliance check to the right framework and merges results across jurisdictions. Use when it is unclear which law applies. |

### Claude Code workflow

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[artifact-lock-7clean](artifact-lock-7clean/)** | Skill | ★★★★★ | Locks a derived artifact against approved sources through 7 consecutive clean hostile audits, then a lock bundle. Use to freeze high-stakes code, protocols or questionnaires. |
| **[claude-cli-subprocess](claude-cli-subprocess/)** | Skill | ★★★★★ | Calls `claude -p` as a subprocess for LLM calls inside pipelines, with Windows gotchas. Use instead of paid SDK calls in scripts. |
| **[claudeception](claudeception/)** | Skill | ★★★★★ | Extracts non-obvious, verified knowledge from a session into a new reusable skill. Use after a hard-won fix or workaround. |
| **[skill-maker](skill-maker/)** | Skill | ★★★★★ | Creates a new `SKILL.md` from a plain-language description. Use to turn a repeatable task into a skill. |
| **[agent-maker](agent-maker/)** | Skill | ★★★★☆ | Creates reusable subagent files and checks that each loads. Use to define a persistent named agent. |
| **[ai-context-engineer](ai-context-engineer/)** | Skill | ★★★★☆ | Structures a request as Context, Constraints and Goal, with templates. Use before an important AI task. |
| **[ai-prompting-optimizer](ai-prompting-optimizer/)** | Skill | ★★★★☆ | Scores a prompt on ten principles and rewrites it. Use to improve a prompt before sending it. |
| **[mistake-analyzer](mistake-analyzer/)** | Skill | ★★★★☆ | Turns logged tool failures into root-cause lessons and prevention rules. Use to stop repeating the same mistakes. |
| **[context-check](context-check/)** | Skill | ★★★☆☆ | Pins down project, goal, files and output before work starts. Use when a request arrives without saying which file or subset. |

### Dev & publishing utilities

| Item | Type | Quality | What it does |
|---|---|---|---|
| **[gh-pages-deploy](gh-pages-deploy/)** | Skill | ★★★★☆ | Deploys static HTML/CSS/JS to GitHub Pages with `gh`. Use to publish a site, tool or demo. |
| **[git-quick](git-quick/)** | Skill | ★★★☆☆ | Quick GitHub operations with `gh`: auth, create, push, status. Use to work with GitHub without a browser. |
| **[python-windows](python-windows/)** | Skill | ★★★☆☆ | Runs Python on Windows through the `py` launcher. Use to avoid the broken Store-Python stub. |

## Licence

MIT. Use them, change them, share them.
