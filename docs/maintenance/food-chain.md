# Food Chain — Mutation Test Finding & Maintenance

## 1. Overview & Context

- **Exercise**: `food-chain`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T033`
- **Learner Solution Stub**: `exercises/practice/food-chain/food-chain.awk`
- **Reference Solution**: `exercises/practice/food-chain/.meta/example.awk`
- **Test Suite**: `exercises/practice/food-chain/test-food-chain.bats`
- **Test Configuration**: `exercises/practice/food-chain/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/food-chain/.meta/config.json`
- **Hints Guide**: `exercises/practice/food-chain/.docs/hints.md`

The goal of the exercise is to generate the cumulative verses of "I Know an Old Lady Who Swallowed a Fly" between a given `start` and `end` verse index.

---

## 2. Deliberate Mutation Analysis

In the reference implementation (`.meta/example.awk`), the cumulative unwinding of animal catch lines is implemented in `verse(i, j)`:

### Original Code
```awk
if (critters[i] != "fly") {
    for (j = i - 1; j >= 1; j--) {
        printf "She swallowed the %s to catch the %s", critters[j + 1], critters[j]
        if (critters[j] == "spider")
            printf " that wriggled and jiggled and tickled inside her"
        printf ".\n"
    }
    print exclamations["fly"]
}
```

### Mutated Code
```awk
if (critters[i] != "fly") {
    for (j = i - 1; j > 1; j--) {
        printf "She swallowed the %s to catch the %s", critters[j + 1], critters[j]
        if (critters[j] == "spider")
            printf " that wriggled and jiggled and tickled inside her"
        printf ".\n"
    }
    print exclamations["fly"]
}
```

### Nature of Mutation
The loop condition `j >= 1` is changed to `j > 1`.
This is a small, deliberate boundary off-by-one condition defect. Instead of iterating down to index 1 (`fly`), the loop terminates early at index 2 (`spider`), omitting the foundational base step of the cumulative catch chain:
`"She swallowed the spider to catch the fly."`

---

## 3. Distinguishing Test Case & Smallest Rejecting Input

### Test Evaluation
- **Test 1 (`fly`, `start=1, end=1`)**:
  - The critter is `"fly"`.
  - Condition `critters[i] != "fly"` evaluates to `false`, bypassing the catch loop entirely.
  - **Result**: PASSES against both original and mutant.

- **Test 2 (`spider`, `start=2, end=2`)**:
  - This is the **smallest input allowed by the specification** that triggers the cumulative catch loop.
  - In the original implementation, `j` runs for `j = 1`, printing `"She swallowed the spider to catch the fly.\n"`.
  - In the mutated implementation, `j = 1` violates `j > 1`, so 0 catch lines are printed.
  - **Result**: FAILS assertion `assert_output "$expected"`.

### Comparison for Smallest Rejecting Case (`spider`, `start=2, end=2`)

**Input Parameters**:
`-v start=2 -v end=2`

**Expected Output (Specification)**:
```text
I know an old lady who swallowed a spider.
It wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.
```

**Actual Output with Mutant**:
```text
I know an old lady who swallowed a spider.
It wriggled and jiggled and tickled inside her.
I don't know why she swallowed the fly. Perhaps she'll die.
```

The test runner detects the missing line:
`She swallowed the spider to catch the fly.`
and triggers an assertion failure.

---

## 4. Test Suite Coverage Assessment

The test suite in `test-food-chain.bats` immediately catches this mutation on:
- Test 2 (`spider`)
- Test 3 (`bird`)
- Test 4 (`cat`)
- Test 5 (`dog`)
- Test 6 (`goat`)
- Test 7 (`cow`)
- Test 9 (`multiple verses`)
- Test 10 (`full song`)

The suite provides complete coverage for the cumulative loop boundary; no test cases are missing.

---

## 5. Verification Harness

The automated verification is executed by `work/R06-T033/check.py`:
- Asserts learner stub `food-chain.awk` remains untouched and unsolved.
- Validates that the original reference implementation passes all 10 tests cleanly.
- Applies the deliberate boundary mutant in an isolated temporary directory and asserts that:
  - Test 1 (`fly`) passes.
  - Test 2 (`spider`) fails the output assertion.
  - The validator exits non-zero (exit code 1).
- Emits verification artifacts in `work/R06-T033/`.
