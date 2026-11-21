# Verification Evidence: R06-T038 (Rotational Cipher Metadata & Runner Verification)

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
| **Real Config** | Authoritative `config.json` | `PASS` | `PASS` | Pass |
| **Missing Reference** | `.meta/nonexistent_example.awk` | `PASS_REJECTED` | `PASS_REJECTED` | Pass |
| **Missing Test** | `missing-test.bats` | `PASS_REJECTED` | `PASS_REJECTED` | Pass |
| **Outside Exercise** | `../../bin/pr` | `PASS_REJECTED` | `PASS_REJECTED` | Pass |

## Runner File Resolution Trace
1. Runner reads `exercises/practice/rotational-cipher/.meta/config.json`.
2. `stub=$(jq -r '.files.solution[0]' "$config")` resolves to `rotational-cipher.awk`.
3. `tests=$(jq -r '.files.test[0]' "$config")` resolves to `test-rotational-cipher.bats`.
4. `solution=$(jq -r '.files.example[0] // .files.exemplar[0]' "$config")` resolves to `.meta/example.awk`.
5. In temporary execution environment, runner copies `$solution` into `$stub` and invokes `bats "$tests"`.
