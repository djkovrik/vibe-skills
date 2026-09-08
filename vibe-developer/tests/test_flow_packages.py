"""Executable regressions for package coordination and scoped evidence."""
import importlib.util
import json
import sys
import unittest
import shutil
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS)); sys.path.insert(0, str(TESTS))
from scoped_evidence import input_fingerprint, registered_scope, receipt_current, receipt_stable
from vibe_protocol import compute_workspace_fingerprint, ProtocolError, read_json, sha256_bytes


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    return module


D = load('flow_fixture', TESTS/'delivery-ledger/test_delivery_protocol_20.py')
WORK = load('delivery_work', SCRIPTS/'delivery-work.py')
CHECK = load('flow_check', SCRIPTS/'run-check.py')


class FlowPackageTests(unittest.TestCase):
    def setUp(self):
        self.fixture = D.DeliveryProtocol20Tests(); self.fixture.setUp(); self.root = self.fixture.root

    def tearDown(self): self.fixture.tearDown()

    def run_request(self, **request):
        request['_requestRef'] = {'path': 'docs/assignment.md', 'sha256': sha256_bytes((self.root/'docs/assignment.md').read_bytes())}
        return WORK.run(self.root, request)

    def package(self):
        return self.run_request(action='package', packageId='catalog', owner='root', acceptanceScenarioIds=['AC-001'],
            fileBoundaries=['src/**', 'tests/**', 'config/**'], integrationGoal='Launch app, save value, reopen persisted value')

    def scope(self):
        self.run_request(action='scope', scopeId='component', patterns=['src/**', 'tests/**'],
            dependencyRationale='All fixture production and test dependencies; config is unrelated', toolchainIdentity='Python fixture v1')

    def assign(self, aid, files):
        self.run_request(action='assign', assignmentId=aid, owner='test', allowedFiles=files,
            acceptanceScenarioIds=['AC-001'], qualityGateIds=[])

    def test_unscoped_targeted_evidence_is_rejected_at_all_boundaries(self):
        self.package(); self.scope()
        with self.assertRaisesRegex(ProtocolError, 'require inputScopeId'):
            CHECK.run_check(self.root, [sys.executable, '-c', 'pass'], [])
        ref = self.fixture.receipt('old-targeted', 0, '2026-09-04T10:02:00Z', ['component-test'], kind='targeted')
        receipt = read_json(self.root/ref)
        self.assertFalse(receipt_current(self.root, receipt, compute_workspace_fingerprint(self.root)))
        self.assertFalse(receipt_stable(receipt))
        before = self.fixture.ledger_path.read_bytes()
        with self.assertRaisesRegex(ProtocolError, 'unsupported targeted receipt'):
            self.run_request(action='bind', receiptRef=ref)
        self.assertEqual(before, self.fixture.ledger_path.read_bytes())
        # Even stale old-format receipts are format errors, not reusable history.
        receipt['workspaceFingerprint']['digest'] = '0'*64
        (self.root/ref).write_text(json.dumps(receipt))
        result = D.VALIDATOR.ValidationResult()
        D.VALIDATOR.load_receipts(self.root, {ref}, compute_workspace_fingerprint(self.root), result)
        self.assertTrue(any('unsupported targeted receipt' in e for e in result.errors))

    def test_global_and_mixed_handoff_formats_are_rejected(self):
        self.package(); self.assign('source', ['src/**'])
        result = self.run_request(action='handoff', assignmentId='source')
        current = read_json(self.root/result['handoffRef'])
        validator = load('current_only_handoff', SCRIPTS/'ingest-handoff.py')
        for data in ({k:v for k,v in current.items() if k!='evidenceMode'},
                     {**current, 'baseWorkspaceFingerprint':compute_workspace_fingerprint(self.root)}):
            errors = validator.validate_handoff(data, self.root, compute_workspace_fingerprint(self.root))
            self.assertTrue(any('unsupported hand-off format' in e for e in errors))

    def test_nonoverlapping_handoffs_survive_other_assignment_edits(self):
        self.package(); self.assign('source', ['src/**']); self.assign('tests', ['tests/**'])
        (self.root/'src/App.kt').write_text('class AppComponent { fun saveValue() = 1 }')
        result = self.run_request(action='handoff', assignmentId='source', productionEvidence=[{'path':'src/App.kt','surface':'public-contract'}])
        original = (self.root/result['handoffRef']).read_bytes()
        (self.root/'tests/AppTest.kt').write_text('fun savedValueIsObservable() = 1')
        self.run_request(action='ingest', handoffRef=result['handoffRef'], inspectionNote='Reviewed source delta')
        self.assertEqual(original, (self.root/result['handoffRef']).read_bytes())
        item = self.fixture.ledger()['acceptanceScenarios'][0]
        self.assertEqual(['src/App.kt'], item['changedFiles'])
        self.assertEqual('in-progress', item['status'])  # The second owner has not returned yet.

    def test_owned_change_after_handoff_rejected_and_overlap_rejected(self):
        self.package(); self.assign('source', ['src/**'])
        with self.assertRaisesRegex(ProtocolError, 'overlaps'): self.assign('other', ['src/new/**'])
        (self.root/'src/App.kt').write_text('changed')
        result = self.run_request(action='handoff', assignmentId='source')
        (self.root/'src/App.kt').write_text('changed again')
        with self.assertRaisesRegex(ProtocolError, 'stale'):
            self.run_request(action='ingest', handoffRef=result['handoffRef'], inspectionNote='review')

    def test_superseded_attempt_preserved_and_digest_conflict_rejected(self):
        self.package(); self.assign('source', ['src/**'])
        (self.root/'src/App.kt').write_text('first result')
        old = self.run_request(action='handoff', assignmentId='source')
        original = (self.root/old['handoffRef']).read_bytes()
        (self.root/'src/App.kt').write_text('corrected result')
        new = self.run_request(action='handoff', assignmentId='source', supersedes=[old['handoffRef']])
        before = self.fixture.ledger()['ledgerDigest']
        with self.assertRaises(ProtocolError):
            self.run_request(action='ingest', handoffRef=new['handoffRef'], inspectionNote='both attempts reviewed', expectedLedgerDigest='0'*64)
        self.assertEqual(before, self.fixture.ledger()['ledgerDigest'])
        self.run_request(action='ingest', handoffRef=new['handoffRef'], inspectionNote='both attempts reviewed')
        self.assertEqual(original, (self.root/old['handoffRef']).read_bytes())
        brief = json.loads(self.fixture.exec_script('resume-delivery.py', str(self.root), '--compact').stdout)
        self.assertEqual([], brief['pendingHandoffs'])
        self.assertTrue(brief['safeToContinue'])

    def test_scope_invalidation_and_metadata_reuse(self):
        self.package(); self.scope()
        scope = registered_scope(self.root, 'component'); initial = input_fingerprint(self.root, scope)
        (self.root/'docs/new-assignment.md').write_text('unrelated planning')
        self.assertEqual(initial, input_fingerprint(self.root, scope))
        (self.root/'src/New.kt').write_text('new source')
        self.assertNotEqual(initial, input_fingerprint(self.root, scope))
        (self.root/'src/New.kt').unlink()
        (self.root/'build.gradle.kts').write_text('toolchain changed')
        self.assertNotEqual(initial, input_fingerprint(self.root, scope))
        (self.root/'build.gradle.kts').unlink()
        (self.root/'app-spec/domain.md').write_text('changed contract')
        self.assertNotEqual(initial, input_fingerprint(self.root, scope))

    def test_check_before_handoff_and_failed_latest_receipt(self):
        self.package(); self.scope(); self.assign('source', ['src/**'])
        coverage = [{'obligationId':'AC-001','surfaces':['component-test']}]
        path, good = CHECK.run_check(self.root, [sys.executable, '-c', 'print("passed")'], coverage, input_scope_id='component')
        self.assertTrue(receipt_stable(good))
        (self.root/'config/quality.yml').write_text('independent edit')
        self.assertTrue(receipt_current(self.root, good, compute_workspace_fingerprint(self.root)))
        self.run_request(action='bind', receiptRef=path.relative_to(self.root).as_posix())
        self.assertEqual('in-progress', self.fixture.ledger()['acceptanceScenarios'][0]['status'])
        self.assertEqual([], list((self.root/'.vibe/handoffs').glob('*.json')))
        badpath, bad = CHECK.run_check(self.root, [sys.executable, '-c', 'raise SystemExit(3)'], coverage, input_scope_id='component')
        self.fixture.verified_ac([path.relative_to(self.root).as_posix(), badpath.relative_to(self.root).as_posix()])
        errors = D.VALIDATOR.validate_ledger(self.root, self.fixture.ledger_path, closure=False).errors
        self.assertTrue(any('latest current receipt' in e for e in errors), errors)
        with self.assertRaisesRegex(ProtocolError, 'final'):
            CHECK.run_check(self.root, [sys.executable, '-c', 'pass'], coverage, kind='final', input_scope_id='component')

    def test_scoped_check_observes_inputs_changing_during_execution(self):
        self.package(); self.scope()
        _, receipt = CHECK.run_check(self.root, [sys.executable, '-c', "from pathlib import Path; Path('src/App.kt').write_text('mutated')"], [], input_scope_id='component')
        self.assertEqual('workspace-changed', receipt['executionStatus'])
        self.assertFalse(receipt_stable(receipt))

    def test_ingest_does_not_swallow_unregistered_workspace_drift(self):
        self.package(); self.assign('source', ['src/**'])
        (self.root/'src/App.kt').write_text('result')
        result = self.run_request(action='handoff', assignmentId='source')
        (self.root/'unrelated.txt').write_text('user change')
        with self.assertRaisesRegex(ProtocolError, 'unexpected workspace drift'):
            self.run_request(action='ingest', handoffRef=result['handoffRef'], inspectionNote='source reviewed')

    def test_package_does_not_claim_integration_from_ac_status(self):
        self.package()
        with self.assertRaisesRegex(ProtocolError, 'evidence'):
            self.run_request(action='integrate', packageId='catalog')
        with self.assertRaisesRegex(ProtocolError, 'integrate'):
            self.run_request(action='package', packageId='next', owner='root', acceptanceScenarioIds=['AC-001'], fileBoundaries=['src/**'], integrationGoal='next')

    @unittest.skipUnless(sys.platform == 'win32' and shutil.which('pwsh'), 'Windows PowerShell runner')
    def test_gradle_json_request_preserves_task_array_and_binds_receipt(self):
        self.package()
        (self.root/'gradlew.bat').write_text('@echo off\necho first=%1 second=%2\nexit /b 0\n')
        self.run_request(action='scope', scopeId='component', patterns=['src/**', 'tests/**'],
            dependencyRationale='Complete fixture dependencies', toolchainIdentity='test wrapper', reconcileDrift='Added isolated test wrapper')
        request_path = self.root/'.vibe/requests/compile.json'; request_path.parent.mkdir(parents=True)
        request_path.write_text(json.dumps({'action':'check', 'runner':'gradle', 'inputScopeId':'component',
            'tasks':[':component:compile', ':component:test'],
            'coveredObligations':[{'obligationId':'AC-001','surfaces':['component-test']}]}))
        result = self.fixture.exec_script('delivery-work.py', str(self.root), '--request', '.vibe/requests/compile.json', check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        refs = self.fixture.ledger()['acceptanceScenarios'][0]['receiptRefs']
        self.assertEqual(1, len(refs))
        receipt = read_json(self.root/refs[0])
        self.assertEqual([':component:compile', ':component:test'], receipt['tasks'])
        self.assertIn('first=:component:compile second=:component:test', (self.root/receipt['log']['path']).read_text())
        self.assertTrue(receipt_current(self.root, receipt, compute_workspace_fingerprint(self.root)))


if __name__ == '__main__': unittest.main()
