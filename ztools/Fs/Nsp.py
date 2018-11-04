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
from Fs.Pfs0 import Pfs0
from Fs.Ticket import Ticket
from Fs.Nca import Nca

MEDIA_SIZE = 0x200

class Nsp(Pfs0):
		
	def __init__(self, path = None, mode = 'rb'):
		self.path = None
		self.titleId = None
		self.hasValidTicket = None
		self.timestamp = None
		self.version = None

		super(Nsp, self).__init__(None, path, mode)
		
		if path:
			self.setPath(path)
			#if files:
			#	self.pack(files)
				
		if self.titleId and self.isUnlockable():
			Print.info('unlockable title found ' + self.path)
		#	self.unlock()

	def loadCsv(self, line, map = ['id', 'path', 'version', 'timestamp', 'hasValidTicket']):
		split = line.split('|')
		for i, value in enumerate(split):
			if i >= len(map):
				Print.info('invalid map index: ' + str(i) + ', ' + str(len(map)))
				continue
			
			i = str(map[i])
			methodName = 'set' + i[0].capitalize() + i[1:]
			method = getattr(self, methodName, lambda x: None)
			method(value.strip())

	def serialize(self, map = ['id', 'path', 'version', 'timestamp', 'hasValidTicket']):
		r = []
		for i in map:
				
			methodName = 'get' + i[0].capitalize() + i[1:]
			method = getattr(self, methodName, lambda: methodName)
			r.append(str(method()))
		return '|'.join(r)

	def __lt__(self, other):
		return str(self.path) < str(other.path)
				
	def __iter__(self):
		return self.files.__iter__()
		
	def title(self):

			
		if self.titleId in Titles.keys():
			return Titles.get(self.titleId)
			
		t = Title.Title()
		t.setId(self.titleId)
		Titles.data()[self.titleId] = t
		return t

	def getUpdateFile(self):
		title = self.title()

		if title.isUpdate or title.isDLC or not title.updateId:
			return None

		for i, nsp in Nsps.files.items():
			if nsp.titleId == title.updateId:
				return nsp

		return None

	def isUpdateAvailable(self):
		title = self.title()

		if self.titleId and title.version != None and self.version < title.version and str(title.version) != '0':
			return {'id': title.id, 'baseId': title.baseId, 'currentVersion': self.version, 'newVersion': title.version}

		if not title.isUpdate and not title.isDLC and Titles.contains(title.updateId):
			updateFile = self.getUpdateFile()

			if updateFile:
				return updateFile.isUpdateAvailable()

			updateTitle = Titles.get(title.updateId)

			if updateTitle.version and str(updateTitle.version) != '0':
				return {'id': updateTitle.id, 'baseId': title.baseId, 'currentVersion': None, 'newVersion': updateTitle.version}

		return None
		
	def readMeta(self):
		self.open()
		try:
			#a = self.application()
			#if a.header.titleId:
			#	self.titleId = a.header.titleId
			#	self.title().setRightsId(a.header.rightsId)

			t = self.ticket()
			rightsId = hx(t.getRightsId().to_bytes(0x10, byteorder='big')).decode('utf-8').upper()
			self.titleId = rightsId[0:16]
			self.title().setRightsId(rightsId)
			Print.debug('rightsId = ' + rightsId)
			Print.debug(self.titleId + ' key = ' +  str(t.getTitleKeyBlock()))
			self.setHasValidTicket(t.getTitleKeyBlock() != 0)
		except BaseException as e:
			Print.info('readMeta filed ' + self.path + ", " + str(e))
			raise
		self.close()

	def unpack(self, path):
		os.makedirs(path, exist_ok=True)

		for nspF in self:
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

	def setHasValidTicket(self, value):
		if self.title().isUpdate:
			self.hasValidTicket = True
			return

		try:
			self.hasValidTicket = (True if value and int(value) != 0 else False) or self.title().isUpdate
		except:
			pass

	def getHasValidTicket(self):
		if self.title().isUpdate:
			return 1
		return (1 if self.hasValidTicket and self.hasValidTicket == True else 0)

	def setId(self, id):
		if re.match('[A-F0-9]{16}', id, re.I):
			self.titleId = id

	def getId(self):
			return self.titleId or ('0' * 16)

	def setTimestamp(self, timestamp):
		try:
			self.timestamp = int(str(timestamp), 10)
		except:
			pass

	def getTimestamp(self):
		return str(self.timestamp or '')

	def setVersion(self, version):
		if version and len(version) > 0:
			self.version = version

	def getVersion(self):
		return self.version or ''
			
	def setPath(self, path):			
		self.path = path
		self.version = '0'
		
		z = re.match('.*\[([a-zA-Z0-9]{16})\].*', path, re.I)
		if z:
			self.titleId = z.groups()[0].upper()
		else:
			self.titleId = None

		z = re.match('.*\[v([0-9]+)\].*', path, re.I)
		if z:
			self.version = z.groups()[0]

		ext = pathlib.Path(path).suffix
		if ext == '.nsp':
			if self.hasValidTicket == None:
				self.setHasValidTicket(True)
		elif ext == '.nsx':
			if self.hasValidTicket == None:
				self.setHasValidTicket(False)
		else:
			return

	def getPath(self):
		return self.path or ''
			
	def open(self, path = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Nsp, self).open(path or self.path, mode, cryptoType, cryptoKey, cryptoCounter)
					
	def move(self):
		if not self.path:
			Print.error('no path set')
			return False
		
		if not self.fileName():
			Print.error('could not get filename for ' + self.path)
			return False

		if os.path.abspath(self.fileName()).lower() == os.path.abspath(self.path).lower():
			return False
		if os.path.isfile(self.fileName()) and os.path.abspath(self.path) == os.path.abspath(self.fileName()):
			Print.info('duplicate title: ')
			Print.info(os.path.abspath(self.path))
			Print.info(os.path.abspath(self.fileName()))
			return False

		try:
			Print.info(self.path + ' -> ' + self.fileName())
			os.makedirs(os.path.dirname(self.fileName()), exist_ok=True)
			newPath = self.fileName()
			os.rename(self.path, newPath)
			self.path = newPath
		except BaseException as e:
			Print.info('failed to rename file! %s -> %s  : %s' % (self.path, self.fileName(), e))
		
		return True
		
	def cleanFilename(self, s):
		#s = re.sub('\s+\Demo\s*', ' ', s, re.I)
		s = re.sub('\s*\[DLC\]\s*', '', s, re.I)
		s = re.sub(r'[\/\\\:\*\?\"\<\>\|\.\s™©®()\~]+', ' ', s)
		return s.strip()

	def dict(self):
		return {"titleId": self.titleId, "hasValidTicket": self.hasValidTicket, 'version': self.version, 'timestamp': self.timestamp, 'path': self.path }
		
	def fileName(self):
		bt = None
		if not self.titleId in Titles.keys():
			if not Title.getBaseId(self.titleId) in Titles.keys():
				Print.info('could not find title key for ' + self.titleId + ' or ' + Title.getBaseId(self.titleId))
				return None
			bt = Titles.get(Title.getBaseId(self.titleId))
			t = Title()
			t.loadCsv(self.titleId + '0000000000000000|0000000000000000|' + bt.name)
		else:
			t = Titles.get(self.titleId)
		
			if not t.baseId in Titles.keys():
				Print.info('could not find baseId for ' + self.path)
				return None
			bt = Titles.get(t.baseId)
		
		if t.isDLC:
			format = Config.paths.getTitleDLC(not self.hasValidTicket)
		elif t.isDemo:
			if t.idExt != 0:
				format = Config.paths.getTitleDemoUpdate(not self.hasValidTicket)
			else:
				format = Config.paths.getTitleDemo(not self.hasValidTicket)
		elif t.idExt != 0:
			format = Config.paths.getTitleUpdate(not self.hasValidTicket)
		else:
			format = Config.paths.getTitleBase(not self.hasValidTicket)
			
		format = format.replace('{id}', self.cleanFilename(t.id))
		format = format.replace('{region}', self.cleanFilename(t.region or ''))
		format = format.replace('{name}', self.cleanFilename(t.name or ''))
		format = format.replace('{version}', str(self.version or 0))
		format = format.replace('{baseId}', self.cleanFilename(bt.id))
		format = format.replace('{baseName}', self.cleanFilename(bt.name or ''))
		
		'''
		if self.hasValidTicket:
			format = os.path.splitext(format)[0] + '.nsp'
		else:
			format = os.path.splitext(format)[0] + '.nsx'
		'''
		
		return format
		
	def ticket(self):
		for f in (f for f in self if type(f) == Ticket):
			return f
		raise IOError('no ticket in NSP')
		
	def cnmt(self):
		for f in (f for f in self if f._path.endswith('.cnmt.nca')):
			return f
		raise IOError('no cnmt in NSP')

	def xml(self):
		for f in (f for f in self if f._path.endswith('.xml')):
			return f
		raise IOError('no XML in NSP')

	def hasDeltas(self):
		return b'DeltaFragment' in self.xml().read()
		
	def application(self):
		for f in (f for f in self if f._path.endswith('.nca') and not f._path.endswith('.cnmt.nca')):
			return f
		raise IOError('no application in NSP')
		
	def isUnlockable(self):
		return (not self.hasValidTicket) and self.titleId and Titles.contains(self.titleId) and Titles.get(self.titleId).key
		
	def unlock(self):
		#if not self.isOpen():
		#	self.open('r+b')

		if not Titles.contains(self.titleId):
			raise IOError('No title key found in database!')

		self.ticket().setTitleKeyBlock(int(Titles.get(self.titleId).key, 16))
		Print.info('setting title key to ' + Titles.get(self.titleId).key)
		self.ticket().flush()
		self.close()
		self.hasValidTicket = True
		self.move()

	def setMasterKeyRev(self, newMasterKeyRev):
		if not Titles.contains(self.titleId):
			raise IOError('No title key found in database! ' + self.titleId)

		ticket = self.ticket()
		masterKeyRev = ticket.getMasterKeyRevision()
		titleKey = ticket.getTitleKeyBlock()
		newTitleKey = Keys.changeTitleKeyMasterKey(titleKey.to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev), Keys.getMasterKeyIndex(newMasterKeyRev))
		rightsId = ticket.getRightsId()

		if rightsId != 0:
			raise IOError('please remove titlerights first')

		if (newMasterKeyRev == None and rightsId == 0) or masterKeyRev == newMasterKeyRev:
			Print.info('Nothing to do')
			return

		Print.info('rightsId =\t' + hex(rightsId))
		Print.info('titleKey =\t' + str(hx(titleKey.to_bytes(16, byteorder='big'))))
		Print.info('newTitleKey =\t' + str(hx(newTitleKey)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))



		for nca in self:
			if type(nca) == Nca:
				if nca.header.getCryptoType2() != masterKeyRev:
					pass
					raise IOError('Mismatched masterKeyRevs!')

		ticket.setMasterKeyRevision(newMasterKeyRev)
		ticket.setRightsId((ticket.getRightsId() & 0xFFFFFFFFFFFFFFFF0000000000000000) + newMasterKeyRev)
		ticket.setTitleKeyBlock(int.from_bytes(newTitleKey, 'big'))

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getCryptoType2() != newMasterKeyRev:
					Print.info('writing masterKeyRev for %s, %d -> %s' % (str(nca._path),  nca.header.getCryptoType2(), str(newMasterKeyRev)))

					encKeyBlock = nca.header.getKeyBlock()

					if sum(encKeyBlock) != 0:
						key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
						Print.info('decrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						crypto = aes128.AESECB(key)
						decKeyBlock = crypto.decrypt(encKeyBlock)

						key = Keys.keyAreaKey(Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex)
						Print.info('encrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex))
						crypto = aes128.AESECB(key)

						reEncKeyBlock = crypto.encrypt(decKeyBlock)
						nca.header.setKeyBlock(reEncKeyBlock)


					if newMasterKeyRev >= 3:
						nca.header.setCryptoType(2)
						nca.header.setCryptoType2(newMasterKeyRev)
					else:
						nca.header.setCryptoType(newMasterKeyRev)
						nca.header.setCryptoType2(0)


	def removeTitleRights(self):
		if not Titles.contains(self.titleId):
			raise IOError('No title key found in database! ' + self.titleId)

		ticket = self.ticket()
		masterKeyRev = ticket.getMasterKeyRevision()
		titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
		rightsId = ticket.getRightsId()

		Print.info('rightsId =\t' + hex(rightsId))
		Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))



		for nca in self:
			if type(nca) == Nca:
				if nca.header.getCryptoType2() != masterKeyRev:
					pass
					raise IOError('Mismatched masterKeyRevs!')


		ticket.setRightsId(0)

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() == 0:
					continue

				Print.info('writing masterKeyRev for %s, %d' % (str(nca._path),  masterKeyRev))
				crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))

				encKeyBlock = crypto.encrypt(titleKeyDec * 4)
				nca.header.setRightsId(0)
				nca.header.setKeyBlock(encKeyBlock)
				Hex.dump(encKeyBlock)
				
	def copy_ticket(self,ofolder):
		for ticket in self:
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
				fp.close()

	def copy_nca(self,ofolder,buffer):
		indent = 1
		tabs = '\t' * indent
		for nca in self:
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
				
	def copy_nca_control(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
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
					
	def copy_nca_meta(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
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

	def copy_pfs0(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				for f in nca:
					nca.rewind()
					f.rewind()
					filename =  str(f._path)
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					if not os.path.exists(outfolder):
						os.makedirs(outfolder)
					fp = open(filepath, 'w+b')
					nca.rewind()
					f.rewind()	
					for data in iter(lambda:f.read(int(buffer)), ""):
						fp.write(data)
						fp.flush()
						if not data:
							break
					fp.close()					
						
	def copy_cnmt(self,ofolder,buffer):
		for nca in self:
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

	def copy_ncap(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					for f in nca:
						nca.rewind()
						f.rewind()
						filename =  str(f._path)
						outfolder = str(ofolder)+'/'
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						fp = open(filepath, 'w+b')
						nca.rewind()
						f.rewind()	
						for data in iter(lambda:f.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							if not data:
								break
						

	def copy_nca_manual(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.MANUAL':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
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
									
	def copy_nca_program(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.PROGRAM':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
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
				
	def copy_nca_data(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.DATA':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
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
									
	def copy_nca_pdata(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.UNKNOWN':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
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

	def copy_other(self,ofolder,buffer):
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
				
	def copy_xml(self,ofolder,buffer):
		for file in self:
			if file._path.endswith('.xml'):
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
		
	def copy_nsp_cert(self,ofolder,buffer):
		for file in self:
			if file._path.endswith('.cert'):
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

	def copy_jpg(self,ofolder,buffer):
		for file in self:
			if file._path.endswith('.jpg'):
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

	def copy_tr_nca(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					if not os.path.exists(outfolder):
						os.makedirs(outfolder)
					fp = open(filepath, 'w+b')
					nca.rewind()			
					for data in iter(lambda: nca.read(312000), ""):
						fp.write(data)
						fp.flush()
						if not data:
							break
					fp.close()				

	def copy_ntr_nca(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() == 0:
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					if not os.path.exists(outfolder):
						os.makedirs(outfolder)
					fp = open(filepath, 'w+b')
					nca.rewind()			
					for data in iter(lambda: nca.read(312000), ""):
						fp.write(data)
						fp.flush()
						if not data:
							break
					fp.close()

					
	def copyandremove_tr_nca(self,ofolder,buffer):
		indent = 1
		tabs = '\t' * indent
		ticket = self.ticket()
		masterKeyRev = ticket.getMasterKeyRevision()
		titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
		rightsId = ticket.getRightsId()
		Print.info('rightsId =\t' + hex(rightsId))
		Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))
		
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getCryptoType2() != masterKeyRev:
					pass
					raise IOError('Mismatched masterKeyRevs!')
		
		for nca in self:
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
					target = Fs.Nca(filepath, 'r+b')
					target.rewind()
					Print.info(tabs + 'Removing titlerights for ' + str(filename))
					Print.info(tabs + 'Writing masterKeyRev for %s, %d' % (str(nca._path),  masterKeyRev))
					crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
					encKeyBlock = crypto.encrypt(titleKeyDec * 4)
					target.header.setRightsId(0)
					target.header.setKeyBlock(encKeyBlock)
					Hex.dump(encKeyBlock)	
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
					
	def copy_KeyBlock(self,ofolder):
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					nca.rewind()
					nca.seek(0x300)
					KeyBlock = nca.read(0x40)
					filename = str(nca._path)
					filename = filename[:-4] + '.keyblock'
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					if not os.path.exists(outfolder):
						os.makedirs(outfolder)
					fp = open(filepath, 'w+b')
					fp.write(KeyBlock)
					fp.flush()
					fp.close()			
				
	def removeTitleRightsnca(self, masterKeyRev, titleKeyDec):
		if not Titles.contains(self.titleId):
			raise IOError('No title key found in database! ' + self.titleId)

		Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))


		for nca in self:
			if type(nca) == Nca:
				if nca.header.getCryptoType2() != masterKeyRev:
					pass
					raise IOError('Mismatched masterKeyRevs!')


		ticket.setRightsId(0)

		for nca in files:
			if type(nca) == Nca:
				if nca.header.getRightsId() == 0:
					continue

				Print.info('writing masterKeyRev for %s, %d' % (str(nca._path),  masterKeyRev))
				crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))

				encKeyBlock = crypto.encrypt(titleKeyDec * 4)
				nca.header.setRightsId(0)
				nca.header.setKeyBlock(encKeyBlock)
				Hex.dump(encKeyBlock)				


		
	def seteshop(self):
		for nca in self:
			if type(nca) == Nca:
				nca.header.setgamecard(0)
			
	def setcgame(self):
		for nca in self:
			if type(nca) == Nca:
				nca.header.setgamecard(1)	
				
				
				
	def getnspid(self):
		target=self.cnmt()
		titleid=str(target.header.titleId)
		return titleid
		
	def nspmasterkey(self):
		if not Titles.contains(self.titleId):
			raise IOError('No title key found in database! ' + self.titleId)
		ticket = self.ticket()
		masterKeyRev = ticket.getMasterKeyRevision()
		titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
		rightsId = ticket.getRightsId()

		return masterKeyRev
		
	def nsptitlekeydec(self):				
		if not Titles.contains(self.titleId):
			raise IOError('No title key found in database! ' + self.titleId)
		ticket = self.ticket()
		masterKeyRev = ticket.getMasterKeyRevision()
		titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
		rightsId = ticket.getRightsId()
		titleKey = ticket.getTitleKeyBlock().to_bytes(16, byteorder='big')

		return titleKeyDec		
		

	def pack(self, files):
		if not self.path:
			return False
			
		Print.info('\tRepacking to NSP...')
		
		hd = self.generateHeader(files)
		
		totSize = len(hd) + sum(os.path.getsize(file) for file in files)
		if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
			Print.info('\t\tRepack %s is already complete!' % self.path)
			return
			
		t = tqdm(total=totSize, unit='B', unit_scale=True, desc=os.path.basename(self.path), leave=False)
		
		t.write('\t\tWriting header...')
		outf = open(self.path, 'wb')
		outf.write(hd)
		t.update(len(hd))
		
		done = 0
		for file in files:
			t.write('\t\tAppending %s...' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(4096)
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))
		t.close()
		
		Print.info('\t\tRepacked to %s!' % outf.name)
		outf.close()

	def generateHeader(self, files):
		filesNb = len(files)
		stringTable = '\x00'.join(os.path.basename(file) for file in files)
		headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
		remainder = 0x10 - headerSize%0x10
		headerSize += remainder
		
		fileSizes = [os.path.getsize(file) for file in files]
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		fileNamesLengths = [len(os.path.basename(file))+1 for file in files] # +1 for the \x00
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

	def verifyKey(self, key):
		for f in self:
			if type(f) == Nca:
				pass

	def exist_control(self):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					return 'TRUE'
		return 'FALSE'	
				
	def trights_set(self):
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					return 'TRUE'	
		return 'FALSE'					

	def exist_ticket(self):
		for ticket in self:
			if type(ticket) == Ticket:
				return 'TRUE'	
		return 'FALSE'			

	def print_file_list(self):
		for nca in self:
			if type(nca) == Nca:
				if nca._path.endswith('.cnmt.nca'):
					continue
				filename = str(nca._path)
				Print.info(str(filename))
		for nca in self:
			if type(nca) == Nca:
				if nca._path.endswith('.cnmt.nca'):
					filename = str(nca._path)
					Print.info(str(filename))
		for file in self:
			if type(file) != Nca:
				filename =  str(file._path)
				Print.info(str(filename))
	

				
				
				