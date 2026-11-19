# Allergies Exercise Maintenance & Reference Clarification

## 1. Overview & Context

- **Exercise**: `allergies`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T014`
- **Learner Solution Stub**: `exercises/practice/allergies/allergies.awk`
- **Reference Solution**: `exercises/practice/allergies/.meta/example.awk`
- **Test Suite**: `exercises/practice/allergies/test-allergies.bats`
- **Test Configuration**: `exercises/practice/allergies/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/allergies/.meta/config.json`

---

## 2. Refactoring Rationale & Invariant Documentation

### Motivation

In the original reference implementation, `is_allergic_to` was implemented as:

```awk
function is_allergic_to(score, allergen) {
    return and(rshift(score, allergies[allergen]), 1) == 1
}
```

While compact, this compressed multiple logical steps into an unannotated single expression:
1. Lookup of the zero-based bit-shift offset (`allergies[allergen]`) corresponding to the allergen flag.
2. The bitwise right-shift of `score` to align the target bit with bit position 0 (the least-significant bit).
3. The bitwise AND masking with 1 and comparison to 1.

Additionally, in AWK, local variables are scoped by listing them after extra whitespace in the function signature. Without an explicit local variable declaration, any extracted state would leak into global scope.

### Refactored Implementation

The refactored reference implementation explicitly extracts the local shift offset and documents the domain invariant:

```awk
# An allergen score is a bitfield where each allergen corresponds to a bit flag (2^i).
# allergies[allergen] stores the zero-based bit shift offset (0 for eggs, 1 for peanuts, etc.).
# Right-shifting the score by shift_offset positions the allergen's bit at bit 0,
# allowing a bitwise AND with 1 to determine if the person is allergic.
function is_allergic_to(score, allergen,    shift_offset) {
    shift_offset = allergies[allergen]
    return and(rshift(score, shift_offset), 1) == 1
}
```

### Invariant & Algorithmic Guarantee

1. **Bitfield Representation**:
   - Each allergen corresponds to a power-of-two bit value ($2^0 = 1$ for eggs, $2^1 = 2$ for peanuts, ..., $2^7 = 128$ for cats).
   - In `BEGIN`, the `allergies` associative array maps each allergen name to its power exponent $i - 1$ (the bit position / shift amount).
2. **Bit Extraction**:
   - By right-shifting `score` by `shift_offset` bits, the target allergen flag is moved to bit 0.
   - Performing `and(..., 1)` isolates bit 0.
   - Comparing `== 1` returns a boolean (1 or 0 in AWK), ensuring exact binary equality with no coercion side-effects.

---

## 3. Behavioral Baseline Verification

The named test cases were traced as the behavioral baseline:

1. **"testing for eggs allergy: not allergic to anything"**
   - **Input**: `0,allergic_to,eggs`
   - **Evaluation**: `allergies["eggs"] = 0`, `rshift(0, 0) = 0`, `and(0, 1) = 0 == 1` $\rightarrow$ `false`
   - **Output**: `false` (Matches expected)

2. **"testing for eggs allergy: allergic only to eggs"**
   - **Input**: `1,allergic_to,eggs`
   - **Evaluation**: `allergies["eggs"] = 0`, `rshift(1, 0) = 1`, `and(1, 1) = 1 == 1` $\rightarrow$ `true`
   - **Output**: `true` (Matches expected)

3. **"testing for eggs allergy: allergic to eggs and something else"**
   - **Input**: `3,allergic_to,eggs`
   - **Evaluation**: `allergies["eggs"] = 0`, `rshift(3, 0) = 3`, `and(3, 1) = 1 == 1` $\rightarrow$ `true`
   - **Output**: `true` (Matches expected)

All 50 test cases in `test-allergies.bats` pass with 100% agreement between the baseline and refactored versions.

---

## 4. Automated Verification

Verification is orchestrated by `work/R06-T014/check.py`:
- Reads `.meta/config.json` to discover solution, test, and reference paths.
- Verifies that `allergies.awk` remains an untouched, unsolved stub.
- Executes `bin/validate_one_exercise exercises/practice/allergies` inside an isolated temporary directory.
- Asserts that all 50 tests pass and explicitly checks the 3 named egg allergy test cases.
- Emits execution evidence in `work/R06-T014/`: `output.txt`, `expected_vs_actual.json`, and `versions.txt`.
