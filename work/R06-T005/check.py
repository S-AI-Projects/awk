from pathlib import Path
import json, re, shutil, statistics, subprocess, tempfile, time
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/run-length-encoding"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]
with tempfile.TemporaryDirectory(prefix="r06-t005-") as td:
    copy=Path(td)/EX.name; shutil.copytree(EX,copy)
    shutil.copy2(copy/FILES["example"][0],copy/FILES["solution"][0])
    p=subprocess.run([str(ROOT/"bin/validate_one_exercise"),str(copy)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert p.returncode==0,p.stdout
    m=re.search(r"(?m)^1\.\.(\d+)\s*$",p.stdout); assert m and int(m.group(1))>0,p.stdout

reference=EX/FILES["example"][0]; records=[]; results=[]
for n in (256,512,1024):
    data="A"*n+"\n"; expected=f"{n}A"
    check=subprocess.run(["gawk","-v","type=encode","-f",str(reference)],input=data,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert check.returncode==0 and check.stdout.strip()==expected,(n,check.returncode,check.stdout,check.stderr)
    samples=[]
    for _ in range(5):
        start=time.perf_counter()
        run=subprocess.run(["gawk","-v","type=encode","-f",str(reference)],input=data,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        samples.append((time.perf_counter()-start)*1000)
        assert run.returncode==0 and run.stdout.strip()==expected,(n,run.returncode,run.stdout,run.stderr)
    median=statistics.median(samples); records.append((n,expected,median)); results.append(f"n={n}; expected={expected}; median_ms={median:.3f}; samples_ms="+",".join(f"{x:.3f}" for x in samples))
awk=subprocess.check_output(["gawk","--version"],text=True).splitlines()[0]
report=f"Reference tests executed: {m.group(1)}\nPython: {__import__('sys').version}\n{awk}\nMeasurements: 5 repetitions per size, correctness asserted before timing; end-to-end process time.\n"+"\n".join(results)+"\n"
(ROOT/"work/R06-T005/results.txt").write_text(report)
print(f"PASS: {m.group(1)} reference cases; 3 valid sizes checked; 5 timings each")
