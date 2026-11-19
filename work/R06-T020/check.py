#!/usr/bin/env python3
"""
Verification Script for Task R06-T020 (bob exercise).
Validates reference implementation across all 26 test cases, confirms 100% agreement
on contract decision table cases ('asking a question', 'shouting', 'forceful question'),
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
    work_dir = os.path.join(repo_root, "work", "R06-T020")
    os.makedirs(work_dir, exist_ok=True)

    print("=== Starting R06-T020 Verification Check ===")

    # 1. Record tool versions
    print("Recording tool versions...")
    record_tool_versions(work_dir)

    # 2. Check learner stub integrity
    exercise_rel_path = os.path.join("exercises", "practice", "bob")
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

    # 3. Validate reference solution in an isolated temporary directory
    print("Executing bin/validate_one_exercise inside isolated temporary directory...")
    with tempfile.TemporaryDirectory() as temp_root:
        temp_exercise_dir = os.path.join(temp_root, "exercises", "practice", "bob")
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

    if len(failed_tests) > 0 or total_tests != 26:
        print(f"Error: Expected 26 passing tests, but found {len(failed_tests)} failures!", file=sys.stderr)
        sys.exit(1)

    # 4. Verify named baseline cases & decision table alignment
    named_cases = [
        (1, "asking a question", "Does this cryogenic chamber make me look fat?", "Sure."),
        (2, "shouting", "WATCH OUT!", "Whoa, chill out!"),
        (3, "forceful question", "WHAT'S GOING ON?", "Calm down, I know what I'm doing!")
    ]

    passed_dict = dict(passed_tests)
    for test_idx, case_name, exp_in, exp_out in named_cases:
        if test_idx not in passed_dict or passed_dict[test_idx] != case_name:
            print(f"Error: Named case #{test_idx} ('{case_name}') was not reported as passed!", file=sys.stderr)
            sys.exit(1)
        print(f"Named Baseline Case #{test_idx} Verified: '{case_name}' [Input: '{exp_in}' -> Expected: '{exp_out}'] -> PASS")

    # 5. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: bob\n"
        f"Task: R06-T020\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Validator Exit Code: {val_res.returncode}\n"
        f"Tests Executed: {total_tests} (Passed: {len(passed_tests)}, Failed: {len(failed_tests)})\n"
        f"Learner Stub Status: Untouched (unsolved)\n\n"
        f"=== NAMED BASELINE CASES ===\n"
        f"1. asking a question: PASS (Output: 'Sure.')\n"
        f"2. shouting: PASS (Output: 'Whoa, chill out!')\n"
        f"3. forceful question: PASS (Output: 'Calm down, I know what I'm doing!')\n\n"
        f"=== VALIDATOR STDOUT ===\n"
        f"{val_res.stdout}\n"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    # 6. Emit expected_vs_actual.json
    case_reports = []
    for num, desc in passed_tests:
        case_reports.append({
            "test_number": num,
            "description": desc,
            "status": "ok",
            "is_named_baseline_case": num in [1, 2, 3]
        })

    decision_table = [
        {
            "category": "Silence",
            "condition": "trim(input) == ''",
            "response": "Fine. Be that way!"
        },
        {
            "category": "Forceful Question",
            "condition": "is_yelling && is_asking",
            "response": "Calm down, I know what I'm doing!"
        },
        {
            "category": "Shouting",
            "condition": "is_yelling && !is_asking",
            "response": "Whoa, chill out!"
        },
        {
            "category": "Question",
            "condition": "!is_yelling && is_asking",
            "response": "Sure."
        },
        {
            "category": "Statement / Other",
            "condition": "default / fallback",
            "response": "Whatever."
        }
    ]

    expected_vs_actual = {
        "exercise": "bob",
        "task": "R06-T020",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validator_run": {
            "exit_code": val_res.returncode,
            "total_cases": total_tests,
            "passed_cases": len(passed_tests),
            "failed_cases": len(failed_tests)
        },
        "decision_table": decision_table,
        "named_baseline_cases": [
            {
                "test_number": 1,
                "description": "asking a question",
                "input": "Does this cryogenic chamber make me look fat?",
                "expected_output": "Sure.",
                "status": "PASS"
            },
            {
                "test_number": 2,
                "description": "shouting",
                "input": "WATCH OUT!",
                "expected_output": "Whoa, chill out!",
                "status": "PASS"
            },
            {
                "test_number": 3,
                "description": "forceful question",
                "input": "WHAT'S GOING ON?",
                "expected_output": "Calm down, I know what I'm doing!",
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
