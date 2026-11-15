# R06-T050 — Scrabble Score Contract Evidence

## Decision Table Verification
| Case | Input | Expected Output | Actual Output | Status |
|---|---|---|---|---|
| lowercase letter | `a` | `A,1` | `A,1` | PASS |
| uppercase letter | `A` | `A,1` | `A,1` | PASS |
| valuable letter | `f` | `F,4` | `F,4` | PASS |

## Test Suite Summary
- Validator Exit Code: 0
- Total Tests Executed: 12
- Passed Tests: 12
- Named cases verified:
  - `lowercase letter`
  - `uppercase letter`
  - `valuable letter`

## Tool Versions
- GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)
- Bats 1.14.0
- GNU bash, version 5.3.20(1)-release (aarch64-apple-darwin27.0.0)
- jq-1.7.1-apple
- Python 3.14.7
