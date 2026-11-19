# Bob Exercise Maintenance & Contract Guidance

## 1. Overview & Context

- **Exercise**: `bob`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T020`
- **Learner Solution Stub**: `exercises/practice/bob/bob.awk`
- **Reference Solution**: `exercises/practice/bob/.meta/example.awk`
- **Test Suite**: `exercises/practice/bob/test-bob.bats`
- **Test Configuration**: `exercises/practice/bob/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/bob/.meta/config.json`
- **Hints Guide**: `exercises/practice/bob/.docs/hints.md`

---

## 2. Contract Decision Table

The behavioral contract maps input predicates to Bob's responses:

| Condition Name | Required Predicate Condition | Output |
|---|---|---|
| **Silence** | `trim(input) == ""` | `"Fine. Be that way!"` |
| **Forceful Question** | `is_yelling(input) && is_asking(input)` | `"Calm down, I know what I'm doing!"` |
| **Shouting** | `is_yelling(input) && !is_asking(input)` | `"Whoa, chill out!"` |
| **Question** | `!is_yelling(input) && is_asking(input)` | `"Sure."` |
| **Statement (Fallback)** | Default / Anything else | `"Whatever."` |

### Invariant Rules
1. **Alphabetical Shouting Rule**: An utterance only constitutes shouting if it contains at least one uppercase letter (`/[[:upper:]]/`) AND zero lowercase letters (`!/[[:lower:]]/`). Non-alphabetic characters (numbers, punctuation) are neutral.
2. **Trailing Question Mark Rule**: A statement is a question if and only if the last non-whitespace character is `'?'`.
3. **Ordering Precedence**: The compound state (`is_yelling && is_asking`) must be tested before evaluating either single state to prevent premature branch matching.

---

## 3. Behavioral Baseline Verification

The named canonical cases were verified against the reference solution:

1. **"asking a question"**
   - **Input**: `'Does this cryogenic chamber make me look fat?'`
   - **Expected**: `"Sure."` | **Actual**: `"Sure."` (PASS)

2. **"shouting"**
   - **Input**: `'WATCH OUT!'`
   - **Expected**: `"Whoa, chill out!"` | **Actual**: `"Whoa, chill out!"` (PASS)

3. **"forceful question"**
   - **Input**: `'WHAT'\''S GOING ON?'`
   - **Expected**: `"Calm down, I know what I'm doing!"` | **Actual**: `"Calm down, I know what I'm doing!"` (PASS)

All 26 test cases in `test-bob.bats` pass with 100% agreement against the reference solution.

---

## 4. Verification Harness

Automated verification is conducted by `work/R06-T020/check.py`:
- Asserts that the learner stub `bob.awk` remains untouched and unsolved.
- Validates the reference solution against `test-bob.bats` via `bin/validate_one_exercise` in an isolated tempdir (26 passing tests).
- Confirms exact matching for all decision table cases and the 3 named baseline cases.
- Saves artifacts in `work/R06-T020/`: `output.txt`, `expected_vs_actual.json`, and `versions.txt`.
