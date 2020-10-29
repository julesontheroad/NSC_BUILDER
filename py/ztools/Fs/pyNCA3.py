#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import io
from struct import pack as pk
from binascii import hexlify as hx, unhexlify as uhx
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Utils import (
	read_at, read_u8, read_u32, read_u64, pk_u32, pk_u64,
	memdump, check_tkey, bytes2human, align_to, FileInContainer
)
from CryptoUtils import validate_rsa2048_pss_sig, gen_aes_kek, AESXTSN
from Fs.pyPFS0 import PFS0Superblock, HashTableWrappedPFS0
from Fs.pyRomFS import IVFCSuperblock, HashTreeWrappedRomFS
from Fs.pyNPDM import NPDM
from NXKeys import ProdKeys, TitleKeys
from tqdm import tqdm

import Keys

keys  = ProdKeys()
tkeys = list()

RSA_PUBLIC_EXPONENT = 0x10001
FS_HEADER_LENGTH = 0x200
nca_header_fixed_key_modulus_00 = 0xBFBE406CF4A780E9F07D0C99611D772F96BC4B9E58381B03ABB175499F2B4D5834B005A37522BE1A3F0373AC7068D116B904465EB707912F078B26DEF60007B2B451F80D0A5E58ADEBBC9AD649B964EFA782B5CF6D7013B00F85F6A908AA4D676687FA89FF7590181E6B3DE98A68C92604D980CE3F5E92CE01FF063BF2C1A90CCE026F16BC92420A4164CD52B6344DAEC02EDEA4DF27683CC1A060AD43F3FC86C13E6C46F77C299FFAFDF0E3CE64E735F2F656566F6DF1E242B08340A5C3202BCC9AAECAED4D7030A8701C70FD1363290279EAD2A7AF3528321C7BE62F1AAA407E328C2742FE8278EC0DEBE6834B6D8104401A9E9A67F67229FA04F09DE4F403
nca_header_fixed_key_modulus_01 = 0xADE3E1FA0435E5B6DD49EA8929B1FFB643DFCA96A04A13DF43D9949796436548705833A27D357B96745E0B5C32181424C258B36C227AA1B7CB90A7A3F97D4516A5C8ED8FAD395E9E4B51687DF80C35C63F91AE44A592300D46F840FFD0FF06D21C7F9618DCB71D663ED173BC158A2F94F300C183F1CDD78188ABDF8CEF97DD1B175F58F69AE9E8C22F3815F52107F837905D2E024024150D25B7265D09CC4CF4F21B94705A9EEEED7777D45199F5DC761EE36C8CD112D457D1B683E4E4FEDAE9B43B33E5378ADFB57F89F19B9EB015B23AFEEA61845B7D4B23120B8312F2226BB922964B260B635E965752A3676422CAD0563E74B5981F0DF8B334E698685AAD
class SectionTable:
	MEDIA_SIZE = 0x200
	def __init__(self, raw_section_table):
		media_start_offset = read_u32(raw_section_table, 0x0)
		media_end_offset   = read_u32(raw_section_table, 0x4)
		self.start_offset = media_start_offset * self.MEDIA_SIZE
		self.end_offset   = media_end_offset * self.MEDIA_SIZE

	def gen(self):
		table = b''
		table += pk_u32(self.start_offset / self.MEDIA_SIZE)
		table += pk_u32(self.end_offset / self.MEDIA_SIZE)
		table += 0x8 * b'\xFF'
		return table

class SectionHeader:
	SECTION_HEADER_LENGTH = 0x138
	part_types = {
		0: 'RomFS',
		1: 'PFS0'
	}
	fs_types = {
		2: 'PFS0',
		3: 'RomFS'
	}
	crypto_types = {
		1: 'None',
		2: 'XTS',
		3: 'CTR',
		4: 'BKTR'
	}
	def __init__(self, raw_section_header, section_table):
		self.offset = section_table.start_offset
		self.size   = section_table.end_offset - self.offset

		self.part_type		= self.part_types[read_u8(raw_section_header, 0x2)]
		self.fs_type		  = self.fs_types[read_u8(raw_section_header, 0x3)]
		self.crypto_type	  = self.crypto_types[read_u8(raw_section_header, 0x4)]
		raw_superblock		= io.BytesIO(read_at(raw_section_header, 0x8, self.SECTION_HEADER_LENGTH))
		self.section_ctr	  = read_u64(raw_section_header, 0x140)

		if self.fs_type == 'PFS0':
			self.superblock = PFS0Superblock(raw_superblock)
			self.fs_offset = self.superblock.offset
			self.fs_size   = self.superblock.size
		elif self.fs_type == 'RomFS':
			self.superblock = IVFCSuperblock(raw_superblock)
			self.fs_offset = self.superblock.lvls[-1].offset
			self.fs_size   = self.superblock.lvls[-1].size

class NCAHeader:
	content_types = {
		0: 'Program',
		1: 'Meta',
		2: 'Control',
		3: 'Manual',
		4: 'Data',
		5: 'PublicData'
	}
	def __init__(self, raw_header):
		self.rsa_sig_1	 = read_at(raw_header, 0x0, 0x100)
		self.rsa_sig_2	 = read_at(raw_header, 0x100, 0x100)
		self.magic		 = read_at(raw_header, 0x200, 0x4)
		self.is_game_card  = bool(read_u8(raw_header, 0x204))
		self.content_type  = self.content_types[read_u8(raw_header, 0x205)]
		self.crypto_type   = read_u8(raw_header, 0x206)
		self.kaek_ind	  = read_u8(raw_header, 0x207)
		self.size		  = read_u64(raw_header, 0x208)
		self.tid		   = read_u64(raw_header, 0x210)
		self.sdk_rev	   = '.'.join(str(read_u8(raw_header, 0x21C + n)) for n in range(4))[::-1]
		self.crypto_type_2 = read_u8(raw_header, 0x220)
		self.sig_key_gen = read_u8(raw_header, 0x221)
		self.rights_id	 = read_at(raw_header, 0x230, 0x10)

		self.section_tables = []
		for n in range(4):
			raw_section_table = io.BytesIO(read_at(raw_header, 0x240 + 0x10 * n, 0x10))
			self.section_tables.append(SectionTable(raw_section_table))

		self.hash_table = []
		for n in range(4):
			self.hash_table.append(read_at(raw_header, 0x280 + n * 0x20, 0x20))
		self.enc_key_area = read_at(raw_header, 0x300, 0x40)

		self.section_headers = []
		for n in range(4):
			if self.section_tables[n].start_offset: # Sections exists
				raw_section_header = io.BytesIO(read_at(raw_header, 0x400 + n * FS_HEADER_LENGTH, FS_HEADER_LENGTH))
				self.section_headers.append(SectionHeader(raw_section_header, self.section_tables[n]))

class NCA3:
	'''Class for manipulating NCA3 files'''
	kaeks = {
		0: keys['key_area_key_application_source'],
		1: keys['key_area_key_ocean_source'],
		2: keys['key_area_key_system_source']
	}
	def __init__(self, fp,ifo=0,name='nca',titlekey=None,buffer=65536,verify=False):
		# print(str(fp))
		# print(str(ifo))
		# print(str(name))
		self.f = fp
		self.ifo=int(ifo)
		self.buffer=buffer
		if name=='nca':
			self.name=self.f.name
		else:
			self.name=name

		self.is_valid = True

		self._parse(titlekey=titlekey, verify=verify)

	def __str__(self):
		string = '%s:\n' % os.path.basename(self.name)
		string += '  Size:				%s\n'	% bytes2human(self.header.size)
		string += '  Content type:		%s\n'	% self.header.content_type
		string += '  Title ID:			%016x\n' % self.header.tid
		if self.has_rights_id:
			string += '  Rights ID:		   %032x\n' % self.rights_id
		string += '  Master key revision: %d\n'	% self.crypto_type
		string += '  Encryption type:	 %s\n'	% ('Titlekey' if self.has_rights_id else 'Standard')
		if self.has_rights_id and not self.has_tkey:
			string += 'Titlekey not available'
			return string
		string += '  Body key:			%s\n\n'	% hx(self.body_key).decode()
		for n, sec in enumerate(self.sections):
			string += 'Section %d: %s (%s)\n' % (
				n,
				('ExeFS' if sec.is_exefs else sec.fs_type),
				bytes2human(sec.size)
			)
			if sec.section_header.fs_type == 'RomFS':
				string += '  Directories: %d\n' % sec.fs.dir_nb
			string += '  Files:	   %d\n' % sec.fs.file_nb
		return string

	def print_more(self):
		print('%s:' % os.path.basename(self.name))
		print('  Content type:		%s'	 % self.header.content_type)
		print('  Size:				%s'	 % bytes2human(self.header.size))
		print('  Distribution Type:   %s'	 % ('Gamecard' if self.header.is_game_card else 'Digital'))
		print('  Title ID:			%016x'  % self.header.tid)
		if self.has_rights_id:
			print('  Rights ID:		   %032x' % self.rights_id)
		print('  Master key revision: %d'	 % self.crypto_type)
		print('  Encryption type:	 %s'	 % ('Titlekey' if self.has_rights_id else 'Standard'))
		if self.has_rights_id and not self.has_tkey:
			print('Titlekey not available')
			return
		print('  Body key:			%s'	 % hx(self.body_key).decode())
		print(memdump(self.header.rsa_sig_1, message='  Fixed key signature: ', length=32))
		print(memdump(self.header.rsa_sig_2, message='  NPDM signature:	  ', length=32))
		print()
		for n, sec in enumerate(self.sections):
			print('Section %d (%s):'	  % (n, bytes2human(sec.size)))
			print('  Type:		 %s'	% ('ExeFS' if sec.is_exefs else sec.fs_type))
			print('  Counter:	  %032x' % ((int.from_bytes(sec.nonce, byteorder='big') << 64) + (sec.section_offset >> 4)))
			print('  Offset:	   0x%x'  % sec.offset_in_cont)
			if sec.section_header.fs_type == 'RomFS':
				print('  Block Size:   0x%x' % sec.section_header.superblock.lvls[0].block_size)
				print('  Directories:  %d'   % sec.fs.dir_nb)
			else:
				print('  Block Size:   0x%x' % sec.section_header.superblock.block_size)
			print('  Files:		%d' % sec.fs.file_nb)
			print(str(sec.fs))
			print()

	def _decrypt_keyarea(self, enc_key_area):
		area_key = gen_aes_kek(self.kaek, self.mkey, keys['aes_kek_generation_source'], keys['aes_key_generation_source'])
		return AES.new(area_key, AES.MODE_ECB).decrypt(enc_key_area)

	def _decrypt_tkey(self, enc_tkey):
		return AES.new(self.tkek, AES.MODE_ECB).decrypt(enc_tkey)

	def _decrypt_header(self):
		self.f.seek(self.ifo+0)
		header_keys = keys['nca_header_key'][:0x10], keys['nca_header_key'][0x10:]
		cipher = AESXTSN(header_keys)
		return cipher.decrypt(self.f.read(0xC00))

	def _parse(self, titlekey=None, verify=False):
		raw_header = self._decrypt_header()
		self.header = NCAHeader(io.BytesIO(raw_header))

		if self.header.magic != b'NCA3':
			raise ValueError('Invalid NCA3 magic')

		if self.header.crypto_type_2 > self.header.crypto_type:
			self.crypto_type = self.header.crypto_type_2
		else:
			self.crypto_type = self.header.crypto_type
		if self.crypto_type > 0:
			self.crypto_type -= 1
		self.mkey = keys['master_key_%02x' % self.crypto_type]

		if titlekey is not None:
			#print(hx(titlekey))
			self.body_key = titlekey
			if self.header.rights_id != 0x10 * b'\0':
				self.has_rights_id = True
			else:
				self.has_rights_id = False
				self.kaek = self.kaeks[self.header.kaek_ind]
				keyblob = self._decrypt_keyarea(self.header.enc_key_area)
				self.key_area = b''.join(keyblob[0x10 * n : 0x10 * (n + 1)] for n in range(4))
		elif self.header.rights_id == 0x10 * b'\0':
			self.has_rights_id = False
			self.kaek = self.kaeks[self.header.kaek_ind]
			keyblob = self._decrypt_keyarea(self.header.enc_key_area)
			self.key_area = b''.join(keyblob[0x10 * n : 0x10 * (n + 1)] for n in range(4))
			self.body_key = self.key_area[0x20:0x30]
			#print(hx(keyblob))
			#print(hx(self.key_area))
			#print(hx(self.body_key))
		else:
			if self.header.rights_id != 0x10 * b'\0':
				self.has_rights_id = True
				self.rights_id = int.from_bytes(self.header.rights_id, byteorder='big')
				self.tkek = keys['titlekek_%02x' % self.crypto_type]
				if titlekey is not None:
					self.enc_tkey = uhx(titlekey)
				else:
					try:
						self.enc_tkey = tkeys['%032x' % self.rights_id]
					except KeyError:
						self.has_tkey = False
						return
				self.has_tkey = True
				self.body_key = self._decrypt_tkey(self.enc_tkey)
		self.sections = []
		if verify:
			self.is_valid = True
		for n, section_header in enumerate(self.header.section_headers):
			self.sections.append(self.SectionInNCA3(self, section_header, verify=verify,ifo=self.ifo))
			if verify and not self.sections[n].fs.is_valid:
				self.is_valid = False

		if verify:
			if self.header.sig_key_gen == 0:
				mod = int(hx(keys['nca_header_fixed_key_modulus_00']), 16)
			else:
				mod = int(hx(keys['nca_header_fixed_key_modulus_01']), 16)
			if not validate_rsa2048_pss_sig(mod, RSA_PUBLIC_EXPONENT, raw_header[0x200:0x400], self.header.rsa_sig_1):
				self.is_valid = False
				print('[WARN] Invalid fixed key signature')
			for sec in self.sections:
				if sec.is_exefs:
					npdm = NPDM(sec.fs.open('main.npdm'))
					mod = int.from_bytes(npdm.acid.rsa_pubk, byteorder='big')
					if not validate_rsa2048_pss_sig(mod, RSA_PUBLIC_EXPONENT, raw_header[0x200:0x400], self.header.rsa_sig_2):
						self.is_valid = False
						print('[WARN] Invalid ACID signature')

	def decrypt_to_plaintext(self, out_f, disp=True):
		if disp:
			print('Decrypting %s to plaintext...' % os.path.basename(self.name))
		t = tqdm(total=self.header.size, unit='B', unit_scale=True, leave=False)
		out = open(out_f, 'wb')
		out.write(self._decrypt_header())
		t.update(int(0x300))
		if not self.has_rights_id: # Write the decrypted key area
			out.seek(self.ifo+0x300)
			out.write(self.key_area)
			t.update(len(self.key_area))
		t.write(' > Parsing nca this may take some time...')
		for _, sec in enumerate(self.sections):
			out.seek(self.ifo+sec.offset_in_cont)
			for buf in sec.decrypt_raw():
				out.write(buf)
				t.update(len(buf))
		t.close()
		out.close()
		if disp:
			print('Decrypted to %s' % out.name)

	def ret_npdm(self):
		for _, sec in enumerate(self.sections):
			if sec.is_exefs:
				npdm = NPDM(sec.fs.open('main.npdm'))
				n=npdm.ret
				return n

	def ret_main(self):
		for _, sec in enumerate(self.sections):
			if sec.is_exefs:
				npdm = NPDM(sec.fs.open('main'))
				n=npdm.ret
				return n

	def print_npdm(self):
		for _, sec in enumerate(self.sections):
			#print(_)
			#print(sec.fs_type)
			if sec.is_exefs:
				npdm = NPDM(sec.fs.open('main.npdm'))
				n=npdm.__str__()
				print(n)
				return n

	def decrypt_raw_sections(self, out_dir, disp=True):
		os.makedirs(out_dir, exist_ok=True)
		for n, sec in enumerate(self.sections):
			dest = os.path.join(out_dir, '.'.join((str(n), 'sec')))
			if disp:
				print('Decrypting raw section %d to %s...' % (n, dest))
			with open(dest, 'wb') as out:
				for buf in sec.decrypt_raw():
					out.write(buf)
		if disp:
			print('Decrypted to %s.' % out_dir)

	def decrypt_raw_conts(self, out_dir, disp=True):
		os.makedirs(out_dir, exist_ok=True)
		for n, sec in enumerate(self.sections):
			dest = os.path.join(out_dir, '.'.join((str(n), sec.fs_type.lower())))
			if disp:
				print('Decrypting raw %s partition %d to %s...' % (sec.fs_type.lower(), n, dest))
			with open(dest, 'wb') as out:
				for buf in sec.decrypt_raw_cont():
					out.write(buf)
		if disp:
			print('Decrypted to %s.' % out_dir)

	def extract_conts(self, out_dir, disp=True):

		for n, sec in enumerate(self.sections):
			try:
				dest = os.path.join(out_dir, '%d [%s]' % (n, sec.fs_type.lower()))
				if not os.path.exists(dest):
					os.makedirs(dest)
				if disp:
					print('Extracting files of %s partition %d to %s...' % (sec.fs_type.lower(), n, dest))

				sec.extract_cont(dest)
			except:continue
		if disp:
			print('Extracted to %s.' % out_dir)

	class SectionInNCA3(FileInContainer):
		def __init__(self, nca3, section_header, verify=False,ifo=0,buffer=65536):
			self.nca = nca3
			self.section_header = section_header

			self.key = self.nca.body_key
			self.nonce = pk_u64(self.section_header.section_ctr, endianness='>')

			self.section_offset = self.section_header.offset
			self.section_size   = self.section_header.size
			self.fs_type		= self.section_header.fs_type
			self.crypto		 = self.section_header.crypto_type
			self.ifo=ifo
			self.buffer=buffer

			if self.crypto in ('BTKR', 'XTS'):
				raise NotImplementedError('BTKR/XTS not implemented')

			super(NCA3.SectionInNCA3, self).__init__(self.nca.f, self.section_offset, self.section_size)

			self.is_exefs = False
			if self.fs_type == 'PFS0':
				self.cont_offset = self.section_header.superblock.offset
				self.cont_size   = self.section_header.superblock.size
				self.fs = HashTableWrappedPFS0(self.section_header.superblock, self, verify=verify)
				if 'main.npdm' in self.fs.files:
					self.is_exefs = True
			elif self.fs_type == 'RomFS':
				self.cont_offset = self.section_header.superblock.lvls[IVFCSuperblock.IVFC_MAX_LEVEL-1].offset
				self.cont_size   = self.section_header.superblock.lvls[IVFCSuperblock.IVFC_MAX_LEVEL-1].size
				self.fs = HashTreeWrappedRomFS(self.section_header.superblock, self, verify=verify)

		def update_ctr(self, off):
			self.ctr = Counter.new(64, prefix=self.nonce, initial_value=((self.section_offset + off) >> 4))
			self.cipher = AES.new(self.key, AES.MODE_CTR, counter=self.ctr)

		def seek(self, off):
			if self.crypto == 'None' or self.crypto == 'BTKR' or self.crypto == 'XTS':
				super(NCA3.SectionInNCA3, self).seek(self.ifo+off)
			elif self.crypto == 'CTR':
				block_offset = off & ~0xF
				self.sector_offset = off & 0xF
				super(NCA3.SectionInNCA3, self).seek(self.ifo+block_offset)
				self.update_ctr(block_offset)

		def read(self, length=None):
			if self.crypto == 'None' or self.crypto == 'BTKR' or self.crypto == 'XTS':
				data = super(NCA3.SectionInNCA3, self).read(length)
				return data
			elif self.crypto == 'CTR':
				aligned_length = align_to(length + self.sector_offset, 0x10)
				dec_data = self.cipher.decrypt(super(NCA3.SectionInNCA3, self).read(aligned_length))
				if aligned_length != length:
					try:
						return dec_data[self.sector_offset : length+self.sector_offset]
					finally: # Seek to what the offset should be if not for the crypto
						self.seek(self.ifo+self.tell() - aligned_length + length)
				else:
					return dec_data[:length]

		def _decrypt_from_offset(self, off, size=None):
			self.seek(off+self.ifo)
			read = 0
			while True:
				buf = self.read(self.buffer)
				if not buf:
					break
				if size and (read + len(buf) >= size):
					yield buf[:size - read]
					break
				yield buf
				read += len(buf)

		def decrypt_raw(self):
			for buf in self._decrypt_from_offset(0):
				yield buf

		def decrypt_raw_cont(self):
			for buf in self._decrypt_from_offset(self.cont_offset, self.cont_size):
				yield buf

		def extract_cont(self, dest=None):
			self.fs.extract(dest, disp=False)
