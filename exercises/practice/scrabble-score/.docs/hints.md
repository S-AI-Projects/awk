# Hints

## Contract Walkthrough and Decision Table

In the AWK track, `scrabble-score` processes each line as an input word and prints the normalized uppercase word and its computed score separated by a comma (using AWK's output field separator, `OFS = ","`).

### Selected Cases Decision Table
| Case | Input | Case Normalization | Character Values | AWK Representation Output |
|---|---|---|---|---|
| **lowercase letter** | `a` | `toupper("a")` -> `"A"` | `tile["A"] = 1` | `A,1` |
| **uppercase letter** | `A` | `toupper("A")` -> `"A"` | `tile["A"] = 1` | `A,1` |
| **valuable letter** | `f` | `toupper("f")` -> `"F"` | `tile["F"] = 4` | `F,4` |

### AWK Representation and Implementation Details
- **Letter Decomposition**: In GNU AWK, setting the field separator or calling `split($1, letters, //)` splits a string into individual single-character array elements.
- **Scoring Map**: Associative arrays (hash maps) populated during `BEGIN` provide $O(1)$ lookups for each letter.
- **Output Format**: Emitting `print $1, sum` with `OFS = ","` produces comma-delimited output matching the test assertions.

### Contract Boundaries and Unspecified Behavior
- **Case Invariance**: The scoring is strictly case-insensitive. Both lowercase and uppercase inputs yield identical scores and are formatted as uppercase in the output.
- **Ordering and Structure**: Letters may appear in any order in multi-character words; the score is commutative (sum of tile values).
- **Unspecified Behavior**: Characters not defined in the Scrabble alphabet (such as spaces or unknown symbols) default to 0 in an uninitialized associative array lookup. The specification does not require extra exception rules or custom error handling for inputs outside the standard domain.
