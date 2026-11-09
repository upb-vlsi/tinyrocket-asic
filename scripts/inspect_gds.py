#!/usr/bin/env python3
"""Read-only release inspection. Requires the KLayout Python module."""
import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path


def records(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as handle:
        while header := handle.read(4):
            if len(header) != 4:
                raise ValueError('Truncated GDS record')
            size, kind, dtype = struct.unpack('>HBB', header)
            if size < 4 or size % 2:
                raise ValueError('Invalid GDS record length')
            data = handle.read(size - 4)
            if len(data) != size - 4:
                raise ValueError('Truncated GDS payload')
            yield kind, data


def main():
    import klayout.db as kdb
    parser = argparse.ArgumentParser()
    parser.add_argument('gds', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    layout = kdb.Layout()
    layout.read(str(args.gds))
    tops = list(layout.top_cells())
    if len(tops) != 1 or tops[0].name != 'ChipTop':
        raise ValueError('Expected exactly one ChipTop root')
    top = tops[0]
    scale = layout.dbu
    def box(b):
        return [round(x * scale, 6) for x in (b.left, b.bottom, b.right, b.top)]
    seal = []
    for cell in layout.each_cell():
        if 'sealring' in cell.name.lower():
            seal.append({'name': cell.name, 'local_bbox_um': box(cell.bbox())})
    layers = []
    for index in layout.layer_indexes():
        info = layout.get_info(index)
        it = top.begin_shapes_rec(index)
        if not it.at_end():
            layers.append({'layer': info.layer, 'datatype': info.datatype,
                           'bbox_um': box(top.bbox(index))})
    zero_paths = 0
    properties = 0
    max_vertices = 0
    current = None
    for kind, data in records(args.gds):
        if kind in (8, 9, 10, 11, 12, 21):
            current = kind
        if kind == 16:
            points = list(struct.iter_unpack('>ii', data))
            if current == 9 and len(set(points)) <= 1:
                zero_paths += 1
            if current == 8:
                max_vertices = max(max_vertices, len(points))
        if kind in (43, 44):
            properties += 1
    opener = gzip.open if args.gds.suffix == '.gz' else open
    digest = hashlib.sha256()
    with opener(args.gds, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    result = dict(top_cell='ChipTop', dbu_um=scale, bbox_um=box(top.bbox()),
                  cell_count=layout.cells(), sealring_cells=seal, layers=layers,
                  uncompressed_sha256=digest.hexdigest(), zero_length_paths=zero_paths,
                  property_records=properties, max_boundary_vertices=max_vertices,
                  geometry_modified=False,
                  note='Read-only inspection; whole-layout bounds are not an IHP-approved billing boundary.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('top_cell', 'dbu_um', 'bbox_um', 'zero_length_paths', 'property_records')}))


if __name__ == '__main__':
    main()
