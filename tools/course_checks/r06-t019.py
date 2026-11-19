#!/usr/bin/env python3
"""
Isolated Runner for Task R06-T019 (prime-factors exercise).
Validates reference solution in isolated temporary directories across standard,
failing reference, and empty test suite modes, verifying SHA256 integrity of learner files.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DIR = ROOT / "exercises/practice/prime-factors"
CONFIG_FILE = EXERCISE_DIR / ".meta/config.json"
EVIDENCE_DIR = ROOT / "work/R06-T019/evidence"


def get_file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def run_isolated(mode="standard"):
    exercise_rel = "exercises/practice/prime-factors"
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    stub_rel = cfg["files"]["solution"][0]
    test_rel = cfg["files"]["test"][0]
    example_rel = cfg["files"]["example"][0]

    working_stub = ROOT / exercise_rel / stub_rel
    hash_before = get_file_hash(working_stub)

    with tempfile.TemporaryDirectory(prefix=f"prime-factors-{mode}-") as tmpdir:
        def ignore_patterns(path, names):
            return [".git", "work"] if Path(path) == ROOT else []

        tmp_repo = Path(tmpdir) / "repo"
        shutil.copytree(ROOT, tmp_repo, ignore=ignore_patterns)

        tmp_exercise = tmp_repo / exercise_rel
        tmp_stub = tmp_exercise / stub_rel
        tmp_example = tmp_exercise / example_rel
        tmp_test = tmp_exercise / test_rel

        if mode == "standard":
            # Real reference against real tests
            pass
        elif mode == "failing-reference":
            # Deliberately failing reference
            tmp_example.write_text('BEGIN { print "forced failure" > "/dev/stderr"; exit 1 }\n', encoding="utf-8")
        elif mode == "empty-tests":
            # Empty test file with no @test cases
            tmp_test.write_text('#!/usr/bin/env bats\nload bats-extra\n', encoding="utf-8")
        else:
            raise ValueError(f"Unknown mode: {mode}")

        cmd = ["bin/validate_one_exercise", exercise_rel]
        proc = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)

        passed = len(re.findall(r"^ok\s+\d+", proc.stdout, re.MULTILINE))
        failed = len(re.findall(r"^not ok\s+\d+", proc.stdout, re.MULTILINE))
        total = passed + failed

    hash_after = get_file_hash(working_stub)
    if hash_before != hash_after:
        raise RuntimeError(f"Learner stub modified in mode '{mode}': hash changed from {hash_before} to {hash_after}")

    return proc.returncode, passed, failed, total, proc.stdout, proc.stderr, hash_before


def main():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    print("Running mode: standard...")
    rc_std, pass_std, fail_std, tot_std, out_std, err_std, sha_stub = run_isolated("standard")
    if rc_std != 0 or fail_std > 0 or tot_std != 12:
        print(f"Standard mode FAILED: rc={rc_std}, passed={pass_std}, failed={fail_std}, total={tot_std}", file=sys.stderr)
        sys.exit(1)
    print(f"Standard mode passed: {pass_std}/{tot_std} tests succeeded.")

    print("Running mode: failing-reference...")
    rc_fail, pass_fail, fail_fail, tot_fail, out_fail, err_fail, _ = run_isolated("failing-reference")
    if rc_fail == 0:
        print("Failing-reference mode FAILED: Expected non-zero return code, got 0!", file=sys.stderr)
        sys.exit(1)
    print(f"Failing-reference mode passed: cleanly failed with exit code {rc_fail} as expected.")

    print("Running mode: empty-tests...")
    rc_empty, pass_empty, fail_empty, tot_empty, out_empty, err_empty, _ = run_isolated("empty-tests")
    if rc_empty == 0 and tot_empty == 0:
        # Zero-test run must not be accepted as valid
        print("Empty-tests mode FAILED: Expected failure on zero-test run, but got exit code 0!", file=sys.stderr)
        sys.exit(1)
    print("Empty-tests mode passed: cleanly rejected zero-test run.")

    evidence_log = (
        "=== ISOLATED RUNNER VERIFICATION ===\n"
        f"Learner Stub SHA256 (Untouched): {sha_stub}\n\n"
        f"1. Standard Mode:          PASS (rc={rc_std}, passed={pass_std}, failed={fail_std})\n"
        f"2. Failing Reference Mode: PASS (rc={rc_fail}, failures detected as expected)\n"
        f"3. Empty Tests Mode:       PASS (rejected zero-test run as expected)\n\n"
        "Integrity: All working tree learner files preserved with identical cryptographic hashes.\n"
    )

    with open(EVIDENCE_DIR / "isolation-results.txt", "w", encoding="utf-8") as f:
        f.write(evidence_log)

    print("All isolation modes and hash checks succeeded cleanly.")


if __name__ == "__main__":
    main()
