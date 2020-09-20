from Fs.File import File
import Fs.Type
from binascii import hexlify as hx, unhexlify as uhx
import Print
import Keys
import Hex
from binascii import hexlify as hx, unhexlify as uhx
import os
indent = 1
tabs = '\t' * indent	

class Ticket(File):
	def __init__(self, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Ticket, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)

		self.signatureType = None
		self.signature = None
		self.signaturePadding = None

		self.issuer = None
		self.titleKeyBlock = None
		self.keyType = None
		self.masterKeyRevision = None
		self.ticketId = None
		self.deviceId = None
		self.rightsId = None
		self.accountId = None

		self.signatureSizes = {}
		self.signatureSizes[Fs.Type.TicketSignature.RSA_4096_SHA1] = 0x200
		self.signatureSizes[Fs.Type.TicketSignature.RSA_2048_SHA1] = 0x100
		self.signatureSizes[Fs.Type.TicketSignature.ECDSA_SHA1] = 0x3C
		self.signatureSizes[Fs.Type.TicketSignature.RSA_4096_SHA256] = 0x200
		self.signatureSizes[Fs.Type.TicketSignature.RSA_2048_SHA256] = 0x100
		self.signatureSizes[Fs.Type.TicketSignature.ECDSA_SHA256] = 0x3C

	def open(self, file = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Ticket, self).open(file, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()
		self.signatureType = self.readInt32()
		try:
			self.signatureType = Fs.Type.TicketSignature(self.signatureType)
		except:
			raise IOError('Invalid ticket format')

		self.signaturePadding = 0x40 - ((self.signatureSizes[self.signatureType] + 4) % 0x40)

		self.seek(0x4 + self.signatureSizes[self.signatureType] + self.signaturePadding)

		self.issuer = self.read(0x40)
		self.titleKeyBlock = self.read(0x100)
		self.readInt8() # unknown
		self.keyType = self.readInt8()
		self.read(0x4) # unknown
		self.masterKeyRevision = self.readInt8()
		self.read(0x9) # unknown
		self.ticketId = hx(self.read(0x8)).decode('utf-8')
		self.deviceId = hx(self.read(0x8)).decode('utf-8')
		self.rightsId = hx(self.read(0x10)).decode('utf-8')
		self.accountId = hx(self.read(0x4)).decode('utf-8')
		self.masterKeyRevision = self.getMasterKeyRevision()

	def seekStart(self, offset):
		self.seek(0x4 + self.signatureSizes[self.signatureType] + self.signaturePadding + offset)

	def getSignatureType(self):
		self.seek(0x0)
		self.signatureType = self.readInt32()
		return self.signatureType

	def setSignatureType(self, value):
		self.seek(0x0)
		self.signatureType = value
		self.writeInt32(value)
		return self.signatureType

	def getSignature(self):
		self.seek(0x4)
		self.signature = self.read(self.signatureSizes[self.getSignatureType()])
		return self.signature

	def setSignature(self, value):
		self.seek(0x4)
		self.signature = value
		self.write(value, self.signatureSizes[self.getSignatureType()])
		return self.signature

	def getSignaturePadding(self):
		self.signaturePadding = 0x40 - ((self.signatureSizes[self.signatureType] + 4) % 0x40)
		return self.signaturePadding

	def getIssuer(self):
		self.seekStart(0x0)
		self.issuer = self.read(0x40)
		return self.issuer

	def setIssuer(self, value):
		self.seekStart(0x0)
		self.issuer = value
		self.write(value, 0x40)
		return self.issuer


	def getTitleKeyBlock(self):
		self.seekStart(0x40)
		#self.titleKeyBlock = self.readInt(0x100, 'big')
		self.titleKeyBlock = self.readInt(0x10, 'big')
		return self.titleKeyBlock

	def getTitleKey(self):
		self.seekStart(0x40)
		return self.read(0x10)

	def setTitleKeyBlock(self, value):
		self.seekStart(0x40)
		self.titleKeyBlock = value
		#self.writeInt(value, 0x100, 'big')
		self.writeInt(value, 0x10, 'big')
		return self.titleKeyBlock


	def getKeyType(self):
		self.seekStart(0x141)
		self.keyType = self.readInt8()
		return self.keyType

	def setKeyType(self, value):
		self.seekStart(0x141)
		self.keyType = value
		self.writeInt8(value)
		return self.keyType

	def getMasterKeyRevision(self):
		self.seekStart(0x144)
		self.masterKeyRevision = self.readInt8() | self.readInt8()
		masterKeyRevision1=self.masterKeyRevision 
		if self.masterKeyRevision == 0:
			self.rewind()
			self.seekStart(0x145)
			self.masterKeyRevision = self.readInt8() | self.readInt8()			
			if self.masterKeyRevision == 0:
				filename = str(self._path)
				filename = filename[:-4] 
				filename = filename[-2:] 	
				if filename != '00':				
					if filename[0]=='0':
						filename=filename[-1] 				
						self.masterKeyRevision = int(filename,16) 
					else:
						try:
							self.masterKeyRevision = int(filename,16)
						except:pass	
				else:self.masterKeyRevision=0
			elif self.masterKeyRevision >2:	
				filename = str(self._path)		
				filename = filename[:-4] 
				filename = filename[-2:] 				
				if filename != '00': 
					if filename[0]=='0':
						filename=filename[-1] 						
						if int(filename,16)==self.masterKeyRevision:
							pass	
						else:
							self.masterKeyRevision=masterKeyRevision1
				else:
					self.masterKeyRevision=masterKeyRevision1					
		elif self.masterKeyRevision > 2:		
			self.rewind()
			self.seekStart(0x145)
			test = self.readInt8() | self.readInt8()
			if test > 0 and test<self.masterKeyRevision:
				filename = str(self._path)
				filename = filename[:-4] 
				filename = filename[-1] 			
				if filename != '00':
					if filename[0]=='0':
						filename=filename[-1] 	
						if int(filename,16) ==test:
							self.masterKeyRevision==test
					else:
						try:					
							self.masterKeyRevision = int(filename,16)	
						except:pass								
		return self.masterKeyRevision

	def setMasterKeyRevision(self, value):
		self.seekStart(0x145)
		self.masterKeyRevision = value
		self.writeInt8(value)
		return self.masterKeyRevision


	def getTicketId(self):
		self.seekStart(0x150)
		self.ticketId = self.readInt64('big')
		return self.ticketId

	def setTicketId(self, value):
		self.seekStart(0x150)
		self.ticketId = value
		self.writeInt64(value, 'big')
		return self.ticketId


	def getDeviceId(self):
		self.seekStart(0x158)
		self.deviceId = self.readInt64('big')
		return self.deviceId

	def setDeviceId(self, value):
		self.seekStart(0x158)
		self.deviceId = value
		self.writeInt64(value, 'big')
		return self.deviceId


	def getRightsId(self):
		self.seekStart(0x160)
		self.rightsId = self.readInt128('big')
		return self.rightsId

	def setRightsId(self, value):
		self.seekStart(0x160)
		self.rightsId = value
		self.writeInt128(value, 'big')
		return self.rightsId


	def getAccountId(self):
		self.seekStart(0x170)
		self.accountId = self.readInt32('big')
		return self.accountId

	def setAccountId(self, value):
		self.seekStart(0x170)
		self.accountId = value
		self.writeInt32(value, 'big')
		return self.accountId
		
	def titleId(self):
		rightsId = format(self.getRightsId(), 'X').zfill(32)
		return rightsId[0:16]

	def titleKey(self):
		return format(self.getTitleKeyBlock(), 'X').zfill(32)		
	

	def printInfo(self, indent = 0):
		tabs = '\t' * indent
		Print.info('\n%sTicket\n' % (tabs))
		super(Ticket, self).printInfo(indent)
		Print.info(tabs + 'signatureType = ' + str(self.signatureType))
		Print.info(tabs + 'keyType = ' + str(self.keyType))
		Print.info(tabs + 'masterKeyRev = ' + str(self.getMasterKeyRevision()))
		Print.info(tabs + 'ticketId = ' + str(self.ticketId))
		Print.info(tabs + 'deviceId = ' + str(self.deviceId))
		Print.info(tabs + 'rightsId = ' + hex(self.getRightsId()))
		Print.info(tabs + 'accountId = ' + str(self.accountId))
		Print.info(tabs + 'titleKey = ' + hex(self.getTitleKeyBlock()))
		Print.info(tabs + 'titleKeyDec = ' + str(hx(Keys.decryptTitleKey((self.getTitleKey()), (Keys.getMasterKeyIndex(self.masterKeyRevision))))))


class PublicTik():
	def generate(self,titleid,titlekey,keygeneration,outfolder=None,Signature=None,signaturePadding=None,RSA_magic='04000100',issuer=None):
		if int(keygeneration,16)>9:
			keygeneration=str(hex(int(keygeneration,16)))[2:]
		try:
			# print(len(str(keygeneration)))
			if len(str(keygeneration))==1:
				tikname=str(titleid).lower()+'000000000000000'+keygeneration+'.tik'
			elif len(str(keygeneration))==2:
				tikname=str(titleid)+'00000000000000'+keygeneration+'.tik'		
			print(tikname)	
			if outfolder != None:
				tikpath=os.path.join(outfolder, tikname)	
			chain=''	
			if RSA_magic=='04000100':
				RSA_2048_SHA256 ='04000100';chain+=RSA_2048_SHA256
			else:
				chain+=RSA_magic
			if Signature==None:
				fake_sig='FF'*0x100;chain+=fake_sig
			else:
				chain+=Signature
			if signaturePadding==None:				
				padding='00'*0x3C;chain+=padding
			else:				
				chain+=signaturePadding
			if issuer==None:
				issuer='526F6F742D434130303030303030332D58533030303030303230';chain+=issuer
			else:
				chain+=issuer
			padding2='00'*0x26;chain+=padding2
			titlekey=str(titlekey).upper();chain+=titlekey
			padding3='00'*0xF0;chain+=padding3
			fixed='02';chain+=fixed
			padding4='00'*0x04;chain+=padding4
			keygeneration=tikname[-6:-4];chain+=keygeneration
			padding5='0000000000000000000000000000000000000000000000000000';chain+=padding5
			rightsid=(str(tikname)[:-4]).upper();chain+=rightsid
			# print(rightsid)
			end_line='0000000000000000C002000000000000';chain+=end_line	
			chain=bytearray.fromhex(chain)
			# Hex.dump(chain)
			return chain			
		except BaseException as e:
			Print.error('Exception: ' + str(e))	

class PublicCert():

	def generate(self,titleid=None,titlekey=None,keygeneration=None,outfolder=None):
		try:	
			if outfolder != None:
				if int(keygeneration,16)>9:
					keygeneration=str(hex(keygeneration))[2:]				
				if len(str(keygeneration))==1:
					certname=str(titleid).lower()+'000000000000000'+keygeneration+'.cert'
				elif len(str(keygeneration))==2:
					certname=str(titleid)+'00000000000000'+keygeneration+'.cert'				
				certpath=os.path.join(outfolder, certname)		
			chain='00010004969FE8288DA6B9DD52C7BD63642A4A9AE5F053ECCB93613FDA37992087BD9199DA5E6797618D77098133FD5B05CD8288139E2E975CD2608003878CDAF020F51A0E5B7692780845561B31C61808E8A47C3462224D94F736E9A14E56ACBF71B7F11BBDEE38DDB846D6BD8F0AB4E4948C5434EAF9BF26529B7EB83671D3CE60A6D7A850DBE6801EC52A7B7A3E5A27BC675BA3C53377CFC372EBCE02062F59F37003AA23AE35D4880E0E4B69F982FB1BAC806C2F75BA29587F2815FD7783998C354D52B19E3FAD9FBEF444C48579288DB0978116AFC82CE54DACB9ED7E1BFD50938F22F85EECF3A4F426AE5FEB15B72F022FB36ECCE9314DAD131429BFC9675F58EE000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000526F6F742D4341303030303030303300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000015853303030303030323000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000D21D3CE67C1069DA049D5E5310E76B907E18EEC80B337C4723E339573F4C664907DB2F0832D03DF5EA5F160A4AF24100D71AFAC2E3AE75AFA1228012A9A21616597DF71EAFCB65941470D1B40F5EF83A597E179FCB5B57C2EE17DA3BC3769864CB47856767229D67328141FC9AB1DF149E0C5C15AEB80BC58FC71BE18966642D68308B506934B8EF779F78E4DDF30A0DCF93FCAFBFA131A8839FD641949F47EE25CEECF814D55B0BE6E5677C1EFFEC6F29871EF29AA3ED9197B0D83852E050908031EF1ABBB5AFC8B3DD937A076FF6761AB362405C3F7D86A3B17A6170A659C16008950F7F5E06A5DE3E5998895EFA7DEEA060BE9575668F78AB1907B3BA1B7D000100010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010003704138EFBBBDA16A987DD901326D1C9459484C88A2861B91A312587AE70EF6237EC50E1032DC39DDE89A96A8E859D76A98A6E7E36A0CFE352CA893058234FF833FCB3B03811E9F0DC0D9A52F8045B4B2F9411B67A51C44B5EF8CE77BD6D56BA75734A1856DE6D4BED6D3A242C7C8791B3422375E5C779ABF072F7695EFA0F75BCB83789FC30E3FE4CC8392207840638949C7F688565F649B74D63D8D58FFADDA571E9554426B1318FC468983D4C8A5628B06B6FC5D507C13E7A18AC1511EB6D62EA5448F83501447A9AFB3ECC2903C9DD52F922AC9ACDBEF58C6021848D96E208732D3D1D9D9EA440D91621C7A99DB8843C59C1F2E2C7D9B577D512C166D6F7E1AAD4A774A37447E78FE2021E14A95D112A068ADA019F463C7A55685AABB6888B9246483D18B9C806F474918331782344A4B8531334B26303263D9D2EB4F4BB99602B352F6AE4046C69A5E7E8E4A18EF9BC0A2DED61310417012FD824CC116CFB7C4C1F7EC7177A17446CBDE96F3EDD88FCD052F0B888A45FDAF2B631354F40D16E5FA9C2C4EDA98E798D15E6046DC5363F3096B2C607A9D8DD55B1502A6AC7D3CC8D8C575998E7D796910C804C495235057E91ECD2637C9C1845151AC6B9A0490AE3EC6F47740A0DB0BA36D075956CEE7354EA3E9A4F2720B26550C7D394324BC0CB7E9317D8A8661F42191FF10B08256CE3FD25B745E5194906B4D61CB4C2E000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000526F6F7400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001434130303030303030330000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007BE8EF6CB279C9E2EEE121C6EAF44FF639F88F078B4B77ED9F9560B0358281B50E55AB721115A177703C7A30FE3AE9EF1C60BC1D974676B23A68CC04B198525BC968F11DE2DB50E4D9E7F071E562DAE2092233E9D363F61DD7C19FF3A4A91E8F6553D471DD7B84B9F1B8CE7335F0F5540563A1EAB83963E09BE901011F99546361287020E9CC0DAB487F140D6626A1836D27111F2068DE4772149151CF69C61BA60EF9D949A0F71F5499F2D39AD28C7005348293C431FFBD33F6BCA60DC7195EA2BCC56D200BAF6D06D09C41DB8DE9C720154CA4832B69C08C69CD3B073A0063602F462D338061A5EA6C915CD5623579C3EB64CE44EF586D14BAAA8834019B3EEBEED3790001000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
			chain=bytearray.fromhex(chain)
			# Hex.dump(chain)
			return chain
		except BaseException as e:
			Print.error('Exception: ' + str(e))		