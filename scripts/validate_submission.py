#!/usr/bin/env python3
"""Validate the minimum delivery, not electrical/physical signoff."""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

from prepare_minimum_release import rename, records


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate(root):
    info = json.loads((root / 'doc/info.json').read_text())
    identity = json.loads((root / 'doc/release-identity.json').read_text())
    name = info['name']
    if name != info['top_cell_name'] or not re.fullmatch(r'RVSoC\d{4}', name):
        raise ValueError('Invalid or inconsistent generated identifier')
    if info['unique_id'] != name[-4:] or info['process'] != 'SG13CMOS5L':
        raise ValueError('Process/identifier mismatch')
    if (info['sealring_x'], info['sealring_y']) != (2600.0, 2600.0):
        raise ValueError('Dimensions must be in microns and match inspected layout')
    if info['registered_area_mm2'] != 6.76:
        raise ValueError('Registered area mismatch')
    for key in ('gds', 'netlist', 'doc'):
        path = root / info['release'][key]
        if not path.exists() or root.resolve() not in path.resolve().parents:
            raise ValueError('Invalid release path: ' + key)
    gds = root / info['release']['gds']
    if gds.name != name + '.gds.gz' or digest(gds) != identity['release_gds_gzip_sha256']:
        raise ValueError('GDS filename/hash mismatch')
    data = gzip.decompress(gds.read_bytes())
    reverted = rename(data, name, 'ChipTop')
    if hashlib.sha256(reverted).hexdigest() != identity['source_gds_uncompressed_sha256']:
        raise ValueError('Renamed GDS does not restore the verified source')
    for relative, entry in identity['netlists'].items():
        path = root / relative
        if digest(path) != entry['sha256']:
            raise ValueError('Netlist checksum mismatch: ' + relative)
        text, count = re.subn(r'(?m)^(module\s+)' + name + r'(?=\s*\()', r'\g<1>ChipTop', path.read_text())
        if count != 1 or hashlib.sha256(text.encode()).hexdigest() != entry['source_sha256']:
            raise ValueError('Netlist is not a name-only conversion')
    status = json.loads((root / 'doc/verification-status.json').read_text())
    if status['fabrication_authorization'] or status['waivers']:
        raise ValueError('No authorization or waiver is recorded for this candidate')
    for mode in ('minimum', 'density', 'antenna'):
        folder = root / (name + '-main/verification/drc') / mode
        result = json.loads((folder / 'summary.json').read_text())
        if result['markers'] != 0 or not result['passed']:
            raise ValueError('Required recorded DRC result is not passing: ' + mode)
        if (folder / 'input.sha256').read_text().split()[0] != identity['source_gds_uncompressed_sha256']:
            raise ValueError('DRC report input mismatch')
    for path in root.rglob('*'):
        if '.git' not in path.parts and path.is_file() and path.stat().st_size >= 100 * 1024 * 1024:
            raise ValueError('File exceeds normal GitHub limit: ' + str(path))
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write-checksums', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    info = validate(root)
    release = root / 'release' / info['release']['version']
    checksum = release / 'SHA256SUMS'
    files = sorted(p for p in release.rglob('*') if p.is_file() and p != checksum)
    lines = ''.join(digest(p) + '  ' + p.relative_to(release).as_posix() + '\n' for p in files)
    if args.write_checksums:
        checksum.write_text(lines)
    elif not checksum.is_file() or checksum.read_text() != lines:
        raise ValueError('Missing or stale release/SHA256SUMS; run --write-checksums')
    print('PASS: minimum submission paths, generated names, dimensions, GDS inverse identity, netlists, DRC provenance and release checksums.')
    print('NOT a full-signoff pass. Repository-name acceptance and physical/electrical dispositions remain with IHP.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL:', error, file=sys.stderr)
        sys.exit(1)
