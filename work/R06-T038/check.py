#!/usr/bin/env python3
"""
Verification script for Task R06-T038: Rotational Cipher Metadata Verification & Runner Tracing.

Checks performed:
1. Strict schema validation of exercises/practice/rotational-cipher/.meta/config.json:
   - Parse files object (solution, test, example, editor).
   - Resolve each path relative to exercise directory.
   - Reject parent traversal (e.g. '..', absolute paths, escaping exercise root).
   - Check that every declared file exists.
2. Negative fixture validation (testing the checker with deliberately invalid metadata):
   - Fixture 1: missing-reference (example pointing to nonexistent file) -> fails with FileNotFoundError.
   - Fixture 2: missing-test (test pointing to nonexistent file) -> fails with FileNotFoundError.
   - Fixture 3: outside-exercise (path traversing to parent '../../bin/pr') -> fails with ValueError.
3. Verification that real metadata passes without error.
4. Verification that learner stub (rotational-cipher.awk) is untouched and unsolved.
5. Temporary directory copying and substitution of example.awk into rotational-cipher.awk only in temp copy.
6. Validation run via bin/validate_one_exercise with assertion of return code 0 and all tests passing.
7. Explicit assertion that the baseline named cases pass:
   - 'rotate a by 0, same output as input'
   - 'rotate a by 1'
   - 'rotate a by 26, same output as input'
8. Generation of artifacts in work/R06-T038/ (inputs.json, expected_vs_actual.json, metadata_validation.json, versions.txt, evidence.md, output.txt).
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path(__file__).resolve().parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "rotational-cipher"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"

ENV = os.environ.copy()
gnubin = "/opt/homebrew/opt/gawk/libexec/gnubin"
homebrew_bin = "/opt/homebrew/bin"
ENV["PATH"] = f"{gnubin}:{homebrew_bin}:{ENV.get('PATH', '')}"


def validate_exercise_metadata(exercise_root: Path, config_path: Path):
    """
    Parses .files object from config.json, resolves each path,
    rejects parent traversal, and asserts file existence.
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file missing: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    files_obj = config.get("files")
    if not isinstance(files_obj, dict):
        raise ValueError(f"Missing or invalid 'files' object in {config_path}")

    required_keys = ["solution", "test", "example"]
    for key in required_keys:
        if key not in files_obj or not files_obj[key]:
            raise ValueError(f"Required key '{key}' missing from 'files' in {config_path}")

    resolved_files = {}
    exercise_root_resolved = exercise_root.resolve()

    for category, file_list in files_obj.items():
        resolved_files[category] = []
        for rel_path_str in file_list:
            # Check for illegal path traversal constructs
            if ".." in Path(rel_path_str).parts:
                raise ValueError(
                    f"Parent traversal '..' forbidden in path: category='{category}', path='{rel_path_str}'"
                )
            if os.path.isabs(rel_path_str):
                raise ValueError(
                    f"Absolute path forbidden: category='{category}', path='{rel_path_str}'"
                )

            # Resolve path relative to exercise root
            target_path = (exercise_root / rel_path_str).resolve()

            # Ensure resolved target is within exercise root
            try:
                target_path.relative_to(exercise_root_resolved)
            except ValueError:
                raise ValueError(
                    f"Path escapes exercise root: category='{category}', path='{rel_path_str}'"
                )

            # Ensure file exists
            if not target_path.is_file():
                raise FileNotFoundError(
                    f"Declared file does not exist: category='{category}', path='{rel_path_str}' (resolved to {target_path})"
                )

            resolved_files[category].append(str(target_path))

    return resolved_files


def test_metadata_fixtures():
    """
    Tests the validator against real metadata and three synthetic invalid fixtures:
    1. missing-reference
    2. missing-test
    3. outside-exercise
    """
    print("Testing metadata validator against real and negative fixtures...")
    fixtures_results = {}

    # 1. Real Metadata Check
    try:
        resolved = validate_exercise_metadata(EXERCISE_DIR, CONFIG_FILE)
        fixtures_results["real_config"] = {
            "status": "PASS",
            "message": "Real metadata resolved all declared files inside exercise root.",
            "resolved_files": resolved,
        }
        print("  [PASS] Real config.json validated successfully.")
    except Exception as e:
        fixtures_results["real_config"] = {"status": "FAIL", "error": str(e)}
        raise AssertionError(f"Real config.json failed validation: {e}")

    # 2. Fixture: Missing Reference
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_ex = Path(tmpdir) / "exercise"
        shutil.copytree(EXERCISE_DIR, tmp_ex, symlinks=True)
        tmp_cfg = tmp_ex / ".meta" / "config.json"
        with open(tmp_cfg, "r", encoding="utf-8") as f:
            cfg_data = json.load(f)
        cfg_data["files"]["example"] = [".meta/nonexistent_example.awk"]
        with open(tmp_cfg, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=2)

        try:
            validate_exercise_metadata(tmp_ex, tmp_cfg)
            raise AssertionError("Validator failed to reject missing reference file!")
        except FileNotFoundError as e:
            fixtures_results["missing_reference_fixture"] = {
                "status": "PASS_REJECTED",
                "caught_exception": type(e).__name__,
                "message": str(e),
            }
            print(f"  [PASS_REJECTED] missing-reference correctly rejected: {e}")

    # 3. Fixture: Missing Test
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_ex = Path(tmpdir) / "exercise"
        shutil.copytree(EXERCISE_DIR, tmp_ex, symlinks=True)
        tmp_cfg = tmp_ex / ".meta" / "config.json"
        with open(tmp_cfg, "r", encoding="utf-8") as f:
            cfg_data = json.load(f)
        cfg_data["files"]["test"] = ["missing-test.bats"]
        with open(tmp_cfg, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=2)

        try:
            validate_exercise_metadata(tmp_ex, tmp_cfg)
            raise AssertionError("Validator failed to reject missing test file!")
        except FileNotFoundError as e:
            fixtures_results["missing_test_fixture"] = {
                "status": "PASS_REJECTED",
                "caught_exception": type(e).__name__,
                "message": str(e),
            }
            print(f"  [PASS_REJECTED] missing-test correctly rejected: {e}")

    # 4. Fixture: Outside Exercise (Parent Traversal)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_ex = Path(tmpdir) / "exercise"
        shutil.copytree(EXERCISE_DIR, tmp_ex, symlinks=True)
        tmp_cfg = tmp_ex / ".meta" / "config.json"
        with open(tmp_cfg, "r", encoding="utf-8") as f:
            cfg_data = json.load(f)
        cfg_data["files"]["solution"] = ["../../bin/pr"]
        with open(tmp_cfg, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=2)

        try:
            validate_exercise_metadata(tmp_ex, tmp_cfg)
            raise AssertionError("Validator failed to reject outside exercise path!")
        except ValueError as e:
            fixtures_results["outside_exercise_fixture"] = {
                "status": "PASS_REJECTED",
                "caught_exception": type(e).__name__,
                "message": str(e),
            }
            print(f"  [PASS_REJECTED] outside-exercise correctly rejected: {e}")

    return fixtures_results


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


def run_validation_in_temp():
    print("Running bin/validate_one_exercise in isolated temp copy...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_exercise = tmp_root / "exercises" / "practice" / "rotational-cipher"
        
        # Copy harness files
        shutil.copytree(REPO_ROOT / "bin", tmp_root / "bin", symlinks=True)
        if (REPO_ROOT / "lib").exists():
            shutil.copytree(REPO_ROOT / "lib", tmp_root / "lib", symlinks=True)
        shutil.copytree(EXERCISE_DIR, tmp_exercise, symlinks=True)
        
        # Substitute example into solution in temp copy only
        shutil.copyfile(tmp_exercise / ".meta" / "example.awk", tmp_exercise / "rotational-cipher.awk")

        cmd = ["bin/validate_one_exercise", "exercises/practice/rotational-cipher"]
        proc = subprocess.run(
            cmd,
            cwd=str(tmp_root),
            capture_output=True,
            text=True,
            env=ENV
        )

        print("Validation process output:")
        print(proc.stdout)
        if proc.stderr:
            print("Stderr:", proc.stderr)

        assert proc.returncode == 0, f"Validation failed with exit code {proc.returncode}"
        assert "ok 1 rotate a by 0, same output as input" in proc.stdout, (
            "Baseline test 'rotate a by 0, same output as input' missing or failed!"
        )
        assert "ok 2 rotate a by 1" in proc.stdout, (
            "Baseline test 'rotate a by 1' missing or failed!"
        )
        assert "ok 3 rotate a by 26, same output as input" in proc.stdout, (
            "Baseline test 'rotate a by 26, same output as input' missing or failed!"
        )
        assert "1..10" in proc.stdout, "Expected 10 tests in TAP summary!"
        print("All 10 tests passed successfully against reference in temporary environment.")
        return proc.stdout


def save_artifacts(fixtures_results, tap_output):
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
        "config_json_path": "exercises/practice/rotational-cipher/.meta/config.json",
        "named_test_cases": [
            "rotate a by 0, same output as input",
            "rotate a by 1",
            "rotate a by 26, same output as input",
        ],
        "test_fixtures": [
            "real_config",
            "missing_reference_fixture",
            "missing_test_fixture",
            "outside_exercise_fixture",
        ],
    }
    (WORK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2) + "\n", encoding="utf-8")

    # 3. metadata_validation.json
    (WORK_DIR / "metadata_validation.json").write_text(json.dumps(fixtures_results, indent=2) + "\n", encoding="utf-8")

    # 4. expected_vs_actual.json
    eva_data = {
        "test_suite": {
            "total_cases": 10,
            "status": "PASS",
            "named_cases": {
                "rotate a by 0, same output as input": "PASS",
                "rotate a by 1": "PASS",
                "rotate a by 26, same output as input": "PASS",
            },
        },
        "metadata_fixtures": {
            "real_config": {"expected": "PASS", "actual": fixtures_results["real_config"]["status"]},
            "missing_reference": {"expected": "PASS_REJECTED", "actual": fixtures_results["missing_reference_fixture"]["status"]},
            "missing_test": {"expected": "PASS_REJECTED", "actual": fixtures_results["missing_test_fixture"]["status"]},
            "outside_exercise": {"expected": "PASS_REJECTED", "actual": fixtures_results["outside_exercise_fixture"]["status"]},
        },
    }
    (WORK_DIR / "expected_vs_actual.json").write_text(json.dumps(eva_data, indent=2) + "\n", encoding="utf-8")

    # 5. output.txt
    out_lines = [
        "=== Validation TAP Output ===",
        tap_output.strip(),
        "",
        "=== Metadata Fixture Evaluation ===",
        json.dumps(fixtures_results, indent=2),
    ]
    (WORK_DIR / "output.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 6. evidence.md
    evidence_md = f"""# Verification Evidence: R06-T038 (Rotational Cipher Metadata & Runner Verification)

## Summary of Results
- **Validation Run**: 10/10 test cases passed in `test-rotational-cipher.bats`.
- **Baseline Cases**: Verified `rotate a by 0, same output as input`, `rotate a by 1`, and `rotate a by 26, same output as input`.
- **Learner Stub**: `exercises/practice/rotational-cipher/rotational-cipher.awk` remains untouched and unsolved.
- **Real Metadata**: Validated `exercises/practice/rotational-cipher/.meta/config.json`. All paths resolve cleanly within the exercise directory.
- **Negative Fixtures**: All 3 deliberate invalid fixtures failed for the intended reasons:
  - `missing-reference`: Rejected with `FileNotFoundError`.
  - `missing-test`: Rejected with `FileNotFoundError`.
  - `outside-exercise`: Rejected with `ValueError` (parent traversal detected).

## Metadata Validation Results
| Fixture | Target Mutation | Expected Status | Actual Status | Result |
|:---|:---|:---:|:---:|:---:|
| **Real Config** | Authoritative `config.json` | `PASS` | `{fixtures_results['real_config']['status']}` | Pass |
| **Missing Reference** | `.meta/nonexistent_example.awk` | `PASS_REJECTED` | `{fixtures_results['missing_reference_fixture']['status']}` | Pass |
| **Missing Test** | `missing-test.bats` | `PASS_REJECTED` | `{fixtures_results['missing_test_fixture']['status']}` | Pass |
| **Outside Exercise** | `../../bin/pr` | `PASS_REJECTED` | `{fixtures_results['outside_exercise_fixture']['status']}` | Pass |

## Runner File Resolution Trace
1. Runner reads `exercises/practice/rotational-cipher/.meta/config.json`.
2. `stub=$(jq -r '.files.solution[0]' "$config")` resolves to `rotational-cipher.awk`.
3. `tests=$(jq -r '.files.test[0]' "$config")` resolves to `test-rotational-cipher.bats`.
4. `solution=$(jq -r '.files.example[0] // .files.exemplar[0]' "$config")` resolves to `.meta/example.awk`.
5. In temporary execution environment, runner copies `$solution` into `$stub` and invokes `bats "$tests"`.
"""
    (WORK_DIR / "evidence.md").write_text(evidence_md, encoding="utf-8")
    print(f"Artifacts successfully written to {WORK_DIR}")


def main():
    print("=" * 60)
    print("Starting Task R06-T038 Verification")
    print("=" * 60)
    
    fixtures_results = test_metadata_fixtures()
    verify_learner_solution(EXERCISE_DIR / "rotational-cipher.awk")
    tap_output = run_validation_in_temp()
    save_artifacts(fixtures_results, tap_output)
    
    print("\nAll checks completed successfully!")


if __name__ == "__main__":
    main()
