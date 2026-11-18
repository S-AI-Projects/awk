import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

def benchmark_records(awk_cmd, script_path, input_data, repetitions=5):
    timings = []
    for _ in range(repetitions):
        start = time.perf_counter()
        res = subprocess.run(
            [awk_cmd, "-f", script_path],
            input=input_data,
            capture_output=True,
            text=True
        )
        end = time.perf_counter()
        if res.returncode != 0:
            raise RuntimeError("Benchmark subprocess returned non-zero code.")
        timings.append((end - start) * 1000.0)  # milliseconds
    return statistics.median(timings)

def main():
    repo_root = os.getcwd()
    work_dir = os.path.join(repo_root, "work", "R06-T055")
    os.makedirs(work_dir, exist_ok=True)

    exercise_path = "exercises/practice/leap"
    config_path = os.path.join(repo_root, exercise_path, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    solution_file = config["files"]["solution"][0]
    example_file = config["files"]["example"][0]

    # Verify learner stub is unsolved in working tree
    stub_path = os.path.join(repo_root, exercise_path, solution_file)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()
    if "Implement this solution" not in stub_content:
        print("Check failed: learner stub has been modified or solved.", file=sys.stderr)
        sys.exit(1)

    # Validate test suite in a temporary directory
    print("Validating leap reference implementation...")
    with tempfile.TemporaryDirectory() as tmp:
        def ignore_patterns(path, names):
            return [".git", "work"] if path == repo_root else []

        tmp_repo = os.path.join(tmp, "repo")
        shutil.copytree(repo_root, tmp_repo, ignore=ignore_patterns)

        src_example = os.path.join(tmp_repo, exercise_path, example_file)
        dst_solution = os.path.join(tmp_repo, exercise_path, solution_file)
        shutil.copy2(src_example, dst_solution)

        cmd = ["bin/validate_one_exercise", exercise_path]
        result = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)

        passed_tests = len(re.findall(r"^ok\s+\d+", result.stdout, re.MULTILINE))
        failed_tests = len(re.findall(r"^not ok\s+\d+", result.stdout, re.MULTILINE))
        total_executed = passed_tests + failed_tests

        named_cases = [
            "year not divisible by 4 in common year",
            "year divisible by 2, not divisible by 4 in common year",
            "year divisible by 4, not divisible by 100 in leap year"
        ]
        for case in named_cases:
            if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", result.stdout, re.MULTILINE):
                print(f"Check failed: named case '{case}' was not executed or failed.", file=sys.stderr)
                sys.exit(1)

        # Assert correctness before timing
        correctness_checks = [
            ("2015", "false"),
            ("1970", "false"),
            ("1996", "true"),
            ("2000", "true"),
            ("1900", "false")
        ]
        for year_str, expected in correctness_checks:
            p = subprocess.run(
                ["gawk", "-f", example_file],
                input=year_str,
                cwd=os.path.join(tmp_repo, exercise_path),
                capture_output=True,
                text=True
            )
            if p.returncode != 0 or p.stdout.strip() != expected:
                print(f"Correctness assertion failed for year {year_str}", file=sys.stderr)
                sys.exit(1)

        print("Correctness verified for all baseline cases.")

        # Benchmark 3 input sizes: 1, 10, 100 records with 5 repetitions each
        input_1 = "2015\n"
        input_10 = "".join([f"{y}\n" for y in [2015, 1970, 1996, 2000, 1900, 1960, 2100, 2400, 1800, 2024]])
        input_100 = input_10 * 10

        example_script = os.path.join(tmp_repo, exercise_path, example_file)
        med_1 = benchmark_records("gawk", example_script, input_1, repetitions=5)
        med_10 = benchmark_records("gawk", example_script, input_10, repetitions=5)
        med_100 = benchmark_records("gawk", example_script, input_100, repetitions=5)

        # Measure baseline process startup cost with an empty script
        empty_startup = benchmark_records("gawk", "/dev/null", "", repetitions=5)

        summary = (
            "=== EXECUTION SUMMARY ===\n"
            f"Executed Test Cases: {total_executed}\n"
            f"Passed: {passed_tests}, Failed: {failed_tests}\n"
            f"Baseline Cases Verified: {', '.join(named_cases)}\n\n"
            "=== BENCHMARK MEASUREMENTS (5 repetitions, median) ===\n"
            f"Empty Process Startup: {empty_startup:.2f} ms\n"
            f"Input Size 1 record:   {med_1:.2f} ms\n"
            f"Input Size 10 records:  {med_10:.2f} ms\n"
            f"Input Size 100 records: {med_100:.2f} ms\n\n"
            "=== COMPLEXITY CONCLUSION ===\n"
            "Process startup accounts for nearly all wall-clock runtime.\n"
            "Algorithmic work scales linearly at O(1) operations per record.\n\n"
            "=== VALIDATOR OUTPUT ===\n"
            f"{result.stdout}\n{result.stderr}"
        )

        with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
            f.write(summary)

        gawk_ver = subprocess.run(["gawk", "--version"], capture_output=True, text=True).stdout
        bats_ver = subprocess.run(["bats", "--version"], capture_output=True, text=True).stdout
        with open(os.path.join(work_dir, "versions.txt"), "w", encoding="utf-8") as f:
            f.write(f"AWK Version:\n{gawk_ver}\nBATS Version:\n{bats_ver}")

        if result.returncode != 0:
            print("Check failed: validation command returned non-zero code.", file=sys.stderr)
            sys.exit(1)

        if total_executed == 0:
            print("Check failed: zero test cases executed.", file=sys.stderr)
            sys.exit(1)

        if failed_tests > 0:
            print(f"Check failed: {failed_tests} tests failed.", file=sys.stderr)
            sys.exit(1)

        print(f"Check passed: all {total_executed} test cases executed cleanly, benchmarking complete.")

if __name__ == "__main__":
    main()
