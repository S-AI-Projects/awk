import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

def main():
    repo_root = os.getcwd()
    work_dir = os.path.join(repo_root, "work", "R06-T058")
    os.makedirs(work_dir, exist_ok=True)

    exercise_path = "exercises/practice/knapsack"
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

    # 1. Run the course check tool
    course_tool = os.path.join(repo_root, "tools", "course_checks", "r06-t058.py")
    course_res = subprocess.run([sys.executable, course_tool], cwd=repo_root, capture_output=True, text=True)
    if course_res.returncode != 0:
        print(f"Check failed: tools/course_checks/r06-t058.py failed.\n{course_res.stderr}", file=sys.stderr)
        sys.exit(1)
    print(course_res.stdout.strip())

    # 2. Test in a temporary directory
    print("Validating knapsack reference implementation...")
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
            "no items",
            "one item, too heavy",
            "five items (cannot be greedy by weight)"
        ]
        for case in named_cases:
            if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", result.stdout, re.MULTILINE):
                print(f"Check failed: named case '{case}' was not executed or failed.", file=sys.stderr)
                sys.exit(1)

        summary = (
            "=== EXECUTION SUMMARY ===\n"
            f"Executed Test Cases: {total_executed}\n"
            f"Passed: {passed_tests}, Failed: {failed_tests}\n"
            f"Named Cases Verified: {', '.join(named_cases)}\n"
            "Metadata Fixture Validation: PASS\n\n"
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

        print(f"Check passed: all {total_executed} test cases and metadata fixtures verified cleanly.")

if __name__ == "__main__":
    main()
