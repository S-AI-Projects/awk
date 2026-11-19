# Hints

## General

- In AWK, standard record processing splits input line-by-line (`RS = "\n"`). However, Bob may receive multi-line statements. Setting `RS = SUBSEP` (or another character unlikely to appear in input) in a `BEGIN` block allows AWK to slurp the entire input as a single record (`$0`).
- Whitespace trailing the input must be removed (or ignored) before checking if the statement ends with a question mark (`?`).

## Contract Decision Table

Bob's responses follow an exact priority hierarchy based on input characteristics:

| Case Category | Example Test Input | Ends With `?` (`is_asking`) | All Caps & Has Letters (`is_yelling`) | Only Whitespace (`is_silence`) | Bob's Response |
|---|---|---|---|---|---|
| **Silence** | `""` or `"   \t\r\n"` | False | False | True | `"Fine. Be that way!"` |
| **Forceful Question** | `"WHAT'S GOING ON?"` | True | True | False | `"Calm down, I know what I'm doing!"` |
| **Shouting** | `"WATCH OUT!"` | False | True | False | `"Whoa, chill out!"` |
| **Asking a Question** | `"Does this cryogenic chamber make me look fat?"` | True | False | False | `"Sure."` |
| **Statement / Other** | `"Tom-ay-to, tom-aaaah-to."` | False | False | False | `"Whatever."` |

### Evaluation Ordering & Precedence

1. **Silence First**: Check whether trimming whitespace leaves an empty string. If so, return `"Fine. Be that way!"`.
2. **Forceful Question Before Individual Traits**: Because a forceful question satisfies *both* `is_yelling` and `is_asking`, testing `is_yelling && is_asking` must happen before checking `is_yelling` or `is_asking` individually.
3. **Shouting vs. Asking**: Shouting requires at least one uppercase alphabetical character (`s ~ /[[:upper:]]/`) and zero lowercase characters (`s !~ /[[:lower:]]/`).
4. **Fallback**: Any input that does not match the above conditions triggers `"Whatever."`.

## Walkthrough of Selected Contract Cases

### 1. Asking a Question
- **Input**: `"Does this cryogenic chamber make me look fat?"`
- **Analysis**:
  - Contains lowercase letters (`"oes"`), so `is_yelling` is false.
  - Trimming whitespace leaves `"?"` at the end, so `is_asking` is true.
  - Does not qualify as forceful yelling.
- **Result**: `"Sure."`

### 2. Shouting
- **Input**: `"WATCH OUT!"`
- **Analysis**:
  - Contains uppercase letters and no lowercase letters, so `is_yelling` is true.
  - Ends with `"!"`, not `"?"`, so `is_asking` is false.
- **Result**: `"Whoa, chill out!"`

### 3. Forceful Question
- **Input**: `"WHAT'S GOING ON?"`
- **Analysis**:
  - Contains uppercase letters and no lowercase letters, so `is_yelling` is true.
  - Ends with `"?"`, so `is_asking` is true.
  - Satisfies `is_yelling && is_asking`.
- **Result**: `"Calm down, I know what I'm doing!"`

## Contract Boundaries & Unspecified Behavior

- **Non-alphabetic inputs**: Statements with numbers or symbols but no letters (e.g. `"1, 2, 3"` or `"4?"`) do not count as yelling, because shouting requires vocalized (alphabetical) intensity. `"4?"` is a question (`"Sure."`), while `"1, 2, 3"` is a statement (`"Whatever."`).
- **Binary/Non-text data**: The exercise contract applies exclusively to valid text streams; arbitrary binary encodings are outside the specification contract.
