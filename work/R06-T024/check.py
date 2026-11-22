#!/usr/bin/env python3
"""
R06-T024 check.py
=================
Validates the line-up exercise reference implementation refactoring:

  1. Resolves paths from exercises/practice/line-up/.meta/config.json.
  2. Copies the exercise including dotfiles to a temporary directory,
     substitutes the reference only in that copy, and runs validation.
  3. Executes: bin/validate_one_exercise exercises/practice/line-up.
  4. Verifies learner stub remains unsolved (exits 1).
  5. Verifies before vs after agreement on all 25 test cases, focusing on:
     - format smallest non-exceptional ordinal numeral 4
     - format greatest single digit non-exceptional ordinal numeral 9
     - format non-exceptional ordinal numeral 5
  6. Records tool versions, inputs, expected vs actual results, and assertions.

Exit codes:
  0  all assertions pass
  1  one or more assertions failed
  2  setup / invocation error
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure Homebrew tools are on PATH
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "line-up"
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = Path(__file__).resolve().parent

EXPECTED_TEST_COUNT = 25

# Original implementation (prior to refactoring) for before/after comparison
ORIGINAL_AWK = """\
{
    print $1 ", you are the " $2 suffix($2) " customer we serve today. Thank you!"
}

function suffix(number) {
    if (number ~ /(1[123]|[^123])$/) return "th"
    else if (number ~ /1$/) return "st"
    else if (number ~ /2$/) return "nd"
    else return "rd"
}
"""

NAMED_CASES = [
    {
        "name": "format smallest non-exceptional ordinal numeral 4",
        "input": "Gianna 4\n",
        "expected": "Gianna, you are the 4th customer we serve today. Thank you!",
    },
    {
        "name": "format greatest single digit non-exceptional ordinal numeral 9",
        "input": "Maarten 9\n",
        "expected": "Maarten, you are the 9th customer we serve today. Thank you!",
    },
    {
        "name": "format non-exceptional ordinal numeral 5",
        "input": "Petronila 5\n",
        "expected": "Petronila, you are the 5th customer we serve today. Thank you!",
    },
]


def die(msg: str, code: int = 2) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def run_cmd(cmd, input_text=None, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_text,
        **kwargs,
    )


def tool_version(cmd: list) -> str:
    r = run_cmd(cmd)
    out = (r.stdout + r.stderr).strip()
    return out.splitlines()[0] if out else "(unavailable)"


def count_bats_tests(bats_path: Path) -> int:
    text = bats_path.read_text()
    return len(re.findall(r"^@test\s+", text, re.MULTILINE))


def count_bats_output_tests(output: str) -> int:
    m = re.search(r"^1\.\.(\d+)", output, re.MULTILINE)
    if m:
        return int(m.group(1))
    return len(re.findall(r"^(?:ok|not ok)\s+\d+", output, re.MULTILINE))


def extract_all_test_cases(bats_path: Path) -> list:
    """Extract all test inputs and expected outputs from the BATS file."""
    text = bats_path.read_text()
    cases = []
    pattern = re.compile(
        r'@test\s+"([^"]+)"\s*\{[^}]*?run gawk -f line-up\.awk <<< "([^"]+)"[^}]*?assert_output "([^"]+)"',
        re.DOTALL,
    )
    for m in pattern.finditer(text):
        cases.append({
            "name": m.group(1),
            "input": m.group(2) + "\n",
            "expected": m.group(3),
        })
    return cases


def main() -> None:
    print("=" * 60)
    print("R06-T024 line-up refactoring check")
    print("=" * 60)

    # 1. Resolve configuration
    if not CONFIG_JSON.is_file():
        die(f"config.json not found: {CONFIG_JSON}")
    config = json.loads(CONFIG_JSON.read_text())
    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = (config["files"].get("example") or config["files"].get("exemplar"))[0]

    solution_src = EXERCISE_DIR / solution_rel
    test_src = EXERCISE_DIR / test_rel
    example_src = EXERCISE_DIR / example_rel

    for p in (solution_src, test_src, example_src):
        if not p.is_file():
            die(f"Required file missing: {p}")

    # 2. Collect tool versions
    gawk_ver = tool_version(["gawk", "--version"])
    bats_ver = tool_version(["bats", "--version"])
    jq_ver = tool_version(["jq", "--version"])
    py_ver = tool_version([sys.executable, "--version"])
    print("\n[versions]")
    print(f"  gawk   : {gawk_ver}")
    print(f"  bats   : {bats_ver}")
    print(f"  jq     : {jq_ver}")
    print(f"  python : {py_ver}")

    # 3. Check learner stub is unsolved
    stub_run = run_cmd(["gawk", "-f", str(solution_src)], input_text="Gianna 4\n")
    stub_unsolved = stub_run.returncode != 0 and "Implement this solution" in (stub_run.stderr + stub_run.stdout)
    print(f"\n[stub] unsolved and fails with expected message: {stub_unsolved}")

    # 4. Copy exercise including dotfiles to a temporary directory and test there
    with tempfile.TemporaryDirectory() as td:
        temp_exercise = Path(td) / "line-up"
        shutil.copytree(EXERCISE_DIR, temp_exercise)
        # Substitute reference into stub in temp copy only
        shutil.copy2(temp_exercise / example_rel, temp_exercise / solution_rel)

        # Run bats directly inside temporary copy
        temp_bats = run_cmd(
            ["bats", test_rel],
            cwd=str(temp_exercise),
            env=dict(os.environ, BATS_RUN_SKIPPED="true"),
        )
        temp_bats_tests = count_bats_output_tests(temp_bats.stdout)
        temp_bats_ok = temp_bats.returncode == 0

    # 5. Run bin/validate_one_exercise
    validate_script = REPO_ROOT / "bin" / "validate_one_exercise"
    if not validate_script.is_file():
        die(f"validate_one_exercise not found: {validate_script}")

    print(f"\n[run] bin/validate_one_exercise exercises/practice/line-up")
    val_run = run_cmd([str(validate_script), str(EXERCISE_DIR)], cwd=str(REPO_ROOT))
    child_rc = val_run.returncode
    tests_run_count = count_bats_output_tests(val_run.stdout)

    # 6. Extract test cases and compare original vs refactored AWK
    all_cases = extract_all_test_cases(test_src)
    print(f"\n[extracted] {len(all_cases)} test cases from {test_rel}")

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        orig_awk_file = td_path / "orig.awk"
        orig_awk_file.write_text(ORIGINAL_AWK)

        case_results = []
        all_cases_match = True

        for c in all_cases:
            res_orig = run_cmd(["gawk", "-f", str(orig_awk_file)], input_text=c["input"])
            res_new = run_cmd(["gawk", "-f", str(example_src)], input_text=c["input"])

            orig_out = res_orig.stdout.strip()
            new_out = res_new.stdout.strip()
            expected = c["expected"]

            agrees = (orig_out == new_out == expected)
            if not agrees:
                all_cases_match = False

            case_results.append({
                "name": c["name"],
                "input": c["input"].strip(),
                "expected": expected,
                "original_output": orig_out,
                "refactored_output": new_out,
                "pass": agrees,
            })

    # Specifically check the three named baseline cases
    named_results = {}
    for nc in NAMED_CASES:
        res = run_cmd(["gawk", "-f", str(example_src)], input_text=nc["input"])
        actual = res.stdout.strip()
        matches = actual == nc["expected"]
        named_results[nc["name"]] = {
            "input": nc["input"].strip(),
            "expected": nc["expected"],
            "actual": actual,
            "pass": matches,
        }

    # 7. Record
    record = {
        "tool_versions": {"gawk": gawk_ver, "bats": bats_ver, "jq": jq_ver, "python": py_ver},
        "enabled_cases": {"expected": EXPECTED_TEST_COUNT, "counted_in_bats": count_bats_tests(test_src)},
        "validate_run": {
            "returncode": child_rc,
            "tests_counted": tests_run_count,
            "stdout": val_run.stdout,
            "stderr": val_run.stderr,
        },
        "temporary_copy_test": {
            "returncode": temp_bats.returncode,
            "tests_counted": temp_bats_tests,
            "pass": temp_bats_ok,
        },
        "learner_stub_unsolved": stub_unsolved,
        "named_cases": named_results,
        "all_cases_agreement": all_cases_match,
        "assertions": {},
    }

    # 8. Assertions
    failures = []

    def assert_eq(name: str, expected, actual) -> None:
        ok = expected == actual
        record["assertions"][name] = {"expected": expected, "actual": actual, "pass": ok}
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}: expected={expected!r}, actual={actual!r}")
        if not ok:
            failures.append(name)

    print("\n[assertions — reference validation]")
    assert_eq("child_returncode_is_zero", 0, child_rc)
    assert_eq("bats_test_count", EXPECTED_TEST_COUNT, count_bats_tests(test_src))
    assert_eq("tests_run_nonzero", True, tests_run_count > 0)
    assert_eq("tests_run_count", EXPECTED_TEST_COUNT, tests_run_count)
    assert_eq("temp_copy_tests_passed", True, temp_bats_ok)
    assert_eq("learner_stub_unsolved", True, stub_unsolved)

    print("\n[assertions — named baseline cases]")
    for nc in NAMED_CASES:
        assert_eq(f"baseline: {nc['name']}", True, named_results[nc["name"]]["pass"])

    print("\n[assertions — before/after equivalence]")
    assert_eq("all_cases_before_after_agree", True, all_cases_match)

    # 9. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 10. Summary
    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
