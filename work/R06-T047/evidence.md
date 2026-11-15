# R06-T047 — Luhn AWK-Specific Guidance Evidence

## Summary
Documented AWK numeric coercion as utilized in `luhn_digit`, contrasted against lexicographical string comparison pitfalls.

## Micro-Example Assertions
1. **Coercion in `luhn_digit` calculation**:
   - Code: `BEGIN { digit = "7"; doubled = digit * 2; print doubled - (doubled > 9 ? 9 : 0) }`
   - Expected Output: `5`
   - Actual Output: `5`
   - Status: PASS

2. **Uncoerced String Comparison Pitfall**:
   - Code: `BEGIN { a = "10"; b = "9"; print (a > b ? "true" : "false") }`
   - Expected Output: `false`
   - Actual Output: `false`
   - Status: PASS

3. **Coerced Numeric Comparison**:
   - Code: `BEGIN { a = "10" + 0; b = "9" + 0; print (a > b ? "true" : "false") }`
   - Expected Output: `true`
   - Actual Output: `true`
   - Status: PASS

## Test Suite Execution
- Total Cases Executed: 22
- Passed Cases: 22
- Named cases verified:
  - `single digit strings can not be valid`
  - `a single zero is invalid`
  - `a simple valid SIN that remains valid if reversed`

## Tool Versions
- GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)
- Bats 1.14.0
- GNU bash, version 5.3.20(1)-release (aarch64-apple-darwin27.0.0)
- jq-1.7.1-apple
- Python 3.14.7
