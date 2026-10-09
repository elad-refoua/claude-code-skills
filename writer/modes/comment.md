# Mode: Comment / Broad-Audience Piece

Journal Comments, Perspectives, and commentary pieces for a broad scientific audience
(npj / Nature-family Comments and similar venues).

**Trigger keywords**: "Comment", "Perspective", "npj Comment", "Nature Comment", "commentary"

Canonical sources: your plain-story / example-led / hand-holding lesson (keep it in
`agent-memory/writer/`) and the antithesis HARD BAN (AGENT.md; writing-rules.md 6.31). This file
maps them onto the genre; on any conflict, the lessons win.

---

## What a Comment is (and how it differs from a manuscript)

- A plain, focused STORY told to a smart non-specialist: an example-led argument, told simply.
- **~1,200-1,500 words.** Do not pad — focused and sharp, not long.
- **Standfirst, no abstract.** A 1-2 sentence bolded standfirst under the title carries the whole
  argument. Skip the IMRaD machinery from manuscript mode (Argument Map scaffold, R-generated
  Results, journal-profile section rules) — a Comment has none of those parts.
- **Hand-hold.** Introduce every concept before using it; assume the reader has NOT read the
  framework.
- **Example-led.** Every axis/category/claim carries a named REAL study in one lay-plain sentence.
  Zero abstract, uncited examples.
- **One sentence of philosophy max**, disavowing ("we borrow the labels and leave the philosophy
  there"). Non-pretentious throughout.
- **The author's specified arc WINS.** When the user gives the parts and their order, build exactly
  to it; never impose your own structure.

## Method (style-hard genre: draft panel, never one-and-done)

1. Research the real-study examples FIRST (one plain sentence + a real citation per category).
2. Generate 2-3 INDEPENDENT plain-style drafts from different narrative angles.
3. Gate each with `scripts/writer_lint.py`; the ANTITHESIS target for a Comment is ~0 (this genre
   is where the ban originated — a rejected draft carried 24 negation sentences).
4. Pick the CLEANEST draft by counted defect, then apply a small punch-list. Never re-polish an
   AI-sounding draft; self-editing regrows its tells.

## Venue front-matter (verify against current author guidelines)

- Nature-family Comments (DIRECTIONAL, from a single observation): DELETE the in-body
  title/author/affiliation/corresponding block (the portal fields carry those); ADD Data
  Availability and Ethical approval statements. Keep venue-specific notes in
  `lessons/journal_adaptation.md`.
- Check the venue's reference cap and standfirst format in its current author guidelines before
  submission; never assume them.

## Everything else

Loading Sequence, LOAD MANIFEST, independent review, lint gate (MOVE 4), learning loops: all per
AGENT.md. This mode changes the genre scaffold only.
