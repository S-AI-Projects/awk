# Verification Evidence: R06-T037 (Killer Sudoku Helper Construct & Pitfall)

## Summary of Results
- **Validation Run**: 13/13 test cases passed in `test-killer-sudoku-helper.bats`.
- **Baseline Cases**: Explicitly verified `1`, `2`, and `3`.
- **Learner Stub**: `exercises/practice/killer-sudoku-helper/killer-sudoku-helper.awk` remains untouched and unsolved.
- **Language Construct Selected**: Dynamic Field Manipulation via `NF`, `$NF`, and record reconstruction (`$0`).
- **Micro-Examples Tested**:
  - Micro-Example 1 (Push/Pop with `NF++` and `NF--`): Output matched expected `1 2\n1 3`.
  - Micro-Example 2 (Contrasting Pitfall omitting `NF--`): Output matched expected `1 2\n1 2 3`.
- **Hints Published**: Published in `exercises/practice/killer-sudoku-helper/.docs/hints.md`.

## Micro-Example Comparison Table
| Snippet | Construct / Control Flow | Expected Output | Actual Output | Agreement |
|:---|:---|:---:|:---:|:---:|
| **Snippet 1 (Stack Push/Pop)** | `push(1); push(2); print; pop(); push(3); print` | `1 2\n1 3` | `1 2\n1 3` | Pass |
| **Snippet 2 (Omitted Pop)** | `push(1); push(2); print; push(3); print` | `1 2\n1 2 3` | `1 2\n1 2 3` | Pass |

## Construct Explanation
- **Why Associative Array Traversal is Incompatible**: `for (key in array)` traverses keys in unspecified hash table order. Killer Sudoku combinations must be sorted in strictly ascending order.
- **Why Dynamic Field Manipulation (`NF` / `$NF`) is Ideal**:
  - Increments `NF` to push elements onto AWK's built-in field list.
  - Automatically joins fields with single spaces (`OFS`) upon invoking `print`.
  - Backtracks cleanly by decrementing `NF` (`NF--`).
