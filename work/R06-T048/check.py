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
EXERCISE_REL = Path("exercises/practice/poker")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")
COURSE_CHECK = ROOT / "tools/course_checks/r06-t048.py"
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
    # Step 1: Run course check for metadata path resolution and invalid fixtures
    check_run = run(["python3", str(COURSE_CHECK)], cwd=ROOT)
    if check_run.returncode != 0:
        raise SystemExit(f"FAIL: tools/course_checks/r06-t048.py failed with exit code {check_run.returncode}:\n{check_run.stderr}")

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

    # Step 2: Test reference in temporary directory via validate_one_exercise
    with tempfile.TemporaryDirectory(prefix="r06-t048-") as temp_dir:
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
            "single hand always wins",
            "highest card out of all hands wins",
            "a tie has multiple winners",
        ]
        passed_test_names = [name for status, name in results if status == "ok"]

        for case in named_cases:
            if case not in passed_test_names:
                raise SystemExit(f"FAIL: named case '{case}' did not pass")

        if any(status != "ok" for status, _ in results):
            raise SystemExit(f"FAIL: some tests failed in suite: {results}")

    # Step 3: Verify learner stub was not modified and is unsolved
    if hashlib.sha256(stub.read_bytes()).hexdigest() != initial_stub_hash:
        raise SystemExit("FAIL: original learner solution was modified")

    stub_check = run(["gawk", "-f", str(stub)], cwd=EXERCISE)
    if stub_check.returncode == 0:
        raise SystemExit("FAIL: learner stub should be unsolved but exited 0")

    # Step 4: Record evidence
    evidence = f"""# R06-T048 — Poker File Mapping and Validation Evidence

## Path and Configuration Verification
Output of `python3 tools/course_checks/r06-t048.py`:
```text
{check_run.stdout.strip()}
```

## BATS Test Execution Summary
- Validator Exit Code: {result.returncode}
- Total Executed Cases: {len(results)}
- Passed Cases: {len(passed_test_names)}
- Named cases verified:
  - `single hand always wins`
  - `highest card out of all hands wins`
  - `a tie has multiple winners`

## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: All {len(results)} tests passed.")
    print("PASS: Path verification and 3 invalid fixtures passed via tools/course_checks/r06-t048.py.")
    print("PASS: Named cases verified.")
    print("PASS: Learner stub remains unchanged and unsolved.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
