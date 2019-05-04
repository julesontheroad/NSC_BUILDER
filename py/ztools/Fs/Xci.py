from binascii import hexlify as hx, unhexlify as uhx
from Fs.Hfs0 import Hfs0
from Fs.Ticket import Ticket
from Fs.Nca import Nca
from Fs.File import File
import os
import Print
import Keys
import aes128
import Title
import Titles
import Hex
import sq_tools
from struct import pack as pk, unpack as upk
from hashlib import sha256
import Fs.Type
import re
import pathlib
import Config
import Print
from tqdm import tqdm
import math  
from operator import itemgetter, attrgetter, methodcaller
#from Cryptodome.Cipher import PKCS1_v1_5 #Add new dependency Cryptodome

MEDIA_SIZE = 0x200
RSA_PUBLIC_EXPONENT = 65537
HFS0_START = 0xf000
XCI_SIGNATURE_SIZE = 0x100
XCI_IV_SIZE = 0x10
XCI_HASH_SIZE = 0x20
XCI_GAMECARD_INFO_LENGTH = 0x70
XCI_GAMECARD_INFO_PADDING_LENGTH = 0x38
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
			
class Xci(File):
	def __init__(self, file = None):
		super(Xci, self).__init__()
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
		self.gamecardInfoIV = None
		
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
		self.gamecardInfoIV = self.gamecardInfo
		
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
		r = super(Xci, self).open(path, mode, cryptoType, cryptoKey, cryptoCounter)
		self.readHeader()
		self.seek(0xF000)
		self.hfs0 = Hfs0(None, cryptoKey = None)
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


	def copy_hfs0(self,ofolder,buffer,token):
		indent = 1
		tabs = '\t' * indent
		if token == "all":
			for nspF in self.hfs0:
				nspF.rewind()
				filename =  str(nspF._path)
				outfolder = str(ofolder)+'/'
				filepath = os.path.join(outfolder, filename)
				if not os.path.exists(outfolder):
					os.makedirs(outfolder)
				fp = open(filepath, 'w+b')
				nspF.rewind()
				Print.info(tabs + 'Copying: ' + str(filename))
				for data in iter(lambda: nspF.read(int(buffer)), ""):
					fp.write(data)
					fp.flush()
					if not data:
						break
				fp.close()
		else:
			for nspF in self.hfs0:
				if token == str(nspF._path):
					nspF.rewind()
					filename =  str(nspF._path)
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					if not os.path.exists(outfolder):
						os.makedirs(outfolder)
					fp = open(filepath, 'w+b')
					nspF.rewind()
					Print.info(tabs + 'Copying: ' + str(filename))
					for data in iter(lambda: nspF.read(int(buffer)), ""):
						fp.write(data)
						fp.flush()
						if not data:
							break
					fp.close()

	def copy_ticket(self,ofolder,buffer,token):
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for ticket in nspF:
					if type(ticket) == Ticket:
						ticket.rewind()
						data = ticket.read()
						filename =  str(ticket._path)
						outfolder = str(ofolder)+'/'
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						fp = open(str(filepath), 'w+b')
						fp.write(data)
						fp.flush()

	def copy_cnmt(self,ofolder,buffer):
		for nspF in self.hfs0:
			if "secure" == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for file in f:
									nca.rewind()
									f.rewind()
									file.rewind()
									filename =  str(file._path)
									outfolder = str(ofolder)+'/'
									filepath = os.path.join(outfolder, filename)
									if not os.path.exists(outfolder):
										os.makedirs(outfolder)
									fp = open(filepath, 'w+b')
									nca.rewind()
									f.rewind()	
									file.rewind()								
									for data in iter(lambda:file.read(int(buffer)), ""):
										fp.write(data)
										fp.flush()
										if not data:
											break
									fp.close()
			
						
	def copy_other(self,ofolder,buffer,token):
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for file in self:
					if type(file) == File:
						file.rewind()
						filename =  str(file._path)
						outfolder = str(ofolder)+'/'
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						fp = open(filepath, 'w+b')
						file.rewind()
						for data in iter(lambda: file.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							if not data:
								break
						fp.close()										
						
	def copy_root_hfs0(self,ofolder,buffer):
		indent = 1
		tabs = '\t' * indent
		target=self.hfs0
		target.rewind()
		filename = 'root.hfs0'
		outfolder = str(ofolder)+'/'
		filepath = os.path.join(outfolder, filename)
		if not os.path.exists(outfolder):
			os.makedirs(outfolder)
		fp = open(filepath, 'w+b')
		target.rewind()
		Print.info(tabs + 'Copying: ' + str(filename))
		for data in iter(lambda: target.read(int(buffer)), ""):
			fp.write(data)
			fp.flush()
			if not data:
				break
		fp.close()

#Copy nca files from secure 
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
					
										
										
#Copy nca files from secure skipping deltas
	def copy_nca_nd(self,ofolder,buffer,metapatch,keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		Print.info('Copying files: ')
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					vfragment="false"
					if type(nca) == Nca:
						vfragment="false"
						if 	str(nca.header.contentType) == 'Content.DATA':
							for f in nca:
									for file in f:
										filename = str(file._path)
										if filename=="fragment":
											vfragment="true"			
						if str(vfragment)=="true":
							Print.info('Skipping delta fragment: ' + str(nca._path))
							continue
						else:			
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
						

#COPY AND CLEAN NCA FILES FROM SECURE AND PATCH NEEDED SYSTEM VERSION			
	def cr_tr_nca(self,ofolder,buffer,metapatch,keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for ticket in nspF:
					if type(ticket) == Ticket:
						masterKeyRev = ticket.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = ticket.getRightsId()
						Print.info('rightsId =\t' + hex(rightsId))
						Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
						Print.info('masterKeyRev =\t' + hex(masterKeyRev))
				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')

				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() == 0:
								if nca.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break									
											
				for nca in nspF:
					vfragment="false"
					if type(nca) == Nca:
						Print.info('Copying files: ')
						if nca.header.getRightsId() != 0:
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
							target = Nca(filepath, 'r+b')
							target.rewind()
							Print.info(tabs + 'Removing titlerights for ' + str(filename))
							Print.info(tabs + 'Writing masterKeyRev for %s, %d' % (str(nca._path),  masterKeyRev))
							crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
							target.header.setRightsId(0)
							target.header.setKeyBlock(encKeyBlock)
							Hex.dump(encKeyBlock)	
							target.close()
							#///////////////////////////////////
							target = Fs.Nca(filepath, 'r+b')
							target.rewind()
							if keypatch != 'false':
								if keypatch < target.header.getCryptoType2():
									self.change_mkrev_nca(target, keypatch)
							target.close()									
						if nca.header.getRightsId() == 0:
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
							


#COPY AND CLEAN NCA FILES FROM SECURE SKIPPING DELTAS AND PATCH NEEDED SYSTEM VERSION
	def cr_tr_nca_nd(self,ofolder,buffer,metapatch,keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for ticket in nspF:
					if type(ticket) == Ticket:
						masterKeyRev = ticket.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = ticket.getRightsId()
						Print.info('rightsId =\t' + hex(rightsId))
						Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
						Print.info('masterKeyRev =\t' + hex(masterKeyRev))
				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')
				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() == 0:
								if nca.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break									

				for nca in nspF:
					vfragment="false"
					if type(nca) == Nca:
						vfragment="false"
						if 	str(nca.header.contentType) == 'Content.DATA':
							for f in nca:
									for file in f:
										filename = str(file._path)
										if filename=="fragment":
											vfragment="true"
						if str(vfragment)=="true":
							Print.info('Skipping delta fragment: ' + str(nca._path))
							continue
						else:
							Print.info('Copying files: ')
							if nca.header.getRightsId() != 0:
								nca.rewind()
								filename =  str(nca._path)
								outfolder = str(ofolder)+'/'
								filepath = os.path.join(outfolder, filename)
								if not os.path.exists(outfolder):
									os.makedirs(outfolder)
								fp = open(filepath, 'w+b')
								nca.rewind()
								Print.info(tabs + 'Copying: ' + str(filename))
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
								target = Nca(filepath, 'r+b')
								target.rewind()
								Print.info(tabs + 'Removing titlerights for ' + str(filename))
								Print.info(tabs + 'Writing masterKeyRev for %s, %d' % (str(nca._path),  masterKeyRev))
								crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
								encKeyBlock = crypto.encrypt(titleKeyDec * 4)
								target.header.setRightsId(0)
								target.header.setKeyBlock(encKeyBlock)
								Hex.dump(encKeyBlock)	
								target.close()
								#///////////////////////////////////
								target = Fs.Nca(filepath, 'r+b')
								target.rewind()
								if keypatch != 'false':
									if keypatch < target.header.getCryptoType2():
										self.change_mkrev_nca(target, keypatch)
								target.close()										
							if nca.header.getRightsId() == 0:
								nca.rewind()
								filename =  str(nca._path)
								outfolder = str(ofolder)+'/'
								filepath = os.path.join(outfolder, filename)
								if not os.path.exists(outfolder):
									os.makedirs(outfolder)
								fp = open(filepath, 'w+b')
								nca.rewind()
								Print.info(tabs + 'Copying: ' + str(filename))
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
		
#///////////////////////////////////////////////////								
# Change MKREV_NCA
#///////////////////////////////////////////////////						
		
	def change_mkrev_nca(self, nca, newMasterKeyRev):
	
		indent = 2
		tabs = '\t' * indent
		indent2 = 3
		tabs2 = '\t' * indent2
		
		masterKeyRev = nca.header.getCryptoType2()	

		if type(nca) == Nca:
			if nca.header.getCryptoType2() != newMasterKeyRev:
				Print.info(tabs + '-----------------------------------')
				Print.info(tabs + 'Changing keygeneration from %d to %s' % ( nca.header.getCryptoType2(), str(newMasterKeyRev)))
				Print.info(tabs + '-----------------------------------')
				encKeyBlock = nca.header.getKeyBlock()
				if sum(encKeyBlock) != 0:
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
					Print.info(tabs2 + '+ decrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
					crypto = aes128.AESECB(key)
					decKeyBlock = crypto.decrypt(encKeyBlock)
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex)
					Print.info(tabs2 + '+ encrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex))
					crypto = aes128.AESECB(key)
					reEncKeyBlock = crypto.encrypt(decKeyBlock)
					nca.header.setKeyBlock(reEncKeyBlock)
				if newMasterKeyRev >= 3:
					nca.header.setCryptoType(2)
					nca.header.setCryptoType2(newMasterKeyRev)
				if newMasterKeyRev == 2:
					nca.header.setCryptoType(2)
					nca.header.setCryptoType2(0)					
				else:
					nca.header.setCryptoType(newMasterKeyRev)
					nca.header.setCryptoType2(0)	
				Print.info(tabs2 + 'DONE')			
	
#///////////////////////////////////////////////////								
#PATCH META FUNCTION
#///////////////////////////////////////////////////	
	def patch_meta(self,filepath,outfolder,RSV_cap):
		RSV_cap=int(RSV_cap)	
		indent = 1
		tabs = '\t' * indent	
		Print.info(tabs + '-------------------------------------')
		Print.info(tabs + 'Checking meta: ')
		meta_nca = Fs.Nca(filepath, 'r+b')
		crypto1=meta_nca.header.getCryptoType()	
		crypto2=meta_nca.header.getCryptoType2()	
		if crypto1 == 2:
			if crypto1 > crypto2:								
				keygen=meta_nca.header.getCryptoType()
			else:			
				keygen=meta_nca.header.getCryptoType2()	
		else:			
			keygen=meta_nca.header.getCryptoType2()					
		RSV=meta_nca.get_req_system()		
		RSVmin=sq_tools.getMinRSV(keygen,RSV)
		RSVmax=sq_tools.getTopRSV(keygen,RSV)		
		if 	RSV > RSVmin:
			if RSVmin >= RSV_cap:
				meta_nca.write_req_system(RSVmin)
			else:
				if keygen < 4:
					if RSV > RSVmax:
						meta_nca.write_req_system(RSV_cap)		
				else:
					meta_nca.write_req_system(RSV_cap)	
			meta_nca.flush()
			meta_nca.close()
			Print.info(tabs + 'Updating cnmt hashes: ')
			############################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha=meta_nca.calc_pfs0_hash()
			Print.info(tabs + '- Calculated hash from pfs0: ')
			Print.info(tabs +'  + '+ str(hx(sha)))					
			meta_nca.flush()
			meta_nca.close()
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.set_pfs0_hash(sha)
			meta_nca.flush()
			meta_nca.close()
			############################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha2=meta_nca.calc_htable_hash()
			Print.info(tabs + '- Calculated table hash: ')	
			Print.info(tabs +'  + '+ str(hx(sha2)))								
			meta_nca.flush()
			meta_nca.close()						
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.header.set_htable_hash(sha2)
			meta_nca.flush()
			meta_nca.close()
			########################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha3=meta_nca.header.calculate_hblock_hash()
			Print.info(tabs + '- Calculated header block hash: ')
			Print.info(tabs +'  + '+ str(hx(sha2)))								
			meta_nca.flush()
			meta_nca.close()						
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.header.set_hblock_hash(sha3)
			meta_nca.flush()
			meta_nca.close()
			########################
			'''			
			with open(filepath, 'r+b') as file:			
				nsha=sha256(file.read()).hexdigest()
			newname=nsha[:32] + '.cnmt.nca'				
			Print.info(tabs +'New name: ' + newname )
			dir=os.path.dirname(os.path.abspath(filepath))
			newpath=dir+ '/' + newname
			os.rename(filepath, newpath)
			Print.info(tabs + '-------------------------------------')
		else:
			Print.info(tabs +'-> No need to patch the meta' )
			Print.info(tabs + '-------------------------------------')	
			'''			
		
#Check if titlerights			
	def trights_set(self):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:	
						if nca.header.getRightsId() != 0:
							return 'TRUE'	
				return 'FALSE'							
		
#Check if exists ticket		
	def exist_ticket(self):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for ticket in nspF:
					if type(ticket) == Ticket:
						return 'TRUE'	
				return 'FALSE'			
		

#READ CNMT FILE WITHOUT EXTRACTION	
	def read_cnmt(self):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()
									min_sversion=cnmt.readInt32()
									length_of_emeta=cnmt.readInt32()	
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
									content_name=str(cnmt._path)
									content_name=content_name[:-22]				
									if content_name == 'AddOnContent':
										Print.info('RequiredUpdateNumber = ' + str(min_sversion))
									if content_name != 'AddOnContent':
										Print.info('RequiredSystemVersion = ' + str(min_sversion))
									cnmt.rewind()
									cnmt.seek(0x20+offset)
									for i in range(content_entries):
										Print.info('........................')							
										Print.info('Content number ' + str(i+1))
										Print.info('........................')
										vhash = cnmt.read(0x20)
										Print.info('hash =\t' + str(hx(vhash)))
										NcaId = cnmt.read(0x10)
										Print.info('NcaId =\t' + str(hx(NcaId)))
										size = cnmt.read(0x6)
										Print.info('Size =\t' + str(int.from_bytes(size, byteorder='little')))
										ncatype = cnmt.read(0x1)
										Print.info('ncatype = ' + str(int.from_bytes(ncatype, byteorder='little')))
										unknown = cnmt.read(0x1)	
										cnmt.seek(0x20+offset+content_entries*0x38+length_of_emeta)			
										digest = cnmt.read(0x20)
										Print.info("")	
										Print.info('digest= '+str(hx(digest)))
										Print.info("")		
										cnmt.seek(0x20+offset+content_entries*0x38)										
										if length_of_emeta>0:
											Print.info('----------------')			
											Print.info('Extended meta')	
											Print.info('----------------')				
											num_prev_cnmt=cnmt.read(0x4)
											num_prev_delta=cnmt.read(0x4)
											num_delta_info=cnmt.read(0x4)
											num_delta_application =cnmt.read(0x4)	
											num_previous_content=cnmt.read(0x4)		
											num_delta_content=cnmt.read(0x4)	
											cnmt.read(0x4)	
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
												titleid=cnmt.readInt64()	
												titleversion = cnmt.read(0x4)	
												type_n = cnmt.read(0x1)					
												unknown1=cnmt.read(0x3)
												vhash = cnmt.read(0x20)
												unknown2=cnmt.read(0x2)
												unknown3=cnmt.read(0x2)
												unknown4=cnmt.read(0x4)				
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
												oldtitleid=cnmt.readInt64()	
												newtitleid=cnmt.readInt64()					
												oldtitleversion = cnmt.read(0x4)	
												newtitleversion = cnmt.read(0x4)	
												size = cnmt.read(0x8)
												unknown1=cnmt.read(0x8)				
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
												oldtitleid=cnmt.readInt64()	
												newtitleid=cnmt.readInt64()					
												oldtitleversion = cnmt.read(0x4)	
												newtitleversion = cnmt.read(0x4)	
												index1=cnmt.readInt64()	
												index2=cnmt.readInt64()				
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
												OldNcaId = cnmt.read(0x10)
												NewNcaId = cnmt.read(0x10)		
												old_size = cnmt.read(0x6)				
												up2bytes = cnmt.read(0x2)
												low4bytes = cnmt.read(0x4)
												unknown1 = cnmt.read(0x2)
												ncatype = cnmt.read(0x1)	
												installable = cnmt.read(0x1)
												unknown2 = cnmt.read(0x4)				
												Print.info('OldNcaId = ' + str(hx(OldNcaId)))	
												Print.info('NewNcaId = ' + str(hx(NewNcaId)))	
												Print.info('Old size = ' +  str(int.from_bytes(old_size, byteorder='little', signed=True)))	
												Print.info('unknown1 = ' + str(int.from_bytes(unknown1, byteorder='little')))
												Print.info('ncatype =  ' + str(int.from_bytes(ncatype, byteorder='little', signed=True)))
												Print.info('installable = ' + str(int.from_bytes(installable, byteorder='little', signed=True)))
												Print.info('Upper 2 bytes of the new size=' + str(hx(up2bytes)))	
												Print.info('Lower 4 bytes of the new size=' + str(hx(low4bytes)))					
												#Print.info('unknown2 =\t' + str(int.from_bytes(unknown2, byteorder='little')))			

											for i in range(int.from_bytes(num_previous_content, byteorder='little')):
												Print.info('...........................................')								
												Print.info('Previous content records: '+ str(i+1))
												Print.info('...........................................')				
												NcaId = cnmt.read(0x10)		
												size = cnmt.read(0x6)				
												ncatype = cnmt.read(0x1)	
												unknown1 = cnmt.read(0x1)				
												Print.info('NcaId = '+ str(hx(NcaId)))	
												Print.info('Size = '+ str(int.from_bytes(size, byteorder='little', signed=True)))	
												Print.info('ncatype = '+ str(int.from_bytes(ncatype, byteorder='little', signed=True)))			
												#Print.info('unknown1 = '+ str(int.from_bytes(unknown1, byteorder='little')))	
				
											for i in range(int.from_bytes(num_delta_content, byteorder='little')):
												Print.info('........................')							
												Print.info('Delta content entry ' + str(i+1))
												Print.info('........................')
												vhash = cnmt.read(0x20)
												Print.info('hash =\t' + str(hx(vhash)))
												NcaId = cnmt.read(0x10)
												Print.info('NcaId =\t' + str(hx(NcaId)))
												size = cnmt.read(0x6)
												Print.info('Size =\t' + str(int.from_bytes(size, byteorder='little', signed=True)))
												ncatype = cnmt.read(0x1)
												Print.info('ncatype = ' + str(int.from_bytes(ncatype, byteorder='little', signed=True)))
												unknown = cnmt.read(0x1)
										
									
#///////////////////////////////////////////////////								
#SPLIT MULTI-CONTENT XCI IN FOLDERS
#///////////////////////////////////////////////////	
	def splitter_read(self,ofolder,buffer,pathend):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:		
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()
									min_sversion=self.readInt32()
									end_of_emeta=self.readInt32()	
									target=str(nca._path)
									contentname = self.splitter_get_title(target,offset,content_entries,original_ID)
									cnmt.rewind()
									cnmt.seek(0x20+offset)
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]
									Print.info('-------------------------------------')
									Print.info('Detected content: ' + str(titleid2))	
									Print.info('-------------------------------------')							
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										ncatype = cnmt.read(0x1)
										unknown = cnmt.read(0x1)		
									#**************************************************************	
										version=str(int.from_bytes(titleversion, byteorder='little'))
										version='[v'+version+']'
										titleid3 ='['+ titleid2+']'
										nca_name=str(hx(NcaId))
										nca_name=nca_name[2:-1]+'.nca'
										ofolder2 = ofolder+ '/'+contentname+' '+ titleid3+' '+version+'/'+pathend
										self.splitter_copy(ofolder2,buffer,nca_name)
									nca_meta=str(nca._path)
									self.splitter_copy(ofolder2,buffer,nca_meta)
									self.splitter_tyc(ofolder2,titleid2)
		dirlist=os.listdir(ofolder)
		textpath = os.path.join(ofolder, 'dirlist.txt')
		with open(textpath, 'a') as tfile:		
			for folder in dirlist:
				item = os.path.join(ofolder, folder)
				tfile.write(item + '\n')

	
		indent = 1
		tabs = '\t' * indent
		token='secure'
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						if nca_name == str(nca._path):
							nca.rewind()
							filename =  str(nca._path)
							outfolder = str(ofolder)+'/'
							filepath = os.path.join(outfolder, filename)
							if not os.path.exists(outfolder):
								os.makedirs(outfolder)
							fp = open(filepath, 'w+b')
							nca.rewind()
							Print.info(tabs + 'Copying: ' + str(filename))
							for data in iter(lambda: nca.read(int(buffer)), ""):
								fp.write(data)
								fp.flush()
								if not data:
									break
							fp.close()
	
	def splitter_copy(self,ofolder,buffer,nca_name):
		indent = 1
		tabs = '\t' * indent
		token='secure'
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						if nca_name == str(nca._path):	
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

	def splitter_tyc(self,ofolder,titleid):
		indent = 1
		tabs = '\t' * indent
		token='secure'
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for ticket in nspF:		
					if type(ticket) == Ticket:
						tik_id = str(ticket._path)
						tik_id =tik_id[:-20]
						if titleid == tik_id:
							ticket.rewind()
							data = ticket.read()
							filename =  str(ticket._path)
							outfolder = str(ofolder)+'/'
							filepath = os.path.join(outfolder, filename)
							if not os.path.exists(outfolder):
								os.makedirs(outfolder)
							fp = open(str(filepath), 'w+b')
							Print.info(tabs + 'Copying: ' + str(filename))
							fp.write(data)
							fp.flush()
							fp.close()
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for cert in nspF:				
					if cert._path.endswith('.cert'):
						cert_id = str(cert._path)
						cert_id =cert_id[:-21]
						if titleid == cert_id:				
							cert.rewind()
							data = cert.read()
							filename =  str(cert._path)
							outfolder = str(ofolder)+'/'
							filepath = os.path.join(outfolder, filename)
							if not os.path.exists(outfolder):
								os.makedirs(outfolder)
							fp = open(str(filepath), 'w+b')
							Print.info(tabs + 'Copying: ' + str(filename))
							fp.write(data)
							fp.flush()
							fp.close()
		
	def splitter_get_title(self,target,offset,content_entries,original_ID):
		content_type=''
		token='secure'		
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						if target ==  str(nca._path):
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()					
									cnmt.seek(0x20+offset)	
									nca_name='false'
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										ncatype = cnmt.read(0x1)
										unknown = cnmt.read(0x1)
										ncatype2 = int.from_bytes(ncatype, byteorder='little')
										if ncatype2 == 3:
											nca_name=str(hx(NcaId))
											nca_name=nca_name[2:-1]+'.nca'
											content_name=str(cnmt._path)
											content_name=content_name[:-22]
											if content_name == 'Patch':
												content_type=' [UPD]'
		if nca_name=='false':
			for nspF in self.hfs0:
				if token == str(nspF._path):
					for nca in nspF:		
						if type(nca) == Nca:
							if 	str(nca.header.contentType) == 'Content.META':
								for f in nca:
									for cnmt in f:
										cnmt.rewind()
										testID=cnmt.readInt64()
										if 	testID == original_ID:
											nca.rewind()
											f.rewind()								
											titleid=cnmt.readInt64()
											titleversion = cnmt.read(0x4)
											cnmt.rewind()
											cnmt.seek(0xE)
											offset=cnmt.readInt16()
											content_entries=cnmt.readInt16()
											meta_entries=cnmt.readInt16()
											cnmt.rewind()
											cnmt.seek(0x20)
											original_ID=cnmt.readInt64()
											min_sversion=self.readInt32()
											end_of_emeta=self.readInt32()	
											target=str(nca._path)
											contentname = self.splitter_get_title(target,offset,content_entries,original_ID)
											cnmt.rewind()
											cnmt.seek(0x20+offset)								
											for i in range(content_entries):
												vhash = cnmt.read(0x20)
												NcaId = cnmt.read(0x10)
												size = cnmt.read(0x6)
												ncatype = cnmt.read(0x1)
												unknown = cnmt.read(0x1)
												ncatype2 = int.from_bytes(ncatype, byteorder='little')
												if ncatype2 == 3:
													nca_name=str(hx(NcaId))
													nca_name=nca_name[2:-1]+'.nca'
													content_type=' [DLC]'
		title='DLC'
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:		
					if type(nca) == Nca:
						if nca_name == str(nca._path):
							for f in nca:
								nca.rewind()
								f.rewind()	
								Langue = list()	
								Langue = [0,1,6,5,7,10,3,4,9,8,2,11,12,13,14]		
								for i in Langue:
									f.seek(0x14200+i*0x300)								
									title = f.read(0x200)		
									title = title.split(b'\0', 1)[0].decode('utf-8')
									title = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', title))
									title = title.strip()
									if title == "":
										title = 'DLC'
									if title != 'DLC':								
										title = title + content_type
										return(title)
		return(title)
												
		

#///////////////////////////////////////////////////								
#PREPARE BASE CONTENT TO UPDATE IT
#///////////////////////////////////////////////////	
	def updbase_read(self,ofolder,buffer,cskip,metapatch, keypatch,RSV_cap):
		indent = 1
		rightsId = 0
		tabs = '\t' * indent		
		titleKeyDec=0x00*10	

		if keypatch != 'false':
			try:
				keypatch = int(keypatch)
			except:
				print("New keygeneration is no valid integer")
		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Ticket:
						masterKeyRev = file.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = file.getRightsId()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:			
					if type(file) == Nca:
						if file.header.getRightsId() != 0:
							if file.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Nca:	
						if file.header.getRightsId() != 0:		
							if file.header.getCryptoType2() == 0:
								if file.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break	

		Print.info('Reading Base XCI:')	
		if rightsId	!=0:	
			Print.info('rightsId =\t' + hex(rightsId))
			Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
			Print.info('masterKeyRev =\t' + hex(masterKeyRev))									
		print("")
		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:	
									content_name=str(cnmt._path)
									content_name=content_name[:-22]
									if content_name == 'Patch':
										if cskip == 'upd':
											continue
										if cskip == 'both':
											continue
									if content_name == 'AddOnContent':
										if cskip == 'dlc':
											continue
										if cskip == 'both':
											continue															
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()
									min_sversion=self.readInt32()
									end_of_emeta=self.readInt32()	
									target=str(nca._path)
									cnmt.rewind()
									cnmt.seek(0x20+offset)
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]
									Print.info('-------------------------------------')
									Print.info('Copying content: ' + str(titleid2))	
									Print.info('-------------------------------------')							
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										ncatype = cnmt.read(0x1)
										unknown = cnmt.read(0x1)		
									#**************************************************************	
										version=str(int.from_bytes(titleversion, byteorder='little'))
										version='[v'+version+']'
										titleid3 ='['+ titleid2+']'
										nca_name=str(hx(NcaId))
										nca_name=nca_name[2:-1]+'.nca'
										self.updbase_copy(ofolder,buffer,nca_name,metapatch, keypatch,RSV_cap,titleKeyDec)
									nca_meta=str(nca._path)
									self.updbase_copy(ofolder,buffer,nca_meta,metapatch, keypatch,RSV_cap,titleKeyDec)
									#self.updbase_tyc(ofolder,titleid2)
									
	def updbase_copy(self,ofolder,buffer,nca_name,metapatch, keypatch,RSV_cap,titleKeyDec):
		indent = 1
		tabs = '\t' * indent
		token='secure'
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						if nca_name == str(nca._path):	
							crypto1=nca.header.getCryptoType()
							crypto2=nca.header.getCryptoType2()	
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:	
								masterKeyRev=crypto1							
							if nca.header.getRightsId() != 0:
								nca.rewind()
								filename =  str(nca._path)
								outfolder = str(ofolder)+'/'
								filepath = os.path.join(outfolder, filename)
								if not os.path.exists(outfolder):
									os.makedirs(outfolder)
								fp = open(filepath, 'w+b')
								nca.rewind()
								Print.info(tabs)
								t = tqdm(total=nca.header.size, unit='B', unit_scale=True, leave=False)
								t.write(tabs + '-> Copying: ' + str(filename))
								for data in iter(lambda: nca.read(int(buffer)), ""):
									fp.write(data)
									t.update(len(data))
									fp.flush()
									if not data:
										fp.close()
										t.close()	
										break						
								target = Fs.Nca(filepath, 'r+b')
								target.rewind()
								Print.info(tabs + 'Removing titlerights for ' + str(filename))
								Print.info(tabs + 'Writing masterKeyRev for %s, %d' % (str(nca._path),  masterKeyRev))
								crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
								encKeyBlock = crypto.encrypt(titleKeyDec * 4)
								target.header.setRightsId(0)
								target.header.setKeyBlock(encKeyBlock)
								Hex.dump(encKeyBlock)
								Print.info('')						
								target.close()						
								#///////////////////////////////////
								target = Fs.Nca(filepath, 'r+b')
								target.rewind()
								if keypatch != 'false':
									if keypatch < target.header.getCryptoType2():
										self.change_mkrev_nca(target, keypatch)
								target.close()										
							if nca.header.getRightsId() == 0:
								nca.rewind()
								filename =  str(nca._path)
								outfolder = str(ofolder)+'/'
								filepath = os.path.join(outfolder, filename)
								if not os.path.exists(outfolder):
									os.makedirs(outfolder)
								fp = open(filepath, 'w+b')
								nca.rewind()
								Print.info(tabs)
								t = tqdm(total=nca.header.size, unit='B', unit_scale=True, leave=False)
								t.write(tabs + '-> Copying: ' + str(filename))
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
								#///////////////////////////////////						
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

	def updbase_tyc(self,ofolder,titleid):
		indent = 1
		tabs = '\t' * indent
		token='secure'
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for ticket in nspF:		
					if type(ticket) == Ticket:
						tik_id = str(ticket._path)
						tik_id =tik_id[:-20]
						if titleid == tik_id:
							ticket.rewind()
							data = ticket.read()
							filename =  str(ticket._path)
							outfolder = str(ofolder)+'/'
							filepath = os.path.join(outfolder, filename)
							if not os.path.exists(outfolder):
								os.makedirs(outfolder)
							fp = open(str(filepath), 'w+b')
							Print.info(tabs + 'Copying: ' + str(filename))
							fp.write(data)
							fp.flush()
							fp.close()
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for cert in nspF:				
					if cert._path.endswith('.cert'):
						cert_id = str(cert._path)
						cert_id =cert_id[:-21]
						if titleid == cert_id:				
							cert.rewind()
							data = cert.read()
							filename =  str(cert._path)
							outfolder = str(ofolder)+'/'
							filepath = os.path.join(outfolder, filename)
							if not os.path.exists(outfolder):
								os.makedirs(outfolder)
							fp = open(str(filepath), 'w+b')
							Print.info(tabs + 'Copying: ' + str(filename))
							fp.write(data)
							fp.flush()
							fp.close()
										
#GET VERSION NUMBER FROM CNMT							
	def get_cnmt_verID(self):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									cnmt.seek(0x8)
									titleversion = cnmt.read(0x4)
									Print.info(str(int.from_bytes(titleversion, byteorder='little')))	
									
#SIMPLE FILE-LIST			
	def print_file_list(self):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if nca._path.endswith('.cnmt.nca'):
							continue
						filename = str(nca._path)
						Print.info(str(filename))
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if nca._path.endswith('.cnmt.nca'):
							filename = str(nca._path)
							Print.info(str(filename))
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) != Nca:
						filename =  str(file._path)
						Print.info(str(filename))									

#ADVANCED FILE-LIST			
	def  adv_file_list(self):
		contentlist=list()	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					size1=0;size2=0;size3=0	
					if type(nca) == Nca:	
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()								
									min_sversion=cnmt.readInt32()
									length_of_emeta=cnmt.readInt32()	
									target=str(nca._path)
									content_type_cnmt=str(cnmt._path)
									content_type_cnmt=content_type_cnmt[:-22]		
									if content_type_cnmt == 'Patch':
										content_type='Update'
										reqtag='- RequiredSystemVersion: '
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)							
										if isdemo == 1:
											content_type='Demo Update'
										if isdemo == 2:
											content_type='RetailInteractiveDisplay Update'											
									if content_type_cnmt == 'AddOnContent':
										content_type='DLC'
										reqtag='- RequiredUpdateNumber: '
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
									if content_type_cnmt == 'Application':
										content_type='Base Game or Application'
										reqtag='- RequiredSystemVersion: '	
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
										if isdemo == 1:
											content_type='Demo'
										if isdemo == 2:
											content_type='RetailInteractiveDisplay'												
									cnmt.rewind()							
									cnmt.seek(0x20+offset)
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]
									version=str(int.from_bytes(titleversion, byteorder='little'))
									v_number=int(int(version)/65536)
									RS_number=int(min_sversion/65536)
									crypto1=nca.header.getCryptoType()
									crypto2=nca.header.getCryptoType2()	
									if crypto1 == 2:
										if crypto1 > crypto2:								
											keygen=nca.header.getCryptoType()
										else:			
											keygen=nca.header.getCryptoType2()	
									else:			
										keygen=nca.header.getCryptoType2()		
									MinRSV=sq_tools.getMinRSV(keygen,min_sversion)
									FW_rq=sq_tools.getFWRangeKG(keygen)
									RSV_rq=sq_tools.getFWRangeRSV(min_sversion)									
									RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)								
									Print.info('-----------------------------')
									Print.info('CONTENT ID: ' + str(titleid2))	
									Print.info('-----------------------------')			
									if content_type_cnmt != 'AddOnContent':									
										Print.info("Titleinfo:")							
										Print.info("- Name: " + tit_name)
										Print.info("- Editor: " + editor)
										Print.info("- Build number: " + str(ediver))
										suplangue=str((', '.join(SupLg)))
										Print.info("- Supported Languages: "+suplangue)
										Print.info("- Content type: "+content_type)
										Print.info("- Version: " + version+' -> '+content_type_cnmt+' ('+str(v_number)+')')
									if content_type_cnmt == 'AddOnContent':
										if tit_name != "DLC":
											Print.info("- Name: " + tit_name)
											Print.info("- Editor: " + editor)										
										Print.info("- Content type: "+"DLC")
										DLCnumb=str(titleid2)
										DLCnumb="0000000000000"+DLCnumb[-3:]									
										DLCnumb=bytes.fromhex(DLCnumb)
										DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
										DLCnumb=int(DLCnumb)
										Print.info("- DLC number: "+str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')')						
										Print.info("- DLC version Number: " + version+' -> '+"Version"+' ('+str(v_number)+')')												
									Print.info("")								
									Print.info("Required Firmware:")			
									if content_type_cnmt == 'AddOnContent':
										if v_number == 0:
											Print.info("- Required game version: " + str(min_sversion)+' -> '+"Application"+' ('+str(RS_number)+')')									
										if v_number > 0:
											Print.info("- Required game version: " + str(min_sversion)+' -> '+"Patch"+' ('+str(RS_number)+')')																									
									else:
										Print.info(reqtag + str(min_sversion)+" -> " +RSV_rq)						
									Print.info('- Encryption (keygeneration): ' + str(keygen)+" -> " +FW_rq)
									if content_type_cnmt != 'AddOnContent':							
										Print.info('- Patchable to: ' + str(MinRSV)+" -> " + RSV_rq_min)
									else:
										Print.info('- Patchable to: DLC -> no RSV to patch')	
									Print.info("")						
									ncalist = list()
									ncasize = 0							
									Print.info('......................')							
									Print.info('NCA FILES (NON DELTAS)')	
									Print.info('......................')							
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										ncatype = cnmt.read(0x1)
										ncatype = int.from_bytes(ncatype, byteorder='little')	
										unknown = cnmt.read(0x1)
										#Print.info(str(ncatype))
										if ncatype != 6:									
											nca_name=str(hx(NcaId))
											nca_name=nca_name[2:-1]+'.nca'
											ncasize=ncasize+self.print_nca_by_title(nca_name,ncatype)
											ncalist.append(nca_name[:-4])
											contentlist.append(nca_name)									
										if ncatype == 6:
											nca_name=str(hx(NcaId))
											nca_name=nca_name[2:-1]+'.nca'
											ncalist.append(nca_name[:-4])
											contentlist.append(nca_name)										
									nca_meta=str(nca._path)
									ncalist.append(nca_meta[:-4])	
									contentlist.append(nca_meta)							
									ncasize=ncasize+self.print_nca_by_title(nca_meta,0)
									size1=ncasize
									size_pr=sq_tools.getSize(ncasize)		
									bigtab="\t"*7
									Print.info(bigtab+"  --------------------")								
									Print.info(bigtab+'  TOTAL SIZE: '+size_pr)	
									if self.actually_has_deltas(ncalist)=="true":
										cnmt.rewind()
										cnmt.seek(0x20+offset)
										for i in range(content_entries):
											vhash = cnmt.read(0x20)
											NcaId = cnmt.read(0x10)
											size = cnmt.read(0x6)
											ncatype = cnmt.read(0x1)
											ncatype = int.from_bytes(ncatype, byteorder='little')		
											unknown = cnmt.read(0x1)								
											if ncatype == 6:							
												Print.info('......................')							
												Print.info('NCA FILES (DELTAS)')	
												Print.info('......................')	
												break
										cnmt.rewind()
										cnmt.seek(0x20+offset)
										ncasize = 0								
										for i in range(content_entries):
											vhash = cnmt.read(0x20)
											NcaId = cnmt.read(0x10)
											size = cnmt.read(0x6)
											ncatype = cnmt.read(0x1)
											ncatype = int.from_bytes(ncatype, byteorder='little')	
											unknown = cnmt.read(0x1)	
											if ncatype == 6:
												nca_name=str(hx(NcaId))
												nca_name=nca_name[2:-1]+'.nca'
												ncasize=ncasize+self.print_nca_by_title(nca_name,ncatype)
										size2=ncasize
										size_pr=sq_tools.getSize(ncasize)		
										bigtab="\t"*7
										Print.info(bigtab+"  --------------------")								
										Print.info(bigtab+'  TOTAL SIZE: '+size_pr)	
									if self.actually_has_other(titleid2,ncalist)=="true":								
										Print.info('......................')							
										Print.info('OTHER TYPES OF FILES')	
										Print.info('......................')
										othersize = 0								
										othersize=othersize+self.print_xml_by_title(ncalist,contentlist)	
										othersize=othersize+self.print_tac_by_title(titleid2,contentlist)
										othersize=othersize+self.print_jpg_by_title(ncalist,contentlist)
										size3=othersize								
										size_pr=sq_tools.getSize(othersize)							
										bigtab="\t"*7
										Print.info(bigtab+"  --------------------")								
										Print.info(bigtab+'  TOTAL SIZE: '+size_pr)
							finalsize=size1+size2+size3	
							size_pr=sq_tools.getSize(finalsize)	
							Print.info("/////////////////////////////////////")							
							Print.info('   FULL CONTENT TOTAL SIZE: '+size_pr+"   ")
							Print.info("/////////////////////////////////////")	
							Print.info("")								
				self.printnonlisted(contentlist)
																				
	def print_nca_by_title(self,nca_name,ncatype):	
		tab="\t"
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:		
					if type(nca) == Nca:
						filename = str(nca._path)
						if filename == nca_name:
							size=nca.header.size
							size_pr=sq_tools.getSize(size)
							content=str(nca.header.contentType)
							content=content[8:]+": "
							ncatype=sq_tools.getTypeFromCNMT(ncatype)	
							if ncatype != "Meta: ":
								Print.info("- "+ncatype+tab+str(filename)+tab+tab+"Size: "+size_pr)	
							else:
								Print.info("- "+ncatype+tab+str(filename)+tab+"Size: "+size_pr)		
							return size		
	def print_xml_by_title(self,ncalist,contentlist):	
		tab="\t"
		size2return=0
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:		
					if file._path.endswith('.xml'):
						size=file.size
						size_pr=sq_tools.getSize(size)			
						filename =  str(file._path)	
						xml=filename[:-4]
						if xml in ncalist:
							Print.info("- XML: "+tab*2+str(filename)+tab+"Size: "+size_pr)
							contentlist.append(filename)	
							size2return=size+size2return			
		return size2return						
	def print_tac_by_title(self,titleid,contentlist):		
		tab="\t"	
		size2return=0	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for ticket in nspF:			
					if type(ticket) == Ticket:
						size=ticket.size			
						size_pr=sq_tools.getSize(size)			
						filename =  str(ticket._path)
						tik=filename[:-20]
						if tik == titleid:
							Print.info("- Ticket: "+tab+str(filename)+tab*2+"Size: "+size_pr)	
							contentlist.append(filename)					
							size2return=size+size2return													
				for cert in nspF:						
					if cert._path.endswith('.cert'):
						size=cert.size		
						size_pr=sq_tools.getSize(size)
						filename = str(cert._path)
						cert_id =filename[:-21]
						if cert_id == titleid:
							Print.info("- Cert: "+tab+str(filename)+tab*2+"Size: "+size_pr)
							contentlist.append(filename)					
							size2return=size+size2return
		return size2return				
	def print_jpg_by_title(self,ncalist,contentlist):	
		size2return=0
		tab="\t"
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":		
				for file in nspF:
					if file._path.endswith('.jpg'):
						size=file.size
						size_pr=sq_tools.getSize(size)			
						filename =  str(file._path)	
						jpg=filename[:32]
						if jpg in ncalist:
							Print.info("- JPG: "+tab*2+"..."+str(filename[-38:])+tab+"Size: "+size_pr)		
							contentlist.append(filename)					
							size2return=size+size2return
		return size2return		
	def actually_has_deltas(self,ncalist):	
		vfragment="false"	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.DATA':
							for f in nca:
									for file in f:
										filename = str(file._path)
										if filename=="fragment":
											if 	nca._path[:-4] in ncalist:	
												vfragment="true"
												break
		return vfragment
	def actually_has_other(self,titleid,ncalist):
		vother="false"	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":		
				for file in nspF:
					if file._path.endswith('.xml'):
						filename =  str(file._path)	
						xml=filename[:-4]
						if xml in ncalist:
							vother="true"	
							break		
					if type(file) == Ticket:		
						filename =  str(file._path)
						tik=filename[:-20]
						if tik == titleid:
							vother="true"	
							break																
					if file._path.endswith('.cert'):
						filename = str(file._path)
						cert_id =filename[:-21]
						if cert_id == titleid:
							vother="true"	
							break		
					if file._path.endswith('.jpg'):
						filename =  str(file._path)	
						jpg=filename[:32]
						if jpg in ncalist:
							vother="true"	
							break	
		return vother					
	def printnonlisted(self,contentlist):
		tab="\t"	
		list_nonlisted="false"
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":		
				for file in nspF:		
					filename =  str(file._path)
					if not filename in contentlist:
						list_nonlisted="true"
		if list_nonlisted == "true":
			Print.info('-----------------------------------')
			Print.info('FILES NOT LINKED TO CONTENT IN NSP')
			Print.info('-----------------------------------')	
			totsnl=0
			for nspF in self.hfs0:
				if str(nspF._path)=="secure":		
					for file in nspF:				
						filename =  str(file._path)
						if not filename in contentlist:
							totsnl=totsnl+file.size
							size_pr=sq_tools.getSize(file.size)						
							Print.info(str(filename)+3*tab+"Size: "+size_pr)		
			bigtab="\t"*7
			size_pr=sq_tools.getSize(totsnl)					
			Print.info(bigtab+"  --------------------")								
			Print.info(bigtab+'  TOTAL SIZE: '+size_pr)			

#ADVANCED FILE-LIST			
	def  adv_content_list(self):
		applist=list();	applist_ID=list()		
		patchlist=list(); patchlist_ID=list()	
		dlclist=list();	dlclist_ID=list()
		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					size1=0;size2=0;size3=0	
					if type(nca) == Nca:	
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:		
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleid = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid = titleid[2:-1]							
									titleversion = cnmt.read(0x4)
									version=str(int.from_bytes(titleversion, byteorder='little'))							
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()	
									original_ID = str(hx(original_ID.to_bytes(8, byteorder='big'))) 	
									original_ID = original_ID[2:-1]								
									min_sversion=cnmt.readInt32()
									length_of_emeta=cnmt.readInt32()	
									target=str(nca._path)
									content_type_cnmt=str(cnmt._path)
									content_type_cnmt=content_type_cnmt[:-22]	
									if content_type_cnmt == 'Application':
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)							
										applist.append([target,titleid,version,tit_name,editor])
									if content_type_cnmt == 'Patch':
										patchlist.append([target,original_ID,version,titleid])
										patchlist_ID.append(target)
									if content_type_cnmt == 'AddOnContent':
										DLCnumb=str(titleid)
										DLCnumb="0000000000000"+DLCnumb[-3:]									
										DLCnumb=bytes.fromhex(DLCnumb)
										DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
										DLCnumb=int(DLCnumb)
										dlclist.append([target,original_ID,version,titleid,DLCnumb])

		applist=sorted(applist, key=itemgetter(1))
		patchlist=sorted(patchlist, key=itemgetter(1))		
		dlclist=sorted(dlclist, key=itemgetter(4))
		patch_called=list()
		dlc_called=list()		
		for i in range(len(applist)):		
			tid=applist[i][1]		
			Print.info('------------------------------------------------')
			Print.info('BASE CONTENT ID: ' + str(tid))	
			Print.info('------------------------------------------------')
			Print.info('Name: '+applist[i][3])	
			Print.info('Editor: '+applist[i][4])	
			Print.info('------------------------------------------------')
			print(applist[i][1]+" [BASE]"+" v"+applist[i][2])
			cupd=0
			for j in range(len(patchlist)):
				if tid == patchlist[j][1]:
					v=patchlist[j][2]
					v_number=str(int(int(v)/65536))
					print(patchlist[j][3]+" [UPD]"+" v"+patchlist[j][2]+" -> Patch("+v_number+")")
					cupd+=1
					patch_called.append(patchlist[j])
			cdlc=0					
			for k in range(len(dlclist)):
				if tid == dlclist[k][1]:
					print(dlclist[k][3]+" [DLC "+str(dlclist[k][4])+"]"+" v"+dlclist[k][2])	
					cdlc+=1		
					dlc_called.append(dlclist[k])					
			Print.info('------------------------------------------------')
			Print.info('CONTENT INCLUDES: 1 BASEGAME '+str(cupd)+' UPDATES '+str(cdlc)+' DLCS')	
			Print.info('------------------------------------------------')		
			if len(patchlist) != len(patch_called):
				Print.info('------------------------------------------------')
				Print.info('ORPHANED UPDATES:')
				Print.info('------------------------------------------------')	
				for j in range(len(patchlist)):	
					if patchlist[j] not in patch_called:
						v=patchlist[j][2]
						v_number=str(int(int(v)/65536))
						print(patchlist[j][3]+" [UPD]"+" v"+patchlist[j][2]+" -> Patch("+v_number+")")						
			if len(dlclist) != len(dlc_called):
				Print.info('------------------------------------------------')
				Print.info('ORPHANED DLCS:')
				Print.info('------------------------------------------------')	
				for k in range(len(dlclist)):	
					if dlclist[k] not in dlc_called:
						print(dlclist[k][3]+" [DLC "+str(dlclist[k][4])+"]"+" v"+dlclist[k][2])		
				
				
#///////////////////////////////////////////////////								
#INFO ABOUT UPD REQUIREMENTS
#///////////////////////////////////////////////////	
	def print_fw_req(self):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()
									RSversion=cnmt.readInt32()
									Emeta=cnmt.readInt32()
									target=str(nca._path)
									content_type_cnmt=str(cnmt._path)
									content_type_cnmt=content_type_cnmt[:-22]		
									if content_type_cnmt == 'Patch':
										content_type='Update'
										reqtag='- RequiredSystemVersion: '
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)							
										if isdemo == 1:
											content_type='Demo Update'
										if isdemo == 2:
											content_type='RetailInteractiveDisplay Update'											
									if content_type_cnmt == 'AddOnContent':
										content_type='DLC'
										reqtag='- RequiredUpdateNumber: '
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
									if content_type_cnmt == 'Application':
										content_type='Base Game or Application'
										reqtag='- RequiredSystemVersion: '	
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
										if isdemo == 1:
											content_type='Demo'
										if isdemo == 2:
											content_type='RetailInteractiveDisplay'											
									cnmt.rewind()							
									cnmt.seek(0x20+offset)
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]
									version=str(int.from_bytes(titleversion, byteorder='little'))
									v_number=int(int(version)/65536)
									RS_number=int(RSversion/65536)									
									crypto1=nca.header.getCryptoType()
									crypto2=nca.header.getCryptoType2()	
									if crypto1 == 2:
										if crypto1 > crypto2:								
											keygen=nca.header.getCryptoType()
										else:			
											keygen=nca.header.getCryptoType2()	
									else:			
										keygen=nca.header.getCryptoType2()					
									MinRSV=sq_tools.getMinRSV(keygen,RSversion)
									FW_rq=sq_tools.getFWRangeKG(keygen)
									RSV_rq=sq_tools.getFWRangeRSV(RSversion)									
									RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)
									content_type_cnmt=str(cnmt._path)
									content_type_cnmt=content_type_cnmt[:-22]		
									if content_type_cnmt == 'Patch':
										content_type='Update'
										reqtag='- RequiredSystemVersion: '
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)							
										if isdemo == 1:
											content_type='Demo Update'
										if isdemo == 2:
											content_type='RetailInteractiveDisplay Update'												
									if content_type_cnmt == 'AddOnContent':
										content_type='DLC'
										reqtag='- RequiredUpdateNumber: '
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
									if content_type_cnmt == 'Application':
										content_type='Base Game or Application'
										reqtag='- RequiredSystemVersion: '	
										tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
										if isdemo == 1:
											content_type='Demo'
										if isdemo == 2:
											content_type='RetailInteractiveDisplay'												
									Print.info('-----------------------------')
									Print.info('CONTENT ID: ' + str(titleid2))	
									Print.info('-----------------------------')			
									if content_type_cnmt != 'AddOnContent':									
										Print.info("Titleinfo:")							
										Print.info("- Name: " + tit_name)
										Print.info("- Editor: " + editor)
										Print.info("- Build number: " + str(ediver))
										suplangue=str((', '.join(SupLg)))
										Print.info("- Supported Languages: "+suplangue)
										Print.info("- Content type: "+content_type)
										Print.info("- Version: " + version+' -> '+content_type_cnmt+' ('+str(v_number)+')')									
									if content_type_cnmt == 'AddOnContent':
										Print.info("Titleinfo:")
										if tit_name != "DLC":
											Print.info("- Name: " + tit_name)
											Print.info("- Editor: " + editor)										
										Print.info("- Content type: "+"DLC")
										DLCnumb=str(titleid2)
										DLCnumb="0000000000000"+DLCnumb[-3:]									
										DLCnumb=bytes.fromhex(DLCnumb)
										DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
										DLCnumb=int(DLCnumb)
										Print.info("- DLC number: "+str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')')					
										Print.info("- DLC version Number: " + version+' -> '+"Version"+' ('+str(v_number)+')')
									Print.info("")								
									Print.info("Required Firmware:")			
									if content_type_cnmt == 'AddOnContent':
										if v_number == 0:
											Print.info("- Required game version: " + str(RSversion)+' -> '+"Application"+' ('+str(RS_number)+')')									
										if v_number > 0:
											Print.info("- Required game version: " + str(RSversion)+' -> '+"Patch"+' ('+str(RS_number)+')')																									
									else:
										Print.info(reqtag + str(RSversion)+" -> " +RSV_rq)						
									Print.info('- Encryption (keygeneration): ' + str(keygen)+" -> " +FW_rq)
									if content_type_cnmt != 'AddOnContent':							
										Print.info('- Patchable to: ' + str(MinRSV)+" -> " + RSV_rq_min)
									else:
										Print.info('- Patchable to: DLC -> no RSV to patch')	
									Print.info("")											
						
	def inf_get_title(self,target,offset,content_entries,original_ID):
		content_type=''
		token='secure'		
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:
					if type(nca) == Nca:
						if target ==  str(nca._path):
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()					
									cnmt.seek(0x20+offset)	
									nca_name='false'
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										ncatype = cnmt.read(0x1)
										unknown = cnmt.read(0x1)
										ncatype2 = int.from_bytes(ncatype, byteorder='little')
										if ncatype2 == 3:
											nca_name=str(hx(NcaId))
											nca_name=nca_name[2:-1]+'.nca'
		if nca_name=='false':
			for nspF in self.hfs0:
				if token == str(nspF._path):
					for nca in nspF:		
						if type(nca) == Nca:
							if 	str(nca.header.contentType) == 'Content.META':
								for f in nca:
									for cnmt in f:
										cnmt.rewind()
										testID=cnmt.readInt64()
										if 	testID == original_ID:
											nca.rewind()
											f.rewind()								
											titleid=cnmt.readInt64()
											titleversion = cnmt.read(0x4)
											cnmt.rewind()
											cnmt.seek(0xE)
											offset=cnmt.readInt16()
											content_entries=cnmt.readInt16()
											meta_entries=cnmt.readInt16()
											cnmt.rewind()
											cnmt.seek(0x20)
											original_ID=cnmt.readInt64()
											min_sversion=self.readInt32()
											end_of_emeta=self.readInt32()	
											target=str(nca._path)
											contentname,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
											cnmt.rewind()
											cnmt.seek(0x20+offset)	
		title = 'DLC'									
		for nspF in self.hfs0:
			if token == str(nspF._path):
				for nca in nspF:		
					if type(nca) == Nca:
						if nca_name == str(nca._path):
							if 	str(nca.header.contentType) == 'Content.CONTROL':
								title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title)
								return(title,editor,ediver,SupLg,regionstr,isdemo)
		regionstr="0|0|0|0|0|0|0|0|0|0|0|0|0|0"								
		return(title,"","","",regionstr,"")	

		
												
	def pack(self,upd_list,norm_list,sec_list,buffer,fat):
		if not self.path:
			return False
		indent = 1
		tabs = '\t' * indent		
		hfs0 = Fs.Hfs0(None, None)				
		root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=hfs0.genRHeader(upd_list,norm_list,sec_list)
		#print(hx(root_header))
		xci_header,game_info,sig_padding,xci_certificate=self.genheader(root_header,rootSize)	
		totSize=len(xci_header)+len(game_info)+len(sig_padding)+len(xci_certificate)+rootSize
	
		if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
			Print.info('\t\tRepack %s is already complete!' % self.path)
			return
		outfile=self.path
		Print.info('Generating XCI:')	
		print("")
		if totSize <= 4294934528:
			fat="exfat"
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294934528)
			index=0
			outfile=outfile[:-1]+str(index)
		c=0
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing XCI header...')
		outf = open(outfile, 'wb')
		outf.write(xci_header)
		t.update(len(xci_header))
		c=c+len(xci_header)				
		t.write(tabs+'- Writing XCI game info...')		
		outf.write(game_info)	
		t.update(len(game_info))
		c=c+len(game_info)					
		t.write(tabs+'- Generating padding...')
		outf.write(sig_padding)	
		t.update(len(sig_padding))			
		c=c+len(sig_padding)			
		t.write(tabs+'- Writing XCI certificate...')
		outf.write(xci_certificate)	
		t.update(len(xci_certificate))	
		c=c+len(xci_certificate)			
		t.write(tabs+'- Writing ROOT HFS0 header...')		
		outf.write(root_header)
		t.update(len(root_header))
		c=c+len(root_header)				
		t.write(tabs+'- Writing UPDATE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(upd_multiplier))	
		outf.write(upd_header)
		t.update(len(upd_header))
		c=c+len(upd_header)			
		for file in upd_list:
			t.write(tabs+'- Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(int(buffer))
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))
					c=c+len(buf)						
		t.write(tabs+'- Writing NORMAL partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(norm_multiplier))			
		outf.write(norm_header)
		t.update(len(norm_header))
		c=c+len(norm_header)	
		for file in norm_list:
			t.write(tabs+'- Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(int(buffer))
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))	
					c=c+len(buf)					
		t.write(tabs+'- Writing SECURE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(sec_multiplier))		
		outf.write(sec_header)
		t.update(len(sec_header))
		c=c+len(sec_header)		
		block=4294934528	
		for file in sec_list:
			t.write(tabs+'  > Appending %s' % os.path.basename(file))
			if file.endswith('.nca'):
				nca =Fs.Nca(file, 'r+b')
				nca.rewind()			
				if	nca.header.getgamecard() == 0:	
					masterKeyRev = nca.header.getCryptoType2()		
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
					crypto = aes128.AESECB(key)					
					KB1L=nca.header.getKB1L()
					KB1L = crypto.decrypt(KB1L)
					if sum(KB1L) == 0:					
						nca.header.setgamecard(1)
				nca.flush()
				nca.close()								
			with open(file, 'rb') as inf:
				while True:
					data = inf.read(int(buffer))
					outf.write(data)
					t.update(len(data))	
					c=c+len(data)
					if fat=="fat32" and (c+len(data))>block:
						n2=block-c
						c=0
						dat2=inf.read(int(n2))
						outf.write(dat2)
						outf.flush()
						outf.close()	
						t.update(len(dat2))
						index=index+1
						outfile=outfile[0:-1]
						outfile=outfile+str(index)
						outf = open(outfile, 'wb')					
					if not data:
						break								
		t.close()
		print("")
		print("Closing file. Please wait")		
		outf.close()			
		
	def genheader(self,root_header,rootSize):		
		signature=sq_tools.randhex(0x100)
		signature= bytes.fromhex(signature)
		sec_offset=root_header[0x90:0x90+0x8]	
		sec_offset=int.from_bytes(sec_offset, byteorder='little')
		sec_offset=int((sec_offset+0xF000+0x200)/0x200)
		sec_offset=sec_offset.to_bytes(4, byteorder='little')
		back_offset=(0xFFFFFFFF).to_bytes(4, byteorder='little')
		kek=(0x00).to_bytes(1, byteorder='big')
		tot_size=0xF000+rootSize
		cardsize,access_freq=sq_tools.getGCsize(tot_size)
		cardsize=cardsize.to_bytes(1, byteorder='big')
		GC_ver=(0x00).to_bytes(1, byteorder='big')
		GC_flag=(0x00).to_bytes(1, byteorder='big')
		pack_id=(0x8750F4C0A9C5A966).to_bytes(8, byteorder='big')
		valid_data=int(((tot_size-0x1)/0x200))
		valid_data=valid_data.to_bytes(8, byteorder='little')	
		
		try:
			key= Keys.get('xci_header_key')
			key= bytes.fromhex(key)
			IV=sq_tools.randhex(0x10)
			IV= bytes.fromhex(IV)
			xkey=True
			#print(hx(IV))
			#print("i'm here") 
		except:
			IV=(0x5B408B145E277E81E5BF677C94888D7B).to_bytes(16, byteorder='big')
			xkey=False
			#print("i'm here 2") 
			
		HFS0_offset=(0xF000).to_bytes(8, byteorder='little')
		len_rHFS0=(len(root_header)).to_bytes(8, byteorder='little')
		sha_rheader=sha256(root_header[0x00:0x200]).hexdigest()	
		sha_rheader=bytes.fromhex(sha_rheader)	
		sha_ini_data=bytes.fromhex('1AB7C7B263E74E44CD3C68E40F7EF4A4D6571551D043FCA8ECF5C489F2C66E7E')	
		SM_flag=(0x01).to_bytes(4, byteorder='little')
		TK_flag=(0x02).to_bytes(4, byteorder='little')		
		K_flag=(0x0).to_bytes(4, byteorder='little')
		end_norm = sec_offset

		header =  b''
		header += signature
		header += b'HEAD'
		header += sec_offset
		header += back_offset
		header += kek	
		header += cardsize	
		header += GC_ver
		header += GC_flag
		header += pack_id
		header += valid_data		
		header += IV		
		header += HFS0_offset				
		header += len_rHFS0		
		header += sha_rheader	
		header += sha_ini_data
		header += SM_flag	
		header += TK_flag	
		header += K_flag			
		header += end_norm
		
		#Game_info
		if xkey==True:
			firm_ver='0100000000000000'
			access_freq=access_freq
			Read_Wait_Time='88130000'
			Read_Wait_Time2='00000000'
			Write_Wait_Time='00000000'		
			Write_Wait_Time2='00000000'		
			Firmware_Mode='00110C00'		
			CUP_Version='5a000200'		
			Empty1='00000000'
			Upd_Hash='9bfb03ddbb7c5fca'
			CUP_Id='1608000000000001'
			Empty2='00'*0x38	
			#print(hx(Empty2))
		
			firm_ver=bytes.fromhex(firm_ver)	
			access_freq=bytes.fromhex(access_freq)	
			Read_Wait_Time=bytes.fromhex(Read_Wait_Time)
			Read_Wait_Time2=bytes.fromhex(Read_Wait_Time2)
			Write_Wait_Time=bytes.fromhex(Write_Wait_Time)
			Write_Wait_Time2=bytes.fromhex(Write_Wait_Time2)		
			Firmware_Mode=bytes.fromhex(Firmware_Mode)
			CUP_Version=bytes.fromhex(CUP_Version)
			Empty1=bytes.fromhex(Empty1)
			Upd_Hash=bytes.fromhex(Upd_Hash)
			CUP_Id=bytes.fromhex(CUP_Id)		
			Empty2=bytes.fromhex(Empty2)	
		
			Game_info =  b''
			Game_info += firm_ver
			Game_info += access_freq
			Game_info += Read_Wait_Time
			Game_info += Read_Wait_Time2		
			Game_info += Write_Wait_Time
			Game_info += Write_Wait_Time2
			Game_info += Firmware_Mode
			Game_info += CUP_Version
			Game_info += Empty1
			Game_info += Upd_Hash
			Game_info += CUP_Id		
			Game_info += Empty2	
			
			gamecardInfoIV=IV[::-1]	
			crypto = aes128.AESCBC(key, gamecardInfoIV)
			enc_info=crypto.encrypt(Game_info)					
		if xkey==False:
			enc_info=sq_tools.get_enc_gameinfo(tot_size)
		
		#print (hx(enc_info))		
		
		#Padding
		sig_padding='00'*0x6E00
		sig_padding=bytes.fromhex(sig_padding)		
		#print (hx(sig_padding))	
		
		#CERT
		fake_CERT='FF'*0x8000
		fake_CERT=bytes.fromhex(fake_CERT)				
		#print (hx(fake_CERT))
		return header,enc_info,sig_padding,fake_CERT
		
	def print_head(self):

		gamecardInfoIV=self.gamecardInfoIV[::-1]
		#print (str(hx(gamecardInfoIV)))
		try:
			key= Keys.get('xci_header_key')
			key= bytes.fromhex(key)
		except:
			pass
		#print(hx(key))
		crypto = aes128.AESCBC(key, gamecardInfoIV)
		#print (self.gamecardInfo.firmwareVersion)
		self.seek(0x190)

		encrypted_info=self.read(0x70)		

		firm_ver= encrypted_info[0x00:0x00+0x8]
		access_freq= encrypted_info[0x08:0x08+0x4]	
		Read_Wait_Time= encrypted_info[0xC:0xC+0x4]	
		Read_Wait_Time2= encrypted_info[0x10:0x10+0x4]	
		Write_Wait_Time= encrypted_info[0x14:0x14+0x4]	
		Write_Wait_Time2= encrypted_info[0x18:0x18+0x4]	
		Firmware_Mode = encrypted_info[0x1C:0x1C+0x4]	
		CUP_Version  = encrypted_info[0x20:0x20+0x4]
		Empty1=encrypted_info[0x24:0x24+0x4]
		Update_Partition_Hash=encrypted_info[0x28:0x28+0x8] 
		CUP_Id =encrypted_info[0x30:0x30+0x8]
		Empty2=encrypted_info[0x38:0x38+0x38]		
		
		print ('firmware version: '+str(hx(firm_ver)))	
		print ('access freq: '+str(hx(access_freq)))
		print ('Read_Wait_Time: '+str(hx(Read_Wait_Time)))
		print ('Read_Wait_Time2: '+str(hx(Read_Wait_Time2)))	
		print ('Write_Wait_Time: '+str(hx(Write_Wait_Time)))
		print ('Write_Wait_Time2: '+str(hx(Write_Wait_Time2)))	
		print ('Firmware_Mode: '+str(hx(Firmware_Mode)))	
		print ('CUP_Version: '+str(hx(CUP_Version)))			
		print ('Empty1: '+str(hx(Empty1)))
		print ('Update_Partition_Hash: '+str(hx(Update_Partition_Hash)))
		print ('CUP_Id: '+str(hx(CUP_Id)))
		print ('Empty2: '+str(hx(Empty2)))		

		#upd_hash= dec_info[0x28:0x28+0x8]
		#print (hx(upd_hash))	
		#print (hx(encrypted_info))	
		#print (hx(dec_info))
	
	def supertrim(self,buffer,outfile,ofolder,fat):

		indent = 1
		rightsId = 0
		tabs = '\t' * indent		
		xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier	=self.get_header()	 			
		
		totSize=len(xci_header)+len(game_info)+len(sig_padding)+len(xci_certificate)+rootSize
	
		if os.path.exists(outfile) and os.path.getsize(outfile) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return
			
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for ticket in nspF:
					if type(ticket) == Ticket:
						masterKeyRev = ticket.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = ticket.getRightsId()
				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')

				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() == 0:
								if nca.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break	
									
		Print.info('Generating XCI:')	
		if rightsId	!=0:	
			Print.info('rightsId =\t' + hex(rightsId))
			Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
			Print.info('masterKeyRev =\t' + hex(masterKeyRev))									
		print("")
		
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294934528)
			index=0
			outfile=outfile[:-1]+str(index)
		c=0
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing XCI header...')
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)
		outf = open(outfile, 'wb')
		outf.write(xci_header)
		t.update(len(xci_header))		
		c=c+len(xci_header)
		t.write(tabs+'- Writing XCI game info...')		
		outf.write(game_info)	
		t.update(len(game_info))	
		c=c+len(game_info)
		t.write(tabs+'- Generating padding...')
		outf.write(sig_padding)	
		t.update(len(sig_padding))		
		c=c+len(sig_padding)		
		t.write(tabs+'- Writing XCI certificate...')
		outf.write(xci_certificate)	
		t.update(len(xci_certificate))	
		c=c+len(xci_certificate)		
		t.write(tabs+'- Writing ROOT HFS0 header...')		
		outf.write(root_header)
		t.update(len(root_header))
		c=c+len(root_header)
		t.write(tabs+'- Writing UPDATE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(upd_multiplier))	
		outf.write(upd_header)
		t.update(len(upd_header))
		c=c+len(upd_header)
		t.write(tabs+'- Writing NORMAL partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(norm_multiplier))			
		outf.write(norm_header)
		t.update(len(norm_header))
		c=c+len(norm_header)
		t.write(tabs+'- Writing SECURE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(sec_multiplier))		
		outf.write(sec_header)
		t.update(len(sec_header))
		c=c+len(sec_header)			
									
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				block=4294934528			
				for nca in nspF:
					#if type(file) == Nca or type(file) == Ticket or file._path.endswith('.cert'):				
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:						
							nca.rewind()
							t.write(tabs+'- Appending: ' + str(nca._path))
							crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
							hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))							
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)	
							nca.rewind()					
							i=0
							for data in iter(lambda: nca.read(int(buffer)), ""):
								if i==0:
									nca.rewind()							
									rawhead=nca.read(0xC00)
									rawhead=hcrypto.decrypt(rawhead)
									header = b''
									header += rawhead[0x00:0x00+0x230]		
									tr='00'*0x10
									tr=bytes.fromhex(tr)							
									header += tr
									header += rawhead[0x240:0x240+0xC0]	
									header += encKeyBlock
									header += rawhead[0x340:]
									newheader=hcrypto.encrypt(header)							
									if fat=="fat32" and (c+len(newheader))>block:
										n2=block-c
										c=0
										dat2=newheader[0x00:0x00+int(n2)]
										outf.write(dat2)
										outf.flush()
										outf.close()	
										t.update(len(dat2))
										index=index+1
										outfile=outfile[0:-1]
										outfile=outfile+str(index)
										outf = open(outfile, 'wb')	
										dat2=newheader[0x00+int(n2)+1:]
										outf.write(dat2)						
										t.update(len(dat2))									
										outf.flush()	
									else:
										outf.write(newheader)
										t.update(len(newheader))	
										c=c+len(newheader)								
									nca.seek(0xC00)									
									i+=1		
								else:			
									outf.write(data)
									t.update(len(data))
									c=c+len(data)
									outf.flush()
									if fat=="fat32" and (c+len(data))>block:
										n2=block-c
										c=0
										dat2=nca.read(int(n2))
										outf.write(dat2)
										outf.flush()
										outf.close()	
										t.update(len(dat2))
										index=index+1
										outfile=outfile[0:-1]
										outfile=outfile+str(index)
										outf = open(outfile, 'wb')
										if totSize>(4294934528+int(buffer)):
											dat2=nca.read(int(buffer))
											outf.write(dat2)						
											t.update(len(dat2))									
											outf.flush()	
									if not data:
										break
						if nca.header.getRightsId() == 0:						
							nca.rewind()
							#fp.seek(pos)
							t.write(tabs+'- Appending: ' + str(nca._path))
							for data in iter(lambda: nca.read(int(buffer)), ""):
								outf.write(data)
								t.update(len(data))
								c=c+len(data)
								outf.flush()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									dat2=nca.read(int(n2))
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')
									if totSize>(4294934528+int(buffer)):
										dat2=nca.read(int(buffer))
										outf.write(dat2)						
										t.update(len(dat2))									
										outf.flush()	
								if not data:
									break									
		t.close()
		print("")
		print("Closing file. Please wait")
		outf.close()	
				
		
	def get_header(self):
		upd_list=list()
		upd_fileSizes = list()		
		norm_list=list()
		norm_fileSizes = list()			
		sec_list=list()
		sec_fileSizes = list()		
		sec_shalist = list()			
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					#if type(file) == Nca or type(file) == Ticket or file._path.endswith('.cert'):
					if type(file) == Nca:					
						sec_list.append(file._path)	
						if type(file) == Nca:
							sec_fileSizes.append(file.header.size)
						#if  type(file) == Ticket or file._path.endswith('.cert'):
						#	sec_fileSizes.append(file.size)
						file.rewind()
						hblock = file.read(0x200)
						sha=sha256(hblock).hexdigest()	
						sec_shalist.append(sha)		
						
		hfs0 = Fs.Hfs0(None, None)							
		root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=hfs0.gen_rhfs0_head(upd_list,norm_list,sec_list,sec_fileSizes,sec_shalist)
		#print (hx(root_header))
		tot_size=0xF000+rootSize
		
		sec_offset=root_header[0x90:0x90+0x8]	
		sec_offset=int.from_bytes(sec_offset, byteorder='little')
		sec_offset=int((sec_offset+0xF000+0x200)/0x200)
		sec_offset=sec_offset.to_bytes(4, byteorder='little')
		backupOffset=self.backupOffset
		titleKekIndex = self.titleKekIndex	
		cardsize,access_freq=sq_tools.getGCsize(tot_size)
		cardsize=cardsize.to_bytes(1, byteorder='big')
		gamecardHeaderVersion = self.gamecardHeaderVersion
		gamecardFlags = self.gamecardFlags
		packageId = self.packageId
		validDataEndOffset = self.validDataEndOffset		
		gamecardInfoIV = self.gamecardInfoIV			
		secureMode = self.secureMode	
		titleKeyFlag = self.titleKeyFlag
		keyFlag = self.keyFlag
		
		HFS0_offset=(0xF000).to_bytes(8, byteorder='little')
		valid_data=int(((tot_size-0x1)/0x200))
		valid_data=valid_data.to_bytes(8, byteorder='little')		
		len_rHFS0 = (len(root_header)).to_bytes(8, byteorder='little')
		sha_rheader	= sha256(root_header[0x00:0x200]).hexdigest()	
		sha_rheader=bytes.fromhex(sha_rheader)		
		sha_ini_data = self.hfs0InitialDataHash	
		end_norm = sec_offset		
		
		header =  b''
		header += self.signature
		header += self.magic
		header += sec_offset
		header += backupOffset.to_bytes(4, byteorder='little')
		header += titleKekIndex.to_bytes(1, byteorder='little')	
		header += cardsize
		header += gamecardHeaderVersion.to_bytes(1, byteorder='little')
		header += gamecardFlags.to_bytes(1, byteorder='little')
		header += packageId.to_bytes(8, byteorder='little')
		header += valid_data	
		header += self.gamecardInfoIV		
		header += HFS0_offset				
		header += len_rHFS0		
		header += sha_rheader	
		header += sha_ini_data
		header += secureMode.to_bytes(4, byteorder='little')	
		header += titleKeyFlag.to_bytes(4, byteorder='little')
		header += keyFlag.to_bytes(4, byteorder='little')		
		header += end_norm				
		#print (hx(header))	

		self.seek(0x190)
		gamecard_info=self.read(0x70)	
		#print (hx(gamecard_info))		
		sig_padding='00'*0x6E00
		sig_padding=bytes.fromhex(sig_padding)		
		#print (hx(sig_padding))	
		#gamecardCert
		CERT_padding='FF'*0x7E0C
		CERT_padding=bytes.fromhex(CERT_padding)				
		#print (hx(fake_CERT))
		CERT = b''
		CERT += self.gamecardCert.signature
		CERT += self.gamecardCert.magic
		CERT += self.gamecardCert.unknown1
		CERT += self.gamecardCert.unknown2		
		CERT += self.gamecardCert.data
		CERT += CERT_padding			
		#print (hx(CERT))	


		return header,gamecard_info,sig_padding,CERT,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier
		
		

	def metapatcher(self,metapatch,RSV_cap,keypatch):					
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':				
							if metapatch == 'true':
								if 	str(nca.header.contentType) == 'Content.META':
									filename=nca
									try:
										f = Fs.Nca(filename, 'r+b')
										f.write_req_system(number)
									except BaseException as e:
										Print.error('Exception: ' + str(e))				
						
						
#///////////////////////////////////////////////////								
#DIRECT NSP TO XCI
#///////////////////////////////////////////////////								
						
	def c_nsp_direct(self,buffer,outfile,ofolder,fat,fx,delta,metapatch,RSV_cap,keypatch):
	
		t = tqdm(total=False, unit='B', unit_scale=False, leave=False)	
		
		if keypatch != 'false':
			try:
				keypatch = int(keypatch)
			except:
				print("New keygeneration is no valid integer")
		indent = 1
		tabs = '\t' * indent
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Ticket:		
						masterKeyRev = file.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = file.getRightsId()						
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if nca.header.getRightsId() != 0:			
							if nca.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if type(nca) == Nca:				
						if nca.header.getRightsId() != 0:
							if nca.header.getCryptoType2() == 0:
								if nca.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break	
							
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:		
					if type(nca) == Nca and str(nca.header.contentType) == 'Content.META':	
						nca.rewind()
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()	
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:	
							masterKeyRev=crypto1						
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))	
						gc_flag='00'*0x01											
						filename =  str(nca._path)
						outfolder = str(ofolder)	
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						fp = open(filepath, 'w+b')
						nca.rewind()
						for data in iter(lambda: nca.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							if not data:
								break		
						fp.close()
						#///////////////////////////////////					
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()
						encKeyBlock = target.header.getKeyBlock()
						if keypatch != 'false':					
							if keypatch < target.header.getCryptoType2():
								encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)								
						newheader=self.get_newheader(target,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)	
						target.rewind()	
						target.write(newheader)								
						target.close()			
						if metapatch == 'true':
							target = Fs.Nca(filepath, 'r+b')
							target.rewind()					
							if 	str(target.header.contentType) == 'Content.META':
								for pfs0 in target:
									for cnmt in pfs0:
										check=str(cnmt._path)
										check=check[:-22]
										if check == 'AddOnContent':
											target.close()										
										else:	
											target.close()	
											self.patcher_meta(filepath,RSV_cap,t)								
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()	
						block = target.read()			
						nsha=sha256(block).hexdigest()	
						target.rewind()				
						xml_file=target.xml_gen(ofolder,nsha)
						target.close()	
						
		t.close()
		
		contentlist=list()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					vfragment="false"		
					if type(nca) == Nca:
						if (delta == False) and (str(nca.header.contentType) == 'Content.DATA'):
							for f in nca:
								for file in f:
									filename = str(file._path)
									if filename=="fragment":
										vfragment="true"
						if str(vfragment)=="true":
							continue			
						contentlist.append(nca._path)	
						if str(nca.header.contentType) == 'Content.META':	
							xmlname=nca._path
							xmlname=xmlname[:-3]+'xml'
							contentlist.append(xmlname)							
		hd = self.gen_nsp_head(contentlist,delta,True,ofolder)
		
		totSize = len(hd) 
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					vfragment="false"	
					if type(nca) == Nca:
						if (delta == False) and (str(nca.header.contentType) == 'Content.DATA'):
							for f in nca:
								for file in f:
									filename = str(file._path)
									if filename=="fragment":
										vfragment="true"
						if str(vfragment)=="true":
							continue			
						totSize=totSize+nca.header.size
						if str(nca.header.contentType) == 'Content.META':	
							xmlname=nca._path
							xmlname=xmlname[:-3]+'xml'
							xmlpath = os.path.join(ofolder, xmlname)
							totSize=totSize+os.path.getsize(xmlpath)						

		if os.path.exists(outfile) and os.path.getsize(outfile) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return					

		indent = 1
		rightsId = 0
		tabs = '\t' * indent
		
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)	
			
		if totSize <= 4294901760:
			fat="exfat"		
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294901760)
			index=0
			outfile=outfile[:-1]+str(index)
		if fx=="folder" and fat=="fat32":
			output_folder ="archfolder" 
			output_folder = os.path.join(ofolder, output_folder)			
			outfile = os.path.join(output_folder, "00")	
			if not os.path.exists(output_folder):
				os.makedirs(output_folder)					
		c=0
		
		Print.info('Generating NSP:')
		if rightsId	!=0:	
			Print.info('rightsId =\t' + hex(rightsId))
			Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
			Print.info('masterKeyRev =\t' + hex(masterKeyRev))	
		print("")
		
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)			
		t.write(tabs+'- Writing header...')			
		outf = open(outfile, 'w+b')		
		outf.write(hd)	
		t.update(len(hd))
		c=c+len(hd)		
		block=4294901760		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					vfragment="false"	
					if type(nca) == Nca and (str(nca.header.contentType) != 'Content.META'):
						if (delta == False) and (str(nca.header.contentType) == 'Content.DATA'):
							for f in nca:
								for file in f:
									filename = str(file._path)
									if filename=="fragment":
										vfragment="true"
						if str(vfragment)=="true":
							t.write(tabs+'- Skipping delta fragment: ' + str(nca._path))				
							continue			
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()	
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:	
							masterKeyRev=crypto1						
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))	
						gc_flag='00'*0x01					
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()					
						if nca.header.getRightsId() != 0:				
							nca.rewind()	
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
							if keypatch != 'false':
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)	
						if nca.header.getRightsId() == 0:
							nca.rewind()				
							encKeyBlock = nca.header.getKeyBlock()	
							if keypatch != 'false':
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)								
						t.write('')							
						t.write(tabs+'- Appending: ' + str(nca._path))
						nca.rewind()					
						i=0
						for data in iter(lambda: nca.read(int(buffer)), ""):
							if i==0:
								newheader=self.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)		
								if fat=="fat32" and (c+len(newheader))>block:
									n2=block-c
									c=0
									dat2=newheader[0x00:0x00+int(n2)]
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')	
									dat2=newheader[0x00+int(n2)+1:]
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
								else:
									outf.write(newheader)
									t.update(len(newheader))	
									c=c+len(newheader)								
								nca.seek(0xC00)									
								i+=1							
							else:
								outf.write(data)				
								t.update(len(data))
								c=c+len(data)									
								outf.flush()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									dat2=nca.read(int(n2))
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')							
								if not data:
									nca.close()
									break
					if type(nca) == Nca and str(nca.header.contentType) == 'Content.META':	
						filename = str(nca._path)
						filepath = os.path.join(outfolder, filename)	
						xml_file=filepath[:-3]+'xml'
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()						
						size=os.path.getsize(filepath)
						t.write(tabs+'- Appending: ' + str(nca._path))						
						for data in iter(lambda: target.read(int(size)), ""):				
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
							outf.flush()
							if fat=="fat32" and (c+len(data))>block:
								n2=block-c
								c=0
								dat2=nca.read(int(n2))
								outf.write(dat2)
								outf.flush()
								outf.close()	
								t.update(len(dat2))
								index=index+1
								outfile=outfile[0:-1]
								outfile=outfile+str(index)
								outf = open(outfile, 'wb')
								if totSize>(4294934528+int(buffer)):
									dat2=nca.read(int(buffer))
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
							if not data:
								target.close()
								break	
						try:
							os.remove(filepath) 	
						except:
							pass	
						with open(xml_file, 'r+b') as xmlf:								
							size=os.path.getsize(xml_file)
							xmlname=str(nca._path)
							xmlname=xmlname[:-3]+'xml'
							t.write(tabs+'- Appending: ' + xmlname)
							xmlf.seek(0x00)
							for data in iter(lambda: xmlf.read(int(buffer)), ""):				
								outf.write(data)
								t.update(len(data))
								c=c+len(data)
								outf.flush()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									dat2=nca.read(int(n2))
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')
									if totSize>(4294934528+int(buffer)):
										dat2=nca.read(int(buffer))
										outf.write(dat2)						
										t.update(len(dat2))									
										outf.flush()	
								if not data:
									xmlf.close()
									break	
						try:
							os.remove(xml_file) 	
						except:
							pass					
				t.close()		
				print("")
				print("Closing file. Please wait")		
				outf.close()								
						
#///////////////////////////////////////////////////								
#DIRECT XCI TO XCI
#///////////////////////////////////////////////////							

	def c_xci_direct(self,buffer,outfile,ofolder,fat,delta,metapatch,RSV_cap,keypatch):	
		if keypatch != 'false':
			try:
				keypatch = int(keypatch)
			except:
				print("New keygeneration is no valid integer")
		indent = 1
		rightsId = 0
		tabs = '\t' * indent		
		xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=self.get_xciheader(delta)	 			
		
		totSize=len(xci_header)+len(game_info)+len(sig_padding)+len(xci_certificate)+rootSize
	
		if os.path.exists(outfile) and os.path.getsize(outfile) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return
			
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Ticket:
						masterKeyRev = file.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = file.getRightsId()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:			
					if type(file) == Nca:
						if file.header.getRightsId() != 0:
							if file.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Nca:	
						if file.header.getRightsId() != 0:		
							if file.header.getCryptoType2() == 0:
								if file.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break	
									
		contTR=0
		contGC=0
		iscartridge=False
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:		
					if type(nca) == Nca:
						contTR+=1					
						if	nca.header.getgamecard() == 0:	
							crypto1=nca.header.getCryptoType()
							crypto2=nca.header.getCryptoType2()	
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:	
								masterKeyRev=crypto1					
							crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) == 0:					
								contGC+=1
							else:					
								contGC+=0
						else:
							contGC+=1											
				if  contTR == contGC and contTR>0 and contGC>0:
					iscartridge=True										
									
		Print.info('Generating XCI:')	
		if rightsId	!=0:	
			Print.info('rightsId =\t' + hex(rightsId))
			Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
			Print.info('masterKeyRev =\t' + hex(masterKeyRev))									
		print("")
		
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294934528)
			index=0
			outfile=outfile[:-1]+str(index)
		c=0
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing XCI header...')
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)
		outf = open(outfile, 'w+b')
		outf.write(xci_header)
		t.update(len(xci_header))		
		c=c+len(xci_header)
		t.write(tabs+'- Writing XCI game info...')		
		outf.write(game_info)	
		t.update(len(game_info))	
		c=c+len(game_info)
		t.write(tabs+'- Generating padding...')
		outf.write(sig_padding)	
		t.update(len(sig_padding))		
		c=c+len(sig_padding)		
		t.write(tabs+'- Writing XCI certificate...')
		outf.write(xci_certificate)	
		t.update(len(xci_certificate))	
		c=c+len(xci_certificate)		
		t.write(tabs+'- Writing ROOT HFS0 header...')		
		outf.write(root_header)
		t.update(len(root_header))
		c=c+len(root_header)
		t.write(tabs+'- Writing UPDATE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(upd_multiplier))	
		outf.write(upd_header)
		t.update(len(upd_header))
		c=c+len(upd_header)
		t.write(tabs+'- Writing NORMAL partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(norm_multiplier))			
		outf.write(norm_header)
		t.update(len(norm_header))
		c=c+len(norm_header)
		t.write(tabs+'- Writing SECURE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(sec_multiplier))		
		outf.write(sec_header)
		t.update(len(sec_header))
		c=c+len(sec_header)			
									
		block=4294934528		
		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					vfragment="false"		
					if type(nca) == Nca and (str(nca.header.contentType) != 'Content.META'):
						if (delta == False) and (str(nca.header.contentType) == 'Content.DATA'):
							for f in nca:
								for file in f:
									filename = str(file._path)
									if filename=="fragment":
										vfragment="true"
						if vfragment=="true":
							t.write(tabs+'- Skipping delta fragment: ' + str(nca._path))				
							continue
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()	
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:	
							masterKeyRev=crypto1								
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))	
						if	nca.header.getgamecard() == 0:	
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) == 0 and iscartridge == True:					
								gc_flag='01'*0x01
							else:					
								gc_flag='00'*0x01
						else:
							if iscartridge == True:
								gc_flag='01'*0x01	
							else:					
								gc_flag='00'*0x01									
						if nca.header.getRightsId() != 0:				
							nca.rewind()
							t.write('')	
							t.write(tabs+'* Appending: ' + str(nca._path))						
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
							if keypatch != 'false':							
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)	
						if nca.header.getRightsId() == 0:
							nca.rewind()
							t.write('')						
							t.write(tabs+'* Appending: ' + str(nca._path))	
							encKeyBlock = nca.header.getKeyBlock()
							if keypatch != 'false':							
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)								
						nca.rewind()					
						i=0
						for data in iter(lambda: nca.read(int(buffer)), ""):
							if i==0:
								newheader=self.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)					
								if fat=="fat32" and (c+len(newheader))>block:
									n2=block-c
									c=0
									dat2=newheader[0x00:0x00+int(n2)]
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')	
									dat2=newheader[0x00+int(n2)+1:]
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
								else:
									outf.write(newheader)
									t.update(len(newheader))	
									c=c+len(newheader)								
								nca.seek(0xC00)									
								i+=1		
							else:			
								outf.write(data)
								t.update(len(data))
								c=c+len(data)
								outf.flush()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									dat2=nca.read(int(n2))
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')
									if totSize>(4294934528+int(buffer)):
										dat2=nca.read(int(buffer))
										outf.write(dat2)						
										t.update(len(dat2))									
										outf.flush()	
								if not data:
									break
					if type(nca) == Nca and str(nca.header.contentType) == 'Content.META':	
						nca.rewind()
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()	
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:	
							masterKeyRev=crypto1							
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))	
						if	nca.header.getgamecard() == 0:	
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) == 0 and iscartridge == True:					
								gc_flag='01'*0x01
							else:					
								gc_flag='00'*0x01
						else:
							if iscartridge == True:
								gc_flag='01'*0x01	
							else:					
								gc_flag='00'*0x01									
						filename =  str(nca._path)
						outfolder = str(ofolder)				
						filepath = os.path.join(outfolder, filename)
						fp = open(filepath, 'w+b')
						nca.rewind()
						t.write('')	
						t.write(tabs+'* Getting: ' + str(nca._path))
						for data in iter(lambda: nca.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							if not data:
								break		
						fp.close()
						#///////////////////////////////////					
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()
						encKeyBlock = target.header.getKeyBlock()
						if keypatch != 'false':					
							if keypatch < target.header.getCryptoType2():
								encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)								
						newheader=self.get_newheader(target,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)	
						target.rewind()	
						target.write(newheader)								
						target.close()				
						if metapatch == 'true':
							target = Fs.Nca(filepath, 'r+b')
							target.rewind()					
							if 	str(target.header.contentType) == 'Content.META':
								for pfs0 in target:
									for cnmt in pfs0:
										check=str(cnmt._path)
										check=check[:-22]
										if check == 'AddOnContent':
											t.write(tabs + '-------------------------------------')
											t.write(tabs +'DLC -> No need to patch the meta' )
											t.write(tabs + '-------------------------------------')
											target.close()	
										else:	
											target.close()	
											self.patcher_meta(filepath,RSV_cap,t)								
						target = Fs.Nca(filepath, 'r+b')
						target.rewind()	
						size=os.path.getsize(filepath)
						t.write(tabs+'- Appending: ' + str(nca._path))						
						for data in iter(lambda: target.read(int(size)), ""):				
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
							outf.flush()
							if fat=="fat32" and (c+len(data))>block:
								n2=block-c
								c=0
								dat2=nca.read(int(n2))
								outf.write(dat2)
								outf.flush()
								outf.close()	
								t.update(len(dat2))
								index=index+1
								outfile=outfile[0:-1]
								outfile=outfile+str(index)
								outf = open(outfile, 'wb')
								if totSize>(4294934528+int(buffer)):
									dat2=nca.read(int(buffer))
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
							if not data:
								break	
						target.close()		
						try:
							os.remove(filepath) 	
						except:							
							pass
		t.close()
		print("")
		print("Closing file. Please wait")				
		outf.close()			

		
	def patcher_meta(self,filepath,RSV_cap,t):
		indent = 1
		RSV_cap=int(RSV_cap)
		tabs = '\t' * indent	
		t.write(tabs + '-------------------------------------')
		t.write(tabs + '')		
		t.write(tabs + 'Checking meta: ')
		meta_nca = Fs.Nca(filepath, 'r+b')
		crypto1=meta_nca.header.getCryptoType()	
		crypto2=meta_nca.header.getCryptoType2()	
		if crypto1 == 2:
			if crypto1 > crypto2:								
				keygen=meta_nca.header.getCryptoType()
			else:			
				keygen=meta_nca.header.getCryptoType2()	
		else:			
			keygen=meta_nca.header.getCryptoType2()	
		RSV=meta_nca.get_req_system()	
		t.write(tabs + '- RequiredSystemVersion = ' + str(RSV))	
		RSVmin=sq_tools.getMinRSV(keygen,RSV)
		RSVmax=sq_tools.getTopRSV(keygen,RSV)		
		if 	RSV > RSVmin:
			if RSVmin >= RSV_cap:
				min_sversion=meta_nca.write_req_system(RSVmin)
				t.write(tabs + '- New RequiredSystemVersion = '+ str(min_sversion))				
			else:
				if keygen < 4:
					if RSV > RSVmax:
						meta_nca.write_req_system(RSV_cap)		
				else:
					meta_nca.write_req_system(RSV_cap)	
			meta_nca.flush()
			meta_nca.close()
			t.write(tabs + '')					
			t.write(tabs + 'Updating cnmt hashes: ')
			############################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha=meta_nca.calc_pfs0_hash()
			t.write(tabs + '- Calculated hash from pfs0:')		
			t.write(tabs + '  + ' + str(hx(sha)))			
			meta_nca.flush()
			meta_nca.close()
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.set_pfs0_hash(sha)
			meta_nca.flush()
			meta_nca.close()
			############################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha2=meta_nca.calc_htable_hash()
			t.write(tabs + '- Calculated table hash: ')	
			t.write(tabs + '  + ' + str(hx(sha2)))				
			meta_nca.flush()
			meta_nca.close()						
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.header.set_htable_hash(sha2)
			meta_nca.flush()
			meta_nca.close()
			########################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha3=meta_nca.header.calculate_hblock_hash()
			t.write(tabs + '- Calculated header block hash: ')	
			t.write(tabs + '  + ' + str(hx(sha3)))				
			meta_nca.flush()
			meta_nca.close()						
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.header.set_hblock_hash(sha3)
			meta_nca.flush()
			meta_nca.close()
			t.write(tabs + '-------------------------------------')
		else:
			t.write(tabs +'-> No need to patch the meta' )
			t.write(tabs + '-------------------------------------')
			meta_nca.close()					
						
	def get_xciheader(self,delta):
		upd_list=list()
		upd_fileSizes = list()		
		norm_list=list()
		norm_fileSizes = list()			
		sec_list=list()
		sec_fileSizes = list()		
		sec_shalist = list()			
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					vfragment="false"			
					if type(file) == Nca:	
						if (delta == False) and (str(file.header.contentType) == 'Content.DATA'):
							for f in file:
								for fn in f:
									filename = str(fn._path)
									if filename=="fragment":
										vfragment="true"
						if str(vfragment)=="true":
							continue
						sec_list.append(file._path)	
						sec_fileSizes.append(file.header.size)		
						file.rewind()
						hblock = file.read(0x200)			
						sha=sha256(hblock).hexdigest()	
						sec_shalist.append(sha)															
																										
		hfs0 = Fs.Hfs0(None, None)							
		root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=hfs0.gen_rhfs0_head(upd_list,norm_list,sec_list,sec_fileSizes,sec_shalist)
		#print (hx(root_header))
		tot_size=0xF000+rootSize
		
		signature=sq_tools.randhex(0x100)
		signature= bytes.fromhex(signature)
		
		sec_offset=root_header[0x90:0x90+0x8]	
		sec_offset=int.from_bytes(sec_offset, byteorder='little')
		sec_offset=int((sec_offset+0xF000+0x200)/0x200)
		sec_offset=sec_offset.to_bytes(4, byteorder='little')
		back_offset=(0xFFFFFFFF).to_bytes(4, byteorder='little')
		kek=(0x00).to_bytes(1, byteorder='big')
		cardsize,access_freq=sq_tools.getGCsize(tot_size)
		cardsize=cardsize.to_bytes(1, byteorder='big')
		GC_ver=(0x00).to_bytes(1, byteorder='big')
		GC_flag=(0x00).to_bytes(1, byteorder='big')
		pack_id=(0x8750F4C0A9C5A966).to_bytes(8, byteorder='big')
		valid_data=int(((tot_size-0x1)/0x200))
		valid_data=valid_data.to_bytes(8, byteorder='little')	
		
		try:
			key= Keys.get('xci_header_key')
			key= bytes.fromhex(key)
			IV=sq_tools.randhex(0x10)
			IV= bytes.fromhex(IV)
			xkey=True
			#print(hx(IV))
			#print("i'm here") 
		except:
			IV=(0x5B408B145E277E81E5BF677C94888D7B).to_bytes(16, byteorder='big')
			xkey=False
			#print("i'm here 2") 
			
		HFS0_offset=(0xF000).to_bytes(8, byteorder='little')
		len_rHFS0=(len(root_header)).to_bytes(8, byteorder='little')
		sha_rheader=sha256(root_header[0x00:0x200]).hexdigest()	
		sha_rheader=bytes.fromhex(sha_rheader)	
		sha_ini_data=bytes.fromhex('1AB7C7B263E74E44CD3C68E40F7EF4A4D6571551D043FCA8ECF5C489F2C66E7E')	
		SM_flag=(0x01).to_bytes(4, byteorder='little')
		TK_flag=(0x02).to_bytes(4, byteorder='little')		
		K_flag=(0x0).to_bytes(4, byteorder='little')
		end_norm = sec_offset	
		
		header =  b''
		header += signature
		header += b'HEAD'
		header += sec_offset
		header += back_offset
		header += kek
		header += cardsize
		header += GC_ver
		header += GC_flag
		header += pack_id
		header += valid_data		
		header += IV		
		header += HFS0_offset				
		header += len_rHFS0		
		header += sha_rheader	
		header += sha_ini_data
		header += SM_flag	
		header += TK_flag	
		header += K_flag			
		header += end_norm		
		
		#Game_info
		if xkey==True:
			firm_ver='0100000000000000'
			access_freq=access_freq
			Read_Wait_Time='88130000'
			Read_Wait_Time2='00000000'
			Write_Wait_Time='00000000'		
			Write_Wait_Time2='00000000'		
			Firmware_Mode='00110C00'		
			CUP_Version='5a000200'		
			Empty1='00000000'
			Upd_Hash='9bfb03ddbb7c5fca'
			CUP_Id='1608000000000001'
			Empty2='00'*0x38	
			#print(hx(Empty2))
		
			firm_ver=bytes.fromhex(firm_ver)	
			access_freq=bytes.fromhex(access_freq)	
			Read_Wait_Time=bytes.fromhex(Read_Wait_Time)
			Read_Wait_Time2=bytes.fromhex(Read_Wait_Time2)
			Write_Wait_Time=bytes.fromhex(Write_Wait_Time)
			Write_Wait_Time2=bytes.fromhex(Write_Wait_Time2)		
			Firmware_Mode=bytes.fromhex(Firmware_Mode)
			CUP_Version=bytes.fromhex(CUP_Version)
			Empty1=bytes.fromhex(Empty1)
			Upd_Hash=bytes.fromhex(Upd_Hash)
			CUP_Id=bytes.fromhex(CUP_Id)		
			Empty2=bytes.fromhex(Empty2)	
		
			Game_info =  b''
			Game_info += firm_ver
			Game_info += access_freq
			Game_info += Read_Wait_Time
			Game_info += Read_Wait_Time2		
			Game_info += Write_Wait_Time
			Game_info += Write_Wait_Time2
			Game_info += Firmware_Mode
			Game_info += CUP_Version
			Game_info += Empty1
			Game_info += Upd_Hash
			Game_info += CUP_Id		
			Game_info += Empty2	
			
			gamecardInfoIV=IV[::-1]	
			crypto = aes128.AESCBC(key, gamecardInfoIV)
			enc_info=crypto.encrypt(Game_info)					
		if xkey==False:
			enc_info=sq_tools.get_enc_gameinfo(tot_size)
		
		#print (hx(enc_info))		
		
		#Padding
		sig_padding='00'*0x6E00
		sig_padding=bytes.fromhex(sig_padding)		
		#print (hx(sig_padding))	
		
		#CERT
		fake_CERT='FF'*0x8000
		fake_CERT=bytes.fromhex(fake_CERT)				
		#print (hx(fake_CERT))
		return header,enc_info,sig_padding,fake_CERT,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier
		
	def get_new_cryptoblock(self, nca, newMasterKeyRev,encKeyBlock,t):
		indent = 1
		tabs = '\t' * indent
		indent2 = 2
		tabs2 = '\t' * indent2
		
		masterKeyRev = nca.header.getCryptoType2()	

		if type(nca) == Nca:
			if nca.header.getCryptoType2() != newMasterKeyRev:
				t.write(tabs + '-----------------------------------')
				t.write(tabs + 'Changing keygeneration from %d to %s' % ( nca.header.getCryptoType2(), str(newMasterKeyRev)))
				t.write(tabs + '-----------------------------------')
				#encKeyBlock = nca.header.getKeyBlock()
				if sum(encKeyBlock) != 0:
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
					t.write(tabs2 + '+ decrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
					crypto = aes128.AESECB(key)
					decKeyBlock = crypto.decrypt(encKeyBlock)
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex)
					t.write(tabs2 + '+ encrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex))
					crypto = aes128.AESECB(key)
					reEncKeyBlock = crypto.encrypt(decKeyBlock)
					encKeyBlock = reEncKeyBlock
				if newMasterKeyRev >= 3:
					crypto1=2
					crypto2=newMasterKeyRev
				if newMasterKeyRev == 2:
					crypto1=2
					crypto2=0				
				if newMasterKeyRev < 2:
					crypto1=newMasterKeyRev
					crypto2=0							
				return encKeyBlock,crypto1,crypto2
		return encKeyBlock,nca.header.getCryptoType(),nca.header.getCryptoType2()				

	def get_newheader(self,target,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag):					
		target.rewind()							
		rawhead=target.read(0xC00)
		rawhead=hcrypto.decrypt(rawhead)
		header = b''
		header += rawhead[0x00:0x00+0x204]	
		#isgamecard 0x204
		GC=bytes.fromhex(gc_flag)
		header += GC				
		#contentType 0x205
		header += rawhead[0x205:0x206]								
		#crypto 1 0x206
		c1=crypto1.to_bytes(1, byteorder='big')
		header += c1		
		#########
		header += rawhead[0x207:0x220]		
		#crypto 1 0x220	
		c2=crypto2.to_bytes(1, byteorder='big')
		header += c2
		#########
		header += rawhead[0x221:0x230]								
		tr='00'*0x10
		tr=bytes.fromhex(tr)							
		header += tr
		header += rawhead[0x240:0x240+0xC0]	
		header += encKeyBlock
		header += rawhead[0x340:]
		newheader=hcrypto.encrypt(header)
		return newheader				
						
						
	def gen_nsp_head(self,files,delta,inc_xml,ofolder):
	
		filesNb = len(files)
		stringTable = '\x00'.join(str(nca) for nca in files)
		headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
		remainder = 0x10 - headerSize%0x10
		headerSize += remainder
		
		fileSizes = list()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					vfragment="false"			
					if type(nca) == Nca:
						if (delta == False) and (str(nca.header.contentType) == 'Content.DATA'):
							for f in nca:
								for file in f:
									filename = str(file._path)
									if filename=="fragment":
										vfragment="true"
						if str(vfragment)=="true":
							continue			
						fileSizes.append(nca.header.size)	
						if str(nca.header.contentType) == 'Content.META' and inc_xml==True:	
							xmlname=nca._path
							xmlname=xmlname[:-3]+'xml'
							xmlpath = os.path.join(ofolder, xmlname)
							size=os.path.getsize(xmlpath)					
							fileSizes.append(int(size))						
				
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		fileNamesLengths = [len(str(nca))+1 for nca in files] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		header =  b''
		header += b'PFS0'
		header += pk('<I', filesNb)
		header += pk('<I', len(stringTable)+remainder)
		header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			header += pk('<Q', fileOffsets[n])
			header += pk('<Q', fileSizes[n])
			header += pk('<I', stringTableOffsets[n])
			header += b'\x00\x00\x00\x00'
		header += stringTable.encode()
		header += remainder * b'\x00'
		
		return header											
						
	def sp_groupncabyid(self,buffer,ofolder,fat,fx,export):
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:		
					completefilelist.append(str(file._path))
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:					
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							crypto1=nca.header.getCryptoType()
							crypto2=nca.header.getCryptoType2()	
							if crypto1 == 2:
								if crypto1 > crypto2:								
									keygen=nca.header.getCryptoType()
								else:			
									keygen=nca.header.getCryptoType2()	
							else:			
								keygen=nca.header.getCryptoType2()				
							ncalist=list()
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()						
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									content_type=str(cnmt._path)
									content_type=content_type[:-22]	
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]	
									cnmt.seek(0x20)
									if content_type=='Application':
										original_ID=titleid2
										cnmt.readInt64()
										ttag=''
										CTYPE='BASE'
									elif content_type=='Patch':
										original_ID=cnmt.readInt64()	
										original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
										original_ID = original_ID[2:-1]	
										ttag=' [UPD]'
										CTYPE='UPDATE'
									elif content_type=='AddOnContent':
										original_ID=cnmt.readInt64()	
										original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
										original_ID = original_ID[2:-1]	
										ttag=' [DLC]'
										CTYPE='DLC'								
									else: 
										original_ID=cnmt.readInt64()	
										original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
										original_ID = original_ID[2:-1]							
									cnmt.seek(0x20+offset)			
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										ncatype = cnmt.read(0x1)
										unknown = cnmt.read(0x1)		
									#**************************************************************	
										version=str(int.from_bytes(titleversion, byteorder='little'))
										version='[v'+version+']'
										titleid3 ='['+ titleid2+']'
										nca_name=str(hx(NcaId))
										nca_name=nca_name[2:-1]+'.nca'
										if nca_name in completefilelist:
											ncalist.append(nca_name)			
									nca_meta=str(nca._path)
									if nca_meta in completefilelist:	
										ncalist.append(nca_meta)
									target=str(nca._path)
									tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
									tit_name = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', tit_name))
									tit_name = tit_name.strip()
									tid='['+titleid2+']'
									filename=tit_name+' '+tid+' '+version+ttag
									titlerights=titleid2+str('0'*15)+str(crypto2)
									contentlist.append([filename,titleid2,titlerights,keygen,ncalist,CTYPE])
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:									
					if type(file) == Ticket or file._path.endswith('.cert'):	
						test=file._path
						test=test[0:32]
						for i in contentlist:
							if i[2]==test:
								i[4].append(file._path)
					elif file._path.endswith('.xml'):	
						test=file._path
						test=test[0:-4]+'.nca'
						for i in contentlist:
							if test in i[4]:
								i[4].append(file._path)

		'''		
		for i in contentlist:
			print("")
			print('Filename: '+i[0])
			print('TitleID: '+i[1])
			print('TitleRights: '+i[2])
			print('Keygen: '+str(i[3]))			
			for j in i[4]:
				print (j)	
		'''								
		for i in contentlist:
			if export == 'both' and i[5] != 'BASE':
				export='nsp'
			if export == 'nsp':
				self.cd_spl_nsp(buffer,i[0],ofolder,i[4],fat,fx)
			if export == 'xci':			
				self.cd_spl_xci(buffer,i[0],ofolder,i[4],fat,fx)
			if export == 'both':	
				self.cd_spl_nsp(buffer,i[0],ofolder,i[4],fat,fx)			
				self.cd_spl_xci(buffer,i[0],ofolder,i[4],fat,fx)						
						
	def cd_spl_nsp(self,buffer,outfile,ofolder,filelist,fat,fx):
		outfile=outfile+'.nsp'	
		filepath = os.path.join(ofolder, outfile)	
		if os.path.exists(filepath) and os.path.getsize(filepath) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return			
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)		
		
		contentlist=list()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if file._path in filelist:
						contentlist.append(file._path)		

		hd = self.cd_spl_gen_nsph(contentlist)
		totSize = len(hd) 
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:		
					if file._path in contentlist:
						totSize=totSize+file.size	

		indent = 1
		rightsId = 0
		tabs = '\t' * indent

		if totSize <= 4294901760:
			fat="exfat"		
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294901760)
			index=0
			filepath=filepath[:-1]+str(index)
		if fx=="folder" and fat=="fat32":
			output_folder ="archfolder" 
			output_folder = os.path.join(ofolder, output_folder)			
			filepath = os.path.join(output_folder, "00")	
			if not os.path.exists(output_folder):
				os.makedirs(output_folder)					
		c=0

		Print.info("")
		Print.info('Generating NSP:')	
		Print.info('Filename: '+outfile)	
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)		
		t.write(tabs+'- Writing header...')	
		outf = open(str(filepath), 'w+b')	
		outf.write(hd)			
		t.update(len(hd))
		c=c+len(hd)		
		block=4294901760	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if type(file) == Nca and file._path in contentlist:		
						crypto1=file.header.getCryptoType()
						crypto2=file.header.getCryptoType2()	
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:	
							masterKeyRev=crypto1							
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), file.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))	
						gc_flag='00'*0x01									
						file.rewind()				
						encKeyBlock = file.header.getKeyBlock()					
						t.write(tabs+'- Appending: ' + str(file._path))
						file.rewind()					
						i=0
						for data in iter(lambda: file.read(int(buffer)), ""):
							if i==0:
								newheader=self.get_newheader(file,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)		
								if fat=="fat32" and (c+len(newheader))>block:
									n2=block-c
									c=0
									dat2=newheader[0x00:0x00+int(n2)]
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')	
									dat2=newheader[0x00+int(n2)+1:]
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
								else:
									outf.write(newheader)
									t.update(len(newheader))	
									c=c+len(newheader)								
								file.seek(0xC00)									
								i+=1							
							else:
								outf.write(data)				
								t.update(len(data))
								c=c+len(data)									
								outf.flush()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									dat2=file.read(int(n2))
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')							
								if not data:
									break					
					if type(file) != Nca and file._path in contentlist:
						file.rewind()			
						t.write(tabs+'- Appending: ' + str(file._path))					
						for data in iter(lambda: file.read(int(buffer)), ""):				
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
							outf.flush()
							if fat=="fat32" and (c+len(data))>block:
								n2=block-c
								c=0
								dat2=file.read(int(n2))
								outf.write(dat2)
								outf.flush()
								outf.close()	
								t.update(len(dat2))
								index=index+1
								outfile=outfile[0:-1]
								outfile=outfile+str(index)
								outf = open(outfile, 'wb')
								if totSize>(4294934528+int(buffer)):
									dat2=file.read(int(buffer))
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
							if not data:
								break							
		t.close()		
		print("Closing file. Please wait")		
		outf.close()

	def cd_spl_gen_nsph(self,filelist):			
		filesNb = len(filelist)
		stringTable = '\x00'.join(str(file) for file in filelist)
		headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
		remainder = 0x10 - headerSize%0x10
		headerSize += remainder

		fileSizes = list()		
		self.rewind()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:			
					if file._path in filelist:
						fileSizes.append(file.size)		

		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		fileNamesLengths = [len(str(file))+1 for file in filelist] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		header =  b''
		header += b'PFS0'
		header += pk('<I', filesNb)
		header += pk('<I', len(stringTable)+remainder)
		header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			header += pk('<Q', fileOffsets[n])
			header += pk('<Q', fileSizes[n])
			header += pk('<I', stringTableOffsets[n])
			header += b'\x00\x00\x00\x00'
		header += stringTable.encode()
		header += remainder * b'\x00'
		return header						
				
	def cd_spl_xci(self,buffer,outfile,ofolder,filelist,fat,fx):	
		outfile=outfile+'.xci'
		filepath = os.path.join(ofolder, outfile)	
		if os.path.exists(filepath) and os.path.getsize(filepath) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return	
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)			
		indent = 1
		rightsId = 0
		tabs = '\t' * indent

		contentlist=list()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Nca: 
						if file._path in filelist:
							contentlist.append(file._path)	
		
		xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=self.cd_spl_gen_xcih(contentlist)		
		totSize=len(xci_header)+len(game_info)+len(sig_padding)+len(xci_certificate)+rootSize		

		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if type(file) == Ticket and file._path in filelist:
						masterKeyRev = file.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = file.getRightsId()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:				
					if type(file) == Nca and file._path in filelist:
						if file.header.getRightsId() != 0:
							if file.header.getCryptoType2() != masterKeyRev:
								pass
								raise IOError('Mismatched masterKeyRevs!')
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if type(file) == Nca and file._path in filelist:	
						if file.header.getRightsId() != 0:		
							if file.header.getCryptoType2() == 0:
								if file.header.getCryptoType() == 2:
									masterKeyRev = 2						
									titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
									break		

		contTR=0
		contGC=0
		iscartridge=False
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:	
					if type(nca) == Nca and nca._path in filelist:
						contTR+=1					
						if	nca.header.getgamecard() == 0:	
							crypto1=nca.header.getCryptoType()
							crypto2=nca.header.getCryptoType2()	
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:	
								masterKeyRev=crypto1					
							crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) == 0:					
								contGC+=1
							else:					
								contGC+=0
						else:
							contGC+=1											
				if  contTR == contGC and contTR>0 and contGC>0:
					iscartridge=True										
		
		Print.info("")
		Print.info('Generating XCI:')	
		Print.info('Filename: '+outfile)
		
		if rightsId	!=0:	
			Print.info('rightsId =\t' + hex(rightsId))
			Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
			Print.info('masterKeyRev =\t' + hex(masterKeyRev))									
		print("")		
		
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294934528)
			index=0
			filepath=filepath[:-1]+str(index)
		c=0
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing XCI header...')
		outf = open(filepath, 'w+b')
		outf.write(xci_header)
		t.update(len(xci_header))		
		c=c+len(xci_header)
		t.write(tabs+'- Writing XCI game info...')		
		outf.write(game_info)	
		t.update(len(game_info))	
		c=c+len(game_info)
		t.write(tabs+'- Generating padding...')
		outf.write(sig_padding)	
		t.update(len(sig_padding))		
		c=c+len(sig_padding)		
		t.write(tabs+'- Writing XCI certificate...')
		outf.write(xci_certificate)	
		t.update(len(xci_certificate))	
		c=c+len(xci_certificate)		
		t.write(tabs+'- Writing ROOT HFS0 header...')		
		outf.write(root_header)
		t.update(len(root_header))
		c=c+len(root_header)
		t.write(tabs+'- Writing UPDATE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(upd_multiplier))	
		outf.write(upd_header)
		t.update(len(upd_header))
		c=c+len(upd_header)
		t.write(tabs+'- Writing NORMAL partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(norm_multiplier))			
		outf.write(norm_header)
		t.update(len(norm_header))
		c=c+len(norm_header)
		t.write(tabs+'- Writing SECURE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(sec_multiplier))		
		outf.write(sec_header)
		t.update(len(sec_header))
		c=c+len(sec_header)			
									
		block=4294934528		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:	
					if type(nca) == Nca and nca._path in contentlist:
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()	
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:	
							masterKeyRev=crypto1							
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))	
						if	nca.header.getgamecard() == 0:	
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) == 0 and iscartridge == True:					
								gc_flag='01'*0x01
							else:					
								gc_flag='00'*0x01
						else:
							if iscartridge == True:
								gc_flag='01'*0x01	
							else:					
								gc_flag='00'*0x01								
						if nca.header.getRightsId() != 0:				
							nca.rewind()
							t.write('')	
							t.write(tabs+'* Appending: ' + str(nca._path))						
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
						if nca.header.getRightsId() == 0:
							nca.rewind()
							t.write('')						
							t.write(tabs+'* Appending: ' + str(nca._path))	
							encKeyBlock = nca.header.getKeyBlock()	
						nca.rewind()					
						i=0
						for data in iter(lambda: nca.read(int(buffer)), ""):
							if i==0:
								newheader=self.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)					
								if fat=="fat32" and (c+len(newheader))>block:
									n2=block-c
									c=0
									dat2=newheader[0x00:0x00+int(n2)]
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')	
									dat2=newheader[0x00+int(n2)+1:]
									outf.write(dat2)						
									t.update(len(dat2))									
									outf.flush()	
								else:
									outf.write(newheader)
									t.update(len(newheader))	
									c=c+len(newheader)								
								nca.seek(0xC00)									
								i+=1		
							else:			
								outf.write(data)
								t.update(len(data))
								c=c+len(data)
								outf.flush()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									dat2=nca.read(int(n2))
									outf.write(dat2)
									outf.flush()
									outf.close()	
									t.update(len(dat2))
									index=index+1
									outfile=outfile[0:-1]
									outfile=outfile+str(index)
									outf = open(outfile, 'wb')
									if totSize>(4294934528+int(buffer)):
										dat2=nca.read(int(buffer))
										outf.write(dat2)						
										t.update(len(dat2))									
										outf.flush()	
								if not data:
									break
		t.close()
		print("")
		print("Closing file. Please wait")				
		outf.close()
		
	def cd_spl_gen_xcih(self,filelist):	
		upd_list=list()
		upd_fileSizes = list()		
		norm_list=list()
		norm_fileSizes = list()			
		sec_list=list()
		sec_fileSizes = list()		
		sec_shalist = list()			
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if file._path in filelist:		
						sec_list.append(file._path)	
						sec_fileSizes.append(file.size)		
						file.rewind()
						hblock = file.read(0x200)			
						sha=sha256(hblock).hexdigest()	
						sec_shalist.append(sha)															
																										
		hfs0 = Fs.Hfs0(None, None)							
		root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=hfs0.gen_rhfs0_head(upd_list,norm_list,sec_list,sec_fileSizes,sec_shalist)
		#print (hx(root_header))
		tot_size=0xF000+rootSize
		
		signature=sq_tools.randhex(0x100)
		signature= bytes.fromhex(signature)
		
		sec_offset=root_header[0x90:0x90+0x8]	
		sec_offset=int.from_bytes(sec_offset, byteorder='little')
		sec_offset=int((sec_offset+0xF000+0x200)/0x200)
		sec_offset=sec_offset.to_bytes(4, byteorder='little')
		back_offset=(0xFFFFFFFF).to_bytes(4, byteorder='little')
		kek=(0x00).to_bytes(1, byteorder='big')
		cardsize,access_freq=sq_tools.getGCsize(tot_size)
		cardsize=cardsize.to_bytes(1, byteorder='big')
		GC_ver=(0x00).to_bytes(1, byteorder='big')
		GC_flag=(0x00).to_bytes(1, byteorder='big')
		pack_id=(0x8750F4C0A9C5A966).to_bytes(8, byteorder='big')
		valid_data=int(((tot_size-0x1)/0x200))
		valid_data=valid_data.to_bytes(8, byteorder='little')	
		
		try:
			Keys.get('xci_header_key')
			key= Keys.get('xci_header_key')
			key= bytes.fromhex(key)
			IV=sq_tools.randhex(0x10)
			IV= bytes.fromhex(IV)
			xkey=True
			#print(hx(IV))
			#print("i'm here") 
		except:
			IV=(0x5B408B145E277E81E5BF677C94888D7B).to_bytes(16, byteorder='big')
			xkey=False
			#print("i'm here 2") 
			
		HFS0_offset=(0xF000).to_bytes(8, byteorder='little')
		len_rHFS0=(len(root_header)).to_bytes(8, byteorder='little')
		sha_rheader=sha256(root_header[0x00:0x200]).hexdigest()	
		sha_rheader=bytes.fromhex(sha_rheader)	
		sha_ini_data=bytes.fromhex('1AB7C7B263E74E44CD3C68E40F7EF4A4D6571551D043FCA8ECF5C489F2C66E7E')	
		SM_flag=(0x01).to_bytes(4, byteorder='little')
		TK_flag=(0x02).to_bytes(4, byteorder='little')		
		K_flag=(0x0).to_bytes(4, byteorder='little')
		end_norm = sec_offset	
		
		header =  b''
		header += signature
		header += b'HEAD'
		header += sec_offset
		header += back_offset
		header += kek
		header += cardsize
		header += GC_ver
		header += GC_flag
		header += pack_id
		header += valid_data		
		header += IV		
		header += HFS0_offset				
		header += len_rHFS0		
		header += sha_rheader	
		header += sha_ini_data
		header += SM_flag	
		header += TK_flag	
		header += K_flag			
		header += end_norm		
		
		#Game_info
		if xkey==True:
			firm_ver='0100000000000000'
			access_freq=access_freq
			Read_Wait_Time='88130000'
			Read_Wait_Time2='00000000'
			Write_Wait_Time='00000000'		
			Write_Wait_Time2='00000000'		
			Firmware_Mode='00110C00'		
			CUP_Version='5a000200'		
			Empty1='00000000'
			Upd_Hash='9bfb03ddbb7c5fca'
			CUP_Id='1608000000000001'
			Empty2='00'*0x38	
			#print(hx(Empty2))
		
			firm_ver=bytes.fromhex(firm_ver)	
			access_freq=bytes.fromhex(access_freq)	
			Read_Wait_Time=bytes.fromhex(Read_Wait_Time)
			Read_Wait_Time2=bytes.fromhex(Read_Wait_Time2)
			Write_Wait_Time=bytes.fromhex(Write_Wait_Time)
			Write_Wait_Time2=bytes.fromhex(Write_Wait_Time2)		
			Firmware_Mode=bytes.fromhex(Firmware_Mode)
			CUP_Version=bytes.fromhex(CUP_Version)
			Empty1=bytes.fromhex(Empty1)
			Upd_Hash=bytes.fromhex(Upd_Hash)
			CUP_Id=bytes.fromhex(CUP_Id)		
			Empty2=bytes.fromhex(Empty2)	
		
			Game_info =  b''
			Game_info += firm_ver
			Game_info += access_freq
			Game_info += Read_Wait_Time
			Game_info += Read_Wait_Time2		
			Game_info += Write_Wait_Time
			Game_info += Write_Wait_Time2
			Game_info += Firmware_Mode
			Game_info += CUP_Version
			Game_info += Empty1
			Game_info += Upd_Hash
			Game_info += CUP_Id		
			Game_info += Empty2	
			
			gamecardInfoIV=IV[::-1]	
			crypto = aes128.AESCBC(key, gamecardInfoIV)
			enc_info=crypto.encrypt(Game_info)					
		if xkey==False:
			enc_info=sq_tools.get_enc_gameinfo(tot_size)
		
		#print (hx(enc_info))		
		
		#Padding
		sig_padding='00'*0x6E00
		sig_padding=bytes.fromhex(sig_padding)		
		#print (hx(sig_padding))	
		
		#CERT
		fake_CERT='FF'*0x8000
		fake_CERT=bytes.fromhex(fake_CERT)				
		#print (hx(fake_CERT))


		return header,enc_info,sig_padding,fake_CERT,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier
			
				
	def get_content(self,ofolder,vkeypatch,delta):
		if vkeypatch=='false':
			vkeypatch=False	
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":	
				for file in nspF:
					completefilelist.append(str(file._path))
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":						
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.META':
							crypto1=nca.header.getCryptoType()
							crypto2=nca.header.getCryptoType2()	
							if crypto1 == 2:
								if crypto1 > crypto2:								
									keygen=nca.header.getCryptoType()
								else:			
									keygen=nca.header.getCryptoType2()	
							else:			
								keygen=nca.header.getCryptoType2()				
							ncalist=list()
							for f in nca:
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()						
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									content_type=str(cnmt._path)
									content_type=content_type[:-22]	
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]	
									cnmt.seek(0x20)
									if content_type=='Application':
										original_ID=titleid2
										cnmt.readInt64()
										ttag=''
										CTYPE='BASE'
									elif content_type=='Patch':
										original_ID=cnmt.readInt64()	
										original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
										original_ID = original_ID[2:-1]	
										ttag=' [UPD]'
										CTYPE='UPDATE'
									elif content_type=='AddOnContent':
										original_ID=cnmt.readInt64()	
										original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
										original_ID = original_ID[2:-1]	
										ttag=' [DLC]'
										CTYPE='DLC'								
									else: 
										original_ID=cnmt.readInt64()	
										original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
										original_ID = original_ID[2:-1]							
									cnmt.seek(0x20+offset)			
									for i in range(content_entries):
										vhash = cnmt.read(0x20)
										NcaId = cnmt.read(0x10)
										size = cnmt.read(0x6)
										size=int.from_bytes(size, byteorder='little')
										ncatype = cnmt.readInt8()
										unknown = cnmt.read(0x1)		
									#**************************************************************	
										version=str(int.from_bytes(titleversion, byteorder='little'))
										ver=version
										ver='[v'+ver+']'
										titleid3 ='['+ titleid2+']'
										nca_name=str(hx(NcaId))
										nca_name=nca_name[2:-1]+'.nca'	
										if nca_name in completefilelist:
											if delta==False and ncatype==6:	
												print(tabs+'- Excluding delta fragment '+nca_name)
												continue	
											else:		
												ncalist.append([nca_name,size])																							
									nca_meta=str(nca._path)
									if nca_meta in completefilelist:	
										ncalist.append([nca_meta,nca.size])
										if ofolder != False:
											target = Fs.Nca(nca, 'r+b')
											target.rewind()		
											outf= os.path.join(ofolder, str(nca._path))									
											fp = open(outf, 'w+b')		
											for data in iter(lambda: target.read(int(32768)), ""):	
												fp.write(data)						
												fp.flush()				
												if not data:
													fp.close()									
													break			
											target = Fs.Nca(outf, 'r+b')										
											block = target.read()			
											nsha=sha256(block).hexdigest()	
											target.rewind()	
											if vkeypatch == False:
												xml=target.xml_gen(ofolder,nsha)	
											else:
												xml=target.xml_gen_mod(ofolder,nsha,vkeypatch)									
											xmlname=nca_meta[:-3]+'xml'
											xmlsize=os.path.getsize(xml)
											ncalist.append([xmlname,xmlsize])		
											target.close()
											try:
												os.remove(outf) 	
											except:
												pass													
									titlerights=titleid2+str('0'*15)+str(crypto2)
									contentlist.append([str(self._path),titleid2,titlerights,keygen,ncalist,CTYPE,version])

		for nspF in self.hfs0:
			if str(nspF._path)=="secure":											
				for file in nspF:
					if type(file) == Ticket or file._path.endswith('.cert'):	
						test=file._path
						test=test[0:32]
						for i in contentlist:
							if i[2]==test:
								i[4].append([file._path,file.size])
		'''
		for i in contentlist:
			print('Filename: '+i[0])
			print('TitleID: '+i[1])
			print('TitleRights: '+i[2])
			print('Version: '+str(i[6]))				
			print('Keygen: '+str(i[3]))		
			print('Content type: '+str(i[5]))			
			for j in i[4]:
				print (j)	
		print("")
		'''
		return contentlist										
						
						
	def get_title(self,baseid):
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:	
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:	
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]	
									if baseid != titleid2:
										continue
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()								
									min_sversion=cnmt.readInt32()
									length_of_emeta=cnmt.readInt32()	
									target=str(nca._path)
									content_type_cnmt=str(cnmt._path)
									content_type_cnmt=content_type_cnmt[:-22]									
									if content_type_cnmt == 'AddOnContent':						
										DLCnumb=str(titleid2)
										DLCnumb="0000000000000"+DLCnumb[-3:]									
										DLCnumb=bytes.fromhex(DLCnumb)
										DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
										DLCnumb=int(DLCnumb)	
										title = 'DLC number '+str(DLCnumb)		
										return(title)	
		title='DLC'							
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.CONTROL':
							title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title)
							return(title)			

	def get_lang_tag(self,baseid):
		languetag=False	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:	
						if 	str(nca.header.contentType) == 'Content.META':
							for f in nca:	
								for cnmt in f:
									nca.rewind()
									f.rewind()
									cnmt.rewind()
									titleid=cnmt.readInt64()
									titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
									titleid2 = titleid2[2:-1]	
									if baseid != titleid2:
										continue
									titleversion = cnmt.read(0x4)
									cnmt.rewind()
									cnmt.seek(0xE)
									offset=cnmt.readInt16()
									content_entries=cnmt.readInt16()
									meta_entries=cnmt.readInt16()
									cnmt.rewind()
									cnmt.seek(0x20)
									original_ID=cnmt.readInt64()								
									min_sversion=cnmt.readInt32()
									length_of_emeta=cnmt.readInt32()	
									target=str(nca._path)
									content_type_cnmt=str(cnmt._path)
									content_type_cnmt=content_type_cnmt[:-22]									
									if content_type_cnmt == 'AddOnContent':									
										return(False)	
		title='DLC'							
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.CONTROL':
							title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title)
							languetag='('
							if ("US (eng)" or "UK (eng)") in SupLg:
								languetag=languetag+'En,'
							if "JP" in SupLg:
								languetag=languetag+'Jp,'				
							if ("CAD (fr)" or "FR") in SupLg:
								languetag=languetag+'Fr,'
							elif ("CAD (fr)") in SupLg:	
								languetag=languetag+'CADFr,'		
							elif ("FR") in SupLg:	
								languetag=languetag+'Fr,'								
							if "DE" in SupLg:
								languetag=languetag+'De,'							
							if ("LAT (spa)" and "SPA") in SupLg:
								languetag=languetag+'Es'
							elif "LAT (spa)" in SupLg:
								languetag=languetag+'LatEs,'
							elif "SPA" in SupLg:
								languetag=languetag+'Es,'									
							if "IT" in SupLg:
								languetag=languetag+'It,'					
							if "DU" in SupLg:
								languetag=languetag+'Du,'
							if "POR" in SupLg:
								languetag=languetag+'Por,'						
							if "RU" in SupLg:
								languetag=languetag+'Ru,'	
							if "KOR" in SupLg:
								languetag=languetag+'Kor,'							
							if "TAI" in SupLg:
								languetag=languetag+'Tw,'	
							if "CH" in SupLg:
								languetag=languetag+'Ch,'
							languetag=languetag[:-1]
							languetag=languetag+')'			
							return(languetag)										
						
	def file_hash(self,target):		
		indent = 1
		gamecard = False		
		tabs = '\t' * indent	
		sha=False;sizef=False
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					docheck = False					
					if str(file._path) == target:
						file.rewind()
						hblock = file.read(0x200)			
						sha=sha256(hblock).hexdigest()	
						sizef=file.size
						#print(str(sizef))
						#return sha,sizef
					if type(file) == Nca and gamecard==False:			
						if	file.header.getgamecard() == 1:	
							gamecard=True
						else:
							nca_id=file.header.titleId
							if nca_id.endswith('000') or nca_id.endswith('800'):
								if 	str(file.header.contentType) == 'Content.PROGRAM':					
									docheck=True
							else:
								if 	str(file.header.contentType) == 'Content.DATA':				
									docheck=True				
							if docheck == True:
								crypto1=file.header.getCryptoType()
								crypto2=file.header.getCryptoType2()	
								if crypto2>crypto1:
									masterKeyRev=crypto2
								if crypto2<=crypto1:	
									masterKeyRev=crypto1	
								crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), file.header.keyIndex))
								KB1L=file.header.getKB1L()
								KB1L = crypto.decrypt(KB1L)	
								if sum(KB1L) == 0:					
									gamecard=True								
		return sha,sizef,gamecard						
						
	def append_content(self,outf,target,buffer,t):			
		indent = 1
		tabs = '\t' * indent	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if str(file._path) == target:
						if type(file) == Nca:
							fp = open(outf, 'a+b')			
							file.rewind()
							t.write(tabs+'- Appending: ' + str(file._path))			
							for data in iter(lambda: file.read(int(buffer)), ""):		
								fp.write(data)
								t.update(len(data))					
								fp.flush()				
								if not data:				
									break					
							if str(file.header.contentType) == 'Content.META':
								target=str(file._path)
								xmlname=target[:-3]+'xml'	
								t.write(tabs+'- Appending: ' + xmlname)								
								dir=os.path.dirname(os.path.abspath(outf))						
								outf= os.path.join(dir, xmlname)		
								xml = open(outf, 'rb')		
								data=xml.read()
								xml.close()
								fp.write(data)
								t.update(len(data))					
								fp.flush()	
								try:
									os.remove(outf) 	
								except:
									pass							
							fp.close()							
						else:
							fp = open(outf, 'a+b')			
							file.rewind()
							t.write(tabs+'- Appending: ' + str(file._path))			
							for data in iter(lambda: file.read(int(buffer)), ""):		
								fp.write(data)
								t.update(len(data))					
								fp.flush()				
								if not data:
									fp.close()					
									break	

	def append_clean_content(self,outf,target,buffer,t,gamecard,keypatch,metapatch,RSV_cap,fat,fx,c,index):	
		block=4294934528		
		indent = 1
		tabs = '\t' * indent	
		ticketlist=list()
		if keypatch != 'false':
			try:
				keypatch = int(keypatch)
			except:
				print("New keygeneration is no valid integer")		
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if type(file) == Ticket:	
						masterKeyRev = file.getMasterKeyRevision()
						titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = str(hx(file.getRightsId().to_bytes(16, byteorder='big')))			
						encryptedkey=file.getTitleKeyBlock().to_bytes(16, byteorder='big')
						ticketlist.append([masterKeyRev,rightsId,encryptedkey])
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:
					if str(file._path) == target:
						if type(file) == Nca:
							gc_flag=file.header.getgamecard()
							if gc_flag != 0:
								if gamecard==False:
									gc_flag='00'*0x01								
								else:
									gc_flag='01'*0x01
							elif gc_flag == 0:
								if gamecard==True:
									gc_flag='01'*0x01								
								else:
									gc_flag='00'*0x01							
							else:
								gc_flag='00'*0x01						
							file.rewind()			
							crypto1=file.header.getCryptoType()
							crypto2=file.header.getCryptoType2()	
							hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))					
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:	
								masterKeyRev=crypto1						
							if file.header.getRightsId() != 0:	
								for i in range(len(ticketlist)):			
									#print(str(file.header.rightsId))	
									#print(ticketlist[i][1])								
									if  str(file.header.rightsId) == ticketlist[i][1]:
										encryptedkey=ticketlist[i][2]
										break	
								titleKeyDec = Keys.decryptTitleKey(encryptedkey, Keys.getMasterKeyIndex(masterKeyRev))
								t.write("")
								t.write(tabs+'rightsId =\t' + str(file.header.rightsId))
								t.write(tabs+'titleKeyDec =\t' + str(hx(titleKeyDec)))
								t.write(tabs+'masterKeyRev =\t' + hex(masterKeyRev))									
								t.write("")
								crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), file.header.keyIndex))							
								file.rewind()
								t.write(tabs+'* Appending: ' + str(file._path))		
								encKeyBlock = crypto.encrypt(titleKeyDec * 4)
								if keypatch != 'false':					
									if keypatch < file.header.getCryptoType2():
										encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(file, keypatch,encKeyBlock,t)								
								#t.write(str(hx(encKeyBlock)))
								newheader=self.get_newheader(file,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)						
								#t.write(str(hx(newheader)))
							if file.header.getRightsId() == 0:				
								t.write(tabs+'* Appending: ' + str(file._path))	
								file.rewind()						
								crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), file.header.keyIndex))					
								encKeyBlock = file.header.getKeyBlock()	
								if keypatch != 'false':					
									if keypatch < file.header.getCryptoType2():
										encKeyBlock,crypto1,crypto2=self.get_new_cryptoblock(file, keypatch,encKeyBlock,t)								
								newheader=self.get_newheader(file,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)						
							if 	str(file.header.contentType) != 'Content.META':							
								i=0					
								sha=sha256()
								fp = open(outf, 'ab')
								file.rewind()										
								for data in iter(lambda: file.read(int(buffer)), ""):	
									if i==0:				
										if fat=="fat32" and (c+len(newheader))>block:									
											n2=block-c
											c=0
											dat2=newheader[0x00:0x00+int(n2)]
											fp.write(dat2)
											fp.flush()
											fp.close()	
											t.update(len(dat2))
											index=index+1
											outf=outf[0:-1]
											outf=outf+str(index)
											fp = open(outf, 'wb')	
											dat2=newheader[0x00+int(n2)+1:]
											fp.write(dat2)						
											t.update(len(dat2))		
											c=c+len(dat2)													
											fp.flush()		
											sha.update(newheader)													
										else:									
											fp.write(newheader)
											t.update(len(newheader))	
											c=c+len(newheader)													
											sha.update(newheader)						
											file.seek(0xC00)									
											i+=1	
									else:	
										if fat=="fat32" and (c+len(data))>block:	
											n2=block-c
											c=0										
											dat2=data[0x00:0x00+int(n2)]										
											fp.write(dat2)
											fp.flush()
											fp.close()	
											t.update(len(dat2))											
											index=index+1
											outf=outf[0:-1]
											outf=outf+str(index)
											fp = open(outf, 'wb')	
											dat2=data[0x00+int(n2)+1:]
											fp.write(dat2)						
											t.update(len(dat2))		
											c=c+len(dat2)													
											fp.flush()				
											sha.update(data)												
										else:
											fp.write(data)
											t.update(len(data))
											c=c+len(data)																		
											fp.flush()		
											sha.update(data)
										if not data:				
											break												
								sha=sha.hexdigest()	
								'''
								if 	str(file._path).endswith('.cnmt.nca'):
									newname=sha[:32]+'.cnmt.nca'		
								else:	
									newname=sha[:32]+'.nca'	
								'''		
								#t.write(tabs+'new hash: '+sha)
								#t.write(tabs+'new name: '+newname)					
								fp.close()								
							elif str(file.header.contentType) == 'Content.META':
								metaname = str(file._path)
								dir=os.path.dirname(os.path.abspath(outf))
								metafile=os.path.join(dir, metaname)
								fp = open(metafile, 'w+b')	
								file.rewind()	
								i=0		
								sha=sha256()						
								for data in iter(lambda: file.read(int(buffer)), ""):	
									if i==0:	
										if fat=="fat32" and (c+len(newheader))>block:									
											n2=block-c
											c=0
											dat2=newheader[0x00:0x00+int(n2)]
											fp.write(dat2)
											fp.flush()
											fp.close()	
											t.update(len(dat2))
											index=index+1
											outf=outf[0:-1]
											outf=outf+str(index)
											fp = open(outf, 'wb')	
											dat2=newheader[0x00+int(n2)+1:]
											fp.write(dat2)						
											t.update(len(dat2))												
											fp.flush()	
											sha.update(newheader)												
										else:														
											fp.write(newheader)
											t.update(len(newheader))												
											c=c+len(newheader)	
											sha.update(newheader)						
											file.seek(0xC00)									
											i+=1	
									else:	
										if fat=="fat32" and (c+len(data))>block:	
											n2=block-c
											c=0										
											dat2=data[0x00:0x00+int(n2)]										
											fp.write(dat2)
											fp.flush()
											fp.close()	
											t.update(len(dat2))											
											index=index+1
											outf=outf[0:-1]
											outf=outf+str(index)
											fp = open(outf, 'wb')	
											dat2=data[0x00+int(n2)+1:]
											fp.write(dat2)						
											t.update(len(dat2))		
											c=c+len(dat2)													
											fp.flush()				
											sha.update(data)												
										else:
											fp.write(data)
											t.update(len(data))
											c=c+len(data)										
											sha.update(data)								
											fp.flush()												
										if not data:				
											break				
								fp.close()		
								if metapatch == 'true' or keypatch != 'false':									
									target = Fs.Nca(metafile, 'r+b')
									target.rewind()					
									if 	str(target.header.contentType) == 'Content.META':
										for pfs0 in target:
											for cnmt in pfs0:
												check=str(cnmt._path)
												check=check[:-22]
												if check == 'AddOnContent':
													t.write(tabs+'   > DLC. No RSV to patch')													
													target.close()										
												else:	
													target.close()	
													minRSV=sq_tools.getMinRSV(keypatch,RSV_cap)
													if int(minRSV)>int(RSV_cap):
														RSV_cap=minRSV
													self.patcher_meta(metafile,RSV_cap,t)
								target = Fs.Nca(metafile, 'r+b')														
								target.rewind()															
								fp = open(outf, 'ab')			
								file.rewind()	
								for data in iter(lambda: target.read(int(buffer)), ""):		
									if fat=="fat32" and (c+len(data))>block:	
										n2=block-c
										c=0										
										dat2=data[0x00:0x00+int(n2)]										
										fp.write(dat2)
										fp.flush()
										fp.close()	
										t.update(len(dat2))											
										index=index+1
										outf=outf[0:-1]
										outf=outf+str(index)
										fp = open(outf, 'wb')	
										dat2=data[0x00+int(n2)+1:]
										fp.write(dat2)						
										t.update(len(dat2))		
										c=c+len(dat2)													
										fp.flush()				
										sha.update(data)												
									else:
										fp.write(data)
										t.update(len(data))
										c=c+len(data)										
										sha.update(data)								
										fp.flush()		
									if not data:		
										target.close()										
										break	
								try:
									os.remove(metafile) 	
								except:
									pass										
								if not outf.endswith('xci'):
									test=outf[0:-1]
									if not test.endswith('xc'): 
										target=str(file._path)
										xmlname=target[:-3]+'xml'	
										t.write(tabs+'* Appending: ' + xmlname)								
										dir=os.path.dirname(os.path.abspath(outf))						
										outf= os.path.join(dir, xmlname)		
										xml = open(outf, 'rb')		
										data=xml.read()
										xml.close()
										if fat=="fat32" and (c+len(data))>block:	
											n2=block-c
											c=0										
											dat2=data[0x00:0x00+int(n2)]										
											fp.write(dat2)
											fp.flush()
											fp.close()	
											t.update(len(dat2))											
											index=index+1
											outf=outf[0:-1]
											outf=outf+str(index)
											fp = open(outf, 'wb')	
											dat2=data[0x00+int(n2)+1:]
											fp.write(dat2)						
											t.update(len(dat2))		
											c=c+len(dat2)													
											fp.flush()															
										else:
											fp.write(data)
											t.update(len(data))
											c=c+len(data)																		
											fp.flush()											
										try:
											os.remove(outf) 	
										except:
											pass																									
								fp.close()		
						else:
							fp = open(outf, 'ab')			
							file.rewind()
							t.write(tabs+'* Appending: ' + str(file._path))			
							for data in iter(lambda: file.read(int(buffer)), ""):		
								if fat=="fat32" and (c+len(data))>block:	
									n2=block-c
									c=0										
									dat2=data[0x00:0x00+int(n2)]										
									fp.write(dat2)
									fp.flush()
									fp.close()	
									t.update(len(dat2))											
									index=index+1
									outf=outf[0:-1]
									outf=outf+str(index)
									fp = open(outf, 'wb')	
									dat2=data[0x00+int(n2)+1:]
									fp.write(dat2)						
									t.update(len(dat2))		
									c=c+len(dat2)													
									fp.flush()															
								else:
									fp.write(data)
									t.update(len(data))
									c=c+len(data)																		
									fp.flush()			
								if not data:				
									break	
								fp.close()
		return outf,index,c						