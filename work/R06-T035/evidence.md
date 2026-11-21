# Verification Evidence: R06-T035 (Affine Cipher Complexity)

## Summary of Results
- **Validation Run**: All 16 tests passed via `bin/validate_one_exercise exercises/practice/affine-cipher`.
- **Baseline Cases**: Explicitly confirmed for `encode yes`, `encode no`, `encode OMG`.
- **Learner Stub**: `exercises/practice/affine-cipher/affine-cipher.awk` remains untouched and unsolved.
- **Process Startup vs. Algorithmic Scaling**:
  - Process startup cost is constant across all sizes: ~**5.1173 ms**.
  - In-memory algorithmic cost scales linearly with character length:
    - Small ($N=3$): **0.001482 ms/call**
    - Medium ($N=14$): **0.004298 ms/call**
    - Large ($N=43$): **0.013271 ms/call**

## Timing Table
| Size ID | Input Size ($N$) | Process Median (ms) | Algorithmic Median (ms/call) | Algorithmic Ratio ($T/T_{\text{small}}$) |
|:---|:---:|:---:|:---:|:---:|
| Small | 3 | 5.1173 | 0.001482 | 1.00x |
| Medium | 14 | 5.0537 | 0.004298 | 2.90x |
| Large | 43 (35 alnum) | 5.4628 | 0.013271 | 8.95x |

## Operations Table
| Metric | Small ($N=3$) | Medium ($N=14$) | Large ($N=43$) |
|:---|:---:|:---:|:---:|
| Raw String Length | 3 | 14 | 43 |
| Alphanumeric Characters ($n$) | 3 | 14 | 35 |
| Alphabet Setup Operations | 52 | 52 | 52 |
| Character Encryption Loops | 3 | 14 | 35 |
| Total Estimated Algorithmic Ops | 72 | 131 | 252 |
