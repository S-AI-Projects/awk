#!/usr/bin/env python3
"""
Verification Script for Task R06-T014 (allergies exercise).
Validates reference implementation readability refactoring, asserts execution
of all 50 test cases including the named eggs allergy baseline cases, verifies
the learner stub remains untouched and unsolved, and records evidence.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib


def record_tool_versions(work_dir: str):
    """Query and record versions of bash, gawk, bats, python3, and jq."""
    versions = {}
    commands = {
        "Bash Version": ["bash", "--version"],
        "AWK Version": ["gawk", "--version"],
        "Bats Version": ["bats", "--version"],
        "Python Version": [sys.executable, "--version"],
        "jq Version": ["jq", "--version"],
    }

    for label, cmd in commands.items():
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            first_line = res.stdout.strip().splitlines()[0] if res.stdout.strip() else res.stderr.strip().splitlines()[0]
            versions[label] = first_line
        except Exception as e:
            versions[label] = f"Error querying: {e}"

    versions_path = os.path.join(work_dir, "versions.txt")
    with open(versions_path, "w", encoding="utf-8") as f:
        for label, ver in versions.items():
            f.write(f"{label}:\n{ver}\n\n")

    return versions


def parse_bats_cases(bats_path: str):
    """Extract test case names, inputs, and expected outputs from test-allergies.bats."""
    with open(bats_path, "r", encoding="utf-8") as f:
        content = f.read()

    test_pattern = re.compile(
        r'@test\s+"([^"]+)"\s*\{\s*'
        r'(?:#?\s*\[\[\s*\$BATS_RUN_SKIPPED\s*==\s*"true"\s*\]\]\s*\|\|\s*skip\s*)?'
        r'run\s+gawk\s+-f\s+allergies\.awk\s+<<<\s*\'([^\']*)\'\s*'
        r'assert_success\s*'
        r'(?:assert_output\s*(?:--partial\s*)?"([^"]*)")?',
        re.MULTILINE
    )

    cases = []
    for match in test_pattern.finditer(content):
        desc = match.group(1).strip()
        inp = match.group(2).strip()
        out = match.group(3) if match.group(3) is not None else ""
        cases.append({
            "description": desc,
            "input": inp,
            "expected_output": out,
            "expected_status": "success"
        })

    return cases


def parse_tap_output(stdout: str):
    """Parse TAP output lines (e.g. 'ok 1 ...' or 'not ok 2 ...')."""
    passed = []
    failed = []
    total = 0

    plan_match = re.search(r"^1\.\.(\d+)", stdout, re.MULTILINE)
    if plan_match:
        total = int(plan_match.group(1))

    for line in stdout.splitlines():
        ok_match = re.match(r"^ok\s+(\d+)\s+(.*)", line)
        not_ok_match = re.match(r"^not ok\s+(\d+)\s+(.*)", line)
        if ok_match:
            passed.append((int(ok_match.group(1)), ok_match.group(2).strip()))
        elif not_ok_match:
            failed.append((int(not_ok_match.group(1)), not_ok_match.group(2).strip()))

    return total, passed, failed


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T014")
    os.makedirs(work_dir, exist_ok=True)

    print("=== Starting R06-T014 Verification Check ===")

    # 1. Record tool versions
    print("Recording tool versions...")
    versions = record_tool_versions(work_dir)

    # 2. Inspect exercise configuration
    exercise_rel_path = os.path.join("exercises", "practice", "allergies")
    exercise_dir = os.path.join(repo_root, exercise_rel_path)
    config_path = os.path.join(exercise_dir, ".meta", "config.json")

    if not os.path.exists(config_path):
        print(f"Error: Missing config.json at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_file = config_data["files"]["solution"][0]
    test_file = config_data["files"]["test"][0]
    example_file = config_data["files"]["example"][0]

    # Verify learner stub integrity (must be unsolved stub)
    stub_path = os.path.join(exercise_dir, solution_file)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()

    if "Implement this solution" not in stub_content or "exit 1" not in stub_content:
        print(f"Error: Learner stub {stub_path} appears solved or modified!", file=sys.stderr)
        sys.exit(1)
    print(f"Verified learner stub {solution_file} remains untouched and unsolved.")

    # Parse test suite cases
    bats_path = os.path.join(exercise_dir, test_file)
    extracted_cases = parse_bats_cases(bats_path)
    print(f"Extracted {len(extracted_cases)} test cases from {test_file}.")

    # Parse tests.toml
    toml_path = os.path.join(exercise_dir, ".meta", "tests.toml")
    with open(toml_path, "rb") as f:
        toml_data = tomllib.load(f)
    print(f"Loaded {len(toml_data)} canonical test cases from tests.toml.")

    # 3. Execute validation in an isolated temporary directory
    print("Executing bin/validate_one_exercise inside isolated temporary directory...")
    with tempfile.TemporaryDirectory() as temp_root:
        temp_exercise_dir = os.path.join(temp_root, "exercises", "practice", "allergies")
        os.makedirs(os.path.dirname(temp_exercise_dir), exist_ok=True)
        shutil.copytree(exercise_dir, temp_exercise_dir)

        # Copy bin directory into temporary root
        temp_bin_dir = os.path.join(temp_root, "bin")
        shutil.copytree(os.path.join(repo_root, "bin"), temp_bin_dir)

        validate_cmd = [
            os.path.join(temp_bin_dir, "validate_one_exercise"),
            temp_exercise_dir
        ]

        run_result = subprocess.run(
            validate_cmd,
            cwd=temp_root,
            capture_output=True,
            text=True
        )

    print(f"Validator exited with status code: {run_result.returncode}")
    if run_result.returncode != 0:
        print(f"Validation FAILED with non-zero exit code {run_result.returncode}!", file=sys.stderr)
        print("STDOUT:\n", run_result.stdout, file=sys.stderr)
        print("STDERR:\n", run_result.stderr, file=sys.stderr)
        sys.exit(run_result.returncode)

    total_tests, passed_tests, failed_tests = parse_tap_output(run_result.stdout)
    print(f"Validation summary: Total={total_tests}, Passed={len(passed_tests)}, Failed={len(failed_tests)}")

    # Strict assertion on test count and zero-failure
    if total_tests == 0 or len(passed_tests) == 0:
        print("Error: Zero test cases were executed!", file=sys.stderr)
        sys.exit(1)

    if len(failed_tests) > 0 or total_tests != 50:
        print(f"Error: Expected 50 passing test cases, but found {len(failed_tests)} failures!", file=sys.stderr)
        sys.exit(1)

    # 4. Verify the named baseline cases
    named_cases = [
        (1, "testing for eggs allergy: not allergic to anything", "0,allergic_to,eggs", "false"),
        (2, "testing for eggs allergy: allergic only to eggs", "1,allergic_to,eggs", "true"),
        (3, "testing for eggs allergy: allergic to eggs and something else", "3,allergic_to,eggs", "true"),
    ]

    passed_dict = dict(passed_tests)
    for test_idx, case_name, exp_in, exp_out in named_cases:
        if test_idx not in passed_dict:
            print(f"Error: Named case #{test_idx} ('{case_name}') was not reported as passed!", file=sys.stderr)
            sys.exit(1)
        if passed_dict[test_idx] != case_name:
            print(f"Warning: Case #{test_idx} name mismatch: expected '{case_name}', got '{passed_dict[test_idx]}'")
        print(f"Named Baseline Case #{test_idx} Verified: '{case_name}' [Input: {exp_in} -> Expected: {exp_out}] -> PASS")

    # 5. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: allergies\n"
        f"Task: R06-T014\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Validator Exit Code: {run_result.returncode}\n"
        f"Total Tests Executed: {total_tests}\n"
        f"Tests Passed: {len(passed_tests)}\n"
        f"Tests Failed: {len(failed_tests)}\n"
        f"Learner Stub Status: Untouched (unsolved)\n\n"
        f"=== NAMED BASELINE CASES ===\n"
        f"1. testing for eggs allergy: not allergic to anything (Input: '0,allergic_to,eggs' -> Output: 'false') [PASSED]\n"
        f"2. testing for eggs allergy: allergic only to eggs (Input: '1,allergic_to,eggs' -> Output: 'true') [PASSED]\n"
        f"3. testing for eggs allergy: allergic to eggs and something else (Input: '3,allergic_to,eggs' -> Output: 'true') [PASSED]\n\n"
        f"=== VALIDATOR STDOUT ===\n"
        f"{run_result.stdout}\n"
        f"=== VALIDATOR STDERR ===\n"
        f"{run_result.stderr}\n"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    # 6. Emit expected_vs_actual.json
    case_reports = []
    for idx, case_info in enumerate(extracted_cases, 1):
        status = "ok" if idx in passed_dict else "not ok"
        case_reports.append({
            "test_number": idx,
            "description": case_info["description"],
            "input": case_info["input"],
            "expected_output": case_info["expected_output"],
            "actual_status": status,
            "is_named_baseline_case": idx in [1, 2, 3]
        })

    expected_vs_actual = {
        "exercise": "allergies",
        "task": "R06-T014",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validator_run": {
            "exit_code": run_result.returncode,
            "total_cases": total_tests,
            "passed_cases": len(passed_tests),
            "failed_cases": len(failed_tests)
        },
        "named_baseline_cases": [
            {
                "test_number": 1,
                "description": "testing for eggs allergy: not allergic to anything",
                "input": "0,allergic_to,eggs",
                "expected_output": "false",
                "status": "PASS"
            },
            {
                "test_number": 2,
                "description": "testing for eggs allergy: allergic only to eggs",
                "input": "1,allergic_to,eggs",
                "expected_output": "true",
                "status": "PASS"
            },
            {
                "test_number": 3,
                "description": "testing for eggs allergy: allergic to eggs and something else",
                "input": "3,allergic_to,eggs",
                "expected_output": "true",
                "status": "PASS"
            }
        ],
        "all_cases": case_reports
    }

    with open(os.path.join(work_dir, "expected_vs_actual.json"), "w", encoding="utf-8") as f:
        json.dump(expected_vs_actual, f, indent=2)

    print("\n--- All Verification Checks Succeeded Cleanly ---")
    print(f"Generated verification artifacts in: {work_dir}")


if __name__ == "__main__":
    main()
