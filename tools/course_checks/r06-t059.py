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
EXERCISE_DIR = ROOT / "exercises/practice/isogram"
CONFIG_FILE = EXERCISE_DIR / ".meta/config.json"
EVIDENCE_DIR = ROOT / "work/R06-T059/evidence"

def get_file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_isolated(mode="standard"):
    exercise_rel = "exercises/practice/isogram"
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    stub_rel = cfg["files"]["solution"][0]
    test_rel = cfg["files"]["test"][0]
    example_rel = cfg["files"]["example"][0]

    working_stub = ROOT / exercise_rel / stub_rel
    hash_before = get_file_hash(working_stub)

    with tempfile.TemporaryDirectory(prefix=f"isogram-{mode}-") as tmpdir:
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
    rc_std, p_std, f_std, tot_std, out_std, err_std, h_std = run_isolated("standard")
    if rc_std != 0 or tot_std == 0 or f_std > 0:
        print(f"FAIL: standard run failed: rc={rc_std}, passed={p_std}, failed={f_std}", file=sys.stderr)
        sys.exit(1)

    named_cases = [
        "empty string",
        "isogram with only lower case characters",
        "word with one duplicated character"
    ]
    for case in named_cases:
        if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", out_std, re.MULTILINE):
            print(f"FAIL: standard run missing named case '{case}'", file=sys.stderr)
            sys.exit(1)

    print(f"Standard run passed: {p_std} tests executed successfully.")

    print("Running mode: failing-reference...")
    rc_fail, p_fail, f_fail, tot_fail, out_fail, err_fail, h_fail = run_isolated("failing-reference")
    if rc_fail == 0 or f_fail == 0:
        print("FAIL: failing-reference run did not fail as expected.", file=sys.stderr)
        sys.exit(1)
    print(f"Failing reference correctly rejected (rc={rc_fail}, failures={f_fail}).")

    print("Running mode: empty-tests...")
    rc_empty, p_empty, f_empty, tot_empty, out_empty, err_empty, h_empty = run_isolated("empty-tests")
    if tot_empty != 0 or rc_empty == 0:
        print(f"FAIL: empty-tests run did not fail for zero tests: rc={rc_empty}, total={tot_empty}", file=sys.stderr)
        sys.exit(1)
    print("Empty test run correctly rejected with non-zero exit.")

    evidence_text = (
        "=== ISOLATED RUNNER VERIFICATION ===\n"
        f"Learner Stub SHA256 (Untouched): {h_std}\n\n"
        f"1. Standard Mode:         PASS (rc={rc_std}, passed={p_std}, failed={f_std})\n"
        f"2. Failing Reference Mode: PASS (rc={rc_fail}, failures={f_fail} as expected)\n"
        f"3. Empty Tests Mode:      PASS (rc={rc_empty}, total={tot_empty} zero-tests rejected)\n\n"
        f"Named Cases Verified: {', '.join(named_cases)}\n"
        "Integrity: All working tree learner files preserved with identical cryptographic hashes.\n"
    )
    (EVIDENCE_DIR / "isolation-results.txt").write_text(evidence_text, encoding="utf-8")
    print("All runner isolation checks passed cleanly.")

if __name__ == "__main__":
    main()
