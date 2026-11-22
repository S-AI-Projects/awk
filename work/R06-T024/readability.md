# Readability Analysis & Trace — line-up (R06-T024)

## Overview

| Property | Value |
|----------|-------|
| Exercise | `line-up` |
| Stub file | `line-up.awk` (unsolved learner stub) |
| Test file | `test-line-up.bats` (25 enabled cases) |
| Reference solution | `.meta/example.awk` |

---

## Behavioral Baseline: Tracing `suffix` for Named Cases

The goal anchors on three specific non-exceptional ordinal numeral cases:
1. `format smallest non-exceptional ordinal numeral 4` (`Gianna 4`)
2. `format greatest single digit non-exceptional ordinal numeral 9` (`Maarten 9`)
3. `format non-exceptional ordinal numeral 5` (`Petronila 5`)

### Original Implementation
```awk
function suffix(number) {
    if (number ~ /(1[123]|[^123])$/) return "th"
    else if (number ~ /1$/) return "st"
    else if (number ~ /2$/) return "nd"
    else return "rd"
}
```

### Trace of the Named Cases in Original:

1. **`number = 4`**
   - Evaluates: `4 ~ /(1[123]|[^123])$/`
   - Does `4` match `1[123]`? No.
   - Does `4` match `[^123]`? Yes, `4` is not in `[123]`.
   - Result: `"th"`. Output: `"Gianna, you are the 4th customer we serve today. Thank you!"`

2. **`number = 9`**
   - Evaluates: `9 ~ /(1[123]|[^123])$/`
   - Does `9` match `1[123]`? No.
   - Does `9` match `[^123]`? Yes, `9` is not in `[123]`.
   - Result: `"th"`. Output: `"Maarten, you are the 9th customer we serve today. Thank you!"`

3. **`number = 5`**
   - Evaluates: `5 ~ /(1[123]|[^123])$/`
   - Does `5` match `1[123]`? No.
   - Does `5` match `[^123]`? Yes, `5` is not in `[123]`.
   - Result: `"th"`. Output: `"Petronila, you are the 5th customer we serve today. Thank you!"`

### What Was Obscure About the Original State?

1. **Conflation of two distinct rules into a single regex:**
   The regex `/(1[123]|[^123])$/` packs two completely separate grammatical rules into one clause:
   - The two-digit "teen" exception (`11, 12, 13`)
   - The general non-exceptional single digits (`0, 4, 5, 6, 7, 8, 9`)
2. **Inverted cognitive ordering via negative character classes:**
   Instead of testing for positive rules (e.g., ends in 1, 2, or 3), it relies on a negated character class `[^123]` to trigger `"th"` early so that `else if (number ~ /1$/)` only sees non-negated single digits.
3. **No explicit local state:**
   The function operated directly on `number` as an implicit string regex target, hiding the two core numerical concepts:
   - The last two digits (determining the 11–13 teen exception).
   - The last single digit (determining the 1/2/3 ordinal suffix).

---

## The Readability Improvement

### Refactored Implementation
```awk
function suffix(number,    last_two, last_digit) {
    last_two = number % 100
    last_digit = number % 10

    if (last_two >= 11 && last_two <= 13) return "th"
    else if (last_digit == 1) return "st"
    else if (last_digit == 2) return "nd"
    else if (last_digit == 3) return "rd"
    else return "th"
}
```

### The Diff
```diff
-function suffix(number) {
-    if (number ~ /(1[123]|[^123])$/) return "th"
-    else if (number ~ /1$/) return "st"
-    else if (number ~ /2$/) return "nd"
-    else return "rd"
+function suffix(number,    last_two, last_digit) {
+    last_two = number % 100
+    last_digit = number % 10
+
+    if (last_two >= 11 && last_two <= 13) return "th"
+    else if (last_digit == 1) return "st"
+    else if (last_digit == 2) return "nd"
+    else if (last_digit == 3) return "rd"
+    else return "th"
 }
```

### Why This Helps This Exercise
1. **Directly maps to the exercise specification:**
   The instructions in `.docs/instructions.md` state:
   - Numbers ending in 1 (unless ending in 11) → `"st"`
   - Numbers ending in 2 (unless ending in 12) → `"nd"`
   - Numbers ending in 3 (unless ending in 13) → `"rd"`
   - All other numbers → `"th"`
   
   The refactored code expresses this rule hierarchy explicitly:
   - Check if the last two digits are 11–13 (the exception).
   - Check if the last digit is 1, 2, or 3.
   - Fall through to `"th"` for all others.

2. **Explicit AWK local variable declaration:**
   By declaring `last_two` and `last_digit` in the function parameter list (separated by extra spaces per standard AWK conventions), we establish clean, scoped local state without global pollution.

3. **Eliminates cryptic regex parsing:**
   Replaces complex regex string operations with clean integer arithmetic (`% 100` and `% 10`), making the intent obvious at a glance to anyone reading the reference implementation.

---

## Verification & Compatibility

- **Return types:** Unchanged (returns string `"th"`, `"st"`, `"nd"`, `"rd"`).
- **Public API / interface:** `suffix(number)` signature and calling convention unchanged.
- **Dependencies:** Standard AWK only; no external tools or functions.
- **All 25 test cases:** Pass with 100% agreement before and after.
