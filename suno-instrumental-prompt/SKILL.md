---
name: suno-instrumental-prompt
description: Write Suno AI prompts for purely instrumental music. The critical rule: ALL stylistic and structural guidance goes in the Style field, the Lyrics field gets ONLY the [Instrumental] tag. Otherwise Suno sings your stage directions as actual lyrics. Includes mood-to-style mappings for clinical/academic demo videos, conference talks, and ambient backing tracks.
---

# Suno Instrumental Prompts

## When to use

User wants AI-generated background music for a video, demo, lecture, or any
context requiring instrumental-only output. Often paired with conference demos
where licensing concerns matter (Suno-generated tracks are user-owned).

Triggers:
- "suno prompt for instrumental"
- "music for my video"
- "background track for talk"
- "prompt for suno"
- "פרומפט לסונו"

## The critical rule

**Style field** = ALL guidance (instruments, mood, tempo, structure, influences)
**Lyrics field** = ONLY `[Instrumental]`

If you put structure directions in Lyrics (e.g., "[0:00] solo piano, then cello
enters") Suno will literally SING those words. The user we learned this from
caught the mistake immediately ("הוא יגיד את שמות הכלים, לא?").

## Anatomy of a working prompt

### Style field structure
```
[primary descriptor], [instrument lineup], [tempo + feel], [in the style of <artists>], [hard constraints]
```

### Real working example (conference demo, used and approved)
```
neoclassical instrumental, piano-led with sustained cello and viola entering halfway, slow 65 BPM, sparse and breathing, intimate contemplative mood, in the style of Ólafur Arnalds and Erik Satie's Gymnopédies, no drums, no percussion, no vocals, dynamic arc that starts with solo piano then adds soft strings then returns to solo piano, unresolved fade out at the end
```

### Lyrics field
```
[Instrumental]
```

That's it.

## Mood-to-style mappings (clinical/academic demos)

### Warm, contemplative, "trying parent" / medium-success demo
```
neoclassical, solo piano with soft sustained strings, slow 65 BPM, sparse and breathing, in the style of Ólafur Arnalds, no drums, no vocals
```
Artists to reference: Ólafur Arnalds, Yann Tiersen, Hania Rani

### Failure, rupture, unresolved emotional pull
```
neoclassical, piano and cello, slow 60 BPM, contemplative with quiet ache, no resolution, in the style of Max Richter "On the Nature of Daylight", no drums, no percussion, no vocals
```
Artists to reference: Max Richter, Jóhann Jóhannsson, Hauschka

### Triumphant, resolution, hope
```
neoclassical, piano with strings swelling, slow build, moderate tempo, hopeful and resolving, in the style of Ludovico Einaudi, no drums, no vocals
```
Avoid this for clinical demos — too on-the-nose. Use for completion/closing.

### Tense, clinical, observational (medical / autopsy / forensic vibe)
```
minimalist piano, very slow 50 BPM, sparse single notes with long pauses, cold but not cruel, in the style of Nils Frahm "Said and Done", no drums, no vocals, no strings
```

### Public-domain safe alternative
```
classical solo piano, Erik Satie Gymnopédie style, very slow, contemplative, no vocals, no other instruments
```
If true PD is critical, just use original Satie recordings (1888) directly.
Suno's "in the style of" output is freshly generated and Suno-licensable, so
this is mostly about feel.

## Hard constraints to remember

Suno sometimes ignores instructions. Add these to Style as needed:
- `no drums, no percussion` — Suno's default rhythm tendency
- `no vocals` — even with `[Instrumental]`, occasionally vocalists slip in
- `strictly instrumental` — emphasis helps
- `tempo <BPM>` — Suno respects rough tempo; specify if needed
- `length <minutes>` — Suno respects up to its model limit

## Iterate, don't agonize

Suno is stochastic. Generate 2-4 candidates per prompt, pick the best.
If all are wrong (too fast, too cheerful, has drums), tighten the Style field
with one more explicit constraint and regenerate.

## Lyrics-field tags that actually work

The only safe Lyrics-field content for instrumentals:
- `[Instrumental]` — the standard
- `[Instrumental, ambient]` — sometimes more reliable
- Empty (leave blank) — works in some Suno versions, not all

Anything else (e.g., `[0:00 piano]`, `[verse]`, `[chorus]`, descriptive text)
risks vocal generation.

## Typical workflow

1. User describes desired mood in plain language ("warm but tentative, medium-skill parent demo")
2. We write the Style field + give `[Instrumental]` for Lyrics
3. User generates in Suno Custom Mode, gets 2-4 candidates
4. User picks one, downloads MP3
5. We mux under their silent video with `volume=0.85` and `afade` (see ffmpeg-motion-only skill)
