from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]; EX=ROOT/"exercises/practice/hello-world"; FILES=json.loads((EX/".meta/config.json").read_text())["files"]
learner=EX/FILES["solution"][0]
def digest(): return hashlib.sha256(learner.read_bytes()).hexdigest()
before=digest(); runner=ROOT/"tools/course_checks/r06-t009.py"

def invoke(*args): return subprocess.run([sys.executable,str(runner),*map(str,args)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
success=invoke(); assert success.returncode==0,success.stdout
assert "Executed tests: 1" in success.stdout,success.stdout
failure=invoke("--example",ROOT/"work/R06-T009/failing-example.awk"); assert failure.returncode!=0,"bad reference unexpectedly passed"
assert "not the expected greeting" in failure.stdout.lower(),failure.stdout
empty=invoke("--filter","^NO_SUCH_HELLO_CASE$"); assert empty.returncode!=0,"zero-test selection unexpectedly passed"
assert "Executed tests: 0" in empty.stdout,empty.stdout
after=digest(); assert before==after,"learner stub changed during isolated runs"
bats=subprocess.check_output(["bats","--version"],text=True).strip(); awk=subprocess.check_output(["gawk","--version"],text=True).splitlines()[0]
(ROOT/"work/R06-T009/results.txt").write_text(f"Learner SHA-256 before: {before}\nLearner SHA-256 after success/failure/zero-selection: {after}\nSuccess exit: {success.returncode}; output:\n{success.stdout}\nFailing-reference exit: {failure.returncode}; output:\n{failure.stdout}\nEmpty-selection exit: {empty.returncode}; output:\n{empty.stdout}\nPython: {sys.version}\n{bats}\n{awk}\n")
print("PASS: reference success, failing reference rejected, zero-test run rejected, learner hash unchanged")
