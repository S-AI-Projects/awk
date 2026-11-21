#!/usr/bin/env python3
"""Run hello-world's configured reference tests in an isolated exercise copy."""
import argparse,json,re,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EX=ROOT/"exercises/practice/hello-world"

def run(example_override: Path|None=None, test_filter: str|None=None) -> tuple[int,int,str]:
    config=json.loads((EX/".meta/config.json").read_text())
    files=config.get("files",{})
    paths={}
    for role in ("solution","test","example"):
        if role not in files or not files[role]: raise ValueError(f"missing {role} path in config")
        rel=Path(files[role][0])
        if rel.is_absolute() or ".." in rel.parts: raise ValueError(f"invalid {role} path")
        path=(EX/rel).resolve()
        if not path.is_relative_to(EX.resolve()) or not path.is_file(): raise ValueError(f"invalid or missing {role} file: {rel}")
        paths[role]=path
    with tempfile.TemporaryDirectory(prefix="r06-t009-") as td:
        copied=Path(td)/EX.name
        shutil.copytree(EX,copied)
        source=example_override or paths["example"]
        shutil.copy2(source,copied/files["example"][0])
        shutil.copy2(copied/files["example"][0],copied/files["solution"][0])
        env=None
        if test_filter is None:
            cmd=[str(ROOT/"bin/validate_one_exercise"),str(copied)]; cwd=ROOT
        else:
            cmd=["bats","--filter",test_filter,files["test"][0]]; cwd=copied
            import os
            env=os.environ.copy(); env["BATS_RUN_SKIPPED"]="true"
        proc=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        match=re.search(r"(?m)^1\.\.(\d+)\s*$",proc.stdout)
        count=int(match.group(1)) if match else 0
        if proc.returncode!=0 or count==0:
            return proc.returncode or 2,count,proc.stdout
        return 0,count,proc.stdout

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--example",type=Path,help="temporary alternate reference for negative checks")
    parser.add_argument("--filter",help="Bats test-name regex; zero matches is an error")
    args=parser.parse_args()
    code,count,out=run(args.example,args.filter)
    print(out,end="")
    print(f"Executed tests: {count}")
    if code: raise SystemExit(code)
if __name__=="__main__": main()
