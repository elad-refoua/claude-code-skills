# Implementation recipes

Read the sections relevant to the implementation. The recipes generalize an existing Hebrew Three.js research presentation; numeric examples describe that project, not universal defaults.

## 1. Data and scene contracts

One practical content shape is:

```js
chapter = {
  id, title, purpose, labels, caption, notes,
  paper, sourceFactIds, sceneCue, activity, speakerSeconds
};
stop = { id, focusSubject, eye, focus, frame, via, activity };
scenePart = { group, setEnabled, update, getState, dispose };
```

Adapt existing contracts rather than adding empty fields. Preserve stable slide IDs when presentation order must follow a source deck. Build-time checks can verify required IDs, order, source references, and total speaker duration.

The source of a claim belongs in the content layer. Decorative floor paths, particles, a clock, or a sculpted face must not silently add quantities or claims. In the originating project, source identifiers remained attached to a stage after dense coefficients moved from the main panel into Sources.

A small diagnostic state surface makes actual navigation testable: current stage, destination, transition progress, active animation, motion state, and renderer counters. It should expose state, not create a privileged production control interface.

## 2. Camera routes and time

Author each destination around a physical subject and a purpose. Compute framing from viewport aspect and reserved reading space. A wide ensemble may need greater distance in a compact landscape panel; a close-up need not inherit that adjustment.

For a continuous path, a useful combination is:

```js
curve = new THREE.CatmullRomCurve3(points, false, 'centripetal');
duration = clamp(baseMs + curve.getLength() * msPerWorldUnit, minMs, maxMs);
e = p * p * p * (p * (p * 6 - 15) + 10); // smooth start/end
position = curve.getPointAt(e);           // distance-based sampling
target.lerpVectors(previousTarget, destinationTarget, e);
camera.position.copy(position);
camera.lookAt(target);
```

Reverse an adjacent route's authored intermediate points. An interrupted route should start at the actual current pose. A direct jump may use a deliberately elevated route, a cut, or another authored transition appropriate to the room; an elevated midpoint alone does not guarantee collision avoidance.

Keep input-driven motion separate from route state. At rest, apply bounded offsets in the camera's right/up basis, damp toward the input, and avoid automatic sine-wave camera rocking. Associate typing, gaze, or a prop's activity with relevant stages rather than repeating the same loop everywhere.

Use a single explicit motion state or clearly named booleans:

```text
running: advance animation and travel clocks
paused or document hidden: preserve pose and stop clock accumulation
reduced motion: show the destination immediately, preserve interactions
dirty: redraw after navigation, resize, visibility, or content changes
```

Reset the previous wall-clock timestamp on pause/resume and visibility changes. Cap the animation delta to avoid a huge pose jump; this is distinct from computing deliberate travel duration. Listen for preference changes if the product should track reduced-motion settings during an open session.

A render loop may keep scheduling callbacks while skipping expensive renders. Verify a settled paused scene's frame counter is stable and that navigation still updates it. Pausing during a transition needs its own check; a guard that skips only when no transition exists can still render frozen frames unnecessarily.

## 3. CSS3D and WebGL registration

The two renderers must agree on camera pose, projection, and viewport. Keep renderer containers in ordinary LTR coordinates; set each Hebrew content panel's direction separately.

For a camera-facing plane at distance `d`, the world units per CSS pixel are:

```js
u = 2 * d * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) / viewportHeight;
worldCentre = cameraPosition.clone().addScaledVector(forward, d)
  .addScaledVector(right, (pixelCentreX - viewportWidth / 2) * u)
  .addScaledVector(up, (viewportHeight / 2 - pixelCentreY) * u);
panelScale = u * fitRatio;
```

`fitRatio = min(availableWidth / naturalDOMWidth, availableHeight / naturalDOMHeight)`. Measure after fonts load, with the same final styles used in the panel. Account for headers, footer controls, paper cards, and actual wrapped height. Re-fit after a viewport or content change. Anchor at the destination pose rather than continually making every label follow the live camera.

The originating implementation enlarged the CSS coordinate system to reduce artifacts from very small transformed DOM elements:

```js
cssScene.scale.setScalar(k);
cssCamera.copy(webglCamera);
cssCamera.position.multiplyScalar(k);
cssCamera.near *= k;
cssCamera.far *= k;
cssCamera.updateProjectionMatrix();
cssCamera.updateMatrixWorld();
```

The same uniform factor must apply to CSS scene space and camera translation/clipping distances. Keep aspect and FOV equal. `k = 100` was a tested project choice, not an API requirement or a universal sharpness fix. Browser compositing, zoom, font rendering, and CSS specificity still require visual inspection.

## 4. Real geometry inside a panel opening

This is a deliberate two-layer composition, not a shared depth-buffer technique. The CSS panel has an unpainted opening; the WebGL sculpture is visible through it. Other parts of the DOM panel still cover the WebGL image.

Prepare each sculpture in a stable local frame. Bake any presentation tilt into a child group. Measure a `Box3` before applying dynamic placement; cache its local centre and size. Keep static symbolic objects distinct from actual plotted quantities.

```js
// Pseudocode: all directions come from the authored destination camera.
openingX = panelCentreX + (openingCentreLocalX - panelNaturalWidth / 2) * fitRatio;
openingY = panelCentreY + (openingCentreLocalY - panelNaturalHeight / 2) * fitRatio;
uNear = unitsPerPixelAtPanel * sculptureDistance / panelDistance;
scale = uNear * fitRatio * Math.min(
  openingWidth * horizontalMargin / boundsSize.x,
  openingHeight * verticalMargin / boundsSize.y
);
model.quaternion.copy(destinationCamera.quaternion);
model.scale.setScalar(scale);
model.position.copy(destinationCamera.position)
  .addScaledVector(forward, sculptureDistance)
  .addScaledVector(right, (openingX - viewportWidth / 2) * uNear)
  .addScaledVector(up, (viewportHeight / 2 - openingY) * uNear)
  .sub(boundsCentre.clone().multiplyScalar(scale).applyQuaternion(model.quaternion));
```

The project placed sculptures closer to the camera than the reading panels so room furniture would not obscure them. Its distances were 2.3 and 5.5 world units; neither was the camera's clipping near plane. Choose distances and margins for the actual scene. Depth variation and differing parallax mean a box fit is an approximation, especially during broad free orbit. Test the maximum permitted movement and actual projected silhouette.

Show the sculpture near arrival, with the matching content. Provide a semantically equivalent SVG for enlargement and portrait reading if the WebGL composition does not suit those surfaces. Keep those representations in sync: a person talking with AI and a person using an AI device communicate different roles, even if both illustrations contain two objects.

## 5. Picking, enlargement, RTL, and fallback

For HTML/SVG panels, use DOM event delegation, stable panel IDs, and normal keyboard semantics. No raycaster is necessary. For mesh interaction, add raycasting against the intended targets and account for overlay interception.

Separate a drag gesture from a click using a small movement threshold and suppress the click produced at release. The project used 6 CSS pixels and a 400 ms suppression window; adjust for touch and the product's interaction model.

Open a native dialog from source panel content. Keep panel-only and full-slide enlargement understandable, with Escape, a visible close control, focus containment, and focus return. Pause scene motion and preview autoplay while reading. Test focus with actual clicks and keyboard use rather than assuming dialog behavior proves the full flow.

Use `dir="rtl"` and right alignment for Hebrew prose, `bdi dir="ltr"` for equations/statistical tokens, and intentional axis direction in SVG or chart containers. Treat the DOM, SVG, and WebGL coordinate systems independently. Do not run numeric-token rewriting inside SVG geometry or already isolated text. An automated bidi helper covers only its recognized expressions, so inspect negative values, ranges, decimals, Latin abbreviations, and mixed titles.

Offer a portrait reading layout instead of shrinking the whole desktop composition. A loading failure should still expose content where feasible. Mobile, enlarged, and full reading views need their own overflow, contrast, and source-access checks.

## 6. Rendering and materials

- Instance repeated objects sharing geometry/material, such as architectural slats.
- Merge static detailed shapes by material after baking their local transforms. Normalize compatible geometry attributes/indexing first. Preserve separate groups when independent motion, picking, or visibility is needed.
- Merging reduces draw calls but may increase vertex memory; it does not reduce triangle count automatically. Transparent merged geometry can introduce ordering artifacts.
- Hide inactive stage illustrations. Dispose replaced stage geometry/materials when rebuilding them; shared resources need ownership-aware disposal.
- Measure the cost of pixel ratio, shadow maps, antialiasing, render targets, bloom, transparency, and texture bandwidth on the intended hardware.
- Start with restrained practical lighting and a few clear forms. Cheap contact-shadow planes can supplement a mapped key-light shadow when physically exact moving shadows are unnecessary.
- Interpret color maps as sRGB and normal/roughness maps as data. Tune roughness and normal intensity in both close and wide shots; a detailed scan can become visual noise behind evidence.
- Clamp values before fractional shader powers when their valid domain is bounded. In the project, clamping a Fresnel input removed observed white bloom artifacts. Review shader modifications again when changing Three.js versions; string replacements in `onBeforeCompile` depend on shader chunks.

Historical observations, not recommended budgets: an early finished room view reported 293 draw calls and 156,688 triangles; later two symbolic sculptures added 13 merged meshes containing 98,936 triangles. The counts come from different stages of development and are not a benchmark of the current full scene. No general frame-rate guarantee follows from them.

## 7. Assets, public builds, and caching

Keep a runtime asset manifest containing origin, license, retained notices, transformations, and file hashes where useful. Verify rights for the actual active model and textures; an old experiment's provenance file does not cover its replacement. Keep generated design references distinct from live assets and actual screenshots.

Use a public allowlist and a complete dependency manifest. Resolve:

1. Static JavaScript modules and the pinned Three.js add-ons they import.
2. Dynamic imports, workers, and runtime URL mappings where present.
3. Models, textures, fonts, data, and CSS-referenced assets.
4. Required licenses and notices.

A regex import walker can suit a small known module graph but is not a full bundler. The originating script reused a publication folder and previously staged WebP textures; it was not a demonstrated clean build from an empty directory. Do not copy that assumption into a reusable build. Generate into a fresh authorized output or compare existing contents against the intended manifest; identify unexpected leftovers without deleting protected originals.

Lossless image conversion is a claim to verify with decoded dimensions and pixels. A smaller file alone is not evidence of unchanged image data.

Derive a release hash from a deterministic, sorted manifest of all runtime paths and bytes, or use a bundler with content-hashed output. Include CSS, content, source metadata, and newly added modules. An explicit incomplete hash list can leave a changed file under an old URL. Ensure imports and the HTML entrypoint refer to the same release. Large unchanged assets may retain their hashes.

For a static site below a repository path, use a configured asset base or relative URLs that resolve correctly there; root-absolute `/assets/...` often points to the host root instead. Test the deployed base path, not just localhost `/`.

Retain the requested repository and canonical site address. Internal asset versions and a temporary verification query do not require a separate public deployment address. After authorized publication, verify the exact built revision, then load the canonical address and check current content and asset requests. A successful push is not a successful browser delivery.

## 8. Evidence and limits

The originating project's evidence lives in its `world.js`, `camera-tour.js`, `needs-scenes.js`, `room-finish.js`, `app.js`, `bidi.js`, `build_public.cjs`, `serve.cjs`, asset license/provenance files, and dated motion/interaction/needs/deployment reports from 7 September 2026. These recipes record those observed choices and their limits; the source files are not runtime dependencies of this skill.

Its camera audit covered 21 unique destinations, 420 ordered pairs, and 34,020 path samples against selected proxy volumes. This supports that tested route, not arbitrary future changes or exhaustive mesh collision safety. Browser reports covered desktop, a compact in-app panel, portrait, enlargement, and real navigation; they do not certify every browser/device or replace fresh review after a change.

For a new implementation, preserve the protected-source checks that the task needs, validate the complete output manifest, and inspect the actual participant-facing browser. Record enough state and screenshots to locate a failure without treating test instrumentation as evidence of visual clarity.
