#!/usr/bin/env python3
"""
Verification Script for Task R06-T012 (tournament exercise).
Validates test execution, anchor test cases, and determinism across temporary environments.
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
import tomllib


def parse_tests_toml(toml_path: str):
    """Load and parse tests.toml returning cases dict and counts."""
    with open(toml_path, "rb") as f:
        toml_data = tomllib.load(f)
    
    included_cases = {}
    excluded_cases = {}
    
    for uuid, case in toml_data.items():
        desc = case.get("description", "")
        # Omitted include key implies inclusion per Exercism specification
        if case.get("include", True):
            included_cases[uuid] = desc
        else:
            excluded_cases[uuid] = desc
            
    return included_cases, excluded_cases


def extract_bats_test_cases(bats_path: str):
    """Extract test case names, inputs, and expected outputs from bats file."""
    with open(bats_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Matches @test "description" blocks
    test_pattern = re.compile(
        r'@test\s+"([^"]+)"\s*\{\s*'
        r'(?:#?\[\[[^\]]+\]\]\s*\|\|\s*skip\s*)?'
        r'input="(.*?)"\s*'
        r'expected="(.*?)"\s*'
        r'assert_in_to_out',
        re.DOTALL
    )
    
    cases = []
    for match in test_pattern.finditer(content):
        desc = match.group(1).strip()
        inp = match.group(2)
        # Normalize backslash-escaped newlines in input/expected
        inp_clean = inp.replace("\\\n", "")
        exp = match.group(3)
        exp_clean = exp.replace("\\\n", "")
        cases.append({
            "description": desc,
            "input": inp_clean,
            "expected_output": exp_clean
        })
    return cases


def run_validation_in_temp_repo(repo_root: str, ex_rel_path: str, tmp_base_dir: str):
    """Cleanly copy the repo to a temp directory and run bin/validate_one_exercise."""
    def ignore_patterns(path, names):
        return [".git", "work"] if path == repo_root else []

    tmp_repo = os.path.join(tmp_base_dir, "repo")
    shutil.copytree(repo_root, tmp_repo, ignore=ignore_patterns, symlinks=True)

    cmd = ["bin/validate_one_exercise", ex_rel_path]
    result = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)
    return result, tmp_repo


def normalize_bats_for_diff(content: str) -> list[str]:
    """Strip dynamic timestamps and trailing whitespace for determinism comparison."""
    lines = []
    for line in content.splitlines():
        if "generated on" in line:
            continue
        lines.append(line.rstrip())
    return lines


def verify_determinism(repo_root: str, ex_rel_path: str, test_rel_path: str):
    """Run test generation / execution check in two independent copies to verify determinism."""
    print("Executing determinism verification across two isolated temporary environments...")
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        res1, repo1 = run_validation_in_temp_repo(repo_root, ex_rel_path, tmp1)
        res2, repo2 = run_validation_in_temp_repo(repo_root, ex_rel_path, tmp2)

        file1 = os.path.join(repo1, ex_rel_path, test_rel_path)
        file2 = os.path.join(repo2, ex_rel_path, test_rel_path)

        with open(file1, "r", encoding="utf-8") as f:
            lines1 = normalize_bats_for_diff(f.read())
        with open(file2, "r", encoding="utf-8") as f:
            lines2 = normalize_bats_for_diff(f.read())

        diff = list(difflib.unified_diff(lines1, lines2, lineterm=""))
        if diff:
            print("Determinism check failed: bats files differ between runs!", file=sys.stderr)
            for line in diff:
                print(line, file=sys.stderr)
            return False, None, None

        if res1.stdout != res2.stdout or res1.returncode != res2.returncode:
            print("Determinism check failed: validator outputs differ between runs!", file=sys.stderr)
            return False, res1, res2

        print("Determinism check passed: runs in independent temporary copies produced identical output.")
        return True, res1, res2


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T012")
    os.makedirs(work_dir, exist_ok=True)

    ex_rel_path = os.path.join("exercises", "practice", "tournament")
    ex_full_path = os.path.join(repo_root, ex_rel_path)
    toml_path = os.path.join(ex_full_path, ".meta", "tests.toml")
    config_path = os.path.join(ex_full_path, ".meta", "config.json")

    # 1. Read configuration from config.json
    if not os.path.exists(config_path):
        print(f"Error: Missing config file at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]

    # Verify learner stub file remains strictly untouched
    stub_path = os.path.join(ex_full_path, solution_rel)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read().strip()
    if "Implement this solution" not in stub_content:
        print("Check failed: Learner stub file tournament.awk has been modified!", file=sys.stderr)
        sys.exit(1)

    # 2. Parse tests.toml
    included_cases, excluded_cases = parse_tests_toml(toml_path)
    print(f"tests.toml: {len(included_cases)} included cases, {len(excluded_cases)} excluded cases")

    # 3. Extract test cases metadata from test-tournament.bats
    bats_full_path = os.path.join(ex_full_path, test_rel)
    extracted_bats_cases = extract_bats_test_cases(bats_full_path)

    with open(os.path.join(work_dir, "inputs_and_expected.json"), "w", encoding="utf-8") as f:
        json.dump(extracted_bats_cases, f, indent=2)

    # 4. Verify test determinism across two fresh temporary copies
    det_ok, res1, res2 = verify_determinism(repo_root, ex_rel_path, test_rel)
    if not det_ok:
        sys.exit(1)

    # 5. Execute validation run cleanly in temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        result, tmp_repo = run_validation_in_temp_repo(repo_root, ex_rel_path, tmp_dir)

    print("Validator execution finished with returncode:", result.returncode)

    # 6. Parse TAP test execution results
    passed_matches = re.findall(r"^ok\s+(\d+)\s+(.+)$", result.stdout, re.MULTILINE)
    failed_matches = re.findall(r"^not ok\s+(\d+)\s+(.+)$", result.stdout, re.MULTILINE)

    passed_tests = {int(num): desc.strip() for num, desc in passed_matches}
    failed_tests = {int(num): desc.strip() for num, desc in failed_matches}
    total_executed = len(passed_tests) + len(failed_tests)

    print(f"Executed: {total_executed}, Passed: {len(passed_tests)}, Failed: {len(failed_tests)}")

    # 7. Check specific anchor test cases
    # Anchors:
    # 1. Just the header if no input.
    # 2. A win is three points, a loss is zero points.
    # 3. A win can also be expressed as a loss.
    required_anchors = [
        "just the header if no input",
        "a win is three points, a loss is zero points",
        "a win can also be expressed as a loss"
    ]

    anchor_status = {}
    passed_descs_norm = {desc.lower().strip("."): (num, desc) for num, desc in passed_tests.items()}

    for anchor in required_anchors:
        norm_key = anchor.lower().strip(".")
        if norm_key in passed_descs_norm:
            tnum, orig_desc = passed_descs_norm[norm_key]
            anchor_status[anchor] = {
                "verified": True,
                "test_number": tnum,
                "description": orig_desc,
                "status": "PASSED"
            }
        else:
            anchor_status[anchor] = {
                "verified": False,
                "status": "FAILED_OR_MISSING"
            }

    # 8. Collect tool versions
    awk_ver = subprocess.run(["awk", "--version"], capture_output=True, text=True).stdout.strip()
    bats_ver = subprocess.run(["bats", "--version"], capture_output=True, text=True).stdout.strip()
    py_ver = sys.version.replace("\n", " ")

    with open(os.path.join(work_dir, "versions.txt"), "w", encoding="utf-8") as f:
        f.write(f"AWK Version:\n{awk_ver}\n\nBATS Version:\n{bats_ver}\n\nPython Version:\n{py_ver}\n")

    # 9. Save execution output summary
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: tournament\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"TOML Included Cases: {len(included_cases)}\n"
        f"TOML Excluded Cases: {len(excluded_cases)}\n"
        f"Executed Test Cases: {total_executed}\n"
        f"Passed: {len(passed_tests)}, Failed: {len(failed_tests)}\n"
        f"Determinism Check: {'PASSED' if det_ok else 'FAILED'}\n\n"
        f"=== ANCHOR VERIFICATION ===\n"
    )
    for anchor, st in anchor_status.items():
        output_log += f"- {anchor}: {st['status']} (Test #{st.get('test_number', 'N/A')})\n"

    output_log += (
        f"\n=== VALIDATOR STDOUT/STDERR ===\n"
        f"{result.stdout}\n{result.stderr}"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_log)

    # 10. Save expected vs actual results
    # Match UUIDs from tests.toml with executed tests
    test_cases_report = []
    # In tournament, order in bats matches order in tests.toml
    toml_items = list(included_cases.items())
    for idx, (num, desc) in enumerate(passed_tests.items()):
        uuid = toml_items[idx][0] if idx < len(toml_items) else None
        is_anchor = any(anchor.lower().strip(".") == desc.lower().strip(".") for anchor in required_anchors)
        test_cases_report.append({
            "test_number": num,
            "uuid": uuid,
            "description": desc,
            "is_anchor": is_anchor,
            "expected_status": "ok",
            "actual_status": "ok",
            "passed": True
        })

    for num, desc in failed_tests.items():
        test_cases_report.append({
            "test_number": num,
            "description": desc,
            "expected_status": "ok",
            "actual_status": "not ok",
            "passed": False
        })

    expected_vs_actual = {
        "exercise": "tournament",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_cases": total_executed,
        "passed_cases": len(passed_tests),
        "failed_cases": len(failed_tests),
        "anchors": anchor_status,
        "cases": test_cases_report
    }

    with open(os.path.join(work_dir, "expected_vs_actual.json"), "w", encoding="utf-8") as f:
        json.dump(expected_vs_actual, f, indent=2)

    # 11. Assertions
    if result.returncode != 0:
        print(f"Check failed: Validator exited with code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    if total_executed == 0:
        print("Check failed: Zero test cases were executed.", file=sys.stderr)
        sys.exit(1)

    if len(failed_tests) > 0:
        print(f"Check failed: {len(failed_tests)} test cases failed.", file=sys.stderr)
        sys.exit(1)

    if total_executed != len(included_cases):
        print(f"Check failed: Executed test count ({total_executed}) does not match included TOML cases ({len(included_cases)}).", file=sys.stderr)
        sys.exit(1)

    for anchor, st in anchor_status.items():
        if not st.get("verified"):
            print(f"Check failed: Required anchor test case '{anchor}' was not verified as passed!", file=sys.stderr)
            sys.exit(1)

    print(f"Check passed! All {total_executed} cases passed cleanly against reference implementation.")
    print("All key anchor test cases verified successfully:")
    for anchor in required_anchors:
        print(f"  [PASS] {anchor}")


if __name__ == "__main__":
    main()
