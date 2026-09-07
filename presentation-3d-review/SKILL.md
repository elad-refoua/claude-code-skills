---
name: presentation-3d-review
description: |
  Use when reviewing or delivering a slide-deck-to-3D website: factual traceability, audience clarity, motion and interaction, RTL layouts, performance evidence, and canonical-site deployment.
  TRIGGERS: "verify 3D presentation", "audit immersive journey", "publish presentation website", "בדיקת מסע תלת ממדי", "המספרים במצגת", "הקישור הראשי" in an immersive presentation project. Not a generic security audit or a replacement for reading research sources.
---

# Verify the journey as its audience experiences it

A passing build is evidence that code can be packaged. A readable, faithful presentation also requires source review and actual browser navigation. Scale the check to the change: a new journey needs a complete pass; a narrow correction needs impacted stops, surfaces, and publication verification.

## Identify the version that actually runs

Read the entrypoint and build order. Follow copy overrides through to the final composed data. A corrected panel can coexist with stale map titles, notes, captions, source drawers, and expanded views. Inspect all surfaces affected by a content change.

Record source deck/version, build identifier, canonical URL, asset identifier, and tested viewport. Check protected originals against the pre-work manifest if preservation was requested. Do not modify or silently recalculate research results to make a presentation consistent.

## Audit meaning and evidence

Use the source-linked stop/fact map from `presentation-3d-story`. Check every displayed number against its actual authorized source, including population, denominator, timeframe, unit, uncertainty, and publication status. A filename or a citation label is not verification.

- User percentages, message percentages, and conversation percentages are different measurements. Do not put them on an apparently common denominator.
- Odds ratios are not probability differences; units such as one point and one SD are not interchangeable. Preserve moderator conditions and the actual outcome.
- Self-reported help, clinical efficacy, theoretical pathways, and recommendations need different wording. Animation must not convert an association into a causal mechanism.
- A planned study, paper under review, and published finding have distinct statuses. Resolve names, dates, and credits from current sources or explicit corrections.
- Illustrative dialogue needs a visible fiction label, plausible turn-taking, a theme grounded in a permissible source, and no fabricated participant quotation or implied outcome.

For substantial research prose, use the available writer agent with its full applicable writing stack. Then use a fresh reader: provide only the displayed stop and ask what was measured, what was found, and what it means. Record actual misunderstandings and correct those.

## Optional structural validator

For a new journey, prepare a manifest using [manifest-contract.md](references/manifest-contract.md); [manifest-example.json](references/manifest-example.json) is a fictional structural example, not research evidence.

Run with a Python 3 interpreter available on the host:

```text
python scripts/validate_journey.py path/to/journey.json
python scripts/validate_journey.py path/to/journey.json --public-root path/to/public
```

The script checks declared coverage, references, timing, camera vectors, and named asset paths. It does not extract papers, verify scientific truth, prove that every public file is safe, or inspect the browser. Review the complete publication tree separately. `--draft` permits unresolved source records with warnings; it does not authorize their publication.

## Browser pass

Load the built package using the browser tools actually available. Prefer existing purpose-built browser tooling; do not assume another runtime's API. Use native clicks and keyboard navigation, not just direct state mutation.

| Area | Observe |
|---|---|
| Arrival | Correct stop, title, source card and panels; no lingering travel caption |
| Travel | Forward, reverse, distant map jump, and interruption; no subject clipping or meaningless return swing |
| Rest | No unwanted camera rocking; bounded user movement; local animation appropriate to the scene |
| Reading | Construct, finding, unit/denominator, and meaning readable at actual projected size |
| Interaction | Chart/slide enlargement, Escape, focus return, sources, map, keyboard controls |
| Motion controls | Pause, reduced motion, hidden-tab return, and modal close do not cause time jumps; navigation still works while paused |
| Content variants | Same current content in panels, map, short labels, caption, notes, sources, expanded and mobile views |
| Viewports | Presentation screen, actual compact app panel, and portrait; no blocked faces/headings or document overflow |
| RTL | Hebrew reading order, English paper titles, minus/plus signs, ranges, chart axes, next/back meaning |
| Fallback | WebGL unavailable or asset failed: readable content and clear loading/error state rather than indefinite spinner |
| Runtime | Browser console, failed network requests, local fonts/assets, and a full run through all stops for a new journey |

Use a small screenshot set with deliberate coverage. In the reference build, 1440×900, 655×578, and 390×844 revealed different issues; these are examples, not universal device sizes. Inspect the screenshots yourself rather than only saving them.

For camera geometry, sample finite endpoints and paths and test against relevant obstacle proxies. State that proxies are not exhaustive mesh collision detection. For performance, record browser/device, viewport, motion setting, and view. Draw calls, triangle counts, asset bytes, loading time, and frame timing measure different things. Do not turn one renderer counter into an FPS guarantee.

## Publish within the user's authorization

Preserve the existing repository, project identity, base path, and canonical address. Build an explicit runtime-only package: assets with licenses, compiled public content, fonts, and needed modules. Inspect for private notes, original decks, source manuscripts, raw data, credentials, QA artifacts, and `.git`; absence from a development server allowlist does not establish absence from a published folder.

Check a clean build or a complete audited manifest. A script that overwrites known files can leave old public files behind; do not describe it as a clean build without verifying that property. Respect file-preservation instructions when choosing a new dated output directory or a bounded cleanup approach.

When publishing is already authorized, finish the work and publish without another ceremonial confirmation. When authorization is absent, prepare the reviewable artifact first and ask only for the external action. Do not create repositories or change hosting providers incidentally.

After deployment, confirm the hosting service built the intended commit/version, then open the canonical URL without a special query parameter. Verify current asset/content identifiers and navigate to the changed stop. Internal asset hashes can invalidate caches while the user keeps one stable address. Do not solve cache problems only by giving the user a new `?v=` link.

## Completion evidence

Write a compact dated verification record: version, source checks, browser actions, inspected sizes, console/network findings, measured performance context, unresolved limitations, canonical URL. Report only checks actually performed. Keep detailed QA local unless the user asks to publish it. Finish with the main address and the concrete behavior delivered.
