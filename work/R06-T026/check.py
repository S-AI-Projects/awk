#!/usr/bin/env python3
"""
R06-T026 check.py
=================
Validates the grains exercise and compares the reference implementation
with an independently written alternative:

  1. Resolves paths from exercises/practice/grains/.meta/config.json.
  2. Copies exercise including dotfiles to a temp directory, substitutes
     the reference in that copy, and validates tests.
  3. Executes: bin/validate_one_exercise exercises/practice/grains.
  4. Verifies learner stub remains unsolved (exits 1).
  5. Asserts the named cases:
     - "grains on square 1"
     - "grains on square 2"
     - "grains on square 3"
  6. Evaluates an independently written alternative implementation
     (precomputed lookup table / doubling simulation) across all 11 cases.
  7. Asserts 100% agreement between reference and alternative implementations.
  8. Records tool versions, inputs, expected vs actual results, and assertions.

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
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "grains"
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = Path(__file__).resolve().parent

EXPECTED_TEST_COUNT = 11

NAMED_CASES = [
    {"name": "grains on square 1", "input": "1\n", "expected": "1", "expected_rc": 0},
    {"name": "grains on square 2", "input": "2\n", "expected": "2", "expected_rc": 0},
    {"name": "grains on square 3", "input": "3\n", "expected": "4", "expected_rc": 0},
]

# Genuinely different alternative implementation:
# Uses array memoization / precomputed lookup table instead of closed-form exponentiation.
ALTERNATIVE_AWK = """\
BEGIN {
    board[1] = 1
    sum = 1
    for (i = 2; i <= 64; i++) {
        board[i] = board[i - 1] * 2
        sum += board[i]
    }
    board["total"] = sum
}

$1 == "total" {
    print board["total"]
    next
}

$1 < 1 || $1 > 64 {
    print "square must be between 1 and 64" > "/dev/stderr"
    exit 1
}

{
    print board[$1]
}
"""

ALL_TEST_CASES = [
    {"name": "grains on square 1", "input": "1\n", "expected": "1", "expected_rc": 0, "needs_m": False},
    {"name": "grains on square 2", "input": "2\n", "expected": "2", "expected_rc": 0, "needs_m": False},
    {"name": "grains on square 3", "input": "3\n", "expected": "4", "expected_rc": 0, "needs_m": False},
    {"name": "grains on square 4", "input": "4\n", "expected": "8", "expected_rc": 0, "needs_m": False},
    {"name": "grains on square 16", "input": "16\n", "expected": "32768", "expected_rc": 0, "needs_m": False},
    {"name": "grains on square 32", "input": "32\n", "expected": "2147483648", "expected_rc": 0, "needs_m": False},
    {"name": "grains on square 64", "input": "64\n", "expected": "9223372036854775808", "expected_rc": 0, "needs_m": False},
    {"name": "square 0 is invalid", "input": "0\n", "expected": "square must be between 1 and 64", "expected_rc": 1, "needs_m": False},
    {"name": "negative square is invalid", "input": "-1\n", "expected": "square must be between 1 and 64", "expected_rc": 1, "needs_m": False},
    {"name": "square greater than 64 is invalid", "input": "65\n", "expected": "square must be between 1 and 64", "expected_rc": 1, "needs_m": False},
    {"name": "returns the total number of grains on the board", "input": "total\n", "expected": "18446744073709551615", "expected_rc": 0, "needs_m": True},
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


def main() -> None:
    print("=" * 60)
    print("R06-T026 grains comparison check")
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
    stub_run = run_cmd(["gawk", "-f", str(solution_src)], input_text="1\n")
    stub_unsolved = stub_run.returncode != 0 and "Implement this solution" in (stub_run.stderr + stub_run.stdout)
    print(f"\n[stub] unsolved and fails with expected message: {stub_unsolved}")

    # 4. Copy exercise including dotfiles to a temporary directory and test there
    with tempfile.TemporaryDirectory() as td:
        temp_exercise = Path(td) / "grains"
        shutil.copytree(EXERCISE_DIR, temp_exercise)
        shutil.copy2(temp_exercise / example_rel, temp_exercise / solution_rel)

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

    print(f"\n[run] bin/validate_one_exercise exercises/practice/grains")
    val_run = run_cmd([str(validate_script), str(EXERCISE_DIR)], cwd=str(REPO_ROOT))
    child_rc = val_run.returncode
    tests_run_count = count_bats_output_tests(val_run.stdout)

    # 6. Verify named cases explicitly on reference
    named_cases_verification = {}
    for nc in NAMED_CASES:
        r = run_cmd(["gawk", "-f", str(example_src)], input_text=nc["input"])
        actual = r.stdout.strip()
        passed = (r.returncode == nc["expected_rc"] and actual == nc["expected"])
        named_cases_verification[nc["name"]] = {
            "input": nc["input"].strip(),
            "expected": nc["expected"],
            "actual": actual,
            "pass": passed,
        }
        print(f"  [named case: reference] {nc['name']}: {'PASS' if passed else 'FAIL'}")

    # 7. Test Alternative Implementation across all cases and compare with reference
    comparison_results = []
    alternative_all_pass = True
    implementations_agree = True

    with tempfile.TemporaryDirectory() as td:
        alt_path = Path(td) / "alt.awk"
        alt_path.write_text(ALTERNATIVE_AWK)

        for case in ALL_TEST_CASES:
            cmd_ref = ["gawk", "-M", "-f", str(example_src)] if case["needs_m"] else ["gawk", "-f", str(example_src)]
            cmd_alt = ["gawk", "-M", "-f", str(alt_path)] if case["needs_m"] else ["gawk", "-f", str(alt_path)]

            r_ref = run_cmd(cmd_ref, input_text=case["input"])
            r_alt = run_cmd(cmd_alt, input_text=case["input"])

            ref_out = (r_ref.stdout if case["expected_rc"] == 0 else r_ref.stderr).strip()
            alt_out = (r_alt.stdout if case["expected_rc"] == 0 else r_alt.stderr).strip()

            ref_pass = (r_ref.returncode == case["expected_rc"] and ref_out == case["expected"])
            alt_pass = (r_alt.returncode == case["expected_rc"] and alt_out == case["expected"])
            agree = (r_ref.returncode == r_alt.returncode and ref_out == alt_out)

            if not alt_pass:
                alternative_all_pass = False
            if not agree:
                implementations_agree = False

            comparison_results.append({
                "case": case["name"],
                "input": case["input"].strip(),
                "expected": case["expected"],
                "ref_output": ref_out,
                "alt_output": alt_out,
                "ref_rc": r_ref.returncode,
                "alt_rc": r_alt.returncode,
                "alt_pass": alt_pass,
                "agree": agree,
            })

    # Also run BATS on alternative in temp directory
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        shutil.copy2(test_src, temp_dir / test_rel)
        shutil.copy2(EXERCISE_DIR / "bats-extra.bash", temp_dir / "bats-extra.bash")
        (temp_dir / solution_rel).write_text(ALTERNATIVE_AWK)

        alt_bats = run_cmd(
            ["bats", test_rel],
            cwd=str(temp_dir),
            env=dict(os.environ, BATS_RUN_SKIPPED="true"),
        )
        alt_bats_pass = alt_bats.returncode == 0
        alt_bats_tests = count_bats_output_tests(alt_bats.stdout)

    print(f"\n[alternative] BATS full suite run: {'PASS' if alt_bats_pass else 'FAIL'} ({alt_bats_tests} tests)")

    # 8. Record everything
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
        "named_cases_reference": named_cases_verification,
        "alternative_evaluation": {
            "all_cases_pass": alternative_all_pass,
            "agree_with_reference": implementations_agree,
            "bats_suite_pass": alt_bats_pass,
            "bats_tests_counted": alt_bats_tests,
            "case_comparisons": comparison_results,
        },
        "assertions": {},
    }

    # 9. Assertions
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

    print("\n[assertions — named cases on reference]")
    for name, data in named_cases_verification.items():
        assert_eq(f"ref_named_case: {name}", True, data["pass"])

    print("\n[assertions — alternative implementation comparison]")
    assert_eq("alt_all_cases_passed", True, alternative_all_pass)
    assert_eq("alt_bats_suite_passed", True, alt_bats_pass)
    assert_eq("alt_bats_tests_counted", EXPECTED_TEST_COUNT, alt_bats_tests)
    assert_eq("implementations_agree_on_all_cases", True, implementations_agree)

    # 10. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 11. Summary
    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
