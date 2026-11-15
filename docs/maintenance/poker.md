# Poker — Maintenance File-Role Mapping

## Purpose
This document maps and verifies the files declared in `exercises/practice/poker/.meta/config.json`, explains how the Exercism test runner locates them, and distinguishes handwritten maintenance files from generated test artifacts.

## File-Role Map
| Role | Declared Relative Path | Full Workspace Path | Artifact Classification | Purpose |
|---|---|---|---|---|
| `solution` | `poker.awk` | `exercises/practice/poker/poker.awk` | Student Stub (Maintained) | Unsolved starter template distributed to learners. |
| `test` | `test-poker.bats` | `exercises/practice/poker/test-poker.bats` | Generated Test Suite | BATS test suite generated from canonical data. |
| `example` | `.meta/example.awk` | `exercises/practice/poker/.meta/example.awk` | Reference Solution (Maintained) | Canonical solution used by `bin/validate_one_exercise` to verify tests. |
| (Metadata) | `.meta/config.json` | `exercises/practice/poker/.meta/config.json` | Exercise Config | Track configuration specifying author and file roles. |
| (Metadata) | `.meta/tests.toml` | `exercises/practice/poker/.meta/tests.toml` | Test Generator Metadata | Tracks canonical UUID inclusion/exclusion status. |

## How the Test Runner Finds Files
The test runner (`bin/validate_one_exercise`) parses `.meta/config.json` using `jq`:
- `stub=$(jq -r '.files.solution[0]' "$config")` -> resolves `poker.awk`
- `tests=$(jq -r '.files.test[0]' "$config")` -> resolves `test-poker.bats`
- `solution=$(jq -r '.files.example[0] // .files.exemplar[0]' "$config")` -> resolves `.meta/example.awk`

The runner creates a temporary directory, copies `example.awk` into the location of `poker.awk`, copies `test-poker.bats`, symlinks support libraries (`bats-extra.bash`), and executes `BATS_RUN_SKIPPED=true bats test-poker.bats`.

## Reproducible Validation Command
To validate the path resolution and configuration consistency against both real files and invalid test fixtures:
```bash
python3 tools/course_checks/r06-t048.py
```
To validate that the reference passes all 37 test cases in an isolated temporary directory:
```bash
python3 work/R06-T048/check.py
```
