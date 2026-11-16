# Protein Translation Exercise Maintenance & Mutation Analysis

## 1. Overview & Context

- **Exercise**: `protein-translation`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T013`
- **Learner Solution Stub**: `exercises/practice/protein-translation/protein-translation.awk`
- **Reference Solution**: `exercises/practice/protein-translation/.meta/example.awk`
- **Test Suite**: `exercises/practice/protein-translation/test-protein-translation.bats`
- **Test Configuration**: `exercises/practice/protein-translation/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/protein-translation/.meta/config.json`
- **Hints Guide**: `exercises/practice/protein-translation/.docs/hints.md`

## 2. Mutation Experiment & Rejection Analysis

### Mutant Definition & Diff

A deliberate boundary condition mutation was introduced into the codon iteration loop of the reference solution:

```diff
--- a/exercises/practice/protein-translation/.meta/example.awk
+++ b/exercises/practice/protein-translation/.meta/example.awk
@@ -25,1 +25,1 @@
-    for (i = 1; i <= NF; i++) {
+    for (i = 1; i < NF; i++) {
```

### Underlying Contract & Mistaken Assumption

- **Underlying Contract**:
  In AWK, splitting an RNA sequence into three-letter codon chunks using `FPAT = "..."` sets `NF` to the total number of matched codons, accessible via fields `$1` through `$NF`. Because AWK field variables are 1-indexed and inclusive, processing every codon requires traversing up to and including `$NF` (`i <= NF`).
- **Mistaken Assumption Exposed**:
  Developers transitioning from 0-indexed languages (e.g., C, Python, JavaScript) frequently assume exclusive upper bounds (`i < count`). Under `i < NF`, any single-codon sequence has `NF = 1`, resulting in `1 < 1` evaluating to false: the translation loop executes zero times and produces an empty string. For multi-codon sequences, the final codon is skipped.

### Behavior Across Named Starting Cases

Evaluation began across the canonical initial cases:

1. **"Empty RNA sequence results in no proteins"**
   - **UUID**: `2c44f7bf-ba20-43f7-a3bf-f2219c0c3f98`
   - **Input**: `""`
   - **Expected**: Exit code 0, output `""`
   - **Mutant Result**: **PASSES** (`NF = 0`; the loop `for (i = 1; i < 0; i++)` does not execute, producing empty string output as required).

2. **"Methionine RNA sequence"**
   - **UUID**: `96d3d44f-34a2-4db4-84cd-fff523e069be`
   - **Input**: `"AUG"`
   - **Expected**: Exit code 0, output `"Methionine"`
   - **Mutant Result**: **FAILS / REJECTED** (`NF = 1`; `i < NF` evaluates to `1 < 1` which is false; loop produces `""`).
   - **Failing Assertion**: `assert_output "Methionine"` at line 17 of `test-protein-translation.bats`.

3. **"Phenylalanine RNA sequence 1"**
   - **UUID**: `1b4c56d8-d69f-44eb-be0e-7b17546143d9`
   - **Input**: `"UUU"`
   - **Expected**: Exit code 0, output `"Phenylalanine"`
   - **Mutant Result**: **FAILS / REJECTED** (`NF = 1`; produces `""`).

### Smallest Rejecting Case

- **Test Description**: `Methionine RNA sequence`
- **Test UUID**: `96d3d44f-34a2-4db4-84cd-fff523e069be`
- **Test ID in Bats**: Test #2
- **Input**: `"AUG"` (length 3, 1 codon)
- **Expected Output**: `"Methionine"`
- **Actual Output**: `""`
- **Failing Assertion**: `assert_output "Methionine"` (`test-protein-translation.bats:17`)

## 3. Canonical Test Cases Mapping

All 31 canonical test cases tracked in `.meta/tests.toml` are enabled and map directly to `test-protein-translation.bats`:

| # | UUID | Description in `tests.toml` | Bats Test Name | Ref Status | Mutant Status |
|---|------|----------------------------|----------------|------------|---------------|
| 1 | `2c44f7bf-ba20-43f7-a3bf-f2219c0c3f98` | Empty RNA sequence results in no proteins | Empty RNA sequence results in no proteins | PASS | PASS |
| 2 | `96d3d44f-34a2-4db4-84cd-fff523e069be` | Methionine RNA sequence | Methionine RNA sequence | PASS | **FAIL (Smallest Rejecting Case)** |
| 3 | `1b4c56d8-d69f-44eb-be0e-7b17546143d9` | Phenylalanine RNA sequence 1 | Phenylalanine RNA sequence 1 | PASS | FAIL |
| 4 | `81b53646-bd57-4732-b2cb-6b1880e36d11` | Phenylalanine RNA sequence 2 | Phenylalanine RNA sequence 2 | PASS | FAIL |
| 5 | `42f69d4f-19d2-4d2c-a8b0-f0ae9ee1b6b4` | Leucine RNA sequence 1 | Leucine RNA sequence 1 | PASS | FAIL |
| 6 | `ac5edadd-08ed-40a3-b2b9-d82bb50424c4` | Leucine RNA sequence 2 | Leucine RNA sequence 2 | PASS | FAIL |
| 7 | `8bc36e22-f984-44c3-9f6b-ee5d4e73f120` | Serine RNA sequence 1 | Serine RNA sequence 1 | PASS | FAIL |
| 8 | `5c3fa5da-4268-44e5-9f4b-f016ccf90131` | Serine RNA sequence 2 | Serine RNA sequence 2 | PASS | FAIL |
| 9 | `00579891-b594-42b4-96dc-7ff8bf519606` | Serine RNA sequence 3 | Serine RNA sequence 3 | PASS | FAIL |
| 10 | `08c61c3b-fa34-4950-8c4a-133945570ef6` | Serine RNA sequence 4 | Serine RNA sequence 4 | PASS | FAIL |
| 11 | `54e1e7d8-63c0-456d-91d2-062c72f8eef5` | Tyrosine RNA sequence 1 | Tyrosine RNA sequence 1 | PASS | FAIL |
| 12 | `47bcfba2-9d72-46ad-bbce-22f7666b7eb1` | Tyrosine RNA sequence 2 | Tyrosine RNA sequence 2 | PASS | FAIL |
| 13 | `3a691829-fe72-43a7-8c8e-1bd083163f72` | Cysteine RNA sequence 1 | Cysteine RNA sequence 1 | PASS | FAIL |
| 14 | `1b6f8a26-ca2f-43b8-8262-3ee446021767` | Cysteine RNA sequence 2 | Cysteine RNA sequence 2 | PASS | FAIL |
| 15 | `1e91c1eb-02c0-48a0-9e35-168ad0cb5f39` | Tryptophan RNA sequence | Tryptophan RNA sequence | PASS | FAIL |
| 16 | `e547af0b-aeab-49c7-9f13-801773a73557` | STOP codon RNA sequence 1 | STOP codon RNA sequence 1 | PASS | PASS |
| 17 | `67640947-ff02-4f23-a2ef-816f8a2ba72e` | STOP codon RNA sequence 2 | STOP codon RNA sequence 2 | PASS | PASS |
| 18 | `9c2ad527-ebc9-4ace-808b-2b6447cb54cb` | STOP codon RNA sequence 3 | STOP codon RNA sequence 3 | PASS | PASS |
| 19 | `f4d9d8ee-00a8-47bf-a1e3-1641d4428e54` | Sequence of two protein codons translates into proteins | Sequence of two protein codons translates into proteins | PASS | FAIL |
| 20 | `dd22eef3-b4f1-4ad6-bb0b-27093c090a9d` | Sequence of two different protein codons translates into proteins | Sequence of two different protein codons translates into proteins | PASS | FAIL |
| 21 | `d0f295df-fb70-425c-946c-ec2ec185388e` | Translate RNA strand into correct protein list | Translate RNA strand into correct protein list | PASS | FAIL |
| 22 | `e30e8505-97ec-4e5f-a73e-5726a1faa1f4` | Translation stops if STOP codon at beginning of sequence | Translation stops if STOP codon at beginning of sequence | PASS | PASS |
| 23 | `5358a20b-6f4c-4893-bce4-f929001710f3` | Translation stops if STOP codon at end of two-codon sequence | Translation stops if STOP codon at end of two-codon sequence | PASS | PASS |
| 24 | `ba16703a-1a55-482f-bb07-b21eef5093a3` | Translation stops if STOP codon at end of three-codon sequence | Translation stops if STOP codon at end of three-codon sequence | PASS | PASS |
| 25 | `4089bb5a-d5b4-4e71-b79e-b8d1f14a2911` | Translation stops if STOP codon in middle of three-codon sequence | Translation stops if STOP codon in middle of three-codon sequence | PASS | PASS |
| 26 | `2c2a2a60-401f-4a80-b977-e0715b23b93d` | Translation stops if STOP codon in middle of six-codon sequence | Translation stops if STOP codon in middle of six-codon sequence | PASS | PASS |
| 27 | `f6f92714-769f-4187-9524-e353e8a41a80` | Sequence of two non-STOP codons does not translate to a STOP codon | Sequence of two non-STOP codons does not translate to a STOP codon | PASS | FAIL |
| 28 | `1e75ea2a-f907-4994-ae5c-118632a1cb0f` | Non-existing codon can't translate | Non-existing codon can't translate | PASS | FAIL |
| 29 | `9eac93f3-627a-4c90-8653-6d0a0595bc6f` | Unknown amino acids, not part of a codon, can't translate | Unknown amino acids, not part of a codon, can't translate | PASS | FAIL |
| 30 | `9d73899f-e68e-4291-b1e2-7bf87c00f024` | Incomplete RNA sequence can't translate | Incomplete RNA sequence can't translate | PASS | PASS |
| 31 | `43945cf7-9968-402d-ab9f-b8a28750b050` | Incomplete RNA sequence can translate if valid until a STOP codon | Incomplete RNA sequence can translate if valid until a STOP codon | PASS | PASS |

## 4. Verification & Validation Architecture

Verification is orchestrated by `work/R06-T013/check.py`:
- Copies the repository cleanly (including dotfiles such as `.meta/`) to isolated temporary directories using `tempfile`.
- Verifies that the unmodified reference implementation `.meta/example.awk` passes all 31 tests via `bin/validate_one_exercise exercises/practice/protein-translation`.
- Applies the documented mutant (`i <= NF` -> `i < NF`) in an independent temporary directory.
- Runs `bin/validate_one_exercise exercises/practice/protein-translation` against the mutant.
- Asserts that:
  - Child exit code for the mutated run is non-zero.
  - Test 1 (`Empty RNA sequence results in no proteins`) passes.
  - Test 2 (`Methionine RNA sequence`, UUID `96d3d44f-34a2-4db4-84cd-fff523e069be`) fails the named assertion `assert_output "Methionine"`.
- Records inputs, expected vs. actual outputs, and tool versions (bash, awk, python, bats) in `work/R06-T013/`.

## 5. Learner Stub Preservation

The learner solution stub `exercises/practice/protein-translation/protein-translation.awk` remains strictly unchanged and unsolved, preserving the learning track experience for students.
