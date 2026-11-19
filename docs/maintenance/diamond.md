# Diamond Maintenance & Metadata Specification

## 1. Overview & Purpose

This document maps and verifies the files declared in `exercises/practice/diamond/.meta/config.json` and explains how the track test runner (`bin/validate_one_exercise`) resolves and executes them.

---

## 2. File Role Map

The `files` object in `exercises/practice/diamond/.meta/config.json` defines the official roles for all files in this exercise:

| Role | Declared Relative Path | Full Path Within Exercise | Classification | Description |
|---|---|---|---|---|
| `solution` | `diamond.awk` | `exercises/practice/diamond/diamond.awk` | Learner Stub | Starter template provided to learners. Must remain an unsolved stub in the repository. |
| `test` | `test-diamond.bats` | `exercises/practice/diamond/test-diamond.bats` | Generated Test Suite | Bats test suite generated from canonical problem-specifications. |
| `example` | `.meta/example.awk` | `exercises/practice/diamond/.meta/example.awk` | Reference Implementation | Maintained reference solution used by continuous integration to validate test suite. |

### Generated vs. Hand-Maintained Artifacts
- **Canonical / Generated Artifacts**: `test-diamond.bats` is generated from problem specifications canonical data via `template.j2` and `.meta/tests.toml`. Any canonical changes must flow through test generation rather than direct edits.
- **Maintained Reference Files**: `.meta/example.awk` and `diamond.awk` are maintained by track contributors.

---

## 3. Runner Path Resolution Mechanism

When executing `bin/validate_one_exercise exercises/practice/diamond`:
1. **Metadata Ingestion**: The runner reads `exercises/practice/diamond/.meta/config.json` using `jq`.
2. **Key Extraction**:
   - `solution` path is resolved via `.files.solution[0]` (`diamond.awk`).
   - `test` path is resolved via `.files.test[0]` (`test-diamond.bats`).
   - `example` reference path is resolved via `.files.example[0]` (`.meta/example.awk`).
3. **Sandbox Provisioning**: Creates an isolated temporary directory via `mktemp -d`.
4. **Artifact Staging**: Copies the reference implementation (`.meta/example.awk`) into the location of the solution stub (`${dir}/${stub}`), along with `${tests}` and `bats-extra.bash`.
5. **Execution**: Evaluates the test suite (`BATS_RUN_SKIPPED=true bats "${tests}"`) inside the isolated sandbox, ensuring the working tree remains untouched.

---

## 4. Path Validation & Security Rules

To ensure repository integrity and prevent sandbox escapes:
- Every declared file must resolve strictly inside `exercises/practice/diamond`.
- Path traversal sequences (such as `..` components or absolute paths) are rejected.
- Declared files must exist on disk as regular files.

---

## 5. Validation Command

```bash
bin/validate_one_exercise exercises/practice/diamond
```

All 5 test cases pass cleanly against the reference implementation:
1. `Degenerate case with a single 'A' row`
2. `Degenerate case with no row containing 3 distinct groups of spaces`
3. `Smallest non-degenerate case with odd diamond side length`
4. `Smallest non-degenerate case with even diamond side length`
5. `Largest possible diamond`
