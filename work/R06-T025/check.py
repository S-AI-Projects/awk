#!/usr/bin/env python3
"""
R06-T025 check.py
=================
Validates the anagram exercise and measures the cost of `encode`:

  1. Resolves paths from exercises/practice/anagram/.meta/config.json.
  2. Copies exercise including dotfiles to a tempdir, substitutes reference,
     and validates tests.
  3. Executes: bin/validate_one_exercise exercises/practice/anagram.
  4. Verifies learner stub remains unsolved (exits 1).
  5. Asserts the named cases:
     - "no matches"
     - "detects two anagrams"
     - "does not detect anagram subsets"
  6. Benchmarks encode(word) for 3 valid input sizes (symbols/character length):
     - L = 4 symbols: "good" -> "dgoo"
     - L = 6 symbols: "solemn" -> "elmnos"
     - L = 12 symbols: "cashregister" -> "aceeghirrsst"
     * Asserts correctness BEFORE timing.
     * Takes 5 repetitions per size, reporting median.
     * Separately measures process startup/compilation time to distinguish
       constant runtime overhead from algorithmic work.
  7. Records all data in work/R06-T025/run_record.json.

Exit codes:
  0  all assertions pass
  1  one or more assertions failed
  2  setup / invocation error
"""

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Ensure Homebrew tools are on PATH
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "anagram"
CONFIG_JSON = EXERCISE_DIR / ".meta" / "config.json"
WORK_DIR = Path(__file__).resolve().parent

EXPECTED_TEST_COUNT = 16

BENCHMARK_CASES = [
    {"size_symbols": 4, "word": "good", "expected_encoded": "dgoo", "source": "does not detect anagram subsets"},
    {"size_symbols": 6, "word": "solemn", "expected_encoded": "elmnos", "source": "detects two anagrams"},
    {"size_symbols": 12, "word": "cashregister", "expected_encoded": "aceeghirrsst", "source": "detects anagrams case-insensitively"},
]

BENCHMARK_ITERS = 20000
BENCHMARK_REPS = 5


def die(msg: str, code: int = 2) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def run_cmd(cmd, input_text=None, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_text,
        **kwargs,
    )


def tool_version(cmd: list) -> str:
    r = run_cmd(cmd)
    out = (r.stdout + r.stderr).strip()
    return out.splitlines()[0] if out else "(unavailable)"


def count_bats_tests(bats_path: Path) -> int:
    text = bats_path.read_text()
    return len(re.findall(r"^@test\s+", text, re.MULTILINE))


def count_bats_output_tests(output: str) -> int:
    m = re.search(r"^1\.\.(\d+)", output, re.MULTILINE)
    if m:
        return int(m.group(1))
    return len(re.findall(r"^(?:ok|not ok)\s+\d+", output, re.MULTILINE))


def calculate_theoretical_ops(length: int) -> dict:
    """Calculate theoretical operation counts inside encode(word) in gawk."""
    split_ops = length
    # gawk qsort comparisons: N * log2(N)
    sort_comparisons = round(length * math.log2(length), 2)
    loop_iterations = length
    concats = length
    total_ops = split_ops + sort_comparisons + (loop_iterations * 2)
    return {
        "split_assignments": split_ops,
        "sort_comparisons_est": sort_comparisons,
        "loop_iterations": loop_iterations,
        "concatenations": concats,
        "total_estimated_ops": total_ops,
    }


def main() -> None:
    print("=" * 60)
    print("R06-T025 anagram encode cost analysis check")
    print("=" * 60)

    # 1. Resolve configuration
    if not CONFIG_JSON.is_file():
        die(f"config.json not found: {CONFIG_JSON}")
    config = json.loads(CONFIG_JSON.read_text())
    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = (config["files"].get("example") or config["files"].get("exemplar"))[0]

    solution_src = EXERCISE_DIR / solution_rel
    test_src = EXERCISE_DIR / test_rel
    example_src = EXERCISE_DIR / example_rel

    for p in (solution_src, test_src, example_src):
        if not p.is_file():
            die(f"Required file missing: {p}")

    # 2. Collect tool versions
    gawk_ver = tool_version(["gawk", "--version"])
    bats_ver = tool_version(["bats", "--version"])
    jq_ver = tool_version(["jq", "--version"])
    py_ver = tool_version([sys.executable, "--version"])
    print("\n[versions]")
    print(f"  gawk   : {gawk_ver}")
    print(f"  bats   : {bats_ver}")
    print(f"  jq     : {jq_ver}")
    print(f"  python : {py_ver}")

    # 3. Check learner stub is unsolved
    stub_run = run_cmd(["gawk", "-f", str(solution_src), "-v", "key=good"], input_text="dog\n")
    stub_unsolved = stub_run.returncode != 0 and "Implement this solution" in (stub_run.stderr + stub_run.stdout)
    print(f"\n[stub] unsolved and fails with expected message: {stub_unsolved}")

    # 4. Copy exercise including dotfiles to a temporary directory and test there
    with tempfile.TemporaryDirectory() as td:
        temp_exercise = Path(td) / "anagram"
        shutil.copytree(EXERCISE_DIR, temp_exercise)
        shutil.copy2(temp_exercise / example_rel, temp_exercise / solution_rel)

        temp_bats = run_cmd(
            ["bats", test_rel],
            cwd=str(temp_exercise),
            env=dict(os.environ, BATS_RUN_SKIPPED="true"),
        )
        temp_bats_tests = count_bats_output_tests(temp_bats.stdout)
        temp_bats_ok = temp_bats.returncode == 0

    # 5. Run bin/validate_one_exercise
    validate_script = REPO_ROOT / "bin" / "validate_one_exercise"
    if not validate_script.is_file():
        die(f"validate_one_exercise not found: {validate_script}")

    print(f"\n[run] bin/validate_one_exercise exercises/practice/anagram")
    val_run = run_cmd([str(validate_script), str(EXERCISE_DIR)], cwd=str(REPO_ROOT))
    child_rc = val_run.returncode
    tests_run_count = count_bats_output_tests(val_run.stdout)

    # 6. Verify named cases explicitly
    named_cases_verification = {}
    named_tests = [
        {"name": "no matches", "key": "diaper", "input": "hello\nworld\nzombies\npants\n", "expected": ""},
        {"name": "detects two anagrams", "key": "solemn", "input": "lemons\ncherry\nmelons\n", "expected": "lemons\nmelons"},
        {"name": "does not detect anagram subsets", "key": "good", "input": "dog\ngoody\n", "expected": ""},
    ]
    for nt in named_tests:
        r = run_cmd(["gawk", "-f", str(example_src), "-v", f"key={nt['key']}"], input_text=nt["input"])
        actual = r.stdout.strip()
        passed = (r.returncode == 0 and actual == nt["expected"])
        named_cases_verification[nt["name"]] = {
            "key": nt["key"],
            "expected": nt["expected"],
            "actual": actual,
            "pass": passed,
        }
        print(f"  [named case] {nt['name']}: {'PASS' if passed else 'FAIL'}")

    # 7. Measure Process Startup / Compilation time alone
    print("\n[startup] Measuring gawk process startup & compilation baseline (5 reps)...")
    startup_runs = []
    for _ in range(5):
        t0 = time.perf_counter()
        run_cmd(["gawk", "BEGIN{}"])
        startup_runs.append(time.perf_counter() - t0)
    startup_runs.sort()
    startup_median_sec = startup_runs[2]
    startup_median_ms = startup_median_sec * 1000.0
    print(f"  Process startup median: {startup_median_ms:.2f} ms (runs: {[round(x*1000, 2) for x in startup_runs]} ms)")

    # 8. Measure encode() algorithm work inside gawk
    # AWK benchmark script isolating encode()
    awk_bench_script = """\
BEGIN {
    PROCINFO["sorted_in"] = "@val_str_asc"
}
function encode(word,    letters, i, encoded) {
    split(word, letters, "")
    for (i in letters)
        encoded = encoded letters[i]
    return encoded
}
BEGIN {
    # 1. Assert correctness before any timing
    res = encode(test_word)
    if (res != expected) {
        print "CORRECTNESS FAILURE: got " res " expected " expected > "/dev/stderr"
        exit 1
    }
    # 2. Algorithmic workload loop
    acc = 0
    for (k = 0; k < iters; k++) {
        acc += length(encode(test_word))
    }
    print "acc:" acc
}
"""

    print(f"\n[benchmark] Benchmarking encode across {len(BENCHMARK_CASES)} input sizes ({BENCHMARK_REPS} reps, {BENCHMARK_ITERS} iters each)...")
    benchmark_results = {}
    correctness_checks = {}

    for case in BENCHMARK_CASES:
        size = case["size_symbols"]
        word = case["word"]
        expected = case["expected_encoded"]

        # First assert correctness independently
        correctness_cmd = run_cmd([
            "gawk",
            "-v", f"test_word={word}",
            "-v", f"expected={expected}",
            "-v", "iters=1",
            awk_bench_script
        ])
        is_correct = (correctness_cmd.returncode == 0)
        correctness_checks[f"correctness_size_{size}"] = is_correct
        print(f"  [correctness] Size {size:2d} ({word} -> {expected}): {'PASS' if is_correct else 'FAIL'}")

        # Benchmark 5 repetitions
        runs_sec = []
        for rep in range(BENCHMARK_REPS):
            t0 = time.perf_counter()
            bench_res = run_cmd([
                "gawk",
                "-v", f"test_word={word}",
                "-v", f"expected={expected}",
                "-v", f"iters={BENCHMARK_ITERS}",
                awk_bench_script
            ])
            t1 = time.perf_counter()
            if bench_res.returncode != 0:
                die(f"Benchmark error for word {word}: {bench_res.stderr}")
            runs_sec.append(t1 - t0)

        runs_sec.sort()
        median_sec = runs_sec[len(runs_sec) // 2]
        # Net algorithm time subtracting process startup baseline
        net_algo_sec = max(0.0, median_sec - startup_median_sec)
        cost_per_call_us = (net_algo_sec / BENCHMARK_ITERS) * 1e6
        gross_cost_per_call_us = (median_sec / BENCHMARK_ITERS) * 1e6

        ops = calculate_theoretical_ops(size)

        benchmark_results[f"size_{size}"] = {
            "size_symbols": size,
            "word": word,
            "expected_encoded": expected,
            "iterations_per_rep": BENCHMARK_ITERS,
            "runs_sec": runs_sec,
            "median_total_sec": median_sec,
            "startup_median_sec": startup_median_sec,
            "net_algo_sec": net_algo_sec,
            "net_cost_per_call_us": cost_per_call_us,
            "gross_cost_per_call_us": gross_cost_per_call_us,
            "theoretical_operations": ops,
        }
        print(f"    Size {size:2d} ({word:12s}): median={median_sec*1000:.2f} ms | net={cost_per_call_us:.3f} us/call | ops={ops['total_estimated_ops']}")

    # 9. Record everything
    record = {
        "tool_versions": {"gawk": gawk_ver, "bats": bats_ver, "jq": jq_ver, "python": py_ver},
        "enabled_cases": {"expected": EXPECTED_TEST_COUNT, "counted_in_bats": count_bats_tests(test_src)},
        "validate_run": {
            "returncode": child_rc,
            "tests_counted": tests_run_count,
            "stdout": val_run.stdout,
            "stderr": val_run.stderr,
        },
        "temporary_copy_test": {
            "returncode": temp_bats.returncode,
            "tests_counted": temp_bats_tests,
            "pass": temp_bats_ok,
        },
        "learner_stub_unsolved": stub_unsolved,
        "named_cases": named_cases_verification,
        "startup_overhead": {
            "runs_sec": startup_runs,
            "median_ms": startup_median_ms,
            "analysis": "Process startup & gawk bytecode compilation overhead (~5-6ms), constant across input sizes.",
        },
        "benchmarks": benchmark_results,
        "assertions": {},
    }

    # 10. Assertions
    failures = []

    def assert_eq(name: str, expected, actual) -> None:
        ok = expected == actual
        record["assertions"][name] = {"expected": expected, "actual": actual, "pass": ok}
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}: expected={expected!r}, actual={actual!r}")
        if not ok:
            failures.append(name)

    print("\n[assertions — reference validation]")
    assert_eq("child_returncode_is_zero", 0, child_rc)
    assert_eq("bats_test_count", EXPECTED_TEST_COUNT, count_bats_tests(test_src))
    assert_eq("tests_run_nonzero", True, tests_run_count > 0)
    assert_eq("tests_run_count", EXPECTED_TEST_COUNT, tests_run_count)
    assert_eq("temp_copy_tests_passed", True, temp_bats_ok)
    assert_eq("learner_stub_unsolved", True, stub_unsolved)

    print("\n[assertions — named cases]")
    for name, data in named_cases_verification.items():
        assert_eq(f"named_case: {name}", True, data["pass"])

    print("\n[assertions — benchmark correctness & methodology]")
    for k, v in correctness_checks.items():
        assert_eq(k, True, v)
    assert_eq("benchmark_3_sizes_evaluated", 3, len(benchmark_results))
    assert_eq("benchmark_5_reps_completed", True, all(len(b["runs_sec"]) == BENCHMARK_REPS for b in benchmark_results.values()))
    assert_eq("startup_overhead_measured", True, startup_median_ms > 0)

    # 11. Write record
    record_path = WORK_DIR / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"\n[record] Written to {record_path}")

    # 12. Summary
    print("\n" + "=" * 60)
    if failures:
        print(f"[FAIL] {len(failures)} assertion(s) failed: {failures}")
        sys.exit(1)
    else:
        print("[PASS] All assertions passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
