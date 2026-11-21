from pathlib import Path
import json, re, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/house"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]

def run(example):
    with tempfile.TemporaryDirectory(prefix="r06-t003-") as td:
        copy=Path(td)/EX.name; shutil.copytree(EX,copy)
        shutil.copy2(example,copy/FILES["example"][0]); shutil.copy2(copy/FILES["example"][0],copy/FILES["solution"][0])
        p=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return p.returncode,p.stdout

normal, normal_out=run(EX/FILES["example"][0]); assert normal==0,normal_out
match=re.search(r"(?m)^1\.\.(\d+)\s*$",normal_out); assert match,normal_out
count=int(match.group(1))
mutant, mutant_out=run(ROOT/"work/R06-T003/mutant.awk"); assert mutant!=0,"mutant unexpectedly passed"
assert 'verse two - the malt that lay' in mutant_out, mutant_out
(ROOT/"work/R06-T003/results.txt").write_text(f"Input: start=2,end=2\nExpected: This is the malt that lay in the house that Jack built.\nOriginal exit: {normal}\nMutant exit: {mutant}\nExecuted original cases: {count}\n\nMutant output:\n{mutant_out}")
print(f"PASS: original passed {count} tests; mutation rejected by verse two case")
