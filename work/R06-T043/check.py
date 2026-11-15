#!/usr/bin/env python3

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE_REL = Path("exercises/practice/two-fer")
VALIDATOR_REL = Path("bin/validate_one_exercise")
EVIDENCE = Path(__file__).resolve().parent / "evidence.md"


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


def version(command):
    result = run(command)
    return result.stdout.splitlines()[0] if result.stdout else result.stderr.splitlines()[0]


def main():
    original_exercise = ROOT / EXERCISE_REL
    config_path = original_exercise / ".meta/config.json"

    config = json.loads(config_path.read_text())
    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]
    stub = original_exercise / solution_rel
    original_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    with tempfile.TemporaryDirectory(prefix="R06-T043-") as temp:
        temp_root = Path(temp)
        copied_exercise = temp_root / EXERCISE_REL

        # copytree includes hidden files and directories.
        shutil.copytree(original_exercise, copied_exercise)

        # The validator needs to run from a repository-like root.
        copied_validator = temp_root / VALIDATOR_REL
        copied_validator.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / VALIDATOR_REL, copied_validator)

        validator_command = [
            "bash",
            str(VALIDATOR_REL),
            str(EXERCISE_REL),
        ]

        # First prove that the original reference passes.
        baseline = run(validator_command, cwd=temp_root)
        baseline_results = test_results(baseline.stdout)

        # Mutate only the copied reference implementation.
        example_file = copied_exercise / example_rel
        original_text = example_file.read_text()

        pattern = re.compile(r"(?m)^NF(\s+)\{name = \$0\}$")
        mutated_text, replacements = pattern.subn(
            r"NR\1{name = $0}",
            original_text,
        )

        if replacements != 1:
            raise RuntimeError(
                "Expected to replace exactly one NF rule; "
                f"replaced {replacements}."
            )

        example_file.write_text(mutated_text)

        # Run the same repository validator against the mutation.
        mutant = run(validator_command, cwd=temp_root)
        mutant_results = test_results(mutant.stdout)

        # Independently capture the mutant's output for a blank record.
        empty_file = copied_exercise / "empty-input.txt"
        empty_file.write_text("\n")

        actual = run(
            ["gawk", "-f", str(example_file), str(empty_file)],
            cwd=copied_exercise,
        )

        expected_results = [
            ("ok", "no file given"),
            ("not ok", "empty file given"),
            ("ok", "a name given"),
            ("ok", "name with a space"),
        ]

        checks = {
            "baseline_returncode": baseline.returncode,
            "baseline_results": baseline_results,
            "mutant_returncode": mutant.returncode,
            "mutant_results": mutant_results,
            "actual_returncode": actual.returncode,
            "actual_output": actual.stdout.rstrip("\n"),
        }

        evidence = f"""# R06-T043 — Two Fer mutation check

## Mutation

Changed the copied reference rule from:

`NF {{name = $0}}`

to:

`NR {{name = $0}}`

The working-tree reference implementation was not modified.

## Baseline

Validator exit code: {baseline.returncode}

```text
{baseline.stdout}{baseline.stderr}
```

## Mutated implementation

Validator exit code: {mutant.returncode}

```text
{mutant.stdout}{mutant.stderr}
```

## Distinguishing input

Input file contents: one newline (one blank record).

Expected output: `One for you, one for me.`

Actual output: `{actual.stdout.rstrip(chr(10))}`

## Tool versions

- {version(["gawk", "--version"])}
- {version(["bats", "--version"])}
- {version(["bash", "--version"])}
- {version(["jq", "--version"])}
- {version(["python3", "--version"])}
"""

        EVIDENCE.write_text(evidence)

        if baseline.returncode != 0 or len(baseline_results) != 4:
            raise SystemExit("FAIL: the unmodified reference did not pass all four tests.")

        if any(status != "ok" for status, _ in baseline_results):
            raise SystemExit("FAIL: a baseline test did not pass.")

        if mutant.returncode == 0:
            raise SystemExit("FAIL: the mutation was not rejected by the test suite.")

        if mutant_results != expected_results:
            raise SystemExit(
                "FAIL: the mutation did not produce the expected test results.\n"
                f"Observed: {mutant_results}"
            )

        if actual.returncode != 0:
            raise SystemExit("FAIL: could not execute the mutated reference.")

        expected_output = "One for you, one for me."
        if actual.stdout.rstrip("\n") == expected_output:
            raise SystemExit("FAIL: the mutant unexpectedly produced the expected output.")

        if hashlib.sha256(stub.read_bytes()).hexdigest() != original_stub_hash:
            raise SystemExit("FAIL: original learner solution was modified.")

        print("PASS: original reference passes all four tests.")
        print("PASS: mutation is rejected by 'empty file given'.")
        print(f"Expected output: {expected_output}")
        print(f"Actual output:   {actual.stdout.rstrip(chr(10))}")
        print("PASS: Original learner solution remains unchanged.")
        print(f"Evidence saved to: {EVIDENCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
