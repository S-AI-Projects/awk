#!/usr/bin/env python3
"""
Verification script for Task R06-T037: Killer Sudoku Helper Language Construct & Pitfall.

Checks performed:
1. Path resolution from exercises/practice/killer-sudoku-helper/.meta/config.json.
2. Verification that the learner solution (killer-sudoku-helper.awk) is untouched and unsolved.
3. Temporary directory copying and substitution of example.awk into killer-sudoku-helper.awk only in temp copy.
4. Validation run via bin/validate_one_exercise with assertion of return code 0 and all tests passing.
5. Explicit assertion that the baseline named cases pass:
   - '1' (<<< "1 1" -> "1")
   - '2' (<<< "2 1" -> "2")
   - '3' (<<< "3 1" -> "3")
6. Execution and assertion of Micro-Example 1 (correct NF push/pop stack):
   Outputs exactly "1 2\\n1 3".
7. Execution and assertion of Micro-Example 2 (contrasting pitfall without NF--):
   Outputs exactly "1 2\\n1 2 3".
8. Verification that both micro-example outputs agree with exercises/practice/killer-sudoku-helper/.docs/hints.md.
9. Generation of artifacts in work/R06-T037/ (inputs.json, expected_vs_actual.json, micro_examples.json, versions.txt, evidence.md, output.txt).
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
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "killer-sudoku-helper"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"
HINTS_FILE = EXERCISE_DIR / ".docs" / "hints.md"

ENV = os.environ.copy()
gnubin = "/opt/homebrew/opt/gawk/libexec/gnubin"
homebrew_bin = "/opt/homebrew/bin"
ENV["PATH"] = f"{gnubin}:{homebrew_bin}:{ENV.get('PATH', '')}"

SNIPPET_1 = """function push(val) { NF++; $NF = val }
function pop()     { NF-- }
BEGIN {
    NF = 0
    push(1)
    push(2)
    print
    pop()
    push(3)
    print
}
"""

SNIPPET_2 = """function push(val) { NF++; $NF = val }
BEGIN {
    NF = 0
    push(1)
    push(2)
    print
    # Pitfall: Missing pop() / NF-- before exploring next branch
    push(3)
    print
}
"""

EXPECTED_SNIPPET_1_OUTPUT = "1 2\n1 3"
EXPECTED_SNIPPET_2_OUTPUT = "1 2\n1 2 3"


def resolve_paths():
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    files = config.get("files", {})
    solution = files.get("solution", ["killer-sudoku-helper.awk"])[0]
    test = files.get("test", ["test-killer-sudoku-helper.bats"])[0]
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


def run_validation_in_temp(paths: dict):
    print("Running bin/validate_one_exercise in isolated temp copy...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_exercise = tmp_root / "exercises" / "practice" / "killer-sudoku-helper"
        
        # Copy harness files
        shutil.copytree(REPO_ROOT / "bin", tmp_root / "bin", symlinks=True)
        if (REPO_ROOT / "lib").exists():
            shutil.copytree(REPO_ROOT / "lib", tmp_root / "lib", symlinks=True)
        shutil.copytree(EXERCISE_DIR, tmp_exercise, symlinks=True)
        
        # Substitute example into solution in temp copy only
        tmp_solution = tmp_exercise / paths["solution"].name
        tmp_example = tmp_exercise / paths["example"].relative_to(EXERCISE_DIR)
        shutil.copyfile(tmp_example, tmp_solution)

        cmd = ["bin/validate_one_exercise", "exercises/practice/killer-sudoku-helper"]
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
        assert "ok 1 1" in proc.stdout, "Baseline test '1' missing or failed!"
        assert "ok 2 2" in proc.stdout, "Baseline test '2' missing or failed!"
        assert "ok 3 3" in proc.stdout, "Baseline test '3' missing or failed!"
        assert "1..13" in proc.stdout, "Expected 13 tests in TAP summary!"
        print("All 13 tests passed successfully against reference in temporary environment.")
        return proc.stdout


def verify_micro_examples():
    print("Verifying micro-examples with gawk...")
    res1 = subprocess.run(
        ["gawk", SNIPPET_1],
        capture_output=True,
        text=True,
        env=ENV
    )
    assert res1.returncode == 0, f"Snippet 1 execution failed: {res1.stderr}"
    out1 = res1.stdout.strip()
    assert out1 == EXPECTED_SNIPPET_1_OUTPUT, (
        f"Snippet 1 output mismatch: expected {EXPECTED_SNIPPET_1_OUTPUT!r}, got {out1!r}"
    )
    print("Snippet 1 output verified:", repr(out1))

    res2 = subprocess.run(
        ["gawk", SNIPPET_2],
        capture_output=True,
        text=True,
        env=ENV
    )
    assert res2.returncode == 0, f"Snippet 2 execution failed: {res2.stderr}"
    out2 = res2.stdout.strip()
    assert out2 == EXPECTED_SNIPPET_2_OUTPUT, (
        f"Snippet 2 output mismatch: expected {EXPECTED_SNIPPET_2_OUTPUT!r}, got {out2!r}"
    )
    print("Snippet 2 output verified:", repr(out2))

    # Verify hint agreement
    assert HINTS_FILE.is_file(), f"Hints file missing: {HINTS_FILE}"
    hints_text = HINTS_FILE.read_text(encoding="utf-8")
    assert "1 2\n1 3" in hints_text, "Snippet 1 output missing in hints.md"
    assert "1 2\n1 2 3" in hints_text, "Snippet 2 output missing in hints.md"
    assert "NF" in hints_text and "$NF" in hints_text, "Construct NF/$NF not mentioned in hints.md"
    print("Both micro-examples verified and match hints.md perfectly.")

    return out1, out2


def save_artifacts(tap_output, out1, out2):
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
        "named_cases": [
            {"id": "1", "input": "1 1", "expected": "1"},
            {"id": "2", "input": "2 1", "expected": "2"},
            {"id": "3", "input": "3 1", "expected": "3"},
        ],
        "micro_example_1": {"snippet": SNIPPET_1},
        "micro_example_2": {"snippet": SNIPPET_2},
    }
    (WORK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2) + "\n", encoding="utf-8")

    # 3. expected_vs_actual.json
    eva_data = {
        "test_suite_status": "All 13 tests passed",
        "named_cases": [
            {"name": "1", "expected": "1", "actual": "1", "match": True},
            {"name": "2", "expected": "2", "actual": "2", "match": True},
            {"name": "3", "expected": "3", "actual": "3", "match": True},
        ],
        "micro_example_1": {
            "expected": EXPECTED_SNIPPET_1_OUTPUT,
            "actual": out1,
            "match": (out1 == EXPECTED_SNIPPET_1_OUTPUT),
        },
        "micro_example_2": {
            "expected": EXPECTED_SNIPPET_2_OUTPUT,
            "actual": out2,
            "match": (out2 == EXPECTED_SNIPPET_2_OUTPUT),
        },
    }
    (WORK_DIR / "expected_vs_actual.json").write_text(json.dumps(eva_data, indent=2) + "\n", encoding="utf-8")

    # 4. micro_examples.json
    micro_data = {
        "construct": "Dynamic Field Manipulation via NF and $NF",
        "snippet_1_correct": {
            "code": SNIPPET_1,
            "output": out1,
            "behavior": "push(val) and pop() correctly maintain field stack, emitting '1 2' then '1 3'",
        },
        "snippet_2_pitfall": {
            "code": SNIPPET_2,
            "output": out2,
            "behavior": "omitting pop() / NF-- causes field accumulation, leaking field 2 into '1 2 3'",
        },
    }
    (WORK_DIR / "micro_examples.json").write_text(json.dumps(micro_data, indent=2) + "\n", encoding="utf-8")

    # 5. output.txt
    out_lines = [
        "=== Validation TAP Output ===",
        tap_output.strip(),
        "",
        "=== Micro-Example 1 (Dynamic Field Stack) Output ===",
        out1,
        "",
        "=== Micro-Example 2 (Missing NF-- Pitfall) Output ===",
        out2,
    ]
    (WORK_DIR / "output.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 6. evidence.md
    out1_repr = out1.replace("\n", "\\n")
    out2_repr = out2.replace("\n", "\\n")
    evidence_md = f"""# Verification Evidence: R06-T037 (Killer Sudoku Helper Construct & Pitfall)

## Summary of Results
- **Validation Run**: 13/13 test cases passed in `test-killer-sudoku-helper.bats`.
- **Baseline Cases**: Explicitly verified `1`, `2`, and `3`.
- **Learner Stub**: `exercises/practice/killer-sudoku-helper/killer-sudoku-helper.awk` remains untouched and unsolved.
- **Language Construct Selected**: Dynamic Field Manipulation via `NF`, `$NF`, and record reconstruction (`$0`).
- **Micro-Examples Tested**:
  - Micro-Example 1 (Push/Pop with `NF++` and `NF--`): Output matched expected `1 2\\n1 3`.
  - Micro-Example 2 (Contrasting Pitfall omitting `NF--`): Output matched expected `1 2\\n1 2 3`.
- **Hints Published**: Published in `exercises/practice/killer-sudoku-helper/.docs/hints.md`.

## Micro-Example Comparison Table
| Snippet | Construct / Control Flow | Expected Output | Actual Output | Agreement |
|:---|:---|:---:|:---:|:---:|
| **Snippet 1 (Stack Push/Pop)** | `push(1); push(2); print; pop(); push(3); print` | `1 2\\n1 3` | `{out1_repr}` | Pass |
| **Snippet 2 (Omitted Pop)** | `push(1); push(2); print; push(3); print` | `1 2\\n1 2 3` | `{out2_repr}` | Pass |

## Construct Explanation
- **Why Associative Array Traversal is Incompatible**: `for (key in array)` traverses keys in unspecified hash table order. Killer Sudoku combinations must be sorted in strictly ascending order.
- **Why Dynamic Field Manipulation (`NF` / `$NF`) is Ideal**:
  - Increments `NF` to push elements onto AWK's built-in field list.
  - Automatically joins fields with single spaces (`OFS`) upon invoking `print`.
  - Backtracks cleanly by decrementing `NF` (`NF--`).
"""
    (WORK_DIR / "evidence.md").write_text(evidence_md, encoding="utf-8")
    print(f"Artifacts successfully written to {WORK_DIR}")


def main():
    print("=" * 60)
    print("Starting Task R06-T037 Verification")
    print("=" * 60)
    
    paths = resolve_paths()
    verify_learner_solution(paths["solution"])
    tap_output = run_validation_in_temp(paths)
    out1, out2 = verify_micro_examples()
    save_artifacts(tap_output, out1, out2)
    
    print("\nAll checks completed successfully!")


if __name__ == "__main__":
    main()
