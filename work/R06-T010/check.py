from pathlib import Path
import json,re,shutil,subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/gigasecond"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]
selected=[("2011-04-25","2043-01-01T01:46:40"),("1977-06-13","2009-02-19T01:46:40"),("1959-07-19","1991-03-27T01:46:40")]
with tempfile.TemporaryDirectory(prefix="r06-t010-") as td:
    copy=Path(td)/EX.name; shutil.copytree(EX,copy)
    shutil.copy2(copy/FILES["example"][0],copy/FILES["solution"][0])
    validator=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert validator.returncode==0,validator.stdout
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",validator.stdout); assert m and int(m.group(1))>0,validator.stdout
    actuals=[]
    for date,expected in selected:
        p=subprocess.run(["gawk","-f",FILES["solution"][0]],cwd=copy,input=date+"\n",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        actual=p.stdout.strip(); assert p.returncode==0 and actual==expected,(date,expected,actual,p.stderr)
        actuals.append(f"input={date}; default=00:00:00 UTC; expected={expected}; actual={actual}; exit={p.returncode}")
awk=subprocess.check_output(["gawk","--version"],text=True).splitlines()[0]
(ROOT/"work/R06-T010/results.txt").write_text(f"Reference cases executed: {m.group(1)}\n{awk}\nPython: {sys.version}\nSelected cases (input / expected / actual):\n"+"\n".join(actuals)+"\n")
print(f"PASS: {m.group(1)} reference cases; all 3 date-only outcomes match")
