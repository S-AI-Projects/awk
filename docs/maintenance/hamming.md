# Hamming Exercise Maintenance & Dual-Approach Study

## 1. Overview & Context

- **Exercise**: `hamming`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Task Reference**: `R06-T016`
- **Learner Solution Stub**: `exercises/practice/hamming/hamming.awk`
- **Reference Solution**: `exercises/practice/hamming/.meta/example.awk`
- **Test Suite**: `exercises/practice/hamming/test-hamming.bats`
- **Test Configuration**: `exercises/practice/hamming/.meta/tests.toml`
- **Exercise Configuration**: `exercises/practice/hamming/.meta/config.json`

---

## 2. Architectural Comparison of Approaches

We evaluate two distinct approaches for calculating Hamming distance in AWK:

### Approach A: Positional Field Splitting (Reference Solution)
```awk
BEGIN {
    FS = ""     # each char is a separate field
}
NR == 1 {
    len = NF
    for (i=1; i<=NF; i++)
        first[i] = $i
    next
}
len != NF {
    print "strands must be of equal length" >"/dev/stderr"
    exit 1
}
{
    diff = 0
    for (i=1; i<=NF; i++)
        if ($i != first[i])
            diff++
    print diff
}
```

### Approach B: Direct Substring Extraction (Alternative Solution)
```awk
NR == 1 {
    first = $0
    len = length($0)
    next
}
length($0) != len {
    print "strands must be of equal length" >"/dev/stderr"
    exit 1
}
{
    diff = 0
    for (i = 1; i <= len; i++)
        if (substr(first, i, 1) != substr($0, i, 1))
            diff++
    print diff
}
```

---

## 3. Comparative Evaluation & Trade-offs

| Dimension | Approach A: Field Splitting (`FS = ""`) | Approach B: Substring Scanning (`substr`) |
|---|---|---|
| **Memory Allocation** | $\mathcal{O}(N)$ fields + $\mathcal{O}(N)$ associative array elements in AWK hash table. | $\mathcal{O}(1)$ auxiliary variables; only scalar strings stored. |
| **Portability** | GNU AWK extension (`FS = ""` character splitting). | Fully portable across POSIX awk, mawk, nawk, and gawk. |
| **Execution Overhead** | Split overhead upon record parse; rapid direct array lookup. | Minimal parse overhead; $2N$ function calls to `substr()`. |
| **Code Simplicity** | Intuitive field access (`$i != first[i]`). | Clean, avoids `BEGIN` block and global `FS` redefinition. |

---

## 4. Behavioral Baseline Verification

Both approaches were executed against the canonical test suite:

1. **"empty strands"**
   - **Input**: `""` vs `""`
   - **Expected**: Exit code 0, Output `0`
   - **Approach A**: `len = 0`, `NF = 0`, loop 0 times $\rightarrow$ Output `0` (PASS)
   - **Approach B**: `len = 0`, `length($0) = 0`, loop 0 times $\rightarrow$ Output `0` (PASS)

2. **"single letter identical strands"**
   - **Input**: `"A"` vs `"A"`
   - **Expected**: Exit code 0, Output `0`
   - **Approach A**: `first[1] = "A"`, `$1 = "A"`, 0 mismatches $\rightarrow$ Output `0` (PASS)
   - **Approach B**: `substr("A", 1, 1) == substr("A", 1, 1)` $\rightarrow$ Output `0` (PASS)

3. **"single letter different strands"**
   - **Input**: `"G"` vs `"T"`
   - **Expected**: Exit code 0, Output `1`
   - **Approach A**: `first[1] = "G"`, `$1 = "T"`, 1 mismatch $\rightarrow$ Output `1` (PASS)
   - **Approach B**: `substr("G", 1, 1) != substr("T", 1, 1)` $\rightarrow$ Output `1` (PASS)

Both implementations pass 100% of all 9 test cases in `test-hamming.bats`.

---

## 5. Verification Harness

Automated verification is conducted by `work/R06-T016/check.py`:
- Validates the untouched learner stub `hamming.awk`.
- Runs `bin/validate_one_exercise exercises/practice/hamming` on Approach A (reference).
- Runs full test suite on Approach B (alternative) in an isolated temporary directory.
- Verifies exact output matching on all 9 test cases, including the 3 named cases.
- Saves artifacts in `work/R06-T016/`: `output.txt`, `expected_vs_actual.json`, `versions.txt`, and `alternative.awk`.
