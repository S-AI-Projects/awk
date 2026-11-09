import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

def count_toml_inclusions(toml_path):
    with open(toml_path, "r") as f:
        content = f.read()
    included = len(re.findall(r"include\s*=\s*true", content))
    excluded = len(re.findall(r"include\s*=\s*false", content))
    return included, excluded

def main():
    repo_root = os.getcwd()
    work_dir = os.path.join(repo_root, "work", "R06-T011")
    os.makedirs(work_dir, exist_ok=True)
    
    ex_path = "exercises/practice/grade-school"
    toml_path = os.path.join(repo_root, ex_path, ".meta", "tests.toml")
    config_path = os.path.join(repo_root, ex_path, ".meta", "config.json")
    
    # 1. Record included/excluded counts before execution
    inc_count, exc_count = count_toml_inclusions(toml_path)
    print(f"tests.toml Inclusions -> Included: {inc_count}, Excluded: {exc_count}")
    
    with open(config_path, "r") as f:
        config = json.load(f)
        
    solution_rel = config["files"]["solution"][0]
    example_rel = config["files"]["example"][0]
    
    with tempfile.TemporaryDirectory() as tmp:
        def ignore_patterns(path, names):
            return [".git", "work"] if path == repo_root else []
            
        tmp_repo = os.path.join(tmp, "repo")
        shutil.copytree(repo_root, tmp_repo, ignore=ignore_patterns)
        
        # Swap reference solution for validation while keeping learner stub unchanged
        src = os.path.join(tmp_repo, ex_path, example_rel)
        dst = os.path.join(tmp_repo, ex_path, solution_rel)
        shutil.copy2(src, dst)
        
        # Run test suite validator
        cmd = ["bin/validate_one_exercise", ex_path]
        result = subprocess.run(cmd, cwd=tmp_repo, capture_output=True, text=True)
        
        # Parse test execution counts from TAP output (e.g., 'ok 1 ...')
        passed_tests = len(re.findall(r"^ok\s+\d+", result.stdout, re.MULTILINE))
        failed_tests = len(re.findall(r"^not ok\s+\d+", result.stdout, re.MULTILINE))
        total_executed = passed_tests + failed_tests
        
        output_log = (
            f"=== EXECUTION SUMMARY ===\n"
            f"TOML Included Cases: {inc_count}\n"
            f"TOML Excluded Cases: {exc_count}\n"
            f"Executed Test Cases: {total_executed}\n"
            f"Passed: {passed_tests}, Failed: {failed_tests}\n\n"
            f"=== VALIDATOR STDOUT/STDERR ===\n"
            f"{result.stdout}\n{result.stderr}"
        )
        
        with open(os.path.join(work_dir, "output.txt"), "w") as f:
            f.write(output_log)
            
        awk_ver = subprocess.run(["awk", "--version"], capture_output=True, text=True).stdout
        bats_ver = subprocess.run(["bats", "--version"], capture_output=True, text=True).stdout
        with open(os.path.join(work_dir, "versions.txt"), "w") as f:
            f.write(f"AWK Version:\n{awk_ver}\nBATS Version:\n{bats_ver}")
            
        # Assertion checks
        if result.returncode != 0:
            print("Check failed: Validation returned a non-zero exit code.", file=sys.stderr)
            sys.exit(1)
            
        if total_executed == 0:
            print("Check failed: Zero test cases were executed.", file=sys.stderr)
            sys.exit(1)
            
        if failed_tests > 0:
            print(f"Check failed: {failed_tests} test cases failed.", file=sys.stderr)
            sys.exit(1)
            
        print(f"Check passed! Executed {total_executed} tests cleanly against reference implementation.")

if __name__ == "__main__":
    main()

