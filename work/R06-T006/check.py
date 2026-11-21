from pathlib import Path
import json,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/atbash-cipher"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]
ALTERNATIVE=ROOT/"work/R06-T006/alternative.awk"

def validate(example):
    with tempfile.TemporaryDirectory(prefix="r06-t006-") as td:
        copy=Path(td)/EX.name; shutil.copytree(EX,copy)
        solution=copy/FILES["solution"][0]
        shutil.copy2(example,solution)
        subprocess.run(["cp",str(example),str(copy/FILES["example"][0])],check=True)
        p=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return p.returncode,p.stdout
reference=EX/FILES["example"][0]
ref_rc,ref_out=validate(reference); alt_rc,alt_out=validate(ALTERNATIVE)
assert ref_rc==alt_rc==0,(ref_out,alt_out)
def count(out):
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",out); assert m,out; return int(m.group(1))
assert count(ref_out)==count(alt_out)>0
micro=[]
for data,expected in (("yes","bvh"),("no","ml"),("OMG","lnt")):
    run=subprocess.run(["gawk","-v","direction=encode","-f",str(ALTERNATIVE)],input=data+"\n",text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert run.returncode==0 and run.stdout.strip()==expected,(data,run.stdout,run.stderr)
    micro.append(f"input={data}; expected={expected}; actual={run.stdout.strip()}; exit={run.returncode}")
awk=subprocess.check_output(["gawk","--version"],text=True).splitlines()[0]
(ROOT/"work/R06-T006/results.txt").write_text(f"Reference cases: {count(ref_out)}\nAlternative cases: {count(alt_out)}\n{awk}\nPython: {__import__('sys').version}\nMicro-examples (expected vs actual):\n"+"\n".join(micro)+"\nTrade-off: direct string search has no map setup but searches the 26-character alphabet for each letter.\n")
print(f"PASS: both approaches pass {count(ref_out)} enabled cases; three micro-examples match")
