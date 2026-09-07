# Art direction: reference to real-time scene

## Compact concept brief

Fill these from the deck and user preferences, rather than inventing a generic room:

| Decision | What to record |
|---|---|
| Subject | What or whom the audience follows, and why |
| Setting | A coherent environment or linked spaces that explain the argument |
| Roles | Who is present; who knows what; where perspectives differ |
| Composition | Where the subject, evidence, and negative space sit at wide and close views |
| Materials | A restrained physical palette and an intentional exception for a symbolic element |
| Light | Key light, environment light, contact grounding, and foreground separation |
| Type | Hebrew/Latin family, title/body hierarchy, projected legibility |
| Motion | What moves during travel, what moves at rest, what user movement permits |
| Evidence | One difficult chart proving that the proposed aesthetic supports reading |

Concept-image prompt pattern:

> Create an art-direction reference for an interactive 3D presentation about [subject]. The audience follows [argument]. Preserve [people/roles/positions from the supplied screenshot if editing]. Show [specific composition] in [setting], with [materials], [lighting], and [one intentional symbolic element]. Leave clear space for reading panels. Target a believable real-time web scene at [aspect ratio]. No embedded interface text or graphs. This is a design reference, not a screenshot of a finished website.

After viewing the image, list the implementable decisions: geometry, textures, model quality, lighting, framing. A photorealistic concept does not justify claiming an equally photorealistic running scene. Compare the actual browser at the same camera and size.

## Corrections that changed the outcome

| Observed failure | Effective correction | Transfer boundary |
|---|---|---|
| The "3D journey" is a slide gallery with an animated backdrop | Make the subject and conceptual relationships persist in a navigable space; assign a spatial purpose to each stop | Different decks may need a landscape, lab, machine, timeline, or several connected spaces |
| Every person-focused transition swings back to the same angle | Progress through relevant points of interest and perspectives; keep the closing composition distinct | Distinct coordinates alone do not guarantee meaningful movement |
| Translucent rectangular text panels blend with bright scene areas | Use opaque reading surfaces and inspect inherited/composited colors | Decorative glass can remain where no essential text depends on it |
| A row of unexplained coefficients is technically correct but unusable | Explain the measured construct and the main association; expose units and technical detail in Sources | Preserve qualifications that change the interpretation |
| Generic icons for "connection" and "agency" are ambiguous | Show human and AI roles: companion facing person; smaller device supporting person's chosen action | These are conceptual metaphors, not treatment outcomes |
| Generated characters look excellent, actual avatars look crude | Review actual models at the closest required camera before completing the world | Close shots demand more asset quality than distant symbolic scenes |
| Floating light dots or wire noise overwhelm the subject | Give the symbolic AI a coherent smooth silhouette, limited ribbons, and controlled glow | Another subject may have no AI figure or emissive object |
| White bloom artifacts obscure translucent geometry | Inspect the shader range and the facing-angle calculation; clamp mathematically invalid inputs | The original fix addressed a particular Fresnel implementation, not every transparency bug |
| A paper card covers a heading in a narrow app panel | Compact peripheral metadata and fit wide framing to aspect ratio | Recheck the exact viewport that exposed the issue |
| Enlarging a world sculpture yields an empty panel | Supply a faithful SVG illustration or a separately rendered modal scene | Do not pretend the CSS3D/WebGL canvases share DOM content |

## Finish hierarchy

1. Silhouette, scale, proportion, sightlines, and readable evidence.
2. Human pose, gaze, hands, and the orientation of screens toward their users.
3. Material grain, upholstery seams, joints, trim, and contact shadows.
4. Selective secondary animation and restrained post-processing.

Spending on level 4 while levels 1–2 are unresolved usually adds noise. A good still composition should remain understandable with all animation paused.

## Visual comparisons to inspect

Inspect a wide view and the closest view of each main subject. Include the densest chart, longest title, longest paper card, a negative/signed statistic, a comparison, an enlarged panel, portrait reading, and the closing credits. Compare paused and moving views. Keep artifact claims tied to these inspected screenshots, not to the reference image.
