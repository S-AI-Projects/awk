#!/usr/bin/env python3

import argparse
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
EXERCISE_REL = Path("exercises/practice/yacht")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")


def get_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_isolated_yacht_test(
    override_reference: str = None,
    empty_tests: bool = False,
) -> dict:
    config_path = EXERCISE / ".meta/config.json"
    if not config_path.is_file():
        raise RuntimeError(f"Missing config at {config_path}")

    config = json.loads(config_path.read_text())
    files = config.get("files", {})
    solution_rel = files["solution"][0]
    test_rel = files["test"][0]
    example_rel = files["example"][0]

    stub_path = EXERCISE / solution_rel
    if not stub_path.is_file():
        raise RuntimeError(f"Missing learner stub at {stub_path}")

    initial_hash = get_sha256(stub_path)

    temp_dir = tempfile.mkdtemp(prefix="yacht-runner-")
    try:
        temp_root = Path(temp_dir)
        temp_exercise = temp_root / EXERCISE_REL
        temp_validator = temp_root / VALIDATOR_REL

        # Copy exercise directory including dotfiles
        shutil.copytree(EXERCISE, temp_exercise)

        # Copy validator script
        temp_validator.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / VALIDATOR_REL, temp_validator)

        # Apply overrides in temp directory only
        if override_reference is not None:
            (temp_exercise / example_rel).write_text(override_reference)

        if empty_tests:
            (temp_exercise / test_rel).write_text("#!/usr/bin/env bats\nload bats-extra\n")

        validator_cmd = ["bash", str(VALIDATOR_REL), str(EXERCISE_REL)]
        result = subprocess.run(
            validator_cmd,
            cwd=temp_root,
            text=True,
            capture_output=True,
        )

        test_lines = re.findall(r"^(ok|not ok) \d+ (.+)$", result.stdout, re.MULTILINE)
        plan_match = re.search(r"^1\.\.(\d+)", result.stdout, re.MULTILINE)
        plan_count = int(plan_match.group(1)) if plan_match else len(test_lines)

        run_info = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "test_count": plan_count,
            "tests": test_lines,
            "passed_tests": [name for status, name in test_lines if status == "ok"],
            "failed_tests": [name for status, name in test_lines if status == "not ok"],
        }
        return run_info

    finally:
        # Guarantee cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

        # Guarantee learner stub integrity check
        final_hash = get_sha256(stub_path)
        if initial_hash != final_hash:
            raise RuntimeError(
                f"FATAL: Learner stub {stub_path} was modified during run! "
                f"Initial: {initial_hash}, Final: {final_hash}"
            )


def main():
    parser = argparse.ArgumentParser(description="Isolated runner for yacht exercise")
    parser.add_argument("--failing-reference", action="store_true", help="Run with deliberately failing reference")
    parser.add_argument("--empty-tests", action="store_true", help="Run with empty test selection")
    args = parser.parse_args()

    override_ref = "BEGIN { print \"deliberate failure\" > \"/dev/stderr\"; exit 1 }\n" if args.failing_reference else None

    info = run_isolated_yacht_test(
        override_reference=override_ref,
        empty_tests=args.empty_tests,
    )

    if args.failing_reference:
        if info["exit_code"] != 0:
            print(f"PASS: Failing reference produced non-zero exit code ({info['exit_code']}).")
            sys.exit(0)
        else:
            print("FAIL: Failing reference unexpectedly exited 0.")
            sys.exit(1)

    if args.empty_tests:
        if info["test_count"] == 0 or info["exit_code"] != 0:
            print(f"PASS: Empty tests produced expected failure/zero-count.")
            sys.exit(0)
        else:
            print("FAIL: Empty tests unexpectedly reported tests.")
            sys.exit(1)

    # Standard run: verify success
    if info["exit_code"] != 0:
        print(f"FAIL: Validator exited {info['exit_code']}:\n{info['stderr']}")
        sys.exit(info["exit_code"])

    if info["test_count"] == 0:
        print("FAIL: Executed 0 tests.")
        sys.exit(1)

    if info["failed_tests"]:
        print(f"FAIL: Tests failed: {info['failed_tests']}")
        sys.exit(1)

    print(f"PASS: All {info['test_count']} yacht tests passed in isolated temporary copy.")
    print("PASS: Learner stub was not altered.")
    sys.exit(0)


if __name__ == "__main__":
    main()
