"""Coalesce ready Gradle requests only when execution inputs are identical."""
from vibe_protocol import ProtocolError


def combine(requests):
    if not requests: raise ProtocolError('no ready checks')
    first = requests[0]
    keys = ('runner', 'kind', 'inputScopeId', 'timeoutSeconds', 'toolchainIdentity')
    if first.get('runner') != 'gradle' or any(any(r.get(k) != first.get(k) for k in keys) for r in requests):
        raise ProtocolError('only compatible Gradle requests may be combined')
    # Options have graph-wide effects; retain exactly one identical option set.
    options = [t for t in first['tasks'] if t.startswith('-')]
    if any([t for t in r['tasks'] if t.startswith('-')] != options for r in requests):
        raise ProtocolError('Gradle options differ')
    coverage = {}
    tasks = []
    for request in requests:
        for task in request['tasks']:
            if task not in tasks: tasks.append(task)
        for row in request['coveredObligations']:
            coverage.setdefault(row['obligationId'], set()).update(row['surfaces'])
    return {**first, 'tasks': tasks, 'sourceCheckIds': [r['checkId'] for r in requests],
            'sourceChecks': [{k:r[k] for k in ('checkId', 'tasks', 'coveredObligations')} for r in requests],
            'coveredObligations': [{'obligationId': i, 'surfaces': sorted(s)} for i, s in sorted(coverage.items())]}
