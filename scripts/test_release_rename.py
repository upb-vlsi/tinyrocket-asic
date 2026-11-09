#!/usr/bin/env python3
import struct
import unittest
from prepare_minimum_release import rename


def record(kind, value):
    if isinstance(value, str):
        value = value.encode('ascii')
    value += b'\0' * (len(value) % 2)
    return struct.pack('>HBB', len(value) + 4, kind, 6) + value


class RenameTests(unittest.TestCase):
    def test_inverse_preserves_every_other_byte(self):
        original = record(6, 'ChipTop') + record(18, 'child') + record(44, 'ChipTop property') + record(6, 'child')
        changed = rename(original, 'ChipTop', 'RVSoC6706')
        self.assertEqual(rename(changed, 'RVSoC6706', 'ChipTop'), original)
        self.assertIn(b'ChipTop property', changed)

    def test_collision_rejected(self):
        with self.assertRaises(ValueError):
            rename(record(6, 'ChipTop') + record(6, 'RVSoC6706'), 'ChipTop', 'RVSoC6706')

    def test_multiple_roots_rejected(self):
        with self.assertRaises(ValueError):
            rename(record(6, 'ChipTop') + record(6, 'other'), 'ChipTop', 'RVSoC6706')

    def test_missing_root_rejected(self):
        with self.assertRaises(ValueError):
            rename(record(6, 'other'), 'ChipTop', 'RVSoC6706')

    def test_referenced_root_rejected(self):
        with self.assertRaises(ValueError):
            rename(record(6, 'ChipTop') + record(18, 'ChipTop'), 'ChipTop', 'RVSoC6706')


if __name__ == '__main__':
    unittest.main()
