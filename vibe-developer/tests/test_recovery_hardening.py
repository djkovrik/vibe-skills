from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent / "scripts"
sys.path.insert(0, str(SCRIPTS)); sys.path.insert(0, str(TESTS))
from vibe_protocol import (read_json, sha256_bytes, compute_workspace_fingerprint, decision_valid,
    with_ledger_digest, utc_now)
from protocol_fixture_support import decision_fixture, launch_fixture, coverage_fixture


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module; spec.loader.exec_module(module); return module


D=load("hardening_delivery_fixture",TESTS/"delivery-ledger"/"test_delivery_protocol_20.py")
CHECK=load("hardening_check",SCRIPTS/"run-check.py")
RECONCILE=load("hardening_reconcile",SCRIPTS/"reconcile-spec.py")


class RecoveryHardeningTests(unittest.TestCase):
    def setUp(self):
        self.case=D.DeliveryProtocol20Tests(); self.case.setUp(); self.root=self.case.root
    def tearDown(self): self.case.tearDown()
    def resume(self):
        return json.loads(self.case.exec_script("resume-delivery.py",str(self.root),check=False).stdout)
    def checkpoint(self,*args):
        return self.case.exec_script("checkpoint-delivery.py",str(self.root),"--expected-ledger-digest",self.case.ledger()["ledgerDigest"],*args,check=False)
    def close_local(self):
        ledger=self.case.ledger()
        for item in [*ledger["acceptanceScenarios"],*ledger["qualityGates"]]:
            item.update(status="waived",decisionReference="docs/decisions/DEC-FIXTURE.json",pendingChecks=[],blockers=[])
            item.pop("blocker",None)
        self.case.save(ledger)
    def request(self,context="fresh-1",request_id=None):
        args=["--expected-ledger-digest",self.case.ledger()["ledgerDigest"],"--auditor-context-id",context]
        if request_id: args += ["--request-id",request_id]
        return self.case.exec_script("create-audit-request.py",str(self.root),*args,check=False)

    def test_resume_never_closes_unstarted_or_failed_or_missing_audit(self):
        self.assertFalse(self.resume()["completionEligible"])
        self.case.start(); ref=self.case.receipt("failed",1,"2026-09-04T10:02:00Z",["component-test"])
        self.case.verified_ac([ref]); brief=self.resume()
        self.assertFalse(brief["completionEligible"]); self.assertTrue(brief["evidenceIssues"])
        ledger=self.case.ledger(); ledger["closureAudit"]={"requestPath":".vibe/audits/AUDIT-REQUEST-missing/request.json"}; self.case.save(ledger)
        self.assertFalse(self.resume()["completionEligible"])

    def test_resume_recovers_saved_blockers_checks_owner_boundaries(self):
        self.case.start(); ledger=self.case.ledger(); item=ledger["acceptanceScenarios"][0]
        item.update(blockers=["Need DEC-42"],pendingChecks=["rerun exact regression"])
        ledger["qualityGates"][0]["blocker"]={"reason":"tool unavailable"}; self.case.save(ledger)
        brief=self.resume()
        self.assertEqual("test",brief["activeSlice"]["owner"])
        self.assertEqual(["src/**","tests/**"],brief["activeSlice"]["fileBoundaries"])
        self.assertIn("DEC-42",json.dumps(brief["blockers"]))
        self.assertIn("exact regression",json.dumps(brief["pendingChecks"]))
        self.assertFalse(brief["safeToContinue"])

    def test_new_success_can_supersede_pre_hardening_receipt_without_deleting_it(self):
        old=self.case.receipt("legacy",0,"2026-09-04T10:02:00Z",["component-test"])
        path=self.root/old; data=read_json(path); data.pop("executionStatus");data.pop("startWorkspaceFingerprint");path.write_text(json.dumps(data))
        original=path.read_bytes();self.case.verified_ac([old])
        self.assertTrue(any("latest current receipt" in e for e in D.VALIDATOR.validate_ledger(self.root,self.case.ledger_path).errors))
        new=self.case.receipt("current",0,"2026-09-04T10:03:00Z",["component-test"]);self.case.verified_ac([old,new])
        self.assertFalse(any("latest current receipt" in e for e in D.VALIDATOR.validate_ledger(self.root,self.case.ledger_path).errors))
        self.assertEqual(original,path.read_bytes())

    def test_gate_only_work_recovers_expected_drift(self):
        result=self.checkpoint("--phase","implementing","--active-gate","QG-001","--owner","architect","--file-boundary","config/**","--next-action","Finish quality config")
        self.assertEqual(0,result.returncode,result.stderr)
        (self.root/"config"/"quality.yml").write_text("changed\n")
        brief=self.resume(); self.assertEqual("expected-drift",brief["driftClassification"])
        self.assertEqual("QG-001",brief["activeSlice"]["id"])

    def test_repeated_audit_attempt_preserves_previous_bytes(self):
        self.close_local(); first=self.request(); self.assertEqual(0,first.returncode,first.stderr)
        binding=self.case.ledger()["closureAudit"]; path=self.root/binding["requestPath"]; before=path.read_bytes()
        second=self.request("fresh-2"); self.assertEqual(0,second.returncode,second.stderr)
        self.assertEqual(before,path.read_bytes()); self.assertNotEqual(binding,self.case.ledger()["closureAudit"])
        self.assertEqual(binding,self.case.ledger()["auditHistory"][0])

    def test_orphan_request_rebinds_after_interrupted_ledger_write(self):
        self.close_local(); original=self.case.ledger(); self.assertEqual(0,self.request(request_id="AUDIT-REQUEST-orphan").returncode)
        binding=self.case.ledger()["closureAudit"]; self.case.save(original)
        self.assertIn(binding["requestPath"],self.resume()["orphanAuditRequests"])
        result=self.request(request_id="AUDIT-REQUEST-orphan"); self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual(binding,self.case.ledger()["closureAudit"])

    def test_scoped_waiver_rejects_source_wrong_scope_tamper_and_supersession(self):
        self.assertFalse(decision_valid(self.root,"src/App.kt","AC-001"))
        reference="docs/decisions/DEC-FIXTURE.json"
        self.assertTrue(decision_valid(self.root,reference,"AC-001"))
        self.assertFalse(decision_valid(self.root,reference,"AC-999"))
        replacement=decision_fixture(self.root,["AC-001"],name="DEC-NEW")
        path=self.root/replacement; value=read_json(path); value["supersedes"]=["DEC-FIXTURE"]; path.write_text(json.dumps(value))
        self.assertFalse(decision_valid(self.root,reference,"AC-001"))
        (self.root/"docs/decisions/DEC-NEW-user.txt").write_text("tampered approval")
        self.assertFalse(decision_valid(self.root,replacement,"AC-001"))

    def test_spec_revision_preserves_history_and_reopens_all_current_work(self):
        self.close_local(); old=self.case.ledger()
        decision=decision_fixture(self.root,["AppSpec"],kind="spec-change",name="DEC-REVISION")
        with (self.root/"app-spec/product.md").open("a") as stream: stream.write("\nApproved new requirement detail.\n")
        result=self.case.exec_script("reconcile-spec.py",str(self.root),"--app-spec","app-spec","--decision-reference",decision,"--expected-ledger-digest",old["ledgerDigest"],check=False)
        self.assertEqual(0,result.returncode,result.stderr)
        ledger=self.case.ledger(); history=read_json(self.root/ledger["specHistory"][0]["path"])
        self.assertEqual(old,history); self.assertEqual("not-started",ledger["acceptanceScenarios"][0]["status"])
        self.assertEqual("clean",self.resume()["driftClassification"])
        self.assertFalse(self.resume()["completionEligible"])

    def test_commit_requires_explicit_reconciliation(self):
        self.case.start(); self.case.git("commit","--allow-empty","-m","checkpoint commit")
        self.assertEqual("unexpected-drift",self.resume()["driftClassification"])
        refused=self.checkpoint("--phase","reconciling","--next-action","Inspect commit")
        self.assertNotEqual(0,refused.returncode)
        accepted=self.checkpoint("--phase","reconciling","--next-action","Rerun verification","--reconcile-drift","Reviewed own checkpoint commit")
        self.assertEqual(0,accepted.returncode,accepted.stderr)

    def test_concurrent_writers_cannot_lose_an_update(self):
        digest=self.case.ledger()["ledgerDigest"]; ledger_path=str(self.case.ledger_path)
        code="import sys,time;sys.path.insert(0,sys.argv[1]);from pathlib import Path;from vibe_protocol import update_ledger_atomic;update_ledger_atomic(Path(sys.argv[2]),sys.argv[3],lambda d:(time.sleep(.3),d.update(updatedAt=sys.argv[4])))"
        args=[sys.executable,"-B","-c",code,str(SCRIPTS),ledger_path,digest]
        first=subprocess.Popen([*args,"writer-one"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        second=subprocess.Popen([*args,"writer-two"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        outputs=[first.communicate(timeout=20),second.communicate(timeout=20)]
        self.assertEqual([0,1],sorted([first.returncode,second.returncode]),outputs)

    def test_real_check_records_timeout_and_workspace_mutation(self):
        coverage=[{"obligationId":"AC-001","surfaces":["component-test"]}]
        _,success=CHECK.run_check(self.root,[sys.executable,"-B","-c","assert 2+2 == 4"],coverage)
        self.assertEqual("completed",success["executionStatus"]); self.assertEqual(0,success["exitCode"])
        _,timeout=CHECK.run_check(self.root,[sys.executable,"-B","-c","import time;time.sleep(5)"],coverage,timeout=.1)
        self.assertEqual("interrupted",timeout["executionStatus"])
        _,changed=CHECK.run_check(self.root,[sys.executable,"-B","-c","from pathlib import Path;Path('src/new.txt').write_text('changed')"],coverage)
        self.assertEqual(0,changed["exitCode"]); self.assertEqual("workspace-changed",changed["executionStatus"])

    def test_specialist_recovers_without_conversation(self):
        result=self.case.exec_script("specialist-state.py","checkpoint",str(self.root),"--assignment-id","ASSIGN-1","--owner","domain","--obligation-id","AC-001","--file-boundary","src/**","--required-read","app-spec/product.md","--pending-check","component regression","--next-action","Finish AC-001")
        self.assertEqual(0,result.returncode)
        (self.root/"src/App.kt").write_text("class AppComponent { fun saveValue() = Unit } // partial work\n")
        result=self.case.exec_script("specialist-state.py","resume",str(self.root),"--assignment-id","ASSIGN-1")
        brief=json.loads(result.stdout); self.assertEqual(["component regression"],brief["packet"]["pendingChecks"])
        self.assertIn("src/App.kt",brief["driftPaths"]); self.assertTrue(brief["safeToContinue"])

    def test_gaps_fix_new_pass_then_final_and_reject_wrong_order(self):
        self.close_local()
        # The first audit identifies a behavior gap despite local waiver claims.
        self.assertEqual(0,self.request("first-context").returncode)
        first_binding=self.case.ledger()["closureAudit"]; first_request=self.root/first_binding["requestPath"]
        first_audit=first_request.with_name("audit.json")
        first_audit.write_text(json.dumps({"schemaVersion":"2.0","verdict":"GAPS","findings":["save path incomplete"]}))
        first_bytes=first_audit.read_bytes()
        start=self.checkpoint("--phase","implementing","--active-ac","AC-001","--owner","fixer","--file-boundary","src/**","--next-action","Repair the save path")
        self.assertEqual(0,start.returncode,start.stderr)
        (self.root/"src/App.kt").write_text("class AppComponent { var value = 0; fun saveValue(v: Int) { value = v } }\n")
        cp=self.checkpoint("--phase","implementing","--active-ac","AC-001","--next-action","Verify save path")
        self.assertEqual(0,cp.returncode,cp.stderr)
        coverage=[{"obligationId":"AC-001","surfaces":["component-test"]}]
        path,receipt=CHECK.run_check(self.root,[sys.executable,"-B","-c","from pathlib import Path;assert 'value = v' in Path('src/App.kt').read_text()"],coverage)
        self.case.verified_ac([path.relative_to(self.root).as_posix()])
        self.assertEqual(0,self.request("second-context").returncode)
        binding=self.case.ledger()["closureAudit"]; request_path=self.root/binding["requestPath"]; request=read_json(request_path)
        audit_started=utc_now()
        _,audit_receipt=CHECK.run_check(self.root,[sys.executable,"-B","-c","from pathlib import Path;assert 'value = v' in Path('src/App.kt').read_text()"],coverage)
        app=read_json(self.root/"app-spec/app-spec.json")
        obligations=[{"id":item_id,"result":"verified","verificationSurfaces":["component-test"],"evidence":[{"path":"src/App.kt","symbol":"saveValue","surface":"component-test"}]} for item_id in ("AC-001","Value:create")]
        obligations += [{"id":g["id"],"result":"waived","verificationSurfaces":g["verificationSurfaces"],"decisionReference":"docs/decisions/DEC-FIXTURE.json","evidence":[]} for g in app["qualityGates"]]
        for obligation in obligations:
            obligation["kind"] = "quality-gate" if obligation["id"].startswith("QG-") else "managed-operation" if ":" in obligation["id"] else "acceptance-scenario"
            obligation["scope"] = next((g["category"] for g in app["qualityGates"] if g["id"]==obligation["id"]),"repository")
        check={k:audit_receipt[k] for k in ("argv","startedAt","completedAt","exitCode","executionStatus","startWorkspaceFingerprint","workspaceFingerprint")}
        check.update(checkId="CHECK-1",coverage=[{"obligationId":i,"surface":"component-test"} for i in ("AC-001","Value:create")])
        from vibe_protocol import canonical_inventory
        audit={"schemaVersion":"2.0","auditId":"AUDIT-PASS","auditRequest":{"path":binding["requestPath"],"requestId":request["requestId"],"sha256":sha256_bytes(request_path.read_bytes())},
            "auditorContext":{"contextId":request["requiredAuditorContextId"],"invocationKind":"fresh-context","implementationContextAvailable":False},
            "startedAt":audit_started,"completedAt":utc_now(),"verdict":"PASS","appSpecFingerprint":request["appSpecFingerprint"],"workspaceFingerprint":request["workspaceFingerprint"],
            "shadowInventory":canonical_inventory(app),"sourceCoverage":coverage_fixture(self.root/"app-spec",["AC-001"]),"obligations":obligations,"checks":[check],"findings":[],"completion":{"implementationComplete":True,"releaseReady":True}}
        audit_path=request_path.with_name("audit.json"); audit_path.write_text(json.dumps(audit))
        launch_fixture(self.root,request_path,request,completed=utc_now())
        final_path,final_receipt=CHECK.run_check(self.root,[sys.executable,"-B","-c","from pathlib import Path;assert 'value = v' in Path('src/App.kt').read_text()"],coverage,kind="final")
        ledger=self.case.ledger(); ledger["finalReceiptRef"]=final_path.relative_to(self.root).as_posix(); ledger["execution"]["phase"]="final-verification"; self.case.save(ledger)
        self.case.run_report("render-delivery-report.py",str(self.root))
        audit_renderer=load("hardening_audit_renderer",SCRIPTS.parents[1]/"vibe-acceptance-auditor/scripts/render-closure-audit.py")
        (self.root/"docs/closure-audit.generated.md").write_text(audit_renderer.render(audit),encoding="utf-8")
        result=D.VALIDATOR.validate_ledger(self.root,self.case.ledger_path)
        self.assertTrue(result.implementation_complete,result.errors); self.assertTrue(self.resume()["completionEligible"])
        self.assertEqual(first_bytes,first_audit.read_bytes())
        final_receipt["startedAt"]=request["createdAt"]; final_path.write_text(json.dumps(final_receipt))
        result=D.VALIDATOR.validate_ledger(self.root,self.case.ledger_path)
        self.assertFalse(result.implementation_complete); self.assertTrue(any("after audit completion" in e for e in result.errors))


if __name__ == "__main__": unittest.main()
