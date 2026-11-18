import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

def main():
    repo_root = os.getcwd()
    work_dir = os.path.join(repo_root, "work", "R06-T053")
    os.makedirs(work_dir, exist_ok=True)

    exercise_path = "exercises/practice/wordy"
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

    # 1. Test original reference in temporary directory
    print("Testing original reference implementation...")
    with tempfile.TemporaryDirectory() as tmp1:
        def ignore_patterns(path, names):
            return [".git", "work"] if path == repo_root else []

        tmp_repo1 = os.path.join(tmp1, "repo")
        shutil.copytree(repo_root, tmp_repo1, ignore=ignore_patterns)

        src_example = os.path.join(tmp_repo1, exercise_path, example_file)
        dst_solution = os.path.join(tmp_repo1, exercise_path, solution_file)
        shutil.copy2(src_example, dst_solution)

        cmd = ["bin/validate_one_exercise", exercise_path]
        orig_res = subprocess.run(cmd, cwd=tmp_repo1, capture_output=True, text=True)

        passed_orig = len(re.findall(r"^ok\s+\d+", orig_res.stdout, re.MULTILINE))
        failed_orig = len(re.findall(r"^not ok\s+\d+", orig_res.stdout, re.MULTILINE))
        total_orig = passed_orig + failed_orig

        if orig_res.returncode != 0 or failed_orig > 0 or total_orig == 0:
            print("Check failed: original reference failed validation.", file=sys.stderr)
            sys.exit(1)

        named_cases = ["just a number", "just a zero", "just a negative number"]
        for case in named_cases:
            if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", orig_res.stdout, re.MULTILINE):
                print(f"Check failed: original did not pass named case '{case}'.", file=sys.stderr)
                sys.exit(1)

        print(f"Original passed all {total_orig} test cases cleanly.")

    # 2. Test mutant implementation in another temporary directory
    print("Testing mutated implementation...")
    with tempfile.TemporaryDirectory() as tmp2:
        tmp_repo2 = os.path.join(tmp2, "repo")
        shutil.copytree(repo_root, tmp_repo2, ignore=ignore_patterns)

        example_path2 = os.path.join(tmp_repo2, exercise_path, example_file)
        with open(example_path2, "r", encoding="utf-8") as f:
            code = f.read()

        mutated_code = code.replace(
            "return num ~ /^[+-]?[[:digit:]]+$/",
            "return num ~ /^[[:digit:]]+$/"
        )
        if mutated_code == code:
            print("Check failed: unable to apply mutant to looks_like_a_number.", file=sys.stderr)
            sys.exit(1)

        with open(example_path2, "w", encoding="utf-8") as f:
            f.write(mutated_code)

        dst_solution2 = os.path.join(tmp_repo2, exercise_path, solution_file)
        shutil.copy2(example_path2, dst_solution2)

        mut_res = subprocess.run(cmd, cwd=tmp_repo2, capture_output=True, text=True)

        # The mutant must fail
        if mut_res.returncode == 0:
            print("Check failed: mutant unexpectedly passed all tests.", file=sys.stderr)
            sys.exit(1)

        if not re.search(r"^not ok\s+\d+\s+just a negative number", mut_res.stdout, re.MULTILINE):
            print("Check failed: mutant did not fail specifically on 'just a negative number'.", file=sys.stderr)
            sys.exit(1)

        print("Mutant correctly rejected by test case 'just a negative number'.")

    # Record evidence
    summary = (
        "=== EXECUTION SUMMARY ===\n"
        f"Original Total Tests: {total_orig}\n"
        f"Original Passed: {passed_orig}\n"
        f"Original Failed: {failed_orig}\n"
        f"Named Cases Verified: {', '.join(named_cases)}\n"
        "Mutant Target: looks_like_a_number stripped of [+-]?\n"
        "Mutant Result: FAILED (as expected)\n"
        "Rejecting Test: just a negative number\n\n"
        "=== ORIGINAL VALIDATOR OUTPUT ===\n"
        f"{orig_res.stdout}\n"
        "=== MUTANT VALIDATOR OUTPUT ===\n"
        f"{mut_res.stdout}\n"
    )
    with open(os.path.join(work_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(summary)

    gawk_ver = subprocess.run(["gawk", "--version"], capture_output=True, text=True).stdout
    bats_ver = subprocess.run(["bats", "--version"], capture_output=True, text=True).stdout
    with open(os.path.join(work_dir, "versions.txt"), "w", encoding="utf-8") as f:
        f.write(f"AWK Version:\n{gawk_ver}\nBATS Version:\n{bats_ver}")

    print("Check passed: mutation analysis verified successfully.")

if __name__ == "__main__":
    main()
