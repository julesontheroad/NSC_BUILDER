import aes128
import Title
import Titles
import Hex
from binascii import hexlify as hx, unhexlify as uhx
from struct import pack as pk, unpack as upk
from Fs.File import File
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
from Fs.BaseFs import BaseFs

MEDIA_SIZE = 0x200
indent = 1
tabs = '\t' * indent	
		
class Pfs0(BaseFs):
	def __init__(self, buffer, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Pfs0, self).__init__(buffer, path, mode, cryptoType, cryptoKey, cryptoCounter)
		
		if buffer:
			self.size = int.from_bytes(buffer[0x48:0x50], byteorder='little', signed=False)
			self.sectionStart = int.from_bytes(buffer[0x40:0x48], byteorder='little', signed=False)
		
	def getHeader():
		stringTable = '\x00'.join(file.name for file in self.files)
		
		headerSize = 0x10 + len(self.files) * 0x18 + len(stringTable)
		remainder = 0x10 - headerSize % 0x10
		headerSize += remainder
	
		h = b''
		h += b'PFS0'
		h += len(self.files).to_bytes(4, byteorder='little')
		h += (len(stringTable)+remainder).to_bytes(4, byteorder='little')
		h += b'\x00\x00\x00\x00'
		
		stringOffset = 0
		
		for f in range(len(self.files)):
			header += f.offset.to_bytes(8, byteorder='little')
			header += f.size.to_bytes(8, byteorder='little')
			header += stringOffset.to_bytes(4, byteorder='little')
			header += b'\x00\x00\x00\x00'
			
			stringOffset += len(f.name) + 1
			
		h += stringTable.encode()
		h += remainder * b'\x00'
		
		return h
		
	def open(self, path = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		r = super(Pfs0, self).open(path, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()
		#self.setupCrypto()
		#Print.info('cryptoType = ' + hex(self.cryptoType))
		#Print.info('titleKey = ' + (self.cryptoKey.hex()))
		#Print.info('cryptoCounter = ' + (self.cryptoCounter.hex()))

		self.magic = self.read(4)
		if self.magic != b'PFS0':
			raise IOError('Not a valid PFS0 partition ' + str(self.magic))
			

		fileCount = self.readInt32()
		stringTableSize = self.readInt32()
		self.readInt32() # junk data

		self.seek(0x10 + fileCount * 0x18)
		stringTable = self.read(stringTableSize)
		stringEndOffset = stringTableSize
		
		headerSize = 0x10 + 0x18 * fileCount + stringTableSize
		self.files = []

		for i in range(fileCount):
			i = fileCount - i - 1
			self.seek(0x10 + i * 0x18)

			offset = self.readInt64()
			size = self.readInt64()
			nameOffset = self.readInt32() # just the offset
			name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
			stringEndOffset = nameOffset

			self.readInt32() # junk data

			f = Fs.factory(name)

			f._path = name
			f.offset = offset
			f.size = size
			
			self.files.append(self.partition(offset + headerSize, f.size, f))

		self.files.reverse()

		'''
		self.seek(0x10 + fileCount * 0x18)
		stringTable = self.read(stringTableSize)
		
		for i in range(fileCount):
			if i == fileCount - 1:
				self.files[i].name = stringTable[self.files[i].nameOffset:].decode('utf-8').rstrip(' \t\r\n\0')
			else:
				self.files[i].name = stringTable[self.files[i].nameOffset:self.files[i+1].nameOffset].decode('utf-8').rstrip(' \t\r\n\0')
		'''
				
		
	def get_cryptoType(self):
		return self.cryptoType
		
	def get_cryptoKey(self):
		return self.cryptoKey

	def get_cryptoCounter(self):
		return self.cryptoCounter			
		
	def read_cnmt(self, path = None, mode = 'rb'):
		cryptoType = self.get_cryptoType()
		cryptoKey = self.get_cryptoKey()
		cryptoCounter = self.get_cryptoCounter()
		r = super(Pfs0, self).open(path, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()
		for cnmt in self:
			f = Fs.factory(cnmt)
			cnmt.rewind()
			titleid=f.readInt64()
			titleversion = cnmt.read(0x4)
			cnmt.rewind()
			cnmt.seek(0xE)
			offset=cnmt.readInt16()
			content_entries=cnmt.readInt16()
			meta_entries=cnmt.readInt16()
			cnmt.rewind()
			cnmt.seek(0x20)
			original_ID=cnmt.readInt64()
			min_sversion=cnmt.readInt64()
			Print.info('')	
			Print.info('...........................................')								
			Print.info('Reading: ' + str(cnmt._path))
			Print.info('...........................................')							
			Print.info('titleid = ' + str(hx(titleid.to_bytes(8, byteorder='big'))))
			Print.info('version = ' + str(int.from_bytes(titleversion, byteorder='little')))
			Print.info('Table offset = '+ str(hx((offset+0x20).to_bytes(2, byteorder='big'))))
			Print.info('number of content = '+ str(content_entries))
			Print.info('number of meta entries = '+ str(meta_entries))
			Print.info('Application id\Patch id = ' + str(hx(original_ID.to_bytes(8, byteorder='big'))))
			Print.info('RequiredSystemVersion = ' + str(min_sversion))
			cnmt.rewind()
			cnmt.seek(0x20+offset)
			#for i in range(content_entries):
			#	Print.info('........................')							
			#	Print.info('Content number ' + str(i+1))
			#	Print.info('........................')
			#	vhash = cnmt.read(0x20)
			#	Print.info('hash =\t' + str(hx(vhash)))
			#	NcaId = cnmt.read(0x10)
			#	Print.info('NcaId =\t' + str(hx(NcaId)))
			#	size = cnmt.read(0x6)
			#	Print.info('Size =\t' + str(int.from_bytes(size, byteorder='little', signed=True)))
			#	ncatype = cnmt.read(0x1)
			#	Print.info('ncatype = ' + str(int.from_bytes(ncatype, byteorder='little', signed=True)))
			#	unknown = cnmt.read(0x1)					
		
		
		
		
						
	def printInfo(self, indent = 0):
		maxDepth = 3
		tabs = '\t' * indent
		Print.info('\n%sPFS0\n' % (tabs))
		super(Pfs0, self).printInfo( indent)
