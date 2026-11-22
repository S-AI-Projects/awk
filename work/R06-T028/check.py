#!/usr/bin/env python3
"""
R06-T028 check.py
=================
Validates metadata resolution and test execution for the say exercise:

  1. Parses the `files` object from exercises/practice/say/.meta/config.json.
  2. Resolves each declared path, strictly rejecting parent traversal ('..')
     or paths escaping the exercise directory, and verifies each file exists.
  3. Tests three deliberately invalid metadata fixtures:
     - Fixture 1: Missing reference file (expected FileNotFoundError)
     - Fixture 2: Missing test file (expected FileNotFoundError)
     - Fixture 3: Parent traversal / outside exercise path (expected ValueError)
     Asserts that real metadata passes and all 3 fixtures fail for the intended reasons.
  4. Copies exercise including dotfiles to a tempdir, substitutes reference,
     and validates tests.
  5. Executes: bin/validate_one_exercise exercises/practice/say.
  6. Verifies learner stub remains unsolved (exits 1).
  7. Asserts the named cases:
     - "zero" (0 -> "zero")
     - "one" (1 -> "one")
     - "fourteen" (14 -> "fourteen")
  8. Records all data in work/R06-T028/run_record.json.

Exit codes:
  0  all assertions pass
  1  one or more assertions failed
  2  setup / invocation error
"""

import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure Homebrew tools are on PATH
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "say"
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = Path(__file__).resolve().parent

EXPECTED_TEST_COUNT = 19

NAMED_CASES = [
    {"name": "zero", "input": "0\n", "expected": "zero", "expected_rc": 0},
    {"name": "one", "input": "1\n", "expected": "one", "expected_rc": 0},
    {"name": "fourteen", "input": "14\n", "expected": "fourteen", "expected_rc": 0},
]


def die(msg: str, code: int = 2) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def run_cmd(cmd, input_text=None, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_text,
        **kwargs,
    )


def tool_version(cmd: list) -> str:
    r = run_cmd(cmd)
    out = (r.stdout + r.stderr).strip()
    return out.splitlines()[0] if out else "(unavailable)"


def count_bats_tests(bats_path: Path) -> int:
    text = bats_path.read_text()
    return len(re.findall(r"^@test\s+", text, re.MULTILINE))


def count_bats_output_tests(output: str) -> int:
    m = re.search(r"^1\.\.(\d+)", output, re.MULTILINE)
    if m:
        return int(m.group(1))
    return len(re.findall(r"^(?:ok|not ok)\s+\d+", output, re.MULTILINE))


def validate_exercise_files(config_data: dict, exercise_root: Path) -> dict:
    """
    Parses the `files` object from config.json.
    Resolves each path strictly within exercise_root.
    Rejects parent traversal ('..') or paths escaping exercise_root.
    Checks that every declared file exists.
    """
    if "files" not in config_data or not isinstance(config_data["files"], dict):
        raise ValueError("Missing or invalid 'files' object in config")

    resolved_files = {}
    exercise_root_resolved = exercise_root.resolve()

    for category, file_list in config_data["files"].items():
        if not isinstance(file_list, list):
            continue
        resolved_files[category] = []
        for rel_path_str in file_list:
            # 1. Reject explicit parent directory traversal or absolute paths
            if ".." in Path(rel_path_str).parts:
                raise ValueError(f"Parent traversal detected in declared path: {rel_path_str!r}")
            if Path(rel_path_str).is_absolute():
                raise ValueError(f"Absolute path not allowed in declared path: {rel_path_str!r}")

            # 2. Resolve relative to exercise root
            target_path = (exercise_root / rel_path_str).resolve()

            # 3. Ensure the resolved path remains strictly within exercise root
            try:
                target_path.relative_to(exercise_root_resolved)
            except ValueError:
                raise ValueError(f"Path escapes exercise directory: {rel_path_str!r} -> {target_path}")

            # 4. Check that the declared file exists
            if not target_path.is_file():
                raise FileNotFoundError(f"Declared file does not exist: {rel_path_str!r} (resolved: {target_path})")

            resolved_files[category].append(str(target_path))

    return resolved_files


def main() -> None:
    print("=" * 60)
    print("R06-T028 say metadata & runner resolution check")
    print("=" * 60)

    # 1. Verify and read config.json
    if not CONFIG_JSON.is_file():
        die(f"config.json not found: {CONFIG_JSON}")
    raw_config = CONFIG_JSON.read_text()
    config_data = json.loads(raw_config)

    # 2. Collect tool versions
    gawk_ver = tool_version(["gawk", "--version"])
    bats_ver = tool_version(["bats", "--version"])
    jq_ver = tool_version(["jq", "--version"])
    py_ver = tool_version([sys.executable, "--version"])
    print("\n[versions]")
    print(f"  gawk   : {gawk_ver}")
    print(f"  bats   : {bats_ver}")
    print(f"  jq     : {jq_ver}")
    print(f"  python : {py_ver}")

    # 3. Test real metadata
    print("\n[metadata validation]")
    try:
        resolved_real = validate_exercise_files(config_data, EXERCISE_DIR)
        real_meta_pass = True
        print("  Real config.json validation: PASS")
    except Exception as e:
        real_meta_pass = False
        print(f"  Real config.json validation: FAIL ({e})")

    # 4. Test Deliberately Invalid Metadata Fixtures
    print("\n[invalid metadata fixtures test]")

    # Fixture 1: Missing reference
    cfg_missing_ref = copy.deepcopy(config_data)
    cfg_missing_ref["files"]["example"] = [".meta/nonexistent-example.awk"]
    fixture_missing_ref_ok = False
    try:
        validate_exercise_files(cfg_missing_ref, EXERCISE_DIR)
    except FileNotFoundError as e:
        if "nonexistent-example.awk" in str(e):
            fixture_missing_ref_ok = True
            print(f"  Fixture 1 (missing reference): PASS (caught expected FileNotFoundError: {e})")
    except Exception as e:
        print(f"  Fixture 1 (missing reference): FAIL (unexpected exception: {e})")

    # Fixture 2: Missing test
    cfg_missing_test = copy.deepcopy(config_data)
    cfg_missing_test["files"]["test"] = ["nonexistent-test.bats"]
    fixture_missing_test_ok = False
    try:
        validate_exercise_files(cfg_missing_test, EXERCISE_DIR)
    except FileNotFoundError as e:
        if "nonexistent-test.bats" in str(e):
            fixture_missing_test_ok = True
            print(f"  Fixture 2 (missing test): PASS (caught expected FileNotFoundError: {e})")
    except Exception as e:
        print(f"  Fixture 2 (missing test): FAIL (unexpected exception: {e})")

    # Fixture 3: Parent traversal / outside exercise path
    cfg_traversal = copy.deepcopy(config_data)
    cfg_traversal["files"]["example"] = ["../outside-exercise.awk"]
    fixture_traversal_ok = False
    try:
        validate_exercise_files(cfg_traversal, EXERCISE_DIR)
    except ValueError as e:
        if "Parent traversal detected" in str(e) or "escapes" in str(e):
            fixture_traversal_ok = True
            print(f"  Fixture 3 (parent traversal): PASS (caught expected ValueError: {e})")
    except Exception as e:
        print(f"  Fixture 3 (parent traversal): FAIL (unexpected exception: {e})")

    # 5. Check learner stub is unsolved
    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = (config_data["files"].get("example") or config_data["files"].get("exemplar"))[0]

    solution_src = EXERCISE_DIR / solution_rel
    test_src = EXERCISE_DIR / test_rel
    example_src = EXERCISE_DIR / example_rel

    stub_run = run_cmd(["gawk", "-f", str(solution_src)], input_text="0\n")
    stub_unsolved = stub_run.returncode != 0 and "Implement this solution" in (stub_run.stderr + stub_run.stdout)
    print(f"\n[stub] unsolved and fails with expected message: {stub_unsolved}")

    # 6. Copy exercise to temporary directory and run tests there
    with tempfile.TemporaryDirectory() as td:
        temp_exercise = Path(td) / "say"
        shutil.copytree(EXERCISE_DIR, temp_exercise)
        shutil.copy2(temp_exercise / example_rel, temp_exercise / solution_rel)

        temp_bats = run_cmd(
            ["bats", test_rel],
            cwd=str(temp_exercise),
            env=dict(os.environ, BATS_RUN_SKIPPED="true"),
        )
        temp_bats_tests = count_bats_output_tests(temp_bats.stdout)
        temp_bats_ok = temp_bats.returncode == 0

    # 7. Run bin/validate_one_exercise
    validate_script = REPO_ROOT / "bin" / "validate_one_exercise"
    if not validate_script.is_file():
        die(f"validate_one_exercise not found: {validate_script}")

    print(f"\n[run] bin/validate_one_exercise exercises/practice/say")
    val_run = run_cmd([str(validate_script), str(EXERCISE_DIR)], cwd=str(REPO_ROOT))
    child_rc = val_run.returncode
    tests_run_count = count_bats_output_tests(val_run.stdout)

    # 8. Verify named cases explicitly on reference
    named_cases_verification = {}
    for nc in NAMED_CASES:
        r = run_cmd(["gawk", "-f", str(example_src)], input_text=nc["input"])
        actual = r.stdout.strip()
        passed = (r.returncode == nc["expected_rc"] and actual == nc["expected"])
        named_cases_verification[nc["name"]] = {
            "input": nc["input"].strip(),
            "expected": nc["expected"],
            "actual": actual,
            "pass": passed,
        }
        print(f"  [named case: reference] {nc['name']}: {'PASS' if passed else 'FAIL'}")

    # 9. Record everything
    record = {
        "tool_versions": {"gawk": gawk_ver, "bats": bats_ver, "jq": jq_ver, "python": py_ver},
        "enabled_cases": {"expected": EXPECTED_TEST_COUNT, "counted_in_bats": count_bats_tests(test_src)},
        "metadata_validation": {
            "real_config_passed": real_meta_pass,
            "resolved_files": resolved_real if real_meta_pass else None,
            "fixtures": {
                "missing_reference": {"passed_expectedly": fixture_missing_ref_ok},
                "missing_test": {"passed_expectedly": fixture_missing_test_ok},
                "parent_traversal": {"passed_expectedly": fixture_traversal_ok},
            },
        },
        "validate_run": {
            "returncode": child_rc,
            "tests_counted": tests_run_count,
            "stdout": val_run.stdout,
            "stderr": val_run.stderr,
        },
        "temporary_copy_test": {
            "returncode": temp_bats.returncode,
            "tests_counted": temp_bats_tests,
            "pass": temp_bats_ok,
        },
        "learner_stub_unsolved": stub_unsolved,
        "named_cases_reference": named_cases_verification,
        "assertions": {},
    }

    # 10. Assertions
    failures = []

    def assert_eq(name: str, expected, actual) -> None:
        ok = expected == actual
        record["assertions"][name] = {"expected": expected, "actual": actual, "pass": ok}
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}: expected={expected!r}, actual={actual!r}")
        if not ok:
            failures.append(name)

    print("\n[assertions — reference validation]")
    assert_eq("child_returncode_is_zero", 0, child_rc)
    assert_eq("bats_test_count", EXPECTED_TEST_COUNT, count_bats_tests(test_src))
    assert_eq("tests_run_nonzero", True, tests_run_count > 0)
    assert_eq("tests_run_count", EXPECTED_TEST_COUNT, tests_run_count)
    assert_eq("temp_copy_tests_passed", True, temp_bats_ok)
    assert_eq("learner_stub_unsolved", True, stub_unsolved)

    print("\n[assertions — named cases on reference]")
    for name, data in named_cases_verification.items():
        assert_eq(f"ref_named_case: {name}", True, data["pass"])

    print("\n[assertions — metadata resolution & fixture tests]")
    assert_eq("real_metadata_passed", True, real_meta_pass)
    assert_eq("fixture_missing_reference_failed_expectedly", True, fixture_missing_ref_ok)
    assert_eq("fixture_missing_test_failed_expectedly", True, fixture_missing_test_ok)
    assert_eq("fixture_parent_traversal_failed_expectedly", True, fixture_traversal_ok)

    # 11. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 12. Summary
    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
