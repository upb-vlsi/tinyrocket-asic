#!/usr/bin/env python3
"""Name-only GDS release conversion with reversible, byte-exact verification."""
import gzip
import hashlib
import json
import re
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/scratch/larluc/chipyard/vlsi/experiments/sg13cmos5l-signoff-20261031')
RUN = BASE / 'reset-debug-20261104'
SOURCE = RUN / 'm2-repair-v5-exact/ChipTop.filled.repaired.gds.gz'
EXPECTED = '251dbb35b9e3d5139a41b2e88ae9211d29e937df8b5a2edcd9470bbfc09021ce'
NAME = 'RVSoC6706'
VERSION = 'v.1.0.0'
RELEASE = ROOT / 'release' / VERSION


def records(data):
    offset = 0
    while offset < len(data):
        length, kind, dtype = struct.unpack_from('>HBB', data, offset)
        if length < 4 or length % 2 or offset + length > len(data):
            raise ValueError('Invalid GDS record')
        yield kind, dtype, data[offset + 4:offset + length]
        offset += length


def rename(data, old, new):
    result = bytearray()
    names, refs = [], set()
    changed = []
    for kind, dtype, payload in records(data):
        if kind in (6, 18):
            text = payload.rstrip(b'\0').decode('ascii')
            if kind == 6:
                names.append(text)
            else:
                refs.add(text)
            if text == new:
                raise ValueError('Destination cell name already exists')
            if text == old:
                payload = new.encode('ascii')
                payload += b'\0' * (len(payload) % 2)
                changed.append(kind)
        result.extend(struct.pack('>HBB', len(payload) + 4, kind, dtype))
        result.extend(payload)
    if len(names) != len(set(names)) or set(names) - refs != {old} or names.count(old) != 1:
        raise ValueError('Unexpected source cell hierarchy')
    if changed != [6]:
        raise ValueError('Expected one root STRNAME change and no references')
    return bytes(result)


def main():
    original = gzip.decompress(SOURCE.read_bytes())
    if hashlib.sha256(original).hexdigest() != EXPECTED:
        raise ValueError('Frozen layout changed')
    renamed = rename(original, 'ChipTop', NAME)
    if rename(renamed, NAME, 'ChipTop') != original:
        raise ValueError('Inverse name transform is not byte-exact')
    target = RELEASE / 'gds' / (NAME + '.gds.gz')
    target.parent.mkdir(parents=True, exist_ok=True)
    compressed = gzip.compress(renamed, mtime=0)
    if target.exists() and target.read_bytes() != compressed:
        raise ValueError('Refusing to overwrite a different release')
    target.write_bytes(compressed)
    (RELEASE / 'netlist').mkdir(exist_ok=True)
    netlists = {}
    for suffix in ('lvs.v', 'sim.v'):
        source = RUN / 'conservative-route-pruned-v6' / ('ChipTop.' + suffix)
        text = source.read_text()
        replacement, count = re.subn(r'(?m)^(module\s+)ChipTop(?=\s*\()', r'\g<1>' + NAME, text)
        if count != 1:
            raise ValueError('Expected one top-level Verilog module declaration')
        dest = RELEASE / 'netlist' / (NAME + '.' + suffix)
        dest.write_text(replacement)
        netlists[dest.relative_to(ROOT).as_posix()] = dict(
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            sha256=hashlib.sha256(dest.read_bytes()).hexdigest(), change='top module declaration only')
    report = dict(source_top='ChipTop', release_top=NAME,
        source_gds_uncompressed_sha256=EXPECTED,
        release_gds_uncompressed_sha256=hashlib.sha256(renamed).hexdigest(),
        release_gds_gzip_sha256=hashlib.sha256(compressed).hexdigest(),
        changed_GDS_records=1, changed_record='STRNAME of root cell',
        reverse_transform_byte_identical=True, geometry_changed=False,
        gds_timestamps_changed=False, properties_changed=False,
        netlists=netlists, scope='Identity transform, not a new DRC/LVS run or signoff waiver.')
    (ROOT / 'doc').mkdir(exist_ok=True)
    (ROOT / 'doc/release-identity.json').write_text(json.dumps(report, indent=2) + '\n')
    physical = json.loads((RUN / 'physical-evidence-v6.json').read_text())
    (ROOT / 'doc/verification-status.json').write_text(json.dumps(dict(
        original_gds_sha256=EXPECTED, renamed_release_identity='doc/release-identity.json',
        drc=physical['drc'], raw_LVS_passed=False, waivers=[],
        qualified_floating_fill_timing=False, fabrication_authorization=False,
        scope='Selected physical-verification status; not a complete signoff declaration.'), indent=2) + '\n')
    for mode in ('minimum', 'density', 'antenna', 'full'):
        dest = ROOT / (NAME + '-main') / 'verification/drc' / mode
        dest.mkdir(parents=True, exist_ok=True)
        for filename in ('summary.json', 'results.lyrdb', 'input.sha256', 'deck.log', 'klayout.log', 'exitcode'):
            shutil.copyfile(RUN / 'fill-pruned-v6' / mode / filename, dest / filename)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
