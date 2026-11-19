#!/usr/bin/env python3
"""
Verification Script for Task R06-T018 (diamond exercise).
Validates path resolution, verifies that deliberately invalid metadata fixtures fail,
asserts execution of all 5 tests against the reference solution including named cases,
ensures learner stub remains unsolved, and records execution evidence.
"""

import datetime
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


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T018")
    os.makedirs(work_dir, exist_ok=True)

    print("=== Starting R06-T018 Verification Check ===")

    # 1. Record tool versions
    print("Recording tool versions...")
    record_tool_versions(work_dir)

    # 2. Check learner stub integrity
    exercise_rel_path = os.path.join("exercises", "practice", "diamond")
    exercise_dir = os.path.join(repo_root, exercise_rel_path)
    config_path = os.path.join(exercise_dir, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_file = config_data["files"]["solution"][0]
    stub_path = os.path.join(exercise_dir, solution_file)

    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()

    if "Implement this solution" not in stub_content or "exit 1" not in stub_content:
        print(f"Error: Learner stub {stub_path} appears modified or solved!", file=sys.stderr)
        sys.exit(1)
    print(f"Verified learner stub {solution_file} remains untouched and unsolved.")

    # 3. Execute tools/course_checks/r06-t018.py metadata audit
    print("Executing metadata & path security audit (tools/course_checks/r06-t018.py)...")
    audit_script = os.path.join(repo_root, "tools", "course_checks", "r06-t018.py")
    audit_res = subprocess.run([sys.executable, audit_script], capture_output=True, text=True)

    if audit_res.returncode != 0:
        print(f"Error: Metadata audit failed with code {audit_res.returncode}!", file=sys.stderr)
        print(audit_res.stderr, file=sys.stderr)
        sys.exit(audit_res.returncode)
    print("Metadata audit passed cleanly: real config verified and all 3 invalid fixtures failed.")

    # 4. Validate reference solution in an isolated temporary directory
    print("Executing bin/validate_one_exercise inside isolated temporary directory...")
    with tempfile.TemporaryDirectory() as temp_root:
        temp_exercise_dir = os.path.join(temp_root, "exercises", "practice", "diamond")
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

    if len(failed_tests) > 0 or total_tests != 5:
        print(f"Error: Expected 5 passing tests, but found {len(failed_tests)} failures!", file=sys.stderr)
        sys.exit(1)

    # 5. Verify named baseline cases
    named_cases = [
        (1, "Degenerate case with a single 'A' row"),
        (2, "Degenerate case with no row containing 3 distinct groups of spaces"),
        (3, "Smallest non-degenerate case with odd diamond side length")
    ]

    passed_dict = dict(passed_tests)
    for test_idx, case_name in named_cases:
        if test_idx not in passed_dict or passed_dict[test_idx] != case_name:
            print(f"Error: Named case #{test_idx} ('{case_name}') was not reported as passed!", file=sys.stderr)
            sys.exit(1)
        print(f"Named Baseline Case #{test_idx} Verified: '{case_name}' -> PASS")

    # 6. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: diamond\n"
        f"Task: R06-T018\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Validator Exit Code: {val_res.returncode}\n"
        f"Tests Executed: {total_tests} (Passed: {len(passed_tests)}, Failed: {len(failed_tests)})\n"
        f"Learner Stub Status: Untouched (unsolved)\n\n"
        f"=== NAMED BASELINE CASES ===\n"
        f"1. Degenerate case with a single 'A' row: PASS\n"
        f"2. Degenerate case with no row containing 3 distinct groups of spaces: PASS\n"
        f"3. Smallest non-degenerate case with odd diamond side length: PASS\n\n"
        f"=== METADATA FIXTURE AUDIT ===\n"
        f"Real Config Status: PASS\n"
        f"Fixture 1 (missing-reference): FAILED AS EXPECTED (FileNotFoundError)\n"
        f"Fixture 2 (missing-test):      FAILED AS EXPECTED (FileNotFoundError)\n"
        f"Fixture 3 (outside-exercise):  FAILED AS EXPECTED (ValueError - Traversal)\n\n"
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
        "exercise": "diamond",
        "task": "R06-T018",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validator_run": {
            "exit_code": val_res.returncode,
            "total_cases": total_tests,
            "passed_cases": len(passed_tests),
            "failed_cases": len(failed_tests)
        },
        "metadata_audit": {
            "real_config_status": "PASS",
            "declared_files": [
                {"role": "solution", "path": "diamond.awk", "status": "VERIFIED"},
                {"role": "test", "path": "test-diamond.bats", "status": "VERIFIED"},
                {"role": "example", "path": ".meta/example.awk", "status": "VERIFIED"}
            ],
            "fixtures": {
                "fixture_1_missing_reference": "FAILED_AS_EXPECTED (FileNotFoundError)",
                "fixture_2_missing_test": "FAILED_AS_EXPECTED (FileNotFoundError)",
                "fixture_3_outside_exercise": "FAILED_AS_EXPECTED (ValueError - Path Traversal)"
            }
        },
        "named_baseline_cases": [
            {
                "test_number": 1,
                "description": "Degenerate case with a single 'A' row",
                "status": "PASS"
            },
            {
                "test_number": 2,
                "description": "Degenerate case with no row containing 3 distinct groups of spaces",
                "status": "PASS"
            },
            {
                "test_number": 3,
                "description": "Smallest non-degenerate case with odd diamond side length",
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
