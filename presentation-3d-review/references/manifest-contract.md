# Prepared journey manifest

This JSON contract describes the planned journey using deliberately prepared, approved aggregate or publication material. It is not a data extraction format. The validator reads only the specified manifest. It never opens a deck, follows a citation, searches a directory, reads an asset's contents, or accesses original participant data. With `--public-root`, it resolves only explicitly named paths and checks file existence.

The example is fictional topology: two conceptual stops, illustrative camera coordinates, and illustrative timing. It contains no scientific estimates, study findings, or participant records. Its `verified` labels demonstrate the accepted schema, not a claim that an external deck was reviewed.

## Fields

| Location | Required contract |
| --- | --- |
| `duration_seconds` | Positive finite JSON number for the complete planned duration. Booleans are not numbers. |
| `source_slides` | Nonempty list of unique positive integer slide numbers in the expected source order. This order need not be numerically ascending. |
| `preserve_order` | JSON boolean. If true, concatenating all stops' `source_slides`, then collapsing consecutive repeats, must equal the root `source_slides` exactly. This allows splitting a source slide across consecutive stops. |
| `facts` | List of fact objects. May be empty when no source claims are represented. |
| `facts[].id` | Nonempty string, unique across all facts and stops. |
| `facts[].source` | Nonempty source reference, such as a deck filename or publication reference. Stored as text; never opened by this tool. |
| `facts[].locator` | Nonempty slide, page, figure, table, or other precise source location. |
| `facts[].claim` | Nonempty statement already checked or awaiting checking against the source. |
| `facts[].status` | Exactly `verified` or `unresolved`. This is the preparer's declaration. The validator cannot verify its truth. |
| `facts[].estimate` | Optional finite JSON number. Every quantitative estimate must be explicitly represented here. |
| `facts[].unit`, `facts[].denominator` | Both required as nonempty strings when `estimate` is present. A descriptive denominator or model basis is valid; it need not be a count. When present without an estimate, each must still be nonempty text. |
| `stops` | Nonempty list of stop objects. |
| `stops[].id` | Nonempty string, unique across all facts and stops. |
| `stops[].source_slides` | Nonempty list of positive integers declared in the root list. Every root slide must appear in at least one stop. |
| `stops[].question`, `takeaway`, `focus`, `transition_reason` | Nonempty strings describing what the viewer should understand, attend to, and why the transition exists. A final stop may describe its hold or closure. |
| `stops[].evidence_type` | Exactly `descriptive`, `association`, `experiment`, `theory`, or `recommendation`. |
| `stops[].fact_ids` | List of references to declared fact IDs. An empty list is permitted for a stop without source claims. Every supplied reference must resolve. |
| `stops[].duration_seconds` | Positive finite number. The sum of stop durations must be within 1 second, inclusive, of the declared total. |
| `stops[].camera.position`, `camera.target` | Each an array of exactly three finite numbers, in the same world coordinate system. Position and target must differ. |
| `assets` | Optional list of asset objects. Only explicitly listed paths are checked; this is not an inventory of the public directory. |
| `assets[].path` | Nonempty relative file path, rooted at `--public-root` when supplied. Forward or backward separators are accepted. |
| `assets[].source`, `assets[].license` | Nonempty source and license descriptions. Their validity still requires human/source review. |

Paths may not be absolute, drive-relative, contain `..`, empty or `.` components, colons, NUL characters, or trailing spaces/dots in components. Components `.git`, `.env`, `private`, `qa`, and names beginning `.env.` are rejected case-insensitively. With `--public-root`, each path must resolve to a file inside that directory; symlinks and junctions cannot escape it or resolve into these sensitive components. The tool does not claim that other filenames or asset contents are public-safe.

Unknown metadata fields are ignored. Recognized fields remain strictly validated. Numeric estimates hidden only in prose cannot be detected reliably: the preparer must put each estimate in `estimate` and review its unit and denominator against the source. Different populations or statistical quantities must remain separate facts. A nonempty denominator string is not evidence that denominators are comparable.

## Export from the story template

The companion story YAML is the full authoring record; this JSON is a smaller structural projection made after the source review and scene implementation. Do not pass the YAML directly to the validator or rename its extension. Export deliberately from the fields below, using either the project's build code or a reviewed manual export:

| Story authoring record | Prepared JSON manifest |
| --- | --- |
| `intake.duration_minutes` | `duration_seconds`, multiplied by 60; include transition time in the complete talk budget |
| `intake.source_slide_order` | Root `source_slides`, in the requested source order |
| `intake.preserve_source_order` | `preserve_order` |
| `facts[].id` | `facts[].id` |
| `facts[].source_file_or_url`, `exact_source_location`, `allowed_claim` | `source`, `locator`, `claim` respectively |
| `facts[].verification_status` | `status`: map only a completed `verified` record to `verified`; map `unverified`, conflicts and open gaps to `unresolved` |
| `facts[].estimate`, `estimate_type_and_unit`, `denominator` | `estimate`, `unit`, `denominator`; never replace null with zero or silently omit an unresolved numeric claim to obtain a pass |
| `stops[].id`, `source_slides`, `fact_ids`, `evidence_type`, `duration_seconds`, `camera` | Same-named JSON fields after implementation |
| `stops[].audience_question`, `main_finding_or_idea`, `camera_focus`, `handoff_to_next_stop` | `question`, `takeaway`, `focus`, `transition_reason` respectively |
| Implemented asset inventory with verified licenses | `assets`; do not derive filenames from imagined models or concept images |

The authoring fields `presentation_mode`, dialogue and metaphors describe how an idea is shown. They do not change its evidence type. For example, a symbolic sculpture explaining a theoretical pathway still has `evidence_type: theory` and can have `presentation_mode: conceptual_illustration`. Do not assign an evidence type before reading its source.

Keep all additional authoring information in the source record or as extra JSON metadata: population, model adjustments, uncertainty, source versions, exact wording, fictional labels, and qualifications are needed for human review even though the structural validator does not check them. The two formats share IDs so reviewers can trace back. Camera vectors come from the actual scene. Missing required values remain unresolved work; never fill them merely to satisfy this tool.

## Run

From the skill directory, using an available Python 3 interpreter:

```text
py scripts/validate_journey.py references/manifest-example.json
py scripts/validate_journey.py path/to/prepared-manifest.json --draft
py scripts/validate_journey.py path/to/prepared-manifest.json --public-root path/to/prepared-public-directory
py -B -m unittest discover -s scripts -p test_validate_journey.py
```

On systems without the Windows `py` launcher, use the installed Python 3 executable. Codex may supply a bundled interpreter even when the system launcher has none.

Default mode blocks any `unresolved` fact. `--draft` converts only that condition into a warning; all structural failures still block. Do not treat draft success as publication readiness.

Exit code `0` means the declared structure passed the checks performed; `1` means validation errors; `2` means unreadable/invalid JSON or command-line usage errors. Diagnostic lines contain a severity, stable error code, field location, and specific explanation. Without `--public-root`, asset existence is explicitly reported as unchecked.

A passing result does **not** establish scientific ground truth, complete source extraction, exact wording preservation, statistical interpretation, audience comprehension, visual legibility, actual playback duration, license validity, absence of sensitive contents, or browser readiness. Those require the skill's source review, browser rehearsal, and publication checks.
