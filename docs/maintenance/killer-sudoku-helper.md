# Maintenance Guide: Killer Sudoku Helper (`killer-sudoku-helper`)

## 1. Problem Formulation & Specification

Killer Sudoku Helper generates all valid digit combinations for a killer cage:
- **Digits**: Only digits $1 \dots 9$ are permitted.
- **Uniqueness**: Digits cannot repeat within a cage.
- **Constraints**:
  - Target sum $S$ (provided as `$1`).
  - Cage size $K$ (provided as `$2`).
  - Excluded digits $E_1, E_2, \dots$ (provided as `$3 \dots \$NF`).
- **Ordering**: Combinations must be output in ascending numerical order, space-separated, with one combination per line.

---

## 2. Language Construct Evaluation in `example.awk`

The prompt directs examining three AWK constructs:
1. **Associative-Array Traversal (`for (k in arr)`)**:
   - Not used in `generate_recursive`.
   - AWK associative arrays are unordered hash maps. Traversal order depends on the internal hash table state, which violates the strict requirement for sorted combinations. The reference only uses associative arrays for $O(1)$ existence checks (`digit in ExcludedDigits`).
2. **Numeric Coercion**:
   - While arithmetic operations (`remainingSum - digit`, `digit <= MaxDigit`) rely on standard AWK numeric conversions, numeric coercion itself does not govern the recursive state or output structure.
3. **Record / Field Manipulation (`NF`, `$NF`, and `$0`)**:
   - **This is the primary language construct used by `generate_recursive`**.
   - Instead of maintaining an auxiliary array or repeatedly concatenating and slicing strings, `generate_recursive` leverages AWK's built-in field mechanism as an execution stack:
     - `NF++` pushes a new field.
     - `$NF = digit` assigns the field value.
     - `print` triggers automatic serialization of `$1 \dots \$NF` joined by `OFS` (default space `" "`).
     - `NF--` pops the top field when backtracking.

---

## 3. Reference Implementation Architecture

Located in `exercises/practice/killer-sudoku-helper/.meta/example.awk`:

```awk
BEGIN {
    MaxDigit = 9
}
{
    cageSum = $1
    cageSize = $2
    for (i = 3; i <= NF; ++i) {
        ExcludedDigits[$i] = 1
    }
    NF = 0
    generate_recursive(1, cageSum, cageSize)
}

function generate_recursive(currentStartDigit, remainingSum, remainingSize,   maxPossibleFirstDigit, digit) {
    NF++
    if (remainingSize == 1) {
        if (currentStartDigit <= remainingSum && remainingSum <= MaxDigit && !(remainingSum in ExcludedDigits)) {
            $NF = remainingSum
            print
        }
    } else {
        maxPossibleFirstDigit = MaxDigit - remainingSize + 1
        for (digit = currentStartDigit; digit <= maxPossibleFirstDigit; ++digit) {
            if (digit in ExcludedDigits)
                continue
            $NF = digit
            generate_recursive(digit + 1, remainingSum - digit, remainingSize - 1)
        }
    }
    NF--
}
```

---

## 4. Standalone Micro-Examples & Pitfall Analysis

### 4.1 Micro-Example 1: Dynamic Field Stack (Correct Usage)
```awk
function push(val) { NF++; $NF = val }
function pop()     { NF-- }
BEGIN {
    NF = 0
    push(1)
    push(2)
    print
    pop()
    push(3)
    print
}
```
**Expected Output**:
```text
1 2
1 3
```

### 4.2 Micro-Example 2: Missing Backtrack (Exercise-Relevant Pitfall)
```awk
function push(val) { NF++; $NF = val }
BEGIN {
    NF = 0
    push(1)
    push(2)
    print
    # Pitfall: Missing pop() / NF-- before exploring next branch
    push(3)
    print
}
```
**Expected Output**:
```text
1 2
1 2 3
```

### 4.3 Root Cause of Divergence
- In AWK, `$0` is dynamically reconstructed from active fields whenever `print` is called.
- In Micro-Example 1, `pop()` decrements `NF` from 2 to 1. The subsequent `push(3)` overwrites `$2` with `3`, yielding the expected combination `1 3`.
- In Micro-Example 2, omitting `NF--` leaves `NF = 2`. The subsequent `push(3)` increments `NF` to 3 and assigns `$3 = 3`, generating `1 2 3`.

### 4.4 Related Pitfall: Destruction of Input Fields on `NF = 0`
In AWK, assigning `NF = 0` immediately deallocates and clears all fields `$1..$NF`. If input variables are referenced via `$1` or `$2` after `NF = 0`, they evaluate to empty strings. The reference implementation properly avoids this pitfall by assigning `cageSum = $1` and `cageSize = $2` before executing `NF = 0`.

---

## 5. Verification Checklist

- [x] All 13 tests pass in `test-killer-sudoku-helper.bats` against reference `example.awk`.
- [x] Baseline named cases pass: `1`, `2`, `3`.
- [x] Learner stub `killer-sudoku-helper.awk` remains unsolved.
- [x] Hint guide `exercises/practice/killer-sudoku-helper/.docs/hints.md` published.
- [x] Both micro-examples validated and asserted by `work/R06-T037/check.py`.
