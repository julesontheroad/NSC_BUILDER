import aes128
import Title
import Titles
import Hex
import math  
from binascii import hexlify as hx, unhexlify as uhx
from struct import pack as pk, unpack as upk
from Fs.File import File
from hashlib import sha256
import Fs.Type
from Fs.Pfs0 import Pfs0
from Fs.Ticket import Ticket
from Fs.Nca import Nca
from Fs.BaseFs import BaseFs
import os
import re
import pathlib
import Keys
import Config
import Print
import Nsps
import Fs
from tqdm import tqdm

MEDIA_SIZE = 0x200
indent = 1
tabs = '\t' * indent	

class Hfs0(Pfs0):
	def __init__(self, path = None, mode = None, cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		super(Hfs0, self).__init__(path, mode, cryptoType, cryptoKey, cryptoCounter)
		

	def open(self, path = None, mode = 'rb', cryptoType = -1, cryptoKey = -1, cryptoCounter = -1):
		r = super(BaseFs, self).open(path, mode, cryptoType, cryptoKey, cryptoCounter)
		self.rewind()

		self.magic = self.read(0x4);
		if self.magic != b'HFS0':
			raise IOError('Not a valid HFS0 partition ' + str(self.magic))
			

		fileCount = self.readInt32()
		stringTableSize = self.readInt32()
		self.readInt32() # junk data

		self.seek(0x10 + fileCount * 0x40)
		stringTable = self.read(stringTableSize)
		stringEndOffset = stringTableSize
		
		headerSize = 0x10 + 0x40 * fileCount + stringTableSize
		self.files = []

		for i in range(fileCount):
			i = fileCount - i - 1
			self.seek(0x10 + i * 0x40)

			offset = self.readInt64()
			size = self.readInt64()
			nameOffset = self.readInt32() # just the offset
			name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
			stringEndOffset = nameOffset

			self.readInt32() # junk data

			#if name in ['update', 'secure', 'normal']:
			if name == 'secure':
				f = Hfs0(None)
				#f = factory(name)
			else:
				f = Fs.factory(name)

			f._path = name
			f.offset = offset
			f.size = size
			self.files.append(self.partition(offset + headerSize, f.size, f))

		self.files.reverse()
		
	def pack(self,files,buffer):
		if not self.path:
			return False
		indent = 1
		tabs = '\t' * indent			
		
		hd,multiplier = self.generateHeader(files)
		
		totSize = len(hd) + sum(os.path.getsize(file) for file in files)
		if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
			Print.info('\t\tRepack %s is already complete!' % self.path)
			return
			
		Print.info('Generating hfs0:')	
		Print.info(tabs+'- Calculated multiplier: '+str(multiplier))			
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing header...')
		outf = open(self.path, 'wb')
		outf.write(hd)
		t.update(len(hd))
		
		done = 0
		for file in files:
			t.write(tabs+'- Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(int(buffer))
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))
		t.close()
		outf.close()

	def generateHeader(self, files):
		#print (files)
		
		hreg=0x200
		hashregion=hreg.to_bytes(0x04, byteorder='little')
		filesNb = len(files)
		stringTable = '\x00'.join(os.path.basename(file) for file in files)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*multiplier - headerSize
		headerSize += remainder
		
		fileSizes = [os.path.getsize(file) for file in files]
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		shalist=list()
		for file in files:
			fp = open(file, 'rb')
			hblock = fp.read(0x200)
			sha=sha256(hblock).hexdigest()		
			shalist.append(sha)	
			fp.close()		
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in files] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		header =  b''
		header += b'HFS0'
		header += pk('<I', filesNb)
		header += pk('<I', len(stringTable)+remainder)
		header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			header += pk('<Q', fileOffsets[n])
			header += pk('<Q', fileSizes[n])
			header += pk('<I', stringTableOffsets[n])
			header += hashregion
			header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			header += bytes.fromhex(shalist[n])		
		header += stringTable.encode()
		header += remainder * b'\x00'	
		return header,multiplier	
		
	def empty_hfs0(self):
		return null
		

	def pack_root(self,upd_list,norm_list,sec_list,buffer):
		if not self.path:
			return False
		indent = 1
		tabs = '\t' * indent			
		root_header,upd_header,norm_header,sec_header,totSize,upd_multiplier,norm_multiplier,sec_multiplier=self.genRHeader(upd_list,norm_list,sec_list)
		if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
			Print.info('\t\tRepack %s is already complete!' % self.path)
			return
			
		Print.info('Generating ROOT hfs0:')			
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
		t.write(tabs+'- Writing ROOT header...')
		outf = open(self.path, 'wb')
		outf.write(root_header)
		t.update(len(root_header))
		t.write(tabs+'- Writing UPDATE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(upd_multiplier))	
		outf.write(upd_header)
		t.update(len(upd_header))
		for file in upd_list:
			t.write(tabs+'- Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(int(buffer))
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))
		t.write(tabs+'- Writing NORMAL partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(norm_multiplier))			
		outf.write(norm_header)
		t.update(len(norm_header))
		for file in norm_list:
			t.write(tabs+'- Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(int(buffer))
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))					
		t.write(tabs+'- Writing SECURE partition header...')
		t.write(tabs+'  Calculated multiplier: '+str(sec_multiplier))		
		outf.write(sec_header)
		t.update(len(sec_header))
		for file in sec_list:
			t.write(tabs+'  > Appending %s' % os.path.basename(file))
			with open(file, 'rb') as inf:
				while True:
					buf = inf.read(int(buffer))
					if not buf:
						break
					outf.write(buf)
					t.update(len(buf))						
		t.close()
		outf.close()		
		
	def genRHeader(self, upd_list,norm_list,sec_list):
		hreg=0x200
		hashregion=hreg.to_bytes(0x04, byteorder='little')	
		#UPD HEADER
		filesNb = len(upd_list)
		stringTable = '\x00'.join(os.path.basename(file) for file in upd_list)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		upd_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*upd_multiplier - headerSize
		headerSize += remainder
		
		fileSizes = [os.path.getsize(file) for file in upd_list]
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		shalist=list()
		for file in upd_list:
			fp = open(file, 'rb')
			hblock = fp.read(0x200)
			sha=sha256(hblock).hexdigest()		
			shalist.append(sha)	
			fp.close()		
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in upd_list] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		upd_header =  b''
		upd_header += b'HFS0'
		upd_header += pk('<I', filesNb)
		upd_header += pk('<I', len(stringTable)+remainder)
		upd_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			upd_header += pk('<Q', fileOffsets[n])
			upd_header += pk('<Q', fileSizes[n])
			upd_header += pk('<I', stringTableOffsets[n])
			upd_header += hashregion
			upd_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			upd_header += bytes.fromhex(shalist[n])		
		upd_header += stringTable.encode()
		upd_header += remainder * b'\x00'
		
		updSize = len(upd_header) + sum(os.path.getsize(file) for file in upd_list)	
		
		#print (hx(upd_header))
		#NORMAL HEADER
		filesNb = len(norm_list)
		stringTable = '\x00'.join(os.path.basename(file) for file in norm_list)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		norm_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*norm_multiplier - headerSize
		headerSize += remainder
		
		fileSizes = [os.path.getsize(file) for file in norm_list]
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		shalist=list()
		for file in norm_list:
			fp = open(file, 'rb')
			hblock = fp.read(0x200)
			sha=sha256(hblock).hexdigest()		
			shalist.append(sha)	
			fp.close()		
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in norm_list] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		norm_header =  b''
		norm_header += b'HFS0'
		norm_header += pk('<I', filesNb)
		norm_header += pk('<I', len(stringTable)+remainder)
		norm_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			norm_header += pk('<Q', fileOffsets[n])
			norm_header += pk('<Q', fileSizes[n])
			norm_header += pk('<I', stringTableOffsets[n])
			norm_header += hashregion
			norm_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			norm_header += bytes.fromhex(shalist[n])		
		norm_header += stringTable.encode()
		norm_header += remainder * b'\x00'
		normSize = len(norm_header) + sum(os.path.getsize(file) for file in norm_list)			
		
		#print (hx(norm_header))		
		
		#SECURE HEADER
		filesNb = len(sec_list)
		stringTable = '\x00'.join(os.path.basename(file) for file in sec_list)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		sec_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*sec_multiplier - headerSize
		headerSize += remainder
		
		fileSizes = [os.path.getsize(file) for file in sec_list]
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		shalist=list()
		for file in sec_list:
			fp = open(file, 'rb')
			hblock = fp.read(0x200)
			sha=sha256(hblock).hexdigest()		
			shalist.append(sha)	
			fp.close()		
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in sec_list] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		sec_header =  b''
		sec_header += b'HFS0'
		sec_header += pk('<I', filesNb)
		sec_header += pk('<I', len(stringTable)+remainder)
		sec_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			sec_header += pk('<Q', fileOffsets[n])
			sec_header += pk('<Q', fileSizes[n])
			sec_header += pk('<I', stringTableOffsets[n])
			sec_header += hashregion
			sec_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			sec_header += bytes.fromhex(shalist[n])		
		sec_header += stringTable.encode()
		sec_header += remainder * b'\x00'
		secSize = len(sec_header) + sum(os.path.getsize(file) for file in sec_list)	
		
		#print (hx(sec_header))		
		
		#ROOT HEADER
		root_hreg=list()
		hr=0x200*upd_multiplier
		root_hreg.append(hr.to_bytes(4, byteorder='little'))
		hr=0x200*norm_multiplier		
		root_hreg.append(hr.to_bytes(4, byteorder='little'))
		hr=0x200*sec_multiplier		
		root_hreg.append(hr.to_bytes(4, byteorder='little'))
		root_list=list()
		root_list.append("update")	
		root_list.append("normal")	
		root_list.append("secure")	
		fileSizes=list()		
		fileSizes.append(updSize)	
		fileSizes.append(normSize)	
		fileSizes.append(secSize)	
		#print(fileSizes)			
		filesNb = len(root_list)
		#print(filesNb)
		stringTable = '\x00'.join(os.path.basename(file) for file in root_list)
		#print(stringTable)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		root_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*root_multiplier - headerSize
		headerSize += remainder
		#print(headerSize)
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]	
		shalist=list()
		sha=sha256(upd_header).hexdigest()	
		shalist.append(sha)	
		sha=sha256(norm_header).hexdigest()	
		shalist.append(sha)		
		sha=sha256(sec_header).hexdigest()	
		shalist.append(sha)				
		
		fileNamesLengths = [len(os.path.basename(file))+1 for file in root_list] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		root_header =  b''
		root_header += b'HFS0'
		root_header += pk('<I', filesNb)
		root_header += pk('<I', len(stringTable)+remainder)
		root_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			root_header += pk('<Q', fileOffsets[n])
			root_header += pk('<Q', fileSizes[n])
			root_header += pk('<I', stringTableOffsets[n])
			root_header += root_hreg[n]
			root_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			root_header += bytes.fromhex(shalist[n])		
		root_header += stringTable.encode()
		root_header += remainder * b'\x00'
		#print (hx(root_header))	
		rootSize = len(root_header) + sum(fileSizes)			
		return root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier

	def readhfs0(self):		
		self.seek(0x4)
		nfiles=self.readInt32()
		stringTableSize = self.readInt32()
		self.readInt32() # junk data
		Print.info("Magic: "+str(self.magic))
		Print.info("Number of files: "+str(nfiles))
		Print.info("Legth of string table: "+str(hx(stringTableSize.to_bytes(4, byteorder='big'))))		
		for i in range(nfiles):
			Print.info('........................')							
			Print.info('Content number ' + str(i+1))
			Print.info('........................')
			file_offset=self.readInt64()	
			file_size=self.readInt64()	
			file_offset_stable=self.readInt32()	
			hashregion=self.readInt32()	
			hashregion=self.read(0x4)				
			self.read(0x8)
			sha=self.read(0x20)
			Print.info('File offset: ' + str(hx(file_offset.to_bytes(8, byteorder='big'))))
			Print.info('Size of file: ' + str(file_size))
			Print.info('Offset in stringtable: ' + str(hx(file_offset_stable.to_bytes(4, byteorder='big'))))
			Print.info('Hash Region: ' + str(hx(hashregion.to_bytes(4, byteorder='big'))))	
			Print.info('Sha 256: ' + str(hx(sha)))			
			#h=0x200
			#hreg=h.to_bytes(0x04, byteorder='little')
			#print (str(hreg))
			#print (str(hashregion))
		
	def printInfo(self, indent = 0):
		maxDepth = 3
		tabs = '\t' * indent
		Print.info('\n%sHFS0\n' % (tabs))
		super(Pfs0, self).printInfo(indent)

		
		
	def gen_rhfs0_head(self, upd_list,norm_list,sec_list,sec_fileSizes,sec_shalist):
				
		hreg=0x200
		hashregion=hreg.to_bytes(0x04, byteorder='little')	
		#UPD HEADER
		filesNb = len(upd_list)
		stringTable = '\x00'.join(str(nca) for nca in upd_list)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		upd_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*upd_multiplier - headerSize
		headerSize += remainder
		fileSizes=list()
		fileOffsets=list()
		shalist=list()
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in upd_list] # +1 for the \x00 
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		upd_header =  b''
		upd_header += b'HFS0'
		upd_header += pk('<I', filesNb)
		upd_header += pk('<I', len(stringTable)+remainder)
		upd_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			upd_header += pk('<Q', fileOffsets[n])
			upd_header += pk('<Q', fileSizes[n])
			upd_header += pk('<I', stringTableOffsets[n])
			upd_header += hashregion
			upd_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			upd_header += bytes.fromhex(shalist[n])		
		upd_header += stringTable.encode()
		upd_header += remainder * b'\x00'
	
		updSize = len(upd_header) + sum(fileSizes)	
	
		
		#print (hx(upd_header))
		#NORMAL HEADER
		filesNb = len(norm_list)
		stringTable = '\x00'.join(str(nca) for nca in norm_list)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		norm_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*norm_multiplier - headerSize
		headerSize += remainder
		fileSizes=list()
		fileOffsets=list()
		shalist=list()
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in norm_list] # +1 for the \x00 
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		norm_header =  b''
		norm_header += b'HFS0'
		norm_header += pk('<I', filesNb)
		norm_header += pk('<I', len(stringTable)+remainder)
		norm_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			norm_header += pk('<Q', fileOffsets[n])
			norm_header += pk('<Q', fileSizes[n])
			norm_header += pk('<I', stringTableOffsets[n])
			norm_header += hashregion
			norm_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			norm_header += bytes.fromhex(shalist[n])		
		norm_header += stringTable.encode()
		norm_header += remainder * b'\x00'
	
		normSize = len(norm_header) + sum(fileSizes)		
		#print (hx(norm_header))		
		
		#SECURE HEADER
		filesNb = len(sec_list)
		stringTable = '\x00'.join(str(nca) for nca in sec_list)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		sec_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*sec_multiplier - headerSize
		headerSize += remainder
		
		fileSizes = sec_fileSizes
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
		
		shalist=sec_shalist
			
		fileNamesLengths = [len(os.path.basename(file))+1 for file in sec_list]  # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		sec_header =  b''
		sec_header += b'HFS0'
		sec_header += pk('<I', filesNb)
		sec_header += pk('<I', len(stringTable)+remainder)
		sec_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			sec_header += pk('<Q', fileOffsets[n])
			sec_header += pk('<Q', fileSizes[n])
			sec_header += pk('<I', stringTableOffsets[n])
			sec_header += hashregion
			sec_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			sec_header += bytes.fromhex(shalist[n])		
		sec_header += stringTable.encode()
		sec_header += remainder * b'\x00'
		secSize = len(sec_header) + sum(fileSizes)		
		
		#print (hx(sec_header))		
		
		#ROOT HEADER
		root_hreg=list()
		hr=0x200*upd_multiplier
		root_hreg.append(hr.to_bytes(4, byteorder='little'))
		hr=0x200*norm_multiplier		
		root_hreg.append(hr.to_bytes(4, byteorder='little'))
		hr=0x200*sec_multiplier		
		root_hreg.append(hr.to_bytes(4, byteorder='little'))
		root_list=list()
		root_list.append("update")	
		root_list.append("normal")	
		root_list.append("secure")	
		fileSizes=list()		
		fileSizes.append(updSize)	
		fileSizes.append(normSize)	
		fileSizes.append(secSize)	
		#print(fileSizes)			
		filesNb = len(root_list)
		#print(filesNb)
		stringTable = '\x00'.join(os.path.basename(file) for file in root_list)
		#print(stringTable)
		headerSize = 0x10 + (filesNb)*0x40 + len(stringTable)
		root_multiplier=math.ceil(headerSize/0x200)
		remainder = 0x200*root_multiplier - headerSize
		headerSize += remainder
		#print(headerSize)
		fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]	
		shalist=list()
		sha=sha256(upd_header).hexdigest()	
		shalist.append(sha)	
		sha=sha256(norm_header).hexdigest()	
		shalist.append(sha)		
		sha=sha256(sec_header).hexdigest()	
		shalist.append(sha)				
		
		fileNamesLengths = [len(os.path.basename(file))+1 for file in root_list] # +1 for the \x00
		stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
		
		root_header =  b''
		root_header += b'HFS0'
		root_header += pk('<I', filesNb)
		root_header += pk('<I', len(stringTable)+remainder)
		root_header += b'\x00\x00\x00\x00'
		for n in range(filesNb):
			root_header += pk('<Q', fileOffsets[n])
			root_header += pk('<Q', fileSizes[n])
			root_header += pk('<I', stringTableOffsets[n])
			root_header += root_hreg[n]
			root_header += b'\x00\x00\x00\x00\x00\x00\x00\x00'			
			root_header += bytes.fromhex(shalist[n])		
		root_header += stringTable.encode()
		root_header += remainder * b'\x00'
		#print (hx(root_header))	
		rootSize = len(root_header) + sum(fileSizes)			
		return root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier

				
					
	def c_nsp_direct(self,ofolder,buffer,metapatch,keypatch,RSV_cap):
		contentlist=list()
		for nca in self:
			if type(nca) == Nca:
				contentlist.append(nca._path)			
		hd = self.gen_nsp_head(contentlist)
		
		totSize = len(hd) 
		for nca in self:
			if type(nca) == Nca:
				totSize=totSize+nca.header.size

		indent = 1
		tabs = '\t' * indent
		
		t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)

		filename=os.path.basename(self._path)
		outfolder = str(ofolder)+'/'	
		filepath = os.path.join(outfolder, filename)	
		if not os.path.exists(outfolder):
			os.makedirs(outfolder)
		t.write('Creating: ' + filename)		
		t.write(tabs+'Writing header...')			
		fp = open(filepath, 'w+b')		
		fp.write(hd)	
		#pos=fp.tell()
		#print (pos)
		fp.close()			
		t.update(len(hd))
		for nca in self:
			if type(nca) == Nca:
				nca.rewind()
				fp = open(filepath, 'r+b')
				#fp.seek(pos)
				t.write(tabs+'Appending: ' + str(nca._path))
				for data in iter(lambda: nca.read(int(buffer)), ""):
					fp.write(data)
					t.update(len(data))
					fp.flush()
					if not data:
						#pos=fp.tell()
						#print (pos)
						fp.close()	
						t.close()	
						break
		t.close()										
						
		
		
