# Roman Numerals Exercise Maintenance & Guidance Documentation

## 1. Overview & Context

- **Exercise**: `roman-numerals`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T017`
- **Learner Solution Stub**: `exercises/practice/roman-numerals/roman-numerals.awk`
- **Reference Solution**: `exercises/practice/roman-numerals/.meta/example.awk`
- **Test Suite**: `exercises/practice/roman-numerals/test-roman-numerals.bats`
- **Test Configuration**: `exercises/practice/roman-numerals/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/roman-numerals/.meta/config.json`
- **Hints Guide**: `exercises/practice/roman-numerals/.docs/hints.md`

---

## 2. Language Construct Analysis: `PROCINFO["sorted_in"]`

### Motivation & Context in Reference Implementation

The reference solution in `exercises/practice/roman-numerals/.meta/example.awk` relies on an associative array `dec` mapping Roman symbols to decimal integers:

```awk
BEGIN {
    dec["M"] = 1000; dec["CM"] = 900; dec["D"] = 500; dec["CD"] = 400
    dec["C"] = 100 ; dec["XC"] = 90 ; dec["L"] = 50 ; dec["XL"] = 40
    dec["X"] = 10  ; dec["IX"] = 9  ; dec["V"] = 5  ; dec["IV"] = 4
    dec["I"] = 1
    PROCINFO["sorted_in"] = "@val_num_desc"
}
```

By default in AWK, iterating `for (key in array)` yields keys in arbitrary internal hash order. A greedy Roman numeral algorithm requires strictly descending numeric ordering (from 1000 down to 1). Setting `PROCINFO["sorted_in"] = "@val_num_desc"` enforces numerical descending traversal of the values.

### Micro-Examples & Pitfall Verification

1. **Construct Micro-Example (`@val_num_desc`)**:
   ```awk
   BEGIN {
       vals["X"] = 10; vals["V"] = 5; vals["I"] = 1
       PROCINFO["sorted_in"] = "@val_num_desc"
       for (k in vals) printf "%s:%d ", k, vals[k]
       print ""
   }
   ```
   - **Output**: `X:10 V:5 I:1` (Correct descending numerical order)

2. **Pitfall Micro-Example (`@val_str_desc`)**:
   ```awk
   BEGIN {
       vals["X"] = 10; vals["V"] = 5; vals["I"] = 1
       PROCINFO["sorted_in"] = "@val_str_desc"
       for (k in vals) printf "%s:%d ", k, vals[k]
       print ""
   }
   ```
   - **Output**: `V:5 X:10 I:1` (Incorrect lexicographic order: `'5' > '1'`, placing 5 before 10)

Both micro-examples are executed and asserted by `work/R06-T017/check.py`.

---

## 3. Behavioral Baseline Verification

The named canonical test cases were verified as the behavioral baseline:

1. **"1 is I"**
   - **Input**: `1`
   - **Expected**: `I` | **Actual**: `I` (PASS)
2. **"2 is II"**
   - **Input**: `2`
   - **Expected**: `II` | **Actual**: `II` (PASS)
3. **"3 is III"**
   - **Input**: `3`
   - **Expected**: `III` | **Actual**: `III` (PASS)

All 27 test cases in `test-roman-numerals.bats` pass with 100% agreement against the reference solution.

---

## 4. Verification Harness

Automated verification is conducted by `work/R06-T017/check.py`:
- Asserts that the learner stub `roman-numerals.awk` remains untouched and unsolved.
- Validates the reference solution against `test-roman-numerals.bats` via `bin/validate_one_exercise` in an isolated tempdir (27 passing tests).
- Executes and asserts expected outputs for both micro-examples:
  - Construct (`@val_num_desc`): asserts output matches `X:10 V:5 I:1 `.
  - Pitfall (`@val_str_desc`): asserts output matches `V:5 X:10 I:1 `.
- Saves artifacts in `work/R06-T017/`: `output.txt`, `expected_vs_actual.json`, and `versions.txt`.
