# Two Fer — Mutation Test Finding

## Purpose
Verify that the test suite distinguishes the correct reference implementation from a deliberate mutation.

## Deliberate mutation
Original rule: NF {name = $0}
Mutated rule: NR {name = $0}

## Distinguishing test
- Bats test: empty file given
- Input: a file containing one newline (one blank record).
- Expected: One for you, one for me.
- Actual with mutation: One for , one for me.

## Results
- Original reference: all four tests pass.
- Mutated reference: only empty file given fails.
- The empty-file Bats case has no canonical UUID in .meta/tests.toml.

## Reproduction
Run: python3 work/R06-T043/check.py
The checker applies the mutation only to a temporary copy.
Detailed results and tool versions are in work/R06-T043/evidence.md.
