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
EXERCISE_REL = Path("exercises/practice/scrabble-score")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")
EVIDENCE_FILE = Path(__file__).resolve().parent / "evidence.md"


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
    example_file = EXERCISE / example_rel
    initial_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    # Step 1: Validate reference implementation with validate_one_exercise
    with tempfile.TemporaryDirectory(prefix="r06-t050-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_exercise = temp_root / EXERCISE_REL
        temp_validator = temp_root / VALIDATOR_REL

        shutil.copytree(EXERCISE, temp_exercise)
        temp_validator.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / VALIDATOR_REL, temp_validator)

        validator_cmd = ["bash", str(VALIDATOR_REL), str(EXERCISE_REL)]
        result = run(validator_cmd, cwd=temp_root)
        results = test_results(result.stdout)

        if result.returncode != 0:
            raise SystemExit(f"FAIL: validator exited with code {result.returncode}")

        if not results:
            raise SystemExit("FAIL: 0 tests executed")

        named_cases = [
            "lowercase letter",
            "uppercase letter",
            "valuable letter",
        ]
        passed_test_names = [name for status, name in results if status == "ok"]

        for case in named_cases:
            if case not in passed_test_names:
                raise SystemExit(f"FAIL: named case '{case}' did not pass")

        if any(status != "ok" for status, _ in results):
            raise SystemExit(f"FAIL: some tests failed in suite: {results}")

    # Step 2: Assert exact direct outputs matching the decision table
    decision_table_tests = [
        ("lowercase letter", "a", "A,1"),
        ("uppercase letter", "A", "A,1"),
        ("valuable letter", "f", "F,4"),
    ]

    direct_results = []
    for label, inp, expected_output in decision_table_tests:
        res = subprocess.run(
            ["gawk", "-f", str(example_file)],
            input=f"{inp}\n",
            text=True,
            capture_output=True,
        )
        if res.returncode != 0:
            raise SystemExit(f"FAIL: execution error on input '{inp}'")

        actual = res.stdout.strip()
        if actual != expected_output:
            raise SystemExit(
                f"FAIL: decision table mismatch for '{label}' (input='{inp}'): "
                f"expected '{expected_output}', got '{actual}'"
            )
        direct_results.append((label, inp, expected_output, actual))

    # Step 3: Verify learner stub was not modified and is unsolved
    if hashlib.sha256(stub.read_bytes()).hexdigest() != initial_stub_hash:
        raise SystemExit("FAIL: original learner solution was modified")

    stub_check = run(["gawk", "-f", str(stub)], cwd=EXERCISE)
    if stub_check.returncode == 0:
        raise SystemExit("FAIL: learner stub should be unsolved but exited 0")

    # Step 4: Record evidence
    evidence = f"""# R06-T050 — Scrabble Score Contract Evidence

## Decision Table Verification
| Case | Input | Expected Output | Actual Output | Status |
|---|---|---|---|---|
"""
    for label, inp, exp, act in direct_results:
        evidence += f"| {label} | `{inp}` | `{exp}` | `{act}` | PASS |\n"

    evidence += f"""
## Test Suite Summary
- Validator Exit Code: {result.returncode}
- Total Tests Executed: {len(results)}
- Passed Tests: {len(passed_test_names)}
- Named cases verified:
  - `lowercase letter`
  - `uppercase letter`
  - `valuable letter`

## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: All {len(results)} tests passed.")
    print("PASS: Decision table matches exact outputs for selected cases.")
    print("PASS: Learner stub remains unchanged and unsolved.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
