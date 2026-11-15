# Hints

## Language-Specific Guidance (AWK)

### Numeric Coercion in `luhn_digit`

In AWK, individual digits extracted from an input string using `substr($0, i, 1)` are strings. When performing calculations for the Luhn algorithm, AWK relies on **numeric coercion**—automatically converting a string to a numeric value when used in an arithmetic context (such as multiplication or addition).

In the reference implementation, `luhn_digit` leverages this when doubling the digit:
```awk
doubled = digit * 2
```
Multiplying `digit` by `2` forces AWK to convert the string `digit` into a number.

#### Micro-Example: Calculation with Coercion
```awk
BEGIN {
    digit = "7"
    doubled = digit * 2
    print doubled - (doubled > 9 ? 9 : 0)
}
```
**Expected Output:**
```text
5
```
Here, `"7"` is coerced to `7`, doubled to `14`, and because `14 > 9` is numerically true, `9` is subtracted to yield `5`.

### Exercise Pitfall: String vs Numeric Comparisons

A common pitfall occurs when comparing string values without numeric coercion. In AWK, comparing two strings performs a **lexicographical (alphabetical) comparison**, not a numeric one.

#### Pitfall Example: Lexicographical Comparison
```awk
BEGIN {
    a = "10"
    b = "9"
    print (a > b ? "true" : "false")
}
```
**Expected Output:**
```text
false
```
Because the character `'1'` has a smaller ASCII code than `'9'`, `"10"` is considered less than `"9"`. If you test whether a two-digit string is greater than `"9"` without coercing it first, the condition will unexpectedly evaluate to `false`.

#### Resolution: Explicit or Arithmetic Coercion
Coerce strings to numbers by performing an arithmetic operation such as adding `0` (`+ 0`) or multiplying by `1`:
```awk
BEGIN {
    a = "10" + 0
    b = "9" + 0
    print (a > b ? "true" : "false")
}
```
**Expected Output:**
```text
true
```

For more details on how AWK handles variable types and conversions, see the [GNU Awk User's Guide on Variable Typing and Comparison](https://www.gnu.org/software/gawk/manual/html_node/Variable-Typing.html).
