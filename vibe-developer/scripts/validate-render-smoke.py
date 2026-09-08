"""Reject empty discovery, stale snapshots and missing/invalid render output."""
import argparse
import struct
from pathlib import Path
from vibe_protocol import ProtocolError, read_json, repository_path, parse_time


def validate(root, data):
    if not isinstance(data.get('previewCount'), int) or data['previewCount'] < 1: raise ProtocolError('zero preview discovery')
    cases = data.get('cases', [])
    if not cases or len({c['id'] for c in cases}) != len(cases): raise ProtocolError('expected unique smoke cases')
    expected = {'light', 'dark', 'ru-200'}
    if not expected <= {c.get('variant') for c in cases}: raise ProtocolError('light/dark/RU200 smoke required')
    started = parse_time(data['startedAt']).timestamp()
    for case in cases:
        path = repository_path(root, case['snapshotPath'])
        if not path.is_file() or path.stat().st_mtime < started: raise ProtocolError('missing or stale render; check resource class/runtime')
        png = path.read_bytes()
        if len(png) < 33 or png[:8] != b'\x89PNG\r\n\x1a\n' or png[12:16] != b'IHDR' or not all(struct.unpack('>II', png[16:24])):
            raise ProtocolError('invalid PNG render')
    return len(cases)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path); parser.add_argument('--inventory', type=Path, required=True)
    args = parser.parse_args()
    try: print(f'Validated {validate(args.repository.resolve(), read_json(args.inventory))} smoke renders')
    except (ProtocolError, OSError, ValueError, KeyError) as exc: parser.exit(1, f'ERROR: {exc}\n')
