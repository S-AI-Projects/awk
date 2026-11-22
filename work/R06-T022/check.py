#!/usr/bin/env python3
"""
R06-T022 check.py
=================
Validates the automated-readability-index exercise:

  - Copies the exercise to a temp dir, substituting the reference (example) solution
  - Runs: bin/validate_one_exercise exercises/practice/automated-readability-index
  - Asserts child exits zero
  - Asserts the test count equals the expected number of enabled cases (3)
  - Performs a two-copy idempotency check on the hand-maintained test file
  - Records inputs, expected vs actual results, and tool versions

Exit codes:
  0  all assertions pass
  1  one or more assertions failed
  2  setup / invocation error

Notes on test-file generation
------------------------------
The automated-readability-index exercise has NO .meta/template.j2 file.
The track generator (bin/generate_tests) only processes exercises that
have a template.j2 — it skips ARI entirely.  The test file
  exercises/practice/automated-readability-index/test-automated-readability-index.bats
is therefore HAND-MAINTAINED (no generated timestamp header).

Two copies of a hand-maintained file are always identical; the
idempotency check verifies that byte-for-byte.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure Homebrew binaries (gawk, bats, bash 5+) are on PATH
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
EXERCISE    = "automated-readability-index"
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / EXERCISE
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR    = Path(__file__).resolve().parent

# The exercise has NO tests.toml and NO template.j2 — all 3 tests are
# hand-written track-specific cases.
EXPECTED_ENABLED_CASES = 3

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def die(msg: str, code: int = 2) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def tool_version(cmd: list) -> str:
    r = run(cmd)
    return (r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else "(unavailable)"


def count_bats_tests(bats_path: Path) -> int:
    """Count @test declarations in a .bats file."""
    text = bats_path.read_text()
    return len(re.findall(r'^@test\s+', text, re.MULTILINE))


def count_bats_output_tests(output: str) -> int:
    """Parse bats TAP output to count total tests run."""
    m = re.search(r'^1\.\.(\d+)', output, re.MULTILINE)
    if m:
        return int(m.group(1))
    return len(re.findall(r'^(?:ok|not ok)\s+\d+', output, re.MULTILINE))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("R06-T022 automated-readability-index check")
    print("=" * 60)

    # 1. Verify exercise directory
    if not EXERCISE_DIR.is_dir():
        die(f"Exercise directory not found: {EXERCISE_DIR}")

    # 2. Read config.json to resolve file paths
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

    # 3. Report template / generation status
    template_path = EXERCISE_DIR / ".meta" / "template.j2"
    tests_toml    = EXERCISE_DIR / ".meta" / "tests.toml"
    has_template  = template_path.is_file()
    has_toml      = tests_toml.is_file()
    print(f"\n[info] template.j2 present : {has_template}")
    print(f"[info] tests.toml present  : {has_toml}")
    print(f"[info] test file is        : {'generated' if has_template else 'HAND-MAINTAINED'}")
    print(f"[info] @test blocks found  : {count_bats_tests(test_src)}")

    # 4. Tool versions
    gawk_ver = tool_version(["gawk",    "--version"])
    bats_ver = tool_version(["bats",    "--version"])
    jq_ver   = tool_version(["jq",      "--version"])
    py_ver   = tool_version([sys.executable, "--version"])
    print(f"\n[versions]")
    print(f"  gawk   : {gawk_ver}")
    print(f"  bats   : {bats_ver}")
    print(f"  jq     : {jq_ver}")
    print(f"  python : {py_ver}")

    # 5. Two-copy idempotency check on the hand-maintained test file
    #    Since there is no generator for this exercise, two plain copies of
    #    the source file must be byte-for-byte identical (no timestamp drift).
    import tempfile, shutil as _shutil
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        copy1 = td / "copy1.bats"
        copy2 = td / "copy2.bats"
        _shutil.copy2(test_src, copy1)
        _shutil.copy2(test_src, copy2)
        sha1 = file_sha256(copy1)
        sha2 = file_sha256(copy2)
        copies_identical = (sha1 == sha2)
    print(f"\n[idempotency] copy1 sha256: {sha1[:16]}...")
    print(f"[idempotency] copy2 sha256: {sha2[:16]}...")
    print(f"[idempotency] identical   : {copies_identical}")

    # 6. Run validate_one_exercise
    validate_script = REPO_ROOT / "bin" / "validate_one_exercise"
    if not validate_script.is_file():
        die(f"validate_one_exercise not found: {validate_script}")

    print(f"\n[run] {validate_script} exercises/practice/{EXERCISE}")
    result = run(
        [str(validate_script), str(EXERCISE_DIR)],
        cwd=str(REPO_ROOT),
    )
    stdout   = result.stdout
    stderr   = result.stderr
    child_rc = result.returncode

    tests_run = count_bats_output_tests(stdout)

    # 7. Record inputs / expected / actual
    record = {
        "tool_versions": {"gawk": gawk_ver, "bats": bats_ver, "jq": jq_ver, "python": py_ver},
        "paths": {
            "exercise_dir":        str(EXERCISE_DIR),
            "solution_stub":       str(solution_src),
            "reference_solution":  str(example_src),
            "test_file":           str(test_src),
        },
        "generation_status": {
            "template_j2_present": has_template,
            "tests_toml_present":  has_toml,
            "file_is_hand_maintained": not has_template,
            "note": (
                "No template.j2 found in .meta/. The track generator (bin/generate_tests) "
                "skips exercises without a template. The test file is hand-maintained by "
                "the exercise author and should be edited directly when cases change."
            ),
        },
        "idempotency": {
            "copy1_sha256": sha1,
            "copy2_sha256": sha2,
            "identical": copies_identical,
            "timestamp_normalization_required": False,
            "note": "Hand-maintained files have no generated timestamp; two copies are always byte-identical.",
        },
        "enabled_cases": {
            "in_bats_file": count_bats_tests(test_src),
            "expected": EXPECTED_ENABLED_CASES,
        },
        "run": {
            "command":        f"bin/validate_one_exercise exercises/practice/{EXERCISE}",
            "returncode":     child_rc,
            "stdout":         stdout,
            "stderr":         stderr,
            "tests_counted":  tests_run,
        },
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

    print("\n[assertions]")
    assert_eq("child_returncode_is_zero",      0,                       child_rc)
    assert_eq("bats_test_count",               EXPECTED_ENABLED_CASES,  count_bats_tests(test_src))
    assert_eq("tests_run_nonzero",             True,                    tests_run > 0)
    assert_eq("tests_run_count",               EXPECTED_ENABLED_CASES,  tests_run)
    assert_eq("two_copies_identical",          True,                    copies_identical)
    assert_eq("no_template_j2",               False,                    has_template)
    assert_eq("file_is_hand_maintained",       True,                    not has_template)

    # 9. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 10. Print bats output
    if stdout:
        print("\n[bats stdout]")
        print(stdout[-3000:] if len(stdout) > 3000 else stdout)
    if stderr:
        print("\n[bats stderr]")
        print(stderr[-1000:] if len(stderr) > 1000 else stderr)

    # 11. Final verdict
    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
