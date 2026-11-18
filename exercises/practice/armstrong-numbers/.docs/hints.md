# Hints

## AWK Specific Guidance

### Splitting Strings into Digits with `split()`

In AWK, to check whether a number is an Armstrong number, you need to count how many digits it has and raise each digit to that power.

You can break a number into its individual digits using the built-in `split()` function by passing an empty string `""` as the third parameter (field separator):

```awk
len = split(num, digits, "")
```

This populates the `digits` array with each single character indexed from 1 to `len`, and returns the total digit count.

#### Executable Micro Example
```awk
BEGIN {
    len = split("153", digits, "")
    print len, digits[1], digits[2], digits[3]
}
```
Expected output:
```text
3 1 5 3
```

### Common Pitfall: Omitting the Empty Separator
If you call `split(num, digits)` without the third argument, AWK defaults to splitting on whitespace (`FS`). Because a number has no spaces, the entire number is assigned to `digits[1]` and `len` becomes 1.

```awk
BEGIN {
    len = split("153", digits)
    print len, digits[1]
}
```
Expected output:
```text
1 153
```
This mistake causes multi digit numbers like 10 to incorrectly compute `10 ^ 1 = 10`, giving false positives. Always pass `""` as the separator when you need character by character splitting.

For more details, see the [GNU Awk String-Manipulation Functions Documentation](https://www.gnu.org/software/gawk/manual/html_node/String-Functions.html).
