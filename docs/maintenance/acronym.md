# Maintenance Guide: Acronym (`acronym`)

## 1. Problem Formulation & Specification

The Acronym exercise converts a natural language phrase into its capitalized acronym:
- Each word in the phrase contributes its first alphabetic character.
- Hyphens (`-`) and whitespace characters (spaces, tabs) act as word delimiters.
- Non-delimiter punctuation marks (such as commas, colons, apostrophes, and surrounding underscores) must not create spurious acronym characters or contaminate word boundaries.
- All characters in the resulting acronym must be capitalized.

---

## 2. Reference Implementation vs. Alternative Paradigm

### 2.1 Maintained Reference Technique (`FS` Delimiter Splitting)
Located in `exercises/practice/acronym/.meta/example.awk`:

```awk
BEGIN {
    # field separator is whitespace or hyphen
    FS = "[[:blank:]-]+"
}
{
    acr = ""
    for (i=1; i<=NF; i++) {
        gsub(/[^[:alpha:]]/, "", $i)    # remove non-letters
        acr = acr substr($i, 1, 1)      # and take the first letter
    }
    print toupper(acr)
}
```

**Mechanics**:
1. Defines the field separator regex `FS = "[[:blank:]-]+"`.
2. Splits the input line into fields `$1..$NF`.
3. Loops over each field and performs in-place mutation: `gsub(/[^[:alpha:]]/, "", $i)` deletes any non-letter characters (e.g., punctuation like commas in `"In,"` or underscores in `"_Not_"`).
4. Takes `substr($i, 1, 1)` from the cleaned field.
5. Emits `toupper(acr)`.

### 2.2 Independently Written Alternative Technique (`FPAT` Word Tokenization)
Implemented as an alternative approach:

```awk
BEGIN {
    # Define fields by word pattern rather than delimiters
    FPAT = "[[:alpha:]][[:alpha:]']*"
}
{
    acr = ""
    for (i = 1; i <= NF; i++) {
        acr = acr substr($i, 1, 1)
    }
    print toupper(acr)
}
```

**Mechanics**:
1. Uses `FPAT` (Field Pattern) to define what a word token *is*, rather than what *separates* words.
2. The regular expression `[[:alpha:]][[:alpha:]']*` matches any contiguous token starting with an alphabetic letter and containing letters or internal apostrophes (e.g., `"Halley's"`).
3. Non-word characters (spaces, hyphens, commas, underscores) are automatically treated as intervening separators without manual deletion.
4. Each field `$i` is directly guaranteed to begin with an alphabetic letter, eliminating the need for `gsub`.
5. Emits `toupper(acr)`.

---

## 3. Comparative Evaluation & Trade-offs

### 3.1 Clarity and Readability
- **Alternative is Clearer**:
  - The alternative directly expresses the problem intent: "an acronym is made of the initial letters of words".
  - It avoids mutating `$i` in place. In AWK, mutating `$i` forces the interpreter to invalidate and recompute `$0`, which is often an unexpected side effect for learners.
- **Reference is More Portable**:
  - `FS` with a regular expression is part of the POSIX AWK standard and runs identically on BSD awk, `mawk`, and `gawk`.
  - `FPAT` is a GNU AWK extension. On non-GNU AWK environments, an equivalent pattern match requires manual `match()` loops or `patsplit()`.

### 3.2 Computational Work & Memory Overhead

| Aspect | Reference (`FS` + `gsub`) | Alternative (`FPAT`) |
|:---|:---|:---|
| **Field Splitting** | Regex split on `[[:blank:]-]+` ($O(L)$) | Regex DFA tokenization on `[[:alpha:]]...` ($O(L)$) |
| **Field Cleaning** | $NF$ calls to `gsub(/[^[:alpha:]]/, "", $i)` ($O(L)$) | **None** ($0$ calls to `gsub`) |
| **Field Recomputation** | Rebuilds `$0` whenever `$i` is modified | No record rebuilding (read-only fields) |
| **Substring Extraction** | $NF$ calls to `substr($i, 1, 1)` | $NF$ calls to `substr($i, 1, 1)` |
| **Memory Allocation** | Re-allocates field string buffers on `gsub` mutation | Allocates token slices during initial `FPAT` parse |
| **Portability** | POSIX AWK compliant | GNU AWK specific (`FPAT`) |

---

## 4. Contract Verification Across Canonical Cases

Both implementations were subjected to all 9 test cases from `test-acronym.bats` and agree with 100% fidelity:

| Test Case | Input Phrase | Reference Output | Alternative Output | Agreement |
|:---|:---|:---:|:---:|:---:|
| `basic` | `"Portable Network Graphics"` | `PNG` | `PNG` | Match |
| `lowercase words` | `"Ruby on Rails"` | `ROR` | `ROR` | Match |
| `punctuation` | `"First In, First Out"` | `FIFO` | `FIFO` | Match |
| `all caps word` | `"GNU Image Manipulation Program"` | `GIMP` | `GIMP` | Match |
| `punctuation without whitespace`| `"Complementary metal-oxide semiconductor"` | `CMOS` | `CMOS` | Match |
| `very long abbreviation` | `"Rolling On The Floor Laughing..."` | `ROTFLSHTMDCOALM`| `ROTFLSHTMDCOALM`| Match |
| `consecutive delimiters` | `"Something - I made up from thin air"` | `SIMUFTA` | `SIMUFTA` | Match |
| `apostrophes` | `"Halley's Comet"` | `HC` | `HC` | Match |
| `underscore emphasis` | `"The Road _Not_ Taken"` | `TRNT` | `TRNT` | Match |

---

## 5. Verification Checklist

- [x] All 9 tests pass against reference `example.awk`.
- [x] All 9 tests pass against the alternative `FPAT` implementation.
- [x] Named baseline cases (`basic`, `lowercase words`, `punctuation`) verified and documented.
- [x] Learner stub `acronym.awk` remains unsolved stub.
- [x] Hint document (`exercises/practice/acronym/.docs/hints.md`) created with worked examples and trade-offs, avoiding full solution spoiler.
- [x] Check script `work/R06-T036/check.py` reproduces all tests and saves artifacts in `work/R06-T036/`.
