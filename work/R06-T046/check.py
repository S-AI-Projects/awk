#!/usr/bin/env python3

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_REL = Path("exercises/practice/word-count")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")
EVIDENCE_FILE = Path(__file__).resolve().parent / "evidence.md"
ALT_FILE = Path(__file__).resolve().parent / "alternative.awk"


def run(command, cwd=None, env=None):
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_results(output):
    return re.findall(r"^(ok|not ok) \d+ (.+)$", output, re.MULTILINE)


def get_version(command):
    res = run(command)
    out = res.stdout.strip() or res.stderr.strip()
    return out.splitlines()[0] if out else "unknown"


def parse_word_count_output(text):
    counts = {}
    for line in text.strip().splitlines():
        if not line:
            continue
        parts = line.split(":")
        if len(parts) == 2:
            counts[parts[0].strip()] = int(parts[1].strip())
    return counts


def main():
    config_path = EXERCISE / ".meta/config.json"
    if not config_path.is_file():
        raise SystemExit(f"FAIL: Missing config {config_path}")

    config = json.loads(config_path.read_text())
    files = config.get("files", {})
    solution_rel = files["solution"][0]
    test_rel = files["test"][0]
    example_rel = files["example"][0]

    stub = EXERCISE / solution_rel
    test_file = EXERCISE / test_rel
    example_file = EXERCISE / example_rel

    initial_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    # Step 1: Validate reference implementation (FPAT) using validate_one_exercise
    with tempfile.TemporaryDirectory(prefix="r06-t046-ref-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_exercise = temp_root / EXERCISE_REL
        temp_validator = temp_root / VALIDATOR_REL

        shutil.copytree(EXERCISE, temp_exercise)
        temp_validator.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / VALIDATOR_REL, temp_validator)

        validator_cmd = ["bash", str(VALIDATOR_REL), str(EXERCISE_REL)]
        ref_run = run(validator_cmd, cwd=temp_root)
        ref_results = test_results(ref_run.stdout)

        if ref_run.returncode != 0:
            raise SystemExit(f"FAIL: reference validator failed with code {ref_run.returncode}")

        if not ref_results:
            raise SystemExit("FAIL: 0 tests executed for reference")

        named_cases = [
            "count one word",
            "count one of each word",
            "multiple occurrences of a word",
        ]
        ref_passed = [name for status, name in ref_results if status == "ok"]
        for case in named_cases:
            if case not in ref_passed:
                raise SystemExit(f"FAIL: named case '{case}' did not pass in reference")

    # Step 2: Validate alternative implementation (match + substr)
    with tempfile.TemporaryDirectory(prefix="r06-t046-alt-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_exercise = temp_root / EXERCISE_REL
        shutil.copytree(EXERCISE, temp_exercise)

        # Substitute the alternative implementation
        shutil.copy2(ALT_FILE, temp_exercise / solution_rel)

        alt_run = run(
            ["bats", str(temp_exercise / test_rel)],
            cwd=temp_exercise,
            env={"BATS_RUN_SKIPPED": "true"},
        )
        alt_results = test_results(alt_run.stdout)

        if alt_run.returncode != 0:
            raise SystemExit(f"FAIL: alternative implementation failed with code {alt_run.returncode}")

        if not alt_results:
            raise SystemExit("FAIL: 0 tests executed for alternative")

        if len(alt_results) != len(ref_results):
            raise SystemExit(f"FAIL: test counts differ (ref={len(ref_results)}, alt={len(alt_results)})")

        for case in named_cases:
            alt_passed = [name for status, name in alt_results if status == "ok"]
            if case not in alt_passed:
                raise SystemExit(f"FAIL: named case '{case}' did not pass in alternative")

    # Step 3: Compare exact direct counts on named cases between both implementations
    test_inputs = [
        ("count one word", "word"),
        ("count one of each word", "one of each"),
        ("multiple occurrences of a word", "one fish two fish red fish blue fish"),
    ]

    comparison_results = []
    for label, inp in test_inputs:
        r1 = subprocess.run(["gawk", "-f", str(example_file)], input=f"{inp}\n", text=True, capture_output=True)
        r2 = subprocess.run(["gawk", "-f", str(ALT_FILE)], input=f"{inp}\n", text=True, capture_output=True)

        if r1.returncode != 0 or r2.returncode != 0:
            raise SystemExit(f"FAIL: execution error on input '{inp}'")

        counts_ref = parse_word_count_output(r1.stdout)
        counts_alt = parse_word_count_output(r2.stdout)

        if counts_ref != counts_alt:
            raise SystemExit(f"FAIL: output mismatch for '{inp}': ref={counts_ref}, alt={counts_alt}")

        comparison_results.append((label, inp, counts_ref))

    # Step 4: Verify learner stub was not modified and is unsolved
    if hashlib.sha256(stub.read_bytes()).hexdigest() != initial_stub_hash:
        raise SystemExit("FAIL: original learner solution was modified")

    stub_check = subprocess.run(["gawk", "-f", str(stub)], input="word\n", text=True, capture_output=True)
    if stub_check.returncode == 0:
        raise SystemExit("FAIL: learner stub should be unsolved but exited 0")

    # Step 5: Save evidence
    evidence = f"""# R06-T046 — Word Count Two Approaches Verification Evidence

## Summary
Compared Approach 1 (Reference `FPAT`) and Approach 2 (Alternative `match` + `substr`).
Both implementations passed all {len(ref_results)} tests in the BATS suite.

## Direct Comparison on Named Cases
| Test Name | Input Phrase | Parsed Frequency Map | Agreement |
|---|---|---|---|
"""
    for label, inp, counts in comparison_results:
        evidence += f"| {label} | `{inp}` | `{json.dumps(counts)}` | MATCH |\n"

    evidence += f"""
## Test Suite Summary
- Reference Tests Executed: {len(ref_results)} (All OK)
- Alternative Tests Executed: {len(alt_results)} (All OK)

## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: Reference passed all {len(ref_results)} tests.")
    print(f"PASS: Alternative passed all {len(alt_results)} tests.")
    print("PASS: Both implementations produce identical results on named cases.")
    print("PASS: Learner stub remains unchanged and unsolved.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
