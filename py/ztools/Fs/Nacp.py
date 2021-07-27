from Fs.File import File
import Fs.Type
from binascii import hexlify as hx, unhexlify as uhx
from enum import IntEnum
import Print

import Keys
import re
import pykakasi
import io
indent = 1
tabs = '\t' * indent

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
	TraditionalChinese = 13
	SimplifiedChinese = 14

class NacpLanguage:
	def __init__(self):
		self.name = None
		self.publisher = None


class OrganizationType(IntEnum):
	CERO = 0
	GRACGCRB = 1
	GSRMR = 2
	ESRB = 3
	ClassInd = 4
	USK = 5
	PEGI = 6
	PEGIPortugal = 7
	PEGIBBFC = 8
	Russian = 9
	ACB = 10
	OFLC = 11

class RatingAge:
	def __init__(self):
		self.age = None


class Nacp(File):
	def __init__(self, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Nacp, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)


		self.languages = []

		for i in range(15):
			self.languages.append(NacpLanguage())

		self.isbn = None
		self.startupUserAccount = None
		self.userAccountSwitchLock = None
		self.addOnContentRegistrationType = None
		self.attribute = None
		self.parentalControl = None
		self.screenshot = None
		self.videoCapture = None
		self.dataLossConfirmation = None
		self.playLogPolicy = None
		self.presenceGroupId = None

		self.ages = []

		for i in range(12):
			self.ages.append(RatingAge())

		self.displayVersion = None
		self.addOnContentBaseId = None
		self.saveDataOwnerId = None
		self.userAccountSaveDataSize = None
		self.userAccountSaveDataJournalSize = None
		self.deviceSaveDataSize = None
		self.deviceSaveDataJournalSize = None
		self.bcatDeliveryCacheStorageSize = None
		self.applicationErrorCodeCategory = None
		self.localCommunicationId = None
		self.logoType = None
		self.logoHandling = None
		self.runtimeAddOnContentInstall = None
		self.crashReport = None
		self.hdcp = None
		self.seedForPseudoDeviceId = None
		self.bcatPassphrase = None
		self.userAccountSaveDataSizeMax = None
		self.userAccountSaveDataJournalSizeMax = None
		self.deviceSaveDataSizeMax = None
		self.deviceSaveDataJournalSizeMax = None
		self.temporaryStorageSize = None
		self.cacheStorageSize = None
		self.cacheStorageJournalSize = None
		self.cacheStorageDataAndJournalSizeMax = None
		self.cacheStorageIndexMax = None
		self.playLogQueryableApplicationId = None
		self.playLogQueryCapability = None
		self.repair = None
		self.programIndex = None
		self.requiredNetworkServiceLicenseOnLaunch = None


	def getName(self, i):
		self.seek(i * 0x300)
		self.languages[i].name = self.read(0x200)
		self.languages[i].name = self.languages[i].name.split(b'\0', 1)[0].decode('utf-8')
		return self.languages[i].name

	def getPublisher(self, i):
		self.seek(i * 0x300 + 0x200)
		self.languages[i].publisher = self.read(0x100)
		self.languages[i].publisher = self.languages[i].publisher.split(b'\0', 1)[0].decode('utf-8')
		return self.languages[i].publisher

	def par_getNameandPub(self, data, feed ='',gui=False,roma=True):
		Langue = list()
		Langue = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
		for i in Langue:
			off1=i*0x300;off2=off1+0x200;off3=off2+0x100
			title=data[off1:off2]
			title = title.split(b'\0', 1)[0].decode('utf-8')
			title = (re.sub(r'[\/\\]+', ' ', title))
			title = title.strip()
			if title == '':
				continue
			else:
				editor=data[off2:off3]
				editor = editor.split(b'\0', 1)[0].decode('utf-8')
				editor = (re.sub(r'[\/\\]+', ' ', editor))
				editor = editor.strip()
				if roma == True:
					if i == 2:
						kakasi = pykakasi.kakasi()
						kakasi.setMode("H", "a")
						kakasi.setMode("K", "a")
						kakasi.setMode("J", "a")
						kakasi.setMode("s", True)
						kakasi.setMode("E", "a")
						kakasi.setMode("a", None)
						kakasi.setMode("C", False)
						converter = kakasi.getConverter()
						title=converter.do(title)
						title=title[0].upper()+title[1:]
						editor=converter.do(editor)
						editor=editor[0].upper()+editor[1:]
					if i == 14 or i == 13 or i==12:
						kakasi = pykakasi.kakasi()
						kakasi.setMode("H", "a")
						kakasi.setMode("K", "a")
						kakasi.setMode("J", "a")
						kakasi.setMode("s", True)
						kakasi.setMode("E", "a")
						kakasi.setMode("a", None)
						kakasi.setMode("C", False)
				if gui==True:
					message=('...............................');print(message);feed+=message+'...............................'*2+'\n'
					message=('Language: '+ str(NacpLanguageType(i)).replace('NacpLanguageType.', ''));print(message);feed+=message+'\n'
					message=('...............................');print(message);feed+=message+'...............................'*2+'\n'
					message=('- Name: '+ title);print(message);feed+=message+'\n'
					message=('- Publisher: '+ editor);print(message);feed+=message+'\n'
				else:
					message=('...............................');print(message);feed+=message+'\n'
					message=('Language: '+ str(NacpLanguageType(i)).replace('NacpLanguageType.', ''));print(message);feed+=message+'\n'
					message=('...............................');print(message);feed+=message+'\n'
					message=('- Name: '+ title);print(message);feed+=message+'\n'
					message=('- Publisher: '+ editor);print(message);feed+=message+'\n'
		return feed


	def getIsbn(self):
		self.seek(0x3000)
		self.isbn = self.read(0x24).split(b'\0', 1)[0].decode('utf-8')
		return self.isbn

	def par_Isbn(self, data, feed =''):
		isbn=data.split(b'\0', 1)[0].decode('utf-8')
		if isbn != '':
			message=('- Isbn: ' + str(isbn));print(message);feed+=message+'\n'
		return feed

	def par_getStartupUserAccount(self, data, feed =''):
		b=data
		if b == 0:
			StartupUserAccount = 'None'
		elif b == 1:
			StartupUserAccount = 'Required'
		elif b == 2:
			StartupUserAccount = 'RequiredWithNetworkServiceAccountAvailable'
		else:
			StartupUserAccount = 'Unknown'
		message=('- StartupUserAccount: ' + str(StartupUserAccount));print(message);feed+=message+'\n'
		return feed

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
			self.startupUserAccount = 'Unknown'
		return self.startupUserAccount

	def par_getUserAccountSwitchLock(self, data, feed =''):
		b=data
		if b == 0:
			userAccountSwitchLock = 'Disable'
		elif b == 1:
			userAccountSwitchLock = 'Enable'
		else:
			userAccountSwitchLock = 'Unknown'
		message=('- UserAccountSwitchLock: ' + str(userAccountSwitchLock));print(message);feed+=message+'\n'
		return feed

	def getUserAccountSwitchLock(self):
		self.seek(0x3026)
		b = self.readInt8('little')
		if b == 0:
			self.userAccountSwitchLock = 'Disable'
		elif b == 1:
			self.userAccountSwitchLock = 'Enable'
		else:
			self.userAccountSwitchLock = 'Unknown'
		return self.userAccountSwitchLock

	def par_getAddOnContentRegistrationType(self, data, feed =''):
		b=data
		if b == 0:
			addOnContentRegistrationType = 'AllOnLaunch'
		elif b == 1:
			addOnContentRegistrationType = 'OnDemand'
		else:
			addOnContentRegistrationType = 'Unknown'
		message=('- AddOnContentRegistrationType: ' + str(addOnContentRegistrationType));print(message);feed+=message+'\n'
		return feed


	def getAddOnContentRegistrationType(self):
		self.seek(0x3027)
		b = self.readInt8('little')
		if b == 0:
			self.addOnContentRegistrationType = 'AllOnLaunch'
		elif b == 1:
			self.addOnContentRegistrationType = 'OnDemand'
		else:
			self.addOnContentRegistrationType = 'Unknown'
		return self.addOnContentRegistrationType

	def par_getContentType(self, data, feed =''):
		b=data
		if b == 0:
			content_type = 'False'
		elif b == 1:
			content_type = 'True'
		elif b == 2:
			content_type = 'RetailInteractiveDisplay'
		else:
			content_type = 'Unknown'
		message=('- IsDemo: ' + str(content_type));print(message);feed+=message+'\n'
		return feed


	def getAttribute(self):
		self.seek(0x3028)
		b = self.readInt8('little')
		if b == 0:
			self.attribute = 'None'
		elif b == 1:
			self.attribute = 'Demo'
		elif b == 2:
			self.attribute = 'RetailInteractiveDisplay'
		else:
			self.attribute = 'Unknown'
		return self.attribute

	def par_getParentalControl(self, data, feed =''):
		b=data
		if b == 0:
			parentalControl = 'None'
		elif b == 1:
			parentalControl = 'FreeCommunication'
		else:
			parentalControl = 'Unknown'
		message=('- ParentalControl: ' + str(parentalControl));print(message);feed+=message+'\n'
		return feed


	def getParentalControl(self):
		self.seek(0x3030)
		b = self.readInt8('little')
		if b == 0:
			self.parentalControl = 'None'
		elif b == 1:
			self.parentalControl = 'FreeCommunication'
		else:
			self.parentalControl = 'Unknown'
		return self.parentalControl

	def par_getScreenshot(self, data, feed =''):
		b=data
		if b == 0:
			screenshot = 'Allowed'
		elif b == 1:
			screenshot = 'Denied'
		else:
			screenshot = 'Unknown'
		message=('- Screenshots: ' + str(screenshot));print(message);feed+=message+'\n'
		return feed


	def getScreenshot(self):
		self.seek(0x3034)
		b = self.readInt8('little')
		if b == 0:
			self.screenshot = 'Allow'
		elif b == 1:
			self.screenshot = 'Deny'
		else:
			self.screenshot = 'Unknown'
		return self.screenshot

	def par_getVideoCapture(self, data, feed =''):
		b=data
		if b == 0:
			videoCapture = 'Disabled'
		elif b == 1:
			videoCapture = 'Manual'
		elif b == 2:
			videoCapture = 'Enabled'
		else:
			videoCapture = 'Unknown'
		message=('- VideoCapture: ' + str(videoCapture));print(message);feed+=message+'\n'
		return feed

	def getVideoCapture(self):
		self.seek(0x3035)
		b = self.readInt8('little')
		if b == 0:
			self.videoCapture = 'Disable'
		elif b == 1:
			self.videoCapture = 'Manual'
		elif b == 2:
			self.videoCapture = 'Enable'
		else:
			self.videoCapture = 'Unknown'
		return self.videoCapture

	def par_dataLossConfirmation(self, data, feed =''):
		b=data
		if b == 0:
			dataLossConfirmation = 'None'
		elif b == 1:
			dataLossConfirmation = 'Required'
		else:
			dataLossConfirmation = 'Unknown'
		message=('- DataLossConfirmation: ' + str(dataLossConfirmation));print(message);feed+=message+'\n'
		return feed

	def getDataLossConfirmation(self):
		self.seek(0x3036)
		b = self.readInt8('little')
		if b == 0:
			self.dataLossConfirmation = 'None'
		elif b == 1:
			self.dataLossConfirmation = 'Required'
		else:
			self.dataLossConfirmation = 'Unknown'
		return self.dataLossConfirmation


	def par_getPlayLogPolicy(self, data, feed =''):
		b=data
		if b == 0:
			playLogPolicy = 'All'
		elif b == 1:
			playLogPolicy = 'LogOnly'
		elif b == 2:
			playLogPolicy = 'None'
		else:
			playLogPolicy = 'Unknown'
		message=('- PlayLogPolicy: ' + str(playLogPolicy));print(message);feed+=message+'\n'
		return feed

	def getPlayLogPolicy(self):
		self.seek(0x3037)
		b = self.readInt8('little')
		if b == 0:
			self.playLogPolicy = 'All'
		elif b == 1:
			self.playLogPolicy = 'LogOnly'
		elif b == 2:
			self.playLogPolicy = 'None'
		else:
			self.playLogPolicy = 'Unknown'
		return self.playLogPolicy

	def par_getPresenceGroupId(self, data, feed =''):
		b=data
		message=('- PresenceGroupId: ' + '0x' + hex(data).replace('0x', '').zfill(16));print(message);feed+=message+'\n'
		return feed

	def getPresenceGroupId(self):
		self.seek(0x3038)
		self.presenceGroupId = self.readInt64('little')
		return self.presenceGroupId

	def par_getRatingAge(self,data,i, feed =''):
		b=data
		if b == 0:
			age = '0'
		elif b == 3:
			age = '3'
		elif b == 4:
			age = '4'
		elif b == 6:
			age = '6'
		elif b == 7:
			age = '7'
		elif b == 8:
			age = '8'
		elif b == 10:
			age = '10'
		elif b == 12:
			age = '12'
		elif b == 13:
			age = '13'
		elif b == 14:
			age = '14'
		elif b == 15:
			age = '15'
		elif b == 16:
			age = '16'
		elif b == 17:
			age = '17'
		elif b == 18:
			age = '18'
		else:
			age = 'Unknown'
		if age != 'Unknown':
			message=('- '+str(OrganizationType(i)).replace('OrganizationType.', '') + ' Rating: '+ str(age));print(message);feed+=message+'\n'
		return feed

	def getRatingAge(self, i):
		self.seek(i + 0x3040)
		b = self.readInt8('little')
		if b == 0:
			self.ages[i].age = '0'
		elif b == 3:
			self.ages[i].age = '3'
		elif b == 4:
			self.ages[i].age = '4'
		elif b == 6:
			self.ages[i].age = '6'
		elif b == 7:
			self.ages[i].age = '7'
		elif b == 8:
			self.ages[i].age = '8'
		elif b == 10:
			self.ages[i].age = '10'
		elif b == 12:
			self.ages[i].age = '12'
		elif b == 13:
			self.ages[i].age = '13'
		elif b == 14:
			self.ages[i].age = '14'
		elif b == 15:
			self.ages[i].age = '15'
		elif b == 16:
			self.ages[i].age = '16'
		elif b == 17:
			self.ages[i].age = '17'
		elif b == 18:
			self.ages[i].age = '18'
		else:
			self.ages[i].age = 'Unknown'
		return self.ages[i].age

	def par_getDisplayVersion(self, data, feed =''):
		b=data
		message=('- Build Number: ' + data.split(b'\0', 1)[0].decode('utf-8'));print(message);feed+=message+'\n'
		return feed

	def getDisplayVersion(self):
		self.seek(0x3060)
		self.displayVersion = self.read(0xF)
		self.displayVersion = self.displayVersion.split(b'\0', 1)[0].decode('utf-8')
		return self.displayVersion

	def par_getAddOnContentBaseId(self, data, feed =''):
		b=data
		message=('- AddOnContentBaseId: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getAddOnContentBaseId(self):
		self.seek(0x3070)
		self.addOnContentBaseId = self.readInt64('little')
		return self.addOnContentBaseId

	def par_getSaveDataOwnerId(self, data, feed =''):
		b=data
		message=('- SaveDataOwnerId: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getSaveDataOwnerId(self):
		self.seek(0x3078)
		self.saveDataOwnerId = self.readInt64('little')
		return self.saveDataOwnerId

	def par_getUserAccountSaveDataSize(self, data, feed =''):
		b=data
		message=('- UserAccountSaveDataSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getUserAccountSaveDataSize(self):
		self.seek(0x3080)
		self.userAccountSaveDataSize = self.readInt64('little')
		return self.userAccountSaveDataSize

	def par_getUserAccountSaveDataJournalSize(self, data, feed =''):
		b=data
		message=('- UserAccountSaveDataJournalSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getUserAccountSaveDataJournalSize(self):
		self.seek(0x3088)
		self.userAccountSaveDataJournalSize = self.readInt64('little')
		return self.userAccountSaveDataJournalSize

	def par_getDeviceSaveDataSize(self, data, feed =''):
		b=data
		if data==0:
			pass
		else:
			message=('- DeviceSaveDataSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getDeviceSaveDataSize(self):
		self.seek(0x3090)
		self.deviceSaveDataSize = self.readInt64('little')
		return self.deviceSaveDataSize

	def par_getDeviceSaveDataJournalSize(self, data, feed =''):
		b=data
		if data==0:
			pass
		else:
			message=('- DeviceSaveDataJournalSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getDeviceSaveDataJournalSize(self):
		self.seek(0x3098)
		self.deviceSaveDataJournalSize = self.readInt64('little')
		return self.deviceSaveDataJournalSize

	def par_getBcatDeliveryCacheStorageSize(self, data, feed =''):
		b=data
		if data==0:
			pass
		else:
			message=('- BcatDeliveryCacheStorageSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getBcatDeliveryCacheStorageSize(self):
		self.seek(0x30A0)
		self.bcatDeliveryCacheStorageSize = self.readInt64('little')
		return self.bcatDeliveryCacheStorageSize

	def par_getApplicationErrorCodeCategory(self, data, feed =''):
		b=data
		applicationErrorCodeCategory = data.split(b'\0', 1)[0].decode('utf-8')
		if applicationErrorCodeCategory == '':
			pass
		else:
			message=('- ApplicationErrorCodeCategory: ' + applicationErrorCodeCategory);print(message);feed+=message+'\n'
		return feed

	def getApplicationErrorCodeCategory(self):
		self.seek(0x30A8)
		self.applicationErrorCodeCategory = self.read(0x7).split(b'\0', 1)[0].decode('utf-8')
		return self.applicationErrorCodeCategory

	def par_getLocalCommunicationId(self, data, feed =''):
		b=data
		message=('- LocalCommunicationId: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getLocalCommunicationId(self):
		self.seek(0x30B0)
		self.localCommunicationId = self.readInt64('little')
		return self.localCommunicationId

	def par_getLogoType(self, data, feed =''):
		b=data
		if b == 0:
			logoType = 'LicensedByNintendo'
		elif b == 2:
			logoType = 'Nintendo'
		else:
			logoType = 'Unknown'
		message=('- LogoType: ' + logoType);print(message);feed+=message+'\n'
		return feed

	def getLogoType(self):
		self.seek(0x30F0)
		b = self.readInt8('little')
		if b == 0:
			self.logoType = 'LicensedByNintendo'
		elif b == 2:
			self.logoType = 'Nintendo'
		else:
			self.logoType = 'Unknown'
		return self.logoType

	def par_getLogoHandling(self, data, feed =''):
		b=data
		if b == 0:
			logoHandling = 'Auto'
		elif b == 1:
			logoHandling = 'Manual'
		else:
			logoHandling = 'Unknown'
		message=('- LogoHandling: ' + logoHandling);print(message);feed+=message+'\n'
		return feed

	def getLogoHandling(self):
		self.seek(0x30F1)
		b = self.readInt8('little')
		if b == 0:
			self.logoHandling = 'Auto'
		elif b == 1:
			self.logoHandling = 'Manual'
		else:
			self.logoHandling = 'Unknown'
		return self.logoHandling

	def par_getRuntimeAddOnContentInstall(self, data, feed =''):
		b=data
		if b == 0:
			runtimeAddOnContentInstall = 'Deny'
		elif b == 1:
			runtimeAddOnContentInstall = 'AllowAppend'
		else:
			runtimeAddOnContentInstall = 'Unknown'
		message=('- RuntimeAddOnContentInstall: ' + runtimeAddOnContentInstall);print(message);feed+=message+'\n'
		return feed

	def getRuntimeAddOnContentInstall(self):
		self.seek(0x30F2)
		b = self.readInt8('little')
		if b == 0:
			self.runtimeAddOnContentInstall = 'Deny'
		elif b == 1:
			self.runtimeAddOnContentInstall = 'AllowAppend'
		else:
			self.runtimeAddOnContentInstall = 'Unknown'
		return self.runtimeAddOnContentInstall

	def par_getCrashReport(self, data, feed =''):
		b=data
		if b == 0:
			crashReport = 'Deny'
		elif b == 1:
			crashReport = 'Allow'
		else:
			crashReport = 'Unknown'
		message=('- CrashReport: ' + crashReport);print(message);feed+=message+'\n'
		return feed

	def getCrashReport(self):
		self.seek(0x30F6)
		b = self.readInt8('little')
		if b == 0:
			self.crashReport = 'Deny'
		elif b == 1:
			self.crashReport = 'Allow'
		else:
			self.crashReport = 'Unknown'
		return self.crashReport

	def par_getHdcp(self, data, feed =''):
		b=data
		if b == 0:
			hdcp = 'None'
		elif b == 1:
			hdcp = 'Required'
		else:
			hdcp = 'Unknown'
		message=('- HDCP: ' + hdcp);print(message);feed+=message+'\n'
		return feed

	def getHdcp(self):
		self.seek(0x30F7)
		b = self.readInt8('little')
		if b == 0:
			self.hdcp = 'None'
		elif b == 1:
			self.hdcp = 'Required'
		else:
			self.hdcp = 'Unknown'
		return self.hdcp

	def par_getSeedForPseudoDeviceId(self, data, feed =''):
		message=('- SeedForPseudoDeviceId: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getSeedForPseudoDeviceId(self):
		self.seek(0x30F8)
		self.seedForPseudoDeviceId = self.readInt64('little')
		return self.seedForPseudoDeviceId

	def par_getBcatPassphrase(self, data, feed =''):
		bcatPassphrase = data.split(b'\0', 1)[0].decode('utf-8')
		if bcatPassphrase == 0:
			pass
		elif str(bcatPassphrase) == '':
			pass
		else:
			message=('- BcatPassphrase: ' + bcatPassphrase);print(message);feed+=message+'\n'
		return feed

	def getBcatPassphrase(self):
		self.seek(0x3100)
		self.bcatPassphrase = self.read(0x40).split(b'\0', 1)[0].decode('utf-8')
		return self.bcatPassphrase

	def par_UserAccountSaveDataSizeMax(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- UserAccountSaveDataSizeMax: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getUserAccountSaveDataSizeMax(self):
		self.seek(0x3148)
		self.userAccountSaveDataSizeMax = self.readInt64('little')
		return self.userAccountSaveDataSizeMax

	def par_UserAccountSaveDataJournalSizeMax(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- UserAccountSaveDataJournalSizeMax: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getUserAccountSaveDataJournalSizeMax(self):
		self.seek(0x3150)
		self.userAccountSaveDataJournalSizeMax = self.readInt64('little')
		return self.userAccountSaveDataJournalSizeMax

	def par_getDeviceSaveDataSizeMax(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- DeviceSaveDataSizeMax: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getDeviceSaveDataSizeMax(self):
		self.seek(0x3158)
		self.deviceSaveDataSizeMax = self.readInt64('little')
		return self.deviceSaveDataSizeMax

	def par_getDeviceSaveDataJournalSizeMax(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- DeviceSaveDataJournalSizeMax: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getDeviceSaveDataJournalSizeMax(self):
		self.seek(0x3160)
		self.deviceSaveDataJournalSizeMax = self.readInt64('little')
		return self.deviceSaveDataJournalSizeMax

	def par_getTemporaryStorageSize(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- TemporaryStorageSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getTemporaryStorageSize(self):
		self.seek(0x3168)
		self.temporaryStorageSize = self.readInt64('little')
		return self.temporaryStorageSize

	def par_getCacheStorageSize(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- CacheStorageSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getCacheStorageSize(self):
		self.seek(0x3170)
		self.cacheStorageSize = self.readInt64('little')
		return self.cacheStorageSize

	def par_getCacheStorageJournalSize(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- CacheStorageJournalSize: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getCacheStorageJournalSize(self):
		self.seek(0x3178)
		self.cacheStorageJournalSize = self.readInt64('little')
		return self.cacheStorageJournalSize

	def par_getCacheStorageDataAndJournalSizeMax(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- CacheStorageDataAndJournalSizeMax: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed


	def getCacheStorageDataAndJournalSizeMax(self):
		self.seek(0x3180)
		self.cacheStorageDataAndJournalSizeMax = self.readInt32('little')
		return self.cacheStorageDataAndJournalSizeMax

	def par_getCacheStorageIndexMax(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- CacheStorageIndexMax: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed

	def getCacheStorageIndexMax(self):
		self.seek(0x3188)
		self.cacheStorageIndexMax = self.readInt16('little')
		return self.cacheStorageIndexMax

	def par_getPlayLogQueryableApplicationId(self, data, feed =''):
		if data == 0:
			pass
		else:
			message=('- PlayLogQueryableApplicationId: ' + '0x' + (hex(data).replace('0x', '').zfill(16)).upper());print(message);feed+=message+'\n'
		return feed


	def getPlayLogQueryableApplicationId(self):
		self.seek(0x3190)
		self.playLogQueryableApplicationId = self.readInt64('little')
		return self.playLogQueryableApplicationId

	def par_getPlayLogQueryCapability(self, data, feed =''):
		b = data
		if b == 0:
			playLogQueryCapability = 'None'
		elif b == 1:
			playLogQueryCapability = 'WhiteList'
		elif b == 2:
			playLogQueryCapability = 'All'
		else:
			playLogQueryCapability = 'Unknown'
			message=('- PlayLogQueryCapability: ' + playLogQueryCapability);print(message);feed+=message+'\n'
		return feed

	def getPlayLogQueryCapability(self):
		self.seek(0x3210)
		b = self.readInt8('little')
		if b == 0:
			self.playLogQueryCapability = 'None'
		elif b == 1:
			self.playLogQueryCapability = 'WhiteList'
		elif b == 2:
			self.playLogQueryCapability = 'All'
		else:
			self.playLogQueryCapability = 'Unknown'
		return self.playLogQueryCapability

	def par_getRepair(self, data, feed =''):
		b = data
		if b == 0:
			repair = 'None'
		elif b == 1:
			repair = 'SuppressGameCardAccess'
		else:
			repair = 'Unknown'
		message=('- Repair: ' + repair);print(message);feed+=message+'\n'
		return feed


	def getRepair(self):
		self.seek(0x3211)
		b = self.readInt8('little')
		if b == 0:
			self.repair = 'None'
		elif b == 1:
			self.repair = 'SuppressGameCardAccess'
		else:
			self.repair = 'Unknown'
		return self.repair

	def par_getProgramIndex(self, data, feed =''):
		message=('- ProgramIndex: ' + str(data));print(message);feed+=message+'\n'
		return feed

	def getProgramIndex(self):
		self.seek(0x3212)
		self.programIndex = self.readInt8('little')
		return self.programIndex

	def par_getRequiredNetworkServiceLicenseOnLaunch(self, data, feed =''):
		b = data
		if b == 0:
			requiredNetworkServiceLicenseOnLaunch = 'None'
		elif b == 1:
			requiredNetworkServiceLicenseOnLaunch = 'Common'
		else:
			requiredNetworkServiceLicenseOnLaunch = 'Unknown'
		message=('- RequiredNetworkServiceLicenseOnLaunch: ' + requiredNetworkServiceLicenseOnLaunch);print(message);feed+=message+'\n'
		return feed

	def getRequiredNetworkServiceLicenseOnLaunch(self):
		self.seek(0x3213)
		b = self.readInt8('little')
		if b == 0:
			self.requiredNetworkServiceLicenseOnLaunch = 'None'
		elif b == 1:
			self.requiredNetworkServiceLicenseOnLaunch = 'Common'
		else:
			self.requiredNetworkServiceLicenseOnLaunch = 'Unknown'
		return self.requiredNetworkServiceLicenseOnLaunch


	def printInfo(self, indent = 0):
		tabs = '\t' * indent
		Print.info('\n%sNintendo Application Control Property (NACP)\n' % (tabs))
		super(Nacp, self).printInfo(indent)

		for i in range(15):
			if self.getName(i) == '':
				pass
			else:
				Print.info('Title:')
				Print.info('  Language: ' + str(NacpLanguageType(i)).replace('NacpLanguageType.', ''))
				Print.info('  Name: ' + self.getName(i))
				Print.info('  Publisher: ' + self.getPublisher(i))

		if str(self.getIsbn()) == '':
			 pass
		else:
			Print.info('Isbn: ' + str(self.getIsbn()))

		Print.info('AddOnContentRegistrationType: ' + str(self.getAddOnContentRegistrationType()))
		Print.info('StartupUserAccount: ' + str(self.getStartupUserAccount()))
		Print.info('UserAccountSwitchLock: ' + str(self.getUserAccountSwitchLock()))
		Print.info('Attribute: ' + str(self.getAttribute()))
		Print.info('ParentalControl: ' + str(self.getParentalControl()))
		Print.info('Screenshot: ' + str(self.getScreenshot()))
		Print.info('VideoCapture: ' + str(self.getVideoCapture()))
		Print.info('DataLossConfirmation: ' + str(self.getDataLossConfirmation()))
		Print.info('PlayLogPolicy: ' + str(self.getPlayLogPolicy()))
		Print.info('PresenceGroupId: ' + '0x' + hex(self.getPresenceGroupId()).replace('0x', '').zfill(16))

		for i in range(12):
			if str(self.getRatingAge(i)) == 'Unknown':
				pass
			else:
				Print.info('Rating:')
				Print.info('  Organization: ' + str(OrganizationType(i)).replace('OrganizationType.', ''))
				Print.info('  Age: ' + str(self.getRatingAge(i)))

		Print.info('DisplayVersion: ' + str(self.getDisplayVersion()))
		Print.info('AddOnContentBaseId: ' + '0x' + hex(self.getAddOnContentBaseId()).replace('0x', '').zfill(16))
		Print.info('SaveDataOwnerId: ' + '0x' + hex(self.getSaveDataOwnerId()).replace('0x', '').zfill(16))
		Print.info('UserAccountSaveDataSize: ' + '0x' + hex(self.getUserAccountSaveDataSize()).replace('0x', '').zfill(16))
		Print.info('UserAccountSaveDataJournalSize: ' + '0x' + hex(self.getUserAccountSaveDataJournalSize()).replace('0x', '').zfill(16))
		Print.info('DeviceSaveDataSize: ' + '0x' + hex(self.getDeviceSaveDataSize()).replace('0x', '').zfill(16))
		Print.info('DeviceSaveDataJournalSize: ' + '0x' + hex(self.getDeviceSaveDataJournalSize()).replace('0x', '').zfill(16))

		if hex(self.getBcatDeliveryCacheStorageSize()).replace('0x', '').zfill(16) == '0000000000000000':
			pass
		else:
			Print.info('BcatDeliveryCacheStorageSize: ' + '0x' + hex(self.getBcatDeliveryCacheStorageSize()).replace('0x', '').zfill(16))

		if str(self.getApplicationErrorCodeCategory()) == '':
			pass
		else:
			Print.info('ApplicationErrorCodeCategory: ' + str(self.getApplicationErrorCodeCategory()))

		Print.info('LocalCommunicationId: ' + '0x' + hex(self.getLocalCommunicationId()).replace('0x', '').zfill(16))
		Print.info('LogoType: ' + str(self.getLogoType()))
		Print.info('LogoHandling: ' + str(self.getLogoHandling()))
		Print.info('RuntimeAddOnContentInstall: ' + str(self.getRuntimeAddOnContentInstall()))
		Print.info('CrashReport: ' + str(self.getCrashReport()))
		Print.info('Hdcp: ' + str(self.getHdcp()))
		Print.info('SeedForPseudoDeviceId: ' + '0x' + hex(self.getSeedForPseudoDeviceId()).replace('0x', '').zfill(16))

		if str(self.getBcatPassphrase()) == '0000000000000000000000000000000000000000000000000000000000000000':
			pass
		elif str(self.getBcatPassphrase()) == '':
			pass
		else:
			Print.info('BcatPassphrase: ' + str(self.getBcatPassphrase()))

		Print.info('UserAccountSaveDataSizeMax: ' + '0x' + hex(self.getUserAccountSaveDataSizeMax()).replace('0x', '').zfill(16))
		Print.info('UserAccountSaveDataJournalSizeMax: ' + '0x' + hex(self.getUserAccountSaveDataJournalSizeMax()).replace('0x', '').zfill(16))
		Print.info('DeviceSaveDataSizeMax: ' + '0x' + hex(self.getDeviceSaveDataSizeMax()).replace('0x', '').zfill(16))
		Print.info('DeviceSaveDataJournalSizeMax: ' + '0x' + hex(self.getDeviceSaveDataJournalSizeMax()).replace('0x', '').zfill(16))
		Print.info('TemporaryStorageSize: ' + '0x' + hex(self.getTemporaryStorageSize()).replace('0x', '').zfill(16))
		Print.info('CacheStorageSize: ' + '0x' + hex(self.getCacheStorageSize()).replace('0x', '').zfill(16))
		Print.info('CacheStorageJournalSize: ' + '0x' + hex(self.getCacheStorageJournalSize()).replace('0x', '').zfill(16))
		Print.info('CacheStorageDataAndJournalSizeMax: ' + '0x' + hex(self.getCacheStorageDataAndJournalSizeMax()).replace('0x', '').zfill(8))
		Print.info('CacheStorageIndexMax: ' + '0x' + hex(self.getCacheStorageIndexMax()).replace('0x', '').zfill(4))
		Print.info('PlayLogQueryableApplicationId: ' + '0x' + hex(self.getPlayLogQueryableApplicationId()).replace('0x', '').zfill(16))
		Print.info('PlayLogQueryCapability: ' + str(self.getPlayLogQueryCapability()))
		Print.info('Repair: ' + str(self.getRepair()))
		Print.info('ProgramIndex: ' + str(self.getProgramIndex()))
		Print.info('RequiredNetworkServiceLicenseOnLaunch: ' + str(self.getRequiredNetworkServiceLicenseOnLaunch()))

############
# RETURNS
############
	def get_NameandPub(self, data):
		Langue = list()
		Langue = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
		lstring={}
		editstring={}
		for i in Langue:
			off1=i*0x300;off2=off1+0x200;off3=off2+0x100
			title=data[off1:off2]
			title = title.split(b'\0', 1)[0].decode('utf-8')
			title = (re.sub(r'[\/\\]+', ' ', title))
			title = title.strip()
			if title == '':
				continue
			else:
				editor=data[off2:off3]
				editor = editor.split(b'\0', 1)[0].decode('utf-8')
				editor = (re.sub(r'[\/\\]+', ' ', editor))
				editor = editor.strip()
				Language=str(NacpLanguageType(i)).replace('NacpLanguageType.', '')
				lstring[Language]=title
				editstring[Language]=editor
		return lstring,editstring

	def get_Isbn(self, data):
		isbn=data.split(b'\0', 1)[0].decode('utf-8')
		if isbn == '':
			isbn=None
		return str(isbn)

	def get_StartupUserAccount(self, data):
		b=data
		if b == 0:
			StartupUserAccount = 'None'
		elif b == 1:
			StartupUserAccount = 'Required'
		elif b == 2:
			StartupUserAccount = 'RequiredWithNetworkServiceAccountAvailable'
		else:
			StartupUserAccount = 'Unknown'
		return str(StartupUserAccount)

	def get_UserAccountSwitchLock(self, data):
		b=data
		if b == 0:
			userAccountSwitchLock = 'Disable'
		elif b == 1:
			userAccountSwitchLock = 'Enable'
		else:
			userAccountSwitchLock = 'Unknown'
		return str(userAccountSwitchLock)

	def get_AddOnContentRegistrationType(self, data):
		b=data
		if b == 0:
			addOnContentRegistrationType = 'AllOnLaunch'
		elif b == 1:
			addOnContentRegistrationType = 'OnDemand'
		else:
			addOnContentRegistrationType = 'Unknown'
		return str(addOnContentRegistrationType)


	def get_ContentType(self, data):
		b=data
		if b == 0:
			content_type = 'False'
		elif b == 1:
			content_type = 'True'
		elif b == 2:
			content_type = 'RetailInteractiveDisplay'
		else:
			content_type = 'Unknown'
		return str(content_type)

	def get_ParentalControl(self, data):
		b=data
		if b == 0:
			parentalControl = 'None'
		elif b == 1:
			parentalControl = 'FreeCommunication'
		else:
			parentalControl = 'Unknown'
		return str(parentalControl)

	def get_Screenshot(self, data):
		b=data
		if b == 0:
			screenshot = 'Allowed'
		elif b == 1:
			screenshot = 'Denied'
		else:
			screenshot = 'Unknown'
		return 	str(screenshot)

	def get_VideoCapture(self, data):
		b=data
		if b == 0:
			videoCapture = 'Disabled'
		elif b == 1:
			videoCapture = 'Manual'
		elif b == 2:
			videoCapture = 'Enabled'
		else:
			videoCapture = 'Unknown'
		return str(videoCapture)

	def get_dataLossConfirmation(self, data):
		b=data
		if b == 0:
			dataLossConfirmation = 'None'
		elif b == 1:
			dataLossConfirmation = 'Required'
		else:
			dataLossConfirmation = 'Unknown'
		return str(dataLossConfirmation)

	def get_PlayLogPolicy(self, data):
		b=data
		if b == 0:
			playLogPolicy = 'All'
		elif b == 1:
			playLogPolicy = 'LogOnly'
		elif b == 2:
			playLogPolicy = 'None'
		else:
			playLogPolicy = 'Unknown'
		return str(playLogPolicy)

	def get_PresenceGroupId(self, data):
		b=data
		PresenceGroupId='0x' + hex(data).replace('0x', '').zfill(16)
		return PresenceGroupId

	def get_RatingAge(self,data):
		inmemoryfile = io.BytesIO(data)
		AgeRatings={}
		for i in range(12):
			b=int(inmemoryfile.read(1)[0])
			if b == 0:
				age = '0'
			elif b == 3:
				age = '3'
			elif b == 4:
				age = '4'
			elif b == 6:
				age = '6'
			elif b == 7:
				age = '7'
			elif b == 8:
				age = '8'
			elif b == 10:
				age = '10'
			elif b == 12:
				age = '12'
			elif b == 13:
				age = '13'
			elif b == 14:
				age = '14'
			elif b == 15:
				age = '15'
			elif b == 16:
				age = '16'
			elif b == 17:
				age = '17'
			elif b == 18:
				age = '18'
			else:
				age = 'Unknown'
			if 	age != 'Unknown':
				Org=str(OrganizationType(i)).replace('OrganizationType.', '')
				AgeRatings[Org]	=str(age)
		#print(AgeRatings)
		return AgeRatings

	def get_DisplayVersion(self, data):
		b=data
		buildnumber=data.split(b'\0', 1)[0].decode('utf-8')
		return buildnumber

	def get_AddOnContentBaseId(self, data):
		b=data
		AddOnContentBaseId= '0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return AddOnContentBaseId

	def get_SaveDataOwnerId(self, data):
		b=data
		SaveDataOwnerId='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return SaveDataOwnerId

	def get_UserAccountSaveDataSize(self, data):
		b=data
		UserAccountSaveDataSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return UserAccountSaveDataSize

	def get_UserAccountSaveDataJournalSize(self, data):
		b=data
		UserAccountSaveDataJournalSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return UserAccountSaveDataJournalSize

	def get_DeviceSaveDataSize(self, data):
		b=data
		if data==0:
			DeviceSaveDataSize='None'
		else:
			DeviceSaveDataSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return DeviceSaveDataSize

	def get_DeviceSaveDataJournalSize(self, data):
		b=data
		if data==0:
			DeviceSaveDataJournalSize='None'
		else:
			DeviceSaveDataJournalSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return DeviceSaveDataJournalSize

	def get_BcatDeliveryCacheStorageSize(self, data):
		b=data
		if data==0:
			BcatDeliveryCacheStorageSize='None'
		else:
			BcatDeliveryCacheStorageSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return BcatDeliveryCacheStorageSize

	def get_ApplicationErrorCodeCategory(self, data):
		b=data
		applicationErrorCodeCategory = data.split(b'\0', 1)[0].decode('utf-8')
		if applicationErrorCodeCategory == '':
			applicationErrorCodeCategory='None'
		return applicationErrorCodeCategory

	def get_LocalCommunicationId(self, data):
		b=data
		LocalCommunicationId='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return LocalCommunicationId

	def get_LogoType(self, data):
		b=data
		if b == 0:
			logoType = 'LicensedByNintendo'
		elif b == 2:
			logoType = 'Nintendo'
		else:
			logoType = 'Unknown'
		return logoType

	def get_LogoHandling(self, data):
		b=data
		if b == 0:
			logoHandling = 'Auto'
		elif b == 1:
			logoHandling = 'Manual'
		else:
			logoHandling = 'Unknown'
		return logoHandling

	def get_RuntimeAddOnContentInstall(self, data):
		b=data
		if b == 0:
			runtimeAddOnContentInstall = 'Deny'
		elif b == 1:
			runtimeAddOnContentInstall = 'AllowAppend'
		else:
			runtimeAddOnContentInstall = 'Unknown'
		return runtimeAddOnContentInstall

	def get_CrashReport(self, data):
		b=data
		if b == 0:
			crashReport = 'Deny'
		elif b == 1:
			crashReport = 'Allow'
		else:
			crashReport = 'Unknown'
		return crashReport

	def get_Hdcp(self, data):
		b=data
		if b == 0:
			hdcp = 'None'
		elif b == 1:
			hdcp = 'Required'
		else:
			hdcp = 'Unknown'
		return hdcp

	def get_SeedForPseudoDeviceId(self, data):
		SeedForPseudoDeviceId='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return SeedForPseudoDeviceId

	def get_BcatPassphrase(self, data):
		bcatPassphrase = data.split(b'\0', 1)[0].decode('utf-8')
		if bcatPassphrase == 0:
			bcatPassphrase='None'
		elif str(bcatPassphrase) == '':
			bcatPassphrase='None'
		return bcatPassphrase

	def get_UserAccountSaveDataSizeMax(self, data):
		if data == 0:
			UserAccountSaveDataSizeMax='None'
		else:
			UserAccountSaveDataSizeMax='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return UserAccountSaveDataSizeMax

	def get_UserAccountSaveDataJournalSizeMax(self, data):
		if data == 0:
			UserAccountSaveDataJournalSizeMax='None'
		else:
			UserAccountSaveDataJournalSizeMax='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return UserAccountSaveDataJournalSizeMax

	def get_DeviceSaveDataSizeMax(self, data):
		if data == 0:
			DeviceSaveDataSizeMax='None'
		else:
			DeviceSaveDataSizeMax='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return DeviceSaveDataSizeMax

	def get_DeviceSaveDataJournalSizeMax(self, data):
		if data == 0:
			DeviceSaveDataJournalSizeMax='None'
		else:
			DeviceSaveDataJournalSizeMax='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return DeviceSaveDataJournalSizeMax

	def get_TemporaryStorageSize(self, data):
		if data == 0:
			TemporaryStorageSize='None'
		else:
			TemporaryStorageSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return TemporaryStorageSize

	def get_CacheStorageSize(self, data):
		if data == 0:
			CacheStorageSize='None'
		else:
			CacheStorageSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return CacheStorageSize

	def get_CacheStorageJournalSize(self, data):
		if data == 0:
			CacheStorageJournalSize='None'
		else:
			CacheStorageJournalSize='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return CacheStorageJournalSize

	def get_CacheStorageDataAndJournalSizeMax(self, data):
		if data == 0:
			CacheStorageDataAndJournalSizeMax='None'
		else:
			CacheStorageDataAndJournalSizeMax='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return CacheStorageDataAndJournalSizeMax

	def get_CacheStorageIndexMax(self, data):
		if data == 0:
			CacheStorageIndexMax='None'
		else:
			CacheStorageIndexMax='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return CacheStorageIndexMax

	def get_PlayLogQueryableApplicationId(self, data):
		if data == 0:
			PlayLogQueryableApplicationId='None'
		else:
			PlayLogQueryableApplicationId='0x' + (hex(data).replace('0x', '').zfill(16)).upper()
		return PlayLogQueryableApplicationId

	def get_PlayLogQueryCapability(self, data):
		b = data
		if b == 0:
			playLogQueryCapability = 'None'
		elif b == 1:
			playLogQueryCapability = 'WhiteList'
		elif b == 2:
			playLogQueryCapability = 'All'
		else:
			playLogQueryCapability = 'Unknown'
		return playLogQueryCapability

	def get_Repair(self, data):
		b = data
		if b == 0:
			repair = 'None'
		elif b == 1:
			repair = 'SuppressGameCardAccess'
		else:
			repair = 'Unknown'
		return repair

	def get_ProgramIndex(self, data):
		ProgramIndex=str(data)
		return ProgramIndex

	def get_RequiredNetworkServiceLicenseOnLaunch(self, data):
		b = data
		if b == 0:
			requiredNetworkServiceLicenseOnLaunch = 'None'
		elif b == 1:
			requiredNetworkServiceLicenseOnLaunch = 'Common'
		else:
			requiredNetworkServiceLicenseOnLaunch = 'Unknown'
		return requiredNetworkServiceLicenseOnLaunch
