# Verification Evidence: R06-T040 (Series Guidance & Decision Table)

## Summary of Results
- **Validation Run**: All 11/11 test cases passed in `test-series.bats`.
- **Baseline Cases**: Explicitly confirmed `slices of one from one`, `slices of one from two`, and `slices of two`.
- **Learner Stub**: `exercises/practice/series/series.awk` remains untouched and unsolved.
- **Decision Table**: All 11 test cases mapped to explicit input conditions and verified against reference implementation.
- **Contract Boundary**: Explicitly separated specified contract behavior from unspecified out-of-contract inputs.
- **Hints Published**: Published student-facing guide in `exercises/practice/series/.docs/hints.md`.

## Decision Table Verification Matrix
| Test Case | Series ($S$) | $L$ | $n$ | Condition | Expected Result | Exit Code | Status |
|:---|:---:|:---:|:---:|:---|:---|:---:|:---:|
| `slices of one from one` | `"1"` | 1 | 1 | 1 <= len <= L (single char) | `1` | 0 | Pass |
| `slices of one from two` | `"12"` | 2 | 1 | 1 <= len <= L (multiple single chars) | `1 2` | 0 | Pass |
| `slices of two` | `"35"` | 2 | 2 | len == L (single full-length slice) | `35` | 0 | Pass |
| `slices of two overlap` | `"9142"` | 4 | 2 | 1 < len < L (overlapping slices) | `91 14 42` | 0 | Pass |
| `slices can include duplicates` | `"777777"` | 6 | 3 | 1 < len < L (duplicate values) | `777 777 777 777` | 0 | Pass |
| `slices of a long series` | `"918493904243"` | 12 | 5 | 1 < len < L (long series) | `91849 18493 84939 49390 93904 39042 90424 04243` | 0 | Pass |
| `slice length is too large` | `"12345"` | 5 | 6 | len == L + 1 (len > L) | `slice length cannot be greater than series length` | 1 | Pass |
| `slice length is way too large` | `"12345"` | 5 | 42 | len >> L (len much greater than L) | `slice length cannot be greater than series length` | 1 | Pass |
| `slice length cannot be zero` | `"12345"` | 5 | 0 | len == 0 | `slice length cannot be zero` | 1 | Pass |
| `slice length cannot be negative` | `"123"` | 3 | -1 | len < 0 | `slice length cannot be negative` | 1 | Pass |
| `empty series is invalid` | `""` | 0 | 1 | L == 0 (empty input string) | `series cannot be empty` | 1 | Pass |

## Contract Separation Analysis
1. **Specified Requirements**:
   - For valid inputs ($1 \le n \le L$): Output contiguous substrings in sequential appearance order, joined by single spaces.
   - For invalid inputs: Trigger exact standard error messages and exit with non-zero status code:
     - $L = 0$: `"series cannot be empty"`
     - $n = 0$: `"slice length cannot be zero"`
     - $n < 0$: `"slice length cannot be negative"`
     - $n > L$: `"slice length cannot be greater than series length"`
2. **Inputs Outside Contract**:
   - Non-digit characters: Not restricted by canonical tests; no spurious validation imposed.
   - Fractional/floating-point slice lengths: Not part of specification.
   - Multi-byte / Unicode characters: Not evaluated.
