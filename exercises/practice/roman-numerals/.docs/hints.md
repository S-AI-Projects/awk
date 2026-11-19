# Hints

## General

- The input to your program is a single decimal integer provided via standard input (`$1`).
- The output should be the Roman numeral representation printed to standard output.
- Converting an Arabic numeral to Roman numerals is commonly implemented using a greedy approach: iterate through standard Roman numeral values from largest to smallest, subtracting each value as many times as possible while appending its Roman symbol to the result.

## Language-Specific Guidance: Associative Array Traversal with `PROCINFO["sorted_in"]`

In AWK, associative arrays store key-value pairs (for example, mapping Roman symbol strings to their decimal values). However, by default, traversing an array with `for (key in array)` visits elements in an **arbitrary, implementation-dependent hash order**.

For a greedy conversion algorithm, keys **must** be traversed in descending order of their numeric values (from 1000 down to 1). GNU AWK (`gawk`) provides the special array `PROCINFO["sorted_in"]` to control traversal order.

### Construct: Numeric Descending Traversal (`@val_num_desc`)

Setting `PROCINFO["sorted_in"] = "@val_num_desc"` forces AWK's `for (key in array)` loop to order elements by their numeric value in descending order:

```awk
BEGIN {
    vals["X"] = 10; vals["V"] = 5; vals["I"] = 1
    PROCINFO["sorted_in"] = "@val_num_desc"
    for (k in vals) printf "%s:%d ", k, vals[k]
    print ""
}
```

**Expected Output:**
```text
X:10 V:5 I:1 
```

### Pitfall: String Comparison Order (`@val_str_desc`)

A common mistake is using string-based sorting such as `@val_str_desc` or omitting `PROCINFO["sorted_in"]` altogether:

```awk
BEGIN {
    vals["X"] = 10; vals["V"] = 5; vals["I"] = 1
    PROCINFO["sorted_in"] = "@val_str_desc"
    for (k in vals) printf "%s:%d ", k, vals[k]
    print ""
}
```

**Expected Output:**
```text
V:5 X:10 I:1 
```

**Why it fails:** Under string-based sorting (`@val_str_desc`), the value `5` is sorted before `10` because the leading character `'5'` is lexicographically greater than `'1'`. If used in a Roman numeral generator, a value like `10` would incorrectly match two `V`s (`"VV"`) instead of `"X"`. Similarly, omitting `PROCINFO["sorted_in"]` visits elements in internal hash order, which may check small values like `"I"` first.

For further reference, see the [GNU Awk User's Guide: Controlling Array Traversal](https://www.gnu.org/software/gawk/manual/html_node/Controlling-Scanning.html).
