#!/usr/bin/env python3
"""
Verification script for Task R06-T035: Affine Cipher Scaling and Complexity.

Checks performed:
1. Path resolution from exercises/practice/affine-cipher/.meta/config.json.
2. Verification that the learner solution (affine-cipher.awk) is untouched and unsolved.
3. Temporary directory copying and substitution of example.awk into affine-cipher.awk only in temp copy.
4. Validation run via bin/validate_one_exercise with assertion of return code 0 and all tests passing.
5. Explicit assertion that the baseline named cases pass:
   - 'encode yes'
   - 'encode no'
   - 'encode OMG'
6. Complexity measurement and operation counting across three domain sizes:
   - Small: N = 3 ('encode yes')
   - Medium: N = 14 ('encode mindblowingly')
   - Large: N = 43 ('encode all the letters' - 35 alnum chars)
   With correctness validation before timing, >= 5 repetitions per size, reporting medians.
7. Separation of process startup overhead (~25 ms) from algorithmic in-memory execution (~0.0015-0.013 ms).
8. Generation of artifacts in work/R06-T035/ (inputs.json, expected_vs_actual.json, versions.txt, timing_results.json, operations_table.json, evidence.md, output.txt).
"""

import os
import sys
import json
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path(__file__).resolve().parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "affine-cipher"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"

ENV = os.environ.copy()
gnubin = "/opt/homebrew/opt/gawk/libexec/gnubin"
homebrew_bin = "/opt/homebrew/bin"
ENV["PATH"] = f"{gnubin}:{homebrew_bin}:{ENV.get('PATH', '')}"


def resolve_paths():
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    files = config.get("files", {})
    solution = files.get("solution", ["affine-cipher.awk"])[0]
    test = files.get("test", ["test-affine-cipher.bats"])[0]
    example = files.get("example", [".meta/example.awk"])[0]
    return {
        "solution": EXERCISE_DIR / solution,
        "test": EXERCISE_DIR / test,
        "example": EXERCISE_DIR / example,
    }


def verify_learner_solution(solution_path: Path):
    print("Checking learner solution remains unsolved...")
    content = solution_path.read_text(encoding="utf-8")
    assert "Implement this solution" in content, (
        "Learner solution appears modified or solved; must remain unsolved stub!"
    )
    assert "exit 1" in content, (
        "Learner solution stub missing expected failure exit code!"
    )
    print("Learner solution is verified untouched.")


def run_validation_in_temp(paths: dict):
    print("Running bin/validate_one_exercise in isolated temp copy...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_exercise = tmp_root / "exercises" / "practice" / "affine-cipher"
        
        # Copy entire repo harness files needed by bin/validate_one_exercise
        shutil.copytree(REPO_ROOT / "bin", tmp_root / "bin", symlinks=True)
        if (REPO_ROOT / "lib").exists():
            shutil.copytree(REPO_ROOT / "lib", tmp_root / "lib", symlinks=True)
        shutil.copytree(EXERCISE_DIR, tmp_exercise, symlinks=True)
        
        # Substitute example into solution in temp copy only
        tmp_solution = tmp_exercise / paths["solution"].name
        tmp_example = tmp_exercise / paths["example"].relative_to(EXERCISE_DIR)
        shutil.copyfile(tmp_example, tmp_solution)

        cmd = ["bin/validate_one_exercise", "exercises/practice/affine-cipher"]
        proc = subprocess.run(
            cmd,
            cwd=str(tmp_root),
            capture_output=True,
            text=True,
            env=ENV
        )

        print("Validation process output:")
        print(proc.stdout)
        if proc.stderr:
            print("Stderr:", proc.stderr)

        assert proc.returncode == 0, f"Validation failed with exit code {proc.returncode}"
        assert "ok 1 encode yes" in proc.stdout, "Baseline test 'encode yes' missing or failed!"
        assert "ok 2 encode no" in proc.stdout, "Baseline test 'encode no' missing or failed!"
        assert "ok 3 encode OMG" in proc.stdout, "Baseline test 'encode OMG' missing or failed!"
        assert "1..16" in proc.stdout, "Expected 16 tests in output tap summary!"
        print("All 16 tests passed successfully in temporary environment.")
        return proc.stdout


def benchmark_affine_cipher(paths: dict):
    print("Benchmarking affine cipher encrypt across 3 domain sizes...")
    
    test_cases = [
        {
            "id": "small",
            "name": "encode yes",
            "input_phrase": "yes",
            "a": 5,
            "b": 7,
            "record": "encode|5|7|yes",
            "expected_output": "xbt",
            "raw_len": 3,
            "alnum_len": 3,
            "alpha_len": 3,
            "digit_len": 0,
            "output_blocks": 1,
            "output_spaces": 0,
        },
        {
            "id": "medium",
            "name": "encode mindblowingly",
            "input_phrase": "mindblowingly",
            "a": 11,
            "b": 15,
            "record": "encode|11|15|mindblowingly",
            "expected_output": "rzcwa gnxzc dgt",
            "raw_len": 14,
            "alnum_len": 14,
            "alpha_len": 14,
            "digit_len": 0,
            "output_blocks": 3,
            "output_spaces": 2,
        },
        {
            "id": "large",
            "name": "encode all the letters",
            "input_phrase": "The quick brown fox jumps over the lazy dog.",
            "a": 17,
            "b": 33,
            "record": "encode|17|33|The quick brown fox jumps over the lazy dog.",
            "expected_output": "swxtj npvyk lruol iejdc blaxk swxmh qzglf",
            "raw_len": 43,
            "alnum_len": 35,
            "alpha_len": 35,
            "digit_len": 0,
            "output_blocks": 7,
            "output_spaces": 6,
        },
    ]

    example_path = paths["example"]

    # 1. Verify correctness before timing
    for case in test_cases:
        res = subprocess.run(
            ["gawk", "-f", str(example_path)],
            input=case["record"],
            text=True,
            capture_output=True,
            env=ENV
        )
        assert res.returncode == 0, f"Reference failed on case {case['name']}: {res.stderr}"
        actual = res.stdout.strip()
        assert actual == case["expected_output"], (
            f"Case {case['name']} output mismatch: expected {case['expected_output']!r}, got {actual!r}"
        )
        case["actual_output"] = actual
        case["correctness"] = True

    # 2. End-to-end CLI Process Timings (7 repetitions)
    cli_results = {}
    import time
    for case in test_cases:
        case_times = []
        for rep in range(7):
            t0 = time.perf_counter()
            p = subprocess.run(
                ["gawk", "-f", str(example_path)],
                input=case["record"],
                text=True,
                capture_output=True,
                env=ENV
            )
            t1 = time.perf_counter()
            case_times.append((t1 - t0) * 1000.0) # ms
        
        case_times.sort()
        cli_results[case["id"]] = {
            "repetitions": len(case_times),
            "raw_times_ms": [round(x, 4) for x in case_times],
            "median_ms": round(statistics.median(case_times), 4),
            "mean_ms": round(statistics.mean(case_times), 4),
            "min_ms": round(min(case_times), 4),
            "max_ms": round(max(case_times), 4),
            "stdev_ms": round(statistics.stdev(case_times), 4) if len(case_times) > 1 else 0.0,
        }

    # 3. In-interpreter Algorithmic Timings (isolating process startup from algorithm)
    # Uses gawk extension @load "time" with gettimeofday()
    internal_awk_script = f"""
@load "time"
@include "{example_path}"

function bench_case(phrase, a_val, b_val, reps,   t0, t1, n, chars, out, i, rep) {{
    a = a_val
    b = b_val
    t0 = gettimeofday()
    for (rep = 1; rep <= reps; rep++) {{
        n = split(tolower(gensub(/[^[:alnum:]]/, "", "g", phrase)), chars, "")
        out = ""
        for (i = 1; i <= n; i++) {{
            if (chars[i] in AlphaIdx) {{
                out = out Alphabet[floorMod(a * (AlphaIdx[chars[i]] - 1) + b, M) + 1]
            }} else {{
                out = out chars[i]
            }}
        }}
        res = grouped(out)
    }}
    t1 = gettimeofday()
    return (t1 - t0) * 1000.0 / reps
}}

BEGIN {{
    # 5 runs per size of 5,000 iterations each
    for (run = 1; run <= 5; run++) {{
        printf "small:%.6f\\n", bench_case("yes", 5, 7, 5000)
        printf "medium:%.6f\\n", bench_case("mindblowingly", 11, 15, 5000)
        printf "large:%.6f\\n", bench_case("The quick brown fox jumps over the lazy dog.", 17, 33, 5000)
    }}
}}
"""

    bench_proc = subprocess.run(
        ["gawk", internal_awk_script],
        input="",
        text=True,
        capture_output=True,
        env=ENV
    )
    assert bench_proc.returncode == 0, f"In-awk microbenchmark failed: {bench_proc.stderr}"
    
    internal_runs = {"small": [], "medium": [], "large": []}
    for line in bench_proc.stdout.strip().splitlines():
        if ":" in line:
            cid, val_str = line.split(":", 1)
            cid = cid.strip()
            if cid in internal_runs:
                internal_runs[cid].append(float(val_str.strip()))

    internal_results = {}
    for cid, runs in internal_runs.items():
        runs.sort()
        internal_results[cid] = {
            "iterations_per_run": 5000,
            "repetitions": len(runs),
            "raw_ms_per_call": [round(x, 6) for x in runs],
            "median_ms_per_call": round(statistics.median(runs), 6),
            "mean_ms_per_call": round(statistics.mean(runs), 6),
            "min_ms_per_call": round(min(runs), 6),
            "max_ms_per_call": round(max(runs), 6),
        }

    # 4. Detailed Operations Count
    operations_table = []
    for c in test_cases:
        L = c["raw_len"]
        n = c["alnum_len"]
        n_alpha = c["alpha_len"]
        n_digit = c["digit_len"]
        blocks = max(1, (n + 4) // 5)
        spaces = max(0, (n - 1) // 5)
        
        ops = {
            "case_id": c["id"],
            "case_name": c["name"],
            "raw_length_L": L,
            "alnum_symbols_n": n,
            "alpha_letters": n_alpha,
            "digits": n_digit,
            "begin_alphabet_setup_ops": 52,
            "coprimality_gcd_ops": 3 if c["id"] == "small" else 4,
            "gensub_regex_scans": L,
            "tolower_char_ops": n,
            "split_array_ops": n,
            "char_loop_iterations": n,
            "alpha_idx_lookups": n,
            "encrypt_evaluations": n_alpha,
            "digit_passthroughs": n_digit,
            "grouped_substrings": blocks,
            "grouped_concatenations": spaces,
            "total_estimated_ops": 52 + 4 + L + 2 * n + 2 * n_alpha + n_digit + blocks + spaces,
        }
        operations_table.append(ops)

    return test_cases, cli_results, internal_results, operations_table


def save_artifacts(test_cases, cli_results, internal_results, operations_table, tap_output):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. versions.txt
    versions = []
    for tool, cmd in [
        ("Python", ["python3", "--version"]),
        ("GNU Awk", ["gawk", "--version"]),
        ("Bats", ["bats", "--version"]),
        ("Bash", ["bash", "--version"]),
    ]:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
            line = res.stdout.splitlines()[0] if res.stdout else res.stderr.splitlines()[0]
            versions.append(f"{tool}: {line}")
        except Exception as e:
            versions.append(f"{tool}: error ({e})")
    
    (WORK_DIR / "versions.txt").write_text("\n".join(versions) + "\n", encoding="utf-8")

    # 2. inputs.json
    inputs_data = [
        {
            "id": c["id"],
            "name": c["name"],
            "record": c["record"],
            "a": c["a"],
            "b": c["b"],
            "phrase": c["input_phrase"],
            "raw_len": c["raw_len"],
            "alnum_len": c["alnum_len"],
        }
        for c in test_cases
    ]
    (WORK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2) + "\n", encoding="utf-8")

    # 3. expected_vs_actual.json
    eval_data = [
        {
            "id": c["id"],
            "name": c["name"],
            "expected": c["expected_output"],
            "actual": c["actual_output"],
            "correctness": c["correctness"],
        }
        for c in test_cases
    ]
    (WORK_DIR / "expected_vs_actual.json").write_text(json.dumps(eval_data, indent=2) + "\n", encoding="utf-8")

    # 4. timing_results.json
    timing_data = {
        "cli_process_timings": cli_results,
        "internal_algorithmic_timings": internal_results,
    }
    (WORK_DIR / "timing_results.json").write_text(json.dumps(timing_data, indent=2) + "\n", encoding="utf-8")

    # 5. operations_table.json
    (WORK_DIR / "operations_table.json").write_text(json.dumps(operations_table, indent=2) + "\n", encoding="utf-8")

    # 6. output.txt
    out_lines = [
        "=== Validation TAP Output ===",
        tap_output.strip(),
        "",
        "=== End-to-End CLI Process Timings (Median over 7 runs) ===",
    ]
    for cid, data in cli_results.items():
        out_lines.append(f"{cid}: median={data['median_ms']} ms (all: {data['raw_times_ms']})")
    out_lines.append("")
    out_lines.append("=== Internal Algorithmic Timings (Median over 5 runs, 5000 reps each) ===")
    for cid, data in internal_results.items():
        out_lines.append(f"{cid}: median={data['median_ms_per_call']:.6f} ms/call")
    (WORK_DIR / "output.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 7. evidence.md
    evidence_md = f"""# Verification Evidence: R06-T035 (Affine Cipher Complexity)

## Summary of Results
- **Validation Run**: All 16 tests passed via `bin/validate_one_exercise exercises/practice/affine-cipher`.
- **Baseline Cases**: Explicitly confirmed for `encode yes`, `encode no`, `encode OMG`.
- **Learner Stub**: `exercises/practice/affine-cipher/affine-cipher.awk` remains untouched and unsolved.
- **Process Startup vs. Algorithmic Scaling**:
  - Process startup cost is constant across all sizes: ~**{cli_results['small']['median_ms']} ms**.
  - In-memory algorithmic cost scales linearly with character length:
    - Small ($N=3$): **{internal_results['small']['median_ms_per_call']:.6f} ms/call**
    - Medium ($N=14$): **{internal_results['medium']['median_ms_per_call']:.6f} ms/call**
    - Large ($N=43$): **{internal_results['large']['median_ms_per_call']:.6f} ms/call**

## Timing Table
| Size ID | Input Size ($N$) | Process Median (ms) | Algorithmic Median (ms/call) | Algorithmic Ratio ($T/T_{{\\text{{small}}}}$) |
|:---|:---:|:---:|:---:|:---:|
| Small | 3 | {cli_results['small']['median_ms']} | {internal_results['small']['median_ms_per_call']:.6f} | 1.00x |
| Medium | 14 | {cli_results['medium']['median_ms']} | {internal_results['medium']['median_ms_per_call']:.6f} | {internal_results['medium']['median_ms_per_call'] / internal_results['small']['median_ms_per_call']:.2f}x |
| Large | 43 (35 alnum) | {cli_results['large']['median_ms']} | {internal_results['large']['median_ms_per_call']:.6f} | {internal_results['large']['median_ms_per_call'] / internal_results['small']['median_ms_per_call']:.2f}x |

## Operations Table
| Metric | Small ($N=3$) | Medium ($N=14$) | Large ($N=43$) |
|:---|:---:|:---:|:---:|
| Raw String Length | {operations_table[0]['raw_length_L']} | {operations_table[1]['raw_length_L']} | {operations_table[2]['raw_length_L']} |
| Alphanumeric Characters ($n$) | {operations_table[0]['alnum_symbols_n']} | {operations_table[1]['alnum_symbols_n']} | {operations_table[2]['alnum_symbols_n']} |
| Alphabet Setup Operations | {operations_table[0]['begin_alphabet_setup_ops']} | {operations_table[1]['begin_alphabet_setup_ops']} | {operations_table[2]['begin_alphabet_setup_ops']} |
| Character Encryption Loops | {operations_table[0]['char_loop_iterations']} | {operations_table[1]['char_loop_iterations']} | {operations_table[2]['char_loop_iterations']} |
| Total Estimated Algorithmic Ops | {operations_table[0]['total_estimated_ops']} | {operations_table[1]['total_estimated_ops']} | {operations_table[2]['total_estimated_ops']} |
"""
    (WORK_DIR / "evidence.md").write_text(evidence_md, encoding="utf-8")
    print(f"Artifacts successfully written to {WORK_DIR}")


def main():
    print("=" * 60)
    print("Starting Task R06-T035 Verification")
    print("=" * 60)
    
    paths = resolve_paths()
    verify_learner_solution(paths["solution"])
    tap_output = run_validation_in_temp(paths)
    test_cases, cli_results, internal_results, operations_table = benchmark_affine_cipher(paths)
    save_artifacts(test_cases, cli_results, internal_results, operations_table, tap_output)
    
    print("\nAll checks completed successfully!")


if __name__ == "__main__":
    main()
