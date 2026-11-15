# Space Age — Complexity and Scaling Study

## Domain and Problem Formulation
The `space-age` exercise processes records of the format:
`<PlanetName> <AgeInSeconds>`
For each record, it calculates the equivalent planetary years using orbital period ratios relative to Earth (31,557,600 seconds/year).

## Algorithmic Complexity

### Operation and Branch Table (Per Record)
| Component | Operations Executed | Time Complexity | Auxiliary Space |
|---|---|---|---|
| `BEGIN` block | 1 scalar assign + 8 table inserts | $O(1)$ (once per process) | $O(1)$ (8 entries) |
| Associative lookup | `earth_ratio[$1]` hash probe | $O(1)$ expected | $O(1)$ |
| Numerical division | `($2 / 31557600) / ratio` (2 divisions) | $O(1)$ | $O(1)$ |
| Output formatting | `printf("%.2f\n", ...)` | $O(1)$ | $O(1)$ |
| Total (N records) | $N$ record iterations | $O(N)$ | $O(1)$ |

### Distinguishing Algorithmic Work vs Process Startup
Invoking the `gawk` process has a fixed initialization overhead (process spawning, binary linking, AWK compilation and AST construction) of ~5–12 ms in POSIX environments.
Algorithmic execution time scales as $O(N)$ when multiple records are streamed into a single AWK process.
Because each record is evaluated independently and immediately emitted without buffering, memory consumption remains strictly constant $O(1)$ across all stream sizes.

## Empirical Measurement Protocol
- Tested across three domain input sizes:
  - Small: $N = 1$ record
  - Medium: $N = 100$ records
  - Large: $N = 1000$ records
- Repetitions: 5 runs per input size under constant environment conditions.
- Correctness is validated before timing.
- Metrics recorded: Median execution time (seconds).

## Reproduction
Run the automated check:
```bash
python3 work/R06-T045/check.py
```
Detailed empirical timings and tool versions are recorded in `work/R06-T045/evidence.md`.
