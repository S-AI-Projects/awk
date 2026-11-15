#!/usr/bin/env python3

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DIR = ROOT / "exercises/practice/poker"
CONFIG_PATH = EXERCISE_DIR / ".meta/config.json"


class ConfigValidationError(Exception):
    pass


def validate_exercise_config(config_data, exercise_root):
    """
    Validates that files in config_data['files'] resolve inside exercise_root
    without parent traversal and that every declared file exists.
    """
    if "files" not in config_data:
        raise ConfigValidationError("Missing 'files' section in config")

    files_obj = config_data["files"]
    required_keys = ["solution", "test", "example"]

    resolved_files = {}

    for key in required_keys:
        if key not in files_obj or not files_obj[key]:
            raise ConfigValidationError(f"Missing or empty required file role '{key}'")

        declared_paths = files_obj[key]
        resolved_files[key] = []

        for rel_path in declared_paths:
            path_obj = Path(rel_path)

            # Reject parent traversal and absolute paths
            if path_obj.is_absolute():
                raise ConfigValidationError(
                    f"Absolute path '{rel_path}' for role '{key}' is not allowed"
                )

            # Check for parent traversal
            resolved = (exercise_root / path_obj).resolve()
            exercise_root_resolved = exercise_root.resolve()

            try:
                resolved.relative_to(exercise_root_resolved)
            except ValueError:
                raise ConfigValidationError(
                    f"Path '{rel_path}' escapes exercise root via parent traversal"
                )

            if ".." in path_obj.parts:
                raise ConfigValidationError(
                    f"Path '{rel_path}' contains parent traversal components ('..')"
                )

            if not resolved.is_file():
                raise ConfigValidationError(
                    f"Declared file '{rel_path}' for role '{key}' does not exist at {resolved}"
                )

            resolved_files[key].append(resolved)

    return resolved_files


def test_invalid_fixtures(real_config_data, exercise_root):
    """
    Tests three deliberately invalid metadata fixtures:
    1. Missing-reference
    2. Missing-test
    3. Outside-exercise path
    Asserts each fixture fails with the expected ConfigValidationError.
    """
    fixtures_tested = []

    # Fixture 1: Missing reference
    fixture1 = json.loads(json.dumps(real_config_data))
    fixture1["files"]["example"] = [".meta/nonexistent-example.awk"]
    try:
        validate_exercise_config(fixture1, exercise_root)
        raise SystemExit("FAIL: Fixture 1 (missing reference) unexpectedly passed")
    except ConfigValidationError as e:
        fixtures_tested.append(("missing-reference", str(e)))

    # Fixture 2: Missing test
    fixture2 = json.loads(json.dumps(real_config_data))
    fixture2["files"]["test"] = ["test-missing-poker.bats"]
    try:
        validate_exercise_config(fixture2, exercise_root)
        raise SystemExit("FAIL: Fixture 2 (missing test) unexpectedly passed")
    except ConfigValidationError as e:
        fixtures_tested.append(("missing-test", str(e)))

    # Fixture 3: Outside-exercise path (parent traversal)
    fixture3 = json.loads(json.dumps(real_config_data))
    fixture3["files"]["solution"] = ["../outside-solution.awk"]
    try:
        validate_exercise_config(fixture3, exercise_root)
        raise SystemExit("FAIL: Fixture 3 (outside-exercise path) unexpectedly passed")
    except ConfigValidationError as e:
        fixtures_tested.append(("outside-exercise", str(e)))

    return fixtures_tested


def main():
    if not CONFIG_PATH.is_file():
        raise SystemExit(f"FAIL: Missing config at {CONFIG_PATH}")

    real_config = json.loads(CONFIG_PATH.read_text())

    # Validate real configuration
    resolved = validate_exercise_config(real_config, EXERCISE_DIR)
    print(f"PASS: Real poker metadata valid. Resolved files:")
    for role, paths in resolved.items():
        print(f"  {role}: {[str(p.relative_to(EXERCISE_DIR)) for p in paths]}")

    # Validate the 3 invalid fixtures fail as intended
    invalid_results = test_invalid_fixtures(real_config, EXERCISE_DIR)
    for name, error_msg in invalid_results:
        print(f"PASS: Deliberate fixture '{name}' failed as expected: {error_msg}")


if __name__ == "__main__":
    main()
