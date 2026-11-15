# R06-T043 — Two Fer mutation check

## Mutation

Changed the copied reference rule from:

`NF {name = $0}`

to:

`NR {name = $0}`

The working-tree reference implementation was not modified.

## Baseline

Validator exit code: 0

```text
Processing two-fer
1..4
ok 1 no file given
ok 2 empty file given
ok 3 a name given
ok 4 name with a space

```

## Mutated implementation

Validator exit code: 1

```text
Processing two-fer
1..4
ok 1 no file given
not ok 2 empty file given
# (from function `assert_output' in file bats-extra.bash, line 394,
#  in test file test-two-fer.bats, line 39)
#   `assert_output "One for you, one for me."' failed
#
# -- output differs --
# expected : One for you, one for me.
# actual   : One for , one for me.
# --
#
ok 3 a name given
ok 4 name with a space

```

## Distinguishing input

Input file contents: one newline (one blank record).

Expected output: `One for you, one for me.`

Actual output: `One for , one for me.`

## Tool versions

- GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)
- Bats 1.14.0
- GNU bash, version 5.3.20(1)-release (aarch64-apple-darwin27.0.0)
- jq-1.7.1-apple
- Python 3.14.7
