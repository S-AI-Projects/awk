# Hints

## Approach Selection

When extracting words and counting occurrences in AWK, there are two primary architectural approaches:

### Approach 1: Declarative Field Pattern Matching (`FPAT`)
- **Concept**: GNU AWK allows configuring `FPAT` (field pattern) rather than `FS` (field separator). Setting `FPAT` to match word tokens (such as `"[[:alnum:]]+('[[:alpha:]]+)?"`) instructs the AWK record parser to automatically populate positional fields (`$1, $2, ... $NF`) with matching tokens.
- **Data Representation**: Fields are accessed positionally via `$i` up to `NF`, and normalized into an associative frequency array: `count[tolower($i)]++`.
- **Trade-off**:
  - *Advantages*: Highly concise, idiomatic in GNU AWK, and delegates tokenization directly to the internal C parsing engine.
  - *Disadvantages*: `FPAT` is a GNU AWK extension and is not portable to standard POSIX `awk` or `mawk`.

### Approach 2: Iterative Token Matching (`match` + `substr`)
- **Concept**: Repeatedly identify word tokens in the input record using the standard built-in `match()` function, extract the matched slice using `substr()`, update the associative frequency table, and advance past the match (`RSTART + RLENGTH`).
- **Data Representation**: A stateful loop advancing through the line buffer and tracking word counts in an associative table.
- **Trade-off**:
  - *Advantages*: Strictly POSIX AWK compliant and portable across all AWK implementations.
  - *Disadvantages*: Requires manual loop state management and incurs additional string allocation overhead for intermediate substrings.

### Small Worked Input
Consider the input string:
`"don't stop, go Go!"`

1. **Token Extraction**:
   - The token pattern extracts `"don't"`, `"stop"`, `"go"`, and `"Go"`, stripping punctuation like commas and exclamation marks while preserving internal apostrophes.
2. **Case Normalization**:
   - Applying `tolower()` maps both `"go"` and `"Go"` to the single key `"go"`.
3. **Accumulated Frequency**:
   - `don't`: 1
   - `stop`: 1
   - `go`: 2
