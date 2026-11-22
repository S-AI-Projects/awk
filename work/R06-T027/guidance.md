# Language Construct Guidance: Numeric Coercion in AWK — collatz-conjecture (R06-T027)

## Overview

| Property | Value |
|----------|-------|
| Exercise | `collatz-conjecture` |
| Stub file | `collatz-conjecture.awk` (unsolved learner stub) |
| Test file | `test-collatz-conjecture.bats` (6 enabled test cases) |
| Reference solution | `.meta/example.awk` |

---

## 1. Candidate Language Constructs

To connect the Collatz Conjecture specification to AWK, we examined three fundamental AWK language features:
1. **Record/Field Splitting (`FS`, `RS`, `split()`):** Not customized in this exercise. The input is simply a single integer per record read via default whitespace field splitting (`$1`).
2. **Associative-Array Traversal (`for (k in arr)`):** Not used. The algorithm maintains scalar state (`n` and `steps`) without collection storage.
3. **Numeric Coercion:** **Selected construct.** The entire reference implementation relies on AWK's dual-type scalar model and implicit numeric coercion for input validation, loop termination, and parity determination.

---

## 2. Location in Reference Implementation

In `exercises/practice/collatz-conjecture/.meta/example.awk`:

```awk
$1 < 1 {
    print "Error: Only positive integers are allowed" > "/dev/stderr"
    exit 1
}

{ 
    n = $1
    steps = 0
    while (n > 1) {
        steps++
        n = (n % 2 == 0) ? n / 2 : 3 * n + 1
    }
    print steps
}
```

### Where Coercion Happens:
- **Line 1 (`$1 < 1`):** Input arriving on standard input is initially parsed as field `$1` with the `strnum` (numeric string) attribute. It is compared to the numeric literal `1`.
- **Line 7 (`n = $1`):** Assigns `$1` to `n`.
- **Line 9 (`while (n > 1)`):** Numeric comparison against literal `1`.
- **Line 11 (`n % 2 == 0`, `n / 2`, `3 * n + 1`):** Arithmetic operators (`%`, `/`, `*`, `+`) force numeric evaluation.

---

## 3. Standalone Micro-Example & The Pitfall

In AWK, comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`) behave differently depending on operand attributes:
- If **both** operands are numeric (or numeric strings `strnum`), AWK performs **numeric comparison**.
- If **either** operand has the string attribute and the other is converted to string (or both are strings), AWK performs **lexicographical string comparison**!

### The Contrasting Snippets

#### Snippet A: Coerced / Numeric Comparison (Correct)
```awk
val = "10"
print (val + 0 < 2)   # Output: 0
```
- Adding `0` forces arithmetic context, converting `"10"` to the number `10`.
- The comparison is `10 < 2`, which is mathematically **false** (`0`).

#### Snippet B: Uncoerced Comparison Pitfall (Contrasting Outcome)
```awk
val = "10"
print (val < 2)       # Output: 1
```
- When `val` has string type, AWK converts the number `2` to the string `"2"`.
- It performs character-by-character string comparison.
- In ASCII, `"10"` begins with character `'1'` (ASCII 49), which precedes `'2'` (ASCII 50).
- Consequently, `"10" < "2"` evaluates to **true** (`1`)!

---

## 4. Why Outcomes Differ and Exercise Relevance

| Expression | Operand Types | Comparison Type | Result | Meaning |
|---|---|---|---|---|
| `(val + 0 < 2)` | `number < number` | Numeric ($10 < 2$) | **`0`** (false) | 10 is greater than 2 |
| `(val < 2)` | `string < number` | Lexicographical (`"10" < "2"`) | **`1`** (true) | `'1'` precedes `'2'` in ASCII |

### Why This Matters for Collatz Conjecture:
- A learner might construct a condition comparing string variables or using string literals:
  - If a learner checks `val < "1"` instead of `val < 1`, or stores intermediate states as strings (e.g. `n = "" $1`), comparisons like `n > 1` or `n < 1` will execute string comparisons.
  - Under lexicographical rules, `"10" < "2"` is true, `"1000000" < "2"` is true, and `"12" > "1"` is true, leading to premature loop termination or failure of the error check (`$1 < 1`).
- **Idiomatic AWK Rule:** Always ensure numbers intended for arithmetic boundaries are either numeric literals or explicitly coerced via `+ 0` when their string attribute is ambiguous.

---

## 5. Verification Commands

```bash
export PATH="/opt/homebrew/bin:$PATH"
bash bin/validate_one_exercise exercises/practice/collatz-conjecture
# → 1..6, all ok

python3 work/R06-T027/check.py
# → [PASS] All assertions passed.
```
