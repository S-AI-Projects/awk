# Beer Song Maintenance

## Purpose
This document explains the test source and reproducibility for the Beer Song exercise in the AWK track.

## Test Source and Input Files
The test suite for Beer Song is located at:
`exercises/practice/beer-song/test-beer-song.bats`

The test suite is maintained from these sources:
* `exercises/practice/beer-song/.meta/tests.toml`: Lists all canonical test cases from problem specifications.
* `exercises/practice/beer-song/.meta/config.json`: Declares the solution stub, test file, and example implementation.
* `canonical-data.json`: Located in the problem specifications cache.

No per exercise Jinja template (`template.j2`) is used for Beer Song because the tests require specific command line variable passing using `-v verse=...` and `-v verses=...`. The test file is maintained by hand directly adhering to the canonical specification cases.

## Canonical Case Mapping
The test cases include the following key verses:

| Canonical UUID | Canonical Description | Bats Test Name | AWK Invocation |
|---|---|---|---|
| `5a02fd08-d336-4607-8006-246fe6fa9fb0` | first generic verse | `first_generic_verse` | `gawk -f beer-song.awk -v verse=99` |
| `77299ca6-545e-4217-a9cc-606b342e0187` | last generic verse | `3rd_last_generic_verse` | `gawk -f beer-song.awk -v verse=3` |
| `102cbca0-b197-40fd-b548-e99609b06428` | verse with 2 bottles | `2nd_last_generic_verse` | `gawk -f beer-song.awk -v verse=2` |
| `b8ef9fce-960e-4d85-a0c9-980a04ec1972` | verse with 1 bottle | `penultimate_verse` | `gawk -f beer-song.awk -v verse=1` |
| `c59d4076-f671-4ee3-baaa-d4966801f90d` | verse with 0 bottles | `verse_with_zero_bottles` | `gawk -f beer-song.awk -v verse=0` |
| `7e17c794-402d-4ca6-8f96-4d8f6ee1ec7e` | first two verses | `first_two_verses` | `gawk -f beer-song.awk -v verse=99 -v verses=2` |
| `949868e7-67e8-43d3-9bb4-69277fe020fb` | last three verses | `last_three_verses` | `gawk -f beer-song.awk -v verse=2 -v verses=3` |
| `bc220626-126c-4e72-8df4-fddfc0c3e458` | all verses | `all_verses` | `gawk -f beer-song.awk` |

## Reproduction and Validation
To verify the test suite against the reference implementation, run:

```bash
bin/validate_one_exercise exercises/practice/beer-song
```

The course check script at `tools/course_checks/r06-t052.py` verifies reproducibility across two independent repository copies, ensuring all 8 tests are preserved and match with no dropped cases.
