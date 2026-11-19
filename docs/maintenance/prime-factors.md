# Prime Factors Maintenance & Isolated Runner Specification

## 1. Overview & Purpose

This document specifies the isolated test runner for the `prime-factors` exercise in the AWK track (`S-AI-Projects/awk`).

The goal of the isolated runner is to validate the reference implementation (`.meta/example.awk`) and test suites without modifying or solving the learner starter files (`prime-factors.awk`), preserving their unsolved state across all validation runs.

---

## 2. Isolated Runner Architecture

The runner (`tools/course_checks/r06-t019.py`) operates strictly within temporary sandbox directories:
1. **Repository Staging**: Copies repository contents into a fresh sandbox directory via `tempfile.TemporaryDirectory`.
2. **Reference Substitution**: Copies the reference implementation `.meta/example.awk` onto the learner stub path (`prime-factors.awk`) strictly inside the temporary sandbox copy.
3. **Execution**: Invokes `bin/validate_one_exercise exercises/practice/prime-factors` within the sandbox.
4. **Output Parsing**: Parses the TAP output protocol to verify test counts and pass/fail statuses.
5. **Cryptographic Integrity**: Calculates the SHA-256 hash of the working tree learner stub before and after each run (including simulated failures), ensuring the working tree is never modified.

---

## 3. Test Execution Modes

The runner evaluates three execution modes to ensure robust failure propagation:
* **Standard Mode:** Executes the official reference implementation against the complete test suite. Expects all 12 test cases to pass with exit code 0.
* **Failing Reference Mode:** Injects a broken reference solution to verify that assertion failures properly trigger a non-zero exit code.
* **Empty Tests Mode:** Injects a test suite with zero test cases to verify that a zero-test run is rejected and causes a non-zero exit code.

---

## 4. Tool Requirements

* GNU Awk (`gawk`) 5.x
* Bats (`bats-core`) 1.x
* Bash 4.x or later
* Python 3.10+
* `jq` 1.6+

---

## 5. Validation Command

```bash
bin/validate_one_exercise exercises/practice/prime-factors
```

All 12 test cases pass cleanly:
1. `no factors`
2. `prime number`
3. `another prime number`
4. `square of a prime`
5. `product of first prime`
6. `cube of a prime`
7. `product of second prime`
8. `product of third prime`
9. `product of first and second prime`
10. `product of primes and non-primes`
11. `product of primes`
12. `factors include a large prime`
