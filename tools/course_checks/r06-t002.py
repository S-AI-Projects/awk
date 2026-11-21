#!/usr/bin/env python3
"""Check simple-cipher's maintained test source in two clean copies."""
import argparse, hashlib, json, pathlib, shutil, tempfile, tomllib
ROOT=pathlib.Path(__file__).resolve().parents[2]
EX=ROOT/"exercises/practice/simple-cipher"
parser=argparse.ArgumentParser(); parser.add_argument("--output",type=pathlib.Path); args=parser.parse_args()
config=json.loads((EX/".meta/config.json").read_text())
test=EX/config["files"]["test"][0]
assert test.is_file()
assert not (EX/".meta/template.j2").exists(), "template appeared; update the maintenance route"
source=test.read_bytes(); digest=hashlib.sha256(source).hexdigest()
canonical=tomllib.loads((EX/".meta/tests.toml").read_text())
expected={
    "defc0050-e87d-4840-85e4-51a1ab9dd6aa":"Random key cipher -> Key is made only of lowercase letters",
    "b8bdfbe1-bea3-41bb-a999-b41403f2b15d":"Random key cipher -> Can encode",
    "3dff7f36-75db-46b4-ab70-644b3f38b81c":"Random key cipher -> Can decode",
}
for uuid,description in expected.items():
    assert canonical[uuid]["description"]==description, f"canonical mapping changed for {uuid}"
with tempfile.TemporaryDirectory(prefix="r06-t002-") as td:
    copies=[]
    for n in ("one","two"):
        target=pathlib.Path(td)/n/EX.name
        shutil.copytree(EX,target)
        copied=target/config["files"]["test"][0]
        copies.append(copied.read_bytes())
    assert copies[0]==copies[1]==source, "maintained test source changed in a clean copy"
for case in ("Can generate a random key","Can encode random","Can decode random"):
    assert f'@test  "{case}"'.encode() in source, f"missing maintained case {case}"
text=(f"PASS: maintained test source copied identically twice; sha256={digest}; "
      "all three required cases are present. bin/generate_tests is not applicable because .meta/template.j2 is absent.\n")
if args.output: args.output.write_text(text)
print(text,end="")
