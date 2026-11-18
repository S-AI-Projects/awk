# Pangram Maintenance

## Purpose
This document records the contract analysis and decision table for the Pangram exercise in AWK.

## Contract Decision Table

The exercise specification defines a pangram as a sentence containing all 26 letters of the English alphabet. The table below connects the input condition to its required output for the target contract cases:

| Test Case Name | Input String | Alphabet Coverage | Output | Invariant / Specification Rule |
|---|---|---|---|---|
| `empty sentence` | `""` | 0 of 26 | `false` | A string with 0 letters cannot satisfy the full alphabet requirement. |
| `perfect lower case` | `"abcdefghijklmnopqrstuvwxyz"` | 26 of 26 (exact) | `true` | Minimal panalphabetic string where each letter appears exactly once. |
| `only lower case` | `"the quick brown fox jumps over the lazy dog"` | 26 of 26 (with repeats and spaces) | `true` | Standard pangram sentence with spaces and duplicates; only letter presence matters. |

## Contract Boundaries
* **Case Insensitivity:** Uppercase and lowercase forms map to the same letter bucket.
* **Non-letters:** Punctuation marks, numbers, and spaces are ignored.
* **Unspecified Behavior:** Behavior for non-ASCII letters (such as accented characters) is outside the exercise contract and not assumed or enforced.

## Verification
The reference implementation was validated against all 10 Bats test cases in `test-pangram.bats`. All 10 cases passed cleanly.
