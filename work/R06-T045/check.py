#!/usr/bin/env python3

import hashlib
import json
import re
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE_REL = Path("exercises/practice/space-age")
EXERCISE = ROOT / EXERCISE_REL
VALIDATOR_REL = Path("bin/validate_one_exercise")
EVIDENCE_FILE = Path(__file__).resolve().parent / "evidence.md"


def run(command, cwd=None):
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_results(output):
    return re.findall(r"^(ok|not ok) \d+ (.+)$", output, re.MULTILINE)


def get_version(command):
    res = run(command)
    out = res.stdout.strip() or res.stderr.strip()
    return out.splitlines()[0] if out else "unknown"


def main():
    config_path = EXERCISE / ".meta/config.json"
    if not config_path.is_file():
        raise SystemExit(f"FAIL: Missing config {config_path}")

    config = json.loads(config_path.read_text())
    files = config.get("files", {})
    solution_rel = files["solution"][0]
    test_rel = files["test"][0]
    example_rel = files["example"][0]

    stub = EXERCISE / solution_rel
    test_file = EXERCISE / test_rel
    example_file = EXERCISE / example_rel

    initial_stub_hash = hashlib.sha256(stub.read_bytes()).hexdigest()

    # Verify baseline with validate_one_exercise in temporary environment
    with tempfile.TemporaryDirectory(prefix="r06-t045-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_exercise = temp_root / EXERCISE_REL
        temp_validator = temp_root / VALIDATOR_REL

        shutil.copytree(EXERCISE, temp_exercise)
        temp_validator.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / VALIDATOR_REL, temp_validator)

        validator_cmd = ["bash", str(VALIDATOR_REL), str(EXERCISE_REL)]
        result = run(validator_cmd, cwd=temp_root)
        results = test_results(result.stdout)

        if result.returncode != 0:
            raise SystemExit(f"FAIL: validator exited with code {result.returncode}")

        if not results:
            raise SystemExit("FAIL: 0 tests executed")

        named_cases = ["age on Earth", "age on Mercury", "age on Venus"]
        passed_test_names = [name for status, name in results if status == "ok"]

        for case in named_cases:
            if case not in passed_test_names:
                raise SystemExit(f"FAIL: named case '{case}' did not pass")

        if any(status != "ok" for status, _ in results):
            raise SystemExit(f"FAIL: some tests failed in suite: {results}")

    # Verify learner stub remains untouched and unsolved
    if hashlib.sha256(stub.read_bytes()).hexdigest() != initial_stub_hash:
        raise SystemExit("FAIL: original learner solution was modified")

    stub_check = subprocess.run(
        ["gawk", "-f", str(stub)],
        input="Earth 1000000000\n",
        text=True,
        capture_output=True,
    )
    if stub_check.returncode == 0:
        raise SystemExit("FAIL: learner stub should be unsolved but exited 0")

    # Assert correctness on inputs before timing
    baseline_cases = [
        ("Earth 1000000000", "31.69"),
        ("Mercury 2134835688", "280.88"),
        ("Venus 189839836", "9.78"),
    ]
    for inp, expected in baseline_cases:
        res = subprocess.run(
            ["gawk", "-f", str(example_file)],
            input=f"{inp}\n",
            text=True,
            capture_output=True,
        )
        if res.returncode != 0:
            raise SystemExit(f"FAIL: execution failed for {inp}")
        act = res.stdout.strip()
        if act != expected:
            raise SystemExit(f"FAIL: correctness check failed for {inp}: expected {expected}, got {act}")

    # Benchmark three valid input sizes: 1 record, 100 records, 1000 records
    # 5 repetitions per size, recording median time
    sizes = [1, 100, 1000]
    benchmark_data = {}

    for size in sizes:
        # Generate valid records cycling through planets
        planets = ["Earth", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        records = [f"{planets[i % len(planets)]} 1000000000" for i in range(size)]
        input_payload = "\n".join(records) + "\n"

        timings = []
        for _ in range(5):
            t0 = time.perf_counter()
            bench_res = subprocess.run(
                ["gawk", "-f", str(example_file)],
                input=input_payload,
                text=True,
                capture_output=True,
            )
            t1 = time.perf_counter()
            if bench_res.returncode != 0:
                raise SystemExit(f"FAIL: benchmark run failed for size {size}")
            timings.append(t1 - t0)

        median_time = statistics.median(timings)
        benchmark_data[size] = {
            "timings": timings,
            "median": median_time,
            "per_record_median": median_time / size,
        }

    # Generate evidence
    evidence = f"""# R06-T045 — Space Age Scaling Study Evidence

## Reference Complexity and Correctness
All {len(results)} canonical tests passed against the reference implementation.
Correctness was verified prior to performance measurement.

### Baseline Correctness Checks
| Input Record | Expected Output | Status |
|---|---|---|
"""
    for inp, exp in baseline_cases:
        evidence += f"| `{inp}` | `{exp}` | PASS |\n"

    evidence += f"""
## Empirical Benchmark Results (5 Repetitions per Size)
| Input Size (Records) | Repetition Timings (s) | Median Total Time (s) | Median Time / Record (µs) |
|---|---|---|---|
"""
    for size, data in benchmark_data.items():
        formatted_timings = ", ".join(f"{t * 1000:.2f}ms" for t in data["timings"])
        evidence += (
            f"| {size} | {formatted_timings} | {data['median'] * 1000:.2f}ms | "
            f"{data['per_record_median'] * 1e6:.2f}µs |\n"
        )

    evidence += f"""
## Algorithmic Complexity Findings
- **Algorithmic Cost**: Fixed O(1) table lookup + 2 divisions per record -> O(N) overall.
- **Process Startup Overhead**: ~{benchmark_data[1]['median'] * 1000:.2f}ms for process initialization, parsing, and execution of a single record.
- **Memory Footprint**: Strict O(1) auxiliary space (8 array elements) regardless of record count.

## Tool Versions
- {get_version(["gawk", "--version"])}
- {get_version(["bats", "--version"])}
- {get_version(["bash", "--version"])}
- {get_version(["jq", "--version"])}
- {get_version(["python3", "--version"])}
"""

    EVIDENCE_FILE.write_text(evidence)

    print(f"PASS: All {len(results)} tests passed.")
    print("PASS: Correctness verified for Earth, Mercury, and Venus.")
    print("PASS: Benchmark completed across sizes 1, 100, 1000.")
    print("PASS: Learner stub remains unchanged and unsolved.")
    print(f"Evidence saved to: {EVIDENCE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
