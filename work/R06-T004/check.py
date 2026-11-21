from pathlib import Path
import json,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/saddle-points"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]

def validate(source):
    with tempfile.TemporaryDirectory(prefix="r06-t004-") as td:
        copy=Path(td)/EX.name; shutil.copytree(EX,copy)
        shutil.copy2(source,copy/FILES["example"][0]); shutil.copy2(copy/FILES["example"][0],copy/FILES["solution"][0])
        p=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return p.returncode,p.stdout
baseline=Path(tempfile.mkstemp(prefix="r06-t004-base-")[1]); baseline.write_bytes(subprocess.check_output(["git","show","origin/main:exercises/practice/saddle-points/.meta/example.awk"],cwd=ROOT))
try:
    before,out_before=validate(baseline); after,out_after=validate(EX/FILES["example"][0])
finally: baseline.unlink(missing_ok=True)
assert before==after==0,(out_before,out_after)
def count(out):
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",out); assert m,out; return int(m.group(1))
assert count(out_before)==count(out_after)>0
(ROOT/"work/R06-T004/results.txt").write_text(f"Baseline cases: {count(out_before)}\nRefactored cases: {count(out_after)}\nBoth runs exit 0; Bats assertions verify the same expected outputs.\n\nBaseline output:\n{out_before}\nRefactored output:\n{out_after}")
print(f"PASS: baseline and refactor both passed {count(out_after)} cases")
