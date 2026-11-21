# Hints

## General

- The Series exercise extracts all contiguous substrings (slices) of length `len` from an input series string.
- Slices must appear in the exact order they occur in the original string (from left to right), separated by single spaces.

## Slicing Mathematics

For an input series $S$ of length $L = \text{length}(S)$ and requested slice length $n = \text{len}$:
- The total number of valid contiguous slices is:
  $$M = L - n + 1$$
- The starting index of each slice $k$ ranges from $1$ to $L - n + 1$.
- Slices are extracted using `substr(string, start, length)` or field referencing when `FS = ""`.

### Worked Examples on Canonical Cases

1. **`slices of one from one`** ($S = \text{"1"}, n = 1$):
   - $L = 1$, $n = 1$.
   - Number of slices: $1 - 1 + 1 = 1$.
   - Slice at index 1: `"1"`. Output: `"1"`.

2. **`slices of one from two`** ($S = \text{"12"}, n = 1$):
   - $L = 2$, $n = 1$.
   - Number of slices: $2 - 1 + 1 = 2$.
   - Slice at index 1: `"1"`. Slice at index 2: `"2"`.
   - Joined by a single space: `"1 2"`.

3. **`slices of two`** ($S = \text{"35"}, n = 2$):
   - $L = 2$, $n = 2$.
   - Number of slices: $2 - 2 + 1 = 1$.
   - Slice at index 1: `"35"`. Output: `"35"`.

---

## Contract Decision Table

| Condition | Series Length ($L$) | Slice Length ($n$) | Contract Status | Expected Behavior |
|:---|:---:|:---:|:---:|:---|
| $1 \le n \le L$ | $L \ge 1$ | $1 \le n \le L$ | **Valid** | Emit $L - n + 1$ space-separated substrings. |
| Empty Series | $L = 0$ | Any $n$ | **Error** | Exit with `"series cannot be empty"`. |
| Zero Slice Length | $L \ge 1$ | $n = 0$ | **Error** | Exit with `"slice length cannot be zero"`. |
| Negative Slice Length | $L \ge 1$ | $n < 0$ | **Error** | Exit with `"slice length cannot be negative"`. |
| Slice Length Exceeds Series | $L \ge 1$ | $n > L$ | **Error** | Exit with `"slice length cannot be greater than series length"`. |

---

## Specified vs. Unspecified Contract Behavior

### Specified Behavior
- **Strict Error Messages**: When an error condition is triggered, the program must output the exact required error message to standard error (`/dev/stderr`) and exit with a non-zero exit code (`exit 1`).
- **Ordering**: Slices must preserve natural sequential order. No re-sorting or numerical comparison should be applied.

### Behavior Outside the Contract
- **Non-Digit Characters**: While the description introduces the problem with digit strings, the specification does not mandate character validation. Do not reject or fail strings containing non-digit characters unless explicitly required.
- **Floating-point Lengths**: Slices are defined strictly over integer lengths. Floating-point inputs or conversions are not tested.
- **Case or Unicode**: Only standard ASCII character sequences are evaluated in this exercise.
