import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

TESTS=Path(__file__).resolve().parent; SCRIPTS=TESTS.parent/"scripts"
sys.path.insert(0,str(SCRIPTS));sys.path.insert(0,str(TESTS))
from vibe_protocol import read_json, sha256_bytes, canonical_inventory, utc_now, ProtocolError
from protocol_fixture_support import coverage_fixture


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
D=load("runner_delivery_fixture",TESTS/"delivery-ledger/test_delivery_protocol_20.py")
RUNNER=load("fresh_audit_runner",SCRIPTS/"run-acceptance-audit.py")


class AuditRunnerTests(unittest.TestCase):
    def setUp(self):
        self.case=D.DeliveryProtocol20Tests();self.case.setUp();self.root=self.case.root
        ledger=self.case.ledger()
        for item in [*ledger["acceptanceScenarios"],*ledger["qualityGates"]]: item.update(status="waived",decisionReference="docs/decisions/DEC-FIXTURE.json")
        self.case.save(ledger)
        self.case.exec_script("create-audit-request.py",str(self.root),"--expected-ledger-digest",self.case.ledger()["ledgerDigest"],"--auditor-context-id","new-process")
        self.request_path=self.root/self.case.ledger()["closureAudit"]["requestPath"]
    def tearDown(self): self.case.tearDown()
    def process_result(self,argv,**kwargs):
        self.assertEqual(["codex","exec","--ephemeral","--json"],argv[:4]);self.assertNotIn("resume",argv)
        request=read_json(self.request_path);app=read_json(self.root/"app-spec/app-spec.json")
        obligations=[{"id":i,"kind":"acceptance-scenario" if i.startswith("AC") else "managed-operation","scope":"repository","result":"gap","verificationSurfaces":["component-test"],"evidence":[]} for i in ("AC-001","Value:create")]
        obligations += [{"id":g["id"],"kind":"quality-gate","scope":g["category"],"result":"waived","verificationSurfaces":g["verificationSurfaces"],"evidence":[],"decisionReference":"docs/decisions/DEC-FIXTURE.json"} for g in app["qualityGates"]]
        now=utc_now();audit={"schemaVersion":"2.0","auditId":"AUDIT-RETURNED","auditRequest":{"path":self.request_path.relative_to(self.root).as_posix(),"requestId":request["requestId"],"sha256":sha256_bytes(self.request_path.read_bytes())},"auditorContext":{"contextId":"new-process","invocationKind":"fresh-context","implementationContextAvailable":False},"startedAt":now,"completedAt":now,"verdict":"GAPS","appSpecFingerprint":request["appSpecFingerprint"],"workspaceFingerprint":request["workspaceFingerprint"],"shadowInventory":canonical_inventory(app),"sourceCoverage":coverage_fixture(self.root/"app-spec",["AC-001"]),"obligations":obligations,"checks":[],"findings":["Missing behavior"],"completion":{"implementationComplete":False,"releaseReady":False}}
        output=Path(argv[argv.index("--output-last-message")+1]);output.write_text(json.dumps(audit),encoding="utf-8")
        return 0,b'{"type":"thread.started","thread_id":"host-session-123"}\n',b'',"completed"

    def test_launcher_records_host_event_and_validates_returned_audit(self):
        with patch.object(RUNNER,"execute_process",side_effect=self.process_result): RUNNER.run(self.root,self.request_path,"codex",10)
        launch=read_json(self.request_path.with_name("launch.json"));self.assertEqual("host-session-123",launch["threadId"])
        self.assertEqual("GAPS",read_json(self.request_path.with_name("audit.json"))["verdict"])
        with self.assertRaises(ProtocolError): RUNNER.run(self.root,self.request_path,"codex",10)

    def test_interrupted_process_leaves_failure_receipt_without_audit(self):
        with patch.object(RUNNER,"execute_process",return_value=(1,b'',b'timeout',"interrupted")):
            with self.assertRaises(ProtocolError): RUNNER.run(self.root,self.request_path,"codex",10)
        self.assertEqual("interrupted",read_json(self.request_path.with_name("launch.json"))["executionStatus"])
        self.assertFalse(self.request_path.with_name("audit.json").exists())


if __name__=="__main__":unittest.main()
