#!/usr/bin/env python3
"""Validate a deliberately prepared publication manifest, never original data.

This checks declared structure and consistency, not scientific ground truth.
Only the manifest is read. Optional asset checks inspect named filesystem paths.
"""

import argparse
import json
import math
from pathlib import Path, PureWindowsPath
import sys


EVIDENCE_TYPES = {"descriptive", "association", "experiment", "theory", "recommendation"}
SENSITIVE_COMPONENTS = {".git", ".env", "private", "qa"}


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def safe_components(parts):
    return all(
        part not in {"", ".", ".."}
        and not part.endswith((" ", "."))
        and part.casefold() not in SENSITIVE_COMPONENTS
        and not part.casefold().startswith(".env.")
        for part in parts
    )


def validate(manifest, *, draft=False, public_root=None):
    """Return (errors, warnings), each as (code, location, explanation) tuples."""
    errors, warnings = [], []

    def error(code, location, explanation):
        errors.append((code, location, explanation))

    def required_text(obj, key, location):
        value = obj.get(key)
        if not isinstance(value, str) or not value.strip():
            error("REQUIRED_TEXT", f"{location}.{key}", "must be a nonempty string")
            return None
        return value

    def positive_duration(value, location):
        if not finite_number(value) or value <= 0:
            error("DURATION", location, "must be a positive finite number")
            return None
        return value

    def slide_list(value, location, unique=False):
        if (not isinstance(value, list) or not value
                or any(type(slide) is not int or slide <= 0 for slide in value)):
            error("SOURCE_SLIDES", location, "must be a nonempty list of positive integers")
            return []
        if unique and len(set(value)) != len(value):
            error("SOURCE_SLIDES", location, "must contain unique slide numbers")
        return value

    def object_list(value, location, nonempty=False):
        if not isinstance(value, list) or (nonempty and not value):
            error("LIST", location, "must be a list" + (" with at least one item" if nonempty else ""))
            return []
        valid = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                error("OBJECT", f"{location}[{index}]", "must be an object")
            else:
                valid.append((index, item))
        return valid

    if not isinstance(manifest, dict):
        error("MANIFEST", "$", "must be a JSON object")
        return errors, warnings

    total = positive_duration(manifest.get("duration_seconds"), "duration_seconds")
    slides = slide_list(manifest.get("source_slides"), "source_slides", unique=True)
    expected_slides = set(slides)
    preserve = manifest.get("preserve_order")
    if type(preserve) is not bool:
        error("PRESERVE_ORDER", "preserve_order", "must be a boolean")

    seen_ids, fact_ids = set(), set()

    def check_id(obj, location):
        identifier = required_text(obj, "id", location)
        if identifier is not None:
            if identifier in seen_ids:
                error("DUPLICATE_ID", f"{location}.id", "must be unique across facts and stops")
            seen_ids.add(identifier)
        return identifier

    for index, fact in object_list(manifest.get("facts"), "facts"):
        location = f"facts[{index}]"
        identifier = check_id(fact, location)
        if identifier is not None:
            fact_ids.add(identifier)
        for key in ("source", "locator", "claim"):
            required_text(fact, key, location)
        status = fact.get("status")
        if status not in ("verified", "unresolved"):
            error("FACT_STATUS", f"{location}.status", "must be verified or unresolved")
        elif status == "unresolved":
            issue = ("FACT_UNRESOLVED", f"{location}.status", "requires source resolution before publication")
            (warnings if draft else errors).append(issue)
        if "estimate" in fact:
            if not finite_number(fact["estimate"]):
                error("ESTIMATE", f"{location}.estimate", "must be a finite JSON number, not a boolean")
            for key in ("unit", "denominator"):
                if not isinstance(fact.get(key), str) or not fact[key].strip():
                    error("NUMERIC_CONTEXT", f"{location}.{key}", "is required for a numeric estimate")
        else:
            for key in ("unit", "denominator"):
                if key in fact:
                    required_text(fact, key, location)

    flattened, durations = [], []
    stop_items = object_list(manifest.get("stops"), "stops", nonempty=True)
    for index, stop in stop_items:
        location = f"stops[{index}]"
        check_id(stop, location)
        for key in ("question", "takeaway", "focus", "transition_reason"):
            required_text(stop, key, location)
        evidence = stop.get("evidence_type")
        if not isinstance(evidence, str) or evidence not in EVIDENCE_TYPES:
            error("EVIDENCE_TYPE", f"{location}.evidence_type", "must be one of " + ", ".join(sorted(EVIDENCE_TYPES)))
        stop_slides = slide_list(stop.get("source_slides"), f"{location}.source_slides")
        flattened.extend(stop_slides)
        if set(stop_slides) - expected_slides:
            error("UNKNOWN_SLIDE", f"{location}.source_slides", "includes slides absent from the declared source_slides")
        refs = stop.get("fact_ids")
        if not isinstance(refs, list):
            error("FACT_REFERENCES", f"{location}.fact_ids", "must be a list of fact IDs")
        else:
            for ref_index, ref in enumerate(refs):
                if not isinstance(ref, str) or ref not in fact_ids:
                    error("UNKNOWN_FACT", f"{location}.fact_ids[{ref_index}]", "does not resolve to a declared fact ID")
        duration = positive_duration(stop.get("duration_seconds"), f"{location}.duration_seconds")
        if duration is not None:
            durations.append(duration)
        camera = stop.get("camera")
        if not isinstance(camera, dict):
            error("CAMERA", f"{location}.camera", "must contain position and target vectors")
            continue
        valid_vectors = True
        for key in ("position", "target"):
            vector = camera.get(key)
            if (not isinstance(vector, list) or len(vector) != 3
                    or not all(finite_number(value) for value in vector)):
                valid_vectors = False
                error("CAMERA_VECTOR", f"{location}.camera.{key}", "must contain exactly three finite numbers")
        if valid_vectors and camera["position"] == camera["target"]:
            error("CAMERA_DIRECTION", f"{location}.camera", "position and target must differ")

    missing = expected_slides - set(flattened)
    if missing:
        error("SLIDE_COVERAGE", "stops", "does not cover source slide(s): " + ", ".join(map(str, sorted(missing))))
    compressed = []
    for slide in flattened:
        if not compressed or compressed[-1] != slide:
            compressed.append(slide)
    if preserve is True and compressed != slides:
        error("SLIDE_ORDER", "stops", "flattened slide order, with consecutive repetitions collapsed, must equal source_slides")
    if total is not None and len(durations) == len(stop_items):
        try:
            planned_total = math.fsum(durations)
        except OverflowError:
            planned_total = math.inf
        if abs(planned_total - total) > 1:
            error("DURATION_SUM", "stops", f"planned total {planned_total:g}s differs from {total:g}s by more than 1s")

    root = None
    if public_root is not None:
        try:
            root = Path(public_root).resolve(strict=True)
            if not root.is_dir():
                raise ValueError("not a directory")
        except (OSError, ValueError, RuntimeError):
            error("ASSET_ROOT", "--public-root", "must resolve to an existing directory")
            root = None
    for index, asset in object_list(manifest.get("assets", []), "assets"):
        location = f"assets[{index}]"
        for key in ("source", "license"):
            required_text(asset, key, location)
        raw_path = required_text(asset, "path", location)
        if raw_path is None:
            continue
        normalized = raw_path.replace("\\", "/")
        parts = normalized.split("/")
        if (PureWindowsPath(raw_path).drive or normalized.startswith("/")
                or ":" in raw_path or "\x00" in raw_path or not safe_components(parts)):
            error("ASSET_PATH", f"{location}.path", "must be a relative path without traversal or private/sensitive components")
            continue
        if root is not None:
            try:
                resolved = root.joinpath(*parts).resolve()
                relative = resolved.relative_to(root)
                if not safe_components(relative.parts):
                    raise ValueError("resolved sensitive path")
            except (OSError, ValueError, RuntimeError):
                error("ASSET_PATH", f"{location}.path", "must resolve inside the public root without sensitive components")
                continue
            if not resolved.is_file():
                error("ASSET_MISSING", f"{location}.path", "does not resolve to an existing file in the public root")
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="deliberately prepared aggregate/publication JSON manifest")
    parser.add_argument("--draft", action="store_true", help="warn about unresolved facts instead of blocking")
    parser.add_argument("--public-root", type=Path, help="check existence and containment of explicitly named assets")
    args = parser.parse_args(argv)
    try:
        with args.manifest.open(encoding="utf-8-sig") as handle:
            prepared = json.load(handle)
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print(f"ERROR [MANIFEST_READ] {args.manifest}: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(prepared, draft=args.draft, public_root=args.public_root)
    for severity, issues in (("WARNING", warnings), ("ERROR", errors)):
        for code, location, explanation in issues:
            print(f"{severity} [{code}] {location}: {explanation}", file=sys.stderr)
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s).", file=sys.stderr)
        return 1
    mode = "draft" if args.draft else "publication-manifest"
    print(f"PASS ({mode}): structural consistency only, not scientific ground-truth verification or publication approval.")
    if args.public_root is None:
        print("Asset existence was not checked; use --public-root for the prepared public directory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
