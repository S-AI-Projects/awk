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
EXERCISE_REL = Path("exercises/practice/luhn")
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
    test_file = EXERCISE / test_rel
    example_file = EXERCISE / example_rel

    initial_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    # Step 1: Validate reference implementation with validate_one_exercise
    with tempfile.TemporaryDirectory(prefix="r06-t047-") as temp_dir:
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
            "single digit strings can not be valid",
            "a single zero is invalid",
            "a simple valid SIN that remains valid if reversed",
        ]
        passed_test_names = [name for status, name in results if status == "ok"]

        for case in named_cases:
            if case not in passed_test_names:
                raise SystemExit(f"FAIL: named case '{case}' did not pass")

        if any(status != "ok" for status, _ in results):
            raise SystemExit(f"FAIL: some tests failed in suite: {results}")

    # Step 2: Assert both micro-example outputs matching published hint
    # Micro-example 1: Numeric coercion in luhn_digit calculation
    code_ex1 = 'BEGIN { digit = "7"; doubled = digit * 2; print doubled - (doubled > 9 ? 9 : 0) }'
    res_ex1 = run(["gawk", code_ex1])
    out_ex1 = res_ex1.stdout.strip()
    if out_ex1 != "5":
        raise SystemExit(f"FAIL: micro-example 1 expected '5', got '{out_ex1}'")

    # Micro-example 2: Lexicographical vs numeric comparison pitfall
    code_ex2_uncoerced = 'BEGIN { a = "10"; b = "9"; print (a > b ? "true" : "false") }'
    res_ex2_uncoerced = run(["gawk", code_ex2_uncoerced])
    out_ex2_uncoerced = res_ex2_uncoerced.stdout.strip()
    if out_ex2_uncoerced != "false":
        raise SystemExit(f"FAIL: uncoerced comparison expected 'false', got '{out_ex2_uncoerced}'")

    code_ex2_coerced = 'BEGIN { a = "10" + 0; b = "9" + 0; print (a > b ? "true" : "false") }'
    res_ex2_coerced = run(["gawk", code_ex2_coerced])
    out_ex2_coerced = res_ex2_coerced.stdout.strip()
    if out_ex2_coerced != "true":
        raise SystemExit(f"FAIL: coerced comparison expected 'true', got '{out_ex2_coerced}'")

    # Step 3: Verify learner stub was not modified and is unsolved
    if hashlib.sha256(stub.read_bytes()).hexdigest() != initial_stub_hash:
        raise SystemExit("FAIL: original learner solution was modified")

    stub_check = run(["gawk", "-f", str(stub)], cwd=EXERCISE)
    if stub_check.returncode == 0:
        raise SystemExit("FAIL: learner stub should be unsolved but exited 0")

    # Step 4: Record evidence
    evidence = f"""# R06-T047 — Luhn AWK-Specific Guidance Evidence

## Summary
Documented AWK numeric coercion as utilized in `luhn_digit`, contrasted against lexicographical string comparison pitfalls.

## Micro-Example Assertions
1. **Coercion in `luhn_digit` calculation**:
   - Code: `{code_ex1}`
   - Expected Output: `5`
   - Actual Output: `{out_ex1}`
   - Status: PASS

2. **Uncoerced String Comparison Pitfall**:
   - Code: `{code_ex2_uncoerced}`
   - Expected Output: `false`
   - Actual Output: `{out_ex2_uncoerced}`
   - Status: PASS

3. **Coerced Numeric Comparison**:
   - Code: `{code_ex2_coerced}`
   - Expected Output: `true`
   - Actual Output: `{out_ex2_coerced}`
   - Status: PASS

## Test Suite Execution
- Total Cases Executed: {len(results)}
- Passed Cases: {len(passed_test_names)}
- Named cases verified:
  - `single digit strings can not be valid`
  - `a single zero is invalid`
  - `a simple valid SIN that remains valid if reversed`

## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: All {len(results)} tests passed.")
    print("PASS: Micro-examples verified and match documentation.")
    print("PASS: Named cases verified.")
    print("PASS: Learner stub remains unchanged and unsolved.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
