#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from math import ceil
from Utils import (
	read_at, read_u32, read_u64, pk_u32, pk_u64, 
	align_to, pad_to, bytes2human, FileInContainer
)
from CryptoUtils import sha256

PFS0_HEADER_LENGTH = 0x10
PFS0_FILE_ENTRY_LENGTH = 0x18

class PFS0:
	'''Class to manipulate PFS0 files'''
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		return 'pfs0:\n  ' +\
			'\n  '.join('%s\t%s' % (bytes2human(d['Size']), name) for name, d in self.files.items())

	def _parse(self):
		if read_at(self.f, 0x0, 0x4) != b'PFS0':
			raise ValueError('Invalid PFS0 magic!')
		
		self.files = {}
		self.file_nb = read_u32(self.f, 0x4)
		string_table_size = read_u32(self.f, 0x8)
		string_table_offset = PFS0_HEADER_LENGTH + self.file_nb * PFS0_FILE_ENTRY_LENGTH
		header_size = string_table_offset + string_table_size
		names = [name.decode() for name in read_at(self.f, string_table_offset, string_table_size).split(b'\x00')][:self.file_nb]
		
		for n in range(self.file_nb):
			self.files[names[n]] = {
				'Offset':	 read_u64(self.f, PFS0_HEADER_LENGTH + n * PFS0_FILE_ENTRY_LENGTH) + header_size,
				'Size':	   read_u64(self.f, PFS0_HEADER_LENGTH + n * PFS0_FILE_ENTRY_LENGTH + 0x8),
				'IsRepacked': True
			}
		self.filedata_size = sum(self.files[file]['Size'] for file in self.files)
		self.size = self.filedata_size + PFS0_HEADER_LENGTH

	@classmethod
	def new(cls, *files):
		pfs0 = super().__new__(cls)
		pfs0.f = None
		pfs0.file_nb = 0
		pfs0.files = {}
		pfs0.filedata_size = 0
		pfs0.add_files(*files)
		return pfs0

	def add_files(self, *args):
		for f in args:
			if f in self.files:
				self.filedata_size -= self.files[f]['SIze']
				self.file_nb -= 1
			self.files[os.path.basename(f)] = {
				'Path':	   f,
				'Size':	   os.path.getsize(f),
				'Offset':	 self.filedata_size,
				'IsRepacked': False
			}
			self.filedata_size += os.path.getsize(f)
			self.file_nb += 1

	def open(self, fn):
		assert fn in self.files, 'Couldn\'t find %s in PFS0' % fn
		if self.files[fn]['IsRepacked']:
			return self.FileinPFS0(self, fn)
		else:
			return open(self.files[fn]['Path'], 'rb')
		
	def extract(self, dest=None, disp=True):
		if dest is None:
			dest = os.path.join(os.path.dirname(__file__), os.path.splitext(self.f.name)[0])
		assert not os.path.isfile(dest), 'Output path is a file'
		os.makedirs(dest, exist_ok=True)
		
		for file in self.files:
			if disp:
				print('Extracting %s...' % file)
			inf = self.open(file)
			outf = open(os.path.join(dest, file), 'wb')
			while True:
				buf = inf.read(0x10000)
				if not buf:
					break
				outf.write(buf)
			inf.close()
			outf.close()
		if disp:
			print('Extracted to %s' % dest)

	def _gen_header(self):
		file_nb = len(self.files)
		string_table = b'\x00'.join(file.encode() for file in self.files)
		header_length = align_to(PFS0_HEADER_LENGTH + file_nb * PFS0_FILE_ENTRY_LENGTH + len(string_table), 0x10)
		string_table_length = header_length - (PFS0_HEADER_LENGTH + file_nb * PFS0_FILE_ENTRY_LENGTH)
		
		file_sizes = [self.files[file]['Size'] for file in self.files]
		file_offsets = [sum(file_sizes[:n]) for n in range(file_nb)]
		
		file_names_lengths = [len(file) + 1 for file in self.files]
		string_table_offsets = [sum(file_names_lengths[:n]) for n in range(file_nb)]
		
		header =  b''
		header += b'PFS0'
		header += pk_u32(file_nb)
		header += pk_u32(string_table_length)
		header += b'\x00\x00\x00\x00'
		for n in range(file_nb):
			header += pk_u64(file_offsets[n])
			header += pk_u64(file_sizes[n])
			header += pk_u32(string_table_offsets[n])
			header += b'\x00\x00\x00\x00'
		header += string_table
		header = pad_to(header, length=header_length)
		return header

	def _buffered_repack(self, disp=True):
		yield self._gen_header()
		for file in self.files:
			if disp:
				print('Appending %s...' % file)
			inf = self.open(file)
			while True:
				buf = inf.read(0x10000)
				if not buf:
					break
				yield buf
			inf.close()   

	def repack(self, dest, disp=True):
		if (self.f is not None) and (dest == self.f.name):
			raise FileExistsError('Can\'t repack PFS0 to its original location')
		with open(dest, 'wb') as outf:
			for data in self._buffered_repack(disp=disp):
				outf.write(data)
		if disp:
			print('Repacked to %s' % dest) 

	class FileinPFS0(FileInContainer):
		def __init__(self, pfs0, name):
			offset = pfs0.files[name]['Offset']
			size   = pfs0.files[name]['Size']
			super(PFS0.FileinPFS0, self).__init__(pfs0.f, offset, size)


class PFS0Superblock:
	def __init__(self, block):
		self.master_hash = read_at(block, 0x0, 0x20)
		self.block_size  = read_u32(block, 0x20)
		if read_u32(block, 0x24) != 2: # Always 2
			print('[WARN] %d should be 2' % read_u32(block, 0x24))
		self.hash_table_offset = read_u64(block, 0x28)
		self.hash_table_size   = read_u64(block, 0x30)
		self.offset = read_u64(block, 0x38)
		self.size   = read_u64(block, 0x40)

	def gen(self):
		block = b''
		block += self.master_hash
		block += pk_u32(self.block_size)
		block += pk_u32(0x2)
		block += pk_u64(self.hash_table_offset)
		block += pk_u64(self.hash_table_size)
		block += pk_u64(self.offset)
		block += pk_u64(self.size)
		block += 0xF0 * b'\0'
		return block

class HashTableWrappedPFS0(PFS0):
	def __init__(self, superblock, fp, verify=False):
		self.superblock = superblock
		self.f = fp
		
		self.master_hash	   = self.superblock.master_hash
		self.hash_table_offset = self.superblock.hash_table_offset
		self.hash_table_size   = self.superblock.hash_table_size
		self.block_size		= self.superblock.block_size
		self.pfs0_offset	   = self.superblock.offset
		self.pfs0_size		 = self.superblock.size

		if verify:
			if self.verify():
				self.is_valid = True
			else:
				self.is_valid = False
				print('[WARN] Invalid PFS0 hash table')

		super(HashTableWrappedPFS0, self).__init__(FileInContainer(self.f, self.pfs0_offset, self.pfs0_size))

	def _get_hash(self, block_nb):
		self.f.seek(0x20 * block_nb)
		return self.f.read(0x20)
	
	def _verify_block_hash(self, ref_hash, block):
		return ref_hash == sha256(block)

	def verify(self):
		self.f.seek(self.hash_table_offset)
		hash_table = self.f.read(self.hash_table_size)
		if not self._verify_block_hash(self.master_hash, hash_table):
			return False

		read = 0
		block_offsets = (self.pfs0_offset + self.block_size * _ for _ in range(ceil(self.pfs0_size / self.block_size)))
		for i, block_offset in enumerate(block_offsets):
			self.f.seek(block_offset)
			if self.pfs0_size - read > self.block_size:
				block = self.f.read(self.block_size)
			else: 
				block = self.f.read(self.pfs0_size - read)
			read += len(block)

			ref_hash = self._get_hash(i)
			if not self._verify_block_hash(ref_hash, block):
				return False
		return True

	def _gen_hash_table(self):
		hash_table = b''
		data_to_hash = b''
		for buf in super(HashTableWrappedPFS0, self)._buffered_repack(disp=False):
			data_to_hash += buf
			while len(data_to_hash) >= self.block_size:
				hash_table += sha256(data_to_hash[:self.block_size])
				data_to_hash = data_to_hash[self.block_size:]
		if data_to_hash:
			hash_table += sha256(data_to_hash)
		self.hash_table_size = len(hash_table)
		return hash_table

	def _get_tot_size(self):
		pfs0_size = align_to(self.size, self.block_size)
		return pfs0_size + align_to(pfs0_size // self.block_size * 0x20, self.block_size)

	def _buffered_repack(self, disp=True):
		yield self._gen_hash_table()
		yield (align_to(self.hash_table_size, self.block_size) - self.hash_table_size) * b'\0'
		written = 0
		for buf in super(HashTableWrappedPFS0, self)._buffered_repack(disp=disp):
			written += len(buf)
			yield buf
		yield (align_to(written, self.block_size) - written) * b'\0'

	def repack(self, dest=None, disp=True):
		if dest == self.f.name:
			raise FileExistsError('Can\'t repack PFS0 to its original location')
		with open(dest, 'wb') as outf:
			for data in self._buffered_repack(disp=disp):
				outf.write(data)
		if disp:
			print('Repacked to %s' % dest) 
	 