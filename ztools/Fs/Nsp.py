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
import sq_tools
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

	def copy_pfs0_meta(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					for f in nca:
						nca.rewind()
						f.rewind()
						filename =  'PFS0'
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

	def copy_ndata(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.DATA':
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
		Print.info(files)
		
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

				
#SIMPLE CHECKS						
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


#SIMPLE FILE-LIST			
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
	
#READ CNMT FILE WITHOUT EXTRACTION	
	def read_cnmt(self):
		for nca in self:
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
							#cnmt.rewind()
							#cnmt.seek(0x28)		
							#cnmt.writeInt64(336592896)
							cnmt.rewind()
							cnmt.seek(0x28)					
							min_sversion=self.readInt32()
							end_of_emeta=self.readInt32()	
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
							for i in range(content_entries):
								Print.info('........................')							
								Print.info('Content number ' + str(i+1))
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

#GET VERSION NUMBER FROM CNMT							
	def get_cnmt_verID(self):
		for nca in self:
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

								
#COPY AND CLEAN NCA FILES AND PATCH NEEDED SYSTEM VERSION			
	def cr_tr_nca(self,ofolder,buffer,metapatch, keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		text_file='newcontent_'+self.getnspid()+'.dat'
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
					textpath = os.path.join(outfolder, text_file)
					with open(textpath, 'a') as tfile:			
						tfile.write(str(nca.header.contentType)+ ': ' + tabs + str(nca._path) + '\n')	
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
							self.patch_meta(filepath,text_file,outfolder,RSV_cap)
						else:					
							textpath = os.path.join(outfolder, text_file)
							with open(textpath, 'a') as tfile:			
								tfile.write(str(nca.header.contentType)+ ': ' + tabs + str(nca._path) + '\n')					
								
						
#COPY AND CLEAN NCA FILES SKIPPING DELTAS AND PATCH NEEDED SYSTEM VERSION						
	def cr_tr_nca_nd(self,ofolder,buffer,metapatch, keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		text_file='newcontent_'+self.getnspid()+'.dat'
		ticket = self.ticket()
		masterKeyRev = ticket.getMasterKeyRevision()
		titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
		rightsId = ticket.getRightsId()
		Print.info('rightsId =\t' + hex(rightsId))
		Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))
		Print.info('Copying files: ')
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getCryptoType2() != masterKeyRev:
					pass
					raise IOError('Mismatched masterKeyRevs!')
		
		for nca in self:
			vfragment="false"
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.DATA':
					for f in nca:
							for file in f:
								filename = str(file._path)
								if filename=="fragment":
									vfragment="true"
				if str(vfragment)=="true":
					Print.info(tabs + 'Skipping delta fragment: ' + str(nca._path))
					continue
				else:
					if nca.header.getRightsId() != 0:
						nca.rewind()
						filename =  str(nca._path)
						outfolder = str(ofolder)+'/'
						filepath = os.path.join(outfolder, filename)
						if not os.path.exists(outfolder):
							os.makedirs(outfolder)
						textpath = os.path.join(outfolder, text_file)
						with open(textpath, 'a') as tfile:			
							tfile.write(str(nca.header.contentType)+ ': ' + tabs + str(nca._path)+'\n')	
						fp = open(filepath, 'w+b')
						nca.rewind()
						Print.info(tabs)
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
						Print.info(tabs + '-> Copying: ' + str(filename))
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
						#///////////////////////////////////						
						if metapatch == 'true':
							if 	str(nca.header.contentType) == 'Content.META':
								self.patch_meta(filepath,text_file,outfolder,RSV_cap)
							else:					
								textpath = os.path.join(outfolder, text_file)
								with open(textpath, 'a') as tfile:			
									tfile.write(str(nca.header.contentType)+ ': ' + tabs + str(nca._path) + '\n')												
									
#Copy nca files						
	def copy_nca(self,ofolder,buffer,metapatch, keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		text_file='newcontent_'+self.getnspid()+'.dat'
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
				#///////////////////////////////////
				target = Fs.Nca(filepath, 'r+b')
				target.rewind()
				if keypatch != 'false':
					if keypatch < target.header.getCryptoType2():
						self.change_mkrev_nca(target, keypatch)
				target.close()						
				if metapatch == 'true':
					if 	str(nca.header.contentType) == 'Content.META':
						self.patch_meta(filepath,text_file,outfolder,RSV_cap)
					else:					
						textpath = os.path.join(outfolder, text_file)
						with open(textpath, 'a') as tfile:			
							tfile.write(str(nca.header.contentType)+ ': ' + tabs + str(nca._path) + '\n')											
				
															
#Copy nca files skipping deltas
	def copy_nca_nd(self,ofolder,buffer,metapatch, keypatch,RSV_cap):
		if keypatch != 'false':
			keypatch = int(keypatch)
		indent = 1
		tabs = '\t' * indent
		text_file='newcontent_'+self.getnspid()+'.dat'
		Print.info('Copying files: ')
		for nca in self:
			vfragment="false"
			if type(nca) == Nca:
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
							self.patch_meta(filepath,text_file,outfolder,RSV_cap)
						else:					
							textpath = os.path.join(outfolder, text_file)
							with open(textpath, 'a') as tfile:			
								tfile.write(str(nca.header.contentType)+ ': ' + tabs + str(nca._path) + '\n')						

#///////////////////////////////////////////////////								
#SPLIT MULTI-CONTENT NSP IN FOLDERS
#///////////////////////////////////////////////////	
	def splitter_read(self,ofolder,buffer,pathend):
		for nca in self:
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

								
	def splitter_copy(self,ofolder,buffer,nca_name):
		indent = 1
		tabs = '\t' * indent
		for nca in self:
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
		for ticket in self:
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
		for cert in self:					
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
		for nca in self:
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
			for nca in self:
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
		for nca in self:
			if type(nca) == Nca:
				if nca_name == str(nca._path):
					for f in nca:
						nca.rewind()
						f.rewind()	
						f.seek(0x14200)
						title = f.read(0x200)		
						title = title.split(b'\0', 1)[0].decode('utf-8')
						title = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', title))
						title = title.strip()
						title = title + content_type
		return(title)


		
		
		





#///////////////////////////////////////////////////								
#INFO ABOUT UPD REQUIREMENTS
#///////////////////////////////////////////////////	
	def print_fw_req(self):
		for nca in self:
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
							contentname = self.inf_get_title(target,offset,content_entries,original_ID)
							cnmt.rewind()
							cnmt.seek(0x20+offset)
							titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
							titleid2 = titleid2[2:-1]
							version=str(int.from_bytes(titleversion, byteorder='little'))
							keygen=nca.header.getCryptoType2()					
							MinRSV=sq_tools.getMinRSV(keygen,RSversion)
							FW_rq=sq_tools.getFWRangeKG(keygen)
							RSV_rq=sq_tools.getFWRangeRSV(RSversion)									
							RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)
							content_name=str(cnmt._path)
							content_name=content_name[:-22]
							if content_name == 'Patch':
								content_type='Update'
							if content_name == 'AddOnContent':
								content_type='DLC'
							if content_name == 'Application':
								content_type='Base Game or Application'
							Print.info('-------------------------------------')
							Print.info('Detected content: ' + str(titleid2))	
							Print.info('-------------------------------------')							
							Print.info("- Name: " + contentname)	
							Print.info("- Version: " + version)
							Print.info("- Type: " + content_type)								
							Print.info('- RequiredSystemVersion: ' + str(RSversion)+" -> " +RSV_rq)	
							Print.info('- Encryption (keygeneration): ' + str(keygen)+" -> " +FW_rq)
							Print.info('- Patchable to: ' + str(MinRSV)+" -> " + RSV_rq_min)		
							
	def inf_get_title(self,target,offset,content_entries,original_ID):
		content_type=''
		for nca in self:
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
			for nca in self:
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
		title='DLC'
		for nca in self:
			if type(nca) == Nca:
				if nca_name == str(nca._path):
					for f in nca:
						nca.rewind()
						f.rewind()	
						f.seek(0x14200)
						title = f.read(0x200)		
						title = title.split(b'\0', 1)[0].decode('utf-8')
						title = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', title))
						title = title.strip()
						title = title
		return(title)							
							
							
#///////////////////////////////////////////////////								
#PREPARE BASE CONTENT TO UPDATE IT
#///////////////////////////////////////////////////	
	def updbase_read(self,ofolder,buffer,cskip):
		for nca in self:
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
							min_sversion=cnmt.readInt32()
							Emeta=cnmt.readInt32()
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
		for nca in self:
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
		for ticket in self:
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
		for cert in self:					
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
				else:
					nca.header.setCryptoType(newMasterKeyRev)
					nca.header.setCryptoType2(0)	
					Print.info(tabs2 + 'DONE')					

#///////////////////////////////////////////////////								
#PATCH META FUNCTION
#///////////////////////////////////////////////////	
	def patch_meta(self,filepath,text_file,outfolder,RSV_cap):
		indent = 1
		tabs = '\t' * indent	
		Print.info(tabs + '-------------------------------------')
		Print.info(tabs + 'Checking meta: ')
		meta_nca = Fs.Nca(filepath, 'r+b')
		keygen=meta_nca.header.getCryptoType2()
		RSV=meta_nca.get_req_system()		
		RSVmin=sq_tools.getMinRSV(keygen,RSV)
		RSVmax=sq_tools.getTopRSV(keygen,RSV)		
		if 	RSV > RSVmin:
			if RSVmin >= RSV_cap:
				meta_nca.write_req_system(RSVmin)
			if keygen < 4:
				if RSV > RSVmax:
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
			textpath = os.path.join(outfolder, text_file)
			with open(textpath, 'a') as tfile:			
				tfile.write(str(meta_nca.header.contentType)+ ': ' + tabs + tabs + newname + '\n')
		else:
			Print.info(tabs +'-> No need to patch the meta' )
			Print.info(tabs + '-------------------------------------')
			textpath = os.path.join(outfolder, text_file)
			with open(textpath, 'a') as tfile:			
				tfile.write(str(meta_nca.header.contentType)+ ': ' + tabs + tabs + str(meta_nca._path) + '\n')									
								
								
	def get_title(self):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					for f in nca:
						nca.rewind()
						f.rewind()	
						f.seek(0x14200)
						title = f.read(0x200)		
						title = title.split(b'\0', 1)[0].decode('utf-8')
					return(title)

					
					
''' TEST CODE 
	def copy_nca_control(self,ofolder,buffer):
		files=[]
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					files.append(str(filepath))
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
		return 	files				
					
	def copy_nca_meta(self,ofolder,buffer):
		files=[]
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					nca.rewind()
					filename =  str(nca._path)
					outfolder = str(ofolder)+'/'
					filepath = os.path.join(outfolder, filename)
					files.append(str(filepath))
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
		return 	files	'''



















					
				
				
				
				
				
				