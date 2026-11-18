import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

def run_tests_with_solution(repo_root, exercise_path, solution_rel, source_file):
    with tempfile.TemporaryDirectory() as tmp:
        def ignore_patterns(path, names):
            return [".git", "work"] if path == repo_root else []

        tmp_repo = os.path.join(tmp, "repo")
        shutil.copytree(repo_root, tmp_repo, ignore=ignore_patterns)

        dst_solution = os.path.join(tmp_repo, exercise_path, solution_rel)
        shutil.copy2(source_file, dst_solution)

        cmd = ["bin/validate_one_exercise", exercise_path]
        result = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)

        passed = len(re.findall(r"^ok\s+\d+", result.stdout, re.MULTILINE))
        failed = len(re.findall(r"^not ok\s+\d+", result.stdout, re.MULTILINE))
        return result.returncode, passed, failed, result.stdout, result.stderr

def main():
    repo_root = os.getcwd()
    work_dir = os.path.join(repo_root, "work", "R06-T056")
    os.makedirs(work_dir, exist_ok=True)

    exercise_path = "exercises/practice/crypto-square"
    config_path = os.path.join(repo_root, exercise_path, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    solution_file = config["files"]["solution"][0]
    example_file = config["files"]["example"][0]
    alternative_file = os.path.join(work_dir, "alternative.awk")

    # Verify learner stub is unsolved in working tree
    stub_path = os.path.join(repo_root, exercise_path, solution_file)
    with open(stub_path, "r", encoding="utf-8") as f:
        stub_content = f.read()
    if "Implement this solution" not in stub_content:
        print("Check failed: learner stub has been modified or solved.", file=sys.stderr)
        sys.exit(1)

    named_cases = [
        "empty plaintext results in an empty ciphertext",
        "normalization results in empty plaintext",
        "Lowercase"
    ]

    # 1. Validate Reference implementation
    print("Validating reference implementation...")
    ref_source = os.path.join(repo_root, exercise_path, example_file)
    rc_ref, passed_ref, failed_ref, stdout_ref, stderr_ref = run_tests_with_solution(
        repo_root, exercise_path, solution_file, ref_source
    )
    if rc_ref != 0 or failed_ref > 0 or passed_ref == 0:
        print("Check failed: reference implementation failed validation.", file=sys.stderr)
        sys.exit(1)

    for case in named_cases:
        if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", stdout_ref, re.MULTILINE):
            print(f"Check failed: reference did not pass '{case}'.", file=sys.stderr)
            sys.exit(1)

    # 2. Validate Alternative implementation
    print("Validating alternative implementation...")
    rc_alt, passed_alt, failed_alt, stdout_alt, stderr_alt = run_tests_with_solution(
        repo_root, exercise_path, solution_file, alternative_file
    )
    if rc_alt != 0 or failed_alt > 0 or passed_alt == 0:
        print(f"Check failed: alternative implementation failed validation.\n{stdout_alt}\n{stderr_alt}", file=sys.stderr)
        sys.exit(1)

    for case in named_cases:
        if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", stdout_alt, re.MULTILINE):
            print(f"Check failed: alternative did not pass '{case}'.", file=sys.stderr)
            sys.exit(1)

    # 3. Direct Output Equivalence Check
    baseline_inputs = ["", "... --- ...", "A", "This is fun!", "Chill out."]
    for inp in baseline_inputs:
        p_ref = subprocess.run(["gawk", "-f", ref_source], input=inp, capture_output=True, text=True)
        p_alt = subprocess.run(["gawk", "-f", alternative_file], input=inp, capture_output=True, text=True)
        if p_ref.stdout != p_alt.stdout:
            print(f"Check failed: output mismatch on input '{inp}'. Ref: '{p_ref.stdout}', Alt: '{p_alt.stdout}'", file=sys.stderr)
            sys.exit(1)

    summary = (
        "=== EXECUTION SUMMARY ===\n"
        f"Reference Tests Passed: {passed_ref}, Failed: {failed_ref}\n"
        f"Alternative Tests Passed: {passed_alt}, Failed: {failed_alt}\n"
        f"Named Cases Verified: {', '.join(named_cases)}\n"
        "Output Agreement: EXACT MATCH on all inputs\n\n"
        "=== REFERENCE VALIDATOR OUTPUT ===\n"
        f"{stdout_ref}\n"
        "=== ALTERNATIVE VALIDATOR OUTPUT ===\n"
        f"{stdout_alt}\n"
    )

    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(summary)

    gawk_ver = subprocess.run(["gawk", "--version"], capture_output=True, text=True).stdout
    bats_ver = subprocess.run(["bats", "--version"], capture_output=True, text=True).stdout
    with open(os.path.join(work_dir, "versions.txt"), "w", encoding="utf-8") as f:
        f.write(f"AWK Version:\n{gawk_ver}\nBATS Version:\n{bats_ver}")

    print(f"Check passed: both implementations executed all {passed_ref} tests with exact agreement.")

if __name__ == "__main__":
    main()
