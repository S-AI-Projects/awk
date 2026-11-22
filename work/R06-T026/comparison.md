# Comparative Analysis: Reference Technique vs. Alternative — grains (R06-T026)

## Overview

| Property | Value |
|----------|-------|
| Exercise | `grains` |
| Stub file | `grains.awk` (unsolved learner stub) |
| Test file | `test-grains.bats` (11 enabled test cases) |
| Reference solution | `.meta/example.awk` |

---

## 1. The Reference Technique: Closed-Form Exponentiation

In `exercises/practice/grains/.meta/example.awk`:

```awk
$1 == "total" {
    # This needs the `-M` option for arbitrary precision arithmetic.
    print ((2 ^ 64) - 1)
    next
}
$1 < 1 || $1 > 64 {
    print "square must be between 1 and 64" > "/dev/stderr"
    exit 1
}
{
    print 2 ^ ($1 - 1)
}
```

### Main Operation
The reference relies on **mathematical closed-form exponentiation**:
- For an individual square $n \in [1, 64]$: computes $2^{n - 1}$ via the binary power operator `^`.
- For the total on the board: computes $(2^{64}) - 1$, relying on the geometric series identity $\sum_{i=0}^{63} 2^i = 2^{64} - 1$.
- Arbitrary precision: Requires gawk's `-M` (bignum/MPFR) flag for `total` to represent $2^{64} - 1 = 18,446,744,073,709,551,615$ without 64-bit IEEE floating-point precision loss.

---

## 2. The Alternative Technique: Precomputed Array Simulation (Lookup Table)

```awk
BEGIN {
    board[1] = 1
    sum = 1
    for (i = 2; i <= 64; i++) {
        board[i] = board[i - 1] * 2
        sum += board[i]
    }
    board["total"] = sum
}

$1 == "total" {
    print board["total"]
    next
}

$1 < 1 || $1 > 64 {
    print "square must be between 1 and 64" > "/dev/stderr"
    exit 1
}

{
    print board[$1]
}
```

### Main Operation
The alternative uses an **array-based data representation** (precomputed state simulation):
- Rather than computing powers of two dynamically upon each input record, it simulates the chessboard in `BEGIN` by doubling the preceding square's grain count (`board[i] = board[i - 1] * 2`) and keeping a running accumulator `sum`.
- Queries are executed as $O(1)$ associative array lookups (`board[$1]`).

---

## 3. Comparison on Named Cases: Squares 1, 2, and 3

Both implementations strictly agree across all inputs. Tracing the first three squares:

| Square | Target | Reference Operation | Alternative Operation | Output |
|---|---|---|---|---|
| **Square 1** | $n = 1$ | `2 ^ (1 - 1) = 2 ^ 0` $\rightarrow 1$ | `board[1] = 1` $\rightarrow 1$ | `"1"` |
| **Square 2** | $n = 2$ | `2 ^ (2 - 1) = 2 ^ 1` $\rightarrow 2$ | `board[2] = board[1] * 2` $\rightarrow 2$ | `"2"` |
| **Square 3** | $n = 3$ | `2 ^ (3 - 1) = 2 ^ 2` $\rightarrow 4$ | `board[3] = board[2] * 2` $\rightarrow 4$ | `"4"` |

---

## 4. Trade-off Analysis: Memory vs. Work

| Dimension | Reference (Analytic Exponentiation) | Alternative (Precomputed Lookup Table) |
|---|---|---|
| **Space Complexity** | **$O(1)$** — uses no array storage. | **$O(K)$** where $K = 64$ — stores 64 integer entries + 1 `"total"` entry in associative array `board`. |
| **Startup Work** | **$O(1)$** — zero work before records arrive. | **$O(64)$** — executes 63 integer multiplications and 63 additions in `BEGIN`. |
| **Query Work** | $O(1)$ power computation per record. | $O(1)$ hash table array lookup per record. |
| **Bignum / Range** | Requires `-M` for `total` ($2^{64} - 1$). | Uses `-M` during loop accumulation for `total`. |
| **Cognitive Simplicity** | Requires mathematical deduction ($2^{n-1}$ and $\sum 2^i = 2^n - 1$). | Directly mirrors the physical problem description ("doubling each time"). |

### When is the Alternative Clearer?
The alternative is clearer when presenting the problem to learners who may not immediately recall or deduce the geometric series sum formula $\sum_{i=0}^{n-1} 2^i = 2^n - 1$.
Because the problem description specifies:
> *"Square 1 has one grain, square 2 has two grains, square 3 has four grains, and so on, doubling each time."*

The alternative's recursive step `board[i] = board[i - 1] * 2` is a direct, literal translation of the English specification into code.

---

## 5. Pedagogical Hint for Learners

> **Worked Example & Trade-off Hint:**
>
> Consider how grains grow across the first few squares:
> - Square 1: $1$ grain
> - Square 2: $1 \times 2 = 2$ grains
> - Square 3: $2 \times 2 = 4$ grains
> - Square 4: $4 \times 2 = 8$ grains
>
> **Pattern Recognition:** Notice that on square $n$, the count is always $2$ multiplied by itself $n - 1$ times (or $2^{n-1}$).
>
> **Design Trade-off:**
> - You can calculate each square's grains on demand using gawk's exponentiation operator `^`. This takes $O(1)$ memory.
> - Alternatively, because a chessboard has a small, fixed domain of 64 squares, you can simulate the doubling process in a loop and store the results in an array. This trades $O(64)$ array space for simple lookup logic.
> - **Note on Total:** A 64-bit integer can hold values up to $2^{64} - 1 \approx 1.84 \times 10^{19}$. In standard AWK without arbitrary precision, integers beyond $2^{53}$ may lose precision due to 64-bit floating point representation. Use `gawk -M` to enable arbitrary-precision arithmetic when evaluating `total`.

---

## 6. Verification Commands

```bash
export PATH="/opt/homebrew/bin:$PATH"
bash bin/validate_one_exercise exercises/practice/grains
# → 1..11, all ok

python3 work/R06-T026/check.py
# → [PASS] All assertions passed.
```
