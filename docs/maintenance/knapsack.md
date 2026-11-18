# Knapsack Maintenance

## Purpose
This document maps and verifies the files declared in `exercises/practice/knapsack/.meta/config.json` and explains how the test runner locates and executes them.

## File Role Map

The `files` object in `.meta/config.json` defines the official roles for all files in this exercise:

| Role | Declared Relative Path | Full Path Within Exercise | Classification | Description |
|---|---|---|---|---|
| `solution` | `knapsack.awk` | `exercises/practice/knapsack/knapsack.awk` | Learner Stub | Starter template provided to learners. Must remain unsolved in the repository. |
| `test` | `test-knapsack.bats` | `exercises/practice/knapsack/test-knapsack.bats` | Generated Test Suite | Bats test suite generated from canonical specifications. |
| `example` | `.meta/example.awk` | `exercises/practice/knapsack/.meta/example.awk` | Reference Implementation | Maintained reference solution used by continuous integration to validate test suite. |

## Runner Path Resolution Mechanism
When running validation through `bin/validate_one_exercise exercises/practice/knapsack`:
1. The script parses `./.meta/config.json` using `jq`.
2. It retrieves the solution file path via `.files.solution[0]` and reference path via `.files.example[0]`.
3. It creates an isolated temporary directory via `mktemp -d`.
4. It copies the reference solution into the location of the solution stub inside the temporary directory.
5. It copies `test-knapsack.bats` and `bats-extra.bash` into the temporary directory.
6. Bats runs the test suite against the reference solution without altering any files in the working tree.

## Path Validation Rules
To ensure security and reliability, all declared paths must:
* Resolve strictly inside `exercises/practice/knapsack`.
* Reject any directory traversal patterns such as `..` or absolute paths.
* Correspond to real, existing files on disk.

## Validation Command
```bash
bin/validate_one_exercise exercises/practice/knapsack
```
All 7 test cases pass cleanly against the reference implementation.
