"""Report category durations and union wall time; overlaps are never added twice."""
import argparse
import json
from pathlib import Path
from vibe_protocol import read_json, parse_time


def union_seconds(intervals):
    total = 0.; end = None
    for start, stop in sorted(intervals):
        if stop < start: raise ValueError('negative interval')
        total += max(0, stop - max(start, end if end is not None else start))
        end = max(stop, end if end is not None else stop)
    return total


def report(root):
    groups = {}
    for path in (root / '.vibe/jobs').glob('*.json'):
        data = read_json(path)
        for a, b in zip(data['events'], data['events'][1:]):
            category = {'queued':'queue', 'running':'execution', 'binding':'binding'}.get(a['stage'])
            if category: groups.setdefault(category, []).append((parse_time(a['at']).timestamp(), parse_time(b['at']).timestamp()))
    for path in (root / '.vibe/timing').glob('*.json'):
        row = read_json(path)
        groups.setdefault(row['category'], []).append((parse_time(row['startedAt']).timestamp(), parse_time(row['completedAt']).timestamp()))
    return {'categorySeconds': {k:union_seconds(v) for k,v in groups.items()},
            'coveredWallSeconds': union_seconds([i for v in groups.values() for i in v]),
            'note':'Category intervals may overlap; do not add category totals.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('repository', type=Path)
    print(json.dumps(report(parser.parse_args().repository), indent=2))
