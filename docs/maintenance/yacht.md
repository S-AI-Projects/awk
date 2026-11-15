# Yacht — Isolated Test Runner Documentation

## Overview
The `yacht` maintenance runner verifies the reference implementation in an isolated temporary directory, safeguarding learner starter files against accidental modification or pollution.

## Prerequisites and Tool Requirements
The runner requires the standard track development tools:
- **Python 3**: Execution environment for `tools/course_checks/r06-t049.py`
- **GNU Awk (`gawk`)**: Track AWK interpreter
- **Bats (`bats`)**: Core test runner for `.bats` test suites
- **GNU Bash (`bash`)**: Subprocess execution shell for `bin/validate_one_exercise`
- **jq**: JSON parser used to inspect `.meta/config.json`

## Isolation and Integrity Design
1. **Dynamic Path Resolution**: Reads `exercises/practice/yacht/.meta/config.json` to resolve:
   - Solution stub: `yacht.awk`
   - Test suite: `test-yacht.bats`
   - Reference solution: `.meta/example.awk`
2. **SHA-256 Hash Verification**: Computes the cryptographic checksum of the learner stub `yacht.awk` prior to execution. A post-execution assertion ensures that the stub was never overwritten, even if test execution fails or encounters a runtime error.
3. **Scratch Environment**: Creates a temporary directory via `tempfile.mkdtemp()`, copies the exercise and validator files, and substitutes the reference solution only inside the sandbox.
4. **Automatic Cleanup**: A `finally` block guarantees directory cleanup upon termination.

## Usage Commands
Standard verification of the reference implementation (29 test cases):
```bash
python3 tools/course_checks/r06-t049.py
```

Deliberately failing reference verification:
```bash
python3 tools/course_checks/r06-t049.py --failing-reference
```

Empty test selection verification:
```bash
python3 tools/course_checks/r06-t049.py --empty-tests
```

Full automated verification check:
```bash
python3 work/R06-T049/check.py
```
