# Tournament Exercise Maintenance & Test Generation Route

## 1. Overview & Context

- **Exercise**: `tournament`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T012`
- **Learner Stub**: `exercises/practice/tournament/tournament.awk`
- **Reference Solution**: `exercises/practice/tournament/.meta/example.awk`
- **Test Suite**: `exercises/practice/tournament/test-tournament.bats`
- **Test Configuration**: `exercises/practice/tournament/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/tournament/.meta/config.json`

## 2. Test Generation Route Analysis

In the Exercism AWK track repository, test generation is governed by `bin/generate_tests`:
- Exercises containing a Jinja2 template (`.meta/template.j2`) are dynamically rendered against the canonical specifications in `problem-specifications/exercises/<exercise>/canonical-data.json`, filtered by `.meta/tests.toml`.
- For `tournament`, **no per-exercise Jinja template (`template.j2`) exists**.
- As specified in the generator design and track maintenance policy, `test-tournament.bats` is a hand-maintained Bats test suite that directly implements the canonical test cases tracked in `.meta/tests.toml`.
- The track's test generator does not invent a synthetic template interface; instead, the maintained Bats test suite serves as the authoritative source for testing tournament tallying behavior in AWK.

## 3. Canonical Test Cases & Key Verification Anchors

All 12 canonical test cases tracked in `.meta/tests.toml` are enabled (default `include = true`) and have corresponding test definitions in `test-tournament.bats`.

### Key Verification Anchors

Verification of the test route is anchored on the following three key test cases:

1. **"just the header if no input"**
   - **UUID**: `67e9fab1-07c1-49cf-9159-bc8671cc7c9c`
   - **Input**: `""` (empty input)
   - **Expected Output**:
     ```text
     Team                           | MP |  W |  D |  L |  P
     ```
   - **Rationale**: Verifies that when no match results are supplied, the script prints only the formatted table header without empty rows or syntax errors.

2. **"a win is three points, a loss is zero points"**
   - **UUID**: `1b4a8aef-0734-4007-80a2-0626178c88f4`
   - **Input**: `"Allegoric Alaskans;Blithering Badgers;win"`
   - **Expected Output**:
     ```text
     Team                           | MP |  W |  D |  L |  P
     Allegoric Alaskans             |  1 |  1 |  0 |  0 |  3
     Blithering Badgers             |  1 |  0 |  0 |  1 |  0
     ```
   - **Rationale**: Verifies the primary point tallying rule: a win grants 3 points to the winning team and 0 points (with 1 loss) to the opposing team.

3. **"a win can also be expressed as a loss"**
   - **UUID**: `5f45ac09-4efe-46e7-8ddb-75ad85f86e05`
   - **Input**: `"Blithering Badgers;Allegoric Alaskans;loss"`
   - **Expected Output**:
     ```text
     Team                           | MP |  W |  D |  L |  P
     Allegoric Alaskans             |  1 |  1 |  0 |  0 |  3
     Blithering Badgers             |  1 |  0 |  0 |  1 |  0
     ```
   - **Rationale**: Verifies symmetric handling of match outcomes: when team 1 is marked as `loss`, team 2 is credited with the win and sorted ahead by points.

### Full Canonical Test Case Mapping

| # | UUID | Description in `tests.toml` | Test Name in `test-tournament.bats` | Status | Anchor |
|---|------|----------------------------|--------------------------------------|--------|--------|
| 1 | `67e9fab1-07c1-49cf-9159-bc8671cc7c9c` | `just the header if no input` | `just the header if no input` | Active (1st test, unskipped) | Yes |
| 2 | `1b4a8aef-0734-4007-80a2-0626178c88f4` | `a win is three points, a loss is zero points` | `a win is three points, a loss is zero points` | Active (skipped by default) | Yes |
| 3 | `5f45ac09-4efe-46e7-8ddb-75ad85f86e05` | `a win can also be expressed as a loss` | `a win can also be expressed as a loss` | Active (skipped by default) | Yes |
| 4 | `fd297368-efa0-442d-9f37-dd3f9a437239` | `a different team can win` | `a different team can win` | Active (skipped by default) | No |
| 5 | `26c016f9-e753-4a93-94e9-842f7b4d70fc` | `a draw is one point each` | `a draw is one point each` | Active (skipped by default) | No |
| 6 | `731204f6-4f34-4928-97eb-1c307ba83e62` | `There can be more than one match` | `There can be more than one match` | Active (skipped by default) | No |
| 7 | `49dc2463-42af-4ea6-95dc-f06cc5776adf` | `There can be more than one winner` | `There can be more than one winner` | Active (skipped by default) | No |
| 8 | `6d930f33-435c-4e6f-9e2d-63fa85ce7dc7` | `There can be more than two teams` | `There can be more than two teams` | Active (skipped by default) | No |
| 9 | `97022974-0c8a-4a50-8fe7-e36bdd8a5945` | `typical input` | `typical input` | Active (skipped by default) | No |
| 10 | `fe562f0d-ac0a-4c62-b9c9-44ee3236392b` | `incomplete competition (not all pairs have played)` | `incomplete competition (not all pairs have played)` | Active (skipped by default) | No |
| 11 | `3aa0386f-150b-4f99-90bb-5195e7b7d3b8` | `ties broken alphabetically` | `ties broken alphabetically` | Active (skipped by default) | No |
| 12 | `f9e20931-8a65-442a-81f6-503c0205b17a` | `ensure points sorted numerically` | `ensure points sorted numerically` | Active (skipped by default) | No |

## 4. Determinism & Isolation Verification

- **Determinism Check**: The test suite file `test-tournament.bats` contains stable, reproducible test cases without non-deterministic components. Copying and executing the test suite across independent temporary runs generates identical results.
- **CI Validation**: When run via `bin/validate_one_exercise exercises/practice/tournament`:
  1. The validator confirms `exercises/practice/tournament/.meta/config.json` specifies valid file entries.
  2. The validator verifies that exactly one commented skip directive exists (`#[[ $BATS_RUN_SKIPPED == "true" ]] || skip` on test 1).
  3. The validator creates an isolated temporary directory, copies `.meta/example.awk` as `tournament.awk`, copies `test-tournament.bats` and `bats-extra.bash`, and runs `BATS_RUN_SKIPPED=true bats test-tournament.bats`.
  4. All 12 test cases execute and pass cleanly.
- **Learner Stub Preservation**: `tournament.awk` remains an unsolved stub in the working tree, preserving the learning experience for track students.
