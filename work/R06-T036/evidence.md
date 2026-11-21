# Verification Evidence: R06-T036 (Acronym Paradigm Comparison)

## Summary of Results
- **Validation Runs**: 9/9 test cases passed on the reference (`example.awk`).
- **Alternative Run**: 9/9 test cases passed on the alternative (`FPAT`).
- **Baseline Cases**: Verified agreement on `basic`, `lowercase words`, `punctuation`.
- **Learner Stub**: `exercises/practice/acronym/acronym.awk` remains untouched and unsolved.
- **Hint Document**: Created `exercises/practice/acronym/.docs/hints.md` containing worked examples and trade-off explanations without spoiling the solution.

## Test Agreement Table
| Test Name | Input Phrase | Expected | Ref Output | Alt Output | Agreement |
|:---|:---|:---:|:---:|:---:|:---:|
| `basic` | `Portable Network Graphics` | `PNG` | `PNG` | `PNG` | Pass |
| `lowercase words` | `Ruby on Rails` | `ROR` | `ROR` | `ROR` | Pass |
| `punctuation` | `First In, First Out` | `FIFO` | `FIFO` | `FIFO` | Pass |
| `all caps word` | `GNU Image Manipulation Program` | `GIMP` | `GIMP` | `GIMP` | Pass |
| `punctuation without whitespace` | `Complementary metal-oxide semiconductor` | `CMOS` | `CMOS` | `CMOS` | Pass |
| `very long abbreviation` | `Rolling On The Floor Laughing So Hard That My Dogs Came Over And Licked Me` | `ROTFLSHTMDCOALM` | `ROTFLSHTMDCOALM` | `ROTFLSHTMDCOALM` | Pass |
| `consecutive delimiters` | `Something - I made up from thin air` | `SIMUFTA` | `SIMUFTA` | `SIMUFTA` | Pass |
| `apostrophes` | `Halley's Comet` | `HC` | `HC` | `HC` | Pass |
| `underscore emphasis` | `The Road _Not_ Taken` | `TRNT` | `TRNT` | `TRNT` | Pass |

## Trade-off Analysis
1. **Approach 1 (Reference - `FS = "[[:blank:]-]+"` + `gsub`)**:
   - *Strengths*: Standard POSIX AWK compatibility; simple field delimiter logic.
   - *Weaknesses*: Mutates `$i` in place, triggering `$0` recomputation; requires secondary regular expression sanitization per field.
2. **Approach 2 (Alternative - `FPAT = "[[:alpha:]][[:alpha:]']*"`)**:
   - *Strengths*: Directly extracts word tokens, bypassing punctuation; eliminates `$i` mutation and per-field `gsub` calls.
   - *Weaknesses*: Depends on GNU AWK specific `FPAT` feature; requires regex engine to maintain token state across entire string.
