
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import sys
import tomllib


# --------------------------------------------------
# 1. Repository and exercise paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

EXERCISE = ROOT / "exercises" / "practice" / "kindergarten-garden"
VALIDATOR = ROOT / "bin" / "validate_one_exercise"
CONFIG = EXERCISE / ".meta" / "config.json"

WORK_DIR = ROOT / "work" / "R06-T041"
INPUT_DIR = WORK_DIR / "inputs"
REPORT_FILE = WORK_DIR / "results.json"

EXPECTED_TESTS = 17


def require(condition, message):
    """Raise an error if a verification condition fails."""
    if not condition:
        raise AssertionError(message)


print("Repository:", ROOT)
print("Exercise:", EXERCISE)
print("Validator:", VALIDATOR)


# --------------------------------------------------
# 2. Verify required files
# --------------------------------------------------

require(ROOT.is_dir(), "Repository directory not found")
require(EXERCISE.is_dir(), "Exercise directory not found")
require(VALIDATOR.is_file(), "Validator not found")
require(CONFIG.is_file(), "Configuration file not found")

with CONFIG.open() as file:
    config = json.load(file)

files = config["files"]

stub = files["solution"][0]
tests = files["test"][0]
reference = files["example"][0]

learner_solution = EXERCISE / stub
reference_solution = EXERCISE / reference
test_file = EXERCISE / tests
tests_toml = EXERCISE / ".meta" / "tests.toml"
# Audit canonical test inclusion settings
toml_before = tests_toml.read_bytes()
canonical_cases = tomllib.loads(toml_before.decode("utf-8"))

included_before = sum(
    1 for case in canonical_cases.values()
    if case.get("include", True)
)

excluded_before = sum(
    1 for case in canonical_cases.values()
    if not case.get("include", True)
)

print("\nCanonical case audit:")
print("Total cases:", len(canonical_cases))
print("Included before:", included_before)
print("Excluded before:", excluded_before)

require(
    len(canonical_cases) == EXPECTED_TESTS,
    "Unexpected number of canonical cases"
)

require(learner_solution.is_file(), "Learner solution not found")
require(reference_solution.is_file(), "Reference solution not found")
require(test_file.is_file(), "Bats test file not found")
require(tests_toml.is_file(), "Canonical tests TOML not found")

print("\nFiles identified from config.json:")
print("Learner solution:", stub)
print("Test file:", tests)
print("Reference solution:", reference)


# --------------------------------------------------
# 3. Save original learner solution
# --------------------------------------------------

learner_before = learner_solution.read_bytes()
learner_hash_before = hashlib.sha256(learner_before).hexdigest()


# --------------------------------------------------
# 4. Save input files for the assignment record
# --------------------------------------------------

INPUT_DIR.mkdir(parents=True, exist_ok=True)

input_files = [
    CONFIG,
    tests_toml,
    test_file,
    reference_solution,
]

for source in input_files:
    destination = INPUT_DIR / source.name
    shutil.copy2(source, destination)

print("\nInput files saved in:", INPUT_DIR)


# --------------------------------------------------
# 5. Find Homebrew Bash
# --------------------------------------------------

brew_prefix = subprocess.run(
    ["brew", "--prefix"],
    capture_output=True,
    text=True,
    check=True
).stdout.strip()

bash = str(Path(brew_prefix) / "bin" / "bash")

require(Path(bash).is_file(), "Homebrew Bash not found")


# --------------------------------------------------
# 6. Record tool versions
# --------------------------------------------------

def get_version(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    output = result.stdout or result.stderr
    return output.splitlines()[0] if output else "Version unavailable"


tool_versions = {
    "python": sys.version.split()[0],
    "bash": get_version([bash, "--version"]),
    "bats": get_version(["bats", "--version"]),
    "gawk": get_version(["gawk", "--version"]),
    "jq": get_version(["jq", "--version"]),
}

print("\nTool versions:")
for tool, version in tool_versions.items():
    print(f"{tool}: {version}")


# --------------------------------------------------
# 7. Create temporary repository and run validator
# --------------------------------------------------

with tempfile.TemporaryDirectory(prefix="R06-T041-") as temp_dir:

    temp_root = Path(temp_dir)

    temp_exercise = (
        temp_root
        / "exercises"
        / "practice"
        / "kindergarten-garden"
    )

    # Copy the complete exercise, including hidden files
    shutil.copytree(EXERCISE, temp_exercise)

    # Substitute the reference solution only in the copy
    shutil.copy2(
        temp_exercise / reference,
        temp_exercise / stub
    )

    print("\nTemporary exercise:", temp_exercise)

    # Verify the temporary solution matches the reference
    require(
        (temp_exercise / stub).read_bytes()
        == reference_solution.read_bytes(),
        "Reference substitution failed"
    )

    # Run the validator from the temporary repository root
    result = subprocess.run(
        [
            bash,
            str(VALIDATOR),
            "exercises/practice/kindergarten-garden"
        ],
        cwd=temp_root,
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )

    actual_output = result.stdout
    actual_errors = result.stderr
    return_code = result.returncode

    print("\nValidator output:")
    print(actual_output)

    if actual_errors:
        print("Validator errors:")
        print(actual_errors)

    print("Validator exit code:", return_code)


# --------------------------------------------------
# 8. Check test execution and results
# --------------------------------------------------

plan_match = re.search(
    r"(?m)^1\.\.(\d+)\s*$",
    actual_output
)

executed_tests = len(
    re.findall(r"(?m)^(?:ok|not ok)\s+\d+", actual_output)
)

passed_tests = len(
    re.findall(r"(?m)^ok\s+\d+", actual_output)
)

planned_tests = int(plan_match.group(1)) if plan_match else 0

print("\nTest summary:")
print("Expected tests:", EXPECTED_TESTS)
print("Planned tests:", planned_tests)
print("Executed tests:", executed_tests)
print("Passed tests:", passed_tests)


# --------------------------------------------------
# 9. Verify original learner solution is unchanged
# --------------------------------------------------

learner_after = learner_solution.read_bytes()
learner_hash_after = hashlib.sha256(learner_after).hexdigest()

original_unchanged = learner_before == learner_after

print("\nOriginal learner solution unchanged:", original_unchanged)


# --------------------------------------------------
# 10. Save expected vs actual results
# --------------------------------------------------

report = {
    "task": "R06-T041",
    "exercise": "kindergarten-garden",
    "timestamp": datetime.now().astimezone().isoformat(),

    "inputs": {
        "canonical_case_audit": {
    "total": len(canonical_cases),
    "included_before": included_before,
    "excluded_before": excluded_before,
    "included_after": included_before,
    "excluded_after": excluded_before,
    "toml_unchanged": (
        tests_toml.read_bytes() == toml_before
    ),
    "decisions": {
        "1fc316ed-17ab-4fba-88ef-3ae78296b692":
            "Keep included: verifies the basic single-student garden assignment.",
        "acd19dc1-2200-4317-bc2a-08f021276b40":
            "Keep included: verifies a different plant arrangement for a single student.",
        "c376fcc8-349c-446c-94b0-903947315757":
            "Keep included: verifies that the second student receives their own garden plants."
    }
},
        "config": str(CONFIG.relative_to(ROOT)),
        "tests_toml": str(tests_toml.relative_to(ROOT)),
        "bats_tests": str(test_file.relative_to(ROOT)),
        "reference_solution": str(reference_solution.relative_to(ROOT)),
        "learner_solution": str(learner_solution.relative_to(ROOT)),
    },

    "expected": {
        "tests": EXPECTED_TESTS,
        "return_code": 0,
        "original_solution_unchanged": True,
    },

    "actual": {
        "planned_tests": planned_tests,
        "executed_tests": executed_tests,
        "passed_tests": passed_tests,
        "return_code": return_code,
        "original_solution_unchanged": original_unchanged,
        "stdout": actual_output,
        "stderr": actual_errors,
    },

    "learner_solution_sha256_before": learner_hash_before,
    "learner_solution_sha256_after": learner_hash_after,

    "tool_versions": tool_versions,
}

REPORT_FILE.write_text(
    json.dumps(report, indent=4)
)

print("\nReport saved to:", REPORT_FILE)


# --------------------------------------------------
# 11. Final assertions
# --------------------------------------------------

require(return_code == 0, "Validator exited with a nonzero status")

require(planned_tests > 0, "Validator executed zero planned tests")

require(
    planned_tests == EXPECTED_TESTS,
    "Unexpected number of planned tests"
)

require(
    executed_tests == EXPECTED_TESTS,
    "Unexpected number of executed tests"
)

require(
    passed_tests == EXPECTED_TESTS,
    "One or more tests failed"
)

require(
    original_unchanged,
    "Original learner solution was modified"
)

print("\nSUCCESS: All 17 reference tests passed.")
print("SUCCESS: Original learner solution remains unchanged.")
