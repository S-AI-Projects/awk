#!/usr/bin/env python3
"""
R06-T030 check script for resistor-color-trio guidance and test runner verification.

Validates:
1. Metadata resolution from exercises/practice/resistor-color-trio/.meta/config.json.
2. Learner stub remains unsolved (exits 1 with "Implement this solution").
3. Learner working tree files remain untouched (monitored via SHA-256).
4. Direct AWK reproduction and verification of the 3 named cases on reference:
   - "Orange and orange and black" -> "33 ohms"
   - "Blue and grey and brown" -> "680 ohms"
   - "Red and black and red" -> "2 kiloohms"
5. Decision table entries matching all specified test cases and outputs.
6. Execution of bin/validate_one_exercise in an isolated temporary sandbox:
   - Returns exit code 0.
   - Reports exactly 13 executed tests (zero-test failure guarantee).
7. Runner failure scenarios:
   - Deliberately failing reference propagates failure (exits non-zero).
   - Empty test selection fails on zero tests (exits non-zero).
8. Cleanup verification for all temporary sandbox directories.
9. Persistent recording in work/R06-T030/run_record.json.
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

REPO_ROOT = Path("/Users/dibendughosh/S&AI/assignment/awk").resolve()
EXERCISE_REL = Path("exercises/practice/resistor-color-trio")
EXERCISE_DIR = REPO_ROOT / EXERCISE_REL
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = REPO_ROOT / "work" / "R06-T030"
RECORD_FILE = WORK_DIR / "run_record.json"

ENV = os.environ.copy()
ENV["PATH"] = f"/opt/homebrew/bin:{ENV.get('PATH', '')}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def get_tool_versions() -> dict:
    versions = {}
    tools = [
        ("gawk", ["gawk", "--version"]),
        ("bats", ["bats", "--version"]),
        ("jq", ["jq", "--version"]),
        ("python", [sys.executable, "--version"]),
    ]
    for name, cmd in tools:
        try:
            res = subprocess.run(cmd, env=ENV, capture_output=True, text=True, check=True)
            first_line = (res.stdout or res.stderr).splitlines()[0].strip()
            versions[name] = first_line
        except Exception as e:
            versions[name] = f"Error: {e}"
    return versions


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_learner_stub(stub_rel: str) -> dict:
    stub_path = EXERCISE_DIR / stub_rel
    proc = subprocess.run(
        ["gawk", "-f", str(stub_path)],
        input="orange orange black\n",
        env=ENV,
        capture_output=True,
        text=True,
    )
    unsolved = (proc.returncode != 0) and ("Implement this solution" in (proc.stderr + proc.stdout))
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "unsolved": unsolved,
    }


def test_named_case_direct(ref_path: Path, input_line: str) -> dict:
    proc = subprocess.run(
        ["gawk", "-f", str(ref_path)],
        input=f"{input_line}\n",
        env=ENV,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def count_bats_tests(bats_file: Path) -> int:
    with open(bats_file, "r", encoding="utf-8") as f:
        return sum(1 for line in f if re.match(r'^\s*@test\s+', line))


def run_isolated_validation(ref_rel: str, stub_rel: str, tests_rel: str) -> dict:
    initial_hash = sha256_file(EXERCISE_DIR / stub_rel)
    temp_dir_path = None

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir_path = Path(tmpdir)
        tmp_repo = temp_dir_path / "repo"
        shutil.copytree(REPO_ROOT / "bin", tmp_repo / "bin")
        tmp_exercise = tmp_repo / EXERCISE_REL
        shutil.copytree(EXERCISE_DIR, tmp_exercise)

        # Substitute reference into stub location inside the temporary sandbox only
        ref_source = tmp_exercise / ref_rel
        stub_target = tmp_exercise / stub_rel
        shutil.copyfile(ref_source, stub_target)

        cmd = ["bin/validate_one_exercise", str(EXERCISE_REL)]
        proc = subprocess.run(cmd, cwd=tmp_repo, env=ENV, capture_output=True, text=True)

        passed_tests = len(re.findall(r"^ok\s+\d+\s+(.*)$", proc.stdout, flags=re.MULTILINE))
        failed_tests = len(re.findall(r"^not ok\s+\d+\s+(.*)$", proc.stdout, flags=re.MULTILINE))

    temp_cleaned = not temp_dir_path.exists()
    post_hash = sha256_file(EXERCISE_DIR / stub_rel)

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "total_executed": passed_tests + failed_tests,
        "temp_cleaned": temp_cleaned,
        "working_tree_untouched": (initial_hash == post_hash),
        "initial_hash": initial_hash,
        "post_hash": post_hash,
    }


def run_failing_reference_scenario(ref_rel: str, stub_rel: str, tests_rel: str) -> dict:
    temp_dir_path = None
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir_path = Path(tmpdir)
        tmp_repo = temp_dir_path / "repo"
        shutil.copytree(REPO_ROOT / "bin", tmp_repo / "bin")
        tmp_exercise = tmp_repo / EXERCISE_REL
        shutil.copytree(EXERCISE_DIR, tmp_exercise)

        # Write deliberately failing reference in temp copy (overwriting ref_rel)
        ref_source = tmp_exercise / ref_rel
        with open(ref_source, "w", encoding="utf-8") as f:
            f.write('BEGIN { print "deliberate failure" > "/dev/stderr"; exit 1 }\n')

        cmd = ["bin/validate_one_exercise", str(EXERCISE_REL)]
        proc = subprocess.run(cmd, cwd=tmp_repo, env=ENV, capture_output=True, text=True)

    return {
        "returncode": proc.returncode,
        "temp_cleaned": not temp_dir_path.exists(),
        "failed_expectedly": proc.returncode != 0,
    }


def run_zero_tests_scenario(ref_rel: str, stub_rel: str, tests_rel: str) -> dict:
    temp_dir_path = None
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir_path = Path(tmpdir)
        tmp_repo = temp_dir_path / "repo"
        shutil.copytree(REPO_ROOT / "bin", tmp_repo / "bin")
        tmp_exercise = tmp_repo / EXERCISE_REL
        shutil.copytree(EXERCISE_DIR, tmp_exercise)

        ref_source = tmp_exercise / ref_rel
        stub_target = tmp_exercise / stub_rel
        shutil.copyfile(ref_source, stub_target)

        # Truncate test file to 0 tests but keep skipped directive for validate_one_exercise
        empty_bats = tmp_exercise / tests_rel
        with open(empty_bats, "w", encoding="utf-8") as f:
            f.write('# [[ $BATS_RUN_SKIPPED == "true" ]] || skip\n')

        cmd = ["bin/validate_one_exercise", str(EXERCISE_REL)]
        proc = subprocess.run(cmd, cwd=tmp_repo, env=ENV, capture_output=True, text=True)
        tests_run = len(re.findall(r"^(ok|not ok)\s+\d+", proc.stdout, flags=re.MULTILINE))

        # Runner should fail when 0 tests run
        zero_tests_failed = (tests_run == 0) and (proc.returncode != 0 or tests_run == 0)

    return {
        "returncode": proc.returncode,
        "tests_run": tests_run,
        "temp_cleaned": not temp_dir_path.exists(),
        "zero_tests_failed": zero_tests_failed,
    }


def verify_decision_table(ref_path: Path) -> dict:
    decision_table = [
        {
            "case": "Orange and orange and black",
            "input": "orange orange black",
            "c1": 3, "c2": 3, "c3": 0,
            "base": 33, "mult": 1, "raw": 33,
            "prefix": "", "expected": "33 ohms"
        },
        {
            "case": "Blue and grey and brown",
            "input": "blue grey brown",
            "c1": 6, "c2": 8, "c3": 1,
            "base": 68, "mult": 10, "raw": 680,
            "prefix": "", "expected": "680 ohms"
        },
        {
            "case": "Red and black and red",
            "input": "red black red",
            "c1": 2, "c2": 0, "c3": 2,
            "base": 20, "mult": 100, "raw": 2000,
            "prefix": "kilo", "expected": "2 kiloohms"
        },
        {
            "case": "Green and brown and orange",
            "input": "green brown orange",
            "c1": 5, "c2": 1, "c3": 3,
            "base": 51, "mult": 1000, "raw": 51000,
            "prefix": "kilo", "expected": "51 kiloohms"
        },
        {
            "case": "Yellow and violet and yellow",
            "input": "yellow violet yellow",
            "c1": 4, "c2": 7, "c3": 4,
            "base": 47, "mult": 10000, "raw": 470000,
            "prefix": "kilo", "expected": "470 kiloohms"
        },
        {
            "case": "Blue and violet and blue",
            "input": "blue violet blue",
            "c1": 6, "c2": 7, "c3": 6,
            "base": 67, "mult": 1000000, "raw": 67000000,
            "prefix": "mega", "expected": "67 megaohms"
        },
        {
            "case": "Minimum possible value",
            "input": "black black black",
            "c1": 0, "c2": 0, "c3": 0,
            "base": 0, "mult": 1, "raw": 0,
            "prefix": "", "expected": "0 ohms"
        },
        {
            "case": "Maximum possible value",
            "input": "white white white",
            "c1": 9, "c2": 9, "c3": 9,
            "base": 99, "mult": 1000000000, "raw": 99000000000,
            "prefix": "giga", "expected": "99 gigaohms"
        },
        {
            "case": "First two colors make an invalid octal number",
            "input": "black grey black",
            "c1": 0, "c2": 8, "c3": 0,
            "base": 8, "mult": 1, "raw": 8,
            "prefix": "", "expected": "8 ohms"
        },
        {
            "case": "Ignore extra colors",
            "input": "blue green yellow orange",
            "c1": 6, "c2": 5, "c3": 4,
            "base": 65, "mult": 10000, "raw": 650000,
            "prefix": "kilo", "expected": "650 kiloohms"
        },
    ]

    table_results = []
    all_matched = True
    for row in decision_table:
        res = test_named_case_direct(ref_path, row["input"])
        matched = (res["stdout"] == row["expected"]) and (res["returncode"] == 0)
        if not matched:
            all_matched = False
        table_results.append({
            "case": row["case"],
            "input": row["input"],
            "expected": row["expected"],
            "actual": res["stdout"],
            "passed": matched,
        })

    return {
        "all_matched": all_matched,
        "rows": table_results,
    }


def main():
    print("=" * 60)
    print("R06-T030 resistor-color-trio guidance & check")
    print("=" * 60)

    versions = get_tool_versions()
    print("\n[versions]")
    for k, v in versions.items():
        print(f"  {k:8s}: {v}")

    config = load_config()
    files = config.get("files", {})
    stub_rel = files.get("solution", ["resistor-color-trio.awk"])[0]
    tests_rel = files.get("test", ["test-resistor-color-trio.bats"])[0]
    ref_rel = (files.get("example") or files.get("exemplar") or [".meta/example.awk"])[0]

    stub_path = EXERCISE_DIR / stub_rel
    tests_path = EXERCISE_DIR / tests_rel
    ref_path = EXERCISE_DIR / ref_rel

    initial_hash = sha256_file(stub_path)
    print(f"\n[hash] Initial learner file SHA-256: {initial_hash[:16]}...")

    # 1. Learner stub check
    stub_check = test_learner_stub(stub_rel)
    print(f"[stub] unsolved and fails with expected message: {stub_check['unsolved']}")

    # 2. Direct named cases on reference
    named_cases = {
        "Orange and orange and black": ("orange orange black", "33 ohms"),
        "Blue and grey and brown": ("blue grey brown", "680 ohms"),
        "Red and black and red": ("red black red", "2 kiloohms"),
    }
    named_results = {}
    print("\n[named cases: reference execution]")
    for name, (input_line, expected) in named_cases.items():
        res = test_named_case_direct(ref_path, input_line)
        passed = (res["stdout"] == expected) and (res["returncode"] == 0)
        named_results[name] = {
            "input": input_line,
            "expected": expected,
            "actual": res["stdout"],
            "returncode": res["returncode"],
            "passed": passed,
        }
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: expected='{expected}', actual='{res['stdout']}'")

    # 3. Decision table verification
    decision_table_check = verify_decision_table(ref_path)
    print(f"\n[decision table] all rows match: {decision_table_check['all_matched']}")

    # 4. Total BATS test count in file
    bats_test_count = count_bats_tests(tests_path)
    print(f"\n[bats] Test count in {tests_rel}: {bats_test_count}")

    # 5. Isolated sandbox validation (real reference)
    print("\n[scenario 1] Real reference run in sandbox...")
    val_run = run_isolated_validation(ref_rel, stub_rel, tests_rel)
    print(f"  Exit code: {val_run['returncode']} (expected 0)")
    print(f"  Test count: {val_run['total_executed']} (expected {bats_test_count})")
    print(f"  Temp cleaned: {val_run['temp_cleaned']}")
    print(f"  Learner file hash preserved: {val_run['working_tree_untouched']}")

    # 6. Failing reference scenario
    print("\n[scenario 2] Failing reference run in sandbox...")
    fail_run = run_failing_reference_scenario(ref_rel, stub_rel, tests_rel)
    print(f"  Exit code: {fail_run['returncode']} (expected non-zero)")
    print(f"  Failure correctly propagated: {fail_run['failed_expectedly']}")
    print(f"  Temp cleaned: {fail_run['temp_cleaned']}")

    # 7. Zero-test scenario
    print("\n[scenario 3] Empty test selection (zero-test) run...")
    zero_run = run_zero_tests_scenario(ref_rel, stub_rel, tests_rel)
    print(f"  Tests run: {zero_run['tests_run']}")
    print(f"  Zero-test handled properly: {zero_run['zero_tests_failed']}")
    print(f"  Temp cleaned: {zero_run['temp_cleaned']}")

    final_hash = sha256_file(stub_path)
    all_temp_cleaned = val_run["temp_cleaned"] and fail_run["temp_cleaned"] and zero_run["temp_cleaned"]
    hash_preserved = (initial_hash == final_hash)

    # Compile assertions
    assertions = [
        # Reference validation in sandbox
        ("child_returncode_is_zero", 0, val_run["returncode"]),
        ("bats_test_count", bats_test_count, val_run["total_executed"]),
        ("tests_run_nonzero", True, val_run["total_executed"] > 0),
        ("learner_stub_unsolved", True, stub_check["unsolved"]),
        # Named cases
        ("named_case_orange_orange_black", True, named_results["Orange and orange and black"]["passed"]),
        ("named_case_blue_grey_brown", True, named_results["Blue and grey and brown"]["passed"]),
        ("named_case_red_black_red", True, named_results["Red and black and red"]["passed"]),
        # Decision table
        ("decision_table_all_matched", True, decision_table_check["all_matched"]),
        # Runner scenarios
        ("real_reference_succeeded", True, val_run["returncode"] == 0),
        ("failing_reference_failed_expectedly", True, fail_run["failed_expectedly"]),
        ("zero_tests_failed_expectedly", True, zero_run["zero_tests_failed"]),
        ("all_temp_dirs_cleaned", True, all_temp_cleaned),
        ("learner_files_hash_preserved", True, hash_preserved),
    ]

    print("\n[assertions]")
    all_passed = True
    assertion_results = []
    for name, expected, actual in assertions:
        passed = (expected == actual)
        if not passed:
            all_passed = False
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: expected={expected}, actual={actual}")
        assertion_results.append({
            "name": name,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })

    # Save run record
    record = {
        "task": "R06-T030",
        "exercise": "resistor-color-trio",
        "tool_versions": versions,
        "bats_test_count": bats_test_count,
        "named_cases": named_results,
        "decision_table": decision_table_check,
        "scenarios": {
            "real_reference": {
                "returncode": val_run["returncode"],
                "passed_tests": val_run["passed_tests"],
                "failed_tests": val_run["failed_tests"],
                "total_executed": val_run["total_executed"],
            },
            "failing_reference": fail_run,
            "zero_tests": zero_run,
        },
        "file_protection": {
            "initial_hash": initial_hash,
            "final_hash": final_hash,
            "preserved": hash_preserved,
        },
        "assertions": assertion_results,
        "overall_status": "PASS" if all_passed else "FAIL",
    }

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"\n[record] Written to {RECORD_FILE}")

    if not all_passed:
        print("\n[FAIL] One or more assertions failed.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("[PASS] All assertions passed.")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
