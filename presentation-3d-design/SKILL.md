---
name: presentation-3d-design
description: |
  Use when designing or refining the appearance of an immersive 3D presentation derived from a slide deck: scene composition, people and symbolic objects, readable charts, RTL typography, and meaningful camera framing.
  TRIGGERS: "3D presentation design", "make the journey beautiful", "cinematic presentation", "עיצוב מצגת תלת ממדית", "מסע תלת ממדי יפה", "הגרפים לא ברורים" in a 3D presentation. Not a general dashboard or ordinary PowerPoint styling skill.
---

# Design a readable, inhabited 3D presentation

Make the scene explain the audience's question. Polish comes from composition, proportion, materials, light, and type; the viewer must still read the evidence immediately.

## Start from meaning

Read the source deck and current storyboard before choosing a visual metaphor. For a new journey, use `presentation-3d-story` first. For an existing one, inspect actual browser screenshots, the final composed content, and the files that own its appearance.

Describe the visual direction in a few concrete decisions: spatial setting; subjects and their roles; material palette; lighting; type hierarchy; space reserved for evidence. Read [art-direction.md](references/art-direction.md) for the concept-image brief and corrective patterns learned from an actual build.

Create two or three meaningfully different concepts when the setting remains open. Compare what each reveals, the audience's reading burden, implementation effort, and expected reuse. Select a direction using the user's stated preferences; an already approved direction does not need a new approval ritual.

## Prove the visual system in the browser

Build a representative working slice: a wide inhabited scene, a difficult data stop, and a conceptual or perspective-change stop. Include the transition between them. A generated reference establishes direction; a browser screenshot establishes implementation quality. Label them accordingly.

If image generation is available and useful, generate a reference with the image tool. For an existing scene, inspect its screenshot and supply it as the edit reference. Preserve the requested people, roles, positions, and palette. Generate atmosphere and composition without embedded chart text. Implement actual geometry and assets afterward.

Choose modeling effort by visible benefit. Use licensed rigged models for close-up people, procedural geometry for symbolic sculptures, and instancing for repeated architecture. Consider Blender when custom anatomy, rigging, sculpting, UVs, or baking materially improve a required shot. An online result can load an exported GLB; Blender is an optional authoring tool, not a runtime dependency. Do not install it merely because the scene is 3D.

## Compose the person, world, and evidence together

- Give every stop a physical focus and a clear evidence area. Keep faces, hands, screens, and the object being explained unobscured.
- Use role-based framing: a face for a person's experience, a device for what happens in an interaction, another person's station for a new perspective, a wider view for system-level implications. Choose subjects appropriate to this deck, rather than copying the original mental-health room.
- At a conceptual comparison, show the compared roles explicitly. Two generic icons often fail to explain the difference.
- Keep one visual mapping consistent. In the original needs example, bronze represented the human and teal the AI: a listening AI companion for relational support, a smaller AI console beside a person choosing steps for agency. The device supports the central human; it does not take over the action.
- Use a concise role caption and familiar example. A face inside an AI cloud can illustrate anthropomorphism; frame it as perceived human qualities, not evidence of machine feelings. Symbolic steps and glows are illustrations unless they encode sourced quantities explicitly.
- Preserve exact requested names, titles, and credit placement. Important credit can remain continuously visible in a restrained footer; repetition and size are not substitutes for clear attribution.

## Keep charts and text optically stable

Use HTML/SVG for primary research text and charts. Avoid perspective-distorted bars, low-resolution text textures, and percentage-as-particle-count decoration. Main reading surfaces should be opaque enough to retain contrast against every scene behind them.

Check computed foreground/background colors, then inspect the actual rendering. A palette token alone does not prove contrast: inherited rules, transparent surfaces, CSS3D compositing, tone mapping, and hover styles can change the result. As a design target, use at least 4.5:1 for normal text and 3:1 for large text and meaningful graphical marks; distinguish series through labels and shape as well as color.

Size type for the projected size of the panel, not its untransformed CSS dimensions. A nominal 28px label can become tiny after a world transform. Test at presentation resolution and at the actual compact app-panel size. Do not fix crowding only by shrinking everything.

Explain the construct before displaying a coefficient. A graph needs a question, labeled denominator/unit, main result, and concise meaning. Put technical details in an accessible enlarged/source view when that helps the main story. Keep qualifications needed for a fair interpretation in the main view.

## RTL and responsive composition

- Use `lang="he"`, `dir="rtl"`, logical CSS properties, deliberate alignment, and a Hebrew-capable font. Isolate English titles, signed values, confidence intervals, and mathematical expressions with `<bdi>` or explicit LTR spans.
- Test reading order, sign placement, chart direction, next/back controls, and keyboard behavior; mirroring the page is not sufficient.
- Keep wide hero shots responsive to aspect ratio. Measure projected bounds, and reposition or compact peripheral paper cards before they cover faces or headings.
- In portrait, provide a readable scrollable layout with the same definitions, numbers, source access, and credits. Use SVG equivalents for world-only sculptures in reading and enlarged views.
- Clicking a chart or slide should expose a large, high-contrast view. Give keyboard focus, Escape-to-close, and focus return. Avoid turning text selection or a drag into an unwanted zoom click.

## Motion as visual meaning

Camera travel belongs to the transition. At rest, give the user small bounded movement while keeping content stable. Use local breathing, a brief typing gesture, light, or an AI form to keep the scene alive. Repeated automatic camera rocking quickly feels like going nowhere.

Animate only what the stop motivates. Typing belongs near a relevant interaction; it should not recur mechanically at every stop about a person. Do not dramatize a correlational finding as an inevitable emotional transformation. Caption a change of conversational focus if useful; avoid production language such as "behind the head".

## Hand off

Deliver the visual brief, chosen references with provenance, representative real browser screenshots, asset/license list, and remaining visual issues. Continue with `presentation-3d-build` for implementation and `presentation-3d-review` for audience and publication checks.
