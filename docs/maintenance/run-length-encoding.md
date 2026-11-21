# run-length-encoding encoder complexity

The encoder reads the already-split input fields from left to right. Each character updates the current run once, so its work is Θ(n) for an input of n characters. The run counters are constant-sized auxiliary state; GNU awk also retains the input record and one field per character, so total memory is Θ(n), plus output.

The exercise permits arbitrary-length strings over `A`–`Z` and whitespace, so these valid input sizes are within the stated domain. `work/R06-T005/check.py` asserts the compressed result before measuring five runs at each size and records the median end-to-end subprocess time:

| Input characters | Correct encoded output | Median wall time |
| ---: | --- | --- |
| 256 | `256A` | See `work/R06-T005/results.txt` |
| 512 | `512A` | See `work/R06-T005/results.txt` |
| 1024 | `1024A` | See `work/R06-T005/results.txt` |

These timings include starting GNU awk, parsing the program, and reading/writing input. They are useful as a reproducible observation, not an isolated measure of loop cost or a performance claim. The asymptotic statement follows from the single pass; the observed times and tool versions are captured by the checker.
