#!/usr/bin/env python3
"""
Verification Script for Task R06-T013 (protein-translation exercise).
Validates reference implementation, tests the loop boundary mutant,
and asserts failure on the smallest rejecting case (Methionine RNA sequence).
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


def parse_tests_toml(toml_path: str):
    """Load and parse tests.toml returning cases dict and counts."""
    with open(toml_path, "rb") as f:
        toml_data = tomllib.load(f)

    included_cases = {}
    excluded_cases = {}

    for uuid, case in toml_data.items():
        desc = case.get("description", "")
        if case.get("include", True):
            included_cases[uuid] = desc
        else:
            excluded_cases[uuid] = desc

    return included_cases, excluded_cases


def extract_bats_test_cases(bats_path: str):
    """Extract test case names, inputs, expected results, and assertions from bats file."""
    with open(bats_path, "r", encoding="utf-8") as f:
        content = f.read()

    test_pattern = re.compile(
        r'@test\s+"([^"]+)"\s*\{\s*'
        r'(?:#?\s*\[\[\s*\$BATS_RUN_SKIPPED\s*==\s*"true"\s*\]\]\s*\|\|\s*skip\s*)?'
        r'run\s+gawk\s+-f\s+protein-translation\.awk\s+<<<\s*"([^"]*)"\s*'
        r'assert_(success|failure)\s*'
        r'(?:assert_output\s*"([^"]*)")?',
        re.MULTILINE
    )

    cases = []
    for match in test_pattern.finditer(content):
        desc = match.group(1).strip()
        inp = match.group(2)
        exp_status = match.group(3)
        exp_out = match.group(4) if match.group(4) is not None else ""
        cases.append({
            "description": desc,
            "input": inp,
            "expected_status": exp_status,
            "expected_output": exp_out
        })
    return cases


def parse_tap_output(stdout: str):
    """Parse TAP-like output from bats."""
    passed_tests = {}
    failed_tests = {}

    for line in stdout.splitlines():
        ok_match = re.match(r"^ok\s+(\d+)\s+(.*)$", line)
        if ok_match:
            num = int(ok_match.group(1))
            desc = ok_match.group(2).strip()
            passed_tests[num] = desc
            continue

        not_ok_match = re.match(r"^not ok\s+(\d+)\s+(.*)$", line)
        if not_ok_match:
            num = int(not_ok_match.group(1))
            desc = not_ok_match.group(2).strip()
            failed_tests[num] = desc
            continue

    total_executed = len(passed_tests) + len(failed_tests)
    return total_executed, passed_tests, failed_tests


def run_validation_in_temp_repo(repo_root: str, ex_rel_path: str, tmp_base_dir: str, mutate: bool = False):
    """
    Cleanly copy the repository (including dotfiles) to a temp directory,
    optionally apply the mutant, and run bin/validate_one_exercise.
    """
    def ignore_patterns(path, names):
        return [".git", "work"] if path == repo_root else []

    tmp_repo = os.path.join(tmp_base_dir, "repo")
    shutil.copytree(repo_root, tmp_repo, dirs_exist_ok=True, ignore=ignore_patterns, symlinks=True)

    config_path = os.path.join(tmp_repo, ex_rel_path, ".meta", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    example_rel = config["files"]["example"][0]
    example_path = os.path.join(tmp_repo, ex_rel_path, example_rel)

    if mutate:
        with open(example_path, "r", encoding="utf-8") as f:
            content = f.read()
        mutated_content = content.replace("for (i = 1; i <= NF; i++)", "for (i = 1; i < NF; i++)")
        if mutated_content == content:
            raise RuntimeError("Failed to apply mutant to example solution")
        with open(example_path, "w", encoding="utf-8") as f:
            f.write(mutated_content)

    cmd = ["bin/validate_one_exercise", ex_rel_path]
    result = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)
    return result, tmp_repo


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T013")
    os.makedirs(work_dir, exist_ok=True)

    ex_rel_path = os.path.join("exercises", "practice", "protein-translation")
    ex_full_path = os.path.join(repo_root, ex_rel_path)
    toml_path = os.path.join(ex_full_path, ".meta", "tests.toml")
    config_path = os.path.join(ex_full_path, ".meta", "config.json")

    # 1. Read config.json
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]
    bats_path = os.path.join(ex_full_path, test_rel)

    # 2. Assert learner stub is unchanged and unsolved
    stub_path = os.path.join(ex_full_path, solution_rel)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()
    if 'print "Implement this solution" > "/dev/stderr"' not in stub_content or "exit 1" not in stub_content:
        print("Check failed: Learner stub has been modified or solved!", file=sys.stderr)
        sys.exit(1)

    # 3. Parse tests.toml and extract bats test cases
    included_cases, excluded_cases = parse_tests_toml(toml_path)
    bats_cases = extract_bats_test_cases(bats_path)

    print(f"Loaded {len(included_cases)} included cases from tests.toml")
    print(f"Extracted {len(bats_cases)} test cases from {test_rel}")

    # Map UUIDs to test cases
    toml_uuids = list(included_cases.keys())
    combined_inputs = []
    for idx, case in enumerate(bats_cases):
        uuid = toml_uuids[idx] if idx < len(toml_uuids) else None
        combined_inputs.append({
            "index": idx + 1,
            "uuid": uuid,
            "description": case["description"],
            "input": case["input"],
            "expected_status": case["expected_status"],
            "expected_output": case["expected_output"]
        })

    with open(os.path.join(work_dir, "inputs_and_expected.json"), "w", encoding="utf-8") as f:
        json.dump(combined_inputs, f, indent=2)

    # 4. Gather tool versions
    bash_ver = subprocess.run(["bash", "--version"], capture_output=True, text=True).stdout.strip().splitlines()[0]
    awk_ver = subprocess.run(["awk", "--version"], capture_output=True, text=True).stdout.strip().splitlines()[0]
    bats_ver = subprocess.run(["bats", "--version"], capture_output=True, text=True).stdout.strip()
    py_ver = sys.version.replace("\n", " ")

    versions_content = (
        f"Bash Version:\n{bash_ver}\n\n"
        f"AWK Version:\n{awk_ver}\n\n"
        f"Bats Version:\n{bats_ver}\n\n"
        f"Python Version:\n{py_ver}\n"
    )
    with open(os.path.join(work_dir, "versions.txt"), "w", encoding="utf-8") as f:
        f.write(versions_content)

    # 5. Run validation against REFERENCE implementation
    print("\n--- Validating REFERENCE Implementation ---")
    with tempfile.TemporaryDirectory() as tmp_ref:
        ref_result, _ = run_validation_in_temp_repo(repo_root, ex_rel_path, tmp_ref, mutate=False)

    ref_total, ref_passed, ref_failed = parse_tap_output(ref_result.stdout)
    print(f"Reference Run -> Exit Code: {ref_result.returncode}, Total: {ref_total}, Passed: {len(ref_passed)}, Failed: {len(ref_failed)}")

    if ref_result.returncode != 0:
        print(f"Check failed: Reference implementation returned non-zero exit code ({ref_result.returncode})", file=sys.stderr)
        print(ref_result.stdout, file=sys.stderr)
        print(ref_result.stderr, file=sys.stderr)
        sys.exit(1)

    if ref_total == 0:
        print("Check failed: Reference run executed zero tests!", file=sys.stderr)
        sys.exit(1)

    if len(ref_failed) > 0:
        print(f"Check failed: Reference run failed {len(ref_failed)} tests!", file=sys.stderr)
        sys.exit(1)

    # 6. Run validation against MUTATED implementation
    print("\n--- Validating MUTATED Implementation ---")
    with tempfile.TemporaryDirectory() as tmp_mut:
        mut_result, _ = run_validation_in_temp_repo(repo_root, ex_rel_path, tmp_mut, mutate=True)

    mut_total, mut_passed, mut_failed = parse_tap_output(mut_result.stdout)
    print(f"Mutant Run -> Exit Code: {mut_result.returncode}, Total: {mut_total}, Passed: {len(mut_passed)}, Failed: {len(mut_failed)}")

    if mut_result.returncode == 0:
        print("Check failed: Mutant run unexpectedly exited with code 0!", file=sys.stderr)
        sys.exit(1)

    if mut_total == 0:
        print("Check failed: Mutant run executed zero tests!", file=sys.stderr)
        sys.exit(1)

    # Assert behavior around named cases
    # Case 1: Empty RNA sequence results in no proteins -> must pass
    if 1 not in mut_passed:
        print("Check failed: Case 1 ('Empty RNA sequence results in no proteins') failed under mutant!", file=sys.stderr)
        sys.exit(1)

    # Case 2: Methionine RNA sequence -> must fail the named assertion
    if 2 not in mut_failed:
        print("Check failed: Case 2 ('Methionine RNA sequence') did not fail under mutant!", file=sys.stderr)
        sys.exit(1)

    # Check for the specific failing assertion
    expected_assertion = 'assert_output "Methionine"'
    if expected_assertion not in mut_result.stdout:
        print(f"Check failed: Named assertion '{expected_assertion}' was not found in mutant failure output!", file=sys.stderr)
        sys.exit(1)

    print(f"Confirmed mutant failed named assertion: `{expected_assertion}`")

    # 7. Save output log
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: protein-translation\n"
        f"Task: R06-T013\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"TOML Included Cases: {len(included_cases)}\n"
        f"Reference Run Exit Code: {ref_result.returncode}\n"
        f"Reference Executed Tests: {ref_total} (Passed: {len(ref_passed)}, Failed: {len(ref_failed)})\n"
        f"Mutant Run Exit Code: {mut_result.returncode}\n"
        f"Mutant Executed Tests: {mut_total} (Passed: {len(mut_passed)}, Failed: {len(mut_failed)})\n"
        f"Smallest Rejecting Case: Methionine RNA sequence (Test #2, UUID: 96d3d44f-34a2-4db4-84cd-fff523e069be)\n"
        f"Failing Assertion: {expected_assertion}\n\n"
        f"=== REFERENCE RUN STDOUT/STDERR ===\n"
        f"{ref_result.stdout}\n{ref_result.stderr}\n\n"
        f"=== MUTANT RUN STDOUT/STDERR ===\n"
        f"{mut_result.stdout}\n{mut_result.stderr}\n"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    # 8. Save expected vs actual results
    case_reports = []
    for idx, case in enumerate(combined_inputs):
        num = case["index"]
        desc = case["description"]
        ref_st = "ok" if num in ref_passed else "not ok"
        mut_st = "ok" if num in mut_passed else "not ok"
        case_reports.append({
            "test_number": num,
            "uuid": case["uuid"],
            "description": desc,
            "input": case["input"],
            "expected_status": case["expected_status"],
            "expected_output": case["expected_output"],
            "reference_actual_status": ref_st,
            "mutant_actual_status": mut_st,
            "is_smallest_rejecting_case": (num == 2)
        })

    expected_vs_actual = {
        "exercise": "protein-translation",
        "task": "R06-T013",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "reference_run": {
            "exit_code": ref_result.returncode,
            "total": ref_total,
            "passed": len(ref_passed),
            "failed": len(ref_failed)
        },
        "mutant_run": {
            "exit_code": mut_result.returncode,
            "total": mut_total,
            "passed": len(mut_passed),
            "failed": len(mut_failed),
            "mutant_description": "Loop boundary mutation: for (i = 1; i <= NF; i++) -> for (i = 1; i < NF; i++)",
            "smallest_rejecting_case": {
                "test_number": 2,
                "uuid": "96d3d44f-34a2-4db4-84cd-fff523e069be",
                "description": "Methionine RNA sequence",
                "input": "AUG",
                "expected_output": "Methionine",
                "actual_output": "",
                "failing_assertion": expected_assertion
            }
        },
        "cases": case_reports
    }

    with open(os.path.join(work_dir, "expected_vs_actual.json"), "w", encoding="utf-8") as f:
        json.dump(expected_vs_actual, f, indent=2)

    print("\n--- All Verification Checks Succeeded Cleanly ---")
    print(f"Outputs successfully generated in: {work_dir}")


if __name__ == "__main__":
    main()
