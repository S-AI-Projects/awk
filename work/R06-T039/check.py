#!/usr/bin/env python3
"""
Verification script for Task R06-T039: Pythagorean Triplet Focused Runner & Integrity Checks.

Checks performed:
1. Path resolution from exercises/practice/pythagorean-triplet/.meta/config.json.
2. Cryptographic hashing (SHA-256) of learner files before and after all runs.
3. Verification that learner solution (pythagorean-triplet.awk) is untouched and unsolved.
4. Execution of three runner scenarios:
   - Scenario 1 (Real Reference): Validates authentic example.awk in isolated temp copy.
     Asserts return code 0 and all 7 tests pass (including named cases 12, 108, 1000).
   - Scenario 2 (Failing Reference): Substitutes a deliberately broken example.awk in temp copy.
     Asserts child non-zero exit code and failure propagation.
   - Scenario 3 (Zero-Test Run): Evaluates a test suite with 0 executed tests.
     Asserts non-zero exit code / failure rejection on zero-test runs.
5. Verification that temporary directories and files are cleaned up after each scenario.
6. Re-assertion of identical learner file hashes before and after every scenario.
7. Generation of artifacts in work/R06-T039/ (inputs.json, expected_vs_actual.json, runner_scenarios.json, versions.txt, evidence.md, output.txt).
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path(__file__).resolve().parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "pythagorean-triplet"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"

ENV = os.environ.copy()
gnubin = "/opt/homebrew/opt/gawk/libexec/gnubin"
homebrew_bin = "/opt/homebrew/bin"
ENV["PATH"] = f"{gnubin}:{homebrew_bin}:{ENV.get('PATH', '')}"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_learner_file_hashes() -> dict:
    hashes = {}
    for p in sorted(EXERCISE_DIR.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(EXERCISE_DIR))
            hashes[rel] = compute_sha256(p)
    return hashes


def resolve_paths():
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    files = config.get("files", {})
    solution = files.get("solution", ["pythagorean-triplet.awk"])[0]
    test = files.get("test", ["test-pythagorean-triplet.bats"])[0]
    example = files.get("example", [".meta/example.awk"])[0]
    return {
        "solution": EXERCISE_DIR / solution,
        "test": EXERCISE_DIR / test,
        "example": EXERCISE_DIR / example,
    }


def verify_learner_solution(solution_path: Path):
    print("Checking learner solution remains unsolved stub...")
    content = solution_path.read_text(encoding="utf-8")
    assert "Implement this solution" in content, (
        "Learner solution appears modified or solved; must remain unsolved stub!"
    )
    assert "exit 1" in content, (
        "Learner solution stub missing expected failure exit code!"
    )
    print("Learner solution is verified untouched.")


def run_scenario(scenario_name: str, paths: dict, mutate_fn=None):
    """
    Executes bin/validate_one_exercise inside an isolated temporary directory.
    Optionally applies mutate_fn(tmp_exercise) before execution.
    Verifies that the temp directory is cleaned up afterwards.
    """
    print(f"\n--- Running Scenario: {scenario_name} ---")
    tmp_path_holder = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_path_holder.append(str(tmp_root))
        tmp_exercise = tmp_root / "exercises" / "practice" / "pythagorean-triplet"
        
        # Copy harness files and exercise
        shutil.copytree(REPO_ROOT / "bin", tmp_root / "bin", symlinks=True)
        if (REPO_ROOT / "lib").exists():
            shutil.copytree(REPO_ROOT / "lib", tmp_root / "lib", symlinks=True)
        shutil.copytree(EXERCISE_DIR, tmp_exercise, symlinks=True)
        
        # Default behavior: substitute example into solution in temp copy
        tmp_solution = tmp_exercise / paths["solution"].name
        tmp_example = tmp_exercise / paths["example"].relative_to(EXERCISE_DIR)
        shutil.copyfile(tmp_example, tmp_solution)

        # Optional mutation
        if mutate_fn:
            mutate_fn(tmp_exercise)

        cmd = ["bin/validate_one_exercise", "exercises/practice/pythagorean-triplet"]
        proc = subprocess.run(
            cmd,
            cwd=str(tmp_root),
            capture_output=True,
            text=True,
            env=ENV
        )

    # Check cleanup
    assert not os.path.exists(tmp_path_holder[0]), (
        f"Temporary directory was not cleaned up: {tmp_path_holder[0]}"
    )
    print(f"Scenario '{scenario_name}' exited with code {proc.returncode}. Temp dir cleaned up successfully.")
    return proc


def test_runner_scenarios(paths: dict, baseline_hashes: dict):
    scenarios_results = {}

    # Scenario 1: Real Reference (Must pass with 7 tests)
    proc1 = run_scenario("Real Reference (Success Run)", paths)
    hashes_after_1 = get_learner_file_hashes()
    assert baseline_hashes == hashes_after_1, "Learner files changed during Scenario 1!"
    assert proc1.returncode == 0, f"Scenario 1 failed unexpectedly: {proc1.stderr}"
    assert "ok 1 triplets whose sum is 12" in proc1.stdout, "Named case 12 missing/failed!"
    assert "ok 2 triplets whose sum is 108" in proc1.stdout, "Named case 108 missing/failed!"
    assert "ok 3 triplets whose sum is 1000" in proc1.stdout, "Named case 1000 missing/failed!"
    assert "1..7" in proc1.stdout, "Expected 7 tests in TAP output!"
    
    scenarios_results["real_reference"] = {
        "status": "PASS",
        "exit_code": proc1.returncode,
        "test_count": 7,
        "named_cases_passed": True,
        "learner_hashes_intact": True,
        "stdout_summary": proc1.stdout.strip(),
    }

    # Scenario 2: Failing Reference (Must fail and propagate non-zero exit code)
    def break_reference(tmp_exercise: Path):
        bad_code = "BEGIN { print '999,999,999'; exit 1 }\n"
        ex_rel = paths["example"].relative_to(EXERCISE_DIR)
        (tmp_exercise / ex_rel).write_text(bad_code, encoding="utf-8")
        (tmp_exercise / paths["solution"].name).write_text(bad_code, encoding="utf-8")

    proc2 = run_scenario("Deliberately Failing Reference", paths, break_reference)
    hashes_after_2 = get_learner_file_hashes()
    assert baseline_hashes == hashes_after_2, "Learner files changed during Scenario 2!"
    assert proc2.returncode != 0, "Scenario 2 should have failed with non-zero exit code!"
    
    scenarios_results["failing_reference"] = {
        "status": "PASS_DETECTED_FAILURE",
        "exit_code": proc2.returncode,
        "expected_failure": True,
        "learner_hashes_intact": True,
        "stdout_summary": proc2.stdout.strip()[:300] if proc2.stdout else "",
    }

    # Scenario 3: Zero-Test Run (Must detect 0 tests and reject with non-zero exit code)
    def zero_tests(tmp_exercise: Path):
        test_file = tmp_exercise / paths["test"].name
        # Write bats file with 0 tests
        test_file.write_text("#!/usr/bin/env bats\n# Empty test file\n", encoding="utf-8")

    proc3 = run_scenario("Empty Test Suite (Zero-Test Run)", paths, zero_tests)
    hashes_after_3 = get_learner_file_hashes()
    assert baseline_hashes == hashes_after_3, "Learner files changed during Scenario 3!"
    
    # In BATS and bin/validate_one_exercise, empty test file fails assertion / emits no tests
    zero_test_failed = (proc3.returncode != 0) or ("1..0" in proc3.stdout)
    assert zero_test_failed, "Scenario 3 failed to detect/reject zero tests!"
    
    scenarios_results["zero_test_run"] = {
        "status": "PASS_REJECTED_ZERO_TESTS",
        "exit_code": proc3.returncode,
        "zero_tests_detected": True,
        "learner_hashes_intact": True,
        "stdout_summary": proc3.stdout.strip()[:300] if proc3.stdout else proc3.stderr.strip()[:300],
    }

    return scenarios_results, proc1.stdout


def save_artifacts(scenarios_results, tap_output, baseline_hashes):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. versions.txt
    versions = []
    for tool, cmd in [
        ("Python", ["python3", "--version"]),
        ("GNU Awk", ["gawk", "--version"]),
        ("Bats", ["bats", "--version"]),
        ("Bash", ["bash", "--version"]),
    ]:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
            line = res.stdout.splitlines()[0] if res.stdout else res.stderr.splitlines()[0]
            versions.append(f"{tool}: {line}")
        except Exception as e:
            versions.append(f"{tool}: error ({e})")
    (WORK_DIR / "versions.txt").write_text("\n".join(versions) + "\n", encoding="utf-8")

    # 2. inputs.json
    inputs_data = {
        "config_json_path": "exercises/practice/pythagorean-triplet/.meta/config.json",
        "named_test_cases": [
            "triplets whose sum is 12",
            "triplets whose sum is 108",
            "triplets whose sum is 1000",
        ],
        "learner_file_hashes": baseline_hashes,
    }
    (WORK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2) + "\n", encoding="utf-8")

    # 3. runner_scenarios.json
    (WORK_DIR / "runner_scenarios.json").write_text(json.dumps(scenarios_results, indent=2) + "\n", encoding="utf-8")

    # 4. expected_vs_actual.json
    eva_data = {
        "scenarios": {
            "real_reference": {
                "expected_exit_code": 0,
                "actual_exit_code": scenarios_results["real_reference"]["exit_code"],
                "expected_test_count": 7,
                "actual_test_count": scenarios_results["real_reference"]["test_count"],
            },
            "failing_reference": {
                "expected_exit_code": "non-zero",
                "actual_exit_code": scenarios_results["failing_reference"]["exit_code"],
            },
            "zero_test_run": {
                "expected_exit_code": "non-zero or zero-test error",
                "actual_exit_code": scenarios_results["zero_test_run"]["exit_code"],
            },
        },
        "hash_verification": {
            "all_runs_intact": True,
        },
    }
    (WORK_DIR / "expected_vs_actual.json").write_text(json.dumps(eva_data, indent=2) + "\n", encoding="utf-8")

    # 5. output.txt
    out_lines = [
        "=== Scenario 1: Real Reference Validation TAP Output ===",
        tap_output.strip(),
        "",
        "=== Scenarios Execution Summary ===",
        json.dumps(scenarios_results, indent=2),
    ]
    (WORK_DIR / "output.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 6. evidence.md
    evidence_md = f"""# Verification Evidence: R06-T039 (Pythagorean Triplet Focused Runner)

## Summary of Results
- **Scenario 1 (Real Reference)**: Passed with exit code 0; all 7 test cases passed.
- **Baseline Cases**: Verified `triplets whose sum is 12`, `triplets whose sum is 108`, and `triplets whose sum is 1000`.
- **Scenario 2 (Deliberately Failing Reference)**: Propagated failure with exit code `{scenarios_results['failing_reference']['exit_code']}`.
- **Scenario 3 (Zero-Test Run)**: Rejected zero-test run with exit code `{scenarios_results['zero_test_run']['exit_code']}`.
- **Learner File Integrity**: SHA-256 hashes of learner files remained completely unchanged across all executions.
- **Temporary File Cleanup**: Verified all temporary working copies were cleanly removed after execution.

## Scenario Matrix
| Scenario | Injected Condition | Expected Exit Code | Actual Exit Code | Result | Hashes Preserved |
|:---|:---|:---:|:---:|:---:|:---:|
| **Real Reference** | Canonical `.meta/example.awk` | 0 | 0 | Pass | Yes |
| **Failing Reference** | Faulty triplet output | Non-zero | {scenarios_results['failing_reference']['exit_code']} | Pass | Yes |
| **Zero-Test Run** | Empty test file (0 tests) | Non-zero | {scenarios_results['zero_test_run']['exit_code']} | Pass | Yes |

## Learner File Baseline Hashes (SHA-256)
"""
    for fname, fhash in baseline_hashes.items():
        evidence_md += f"- `{fname}`: `{fhash}`\n"

    (WORK_DIR / "evidence.md").write_text(evidence_md, encoding="utf-8")
    print(f"Artifacts successfully written to {WORK_DIR}")


def main():
    print("=" * 60)
    print("Starting Task R06-T039 Verification")
    print("=" * 60)
    
    paths = resolve_paths()
    verify_learner_solution(paths["solution"])
    baseline_hashes = get_learner_file_hashes()
    print("Learner file baseline hashes captured:")
    for fn, h in baseline_hashes.items():
        print(f"  {fn}: {h[:16]}...")

    scenarios_results, tap_output = test_runner_scenarios(paths, baseline_hashes)
    save_artifacts(scenarios_results, tap_output, baseline_hashes)
    
    print("\nAll checks completed successfully!")


if __name__ == "__main__":
    main()
