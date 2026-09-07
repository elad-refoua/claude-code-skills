---
name: presentation-3d-story
description: >-
  Use when turning a source presentation into the narrative and scene plan for an interactive 3D journey, or repairing an existing journey's unclear story, examples, or research explanations. TRIGGERS: presentation to 3D, deck to journey, spatial storytelling, slide-to-scene mapping, מסע תלת ממדי, מצגת בתלת מימד, להפוך מצגת למסע, סיפור במרחב. Covers source-faithful narration and meaningful scene transitions; visual production, implementation, and browser review use the companion skills.
---

# Presentation 3D Story

Make the source argument understandable through a sequence of places, viewpoints, and actions. A beautiful scene needs a job in that argument.

## Scope and handoff

- Work with `presentation-journey-architect` when that coordinating agent is available. This skill can also produce a standalone narrative plan.
- Send scene intentions to [presentation-3d-design](../presentation-3d-design/SKILL.md), approved content and fact IDs to [presentation-3d-build](../presentation-3d-build/SKILL.md), and evidence boundaries to [presentation-3d-review](../presentation-3d-review/SKILL.md). Use companions when available and relevant; their absence does not prevent source mapping.
- Respect existing authorization. Concept development is a work step, not an automatic approval pause. Ask only about consequential missing information; continue independent work.

## 1. Establish the source contract

- Read the actual deck, including speaker notes and visual content, using the available presentation-reading tools. Identify current project instructions and prior accepted decisions.
- Record audience, purpose, duration, language/direction, required wording, credits, source files, delivery scope, and existing project identity. Reuse supplied context instead of asking again.
- Preserve slide order as the default narrative spine. When the user requests fidelity, preserve the requested order and wording; record source-slide mappings for any necessary split or combination.
- Distinguish a wording preference from a factual error. Document sourced corrections; do not silently preserve an unsupported claim for fidelity or silently rewrite requested terminology for style.
- Use a dated output folder and obey source-preservation constraints. Never read or use raw clinical or participant records without explicit permission for that specific use; filenames alone do not authorize reading.
- Start [the story template](templates/journey-story.yaml). Unknown facts stay `unverified` with null values; missing scope information stays explicit.

## 2. Map the argument before writing the scenes

For each source slide, record the audience question, its job in the argument, the evidence, the main meaning, and the question that follows. Account for every source slide without assuming a fixed number of stops.

Separate what the audience sees immediately from optional depth:

1. Define unfamiliar terms needed to understand the stop.
2. State the finding or idea in ordinary language.
3. Explain its consequence for the audience's question.
4. Put methods, detailed statistics, and citations in accessible notes/details, retaining essential qualifications beside the claim.

Use the available `aitom` skill for reader awareness: identify what this audience already knows, what the current stop must teach, and what they might misread. Do not infer that a technical audience knows every construct. Do not update reader memories without an explicit user request.

For scholarly or professional research material, read [research narration](references/research-narration.md) before drafting or revising substantive claims. Use the available writer agent and its complete canonical stack when required, rather than writing around a lightweight summary.

## 3. Explore a small set of coherent concepts

When the spatial concept is unsettled, develop a few meaningfully different options. For each, specify the central subject, world, audience viewpoint, recurring visual motif, and how movement reveals the argument. Explain why it fits this source and its audience.

Avoid making a room, a human character, or a chronological biography the universal default. A system, landscape, process, collection, or network may fit better. Use generated concept images when they help settle composition or roles; they do not substitute for a working 3D scene or evidence.

Select using the user's expressed preferences and available evidence. Build a representative working slice before expanding: an opening, a demanding explanation, a contrasting type of stop, and meaningful transitions. Adapt the sample to the task; a narrow revision needs only the affected slice.

## 4. Give each stop and transition a reason

- Specify camera focus, visible objects, interaction, and movement in terms of what they explain. Keep the audience oriented during travel and at rest.
- State the conceptual handoff: a new question, perspective, population, paper, scale, or phase. Camera travel alone does not create a transition.
- Introduce a new paper with its title or short identity and the question it addresses. Explain shared samples instead of presenting every paper as independent evidence.
- Make viewpoint choices explicit: name whom or what the audience can select and what that selection reveals.
- Keep recurring roles and language consistent. Small resting motion can convey life; animation must not imply an unmeasured outcome or causal process.
- For each metaphor, specify what maps to the concept and what must not be inferred. Distinguish symbols from quantitative marks. A growing object needs a clear conceptual label unless its growth encodes verified data.

## 5. Add examples only where they improve understanding

- Give a fictional character a concrete concern, not a speech announcing the presentation's thesis. Tie each excerpt to the current stop's construct or question.
- Source plausible themes from authorized aggregate findings or published syntheses; do not adapt individual participant stories or clinical cases without specific permission.
- Label fiction visibly. Record its source basis and why it belongs. A source supports the theme, not the invented exchange or its outcome.
- Vary response styles naturally: a question, tentative reflection, practical suggestion, or editable draft. Keep speakers distinct; a chatbot need not sound like a therapist.
- Use a recurring thread only while its continuity is defensible. Label alternative situations separately instead of turning unrelated associations into one person's causal progression.
- Keep excerpts compact and preserve the main evidence panel. Choose length from the available display area, then check rendered lines; never truncate away meaning to satisfy a character target.

## 6. Deliver a traceable narrative package

Complete the relevant sections of the template: intake, concepts, stops, facts, dialogue, and metaphors. Remove unused optional sections from the task deliverable. Provide exact copy in machine-readable fields plus a concise argument map when it helps review.

This YAML is an authoring record, not the review validator's JSON input. For structural checks after implementation, export the smaller manifest using the explicit [field mapping](../presentation-3d-review/references/manifest-contract.md#export-from-the-story-template). Keep the rich source/wording record; do not discard it in the export. A conceptual illustration is a presentation mode, independent of whether its source argument is theory, description, or another evidence type.

Carry forward source IDs even when numbers move to details. Record changes to requested wording and unresolved evidence gaps. Do not invent values, citations, publication status, model predictions, or participant characteristics.

Review the final composed content, including titles, short map labels, captions, notes, paper cards, source drawers, expanded views, and scene cues. Layered overrides may leave stale claims in secondary surfaces. Distinguish copy validation from the companion review skill's browser verification before declaring the user-facing journey complete.
