# Maintenance Guide: Pythagorean Triplet (`pythagorean-triplet`)

## 1. Problem Formulation & Specification

A Pythagorean triplet is a set of three natural numbers $\{a, b, c\}$ such that:

$$a^2 + b^2 = c^2 \quad \text{where} \quad a < b < c$$

Given an integer sum $N$, the program must output all triplets such that:

$$a + b + c = N$$

### Algorithmic Formulation
Rather than an $O(N^2)$ brute-force search over $a$ and $b$, the reference implementation algebraically derives $b$ from $a$ and $N$:
1. Since $c = N - a - b$, substituting into $a^2 + b^2 = c^2$:
   $$a^2 + b^2 = (N - a - b)^2 = (N - a)^2 - 2b(N - a) + b^2$$
   $$a^2 = (N - a)^2 - 2b(N - a)$$
   $$2b(N - a) = (N - a)^2 - a^2 = N^2 - 2Na$$
   $$b = \frac{N^2 - 2Na}{2(N - a)}$$
2. For any candidate $a$, if the numerator $N^2 - 2Na$ is evenly divisible by $2(N - a)$, then $b$ is an integer.
3. If $a < b$, then $c = N - a - b$ completes the valid triplet.
4. Triplet generation is bounded by $a \le \lfloor N / 3 \rfloor$, running in $\mathcal{O}(N)$ time.

---

## 2. Focused Runner Architecture & Learner Protection

The test harness enforces a strict separation between the learner's working tree files and the evaluation harness.

### 2.1 File Resolution from `.meta/config.json`
The runner ingests `exercises/practice/pythagorean-triplet/.meta/config.json`:
- `files.solution[0]` $\to$ `pythagorean-triplet.awk` (learner stub)
- `files.test[0]` $\to$ `test-pythagorean-triplet.bats` (BATS test suite)
- `files.example[0]` $\to$ `.meta/example.awk` (reference implementation)

### 2.2 Isolated Temporary Copy Workflow
1. The runner creates an isolated temporary directory via Python `tempfile.TemporaryDirectory`.
2. The entire exercise directory (including dotfiles) and harness scripts (`bin/`, `lib/`) are copied into the temporary sandbox.
3. The reference solution (`.meta/example.awk`) is copied onto the stub path (`pythagorean-triplet.awk`) **only inside the temporary copy**.
4. The working tree copy of `pythagorean-triplet.awk` is never modified or rewritten.
5. All temporary directories are guaranteed to be cleaned up immediately upon process termination.

### 2.3 Cryptographic Integrity Protection (SHA-256 Hashing)
To verify that the working tree is never contaminated:
- SHA-256 digests of all learner files are computed before every validation run.
- SHA-256 digests are re-verified after every run (including normal, failing, zero-test, and interrupted scenarios).
- Any discrepancy raises a fatal assertion error.

---

## 3. Runner Scenario Testing & Failure Propagation

The runner (`work/R06-T039/check.py`) executes and validates three operational scenarios:

| Scenario | Injected Condition | Expected Behavior | Working Tree Hash Intact |
|:---|:---|:---|:---:|
| **1. Real Reference** | Authoritative `.meta/example.awk` | Return code 0, all 7 tests pass. | Yes |
| **2. Failing Reference** | Deliberately corrupted triplet calculation | Non-zero exit code, test failure reported. | Yes |
| **3. Zero-Test Run** | Test suite producing 0 executed cases | Non-zero exit code, zero-count rejected. | Yes |

### 3.1 Canonical Baseline Cases
The test suite validates 7 canonical cases, anchored on:
- `triplets whose sum is 12` ($N=12 \to 3,4,5$)
- `triplets whose sum is 108` ($N=108 \to 27,36,45$)
- `triplets whose sum is 1000` ($N=1000 \to 200,375,425$)

All 7 cases pass against the reference implementation.

---

## 4. Verification Checklist

- [x] All 7 test cases pass against reference `example.awk`.
- [x] Baseline named cases pass: `triplets whose sum is 12`, `triplets whose sum is 108`, `triplets whose sum is 1000`.
- [x] Learner stub `pythagorean-triplet.awk` remains unsolved.
- [x] SHA-256 hashes of learner files are identical before and after all test runs.
- [x] Runner fails cleanly on assertion failure (corrupted reference) and zero-test runs.
- [x] All temporary directories and files are cleaned up upon execution completion.
- [x] Check script `work/R06-T039/check.py` produces all required reproduction artifacts.
