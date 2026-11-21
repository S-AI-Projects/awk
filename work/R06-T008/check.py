from pathlib import Path
import json,re,shutil,subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/rectangles"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]
check=subprocess.run([sys.executable,str(ROOT/"tools/course_checks/r06-t008.py")],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
assert check.returncode==0,check.stdout
for role in ("solution","test","example"):
    with tempfile.TemporaryDirectory(prefix=f"r06-t008-{role}-") as td:
        bad=json.loads((EX/".meta/config.json").read_text())
        if role=="solution": bad["files"][role]=["missing.awk"]
        elif role=="test": bad["files"][role]=["missing.bats"]
        else: bad["files"][role]=["../outside.awk"]
        fixture=Path(td)/"config.json"; fixture.write_text(json.dumps(bad))
        code="import importlib.util,json,sys;from pathlib import Path;s=importlib.util.spec_from_file_location('check',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.validate_files(Path(sys.argv[2]),json.load(open(sys.argv[3])))"
        p=subprocess.run([sys.executable,"-c",code,str(ROOT/"tools/course_checks/r06-t008.py"),str(EX),str(fixture)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert p.returncode!=0, f"invalid {role} fixture unexpectedly passed"
        reason="path outside exercise" if role=="example" else "missing"
        assert reason in p.stderr,(role,p.stderr)
with tempfile.TemporaryDirectory(prefix="r06-t008-validate-") as td:
    copy=Path(td)/EX.name; shutil.copytree(EX,copy); shutil.copy2(copy/FILES["example"][0],copy/FILES["solution"][0])
    run=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert run.returncode==0,run.stdout
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",run.stdout); assert m and int(m.group(1))>0,run.stdout
(ROOT/"work/R06-T008/results.txt").write_text(f"Config checker: {check.stdout}Negative fixtures: missing solution file, missing test file, outside-exercise example path all rejected for intended reasons.\nReference cases executed: {m.group(1)}\nPython: {sys.version}\nValidator output:\n{run.stdout}")
print(f"PASS: real config; 3 invalid metadata fixtures rejected; {m.group(1)} reference cases")
