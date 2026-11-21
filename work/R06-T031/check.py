#!/usr/bin/env python3
"""
Verification Script for Task R06-T031 (largest-series-product exercise).

Validates:
1. Canonical case entries in exercises/practice/largest-series-product/.meta/tests.toml:
   - 18 total canonical cases
   - 13 included, 5 excluded
   - Rationales provided for UUIDs 5d81aaf7-4f67-4125-bf33-11493cc7eab7,
     06bc8b90-0c51-4c54-ac22-3ec3893a079e, and 3ec0d92e-f2e2-4090-a380-70afee02f4c0
     citing AWK operations and distinguishing replacement cases from unsupported behavior.
2. Learner stub remains unsolved and untouched.
3. Isolated execution of bin/validate_one_exercise in a temporary directory with the reference
   solution substituted only in that copy.
4. Named baseline cases and all enabled cases pass cleanly against the reference.
5. Verification artifacts generated in work/R06-T031/.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None


def parse_toml(file_path: str) -> dict:
    """Parse TOML using tomllib/tomli if available, or fallback regex parser."""
    if tomllib is not None:
        with open(file_path, "rb") as f:
            return tomllib.load(f)

    # Fallback basic TOML parser for table-based tests.toml
    data = {}
    current_section = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            section_match = re.match(r"^\[([a-zA-Z0-9_-]+)\]$", line)
            if section_match:
                current_section = section_match.group(1)
                data[current_section] = {}
                continue
            if current_section and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                if val.lower() == "true":
                    data[current_section][key] = True
                elif val.lower() == "false":
                    data[current_section][key] = False
                elif val.startswith('"') and val.endswith('"'):
                    data[current_section][key] = val[1:-1]
                else:
                    data[current_section][key] = val
    return data


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


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R06-T031")
    inputs_dir = os.path.join(work_dir, "inputs")
    os.makedirs(inputs_dir, exist_ok=True)

    print("=== Starting R06-T031 Verification Check ===")

    # 1. Query & Record Tool Versions
    print("1. Recording tool versions...")
    versions = record_tool_versions(work_dir)

    # 2. Inspect Learner Stub Integrity in Working Tree
    print("2. Checking learner stub integrity...")
    exercise_rel_path = os.path.join("exercises", "practice", "largest-series-product")
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
    print(f"   Verified: Learner stub '{solution_file}' remains untouched and unsolved.")

    # 3. Review canonical cases & rationales in tests.toml
    print("3. Reviewing tests.toml configuration...")
    toml_path = os.path.join(exercise_dir, ".meta", "tests.toml")
    shutil.copy2(toml_path, os.path.join(inputs_dir, "tests.toml"))

    toml_data = parse_toml(toml_path)
    total_canonical = len(toml_data)
    excluded_cases = [uuid for uuid, entry in toml_data.items() if not entry.get("include", True)]
    included_cases = [uuid for uuid, entry in toml_data.items() if entry.get("include", True)]

    print(f"   Canonical Cases Count: Total={total_canonical}, Included={len(included_cases)}, Excluded={len(excluded_cases)}")

    if total_canonical != 18:
        print(f"Error: Expected 18 canonical cases in tests.toml, found {total_canonical}!", file=sys.stderr)
        sys.exit(1)

    if len(included_cases) != 13 or len(excluded_cases) != 5:
        print(f"Error: Expected 13 included and 5 excluded cases, found {len(included_cases)} inc, {len(excluded_cases)} exc!", file=sys.stderr)
        sys.exit(1)

    target_uuids = {
        "5d81aaf7-4f67-4125-bf33-11493cc7eab7": {
            "name": "rejects span longer than string length",
            "type": "replacement",
            "required_kw": ["Replacement", "0ae1ce53-d9ba-41bb-827f-2fceb64f058b"]
        },
        "06bc8b90-0c51-4c54-ac22-3ec3893a079e": {
            "name": "reports 1 for empty string and empty product (0 span)",
            "type": "unsupported",
            "required_kw": ["Unsupported", "FS"]
        },
        "3ec0d92e-f2e2-4090-a380-70afee02f4c0": {
            "name": "reports 1 for nonempty string and empty product (0 span)",
            "type": "unsupported",
            "required_kw": ["Unsupported", "substr"]
        }
    }

    rationales = {}
    for uuid, meta in target_uuids.items():
        if uuid not in toml_data:
            print(f"Error: Target UUID {uuid} missing from tests.toml!", file=sys.stderr)
            sys.exit(1)
        entry = toml_data[uuid]
        if entry.get("include", True):
            print(f"Error: Target UUID {uuid} should have include = false!", file=sys.stderr)
            sys.exit(1)
        comment = entry.get("comment", "")
        if not comment:
            print(f"Error: Target UUID {uuid} is missing a rationale comment!", file=sys.stderr)
            sys.exit(1)
        for kw in meta["required_kw"]:
            if kw not in comment:
                print(f"Error: Target UUID {uuid} rationale missing keyword '{kw}'!", file=sys.stderr)
                sys.exit(1)
        rationales[uuid] = {
            "description": entry.get("description", meta["name"]),
            "include": entry.get("include", True),
            "category": meta["type"],
            "comment": comment
        }
        print(f"   Target UUID Verified: {uuid} ({meta['type'].title()}): {comment[:70]}...")

    # Save inputs summary
    inputs_summary = {
        "exercise": "largest-series-product",
        "task": "R06-T031",
        "total_canonical_cases": total_canonical,
        "included_count": len(included_cases),
        "excluded_count": len(excluded_cases),
        "target_rationales": rationales,
        "tool_versions": versions
    }
    with open(os.path.join(work_dir, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(inputs_summary, f, indent=2)

    # 4. Execute bin/validate_one_exercise inside Temporary Directory
    print("4. Executing bin/validate_one_exercise in isolated temporary directory...")
    with tempfile.TemporaryDirectory() as temp_root:
        temp_exercise_dir = os.path.join(temp_root, "exercises", "practice", "largest-series-product")
        os.makedirs(os.path.dirname(temp_exercise_dir), exist_ok=True)
        # Copy exercise directory including dotfiles
        shutil.copytree(exercise_dir, temp_exercise_dir)

        # Substitute reference solution ONLY in temporary copy
        src_example = os.path.join(temp_exercise_dir, example_file)
        dst_solution = os.path.join(temp_exercise_dir, solution_file)
        shutil.copy2(src_example, dst_solution)

        # Copy bin directory
        temp_bin_dir = os.path.join(temp_root, "bin")
        shutil.copytree(os.path.join(repo_root, "bin"), temp_bin_dir)

        val_cmd = [os.path.join(temp_bin_dir, "validate_one_exercise"), temp_exercise_dir]
        val_res = subprocess.run(val_cmd, cwd=temp_root, capture_output=True, text=True)

    if val_res.returncode != 0:
        print(f"Error: Validator returned non-zero exit code {val_res.returncode}!", file=sys.stderr)
        print(val_res.stderr, file=sys.stderr)
        sys.exit(val_res.returncode)

    total_tests, passed_tests, failed_tests = parse_tap_output(val_res.stdout)
    print(f"   Validation summary: Total={total_tests}, Passed={len(passed_tests)}, Failed={len(failed_tests)}")

    if total_tests == 0 or len(passed_tests) == 0:
        print("Error: Zero test cases were executed!", file=sys.stderr)
        sys.exit(1)

    if len(failed_tests) > 0 or total_tests != 13:
        print(f"Error: Expected 13 passing tests, but found {len(failed_tests)} failures / total {total_tests}!", file=sys.stderr)
        sys.exit(1)

    # 5. Verify Named Baseline Cases
    print("5. Verifying named baseline cases...")
    named_cases = [
        (1, "finds the largest product if span equals length", "29,2", "18"),
        (2, "can find the largest product of 2 with numbers in order", "0123456789,2", "72"),
        (3, "can find the largest product of 2", "576802143,2", "48")
    ]

    passed_dict = dict(passed_tests)
    for test_idx, case_name, exp_in, exp_out in named_cases:
        if test_idx not in passed_dict or passed_dict[test_idx] != case_name:
            print(f"Error: Named case #{test_idx} ('{case_name}') was not reported as passed!", file=sys.stderr)
            sys.exit(1)
        print(f"   Named Case #{test_idx} PASS: '{case_name}' [Input: '{exp_in}' -> Expected: '{exp_out}']")

    # 6. Emit output.txt
    output_log = (
        f"=== EXECUTION SUMMARY ===\n"
        f"Exercise: largest-series-product\n"
        f"Task: R06-T031\n"
        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        f"Validator Exit Code: {val_res.returncode}\n"
        f"TOML Canonical Cases: {total_canonical} (Included: {len(included_cases)}, Excluded: {len(excluded_cases)})\n"
        f"Tests Executed: {total_tests} (Passed: {len(passed_tests)}, Failed: {len(failed_tests)})\n"
        f"Learner Stub Status: Untouched (unsolved)\n\n"
        f"=== NAMED BASELINE CASES ===\n"
        f"1. finds the largest product if span equals length: PASS (Output: '18')\n"
        f"2. can find the largest product of 2 with numbers in order: PASS (Output: '72')\n"
        f"3. can find the largest product of 2: PASS (Output: '48')\n\n"
        f"=== TARGET UUID RATIONALES ===\n"
        f"- 5d81aaf7-4f67-4125-bf33-11493cc7eab7: {rationales['5d81aaf7-4f67-4125-bf33-11493cc7eab7']['comment']}\n"
        f"- 06bc8b90-0c51-4c54-ac22-3ec3893a079e: {rationales['06bc8b90-0c51-4c54-ac22-3ec3893a079e']['comment']}\n"
        f"- 3ec0d92e-f2e2-4090-a380-70afee02f4c0: {rationales['3ec0d92e-f2e2-4090-a380-70afee02f4c0']['comment']}\n\n"
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
            "status": "PASS",
            "is_named_baseline_case": num in [1, 2, 3]
        })

    expected_vs_actual = {
        "exercise": "largest-series-product",
        "task": "R06-T031",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validator_run": {
            "exit_code": val_res.returncode,
            "total_cases": total_tests,
            "passed_cases": len(passed_tests),
            "failed_cases": len(failed_tests)
        },
        "toml_metrics": {
            "total_canonical": total_canonical,
            "included": len(included_cases),
            "excluded": len(excluded_cases)
        },
        "target_rationales": rationales,
        "named_baseline_cases": [
            {
                "test_number": 1,
                "description": "finds the largest product if span equals length",
                "input": "29,2",
                "expected_output": "18",
                "status": "PASS"
            },
            {
                "test_number": 2,
                "description": "can find the largest product of 2 with numbers in order",
                "input": "0123456789,2",
                "expected_output": "72",
                "status": "PASS"
            },
            {
                "test_number": 3,
                "description": "can find the largest product of 2",
                "input": "576802143,2",
                "expected_output": "48",
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
