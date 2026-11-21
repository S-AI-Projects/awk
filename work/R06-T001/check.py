from pathlib import Path
import subprocess, sys, tomllib
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/course_checks"))
from common import validate_reference

meta = ROOT / "exercises/practice/variable-length-quantity/.meta/tests.toml"
data = tomllib.loads(meta.read_text())
before_text = subprocess.check_output(["git", "show", "origin/main:exercises/practice/variable-length-quantity/.meta/tests.toml"], cwd=ROOT, text=True)
before = tomllib.loads(before_text)
def counts(cases):
    included = sum(case.get("include", True) is not False for case in cases.values())
    excluded = sum(case.get("include", True) is False for case in cases.values())
    return included, excluded
before_included, before_excluded = counts(before)
after_included, after_excluded = counts(data)
assert len(data) == 31, f"expected 31 canonical entries, got {len(data)}"
assert all(not item.get("include") is False for item in data.values()), "unexpected exclusion"
ids = ["35c9db2e-f781-4c52-b73b-8e76427defd0", "be44d299-a151-4604-a10e-d4b867f41540", "890bc344-cb80-45af-b316-6806a6971e81"]
for key in ids:
    assert data[key].get("comment"), f"missing rationale for {key}"
out, count = validate_reference(ROOT, "variable-length-quantity")
assert (before_included, before_excluded) == (after_included, after_excluded), "canonical include/exclude counts changed"
versions = "\n".join((sys.version, subprocess.check_output(["gawk", "--version"], text=True).splitlines()[0], subprocess.check_output(["bats", "--version"], text=True).strip()))
report = (f"Before: included={before_included}; excluded={before_excluded}\n"
          f"After: included={after_included}; excluded={after_excluded}\n"
          f"Executed Bats cases: {count}\nTool versions:\n{versions}\n\n{out}")
(ROOT / "work/R06-T001/results.txt").write_text(report)
print(f"PASS: included/excluded unchanged ({after_included}/{after_excluded}); {count} reference tests executed")
