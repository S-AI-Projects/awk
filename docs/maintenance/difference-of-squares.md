# Difference of Squares Maintenance

## Canonical Test Cases Mapping

The canonical test cases for difference of squares check three operations: square of sum, sum of squares, and the difference between them. In the AWK track, input arrives as comma separated values like `square_of_sum,5`. The script parses the function name into `$1` and the integer into `$2`, calling the target function directly.

| UUID | Test Case Title | Inclusion Status | AWK Rationale |
|---|---|---|---|
| `e46c542b-31fc-4506-bcae-6b62b3268537` | square of sum 1 | Included | Tests the lower boundary where n is 1. The loop runs once, sum is 1, and 1 squared produces 1. This verifies base loop initialization in AWK. |
| `9b3f96cb-638d-41ee-99b7-b4f9c0622948` | square of sum 5 | Included | Tests a typical small positive integer. The loop accumulates numbers from 1 to 5 to reach 15, and 15 squared produces 225. This checks general loop iteration. |
| `54ba043f-3c35-4d43-86ff-3a41625d5e86` | square of sum 100 | Included | Tests a larger input value. The loop accumulates numbers from 1 to 100 to reach 5050, and squaring produces 25502500. This confirms that standard AWK integer arithmetic calculates the large sum without any precision issues. |

## Notes
All 9 canonical cases from problem specifications are active and enabled in the AWK track test suite. There are zero exclusions for this exercise.
