"""CLI contract tests. Fixtures contain fictional concepts, never research data."""

import copy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("validate_journey.py")


def manifest():
    return {
        "duration_seconds": 60,
        "source_slides": [1, 2],
        "preserve_order": True,
        "facts": [
            {"id": "concept-a", "source": "example-deck.pptx", "locator": "slide 1",
             "claim": "Fictional concept A.", "status": "verified"},
            {"id": "concept-b", "source": "example-deck.pptx", "locator": "slide 2",
             "claim": "Fictional concept B.", "status": "verified"},
        ],
        "stops": [
            {"id": "stop-a", "source_slides": [1], "question": "What is concept A?",
             "takeaway": "Introduce the fictional concept.", "evidence_type": "theory",
             "fact_ids": ["concept-a"], "duration_seconds": 30,
             "focus": "One solid object", "transition_reason": "Introduce the next concept.",
             "camera": {"position": [0, 0, 5], "target": [0, 0, 0]}},
            {"id": "stop-b", "source_slides": [2], "question": "How does concept B relate?",
             "takeaway": "Compare fictional conceptual arrangements.", "evidence_type": "theory",
             "fact_ids": ["concept-b"], "duration_seconds": 30,
             "focus": "Two solid objects", "transition_reason": "Close the conceptual example.",
             "camera": {"position": [5, 0, 5], "target": [5, 0, 0]}},
        ],
    }


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        # Keep fixture creation and cleanup inside the caller's working directory.
        self.temp = tempfile.TemporaryDirectory(
            prefix=f"journey-validator-tests-{date.today().isoformat()}-", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.public = self.root / "public"
        self.public.mkdir()

    def run_manifest(self, data, *options):
        path = self.root / "prepared-manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(path), *map(str, options)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def assert_rejected(self, data, code, *options):
        result = self.run_manifest(data, *options)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(code, result.stderr)

    def test_valid_conceptual_manifest(self):
        result = self.run_manifest(manifest())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)
        self.assertIn("not scientific", result.stdout)

    def test_unresolved_blocks_publication(self):
        data = manifest()
        data["facts"][0]["status"] = "unresolved"
        self.assert_rejected(data, "FACT_UNRESOLVED")

    def test_draft_allows_unresolved_with_warning(self):
        data = manifest()
        data["facts"][0]["status"] = "unresolved"
        result = self.run_manifest(data, "--draft")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING [FACT_UNRESOLVED]", result.stderr)
        self.assertIn("draft", result.stdout)

    def test_draft_does_not_allow_broken_reference(self):
        data = manifest()
        data["stops"][0]["fact_ids"] = ["missing"]
        self.assert_rejected(data, "UNKNOWN_FACT", "--draft")

    def test_missing_slide_coverage(self):
        data = manifest()
        data["stops"][1]["source_slides"] = [1]
        self.assert_rejected(data, "SLIDE_COVERAGE")

    def test_unlisted_slide_is_rejected(self):
        data = manifest()
        data["stops"][0]["source_slides"] = [1, 3]
        self.assert_rejected(data, "UNKNOWN_SLIDE")

    def test_duplicate_ids_are_rejected(self):
        for collection in ("facts", "stops"):
            with self.subTest(collection=collection):
                data = manifest()
                data[collection][1]["id"] = data[collection][0]["id"]
                self.assert_rejected(data, "DUPLICATE_ID")

    def test_root_source_slides_must_be_unique_positive_integers(self):
        for slides in ([1, 1], [1, 0], [True, 2], [1, 2.5], []):
            with self.subTest(slides=slides):
                data = manifest()
                data["source_slides"] = slides
                self.assert_rejected(data, "SOURCE_SLIDES")

    def test_duration_mismatch(self):
        data = manifest()
        data["stops"][0]["duration_seconds"] = 28
        self.assert_rejected(data, "DURATION_SUM")

    def test_duration_tolerance_is_one_second(self):
        data = manifest()
        data["stops"][0]["duration_seconds"] = 29
        result = self.run_manifest(data)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_durations_must_be_positive_finite_numbers(self):
        for value in (0, -1, True, float("inf"), "30"):
            with self.subTest(value=value):
                data = manifest()
                data["stops"][0]["duration_seconds"] = value
                self.assert_rejected(data, "DURATION")

    def test_nonfinite_camera_vector(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value):
                data = manifest()
                data["stops"][0]["camera"]["position"][0] = value
                self.assert_rejected(data, "CAMERA_VECTOR")

    def test_camera_position_cannot_equal_target(self):
        data = manifest()
        data["stops"][0]["camera"]["position"] = [0, 0, 0]
        self.assert_rejected(data, "CAMERA_DIRECTION")

    def test_reversed_order_is_rejected_when_preserved(self):
        data = manifest()
        data["stops"].reverse()
        self.assert_rejected(data, "SLIDE_ORDER")

    def test_reversed_order_can_be_explicitly_allowed(self):
        data = manifest()
        data["preserve_order"] = False
        data["stops"].reverse()
        result = self.run_manifest(data)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_split_slide_can_repeat_consecutively(self):
        data = manifest()
        split = copy.deepcopy(data["stops"][0])
        split["id"] = "stop-a-detail"
        split["duration_seconds"] = 15
        data["stops"][0]["duration_seconds"] = 15
        data["stops"].insert(1, split)
        result = self.run_manifest(data)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_slide_cannot_reappear_after_a_later_slide(self):
        data = manifest()
        data["stops"][1]["source_slides"] = [2, 1]
        self.assert_rejected(data, "SLIDE_ORDER")

    def test_empty_concept_field_is_rejected(self):
        for field in ("question", "takeaway", "focus", "transition_reason"):
            with self.subTest(field=field):
                data = manifest()
                data["stops"][0][field] = " "
                self.assert_rejected(data, "REQUIRED_TEXT")

    def test_evidence_type_is_controlled(self):
        data = manifest()
        data["stops"][0]["evidence_type"] = "proof"
        self.assert_rejected(data, "EVIDENCE_TYPE")

    def test_estimate_requires_unit_and_denominator(self):
        data = manifest()
        # This is a validator boundary fixture, not a scientific estimate.
        data["facts"][0]["estimate"] = 0
        self.assert_rejected(data, "NUMERIC_CONTEXT")
        data["facts"][0]["unit"] = "example units"
        data["facts"][0]["denominator"] = "fictional illustrative base"
        result = self.run_manifest(data)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_numeric_estimate_must_be_finite_and_not_boolean(self):
        for estimate in (True, float("nan"), "unparsed"):
            with self.subTest(estimate=estimate):
                data = manifest()
                data["facts"][0].update(
                    estimate=estimate, unit="example units", denominator="illustrative base")
                self.assert_rejected(data, "ESTIMATE")

    def test_named_asset_exists_with_source_and_license(self):
        (self.public / "shape.svg").touch()
        data = manifest()
        data["assets"] = [{"path": "shape.svg", "source": "self-created", "license": "CC0"}]
        result = self.run_manifest(data, "--public-root", self.public)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_asset(self):
        data = manifest()
        data["assets"] = [{"path": "missing.svg", "source": "self-created", "license": "CC0"}]
        self.assert_rejected(data, "ASSET_MISSING", "--public-root", self.public)

    def test_asset_paths_reject_traversal_absolute_and_sensitive_components(self):
        for path in ("../secret.svg", "assets/../../secret.svg", "..\\secret.svg",
                     "/absolute.svg", "C:\\private\\secret.svg", "C:secret.svg",
                     "//server/share.svg", "assets/.git/config", ".env", ".env.local",
                     "PRIVATE/asset.svg", "qa/screen.png", "private./asset.svg"):
            with self.subTest(path=path):
                data = manifest()
                data["assets"] = [{"path": path, "source": "example", "license": "CC0"}]
                self.assert_rejected(data, "ASSET_PATH", "--public-root", self.public)

    def test_asset_source_and_license_are_required(self):
        for field in ("source", "license"):
            with self.subTest(field=field):
                data = manifest()
                asset = {"path": "shape.svg", "source": "self-created", "license": "CC0"}
                del asset[field]
                data["assets"] = [asset]
                self.assert_rejected(data, "REQUIRED_TEXT")

    def test_resolved_symlink_cannot_escape_public_root(self):
        outside = self.root / "outside.svg"
        outside.touch()
        try:
            (self.public / "escape.svg").symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is unavailable on this host")
        data = manifest()
        data["assets"] = [{"path": "escape.svg", "source": "example", "license": "CC0"}]
        self.assert_rejected(data, "ASSET_PATH", "--public-root", self.public)

    def test_malformed_shape_reports_errors_without_traceback(self):
        for data in ([], {"facts": [None], "stops": [None]},
                     {**manifest(), "preserve_order": "true"}):
            with self.subTest(data=data):
                result = self.run_manifest(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERROR", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
