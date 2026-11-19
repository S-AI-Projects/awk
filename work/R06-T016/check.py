#!/usr/bin/env python3
"""
Verification Script for Task R06-T016 (hamming exercise).
Validates reference implementation (Approach A: field-splitting) and alternative
implementation (Approach B: substr extraction) across all 9 test cases in test-hamming.bats,
confirms 100% agreement on named baseline cases, asserts learner stub integrity,
and records execution evidence.
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


def run_test_suite_with_solution(exercise_dir: str, solution_awk_path: str):
    """Run bats test-hamming.bats with a given solution in an isolated temp directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_src = os.path.join(exercise_dir, "test-hamming.bats")
        extra_src = os.path.join(exercise_dir, "bats-extra.bash")

        temp_test = os.path.join(temp_dir, "test-hamming.bats")
        temp_extra = os.path.join(temp_dir, "bats-extra.bash")
        temp_sol = os.path.join(temp_dir, "hamming.awk")

        shutil.copyfile(test_src, temp_test)
        shutil.copyfile(extra_src, temp_extra)
        shutil.copyfile(solution_awk_path, temp_sol)

        env = os.environ.copy()
        env["BATS_RUN_SKIPPED"] = "true"

        res = subprocess.run(
            ["bats", temp_test],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            env=env
        )

        return res


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T016")
    os.makedirs(work_dir, exist_ok=True)

    print("=== Starting R06-T016 Verification Check ===")

    # 1. Record tool versions
    print("Recording tool versions...")
    record_tool_versions(work_dir)

    # 2. Check learner stub integrity
    exercise_rel_path = os.path.join("exercises", "practice", "hamming")
    exercise_dir = os.path.join(repo_root, exercise_rel_path)
    config_path = os.path.join(exercise_dir, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_file = config_data["files"]["solution"][0]
    example_file = config_data["files"]["example"][0]
    test_file = config_data["files"]["test"][0]

    stub_path = os.path.join(exercise_dir, solution_file)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()

    if "Implement this solution" not in stub_content or "exit 1" not in stub_content:
        print(f"Error: Learner stub {stub_path} appears modified or solved!", file=sys.stderr)
        sys.exit(1)
    print(f"Verified learner stub {solution_file} remains untouched and unsolved.")

    # 3. Test Approach A (Reference implementation via validate_one_exercise)
    print("Validating Approach A (Reference: Field-splitting) via bin/validate_one_exercise...")
    with tempfile.TemporaryDirectory() as temp_root:
        temp_exercise_dir = os.path.join(temp_root, "exercises", "practice", "hamming")
        os.makedirs(os.path.dirname(temp_exercise_dir), exist_ok=True)
        shutil.copytree(exercise_dir, temp_exercise_dir)

        temp_bin_dir = os.path.join(temp_root, "bin")
        shutil.copytree(os.path.join(repo_root, "bin"), temp_bin_dir)

        val_cmd = [os.path.join(temp_bin_dir, "validate_one_exercise"), temp_exercise_dir]
        ref_res = subprocess.run(val_cmd, cwd=temp_root, capture_output=True, text=True)

    if ref_res.returncode != 0:
        print(f"Error: Approach A failed validation with code {ref_res.returncode}!", file=sys.stderr)
        print(ref_res.stderr, file=sys.stderr)
        sys.exit(ref_res.returncode)

    ref_total, ref_passed, ref_failed = parse_tap_output(ref_res.stdout)
    print(f"Approach A (Reference): Total={ref_total}, Passed={len(ref_passed)}, Failed={len(ref_failed)}")

    # 4. Test Approach B (Alternative implementation: substr scanning)
    alt_path = os.path.join(work_dir, "alternative.awk")
    if not os.path.exists(alt_path):
        print(f"Error: Missing alternative implementation at {alt_path}!", file=sys.stderr)
        sys.exit(1)

    print("Validating Approach B (Alternative: substr scanning) via bats...")
    alt_res = run_test_suite_with_solution(exercise_dir, alt_path)
    if alt_res.returncode != 0:
        print(f"Error: Approach B failed test execution with code {alt_res.returncode}!", file=sys.stderr)
        print(alt_res.stderr, file=sys.stderr)
        sys.exit(alt_res.returncode)

    alt_total, alt_passed, alt_failed = parse_tap_output(alt_res.stdout)
    print(f"Approach B (Alternative): Total={alt_total}, Passed={len(alt_passed)}, Failed={len(alt_failed)}")

    # 5. Assert equality of test outcomes
    if ref_total != 9 or alt_total != 9:
        print(f"Error: Expected 9 tests for both approaches, got ref={ref_total}, alt={alt_total}", file=sys.stderr)
        sys.exit(1)

    if len(ref_failed) > 0 or len(alt_failed) > 0:
        print(f"Error: Detected test failures! Ref failures: {len(ref_failed)}, Alt failures: {len(alt_failed)}", file=sys.stderr)
        sys.exit(1)

    # 6. Verify named baseline cases
    named_cases = [
        (1, "empty strands", "'' vs ''", "0"),
        (2, "single letter identical strands", "'A' vs 'A'", "0"),
        (3, "single letter different strands", "'G' vs 'T'", "1")
    ]

    ref_passed_dict = dict(ref_passed)
    alt_passed_dict = dict(alt_passed)

    for test_idx, case_name, exp_in, exp_out in named_cases:
        if test_idx not in ref_passed_dict or test_idx not in alt_passed_dict:
            print(f"Error: Named case #{test_idx} ('{case_name}') failed to pass in both approaches!", file=sys.stderr)
            sys.exit(1)
        print(f"Named Baseline Case #{test_idx} Verified: '{case_name}' [Input: {exp_in} -> Expected: {exp_out}] -> PASS in both")

    # 7. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: hamming\n"
        f"Task: R06-T016\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Learner Stub Status: Untouched (unsolved)\n\n"
        f"=== APPROACH A: REFERENCE (FIELD-SPLITTING) ===\n"
        f"Validator Exit Code: {ref_res.returncode}\n"
        f"Tests Executed: {ref_total} (Passed: {len(ref_passed)}, Failed: {len(ref_failed)})\n\n"
        f"=== APPROACH B: ALTERNATIVE (SUBSTR EXTRACTION) ===\n"
        f"Bats Exit Code: {alt_res.returncode}\n"
        f"Tests Executed: {alt_total} (Passed: {len(alt_passed)}, Failed: {len(alt_failed)})\n\n"
        f"=== NAMED BASELINE CASES (BOTH PASSED) ===\n"
        f"1. empty strands: PASS (Output: 0)\n"
        f"2. single letter identical strands: PASS (Output: 0)\n"
        f"3. single letter different strands: PASS (Output: 1)\n\n"
        f"=== APPROACH A OUTPUT ===\n"
        f"{ref_res.stdout}\n"
        f"=== APPROACH B OUTPUT ===\n"
        f"{alt_res.stdout}\n"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    # 8. Emit expected_vs_actual.json
    case_reports = []
    for num, desc in ref_passed:
        case_reports.append({
            "test_number": num,
            "description": desc,
            "approach_a_status": "ok",
            "approach_b_status": "ok",
            "is_named_baseline_case": num in [1, 2, 3]
        })

    expected_vs_actual = {
        "exercise": "hamming",
        "task": "R06-T016",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "approaches_evaluated": {
            "approach_a": {
                "name": "Positional Field-Splitting (Reference)",
                "file": "exercises/practice/hamming/.meta/example.awk",
                "exit_code": ref_res.returncode,
                "passed_tests": len(ref_passed),
                "total_tests": ref_total
            },
            "approach_b": {
                "name": "Direct Substring Scanning (Alternative)",
                "file": "work/R06-T016/alternative.awk",
                "exit_code": alt_res.returncode,
                "passed_tests": len(alt_passed),
                "total_tests": alt_total
            }
        },
        "named_baseline_cases": [
            {
                "test_number": 1,
                "description": "empty strands",
                "input": "'' vs ''",
                "expected_output": "0",
                "approach_a_result": "PASS",
                "approach_b_result": "PASS"
            },
            {
                "test_number": 2,
                "description": "single letter identical strands",
                "input": "'A' vs 'A'",
                "expected_output": "0",
                "approach_a_result": "PASS",
                "approach_b_result": "PASS"
            },
            {
                "test_number": 3,
                "description": "single letter different strands",
                "input": "'G' vs 'T'",
                "expected_output": "1",
                "approach_a_result": "PASS",
                "approach_b_result": "PASS"
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
