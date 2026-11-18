# RNA Transcription Maintenance

## Purpose
This document describes the readability improvement made to the RNA Transcription reference implementation in `exercises/practice/rna-transcription/.meta/example.awk`.

## Readability Refactoring
The original reference implementation used generic variable names such as `translation` and `out`. 

In this refactor:
* The lookup table was renamed from `translation` to `complement`, directly reflecting the biological rule of DNA to RNA complementary base pairing.
* The output accumulator variable was renamed from `out` to `rna`, making the target product explicit.
* Each field `$i` is assigned to a readable local variable named `nucleotide` before checking membership in the complement array.
* A clear invariant comment was added documenting that valid DNA nucleotides (G, C, T, A) map strictly to RNA complements (C, G, A, U), while any unknown symbol halts execution with an error.

## Behavioral Verification
All 9 test cases in `test-rna-transcription.bats` pass with identical output. The baseline cases (`Empty RNA sequence`, `RNA complement of cytosine is guanine`, and `RNA complement of guanine is cytosine`) were verified directly before and after the change. No external dependencies or API changes were introduced.
