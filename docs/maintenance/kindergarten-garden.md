
# Kindergarten Garden — Canonical Test Decisions

## Overview

This document records the rationale for the three selected canonical test cases in `exercises/practice/kindergarten-garden/.meta/tests.toml`.

All 17 canonical test cases remain included. None of the selected cases is excluded because each verifies supported behaviour of the kindergarten-garden exercise.

## Canonical Case Mapping

| UUID | Test description | Decision | Rationale |
|---|---|---|---|
| `1fc316ed-17ab-4fba-88ef-3ae78296b692` | Partial garden → garden with single student | Keep included | Verifies that the reference solution correctly assigns four plants to Alice from the two rows. |
| `acd19dc1-2200-4317-bc2a-08f021276b40` | Partial garden → different garden with single student | Keep included | Verifies a different plant arrangement and confirms that plant order is preserved when converting plant codes into names. |
| `c376fcc8-349c-446c-94b0-903947315757` | Partial garden → garden with two students | Keep included | Verifies that Bob receives the correct four plants based on the student ordering and the corresponding garden columns. |

## Reference Implementation Details

The maintained GNU AWK reference implementation uses the following operations:

- `FPAT = ".."`: treats each two-character pair in a garden row as a separate field.
- `split(...)`: establishes the ordered list of student names and separates the assigned plant codes.
- `plots[names[i]]`: associates each student's name with their assigned garden sections.
- `plants[...]`: maps plant codes (`G`, `C`, `R`, and `V`) to their corresponding plant names.

These operations support the three selected cases by checking plant parsing, ordering, and student-specific assignment.

## Inclusion Summary

| Metric | Before | After |
|---|---:|---:|
| Total canonical cases | 17 | 17 |
| Included cases | 17 | 17 |
| Excluded cases | 0 | 0 |

No inclusion or exclusion values were changed. Only explanatory `comment` keys were added to the three selected UUID entries in `tests.toml`.

## Verification

The automated verification is performed using:

```bash
python3 work/R06-T041/check.py
```

The check runs the maintained reference implementation against the canonical Bats tests in a temporary exercise copy. The original learner solution is kept unchanged.

Expected verification:

- All 17 canonical tests execute.
- All 17 tests pass against the maintained reference.
- A zero-test run or non-zero validator exit is treated as a failure.
- The original learner solution remains unchanged.
