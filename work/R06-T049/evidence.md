# R06-T049 — Yacht Isolated Test Runner Evidence

## Test Runner Execution Matrix
| Configuration | Command | Expected Outcome | Observed Outcome | Stub Hash Intact | Status |
|---|---|---|---|---|---|
| Normal Reference | `python3 tools/course_checks/r06-t049.py` | Exit 0, 29 tests pass | PASS: All 29 yacht tests passed in isolated temporary copy.
PASS: Learner stub was not altered. | Yes | PASS |
| Failing Reference | `python3 tools/course_checks/r06-t049.py --failing-reference` | Non-zero child exit caught | PASS: Failing reference produced non-zero exit code (1). | Yes | PASS |
| Empty Test Suite | `python3 tools/course_checks/r06-t049.py --empty-tests` | Zero-test error caught | PASS: Empty tests produced expected failure/zero-count. | Yes | PASS |

## Test Suite Execution Details
- Total Cases: 29
- Passed Cases: 29
- Named cases verified:
  - `Yacht`
  - `Not Yacht`
  - `Ones`

## Cryptographic Stub Verification
- Initial SHA256: `f24fb8f97ca628345685ef6e78f349d5cfe86bee162f48c84ce2842abed28552`
- Post-Test 1 SHA256: `f24fb8f97ca628345685ef6e78f349d5cfe86bee162f48c84ce2842abed28552`
- Post-Test 2 SHA256: `f24fb8f97ca628345685ef6e78f349d5cfe86bee162f48c84ce2842abed28552`
- Post-Test 3 SHA256: `f24fb8f97ca628345685ef6e78f349d5cfe86bee162f48c84ce2842abed28552`
- Final SHA256: `f24fb8f97ca628345685ef6e78f349d5cfe86bee162f48c84ce2842abed28552`

## Tool Versions
- GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)
- Bats 1.14.0
- GNU bash, version 5.3.20(1)-release (aarch64-apple-darwin27.0.0)
- jq-1.7.1-apple
- Python 3.14.7
