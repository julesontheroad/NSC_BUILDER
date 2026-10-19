"""Expose the bundled update's Control NCA to CNMT-based library scanners.

This changes Application metadata only. Program and Patch NCAs remain separate;
emulators that require explicit update selection still need that selection.
"""

import hashlib
import os
import shutil
import struct
import tempfile
from pathlib import Path


def read_cnmt(data):
    if len(data) < 0x40:
        raise ValueError('Truncated CNMT')
    title_id, version, kind = struct.unpack_from('<QIB', data)
    extra, count, meta_count = struct.unpack_from('<HHH', data, 0xE)
    start = 0x20 + extra
    end = start + count * 0x38
    if end + meta_count * 0x10 > len(data) - 0x20:
        raise ValueError('Truncated CNMT content table')
    if kind in (0x80, 0x81) and extra < 0x10:
        raise ValueError('Missing Application/Patch extended header')
    return {
        'title_id': title_id, 'version': version, 'kind': kind,
        'application_id': struct.unpack_from('<Q', data, 0x20)[0],
        'start': start,
        'entries': [data[i:i + 0x38] for i in range(start, end, 0x38)],
    }


def control_replacements(application, patches, available):
    """Match by the CNMT relationship and program index, never by filename."""
    base = read_cnmt(application)
    if base['kind'] != 0x80:
        return {}
    candidates = [read_cnmt(patch) for patch in patches]
    candidates = [patch for patch in candidates
                  if patch['kind'] == 0x81
                  and patch['application_id'] == base['title_id']
                  and patch['title_id'] == base['application_id']
                  and patch['version'] > base['version']]
    if not candidates:
        return {}
    patch = max(candidates, key=lambda item: item['version'])
    controls = {entry[0x37]: entry for entry in patch['entries'] if entry[0x36] == 3}
    programs = {entry[0x37] for entry in patch['entries'] if entry[0x36] == 1}
    replacements = {}
    for entry in base['entries']:
        index = entry[0x37]
        if entry[0x36] != 3 or index not in controls:
            continue
        if index not in programs:
            raise ValueError('Update has Control metadata without its Program patch')
        for content in patch['entries']:
            if content[0x36] in (1, 3):
                name = content[0x20:0x30].hex() + '.nca'
                if available.get(name) != int.from_bytes(content[0x30:0x36], 'little'):
                    raise ValueError('Bundled update is missing content: ' + name)
        replacements[index] = controls[index]
    return replacements


def replace_controls(data, replacements):
    meta = read_cnmt(data)
    result = bytearray(data)
    for number, entry in enumerate(meta['entries']):
        if entry[0x36] == 3 and entry[0x37] in replacements:
            start = meta['start'] + number * 0x38
            result[start:start + 0x38] = replacements[entry[0x37]]
    result[-0x20:] = hashlib.sha256(result[:-0x20]).digest()
    return bytes(result)


def read_pfs0(stream):
    stream.seek(0, os.SEEK_END)
    total = stream.tell()
    stream.seek(0)
    header = stream.read(0x10)
    if len(header) != 0x10 or header[:4] != b'PFS0':
        raise ValueError('Expected an unsplit NSP (PFS0)')
    count, strings_size = struct.unpack_from('<II', header, 4)
    data_start = 0x10 + count * 0x18 + strings_size
    if data_start > total:
        raise ValueError('Truncated NSP header')
    records = stream.read(count * 0x18)
    strings = stream.read(strings_size)
    entries = []
    for i in range(count):
        offset, size, name_offset = struct.unpack_from('<QQI', records, i * 0x18)
        name_end = strings.find(b'\0', name_offset)
        if name_offset >= len(strings) or name_end < 0 or data_start + offset + size > total:
            raise ValueError('Invalid NSP entry')
        name = strings[name_offset:name_end].decode('utf-8')
        if Path(name).name != name or name in ('', '.', '..'):
            raise ValueError('Invalid NSP filename')
        entries.append((name, data_start + offset, size))
    if len({entry[0] for entry in entries}) != count:
        raise ValueError('Duplicate NSP filenames')
    return entries


def pfs0_header(entries):
    strings = bytearray()
    records = bytearray()
    offset = 0
    for name, size in entries:
        records.extend(struct.pack('<QQII', offset, size, len(strings), 0))
        strings.extend(name.encode('utf-8') + b'\0')
        offset += size
    strings.extend(b'\0' * (-(0x10 + len(records) + len(strings)) % 0x10))
    return struct.pack('<4sIII', b'PFS0', len(entries), len(strings), 0) + records + strings


def copy_bytes(source, target, size):
    while size:
        data = source.read(min(size, 1024 * 1024))
        if not data:
            raise ValueError('Unexpected end of NSP content')
        target.write(data)
        size -= len(data)


def cnmt_files(nca):
    for section in nca:
        for cnmt in section:
            if str(cnmt._path).endswith('.cnmt'):
                yield cnmt


def patch_meta(path, replacements, nca_factory):
    nca = nca_factory(str(path), 'r+b')
    try:
        # The existing NCA hash helpers support a single PFS0 hash block.
        if nca.pfs0_MULT() != 1:
            raise ValueError('Update metadata mode requires a single-block Application CNMT')
        for cnmt in cnmt_files(nca):
            cnmt.rewind()
            data = cnmt.read()
            if read_cnmt(data)['kind'] == 0x80:
                cnmt.rewind()
                cnmt.write(replace_controls(data, replacements))
        nca.flush()
    finally:
        nca.close()
    # Reopen after each write, as required by the encrypted File buffers.
    for calculate, write in (
        (lambda nca: nca.calc_pfs0_hash(), lambda nca, value: nca.set_pfs0_hash(value)),
        (lambda nca: nca.calc_htable_hash(), lambda nca, value: nca.header.set_htable_hash(value)),
        (lambda nca: nca.header.calculate_hblock_hash(),
         lambda nca, value: nca.header.set_hblock_hash(value)),
    ):
        nca = nca_factory(str(path), 'r+b')
        try:
            value = calculate(nca)
        finally:
            nca.close()
        nca = nca_factory(str(path), 'r+b')
        try:
            write(nca, value)
            nca.flush()
        finally:
            nca.close()


def prefer_update_metadata(path):
    """Atomically replace a generated, ticketless, unsplit NSP; return count."""
    import Fs

    path = Path(path)
    with path.open('rb') as source:
        entries = read_pfs0(source)
        available = {name: size for name, _, size in entries}
        with tempfile.TemporaryDirectory(prefix='.nscb-metadata-', dir=path.parent) as temp:
            temp = Path(temp)
            metadata = []
            for name, offset, size in entries:
                if not name.endswith('.cnmt.nca'):
                    continue
                local = temp / name
                source.seek(offset)
                with local.open('wb') as target:
                    copy_bytes(source, target, size)
                nca = Fs.Nca(str(local), 'rb')
                try:
                    for cnmt in cnmt_files(nca):
                        cnmt.rewind()
                        metadata.append((name, cnmt.read()))
                finally:
                    nca.close()
            overrides = {}
            patches = [data for _, data in metadata if read_cnmt(data)['kind'] == 0x81]
            for name, data in metadata:
                replacements = control_replacements(data, patches, available)
                if not replacements:
                    continue
                local = temp / name
                patch_meta(local, replacements, Fs.Nca)
                digest = hashlib.sha256(local.read_bytes()).hexdigest()
                new_name = digest[:32] + '.cnmt.nca'
                renamed = temp / new_name
                local.rename(renamed)
                overrides[name] = renamed
                nca = Fs.Nca(str(renamed), 'rb')
                try:
                    xml = Path(nca.xml_gen(str(temp), digest))
                finally:
                    nca.close()
                old_xml = name[:-3] + 'xml'
                if old_xml in available:
                    overrides[old_xml] = xml
            if not overrides:
                return 0
            output_entries = [(overrides[name].name, overrides[name].stat().st_size)
                              if name in overrides else (name, size)
                              for name, _, size in entries]
            required = len(pfs0_header(output_entries)) + sum(size for _, size in output_entries)
            if shutil.disk_usage(path.parent).free < required:
                raise OSError('Not enough free space to rebuild NSP with update metadata')
            rebuilt = temp / 'rebuilt.nsp'
            with rebuilt.open('wb') as target:
                target.write(pfs0_header(output_entries))
                for name, offset, size in entries:
                    if name in overrides:
                        with overrides[name].open('rb') as replacement:
                            shutil.copyfileobj(replacement, target, 1024 * 1024)
                    else:
                        source.seek(offset)
                        copy_bytes(source, target, size)
                target.flush()
                os.fsync(target.fileno())
            os.chmod(rebuilt, path.stat().st_mode & 0o777)
            # Close the original before replacing it for Windows compatibility.
            source.close()
            os.replace(rebuilt, path)
            return sum(name.endswith('.cnmt.nca') for name in overrides)
