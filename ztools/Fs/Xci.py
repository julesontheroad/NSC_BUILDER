from binascii import hexlify as hx, unhexlify as uhx
from Fs.Hfs0 import Hfs0
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
						Print.info(tabs + 'Copying: ' + str(filename))
						for data in iter(lambda: nca.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							if not data:
								break
						fp.close()
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
							Print.info(tabs + 'Copying: ' + str(filename))
							for data in iter(lambda: nca.read(int(buffer)), ""):
								fp.write(data)
								fp.flush()
								if not data:
									break
							fp.close()
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
							Print.info(tabs + 'Copying: ' + str(filename))
							for data in iter(lambda: nca.read(int(buffer)), ""):
								fp.write(data)
								fp.flush()
								if not data:
									break
							fp.close()							
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
							for data in iter(lambda: nca.read(int(buffer)), ""):
								fp.write(data)
								fp.flush()
								if not data:
									break				
							fp.close()
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
								for data in iter(lambda: nca.read(int(buffer)), ""):
									fp.write(data)
									fp.flush()
									if not data:
										break
								fp.close()
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
								for data in iter(lambda: nca.read(int(buffer)), ""):
									fp.write(data)
									fp.flush()
									if not data:
										break
								fp.close()
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
			meta_nca.flush()
			meta_nca.close()
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.set_pfs0_hash(sha)
			meta_nca.flush()
			meta_nca.close()
			############################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha2=meta_nca.calc_htable_hash()
			meta_nca.flush()
			meta_nca.close()						
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.header.set_htable_hash(sha2)
			meta_nca.flush()
			meta_nca.close()
			########################
			meta_nca = Fs.Nca(filepath, 'r+b')
			sha3=meta_nca.header.calculate_hblock_hash()
			meta_nca.flush()
			meta_nca.close()						
			meta_nca = Fs.Nca(filepath, 'r+b')
			meta_nca.header.set_hblock_hash(sha3)
			meta_nca.flush()
			meta_nca.close()
			########################
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
							Print.info(tabs + 'Copying: ' + str(filename))
							for data in iter(lambda: nca.read(int(buffer)), ""):
								fp.write(data)
								fp.flush()
								if not data:
									break
							fp.close()

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
	def updbase_read(self,ofolder,buffer,cskip):
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
										self.updbase_copy(ofolder,buffer,nca_name)
									nca_meta=str(nca._path)
									self.updbase_copy(ofolder,buffer,nca_meta)
									self.updbase_tyc(ofolder,titleid2)
									
	def updbase_copy(self,ofolder,buffer,nca_name):
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
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)							
									if content_type_cnmt == 'AddOnContent':
										content_type='DLC'
										reqtag='- RequiredUpdateNumber: '
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)	
									if content_type_cnmt == 'Application':
										content_type='Base Game or Application'
										reqtag='- RequiredSystemVersion: '	
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)	
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
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)							
									if content_type_cnmt == 'AddOnContent':
										content_type='DLC'
										reqtag='- RequiredUpdateNumber: '
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)	
									if content_type_cnmt == 'Application':
										content_type='Base Game or Application'
										reqtag='- RequiredSystemVersion: '	
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)	
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
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)							
									if content_type_cnmt == 'AddOnContent':
										content_type='DLC'
										reqtag='- RequiredUpdateNumber: '
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)	
									if content_type_cnmt == 'Application':
										content_type='Base Game or Application'
										reqtag='- RequiredSystemVersion: '	
										tit_name,editor,ediver,SupLg = self.inf_get_title(target,offset,content_entries,original_ID)	
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
											contentname = self.inf_get_title(target,offset,content_entries,original_ID)
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
		title = 'DLC'									
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
								SupLg=list()
								for i in Langue:
									f.seek(0x14200+i*0x300)	
									title = f.read(0x200)		
									title = title.split(b'\0', 1)[0].decode('utf-8')
									title = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', title))
									title = title.strip()
									if title != "":	
										if i==0:
											SupLg.append("US (eng)")
										if i==1:
											SupLg.append("GK (eng)")
										if i==2:
											SupLg.append("JP")
										if i==3:
											SupLg.append("FR")		
										if i==4:
											SupLg.append("DE")	
										if i==5:
											SupLg.append("LAT (spa)")	
										if i==6:
											SupLg.append("SPA")	
										if i==7:
											SupLg.append("IT")	
										if i==8:
											SupLg.append("DU")	
										if i==9:
											SupLg.append("CAD (fr)")	
										if i==10:
											SupLg.append("POR")	
										if i==11:
											SupLg.append("RU")	
										if i==12:
											SupLg.append("KOR")	
										if i==13:
											SupLg.append("TAI")		
										if i==14:
											SupLg.append("CH")															
								for i in Langue:
									f.seek(0x14200+i*0x300)		
									title = f.read(0x200)
									editor = f.read(0x100)							
									title = title.split(b'\0', 1)[0].decode('utf-8')
									title = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', title))
									title = title.strip()
									editor = editor.split(b'\0', 1)[0].decode('utf-8')
									editor = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\s™©®()\~]+', ' ', editor))
									editor = editor.strip()							
									if title == "":
										title = 'DLC'
									if title != 'DLC':
										title = title
										f.seek(0x17260)	
										ediver = f.read(0x10)
										ediver = ediver.split(b'\0', 1)[0].decode('utf-8')
										ediver = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\s™©®()\~]+', ' ', ediver))
										ediver = ediver.strip()															
										return(title,editor,ediver,SupLg)
		return(title,"","","")			
												
						