import aes128
import Title
import Titles
import Hex
from binascii import hexlify as hx, unhexlify as uhx
from struct import pack as pk, unpack as upk
from Fs.File import File
from hashlib import sha256,sha1
import Fs.Type
from Fs import Type
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
from Fs.Nacp import Nacp
from Fs.ChromeNacp import ChromeNacp
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
from Fs.pyNCA3 import NCA3
from Fs.pyNPDM import NPDM
import math
import sys
import shutil
import DBmodule
if sys.platform == 'win32':
	import win32con, win32api
from operator import itemgetter, attrgetter, methodcaller
from Crypto.Cipher import AES
import io
import nutdb
import textwrap
from PIL import Image
import zstandard
from Crypto.Cipher import AES
from Crypto.Util import Counter
import time

#from Cryptodome.Signature import pss
#from Cryptodome.PublicKey import RSA
#from Cryptodome import Random
#from Cryptodome.Hash import SHA256 as newsha

MEDIA_SIZE = 0x200
indent = 1
tabs = '\t' * indent
htmlspace='&nbsp;'

def readInt64(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(8), byteorder=byteorder, signed=signed)

def readInt128(f, byteorder='little', signed = False):
	return int.from_bytes(f.read(16), byteorder=byteorder, signed=signed)

class AESCTR:
	def __init__(self, key, nonce, offset = 0):
		self.key = key
		self.nonce = nonce
		self.seek(offset)

	def encrypt(self, data, ctr=None):
		if ctr is None:
			ctr = self.ctr
		return self.aes.encrypt(data)

	def decrypt(self, data, ctr=None):
		return self.encrypt(data, ctr)

	def seek(self, offset):
		self.ctr = Counter.new(64, prefix=self.nonce[0:8], initial_value=(offset >> 4))
		self.aes = AES.new(self.key, AES.MODE_CTR, counter=self.ctr)

class Section:
	def __init__(self, f):
		self.f = f
		self.offset = readInt64(f)
		self.size = readInt64(f)
		self.cryptoType = readInt64(f)
		readInt64(f) # padding
		self.cryptoKey = f.read(16)
		self.cryptoCounter = f.read(16)

class ChromeNsp(Pfs0):

	def __init__(self, path = None, mode = 'rb'):
		self.path = None
		self.titleId = None
		self.hasValidTicket = None
		self.timestamp = None
		self.version = None

		super(ChromeNsp, self).__init__(None, path, mode)

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
		super(ChromeNsp, self).open(path or self.path, mode, cryptoType, cryptoKey, cryptoCounter)

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


	# ...................................................
	# Patch requrements for network account
	# ...................................................
	def gen_ctrl_list(self):
		print('- Seeking control nca files...')
		ctrl_list=list()
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					ctrl_list.append(nca._path)
				else:
					pass
		return ctrl_list

	def patch_netlicense(self,item=False):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if item == False or nca._path == item:
						check=nca.patch_netlicense()
						return check

	def reb_lv_hashes(self,item=False):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if item == False or nca._path == item:
						print('-------------------------------------------------')
						print('Get Current IVFC level data:')
						print('-------------------------------------------------')
						leveldata,superhashoffset=nca.redo_lvhashes()
						return leveldata,superhashoffset

	def set_lv_hash(self,j,leveldata,item=False):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if item == False or nca._path == item:
						print('-------------------------------------------------')
						print('Rebuild hashes for IVFC level '+str(j)+':')
						print('-------------------------------------------------')
						nca.set_lv_hash(j,leveldata)

	def set_lvsuperhash(self,leveldata,superhashoffset,item=False):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if item == False or nca._path == item:
						print('-------------------------------------------------')
						print('Rebuild IVFC superhash:')
						print('-------------------------------------------------')
						nca.set_lvsuperhash(leveldata,superhashoffset)

	def ctrl_upd_hblock_hash(self,item=False):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if item == False or nca._path == item:
						print('-------------------------------------------------')
						print('Rebuild nca hash-table:')
						print('-------------------------------------------------')
						oldhash=nca.header.get_hblock_hash();print('- Old nca sblock hash: '+str(hx(oldhash)))
						newhash=nca.header.calculate_hblock_hash();print('- New nca sblock hash: '+str(hx(newhash)))
						nca.header.set_hblock_hash(newhash)

	# ...................................................

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
				if nca.header.getRightsId() != 0:
					if nca.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(nca._path)} - {nca.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.getCryptoType2() == 0:
						if nca.header.getCryptoType() == 2:
							masterKeyRev = 2
							titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
							break

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
					if newMasterKeyRev == 2:
						nca.header.setCryptoType(2)
						nca.header.setCryptoType2(0)
					else:
						nca.header.setCryptoType(newMasterKeyRev)
						nca.header.setCryptoType2(0)

	def nsptype(self):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					for f in nca:
						for cnmt in f:
							content_type_cnmt=str(cnmt._path)
							content_type_cnmt=content_type_cnmt[:-22]
							if content_type_cnmt == 'Patch':
								return 'UPDATE'
							if content_type_cnmt == 'AddOnContent':
								return 'DLC'
							if content_type_cnmt == 'Application':
								return 'BASE'

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
				if nca.header.getRightsId() != 0:
					if nca.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(nca._path)} - {nca.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.getCryptoType2() == 0:
						if nca.header.getCryptoType() == 2:
							masterKeyRev = 2
							titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
							break

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

#Extract all files
	def extract_all(self,ofolder,buffer):
		indent = 1
		tabs = '\t' * indent
		print("Processing: "+str(self._path))
		for file in self:
			file.rewind()
			filename =  str(file._path)
			outfolder = str(ofolder)+'/'
			filepath = os.path.join(outfolder, filename)
			if not os.path.exists(outfolder):
				os.makedirs(outfolder)
			fp = open(filepath, 'w+b')
			file.rewind()
			t = tqdm(total=file.size, unit='B', unit_scale=True, leave=False)
			t.write(tabs+'Copying: ' + str(filename))
			for data in iter(lambda: file.read(int(buffer)), ""):
				fp.write(data)
				t.update(len(data))
				fp.flush()
				if not data:
					fp.close()
					t.close()
					break

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
							fp.close()
							break

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
							fp.close()
							break

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
						for data in iter(lambda: nca.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							if not data:
								fp.close()
								break

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
							for data in iter(lambda: nca.read(int(buffer)), ""):
								fp.write(data)
								fp.flush()
								if not data:
									fp.close()
									break

	def copy_nacp(self,ofolder,buffer=32768):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					ncaname =  str(nca._path)[:-4]+'_nca'
					ncafolder = os.path.join(ofolder,ncaname)
					filename = 'control.nacp'
					filepath = os.path.join(ncafolder,filename)
					if not os.path.exists(ncafolder):
						os.makedirs(ncafolder)
					offset=nca.get_nacp_offset()
					for f in nca:
						totSize=f.size-offset
						t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
						t.write('- Writing control.nacp...')
						f.seek(offset)
						fp = open(filepath, 'w+b')
						for data in iter(lambda: f.read(int(buffer)), ""):
							fp.write(data)
							fp.flush()
							t.update(len(data))
							if not data:
								fp.close()
								t.close()
								break
						break
					print('  DONE')

	def copy_as_plaintext(self,ofolder,files_list,buffer=32768):
		for nca in self:
			tk=None;skip=False
			if type(nca) == Nca:
				for fs in nca.sectionFilesystems:
					if fs.cryptoType == Type.Crypto.BKTR:
						skip=True
						break
				if nca.header.getRightsId() != 0:
					correct, tkey = self.verify_nca_key(str(nca._path))
					if correct == True:
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:
							masterKeyRev=crypto1
						tk = Keys.decryptTitleKey(tkey, Keys.getMasterKeyIndex(int(masterKeyRev)))
				else:
					tk=nca.header.titleKeyDec
				if skip == False:
					ncaname =  str(nca._path)
					PN = os.path.join(ofolder,ncaname)
					if not os.path.exists(ofolder):
						os.makedirs(ofolder)
					for i in range(len(files_list)):
						if str(nca._path) == files_list[i][0]:
							offset=files_list[i][1]
							#print(offset)
							break
					#print(nca.size)
					#print(str(nca._path)[-9:])
					lon=0;test=str(nca._path)[-9:]
					if test=='.cnmt.nca':
						ext='.plain.cnmt.nca'
					else:
						ext='.plain.nca'
					lon=(-1)*len(ext)
					try:
						fp=open(str(self._path), 'rb')
						nca3=NCA3(fp,int(offset),str(nca._path),tk)
						nca3.decrypt_to_plaintext(PN.replace(str(nca._path)[lon:], ext))
						fp.close();
					except BaseException as e:
						#Print.error('Exception: ' + str(e))
						if nca.size<int(1073725440):
							try:
								nca.rewind()
								inmemoryfile = io.BytesIO(nca.read())
								nca3=NCA3(inmemoryfile,0,str(nca._path),tk,buffer)
								nca3.decrypt_to_plaintext(PN.replace(str(nca._path)[lon:], ext))
							except BaseException as e:
								#Print.error('Exception: ' + str(e))
								try:
									with open(str(self._path), 'rb') as f:
										f.seek(offset)
										inmemoryfile = io.BytesIO(f.read(files_list[i][3]))
										nca3=NCA3(inmemoryfile,int(0),str(nca._path),tk,buffer)
										nca3.decrypt_to_plaintext(PN.replace(str(nca._path)[lon:], ext))
								except BaseException as e:
									#Print.error('Exception: ' + str(e))
									t = tqdm(total=nca.size, unit='B', unit_scale=True, leave=False)
									t.write(str(nca._path)+' needs to be pre-extracted')
									outnca=open(str(PN), 'w+b')
									nca.rewind()
									try:
										for data in iter(lambda: nca.read(int(buffer)), ""):
											outnca.write(data)
											t.update(len(data))
											outnca.flush()
											if not data:
												outnca.close()
												t.close()
												break
										with open(str(PN), 'rb') as f:
											nca3=NCA3(f,int(0),str(nca._path),tk,buffer)
											nca3.decrypt_to_plaintext(PN.replace(str(nca._path)[lon:], ext))
										try:
											os.remove(str(PN))
										except:
											pass
									except BaseException as e:
										Print.error('Exception: ' + str(e))
										outnca.close()
										t.close()
										try:
											os.remove(str(PN))
										except:
											pass
										continue
						else:
							t = tqdm(total=nca.size, unit='B', unit_scale=True, leave=False)
							t.write(str(nca._path)+' needs to be pre-extracted')
							outnca=open(str(PN), 'w+b')
							nca.rewind()
							for data in iter(lambda: nca.read(int(buffer)), ""):
								try:
									nca.rewind()
									for data in iter(lambda: nca.read(int(buffer)), ""):
										outnca.write(data)
										t.update(len(data))
										outnca.flush()
										if not data:
											outnca.close()
											t.close()
											break
									with open(str(PN), 'rb') as f:
										nca3=NCA3(f,int(0),str(nca._path),tk,buffer)
										nca3.decrypt_to_plaintext(PN.replace(str(nca._path)[lon:], ext))
									try:
										os.remove(str(PN))
									except:
										pass
								except BaseException as e:
									Print.error('Exception: ' + str(e))
									outnca.close()
									t.close()
									try:
										os.remove(str(PN))
									except:
										pass
									continue

	def read_npdm(self,files_list,buffer=32768):
		feed=''
		try:
			for nca in self:
				if type(nca) == Fs.Nca and nca.header.getRightsId() == 0:
					if 	str(nca.header.contentType) == 'Content.PROGRAM':
						titleid2=nca.header.titleId
						feed=self.html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
						feed+='<p style="font-size: 1.86vh;text-align: left;white-space: pre-line;margin-top:0.2vh;"><strong><span">'
						for i in range(len(files_list)):
							if str(nca._path) == files_list[i][0]:
								offset=files_list[i][1]
								#print(offset)
								break
						decKey=nca.header.titleKeyDec
						try:
							fp=open(str(self._path), 'rb')
							nca3=NCA3(fp,int(offset),str(nca._path),decKey)
							feed+=nca3.print_npdm()
							fp.close();
							feed+='</span></strong></p>'
							return feed
						except BaseException as e:
							#Print.error('Exception: ' + str(e))
							nca.rewind()
							for f in nca:
								for g in f:
									if str(g._path)=='main.npdm':
										inmemoryfile = io.BytesIO(g.read())
										npdm = NPDM(inmemoryfile)
										n=npdm.__str__()
										feed+=n
										feed+='</span></strong></p>'
										return feed
				if type(nca) == Fs.Nca and nca.header.getRightsId() != 0:
					if 	str(nca.header.contentType) == 'Content.PROGRAM':
						titleid2=nca.header.titleId
						feed=self.html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
						feed+='<p style="font-size: 1.86vh;text-align: left;white-space: pre-line;margin-top:0.2vh;"><strong><span">'
						correct, tkey = self.verify_nca_key(str(nca._path))
						if correct == True:
							crypto1=nca.header.getCryptoType()
							crypto2=nca.header.getCryptoType2()
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:
								masterKeyRev=crypto1
							decKey = Keys.decryptTitleKey(tkey, Keys.getMasterKeyIndex(int(masterKeyRev)))
						for i in range(len(files_list)):
							if str(nca._path) == files_list[i][0]:
								offset=files_list[i][1]
								#print(offset)
								break
						try:
							fp=open(str(self._path), 'rb')
							nca3=NCA3(fp,int(offset),str(nca._path),decKey)
							feed+=nca3.print_npdm()
							fp.close();
							feed+='</span></strong></p>'
							return feed
						except BaseException as e:
							#Print.error('Exception: ' + str(e))
							nca.rewind()
							for fs in nca.sectionFilesystems:
								#print(fs.fsType)
								#print(fs.cryptoType)
								if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
									nca.seek(0)
									ncaHeader = NcaHeader()
									ncaHeader.open(MemoryFile(nca.read(0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
									ncaHeader.seek(0)
									fs.rewind()
									pfs0=fs
									sectionHeaderBlock = fs.buffer
									nca.seek(fs.offset)
									pfs0Offset=fs.offset
									pfs0Header = nca.read(0x10*30)
									mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
									data = mem.read();
									#Hex.dump(data)
									head=data[0:4]
									n_files=(data[4:8])
									n_files=int.from_bytes(n_files, byteorder='little')
									st_size=(data[8:12])
									st_size=int.from_bytes(st_size, byteorder='little')
									junk=(data[12:16])
									offset=(0x10 + n_files * 0x18)
									stringTable=(data[offset:offset+st_size])
									stringEndOffset = st_size
									headerSize = 0x10 + 0x18 * n_files + st_size
									#print(head)
									if head!=b'PFS0':
										feed=self.html_feed(feed,2,message=str('- Error decrypting npdm'))
										continue
									#print(str(n_files))
									#print(str(st_size))
									#print(str((stringTable)))
									files_list=list()
									for i in range(n_files):
										i = n_files - i - 1
										pos=0x10 + i * 0x18
										offset = data[pos:pos+8]
										offset=int.from_bytes(offset, byteorder='little')
										size = data[pos+8:pos+16]
										size=int.from_bytes(size, byteorder='little')
										nameOffset = data[pos+16:pos+20] # just the offset
										nameOffset=int.from_bytes(nameOffset, byteorder='little')
										name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
										stringEndOffset = nameOffset
										junk2 = data[pos+20:pos+24] # junk data
										#print(name)
										#print(offset)
										#print(size)
										files_list.append([name,offset,size])
									files_list.reverse()
									#print(files_list)
									for i in range(len(files_list)):
										if files_list[i][0] == 'main.npdm':
											off1=files_list[i][1]+pfs0Offset+headerSize
											nca.seek(off1)
											np=nca.read(files_list[i][2])
											mem = MemoryFile(np, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = off1)
											data = mem.read();
											#Hex.dump(data)
											inmemoryfile = io.BytesIO(data)
											npdm = NPDM(inmemoryfile)
											n=npdm.__str__()
											feed+=n
											feed+='</span></strong></p>'
											return feed
								break
							return feed
		except:
			feed=self.html_feed(feed,2,message=str('- Error decrypting npdm'))
		return feed

	def read_buildid(self,target=None):
		iscorrect=False;
		ModuleId='';BuildID8='';BuildID16=''
		files_list=sq_tools.ret_nsp_offsets(self._path)
		# print(files_list)
		for nca in self:
			if type(nca) == Fs.Nca:
				if 	str(nca.header.contentType) == 'Content.PROGRAM':
					if target==None:
						target=str(nca._path)
					if str(nca._path)==target:
						if nca.header.getRightsId() == 0:
							decKey=nca.header.titleKeyDec
						if nca.header.getRightsId() != 0:
							correct, tkey = self.verify_nca_key(str(nca._path))
							if correct == True:
								crypto1=nca.header.getCryptoType()
								crypto2=nca.header.getCryptoType2()
								if crypto2>crypto1:
									masterKeyRev=crypto2
								if crypto2<=crypto1:
									masterKeyRev=crypto1
								decKey = Keys.decryptTitleKey(tkey, Keys.getMasterKeyIndex(int(masterKeyRev)))
							else:
								decKey=nca.header.titleKeyDec
						for i in range(len(files_list)):
							if str(nca._path) == files_list[i][0]:
								offset=files_list[i][1]
								# print(offset)
								break
						nca.rewind()
						for fs in nca.sectionFilesystems:
							#print(fs.fsType)
							#print(fs.cryptoType)
							if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
								nca.seek(0)
								ncaHeader = NcaHeader()
								ncaHeader.open(MemoryFile(nca.read(0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
								ncaHeader.seek(0)
								fs.rewind()
								pfs0=fs
								sectionHeaderBlock = fs.buffer
								nca.seek(fs.offset)
								pfs0Offset=fs.offset
								pfs0Header = nca.read(0x10*30)
								mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
								data = mem.read();
								#Hex.dump(data)
								head=data[0:4]
								n_files=(data[4:8])
								n_files=int.from_bytes(n_files, byteorder='little')
								st_size=(data[8:12])
								st_size=int.from_bytes(st_size, byteorder='little')
								junk=(data[12:16])
								offset=(0x10 + n_files * 0x18)
								stringTable=(data[offset:offset+st_size])
								stringEndOffset = st_size
								headerSize = 0x10 + 0x18 * n_files + st_size
								#print(head)
								if head!=b'PFS0':
									continue
								#print(str(n_files))
								#print(str(st_size))
								#print(str((stringTable)))
								files_list=list()
								for i in range(n_files):
									i = n_files - i - 1
									pos=0x10 + i * 0x18
									offset = data[pos:pos+8]
									offset=int.from_bytes(offset, byteorder='little')
									size = data[pos+8:pos+16]
									size=int.from_bytes(size, byteorder='little')
									nameOffset = data[pos+16:pos+20] # just the offset
									nameOffset=int.from_bytes(nameOffset, byteorder='little')
									name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
									stringEndOffset = nameOffset
									junk2 = data[pos+20:pos+24] # junk data
									#print(name)
									#print(offset)
									#print(size)
									files_list.append([name,offset,size])
								files_list.reverse()
								#print(files_list)
								for i in range(len(files_list)):
									if files_list[i][0] == 'main':
										off1=files_list[i][1]+pfs0Offset+headerSize
										nca.seek(off1)
										np=nca.read(0x60)
										mem = MemoryFile(np, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = off1)
										magic=mem.read(0x4)
										if magic==b'NSO0':
											mem.seek(0x40)
											data = mem.read(0x20);
											ModuleId=(str(hx(data)).upper())[2:-1]
											BuildID8=(str(hx(data[:8])).upper())[2:-1]
											BuildID16=(str(hx(data[:16])).upper())[2:-1]
											iscorrect=True;
										break
							break
		if iscorrect==False:
			try:
				from nutFS.Nca import Nca as nca3type
				for nca in self:
					if type(nca) == Fs.Nca:
						if 	str(nca.header.contentType) == 'Content.PROGRAM':
							if target==None or str(nca._path)==target:
								nca3type=Nca(nca)
								nca3type._path=nca._path
								ModuleId=str(nca3type.buildId)
								BuildID8=ModuleId[:8]
								BuildID16=ModuleId[:16]
			except:
				ModuleId='';BuildID8='';BuildID16='';
		return ModuleId,BuildID8,BuildID16


	def extract_nca(self,ofolder,files_list,buffer=32768):
		for nca in self:
			tk=None;skip=False
			if type(nca) == Nca:
				for fs in nca.sectionFilesystems:
					if fs.cryptoType == Type.Crypto.BKTR:
						skip=True
						break
				if nca.header.getRightsId() != 0:
					correct, tkey = self.verify_nca_key(str(nca._path))
					if correct == True:
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:
							masterKeyRev=crypto1
						tk = Keys.decryptTitleKey(tkey, Keys.getMasterKeyIndex(int(masterKeyRev)))
				else:
					tk=nca.header.titleKeyDec
			if skip == False:
				if type(nca) == Nca:
					ncaname =  str(nca._path)[:-4]+'_nca'
					ncafolder = os.path.join(ofolder,ncaname)
					ncaname2 =  str(nca._path)
					PN = os.path.join(ofolder,ncaname2)
					if not os.path.exists(ncafolder):
						os.makedirs(ncafolder)
					for i in range(len(files_list)):
						if str(nca._path) == files_list[i][0]:
							offset=files_list[i][1]
							break
					#t = tqdm(total=nca.size, unit='B', unit_scale=True, leave=False)
					try:
						fp=open(str(self._path), 'rb')
						nca3=NCA3(fp,int(offset),str(nca._path),tk,buffer)
						nca3.extract_conts(ncafolder, disp=True)
						fp.close()
					except:
						#Print.error('Exception: ' + str(e))
						if nca.size<int(1073725440):
							try:
								nca.rewind()
								inmemoryfile = io.BytesIO(nca.read())
								nca3=NCA3(inmemoryfile,0,str(nca._path),tk,buffer)
								nca3.extract_conts(ncafolder, disp=True)
							except BaseException as e:
								#Print.error('Exception: ' + str(e))
								try:
									with open(str(self._path), 'rb') as f:
										f.seek(offset)
										inmemoryfile = io.BytesIO(f.read(files_list[i][3]))
										nca3=NCA3(inmemoryfile,int(0),str(nca._path),tk,buffer)
										nca3.extract_conts(ncafolder, disp=True)
								except BaseException as e:
									#Print.error('Exception: ' + str(e))
									t = tqdm(total=nca.size, unit='B', unit_scale=True, leave=False)
									t.write(str(nca._path)+' needs to be pre-extracted')
									outnca=open(str(PN), 'w+b')
									nca.rewind()
									try:
										for data in iter(lambda: nca.read(int(buffer)), ""):
											outnca.write(data)
											t.update(len(data))
											outnca.flush()
											if not data:
												outnca.close()
												t.close()
												break
										with open(str(PN), 'rb') as f:
											nca3=NCA3(f,int(0),str(nca._path),tk,buffer)
											nca3.extract_conts(ncafolder, disp=True)
										try:
											os.remove(str(PN))
										except:
											pass
									except BaseException as e:
										Print.error('Exception: ' + str(e))
										outnca.close()
										t.close()
										try:
											os.remove(str(PN))
										except:
											pass
										continue
						else:
							t = tqdm(total=nca.size, unit='B', unit_scale=True, leave=False)
							t.write(str(nca._path)+' needs to be pre-extracted')
							outnca=open(str(PN), 'w+b')
							nca.rewind()
							try:
								for data in iter(lambda: nca.read(int(buffer)), ""):
									outnca.write(data)
									t.update(len(data))
									outnca.flush()
									if not data:
										outnca.close()
										t.close()
										break
								with open(str(PN), 'rb') as f:
									nca3=NCA3(f,int(0),str(nca._path),tk,buffer)
									nca3.extract_conts(ncafolder, disp=True)
								try:
									os.remove(str(PN))
								except:
									pass
							except BaseException as e:
								Print.error('Exception: ' + str(e))
								outnca.close()
								t.close()
								try:
									os.remove(str(PN))
								except:
									pass
								continue

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
							fp.close()
							break

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
							fp.close()
							break

	def test(self):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.PROGRAM':
					masterKeyRev = nca.header.getCryptoType2()
					encKeyBlock = nca.header.getKeyBlock()
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
					crypto = aes128.AESECB(key)
					decKeyBlock = crypto.decrypt(encKeyBlock[:16])
					print ("- Encrypted titlekey: "+str(hx(decKeyBlock)))
					titleKeyEnc = Keys.encryptTitleKey(decKeyBlock, Keys.getMasterKeyIndex(masterKeyRev))
					print ("- Restored titlekey: "+str(hx(titleKeyEnc)))
					'''nca.rewind()
					sig1=nca.read(0x100)
					sig2=nca.read(0x100)
					val=nca.read(0x200)
					pub = 0x10001
					mod='BFBE406CF4A780E9F07D0C99611D772F96BC4B9E58381B03ABB175499F2B4D5834B005A37522BE1A3F0373AC7068D116B904465EB707912F078B26DEF60007B2B451F80D0A5E58ADEBBC9AD649B964EFA782B5CF6D7013B00F85F6A908AA4D676687FA89FF7590181E6B3DE98A68C92604D980CE3F5E92CE01FF063BF2C1A90CCE026F16BC92420A4164CD52B6344DAEC02EDEA4DF27683CC1A060AD43F3FC86C13E6C46F77C299FFAFDF0E3CE64E735F2F656566F6DF1E242B08340A5C3202BCC9AAECAED4D7030A8701C70FD1363290279EAD2A7AF3528321C7BE62F1AAA407E328C2742FE8278EC0DEBE6834B6D8104401A9E9A67F67229FA04F09DE4F403'
					mod= bytes.fromhex(mod)
					mod = int(hx(mod), 16)
					crypto = pss.new(RSA.construct([mod, pub]))
					print (crypto)
					sha = newsha.new(val)
					print (sha)
					crypto.sign(sha)
					print(sig1)
					print(crypto)'''




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
							fp.close()
							break

	def copy_nca_pdata(self,ofolder,buffer):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.PUBLIC_DATA':
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
							fp.close()
							break
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
						fp.close()
						break

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
				if nca.header.getRightsId() != 0:
					if nca.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(nca._path)} - {nca.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.getCryptoType2() == 0:
						if nca.header.getCryptoType() == 2:
							masterKeyRev = 2
							break

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
		ticket = self.ticket()
		for nca in self:
			if type(nca) == Nca:
				crypto1=nca.header.getCryptoType()
				crypto2=nca.header.getCryptoType2()
				if crypto1 == 2:
					if crypto1 > crypto2:
						masterKeyRev=nca.header.getCryptoType()
					else:
						masterKeyRev=nca.header.getCryptoType2()
				else:
					masterKeyRev=nca.header.getCryptoType2()
				if nca.header.getRightsId() != 0:
					break


		titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
		rightsId = ticket.getRightsId()
		titleKey = ticket.getTitleKeyBlock().to_bytes(16, byteorder='big')

		return titleKeyDec


	def pack(self, files,buffer,fat,fx):
		if not self.path:
			return False
		indent = 1
		tabs = '\t' * indent

		hd = self.generateHeader(files)

		totSize = len(hd) + sum(os.path.getsize(file) for file in files)
		if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
			Print.info('\t\tRepack %s is already complete!' % self.path)
			return
		outfile=self.path
		if totSize <= 4294901760:
			fat="exfat"
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294901760)
			index=0
			outfile=outfile[:-1]+str(index)
		if fx=="folder" and fat=="fat32":
			output_folder ="archfolder"
			dir_path = os.path.dirname(os.path.realpath(self.path))
			output_folder = os.path.join(dir_path, output_folder)
			outfile = os.path.join(output_folder, "00")
			if not os.path.exists(output_folder):
				os.makedirs(output_folder)
		c=0
		Print.info('Generating nsp:')
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing header...')

		outf = open(outfile, 'wb')
		outf.write(hd)
		t.update(len(hd))
		c=c+len(hd)
		block=4294901760
		for file in files:
			if file.endswith('.nca'):
				nca =Fs.Nca(file, 'r+b')
				nca.rewind()
				if	nca.header.getgamecard() == 1:
					nca.header.setgamecard(0)
				nca.flush()
				nca.close()
			t.write(tabs+'- Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					data = inf.read(int(buffer))
					outf.write(data)
					t.update(len(data))
					c=c+len(data)
					outf.flush()
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

	def html_feed(self,feed='',style=1,message=''):
		if feed==None:
			feed=''
		if message==None:
			message=''
		if style==1:
			feed+='<p style="font-size: 14px; justify;text-justify: inter-word;"><strong>{}</strong></p>'.format(message)
			return feed
		if style==2:
			feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 2vh"><strong>{}</strong></p>'.format(message)
			return feed
		if style==3:
			feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>{} </strong><span>{}</span></li>'.format(message[0],message[1])
			return feed
		if style==4:
			feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>{} </strong><span>{}. </span><strong>{} </strong><strong>{}</strong></li>'.format(message[0],message[1],message[2],message[3])
			return feed
		if style==5:
			feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 2vh;text-indent:5vh";><strong style="text-indent:5vh;">{}</strong></p>'.format(message)
			return feed
		if style==6:
			feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;";><strong>{}</strong></p>'.format(message)
			return feed
		if style==7:
			feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;";><strong>{}</strong>{}</p>'.format(message[0],message[1])
		if style==8:
			feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>[{}] {} </strong><span>{}. </span><strong>{} </strong><strong>{}</strong></li>'.format(message[3],message[0],message[1],message[4],message[5])
			return feed

#ADVANCED FILE-LIST
	def  adv_file_list(self):
		contentlist=list()
		feed='';ncadb={};size_pr=0
		for nca in self:
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
								reqtag='RequiredSystemVersion: '
								tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
								if isdemo == 1:
									content_type='Demo Update'
								if isdemo == 2:
									content_type='RetailInteractiveDisplay Update'
							if content_type_cnmt == 'AddOnContent':
								content_type='DLC'
								reqtag='RequiredUpdateNumber: '
								tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
							if content_type_cnmt == 'Application':
								content_type='Game or Application'
								reqtag='RequiredSystemVersion: '
								tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
								if isdemo == 1:
									content_type='Demo'
								if isdemo == 2:
									content_type='RetailInteractiveDisplay'
							cnmt.rewind()
							cnmt.seek(0x20+offset)
							titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
							titleid2 = titleid2[2:-1]
							original_ID2 = str(hx(original_ID.to_bytes(8, byteorder='big')))
							original_ID2 = original_ID2[2:-1]
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
							programSDKversion,dataSDKversion=self.getsdkvertit(titleid2)
							sdkversion=nca.get_sdkversion()
							MinRSV=sq_tools.getMinRSV(keygen,min_sversion)
							FW_rq=sq_tools.getFWRangeKG(keygen)
							RSV_rq=sq_tools.getFWRangeRSV(min_sversion)
							RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)
							feed=self.html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
							feed=self.html_feed(feed,2,message=str("- Titleinfo:"))
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							if content_type_cnmt != 'AddOnContent':
								message=["Name:",tit_name];feed=self.html_feed(feed,3,message)
								message=["Editor:",editor];feed=self.html_feed(feed,3,message)
								message=["Display Version:",str(ediver)];feed=self.html_feed(feed,3,message)
								message=["Meta SDK version:",sdkversion];feed=self.html_feed(feed,3,message)
								message=["Program SDK version:",programSDKversion];feed=self.html_feed(feed,3,message)
								suplangue=str((', '.join(SupLg)))
								message=["Supported Languages:",suplangue];feed=self.html_feed(feed,3,message)
								message=["Content type:",content_type];feed=self.html_feed(feed,3,message)
								v_number=str(v_number)
								data='{} -> {} ({})'.format(version,content_type_cnmt,v_number)
								message=["Version:",data];feed=self.html_feed(feed,3,message=message);
							if content_type_cnmt == 'AddOnContent':
								if tit_name != "DLC":
									message=["Name:",tit_name];feed=self.html_feed(feed,3,message)
									message=["Editor:",editor];feed=self.html_feed(feed,3,message)
								message=["Content type:","DLC"];feed=self.html_feed(feed,3,message)
								DLCnumb=str(titleid2)
								DLCnumb="0000000000000"+DLCnumb[-3:]
								DLCnumb=bytes.fromhex(DLCnumb)
								DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
								DLCnumb=int(DLCnumb)
								message=["DLC number:",str(str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')')];feed=self.html_feed(feed,3,message)
								message=["DLC version Number:",str( version+' -> '+"Version"+' ('+str(v_number)+')')];feed=self.html_feed(feed,3,message)
								message=["Meta SDK version:",sdkversion];feed=self.html_feed(feed,3,message)
								message=["Data SDK version:",dataSDKversion];feed=self.html_feed(feed,3,message)
								if SupLg !='':
									suplangue=str((', '.join(SupLg)))
									message=["Supported Languages:",suplangue];feed=self.html_feed(feed,3,message)
							feed+='</ul>'
							feed=self.html_feed(feed,2,message=str("- Required Firmware:"))
							incl_Firm=DBmodule.FWDB.detect_xci_fw(self._path,False)
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							message=["Included Firmware:",str(str(incl_Firm))];feed=self.html_feed(feed,3,message)
							if content_type_cnmt == 'AddOnContent':
								if v_number == 0:
									message=["Required game version:",str(str(min_sversion)+' -> '+"Application"+' ('+str(RS_number)+')')];feed=self.html_feed(feed,3,message)
									message=["Required game version:",str(str(min_sversion)+' -> '+"Application"+' ('+str(RS_number)+')')];feed=self.html_feed(feed,3,message)
								if v_number > 0:
									message=["Required game version:",str(str(min_sversion)+' -> '+"Patch"+' ('+str(RS_number)+')')];feed=self.html_feed(feed,3,message)

							else:
								message=[reqtag,(str(min_sversion)+" -> " +RSV_rq)];feed=self.html_feed(feed,3,message)
							message=['Encryption (keygeneration):',(str(keygen)+" -> " +FW_rq)];feed=self.html_feed(feed,3,message)
							if content_type_cnmt != 'AddOnContent':
								message=['Patchable to:',(str(MinRSV)+" -> " + RSV_rq_min)];feed=self.html_feed(feed,3,message)

							else:
								message=['Patchable to:',('DLC -> no RSV to patch')];feed=self.html_feed(feed,3,message)
							feed+='</ul>'
							ncalist = list()
							ncasize = 0
							feed=self.html_feed(feed,2,message=str("- Nca files (Non Deltas):"))
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							for i in range(content_entries):
								vhash = cnmt.read(0x20)
								NcaId = cnmt.read(0x10)
								size = cnmt.read(0x6)
								ncatype = cnmt.read(0x1)
								ncatype = int.from_bytes(ncatype, byteorder='little')
								IdOffset = cnmt.read(0x1)
								IdOffset = int.from_bytes(IdOffset, byteorder='little', signed=True)
								#Print.info(str(ncatype))
								if ncatype != 6:
									nca_name=str(hx(NcaId))
									nca_name=nca_name[2:-1]+'.nca'
									if titleid2.endswith('800'):
										showID=str(original_ID2).upper()
									else:
										showID=str(titleid2).upper()
									if IdOffset>0:
										showID=showID[:-1]+str(IdOffset)
									ncadb[nca_name]=[showID,version,v_number]
									showID=showID+' v'+version
									s1=0;s1,feed=self.print_nca_by_title(nca_name,ncatype,showID,feed)
									ncasize=ncasize+s1
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
							showID=str(titleid2).upper()
							ncadb[nca_name]=[showID,version,v_number]
							showID=showID+' v'+version
							s1=0;s1,feed=self.print_nca_by_title(nca_meta,0,showID,feed)
							ncasize=ncasize+s1
							size1=ncasize
							size_pr=sq_tools.getSize(ncasize)
							feed+='</ul>'
							feed=self.html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
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
										feed=self.html_feed(feed,2,message=('- Nca files (Deltas):'))
										feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
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
									IdOffset = cnmt.read(0x1)
									IdOffset = int.from_bytes(IdOffset, byteorder='little', signed=True)
									if ncatype == 6:
										nca_name=str(hx(NcaId))
										nca_name=nca_name[2:-1]+'.nca'
										if titleid2.endswith('800'):
											showID=str(original_ID2).upper()
										else:
											showID=str(titleid2).upper()
										if IdOffset>0:
											showID=showID[:-1]+str(IdOffset)
										ncadb[nca_name]=[showID,version,v_number]
										showID=showID+' v'+version
										s1=0;s1,feed=self.print_nca_by_title(nca_name,ncatype,showID,feed)
										ncasize=ncasize+s1
								size2=ncasize
								size_pr=sq_tools.getSize(ncasize)
								feed+='</ul>'
								feed=self.html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
							if self.actually_has_other(titleid2,ncalist)=="true":
								feed=self.html_feed(feed,2,message=('- Other types of files:'))
								feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
								othersize=0;os1=0;os2=0;os3=0
								os1,feed=self.print_xml_by_title(ncalist,contentlist,feed)
								os2,feed=self.print_tac_by_title(titleid2,contentlist,feed)
								os3,feed=self.print_jpg_by_title(ncalist,contentlist,feed)
								othersize=othersize+os1+os2+os3
								size3=othersize
								size_pr=sq_tools.getSize(othersize)
								feed+='</ul>'
								feed=self.html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
					finalsize=size1+size2+size3
		size_pr=sq_tools.getSize(finalsize)
		feed=self.html_feed(feed,2,message=('FULL CONTENT TOTAL SIZE: '+size_pr))
		feed=self.printnonlisted(contentlist,feed)
		feed=self.print_BuildIDs(ncadb,feed)
		return feed


	def print_nca_by_title(self,nca_name,ncatype,showID,feed):
		tab="\t";
		size=0
		ncz_name=nca_name[:-1]+'z'
		for nca in self:
			filename = str(nca._path)
			if type(nca) == Nca:
				if filename == nca_name:
					size=nca.header.size
					size_pr=sq_tools.getSize(size)
					content=str(nca.header.contentType)
					content=content[8:]+": "
					ncatype=sq_tools.getTypeFromCNMT(ncatype)
					if ncatype != "Meta: ":
						message=[ncatype,str(filename),'TitleID:',showID,'Size',size_pr];feed=self.html_feed(feed,8,message)
					else:
						message=[ncatype,str(filename),'TitleID:',showID,'Size',size_pr];feed=self.html_feed(feed,8,message)
					return size,feed
			elif filename == ncz_name:
				ncztype=Nca(nca)
				ncztype._path=nca._path
				size=ncztype.header.size
				size_pr=sq_tools.getSize(size)
				content=str(ncztype.header.contentType)
				content=content[8:]+": "
				ncatype=sq_tools.getTypeFromCNMT(ncatype)
				if ncatype != "Meta: ":
					message=[ncatype,str(filename),'TitleID:',showID,'Size',size_pr];feed=self.html_feed(feed,8,message)
				else:
					message=[ncatype,str(filename),'TitleID:',showID,'Size',size_pr];feed=self.html_feed(feed,8,message)
				return size,feed
		return size,feed
	def print_xml_by_title(self,ncalist,contentlist,feed=''):
		tab="\t";
		size2return=0
		for file in self:
			if file._path.endswith('.xml'):
				size=file.size
				size_pr=sq_tools.getSize(size)
				filename =  str(file._path)
				xml=filename[:-4]
				if xml in ncalist:
					message=['XML:',str(filename),'Size:',size_pr];feed=self.html_feed(feed,4,message)
					contentlist.append(filename)
					size2return=size+size2return
		return size2return,feed
	def print_tac_by_title(self,titleid,contentlist,feed=''):
		tab="\t";
		size2return=0
		for ticket in self:
			if type(ticket) == Ticket:
				size=ticket.size
				size_pr=sq_tools.getSize(size)
				filename =  str(ticket._path)
				tik=filename[:-20]
				if tik == titleid:
					message=['Ticket:',str(filename),'Size:',size_pr];feed=self.html_feed(feed,4,message)
					contentlist.append(filename)
					size2return=size+size2return
		for cert in self:
			if cert._path.endswith('.cert'):
				size=cert.size
				size_pr=sq_tools.getSize(size)
				filename = str(cert._path)
				cert_id =filename[:-21]
				if cert_id == titleid:
					message=['Cert:',str(filename),'Size:',size_pr];feed=self.html_feed(feed,4,message)
					contentlist.append(filename)
					size2return=size+size2return
		return size2return,feed
	def print_jpg_by_title(self,ncalist,contentlist,feed=''):
		size2return=0
		tab="\t";
		for file in self:
			if file._path.endswith('.jpg'):
				size=file.size
				size_pr=sq_tools.getSize(size)
				filename =  str(file._path)
				jpg=filename[:32]
				if jpg in ncalist:
					message=['JPG:',str(filename),'Size:',size_pr];feed=self.html_feed(feed,4,message)
					contentlist.append(filename)
					size2return=size+size2return
		return size2return,feed
	def actually_has_deltas(self,ncalist):
		vfragment="false"
		for nca in self:
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
		for file in self:
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
	def printnonlisted(self,contentlist,feed=''):
		tab="\t";
		list_nonlisted="false"
		for file in self:
			filename =  str(file._path)
			if not filename in contentlist:
				list_nonlisted="true"
		if list_nonlisted == "true":
			feed=self.html_feed(feed,2,'- Files not linked to content in nsp:')
			totsnl=0
			for file in self:
				filename =  str(file._path)
				nczname= str(file._path)[:-1]+'z'
				if not filename in contentlist and not nczname in contentlist:
					totsnl=totsnl+file.size
					size_pr=sq_tools.getSize(file.size)
					message=['OTHER:',str(filename),'Size:',size_pr];feed=self.html_feed(feed,4,message)
			size_pr=sq_tools.getSize(totsnl)
			feed=self.html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
		return feed

	def print_BuildIDs(self,ncadb,feed=''):
		c=0
		for nca in self:
			size1=0;size2=0;size3=0
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.PROGRAM':
					target=str(nca._path)
					tit=str(nca.header.titleId).upper()
					entry=ncadb[target]
					ModuleId,BuildID8,BuildID16=self.read_buildid(target)
					ModuleId=sq_tools.trimm_module_id(ModuleId)
					if ModuleId!="":
						if c==0:
							feed=self.html_feed(feed,2,'EXEFS DATA:')
							c+=1
						feed=self.html_feed(feed,2,f'[Title: {tit} v{entry[1]}]')
						message=[f'BuildID8:',str(BuildID8)];feed=self.html_feed(feed,3,message)
						message=[f'BuildID:',str(ModuleId)];feed=self.html_feed(feed,3,message)
		return feed

#ADVANCED FILE-LIST
	def  adv_content_list(self):
		feed=''
		applist=list();	applist_ID=list()
		patchlist=list(); patchlist_ID=list()
		dlclist=list();	dlclist_ID=list()
		for nca in self:
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
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
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
		if len(applist) != 0:
			for i in range(len(applist)):
				tid=applist[i][1]
				message='------------------------------------------------';print(message);feed+=message+'\n'
				message='BASE CONTENT ID: ' + str(tid);print(message);feed+=message+'\n'
				message='------------------------------------------------';print(message);feed+=message+'\n'
				message='Name: '+applist[i][3];print(message);feed+=message+'\n'
				message='Editor: '+applist[i][4];print(message);feed+=message+'\n'
				message='------------------------------------------------';print(message);feed+=message+'\n'
				message=applist[i][1]+" [BASE]"+" v"+applist[i][2];print(message);feed+=message+'\n'
				cupd=0
				for j in range(len(patchlist)):
					if tid == patchlist[j][1]:
						v=patchlist[j][2]
						v_number=str(int(int(v)/65536))
						message=patchlist[j][3]+" [UPD]"+" v"+patchlist[j][2]+" -> Patch("+v_number+")";print(message);feed+=message+'\n'
						cupd+=1
						patch_called.append(patchlist[j])
				cdlc=0
				for k in range(len(dlclist)):
					if tid == dlclist[k][1]:
						message=dlclist[k][3]+" [DLC "+str(dlclist[k][4])+"]"+" v"+dlclist[k][2];print(message);feed+=message+'\n'
						cdlc+=1
						dlc_called.append(dlclist[k])
				message='------------------------------------------------';print(message);feed+=message+'\n'
				message='CONTENT INCLUDES: 1 BASEGAME '+str(cupd)+' UPDATES '+str(cdlc)+' DLCS';print(message);feed+=message+'\n'
				message='------------------------------------------------';print(message);feed+=message+'\n'
				if len(patchlist) != len(patch_called):
					message='------------------------------------------------';print(message);feed+=message+'\n'
					message='ORPHANED UPDATES:';print(message);feed+=message+'\n'
					message='------------------------------------------------';print(message);feed+=message+'\n'
					for j in range(len(patchlist)):
						if patchlist[j] not in patch_called:
							v=patchlist[j][2]
							v_number=str(int(int(v)/65536))
							message=patchlist[j][3]+" [UPD]"+" v"+patchlist[j][2]+" -> Patch("+v_number+")";print(message);feed+=message+'\n'
				if len(dlclist) != len(dlc_called):
					message='------------------------------------------------';print(message);feed+=message+'\n'
					message='ORPHANED DLCS:';print(message);feed+=message+'\n'
					message='------------------------------------------------';print(message);feed+=message+'\n'
					for k in range(len(dlclist)):
						if dlclist[k] not in dlc_called:
							message=dlclist[k][3]+" [DLC "+str(dlclist[k][4])+"]"+" v"+dlclist[k][2];print(message);feed+=message+'\n'
		else:
			message='This option is currently meant for multicontent, that includes at least a base game';print(message);feed+=message+'\n'
		return feed

#READ NACP FILE WITHOUT EXTRACTION
	def read_nacp(self,feed='',gui=False):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					titleid2=nca.header.titleId
					feed=self.html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
					offset=nca.get_nacp_offset()
					for f in nca:
						f.seek(offset)
						nacp = ChromeNacp()
						feed=nacp.par_getNameandPub(f.read(0x300*15),feed,gui)
						feed=self.html_feed(feed,2,message=str("Nacp Flags:"))
						feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
						f.seek(offset+0x3000)
						feed=nacp.par_Isbn(f.read(0x24),feed)
						f.seek(offset+0x3025)
						feed=nacp.par_getStartupUserAccount(f.readInt8('little'),feed)
						feed=nacp.par_getUserAccountSwitchLock(f.readInt8('little'),feed)
						feed=nacp.par_getAddOnContentRegistrationType(f.readInt8('little'),feed)
						feed=nacp.par_getContentType(f.readInt8('little'),feed)
						f.seek(offset+0x3030)
						feed=nacp.par_getParentalControl(f.readInt8('little'),feed)
						f.seek(offset+0x3034)
						feed=nacp.par_getScreenshot(f.readInt8('little'),feed)
						feed=nacp.par_getVideoCapture(f.readInt8('little'),feed)
						feed=nacp.par_dataLossConfirmation(f.readInt8('little'),feed)
						feed=nacp.par_getPlayLogPolicy(f.readInt8('little'),feed)
						f.seek(offset+0x3038)
						feed=nacp.par_getPresenceGroupId(f.readInt64('little'),feed)
						feed+='</ul>'
						f.seek(offset+0x3040)
						listages=list()
						feed=self.html_feed(feed,2,message=str("Age Ratings:"))
						feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
						for i in range(12):
							feed=nacp.par_getRatingAge(f.readInt8('little'),i,feed)
						feed+='</ul>'
						f.seek(offset+0x3060)
						try:
							feed=self.html_feed(feed,2,message=str("Nacp Atributes:"))
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							feed=nacp.par_getDisplayVersion(f.read(0xF),feed)
							f.seek(offset+0x3070)
							feed=nacp.par_getAddOnContentBaseId(f.readInt64('little'),feed)
							f.seek(offset+0x3078)
							feed=nacp.par_getSaveDataOwnerId(f.readInt64('little'),feed)
							f.seek(offset+0x3080)
							feed=nacp.par_getUserAccountSaveDataSize(f.readInt64('little'),feed)
							f.seek(offset+0x3088)
							feed=nacp.par_getUserAccountSaveDataJournalSize(f.readInt64('little'),feed)
							f.seek(offset+0x3090)
							feed=nacp.par_getDeviceSaveDataSize(f.readInt64('little'),feed)
							f.seek(offset+0x3098)
							feed=nacp.par_getDeviceSaveDataJournalSize(f.readInt64('little'),feed)
							f.seek(offset+0x30A0)
							feed=nacp.par_getBcatDeliveryCacheStorageSize(f.readInt64('little'),feed)
							f.seek(offset+0x30A8)
							feed=nacp.par_getApplicationErrorCodeCategory(f.read(0x07),feed)
							f.seek(offset+0x30B0)
							feed=nacp.par_getLocalCommunicationId(f.readInt64('little'),feed)
							f.seek(offset+0x30F0)
							feed=nacp.par_getLogoType(f.readInt8('little'),feed)
							feed=nacp.par_getLogoHandling(f.readInt8('little'),feed)
							feed=nacp.par_getRuntimeAddOnContentInstall(f.readInt8('little'),feed)
							f.seek(offset+0x30F6)
							feed=nacp.par_getCrashReport(f.readInt8('little'),feed)
							feed=nacp.par_getHdcp(f.readInt8('little'),feed)
							feed=nacp.par_getSeedForPseudoDeviceId(f.readInt64('little'),feed)
							f.seek(offset+0x3100)
							feed=nacp.par_getBcatPassphrase(f.read(0x40),feed)
							f.seek(offset+0x3148)
							feed=nacp.par_UserAccountSaveDataSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3150)
							feed=nacp.par_UserAccountSaveDataJournalSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3158)
							feed=nacp.par_getDeviceSaveDataSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3160)
							feed=nacp.par_getDeviceSaveDataJournalSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3168)
							feed=nacp.par_getTemporaryStorageSize(f.readInt64('little'),feed)
							feed=nacp.par_getCacheStorageSize(f.readInt64('little'),feed)
							f.seek(offset+0x3178)
							feed=nacp.par_getCacheStorageJournalSize(f.readInt64('little'),feed)
							feed=nacp.par_getCacheStorageDataAndJournalSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3188)
							feed=nacp.par_getCacheStorageIndexMax(f.readInt64('little'),feed)
							f.seek(offset+0x3188)
							feed=nacp.par_getPlayLogQueryableApplicationId(f.readInt64('little'),feed)
							f.seek(offset+0x3210)
							feed=nacp.par_getPlayLogQueryCapability(f.readInt8('little'),feed)
							feed=nacp.par_getRepair(f.readInt8('little'),feed)
							feed=nacp.par_getProgramIndex(f.readInt8('little'),feed)
							feed=nacp.par_getRequiredNetworkServiceLicenseOnLaunch(f.readInt8('little'),feed)
							feed+='</ul>'
						except BaseException as e:
							Print.error('Exception: ' + str(e))
							feed+='</ul>'
							continue
		return feed


#READ CNMT FILE WITHOUT EXTRACTION
	def read_cnmt(self):
		feed=''
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					titleid2=nca.header.titleId
					feed=self.html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
					for f in nca:
						for cnmt in f:
							nca.rewind()
							f.rewind()
							cnmt.rewind()
							titleid=cnmt.readInt64()
							titleversion = cnmt.read(0x4)
							type_n = cnmt.read(0x1)
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
							min_sversion=cnmt.readInt32()
							length_of_emeta=cnmt.readInt32()
							feed=self.html_feed(feed,6,message=str(str(cnmt._path)))
							message=["Titleid:",(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
							message=["Version:",(str(int.from_bytes(titleversion, byteorder='little')))];feed=self.html_feed(feed,3,message)
							message=["Cnmt Type:",(sq_tools.cnmt_type(type_n))];feed=self.html_feed(feed,3,message)
							message=["Table offset:",(str(hx((offset+0x20).to_bytes(2, byteorder='big'))))];feed=self.html_feed(feed,3,message)
							message=["Number of content:",(str(content_entries))];feed=self.html_feed(feed,3,message)
							message=["Number of meta entries:",(str(meta_entries))];feed=self.html_feed(feed,3,message)
							message=["Application id\Patch id:",((str(hx(original_ID.to_bytes(8, byteorder='big')))[2:-1]).upper())];feed=self.html_feed(feed,3,message)

							content_name=str(cnmt._path)
							content_name=content_name[:-22]
							if content_name == 'AddOnContent':
								message=["RequiredUpdateNumber:",(str(min_sversion))];feed=self.html_feed(feed,3,message)
							if content_name != 'AddOnContent':
								message=["RequiredSystemVersion:",(str(min_sversion))];feed=self.html_feed(feed,3,message)
							message=["Length of exmeta:",(str(min_sversion))];feed=self.html_feed(feed,3,message)
							cnmt.rewind()
							cnmt.seek(0x20+offset)
							for i in range(content_entries):
								feed=self.html_feed(feed,2,message=str('Content number ' + str(i+1)))
								vhash = cnmt.read(0x20)
								message=["Hash:",(str(hx(vhash))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
								NcaId = cnmt.read(0x10)
								message=["NcaId:",(str(hx(NcaId))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
								size = cnmt.read(0x6)
								message=["Size:",(str(sq_tools.getSize(int.from_bytes(size, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
								ncatype = cnmt.read(0x1)
								message=["Ncatype:",(sq_tools.getmetacontenttype(str(int.from_bytes(ncatype, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
								IdOffset = cnmt.read(0x1)
								message=["IdOffset:",(str(int.from_bytes(IdOffset, byteorder='little', signed=True)))];feed=self.html_feed(feed,3,message)
							cnmt.seek(0x20+offset+content_entries*0x38+length_of_emeta)
							digest = cnmt.read(0x20)
							feed=self.html_feed(feed,7,message=['Digest= ',(str((str(hx(digest))[2:-1]).upper()))])
							cnmt.seek(0x20+offset+content_entries*0x38)
							if length_of_emeta>0:
								feed=self.html_feed(feed,2,message=str('Extended meta:'))
								num_prev_cnmt=cnmt.read(0x4)
								num_prev_delta=cnmt.read(0x4)
								num_delta_info=cnmt.read(0x4)
								num_delta_application =cnmt.read(0x4)
								num_previous_content=cnmt.read(0x4)
								num_delta_content=cnmt.read(0x4)
								cnmt.read(0x4)
								message=["Number of previous cnmt entries:",(str(int.from_bytes(num_prev_cnmt, byteorder='little')))];feed=self.html_feed(feed,3,message)
								message=["Number of previous delta entries:",(str(int.from_bytes(num_prev_delta, byteorder='little')))];feed=self.html_feed(feed,3,message)
								message=["Number of previous content entries:",(str(int.from_bytes(num_previous_content, byteorder='little')))];feed=self.html_feed(feed,3,message)
								message=["Number of delta content entries:",(str(int.from_bytes(num_delta_content, byteorder='little')))];feed=self.html_feed(feed,3,message)
								for i in range(int.from_bytes(num_prev_cnmt, byteorder='little')):
									feed=self.html_feed(feed,2,message=str('Previous cnmt records: '+ str(i+1)))
									titleid=cnmt.readInt64()
									titleversion = cnmt.read(0x4)
									type_n = cnmt.read(0x1)
									unknown1=cnmt.read(0x3)
									vhash = cnmt.read(0x20)
									unknown2=cnmt.read(0x2)
									unknown3=cnmt.read(0x2)
									unknown4=cnmt.read(0x4)
									message=["Titleid:",(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1].upper())];feed=self.html_feed(feed,3,message)
									message=["Version:",(str(int.from_bytes(titleversion, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["Content Type:",(sq_tools.cnmt_type(type_n))];feed=self.html_feed(feed,3,message)
									message=["Hash:",(str(hx(vhash))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
									message=["Ncatype:",(sq_tools.getmetacontenttype(str(int.from_bytes(unknown2, byteorder='little'))))];feed=self.html_feed(feed,3,message)
								for i in range(int.from_bytes(num_prev_delta, byteorder='little')):
									feed=self.html_feed(feed,2,message=str('Previous delta records: '+ str(i+1)))
									oldtitleid=cnmt.readInt64()
									newtitleid=cnmt.readInt64()
									oldtitleversion = cnmt.read(0x4)
									newtitleversion = cnmt.read(0x4)
									size = cnmt.read(0x8)
									unknown1=cnmt.read(0x8)
									message=["Old titleid:",(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1].upper())];feed=self.html_feed(feed,3,message)
									message=["New titleid:",(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1].upper())];feed=self.html_feed(feed,3,message)
									message=["Old version:",(str(int.from_bytes(oldtitleversion, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["New version:",(str(int.from_bytes(newtitleversion, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["Size:",(str(sq_tools.getSize(int.from_bytes(size, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
								for i in range(int.from_bytes(num_delta_info, byteorder='little')):
									feed=self.html_feed(feed,2,message=str('Delta info: '+ str(i+1)))
									oldtitleid=cnmt.readInt64()
									newtitleid=cnmt.readInt64()
									oldtitleversion = cnmt.read(0x4)
									newtitleversion = cnmt.read(0x4)
									index1=cnmt.readInt64()
									index2=cnmt.readInt64()
									message=["Old titleid:",(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1].upper())];feed=self.html_feed(feed,3,message)
									message=["New titleid:",(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1].upper())];feed=self.html_feed(feed,3,message)
									message=["Old version:",(str(int.from_bytes(oldtitleversion, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["New version:",(str(int.from_bytes(newtitleversion, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["Index1:",(str(hx(index1.to_bytes(8, byteorder='big'))))];feed=self.html_feed(feed,3,message)
									message=["Index2:",(str(hx(index2.to_bytes(8, byteorder='big'))))];feed=self.html_feed(feed,3,message)
								for i in range(int.from_bytes(num_delta_application, byteorder='little')):
									feed=self.html_feed(feed,2,message=str('Delta application info: '+ str(i+1)))
									OldNcaId = cnmt.read(0x10)
									NewNcaId = cnmt.read(0x10)
									old_size = cnmt.read(0x6)
									up2bytes = cnmt.read(0x2)
									low4bytes = cnmt.read(0x4)
									unknown1 = cnmt.read(0x2)
									ncatype = cnmt.read(0x1)
									installable = cnmt.read(0x1)
									unknown2 = cnmt.read(0x4)
									message=["OldNcaId:",(str(hx(OldNcaId))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
									message=["NewNcaId:",(str(hx(NewNcaId))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
									message=["Old size:",(str(sq_tools.getSize(int.from_bytes(old_size, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
									message=["Unknown1:",(str(int.from_bytes(unknown1, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["Ncatype:",(sq_tools.getmetacontenttype(str(int.from_bytes(ncatype, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
									message=["Installable:",(str(int.from_bytes(installable, byteorder='little')))];feed=self.html_feed(feed,3,message)
									message=["Upper 2 bytes of the new size:",(str(hx(up2bytes)))];feed=self.html_feed(feed,3,message)
									message=["Lower 4 bytes of the new size:",(str(hx(low4bytes)))];feed=self.html_feed(feed,3,message)
								for i in range(int.from_bytes(num_previous_content, byteorder='little')):
									feed=self.html_feed(feed,2,message=str('Previous content records: '+ str(i+1)))
									NcaId = cnmt.read(0x10)
									size = cnmt.read(0x6)
									ncatype = cnmt.read(0x1)
									unknown1 = cnmt.read(0x1)
									message=["NcaId:",(str(hx(NcaId))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
									message=["Size:",(str(sq_tools.getSize(int.from_bytes(size, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
									message=["Ncatype:",(sq_tools.getmetacontenttype(str(int.from_bytes(ncatype, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
								for i in range(int.from_bytes(num_delta_content, byteorder='little')):
									feed=self.html_feed(feed,2,message=str('Delta content entry: '+ str(i+1)))
									vhash = cnmt.read(0x20)
									message=["Hash:",(str(hx(vhash))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
									NcaId = cnmt.read(0x10)
									message=["NcaId:",(str(hx(NcaId))[2:-1]).upper()];feed=self.html_feed(feed,3,message)
									size = cnmt.read(0x6)
									message=["Size:",(str(sq_tools.getSize(int.from_bytes(size, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
									ncatype = cnmt.read(0x1)
									message=["Ncatype:",(sq_tools.getmetacontenttype(str(int.from_bytes(ncatype, byteorder='little', signed=True))))];feed=self.html_feed(feed,3,message)
									IdOffset = cnmt.read(0x1)
									message=["IdOffset:",(str(int.from_bytes(IdOffset, byteorder='little', signed=True)))];feed=self.html_feed(feed,3,message)
		return feed

#READ CNMT FILE WITHOUT EXTRACTION
	def ret_xml(self,nca):
		crypto1=nca.header.getCryptoType()
		crypto2=nca.header.getCryptoType2()
		if crypto2>crypto1:
			keygeneration=crypto2
		if crypto2<=crypto1:
			keygeneration=crypto1
		xmlname = str(nca._path)
		xmlname = xmlname[:-4] + '.xml'
		metaname=str(nca._path)
		metaname =  metaname[:-9]
		for f in nca:
			for cnmt in f:
				nca.rewind()
				f.rewind()
				cnmt.rewind()
				titleid=cnmt.readInt64()
				titleversion = cnmt.read(0x4)
				type_n = cnmt.read(0x1)
				cnmt.seek(0xE)
				offset=cnmt.readInt16()
				content_entries=cnmt.readInt16()
				meta_entries=cnmt.readInt16()
				cnmt.seek(0x18)
				RDSV=cnmt.readInt64()
				cnmt.seek(0x20)
				original_ID=cnmt.readInt64()
				cnmt.seek(0x28)
				min_sversion=cnmt.readInt32()
				length_of_emeta=cnmt.readInt32()
				cnmt.seek(0x20+offset)
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
					vhash = cnmt.read(0x20)
					NcaId = cnmt.read(0x10)
					size = cnmt.read(0x6)
					ncatype = cnmt.readInt8()
					unknown = cnmt.read(0x1)
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

				cnmt.seek(0x20+offset+content_entries*0x38+length_of_emeta)
				digest = str(hx(cnmt.read(0x20)))
				digest=digest[2:-1]
				original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
				original_ID='0x'+original_ID[2:-1]
				size=str(nca.header.size)
				block = nca.read()
				nsha=sha256(block).hexdigest()
				xml_string +=('  <Content>' + '\n')
				xml_string +=('    <Type>'+ 'Meta' +'</Type>' + '\n')
				xml_string +=('    <Id>'+ metaname +'</Id>' + '\n')
				xml_string +=('    <Size>'+ size +'</Size>' + '\n')
				xml_string +=('    <Hash>'+ str(nsha) +'</Hash>' + '\n')
				xml_string +=('    <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')
				xml_string +=('  </Content>' + '\n')
				xml_string +=('  <Digest>'+ digest +'</Digest>' + '\n')
				xml_string +=('  <KeyGeneration>'+ str(keygeneration) +'</KeyGeneration>' + '\n')
				xml_string +=('  <RequiredSystemVersion>'+ str(min_sversion) +'</RequiredSystemVersion>' + '\n')
				xml_string +=('  <OriginalId>'+ original_ID +'</OriginalId>' + '\n')
				xml_string +=('</ContentMeta>')

				xmlsize=len(xml_string)
				return xmlname,xmlsize


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
				if nca.header.getRightsId() != 0:
					if nca.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(nca._path)} - {nca.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.getCryptoType2() == 0:
						if nca.header.getCryptoType() == 2:
							masterKeyRev = 2
							titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
							break

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

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(nca._path)} - {nca.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")

		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.getCryptoType2() == 0:
						if nca.header.getCryptoType() == 2:
							masterKeyRev = 2
							titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
							break

		Print.info('rightsId =\t' + hex(rightsId))
		Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
		Print.info('masterKeyRev =\t' + hex(masterKeyRev))
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

#Copy nca files
	def copy_nca(self,ofolder,buffer,metapatch,keypatch,RSV_cap):
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
		t.close()


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
#INFO ABOUT UPD REQUIREMENTS
#///////////////////////////////////////////////////
	def getsdkvertit(self,titid):
		programSDKversion=''
		dataSDKversion=''
		for nca in self:
			if type(nca) == Nca:
				nca_id=nca.header.titleId
				if str(titid[:-3]).upper() == str(nca_id[:-3]).upper():
					if 	str(nca.header.contentType) == 'Content.PROGRAM':
						programSDKversion=nca.get_sdkversion()
						break
		if 	programSDKversion=='':
			for nca in self:
				if type(nca) == Nca:
					nca_id=nca.header.titleId
					if str(titid[:-3]).upper() == str(nca_id[:-3]).upper():
						if 	str(nca.header.contentType) == 'Content.CONTROL':
							programSDKversion=nca.get_sdkversion()
							break
		if 	programSDKversion=='':
			for nca in self:
				if type(nca) == Nca:
					nca_id=nca.header.titleId
					if str(titid[:-3]).upper() == str(nca_id[:-3]).upper():
						if 	str(nca.header.contentType) == 'Content.PUBLIC_DATA':
							dataSDKversion = nca.get_sdkversion()
							break
		return 	programSDKversion,dataSDKversion

	def print_fw_req(self,trans=True):
		feed=''
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
							content_type_cnmt=str(cnmt._path)
							content_type_cnmt=content_type_cnmt[:-22]
							if content_type_cnmt == 'Patch':
								content_type='Update'
								reqtag='- RequiredSystemVersion: '
								tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
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
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
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
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
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
								if tit_name=='DLC':
									tit_name='-'
									editor='-'
								if isdemo == 1:
									content_type='Demo'
								if isdemo == 2:
									content_type='RetailInteractiveDisplay'
							programSDKversion,dataSDKversion=self.getsdkvertit(titleid2)
							nsuId,releaseDate,category,ratingContent,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(titleid2,trans)
							sdkversion=nca.get_sdkversion()
							message=('-----------------------------');print(message);feed+=message+'\n'
							message=('CONTENT ID: ' + str(titleid2));print(message);feed+=message+'\n'
							message=('-----------------------------');print(message);feed+=message+'\n'
							if content_type_cnmt != 'AddOnContent':
								message=("Titleinfo:");print(message);feed+=message+'\n'
								message=("- Name: " + tit_name);print(message);feed+=message+'\n'
								message=("- Editor: " + editor);print(message);feed+=message+'\n'
								message=("- Display Version: " + str(ediver));print(message);feed+=message+'\n'
								message=("- Meta SDK version: " + sdkversion);print(message);feed+=message+'\n'
								message=("- Program SDK version: " + programSDKversion);print(message);feed+=message+'\n'
								suplangue=str((', '.join(SupLg)))
								message=("- Supported Languages: "+suplangue);
								par = textwrap.dedent(message).strip()
								message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
								message=("- Content type: "+content_type);print(message);feed+=message+'\n'
								message=("- Version: " + version+' -> '+content_type_cnmt+' ('+str(v_number)+')');print(message);feed+=message+'\n'
							if content_type_cnmt == 'AddOnContent':
								nsuId=nutdb.get_dlcnsuId(titleid2)
								message=("Titleinfo:");print(message);feed+=message+'\n'
								if tit_name != "DLC":
									message=("- Name: " + tit_name);print(message);feed+=message+'\n'
									message=("- Editor: " + editor);print(message);feed+=message+'\n'
								message=("- Content type: "+"DLC");print(message);feed+=message+'\n'
								DLCnumb=str(titleid2)
								DLCnumb="0000000000000"+DLCnumb[-3:]
								DLCnumb=bytes.fromhex(DLCnumb)
								DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
								DLCnumb=int(DLCnumb)
								message=("- DLC number: "+str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')');print(message);feed+=message+'\n'
								message=("- DLC version Number: " + version+' -> '+"Version"+' ('+str(v_number)+')');print(message);feed+=message+'\n'
								message=("- Meta SDK version: " + sdkversion);print(message);feed+=message+'\n'
								message=("- Data SDK version: " + dataSDKversion);print(message);feed+=message+'\n'
								if SupLg !='':
									suplangue=str((', '.join(SupLg)))
									message=("- Supported Languages: "+suplangue);
									par = textwrap.dedent(message).strip()
									message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
							message=("\nRequired Firmware:");print(message);feed+=message+'\n'
							if content_type_cnmt == 'AddOnContent':
								if v_number == 0:
									message=("- Required game version: " + str(RSversion)+' -> '+"Application"+' ('+str(RS_number)+')');print(message);feed+=message+'\n'
								if v_number > 0:
									message=("- Required game version: " + str(RSversion)+' -> '+"Patch"+' ('+str(RS_number)+')');print(message);feed+=message+'\n'
							else:
								message=(reqtag + str(RSversion)+" -> " +RSV_rq);print(message);feed+=message+'\n'
							message=('- Encryption (keygeneration): ' + str(keygen)+" -> " +FW_rq);print(message);feed+=message+'\n'
							if content_type_cnmt != 'AddOnContent':
								message=('- Patchable to: ' + str(MinRSV)+" -> " + RSV_rq_min+'\n');print(message);feed+=message+'\n'
							else:
								message=('- Patchable to: DLC -> no RSV to patch\n');print(message);feed+=message+'\n'
							try:
								if content_type_cnmt != 'AddOnContent':
									message=('ExeFS Data:');print(message);feed+=message+'\n'
									ModuleId,BuildID8,BuildID16=self.read_buildid()
									message=('- BuildID8:  '+ BuildID8);print(message);feed+=message+'\n'
									message=('- BuildID16: '+ BuildID16);print(message);feed+=message+'\n'
									message=('- BuildID32: '+ ModuleId +'\n');print(message);feed+=message+'\n'
							except:pass
							if nsuId!=False or numberOfPlayers!=False or releaseDate!=False or category!=False or ratingContent!=False:
								message=('Eshop Data:');print(message);feed+=message+'\n'
							if nsuId!=False:
								message=("- nsuId: " + nsuId);print(message);feed+=message+'\n'
							if region!=False:
								message=('- Data from Region: ' + region);print(message);feed+=message+'\n'
							if numberOfPlayers!=False:
								message=("- Number of Players: " + numberOfPlayers);print(message);feed+=message+'\n'
							if releaseDate!=False:
								message=("- Release Date: " + releaseDate);print(message);feed+=message+'\n'
							if category!=False:
								category=str((', '.join(category)))
								message=("- Genres: " + category);
								par = textwrap.dedent(message).strip()
								message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
							if rating!=False:
								message=("- AgeRating: " + rating);print(message);feed+=message+'\n'
							if ratingContent!=False:
								ratingContent=str((', '.join(ratingContent)))
								message=("- Rating tags: " + ratingContent);
								par = textwrap.dedent(message).strip()
								message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
							if intro!=False or description!=False:
								message=('\nDescription:');print(message);feed+=message+'\n'
							if intro!=False:
								par = textwrap.dedent(intro).strip().upper()
								message=('-----------------------------------------------------------------------------');print(message);feed+=message+'\n'
								message=(textwrap.fill(par,width=80,initial_indent=' ', subsequent_indent=' ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
								message=('-----------------------------------------------------------------------------');print(message);feed+=message+'\n'
							if description!=False:
								if "•" in description:
									data=description.split("• ")
									token='• '
								elif "★" in description:
									data=description.split("★ ")
									token='* '
								elif "*" in description:
									data=description.split("* ")
									token='* '
								elif "■" in description:
									data=description.split("* ")
									token='• '
								elif "●" in description:
									data=description.split("● ")
									token='• '
								elif "-" in description:
									data=description.split("- ")
									token='- '
								else:
									data=description.split("  ")
									token=''
								i=0
								for d in data:
									if i>0:
										d=token+d
									i+=1
									par = textwrap.dedent(d).strip()
									message=(textwrap.fill(par,width=80,initial_indent=' ', subsequent_indent=' ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
		return feed

	def inf_get_title(self,target,offset,content_entries,original_ID,roman=True):
		content_type=''
		for nca in self:
			if type(nca) == Nca:
				if target ==  str(nca._path):
					for f in nca:
						for cnmt in f:
							nca.rewind()
							f.rewind()
							cnmt.rewind()
							titleid=cnmt.readInt64()
							titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
							titleid2 = titleid2[2:-1]
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
			title = 'DLC'
			title,editor=nutdb.get_dlcData(titleid2)
			if editor==False:
				editor=""
			if title==False:
				title = 'DLC'
			else:
				SupLg=nutdb.get_content_langue(titleid2)
				if SupLg==False:
					SupLg=""
				#return(title,editor,ediver,SupLg,regionstr,isdemo)
				regionstr="0|0|0|0|0|0|0|0|0|0|0|0|0|0"
				return(title,editor,"",SupLg,regionstr,"")
		if nca_name=='false' and title == 'DLC'	:
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
									contentname,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
									DLCnumb=str(titleid2)
									DLCnumb="0000000000000"+DLCnumb[-3:]
									DLCnumb=bytes.fromhex(DLCnumb)
									DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
									DLCnumb=int(DLCnumb)
									name = contentname+' '+'['+str(DLCnumb)+']'
									return name,editor,"","",regionstr,""
		title = 'DLC'
		for nca in self:
			if type(nca) == Nca:
				if nca_name == str(nca._path):
					if 	str(nca.header.contentType) == 'Content.CONTROL':
						title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title,roman)
						return(title,editor,ediver,SupLg,regionstr,isdemo)
		regionstr="0|0|0|0|0|0|0|0|0|0|0|0|0|0"
		return(title,"","","",regionstr,"")


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
		for file in self:
			if type(file) == Ticket:
				masterKeyRev = file.getMasterKeyRevision()
				titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
				rightsId = file.getRightsId()
		for file in self:
			if type(file) == Nca:
				if file.header.getRightsId() != 0:
					if file.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(file._path)} - {file.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")
		for file in self:
			if type(file) == Nca:
				if file.header.getRightsId() != 0:
					if file.header.getCryptoType2() == 0:
						if file.header.getCryptoType() == 2:
							masterKeyRev = 2
							titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
							break
		Print.info('Reading Base NSP:')
		if rightsId	!=0:
			Print.info('rightsId =\t' + hex(rightsId))
			Print.info('titleKeyDec =\t' + str(hx(titleKeyDec)))
			Print.info('masterKeyRev =\t' + hex(masterKeyRev))
		print("")

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
								self.updbase_copy(ofolder,buffer,nca_name,metapatch, keypatch,RSV_cap,titleKeyDec)
							nca_meta=str(nca._path)
							self.updbase_copy(ofolder,buffer,nca_meta,metapatch, keypatch,RSV_cap,titleKeyDec)
							#self.updbase_tyc(ofolder,titleid2)

	def updbase_copy(self,ofolder,buffer,nca_name,metapatch, keypatch,RSV_cap,titleKeyDec):
		indent = 1
		tabs = '\t' * indent

		for nca in self:
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

	def change_mkrev_nca(self, nca, newMasterKeyRev,silent=False):

		indent = 2
		tabs = '\t' * indent
		indent2 = 3
		tabs2 = '\t' * indent2

		crypto1=nca.header.getCryptoType()
		crypto2=nca.header.getCryptoType2()
		if crypto2>crypto1:
			masterKeyRev=crypto2
		if crypto2<=crypto1:
			masterKeyRev=crypto1

		if type(nca) == Nca:
			if nca.header.getCryptoType2() != newMasterKeyRev:
				if silent == False:
					Print.info(tabs + '-----------------------------------')
					Print.info(tabs + 'Changing keygeneration from %d to %s' % ( nca.header.getCryptoType2(), str(newMasterKeyRev)))
					Print.info(tabs + '-----------------------------------')
				encKeyBlock = nca.header.getKeyBlock()
				if sum(encKeyBlock) != 0:
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
					if silent == False:
						Print.info(tabs2 + '+ decrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
					crypto = aes128.AESECB(key)
					decKeyBlock = crypto.decrypt(encKeyBlock)
					key = Keys.keyAreaKey(Keys.getMasterKeyIndex(newMasterKeyRev), nca.header.keyIndex)
					if silent == False:
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
				if newMasterKeyRev < 2:
					nca.header.setCryptoType(newMasterKeyRev)
					nca.header.setCryptoType2(0)
				if silent == False:
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
			Print.info(tabs +'  + '+ str(hx(sha3)))
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


	def get_title(self,baseid,roman=True,tag=False):
		for nca in self:
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
								if tag==False:
									nutdbname=nutdb.get_dlcname(titleid2)
								else:
									nutdbname=False
								if nutdbname!=False:
									title=nutdbname
								else:
									DLCnumb=str(titleid2)
									DLCnumb="0000000000000"+DLCnumb[-3:]
									DLCnumb=bytes.fromhex(DLCnumb)
									DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
									DLCnumb=int(DLCnumb)
									title = 'DLC number '+str(DLCnumb)
								return(title)
		title='DLC'
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title,roman)
					return(title)

	def get_lang_tag(self,baseid):
		languetag=False
		for nca in self:
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
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title)
					languetag='('
					if ("US (eng)" in SupLg) or ("UK (eng)" in SupLg):
						languetag=languetag+'En,'
					if "JP" in SupLg:
						languetag=languetag+'Jp,'
					if ("CAD (fr)" in SupLg) or ("FR" in SupLg):
						languetag=languetag+'Fr,'
					elif ("CAD (fr)" in SupLg):
						languetag=languetag+'CADFr,'
					elif ("FR") in SupLg:
						languetag=languetag+'Fr,'
					if "DE" in SupLg:
						languetag=languetag+'De,'
					if ("LAT (spa)" in SupLg) and ("SPA" in SupLg):
						languetag=languetag+'Es,'
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

	def gen_nsp_head(self,files,delta,inc_xml,ofolder):

		filesNb = len(files)
		stringTable = '\x00'.join(str(nca) for nca in files)
		headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
		remainder = 0x10 - headerSize%0x10
		headerSize += remainder

		fileSizes = list()
		for nca in self:
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

	def c_nsp_direct(self,buffer,outfile,ofolder,fat,fx,delta,metapatch,RSV_cap,keypatch):

		t = tqdm(total=False, unit='B', unit_scale=False, leave=False)

		if keypatch != 'false':
			try:
				keypatch = int(keypatch)
			except:
				print("New keygeneration is no valid integer")
		indent = 1
		tabs = '\t' * indent

		for file in self:
			if type(file) == Ticket:
				masterKeyRev = file.getMasterKeyRevision()
				ticket=file
				titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
				rightsId = file.getRightsId()
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(nca._path)} - {nca.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					if nca.header.getCryptoType2() == 0:
						if nca.header.getCryptoType() == 2:
							masterKeyRev = 2
							titleKeyDec = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
							break

		for nca in self:
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
		for nca in self:
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
		for nca in self:
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
		for nca in self:
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
							inmemoryfile = io.BytesIO(newheader)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(newheader)-n2)
							inmemoryfile.close()
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
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
							outf.write(dat2)
							t.update(len(dat2))
							outf.flush()
						else:
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
							outf.flush()
						if not data:
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
					if fat=="fat32" and (c+len(data))>block:
						n2=block-c
						c=0
						inmemoryfile = io.BytesIO()
						inmemoryfile.write(data)
						inmemoryfile.seek(0)
						dat2=inmemoryfile.read(n2)
						outf.write(dat2)
						outf.flush()
						outf.close()
						t.update(len(dat2))
						index=index+1
						outfile=outfile[0:-1]
						outfile=outfile+str(index)
						outf = open(outfile, 'wb')
						inmemoryfile.seek(n2)
						dat2=inmemoryfile.read(len(data)-n2)
						inmemoryfile.close()
						outf.write(dat2)
						t.update(len(dat2))
						outf.flush()
					else:
						outf.write(data)
						t.update(len(data))
						c=c+len(data)
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
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
							outf.write(dat2)
							t.update(len(dat2))
							outf.flush()
						else:
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
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
#ADD TO DATABASE
#///////////////////////////////////////////////////
	def addtodb(self,ofile,dbtype,roman=True):
		for nca in self:
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
							titleversion = cnmt.read(0x4)
							version=str(int.from_bytes(titleversion, byteorder='little'))
							cnmt.seek(0xE)
							offset=cnmt.readInt16()
							content_entries=cnmt.readInt16()
							content_type=str(cnmt._path)
							content_type=content_type[:-22]
							cnmt.seek(0x20)
							if content_type=='Application':
								original_ID=titleid2
								cnmt.readInt64()
							else:
								original_ID=cnmt.readInt64()
								original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
								original_ID = original_ID[2:-1]
							min_sversion=cnmt.readInt32()
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
							sdkversion=nca.get_sdkversion()
							programSDKversion,dataSDKversion=self.getsdkvertit(titleid2)
							MinRSV=sq_tools.getMinRSV(keygen,min_sversion)
							RSV_rq=sq_tools.getFWRangeRSV(min_sversion)
							length_of_emeta=cnmt.readInt32()
							target=str(nca._path)
							titlerights,ckey=self.getdbtr(original_ID,content_type,titleid2)
							if ckey == '0':
								ckey=self.getdbkey(titlerights)
							target=str(nca._path)
							tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID,roman)
							if tit_name=='DLC' and (str(titlerights).endswith('000') or str(titlerights).endswith('800')):
								tit_name='-'
								editor='-'
							if dbtype == 'extended' or dbtype == 'all':
								dbstring=self.getdbstr(titleid2,titlerights,ckey,content_type,tit_name,version,crypto1,crypto2,keygen,min_sversion,RSV_rq[1:-1],RS_number,MinRSV,regionstr,ediver,editor,isdemo,sdkversion,programSDKversion,dataSDKversion)
							if dbtype == 'keyless' or dbtype == 'all':
								kdbstring=self.getkeylessdbstr(titleid2,titlerights,ckey,content_type,tit_name,version,crypto1,crypto2,keygen,min_sversion,RSV_rq[1:-1],RS_number,MinRSV,regionstr,ediver,editor,isdemo,sdkversion,programSDKversion,dataSDKversion)
							if dbtype == 'nutdb' or dbtype == 'all':
								ndbstring=self.getnutdbstr(titleid2,titlerights,ckey,content_type,tit_name,version,regionstr,isdemo)
							if dbtype == 'simple' or dbtype == 'all':
								simplbstr=self.simplbstr(titlerights,ckey,tit_name)
							print ("- Processing: "+ str(self._path))
							print("")
							if dbtype == 'extended':
								print("EXTENDED DB STRING:")
								self.appendtodb(dbstring,ofile,dbtype)
							if dbtype == 'keyless':
								print("EXTENDED KEYLESS DB STRING:")
								self.appendtodb(kdbstring,ofile,dbtype)
							if dbtype == 'nutdb':
								print("NUTDB DB STRING:")
								self.appendtodb(ndbstring,ofile,dbtype)
							if dbtype == 'simple':
								print("SIMPLE DB STRING:")
								self.appendtodb(simplbstr,ofile,dbtype)
							if dbtype == 'all':
								dir=os.path.dirname(os.path.abspath(ofile))
								edbf='extended_DB.txt'
								edbf = os.path.join(dir, edbf)
								ndbf='nutdb_DB.txt'
								ndbf = os.path.join(dir, ndbf)
								kdbfile='keyless_DB.txt'
								kdbfile = os.path.join(dir, kdbfile)
								simpbfile='simple_DB.txt'
								simpbfile = os.path.join(dir, simpbfile)
								print("EXTENDED DB STRING:")
								self.appendtodb(dbstring,edbf,"extended")
								print("")
								print("EXTENDED KEYLESS DB STRING:")
								self.appendtodb(kdbstring,kdbfile,"keyless")
								print("")
								print("NUTDB DB STRING:")
								self.appendtodb(ndbstring,ndbf,"nutdb")
								print("")
								print("SIMPLE DB STRING:")
								self.appendtodb(simplbstr,simpbfile,"simple")
							print("")


	def getdbtr(self,original_ID,content_type,cnmt_id):
		titleKeyDec='0'
		nca_id=''
		self.rewind()
		tr=''
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					crypto1=nca.header.getCryptoType()
					crypto2=nca.header.getCryptoType2()
					nca_id=nca.header.titleId
					nca_id=nca_id.lower()
					if original_ID==nca_id:
						tr=str(nca.header.rightsId)
						tr = tr[2:-1]
						check=tr[:16]
						if check.endswith('000') and content_type=='Application':
							return tr,titleKeyDec
						if check.endswith('800') and content_type=='Patch':
							return tr,titleKeyDec
						if not check.endswith('000') and not tr.endswith('800') and content_type=='AddOnContent':
							return tr,titleKeyDec
					else:
						tr=str(nca.header.rightsId)
						tr = tr[2:-1]
						return tr,titleKeyDec
				if nca.header.getRightsId() == 0:
					crypto1=nca.header.getCryptoType()
					crypto2=nca.header.getCryptoType2()
					nca_id=nca.header.titleId
					nca_id=nca_id.lower()
					if original_ID==nca_id:
						if	nca.header.getgamecard() == 0:
							if crypto1>crypto2:
								masterKeyRev = crypto1
							else:
								masterKeyRev = crypto2
							key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
							crypto = aes128.AESECB(key)
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) != 0:
								encKeyBlock = nca.header.getKeyBlock()
								decKeyBlock = crypto.decrypt(encKeyBlock[:16])
								titleKeyDec = hx(Keys.encryptTitleKey(decKeyBlock, Keys.getMasterKeyIndex(masterKeyRev)))
								titleKeyDec=str(titleKeyDec)[2:-1]
								tr=cnmt_id+'000000000000000'+str(crypto2)
								check=tr[:16]
								if check.endswith('000') and content_type=='Application':
									return tr,titleKeyDec
								if check.endswith('800') and content_type=='Patch':
									return tr,titleKeyDec
					elif cnmt_id==nca_id:
						if	nca.header.getgamecard() == 0:
							if crypto1>crypto2:
								masterKeyRev = crypto1
							else:
								masterKeyRev = crypto2
							key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex)
							crypto = aes128.AESECB(key)
							KB1L=nca.header.getKB1L()
							KB1L = crypto.decrypt(KB1L)
							if sum(KB1L) != 0:
								encKeyBlock = nca.header.getKeyBlock()
								decKeyBlock = crypto.decrypt(encKeyBlock[:16])
								titleKeyDec = hx(Keys.encryptTitleKey(decKeyBlock, Keys.getMasterKeyIndex(masterKeyRev)))
								titleKeyDec=str(titleKeyDec)[2:-1]
								tr=cnmt_id+'000000000000000'+str(crypto2)
								check=tr[:16]
								if not check.endswith('000') and not tr.endswith('800') and content_type=='AddOnContent':
									return tr,titleKeyDec
							else:
								tr=cnmt_id+'000000000000000'+str(crypto2)
						else:
							tr=cnmt_id+'000000000000000'+str(crypto2)
		if tr=='':
			tr=cnmt_id+'000000000000000'+str(crypto2)
		titleKeyDec='00000000000000000000000000000000'
		return tr,titleKeyDec

	def getdbkey(self,titlerights):
		for ticket in self:
			if type(ticket) == Ticket:
				tikrights = hex(ticket.getRightsId())
				tikrights = '0'+tikrights[2:]
				if titlerights == tikrights:
					titleKey = ticket.getTitleKeyBlock()
					titleKey=str(hx(titleKey.to_bytes(16, byteorder='big')))
					titleKey=titleKey[2:-1]
					return str(titleKey)

	def getdbstr(self,titleid,titlerights,ckey,content_type,tit_name,version,crypto1,crypto2,keygen,min_sversion,RSV_rq,RS_number,MinRSV,regionstr,ediver,editor,isdemo,sdkversion,programSDKversion,dataSDKversion):
		dbstr=str()
		dbstr+=str(titleid).upper()+'|'
		dbstr+=str(titlerights).upper()+'|'
		dbstr+=str(keygen)+'|'
		if content_type == 'AddOnContent':
			RSV_rq=sq_tools.getFWRangeRSV(MinRSV)
			RSV_rq=RSV_rq[1:-1]
			ediver='-'
			editor='-'
		dbstr+=str(RSV_rq)+'|'
		if content_type == 'AddOnContent':
			RGV_rq=RS_number
		else:
			RGV_rq="0"
		dbstr+=str(RGV_rq)+'|'
		dbstr+=str(ckey).upper()+'|'
		if content_type == 'Application' and isdemo==0:
			if tit_name == 'DLC':
				tit_name = '-'
			dbstr+='GAME|'
		elif content_type=='Patch' and isdemo==0:
			dbstr+='UPD|'
		elif content_type=='AddOnContent':
			dbstr+='DLC|'
			if tit_name == 'DLC':
				DLCnumb=str(titleid)
				DLCnumb="0000000000000"+DLCnumb[-3:]
				DLCnumb=bytes.fromhex(DLCnumb)
				DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
				DLCnumb=int(DLCnumb)
				tit_name="DLC Numb. "+str(DLCnumb)
		elif content_type == 'Application' and isdemo!=0:
			if isdemo == 2:
				dbstr+='INT DISPLAY|'
			else:
				dbstr+='DEMO|'
		elif content_type == 'Patch' and isdemo!=0:
			if isdemo == 2:
				dbstr+='UPD INT DISPLAY|'
			else:
				dbstr+='UPD DEMO|'
		elif content_type == 'Application':
			dbstr+='DEMO|'
		elif content_type == 'Patch':
			dbstr+='UPD DEMO|'
		else:
			dbstr+='-|'
		dbstr+=str(tit_name)+'|'
		dbstr+=str(editor)+'|'
		dbstr+=str(version)+'|'
		dbstr+=str(ediver)+'|'
		dbstr+=sdkversion+'|'
		if content_type!='AddOnContent':
			dbstr+=programSDKversion+'|'
		else:
			dbstr+=dataSDKversion+'|'
		dbstr+=regionstr
		return dbstr

	def getkeylessdbstr(self,titleid,titlerights,ckey,content_type,tit_name,version,crypto1,crypto2,keygen,min_sversion,RSV_rq,RS_number,MinRSV,regionstr,ediver,editor,isdemo,sdkversion,programSDKversion,dataSDKversion):
		dbstr=str()
		dbstr+=str(titleid).upper()+'|'
		dbstr+=str(titlerights).upper()+'|'
		dbstr+=str(keygen)+'|'
		if content_type == 'AddOnContent':
			RSV_rq=sq_tools.getFWRangeRSV(MinRSV)
			RSV_rq=RSV_rq[1:-1]
			ediver='-'
			editor='-'
		dbstr+=str(RSV_rq)+'|'
		if content_type == 'AddOnContent':
			RGV_rq=RS_number
		else:
			RGV_rq="0"
		dbstr+=str(RGV_rq)+'|'
		if content_type == 'Application' and isdemo==0:
			if tit_name == 'DLC':
				tit_name = '-'
			dbstr+='GAME|'
		elif content_type=='Patch' and isdemo==0:
			dbstr+='UPD|'
		elif content_type=='AddOnContent':
			dbstr+='DLC|'
			if tit_name == 'DLC':
				DLCnumb=str(titleid)
				DLCnumb="0000000000000"+DLCnumb[-3:]
				DLCnumb=bytes.fromhex(DLCnumb)
				DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
				DLCnumb=int(DLCnumb)
				tit_name="DLC Numb. "+str(DLCnumb)
		elif content_type == 'Application' and isdemo!=0:
			if isdemo == 2:
				dbstr+='INT DISPLAY|'
			else:
				dbstr+='DEMO|'
		elif content_type == 'Patch' and isdemo!=0:
			if isdemo == 2:
				dbstr+='UPD INT DISPLAY|'
			else:
				dbstr+='UPD DEMO|'
		elif content_type == 'Application':
			dbstr+='DEMO|'
		elif content_type == 'Patch':
			dbstr+='UPD DEMO|'
		else:
			dbstr+='-|'
		dbstr+=str(tit_name)+'|'
		dbstr+=str(editor)+'|'
		dbstr+=str(version)+'|'
		dbstr+=str(ediver)+'|'
		dbstr+=sdkversion+'|'
		if content_type!='AddOnContent':
			dbstr+=programSDKversion+'|'
		else:
			dbstr+=dataSDKversion+'|'
		dbstr+=regionstr
		return dbstr

	def getnutdbstr(self,titleid,titlerights,ckey,content_type,tit_name,version,regionstr,isdemo,):
		dbstr=str()
		dbstr+=str(titleid).upper()+'|'
		dbstr+=str(titlerights).upper()+'|'
		dbstr+=str(ckey).upper()+'|'
		if content_type == 'Application' and isdemo==0:
			if tit_name == 'DLC':
				tit_name = '-'
			dbstr+='0|0|0|'
		elif content_type=='Patch' and isdemo==0:
			dbstr+='1|0|0|'
		elif content_type=='AddOnContent':
			dbstr+='0|1|0|'
			if tit_name == 'DLC':
				DLCnumb=str(titleid)
				DLCnumb="0000000000000"+DLCnumb[-3:]
				DLCnumb=bytes.fromhex(DLCnumb)
				DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
				DLCnumb=int(DLCnumb)
				tit_name="DLC Numb. "+str(DLCnumb)
		elif content_type == 'Application' and isdemo!=0:
			dbstr+='0|0|1|'
		elif content_type == 'Patch' and isdemo!=0:
			dbstr+='1|0|1|'
		elif content_type == 'Application':
			dbstr+='0|0|1|'
		elif content_type == 'Patch':
			dbstr+='1|0|1|'
		else:
			dbstr+='-|'
		dbstr+=str(tit_name)+'|'
		dbstr+=str(tit_name)+'|'
		dbstr+=str(version)+'|'
		if regionstr[0]=="1" and regionstr[2]=="0":
			Regionvar="US"
		elif regionstr[0]=="1" and regionstr[2]=="1":
			Regionvar="WORLD"
		elif regionstr[0]=="0" and (regionstr[2]=="1" or regionstr[6]=="1" or regionstr[8]=="1" or regionstr[12]=="1" or regionstr[14]=="1" or regionstr[16]=="1" or regionstr[20]=="1"):
			Regionvar="EUR"
		elif regionstr[4]=="1" and (regionstr[24]=="1" or regionstr[26]=="1" or regionstr[28]=="1"):
			Regionvar="AS"
		elif regionstr[4]=="1" and (regionstr[0]=="0" or regionstr[2]=="0"):
			Regionvar="JAP"
		else:
			Regionvar="-"
		dbstr+=Regionvar
		return dbstr

	def simplbstr(self,titlerights,ckey,tit_name):
		dbstr=str()
		dbstr+=str(titlerights).upper()+'|'
		dbstr+=str(ckey).upper()+'|'
		dbstr+=str(tit_name)
		return dbstr

	def appendtodb(self,dbstring,ofile,dbtype):
		if dbtype == 'extended':
			initdb='id|rightsId|keygeneration|RSV|RGV|key|ContentType|baseName|editor|version|cversion|metasdkversion|exesdkversion|us|uk|jp|fr|de|lat|spa|it|du|cad|por|ru|kor|tai|ch'
		if dbtype == 'keyless':
			initdb='id|rightsId|keygeneration|RSV|RGV|ContentType|baseName|editor|version|cversion|metasdkversion|exesdkversion|us|uk|jp|fr|de|lat|spa|it|du|cad|por|ru|kor|tai|ch'
		if dbtype == 'nutdb':
			initdb='id|rightsId|key|isUpdate|isDLC|isDemo|baseName|name|version|region'
		if dbtype == 'simple':
			initdb='rightsId|key|name'
		if not os.path.exists(ofile):
			with open(ofile, 'a') as dbfile:
				dbfile.write(initdb+ '\n')
		with open(ofile, 'ab') as dbfile:
			print(dbstring)
			dbfile.write(dbstring.encode('utf-8'))
		with open(ofile, 'a') as dbfile:
			dbfile.write('\n')

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

		for file in self:
			if type(file) == Ticket:
				masterKeyRev = file.getMasterKeyRevision()
				titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
				rightsId = file.getRightsId()
		for file in self:
			if type(file) == Nca:
				if file.header.getRightsId() != 0:
					if file.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(file._path)} - {file.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")
		for file in self:
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
		for nca in self:
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

		for nca in self:
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
							inmemoryfile = io.BytesIO(newheader)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(newheader)-n2)
							inmemoryfile.close()
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
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
							outf.write(dat2)
							t.update(len(dat2))
							outf.flush()
						else:
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
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
				outfolder = str(ofolder)+'/'
				filepath = os.path.join(outfolder, filename)
				if not os.path.exists(outfolder):
					os.makedirs(outfolder)
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
								else:
									target.close()
									self.patcher_meta(filepath,RSV_cap,t)
				target = Fs.Nca(filepath, 'r+b')
				target.rewind()
				size=os.path.getsize(filepath)
				t.write(tabs+'- Appending: ' + str(nca._path))
				for data in iter(lambda: target.read(int(size)), ""):
					if fat=="fat32" and (c+len(data))>block:
						n2=block-c
						c=0
						inmemoryfile = io.BytesIO()
						inmemoryfile.write(data)
						inmemoryfile.seek(0)
						dat2=inmemoryfile.read(n2)
						outf.write(dat2)
						outf.flush()
						outf.close()
						t.update(len(dat2))
						index=index+1
						outfile=outfile[0:-1]
						outfile=outfile+str(index)
						outf = open(outfile, 'wb')
						inmemoryfile.seek(n2)
						dat2=inmemoryfile.read(len(data)-n2)
						inmemoryfile.close()
						outf.write(dat2)
						t.update(len(dat2))
						outf.flush()
					else:
						outf.write(data)
						t.update(len(data))
						c=c+len(data)
						outf.flush()
					if not data:
						target.close()
						break
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



	def metapatcher(self,number):
		for nca in self:
			if type(nca) == Nca:
				if str(nca.header.contentType) == 'Content.META':
					filename=nca
					try:
						f = Fs.Nca(filename, 'r+b')
						f.write_req_system(number)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha=f.calc_pfs0_hash()
						f.flush()
						f.close()
						f = Fs.Nca(filename, 'r+b')
						f.set_pfs0_hash(sha)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha2=f.calc_htable_hash()
						f.flush()
						f.close()
						f = Fs.Nca(filename, 'r+b')
						f.header.set_htable_hash(sha2)
						f.flush()
						f.close()
						########################
						f = Fs.Nca(filename, 'r+b')
						sha3=f.header.calculate_hblock_hash()
						f.flush()
						f.close()
						f = Fs.Nca(filename, 'r+b')
						f.header.set_hblock_hash(sha3)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))


	def get_xciheader(self,delta):
		upd_list=list()
		upd_fileSizes = list()
		norm_list=list()
		norm_fileSizes = list()
		sec_list=list()
		sec_fileSizes = list()
		sec_shalist = list()
		for file in self:
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
			Keys.get('xci_header_key')
			key= Keys.get('xci_header_key')
			key= bytes.fromhex(key)
			IV=sq_tools.randhex(0x10)
			IV= bytes.fromhex(IV)
			xkey=True
			#print(hx(IV))
		except:
			IV=(0x5B408B145E277E81E5BF677C94888D7B).to_bytes(16, byteorder='big')
			xkey=False

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

#///////////////////////////////////////////////////
# Change MKREV_NCA
#///////////////////////////////////////////////////

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

	def rebuild(self,buffer,filepath,delta,ndskip,xml_gen):
		ofolder=os.path.dirname(os.path.abspath(filepath))
		if ndskip==True:
			vfragment=False
			for nca in self:
				if type(nca) == Nca:
					if 	str(nca.header.contentType) == 'Content.DATA':
						try:
							for f in nca:
									for file in f:
										filename = str(file._path)
										if filename=="fragment":
											vfragment=True
											break
						except:
							pass
			if vfragment != True:
				print("> File doesn't have deltas. Skipping")
				return
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		xmlsize=0
		self.rewind()
		for file in self:
			completefilelist.append(str(file._path))
		self.rewind()
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
							content_type=str(cnmt._path)
							content_type=content_type[:-22]
							titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
							titleid2 = titleid2[2:-1]
							cnmt.seek(0x20)
							if content_type=='Application':
								original_ID=cnmt.readInt64()
								original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
								original_ID = original_ID[2:-1]
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
								print(titleid2+' is not an update. Skipping')
								continue
							cnmt.seek(0x20+offset)
							for i in range(content_entries):
								vhash = cnmt.read(0x20)
								NcaId = cnmt.read(0x10)
								size = cnmt.read(0x6)
								ncatype = cnmt.readInt8()
								unknown = cnmt.read(0x1)
							#**************************************************************
								version=str(int.from_bytes(titleversion, byteorder='little'))
								version='[v'+version+']'
								titleid3 ='['+ titleid2+']'
								nca_name=str(hx(NcaId))
								nca_name=nca_name[2:-1]+'.nca'
								if nca_name in completefilelist:
									if ncatype==6 and delta==False:
										print('Skipping delta fragment '+nca_name)
										continue
									else:
										contentlist.append(nca_name)
							nca_meta=str(nca._path)
							if nca_meta in completefilelist:
								contentlist.append(nca_meta)
								if xml_gen == True:
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
									xml=target.xml_gen(ofolder,nsha)
									xmlname=nca_meta[:-3]+'xml'
									xmlsize=xmlsize+os.path.getsize(xml)
									contentlist.append(xmlname)
									target.close()
									try:
										os.remove(outf)
									except:
										pass
							for f in completefilelist:
								if f.endswith('.tik') or f.endswith('.cert'):
									test=f[0:16]
									if titleid2==test:
										contentlist.append(f)

		filesNb = len(contentlist)
		stringTable = '\x00'.join(str(file) for file in contentlist)
		headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
		remainder = 0x10 - headerSize%0x10
		headerSize += remainder

		fileSizes = list()
		self.rewind()
		for f in contentlist:
			if not f.endswith('.xml'):
				for file in self:
					if file._path==f:
						fileSizes.append(file.size)
			elif f.endswith('.xml'):
				xmlfile= os.path.join(ofolder, f)
				fileSizes.append(os.path.getsize(xmlfile))
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		fileNamesLengths = [len(str(file))+1 for file in contentlist] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]

		hd =  b''
		hd += b'PFS0'
		hd += pk('<I', filesNb)
		hd += pk('<I', len(stringTable)+remainder)
		hd += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			hd += pk('<Q', fileOffsets[n])
			hd += pk('<Q', fileSizes[n])
			hd += pk('<I', stringTableOffsets[n])
			hd += b'\x00\x00\x00\x00'
		hd += stringTable.encode()
		hd += remainder * b'\x00'

		totSize = len(hd)+xmlsize
		for f in contentlist:
			if not f.endswith('.xml'):
				for file in self:
					if file._path==f:
						totSize=totSize+file.size

		indent = 1
		rightsId = 0
		tabs = '\t' * indent

		Print.info("")
		Print.info('Generating NSP:')
		Print.info('Filename: '+filepath)
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing header...')
		outf = open(str(filepath), 'w+b')
		outf.write(hd)
		t.update(len(hd))
		for f in contentlist:
			if not f.endswith('.xml'):
				for file in self:
					if file._path==f:
						file.rewind()
						t.write(tabs+'- Appending: ' + str(file._path))
						for data in iter(lambda: file.read(int(buffer)), ""):
							outf.write(data)
							t.update(len(data))
							outf.flush()
							if not data:
								break
			elif f.endswith('.xml'):
				t.write(tabs+'- Appending: ' + f)
				dir=os.path.dirname(os.path.abspath(filepath))
				xmlfile= os.path.join(dir, f)
				xml = open(xmlfile, 'rb')
				data=xml.read()
				xml.close()
				outf.write(data)
				t.update(len(data))
				outf.flush()
				try:
					os.remove(xmlfile)
				except:
					pass
		t.close()
		print("Closing file. Please wait")
		outf.close()


	def sp_groupncabyid_ND(self,buffer,ofolder,fat,fx,incxml):
		vfragment=False
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.DATA':
					for f in nca:
							for file in f:
								filename = str(file._path)
								if filename=="fragment":
									vfragment=True
									break
		if vfragment != True:
			print("> File doesn't have deltas. Skipping")
			return
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		for file in self:
			completefilelist.append(str(file._path))
		for nca in self:
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
								original_ID=cnmt.readInt64()
								original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
								original_ID = original_ID[2:-1]
								ttag=''
								CTYPE='BASE'
								if incxml != "special":
									print(titleid2+' is not an update. Skipping')
									continue
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
								if incxml != "special":
									print(titleid2+' is not an update. Skipping')
									continue
							else:
								print(titleid2+' is not an update. Skipping')
								continue
							cnmt.seek(0x20+offset)
							for i in range(content_entries):
								vhash = cnmt.read(0x20)
								NcaId = cnmt.read(0x10)
								size = cnmt.read(0x6)
								ncatype = cnmt.readInt8()
								unknown = cnmt.read(0x1)
							#**************************************************************
								version=str(int.from_bytes(titleversion, byteorder='little'))
								version='[v'+version+']'
								titleid3 ='['+ titleid2+']'
								nca_name=str(hx(NcaId))
								nca_name=nca_name[2:-1]+'.nca'
								if nca_name in completefilelist:
									if ncatype==6:
										print('Skipping delta fragment '+nca_name)
										continue
									else:
										ncalist.append(nca_name)
							nca_meta=str(nca._path)
							if nca_meta in completefilelist:
								ncalist.append(nca_meta)
							target=str(nca._path)
							tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)
							tit_name = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', tit_name))
							tit_name = tit_name.strip()
							if tit_name=='DLC' and (str(titleid2).endswith('000') or str(titleid2).endswith('800')):
								tit_name='-'
								editor='-'
							tid='['+titleid2+']'
							tid=tid.upper()
							filename=tit_name+' '+tid+' '+version
							titlerights=titleid2+str('0'*15)+str(crypto2)
							contentlist.append([filename,titleid2,titlerights,keygen,ncalist,CTYPE])

		for file in self:
			if type(file) == Ticket or file._path.endswith('.cert'):
				test=file._path
				test=test[0:32]
				for i in contentlist:
					if i[2]==test:
						i[4].append(file._path)
			elif file._path.endswith('.xml') and incxml==True:
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
			self.cd_spl_nsp_ND(buffer,i[0],ofolder,i[4],fat,fx)

	def cd_spl_nsp_ND(self,buffer,ofile,ofolder,filelist,fat,fx):
		self.rewind()
		outfile=ofile+'.nsp'
		filepath = os.path.join(ofolder, outfile)
		if os.path.exists(filepath) and os.path.getsize(filepath) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)
		self.rewind()

		contentlist=list()
		for file in self:
			if file._path in filelist:
				contentlist.append(file._path)

		hd = self.cd_spl_gen_nsph(contentlist)
		totSize = len(hd)
		for file in self:
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
		for file in self:
			if file._path in contentlist:
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


	def get_content(self,ofolder,vkeypatch,delta):
		indent = 1
		tabs = '\t' * indent
		if vkeypatch=='false':
			vkeypatch=False
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		for file in self:
			completefilelist.append(str(file._path))
		for nca in self:
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

		for file in self:
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


	def get_content_placeholder(self,ofolder):
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		for file in self:
			if type(file) == Nca:
				if 	str(file.header.contentType) != 'Content.META' and str(file.header.contentType) != 'Content.CONTROL':
					continue
				else:
					completefilelist.append(str(file._path))
			elif str(file._path).endswith('.xml'):
				pass
			else:
				completefilelist.append(str(file._path))
		print (completefilelist)
		for nca in self:
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
								ncatype = cnmt.read(0x1)
								unknown = cnmt.read(0x1)
							#**************************************************************
								version=str(int.from_bytes(titleversion, byteorder='little'))
								ver=version
								ver='[v'+ver+']'
								titleid3 ='['+ titleid2+']'
								nca_name=str(hx(NcaId))
								nca_name=nca_name[2:-1]+'.nca'
								if nca_name in completefilelist:
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
									xml=target.xml_gen(ofolder,nsha)
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

		for file in self:
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

	def append_content(self,outf,target,buffer,t,fat='exfat',fx='files',c=0,index=0):
		block=4294934528
		indent = 1
		tabs = '\t' * indent
		for file in self:
			if str(file._path) == target:
				if type(file) == Nca:
					fp = open(outf, 'a+b')
					file.rewind()
					t.write(tabs+'- Appending: ' + str(file._path))
					for data in iter(lambda: file.read(int(buffer)), ""):
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							fp.write(dat2)
							fp.flush()
							fp.close()
							t.update(len(dat2))
							index=index+1
							outf=outf[0:-1]
							outf=outf+str(index)
							fp = open(outf, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
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
					if str(file.header.contentType) == 'Content.META':
						target=str(file._path)
						xmlname=target[:-3]+'xml'
						t.write(tabs+'- Appending: ' + xmlname)
						dir=os.path.dirname(os.path.abspath(outf))
						xmlfile= os.path.join(dir, xmlname)
						xml = open(xmlfile, 'rb')
						data=xml.read()
						xml.close()
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							fp.write(dat2)
							fp.flush()
							fp.close()
							t.update(len(dat2))
							index=index+1
							outf=outf[0:-1]
							outf=outf+str(index)
							fp = open(outf, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
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
					fp = open(outf, 'a+b')
					file.rewind()
					t.write(tabs+'- Appending: ' + str(file._path))
					for data in iter(lambda: file.read(int(buffer)), ""):
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							fp.write(dat2)
							fp.flush()
							fp.close()
							t.update(len(dat2))
							index=index+1
							outf=outf[0:-1]
							outf=outf+str(index)
							fp = open(outf, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
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
		for file in self:
			if type(file) == Ticket:
				masterKeyRev = file.getMasterKeyRevision()
				titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
				rightsId = str(hx(file.getRightsId().to_bytes(16, byteorder='big')))
				encryptedkey=file.getTitleKeyBlock().to_bytes(16, byteorder='big')
				ticketlist.append([masterKeyRev,rightsId,encryptedkey])
		for file in self:
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
									inmemoryfile = io.BytesIO()
									inmemoryfile.write(newheader)
									inmemoryfile.seek(0)
									dat2=inmemoryfile.read(n2)
									fp.write(dat2)
									fp.flush()
									fp.close()
									t.update(len(dat2))
									index=index+1
									outf=outf[0:-1]
									outf=outf+str(index)
									fp = open(outf, 'wb')
									inmemoryfile.seek(n2)
									dat2=inmemoryfile.read(len(newheader)-n2)
									inmemoryfile.close()
									fp.write(dat2)
									t.update(len(dat2))
									c=c+len(dat2)
									fp.flush()
									sha.update(newheader)
									file.seek(0xC00)
								else:
									fp.write(newheader)
									t.update(len(newheader))
									c=c+len(newheader)
									sha.update(newheader)
									file.seek(0xC00)
									i+=1
									fp.flush()
							else:
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									inmemoryfile = io.BytesIO()
									inmemoryfile.write(data)
									inmemoryfile.seek(0)
									dat2=inmemoryfile.read(n2)
									fp.write(dat2)
									fp.flush()
									fp.close()
									t.update(len(dat2))
									index=index+1
									outf=outf[0:-1]
									outf=outf+str(index)
									fp = open(outf, 'wb')
									inmemoryfile.seek(n2)
									dat2=inmemoryfile.read(len(data)-n2)
									inmemoryfile.close()
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
									inmemoryfile = io.BytesIO()
									inmemoryfile.write(newheader)
									inmemoryfile.seek(0)
									dat2=inmemoryfile.read(n2)
									fp.write(dat2)
									fp.flush()
									fp.close()
									t.update(len(dat2))
									index=index+1
									outf=outf[0:-1]
									outf=outf+str(index)
									fp = open(outf, 'wb')
									inmemoryfile.seek(n2)
									dat2=inmemoryfile.read(len(newheader)-n2)
									inmemoryfile.close()
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
									fp.flush()
							else:
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									inmemoryfile = io.BytesIO()
									inmemoryfile.write(data)
									inmemoryfile.seek(0)
									dat2=inmemoryfile.read(n2)
									fp.write(dat2)
									fp.flush()
									fp.close()
									t.update(len(dat2))
									index=index+1
									outf=outf[0:-1]
									outf=outf+str(index)
									fp = open(outf, 'wb')
									inmemoryfile.seek(n2)
									dat2=inmemoryfile.read(len(data)-n2)
									inmemoryfile.close()
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
								inmemoryfile = io.BytesIO()
								inmemoryfile.write(data)
								inmemoryfile.seek(0)
								dat2=inmemoryfile.read(n2)
								fp.write(dat2)
								fp.flush()
								fp.close()
								t.update(len(dat2))
								index=index+1
								outf=outf[0:-1]
								outf=outf+str(index)
								fp = open(outf, 'wb')
								inmemoryfile.seek(n2)
								dat2=inmemoryfile.read(len(data)-n2)
								inmemoryfile.close()
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
								xmlfile= os.path.join(dir, xmlname)
								xml = open(xmlfile, 'rb')
								data=xml.read()
								xml.close()
								if fat=="fat32" and (c+len(data))>block:
									n2=block-c
									c=0
									inmemoryfile = io.BytesIO()
									inmemoryfile.write(data)
									inmemoryfile.seek(0)
									dat2=inmemoryfile.read(n2)
									fp.write(dat2)
									fp.flush()
									fp.close()
									t.update(len(dat2))
									index=index+1
									outf=outf[0:-1]
									outf=outf+str(index)
									fp = open(outf, 'wb')
									inmemoryfile.seek(n2)
									dat2=inmemoryfile.read(len(data)-n2)
									inmemoryfile.close()
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
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							fp.write(dat2)
							fp.flush()
							fp.close()
							t.update(len(dat2))
							index=index+1
							outf=outf[0:-1]
							outf=outf+str(index)
							fp = open(outf, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
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
		try:
			fp.close()
		except:pass
		return outf,index,c

	def sp_groupncabyid(self,buffer,ofolder,fat,fx,export):
		contentlist=list()
		ncalist=list()
		completefilelist=list()
		for file in self:
			completefilelist.append(str(file._path))
		for nca in self:
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
							if tit_name=='DLC' and (str(titleid2).endswith('000') or str(titleid2).endswith('800')):
								tit_name='-'
								editor='-'
							filename=tit_name+' '+titleid3+' '+version
							titlerights=titleid2+str('0'*15)+str(crypto2)
							contentlist.append([filename,titleid2,titlerights,keygen,ncalist,CTYPE])

		for file in self:
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

	def cd_spl_nsp(self,buffer,ofile,ofolder,filelist,fat,fx):
		self.rewind()
		outfile=ofile+'.nsp'
		filepath = os.path.join(ofolder, outfile)
		if os.path.exists(filepath) and os.path.getsize(filepath) == totSize:
			Print.info('\t\tRepack %s is already complete!' % outfile)
			return
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)
		self.rewind()

		contentlist=list()
		for file in self:
			if file._path in filelist:
				contentlist.append(file._path)

		hd = self.cd_spl_gen_nsph(contentlist)
		totSize = len(hd)
		for file in self:
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
		outfile=str(filepath)
		outf.write(hd)
		t.update(len(hd))
		c=c+len(hd)
		block=4294901760
		for file in self:
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
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(newheader)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(newheader)-n2)
							inmemoryfile.close()
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
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
							outf.write(dat2)
							t.update(len(dat2))
							outf.flush()
						else:
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
							outf.flush()
						if not data:
							break
			if type(file) != Nca and file._path in contentlist:
				file.rewind()
				t.write(tabs+'- Appending: ' + str(file._path))
				for data in iter(lambda: file.read(int(buffer)), ""):
					if fat=="fat32" and (c+len(data))>block:
						n2=block-c
						c=0
						inmemoryfile = io.BytesIO()
						inmemoryfile.write(data)
						inmemoryfile.seek(0)
						dat2=inmemoryfile.read(n2)
						outf.write(dat2)
						outf.flush()
						outf.close()
						t.update(len(dat2))
						index=index+1
						outfile=outfile[0:-1]
						outfile=outfile+str(index)
						outf = open(outfile, 'wb')
						inmemoryfile.seek(n2)
						dat2=inmemoryfile.read(len(data)-n2)
						inmemoryfile.close()
						outf.write(dat2)
						t.update(len(dat2))
						outf.flush()
					else:
						outf.write(data)
						t.update(len(data))
						c=c+len(data)
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
		for file in self:
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

	def cd_spl_xci(self,buffer,ofile,ofolder,filelist,fat,fx):
		self.rewind()
		outfile=ofile+'.xci'
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
		for file in self:
			if type(file) == Nca:
				if file._path in filelist:
					contentlist.append(file._path)

		xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=self.cd_spl_gen_xcih(contentlist)
		totSize=len(xci_header)+len(game_info)+len(sig_padding)+len(xci_certificate)+rootSize

		for file in self:
			if type(file) == Ticket and file._path in filelist:
				masterKeyRev = file.getMasterKeyRevision()
				titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
				rightsId = file.getRightsId()
		for file in self:
			if type(file) == Nca and file._path in filelist:
				if file.header.getRightsId() != 0:
					if file.header.masterKeyRev != masterKeyRev:
						print('WARNING!!! Mismatched masterKeyRevs!')
						print(f"{str(file._path)} - {file.header.masterKeyRev}")
						print(f"{str(ticket._path)} - {masterKeyRev}")
		for file in self:
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
		for nca in self:
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

		if totSize <= 4294934528:
			fat="exfat"
		if fat=="fat32":
			splitnumb=math.ceil(totSize/4294934528)
			index=0
			filepath=filepath[:-1]+str(index)

		outfile=str(filepath)
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
		for nca in self:
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
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(newheader)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(newheader)-n2)
							inmemoryfile.close()
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
						if fat=="fat32" and (c+len(data))>block:
							n2=block-c
							c=0
							inmemoryfile = io.BytesIO()
							inmemoryfile.write(data)
							inmemoryfile.seek(0)
							dat2=inmemoryfile.read(n2)
							outf.write(dat2)
							outf.flush()
							outf.close()
							t.update(len(dat2))
							index=index+1
							outfile=outfile[0:-1]
							outfile=outfile+str(index)
							outf = open(outfile, 'wb')
							inmemoryfile.seek(n2)
							dat2=inmemoryfile.read(len(data)-n2)
							inmemoryfile.close()
							outf.write(dat2)
							t.update(len(dat2))
							outf.flush()
						else:
							outf.write(data)
							t.update(len(data))
							c=c+len(data)
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
		for file in self:
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


	def file_hash(self,target):
		indent = 1
		gamecard = False
		tabs = '\t' * indent
		sha=False;sizef=False
		for file in self:
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

	def verify(self):
		contentlist=list()
		validfiles=list()
		listed_files=list()
		contentlist=list()
		feed=''
		delta = False
		verdict = True
		checktik=False
		feed=self.html_feed(feed,2,message=('DECRYPTION TEST:'))
		for file in self:
			if str(file._path).endswith('.nca'):
				listed_files.append(str(file._path))
			if type(file) == Nca:
				validfiles.append(str(file._path))
			if str(file._path).endswith('.ncz'):
				listed_files.append(str(file._path))
				validfiles.append(str(file._path))
		for file in self:
			if str(file._path).endswith('.tik'):
				listed_files.append(str(file._path))
			if type(file) == Ticket:
				validfiles.append(str(file._path))

		for file in listed_files:
			correct=False;baddec=False
			if file in validfiles:
				if file.endswith('cnmt.nca'):
					for f in self:
						if str(f._path) == file:
							message=(str(f.header.titleId)+' - '+str(f.header.contentType));feed+=message+'\n'
							for nf in f:
								nf.rewind()
								test=nf.read(0x4)
								#print(test)
								if str(test) == "b'PFS0'":
									correct=True
									break
							if correct == True:
								correct = self.verify_enforcer(file)
				elif file.endswith('.nca'):
					for f in self:
						if str(f._path) == file:
							message=(str(f.header.titleId)+' - '+str(f.header.contentType));feed+=message+'\n'
							if str(f.header.contentType) != 'Content.PROGRAM':
								correct = self.verify_enforcer(file)
								if correct == True:
									if str(f.header.contentType) == 'Content.PUBLIC_DATA' and f.header.getRightsId() == 0:
										correct = f.pr_noenc_check_dlc()
										if correct == False:
											baddec=True
							else:
								for nf in f:
									try:
										nf.rewind()
										test=nf.read(0x4)
										if str(test) == "b'PFS0'":
											correct=True
											break
									except:
										print(f"{tabs} Error reading {nf}" )
										pass
									f.rewind()
								if correct == True:
									correct = self.verify_enforcer(file)
								if correct == False and f.header.getRightsId() == 0:
									correct = f.pr_noenc_check()
								if correct == False and f.header.getRightsId() != 0:
									correct,tk = self.verify_nca_key(file)
								if correct == True and f.header.getRightsId() == 0:
									correct = f.pr_noenc_check()
									if correct == False:
										baddec=True
				elif file.endswith('.ncz'):
					for f in self:
						if str(f._path)[:-1] == file[:-1]:
							ncztype=Nca(f)
							ncztype._path=f._path
							message=(str(ncztype.header.titleId)+' - '+str(ncztype.header.contentType));feed+=message+'\n'
							correct=self.verify_ncz(file)
							break
				elif file.endswith('.tik'):
					tikfile=str(file)
					checktik == False
					for f in self:
						if str(f._path).endswith('.nca'):
							if checktik == False and f.header.getRightsId() != 0:
								checktik = self.verify_key(str(f._path),tikfile)
								if 	checktik == True:
									break
					if checktik==False and str(self._path).endswith('.nsz'):
						checktik='nsz'
					else:
						message=('Content.TICKET');feed+=message+'\n'
					correct = checktik
				else:
					correct=False
			if correct==True:
				if file.endswith('cnmt.nca'):
					message=(tabs+file+' -> is CORRECT');feed+=message+'\n'
				else:
					message=(tabs+file+tabs+'  -> is CORRECT');feed+=message+'\n'
			elif correct=='ncz':
				message=(tabs+file+tabs+'  -> ncz file needs HASH check');feed+=message+'\n'
			elif correct=='nsz':
				pass
			else:
				verdict=False
				if file.endswith('cnmt.nca'):
					message=(tabs+file+' -> is CORRUPT <<<-');feed+=message+'\n'
				elif file.endswith('nca'):
					message=(tabs+file+tabs+'  -> is CORRUPT <<<-');feed+=message+'\n'
					if baddec == True:
						message=(tabs+'  * NOTE: S.C. CONVERSION WAS PERFORMED WITH BAD KEY');feed+=message+'\n'
				elif file.endswith('tik') and not str(self._path).endswith('.nsz'):
					message=(tabs+file+tabs+'  -> titlekey is INCORRECT <<<-');feed+=message+'\n'
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					for f in nca:
						for cnmt in f:
							nca.rewind()
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
								ncz_name=nca_name[:-4]+'.ncz'
								if (nca_name not in listed_files and ncatype!=6) or (nca_name not in validfiles and ncatype!=6):
									if ncz_name not in listed_files:
										verdict = False
										message=('\n- Missing file from '+titleid2+': '+nca_name);feed+=message+'\n'

		ticketlist=list()
		for ticket in self:
			if type(ticket) == Ticket:
				ticketlist.append(str(ticket._path))
		titlerights=list()
		for nca in self:
			if type(nca) == Nca:
				if nca.header.getRightsId() != 0:
					rightsId = hx(nca.header.getRightsId().to_bytes(0x10, byteorder='big')).decode('utf-8').lower()
					if rightsId not in titlerights:
						titlerights.append(rightsId)
						mtick=rightsId+'.tik'
						if mtick not in ticketlist:
							message=('\n- File has titlerights!!! Missing ticket: '+mtick);feed+=message+'\n'
							verdict = False

		if str(self.path).endswith('.nsz'):
			token='NSZ'
		elif str(self.path).endswith('.nsx'):
			token='NSX'
		elif str(self.path).endswith('.nsp'):
			token='NSP'
		else:
			token='NSP'
		if verdict == False:
			message='\nVERDICT: {} FILE IS CORRUPT OR MISSES FILES\n'.format(token);feed+=message+'\n'
		if verdict == True:
			message='\nVERDICT: {} FILE IS CORRECT\n'.format(token);feed+=message
		return verdict,feed

	def verify_sig(self,feed,tmpfolder):
		hlisthash=False
		if feed == False:
			feed=''
		verdict=True
		headerlist=list()
		keygenerationlist=list()
		feed=self.html_feed(feed,2,message=('\nSIGNATURE 1 TEST:'))
		for f in self:
			if type(f) == Nca and f.header.contentType != Type.Content.META:
				message=(str(f.header.titleId)+' - '+str(f.header.contentType));feed+=message+'\n'
				verify,origheader,ncaname,feed,origkg,tr,tkey,iGC=f.verify(feed)
				# headerlist.append([ncaname,origheader,hlisthash])
				headerlist.append([ncaname,origheader,hlisthash,tr,tkey,iGC])
				keygenerationlist.append([ncaname,origkg])
				if verdict == True:
					verdict=verify
				message='';feed+=message+'\n'
			if str(f._path).endswith('.ncz'):
				ncz=Nca(f)
				ncz._path=f._path
				message=(str(ncz.header.titleId)+' - '+str(ncz.header.contentType));feed+=message+'\n'
				verify,origheader,ncaname,feed,origkg,tr,tkey,iGC=ncz.verify(feed)
				# headerlist.append([ncaname,origheader,hlisthash])
				headerlist.append([ncaname,origheader,hlisthash,tr,tkey,iGC])
				keygenerationlist.append([ncaname,origkg])
				if verdict == True:
					verdict=verify
				message='';feed+=message+'\n'
		for f in self:
			if type(f) == Nca and f.header.contentType == Type.Content.META:
				meta_nca=f._path
				f.rewind();meta_dat=f.read()
				message=(str(f.header.titleId)+' - '+str(f.header.contentType));feed+=message+'\n'
				targetkg,minrsv=self.find_addecuatekg(meta_nca,keygenerationlist)
				verify,origheader,ncaname,feed,origkg,tr,tkey,iGC=f.verify(feed)
				#print(targetkg)
				if verify == False:
					tempfile=os.path.join(tmpfolder,meta_nca)
					if not os.path.exists(tmpfolder):
						os.makedirs(tmpfolder)
					fp = open(tempfile, 'w+b')
					fp.write(meta_dat);fp.flush();fp.close()
					kglist=sq_tools.kgstring()
					numb=0;topkg=len(kglist)
					for kg in kglist:
						topkg-=1
						if topkg >= origkg:
							for verNumber in kg:
								numb+=1
					cnmtdidverify=False
					t = tqdm(total=numb, unit='RSV', unit_scale=True, leave=False)
					topkg=len(kglist)
					for kg in kglist:
						if cnmtdidverify == True:
							break
						topkg-=1
						#print(topkg)
						if topkg >= origkg:
							c=0;rsv_endcheck=False
							for verNumber in kg:
								c+=1
								if topkg == origkg:
									if c == len(kg):
										rsv_endcheck=True
								#print(verNumber)
								fp = Fs.Nca(tempfile, 'r+b')
								fp.write_req_system(verNumber)
								fp.flush()
								fp.close()
								############################
								fp = Fs.Nca(tempfile, 'r+b')
								sha=fp.calc_pfs0_hash()
								fp.flush()
								fp.close()
								fp = Fs.Nca(tempfile, 'r+b')
								fp.set_pfs0_hash(sha)
								fp.flush()
								fp.close()
								############################
								fp = Fs.Nca(tempfile, 'r+b')
								sha2=fp.calc_htable_hash()
								fp.flush()
								fp.close()
								fp = Fs.Nca(tempfile, 'r+b')
								fp.header.set_htable_hash(sha2)
								fp.flush()
								fp.close()
								########################
								fp = Fs.Nca(tempfile, 'r+b')
								sha3=fp.header.calculate_hblock_hash()
								fp.flush()
								fp.close()
								fp = Fs.Nca(tempfile, 'r+b')
								fp.header.set_hblock_hash(sha3)
								fp.flush()
								fp.close()
								fp = Fs.Nca(tempfile, 'r+b')
								progress=True
								verify,origheader,ncapath,feed,origkg,tr,tkey,iGC=fp.verify(feed,targetkg,rsv_endcheck,progress,t)
								fp.close()
								t.update(1)
								if verify == True:
									t.close()
									message=(tabs+'* '+"RSV WAS CHANGED FROM "+str(verNumber)+" TO "+str(minrsv));feed+=message+'\n'
									message=(tabs+'* '+"THE CNMT FILE IS CORRECT");feed+=message+'\n'
									if origheader != False:
										hlisthash=True;i=0
										fp = Fs.Nca(tempfile, 'r+b')
										for data in iter(lambda: fp.read(int(32768)), ""):
											if i==0:
												sha0=sha256()
												sha0.update(origheader)
												i+=1
												fp.flush()
												fp.seek(0xC00)
											else:
												sha0.update(data)
												fp.flush()
												if not data:
													fp.close()
													cnmtdidverify=True
													break
									break
						else:break
				try:
					t.close()
				except:pass
				if hlisthash == True:
					sha0=sha0.hexdigest()
					hlisthash=sha0
				headerlist.append([ncaname,origheader,hlisthash,tr,tkey,iGC])
				message='';feed+=message+'\n'
		try:
			shutil.rmtree(tmpfolder)
		except:pass
		if str(self.path).endswith('.nsz'):
			token='NSZ'
		elif str(self.path).endswith('.nsx'):
			token='NSX'
		elif str(self.path).endswith('.nsp'):
			token='NSP'
		else:
			token='NSP'
		if verdict == False:
			message=("VERDICT: {} FILE COULD'VE BEEN TAMPERED WITH").format(token);feed+=message+'\n'
		if verdict == True:
			message=('VERDICT: {}  FILE IS SAFE').format(token);feed+=message+'\n'
		return 	verdict,headerlist,feed


	def find_addecuatekg(self,ncameta,keygenerationlist):
		ncalist=list()
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					if nca._path == ncameta:
						for f in nca:
							for cnmt in f:
								nca.rewind()
								cnmt.rewind()
								titleid=cnmt.readInt64()
								titleversion = cnmt.read(0x4)
								cnmt.rewind()
								cnmt.seek(0xE)
								offset=cnmt.readInt16()
								content_entries=cnmt.readInt16()
								cnmt.seek(0x20)
								original_ID=cnmt.readInt64()
								min_sversion=cnmt.readInt32()
								cnmt.seek(0x20+offset)
								for i in range(content_entries):
									vhash = cnmt.read(0x20)
									NcaId = cnmt.read(0x10)
									ncaname=(str(hx(NcaId)))[2:-1]+'.nca'
									for i in range(len(keygenerationlist)):
										if ncaname == keygenerationlist[i][0]:
											if keygenerationlist[i][1] != False:
												return keygenerationlist[i][1],min_sversion
									else:
										size = cnmt.read(0x6)
										size=int.from_bytes(size, byteorder='little')
										ncatype = cnmt.readInt8()
										unknown = cnmt.read(0x1)
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					if nca._path == ncameta:
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto2>crypto1:
							keygeneration=crypto2
						if crypto2<=crypto1:
							keygeneration=crypto1
						return keygeneration,min_sversion
		return False,False


	def verify_hash_nca(self,buffer,headerlist,didverify,feed):
		verdict=True
		if feed == False:
			feed=''
		message='\n***************';print(message);feed+=message+'\n'
		message=('HASH TEST');print(message);feed+=message+'\n'
		message='***************';print(message);feed+=message+'\n'
		for f in self:
			if type(f) == Nca:
				origheader=False
				for i in range(len(headerlist)):
					if str(f._path)==headerlist[i][0]:
						origheader=headerlist[i][1]
						listedhash=headerlist[i][2]
						break
				message=(str(f.header.titleId)+' - '+str(f.header.contentType));print(message);feed+=message+'\n'
				ncasize=f.header.size
				t = tqdm(total=ncasize, unit='B', unit_scale=True, leave=False)
				i=0
				f.rewind();
				rawheader=f.read(0xC00)
				f.rewind()
				for data in iter(lambda: f.read(int(buffer)), ""):
					if i==0:
						sha=sha256()
						f.seek(0xC00)
						sha.update(rawheader)
						if origheader != False and listedhash == False:
							sha0=sha256()
							sha0.update(origheader)
						i+=1
						t.update(len(data))
						f.flush()
					else:
						sha.update(data)
						if origheader != False and listedhash == False:
							sha0.update(data)
						t.update(len(data))
						f.flush()
						if not data:
							break
				t.close()
				sha=sha.hexdigest()
				if listedhash != False:
					sha0=listedhash
				elif origheader != False:
					sha0=sha0.hexdigest()
				message=('  - File name: '+f._path);print(message);feed+=message+'\n'
				message=('  - SHA256: '+sha);print(message);feed+=message+'\n'
				if origheader != False:
					message=('  - ORIG_SHA256: '+sha0);print(message);feed+=message+'\n'
				if str(f._path)[:16] == str(sha)[:16]:
					message=('   > FILE IS CORRECT');print(message);feed+=message+'\n'
				elif origheader != False:
					if str(f._path)[:16] == str(sha0)[:16]:
						message=('   > FILE IS CORRECT');print(message);feed+=message+'\n'
					else:
						message=('   > FILE IS CORRUPT');print(message);feed+=message+'\n'
						verdict = False
				elif  f.header.contentType == Type.Content.META and didverify == True:
					message=('   > RSV WAS CHANGED');print(message);feed+=message+'\n'
					#print('   > CHECKING INTERNAL HASHES')
					message=('     * FILE IS CORRECT');print(message);feed+=message+'\n'
				else:
					message=('   > FILE IS CORRUPT');print(message);feed+=message+'\n'
					verdict = False
				message=('');print(message);feed+=message+'\n'
		if verdict == False:
			message=("VERDICT: NSP FILE IS CORRUPT");print(message);feed+=message+'\n'
		if verdict == True:
			message=('VERDICT: NSP FILE IS CORRECT');print(message);feed+=message+'\n'
		return 	verdict,feed

	def verify_enforcer(self,nca):

		for f in self:
			if str(f._path) == nca:
				if type(f) == Fs.Nca and f.header.contentType == Type.Content.PROGRAM:
					for fs in f.sectionFilesystems:
						if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
							f.seek(0)
							ncaHeader = f.read(0x400)

							sectionHeaderBlock = fs.buffer

							f.seek(fs.offset)
							pfs0Header = f.read(0x10)
							return True
						else:
							return False
				if type(f) == Fs.Nca and f.header.contentType == Type.Content.META:
					for fs in f.sectionFilesystems:
						if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
							f.seek(0)
							ncaHeader = f.read(0x400)

							sectionHeaderBlock = fs.buffer

							f.seek(fs.offset)
							pfs0Header = f.read(0x10)
							return True
						else:
							return False

				if type(f) == Fs.Nca:
					for fs in f.sectionFilesystems:
						if fs.fsType == Type.Fs.ROMFS and fs.cryptoType == Type.Crypto.CTR or f.header.contentType == Type.Content.MANUAL or f.header.contentType == Type.Content.DATA:
							f.seek(0)
							ncaHeader = f.read(0x400)

							sectionHeaderBlock = fs.buffer

							levelOffset = int.from_bytes(sectionHeaderBlock[0x18:0x20], byteorder='little', signed=False)
							levelSize = int.from_bytes(sectionHeaderBlock[0x20:0x28], byteorder='little', signed=False)

							offset = fs.offset + levelOffset

							f.seek(offset)
							pfs0Header = f.read(levelSize)
							return True
						else:
							return False

	def verify_nca_key(self,nca):
		check=False;titleKey=0
		for file in self:
			if (file._path).endswith('.tik'):
				titleKey = file.getTitleKeyBlock().to_bytes(16, byteorder='big')
				check=self.verify_key(nca,str(file._path))
				if check==True:
					break
		return check,titleKey

	def verify_key(self,nca,ticket):
		verticket=ticket
		for file in self:
			if type(file) == Nca:
				crypto1=file.header.getCryptoType()
				crypto2=file.header.getCryptoType2()
				if crypto1 == 2:
					if crypto1 > crypto2:
						masterKeyRev=file.header.getCryptoType()
					else:
						masterKeyRev=file.header.getCryptoType2()
				else:
					masterKeyRev=file.header.getCryptoType2()
				if str(file._path) == nca:
					break

		for file in self:
			if type(file) == Ticket:
				if ticket != False:
					if str(file._path) == ticket:
						titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
						rightsId = file.getRightsId()
						break
				else:
					ticket = str(file._path)
					titleKeyDec = Keys.decryptTitleKey(file.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(masterKeyRev))
					rightsId = file.getRightsId()

		decKey = titleKeyDec

		for f in self:
			if str(f._path) == nca:
				if type(f) == Fs.Nca and f.header.getRightsId() != 0:
					for fs in f.sectionFilesystems:
						#print(fs.fsType)
						#print(fs.cryptoType)
						if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
							f.seek(0)
							ncaHeader = NcaHeader()
							ncaHeader.open(MemoryFile(f.read(0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
							pfs0=fs
							sectionHeaderBlock = fs.buffer
							f.seek(fs.offset)
							pfs0Offset=fs.offset
							pfs0Header = f.read(0x10)
							#print(sectionHeaderBlock[8:12] == b'IVFC')
							if sectionHeaderBlock[8:12] == b'IVFC':
								#Hex.dump(self.sectionHeaderBlock)
								#Print.info(hx(self.sectionHeaderBlock[0xc8:0xc8+0x20]).decode('utf-8'))
								mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
								data = mem.read();
								#Hex.dump(data)
								#print('hash = %s' % str(sha256(data).hexdigest()))
								if hx(sectionHeaderBlock[0xc8:0xc8+0x20]).decode('utf-8') == str(sha256(data).hexdigest()):
									return True
								else:
									return False
							else:
								mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
								data = mem.read();
								#Hex.dump(data)
								magic = mem.read()[0:4]
								#print(magic)
								if magic != b'PFS0':
									pass
								else:
									return True

						if fs.fsType == Type.Fs.ROMFS and fs.cryptoType == Type.Crypto.CTR:
							f.seek(0)
							ncaHeader = NcaHeader()
							ncaHeader.open(MemoryFile(f.read(0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
							ncaHeader = f.read(0x400)
							pfs0=fs
							sectionHeaderBlock = fs.buffer

							levelOffset = int.from_bytes(sectionHeaderBlock[0x18:0x20], byteorder='little', signed=False)
							levelSize = int.from_bytes(sectionHeaderBlock[0x20:0x28], byteorder='little', signed=False)

							pfs0Offset = fs.offset + levelOffset
							f.seek(pfs0Offset)
							pfs0Header = f.read(levelSize)
							#print(sectionHeaderBlock[8:12] == b'IVFC')
							if sectionHeaderBlock[8:12] == b'IVFC':
								#Hex.dump(sectionHeaderBlock)
								#Print.info(hx(sectionHeaderBlock[0xc8:0xc8+0x20]).decode('utf-8'))
								mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
								data = mem.read();
								#Hex.dump(data)
								#print('hash = %s' % str(sha256(data).hexdigest()))
								if hx(sectionHeaderBlock[0xc8:0xc8+0x20]).decode('utf-8') == str(sha256(data).hexdigest()):
									return True
								else:
									return False
							else:
								mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
								data = mem.read();
								#Hex.dump(data)
								magic = mem.read()[0:4]
								#print(magic)
								if magic != b'PFS0':
									return False
								else:
									return True

						if fs.fsType == Type.Fs.ROMFS and fs.cryptoType == Type.Crypto.BKTR and str(f.header.contentType) == 'Content.PROGRAM':
							f.seek(0)
							ncaHeader = NcaHeader()
							ncaHeader.open(MemoryFile(f.read(0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
							ncaHeader = f.read(0x400)
							pfs0=fs
							sectionHeaderBlock = fs.buffer

							levelOffset = int.from_bytes(sectionHeaderBlock[0x18:0x20], byteorder='little', signed=False)
							levelSize = int.from_bytes(sectionHeaderBlock[0x20:0x28], byteorder='little', signed=False)

							pfs0Offset = fs.offset + levelOffset
							f.seek(pfs0Offset)
							pfs0Header = f.read(levelSize)
							if sectionHeaderBlock[8:12] == b'IVFC':
								for i in range(10):
									ini=0x100+(i*0x10)
									fin=0x110+(i*4)
									test=sectionHeaderBlock[ini:fin]
									if test==b'BKTR':
										return True
		return False



	def cnmt_get_baseids(self):
		ctype='addon'
		idlist=list()
		counter=0
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					for pfs0 in nca:
						for cnmt in pfs0:
							cnmt.rewind()
							titleid=cnmt.readInt64()
							titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
							titleid2 = titleid2[2:-1]
							if counter>0 and not str(titleid2).endswith('000'):
								counter+=1
								break
							else:
								counter+=1
							titleversion = cnmt.read(0x4);cnmt.seek(0xE)
							offset=cnmt.readInt16();content_entries=cnmt.readInt16()
							meta_entries=cnmt.readInt16();content_type=str(cnmt._path);content_type=content_type[:-22]
							cnmt.seek(0x20)
							if content_type=='Application':
								original_ID=titleid2
								if original_ID not in idlist:
									idlist.append(original_ID)
								ctype='base'
							elif content_type=='Patch':
								original_ID=cnmt.readInt64()
								original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
								original_ID = original_ID[2:-1]
								if original_ID not in idlist:
									idlist.append(original_ID)
								ctype='update'
							elif content_type=='AddOnContent':
								original_ID=cnmt.readInt64()
								original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
								original_ID = original_ID[2:-1]
								if original_ID not in idlist:
									idlist.append(original_ID)
								ctype='addon'
							else:
								original_ID=cnmt.readInt64()
								original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
								original_ID = original_ID[2:-1]
								if original_ID not in idlist:
									idlist.append(original_ID)
								ctype='addon'
							break

		'''
		for i in idlist:
			print(i)
		'''
		return ctype,idlist

##################
#FILE RESTORATION
##################




##################
#DB DATA
##################
	def Incorporate_to_permaDB(self,dbfile,trans=True):
		Datashelve = DBmodule.Dict(dbfile)
		cnmtnames=list()
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					cnmtnames.append(str(nca._path))
		for file in cnmtnames:
			DBdict=self.getDBdict(file,trans)
			dbkey=(str(DBdict['id'])+'_v'+str(DBdict['version'])).lower()
			if not 'fields' in Datashelve:
				DBmodule.MainDB.initializeDB(dbfile)
			if not dbkey in Datashelve:
				Datashelve[dbkey]=DBdict
		Datashelve.close()

	def return_DBdict(self):
		cnmtnames=list()
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					cnmtnames.append(str(nca._path))
		content_number=len(cnmtnames)
		if content_number>1:
			file,mcstring,mGame=self.choosecnmt(cnmtnames)
			DBdict=self.getDBdict(file,content_number=content_number,mcstring=mcstring,mGame=mGame)
		else:
			DBdict=self.getDBdict(cnmtnames[0],content_number=content_number)
		return DBdict

	def choosecnmt(self,cnmtnames):
		file=False;titleid=False;nG=0;nU=0;nD=0;mcstring="";mGame=False
		for nca in self:
			if str(nca._path) in cnmtnames:
				if type(nca) == Nca:
					if titleid==False:
						file=str(nca._path)
					titleid=str(nca.header.titleId)
					if str(nca.header.titleId).endswith('000'):
						nG+=1
					elif str(nca.header.titleId).endswith('800'):
						if nU==0 and nG<2:
							file=str(nca._path)
						nU+=1
					else:
						nD+=1
		if nG>0:
			mcstring+='{} Game'.format(str(nG))
			if nG>1:
				mcstring+='s'
				mGame=True
		if nU>0:
			if nG>0:
				mcstring+=', '
			mcstring+='{} Update'.format(str(nU))
			if nU>1:
				mcstring+='s'
		if nD>0:
			if nG>0 or nU>0:
				mcstring+=', '
			mcstring+='{} DLC'.format(str(nD))
			if nD>1:
				mcstring+='s'
		return file,mcstring,mGame


	def getDBdict(self,cnmtname,json=False,trans=True,content_number=False,mcstring=False,mGame=False):
		DBdict={}
		titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=self.get_data_from_cnmt(cnmtname)
		try:
			sqname,sqeditor,SupLg,ctype=self.DB_get_names(ctype,ncadata)
		except:
			sqname,sqeditor,SupLg=self.DB_get_names_from_nutdb(titleid)
		if ctype != 'DLC':
			nacpdict=self.get_data_from_nacp(ncadata)
		titlekey,dectkey=self.db_get_titlekey(rightsId,keygeneration)
		#cnmt flags
		DBdict['id']=titleid
		DBdict['baseid']=base_ID
		DBdict['rightsId']=rightsId
		DBdict['Type']=ctype
		DBdict['version']=titleversion
		DBdict['keygeneration']=keygeneration
		DBdict['RSV']=RSV[1:-1]
		DBdict['RGV']=RGV
		DBdict['metasdkversion']=metasdkversion
		DBdict['exesdkversion']=exesdkversion
		DBdict['InstalledSize']=Installedsize
		DBdict['deltasize']=DeltaSize
		DBdict['HtmlManual']=hasHtmlManual
		DBdict['ncasizes']=ncadata

		#nacpt flags
		if ctype != 'DLC':
			DBdict['baseName']=sqname
			DBdict['contentname']='-'
		else:
			DBdict['baseName']='-'
			DBdict['contentname']=sqname
		DBdict['editor']=sqeditor
		DBdict['languages']=SupLg
		if ctype != 'DLC':
			try:
				if nacpdict['StartupUserAccount']=='RequiredWithNetworkServiceAccountAvailable' or nacpdict['RequiredNetworkServiceLicenseOnLaunch']!='None':
					DBdict['linkedAccRequired']='True'
				else:
					DBdict['linkedAccRequired']='False'
				DBdict['dispversion']=nacpdict['BuildNumber']
			except:pass

		#ticket flags
		if titlekey==False:
			titlekey='-'
			dectkey='-'
		DBdict['key']=titlekey
		DBdict['deckey']=dectkey

		#Distribution type flags
		if ctype=='GAME':
			DBdict['DistEshop']='True'
			DBdict['DistCard']='-'
		else:
			DBdict['DistEshop']='-'
			DBdict['DistCard']='-'

		#Check if multicontent
		if content_number==False:
			content_number=sq_tools.count_content(self._path)
		# print(str(content_number))
		DBdict['ContentNumber']=str(content_number)
		if mcstring !=False:
			DBdict['ContentString']=mcstring
		if content_number!=False and content_number>1:
			if mGame==True:
				DBdict['Type']="MULTIGAME"
			else:
				DBdict['Type']="MULTICONTENT"
			DBdict['InstalledSize']=sq_tools.get_mc_isize(self._path)

		DBdict['nsuId']='-'
		DBdict['genretags']='-'
		DBdict['ratingtags']='-'
		DBdict['worldreleasedate']='-'
		DBdict['numberOfPlayers']='-'
		DBdict['iconUrl']='-'
		DBdict['screenshots']='-'
		DBdict['bannerUrl']='-'
		DBdict['intro']='-'
		DBdict['description']='-'
		if ctype=='GAME' or ctype=='DLC' or ctype=='DEMO':
			nsuId,worldreleasedate,genretags,ratingtags,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(titleid,trans)
			regions=nutdb.get_contenregions(titleid)
		else:
			nsuId,worldreleasedate,genretags,ratingtags,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(base_ID,trans)
			regions=nutdb.get_contenregions(base_ID)
		if 	nsuId!=False:
			DBdict['nsuId']=nsuId
		if 	genretags!=False:
			DBdict['genretags']=genretags
		if 	ratingtags!=False:
			DBdict['ratingtags']=ratingtags
		if 	worldreleasedate!=False:
			DBdict['worldreleasedate']=worldreleasedate
		if 	numberOfPlayers!=False:
			DBdict['numberOfPlayers']=numberOfPlayers
		if 	iconUrl!=False:
			DBdict['iconUrl']=iconUrl
		if 	screenshots!=False:
			DBdict['screenshots']=screenshots
		if 	bannerUrl!=False:
			DBdict['bannerUrl']=bannerUrl
		if 	intro!=False:
			DBdict['intro']=intro
		if 	description!=False:
			DBdict['description']=description
		if 	rating!=False:
			DBdict['eshoprating']=rating
		if 	developer!=False:
			DBdict['developer']=developer
		if 	productCode!=False:
			DBdict['productCode']=productCode
		if 	OnlinePlay!=False:
			DBdict['OnlinePlay']=OnlinePlay
		if 	SaveDataCloud!=False:
			DBdict['SaveDataCloud']=SaveDataCloud
		if 	playmodes!=False:
			DBdict['playmodes']=playmodes
		if 	video!=False:
			DBdict['video']=video
		if 	shopurl!=False:
			DBdict['shopurl']=shopurl
		if 	len(regions)>0:
			DBdict['regions']=regions
		metascore,userscore,openscore=nutdb.get_metascores(titleid)
		DBdict['metascore']='-'
		DBdict['userscore']='-'
		DBdict['openscore']='-'
		if 	metascore!=False:
			DBdict['metascore']=metascore
		if 	userscore!=False:
			DBdict['userscore']=userscore
		if 	openscore!=False:
			DBdict['openscore']=openscore
		return DBdict

	def DB_get_names_from_nutdb(self,titleid):
		try:
			sqname,sqeditor=nutdb.get_dlcData(titleid)
			SupLg=nutdb.get_content_langue(titleid)
			return sqname,sqeditor,SupLg
		except BaseException as e:
			Print.error('Exception: ' + str(e))
			return "-","-","-"

	def get_data_from_cnmt(self,cnmtname):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.META':
					if str(nca._path)==cnmtname:
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto2>crypto1:
							keygeneration=crypto2
						if crypto2<=crypto1:
							keygeneration=crypto1
						for f in nca:
							for cnmt in f:
								nca.rewind()
								f.rewind()
								cnmt.rewind()
								titleid=cnmt.readInt64()
								titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
								titleid2 = titleid2[2:-1]
								titleid=(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1]).upper()
								titleversion = cnmt.read(0x4)
								titleversion=str(int.from_bytes(titleversion, byteorder='little'))
								type_n = cnmt.read(0x1)
								cnmt.rewind()
								cnmt.seek(0xE)
								offset=cnmt.readInt16()
								content_entries=cnmt.readInt16()
								meta_entries=cnmt.readInt16()
								cnmt.rewind()
								cnmt.seek(0x20)
								base_ID=cnmt.readInt64()
								base_ID=(str(hx(base_ID.to_bytes(8, byteorder='big')))[2:-1]).upper()
								cnmt.rewind()
								cnmt.seek(0x28)
								min_sversion=cnmt.readInt32()
								length_of_emeta=cnmt.readInt32()
								content_type_cnmt=str(cnmt._path)
								content_type_cnmt=content_type_cnmt[:-22]
								if content_type_cnmt != 'AddOnContent':
									RSV=str(min_sversion)
									RSV=sq_tools.getFWRangeRSV(int(RSV))
									RGV=0
								if content_type_cnmt == 'AddOnContent':
									RSV_rq_min=sq_tools.getMinRSV(keygeneration, 0)
									RSV=sq_tools.getFWRangeRSV(int(RSV_rq_min))
									RGV=str(min_sversion)
								if str(hx(type_n)) == "b'1'":
									ctype='SystemProgram'
								if str(hx(type_n)) == "b'2'":
									ctype='SystemData'
								if str(hx(type_n)) == "b'3'":
									ctype='SystemUpdate'
								if str(hx(type_n)) == "b'4'":
									ctype='BootImagePackage'
								if str(hx(type_n)) == "b'5'":
									ctype='BootImagePackageSafe'
								if str(hx(type_n)) == "b'80'":
									ctype='GAME'
								if str(hx(type_n)) == "b'81'":
									ctype='UPDATE'
								if str(hx(type_n)) == "b'82'":
									ctype='DLC'
								if str(hx(type_n)) == "b'83'":
									ctype='Delta'
								metasdkversion=nca.get_sdkversion()
								programSDKversion,dataSDKversion=self.getsdkvertit(titleid2)
								if content_type_cnmt == 'AddOnContent':
									exesdkversion=dataSDKversion
								if content_type_cnmt != 'AddOnContent':
									exesdkversion=programSDKversion
								ncadata=list()
								hasHtmlManual=False
								Installedsize=int(nca.header.size);DeltaSize=0
								cnmt.rewind()
								cnmt.seek(0x20+offset)
								for i in range(content_entries):
									data={}
									vhash = cnmt.read(0x20)
									vhash=str(hx(vhash))
									NcaId = cnmt.read(0x10)
									NcaId=str(hx(NcaId))
									size = cnmt.read(0x6)
									size=str(int.from_bytes(size, byteorder='little', signed=True))
									ncatype = cnmt.read(0x1)
									ncatype=str(int.from_bytes(ncatype, byteorder='little', signed=True))
									ncatype=sq_tools.getmetacontenttype(ncatype)
									IdOffset = cnmt.read(0x1)
									IdOffset=str(int.from_bytes(IdOffset, byteorder='little', signed=True))
									data['NcaId']=NcaId[2:-1]
									data['NCAtype']=ncatype
									data['Size']=size
									data['Hash']=vhash[2:-1]
									data['IdOffset']=IdOffset
									if int(IdOffset)>0:
										if ctype=='MultiProgram' or ctype=='MultiProgram UPD':
											pass
										elif ctype != 'UPDATE':
											ctype='MultiProgram'
										else:
											ctype='MultiProgram UPD'
									if ncatype != "DeltaFragment":
										Installedsize=Installedsize+int(size)
									else:
										DeltaSize=DeltaSize+int(size)
									if ncatype == "HtmlDocument":
										hasHtmlManual=True
									ncadata.append(data)
								cnmtdata={}
								metaname=str(nca._path);metaname =  metaname[:-9]
								nca.rewind();block = nca.read();nsha=sha256(block).hexdigest()
								cnmtdata['NcaId']=metaname
								cnmtdata['NCAtype']='Meta'
								cnmtdata['Size']=str(nca.header.size)
								cnmtdata['Hash']=str(nsha)
								ncadata.append(cnmtdata)
						rightsId=titleid+'000000000000000'+str(crypto2)
						return 	titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata

	def get_data_from_nacp(self,ncadata):
		for entry in ncadata:
			if entry['NCAtype'].lower()=='control':
				target=entry['NcaId']+'.nca'
		dict={}
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if target==str(nca._path):
						offset=nca.get_nacp_offset()
						for f in nca:
							nacp = Nacp()
							f.seek(offset+0x3025)
							dict['StartupUserAccount']=nacp.get_StartupUserAccount(f.readInt8('little'))
							f.seek(offset+0x3060)
							try:
								dict['BuildNumber']=nacp.get_DisplayVersion(f.read(0xF))
								f.seek(offset+0x3213)
								dict['RequiredNetworkServiceLicenseOnLaunch']=nacp.get_RequiredNetworkServiceLicenseOnLaunch(f.readInt8('little'))
							except:continue
						return dict

	def DB_get_names(self,ctype,ncadata):
		for entry in ncadata:
			if str(entry['NCAtype']).lower()=='control':
				target=str(entry['NcaId'])+'.nca'
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					if target==str(nca._path):
						title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock('DLC',roman=True)
						if ctype=='GAME':
							if isdemo==1:
								ctype='DEMO'
							if isdemo==2:
								ctype='RETAILINTERACTIVEDISPLAY'
						elif ctype=='UPDATE':
							if isdemo==1:
								ctype='DEMO UPDATE'
							if isdemo==2:
								ctype='RETAILINTERACTIVEDISPLAY UPDATE'
						else:
							ctype=ctype
						return 	title,editor,SupLg,ctype

	def db_get_titlekey(self,rightsId,keygeneration):
		#print(rightsId)
		#print(keygeneration)
		for ticket in self:
			if type(ticket) == Ticket:
				tikrights = hex(ticket.getRightsId())
				tikrights = '0'+tikrights[2:]
				if str(rightsId).lower() == str(tikrights).lower():
					titleKey = ticket.getTitleKeyBlock()
					titleKey=str(hx(titleKey.to_bytes(16, byteorder='big')))
					titleKey=titleKey[2:-1].upper()
					deckey = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(int(keygeneration)))
					deckey=(str(hx(deckey))[2:-1]).upper()
					#print(titleKey)
					#print(deckey)
					return str(titleKey),str(deckey)
		return False,False

	def icon_info(self,files_list,buffer = 65536):
		for nca in self:
			if type(nca) == Nca:
				if 	str(nca.header.contentType) == 'Content.CONTROL':
					tk=nca.header.titleKeyDec
					for i in range(len(files_list)):
						if str(nca._path) == files_list[i][0]:
							offset=files_list[i][1]
							#print(offset)
							break
					checksums = list()
					try:
						fp=open(str(self._path), 'rb')
						nca3=NCA3(fp,int(offset),str(nca._path),tk)
						for dat in self.open_all_dat(nca3):
							checksum = sha1(dat.read()).digest()
							if checksum not in checksums:
								checksums.append(checksum)
								a=self.print_dat(dat)
								return a
								break
						fp.close()
					except BaseException as e:
						# Print.error('Exception: ' + str(e))
						try:
							with open(str(self._path), 'rb') as f:
								f.seek(offset)
								inmemoryfile = io.BytesIO(f.read(files_list[i][3]))
								nca3=NCA3(inmemoryfile,int(0),str(nca._path),tk,buffer)
								for dat in self.open_all_dat(nca3):
									checksum = sha1(dat.read()).digest()
									if checksum not in checksums:
										checksums.append(checksum)
										a=self.print_dat(dat)
										return a
										break
								fp.close()
						except BaseException as e:
							#Print.error('Exception: ' + str(e))
							pass
	def open_all_dat(self,nca):
		# Iterators that yields all the icon file handles inside an NCA
		for _, sec in enumerate(nca.sections):
			if sec.fs_type == 'PFS0':
				continue
			cur_file = sec.fs.first_file
			while cur_file is not None:
				if cur_file.name.endswith('.dat'):
					yield sec.fs.open(cur_file)
				cur_file = cur_file.next

	def print_dat(self,dat):
		dat.seek(0)
		a=dat.read()
		# print(a)
		# img = Image.open(dat)
		# img.show()
		return a

	def decompress(self,output,buffer = 65536):
		print('Decompressing {}'.format(self._path))
		files_list=sq_tools.ret_nsp_offsets(self._path)
		files=list();filesizes=list()
		fplist=list()
		for k in range(len(files_list)):
			entry=files_list[k]
			fplist.append(entry[0])
		for i in range(len(files_list)):
			entry=files_list[i]
			filepath=entry[0]
			if filepath.endswith('.cnmt.nca'):
				titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=self.get_data_from_cnmt(filepath)
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']!='Meta':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist or test2 in fplist:
							# print(str(row['NcaId'])+'.nca')
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
					else:
						# print(str(row['NcaId'])+'.cnmt.nca')
						files.append(str(row['NcaId'])+'.cnmt.nca')
						filesizes.append(int(row['Size']))
				for k in range(len(files_list)):
					entry=files_list[k]
					fp=entry[0];sz=int(entry[3])
					if fp.endswith('xml'):
						files.append(fp)
						filesizes.append(sz)
				for k in range(len(files_list)):
					entry=files_list[k]
					fp=entry[0];sz=int(entry[3])
					if fp.endswith('.tik'):
						files.append(fp)
						filesizes.append(sz)
				for k in range(len(files_list)):
					entry=files_list[k]
					fp=entry[0];sz=int(entry[3])
					if fp.endswith('.cert'):
						files.append(fp)
						filesizes.append(sz)
		nspheader=sq_tools.gen_nsp_header(files,filesizes)
		totsize=0
		for s in filesizes:
			totsize+=s
		for i in range(len(files_list)):
			entry=files_list[i]
			fp=entry[0]
			if fp.endswith('.ncz'):
				for j in range(len(files)):
					fp2=files[j]
					if str(fp2[:-1])==str(fp[:-1]):
						totsize+=filesizes[j]
		t = tqdm(total=totsize, unit='B', unit_scale=True, leave=False)
		# Hex.dump(nspheader)
		with open(output, 'wb') as o:
			o.write(nspheader)
			t.update(len(nspheader))
		for file in files:
			if file.endswith('cnmt.nca'):
				for nca in self:
					if str(nca._path)==file:
						t.write('- Appending {}'.format(str(nca._path)))
						nca.rewind()
						data=nca.read()
						with open(output, 'ab') as o:
							o.write(data)
							t.update(len(data))
			elif file.endswith('nca'):
				for nca in self:
					if str(nca._path)[:-1]==file[:-1] and not str(nca._path).endswith('.ncz'):
						t.write('- Appending {}'.format(str(nca._path)))
						o = open(output, 'ab+')
						nca.rewind()
						for data in iter(lambda: nca.read(int(buffer)), ""):
							o.write(data)
							t.update(len(data))
							o.flush()
							if not data:
								o.close()
								break
					elif str(nca._path)[:-1]==file[:-1] and str(nca._path).endswith('ncz'):
						# print(nca._path)
						nca.rewind()
						header = nca.read(0x4000)
						magic = readInt64(nca)
						sectionCount = readInt64(nca)
						sections = []
						for i in range(sectionCount):
							sections.append(Section(nca))
						# print(sections)
						dctx = zstandard.ZstdDecompressor()
						reader = dctx.stream_reader(nca)
						with open(output, 'rb+') as o:
							o.seek(0, os.SEEK_END)
							curr_off= o.tell()
							t.write('- Appending decompressed {}'.format(str(nca._path)))
							t.write('  Writing nca header')
							o.write(header)
							t.update(len(header))
							timestamp = time.time()
							t.write('  Writing decompressed body in plaintext')
							while True:
								chunk = reader.read(16384)
								if not chunk:
									break
								o.write(chunk)
								t.update(len(chunk))
							c=0;spsize=0
							t.write('  + Restoring crypto in sections')
							for s in sections:
								c+=1
								if s.cryptoType == 1: #plain text
									t.write('    * Section {} is plaintext'.format(str(c)))
									t.write('      %x - %d bytes, Crypto type %d' % ((s.offset), s.size, s.cryptoType))
									t.update(s.size);spsize+=s.size
									continue
								if s.cryptoType not in (3, 4):
									raise IOError('Unknown crypto type: %d' % s.cryptoType)
								t.write('    * Section {} needs decompression'.format(str(c)))
								t.write('      %x - %d bytes, Crypto type %d' % ((s.offset), s.size, s.cryptoType))
								t.write('      Key: %s, IV: %s' % (str(hx(s.cryptoKey)), str(hx(s.cryptoCounter))))
								i = s.offset
								crypto = AESCTR(s.cryptoKey, s.cryptoCounter)
								end = s.offset + s.size
								spsize+=s.size
								while i < end:
									o.seek(i+curr_off)
									crypto.seek(i)
									chunkSz = 0x10000 if end - i > 0x10000 else end - i
									buf = o.read(chunkSz)
									if not len(buf):
										break
									o.seek(i+curr_off)
									o.write(crypto.encrypt(buf))
									t.update(len(buf))
									i += chunkSz
							elapsed = time.time() - timestamp
							minutes = elapsed / 60
							seconds = elapsed % 60

							speed = 0 if elapsed == 0 else (spsize / elapsed)
							t.write('\n    Decompressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))

			else:
				for ot in self:
					if str(ot._path)==file:
						t.write('- Appending {}'.format(str(ot._path)))
						ot.rewind()
						data=ot.read()
						with open(output, 'ab') as o:
							o.write(data)
							t.update(len(data))

	def decompress_direct(self,output,buffer = 65536):
		print('Decompressing {}'.format(self._path))
		files_list=sq_tools.ret_nsp_offsets(self._path)
		files=list();filesizes=list()
		fplist=list()
		for k in range(len(files_list)):
			entry=files_list[k]
			fplist.append(entry[0])
		for i in range(len(files_list)):
			entry=files_list[i]
			filepath=entry[0]
			if filepath.endswith('.cnmt.nca'):
				titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=self.get_data_from_cnmt(filepath)
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']!='Meta':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist or test2 in fplist:
							# print(str(row['NcaId'])+'.nca')
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
					else:
						# print(str(row['NcaId'])+'.cnmt.nca')
						files.append(str(row['NcaId'])+'.cnmt.nca')
						filesizes.append(int(row['Size']))
				for k in range(len(files_list)):
					entry=files_list[k]
					fp=entry[0];sz=int(entry[3])
					if fp.endswith('xml'):
						files.append(fp)
						filesizes.append(sz)
				for k in range(len(files_list)):
					entry=files_list[k]
					fp=entry[0];sz=int(entry[3])
					if fp.endswith('.tik'):
						files.append(fp)
						filesizes.append(sz)
				for k in range(len(files_list)):
					entry=files_list[k]
					fp=entry[0];sz=int(entry[3])
					if fp.endswith('.cert'):
						files.append(fp)
						filesizes.append(sz)
		nspheader=sq_tools.gen_nsp_header(files,filesizes)
		totsize=0
		for s in filesizes:
			totsize+=s
		t = tqdm(total=totsize, unit='B', unit_scale=True, leave=False)
		# Hex.dump(nspheader)
		with open(output, 'wb') as o:
			o.write(nspheader)
			t.update(len(nspheader))
		for file in files:
			if file.endswith('cnmt.nca'):
				for nca in self:
					if str(nca._path)==file:
						t.write('- Appending {}'.format(str(nca._path)))
						nca.rewind()
						data=nca.read()
						with open(output, 'ab') as o:
							o.write(data)
							t.update(len(data))
			elif file.endswith('nca'):
				for nca in self:
					if str(nca._path)[:-1]==file[:-1] and not str(nca._path).endswith('.ncz'):
						t.write('- Appending {}'.format(str(nca._path)))
						o = open(output, 'ab+')
						nca.rewind()
						for data in iter(lambda: nca.read(int(buffer)), ""):
							o.write(data)
							t.update(len(data))
							o.flush()
							if not data:
								o.close()
								break
					elif str(nca._path)[:-1]==file[:-1] and str(nca._path).endswith('ncz'):
						# print(nca._path)
						nca.rewind()
						header = nca.read(0x4000)
						magic = readInt64(nca)
						sectionCount = readInt64(nca)
						sections = []
						for i in range(sectionCount):
							sections.append(Section(nca))
						# print(sections)
						dctx = zstandard.ZstdDecompressor()
						reader = dctx.stream_reader(nca)
						with open(output, 'rb+') as o:
							o.seek(0, os.SEEK_END)
							curr_off= o.tell()
							t.write('- Appending decompressed {}'.format(str(nca._path)))
							t.write('  Writing nca header')
							o.write(header)
							t.update(len(header))
							timestamp = time.time()
							t.write('  Writing decompressed body in plaintext')
							count=0;checkstarter=0
							dctx = zstandard.ZstdDecompressor()
							reader = dctx.stream_reader(nca)
							c=0;spsize=0
							for s in sections:
								end = s.offset + s.size
								if s.cryptoType == 1: #plain text
									t.write('    * Section {} is plaintext'.format(str(c)))
									t.write('      %x - %d bytes, Crypto type %d' % ((s.offset), s.size, s.cryptoType))
									spsize+=s.size
									end = s.offset + s.size
									i = s.offset
									while i < end:
										chunkSz = buffer if end - i > buffer else end - i
										chunk = reader.read(chunkSz)
										if not len(chunk):
											break
										o.write(chunk)
										t.update(len(chunk))
										i += chunkSz
								elif s.cryptoType not in (3, 4):
									raise IOError('Unknown crypto type: %d' % s.cryptoType)
								else:
									t.write('    * Section {} needs decompression'.format(str(c)))
									t.write('      %x - %d bytes, Crypto type %d' % ((s.offset), s.size, s.cryptoType))
									t.write('      Key: %s, IV: %s' % (str(hx(s.cryptoKey)), str(hx(s.cryptoCounter))))
									crypto = AESCTR(s.cryptoKey, s.cryptoCounter)
									spsize+=s.size
									test=int(spsize/(buffer))
									i = s.offset
									while i < end:
										crypto.seek(i)
										chunkSz = buffer if end - i > buffer else end - i
										chunk = reader.read(chunkSz)
										if not len(chunk):
											break
										o.write(crypto.encrypt(chunk))
										t.update(len(chunk))
										i += chunkSz

							elapsed = time.time() - timestamp
							minutes = elapsed / 60
							seconds = elapsed % 60

							speed = 0 if elapsed == 0 else (spsize / elapsed)
							t.write('\n    Decompressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))

			else:
				for ot in self:
					if str(ot._path)==file:
						t.write('- Appending {}'.format(str(ot._path)))
						ot.rewind()
						data=ot.read()
						with open(output, 'ab') as o:
							o.write(data)
							t.update(len(data))


	def verify_ncz(self,target):
		files_list=sq_tools.ret_nsp_offsets(self._path)
		files=list();
		fplist=list()
		for k in range(len(files_list)):
			entry=files_list[k]
			fplist.append(entry[0])
		for i in range(len(files_list)):
			entry=files_list[i]
			filepath=entry[0]
			if filepath.endswith('.cnmt.nca'):
				titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=self.get_data_from_cnmt(filepath)
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']!='Meta':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist or test2 in fplist:
							# print(str(row['NcaId'])+'.nca')
							if str(row['NcaId'])==target[:-4]:
								files.append(str(row['NcaId'])+'.nca')
								break
		for file in files:
			if file.endswith('nca'):
				for nca in self:
					if str(nca._path)[:-1]==file[:-1] and str(nca._path).endswith('ncz'):
						# print(nca._path)
						nca.rewind()
						header = nca.read(0x4000)
						magic = readInt64(nca)
						sectionCount = readInt64(nca)
						sections = []
						for i in range(sectionCount):
							sections.append(Section(nca))
						count=0;checkstarter=0
						if titleid.endswith('000'):
							for s in sections:
								count+=1
								if count==2:
									break
								# print(s.cryptoType)
								# print(s.size)
								checkstarter+=s.size
								# print(s.size)
							dctx = zstandard.ZstdDecompressor()
							reader = dctx.stream_reader(nca)
							test=int(checkstarter/(16384))
							for i in (range(test+1)):
								reader.seek(16384,1)
							chunk = reader.read(16384)
							b1=chunk[:32];# Hex.dump(b1)
							b2=chunk[32:64];# Hex.dump(b2)
							if sum(b1)!=0 and sum(b2)==0:
								return True
							else:
								return 'ncz'
						if not titleid.endswith('800'):
							dctx = zstandard.ZstdDecompressor()
							reader = dctx.stream_reader(nca)
							chunk = reader.read(16384)
							b1=chunk[:32];# Hex.dump(b1)
							b2=chunk[32:64];# Hex.dump(b2)
							if sum(b1)!=0 and sum(b2)==0:
								return True
							else:
								return 'ncz'
						elif titleid.endswith('800'):
							dctx = zstandard.ZstdDecompressor()
							reader = dctx.stream_reader(nca)
							chunk = reader.read(16384)
							b1=chunk[:32];# Hex.dump(b1)
							b2=chunk[32:64];# Hex.dump(b2)
							if sum(b1)!=0 and sum(b2)==0:
								return True
							else:
								return 'ncz'


	def nsz_hasher(self,buffer,headerlist,didverify,feed):
		buffer=int(buffer)
		verdict=True
		if feed == False:
			feed=''
		message='\n***************';print(message);feed+=message+'\n'
		message=('HASH TEST');print(message);feed+=message+'\n'
		message='***************';print(message);feed+=message+'\n'
		for f in self:
			if type(f) == Nca:
				origheader=False
				for i in range(len(headerlist)):
					if str(f._path)==headerlist[i][0]:
						origheader=headerlist[i][1]
						listedhash=headerlist[i][2]
						break
				message=(str(f.header.titleId)+' - '+str(f.header.contentType));print(message);feed+=message+'\n'
				ncasize=f.header.size
				t = tqdm(total=ncasize, unit='B', unit_scale=True, leave=False)
				i=0
				f.rewind();
				rawheader=f.read(0xC00)
				f.rewind()
				for data in iter(lambda: f.read(int(buffer)), ""):
					if i==0:
						sha=sha256()
						f.seek(0xC00)
						sha.update(rawheader)
						if origheader != False and listedhash == False:
							sha0=sha256()
							sha0.update(origheader)
						i+=1
						t.update(len(data))
						f.flush()
					else:
						sha.update(data)
						if origheader != False and listedhash == False:
							sha0.update(data)
						t.update(len(data))
						f.flush()
						if not data:
							break
				t.close()
				sha=sha.hexdigest()
				if listedhash != False:
					sha0=listedhash
				elif origheader != False:
					sha0=sha0.hexdigest()
				message=('  - File name: '+f._path);print(message);feed+=message+'\n'
				message=('  - SHA256: '+sha);print(message);feed+=message+'\n'
				if origheader != False:
					message=('  - ORIG_SHA256: '+sha0);print(message);feed+=message+'\n'
				if str(f._path)[:16] == str(sha)[:16]:
					message=('   > FILE IS CORRECT');print(message);feed+=message+'\n'
				elif origheader != False:
					if str(f._path)[:16] == str(sha0)[:16]:
						message=('   > FILE IS CORRECT');print(message);feed+=message+'\n'
					else:
						message=('   > FILE IS CORRUPT');print(message);feed+=message+'\n'
						verdict = False
				elif  f.header.contentType == Type.Content.META and didverify == True:
					message=('   > RSV WAS CHANGED');print(message);feed+=message+'\n'
					#print('   > CHECKING INTERNAL HASHES')
					message=('     * FILE IS CORRECT');print(message);feed+=message+'\n'
				else:
					message=('   > FILE IS CORRUPT');print(message);feed+=message+'\n'
					verdict = False
				message=('');print(message);feed+=message+'\n'
			if (f._path).endswith('ncz'):
				ncz=Nca(f)
				ncz._path=f._path
				origheader=False
				for i in range(len(headerlist)):
					if str(f._path)==headerlist[i][0]:
						origheader=headerlist[i][1]
						listedhash=headerlist[i][2]
						break
				message=(str(ncz.header.titleId)+' - '+str(ncz.header.contentType));print(message);feed+=message+'\n'
				ncasize=ncz.header.size
				t = tqdm(total=ncasize, unit='B', unit_scale=True, leave=False)
				i=0
				f.rewind();
				rawheader=f.read(0xC00)
				f.rewind()
				sha=sha256()
				f.seek(0xC00)
				sha.update(rawheader)
				if origheader != False and listedhash == False:
					sha0=sha256()
					sha0.update(origheader)
				i+=1
				t.update(len(rawheader))
				f.flush()
				size=0x4000-0xC00
				dif = f.read(size)
				sha.update(dif)
				if origheader != False and listedhash == False:
					sha0.update(dif)
				t.update(len(dif))
				f.flush()
				f.seek(0x4000)
				magic = readInt64(f)
				sectionCount = readInt64(f)
				sections = []
				for i in range(sectionCount):
					sections.append(Section(f))
				# print(sections)
				count=0;checkstarter=0
				dctx = zstandard.ZstdDecompressor()
				reader = dctx.stream_reader(f)
				c=0;spsize=0
				for s in sections:
					end = s.offset + s.size
					if s.cryptoType == 1: #plain text
						spsize+=s.size
						end = s.offset + s.size
						i = s.offset
						while i < end:
							chunkSz = buffer if end - i > buffer else end - i
							chunk = reader.read(chunkSz)
							if not len(chunk):
								break
							sha.update(chunk)
							if origheader != False and listedhash == False:
								sha0.update(chunk)
							t.update(len(chunk))
							i += chunkSz
					elif s.cryptoType not in (3, 4):
						raise IOError('Unknown crypto type: %d' % s.cryptoType)
					else:
						crypto = AESCTR(s.cryptoKey, s.cryptoCounter)
						spsize+=s.size
						test=int(spsize/(buffer))
						i = s.offset
						while i < end:
							crypto.seek(i)
							chunkSz = buffer if end - i > buffer else end - i
							chunk = reader.read(chunkSz)
							if not len(chunk):
								break
							crpt=crypto.encrypt(chunk)
							sha.update(crpt)
							if origheader != False and listedhash == False:
								sha0.update(crpt)
							t.update(len(chunk))
							i += chunkSz
				t.close()
				sha=sha.hexdigest()
				if listedhash != False:
					sha0=listedhash
				elif origheader != False:
					sha0=sha0.hexdigest()
				message=('  - File name: '+ncz._path);print(message);feed+=message+'\n'
				message=('  - SHA256: '+sha);print(message);feed+=message+'\n'
				if origheader != False:
					message=('  - ORIG_SHA256: '+sha0);print(message);feed+=message+'\n'
				if str(ncz._path)[:16] == str(sha)[:16]:
					message=('   > FILE IS CORRECT');print(message);feed+=message+'\n'
				elif origheader != False:
					if str(ncz._path)[:16] == str(sha0)[:16]:
						message=('   > FILE IS CORRECT');print(message);feed+=message+'\n'
					else:
						message=('   > FILE IS CORRUPT');print(message);feed+=message+'\n'
						verdict = False
				elif  ncz.header.contentType == Type.Content.META and didverify == True:
					message=('   > RSV WAS CHANGED');print(message);feed+=message+'\n'
					#print('   > CHECKING INTERNAL HASHES')
					message=('     * FILE IS CORRECT');print(message);feed+=message+'\n'
				else:
					message=('   > FILE IS CORRUPT');print(message);feed+=message+'\n'
					verdict = False
				message=('');print(message);feed+=message+'\n'
		if str(self.path).endswith('.nsz'):
			token='NSZ'
		elif str(self.path).endswith('.nsx'):
			token='NSX'
		elif str(self.path).endswith('.nsp'):
			token='NSP'
		else:
			token='NSP'
		if verdict == False:
			message=("VERDICT: {} FILE IS CORRUPT").format(token);print(message);feed+=message+'\n'
		if verdict == True:
			message=('VERDICT: {} FILE IS CORRECT').format(token);print(message);feed+=message+'\n'
		return 	verdict,feed
