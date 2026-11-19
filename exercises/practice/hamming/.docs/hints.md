# Hints

## General

- The input file contains two lines (records), where the first record represents the first DNA strand and the second record represents the second DNA strand.
- In AWK, the current record number is tracked by `NR`, allowing you to store the first strand when `NR == 1` and process the second strand when `NR == 2`.
- Unequal length strands must emit the error message `"strands must be of equal length"` to `/dev/stderr` and terminate with a non-zero exit code (`exit 1`).

## Approach Selection

There are two primary paradigms in AWK to compare two sequences character by character:

### 1. Positional Field Splitting (`FS = ""`)
- **Data Representation**: Setting `FS = ""` in a `BEGIN` block tells AWK to break each character into a distinct field variable (`$1, $2, ..., $NF`).
- **Control Flow**:
  - Store fields `$1..$NF` of the first record into an associative array (e.g. `strand[i] = $i`).
  - When processing the second record, iterate through `$1..$NF` and count positions where `$i != strand[i]`.
- **Trade-offs**:
  - *Pros*: Natural AWK field syntax; fast direct array lookups.
  - *Cons*: Allocates $N$ distinct field variables and array elements in AWK's internal symbol table. Also, character-level field splitting with `FS = ""` is a GNU Awk extension and not strictly mandated by POSIX standard awk.

### 2. Direct Substring Scanning (`substr`)
- **Data Representation**: Keep records as standard monolithic strings without modifying `FS`.
- **Control Flow**:
  - Save the first record string into a scalar variable (e.g. `first = $0`).
  - When processing the second record, use a loop from `1` to `length($0)` and inspect single characters using `substr(first, i, 1)` and `substr($0, i, 1)`.
- **Trade-offs**:
  - *Pros*: Portable across all POSIX-compliant AWK implementations. Avoids allocating array hash tables and individual field structures, using minimal $\mathcal{O}(1)$ auxiliary memory.
  - *Cons*: Invokes the `substr()` built-in function twice per character comparison.

### Worked Example

Consider the inputs `"GAGC"` (record 1) and `"GATC"` (record 2):
1. Both strings have length 4 (`length(first) == length($0)`), so validation passes.
2. Iterating through positions 1 to 4:
   - Index 1: `'G'` vs `'G'` $\rightarrow$ match
   - Index 2: `'A'` vs `'A'` $\rightarrow$ match
   - Index 3: `'G'` vs `'T'` $\rightarrow$ mismatch! (`diff` increments from 0 to 1)
   - Index 4: `'C'` vs `'C'` $\rightarrow$ match
3. Final Hamming distance printed: `1`.
