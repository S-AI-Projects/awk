#!/usr/bin/env python3
"""
Configuration and Path Security Checker for Task R06-T018 (diamond exercise).
Validates declared files in exercises/practice/diamond/.meta/config.json,
enforces path traversal prevention, and verifies that deliberately invalid fixtures fail.
"""

import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DIR = ROOT / "exercises/practice/diamond"
CONFIG_FILE = EXERCISE_DIR / ".meta/config.json"
EVIDENCE_DIR = ROOT / "work/R06-T018/evidence"


def validate_config(config_data, base_dir):
    """
    Validates that all paths declared under 'files' exist and do not traverse
    outside the exercise directory.
    """
    files_obj = config_data.get("files", {})
    checked_files = []

    for role in ["solution", "test", "example"]:
        declared_list = files_obj.get(role, [])
        if not declared_list:
            raise ValueError(f"Required role '{role}' has no declared files.")

        for rel_path in declared_list:
            # Check for path traversal or absolute paths
            if ".." in Path(rel_path).parts or os.path.isabs(rel_path):
                raise ValueError(f"Path traversal detected in role '{role}': '{rel_path}'")

            full_path = (base_dir / rel_path).resolve()
            try:
                full_path.relative_to(base_dir.resolve())
            except ValueError:
                raise ValueError(f"Declared path escapes exercise directory: '{rel_path}'")

            if not full_path.is_file():
                raise FileNotFoundError(f"Declared file does not exist for role '{role}': '{rel_path}'")

            checked_files.append((role, rel_path))

    return checked_files


def run_metadata_audit():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(f"{CONFIG_FILE} does not exist.")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        real_config = json.load(f)

    # 1. Real metadata validation
    resolved_files = validate_config(real_config, EXERCISE_DIR)

    # 2. Test Fixture 1: Missing Reference
    fixture_missing_ref = copy.deepcopy(real_config)
    fixture_missing_ref["files"]["example"] = [".meta/non_existent_example.awk"]
    f1_passed = False
    try:
        validate_config(fixture_missing_ref, EXERCISE_DIR)
    except FileNotFoundError:
        f1_passed = True

    if not f1_passed:
        raise AssertionError("Fixture 1 (missing-reference) did not fail as expected!")

    # 3. Test Fixture 2: Missing Test
    fixture_missing_test = copy.deepcopy(real_config)
    fixture_missing_test["files"]["test"] = ["non_existent_test.bats"]
    f2_passed = False
    try:
        validate_config(fixture_missing_test, EXERCISE_DIR)
    except FileNotFoundError:
        f2_passed = True

    if not f2_passed:
        raise AssertionError("Fixture 2 (missing-test) did not fail as expected!")

    # 4. Test Fixture 3: Outside Exercise Traversal
    fixture_outside = copy.deepcopy(real_config)
    fixture_outside["files"]["solution"] = ["../outside_solution.awk"]
    f3_passed = False
    try:
        validate_config(fixture_outside, EXERCISE_DIR)
    except ValueError:
        f3_passed = True

    if not f3_passed:
        raise AssertionError("Fixture 3 (outside-exercise) did not fail as expected!")

    fixture_log = (
        "=== CONFIGURATION AND FIXTURE AUDIT ===\n"
        "Real Config Status: PASS\n"
        f"Verified Files: {resolved_files}\n\n"
        "Fixture 1 (missing-reference): FAILED AS EXPECTED (FileNotFoundError)\n"
        "Fixture 2 (missing-test):      FAILED AS EXPECTED (FileNotFoundError)\n"
        "Fixture 3 (outside-exercise):  FAILED AS EXPECTED (ValueError - Traversal)\n"
    )

    with open(EVIDENCE_DIR / "fixture-results.txt", "w", encoding="utf-8") as f:
        f.write(fixture_log)

    return resolved_files


def main():
    try:
        files = run_metadata_audit()
        print(f"Metadata audit passed cleanly: {len(files)} files verified, all 3 invalid fixtures failed as expected.")
        sys.exit(0)
    except Exception as e:
        print(f"Metadata audit FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
