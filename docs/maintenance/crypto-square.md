# Crypto Square Maintenance

## Purpose
This document compares two implementation approaches for the Crypto Square exercise in AWK: the reference field accumulation method and an alternative explicit 2D column major matrix method.

## Approach Comparison

| Metric / Aspect | Approach 1: Positional Field Accumulation (Reference) | Approach 2: Explicit 2D Matrix Transposition (Alternative) |
|---|---|---|
| **Primary Mechanism** | Modulo field indexing into AWK `$chunk` variables | Pre padded string with nested column row index mapping `(r-1)*cols + c` |
| **Control Flow** | Single loop from 0 to `(rows * cols - 1)` | Two nested loops: column outer loop `1..cols`, row inner loop `1..rows` |
| **Output Assembly** | Automatic space separation via AWK `print` on `$0` | Explicit string concatenation with space delimiter |
| **String Normalization** | GNU extension `gensub()` | Portable POSIX `gsub()` and `tolower()` |
| **Memory Characteristics** | Allocates AWK internal field table | Allocates a padded string of length `rows * cols` |
| **Readability** | Compact and idiomatic AWK, but abstract field math | Highly transparent, maps directly to linear algebra transposition |

## Verification on Baseline Cases
Both approaches were verified against all 8 tests in `test-crypto-square.bats`. They agree exactly on all test cases, including the following key baseline cases:
1. `empty plaintext results in an empty ciphertext` (input: `""` -> output: `""`)
2. `normalization results in empty plaintext` (input: `"... --- ..."` -> output: `""`)
3. `Lowercase` (input: `"A"` -> output: `"a"`)

The alternative implementation is preserved under `work/R06-T056/alternative.awk` for automated regression checks.
