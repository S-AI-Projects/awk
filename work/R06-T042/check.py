
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/pascals-triangle"
VALIDATOR = ROOT / "bin/validate_one_exercise"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config_path = EXERCISE / ".meta/config.json"

    if not config_path.is_file():
        fail("Missing .meta/config.json")

    config = json.loads(config_path.read_text())
    files = config.get("files", {})

    solution = files.get("solution", [])
    tests = files.get("test", [])
    example = files.get("example") or files.get("exemplar", [])

    if not solution or not tests or not example:
        fail("Missing solution, test, or example entry in config.json")

    stub = EXERCISE / solution[0]
    test_file = EXERCISE / tests[0]
    reference = EXERCISE / example[0]

    for path in (stub, test_file, reference, VALIDATOR):
        if not path.is_file():
            fail(f"Missing required file: {path}")

    expected_count = sum(
        bool(re.match(r"^\s*@test\b", line))
        for line in test_file.read_text().splitlines()
    )

    if expected_count == 0:
        fail("Zero tests found in the Bats file")

    original_hash = sha256(stub)

    with tempfile.TemporaryDirectory(prefix="r06-t042-") as temp:
        temp_exercise = Path(temp) / "pascals-triangle"

        # Copy the complete exercise, including hidden files.
        shutil.copytree(EXERCISE, temp_exercise)

        # Use the reference only in the temporary copy.
        shutil.copy2(
            temp_exercise / example[0],
            temp_exercise / solution[0]
        )

        result = subprocess.run(
            ["bash", str(VALIDATOR), str(temp_exercise)],
            cwd=ROOT,
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr
        print(output)

        if result.returncode != 0:
            fail(f"Validator exited with code {result.returncode}")

        plans = re.findall(r"(?m)^1\.\.(\d+)\s*$", output)

        if not plans:
            fail("Could not find the Bats test count")

        actual_count = int(plans[-1])

        if actual_count == 0:
            fail("Validator executed zero tests")

        if actual_count != expected_count:
            fail(
                f"Expected {expected_count} tests, "
                f"but found {actual_count}"
            )

    if sha256(stub) != original_hash:
        fail("Original learner solution was modified")

    print(f"PASS: All {actual_count} tests passed.")
    print("PASS: Validator exited successfully.")
    print("PASS: Original learner solution remains unchanged.")


if __name__ == "__main__":
    main()
