import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

def count_toml_cases(toml_path):
    with open(toml_path, "r", encoding="utf-8") as f:
        content = f.read()
    # In tests.toml, sections [uuid] represent test cases
    uuids = re.findall(r"^\[([0-9a-fA-F-]+)\]", content, re.MULTILINE)
    excluded = len(re.findall(r"include\s*=\s*false", content))
    included = len(uuids) - excluded
    return included, excluded, content

def main():
    repo_root = os.getcwd()
    work_dir = os.path.join(repo_root, "work", "R06-T051")
    os.makedirs(work_dir, exist_ok=True)

    exercise_path = "exercises/practice/difference-of-squares"
    meta_dir = os.path.join(repo_root, exercise_path, ".meta")
    toml_path = os.path.join(meta_dir, "tests.toml")
    config_path = os.path.join(meta_dir, "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    solution_file = config["files"]["solution"][0]
    example_file = config["files"]["example"][0]

    # Verify learner stub is unsolved in working tree
    with open(os.path.join(repo_root, exercise_path, solution_file), "r", encoding="utf-8") as f:
        stub_content = f.read()
    if "Implement this solution" not in stub_content:
        print("Check failed: learner stub has been modified or solved.", file=sys.stderr)
        sys.exit(1)

    # Check tests.toml rationales
    inc_count, exc_count, toml_text = count_toml_cases(toml_path)
    print(f"tests.toml cases -> Included: {inc_count}, Excluded: {exc_count}")

    target_uuids = [
        "e46c542b-31fc-4506-bcae-6b62b3268537",
        "9b3f96cb-638d-41ee-99b7-b4f9c0622948",
        "54ba043f-3c35-4d43-86ff-3a41625d5e86"
    ]
    for uid in target_uuids:
        if uid not in toml_text:
            print(f"Check failed: UUID {uid} missing in tests.toml", file=sys.stderr)
            sys.exit(1)
        # Verify comment key is present for each target
        match = re.search(rf"\[{uid}\](.*?)(?=\n\[|\Z)", toml_text, re.DOTALL)
        if not match or "comment" not in match.group(1):
            print(f"Check failed: comment rationale missing for {uid}", file=sys.stderr)
            sys.exit(1)

    # Test in a temporary directory
    with tempfile.TemporaryDirectory() as tmp:
        def ignore_patterns(path, names):
            return [".git", "work"] if path == repo_root else []

        tmp_repo = os.path.join(tmp, "repo")
        shutil.copytree(repo_root, tmp_repo, ignore=ignore_patterns)

        # Substitute reference solution only in the temp copy
        src_example = os.path.join(tmp_repo, exercise_path, example_file)
        dst_solution = os.path.join(tmp_repo, exercise_path, solution_file)
        shutil.copy2(src_example, dst_solution)

        cmd = ["bin/validate_one_exercise", exercise_path]
        result = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)

        passed_tests = len(re.findall(r"^ok\s+\d+", result.stdout, re.MULTILINE))
        failed_tests = len(re.findall(r"^not ok\s+\d+", result.stdout, re.MULTILINE))
        total_executed = passed_tests + failed_tests

        # Ensure named cases pass
        named_cases = ["square of sum 1", "square of sum 5", "square of sum 100"]
        for case in named_cases:
            if not re.search(rf"^ok\s+\d+\s+{re.escape(case)}", result.stdout, re.MULTILINE):
                print(f"Check failed: named case '{case}' was not executed or failed.", file=sys.stderr)
                sys.exit(1)

        summary = (
            f"=== EXECUTION SUMMARY ===\n"
            f"TOML Included Cases: {inc_count}\n"
            f"TOML Excluded Cases: {exc_count}\n"
            f"Executed Test Cases: {total_executed}\n"
            f"Passed: {passed_tests}, Failed: {failed_tests}\n\n"
            f"=== VALIDATOR OUTPUT ===\n"
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

        print(f"Check passed: {total_executed} test cases executed cleanly against reference solution.")

if __name__ == "__main__":
    main()
