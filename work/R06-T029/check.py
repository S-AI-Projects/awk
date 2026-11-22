#!/usr/bin/env python3
"""
R06-T029 check.py
=================
Focused runner and validation checker for robot-simulator:

  1. Resolves paths from exercises/practice/robot-simulator/.meta/config.json.
  2. Protects learner files: computes SHA-256 hashes of learner files before/after
     every run, guaranteeing working tree immutability.
  3. Runs tests in an isolated temporary copy substituting the reference.
  4. Tests three operational runner scenarios:
     a) Real reference: succeeds with code 0 and reports 21 executed cases.
     b) Deliberately failing reference: fails with non-zero exit and propagates failure.
     c) Zero-test run: fails with non-zero status upon detecting 0 executed tests.
  5. Executes bin/validate_one_exercise exercises/practice/robot-simulator.
  6. Asserts named cases:
     - "Robots are created with a position and direction"
     - "Robots are created with a default position and direction"
     - "Negative positions are allowed"
  7. Ensures all temporary directories are cleaned up.
  8. Records all results in work/R06-T029/run_record.json.

Exit codes:
  0  all assertions pass
  1  one or more assertions failed
  2  setup / invocation error
"""

import hashlib
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
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "robot-simulator"
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = Path(__file__).resolve().parent

EXPECTED_TEST_COUNT = 21

NAMED_CASES = [
    {"name": "Robots are created with a position and direction", "input_args": ["-v", "x=0", "-v", "y=0", "-v", "dir=north", "/dev/null"], "expected": "0 0 north"},
    {"name": "Robots are created with a default position and direction", "input_args": ["/dev/null"], "expected": "0 0 north"},
    {"name": "Negative positions are allowed", "input_args": ["-v", "x=-1", "-v", "y=-1", "-v", "dir=south", "/dev/null"], "expected": "-1 -1 south"},
]

# Deliberately broken reference implementation for failure testing
FAILING_AWK = """\
BEGIN {
    print "deliberate test failure: broken direction" > "/dev/stderr"
    exit 1
}
"""

# Empty BATS file for zero-test testing
EMPTY_BATS = """#!/usr/bin/env bats
load bats-extra
# No @test cases declared
"""


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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_isolated_test(
    exercise_dir: Path,
    solution_rel: str,
    test_rel: str,
    example_rel: str,
    reference_content: str = None,
    empty_tests: bool = False,
) -> dict:
    """
    Executes a test run in an isolated temporary directory.
    Substitutes the reference into the temporary copy only.
    Returns returncode, test count, stdout, stderr, and whether temp files were cleaned.
    """
    temp_dir_path = None
    with tempfile.TemporaryDirectory() as td:
        temp_dir_path = Path(td)
        temp_ex = temp_dir_path / "exercise"
        shutil.copytree(exercise_dir, temp_ex)

        dest_solution = temp_ex / solution_rel
        dest_test = temp_ex / test_rel

        # Substitute reference or custom content
        if reference_content is not None:
            dest_solution.write_text(reference_content)
        else:
            shutil.copy2(temp_ex / example_rel, dest_solution)

        # Substitute empty test file if requested
        if empty_tests:
            dest_test.write_text(EMPTY_BATS)

        # Run bats in temporary copy
        r = run_cmd(
            ["bats", test_rel],
            cwd=str(temp_ex),
            env=dict(os.environ, BATS_RUN_SKIPPED="true"),
        )
        test_count = count_bats_output_tests(r.stdout)

        # Runner failure logic: non-zero exit OR zero tests run is a failure
        runner_exit_code = r.returncode
        if test_count == 0 and runner_exit_code == 0:
            runner_exit_code = 1  # Propagate zero-test failure

        result = {
            "exit_code": runner_exit_code,
            "bats_returncode": r.returncode,
            "test_count": test_count,
            "stdout": r.stdout,
            "stderr": r.stderr,
        }

    # Verify temp directory was cleaned up
    result["temp_cleaned"] = not temp_dir_path.exists()
    return result


def main() -> None:
    print("=" * 60)
    print("R06-T029 robot-simulator focused runner check")
    print("=" * 60)

    # 1. Resolve configuration
    if not CONFIG_JSON.is_file():
        die(f"config.json not found: {CONFIG_JSON}")
    config = json.loads(CONFIG_JSON.read_text())
    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = (config["files"].get("example") or config["files"].get("exemplar"))[0]

    solution_src = EXERCISE_DIR / solution_rel
    test_src = EXERCISE_DIR / test_rel
    example_src = EXERCISE_DIR / example_rel

    for p in (solution_src, test_src, example_src):
        if not p.is_file():
            die(f"Required file missing: {p}")

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

    # 3. Check learner stub is unsolved
    stub_run = run_cmd(["gawk", "-f", str(solution_src), "/dev/null"])
    stub_unsolved = stub_run.returncode != 0 and "Implement this solution" in (stub_run.stderr + stub_run.stdout)
    print(f"\n[stub] unsolved and fails with expected message: {stub_unsolved}")

    # 4. Hash learner files before testing
    learner_hash_initial = file_sha256(solution_src)
    print(f"[hash] Initial learner file SHA-256: {learner_hash_initial[:16]}...")

    # 5. Test 1: Real Reference in isolated temp copy
    print("\n[scenario 1] Real reference run...")
    hash_pre_1 = file_sha256(solution_src)
    real_run = run_isolated_test(EXERCISE_DIR, solution_rel, test_rel, example_rel)
    hash_post_1 = file_sha256(solution_src)
    real_hash_match = (hash_pre_1 == hash_post_1 == learner_hash_initial)
    real_pass = (real_run["exit_code"] == 0 and real_run["test_count"] == EXPECTED_TEST_COUNT)
    print(f"  Exit code: {real_run['exit_code']} (expected 0)")
    print(f"  Test count: {real_run['test_count']} (expected {EXPECTED_TEST_COUNT})")
    print(f"  Temp cleaned: {real_run['temp_cleaned']}")
    print(f"  Learner file hash preserved: {real_hash_match}")

    # 6. Test 2: Deliberately Failing Reference
    print("\n[scenario 2] Deliberately failing reference run...")
    hash_pre_2 = file_sha256(solution_src)
    failing_run = run_isolated_test(
        EXERCISE_DIR, solution_rel, test_rel, example_rel,
        reference_content=FAILING_AWK
    )
    hash_post_2 = file_sha256(solution_src)
    failing_hash_match = (hash_pre_2 == hash_post_2 == learner_hash_initial)
    failing_pass = (failing_run["exit_code"] != 0 and failing_run["temp_cleaned"])
    print(f"  Exit code: {failing_run['exit_code']} (expected non-zero)")
    print(f"  Failure correctly propagated: {failing_pass}")
    print(f"  Temp cleaned: {failing_run['temp_cleaned']}")
    print(f"  Learner file hash preserved: {failing_hash_match}")

    # 7. Test 3: Empty Test Selection (Zero-test run)
    print("\n[scenario 3] Empty test selection (zero-test) run...")
    hash_pre_3 = file_sha256(solution_src)
    zero_run = run_isolated_test(
        EXERCISE_DIR, solution_rel, test_rel, example_rel,
        empty_tests=True
    )
    hash_post_3 = file_sha256(solution_src)
    zero_hash_match = (hash_pre_3 == hash_post_3 == learner_hash_initial)
    zero_pass = (zero_run["test_count"] == 0 and zero_run["exit_code"] != 0 and zero_run["temp_cleaned"])
    print(f"  Test count: {zero_run['test_count']} (expected 0)")
    print(f"  Exit code: {zero_run['exit_code']} (expected non-zero)")
    print(f"  Zero-test correctly failed: {zero_pass}")
    print(f"  Temp cleaned: {zero_run['temp_cleaned']}")
    print(f"  Learner file hash preserved: {zero_hash_match}")

    # 8. Run bin/validate_one_exercise from repository root
    print("\n[run] bin/validate_one_exercise exercises/practice/robot-simulator")
    hash_pre_val = file_sha256(solution_src)
    validate_script = REPO_ROOT / "bin" / "validate_one_exercise"
    if not validate_script.is_file():
        die(f"validate_one_exercise not found: {validate_script}")
    val_run = run_cmd([str(validate_script), str(EXERCISE_DIR)], cwd=str(REPO_ROOT))
    hash_post_val = file_sha256(solution_src)
    val_hash_match = (hash_pre_val == hash_post_val == learner_hash_initial)
    child_rc = val_run.returncode
    val_tests_count = count_bats_output_tests(val_run.stdout)
    print(f"  validate_one_exercise exit code: {child_rc}")
    print(f"  Tests counted: {val_tests_count}")
    print(f"  Learner file hash preserved: {val_hash_match}")

    # 9. Verify named cases explicitly on reference
    named_cases_verification = {}
    for nc in NAMED_CASES:
        cmd = ["gawk", "-f", str(example_src)] + nc["input_args"]
        r = run_cmd(cmd)
        actual = r.stdout.strip()
        passed = (r.returncode == 0 and actual == nc["expected"])
        named_cases_verification[nc["name"]] = {
            "args": nc["input_args"],
            "expected": nc["expected"],
            "actual": actual,
            "pass": passed,
        }
        print(f"  [named case: reference] {nc['name']}: {'PASS' if passed else 'FAIL'}")

    # Final hash check
    learner_hash_final = file_sha256(solution_src)
    overall_hash_unaltered = (learner_hash_initial == learner_hash_final)

    # 10. Record everything
    record = {
        "tool_versions": {"gawk": gawk_ver, "bats": bats_ver, "jq": jq_ver, "python": py_ver},
        "enabled_cases": {"expected": EXPECTED_TEST_COUNT, "counted_in_bats": count_bats_tests(test_src)},
        "learner_file_integrity": {
            "initial_sha256": learner_hash_initial,
            "final_sha256": learner_hash_final,
            "unaltered_across_all_runs": overall_hash_unaltered,
        },
        "scenarios": {
            "real_reference": {
                "exit_code": real_run["exit_code"],
                "test_count": real_run["test_count"],
                "temp_cleaned": real_run["temp_cleaned"],
                "hash_preserved": real_hash_match,
            },
            "failing_reference": {
                "exit_code": failing_run["exit_code"],
                "failure_propagated": failing_pass,
                "temp_cleaned": failing_run["temp_cleaned"],
                "hash_preserved": failing_hash_match,
            },
            "zero_tests": {
                "exit_code": zero_run["exit_code"],
                "test_count": zero_run["test_count"],
                "failure_propagated": zero_pass,
                "temp_cleaned": zero_run["temp_cleaned"],
                "hash_preserved": zero_hash_match,
            },
        },
        "validate_run": {
            "returncode": child_rc,
            "tests_counted": val_tests_count,
            "stdout": val_run.stdout,
            "stderr": val_run.stderr,
        },
        "learner_stub_unsolved": stub_unsolved,
        "named_cases_reference": named_cases_verification,
        "assertions": {},
    }

    # 11. Assertions
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
    assert_eq("tests_run_nonzero", True, val_tests_count > 0)
    assert_eq("tests_run_count", EXPECTED_TEST_COUNT, val_tests_count)
    assert_eq("learner_stub_unsolved", True, stub_unsolved)

    print("\n[assertions — named cases]")
    for name, data in named_cases_verification.items():
        assert_eq(f"ref_named_case: {name}", True, data["pass"])

    print("\n[assertions — runner scenarios & protection]")
    assert_eq("real_reference_succeeded", True, real_pass)
    assert_eq("failing_reference_failed_expectedly", True, failing_pass)
    assert_eq("zero_tests_failed_expectedly", True, zero_pass)
    assert_eq("all_temp_dirs_cleaned", True, real_run["temp_cleaned"] and failing_run["temp_cleaned"] and zero_run["temp_cleaned"])
    assert_eq("learner_files_hash_preserved", True, overall_hash_unaltered)

    # 12. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 13. Summary
    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
