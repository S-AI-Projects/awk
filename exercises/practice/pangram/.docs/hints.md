# Hints

## Contract Cases Walkthrough

A pangram is a sentence using every letter of the English alphabet at least once. Case is insensitive, and non alphabetic characters are ignored.

### Selected Contract Cases

| Case Name | Input String | Unique Letters Found | Expected Output | Contract Reason |
|---|---|---|---|---|
| `empty sentence` | `""` | 0 | `false` | An empty string has no characters. 0 letters is less than 26, so the result is false. |
| `perfect lower case` | `"abcdefghijklmnopqrstuvwxyz"` | 26 | `true` | Contains each lowercase letter from 'a' to 'z' exactly once with no repetitions. |
| `only lower case` | `"the quick brown fox jumps over the lazy dog"` | 26 | `true` | Contains all 26 letters with spaces and repeat letters. Repeating letters do not invalidate a pangram. |

### AWK Representation and Implementation
* In AWK, you can split a line into individual characters using `split($0, chars, "")`.
* Loop through the characters, check if each character is alphabetic using `/[[:alpha:]]/`, and normalize it using `tolower()`.
* Store seen characters as keys in an associative array like `seen[tolower(c)] = 1`.
* In AWK, the number of unique keys in the array can be checked with `length(seen)`. If `length(seen) == 26`, the input is a pangram.

### Unspecified Behavior
* **Non ASCII characters:** Non English letters with accents or symbols outside basic ASCII 'a' through 'z' are outside the problem contract.
* **Stream termination:** The contract evaluates each input line independently. Missing letters simply produce the output string `"false"` with success exit code 0 rather than raising an error.
