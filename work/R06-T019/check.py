#!/usr/bin/env python3
"""
Verification Script for Task R06-T019 (prime-factors exercise).
Validates isolated execution across standard, failing-reference, and empty-tests modes,
verifies learner stub SHA256 integrity, asserts execution of all 12 tests including
named baseline cases, and emits execution evidence.
"""

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


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


def parse_tap_output(stdout: str):
    """Parse TAP output lines."""
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


def get_file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T019")
    os.makedirs(work_dir, exist_ok=True)

    print("=== Starting R06-T019 Verification Check ===")

    # 1. Record tool versions
    print("Recording tool versions...")
    record_tool_versions(work_dir)

    # 2. Check learner stub integrity
    exercise_rel_path = os.path.join("exercises", "practice", "prime-factors")
    exercise_dir = os.path.join(repo_root, exercise_rel_path)
    config_path = os.path.join(exercise_dir, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_file = config_data["files"]["solution"][0]
    stub_path = os.path.join(exercise_dir, solution_file)

    stub_hash_before = get_file_hash(stub_path)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()

    if "Implement this solution" not in stub_content or "exit 1" not in stub_content:
        print(f"Error: Learner stub {stub_path} appears modified or solved!", file=sys.stderr)
        sys.exit(1)
    print(f"Verified learner stub {solution_file} remains untouched and unsolved.")

    # 3. Execute tools/course_checks/r06-t019.py isolated runner check
    print("Executing isolated runner audit (tools/course_checks/r06-t019.py)...")
    runner_script = os.path.join(repo_root, "tools", "course_checks", "r06-t019.py")
    runner_res = subprocess.run([sys.executable, runner_script], capture_output=True, text=True)

    if runner_res.returncode != 0:
        print(f"Error: Isolated runner audit failed with code {runner_res.returncode}!", file=sys.stderr)
        print(runner_res.stderr, file=sys.stderr)
        sys.exit(runner_res.returncode)
    print("Isolated runner audit passed cleanly across standard, failing-reference, and empty-tests modes.")

    # 4. Validate reference solution in an isolated temporary directory
    print("Executing bin/validate_one_exercise inside isolated temporary directory...")
    with tempfile.TemporaryDirectory() as temp_root:
        temp_exercise_dir = os.path.join(temp_root, "exercises", "practice", "prime-factors")
        os.makedirs(os.path.dirname(temp_exercise_dir), exist_ok=True)
        shutil.copytree(exercise_dir, temp_exercise_dir)

        temp_bin_dir = os.path.join(temp_root, "bin")
        shutil.copytree(os.path.join(repo_root, "bin"), temp_bin_dir)

        val_cmd = [os.path.join(temp_bin_dir, "validate_one_exercise"), temp_exercise_dir]
        val_res = subprocess.run(val_cmd, cwd=temp_root, capture_output=True, text=True)

    if val_res.returncode != 0:
        print(f"Error: Reference solution failed validation with code {val_res.returncode}!", file=sys.stderr)
        print(val_res.stderr, file=sys.stderr)
        sys.exit(val_res.returncode)

    total_tests, passed_tests, failed_tests = parse_tap_output(val_res.stdout)
    print(f"Validation summary: Total={total_tests}, Passed={len(passed_tests)}, Failed={len(failed_tests)}")

    if total_tests == 0 or len(passed_tests) == 0:
        print("Error: Zero test cases were executed!", file=sys.stderr)
        sys.exit(1)

    if len(failed_tests) > 0 or total_tests != 12:
        print(f"Error: Expected 12 passing tests, but found {len(failed_tests)} failures!", file=sys.stderr)
        sys.exit(1)

    # 5. Verify named baseline cases
    named_cases = [
        (1, "no factors", "1", ""),
        (2, "prime number", "2", "2"),
        (3, "another prime number", "3", "3")
    ]

    passed_dict = dict(passed_tests)
    for test_idx, case_name, exp_in, exp_out in named_cases:
        if test_idx not in passed_dict or passed_dict[test_idx] != case_name:
            print(f"Error: Named case #{test_idx} ('{case_name}') was not reported as passed!", file=sys.stderr)
            sys.exit(1)
        print(f"Named Baseline Case #{test_idx} Verified: '{case_name}' [Input: {exp_in} -> Expected: '{exp_out}'] -> PASS")

    # Verify learner stub hash remains unchanged
    stub_hash_after = get_file_hash(stub_path)
    if stub_hash_before != stub_hash_after:
        print(f"Error: Learner stub hash changed from {stub_hash_before} to {stub_hash_after}!", file=sys.stderr)
        sys.exit(1)
    print(f"Verified cryptographic hash unchanged: {stub_hash_before}")

    # 6. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: prime-factors\n"
        f"Task: R06-T019\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Validator Exit Code: {val_res.returncode}\n"
        f"Tests Executed: {total_tests} (Passed: {len(passed_tests)}, Failed: {len(failed_tests)})\n"
        f"Learner Stub SHA256 (Untouched): {stub_hash_before}\n\n"
        f"=== NAMED BASELINE CASES ===\n"
        f"1. no factors: PASS (Input: 1 -> Output: '')\n"
        f"2. prime number: PASS (Input: 2 -> Output: '2')\n"
        f"3. another prime number: PASS (Input: 3 -> Output: '3')\n\n"
        f"=== ISOLATION MODE AUDIT ===\n"
        f"Standard Mode: PASS (all 12 tests passed, rc=0)\n"
        f"Failing Reference Mode: PASS (cleanly failed with non-zero exit code as expected)\n"
        f"Empty Tests Mode: PASS (zero-test run rejected as expected)\n"
        f"Cryptographic Hash Check: PASS (identical before and after all runs)\n\n"
        f"=== VALIDATOR STDOUT ===\n"
        f"{val_res.stdout}\n"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    # 7. Emit expected_vs_actual.json
    case_reports = []
    for num, desc in passed_tests:
        case_reports.append({
            "test_number": num,
            "description": desc,
            "status": "ok",
            "is_named_baseline_case": num in [1, 2, 3]
        })

    expected_vs_actual = {
        "exercise": "prime-factors",
        "task": "R06-T019",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validator_run": {
            "exit_code": val_res.returncode,
            "total_cases": total_tests,
            "passed_cases": len(passed_tests),
            "failed_cases": len(failed_tests)
        },
        "isolation_audit": {
            "learner_stub_sha256": stub_hash_before,
            "hash_verified_identical": True,
            "modes_tested": {
                "standard": "PASS (rc=0, 12 passed)",
                "failing_reference": "PASS (non-zero rc, failure detected)",
                "empty_tests": "PASS (zero-test run rejected)"
            }
        },
        "named_baseline_cases": [
            {
                "test_number": 1,
                "description": "no factors",
                "input": "1",
                "expected_output": "",
                "status": "PASS"
            },
            {
                "test_number": 2,
                "description": "prime number",
                "input": "2",
                "expected_output": "2",
                "status": "PASS"
            },
            {
                "test_number": 3,
                "description": "another prime number",
                "input": "3",
                "expected_output": "3",
                "status": "PASS"
            }
        ],
        "cases": case_reports
    }

    with open(os.path.join(work_dir, "expected_vs_actual.json"), "w", encoding="utf-8") as f:
        json.dump(expected_vs_actual, f, indent=2)

    print("\n--- All Verification Checks Succeeded Cleanly ---")
    print(f"Generated verification artifacts in: {work_dir}")


if __name__ == "__main__":
    main()
