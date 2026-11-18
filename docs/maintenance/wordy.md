# Wordy Maintenance

## Purpose
This document records the mutation analysis performed on the `looks_like_a_number` function in the Wordy reference implementation.

## Reference Function
In `.meta/example.awk`, the original helper function is:

```awk
function looks_like_a_number(num) {
    return num ~ /^[+-]?[[:digit:]]+$/
}
```

This regular expression correctly permits an optional leading positive or negative sign followed by digits.

## Deliberate Mutation
To test regression rejection, a deliberate mutant was created that removes the optional sign:

```awk
function looks_like_a_number(num) {
    return num ~ /^[[:digit:]]+$/
}
```

## Rejecting Test Case
The mutant was tested against the full Bats test suite. It was immediately caught and rejected by the following test case:

* Canonical UUID: `607c08ee-2241-4288-916d-dae5455c87e6`
* Test Name: `just a negative number`
* Input: `What is -123?`
* Expected Behavior: Returns success with output `-123`.
* Mutant Behavior: Rejects `-123` because the leading minus sign is not matched, calling `syntax_error()` and exiting with status 1.

## Conclusion
The existing test suite properly rejects this mutation without requiring new test cases. The hint added in `.docs/hints.md` clarifies this requirement for learners without giving away the full solution.
