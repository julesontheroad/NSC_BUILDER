import aes128
import Title
import Titles
import Hex
import math
from binascii import hexlify as hx, unhexlify as uhx
from struct import pack as pk, unpack as upk
from hashlib import sha256
import Fs.Type
import os
import re
import pathlib
import Keys
import Config
import Print
import Nsps
from tqdm import tqdm
import Fs
from Fs.File import File
from Fs.Rom import Rom
from Fs.Pfs0 import Pfs0
from Fs.BaseFs import BaseFs
from Fs.Ticket import Ticket
import sq_tools

MEDIA_SIZE = 0x200
indent = 1
tabs = '\t' * indent	


class SectionTableEntry:
	def __init__(self, d):
		self.mediaOffset = int.from_bytes(d[0x0:0x4], byteorder='little', signed=False)
		self.mediaEndOffset = int.from_bytes(d[0x4:0x8], byteorder='little', signed=False)
		
		self.offset = self.mediaOffset * MEDIA_SIZE
		self.endOffset = self.mediaEndOffset * MEDIA_SIZE
		
		self.unknown1 = int.from_bytes(d[0x8:0xc], byteorder='little', signed=False)
		self.unknown2 = int.from_bytes(d[0xc:0x10], byteorder='little', signed=False)
		self.sha1 = None
		
	
def GetSectionFilesystem(buffer, cryptoKey):
	fsType = buffer[0x3]
	if fsType == Fs.Type.Fs.PFS0:
		return Fs.Pfs0(buffer, cryptoKey = cryptoKey)
		
	if fsType == Fs.Type.Fs.ROMFS:
		return Fs.Rom(buffer, cryptoKey = cryptoKey)
		
	return BaseFs(buffer, cryptoKey = cryptoKey)
	
class NcaHeader(File):
	def __init__(self, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		self.signature1 = None
		self.signature2 = None
		self.magic = None
		self.isGameCard = None
		self.contentType = None
		self.cryptoType = None
		self.keyIndex = None
		self.size = None
		self.titleId = None
		self.sdkVersion = None
		self.cryptoType2 = None
		self.rightsId = None
		self.titleKeyDec = None
		self.masterKey = None
		self.sectionTables = []
		self.keys = []
		
		super(NcaHeader, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)
		
	def open(self, file = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(NcaHeader, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()
		self.signature1 = self.read(0x100)
		self.signature2 = self.read(0x100)
		self.magic = self.read(0x4)
		self.isGameCard = self.readInt8()
		self.contentType = self.readInt8()

		try:
			self.contentType = Fs.Type.Content(self.contentType)
		except:
			pass

		self.cryptoType = self.readInt8()
		self.keyIndex = self.readInt8()
		self.size = self.readInt64()
		self.titleId = hx(self.read(8)[::-1]).decode('utf-8').upper()
		
		self.readInt32() # padding
		

		self.sdkVersion = self.readInt32()
		self.cryptoType2 = self.readInt8()
		
		self.read(0xF) # padding
		
		self.rightsId = hx(self.read(0x10))
		
		if self.magic not in [b'NCA3', b'NCA2']:
			raise Exception('Failed to decrypt NCA header: ' + str(self.magic))
		
		self.sectionHashes = []
		
		for i in range(4):
			self.sectionTables.append(SectionTableEntry(self.read(0x10)))
			
		for i in range(4):
			self.sectionHashes.append(self.sectionTables[i])

		self.masterKey = (self.cryptoType if self.cryptoType > self.cryptoType2 else self.cryptoType2)-1

		if self.masterKey < 0:
			self.masterKey = 0
		
		
		self.encKeyBlock = self.getKeyBlock()
		#for i in range(4):
		#	offset = i * 0x10
		#	key = encKeyBlock[offset:offset+0x10]
		#	Print.info('enc %d: %s' % (i, hx(key)))

		if Keys.keyAreaKey(self.masterKey, self.keyIndex):
			crypto = aes128.AESECB(Keys.keyAreaKey(self.masterKey, self.keyIndex))
			self.keyBlock = crypto.decrypt(self.encKeyBlock)
			self.keys = []
			for i in range(4):
				offset = i * 0x10
				key = self.keyBlock[offset:offset+0x10]
				#Print.info('dec %d: %s' % (i, hx(key)))
				self.keys.append(key)
		else:
			self.keys = [None, None, None, None, None, None, None]
		

		if self.hasTitleRights():
			if self.titleId.upper() in Titles.keys() and Titles.get(self.titleId.upper()).key:
				self.titleKeyDec = Keys.decryptTitleKey(uhx(Titles.get(self.titleId.upper()).key), self.masterKey)
			else:
				pass
				#Print.info('could not find title key!')
		else:
			self.titleKeyDec = self.key()

	def key(self):
		return self.keys[2]
		return self.keys[self.cryptoType]

	def hasTitleRights(self):
		return self.rightsId != (b'0' * 32)

	def getKeyBlock(self):
		self.seek(0x300)
		return self.read(0x40)

	def getKB1L(self):
		self.seek(0x300)
		return self.read(0x10)		

	def setKeyBlock(self, value):
		if len(value) != 0x40:
			raise IOError('invalid keyblock size')
		self.seek(0x300)
		return self.write(value)

	def getCryptoType(self):
		self.seek(0x206)
		return self.readInt8()

	def setCryptoType(self, value):
		self.seek(0x206)
		self.writeInt8(value)
		
	def setgamecard(self, value):
		self.seek(0x204)
		self.writeInt8(value)
		
	def getgamecard(self):
		self.seek(0x204)
		return self.readInt8()

	def getCryptoType2(self):
		self.seek(0x220)
		return self.readInt8()

	def setCryptoType2(self, value):
		self.seek(0x220)
		self.writeInt8(value)

	def getRightsId(self):
		self.seek(0x230)
		return self.readInt128('big')

	def setRightsId(self, value):
		self.seek(0x230)
		self.writeInt128(value, 'big')
			
	def get_hblock_hash(self):
		self.seek(0x280)
		return self.read(0x20)
		
	def set_hblock_hash(self, value):
		self.seek(0x280)
		return self.write(value)		

	def calculate_hblock_hash(self):
		indent = 2
		tabs = '\t' * indent
		self.seek(0x400)
		hblock = self.read(0x200)	 
		sha=sha256(hblock).hexdigest()		
		sha_hash= bytes.fromhex(sha)
		#Print.info(tabs + 'calculated header block hash: ' + str(hx(sha_hash)))
		return sha_hash 
		
	def get_hblock_version(self):
		self.seek(0x400)
		return self.read(0x02)	
		
	def get_hblock_filesystem(self):
		self.seek(0x403)
		return self.read(0x01)	

	def get_hblock_hash_type(self):
		self.seek(0x404)
		return self.read(0x01)	
		
	def get_hblock_crypto_type(self):
		self.seek(0x405)
		return self.read(0x01)	
		
	def get_htable_hash(self):
		self.seek(0x408)
		return self.read(0x20)	

	def set_htable_hash(self, value):
		self.seek(0x408)
		return self.write(value)		
	
	def get_hblock_block_size(self):
		self.seek(0x428)
		return self.readInt32()

	def get_hblock_uk1(self):
		self.seek(0x42C)
		return self.read(0x04)			

	def get_htable_offset(self):
		self.seek(0x430)
		return self.readInt64()	
		
	def get_htable_size(self):
		self.seek(0x438)
		return self.readInt64()				
	
	def get_pfs0_offset(self):
		self.seek(0x440)
		return self.readInt64()			
		
	def get_pfs0_size(self):
		self.seek(0x448)
		return self.readInt64()			


class Nca(File):
	def __init__(self, path = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		self.header = None
		self.sectionFilesystems = []
		super(Nca, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)
			
	def __iter__(self):
		return self.sectionFilesystems.__iter__()
		
	def __getitem__(self, key):
		return self.sectionFilesystems[key]

	def open(self, file = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):

		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)

		self.header = NcaHeader()
		self.partition(0x0, 0xC00, self.header, Fs.Type.Crypto.XTS, uhx(Keys.get('header_key')))
		#Print.info('partition complete, seeking')
		
		self.header.seek(0x400)
		#Print.info('reading')
		#Hex.dump(self.header.read(0x200))
		#exit()

		for i in range(4):
			fs = GetSectionFilesystem(self.header.read(0x200), cryptoKey = self.header.titleKeyDec)
			#Print.info('fs type = ' + hex(fs.fsType))
			#Print.info('fs crypto = ' + hex(fs.cryptoType))
			#Print.info('st end offset = ' + str(self.header.sectionTables[i].endOffset - self.header.sectionTables[i].offset))
			#Print.info('fs offset = ' + hex(self.header.sectionTables[i].offset))
			#Print.info('fs section start = ' + hex(fs.sectionStart))
			#Print.info('titleKey = ' + str(hx(self.header.titleKeyDec)))
			try:
				self.partition(self.header.sectionTables[i].offset + fs.sectionStart, self.header.sectionTables[i].endOffset - self.header.sectionTables[i].offset, fs, cryptoKey = self.header.titleKeyDec)
			except BaseException as e:
				pass
				#Print.info(e)
				#raise

			if fs.fsType:
				self.sectionFilesystems.append(fs)
		
		
		self.titleKeyDec = None
		self.masterKey = None

	def get_hblock(self):		
		version = self.header.get_hblock_version()
		Print.info('version: ' + str(int.from_bytes(version, byteorder='little')))
		filesystem = self.header.get_hblock_filesystem()
		Print.info('filesystem: ' + str(int.from_bytes(filesystem, byteorder='little')))
		hash_type = self.header.get_hblock_hash_type()
		Print.info('hash type: ' + str(int.from_bytes(hash_type, byteorder='little')))
		crypto_type = self.header.get_hblock_crypto_type()
		Print.info('crypto type: ' + str(int.from_bytes(crypto_type, byteorder='little')))
		hash_from_htable = self.header.get_htable_hash()
		Print.info('hash from hash table: ' + str(hx(hash_from_htable)))
		block_size = self.header.get_hblock_block_size()
		Print.info('block size in bytes: ' + str(hx(block_size.to_bytes(8, byteorder='big'))))
		v_unkn1 = self.header.get_hblock_uk1()
		htable_offset = self.header.get_htable_offset()
		Print.info('hash table offset: ' +  str(hx(htable_offset.to_bytes(8, byteorder='big'))))
		htable_size = self.header.get_htable_size()
		Print.info('Size of hash-table: ' +  str(hx(htable_size.to_bytes(8, byteorder='big'))))			
		pfs0_offset = self.header.get_pfs0_offset()
		Print.info('Pfs0 offset: ' +  str(hx(pfs0_offset.to_bytes(8, byteorder='big'))))	
		pfs0_size = self.header.get_pfs0_size()
		Print.info('Pfs0 size: ' +  str(hx(pfs0_size.to_bytes(8, byteorder='big'))))	
			
		
	def get_pfs0_hash_data(self):	
		block_size = self.header.get_hblock_block_size()
		#Print.info('block size in bytes: ' + str(hx(block_size.to_bytes(8, byteorder='big'))))
		pfs0_size = self.header.get_pfs0_size()
		#Print.info('Pfs0 size: ' +  str(hx(pfs0_size.to_bytes(8, byteorder='big'))))
		multiplier=pfs0_size/block_size
		multiplier=math.ceil(multiplier)
		#Print.info('Multiplier: ' +  str(multiplier))
		return pfs0_size,block_size,multiplier
		
	def pfs0_MULT(self):	
		block_size = self.header.get_hblock_block_size()
		#Print.info('block size in bytes: ' + str(hx(block_size.to_bytes(8, byteorder='big'))))
		pfs0_size = self.header.get_pfs0_size()
		#Print.info('Pfs0 size: ' +  str(hx(pfs0_size.to_bytes(8, byteorder='big'))))
		multiplier=pfs0_size/block_size
		multiplier=math.ceil(multiplier)
		#Print.info('Multiplier: ' +  str(multiplier))
		return multiplier		
	
	def get_pfs0_hash(self, file = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):		
		mult=self.pfs0_MULT()
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(0xC00+self.header.get_htable_offset())
		hash_from_pfs0=self.read(0x20*mult)
		return hash_from_pfs0
		
	def calc_htable_hash(self):		
		indent = 2
		tabs = '\t' * indent
		htable = self.get_pfs0_hash()
		sha=sha256(htable).hexdigest()		
		sha_hash= bytes.fromhex(sha)
		#Print.info(tabs + 'calculated table hash: ' + str(hx(sha_hash)))
		return sha_hash		

	def calc_pfs0_hash(self, file = None, mode = 'rb'):	
		mult=self.pfs0_MULT()
		indent = 2
		tabs = '\t' * indent
		for f in self:
			cryptoType2=f.get_cryptoType()
			cryptoKey2=f.get_cryptoKey()	
			cryptoCounter2=f.get_cryptoCounter()
		super(Nca, self).open(file, mode, cryptoType2, cryptoKey2, cryptoCounter2)
		pfs0_offset = self.header.get_pfs0_offset()
		pfs0_size = self.header.get_pfs0_size()
		block_size = self.header.get_hblock_block_size()
		self.seek(0xC00+self.header.get_htable_offset()+pfs0_offset)
		if mult>1:
			pfs0=self.read(block_size)
		else:
			pfs0=self.read(pfs0_size)
		sha=sha256(pfs0).hexdigest()
		#Print.info('caculated hash from pfs0: ' + sha)	
		sha_signature = bytes.fromhex(sha)
		#Print.info(tabs + 'calculated hash from pfs0: ' + str(hx(sha_signature)))
		return sha_signature
		
	def set_pfs0_hash(self,value):
		file = None	
		mode = 'r+b'
		for f in self:
			cryptoType2=f.get_cryptoType()
			cryptoKey2=f.get_cryptoKey()	
			cryptoCounter2=f.get_cryptoCounter()
		super(Nca, self).open(file, mode, cryptoType2, cryptoKey2, cryptoCounter2)
		self.seek(0xC00+self.header.get_htable_offset())
		self.write(value)		
	
	def get_req_system(self, file = None, mode = 'rb'):	
		indent = 1
		tabs = '\t' * indent
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()		
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset+0x28)		
		min_sversion=self.readInt32()
		#Print.info(tabs + 'RequiredSystemVersion = ' + str(min_sversion))
		return min_sversion		

	def write_req_system(self, verNumber):
		indent = 1
		tabs = '\t' * indent
		file = None
		mode = 'r+b'	
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset+0x28)	
		min_sversion=self.readInt32()
		#Print.info('Original RequiredSystemVersion = ' + str(min_sversion))
		self.seek(cmt_offset+0x28)	
		self.writeInt64(verNumber)
		self.seek(cmt_offset+0x28)	
		min_sversion=self.readInt32()
		#Print.info(tabs + 'New RequiredSystemVersion = ' + str(min_sversion))
		return min_sversion

	def write_version(self, verNumber):
		indent = 1
		tabs = '\t' * indent
		file = None
		mode = 'r+b'	
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset)
		titleid=self.readInt64()
		tnumber = verNumber.to_bytes(0x04, byteorder='little')
		titleversion = self.write(tnumber)
		self.seek(cmt_offset)
		titleid=self.readInt64()
		titleversion = self.read(0x4)
		Print.info('version = ' + str(int.from_bytes(titleversion, byteorder='little')))
		return titleversion			
		
	def removeTitleRightsnca(self, masterKeyRev, titleKeyDec):
		Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))
		Print.info('writing masterKeyRev for %s, %d' % (str(self._path),  masterKeyRev))
		crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), self.header.keyIndex))
		encKeyBlock = crypto.encrypt(titleKeyDec * 4)
		self.header.setRightsId(0)
		self.header.setKeyBlock(encKeyBlock)
		Hex.dump(encKeyBlock)		
		
	def printtitleId(self, indent = 0):	
		Print.info(str(self.header.titleId))
		
	def print_nca_type(self, indent = 0):	
		Print.info(str(self.header.contentType))
			
	def cardstate(self, indent = 0):	
		Print.info(hex(self.header.isGameCard))
		
	def read_pfs0_header(self, file = None, mode = 'rb'):
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()		
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset)
		pfs0_magic = self.read(4)
		pfs0_nfiles=self.readInt32()
		pfs0_table_size=self.readInt32()
		pfs0_reserved=self.read(0x4)
		Print.info('PFS0 Magic = ' + str(pfs0_magic))
		Print.info('PFS0 number of files = ' + str(pfs0_nfiles))
		Print.info('PFS0 string table size = ' + str(hx(pfs0_table_size.to_bytes(4, byteorder='big'))))
		for i in range(pfs0_nfiles):
			Print.info('........................')							
			Print.info('PFS0 Content number ' + str(i+1))
			Print.info('........................')
			f_offset = self.readInt64()
			Print.info('offset = ' + str(hx(f_offset.to_bytes(8, byteorder='big'))))
			f_size = self.readInt32()
			Print.info('Size =\t' +  str(hx(pfs0_table_size.to_bytes(4, byteorder='big'))))
			filename_offset = self.readInt32()
			Print.info('offset of filename = ' + str(hx(f_offset.to_bytes(8, byteorder='big'))))
			f_reserved= self.read(0x4)

	def read_cnmt(self, file = None, mode = 'rb'):
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		pfs0_size = self.header.get_pfs0_size()		
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset)
		titleid=self.readInt64()
		titleversion = self.read(0x4)
		type_n = self.read(0x1)		
		self.seek(cmt_offset+0xE)
		offset=self.readInt16()
		content_entries=self.readInt16()
		meta_entries=self.readInt16()
		self.seek(cmt_offset+0x20)
		original_ID=self.readInt64()
		self.seek(cmt_offset+0x28)					
		min_sversion=self.readInt32()
		length_of_emeta=self.readInt32()		
		Print.info('')	
		Print.info('...........................................')								
		Print.info('Reading: ' + str(self._path))
		Print.info('...........................................')							
		Print.info('titleid = ' + str(hx(titleid.to_bytes(8, byteorder='big'))))
		Print.info('version = ' + str(int.from_bytes(titleversion, byteorder='little')))
		Print.info('type number = ' + str(hx(type_n)))		
		Print.info('Table offset = '+ str(hx((offset+0x20).to_bytes(2, byteorder='big'))))
		Print.info('number of content = '+ str(content_entries))
		Print.info('number of meta entries = '+ str(meta_entries))
		Print.info('Application id\Patch id = ' + str(hx(original_ID.to_bytes(8, byteorder='big'))))
		Print.info('RequiredVersion = ' + str(min_sversion))
		Print.info('Length of exmeta = ' + str(length_of_emeta))		
		self.seek(cmt_offset+offset+0x20)
		for i in range(content_entries):
			Print.info('........................')							
			Print.info('Content number ' + str(i+1))
			Print.info('........................')
			vhash = self.read(0x20)
			Print.info('hash =\t' + str(hx(vhash)))
			NcaId = self.read(0x10)
			Print.info('NcaId =\t' + str(hx(NcaId)))
			size = self.read(0x6)
			Print.info('Size =\t' + str(int.from_bytes(size, byteorder='little', signed=True)))
			ncatype = self.read(0x1)
			Print.info('ncatype = ' + str(int.from_bytes(ncatype, byteorder='little', signed=True)))
			unknown = self.read(0x1)	
			
		self.seek(pfs0_offset+pfs0_size-0x20)			
		digest = self.read(0x20)
		Print.info("")	
		Print.info('digest= '+str(hx(digest)))
		Print.info("")		
		self.seek(cmt_offset+offset+0x20+content_entries*0x38)			
		if length_of_emeta>0:
			Print.info('----------------')			
			Print.info('Extended meta')	
			Print.info('----------------')				
			num_prev_cnmt=self.read(0x4)
			num_prev_delta=self.read(0x4)
			num_delta_info=self.read(0x4)
			num_delta_application =self.read(0x4)	
			num_previous_content=self.read(0x4)		
			num_delta_content=self.read(0x4)	
			self.read(0x4)	
			Print.info('Number of previous cnmt entries = ' + str(int.from_bytes(num_prev_cnmt, byteorder='little')))	
			Print.info('Number of previous delta entries = ' + str(int.from_bytes(num_prev_delta, byteorder='little')))	
			Print.info('Number of delta info entries = ' + str(int.from_bytes(num_delta_info, byteorder='little')))			
			Print.info('Number of delta application info entries = ' + str(int.from_bytes(num_delta_application, byteorder='little')))	
			Print.info('Number of previous content entries = ' + str(int.from_bytes(num_previous_content, byteorder='little')))	
			Print.info('Number of delta content entries = ' + str(int.from_bytes(num_delta_content, byteorder='little')))			
			for i in range(int.from_bytes(num_prev_cnmt, byteorder='little')):
				Print.info('...........................................')								
				Print.info('Previous cnmt records: '+ str(i+1))
				Print.info('...........................................')				
				titleid=self.readInt64()	
				titleversion = self.read(0x4)	
				type_n = self.read(0x1)					
				unknown1=self.read(0x3)
				vhash = self.read(0x20)
				unknown2=self.read(0x2)
				unknown3=self.read(0x2)
				unknown4=self.read(0x4)				
				Print.info('titleid = ' + str(hx(titleid.to_bytes(8, byteorder='big'))))	
				Print.info('version = ' + str(int.from_bytes(titleversion, byteorder='little')))
				Print.info('type number = ' + str(hx(type_n)))	
				#Print.info('unknown1 = ' + str(int.from_bytes(unknown1, byteorder='little')))			
				Print.info('hash =\t' + str(hx(vhash)))				
				Print.info('content nca number = ' + str(int.from_bytes(unknown2, byteorder='little')))				
				#Print.info('unknown3 = ' + str(int.from_bytes(unknown3, byteorder='little')))				
				#Print.info('unknown4 = ' + str(int.from_bytes(unknown4, byteorder='little')))
			for i in range(int.from_bytes(num_prev_delta, byteorder='little')):
				Print.info('...........................................')								
				Print.info('Previous delta records: '+ str(i+1))
				Print.info('...........................................')				
				oldtitleid=self.readInt64()	
				newtitleid=self.readInt64()					
				oldtitleversion = self.read(0x4)	
				newtitleversion = self.read(0x4)	
				size = self.read(0x8)
				unknown1=self.read(0x8)				
				Print.info('old titleid = ' + str(hx(oldtitleid.to_bytes(8, byteorder='big'))))	
				Print.info('new titleid = ' + str(hx(newtitleid.to_bytes(8, byteorder='big'))))						
				Print.info('old version = ' + str(int.from_bytes(oldtitleversion, byteorder='little')))
				Print.info('new version = ' + str(int.from_bytes(newtitleversion, byteorder='little')))	
				Print.info('size = ' + str(int.from_bytes(size, byteorder='little', signed=True)))					
				#Print.info('unknown1 = ' + str(int.from_bytes(unknown1, byteorder='little')))			
			for i in range(int.from_bytes(num_delta_info, byteorder='little')):
				Print.info('...........................................')								
				Print.info('Delta info: '+ str(i+1))
				Print.info('...........................................')				
				oldtitleid=self.readInt64()	
				newtitleid=self.readInt64()					
				oldtitleversion = self.read(0x4)	
				newtitleversion = self.read(0x4)	
				index1=self.readInt64()	
				index2=self.readInt64()				
				Print.info('old titleid = ' + str(hx(oldtitleid.to_bytes(8, byteorder='big'))))	
				Print.info('new titleid = ' + str(hx(newtitleid.to_bytes(8, byteorder='big'))))						
				Print.info('old version = ' + str(int.from_bytes(oldtitleversion, byteorder='little')))
				Print.info('new version = ' + str(int.from_bytes(newtitleversion, byteorder='little')))	
				Print.info('index1 = ' + str(hx(index1.to_bytes(8, byteorder='big'))))	
				Print.info('index2 = ' + str(hx(index2.to_bytes(8, byteorder='big'))))						
				#Print.info('unknown1 = ' + str(int.from_bytes(unknown1, byteorder='little')))
			for i in range(int.from_bytes(num_delta_application, byteorder='little')):
				Print.info('...........................................')								
				Print.info('Delta application info: '+ str(i+1))
				Print.info('...........................................')				
				OldNcaId = self.read(0x10)
				NewNcaId = self.read(0x10)		
				old_size = self.read(0x6)				
				up2bytes = self.read(0x2)
				low4bytes = self.read(0x4)
				unknown1 = self.read(0x2)
				ncatype = self.read(0x1)	
				installable = self.read(0x1)
				unknown2 = self.read(0x4)				
				Print.info('OldNcaId =\t' + str(hx(OldNcaId)))	
				Print.info('NewNcaId =\t' + str(hx(NewNcaId)))	
				Print.info('Old size =\t' +  str(int.from_bytes(old_size, byteorder='little', signed=True)))	
				Print.info('unknown1 =\t' + str(int.from_bytes(unknown1, byteorder='little')))
				Print.info('ncatype =\t' + str(int.from_bytes(ncatype, byteorder='little', signed=True)))
				Print.info('installable =\t' + str(int.from_bytes(installable, byteorder='little', signed=True)))
				Print.info('Upper 2 bytes of the new size=\t' + str(hx(up2bytes)))	
				Print.info('Lower 4 bytes of the new size=\t' + str(hx(low4bytes)))					
				#Print.info('unknown2 =\t' + str(int.from_bytes(unknown2, byteorder='little')))			

			for i in range(int.from_bytes(num_previous_content, byteorder='little')):
				Print.info('...........................................')								
				Print.info('Previous content records: '+ str(i+1))
				Print.info('...........................................')				
				NcaId = self.read(0x10)		
				size = self.read(0x6)				
				ncatype = self.read(0x1)	
				unknown1 = self.read(0x1)				
				Print.info('NcaId = '+ str(hx(NcaId)))	
				Print.info('Size = '+ str(int.from_bytes(size, byteorder='little', signed=True)))	
				Print.info('ncatype = '+ str(int.from_bytes(ncatype, byteorder='little', signed=True)))			
				#Print.info('unknown1 = '+ str(int.from_bytes(unknown1, byteorder='little')))	
				
			for i in range(int.from_bytes(num_delta_content, byteorder='little')):
				Print.info('........................')							
				Print.info('Delta content entry ' + str(i+1))
				Print.info('........................')
				vhash = self.read(0x20)
				Print.info('hash =\t' + str(hx(vhash)))
				NcaId = self.read(0x10)
				Print.info('NcaId =\t' + str(hx(NcaId)))
				size = self.read(0x6)
				Print.info('Size =\t' + str(int.from_bytes(size, byteorder='little', signed=True)))
				ncatype = self.read(0x1)
				Print.info('ncatype = ' + str(int.from_bytes(ncatype, byteorder='little', signed=True)))
				unknown = self.read(0x1)		
		

	def xml_gen(self,ofolder,nsha):
		file = None
		mode = 'rb'
		crypto1=self.header.getCryptoType()
		crypto2=self.header.getCryptoType2()			
		if crypto2>crypto1:
			keygeneration=crypto2
		if crypto2<=crypto1:	
			keygeneration=crypto1			
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		pfs0_size = self.header.get_pfs0_size()		
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset)
		titleid=self.readInt64()
		titleversion = self.read(0x4)
		type_n = self.read(0x1)		
		self.seek(cmt_offset+0xE)
		offset=self.readInt16()
		content_entries=self.readInt16()
		meta_entries=self.readInt16()
		self.seek(cmt_offset+0x18)		
		RDSV=self.readInt64()		
		self.seek(cmt_offset+0x20)
		original_ID=self.readInt64()
		self.seek(cmt_offset+0x28)					
		min_sversion=self.readInt32()
		length_of_emeta=self.readInt32()		
		self.seek(cmt_offset+offset+0x20)
		
		if str(hx(type_n)) == "b'1'":
			type='SystemProgram'		
		if str(hx(type_n)) == "b'2'":
			type='SystemData'
		if str(hx(type_n)) == "b'3'":
			type='SystemUpdate'
		if str(hx(type_n)) == "b'4'":
			type='BootImagePackage'		
		if str(hx(type_n)) == "b'5'":
			type='BootImagePackageSafe'		
		if str(hx(type_n)) == "b'80'":
			type='Application'			
		if str(hx(type_n)) == "b'81'":
			type='Patch'
		if str(hx(type_n)) == "b'82'":
			type='AddOnContent'
		if str(hx(type_n)) == "b'83'":
			type='Delta'

		titleid=str(hx(titleid.to_bytes(8, byteorder='big')))	
		titleid='0x'+titleid[2:-1]
		version = str(int.from_bytes(titleversion, byteorder='little'))
		RDSV=str(RDSV)
		xmlname = str(self._path)	
		xmlname = xmlname[:-4] + '.xml'	
		outfolder = str(ofolder)+'\\'		
		textpath = os.path.join(outfolder, xmlname)
		with open(textpath, 'w+') as tfile:			
			tfile.write('<?xml version="1.0" encoding="utf-8"?>' + '\n')	
			tfile.write('<ContentMeta>' + '\n')	
			tfile.write('  <Type>'+ type +'</Type>' + '\n')	
			tfile.write('  <Id>'+ titleid +'</Id>' + '\n')	
			tfile.write('  <Version>'+ version +'</Version>' + '\n')
			tfile.write('  <RequiredDownloadSystemVersion>'+ RDSV +'</RequiredDownloadSystemVersion>' + '\n')	
			
		for i in range(content_entries):
			vhash = self.read(0x20)
			NcaId = self.read(0x10)
			size = self.read(0x6)
			ncatype = self.readInt8()
			unknown = self.read(0x1)
			if ncatype==0:
				type='Meta'		
			if str(ncatype)=="1":
				type='Program'		
			if ncatype==2:
				type='Data'		
			if ncatype==3:
				type='Control'		
			if ncatype==4:
				type='HtmlDocument'	
			if ncatype==5:
				type='LegalInformation'		
			if ncatype==6:
				type='DeltaFragment'						
				
			NcaId=str(hx(NcaId))
			NcaId=NcaId[2:-1]
			size=str(int.from_bytes(size, byteorder='little'))
			vhash=str(hx(vhash))
			vhash=vhash[2:-1]			
							
			with open(textpath, 'a') as tfile:	
				tfile.write('  <Content>' + '\n')	
				tfile.write('    <Type>'+ type +'</Type>' + '\n')
				tfile.write('    <Id>'+ NcaId +'</Id>' + '\n')
				tfile.write('    <Size>'+ size +'</Size>' + '\n')				
				tfile.write('    <Hash>'+ vhash +'</Hash>' + '\n')	
				tfile.write('    <KeyGeneration>'+ str(self.header.cryptoType2) +'</KeyGeneration>' + '\n')				
				tfile.write('  </Content>' + '\n')						

		self.seek(pfs0_offset+pfs0_size-0x20)			
		digest = str(hx(self.read(0x20)))
		digest=digest[2:-1]			
		original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
		original_ID='0x'+original_ID[2:-1]	
		metaname=os.path.basename(os.path.abspath(self._path))
		metaname =  metaname[:-9]
		size=str(os.path.getsize(self._path))		
		with open(textpath, 'a') as tfile:	
			tfile.write('  <Content>' + '\n')	
			tfile.write('    <Type>'+ 'Meta' +'</Type>' + '\n')
			tfile.write('    <Id>'+ metaname +'</Id>' + '\n')
			tfile.write('    <Size>'+ size +'</Size>' + '\n')				
			tfile.write('    <Hash>'+ nsha +'</Hash>' + '\n')				
			tfile.write('    <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')					
			tfile.write('  </Content>' + '\n')						
			tfile.write('  <Digest>'+ digest +'</Digest>' + '\n')
			tfile.write('  <KeyGenerationMin>'+ str(keygeneration) +'</KeyGenerationMin>' + '\n')
			tfile.write('  <RequiredSystemVersion>'+ str(min_sversion) +'</RequiredSystemVersion>' + '\n')				
			tfile.write('  <OriginalId>'+ original_ID +'</OriginalId>' + '\n')	
			tfile.write('</ContentMeta>')					
		return textpath

	def xml_gen_mod(self,ofolder,nsha,keygeneration):
		file = None
		mode = 'rb'
		crypto1=self.header.getCryptoType()
		crypto2=self.header.getCryptoType2()						
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		pfs0_size = self.header.get_pfs0_size()		
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset)
		titleid=self.readInt64()
		titleversion = self.read(0x4)
		type_n = self.read(0x1)		
		self.seek(cmt_offset+0xE)
		offset=self.readInt16()
		content_entries=self.readInt16()
		meta_entries=self.readInt16()
		self.seek(cmt_offset+0x18)		
		RDSV=self.readInt64()		
		self.seek(cmt_offset+0x20)
		original_ID=self.readInt64()
		self.seek(cmt_offset+0x28)					
		min_sversion=self.readInt32()
		length_of_emeta=self.readInt32()		
		self.seek(cmt_offset+offset+0x20)
		
		if str(hx(type_n)) == "b'1'":
			type='SystemProgram'		
		if str(hx(type_n)) == "b'2'":
			type='SystemData'
		if str(hx(type_n)) == "b'3'":
			type='SystemUpdate'
		if str(hx(type_n)) == "b'4'":
			type='BootImagePackage'		
		if str(hx(type_n)) == "b'5'":
			type='BootImagePackageSafe'		
		if str(hx(type_n)) == "b'80'":
			type='Application'			
		if str(hx(type_n)) == "b'81'":
			type='Patch'
		if str(hx(type_n)) == "b'82'":
			type='AddOnContent'
		if str(hx(type_n)) == "b'83'":
			type='Delta'

		titleid=str(hx(titleid.to_bytes(8, byteorder='big')))	
		titleid='0x'+titleid[2:-1]
		version = str(int.from_bytes(titleversion, byteorder='little'))
		RDSV=str(RDSV)
		xmlname = str(self._path)	
		xmlname = xmlname[:-4] + '.xml'	
		outfolder = str(ofolder)+'\\'		
		textpath = os.path.join(outfolder, xmlname)
		with open(textpath, 'w+') as tfile:			
			tfile.write('<?xml version="1.0" encoding="utf-8"?>' + '\n')	
			tfile.write('<ContentMeta>' + '\n')	
			tfile.write('  <Type>'+ type +'</Type>' + '\n')	
			tfile.write('  <Id>'+ titleid +'</Id>' + '\n')	
			tfile.write('  <Version>'+ version +'</Version>' + '\n')
			tfile.write('  <RequiredDownloadSystemVersion>'+ RDSV +'</RequiredDownloadSystemVersion>' + '\n')	
			
		for i in range(content_entries):
			vhash = self.read(0x20)
			NcaId = self.read(0x10)
			size = self.read(0x6)
			ncatype = self.readInt8()
			unknown = self.read(0x1)
			if ncatype==0:
				type='Meta'		
			if str(ncatype)=="1":
				type='Program'		
			if ncatype==2:
				type='Data'		
			if ncatype==3:
				type='Control'		
			if ncatype==4:
				type='HtmlDocument'	
			if ncatype==5:
				type='LegalInformation'		
			if ncatype==6:
				type='DeltaFragment'						
				
			NcaId=str(hx(NcaId))
			NcaId=NcaId[2:-1]
			size=str(int.from_bytes(size, byteorder='little'))
			vhash=str(hx(vhash))
			vhash=vhash[2:-1]			
							
			with open(textpath, 'a') as tfile:	
				tfile.write('  <Content>' + '\n')	
				tfile.write('    <Type>'+ type +'</Type>' + '\n')
				tfile.write('    <Id>'+ NcaId +'</Id>' + '\n')
				tfile.write('    <Size>'+ size +'</Size>' + '\n')				
				tfile.write('    <Hash>'+ vhash +'</Hash>' + '\n')	
				tfile.write('    <KeyGeneration>'+ str(self.header.cryptoType2) +'</KeyGeneration>' + '\n')				
				tfile.write('  </Content>' + '\n')						

		self.seek(pfs0_offset+pfs0_size-0x20)			
		digest = str(hx(self.read(0x20)))
		digest=digest[2:-1]			
		original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
		original_ID='0x'+original_ID[2:-1]	
		metaname=os.path.basename(os.path.abspath(self._path))
		metaname =  metaname[:-9]
		size=str(os.path.getsize(self._path))		
		with open(textpath, 'a') as tfile:	
			tfile.write('  <Content>' + '\n')	
			tfile.write('    <Type>'+ 'Meta' +'</Type>' + '\n')
			tfile.write('    <Id>'+ metaname +'</Id>' + '\n')
			tfile.write('    <Size>'+ size +'</Size>' + '\n')				
			tfile.write('    <Hash>'+ nsha +'</Hash>' + '\n')				
			tfile.write('    <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')					
			tfile.write('  </Content>' + '\n')						
			tfile.write('  <Digest>'+ digest +'</Digest>' + '\n')
			tfile.write('  <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')
			min_sversion=sq_tools.getMinRSV(keygeneration,min_sversion)			
			tfile.write('  <RequiredSystemVersion>'+ str(min_sversion) +'</RequiredSystemVersion>' + '\n')				
			tfile.write('  <OriginalId>'+ original_ID +'</OriginalId>' + '\n')	
			tfile.write('</ContentMeta>')					
		return textpath



		
	def ret_xml(self):
		file = None
		mode = 'rb'
		crypto1=self.header.getCryptoType()
		crypto2=self.header.getCryptoType2()			
		if crypto2>crypto1:
			keygeneration=crypto2
		if crypto2<=crypto1:	
			keygeneration=crypto1		
		xmlname = str(self._path)	
		xmlname = xmlname[:-4] + '.xml'
		metaname=str(self._path)
		metaname =  metaname[:-9]		
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		pfs0_size = self.header.get_pfs0_size()		
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset)
		titleid=self.readInt64()
		titleversion = self.read(0x4)
		type_n = self.read(0x1)		
		self.seek(cmt_offset+0xE)
		offset=self.readInt16()
		content_entries=self.readInt16()
		meta_entries=self.readInt16()
		self.seek(cmt_offset+0x18)		
		RDSV=self.readInt64()		
		self.seek(cmt_offset+0x20)
		original_ID=self.readInt64()
		self.seek(cmt_offset+0x28)					
		min_sversion=self.readInt32()
		length_of_emeta=self.readInt32()		
		self.seek(cmt_offset+offset+0x20)
		
		if str(hx(type_n)) == "b'1'":
			type='SystemProgram'		
		if str(hx(type_n)) == "b'2'":
			type='SystemData'
		if str(hx(type_n)) == "b'3'":
			type='SystemUpdate'
		if str(hx(type_n)) == "b'4'":
			type='BootImagePackage'		
		if str(hx(type_n)) == "b'5'":
			type='BootImagePackageSafe'		
		if str(hx(type_n)) == "b'80'":
			type='Application'			
		if str(hx(type_n)) == "b'81'":
			type='Patch'
		if str(hx(type_n)) == "b'82'":
			type='AddOnContent'
		if str(hx(type_n)) == "b'83'":
			type='Delta'

		titleid=str(hx(titleid.to_bytes(8, byteorder='big')))	
		titleid='0x'+titleid[2:-1]
		version = str(int.from_bytes(titleversion, byteorder='little'))
		RDSV=str(RDSV)
	
		xml_string = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
		xml_string += '<ContentMeta>' + '\n'
		xml_string +='  <Type>'+ type +'</Type>' + '\n' 
		xml_string +=('  <Id>'+ titleid +'</Id>' + '\n')	
		xml_string +=('  <Version>'+ version +'</Version>' + '\n')
		xml_string +=('  <RequiredDownloadSystemVersion>'+ RDSV +'</RequiredDownloadSystemVersion>' + '\n')	
			
		for i in range(content_entries):
			vhash = self.read(0x20)
			NcaId = self.read(0x10)
			size = self.read(0x6)
			ncatype = self.readInt8()
			unknown = self.read(0x1)
			if ncatype==0:
				type='Meta'		
			if str(ncatype)=="1":
				type='Program'		
			if ncatype==2:
				type='Data'		
			if ncatype==3:
				type='Control'		
			if ncatype==4:
				type='HtmlDocument'	
			if ncatype==5:
				type='LegalInformation'		
			if ncatype==6:
				type='DeltaFragment'						
				
			NcaId=str(hx(NcaId))
			NcaId=NcaId[2:-1]
			size=str(int.from_bytes(size, byteorder='little'))
			vhash=str(hx(vhash))
			vhash=vhash[2:-1]			
							
			xml_string +=('  <Content>' + '\n')	
			xml_string +=('    <Type>'+ type +'</Type>' + '\n')
			xml_string +=('    <Id>'+ NcaId +'</Id>' + '\n')
			xml_string +=('    <Size>'+ size +'</Size>' + '\n')				
			xml_string +=('    <Hash>'+ vhash +'</Hash>' + '\n')	
			xml_string +=('    <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')				
			xml_string +=('  </Content>' + '\n')						

		self.seek(pfs0_offset+pfs0_size-0x20)			
		digest = str(hx(self.read(0x20)))
		digest=digest[2:-1]			
		original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
		original_ID='0x'+original_ID[2:-1]	
		size=str(os.path.getsize(self._path))	
		
		xml_string +=('  <Content>' + '\n')	
		xml_string +=('    <Type>'+ 'Meta' +'</Type>' + '\n')
		xml_string +=('    <Id>'+ metaname +'</Id>' + '\n')
		xml_string +=('    <Size>'+ size +'</Size>' + '\n')				
		xml_string +=('    <Hash>'+ nsha +'</Hash>' + '\n')				
		xml_string +=('    <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')					
		xml_string +=('  </Content>' + '\n')						
		xml_string +=('  <Digest>'+ digest +'</Digest>' + '\n')
		xml_string +=('  <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')
		xml_string +=('  <RequiredSystemVersion>'+ str(min_sversion) +'</RequiredSystemVersion>' + '\n')				
		xml_string +=('  <OriginalId>'+ original_ID +'</OriginalId>' + '\n')	
		xml_string +=('</ContentMeta>')	
		
		#print(xml_string)
		
		size=len(xml_string)
		
		return xmlname,size,xml_string
		
			
	def printInfo(self, indent = 0):
		tabs = '\t' * indent
		Print.info('\n%sNCA Archive\n' % (tabs))
		super(Nca, self).printInfo(indent)
#		Print.info(tabs + 'Header Block Hash: ' + str(hx(self.header.get_hblock_hash())))
#		self.header.calculate_hblock_hash()
#		self.get_hblock()
#		self.calc_htable_hash()
#		Print.info('hash from pfs0: ' + str(hx(self.get_pfs0_hash())))
#		self.calc_pfs0_hash()
#		self.get_req_system()
#		Print.info(tabs + 'RSA-2048 signature 1 = ' + str(hx(self.header.signature1)))
#		Print.info(tabs + 'RSA-2048 signature 2 = ' + str(hx(self.header.signature2)))
		Print.info(tabs + 'magic = ' + str(self.header.magic))
		Print.info(tabs + 'titleId = ' + str(self.header.titleId))
		Print.info(tabs + 'rightsId = ' + str(self.header.rightsId))
		Print.info(tabs + 'isGameCard = ' + hex(self.header.isGameCard))
		Print.info(tabs + 'contentType = ' + str(self.header.contentType))
		#Print.info(tabs + 'cryptoType = ' + str(self.header.getCryptoType()))
		Print.info(tabs + 'SDK version = ' + str(self.header.sdkVersion))
		Print.info(tabs + 'Size: ' + str(self.header.size))
		Print.info(tabs + 'Crypto-Type1: ' + str(self.header.cryptoType))
		Print.info(tabs + 'Crypto-Type2: ' + str(self.header.cryptoType2))
		Print.info(tabs + 'key Index: ' + str(self.header.keyIndex))
		#Print.info(tabs + 'key Block: ' + str(self.header.getKeyBlock()))
		for key in self.header.keys:
			Print.info(tabs + 'key Block: ' + str(hx(key)))
		
		Print.info('\n%sPartitions:' % (tabs))
		
		for s in self:
			s.printInfo(indent+1)
			
		#self.read_pfs0_header()	
		#self.read_cnmt()


	def ncalist_bycnmt(self, file = None, mode = 'rb'):
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()
		pfs0_offset=0xC00+self.header.get_htable_offset()+self.header.get_pfs0_offset()
		pfs0_size = self.header.get_pfs0_size()		
		super(Nca, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.seek(pfs0_offset+0x8)
		pfs0_table_size=self.readInt32()
		cmt_offset=pfs0_offset+0x28+pfs0_table_size
		self.seek(cmt_offset)
		titleid=self.readInt64()
		titleversion = self.read(0x4)
		type_n = self.read(0x1)		
		self.seek(cmt_offset+0xE)
		offset=self.readInt16()
		content_entries=self.readInt16()
		meta_entries=self.readInt16()
		self.seek(cmt_offset+0x20)
		original_ID=self.readInt64()
		self.seek(cmt_offset+0x28)					
		min_sversion=self.readInt32()
		length_of_emeta=self.readInt32()			
		self.seek(cmt_offset+offset+0x20)
		ncalist=list()
		for i in range(content_entries):
			vhash = self.read(0x20)
			NcaId = self.read(0x10)
			size = self.read(0x6)
			ncatype = self.read(0x1)
			unknown = self.read(0x1)
			nca2append=str(hx(NcaId))
			nca2append=nca2append[2:-1]+'.nca'
			ncalist.append(nca2append)
		nca_meta=str(self._path)	
		ncalist.append(nca_meta)
		return ncalist

	def copy(self,ofolder,buffer):
		i=0
		for f in self:
			self.rewind()			
			f.rewind()
			filename =  str(i)
			i+=1
			outfolder = str(ofolder)+'/'
			filepath = os.path.join(outfolder, filename)
			if not os.path.exists(outfolder):
				os.makedirs(outfolder)
			fp = open(filepath, 'w+b')
			self.rewind()
			f.rewind()	
			for data in iter(lambda: f.read(int(buffer)), ""):
				fp.write(data)
				fp.flush()
				if not data:
					fp.close()
					break	
					
	def get_langueblock(self,title):
		for f in self:
			self.rewind()					
			f.rewind()	
			Langue = list()	
			Langue = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
			SupLg=list()
			regionstr=""
			offset=0x14200
			for i in Langue:
				f.seek(offset+i*0x300)
				test=f.read(0x200)
				test = test.split(b'\0', 1)[0].decode('utf-8')
				test = (re.sub(r'[\/\\]+', ' ', test))
				test = test.strip()
				test2=f.read(0x100)
				test2 = test2.split(b'\0', 1)[0].decode('utf-8')
				test2 = (re.sub(r'[\/\\]+', ' ', test2))
				test2 = test2.strip()					
				if test == "" or test2 == "":	
					offset=0x14400
					f.seek(offset+i*0x300)
					test=f.read(0x200)
					test = test.split(b'\0', 1)[0].decode('utf-8')
					test = (re.sub(r'[\/\\]+', ' ', test))
					test = test.strip()	
					test2=f.read(0x100)
					test2 = test2.split(b'\0', 1)[0].decode('utf-8')
					test2 = (re.sub(r'[\/\\]+', ' ', test2))
					test2 = test2.strip()							
					if test == "" or test2 == "":					
						offset=0x14000
						while offset<=(0x14200+i*0x300):
							offset=offset+0x100
							f.seek(offset+i*0x300)
							test=f.read(0x200)
							test = test.split(b'\0', 1)[0].decode('utf-8')
							test = (re.sub(r'[\/\\]+', ' ', test))
							test = test.strip()
							test2=f.read(0x100)
							test2 = test2.split(b'\0', 1)[0].decode('utf-8')
							test2 = (re.sub(r'[\/\\]+', ' ', test2))
							test2 = test2.strip()										
							if test != "" and test2 != "" :	
								offset=offset
								break
						if test != "":	
							offset=offset
							break			
					if test != "":	
						offset=offset
						break								
				else:
					break
			f.seek(offset+0x3060)	
			ediver = f.read(0x10)
			ediver = ediver.split(b'\0', 1)[0].decode('utf-8')
			ediver = (re.sub(r'[\/\\]+', ' ', ediver))
			ediver = ediver.strip()	
			try:  
				int(ediver[0])+1
			except:
				ediver="-"
			if ediver == '-':
				offset2=offset-0x300
				f.seek(offset2+0x3060)			
				ediver = f.read(0x10)
				ediver = ediver.split(b'\0', 1)[0].decode('utf-8')
				ediver = (re.sub(r'[\/\\]+', ' ', ediver))
				ediver = ediver.strip()	
				try:  
					int(ediver[0])+1
					offset=offset2
				except:
					ediver="-"			
			if ediver == '-':
				try:
					while (offset2+0x3060)<=0x18600:
						offset2+=0x100
						f.seek(offset2+0x3060)	
						ediver = f.read(0x10)
						ediver = ediver.split(b'\0', 1)[0].decode('utf-8')
						ediver = (re.sub(r'[\/\\]+', ' ', ediver))
						ediver = ediver.strip()	
						if ediver != '':
							if str(ediver[0])!='v' and str(ediver[0])!='V':
								try:  
									int(ediver[0])+1
									offset=offset2
									break
								except:
									ediver="-"
									break		
				except:
					ediver="-"					
			Langue = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]				
			for i in Langue:
				f.seek(offset+i*0x300)	
				title = f.read(0x200)		
				title = title.split(b'\0', 1)[0].decode('utf-8')
				title = (re.sub(r'[\/\\]+', ' ', title))
				title = title.strip()
				if title != "":	
					if i==0:
						SupLg.append("US (eng)")
						regionstr+='1|'
					if i==1:
						SupLg.append("UK (eng)")
						regionstr+='1|'							
					if i==2:
						SupLg.append("JP")
						regionstr+='1|'							
					if i==3:
						SupLg.append("FR")	
						regionstr+='1|'					
					if i==4:
						SupLg.append("DE")
						regionstr+='1|'			
					if i==5:
						SupLg.append("LAT (spa)")	
						regionstr+='1|'						
					if i==6:
						SupLg.append("SPA")	
						regionstr+='1|'				
					if i==7:
						SupLg.append("IT")	
						regionstr+='1|'							
					if i==8:
						SupLg.append("DU")	
						regionstr+='1|'					
					if i==9:
						SupLg.append("CAD (fr)")
						regionstr+='1|'						
					if i==10:
						SupLg.append("POR")	
						regionstr+='1|'						
					if i==11:
						SupLg.append("RU")	
						regionstr+='1|'					
					if i==12:
						SupLg.append("KOR")	
						regionstr+='1|'			
					if i==13:
						SupLg.append("TAI")		
						regionstr+='1|'			
					if i==14:
						SupLg.append("CH")	
						regionstr+='1|'
				else:
					regionstr+='0|'	
			Langue = [0,1,6,5,7,10,3,4,9,8,2,11,12,13,14]						
			for i in Langue:
				f.seek(offset+i*0x300)		
				title = f.read(0x200)
				editor = f.read(0x100)							
				title = title.split(b'\0', 1)[0].decode('utf-8')
				title = (re.sub(r'[\/\\]+', ' ', title))
				title = title.strip()
				editor = editor.split(b'\0', 1)[0].decode('utf-8')
				editor = (re.sub(r'[\/\\]+', ' ', editor))
				editor = editor.strip()							
				if title == "":
					title = 'DLC'
				if title != 'DLC':
					title = title
					f.seek(offset+0x3060)	
					ediver = f.read(0x10)
					ediver = ediver.split(b'\0', 1)[0].decode('utf-8')
					ediver = (re.sub(r'[\/\\]+', ' ', ediver))
					ediver = ediver.strip()	
					if ediver == '':
						try:
							while (offset+0x3060)<=0x18600:
								offset+=0x100
								f.seek(offset+0x3060)	
								ediver = f.read(0x10)
								ediver = ediver.split(b'\0', 1)[0].decode('utf-8')
								ediver = (re.sub(r'[\/\\]+', ' ', ediver))
								ediver = ediver.strip()	
								if ediver != '':
									if str(ediver[0])!='v' and str(ediver[0])!='V':
										try:  
											int(ediver[0])+1
											break
										except:
											ediver="-"
											break		
						except:
							ediver="-"
					f.seek(offset+0x3028)	
					isdemo = f.readInt8('little')
					if ediver !='-':
						if isdemo == 0:
							isdemo = 0
						elif isdemo == 1:
							isdemo = 1
						elif isdemo == 2:
							isdemo = 2
						else:
							isdemo = 0
					else:
						isdemo = 0
					return(title,editor,ediver,SupLg,regionstr[:-1],isdemo)
		regionstr="0|0|0|0|0|0|0|0|0|0|0|0|0|0"		
		ediver='-'		
		return(title,"",ediver,"",regionstr,"")			
				
					
					
	'''
	def c_clean(self,ofolder,buffer):
		for f in self:
			cryptoType=f.get_cryptoType()
			cryptoKey=f.get_cryptoKey()	
			cryptoCounter=f.get_cryptoCounter()	
		filename =  str(self._path)
		outfolder = str(ofolder)+'/'
		filepath = os.path.join(outfolder, filename)
		if not os.path.exists(outfolder):
			os.makedirs(outfolder)
		fp = open(filepath, 'w+b')
		self.rewind()
		for data in iter(lambda: self.read(int(buffer)), ""):
			fp.write(data)
			fp.flush()
			if not data:
				fp.close()
				break	
	'''					