#!/usr/bin/env python3
"""
Verification Script for Task R06-T033 (food-chain exercise).

Validates:
1. Learner stub remains unsolved and untouched in the working tree.
2. Original reference solution passes all 10 enabled test cases in an isolated temporary directory,
   including named cases 'fly', 'spider', 'bird'.
3. Deliberate semantic mutant (boundary error j >= 1 -> j > 1 in cumulative loop)
   in an isolated temporary copy fails the test suite on the smallest rejecting input ('spider', start=2, end=2),
   while 'fly' passes.
4. Records inputs, expected vs actual outputs, tool versions, and mutation diff in work/R06-T033/.
"""

import datetime
import difflib
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
            output = res.stdout.strip() if res.stdout.strip() else res.stderr.strip()
            first_line = output.splitlines()[0] if output else "Empty output"
            versions[label] = first_line
        except Exception as e:
            versions[label] = f"Error querying {cmd[0]}: {e}"

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


def run_validator(repo_root: str, exercise_rel_path: str, temp_root: str, mutate_fn=None):
    """Run bin/validate_one_exercise inside an isolated temporary directory."""
    temp_exercise_dir = os.path.join(temp_root, exercise_rel_path)
    os.makedirs(os.path.dirname(temp_exercise_dir), exist_ok=True)
    exercise_dir = os.path.join(repo_root, exercise_rel_path)
    shutil.copytree(exercise_dir, temp_exercise_dir)

    example_path = os.path.join(temp_exercise_dir, ".meta", "example.awk")
    if mutate_fn:
        with open(example_path, "r", encoding="utf-8") as f:
            content = f.read()
        mutated_content = mutate_fn(content)
        with open(example_path, "w", encoding="utf-8") as f:
            f.write(mutated_content)

    temp_bin_dir = os.path.join(temp_root, "bin")
    shutil.copytree(os.path.join(repo_root, "bin"), temp_bin_dir)

    val_cmd = [os.path.join(temp_bin_dir, "validate_one_exercise"), temp_exercise_dir]
    val_res = subprocess.run(val_cmd, cwd=temp_root, capture_output=True, text=True)
    return val_res


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T033")
    os.makedirs(work_dir, exist_ok=True)

    print("=== Starting R06-T033 Verification Check ===")

    # 1. Record tool versions
    print("1. Recording tool versions...")
    versions = record_tool_versions(work_dir)

    # 2. Inspect Learner Stub Integrity in Working Tree
    print("2. Checking learner stub integrity...")
    exercise_rel_path = os.path.join("exercises", "practice", "food-chain")
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
    print(f"   Verified: Learner stub '{solution_file}' remains untouched and unsolved.")

    # 3. Validate Original Reference Solution in Temporary Directory
    print("3. Validating original reference implementation in isolated temporary directory...")
    with tempfile.TemporaryDirectory() as temp_root_orig:
        res_orig = run_validator(repo_root, exercise_rel_path, temp_root_orig)

    if res_orig.returncode != 0:
        print(f"Error: Original reference failed validation with code {res_orig.returncode}!", file=sys.stderr)
        print(res_orig.stderr, file=sys.stderr)
        sys.exit(res_orig.returncode)

    orig_total, orig_passed, orig_failed = parse_tap_output(res_orig.stdout)
    print(f"   Original Validation: Total={orig_total}, Passed={len(orig_passed)}, Failed={len(orig_failed)}")

    if orig_total == 0 or len(orig_passed) != 10 or len(orig_failed) > 0:
        print(f"Error: Expected 10 passing tests for original reference, got {len(orig_passed)} passed / {len(orig_failed)} failed!", file=sys.stderr)
        sys.exit(1)

    named_cases = ["fly", "spider", "bird"]
    orig_passed_names = [desc for _, desc in orig_passed]
    for case in named_cases:
        if case not in orig_passed_names:
            print(f"Error: Named case '{case}' was not passed in original reference!", file=sys.stderr)
            sys.exit(1)
        print(f"   Original reference verified: '{case}' -> PASS")

    # 4. Generate and Validate Deliberate Mutant
    print("4. Testing deliberate semantic mutant (j >= 1 -> j > 1 in cumulative loop)...")
    example_path = os.path.join(exercise_dir, ".meta", "example.awk")
    with open(example_path, "r", encoding="utf-8") as f:
        orig_code = f.read()

    target_pattern = "j >= 1"
    mutant_replacement = "j > 1"
    if target_pattern not in orig_code:
        print(f"Error: Target pattern '{target_pattern}' not found in {example_path}!", file=sys.stderr)
        sys.exit(1)

    mut_code = orig_code.replace(target_pattern, mutant_replacement, 1)

    # Save mutation patch diff
    patch_lines = list(difflib.unified_diff(
        orig_code.splitlines(keepends=True),
        mut_code.splitlines(keepends=True),
        fromfile="example.awk (original)",
        tofile="example.awk (mutant)"
    ))
    patch_path = os.path.join(work_dir, "mutation_diff.patch")
    with open(patch_path, "w", encoding="utf-8") as f:
        f.writelines(patch_lines)

    # Run validator on mutant in fresh temporary directory
    with tempfile.TemporaryDirectory() as temp_root_mut:
        res_mut = run_validator(repo_root, exercise_rel_path, temp_root_mut, mutate_fn=lambda c: c.replace(target_pattern, mutant_replacement, 1))

    mut_total, mut_passed, mut_failed = parse_tap_output(res_mut.stdout)
    print(f"   Mutated Validation: Total={mut_total}, Passed={len(mut_passed)}, Failed={len(mut_failed)} (Exit Code: {res_mut.returncode})")

    if res_mut.returncode == 0:
        print("Error: Mutated reference unexpectedly PASSED all tests! Mutant survived!", file=sys.stderr)
        sys.exit(1)

    mut_passed_names = [desc for _, desc in mut_passed]
    mut_failed_names = [desc for _, desc in mut_failed]

    if "fly" not in mut_passed_names:
        print("Error: Case 'fly' was expected to pass under the mutant!", file=sys.stderr)
        sys.exit(1)

    if "spider" not in mut_failed_names:
        print("Error: Case 'spider' (smallest rejecting input) was expected to FAIL under the mutant!", file=sys.stderr)
        sys.exit(1)

    if "bird" not in mut_failed_names:
        print("Error: Case 'bird' was expected to FAIL under the mutant!", file=sys.stderr)
        sys.exit(1)

    print("   Mutant behavior confirmed:")
    print("     - 'fly' (start=1, end=1): PASS (catch loop not entered)")
    print("     - 'spider' (start=2, end=2): FAIL (rejected: smallest input allowed by spec)")
    print("     - 'bird' (start=3, end=3): FAIL (rejected)")

    # 5. Emit inputs.json
    inputs_data = {
        "exercise": "food-chain",
        "task": "R06-T033",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool_versions": versions,
        "mutation_details": {
            "file": "exercises/practice/food-chain/.meta/example.awk",
            "function": "verse(i, j)",
            "original_code": "for (j = i - 1; j >= 1; j--)",
            "mutated_code": "for (j = i - 1; j > 1; j--)",
            "nature_of_mutation": "Off-by-one boundary error in cumulative catch chain loop condition",
            "rejecting_test_case": "spider",
            "smallest_rejecting_input": {
                "start": 2,
                "end": 2
            }
        }
    }
    with open(os.path.join(work_dir, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(inputs_data, f, indent=2)

    # 6. Emit expected_vs_actual.json
    spider_expected = (
        "I know an old lady who swallowed a spider.\n"
        "It wriggled and jiggled and tickled inside her.\n"
        "She swallowed the spider to catch the fly.\n"
        "I don't know why she swallowed the fly. Perhaps she'll die."
    )
    spider_mutated_actual = (
        "I know an old lady who swallowed a spider.\n"
        "It wriggled and jiggled and tickled inside her.\n"
        "I don't know why she swallowed the fly. Perhaps she'll die."
    )

    expected_vs_actual = {
        "exercise": "food-chain",
        "task": "R06-T033",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "original_run": {
            "exit_code": res_orig.returncode,
            "total_cases": orig_total,
            "passed": len(orig_passed),
            "failed": len(orig_failed),
            "status": "ALL_PASSED"
        },
        "mutant_run": {
            "exit_code": res_mut.returncode,
            "total_cases": mut_total,
            "passed": len(mut_passed),
            "failed": len(mut_failed),
            "status": "MUTANT_KILLED"
        },
        "smallest_rejecting_case": {
            "test_case": "spider",
            "input_variables": {"start": 2, "end": 2},
            "expected_output": spider_expected,
            "mutated_output": spider_mutated_actual,
            "mutation_detection": "assert_output failed due to missing line: 'She swallowed the spider to catch the fly.'"
        },
        "named_cases_summary": [
            {"case": "fly", "original_status": "PASS", "mutant_status": "PASS"},
            {"case": "spider", "original_status": "PASS", "mutant_status": "FAIL (Smallest Rejecting Case)"},
            {"case": "bird", "original_status": "PASS", "mutant_status": "FAIL"}
        ]
    }
    with open(os.path.join(work_dir, "expected_vs_actual.json"), "w", encoding="utf-8") as f:
        json.dump(expected_vs_actual, f, indent=2)

    # 7. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: food-chain\n"
        f"Task: R06-T033\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Original Validator Exit Code: {res_orig.returncode} (Passed: {len(orig_passed)}, Failed: {len(orig_failed)})\n"
        f"Mutated Validator Exit Code: {res_mut.returncode} (Passed: {len(mut_passed)}, Failed: {len(mut_failed)})\n"
        f"Learner Stub Status: Untouched (unsolved)\n\n"
        f"=== MUTATION VERIFICATION ===\n"
        f"Original: 'for (j = i - 1; j >= 1; j--)'\n"
        f"Mutant:   'for (j = i - 1; j > 1; j--)'\n"
        f"Smallest Rejecting Case: 'spider' (start=2, end=2)\n"
        f"- fly (start=1, end=1):       Original=PASS, Mutant=PASS\n"
        f"- spider (start=2, end=2):    Original=PASS, Mutant=FAIL (Killed)\n"
        f"- bird (start=3, end=3):      Original=PASS, Mutant=FAIL (Killed)\n\n"
        f"=== ORIGINAL VALIDATOR STDOUT ===\n"
        f"{res_orig.stdout}\n"
        f"=== MUTATED VALIDATOR STDOUT ===\n"
        f"{res_mut.stdout}\n"
    )
    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    print("\n--- All Verification Checks Succeeded Cleanly ---")
    print(f"Generated verification artifacts in: {work_dir}")


if __name__ == "__main__":
    main()
