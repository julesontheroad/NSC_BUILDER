from Fs.File import File
import Fs.Type
from binascii import hexlify as hx, unhexlify as uhx
from enum import IntEnum
import Print
import Keys

class NacpLanguageType(IntEnum):
	AmericanEnglish = 0
	BritishEnglish = 1
	Japanese = 2
	French = 3
	German = 4
	LatinAmericanSpanish = 5
	Spanish = 6
	Italian = 7
	Dutch = 8
	CanadianFrench = 9
	Portuguese = 10
	Russian = 11
	Korean = 12
	Taiwanese = 13
	Chinese = 14

class NacpLanguage:
	def __init__(self):
		self.name = None
		self.developer = None


class Nacp(File):
	def __init__(self, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Nacp, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)
		
		self.applicationId = None
		self.startupUserAccount = None
		
		self.languages = []
		
		for i in range(15):
			self.languages.append(NacpLanguage())
		
		
		
	def getApplicationId(self):
		self.seek(0x3038)
		self.applicationId = self.readInt64('little')
		return self.applicationId

		
	def getTitle(self, i):
		self.seek(i * 0x300)
		self.languages[i].title = self.read(0x200)
		self.languages[i].title = self.languages[i].title.split(b'\0', 1)[0].decode('utf-8')
		return self.languages[i].title
		
		
	def getDeveloper(self, i):
		self.seek(i * 0x300 + 0x200)
		self.languages[i].developer = self.read(0x100)
		self.languages[i].developer = self.languages[i].developer.split(b'\0', 1)[0].decode('utf-8')
		return self.languages[i].developer
		
		
	def getStartupUserAccount(self):
		self.seek(0x3025)
		b = self.readInt8('little')
		if b == 0:
			self.startupUserAccount = 'None'
		elif b == 1:
			self.startupUserAccount = 'Required'
		elif b == 2:
			self.startupUserAccount = 'RequiredWithNetworkServiceAccountAvailable'
		else:
			self.startupUserAccount = 'Invalid offset'
		return self.startupUserAccount
		
		
	def printInfo(self, maxDepth = 3, indent = 0):
		tabs = '\t' * indent
		Print.info('\n%sNacp\n' % (tabs))
		super(Nacp, self).printInfo(maxDepth, indent)
		Print.info(tabs + 'Application Id = ' + hex(self.getApplicationId()))

		for i in range(15):
			Print.info(tabs + str(NacpLanguageType(i)) + ' Title = ' + self.getTitle(i))
			Print.info(tabs + str(NacpLanguageType(i)) + ' Developer = ' + self.getDeveloper(i))

		Print.info(tabs + 'Startup User Account = ' + str(self.getStartupUserAccount()))