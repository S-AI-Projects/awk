# Alphametics — Reference Implementation Readability Maintenance

## 1. Overview & Context

- **Exercise**: `alphametics`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T034`
- **Learner Solution Stub**: `exercises/practice/alphametics/alphametics.awk`
- **Reference Solution**: `exercises/practice/alphametics/.meta/example.awk`
- **Test Suite**: `exercises/practice/alphametics/test-alphametics.bats`
- **Test Configuration**: `exercises/practice/alphametics/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/alphametics/.meta/config.json`

The objective of `alphametics` is to solve cryptarithm word addition puzzles (such as `SEND + MORE == MONEY`), assigning unique digits (0–9) to each letter without leading zeros.

---

## 2. Readability Improvement & Focus on `colchar`

The alphametics reference implementation utilizes a column-by-column backtracking approach, proceeding from the units column ($col = 0$) towards the highest place value.

### Analysis of the Original `colchar` Function
```awk
function colchar(word, col,    L) {
    L = length(word)
    if (col < L) return substr(word, L - col, 1)
    return ""
}
```

In the original code:
- The local variable `L` was a terse single-character variable name that obscured its role.
- The 1-based string offset calculation `L - col` was inlined directly in the `substr()` call without explanation of the right-to-left column mapping.
- In the main record block, single-letter `L` was similarly reused for string length.

### Refactored Implementation
```awk
# Extracts the character from word at column index col,
# counting from col = 0 at the rightmost (units) digit.
# Returns "" if col exceeds the length of the word.
function colchar(word, col,    word_len, char_pos) {
    word_len = length(word)
    if (col < word_len) {
        char_pos = word_len - col
        return substr(word, char_pos, 1)
    }
    return ""
}
```

### Key Readability Improvements
1. **Explicit Variable Naming**:
   - `L` was renamed to `word_len`, clearly conveying that it stores the length of the word string.
   - The 1-based character position calculation `word_len - col` was extracted into `char_pos`.
2. **Clear Invariant Documentation**:
   - Added clear function documentation explaining that `col = 0` represents the rightmost (units) place value, and higher column indices step leftwards.
   - When `col >= word_len`, the function returns empty string (`""`), cleanly indicating that the word has fewer digits than the current column position.
3. **Standard POSIX Whitespace Character Class**:
   - Updated input regex splitting from GNU-specific `\s*` to standard POSIX `[[:space:]]*`, ensuring clean portability across AWK implementations.

---

## 3. Behavioral Baseline Verification

Verification was anchored on the three required baseline cases:

1. **"puzzle with three letters"**
   - **Input**: `"I + BB == ILL"`
   - **Expected**: `"B=9 I=1 L=0"`
   - **Trace**:
     - Column 0: `colchar("I", 0) -> "I"`, `colchar("BB", 0) -> "B"`, `colchar("ILL", 0) -> "L"`.
     - Column 1: `colchar("I", 1) -> ""`, `colchar("BB", 1) -> "B"`, `colchar("ILL", 1) -> "L"`.
     - Column 2: `colchar("I", 2) -> ""`, `colchar("BB", 2) -> ""`, `colchar("ILL", 2) -> "I"`.
   - **Result**: PASS

2. **"solution must have unique value for each letter"**
   - **Input**: `"A == B"`
   - **Expected**: No output (refuted)
   - **Trace**: Backtracking detects `A == B` requires assigning identical digits, violating the uniqueness constraint.
   - **Result**: PASS

3. **"leading zero solution is invalid"**
   - **Input**: `"ACA + DD == BD"`
   - **Expected**: No output (refuted)
   - **Trace**: `leading[A]`, `leading[D]`, `leading[B]` prevent assigning digit 0 to initial letters.
   - **Result**: PASS

All 10 test cases in `test-alphametics.bats` pass with 100% agreement between original and refactored versions.

---

## 4. Verification Harness

The automated check script [work/R06-T034/check.py](file:///Users/ayaz/awk/work/R06-T034/check.py):
- Confirms learner stub `alphametics.awk` remains untouched and unsolved.
- Validates that the refactored reference implementation passes all 10 tests in an isolated temporary directory.
- Verifies output equivalence against all test cases.
- Saves execution artifacts in `work/R06-T034/`.
