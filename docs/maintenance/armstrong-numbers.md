# Armstrong Numbers Maintenance

## Purpose
This document records the language guidance and construct analysis added for the Armstrong Numbers exercise in AWK.

## Language Construct Analysis
In `exercises/practice/armstrong-numbers/.meta/example.awk`, the function `is_armstrong` decomposes the input number into individual digits using:

```awk
len = split(num, digits, "")
```

In AWK:
* When the third argument to `split()` is the empty string `""`, AWK splits the target string character by character into the destination array.
* The return value is the number of elements created, which represents the number of digits in the input.

## Pitfall Analysis
* If a learner omits the third argument `split(num, digits)`, AWK uses the default field separator (`FS`, which is whitespace).
* Since an integer string contains no whitespace, `split()` treats the input as a single token, setting `digits[1] = num` and returning `len = 1`.
* This bug would calculate `num ^ 1 == num` for every input, causing numbers like 10 or 100 to incorrectly evaluate as Armstrong numbers.

## Baseline Test Coverage
The reference implementation was validated against all 11 test cases in `test-armstrong-numbers.bats`. All test cases passed cleanly, including the baseline cases:
1. `Zero is an Armstrong number` (input: 0 -> output: `true`)
2. `Single-digit numbers are Armstrong numbers` (input: 5 -> output: `true`)
3. `There are no two-digit Armstrong numbers` (input: 10 -> output: `false`)

Both micro-examples were tested with `gawk` and verified for expected output.
