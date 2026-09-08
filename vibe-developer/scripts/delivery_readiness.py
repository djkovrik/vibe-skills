"""Cheap preflight and explicit host-local coverage, without weakening full completion."""
import platform
import shutil
from vibe_protocol import pending_handoff_paths, verification_surface_map


def host_availability(app):
    rows = []
    for obligation, surfaces in verification_surface_map(app).items():
        for surface in surfaces:
            unavailable = surface in {'ios-link-test', 'ios-build'} and platform.system() != 'Darwin'
            rows.append({'obligationId': obligation, 'surface': surface,
                'available': not unavailable, 'reason': 'Requires macOS/Xcode' if unavailable else '',
                'prerequisites': ['macOS', 'Xcode'] if unavailable else []})
    return {'host': platform.system(), 'tools': {tool: shutil.which(tool) for tool in ('python', 'java', 'pwsh', 'xcodebuild')}, 'surfaces': rows}


def unavailable_pairs(ledger):
    result = []
    gates = {g['id']: g for g in ledger['qualityGates']}
    for row in ledger.get('hostAvailability', {}).get('surfaces', []):
        if row.get('available') is not False: continue
        gate = gates.get(row['obligationId'], {})
        if not row.get('reason') or not row.get('prerequisites'): continue
        # Repository-verifiable failures cannot be relabeled as host limitations.
        if row['surface'] in {'ios-link-test', 'ios-build'} or gate.get('category') in {'platform', 'external', 'release'}:
            result.append(row)
    return result


def preflight(root, ledger):
    errors = []
    unavailable = {(r['obligationId'], r['surface']) for r in unavailable_pairs(ledger)}
    for item in ledger['acceptanceScenarios'] + ledger['qualityGates']:
        if item.get('applicability') == 'not-applicable' or item['status'] == 'waived': continue
        if item['status'] == 'blocked-external' and item.get('category') in {'platform', 'external', 'release'} and item.get('blocker'): continue
        if item.get('pendingChecks') or item.get('blockers'): errors.append(f"{item['id']}: unresolved work")
        local = [s for s in item['requiredVerificationSurfaces'] if (item['id'], s) not in unavailable]
        if item['status'] not in {'verified', 'implemented-unverified'}: errors.append(f"{item['id']}: implementation is not ready")
        elif item['status'] != 'verified' and (not unavailable or len(local) == len(item['requiredVerificationSurfaces'])):
            errors.append(f"{item['id']}: implementation is not ready")
        if local and (not item.get('productionEvidence') or not item.get('testEvidence')):
            errors.append(f"{item['id']}: missing evidence references")
    errors += [f'pending specialist hand-offs: {p}' for p in pending_handoff_paths(root, ledger)]
    return errors
