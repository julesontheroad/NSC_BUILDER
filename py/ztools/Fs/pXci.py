from binascii import hexlify as hx, unhexlify as uhx
from Fs.pHfs0 import uHfs0
from Fs.pHfs0 import nHfs0
from Fs.Ticket import Ticket
from Fs.Nca import Nca
from Fs.File import File
import os
import Print
import Keys
import aes128
import Hex
import Title
import Titles
import Hex
import sq_tools
from struct import pack as pk, unpack as upk
from hashlib import sha256
import Fs.Type
import re
import pathlib
import Keys
import Config
import Print
from tqdm import tqdm

MEDIA_SIZE = 0x200
indent = 1
tabs = '\t' * indent	

class GamecardInfo(File):
	def __init__(self, file = None):
		super(GamecardInfo, self).__init__()
		if file:
			self.open(file)
	
	def open(self, file, mode='rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(GamecardInfo, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()
		self.firmwareVersion = self.readInt64()
		self.accessControlFlags = self.readInt32()
		self.readWaitTime = self.readInt32()
		self.readWaitTime2 = self.readInt32()
		self.writeWaitTime = self.readInt32()
		self.writeWaitTime2 = self.readInt32()
		self.firmwareMode = self.readInt32()
		self.cupVersion = self.readInt32()
		self.empty1 = self.readInt32()
		self.updatePartitionHash = self.readInt64()
		self.cupId = self.readInt64()
		self.empty2 = self.read(0x38)
		
class GamecardCertificate(File):
	def __init__(self, file = None):
		super(GamecardCertificate, self).__init__()
		self.signature = None
		self.magic = None
		self.unknown1 = None
		self.unknown2 = None
		self.data = None
		
		if file:
			self.open(file)
			
	def open(self, file, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(GamecardCertificate, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()
		self.signature = self.read(0x100)
		self.magic = self.read(0x4)
		self.unknown1 = self.read(0x10)
		self.unknown2 = self.read(0xA)
		self.data = self.read(0xD6)
			
class uXci(File):
	def __init__(self, file = None):
		super(uXci, self).__init__()
		self.header = None
		self.signature = None
		self.magic = None
		self.secureOffset = None
		self.backupOffset = None
		self.titleKekIndex = None
		self.gamecardSize = None
		self.gamecardHeaderVersion = None
		self.gamecardFlags = None
		self.packageId = None
		self.validDataEndOffset = None
		self.gamecardInfo = None
		
		self.hfs0Offset = None
		self.hfs0HeaderSize = None
		self.hfs0HeaderHash = None
		self.hfs0InitialDataHash = None
		self.secureMode = None
		
		self.titleKeyFlag = None
		self.keyFlag = None
		self.normalAreaEndOffset = None
		
		self.gamecardInfo = None
		self.gamecardCert = None
		self.hfs0 = None
		
		if file:
			self.open(file)
		
	def readHeader(self):
	
		self.signature = self.read(0x100)
		self.magic = self.read(0x4)
		self.secureOffset = self.readInt32()
		self.backupOffset = self.readInt32()
		self.titleKekIndex = self.readInt8()
		self.gamecardSize = self.readInt8()
		self.gamecardHeaderVersion = self.readInt8()
		self.gamecardFlags = self.readInt8()
		self.packageId = self.readInt64()
		self.validDataEndOffset = self.readInt64()
		self.gamecardInfo = self.read(0x10)
		
		self.hfs0Offset = self.readInt64()
		self.hfs0HeaderSize = self.readInt64()
		self.hfs0HeaderHash = self.read(0x20)
		self.hfs0InitialDataHash = self.read(0x20)
		self.secureMode = self.readInt32()
		
		self.titleKeyFlag = self.readInt32()
		self.keyFlag = self.readInt32()
		self.normalAreaEndOffset = self.readInt32()
		
		self.gamecardInfo = GamecardInfo(self.partition(self.tell(), 0x70))
		self.gamecardCert = GamecardCertificate(self.partition(0x7000, 0x200))
		

	def open(self, path = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		r = super(uXci, self).open(path, mode, cryptoType, cryptoKey, cryptoCounter)
		self.readHeader()
		self.seek(0xF000)
		self.hfs0 = uHfs0(None, cryptoKey = None)
		self.partition(0xf000, None, self.hfs0, cryptoKey = None)

	def unpack(self, path):
		os.makedirs(path, exist_ok=True)

		for nspF in self.hfs0:
			filePath = os.path.abspath(path + '/' + nspF._path)
			f = open(filePath, 'wb')
			nspF.rewind()
			i = 0

			pageSize = 0x10000

			while True:
				buf = nspF.read(pageSize)
				if len(buf) == 0:
					break
				i += len(buf)
				f.write(buf)
			f.close()
			Print.info(filePath)
			
	def copy_nca(self,ofolder,buffer,token,metapatch,keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						nca.rewind()
						filename =  str(nca._path)
						outfolder = str(ofolder)+'/'
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						fp = open(filepath, 'w+b')
						nca.rewind()
						t = tqdm(total=nca.header.size, unit='B', unit_scale=True, leave=False)
						t.write(tabs+'Copying: ' + str(filename))
						for data in iter(lambda: nca.read(int(buffer)), ""):
							fp.write(data)
							t.update(len(data))
							fp.flush()
							if not data:
								fp.close()
								t.close()	
								break
						#///////////////////////////////////
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()
						if keypatch != 'false':
							if keypatch < target.header.getCryptoType2():
								self.change_mkrev_nca(target, keypatch)
						target.close()		
						if metapatch == 'true':
							if 	str(nca.header.contentType) == 'Content.META':
								for pfs0 in nca:
									for cnmt in pfs0:
										check=str(cnmt._path)
										check=check[:-22]
									if check == 'AddOnContent':
										Print.info(tabs + '-------------------------------------')
										Print.info(tabs +'DLC -> No need to patch the meta' )
										Print.info(tabs + '-------------------------------------')
									else:	
										self.patch_meta(filepath,outfolder,RSV_cap)			
		
	def printInfo(self):
		maxDepth = 3
		indent = 0
		tabs = '\t' * indent
		Print.info('\n%sXCI Archive\n' % (tabs))
		super(Xci, self).printInfo(maxDepth, indent)
		
		Print.info(tabs + 'magic = ' + str(self.magic))
		Print.info(tabs + 'titleKekIndex = ' + str(self.titleKekIndex))
		
		Print.info(tabs + 'gamecardCert = ' + str(hx(self.gamecardCert.magic + self.gamecardCert.unknown1 + self.gamecardCert.unknown2 + self.gamecardCert.data)))
		self.hfs0.printInfo( indent)


class nXci(File):
	def __init__(self, file = None):
		super(nXci, self).__init__()
		self.header = None
		self.signature = None
		self.magic = None
		self.secureOffset = None
		self.backupOffset = None
		self.titleKekIndex = None
		self.gamecardSize = None
		self.gamecardHeaderVersion = None
		self.gamecardFlags = None
		self.packageId = None
		self.validDataEndOffset = None
		self.gamecardInfo = None
		
		self.hfs0Offset = None
		self.hfs0HeaderSize = None
		self.hfs0HeaderHash = None
		self.hfs0InitialDataHash = None
		self.secureMode = None
		
		self.titleKeyFlag = None
		self.keyFlag = None
		self.normalAreaEndOffset = None
		
		self.gamecardInfo = None
		self.gamecardCert = None
		self.hfs0 = None
		
		if file:
			self.open(file)
		
	def readHeader(self):
	
		self.signature = self.read(0x100)
		self.magic = self.read(0x4)
		self.secureOffset = self.readInt32()
		self.backupOffset = self.readInt32()
		self.titleKekIndex = self.readInt8()
		self.gamecardSize = self.readInt8()
		self.gamecardHeaderVersion = self.readInt8()
		self.gamecardFlags = self.readInt8()
		self.packageId = self.readInt64()
		self.validDataEndOffset = self.readInt64()
		self.gamecardInfo = self.read(0x10)
		
		self.hfs0Offset = self.readInt64()
		self.hfs0HeaderSize = self.readInt64()
		self.hfs0HeaderHash = self.read(0x20)
		self.hfs0InitialDataHash = self.read(0x20)
		self.secureMode = self.readInt32()
		
		self.titleKeyFlag = self.readInt32()
		self.keyFlag = self.readInt32()
		self.normalAreaEndOffset = self.readInt32()
		
		self.gamecardInfo = GamecardInfo(self.partition(self.tell(), 0x70))
		self.gamecardCert = GamecardCertificate(self.partition(0x7000, 0x200))
		

	def open(self, path = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		r = super(nXci, self).open(path, mode, cryptoType, cryptoKey, cryptoCounter)
		self.readHeader()
		self.seek(0xF000)
		self.hfs0 = nHfs0(None, cryptoKey = None)
		self.partition(0xf000, None, self.hfs0, cryptoKey = None)

	def unpack(self, path):
		os.makedirs(path, exist_ok=True)

		for nspF in self.hfs0:
			filePath = os.path.abspath(path + '/' + nspF._path)
			f = open(filePath, 'wb')
			nspF.rewind()
			i = 0

			pageSize = 0x10000

			while True:
				buf = nspF.read(pageSize)
				if len(buf) == 0:
					break
				i += len(buf)
				f.write(buf)
			f.close()
			Print.info(filePath)

	def copy_nca(self,ofolder,buffer,token,metapatch,keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						nca.rewind()
						filename =  str(nca._path)
						outfolder = str(ofolder)+'/'
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						fp = open(filepath, 'w+b')
						nca.rewind()
						t = tqdm(total=nca.header.size, unit='B', unit_scale=True, leave=False)
						t.write(tabs+'Copying: ' + str(filename))
						for data in iter(lambda: nca.read(int(buffer)), ""):
							fp.write(data)
							t.update(len(data))
							fp.flush()
							if not data:
								fp.close()
								t.close()	
								break
						#///////////////////////////////////
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()
						if keypatch != 'false':
							if keypatch < target.header.getCryptoType2():
								self.change_mkrev_nca(target, keypatch)
						target.close()		
						if metapatch == 'true':
							if 	str(nca.header.contentType) == 'Content.META':
								for pfs0 in nca:
									for cnmt in pfs0:
										check=str(cnmt._path)
										check=check[:-22]
									if check == 'AddOnContent':
										Print.info(tabs + '-------------------------------------')
										Print.info(tabs +'DLC -> No need to patch the meta' )
										Print.info(tabs + '-------------------------------------')
									else:	
										self.patch_meta(filepath,outfolder,RSV_cap)				
		
	def printInfo(self):
		maxDepth = 3
		indent = 0
		tabs = '\t' * indent
		Print.info('\n%sXCI Archive\n' % (tabs))
		super(Xci, self).printInfo(maxDepth, indent)
		
		Print.info(tabs + 'magic = ' + str(self.magic))
		Print.info(tabs + 'titleKekIndex = ' + str(self.titleKekIndex))
		
		Print.info(tabs + 'gamecardCert = ' + str(hx(self.gamecardCert.magic + self.gamecardCert.unknown1 + self.gamecardCert.unknown2 + self.gamecardCert.data)))
		self.hfs0.printInfo( indent)		