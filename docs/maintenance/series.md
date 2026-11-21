# Maintenance Guide: Series (`series`)

## 1. Problem Formulation & Specification

Given an input series string $S$ and an integer slice length $n$ (passed via `-v len=...`):
- Compute all contiguous substrings of length $n$.
- Output the substrings joined by single spaces in their order of appearance.

### Slicing Mechanics
For an input string with character length $L$:
- Slices exist if and only if $1 \le n \le L$.
- Number of contiguous slices: $M = L - n + 1$.
- Slices start at 1-based index $i \in [1, L - n + 1]$.
- Substring slice: $S[i \dots i + n - 1]$.

---

## 2. Canonical Case Analysis

### 2.1 `slices of one from one`
- **Input**: `S = "1"`, `len = 1`
- **Math**: $L = 1, n = 1 \implies M = 1 - 1 + 1 = 1$.
- **Slice**: $S[1 \dots 1] = \text{"1"}$.
- **Expected Output**: `"1"`.

### 2.2 `slices of one from two`
- **Input**: `S = "12"`, `len = 1`
- **Math**: $L = 2, n = 1 \implies M = 2 - 1 + 1 = 2$.
- **Slices**: $S[1 \dots 1] = \text{"1"}$, $S[2 \dots 2] = \text{"2"}$.
- **Expected Output**: `"1 2"`.

### 2.3 `slices of two`
- **Input**: `S = "35"`, `len = 2`
- **Math**: $L = 2, n = 2 \implies M = 2 - 2 + 1 = 1$.
- **Slice**: $S[1 \dots 2] = \text{"35"}$.
- **Expected Output**: `"35"`.

---

## 3. Decision Table Across Test Suite

The decision table below connects each input condition to its required contract behavior:

| Test Case | Input Series ($S$) | $L$ | $n$ | Condition | Expected Result | Exit Code |
|:---|:---:|:---:|:---:|:---|:---|:---:|
| `slices of one from one` | `"1"` | 1 | 1 | $1 \le n \le L$ | `"1"` | 0 |
| `slices of one from two` | `"12"` | 2 | 1 | $1 \le n \le L$ | `"1 2"` | 0 |
| `slices of two` | `"35"` | 2 | 2 | $1 \le n \le L$ | `"35"` | 0 |
| `slices of two overlap` | `"9142"` | 4 | 2 | $1 \le n \le L$ | `"91 14 42"` | 0 |
| `slices can include duplicates` | `"777777"` | 6 | 3 | $1 \le n \le L$ | `"777 777 777 777"` | 0 |
| `slices of a long series` | `"918493904243"`| 12 | 5 | $1 \le n \le L$ | `"91849 18493 84939 49390 93904 39042 90424 04243"` | 0 |
| `slice length is too large` | `"12345"` | 5 | 6 | $n > L$ | `"slice length cannot be greater than series length"` | 1 |
| `slice length is way too large` | `"12345"` | 5 | 42 | $n \gg L$ | `"slice length cannot be greater than series length"` | 1 |
| `slice length cannot be zero` | `"12345"` | 5 | 0 | $n = 0$ | `"slice length cannot be zero"` | 1 |
| `slice length cannot be negative` | `"123"` | 3 | -1 | $n < 0$ | `"slice length cannot be negative"` | 1 |
| `empty series is invalid` | `""` | 0 | 1 | $L = 0$ | `"series cannot be empty"` | 1 |

---

## 4. Separation of Specified Behavior vs. Unspecified Inputs

### Specified Behavior
- **Exact Error Strings**: The four failure conditions must output their exact standard strings to standard error and exit with status 1.
- **Space-Delimited Output**: Slices must be separated by exactly one space character, with no trailing space.
- **Positional Ordering**: Slices must appear strictly in order from left to right.

### Unspecified Behavior (Out-of-Contract Inputs)
- **Non-Digit Content**: The problem description states "Given a string of digits", but canonical-data does not require validating whether characters are numeric digits. Slicing arbitrary characters (e.g. letters) should succeed without error.
- **Non-Integer or Float `len`**: `len` is an integer. No floating-point or fractional slice lengths are tested.
- **Multi-line Records**: Handled per-record according to standard AWK record-processing semantics.
- **No Extra Coercions**: Do not impose extra exceptions or constraints beyond the problem specifications.

---

## 5. Verification Checklist

- [x] All 11 tests pass in `test-series.bats` against reference `example.awk`.
- [x] Baseline named cases pass: `slices of one from one`, `slices of one from two`, `slices of two`.
- [x] Learner stub `series.awk` remains unsolved.
- [x] Decision table matches all canonical test inputs and outcomes.
- [x] Hint guide published in `exercises/practice/series/.docs/hints.md`.
- [x] Automated check script `work/R06-T040/check.py` verifies all test cases and decision table mappings.
