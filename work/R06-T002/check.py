from pathlib import Path
import json, re, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[2]
EX=ROOT/"exercises/practice/simple-cipher"
config=json.loads((EX/".meta/config.json").read_text()); files=config["files"]
for role in ("solution","test","example"):
    p=EX/files[role][0]
    assert p.is_file() and p.resolve().is_relative_to(EX.resolve()), (role,p)

with tempfile.TemporaryDirectory(prefix="r06-t002-validate-") as td:
    copy=Path(td)/EX.name; shutil.copytree(EX,copy)
    shutil.copy2(copy/files["example"][0],copy/files["solution"][0])
    run=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert run.returncode==0,run.stdout
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",run.stdout); assert m and int(m.group(1))>0,run.stdout
proc=subprocess.run([sys.executable,str(ROOT/"tools/course_checks/r06-t002.py"),"--output",str(ROOT/"work/R06-T002/generation.txt")],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
assert proc.returncode==0,proc.stdout
(ROOT/"work/R06-T002/results.txt").write_text(f"Executed cases: {m.group(1)}\nMaintained-source check: {proc.stdout}\nValidator output:\n{run.stdout}\nPython: {sys.version}\nGNU awk: {subprocess.check_output(['gawk','--version'],text=True).splitlines()[0]}\nBats: {subprocess.check_output(['bats','--version'],text=True).strip()}\n")
print(f"PASS: {m.group(1)} Bats cases; maintained test source is stable across two copies")
