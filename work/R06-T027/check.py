#!/usr/bin/env python3
"""
R06-T027 check.py
=================
Validates the collatz-conjecture exercise and asserts micro-examples of AWK numeric coercion:

  1. Resolves paths from exercises/practice/collatz-conjecture/.meta/config.json.
  2. Copies exercise including dotfiles to a tempdir, substitutes reference,
     and validates tests.
  3. Executes: bin/validate_one_exercise exercises/practice/collatz-conjecture.
  4. Verifies learner stub remains unsolved (exits 1).
  5. Asserts the named cases:
     - "zero steps for one" (1 -> 0)
     - "divide if even" (16 -> 4)
     - "even and odd steps" (12 -> 9)
  6. Evaluates and asserts the two micro-examples for numeric coercion and the pitfall:
     - Micro-example 1 (numeric coercion): val = "10"; print (val + 0 < 2) -> "0"
     - Micro-example 2 (string comparison pitfall): val = "10"; print (val < 2) -> "1"
  7. Records all data in work/R06-T027/run_record.json.

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
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "collatz-conjecture"
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = Path(__file__).resolve().parent

EXPECTED_TEST_COUNT = 6

NAMED_CASES = [
    {"name": "zero steps for one", "input": "1\n", "expected": "0", "expected_rc": 0},
    {"name": "divide if even", "input": "16\n", "expected": "4", "expected_rc": 0},
    {"name": "even and odd steps", "input": "12\n", "expected": "9", "expected_rc": 0},
]

# Micro-examples demonstrating the construct and pitfall
SNIPPET_COERCED = 'BEGIN { val = "10"; print (val + 0 < 2) }'
SNIPPET_PITFALL = 'BEGIN { val = "10"; print (val < 2) }'


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
    print("R06-T027 collatz-conjecture numeric coercion check")
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
        temp_exercise = Path(td) / "collatz-conjecture"
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

    print(f"\n[run] bin/validate_one_exercise exercises/practice/collatz-conjecture")
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

    # 7. Evaluate micro-examples of numeric coercion and pitfall
    r_coerced = run_cmd(["gawk", SNIPPET_COERCED])
    r_pitfall = run_cmd(["gawk", SNIPPET_PITFALL])

    out_coerced = r_coerced.stdout.strip()
    out_pitfall = r_pitfall.stdout.strip()

    pass_coerced = (r_coerced.returncode == 0 and out_coerced == "0")
    pass_pitfall = (r_pitfall.returncode == 0 and out_pitfall == "1")

    print(f"\n[micro-examples]")
    print(f"  Micro-example 1 (numeric coercion `(val + 0 < 2)`): got {out_coerced!r} (expected '0') -> {'PASS' if pass_coerced else 'FAIL'}")
    print(f"  Micro-example 2 (string pitfall    `(val < 2)`):     got {out_pitfall!r} (expected '1') -> {'PASS' if pass_pitfall else 'FAIL'}")

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
        "language_construct": {
            "name": "numeric coercion",
            "examined_constructs": ["record/field splitting", "numeric coercion", "associative-array traversal"],
            "selected_construct": "numeric coercion",
            "presence_in_reference": "Used in $1 < 1, n = $1, while (n > 1), and n % 2 == 0.",
            "micro_example_coerced": {
                "snippet": SNIPPET_COERCED,
                "output": out_coerced,
                "expected": "0",
                "pass": pass_coerced,
            },
            "micro_example_pitfall": {
                "snippet": SNIPPET_PITFALL,
                "output": out_pitfall,
                "expected": "1",
                "pass": pass_pitfall,
            },
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

    print("\n[assertions — micro-examples]")
    assert_eq("micro_example_coerced_output_0", "0", out_coerced)
    assert_eq("micro_example_pitfall_output_1", "1", out_pitfall)
    assert_eq("micro_examples_differ", True, out_coerced != out_pitfall)

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
