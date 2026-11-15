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
EXERCISE_REL = Path("exercises/practice/yacht")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")
RUNNER = ROOT / "tools/course_checks/r06-t049.py"
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
    initial_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    # Test 1: Real reference execution
    h_before_1 = hashlib.sha256(stub.read_bytes()).hexdigest()
    run_1 = run(["python3", str(RUNNER)], cwd=ROOT)
    h_after_1 = hashlib.sha256(stub.read_bytes()).hexdigest()

    if h_before_1 != h_after_1:
        raise SystemExit("FAIL: Learner stub modified during normal run")

    if run_1.returncode != 0:
        raise SystemExit(f"FAIL: Normal runner execution failed ({run_1.returncode}):\n{run_1.stderr}")

    # Validate output test names
    # Also run validate_one_exercise directly to verify test results
    with tempfile.TemporaryDirectory(prefix="r06-t049-val-") as temp_dir:
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

        named_cases = ["Yacht", "Not Yacht", "Ones"]
        passed_test_names = [name for status, name in results if status == "ok"]

        for case in named_cases:
            if case not in passed_test_names:
                raise SystemExit(f"FAIL: named case '{case}' did not pass")

        if any(status != "ok" for status, _ in results):
            raise SystemExit(f"FAIL: some tests failed in suite: {results}")

    # Test 2: Deliberately failing reference
    h_before_2 = hashlib.sha256(stub.read_bytes()).hexdigest()
    run_2 = run(["python3", str(RUNNER), "--failing-reference"], cwd=ROOT)
    h_after_2 = hashlib.sha256(stub.read_bytes()).hexdigest()

    if h_before_2 != h_after_2:
        raise SystemExit("FAIL: Learner stub modified during failing-reference run")

    if run_2.returncode != 0:
        raise SystemExit("FAIL: Failing reference run did not handle error cleanly")

    # Test 3: Empty test selection
    h_before_3 = hashlib.sha256(stub.read_bytes()).hexdigest()
    run_3 = run(["python3", str(RUNNER), "--empty-tests"], cwd=ROOT)
    h_after_3 = hashlib.sha256(stub.read_bytes()).hexdigest()

    if h_before_3 != h_after_3:
        raise SystemExit("FAIL: Learner stub modified during empty-tests run")

    if run_3.returncode != 0:
        raise SystemExit("FAIL: Empty tests run did not handle zero-test condition cleanly")

    # Verify learner stub unsolved
    final_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()
    if final_stub_hash != initial_stub_hash:
        raise SystemExit("FAIL: Final learner stub hash differs from initial hash")

    stub_check = run(["gawk", "-f", str(stub)], cwd=EXERCISE)
    if stub_check.returncode == 0:
        raise SystemExit("FAIL: Learner stub should be unsolved but exited 0")

    # Record evidence
    evidence = f"""# R06-T049 — Yacht Isolated Test Runner Evidence

## Test Runner Execution Matrix
| Configuration | Command | Expected Outcome | Observed Outcome | Stub Hash Intact | Status |
|---|---|---|---|---|---|
| Normal Reference | `python3 tools/course_checks/r06-t049.py` | Exit 0, 29 tests pass | {run_1.stdout.strip()} | Yes | PASS |
| Failing Reference | `python3 tools/course_checks/r06-t049.py --failing-reference` | Non-zero child exit caught | {run_2.stdout.strip()} | Yes | PASS |
| Empty Test Suite | `python3 tools/course_checks/r06-t049.py --empty-tests` | Zero-test error caught | {run_3.stdout.strip()} | Yes | PASS |

## Test Suite Execution Details
- Total Cases: {len(results)}
- Passed Cases: {len(passed_test_names)}
- Named cases verified:
  - `Yacht`
  - `Not Yacht`
  - `Ones`

## Cryptographic Stub Verification
- Initial SHA256: `{initial_stub_hash}`
- Post-Test 1 SHA256: `{h_after_1}`
- Post-Test 2 SHA256: `{h_after_2}`
- Post-Test 3 SHA256: `{h_after_3}`
- Final SHA256: `{final_stub_hash}`

## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: All {len(results)} tests passed in isolated runner.")
    print("PASS: Failing reference and empty-tests modes verified.")
    print("PASS: Learner stub cryptographic hashes confirmed unchanged across all runs.")
    print("PASS: Named cases (Yacht, Not Yacht, Ones) verified.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
