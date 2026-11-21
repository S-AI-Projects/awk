from pathlib import Path
import json,re,shutil,subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/darts"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]
with tempfile.TemporaryDirectory(prefix="r06-t007-") as td:
    copy=Path(td)/EX.name; shutil.copytree(EX,copy)
    shutil.copy2(copy/FILES["example"][0],copy/FILES["solution"][0])
    p=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert p.returncode==0,p.stdout
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",p.stdout); assert m and int(m.group(1))>0,p.stdout
snippet="printf '3 4\\n' | gawk '{ d = sqrt($1^2 + $2^2); print d, d <= 5, d < 5 }'"
actual=subprocess.run(["sh","-c",snippet],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
expected="5 1 0"
assert actual.returncode==0 and actual.stdout.strip()==expected,(actual.returncode,actual.stdout,actual.stderr)
awk=subprocess.check_output(["gawk","--version"],text=True).splitlines()[0]
(ROOT/"work/R06-T007/results.txt").write_text(f"Reference cases executed: {m.group(1)}\nMicro-example input: 3 4\nExpected: {expected}\nActual: {actual.stdout.strip()}\n{awk}\nPython: {sys.version}\n")
print(f"PASS: {m.group(1)} reference cases; numeric coercion/boundary example prints {expected}")
