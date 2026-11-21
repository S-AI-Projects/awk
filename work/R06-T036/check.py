#!/usr/bin/env python3
"""
Verification script for Task R06-T036: Acronym Alternative Implementation Comparison.

Checks performed:
1. Path resolution from exercises/practice/acronym/.meta/config.json.
2. Verification that the learner solution (acronym.awk) is untouched and unsolved.
3. Temporary directory copying and substitution of example.awk into acronym.awk only in temp copy.
4. Validation run via bin/validate_one_exercise with assertion of return code 0 and all tests passing.
5. Execution of both reference and alternative implementations across all 9 test cases.
6. Explicit verification of named baseline cases:
   - 'basic' ("Portable Network Graphics" -> "PNG")
   - 'lowercase words' ("Ruby on Rails" -> "ROR")
   - 'punctuation' ("First In, First Out" -> "FIFO")
7. Timing and trade-off comparison between reference (FS + gsub) and alternative (FPAT).
8. Generation of artifacts in work/R06-T036/ (inputs.json, expected_vs_actual.json, comparison.json, versions.txt, evidence.md, output.txt).
"""

import os
import sys
import json
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path(__file__).resolve().parent
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "acronym"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"

ENV = os.environ.copy()
gnubin = "/opt/homebrew/opt/gawk/libexec/gnubin"
homebrew_bin = "/opt/homebrew/bin"
ENV["PATH"] = f"{gnubin}:{homebrew_bin}:{ENV.get('PATH', '')}"

ALTERNATIVE_AWK = """BEGIN {
    # Define fields by word pattern rather than delimiters
    FPAT = "[[:alpha:]][[:alpha:]']*"
}
{
    acr = ""
    for (i = 1; i <= NF; i++) {
        acr = acr substr($i, 1, 1)
    }
    print toupper(acr)
}
"""

CANONICAL_TEST_CASES = [
    {
        "id": "basic",
        "name": "basic",
        "input": "Portable Network Graphics",
        "expected": "PNG",
    },
    {
        "id": "lowercase_words",
        "name": "lowercase words",
        "input": "Ruby on Rails",
        "expected": "ROR",
    },
    {
        "id": "punctuation",
        "name": "punctuation",
        "input": "First In, First Out",
        "expected": "FIFO",
    },
    {
        "id": "all_caps_word",
        "name": "all caps word",
        "input": "GNU Image Manipulation Program",
        "expected": "GIMP",
    },
    {
        "id": "punctuation_without_whitespace",
        "name": "punctuation without whitespace",
        "input": "Complementary metal-oxide semiconductor",
        "expected": "CMOS",
    },
    {
        "id": "very_long_abbreviation",
        "name": "very long abbreviation",
        "input": "Rolling On The Floor Laughing So Hard That My Dogs Came Over And Licked Me",
        "expected": "ROTFLSHTMDCOALM",
    },
    {
        "id": "consecutive_delimiters",
        "name": "consecutive delimiters",
        "input": "Something - I made up from thin air",
        "expected": "SIMUFTA",
    },
    {
        "id": "apostrophes",
        "name": "apostrophes",
        "input": "Halley's Comet",
        "expected": "HC",
    },
    {
        "id": "underscore_emphasis",
        "name": "underscore emphasis",
        "input": "The Road _Not_ Taken",
        "expected": "TRNT",
    },
]


def resolve_paths():
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    files = config.get("files", {})
    solution = files.get("solution", ["acronym.awk"])[0]
    test = files.get("test", ["test-acronym.bats"])[0]
    example = files.get("example", [".meta/example.awk"])[0]
    return {
        "solution": EXERCISE_DIR / solution,
        "test": EXERCISE_DIR / test,
        "example": EXERCISE_DIR / example,
    }


def verify_learner_solution(solution_path: Path):
    print("Checking learner solution remains unsolved stub...")
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
        tmp_exercise = tmp_root / "exercises" / "practice" / "acronym"
        
        # Copy harness files
        shutil.copytree(REPO_ROOT / "bin", tmp_root / "bin", symlinks=True)
        if (REPO_ROOT / "lib").exists():
            shutil.copytree(REPO_ROOT / "lib", tmp_root / "lib", symlinks=True)
        shutil.copytree(EXERCISE_DIR, tmp_exercise, symlinks=True)
        
        # Substitute example into solution in temp copy only
        tmp_solution = tmp_exercise / paths["solution"].name
        tmp_example = tmp_exercise / paths["example"].relative_to(EXERCISE_DIR)
        shutil.copyfile(tmp_example, tmp_solution)

        cmd = ["bin/validate_one_exercise", "exercises/practice/acronym"]
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
        assert "ok 1 basic" in proc.stdout, "Baseline test 'basic' missing or failed!"
        assert "ok 2 lowercase words" in proc.stdout, "Baseline test 'lowercase words' missing or failed!"
        assert "ok 3 punctuation" in proc.stdout, "Baseline test 'punctuation' missing or failed!"
        assert "1..9" in proc.stdout, "Expected 9 tests in TAP summary!"
        print("All 9 tests passed successfully against reference in temporary environment.")
        return proc.stdout


def run_bats_against_alternative():
    print("Testing alternative implementation (FPAT) against full test-acronym.bats suite...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_exercise = Path(tmpdir) / "acronym"
        shutil.copytree(EXERCISE_DIR, tmp_exercise, symlinks=True)
        
        # Write alternative implementation to acronym.awk
        (tmp_exercise / "acronym.awk").write_text(ALTERNATIVE_AWK, encoding="utf-8")
        
        bats_env = ENV.copy()
        bats_env["BATS_RUN_SKIPPED"] = "true"
        
        proc = subprocess.run(
            ["bats", "test-acronym.bats"],
            cwd=str(tmp_exercise),
            capture_output=True,
            text=True,
            env=bats_env
        )
        
        print("Bats output for alternative:")
        print(proc.stdout)
        assert proc.returncode == 0, f"Alternative failed bats tests: {proc.stderr}"
        assert "ok 1 basic" in proc.stdout, "Alternative failed 'basic'!"
        assert "ok 2 lowercase words" in proc.stdout, "Alternative failed 'lowercase words'!"
        assert "ok 3 punctuation" in proc.stdout, "Alternative failed 'punctuation'!"
        assert "1..9" in proc.stdout, "Expected 9 tests in TAP output for alternative!"
        print("Alternative implementation passed all 9 bats test cases!")
        return proc.stdout


def compare_implementations(paths: dict):
    print("Comparing reference and alternative across all test cases...")
    example_path = paths["example"]
    ref_code = example_path.read_text(encoding="utf-8")
    
    results = []
    ref_timings = []
    alt_timings = []
    
    for case in CANONICAL_TEST_CASES:
        inp = case["input"]
        expected = case["expected"]
        
        # Run Reference
        res_ref = subprocess.run(
            ["gawk", ref_code],
            input=inp,
            text=True,
            capture_output=True,
            env=ENV
        )
        assert res_ref.returncode == 0, f"Ref error on {case['name']}: {res_ref.stderr}"
        ref_out = res_ref.stdout.strip()
        assert ref_out == expected, f"Ref mismatch on {case['name']}: expected {expected}, got {ref_out}"
        
        # Run Alternative
        res_alt = subprocess.run(
            ["gawk", ALTERNATIVE_AWK],
            input=inp,
            text=True,
            capture_output=True,
            env=ENV
        )
        assert res_alt.returncode == 0, f"Alt error on {case['name']}: {res_alt.stderr}"
        alt_out = res_alt.stdout.strip()
        assert alt_out == expected, f"Alt mismatch on {case['name']}: expected {expected}, got {alt_out}"
        
        # Benchmark 7 repetitions
        ref_reps = []
        alt_reps = []
        for _ in range(7):
            t0 = time.perf_counter()
            subprocess.run(["gawk", ref_code], input=inp, text=True, capture_output=True, env=ENV)
            t1 = time.perf_counter()
            ref_reps.append((t1 - t0) * 1000)
            
            t2 = time.perf_counter()
            subprocess.run(["gawk", ALTERNATIVE_AWK], input=inp, text=True, capture_output=True, env=ENV)
            t3 = time.perf_counter()
            alt_reps.append((t3 - t2) * 1000)
            
        ref_reps.sort()
        alt_reps.sort()
        ref_med = statistics.median(ref_reps)
        alt_med = statistics.median(alt_reps)
        
        results.append({
            "id": case["id"],
            "name": case["name"],
            "input": inp,
            "expected": expected,
            "ref_actual": ref_out,
            "alt_actual": alt_out,
            "match": (ref_out == alt_out == expected),
            "ref_median_ms": round(ref_med, 4),
            "alt_median_ms": round(alt_med, 4),
        })

    return results


def save_artifacts(results, ref_tap, alt_tap):
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
        {"id": c["id"], "name": c["name"], "input": c["input"]}
        for c in results
    ]
    (WORK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2) + "\n", encoding="utf-8")

    # 3. expected_vs_actual.json
    eva_data = [
        {
            "id": c["id"],
            "name": c["name"],
            "expected": c["expected"],
            "ref_actual": c["ref_actual"],
            "alt_actual": c["alt_actual"],
            "match": c["match"],
        }
        for c in results
    ]
    (WORK_DIR / "expected_vs_actual.json").write_text(json.dumps(eva_data, indent=2) + "\n", encoding="utf-8")

    # 4. comparison.json
    comp_data = {
        "summary": {
            "total_cases": len(results),
            "matching_cases": sum(1 for c in results if c["match"]),
            "technique_1": "Delimiter splitting via FS + in-place field gsub sanitization",
            "technique_2": "Token matching via FPAT word extraction",
        },
        "cases": results,
    }
    (WORK_DIR / "comparison.json").write_text(json.dumps(comp_data, indent=2) + "\n", encoding="utf-8")

    # 5. output.txt
    out_lines = [
        "=== Reference TAP Output ===",
        ref_tap.strip(),
        "",
        "=== Alternative TAP Output ===",
        alt_tap.strip(),
        "",
        "=== Case Agreement & Performance ===",
    ]
    for c in results:
        out_lines.append(
            f"{c['name']}: expected={c['expected']!r}, ref={c['ref_actual']!r}, "
            f"alt={c['alt_actual']!r}, ref_time={c['ref_median_ms']}ms, alt_time={c['alt_median_ms']}ms"
        )
    (WORK_DIR / "output.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 6. evidence.md
    evidence_md = f"""# Verification Evidence: R06-T036 (Acronym Paradigm Comparison)

## Summary of Results
- **Validation Runs**: 9/9 test cases passed on the reference (`example.awk`).
- **Alternative Run**: 9/9 test cases passed on the alternative (`FPAT`).
- **Baseline Cases**: Verified agreement on `basic`, `lowercase words`, `punctuation`.
- **Learner Stub**: `exercises/practice/acronym/acronym.awk` remains untouched and unsolved.
- **Hint Document**: Created `exercises/practice/acronym/.docs/hints.md` containing worked examples and trade-off explanations without spoiling the solution.

## Test Agreement Table
| Test Name | Input Phrase | Expected | Ref Output | Alt Output | Agreement |
|:---|:---|:---:|:---:|:---:|:---:|
"""
    for c in results:
        evidence_md += f"| `{c['name']}` | `{c['input']}` | `{c['expected']}` | `{c['ref_actual']}` | `{c['alt_actual']}` | {'Pass' if c['match'] else 'Fail'} |\n"

    evidence_md += """
## Trade-off Analysis
1. **Approach 1 (Reference - `FS = "[[:blank:]-]+"` + `gsub`)**:
   - *Strengths*: Standard POSIX AWK compatibility; simple field delimiter logic.
   - *Weaknesses*: Mutates `$i` in place, triggering `$0` recomputation; requires secondary regular expression sanitization per field.
2. **Approach 2 (Alternative - `FPAT = "[[:alpha:]][[:alpha:]']*"`)**:
   - *Strengths*: Directly extracts word tokens, bypassing punctuation; eliminates `$i` mutation and per-field `gsub` calls.
   - *Weaknesses*: Depends on GNU AWK specific `FPAT` feature; requires regex engine to maintain token state across entire string.
"""
    (WORK_DIR / "evidence.md").write_text(evidence_md, encoding="utf-8")
    print(f"Artifacts successfully written to {WORK_DIR}")


def main():
    print("=" * 60)
    print("Starting Task R06-T036 Verification")
    print("=" * 60)
    
    paths = resolve_paths()
    verify_learner_solution(paths["solution"])
    ref_tap = run_validation_in_temp(paths)
    alt_tap = run_bats_against_alternative()
    results = compare_implementations(paths)
    save_artifacts(results, ref_tap, alt_tap)
    
    print("\nAll checks completed successfully!")


if __name__ == "__main__":
    main()
