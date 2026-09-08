"""Behavioral and complexity regressions for the BagCue throughput changes."""
import copy
import json
import subprocess
import time
import unittest
from unittest.mock import patch
import test_flow_packages as flow
from test_flow_packages import load, SCRIPTS
from validation_context import ValidationContext
from vibe_protocol import ProtocolError, compute_workspace_fingerprint, fingerprint_equal, read_json, sha256_bytes
from evidence_registry import register, reconcile, check_anchor
from check_jobs import bind_completed, bind_receipt
from check_queue import combine


class OptimizationTests(unittest.TestCase):
    setUp = flow.FlowPackageTests.setUp
    tearDown = flow.FlowPackageTests.tearDown
    run_request = flow.FlowPackageTests.run_request
    package = flow.FlowPackageTests.package
    scope = flow.FlowPackageTests.scope
    assign = flow.FlowPackageTests.assign
    def test_receipt_bind_preserves_checkpoint_and_is_idempotent(self):
        ref = self.fixture.receipt('bind', 0, '2026-09-04T10:01:00Z', ['component-test'])
        old = copy.deepcopy(self.fixture.ledger()['execution']['checkpoint'])
        (self.root/'src/App.kt').write_text('concurrent source edit')
        ledger = self.fixture.ledger()
        bind_receipt(self.root, ledger, ref)
        once = copy.deepcopy(ledger['acceptanceScenarios'])
        bind_receipt(self.root, ledger, ref)
        self.assertEqual(once, ledger['acceptanceScenarios'])
        self.assertEqual(old, ledger['execution']['checkpoint'])
        receipt = read_json(self.root/ref); receipt['exitCode'] = 1
        (self.root/ref).write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ProtocolError, 'hash changed'): bind_receipt(self.root, ledger, ref)

    def test_bind_timeout_keeps_receipt_and_only_retries_registration(self):
        ref = self.fixture.receipt('timeout-bind', 0, '2026-09-04T10:01:00Z', ['component-test'])
        original = (self.root/ref).read_bytes()
        with patch('check_jobs.subprocess.run', side_effect=subprocess.TimeoutExpired('bind', .01)):
            self.assertEqual('binding-pending', bind_completed(self.root, ref, 'job', .01))
        self.assertEqual(original, (self.root/ref).read_bytes())
        self.assertEqual('bound', bind_completed(self.root, ref, 'job'))
        self.assertEqual(original, (self.root/ref).read_bytes())
        self.assertEqual(1, len(list((self.root/'.vibe/receipts').glob('*.json'))))

    def test_150_obligations_500_receipts_fingerprint_scope_once(self):
        self.package(); self.scope()
        context = ValidationContext(self.root)
        fp = context.scope('component')
        workspace = context.workspace
        receipts = {}
        for n in range(500):
            receipts[str(n)] = {'schemaVersion':'2.0', 'receiptId':str(n), 'kind':'targeted',
                'inputScopeId':'component', 'inputFingerprint':fp, 'startInputFingerprint':fp,
                'workspaceFingerprint':workspace, 'startWorkspaceFingerprint':workspace,
                'completedAt':'2026-09-04T10:00:00Z', 'executionStatus':'completed', 'exitCode':0,
                'coveredObligations':[{'obligationId':f'AC-{i}', 'surfaces':['component-test']} for i in range(150)]}
        directory = self.root / '.vibe/receipts'
        directory.mkdir(exist_ok=True)
        for name, receipt in receipts.items():
            (directory / f'{name}.json').write_text(json.dumps(receipt), encoding='utf-8')
        context = ValidationContext(self.root)
        from scoped_evidence import input_fingerprint
        with patch('validation_context.input_fingerprint', wraps=input_fingerprint) as capture, patch('validation_context.read_json', wraps=read_json) as reads:
            started = time.perf_counter()
            for i in range(150): self.assertFalse(context.latest[(f'AC-{i}', 'component-test')][0][1])
            self.assertEqual(1, capture.call_count)
            self.assertEqual(500, sum(1 for call in reads.call_args_list if call.args[0].parent == directory))
            self.assertLess(time.perf_counter()-started, 10)

    def test_evidence_exact_coverage_and_replacement_preserve_history(self):
        ledger = self.fixture.ledger()
        duplicate = copy.deepcopy(ledger['acceptanceScenarios'][0]); duplicate['id'] = 'AC-002'
        ledger['acceptanceScenarios'].append(duplicate)
        row = {'path':'tests/AppTest.kt','testName':'savedValueIsObservable','surface':'component-test',
               'coverage':[{'obligationId':'AC-001','surface':'component-test'}]}
        eid = register(self.root, ledger, row, 'testEvidence', ['AC-001','AC-002'], 'original-handoff')
        self.assertEqual([], duplicate['testEvidence'])
        self.assertEqual(1, len(ledger['evidence']))
        (self.root/'tests/AppTest.kt').write_text('fun renamedSaveTest() = Unit')
        replacement = {**row,'testName':'renamedSaveTest','kind':'testEvidence'}
        reconcile(self.root, ledger, {'oldEvidenceIds':[eid],'obligationIds':['AC-001'],
            'newEvidence':[replacement], 'reason':'test renamed','inspectionNote':'same observable assertion'})
        self.assertIn(eid, ledger['evidence'])
        self.assertNotIn(eid, ledger['acceptanceScenarios'][0]['testEvidence'])
        self.assertEqual(1, len(ledger['evidenceHistory']))

    def test_xml_anchor_ignores_prefix_and_format(self):
        path = self.root/'src/AndroidManifest.xml'
        path.write_text('<manifest xmlns:a="http://schemas.android.com/apk/res/android"><uses-permission a:name="p" /></manifest>')
        row = {'path':'src/AndroidManifest.xml','anchor':{'kind':'xml','element':'uses-permission',
            'attributes':{'{http://schemas.android.com/apk/res/android}name':'p'}}}
        check_anchor(self.root, row)
        row['anchor']['attributes']['{http://schemas.android.com/apk/res/android}name'] = 'missing'
        with self.assertRaisesRegex(ProtocolError, 'XML anchor'): check_anchor(self.root, row)

    def test_independent_packages_can_overlap_in_time_not_writers(self):
        self.package()
        ledger = self.fixture.ledger(); ac = copy.deepcopy(ledger['acceptanceScenarios'][0])
        ac.update(id='AC-002', status='not-started'); ledger['acceptanceScenarios'].append(ac); self.fixture.save(ledger)
        self.run_request(action='package', packageId='independent', owner='other', acceptanceScenarioIds=['AC-002'],
            fileBoundaries=['config/**'], integrationGoal='independent flow')
        self.assertEqual(['catalog','independent'], self.fixture.ledger()['execution']['activePackageIds'])
        self.assign('first', ['src/**'])
        with self.assertRaisesRegex(ProtocolError, 'overlaps'): self.assign('second', ['src/**'])

    def test_content_identity_survives_commit_and_detects_source_change(self):
        before = compute_workspace_fingerprint(self.root)
        self.fixture.git('commit','--allow-empty','-m','provenance')
        self.assertTrue(fingerprint_equal(before, compute_workspace_fingerprint(self.root)))
        (self.root/'src/App.kt').write_text('changed')
        self.assertFalse(fingerprint_equal(before, compute_workspace_fingerprint(self.root)))

    def test_module_scope_includes_transitive_contracts_not_unrelated_ui(self):
        from module_scope import resolve_modules
        graph = {':feature': {'directory':'shared/feature', 'dependencies':[':domain']},
                 ':domain': {'directory':'shared/domain', 'dependencies':[]},
                 ':ui': {'directory':'shared/compose', 'dependencies':[':domain']}}
        patterns, modules = resolve_modules([':feature'], graph)
        self.assertEqual(['shared/domain/**', 'shared/feature/**'], patterns)
        with self.assertRaisesRegex(ProtocolError, 'unknown module'): resolve_modules([':missing'], graph)

    def test_ready_check_batch_preserves_inputs_and_coverage(self):
        a = {'runner':'gradle','kind':'targeted','inputScopeId':'scope','checkId':'a',
             'tasks':[':domain:test'], 'coveredObligations':[{'obligationId':'AC-001','surfaces':['component-test']}]}
        b = {**a, 'checkId':'b','tasks':[':component:test']}
        merged = combine([a,b])
        self.assertEqual([':domain:test', ':component:test'], merged['tasks'])
        self.assertEqual(['a','b'], merged['sourceCheckIds'])
        with self.assertRaisesRegex(ProtocolError, 'compatible'): combine([a,{**b,'inputScopeId':'different'}])

    def test_smoke_rejects_zero_and_missing_runtime_output(self):
        smoke = load('optimization_smoke', SCRIPTS/'validate-render-smoke.py')
        with self.assertRaisesRegex(ProtocolError, 'zero'): smoke.validate(self.root, {'previewCount':0})
        data = {'previewCount':3, 'startedAt':'2026-01-01T00:00:00Z',
            'cases':[{'id':v,'variant':v,'snapshotPath':f'{v}.png'} for v in ('light','dark','ru-200')]}
        with self.assertRaisesRegex(ProtocolError, 'resource class'): smoke.validate(self.root, data)

    def test_timing_reports_union_not_sum(self):
        timing = load('optimization_timing', SCRIPTS/'delivery-timing.py')
        self.assertEqual(15, timing.union_seconds([(0,10),(5,15)]))

    def test_technical_path_change_preserves_unrelated_evidence(self):
        from protocol_fixture_support import decision_fixture
        from vibe_protocol import compute_app_spec_fingerprint
        decision = decision_fixture(self.root, ['AppSpec'], kind='spec-change', name='DEC-PATH')
        path = 'shared/compose/src/commonMain/composeResources/drawable/icon.xml'
        (self.root/path).parent.mkdir(parents=True); (self.root/path).write_text('<vector/>')
        old = read_json(self.root/'app-spec/app-spec.json')
        old['assetRequirements'] = {'items':[{'id':'ASSET-001','variants':[{'path':'composeApp/icon.xml'}]}]}
        (self.root/'app-spec/app-spec.json').write_text(json.dumps(old))
        ledger = self.fixture.ledger(); ledger['appSpecDocument'] = old
        ledger['appSpec']['fingerprint'] = compute_app_spec_fingerprint(self.root/'app-spec')
        ledger['workspaceFingerprint'] = compute_workspace_fingerprint(self.root)
        ledger['acceptanceScenarios'][0]['status'] = 'verified'
        new = copy.deepcopy(old); new['assetRequirements']['items'][0]['variants'][0]['path'] = path
        (self.root/'app-spec/app-spec.json').write_text(json.dumps(new))
        module = load('optimization_reconcile', SCRIPTS/'reconcile-spec.py')
        with patch('vibe_protocol.validate_app_spec', return_value=(new, [], [])):
            module.reconcile(ledger, self.root, self.root/'app-spec', decision, 'technical-paths')
        self.assertEqual('verified', ledger['acceptanceScenarios'][0]['status'])
        self.assertEqual(1, len(ledger['technicalReconciliations']))
        self.assertTrue((self.root/ledger['technicalReconciliations'][0]['historyRef']).exists())

    def test_removing_live_evidence_reopens_verification(self):
        ledger = self.fixture.ledger(); item = ledger['acceptanceScenarios'][0]
        eid = register(self.root, ledger, {'path':'tests/AppTest.kt','testName':'savedValueIsObservable','surface':'component-test'},
                       'testEvidence', ['AC-001'], 'handoff')
        item['status'] = 'verified'
        reconcile(self.root, ledger, {'oldEvidenceIds':[eid],'obligationIds':['AC-001'],
            'newEvidence':[], 'reason':'test removed','inspectionNote':'coverage must be restored'})
        self.assertEqual('implemented-unverified', item['status'])


if __name__ == '__main__': unittest.main()
