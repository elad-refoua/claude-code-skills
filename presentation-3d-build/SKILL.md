---
name: presentation-3d-build
description: >-
  Build or refine an online Three.js presentation as a meaningful spatial journey, with readable HTML/SVG evidence panels, camera choreography, responsive fallbacks, measured rendering performance, and a scoped static-site build. TRIGGERS: "3D presentation", "Three.js presentation", "spatial presentation", "camera tour", "מצגת תלת ממדית", "מסע תלת ממדי", "סיור במרחב", "מצגת ב-three.js". Use for implementation after the story and visual direction are sufficiently defined; not for a plain slide deck or unrelated 3D modelling.
---

# Presentation 3D Build

Build a browser presentation whose movement and objects explain the subject. Preserve the user's existing project, content order, publication identity, and file boundaries.

## Establish the implementation boundary

- Read the actual entrypoint, content schema, scene, camera, styles, build, and handoff before choosing integrations.
- Keep source documents and individual research records outside the runtime. Use approved aggregate findings and explicitly identified fictional illustrations.
- Work in the authorized location. When protecting an inherited project, a dated child workspace and hashes of the protected originals provide an auditable boundary.
- Use Three.js directly when geometry/materials satisfy the brief. Blender is optional for authored models or animation; export suitable web assets if used. The audience should need only the online site.
- Do not add a backend, chat service, paid API, installation, or publishing destination merely because it could support the scene.

## Separate responsibilities

Keep content/facts, camera stops, scene construction, interaction, and publication independently understandable. Existing file boundaries may already serve this purpose; avoid refactoring only to match a template.

- Content owns slide identity, headings, evidence, qualifications, sources, and illustrative dialogue.
- Camera stops own viewpoint, subject, optional waypoints, framing, and relevant activity.
- Scene modules own geometry, materials, bounded updates, visibility, and disposal where needed.
- UI owns navigation, accessible enlargement, sources, reading fallback, and pause state.
- Build owns approved output files, dependency resolution, asset licenses, base paths, and cache versions.

The same content should feed the spatial panels, enlargement, mobile reading, and source drawer. Keep identifiers for source facts even when their numeric detail moves out of the main view.

## Choreograph a meaningful tour

- Give consecutive stops a different reason to exist: a face, phone, everyday object, AI, professional, or wider context. Varying coordinates alone does not make a story.
- Keep the room's objects stable; compose each destination around the subject and actual reading space.
- For sustained travel, use an authored path with smooth endpoints, distance-aware duration, reverse traversal, and deliberate handling of interrupted navigation and map jumps.
- At rest, prefer a steady camera with small bounded pointer/drag movement. Animate relevant activity in the scene rather than continuously rocking the viewpoint.
- Audience captions should name a meaningful change of focus. Do not narrate technical camera angles or repeat a caption for every small move.
- Test forward, reverse, direct jumps, and interruptions. A path clear of a few proxy volumes is not guaranteed clear of every mesh.

## Make the hybrid composition readable

Use HTML/SVG for exact text and charts when they need crisp resizing, selection, keyboard access, and enlargement. Use real geometry for the spatial subject or meaningful symbolic scene.

- Read [implementation-recipes.md](references/implementation-recipes.md) before combining CSS3D and WebGL or fitting a sculpture inside a transparent panel opening.
- Fit panels from the destination camera and measured DOM dimensions after fonts load. Anchor them in world space for controlled parallax; re-fit on layout changes.
- CSS3D and WebGL do not share a depth buffer. Plan layer order and transparent openings deliberately; do not promise physical occlusion between DOM panels and meshes.
- Make the human/AI/tool roles recognizable in the geometry. Two generic people do not explain the difference between an AI companion and an AI instrument.
- Use opaque reading surfaces where contrast must remain stable. Reserve transparency for a composition that still reads over every tested background.
- Keep Hebrew reading direction RTL while isolating numbers, equations, and chart axes as appropriate. Do not mirror the entire WebGL coordinate system to implement RTL.

## Support interaction and alternative views

- Prefer DOM hit targets for HTML/SVG panels; add mesh raycasting only for interactions with actual meshes.
- Separate drag from click, and support keyboard opening, closing, and focus return.
- Enlarge from the original content, not a screenshot. Freeze scene motion while the reader inspects the enlarged panel.
- Provide a usable portrait/reading view and an error fallback when the WebGL scene cannot load. A comparable SVG can represent a symbolic sculpture in these views.
- Respect reduced motion and a manual freeze control. Stop elapsed-time accumulation while hidden or paused; navigation and resize must still redraw.
- Keep preview autoplay separate from speaker pacing. A short visual preview is not automatically the timed talk.

## Measure and package

- Inspect draw calls, triangles, memory, loading, and representative frame timing on the intended devices. Choose budgets from that evidence; do not adopt another project's numbers as targets.
- Instance repeated geometry; merge static shapes by material when independent transforms are no longer needed. Measure transparency and postprocessing cost, not just triangle count.
- Include active asset licenses and provenance. A generated reference image is art direction unless deliberately used as an asset; it is not evidence that the live scene matches the reference.
- Build from an explicit public manifest into an isolated output. Resolve static and dynamic dependencies and non-code assets; detect leftovers and missing files without altering protected originals.
- Version all changed runtime dependencies coherently. Retain the canonical public address and the existing repository when that is the requested destination.

## Completion evidence

Verify the actual browser experience: wide desktop, the application's compact panel size, portrait, enlargement, keyboard, reverse navigation, frozen motion, and relevant scene transitions. Check console/resource failures and the published canonical URL after deployment is authorized.

Report the change and the limits of the tested evidence. Do not turn a successful screenshot, a proxy collision check, or one renderer sample into a universal performance or accessibility claim.
