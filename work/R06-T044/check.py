#!/usr/bin/env python3

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_REL = Path("exercises/practice/eliuds-eggs")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")
EVIDENCE_FILE = Path(__file__).resolve().parent / "evidence.md"


def run(command, cwd=None):
    return subprocess.run(
        command,
        cwd=cwd,
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
    test_file = EXERCISE / test_rel
    example_file = EXERCISE / example_rel

    initial_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    # Verify baseline test execution with validate_one_exercise
    with tempfile.TemporaryDirectory(prefix="r06-t044-") as temp_dir:
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

        named_cases = ["0 eggs", "1 egg", "4 eggs"]
        passed_test_names = [name for status, name in results if status == "ok"]

        for case in named_cases:
            if case not in passed_test_names:
                raise SystemExit(f"FAIL: named case '{case}' was not among passed tests")

        if any(status != "ok" for status, _ in results):
            raise SystemExit(f"FAIL: some tests failed in suite: {results}")

        # Verify direct outputs on baseline cases
        cases_to_test = [
            ("0", "0"),
            ("16", "1"),
            ("89", "4"),
            ("2000000000", "13"),
        ]

        direct_results = []
        for inp, expected in cases_to_test:
            gawk_res = subprocess.run(
                ["gawk", "-f", str(example_file)],
                input=f"{inp}\n",
                text=True,
                capture_output=True,
            )
            if gawk_res.returncode != 0:
                raise SystemExit(f"FAIL: gawk execution failed on input {inp}")
            actual = gawk_res.stdout.strip()
            if actual != expected:
                raise SystemExit(f"FAIL: input {inp} expected {expected}, got {actual}")
            direct_results.append((inp, expected, actual))

    # Verify original learner stub was not modified and is still unsolved
    current_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()
    if current_stub_hash != initial_stub_hash:
        raise SystemExit("FAIL: original learner solution was modified")

    # Verify learner stub fails or reports unsolved
    stub_test = subprocess.run(
        ["gawk", "-f", str(stub)],
        input="16\n",
        text=True,
        capture_output=True,
    )
    if stub_test.returncode == 0:
        raise SystemExit("FAIL: learner stub should be unsolved but exited 0")

    # Record evidence
    evidence = f"""# R06-T044 — eliuds-eggs reference refactor check

## Summary
Refactored exercises/practice/eliuds-eggs/.meta/example.awk for domain clarity:
- Renamed generic variables `count` and `num` to domain-specific names `egg_count` and `value`.
- Added explanatory documentation detailing the bitwise population-count invariant.
- All 4 test cases pass identically without modifying public API or adding external dependencies.

## Validator Output
Exit code: {result.returncode}
```text
{result.stdout}{result.stderr}
```

## Named Cases Direct Evaluation
| Input Decimal | Expected Eggs | Actual Output | Status |
|---------------|---------------|---------------|--------|
"""
    for inp, exp, act in direct_results:
        evidence += f"| {inp} | {exp} | {act} | PASS |\n"

    evidence += f"""
## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: All {len(results)} tests passed.")
    print("PASS: Named cases (0 eggs; 1 egg; 4 eggs) verified.")
    print("PASS: Learner stub remains unsolved and unchanged.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
