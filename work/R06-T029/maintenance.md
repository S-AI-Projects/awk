# Focused Runner Architecture & Isolation — robot-simulator (R06-T029)

## Overview

| Property | Value |
|----------|-------|
| Exercise | `robot-simulator` |
| Exercise Directory | `exercises/practice/robot-simulator` |
| Config File | `exercises/practice/robot-simulator/.meta/config.json` |
| Learner Stub | `exercises/practice/robot-simulator/robot-simulator.awk` |
| Reference Solution | `exercises/practice/robot-simulator/.meta/example.awk` |
| Test Suite | `exercises/practice/robot-simulator/test-robot-simulator.bats` (21 cases) |

---

## 1. Focused Runner Purpose & Design

The purpose of the focused runner (`work/R06-T029/check.py`) is to test the reference implementation in an isolated temporary copy without modifying the learner's starter files, reporting the exact test case count, and properly propagating all failure modes.

### Key Operational Guarantees:
1. **Isolated Temporary Environment:**
   All execution occurs in a dedicated temporary directory (`tempfile.TemporaryDirectory`).
2. **Zero Working Tree Mutation:**
   The reference (`.meta/example.awk`) is substituted as `robot-simulator.awk` **only inside the temporary copy**. The working tree starter file `exercises/practice/robot-simulator/robot-simulator.awk` is never modified.
3. **Learner File Immutability:**
   SHA-256 hashes of the learner stub are computed before and after every execution (including failing and zero-test runs) to guarantee byte-for-byte integrity.
4. **Accurate Execution Counting & Failure Propagation:**
   - Reports the real executed test count (`21` for `robot-simulator`).
   - Propagates non-zero child exit codes upon test assertion failures.
   - Detects and fails on zero-test runs.
5. **Automatic Sandbox Cleanup:**
   Temporary sandbox directories are completely cleaned up upon completion.

---

## 2. Runner Scenarios Evaluated

The runner tests three distinct operational conditions:

| Scenario | Condition | Expected Behavior | Observed Result | Status |
|---|---|---|---|---|
| **Scenario 1: Real Reference** | Standard reference (`example.awk`) | Passes all 21 test cases with exit code 0. | `exit_code: 0`, `tests: 21` | **PASS** |
| **Scenario 2: Failing Reference** | Mutated reference (`BEGIN { exit 1 }`) | Fails test assertions, propagates non-zero exit. | `exit_code: 1` | **PASS** |
| **Scenario 3: Zero-Test Selection** | Empty BATS suite (0 tests) | Detects 0 tests, fails with non-zero exit. | `test_count: 0`, `exit_code: 1` | **PASS** |

In all three scenarios, temporary directories were cleanly removed and the learner file SHA-256 hash was preserved unaltered.

---

## 3. Named Cases Verification

The runner explicitly verifies the three required named cases on the reference implementation:

1. **`Robots are created with a position and direction`**
   - Args: `-v x=0 -v y=0 -v dir=north /dev/null`
   - Expected Output: `0 0 north` (PASS)
2. **`Robots are created with a default position and direction`**
   - Args: `/dev/null`
   - Expected Output: `0 0 north` (PASS)
3. **`Negative positions are allowed`**
   - Args: `-v x=-1 -v y=-1 -v dir=south /dev/null`
   - Expected Output: `-1 -1 south` (PASS)

---

## 4. Verification Commands

```bash
export PATH="/opt/homebrew/bin:$PATH"
bash bin/validate_one_exercise exercises/practice/robot-simulator
# → 1..21, all ok

python3 work/R06-T029/check.py
# → [PASS] All assertions passed.
```
