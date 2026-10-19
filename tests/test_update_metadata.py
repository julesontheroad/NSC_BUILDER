import hashlib
import io
import os
import struct
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'py/ztools/lib'))
import update_metadata as metadata

BASE_ID = 0x0100000000000000
PATCH_ID = BASE_ID + 0x800


def content(marker, kind, index=0, size=100):
    return (bytes([marker]) * 32 + bytes([marker]) * 16
            + size.to_bytes(6, 'little') + bytes([kind, index]))


def cnmt(kind, entries, version=0, application_id=BASE_ID, title_id=None):
    if title_id is None:
        title_id = BASE_ID if kind == 0x80 else PATCH_ID
    data = bytearray(0x30)
    struct.pack_into('<QIB', data, 0, title_id, version, kind)
    struct.pack_into('<HHH', data, 0xE, 0x10, len(entries), 0)
    struct.pack_into('<Q', data, 0x20, PATCH_ID if kind == 0x80 else application_id)
    data.extend(b''.join(entries))
    return bytes(data) + hashlib.sha256(data).digest()


def available(*entries):
    return {entry[0x20:0x30].hex() + '.nca': int.from_bytes(entry[0x30:0x36], 'little')
            for entry in entries}


class ControlMetadataTests(unittest.TestCase):
    def setUp(self):
        self.program = content(1, 1)
        self.control = content(2, 3)
        self.new_program = content(3, 1)
        self.new_control = content(4, 3, size=12345)
        self.base = cnmt(0x80, [self.program, self.control])
        self.patch = cnmt(0x81, [self.new_program, self.new_control], version=65536)
        self.files = available(self.new_program, self.new_control)

    def test_application_resolves_to_update_control_without_changing_program(self):
        replacements = metadata.control_replacements(self.base, [self.patch], self.files)
        changed = metadata.replace_controls(self.base, replacements)
        parsed = metadata.read_cnmt(changed)
        self.assertEqual(parsed['entries'], [self.program, self.new_control])
        self.assertEqual(changed[:0x30], self.base[:0x30])
        self.assertEqual(changed[-32:], hashlib.sha256(changed[:-32]).digest())
        self.assertEqual(len(changed), len(self.base))

    def test_highest_numeric_patch_version_wins_regardless_of_input_order(self):
        newer = cnmt(0x81, [self.new_program, content(5, 3)], version=131072)
        files = dict(self.files, **available(content(5, 3)))
        for patches in ([newer, self.patch], [self.patch, newer]):
            replacement = metadata.control_replacements(self.base, patches, files)
            self.assertEqual(replacement[0], content(5, 3))

    def test_other_game_patch_and_dlc_are_ignored(self):
        other = cnmt(0x81, [self.new_program, self.new_control], version=65536,
                     application_id=BASE_ID + 0x2000)
        dlc = cnmt(0x82, [self.new_control], version=65536)
        self.assertEqual(metadata.control_replacements(self.base, [other, dlc], self.files), {})

    def test_patch_id_must_match_application_patch_relationship(self):
        other = cnmt(0x81, [self.new_program, self.new_control], version=65536,
                     title_id=PATCH_ID + 0x2000)
        self.assertEqual(metadata.control_replacements(self.base, [other], self.files), {})

    def test_base_only_or_older_patch_is_unchanged(self):
        self.assertEqual(metadata.control_replacements(self.base, [], {}), {})
        same_version = cnmt(0x81, [self.new_program, self.new_control])
        self.assertEqual(metadata.control_replacements(self.base, [same_version], self.files), {})

    def test_missing_program_or_control_is_rejected(self):
        for missing in self.files:
            files = {name: size for name, size in self.files.items() if name != missing}
            with self.assertRaisesRegex(ValueError, 'missing content'):
                metadata.control_replacements(self.base, [self.patch], files)

    def test_incorrect_content_size_is_rejected(self):
        files = {name: size + 1 for name, size in self.files.items()}
        with self.assertRaisesRegex(ValueError, 'missing content'):
            metadata.control_replacements(self.base, [self.patch], files)

    def test_control_only_patch_is_rejected(self):
        patch = cnmt(0x81, [self.new_control], version=65536)
        with self.assertRaisesRegex(ValueError, 'without its Program'):
            metadata.control_replacements(self.base, [patch], self.files)

    def test_multi_program_controls_match_by_index(self):
        base = cnmt(0x80, [self.control, content(6, 3, index=1)])
        patch = cnmt(0x81, [self.new_program, self.new_control, content(7, 1, index=1),
                            content(8, 3, index=1)], version=65536)
        files = available(*metadata.read_cnmt(patch)['entries'])
        replacements = metadata.control_replacements(base, [patch], files)
        changed = metadata.read_cnmt(metadata.replace_controls(base, replacements))
        self.assertEqual(changed['entries'], [self.new_control, content(8, 3, index=1)])

    def test_truncated_metadata_is_rejected(self):
        for data in (b'', self.base[:32], self.base[:-1]):
            with self.assertRaisesRegex(ValueError, 'Truncated'):
                metadata.read_cnmt(data)


class PackageTests(unittest.TestCase):
    def test_pfs0_round_trip_with_unicode_and_changed_entry_sizes(self):
        entries = [('first.cnmt.nca', b'updated metadata'), ('second.nca', b'program'),
                   ('informação.xml', b'<updated/>')]
        header = metadata.pfs0_header([(name, len(data)) for name, data in entries])
        package = io.BytesIO(header + b''.join(data for _, data in entries))
        for (name, offset, size), (expected_name, expected_data) in zip(
                metadata.read_pfs0(package), entries):
            package.seek(offset)
            self.assertEqual(name, expected_name)
            self.assertEqual(package.read(size), expected_data)
        self.assertEqual(len(header) % 16, 0)

    def test_duplicate_and_truncated_package_entries_are_rejected(self):
        for package in (b'PFS0', metadata.pfs0_header([('a.nca', 100)]),
                        metadata.pfs0_header([('a.nca', 0), ('a.nca', 0)])):
            with self.assertRaises(ValueError):
                metadata.read_pfs0(io.BytesIO(package))

    def test_truncated_stream_copy_is_rejected(self):
        with self.assertRaises(ValueError):
            metadata.copy_bytes(io.BytesIO(b'a'), io.BytesIO(), 2)


@unittest.skipUnless(os.environ.get('NSCB_NCA_TESTS') == '1',
                     'Set NSCB_NCA_TESTS=1 with NSCB Python dependencies installed')
class EncryptedPackageTests(unittest.TestCase):
    """Exercise the real NCA reader/writer using invented keys and content."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'py/ztools'))
        # Only suppress unrelated network DB initialization and extraction tools.
        extraction = types.ModuleType('Fs.pyNCA3')
        extraction.NCA3 = None
        cls.import_context = mock.patch.dict(sys.modules, {'nutdb': types.ModuleType('nutdb'),
                                                           'Fs.pyNCA3': extraction})
        cls.import_context.start()
        cls.addClassCleanup(cls.import_context.stop)
        import Fs
        import Keys
        import aes128
        cls.Fs, cls.Keys, cls.aes = Fs, Keys, aes128
        cls.old_keys, cls.old_area = Keys.keys.copy(), Keys.keyAreaKeys
        cls.header_key = bytes(range(32))
        cls.area_key = bytes(range(16))
        cls.data_key = bytes(range(16, 32))
        Keys.keys['header_key'] = cls.header_key.hex()
        Keys.keyAreaKeys = [[cls.area_key] * 3]

    @classmethod
    def tearDownClass(cls):
        cls.Keys.keys.clear()
        cls.Keys.keys.update(cls.old_keys)
        cls.Keys.keyAreaKeys = cls.old_area

    def make_meta(self, data, name):
        pfs = metadata.pfs0_header([(name, len(data))]) + data
        header = bytearray(0xC00)
        header[0x200:0x204] = b'NCA3'
        header[0x205] = 1
        size = 0xE00 + len(pfs)
        size += -size % 0x200
        struct.pack_into('<QQ', header, 0x208, size, BASE_ID)
        struct.pack_into('<II', header, 0x240, 6, size // 0x200)
        header[0x300:0x340] = self.aes.AESECB(self.area_key).encrypt(self.data_key * 4)
        header[0x400:0x405] = bytes([2, 0, 0, 2, 3])
        struct.pack_into('<I', header, 0x428, 0x4000)
        struct.pack_into('<QQQQ', header, 0x430, 0, 0x20, 0x200, len(pfs))
        header[0x408:0x428] = hashlib.sha256(hashlib.sha256(pfs).digest()).digest()
        header[0x280:0x2A0] = hashlib.sha256(header[0x400:0x600]).digest()
        section = hashlib.sha256(pfs).digest() + bytes(0x1E0) + pfs
        section += bytes(size - 0xC00 - len(section))
        return (self.aes.AESXTS(self.header_key).encrypt(bytes(header))
                + self.aes.AESCTR(self.data_key, bytearray(16), offset=0xC00).encrypt(section))

    def make_package(self, directory, include_patch=True):
        base_control = bytearray(0x3070)
        base_control[0x3060:0x3065] = b'1.0.0'
        update_control = bytearray(base_control)
        update_control[0x3060:0x3065] = b'1.4.2'
        payloads = [b'original program', bytes(base_control), b'update program', bytes(update_control)]
        entries = []
        records = []
        for payload, kind in zip(payloads, (1, 3, 1, 3)):
            digest = hashlib.sha256(payload).digest()
            entries.append((digest[:16].hex() + '.nca', payload))
            records.append(digest + digest[:16] + len(payload).to_bytes(6, 'little') + bytes([kind, 0]))
        base = self.make_meta(cnmt(0x80, records[:2]), 'Application_0100000000000000.cnmt')
        patch = self.make_meta(cnmt(0x81, records[2:], version=65536), 'Patch_0100000000000800.cnmt')
        entries.append((hashlib.sha256(base).hexdigest()[:32] + '.cnmt.nca', base))
        if include_patch:
            entries.append((hashlib.sha256(patch).hexdigest()[:32] + '.cnmt.nca', patch))
        entries.append((entries[4][0][:-3] + 'xml', b'<old XML/>'))
        path = directory / 'Mario.nsp'
        path.write_bytes(metadata.pfs0_header([(name, len(data)) for name, data in entries])
                         + b''.join(data for _, data in entries))
        return path, dict(entries)

    def test_rebuilt_package_reports_update_version_and_preserves_payloads(self):
        with tempfile.TemporaryDirectory() as directory:
            path, original = self.make_package(Path(directory))
            self.assertEqual(metadata.prefer_update_metadata(path), 1)
            with path.open('rb') as source:
                output = {}
                for name, offset, size in metadata.read_pfs0(source):
                    source.seek(offset)
                    output[name] = source.read(size)
            for name, payload in original.items():
                if name.endswith('.nca') and not name.endswith('.cnmt.nca'):
                    self.assertEqual(output[name], payload)
            new_names = output.keys() - original.keys()
            new_meta = next(name for name in new_names if name.endswith('.cnmt.nca'))
            self.assertEqual(new_meta[:32], hashlib.sha256(output[new_meta]).hexdigest()[:32])
            local = Path(directory) / new_meta
            local.write_bytes(output[new_meta])
            nca = self.Fs.Nca(str(local), 'rb')
            try:
                data = next(metadata.cnmt_files(nca))
                data.rewind()
                parsed = metadata.read_cnmt(data.read())
            finally:
                nca.close()
            selected = next(entry for entry in parsed['entries'] if entry[0x36] == 3)
            control = output[selected[0x20:0x30].hex() + '.nca']
            self.assertEqual(control[0x3060:0x3070].rstrip(b'\0'), b'1.4.2')
            # Independently decrypt and verify every integrity layer.
            encrypted = output[new_meta]
            header = self.aes.AESXTS(self.header_key).decrypt(encrypted[:0xC00])
            section = self.aes.AESCTR(self.data_key, bytearray(16), offset=0xC00).decrypt(encrypted[0xC00:])
            pfs_size = struct.unpack_from('<Q', header, 0x448)[0]
            self.assertEqual(section[:32], hashlib.sha256(section[0x200:0x200 + pfs_size]).digest())
            self.assertEqual(header[0x408:0x428], hashlib.sha256(section[:32]).digest())
            self.assertEqual(header[0x280:0x2A0], hashlib.sha256(header[0x400:0x600]).digest())
            xml = output[new_meta[:-3] + 'xml']
            self.assertIn(selected[0x20:0x30].hex().encode(), xml)
            self.assertIn(hashlib.sha256(encrypted).hexdigest().encode(), xml)

    def test_base_only_package_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = self.make_package(Path(directory), include_patch=False)
            original = path.read_bytes()
            self.assertEqual(metadata.prefer_update_metadata(path), 0)
            self.assertEqual(path.read_bytes(), original)

    def test_failed_rebuild_keeps_original_output_and_removes_temporary_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = self.make_package(Path(directory))
            original = path.read_bytes()
            with mock.patch.object(metadata.os, 'replace', side_effect=OSError('test failure')):
                with self.assertRaisesRegex(OSError, 'test failure'):
                    metadata.prefer_update_metadata(path)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
