from Fs.File import File
import Print
from binascii import hexlify as hx, unhexlify as uhx
indent = 1
tabs = '\t' * indent

class BaseFs(File):
	def __init__(self, buffer, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):		
		self.buffer = buffer
		self.sectionStart = 0
		self.fsType = None
		self.cryptoType = None
		self.size = 0
		self.cryptoCounter = None
		self.magic = None
		
		#if buffer:
		#	Hex.dump(buffer)
			
		self.files = []
		
		if buffer:
			self.buffer = buffer
			try:
				self.fsType = Fs.Type.Fs(buffer[0x3])
			except:
				self.fsType = buffer[0x3]

			try:
				self.cryptoType = Fs.Type.Crypto(buffer[0x4])
			except:
				self.cryptoType = buffer[0x4]
			
			self.cryptoCounter = bytearray((b"\x00"*8) + buffer[0x140:0x148])
			self.cryptoCounter = self.cryptoCounter[::-1]
			
			cryptoType = self.cryptoType
			cryptoCounter = self.cryptoCounter
		#else:
		#	Print.info('no sfs buffer')
			
		super(BaseFs, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)
		
	def __getitem__(self, key):
		if isinstance(key, str):
			for f in self.files:
				if f.name == key:
					return f
		elif isinstance(key, int):
			return self.files[key]
				
		raise IOError('FS File Not Found')
		
	def printInfo(self, indent):
		tabs = '\t' * indent
		Print.info(tabs + 'magic = ' + str(self.magic))
		Print.info(tabs + 'fsType = ' + str(self.fsType))
		Print.info(tabs + 'cryptoType = ' + str(self.cryptoType))
		Print.info(tabs + 'size = ' + str(self.size))
		Print.info(tabs + 'offset = ' + str(self.offset))
		if self.cryptoCounter:
			Print.info(tabs + 'cryptoCounter = ' + str(hx(self.cryptoCounter)))
			
		if self.cryptoKey:
			Print.info(tabs + 'cryptoKey = ' + str(hx(self.cryptoKey)))
		
		Print.info('\n%s\t%s\n' % (tabs, '*' * 64))
		Print.info('\n%s\tFiles:\n' % (tabs))
		
		for f in self:
			f.printInfo(indent+1)
			Print.info('\n%s\t%s\n' % (tabs, '*' * 64))
	def get_cryptoType(self):
		return self.cryptoType
		
	def get_cryptoKey(self):
		return self.cryptoKey

	def get_cryptoCounter(self):
		return self.cryptoCounter					