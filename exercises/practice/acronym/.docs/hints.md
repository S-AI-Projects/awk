# Hints

## General

- An acronym is formed by taking the first letter of each word in a phrase and converting all letters to uppercase.
- Hyphens (`-`) are word separators just like spaces and tabs.
- Other punctuation (like commas `,`, apostrophes `'`, and underscores `_`) must not contribute acronym letters.

## Word Isolation Strategies

There are two primary paradigms in AWK for isolating the relevant words from an input string:

### Approach A: Delimiter-Based Splitting (`FS`)
- You can configure the Field Separator (`FS`) in a `BEGIN` block to split records on whitespace and hyphens:
  ```awk
  FS = "[[:blank:]-]+"
  ```
- **Worked Example**:
  For the input `"First In, First Out"`:
  - Splitting on `[[:blank:]-]+` produces the fields: `$1 = "First"`, `$2 = "In,"`, `$3 = "First"`, `$4 = "Out"`.
  - Notice that field `$2` still contains a trailing comma (`"In,"`). Similarly, input with emphasis like `"_Not_"` retains surrounding underscores.
  - To extract only the alphabetic characters, you can sanitize each field by removing non-letter characters before taking the first letter.
- **Trade-offs**:
  - *Pros*: Portable across all standard POSIX AWK interpreters; conceptually straightforward.
  - *Cons*: Modifies fields in-place or requires secondary regex sanitization per field to strip non-alphanumeric punctuation.

### Approach B: Pattern-Based Tokenization (`FPAT`)
- Instead of specifying what *separates* words, you can define what *constitutes* a word using the GNU AWK `FPAT` variable:
  ```awk
  FPAT = "[[:alpha:]][[:alpha:]']*"
  ```
- **Worked Example**:
  For the input `"First In, First Out"`:
  - `FPAT` matches contiguous word tokens starting with a letter: `$1 = "First"`, `$2 = "In"`, `$3 = "First"`, `$4 = "Out"`.
  - Notice that punctuation like commas, surrounding underscores, and hyphens are automatically bypassed as non-matching separator text.
  - The first letter of each field `$i` is guaranteed to be an alphabetic character without additional per-field substitution.
- **Trade-offs**:
  - *Pros*: Cleaner representation; eliminates the secondary regex pass and field mutation.
  - *Cons*: Relies on GNU AWK extensions (`FPAT`); regex engine maintains token matching state across the entire record string.

## Building the Acronym

- AWK provides `substr(string, start, length)` to extract substrings (1-indexed).
- The `toupper(string)` function converts lowercase characters to uppercase.
