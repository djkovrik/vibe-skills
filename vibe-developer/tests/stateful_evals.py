"""Materialized two-process recovery eval; grading uses files and command events, never answer keywords."""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

PACKAGE=Path(__file__).resolve().parents[2]
SCRIPTS=PACKAGE/"vibe-developer"/"scripts"
sys.path.insert(0,str(SCRIPTS))
from vibe_protocol import read_json, compute_workspace_fingerprint, with_ledger_digest, sha256_bytes


def prepare(destination):
    destination.mkdir(parents=True,exist_ok=False)
    shutil.copytree(PACKAGE/"vibe-developer/tests/delivery-ledger/fixtures/app-spec",destination/"app-spec")
    for directory in ("src","tests","config","docs/assignments"): (destination/directory).mkdir(parents=True)
    (destination/"src/value.py").write_text("class ValueStore:\n    def save(self, value):\n        raise NotImplementedError\n\n    def read(self):\n        raise NotImplementedError\n",encoding="utf-8")
    (destination/"tests/verify_value.py").write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))\nfrom value import ValueStore\ns=ValueStore()\ns.save(42)\nassert s.read()==42\ns.save(7)\nassert s.read()==7\nprint('observable value verified')\n",encoding="utf-8")
    (destination/"config/user-owned.txt").write_text("Keep this user's configuration exactly.\n",encoding="utf-8")
    (destination/".gitignore").write_text("__pycache__/\n",encoding="utf-8")
    request=("Implement the small protocol test fixture ValueStore: save(value) must replace the in-memory value and read() must return the last saved value. "
        "Keep class and method names. Only src/value.py may change. The verification contract is tests/verify_value.py; preserve its exact assertions. "
        "Preserve config/user-owned.txt. This is a bounded protocol fixture, not a request to scaffold a KMP application or change its AppSpec. "
        f"Use Python {sys.executable}. Shared recovery/checkpoint/receipt scripts are at {SCRIPTS}. "
        "After verification, checkpoint with phase implementing, status implemented-unverified and no pending check; final app completion is outside this assignment.")
    (destination/"docs/assignments/ASSIGN-EVAL.md").write_text(request,encoding="utf-8")
    (destination/"docs/coverage.json").write_text(json.dumps({"coveredObligations":[{"obligationId":"AC-001","surfaces":["component-test"]}]}),encoding="utf-8")
    for args in (["init","-q"],["config","user.email","fixture@example.test"],["config","user.name","Fixture"],["add","."],["commit","-qm","materialized fixture"]):
        subprocess.run(["git","-C",str(destination),*args],check=True,capture_output=True)
    subprocess.run([sys.executable,str(SCRIPTS/"init-delivery-ledger.py"),str(destination/"app-spec"),"--project-root",str(destination)],check=True,capture_output=True)
    ledger=read_json(destination/".vibe/delivery-ledger.json")
    subprocess.run([sys.executable,str(SCRIPTS/"checkpoint-delivery.py"),str(destination),"--expected-ledger-digest",ledger["ledgerDigest"],"--phase","implementing","--active-ac","AC-001","--owner","evaluation","--file-boundary","src/value.py","--pending-check","Run tests/verify_value.py","--required-read","docs/assignments/ASSIGN-EVAL.md","--next-action","Implement save(value), then checkpoint before completing read()."],check=True,capture_output=True)
    return {"repository":str(destination),"protected":{name:sha256_bytes((destination/name).read_bytes()) for name in ("config/user-owned.txt","tests/verify_value.py","docs/assignments/ASSIGN-EVAL.md")}}


def grade(root, oracle, phase, events=None):
    errors=[]
    for name,digest in oracle["protected"].items():
        if sha256_bytes((root/name).read_bytes())!=digest: errors.append(f"protected file changed: {name}")
    ledger=read_json(root/".vibe/delivery-ledger.json"); ac=ledger["acceptanceScenarios"][0]
    if ledger["execution"].get("phase")=="complete": errors.append("fixture incorrectly claimed final completion")
    if phase==1:
        result=subprocess.run([sys.executable,"-B","-c","from src.value import ValueStore;s=ValueStore();s.save(42)"],cwd=root,capture_output=True)
        if result.returncode: errors.append("save behavior still incomplete")
        if not ac.get("pendingChecks") or not ledger["execution"].get("nextAction"): errors.append("unfinished work was not checkpointed")
    else:
        result=subprocess.run([sys.executable,"-B","tests/verify_value.py"],cwd=root,capture_output=True)
        if result.returncode: errors.append("observable value behavior failed")
        if ac.get("pendingChecks"): errors.append("completed check remains pending")
        fingerprint=compute_workspace_fingerprint(root)
        receipts=[read_json(p) for p in (root/".vibe/receipts").glob("*.json")]
        if not any(r.get("exitCode")==0 and r.get("executionStatus")=="completed" and r.get("workspaceFingerprint")==fingerprint and any("verify_value.py" in arg for arg in r.get("argv",[])) for r in receipts): errors.append("no real current verification receipt")
    if events is not None:
        event_items=[json.loads(line) for line in events.read_text(encoding="utf-8").splitlines() if line.strip()]
        command_events=[e for e in event_items if e.get("type")=="item.completed" and e.get("item",{}).get("type")=="command_execution"]
        if not any("resume-delivery.py" in e["item"].get("command","") for e in command_events): errors.append("no completed resume command in host events")
    return errors


def run_agents(output, executable, timeout):
    root=output/"project"; oracle=prepare(root); (output/"oracle.json").write_text(json.dumps(oracle),encoding="utf-8")
    for phase in (1,2):
        prompt=(f"Use $vibe-developer at {PACKAGE/'vibe-developer/SKILL.md'} for the bounded fixture assignment in docs/assignments/ASSIGN-EVAL.md. You are the sole delivery orchestrator for this fixture and may update its ledger with the supplied scripts. "
            + ("Implement only save(value) in this pass; preserve read() unfinished and checkpoint the remaining work before returning." if phase==1 else "Continue the interrupted assignment using repository state. No earlier conversation is available. Finish its observable behavior, run targeted verification with a receipt, and checkpoint the result."))
        events=output/f"phase-{phase}.jsonl"
        process=subprocess.run([executable,"exec","--ephemeral","--json","--sandbox","workspace-write","-C",str(root),"-"],input=prompt,text=True,encoding="utf-8",capture_output=True,timeout=timeout)
        events.write_text(process.stdout,encoding="utf-8"); (output/f"phase-{phase}.stderr.log").write_text(process.stderr,encoding="utf-8")
        errors=grade(root,oracle,phase,events) if process.returncode==0 else [f"agent exit {process.returncode}"]
        (output/f"phase-{phase}-grade.json").write_text(json.dumps({"errors":errors}),encoding="utf-8")
        if errors: raise RuntimeError(f"phase {phase}: {errors}")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=PACKAGE/".tooling"/"stateful-agent-evals"/uuid.uuid4().hex)
    parser.add_argument("--prepare-only",action="store_true"); parser.add_argument("--timeout",type=int,default=600)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    if args.prepare_only:
        result=prepare(args.output/"project"); (args.output/"oracle.json").write_text(json.dumps(result),encoding="utf-8"); print(json.dumps(result))
    else:
        executable=shutil.which("codex")
        if not executable: raise SystemExit("Codex CLI required for stateful agent evals")
        run_agents(args.output.resolve(),executable,args.timeout); print("STATEFUL AGENT EVALS PASSED")
