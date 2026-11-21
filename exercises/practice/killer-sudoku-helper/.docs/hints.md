# Hints

## General

- Killer Sudoku requires listing all valid combinations of digits ($1$ to $9$) that add up to a cage's target sum, without repeating any digit within the cage, and excluding specified digits.
- Combinations must be output sorted in ascending order.

## Construct Analysis: Record & Field Manipulation (`NF` and `$NF`)

When generating combinations recursively, AWK programmers often consider three language mechanisms:

1. **Associative-Array Traversal (`for (key in array)`)**:
   - In AWK, traversing an associative array yields keys in an undefined, pseudo-random order determined by internal hash buckets.
   - Because the exercise requires combinations to be emitted in strictly ascending sorted order, associative-array traversal is unsuitable for driving recursive output generation.

2. **Numeric Coercion**:
   - AWK performs automatic numeric coercion during arithmetic comparisons (`<=`) and subtractions (`remainingSum - digit`).
   - While coercion ensures strings from `$1` and `$2` can participate in arithmetic, it does not solve combination tracking or output formatting.

3. **Dynamic Record & Field Splitting (`NF`, `$NF`, and `$0`)**:
   - This is the construct actually utilized by `generate_recursive`.
   - In AWK, the Number of Fields (`NF`) can be manipulated directly at runtime. Incrementing `NF` (`NF++`) dynamically allocates a new field `$NF`.
   - Calling `print` without arguments automatically joins all active fields `$1` through `$NF` using the Output Field Separator (`OFS`, which defaults to a single space `" "`).
   - Backtracking is accomplished simply by decrementing `NF` (`NF--`).

---

## Standalone Micro-Example

The following minimal snippet demonstrates using `NF` as a dynamic recursion stack to emit space-separated combinations:

```awk
function push(val) { NF++; $NF = val }
function pop()     { NF-- }
BEGIN {
    NF = 0
    push(1)
    push(2)
    print
    pop()
    push(3)
    print
}
```

**Output**:
```text
1 2
1 3
```

---

## Exercise-Relevant Pitfall: Omitting Backtracking / Field Accumulation

### The Pitfall
Because `$0` is bidirectionally synchronized with fields `$1..$NF`, any modification to `NF` persists until explicitly adjusted. If `NF--` is omitted during recursive backtracking, fields from previously explored branches leak into subsequent branches.

```awk
function push(val) { NF++; $NF = val }
BEGIN {
    NF = 0
    push(1)
    push(2)
    print
    # Pitfall: Missing pop() / NF-- before exploring next branch
    push(3)
    print
}
```

**Contrasting Output**:
```text
1 2
1 2 3
```

### Why the Outcomes Differ
- In the first snippet, `pop()` (`NF--`) removes field 2 from the record before pushing `3`, correctly producing the alternative 2-digit combination `1 3`.
- In the second snippet, without `NF--`, pushing `3` increments `NF` to 3, inadvertently creating an invalid 3-digit combination `1 2 3`.

### Related Pitfall: Resetting `NF = 0` Before Caching Input Fields
Setting `NF = 0` immediately clears all input fields `$1`, `$2`, ..., `$NF`. Always cache `$1` (cage sum) and `$2` (cage size) into local variables before resetting `NF = 0` for recursive field accumulation.
