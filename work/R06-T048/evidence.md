# R06-T048 — Poker File Mapping and Validation Evidence

## Path and Configuration Verification
Output of `python3 tools/course_checks/r06-t048.py`:
```text
PASS: Real poker metadata valid. Resolved files:
  solution: ['poker.awk']
  test: ['test-poker.bats']
  example: ['.meta/example.awk']
PASS: Deliberate fixture 'missing-reference' failed as expected: Declared file '.meta/nonexistent-example.awk' for role 'example' does not exist at /Users/ishanjanwa/Documents/awk/exercises/practice/poker/.meta/nonexistent-example.awk
PASS: Deliberate fixture 'missing-test' failed as expected: Declared file 'test-missing-poker.bats' for role 'test' does not exist at /Users/ishanjanwa/Documents/awk/exercises/practice/poker/test-missing-poker.bats
PASS: Deliberate fixture 'outside-exercise' failed as expected: Path '../outside-solution.awk' escapes exercise root via parent traversal
```

## BATS Test Execution Summary
- Validator Exit Code: 0
- Total Executed Cases: 37
- Passed Cases: 37
- Named cases verified:
  - `single hand always wins`
  - `highest card out of all hands wins`
  - `a tie has multiple winners`

## Tool Versions
- GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)
- Bats 1.14.0
- GNU bash, version 5.3.20(1)-release (aarch64-apple-darwin27.0.0)
- jq-1.7.1-apple
- Python 3.14.7
