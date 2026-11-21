# Largest Series Product — Maintenance and Canonical Test Decisions

## 1. Overview & Context

- **Exercise**: `largest-series-product`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T031`
- **Learner Solution Stub**: `exercises/practice/largest-series-product/largest-series-product.awk`
- **Reference Solution**: `exercises/practice/largest-series-product/.meta/example.awk`
- **Test Suite**: `exercises/practice/largest-series-product/test-largest-series-product.bats`
- **Test Configuration**: `exercises/practice/largest-series-product/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/largest-series-product/.meta/config.json`

The exercise requires calculating the largest product for a contiguous substring of digits of length $n$ (the span) from an input string of digits.

---

## 2. Canonical Case Analysis & Rationale

Canonical problem specifications define 18 test cases. In the AWK track, 13 test cases are active and 5 test cases are excluded in `tests.toml`.

This section documents the specific rationale for the three selected canonical entries:
- `5d81aaf7-4f67-4125-bf33-11493cc7eab7`
- `06bc8b90-0c51-4c54-ac22-3ec3893a079e`
- `3ec0d92e-f2e2-4090-a380-70afee02f4c0`

### Decision & Mapping Table

| UUID | Test Case Title | Inclusion Decision | Category | Rationale & Cited AWK Operations |
|---|---|---|---|---|
| `5d81aaf7-4f67-4125-bf33-11493cc7eab7` | rejects span longer than string length | `include = false` | Replacement Case | **Superseded by replacement case `0ae1ce53-d9ba-41bb-827f-2fceb64f058b`** (`reimplements = "5d81aaf7-4f67-4125-bf33-11493cc7eab7"`). The original specification expected the obsolete error message `"span must be smaller than string length"`. The AWK reference implementation evaluates length via `len = length($1)` and validates `assert(span <= len, "span must not exceed string length")`. The replacement test is actively enabled and verified in the test suite. |
| `06bc8b90-0c51-4c54-ac22-3ec3893a079e` | reports 1 for empty string and empty product (0 span) | `include = false` | Unsupported Behavior | **Excluded due to AWK field splitting and contract definition.** When reading comma-separated inputs with `FS = ","`, empty digits produce an empty field `$1` (`length($1) == 0`). This fails the canonical input validation `assert($1 ~ /^[[:digit:]]+$/, "digits input must only contain digits")` and the positive span contract `assert(span > 0, "span must not be negative")`. Because no series of positive length exists in an empty string, this edge case is excluded from the student exercise contract. |
| `3ec0d92e-f2e2-4090-a380-70afee02f4c0` | reports 1 for nonempty string and empty product (0 span) | `include = false` | Unsupported Behavior | **Excluded due to degenerative AWK string operations and contract invariants.** In AWK, evaluating a span of 0 with `substr($1, i, span)` returns an empty string `""`. Passing this to `product()` causes `split("", digits, "")` to return `n = 0`, producing a degenerate product. Furthermore, the exercise contract enforces non-empty series requiring `assert(span > 0)`. The empty product (identity 1 for 0-length span) is considered out of scope for the AWK practice problem. |

---

## 3. Inclusion Summary

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Total Canonical Cases | 18 | 18 | 0 |
| Included Cases | 13 | 13 | 0 |
| Excluded Cases | 5 | 5 | 0 |

No inclusion or exclusion values were altered. All 13 included test cases correspond directly to passing tests in `test-largest-series-product.bats`.

---

## 4. Reference Implementation Baseline Verification

The reference implementation (`.meta/example.awk`) satisfies all 13 enabled canonical test cases, including the three named baseline cases:

1. **"finds the largest product if span equals length"**
   - **Input**: `"29,2"`
   - **Expected**: `"18"`
   - **Result**: PASS

2. **"can find the largest product of 2 with numbers in order"**
   - **Input**: `"0123456789,2"`
   - **Expected**: `"72"`
   - **Result**: PASS

3. **"can find the largest product of 2"**
   - **Input**: `"576802143,2"`
   - **Expected**: `"48"`
   - **Result**: PASS

The learner stub (`largest-series-product.awk`) remains untouched and unsolved (`exit 1` with `"Implement this solution"`).

---

## 5. Verification Harness

The check script `work/R06-T031/check.py`:
- Copies the exercise (including dotfiles) to an isolated temporary directory.
- Substitutes the reference implementation into the temporary copy only, preserving the working tree.
- Executes `bin/validate_one_exercise exercises/practice/largest-series-product`.
- Validates child exit codes and asserts that all 13 tests pass without failure.
- Verifies learner stub integrity and records execution artifacts in `work/R06-T031/`.
