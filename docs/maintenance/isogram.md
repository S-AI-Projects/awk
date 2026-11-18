# Isogram Maintenance

## Purpose
This document explains the isolated test runner for the Isogram exercise in the AWK track.

## Isolated Runner Design
The runner executes the maintained reference implementation without modifying the learner files in the repository.

To achieve complete isolation:
1. It copies the exercise and repository files into a fresh temporary directory using `tempfile.TemporaryDirectory`.
2. It substitutes `.meta/example.awk` onto the learner stub path (`isogram.awk`) strictly inside the temporary copy.
3. It runs `bin/validate_one_exercise exercises/practice/isogram` inside the sandbox.
4. It parses test outputs (TAP protocol) to verify test counts and failures.
5. It computes the SHA256 cryptographic hash of the working tree learner files before and after each run to ensure the working tree is never touched or modified.

## Test Execution Modes
The runner supports three test modes to ensure robust error propagation:
* **Standard Mode:** Executes the official reference implementation against the full test suite. Expects all 14 tests to pass with exit code 0.
* **Failing Reference Mode:** Simulates a broken solution to confirm that test assertions properly fail and return a non zero exit code.
* **Empty Suite Mode:** Tests behavior when no tests are executed, confirming that a zero test run fails validation.

## Tool Requirements
* GNU Awk (`gawk`)
* Bats (`bats-core`)
* Bash (version 4 or later)
* Python 3
* `jq`

## Validation Command
```bash
bin/validate_one_exercise exercises/practice/isogram
```
All 14 test cases pass cleanly.
