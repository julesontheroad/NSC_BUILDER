#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import io
from math import ceil
from Crypto.Hash import SHA256
from Utils import (
	read_at, read_u32, read_u64, pk_u32, pk_u64, align_to, 
	bytes2human, pad_to, FileInContainer
)
from CryptoUtils import sha256

ROMFS_HEADER_LENGTH = 0x50
ROMFS_FILEPARTITION_OFS = 0x200
ROMFS_ENTRY_EMPTY = 0xFFFFFFFF

class HashTable:
	def __init__(self, entry_count):
		self.entry_count = entry_count
		self.data		= entry_count * [pk_u32(ROMFS_ENTRY_EMPTY)]

	def add(self, entry, entry_table):
		assert isinstance(entry, DirEntry) or isinstance(entry, FileEntry), 'Invalid entry type'
		index = entry.hash % self.entry_count
		if self.data[index] != ROMFS_ENTRY_EMPTY:
			entry_table.data[-1]['PreviousHash'] = self.data[index]
		self.data[index] = pk_u32(entry.offsets['Self'])
			
	def get_table(self):
		return b''.join(_ for _ in self.data)

class EntryTable:
	def __init__(self, entry_type, entry_nb):
		if (entry_type != DirEntry) and (entry_type != FileEntry):
			raise TypeError('Invalid entry type')
		self.entry_type = entry_type
		self.entry_nb   = entry_nb
		self.data	   = []

	def add(self, entry):
		assert isinstance(entry, self.entry_type), 'Invalid entry type'
		if (len(self.data) <= self.entry_nb) and (self.entry_type is DirEntry):
			self.data.append({
				'Parent':	   pk_u32(entry.offsets['Parent']),
				'Sibling':	  pk_u32(entry.offsets['Sibling']),
				'Child':		pk_u32(entry.offsets['Child']),
				'File':		 pk_u32(entry.offsets['File']),
				'PreviousHash': pk_u32(ROMFS_ENTRY_EMPTY),
				'NameLength':   pk_u32(len(entry.name)),
				'Name':		 pad_to(entry.name.encode(), multiple=4)
			})
		elif len(self.data) <= self.entry_nb:
			self.data.append({
				'Parent':	   pk_u32(entry.offsets['Parent']),
				'Sibling':	  pk_u32(entry.offsets['Sibling']),
				'DataOffset':   pk_u64(entry.offsets['Data']),
				'Size':		 pk_u64(entry.offsets['Size']),
				'PreviousHash': pk_u32(ROMFS_ENTRY_EMPTY),
				'NameLength':   pk_u32(len(entry.name)),
				'Name':		 pad_to(entry.name.encode(), multiple=4)
			})
		else:
			raise ValueError('Table is already filled up')

	def get_table(self):
		table = b''
		for d in self.data:
			table += b''.join(d[_] for _ in d)
		return table

class DirEntry:
	ROMFS_DIRENTRY_LENGTH = 0x18
	def __init__(self, parent, name):
		if isinstance(name, bytes):
			name = name.decode()
		self.parent	 = parent
		self.prev	   = None
		self.next	   = None
		self.name	   = name
		self.hash	   = 0
		if parent is None:
			self.path_in_romfs = 'romfs:'				
		else:
			self.path_in_romfs = '/'.join((parent.path_in_romfs, name))
		self.offsets = {
			'Self':	0,
			'Parent':  0,
			'Sibling': ROMFS_ENTRY_EMPTY,
			'Child':   ROMFS_ENTRY_EMPTY,
			'File':	ROMFS_ENTRY_EMPTY
		}
		self.childs = []
		self.files  = []
		
	def __getattribute__(self, attr):
		return object.__getattribute__(self, attr)

class FileEntry:
	ROMFS_FILEENTRY_LENGTH = 0x20
	def __init__(self, parent, name, size):
		if isinstance(name, bytes):
			name = name.decode()
		self.parent		= parent
		self.prev		  = None
		self.next		  = None
		self.name		  = name
		self.path_in_romfs = '/'.join((parent.path_in_romfs, name))
		self.size		  = size
		self.hash		  = 0
		self.offsets	   = {
			'Self':	0,
			'Parent':  0,
			'Sibling': ROMFS_ENTRY_EMPTY,
			'Data':	0,
			'Size':	0
		}
		self.offset_in_romfs_data = 0
		self.is_repacked = False
		
	def __getattribute__(self, attr):
		return object.__getattribute__(self, attr)

class RomFS:
	'''Class to manipulate RomFS files'''
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		return 'romfs:' + self._print_dir(self.root, lvl=1)

	def _print_dir(self, dir, lvl=0, char='  '):
		tab = lvl * char
		string = ''
		for child in dir.childs:
			string += '\n' + tab + child.name
			string += self._print_dir(child, lvl + 1, char)
		for file in dir.files:
			string += '\n' + tab + bytes2human(file.size) + '\t' + file.name
		return string

	def _parse(self):
		if read_u64(self.f, 0x0) != 0x50:
			print('[WARN] RomFS header size isn\'t 0x50')
		self.dir_table   = io.BytesIO(read_at(self.f, read_u64(self.f, 0x18), read_u64(self.f, 0x20)))
		self.file_table  = io.BytesIO(read_at(self.f, read_u64(self.f, 0x38), read_u64(self.f, 0x40)))
		self.data_offset = read_u64(self.f, 0x48)
		if self.data_offset != ROMFS_FILEPARTITION_OFS:
			print('[WARN] Data offset isn\'t 0x200')
		
		self.first_file = None
		_, self.root = self._parse_dir(0, None)
		self._gen_metadata()

	def _parse_dir(self, offset, parent):
		cur_dir_dict = {
			'Parent':  read_u32(self.dir_table, offset + 0x0),
			'Sibling': read_u32(self.dir_table, offset + 0x4),
			'Child':   read_u32(self.dir_table, offset + 0x8),
			'File':	read_u32(self.dir_table, offset + 0xC),
			'Name':	read_at(self.dir_table, offset + 0x18, read_u32(self.dir_table, offset + 0x14)).decode()
		}
		dir_entry = DirEntry(parent, cur_dir_dict['Name'])

		if cur_dir_dict['Child'] != ROMFS_ENTRY_EMPTY: # if not cur_dir_dict['Child'] + 1 & 1 << 32:
			child_dict, child_entry = self._parse_dir(cur_dir_dict['Child'], dir_entry)
			dir_entry.childs.append(child_entry)
			while child_dict['Sibling'] != ROMFS_ENTRY_EMPTY:
				child_dict, child_entry = self._parse_dir(child_dict['Sibling'], dir_entry)
				dir_entry.childs.append(child_entry)
		if cur_dir_dict['File'] != ROMFS_ENTRY_EMPTY:
			file_dict, file_entry = self._parse_file(cur_dir_dict['File'], dir_entry)
			dir_entry.files.append(file_entry)
			while file_dict['Sibling'] != ROMFS_ENTRY_EMPTY:
				file_dict, file_entry = self._parse_file(file_dict['Sibling'], dir_entry)
				dir_entry.files.append(file_entry)
		return cur_dir_dict, dir_entry

	def _parse_file(self, offset, parent):
		file_dict = {
			'Parent':	 read_u32(self.file_table, offset + 0x0),
			'Sibling':	read_u32(self.file_table, offset + 0x4),
			'DataOffset': read_u64(self.file_table, offset + 0x8),
			'Size':	   read_u32(self.file_table, offset + 0x10),
			'Name':	   read_at(self.file_table, offset + 0x20, read_u32(self.file_table, offset + 0x1C)).decode()
		}
		file_entry = FileEntry(parent, file_dict['Name'], file_dict['Size'])
		file_entry.offset_in_romfs_data = file_dict['DataOffset']
		file_entry.is_repacked = True
		return file_dict, file_entry

	def _gen_metadata(self):
		self.dir_table_size = 0x18 # root
		self.dir_nb = 1			# root
		self.file_nb = 0
		self.data_size = self.file_table_size = self.dir_table_size = 0
		self.prev_dir = self.prev_file = None
		self._gen_dir_metadata(self.root)
		del self.prev_dir, self.prev_file

		self.first_file = self._find_first_file()
		self.dir_hash_table_entry_count  = self._calc_hash_table_entry_count(self.dir_nb)
		self.file_hash_table_entry_count = self._calc_hash_table_entry_count(self.file_nb)
		self.size = self.data_size + self.file_table_size + self.dir_table_size +\
			0x4 * (self.dir_hash_table_entry_count + self.file_hash_table_entry_count)
			

	def _gen_dir_metadata(self, dir_entry):
		if self.prev_dir is not None:
			self.prev_dir.next = dir_entry
		dir_entry.prev, self.prev_dir = self.prev_dir, dir_entry

		dir_entry.hash = self._calc_path_hash(dir_entry.offsets['Parent'], dir_entry.name.encode())

		for child in dir_entry.childs:
			self.dir_nb += 1
			if dir_entry.offsets['Child'] == ROMFS_ENTRY_EMPTY:
				dir_entry.offsets['Child'] = self.dir_table_size
			child.offsets['Parent'] = dir_entry.offsets['Self']
			child.offsets['Self'] = self.dir_table_size
			self.dir_table_size += DirEntry.ROMFS_DIRENTRY_LENGTH + align_to(len(child.name), 4)
			self._gen_dir_metadata(child)
			if child != dir_entry.childs[-1]:
				child.offsets['Sibling'] = self.dir_table_size
			else:
				child.offsets['Sibling'] = ROMFS_ENTRY_EMPTY
		for file_entry in dir_entry.files:
			self.file_nb += 1
			if self.prev_file is not None:
				self.prev_file.next = file_entry
			file_entry.prev, self.prev_file = self.prev_file, file_entry

			if dir_entry.offsets['File'] == ROMFS_ENTRY_EMPTY:
				dir_entry.offsets['File'] = self.file_table_size
			file_entry.offsets['Parent'] = dir_entry.offsets['Self']
			file_entry.offsets['Self'] = self.file_table_size
			self.file_table_size += FileEntry.ROMFS_FILEENTRY_LENGTH + align_to(len(file_entry.name), 4)
			if file_entry != dir_entry.files[-1]:
				file_entry.offsets['Sibling'] = self.file_table_size
			else:
				file_entry.offsets['Sibling'] = ROMFS_ENTRY_EMPTY
				
			file_entry.hash = self._calc_path_hash(file_entry.offsets['Parent'], file_entry.name.encode())

			file_entry.offsets['Size'] = file_entry.size
			file_entry.offsets['Data'] = self.data_size
			self.data_size += align_to(file_entry.size, 0x10)

	def _calc_path_hash(self, parent_offset, name):
		# https://www.3dbrew.org/wiki/RomFS#Hash_Table_Structure
		hash = parent_offset ^ 123456789
		for c in name:
			hash = (hash >> 5) | (hash << 27)
			hash &= (1 << 32) - 1 # Reproduce uint32 overflow
			hash ^= c
		return hash

	def _find_first_file(self):
		cur_dir = self.root
		while cur_dir.childs:
			cur_dir = cur_dir.childs[0]
		while not cur_dir.files:
			cur_dir = cur_dir.next
		return cur_dir.files[0]

	@classmethod
	def new(cls, *dirs):
		romfs = super().__new__(cls)
		romfs.f = None
		romfs.data_offset = 0x200
		romfs.root = DirEntry(None, '')
		romfs.add_dirs(*dirs)
		return romfs

	def add_dirs(self, *args):
		for arg in args:
			self._add_dir(arg, self.root)
		self._gen_metadata()

	def _add_dir(self, parent, parent_entry):
		if not (os.path.exists(parent) and os.path.isdir(parent)):
			raise ValueError('Wrong argument %s (doesn\'t exist, or is not a directory)' % parent)
		if not os.listdir(parent):
			raise Exception('Directory %s is empty' % parent)
		for item in os.listdir(parent):
			if os.path.isdir(os.path.join(parent, item)):
				child_entry = DirEntry(parent_entry, item)
				if parent_entry.childs:
					for child in parent_entry.childs:
						if child.name == item:
							child_entry = child # Merge the existing dir with the new one
							break
						elif child == parent_entry.childs[-1]:
							parent_entry.childs = self._ordered_insertion(child_entry, parent_entry.childs)
							break # List is modified, need to break out of it 
				else:
					parent_entry.childs = self._ordered_insertion(child_entry, parent_entry.childs)
				self._add_dir(os.path.join(parent, item), child_entry)

			elif os.path.isfile(os.path.join(parent, item)):
				file_entry = FileEntry(parent_entry, item, os.path.getsize(os.path.join(parent, item)))
				file_entry.path = os.path.join(parent, item)
				if parent_entry.files:
					for file in parent_entry.files:
						if file.name == item:
							index = parent_entry.files.index(file)
							parent_entry.files[index] = file_entry # Replace the old file with the new one
							break
						elif file == parent_entry.files[-1]:
							parent_entry.files = self._ordered_insertion(file_entry, parent_entry.files)
							break
				else:
					parent_entry.files = self._ordered_insertion(file_entry, parent_entry.files)

	def _ordered_insertion(self, item, list):
		list.append(item)
		return sorted(list, key=lambda x: x.name)

	def open(self, arg):
		if isinstance(arg, FileEntry): # Entry is provided
			entry = arg
		else:						  # Find the entry given its path
			arg = arg.replace('\\', '/')
			cur_file = self.first_file
			while cur_file.path_in_romfs != arg:
				if cur_file.next is None:
					raise FileNotFoundError('Can\'t find file in romfs')
				cur_file = cur_file.next
			entry = cur_file
				
		if entry.is_repacked:
			return self.FileInRomFS(self, entry)
		elif entry:
			return open(entry.path, 'rb')
		else:
			raise ValueError('Nothing to open')
	
	def extract(self, dest=None, disp=True):
		if dest is None:
			dest = os.path.join(os.path.dirname(__file__), os.path.splitext(self.f.name)[0])
		assert not os.path.isfile(dest), 'Output path is a file'
		os.makedirs(dest, exist_ok=True)
		
		cur_file = self.first_file
		while cur_file is not None:
			if disp:
				print('Extracting %s...' % cur_file.path_in_romfs)
			path = os.path.join(dest, cur_file.path_in_romfs.replace('romfs:/', ''))
			os.makedirs(os.path.dirname(path), exist_ok=True)
			inf = self.open(cur_file)
			outf = open(path, 'wb')
			while True:
				buf = inf.read(0x10000)
				if not buf:
					break
				outf.write(buf)
			inf.close()
			outf.close()
			cur_file = cur_file.next
		if disp:
			print('Extracted to %s' % dest)

	def _calc_hash_table_entry_count(self, entries_nb):
		# https://www.3dbrew.org/wiki/RomFS#Hash_Table_Structure
		count = entries_nb
		if entries_nb < 3:
			count = 3
		elif entries_nb < 19:
			count |= 1
		else:
			while (count % 2 == 0) or (count % 3 == 0) or (count % 5 == 0) or (count % 7 == 0)\
					or (count % 11 == 0) or (count % 13 == 0) or (count % 17 == 0):
				count += 1
		return count

	def _gen_footer(self):
		dir_hash_table = HashTable(self.dir_hash_table_entry_count)
		dir_table = EntryTable(DirEntry, self.dir_nb)
		cur_dir = self.root
		while cur_dir is not None:
			dir_table.add(cur_dir)
			dir_hash_table.add(cur_dir, dir_table)
			cur_dir = cur_dir.next
		dir_hash_table = dir_hash_table.get_table()
		self.dir_table = dir_table.get_table()

		file_hash_table = HashTable(self.file_hash_table_entry_count)
		file_table = EntryTable(FileEntry, self.file_nb)
		cur_file = self.first_file
		while cur_file is not None:
			file_table.add(cur_file)
			file_hash_table.add(cur_file, file_table)
			cur_file = cur_file.next
		file_hash_table = file_hash_table.get_table()
		self.file_table = file_table.get_table()
		return dir_hash_table + self.dir_table + file_hash_table + self.file_table

	def _gen_header(self):
		dir_hash_table_offset = ROMFS_FILEPARTITION_OFS + self.data_size
		dir_hash_table_length  = 4 * self.dir_hash_table_entry_count
		dir_table_offset = dir_hash_table_offset + dir_hash_table_length
		dir_table_length = len(self.dir_table)
		file_hash_table_offset = dir_table_offset + len(self.dir_table)
		file_hash_table_length = 4 * self.file_hash_table_entry_count
		file_table_offset = file_hash_table_offset + file_hash_table_length
		file_table_length = len(self.file_table)

		header = b''
		header += pk_u64(ROMFS_HEADER_LENGTH)
		header += pk_u64(dir_hash_table_offset)
		header += pk_u64(dir_hash_table_length)
		header += pk_u64(dir_table_offset)
		header += pk_u64(dir_table_length)
		header += pk_u64(file_hash_table_offset)
		header += pk_u64(file_hash_table_length)
		header += pk_u64(file_table_offset)
		header += pk_u64(file_table_length)
		header += pk_u64(ROMFS_FILEPARTITION_OFS)
		header = pad_to(header, length=ROMFS_FILEPARTITION_OFS)
		return header

	def _get_metadata(self):
		# In that order
		footer = self._gen_footer()
		header = self._gen_header()
		return header, footer

	def _buffered_repack(self, disp):
		header, footer = self._get_metadata()

		yield header
		cur_file = self.first_file
		while cur_file is not None:
			if disp:
				print('Appending %s...' % cur_file.path_in_romfs)
			inf = self.open(cur_file)
			while True:
				buf = inf.read(0x10000)
				if not buf:
					break
				yield pad_to(buf, multiple=0x10)
			inf.close()
			cur_file = cur_file.next
		yield footer

	def repack(self, dest, disp=True):
		if (self.f is not None) and (dest == self.f.name):
			raise FileExistsError('Can\'t repack RomFS to its original location')
		with open(dest, 'wb') as outf:
			for data in self._buffered_repack(disp=disp):
				outf.write(data)
		if disp:
			print('Repacked to %s' % dest)

	class FileInRomFS(FileInContainer):
		def __init__(self, romfs, file_entry):
			offset = file_entry.offset_in_romfs_data + ROMFS_FILEPARTITION_OFS
			size   = file_entry.size
			super(RomFS.FileInRomFS, self).__init__(romfs.f, offset, size)



class IVFCSuperblock:
	IVFC_MAX_LEVEL = 6
	def __init__(self, block):
		if read_at(block, 0x0, 0x4) != b'IVFC':
			print('[WARN] Invalid IVFC magic')
		if read_u32(block, 0x4) != 0x20000:
			print('[WARN] Invalid 0x20000 IVFC magic')
		self.master_hash_size = read_u32(block, 0x8)
		self.nb_lvl = read_u32(block, 0xC)
		
		self.lvls = []
		for n in range(self.IVFC_MAX_LEVEL):
			lvl = io.BytesIO(read_at(block, 0x10 + n*0x18, 0x18))
			self.lvls.append(self.IVFClvl(lvl))
		self.master_hash = read_at(block, 0xC0, self.master_hash_size)

	def gen(self):
		block = b''
		block += b'IVFC'
		block += pk_u32(0x20000)
		block += pk_u32(self.master_hash_size)
		block += pk_u32(self.IVFC_MAX_LEVEL+1) # Nb of levels
		block += b''.join(lvl.gen() for lvl in self.lvls)
		block += 0x20 * b'\0'
		block += self.master_hash
		block += 0x58 * b'\0'
		return block

	class IVFClvl:
		def __init__(self, block):
			self.offset = read_u64(block, 0x0)
			self.size = read_u64(block, 0x8)
			self.block_size = 1 << read_u32(block, 0x10) # In log2 in the header

		def gen(self):
			from math import log2
			lvl = b''
			lvl += pk_u64(self.offset)
			lvl += pk_u64(self.size)
			lvl += pk_u32(int(log2(self.block_size)))
			lvl += 0x4 * b'\0'
			return lvl

class HashTreeWrappedRomFS(RomFS):
	def __init__(self, section_header, fp, verify=False):
		self.section_header = section_header
		self.f = fp

		self.romfs_offset = self.section_header.lvls[IVFCSuperblock.IVFC_MAX_LEVEL-1].offset
		self.romfs_size   = self.section_header.lvls[IVFCSuperblock.IVFC_MAX_LEVEL-1].size
		
		if verify:
			if self.verify():
				self.is_valid = True
			else:
				self.is_valid = False
				print('[WARN] Invalid IVFC hash tree')
				
		super(HashTreeWrappedRomFS, self).__init__(FileInContainer(self.f, self.romfs_offset, self.romfs_size))
		
	def _get_tot_size(self):
		tot = cur_lvl_size = align_to(self.size, self.section_header.lvls[-1].block_size)
		for n in reversed(range(IVFCSuperblock.IVFC_MAX_LEVEL-1)):
			cur_lvl_size = align_to(cur_lvl_size // self.section_header.lvls[n].block_size * 0x20, self.section_header.lvls[n-1].block_size) 
			tot += cur_lvl_size
		return tot

	def _get_hash(self, lvl, block_nb):
		self.f.seek(self.section_header.lvls[lvl].offset + 0x20 * block_nb)
		return self.f.read(0x20)
	
	def _verify_block_hash(self, ref_hash, block, block_size):
		h = SHA256.new(block)
		if len(block) != block_size:
			h.update((block_size - len(block)) * b'\0')
		return ref_hash == h.digest()

	def verify(self):
		for lvl in range(IVFCSuperblock.IVFC_MAX_LEVEL):
			lvl_offset = self.section_header.lvls[lvl].offset
			lvl_size   = self.section_header.lvls[lvl].size
			block_size = self.section_header.lvls[lvl].block_size
			if lvl == 0:
				self.f.seek(lvl_offset)
				block = self.f.read(block_size)

				ref_hash = self.section_header.master_hash
				if not self._verify_block_hash(ref_hash, block, block_size):
					return False
				continue

			read = 0
			block_offsets = (lvl_offset + block_size * _ for _ in range(ceil(lvl_size / block_size)))
			for i, block_offset in enumerate(block_offsets):
				self.f.seek(block_offset)
				if lvl_size - read > block_size:
					block = self.f.read(block_size)
				else:
					block = self.f.read(lvl_size - read)
				read += len(block)

				ref_hash = self._get_hash(lvl-1, i)
				if not self._verify_block_hash(ref_hash, block, block_size):
					return False
		return True

	def _gen_hash_table(self, data_to_hash, block_size=0x4000):
		hash_table = b''
		n = 0
		while True:
			block = data_to_hash[n * block_size : (n + 1) * block_size]
			if not block:
				break
			hash_table += sha256(pad_to(block, multiple=block_size))
			n += 1
		return hash_table

	def _gen_hash_tree(self, disp=True):
		# If we want to yield the section in the right order,
		# we have no choice but to completely hash the romfs beforehand
		if disp:
			print('Hashing RomFS...')
		lvl_5 = b''
		data_to_hash = b''
		block_size = self.section_header.lvls[5].block_size
		for buf in super(HashTreeWrappedRomFS, self)._buffered_repack(disp=False):
			data_to_hash += buf
			while len(data_to_hash) >= block_size:
				lvl_5 += sha256(data_to_hash[:block_size])
				data_to_hash = data_to_hash[block_size:]
		if data_to_hash:
			lvl_5 += sha256(pad_to(data_to_hash, multiple=block_size))
		self.lvl_5_size = len(lvl_5)
		
		if disp:
			print('Hashing levels...')
		lvl_4 = self._gen_hash_table(lvl_5, block_size=self.section_header.lvls[4].block_size)
		self.lvl_4_size = len(lvl_4)
		lvl_3 = self._gen_hash_table(lvl_4, block_size=self.section_header.lvls[3].block_size)
		self.lvl_3_size = len(lvl_3)
		lvl_2 = self._gen_hash_table(lvl_3, block_size=self.section_header.lvls[2].block_size)
		self.lvl_2_size = len(lvl_2)
		lvl_1 = self._gen_hash_table(lvl_2, block_size=self.section_header.lvls[1].block_size)
		self.lvl_1_size = len(lvl_1)
		self.master_hash = self._gen_hash_table(lvl_1, block_size=blself.section_header.lvls[0].block_sizeock_size)

		return lvl_1, lvl_2, lvl_3, lvl_4, lvl_5

	@classmethod
	def new(cls, *files):
		super().new(*files)
		self.size = self._get_size()

	def _buffered_repack(self, block_size=0x4000, disp=True):
		lvl_1, lvl_2, lvl_3, lvl_4, lvl_5 = self._gen_hash_tree(block_size=block_size, disp=disp)
		
		if disp:
			print('Writing IVFC levels...')
		yield lvl_1
		yield (align_to(self.lvl_1_size, block_size) - self.lvl_1_size) * b'\0'
		yield lvl_2
		yield (align_to(self.lvl_2_size, block_size) - self.lvl_2_size) * b'\0'
		yield lvl_3
		yield (align_to(self.lvl_3_size, block_size) - self.lvl_3_size) * b'\0'
		yield lvl_4
		yield (align_to(self.lvl_4_size, block_size) - self.lvl_4_size) * b'\0'
		yield lvl_5
		yield (align_to(self.lvl_5_size, block_size) - self.lvl_5_size) * b'\0'
		
		if disp:
			print('Writing RomFS...')
		written = 0
		for buf in super(HashTreeWrappedRomFS, self)._buffered_repack(disp=disp):
			written += len(buf)
			yield buf
		yield (align_to(written, block_size) - written) * b'\0'

	def repack(self, dest, disp=True):
		if dest == self.f.name:
			raise FileExistsError('Can\'t repack RomFS to its original location')
		with open(dest, 'wb') as outf:
			for data in self._buffered_repack(disp=disp):
				outf.write(data)
		if disp:
			print('Repacked to %s' % dest)
