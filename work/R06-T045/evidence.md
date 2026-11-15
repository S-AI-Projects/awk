# R06-T045 — Space Age Scaling Study Evidence

## Reference Complexity and Correctness
All 9 canonical tests passed against the reference implementation.
Correctness was verified prior to performance measurement.

### Baseline Correctness Checks
| Input Record | Expected Output | Status |
|---|---|---|
| `Earth 1000000000` | `31.69` | PASS |
| `Mercury 2134835688` | `280.88` | PASS |
| `Venus 189839836` | `9.78` | PASS |

## Empirical Benchmark Results (5 Repetitions per Size)
| Input Size (Records) | Repetition Timings (s) | Median Total Time (s) | Median Time / Record (µs) |
|---|---|---|---|
| 1 | 10.18ms, 9.87ms, 9.52ms, 9.85ms, 10.20ms | 9.87ms | 9868.75µs |
| 100 | 10.12ms, 9.35ms, 9.77ms, 9.68ms, 10.29ms | 9.77ms | 97.74µs |
| 1000 | 10.75ms, 10.52ms, 11.12ms, 10.70ms, 10.71ms | 10.71ms | 10.71µs |

## Algorithmic Complexity Findings
- **Algorithmic Cost**: Fixed O(1) table lookup + 2 divisions per record -> O(N) overall.
- **Process Startup Overhead**: ~9.87ms for process initialization, parsing, and execution of a single record.
- **Memory Footprint**: Strict O(1) auxiliary space (8 array elements) regardless of record count.

## Tool Versions
- GNU Awk 5.4.1, API 4.1, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)
- Bats 1.14.0
- GNU bash, version 5.3.20(1)-release (aarch64-apple-darwin27.0.0)
- jq-1.7.1-apple
- Python 3.14.7
