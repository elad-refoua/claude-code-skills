# Claude Code — Skills & Agents

A curated, privacy-scrubbed collection of Claude Code **skills** and **agents**, built and
used in real academic, clinical and research work, then stripped of personal data so they
drop into your own setup.

Shared by [Elad Refoua](https://eladrefoua.com).

> **⚠️ Most items need a small adjustment before they run.** Names, paths, contacts and
> project specifics were replaced with placeholders such as `<SET_YOUR_PATH>`,
> `<YOUR_API_KEY>`, `<USER>` and `<ADVISOR>`. Anything carrying a placeholder will not work
> untouched. Open the item's own file and fill them in.

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

# one skill
cp -r claude-code-skills/ref-verify ~/.claude/skills/

# one agent
cp -r claude-code-skills/writer ~/.claude/agents/
```

Then open the file you copied and replace any `<PLACEHOLDER>` it contains.


## 🤖 Agents (6)

| Agent | Quality | What it does |
|---|---|---|
| **[dashboard-expert](dashboard-expert/)** | ★★★☆☆ | Builds interactive **research data explorers** (R/Python→JSON→HTML) with a client-side stats engine (OLS, logistic, Sobel mediation, moderation). Use to turn analysis output into a shareable dashboard. |
| **[privacy-compliance](privacy-compliance/)** | ★★★★☆ | Privacy Compliance Officer covering **HIPAA, GDPR, and Israeli Privacy Law** — assessments, DPIAs, code review, incident plans. Use when a system touches personal or health data. |
| **[r-coder](r-coder/)** | ★★★★★ | Reviewable-R-code agent that enforces a 13-rule **R Style Constitution** (linear narrative scripts, config-as-data, semantic selection, per-step save + PASS/FAIL, checks-checklist, Results.md via glue()) plus a deterministic `r_lint.py` gate. *Scaffold — personal style examples removed.* Use for any R analysis/cleaning code a human will review. |
| **[story-to-video](story-to-video/)** | ★★★★☆ | Turns a personal story or YouTube transcript into an **illustrated narrated video** with consistent watercolor characters (Hebrew/English). Use for testimony, memorial, or children's story videos. |
| **[video-producer](video-producer/)** | ★★★★☆ | End-to-end **narrated video** pipeline: TTS (30-voice Hebrew/English), AI-illustrated frames, Ken Burns effects, ASS subtitles, ffmpeg assembly. Use for training/explainer/promo videos. |
| **[writer](writer/)** | ★★★★★ | Publication-quality academic writing agent (APA 7th) with a THINK→WRITE→VERIFY pipeline, a 31-check anti-AI-detection system (grounded in Kobak et al. 2025), and modes for grants/comments/posts/opinion/revision. *Scaffold only — personal voice corpus removed.* Use for manuscripts, grants, or any publication-quality text. |

## 🧩 Skills (44)

| Skill | Quality | What it does |
|---|---|---|
| **[academic-figures](academic-figures/)** | ★★★★★ | Publication figures via HTML layout + Gemini polish (exact label control). Use for any paper figure. |
| **[agent-maker](agent-maker/)** | ★★★★☆ | Creates agent definition files. Use to define a persistent named agent. |
| **[ai-context-engineer](ai-context-engineer/)** | ★★★★☆ | Structure any prompt via Context/Constraints/Goal + domain templates. Use before complex AI tasks. |
| **[ai-prompting-optimizer](ai-prompting-optimizer/)** | ★★★★☆ | Scores a prompt on 10 principles and rewrites it. Use to improve a prompt before sending. |
| **[anonymize-hebrew](anonymize-hebrew/)** | ★★★★★ | Hebrew-aware PII scrubber for text/Word/PDF (word-boundary-safe). Use before sending Hebrew data to the cloud. |
| **[apa-manuscript](apa-manuscript/)** | ★★★★★ | Generates APA Word manuscripts from R output via `glue()` — every statistic pulled from code, with a CSV citation system. Use to write a paper from analysis tables. |
| **[artifact-lock-7clean](artifact-lock-7clean/)** | ★★★★★ | Locks a derived artifact against an approved source-of-truth via **7 consecutive clean hostile audits** + behavioral smoke-tests, then a lock bundle. Use to freeze high-stakes code/protocols/questionnaires before submission. |
| **[block-files](block-files/)** | ★★★★★ | Hard-block Claude from reading sensitive files via `permissions.deny`. Use to protect data/credentials. |
| **[claude-cli-subprocess](claude-cli-subprocess/)** | ★★★★★ | Call `claude -p` as a subprocess for **free** LLM calls in pipelines. Use to replace paid SDK calls in scripts. |
| **[claudeception](claudeception/)** | ★★★★★ | Extracts reusable knowledge from a finished session into a new skill. Use after non-obvious debugging/workarounds. |
| **[context-check](context-check/)** | ★★★☆☆ | Pre-work checklist that nails scope/files/output before acting. Use at the start of ambiguous multi-step tasks. |
| **[dashboard-style](dashboard-style/)** | ★★★★★ | Dark research-UI design system + 17 hard-won design lessons. Use to build a standalone HTML dashboard. |
| **[diary-numbering-check](diary-numbering-check/)** | ★★★★★ | Validates ESM/diary day & time numbering (wraparound, duplicates, calendar skips). Use before any lag analysis. |
| **[ffmpeg-motion-only](ffmpeg-motion-only/)** | ★★★★☆ | Trim screen recordings to motion-only moments (mpdecimate). Use to compress demo/lecture recordings. |
| **[gemini-consult](gemini-consult/)** | ★★★★☆ | Get a second opinion from Gemini 3 Pro (writing/process/ideas), embeddable as Word comments. Use for a cross-model review. |
| **[gh-pages-deploy](gh-pages-deploy/)** | ★★★★☆ | Deploy static HTML to GitHub Pages via `gh`. Use to publish a site/tool/demo. |
| **[git-quick](git-quick/)** | ★★★☆☆ | Fast GitHub ops via `gh` (create/push/auth). Use for a no-browser GitHub workflow. |
| **[hebrew-docx](hebrew-docx/)** | ★★★★★ | Correct 3-level RTL Hebrew Word docs via python-docx. Use when generating Hebrew .docx. |
| **[html-to-pdf](html-to-pdf/)** | ★★★★★ | Pixel-perfect HTML→PDF (Puppeteer) with Hebrew/RTL. Use for reports/exports from HTML. |
| **[html-to-pptx](html-to-pptx/)** | ★★★★☆ | HTML→PowerPoint (text or image mode) with RTL. Use to generate slides from HTML. |
| **[jcr-lookup](jcr-lookup/)** | ★★★☆☆ | Journal Impact Factor / ranking / quartile via Clarivate JCR API. Use for CV or publication metadata. |
| **[lit-synthesis](lit-synthesis/)** | ★★★☆☆ | Merges several AI literature-review PDFs into a cohesive APA introduction + papers DB. Use to synthesize lit reviews. |
| **[manuscript-submit](manuscript-submit/)** | ★★★★☆ | End-to-end submission: journal selection, reference verification, APA formatting, Elsevier portal automation. Use when ready to submit. |
| **[mistake-analyzer](mistake-analyzer/)** | ★★★★☆ | Root-cause (5-Whys) analysis of tool failures → prevention rules. Use periodically to reduce repeat mistakes. |
| **[mlm-prepost-design](mlm-prepost-design/)** | ★★★★★ | Field-standard defaults for multilevel pre-post studies (random effects, effect sizes, power, missing data) — all references DOI-verified. Use when planning/analyzing within-subjects MLM. |
| **[nano-banana-poster](nano-banana-poster/)** | ★★★★☆ | Generate images/posters via Gemini (Nano Banana). Use for AI images or HTML-screenshot diagrams. |
| **[nano-deck](nano-deck/)** | ★★★★☆ | Generate full AI-image presentations assembled into PPTX. Use to build an AI-designed deck. |
| **[privacy-check](privacy-check/)** | ★★★☆☆ | Router that picks the right privacy framework for your project. Use when the jurisdiction is unclear. |
| **[privacy-gdpr](privacy-gdpr/)** | ★★★★☆ | GDPR reference: principles, rights, breach timelines, DPIA. Use for EU data subjects. |
| **[privacy-hipaa](privacy-hipaa/)** | ★★★★☆ | HIPAA checklist + GCP/Vertex AI (WIF) setup guide. Use for health-data systems. |
| **[python-windows](python-windows/)** | ★★★☆☆ | Use the `py` launcher for all Python on Windows. Use to avoid Store-Python stub failures. |
| **[qualtrics-cleaning](qualtrics-cleaning/)** | ★★★★☆ | Import + clean Qualtrics data in R (merge branches/rounds, build scales). Use to clean survey exports. |
| **[qualtrics-survey-builder](qualtrics-survey-builder/)** | ★★★★★ | Build/modify Qualtrics surveys via API v3 (safe update pattern, Hebrew RTL, branching). Use to create surveys programmatically. |
| **[r-analysis](r-analysis/)** | ★★★★☆ | Consistent R style (headers, no loops, MLM, sjPlot, ggplot). Use for any reproducible analysis script. |
| **[r-results-narrative](r-results-narrative/)** | ★★★★☆ | R scripts that auto-write `Results.md` with tables + paper-ready prose (embedded stats). Use when finishing an R analysis. |
| **[read-docx](read-docx/)** | ★★★★☆ | Extract text/tables/tracked-changes from .docx (Windows). Use to read Word files. |
| **[ref-check](ref-check/)** | ★★★★★ | Cross-references the in-text citations against the reference list in a .docx and returns a colour-coded Word file: green matched, cyan fuzzy, yellow cited but missing from the list, red listed but never cited. |
| **[ref-context](ref-context/)** | ★★★★☆ | Checks whether each citation actually supports the sentence it is attached to, which is the failure that survives proofreading. |
| **[ref-verify](ref-verify/)** | ★★★★★ | Verifies every reference for factual accuracy (authors, year, title, journal, pages, DOI) with double-control web-search sub-agents. Outputs an Excel table and a Zotero-ready RIS file. |
| **[scientific-figures](scientific-figures/)** | ★★★★☆ | Evidence-based viz guidance (channels, palettes, accessibility), per Franconeri et al. 2021. Use when choosing chart types. |
| **[skill-maker](skill-maker/)** | ★★★★★ | Generates new `SKILL.md` files from a description. Use to author your own skills. |
| **[suno-instrumental-prompt](suno-instrumental-prompt/)** | ★★★☆☆ | Write Suno prompts for purely instrumental music. Use for talk/demo backing tracks. |
| **[synth-typing-sounds](synth-typing-sounds/)** | ★★★★☆ | Synthesize keyboard typing sounds in pure-Python stdlib. Use for demo-video sound design. |
| **[web-research](web-research/)** | ★★★☆☆ | Token-efficient multi-source web research → dated markdown. Use to research a topic across sources. |

## Quality rating

An honest self-assessment of how polished and broadly useful each item is:
★★★★★ flagship · ★★★★☆ strong · ★★★☆☆ solid but niche · ★★☆☆☆ thin.

## Licence

MIT. Use them, change them, share them.
