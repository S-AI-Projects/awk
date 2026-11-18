import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DIR = ROOT / "exercises/practice/knapsack"
CONFIG_FILE = EXERCISE_DIR / ".meta/config.json"
EVIDENCE_DIR = ROOT / "work/R06-T058/evidence"

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
            # Check for path traversal
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

def main():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.is_file():
        print(f"FAIL: {CONFIG_FILE} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        real_config = json.load(f)

    # 1. Real metadata must pass
    print("Validating real knapsack metadata...")
    try:
        resolved_files = validate_config(real_config, EXERCISE_DIR)
        print(f"Real config passed: {len(resolved_files)} declared files verified.")
    except Exception as e:
        print(f"FAIL: Real config validation failed unexpectedly: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Test Fixture 1: Missing Reference
    print("Testing fixture: missing-reference...")
    cfg_missing_ref = copy.deepcopy(real_config)
    cfg_missing_ref["files"]["example"] = [".meta/nonexistent_example.awk"]
    try:
        validate_config(cfg_missing_ref, EXERCISE_DIR)
        print("FAIL: missing-reference fixture did not fail.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"missing-reference failed as expected: {e}")

    # 3. Test Fixture 2: Missing Test
    print("Testing fixture: missing-test...")
    cfg_missing_test = copy.deepcopy(real_config)
    cfg_missing_test["files"]["test"] = ["nonexistent_test.bats"]
    try:
        validate_config(cfg_missing_test, EXERCISE_DIR)
        print("FAIL: missing-test fixture did not fail.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"missing-test failed as expected: {e}")

    # 4. Test Fixture 3: Outside Exercise (Path Traversal)
    print("Testing fixture: outside-exercise...")
    cfg_outside = copy.deepcopy(real_config)
    cfg_outside["files"]["example"] = ["../outside_reference.awk"]
    try:
        validate_config(cfg_outside, EXERCISE_DIR)
        print("FAIL: outside-exercise fixture did not fail.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"outside-exercise failed as expected: {e}")

    # Save evidence report
    evidence_text = (
        "=== CONFIGURATION AND FIXTURE AUDIT ===\n"
        "Real Config Status: PASS\n"
        f"Verified Files: {resolved_files}\n\n"
        "Fixture 1 (missing-reference): FAILED AS EXPECTED (FileNotFoundError)\n"
        "Fixture 2 (missing-test):      FAILED AS EXPECTED (FileNotFoundError)\n"
        "Fixture 3 (outside-exercise):  FAILED AS EXPECTED (ValueError - Traversal)\n"
    )
    (EVIDENCE_DIR / "fixture-results.txt").write_text(evidence_text, encoding="utf-8")
    print("All metadata fixtures and real configuration verified successfully.")

if __name__ == "__main__":
    main()
