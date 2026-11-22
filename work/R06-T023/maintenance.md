# Mutation Analysis — ocr-numbers (R06-T023)

## Exercise overview

| Property | Value |
|----------|-------|
| Exercise | `ocr-numbers` |
| Stub | `ocr-numbers.awk` |
| Test file | `test-ocr-numbers.bats` (generated, 18 cases) |
| Reference | `.meta/example.awk` |
| Enabled cases | 18 (17 in `tests.toml` + 1 track-local "No input") |

---

## The contract

Each digit is represented by a 3-column × 4-row cell.
The reference implementation uses `FPAT="..."` to split each input row into
3-character fields, then concatenates the fields from rows 1–3 of each group
into a 9-character key that is looked up in a pre-built `digit[]` table:

```
row1[col]  (3 chars)
row2[col]  (3 chars)   →  9-char key  →  digit[] lookup  →  "0"–"9" or "?"
row3[col]  (3 chars)
```

**Key invariant:** Every recognised digit has an exact 9-character string
(spaces, pipes, underscores in fixed positions).  An off-by-one in any
position produces a key that is absent from the table → `"?"`.

---

## The mutation

### What was changed (one line, semantic — not formatting)

```diff
- digit["     |  |"] = "1"   # original: 5 spaces, pipe, 2 spaces, pipe
+ digit["    |   |"] = "1"   # mutant:   4 spaces, pipe, 3 spaces, pipe
```

Both strings are 9 characters.  The change shifts one space from before the
pipe to after it, so the key no longer matches the pattern that `FPAT="..."`
assembles from the standard "1" glyph.

### Why this is a semantic mutation

The position of each `|` or `_` within a 3-character field encodes the actual
pixel column of the glyph.  Moving a space from column 1 to column 3 of a
field changes which visual pattern the key represents.  Formatting mutations
(e.g. changing `"` to `'` or reordering array assignments) would not affect
the lookup result.

---

## Diagnostic input

The smallest input that distinguishes the original from the mutant is the
single digit "1" (the minimum valid input: 4 lines × 3 columns):

```
   
  |
  |
   
```

```bash
# Against the original reference → prints "1"
gawk -f .meta/example.awk <<'INPUT'
   
  |
  |
   
INPUT

# Against the mutant → prints "?" (key not found)
# (mutant is a scratch copy only — never committed)
```

---

## Existing test that rejects the mutant

**"Recognizes 1"** (test #2, UUID `027ada25-17fd-4d78-aee6-35a19623639d`) is
the **smallest and first** existing case that rejects the mutant:

| | Original | Mutant |
|--|---------|--------|
| Input | single "1" glyph (4 lines × 3 cols) | same |
| Expected | `"1"` | `"1"` |
| Actual | `"1"` ✓ | `"?"` ✗ |

Five tests in total fail against the mutant (every test involving at least
one "1" digit):

1. `Recognizes 1` ← smallest rejecting case
2. `Recognizes 110101100`
3. `Garbled numbers in a string are replaced with ?`
4. `Recognizes string of decimal numbers`
5. `Numbers separated by empty lines are recognized. Lines are joined by commas.`

No new test case needs to be added; the existing suite is sufficient.

---

## Hint for learners (without publishing the solution)

> **Contract:** Each cell is exactly 3 columns wide and 4 rows tall.
> Your program reads the rows of a cell-group, assembles a fixed-width key
> per column, and uses that key to identify the digit.
>
> **Diagnostic:** If your implementation returns `"?"` for a known digit,
> check how you assemble the key — in particular, whether every field is
> exactly 3 characters (including trailing spaces) before you concatenate
> the three rows.
>
> **Test:** The minimum input that must return `"1"` is:
> ```
>    
>   |
>   |
>    
> ```
> (three spaces on rows 1 and 4; two spaces then `|` on rows 2 and 3)

---

## Validation command

```bash
export PATH="/opt/homebrew/bin:$PATH"
bash bin/validate_one_exercise exercises/practice/ocr-numbers
# → 1..18, all ok

python3 work/R06-T023/check.py
# → [PASS] All assertions passed.
```
