# Hints

## General

- In AWK, you can split strings into chunks using the `FPAT` variable (field pattern) or by slicing substrings with the `substr()` function.
- An associative array can map three-letter codon sequences (such as `"AUG"`) to their corresponding protein names.

## Processing Codons

- When iterating through matched codons in AWK (using fields `$1` through `$NF`), remember that AWK field indices are 1-based and run through `$NF` inclusive.
- Be careful with loop boundary conditions: using a strict upper-bound inequality (`i < NF`) is a common off-by-one error borrowed from 0-indexed languages. With `< NF`, single-codon sequences (such as `"AUG"`) will have zero iterations and produce empty output, and multi-codon sequences will omit their final codon. Ensure your loop condition processes through the last codon (`i <= NF`).
- Remember to stop translating immediately when encountering a `STOP` codon, ignoring any subsequent codons.
- For output formatting, ensure multiple protein names are separated by a single space without leading or trailing whitespace.
