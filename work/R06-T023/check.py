#!/usr/bin/env python3
"""
R06-T023 check.py
=================
Validates the ocr-numbers exercise:

  1. Copies the exercise to a temp dir with the reference (example) solution
     and runs: bin/validate_one_exercise exercises/practice/ocr-numbers
     → asserts child exits zero and 18 tests run

  2. Runs the ORIGINAL reference against the three named inputs and asserts
     correct output (Recognizes 0 → "0"; Recognizes 1 → "1"; Unreadable → "?")

  3. Creates the MUTANT (corrupted digit-1 lookup key), runs it against the
     same input, and asserts it FAILS (returns "?" instead of "1")

  4. Confirms the existing "Recognizes 1" test rejects the mutant

Exit codes:
  0  all assertions pass
  1  one or more assertions failed
  2  setup / invocation error

Mutation description
--------------------
The mutation changes the lookup key for digit "1" in the BEGIN block:

  ORIGINAL:  digit["     |  |"] = "1"   (5 spaces, pipe, 2 spaces, pipe)
  MUTANT:    digit["    |   |"] = "1"   (4 spaces, pipe, 3 spaces, pipe)

The key is assembled from three FPAT=".." fields across rows 1-3 of the
4-line input group.  With the wrong key, the digit "1" pattern is never
found in the lookup table, so the reference returns "?" for every "1" cell.

This is a semantic mutation (wrong boundary in pattern recognition), not a
formatting change.  The existing test "Recognizes 1" rejects it immediately.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

# Ensure Homebrew binaries are on PATH
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
EXERCISE     = "ocr-numbers"
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / EXERCISE
CONFIG_JSON  = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR     = Path(__file__).resolve().parent

EXPECTED_ENABLED_CASES = 18

# The 9-character lookup keys: 3 chars per row × 3 rows
DIGIT_1_ORIGINAL_KEY = "     |  |"   # correct: 5sp + | + 2sp + |
DIGIT_1_MUTANT_KEY   = "    |   |"   # wrong:   4sp + | + 3sp + |

# Named test inputs (each is a 4-line block; 4th line is blank row)
INPUT_0 = " _ \n| |\n|_|\n   \n"
INPUT_1 = "   \n  |\n  |\n   \n"
INPUT_Q = "   \n  _\n  |\n   \n"   # unreadable but correctly sized

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def die(msg: str, code: int = 2) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd, input_text=None, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True,
        input=input_text, **kwargs
    )


def tool_version(cmd: list) -> str:
    r = run(cmd)
    return (r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else "(unavailable)"


def count_bats_tests(bats_path: Path) -> int:
    text = bats_path.read_text()
    return len(re.findall(r'^@test\s+', text, re.MULTILINE))


def count_bats_output_tests(output: str) -> int:
    m = re.search(r'^1\.\.(\d+)', output, re.MULTILINE)
    if m:
        return int(m.group(1))
    return len(re.findall(r'^(?:ok|not ok)\s+\d+', output, re.MULTILINE))


def run_gawk(awk_file: Path, input_text: str) -> subprocess.CompletedProcess:
    return run(["gawk", "-f", str(awk_file)], input_text=input_text)


def make_mutant(original: Path, dest: Path) -> None:
    """Write a mutated copy: corrupt the digit-1 lookup key."""
    text = original.read_text()
    mutated = text.replace(
        f'digit["{DIGIT_1_ORIGINAL_KEY}"] = "1"',
        f'digit["{DIGIT_1_MUTANT_KEY}"] = "1"',
    )
    if mutated == text:
        die(f"Mutation pattern not found in {original} — check key string")
    dest.write_text(mutated)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("R06-T023 ocr-numbers check")
    print("=" * 60)

    # 1. Resolve paths from config.json
    if not CONFIG_JSON.is_file():
        die(f"config.json not found: {CONFIG_JSON}")
    config = json.loads(CONFIG_JSON.read_text())
    solution_rel = config["files"]["solution"][0]
    test_rel     = config["files"]["test"][0]
    example_rel  = (config["files"].get("example") or config["files"].get("exemplar"))[0]

    solution_src = EXERCISE_DIR / solution_rel
    test_src     = EXERCISE_DIR / test_rel
    example_src  = EXERCISE_DIR / example_rel

    for p in (solution_src, test_src, example_src):
        if not p.is_file():
            die(f"Required file missing: {p}")

    # 2. Tool versions
    gawk_ver = tool_version(["gawk", "--version"])
    bats_ver = tool_version(["bats", "--version"])
    jq_ver   = tool_version(["jq",   "--version"])
    py_ver   = tool_version([sys.executable, "--version"])
    print(f"\n[versions]")
    print(f"  gawk   : {gawk_ver}")
    print(f"  bats   : {bats_ver}")
    print(f"  jq     : {jq_ver}")
    print(f"  python : {py_ver}")
    print(f"\n[info] @test blocks: {count_bats_tests(test_src)}")

    # 3. Run validate_one_exercise (reference substituted)
    validate_script = REPO_ROOT / "bin" / "validate_one_exercise"
    if not validate_script.is_file():
        die(f"validate_one_exercise not found: {validate_script}")

    print(f"\n[run] bin/validate_one_exercise exercises/practice/{EXERCISE}")
    vresult  = run([str(validate_script), str(EXERCISE_DIR)], cwd=str(REPO_ROOT))
    child_rc = vresult.returncode
    tests_run = count_bats_output_tests(vresult.stdout)

    # 4. Create mutant in a temp dir
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        mutant_path = td / "mutant.awk"
        make_mutant(example_src, mutant_path)

        # 5. Run original and mutant against named inputs
        orig_0 = run_gawk(example_src, INPUT_0)
        orig_1 = run_gawk(example_src, INPUT_1)
        orig_q = run_gawk(example_src, INPUT_Q)

        mut_0  = run_gawk(mutant_path, INPUT_0)
        mut_1  = run_gawk(mutant_path, INPUT_1)
        mut_q  = run_gawk(mutant_path, INPUT_Q)

        # 6. Run full bats suite against mutant to find rejecting tests
        tmpdir2 = td / "bats_mutant"
        tmpdir2.mkdir()
        shutil.copy(mutant_path, tmpdir2 / solution_rel)
        shutil.copy(test_src,    tmpdir2 / test_rel)
        shutil.copy(EXERCISE_DIR / "bats-extra.bash", tmpdir2 / "bats-extra.bash")
        bats_mutant = run(
            ["bats", test_rel],
            cwd=str(tmpdir2),
            input_text=None,
        )
        # Override env for skip
        import os as _os
        env = dict(_os.environ)
        env["BATS_RUN_SKIPPED"] = "true"
        bats_mutant = subprocess.run(
            ["bats", test_rel],
            cwd=str(tmpdir2),
            capture_output=True, text=True,
            env=env,
        )
        mutant_failures = re.findall(r'^not ok \d+ (.+)', bats_mutant.stdout, re.MULTILINE)

    # 7. Record
    record = {
        "tool_versions": {"gawk": gawk_ver, "bats": bats_ver, "jq": jq_ver, "python": py_ver},
        "enabled_cases": {"in_bats_file": count_bats_tests(test_src), "expected": EXPECTED_ENABLED_CASES},
        "validate_run": {"returncode": child_rc, "tests_counted": tests_run,
                         "stdout": vresult.stdout, "stderr": vresult.stderr},
        "mutation": {
            "description": "Corrupt digit-1 lookup key: change 5-space prefix to 4-space",
            "original_key": DIGIT_1_ORIGINAL_KEY,
            "mutant_key":   DIGIT_1_MUTANT_KEY,
            "original_key_repr": repr(DIGIT_1_ORIGINAL_KEY),
            "mutant_key_repr":   repr(DIGIT_1_MUTANT_KEY),
            "diff": f'< digit["{DIGIT_1_ORIGINAL_KEY}"] = "1"\n> digit["{DIGIT_1_MUTANT_KEY}"] = "1"',
        },
        "named_cases": {
            "Recognizes 0": {
                "input": INPUT_0,
                "original_output": orig_0.stdout.strip(), "original_rc": orig_0.returncode,
                "mutant_output":   mut_0.stdout.strip(),  "mutant_rc":   mut_0.returncode,
            },
            "Recognizes 1": {
                "input": INPUT_1,
                "original_output": orig_1.stdout.strip(), "original_rc": orig_1.returncode,
                "mutant_output":   mut_1.stdout.strip(),  "mutant_rc":   mut_1.returncode,
            },
            "Unreadable but correctly sized inputs return ?": {
                "input": INPUT_Q,
                "original_output": orig_q.stdout.strip(), "original_rc": orig_q.returncode,
                "mutant_output":   mut_q.stdout.strip(),  "mutant_rc":   mut_q.returncode,
            },
        },
        "mutant_rejecting_tests": mutant_failures,
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

    print("\n[assertions — reference suite]")
    assert_eq("child_returncode_is_zero",   0,                       child_rc)
    assert_eq("bats_test_count",            EXPECTED_ENABLED_CASES,  count_bats_tests(test_src))
    assert_eq("tests_run_nonzero",          True,                    tests_run > 0)
    assert_eq("tests_run_count",            EXPECTED_ENABLED_CASES,  tests_run)

    print("\n[assertions — named cases: original]")
    assert_eq("orig_recognizes_0",          "0",   orig_0.stdout.strip())
    assert_eq("orig_recognizes_1",          "1",   orig_1.stdout.strip())
    assert_eq("orig_unreadable_returns_?",  "?",   orig_q.stdout.strip())

    print("\n[assertions — named cases: mutant]")
    assert_eq("mutant_digit0_unchanged",    "0",   mut_0.stdout.strip())
    assert_eq("mutant_digit1_now_?",        "?",   mut_1.stdout.strip())   # key failure
    assert_eq("mutant_unreadable_still_?",  "?",   mut_q.stdout.strip())

    print("\n[assertions — mutation semantics]")
    assert_eq("mutant_differs_from_original_on_1",
              True, orig_1.stdout.strip() != mut_1.stdout.strip())
    assert_eq("recognizes_1_rejects_mutant",
              True, "Recognizes 1" in mutant_failures)

    # 9. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 10. Summary
    if vresult.stdout:
        print("\n[bats stdout]")
        print(vresult.stdout)
    if mutant_failures:
        print(f"\n[mutant] Rejecting tests ({len(mutant_failures)}): {mutant_failures}")

    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
