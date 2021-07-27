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
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
from Fs.pyNCA3 import NCA3
from Fs.pyNPDM import NPDM
from Fs.BaseFs import BaseFs
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
from Utils import bytes2human

class SectionTableEntry:
	def __init__(self, d):
		self.mediaOffset = int.from_bytes(d[0x0:0x4], byteorder='little', signed=False)
		self.mediaEndOffset = int.from_bytes(d[0x4:0x8], byteorder='little', signed=False)

		self.offset = self.mediaOffset * MEDIA_SIZE
		self.endOffset = self.mediaEndOffset * MEDIA_SIZE

		self.unknown1 = int.from_bytes(d[0x8:0xc], byteorder='little', signed=False)
		self.unknown2 = int.from_bytes(d[0xc:0x10], byteorder='little', signed=False)
		self.sha1 = None


def GetSectionFilesystem(buffer, cryptoKey):
	fsType = buffer[0x3]
	if fsType == Fs.Type.Fs.PFS0:
		return Fs.Pfs0(buffer, cryptoKey = cryptoKey)

	if fsType == Fs.Type.Fs.ROMFS:
		return Fs.Rom(buffer, cryptoKey = cryptoKey)

	return BaseFs(buffer, cryptoKey = cryptoKey)

#from Cryptodome.Signature import pss
#from Cryptodome.PublicKey import RSA
#from Cryptodome import Random
#from Cryptodome.Hash import SHA256 as newsha

MEDIA_SIZE = 0x200
indent = 1
tabs = '\t' * indent

def get_file_and_offset(filelist,targetoffset):
	startoffset=0;endoffset=0
	# print(targetoffset)
	# print(filelist)
	for i in range(len(filelist)):
		entry=filelist[i]
		filepath=entry[0];size=entry[1]
		startoffset=endoffset
		endoffset+=size
		# print(endoffset)
		if targetoffset>endoffset:
			pass
		else:
			partialoffset=targetoffset-startoffset
			return filepath,partialoffset
	return False,False


def chain_streams(streams, buffer_size=io.DEFAULT_BUFFER_SIZE):
	"""
	Chain an iterable of streams together into a single buffered stream.
	Usage:
		def generate_open_file_streams():
			for file in filenames:
				yield open(file, 'rb')
		f = chain_streams(generate_open_file_streams())
		f.read()
	"""

	class ChainStream(io.RawIOBase):
		def __init__(self):
			self.leftover = b''
			self.stream_iter = iter(streams)
			try:
				self.stream = next(self.stream_iter)
			except StopIteration:
				self.stream = None

		def readable(self):
			return True

		def _read_next_chunk(self, max_length):
			# Return 0 or more bytes from the current stream, first returning all
			# leftover bytes. If the stream is closed returns b''
			if self.leftover:
				return self.leftover
			elif self.stream is not None:
				return self.stream.read(max_length)
			else:
				return b''

		def readinto(self, b):
			buffer_length = len(b)
			chunk = self._read_next_chunk(buffer_length)
			while len(chunk) == 0:
				# move to next stream
				if self.stream is not None:
					self.stream.close()
				try:
					self.stream = next(self.stream_iter)
					chunk = self._read_next_chunk(buffer_length)
				except StopIteration:
					# No more streams to chain together
					self.stream = None
					return 0  # indicate EOF
			output, self.leftover = chunk[:buffer_length], chunk[buffer_length:]
			b[:len(output)] = output
			return len(output)

	return io.BufferedReader(ChainStream(), buffer_size=buffer_size)

def generate_open_file_streams(filenames):
	for file in filenames:
		yield open(file, 'rb')


def read_start(filepath):
	filelist=retchunks(filepath)
	filenames=[];
	for item in filelist:
		filenames.append(item[0])
	f = chain_streams(generate_open_file_streams(filenames))
	if filepath.endswith('.xc0'):
		files_list=sq_tools.ret_xci_offsets(filepath)
	elif filepath.endswith('.ns0'):
		files_list=sq_tools.ret_nsp_offsets(filepath)
	print(files_list)

	# feed=f.read(0x500)
	# Hex.dump(feed)
	f.flush()
	f.close()

def file_location(filepath,t='all',Printdata=False):
	filenames=retchunks(filepath)
	# print(filenames)
	locations=list()
	if filepath.endswith('.xc0'):
		files_list=sq_tools.ret_xci_offsets(filepath)
	elif filepath.endswith('.ns0'):
		files_list=sq_tools.ret_nsp_offsets(filepath)
	for file in files_list:
		if not t.lower()=='all':
			# print(file)
			if (str(file[0]).lower()).endswith(t.lower()):
				location1,tgoffset1=get_file_and_offset(filenames,file[1])
				location2,tgoffset2=get_file_and_offset(filenames,file[2])
				locations.append([file[0],file[3],location1,tgoffset1,location2,tgoffset2])
				if Printdata==True:
					print('{}'.format(file[0]))
					print('- Starts in file {} at offset {}'.format(location1[-4:],tgoffset1))
					print('- Ends in file {} at offset {}'.format(location2[-4:],tgoffset2))
					print('')
			else:pass
		else:
			location1,tgoffset1=get_file_and_offset(filenames,file[1])
			location2,tgoffset2=get_file_and_offset(filenames,file[2])
			locations.append([file[0],file[3],location1,tgoffset1,location2,tgoffset2])
			if Printdata==True:
				print('{}'.format(file[0]))
				print('- Starts in file {} at offset {}'.format(location1[-4:],tgoffset1))
				print('- Ends in file {} at offset {}'.format(location2[-4:],tgoffset2))
				print('')
	return locations

def retchunks(filepath):
	file_list=list()
	try:
		bname=os.path.basename(os.path.abspath(filepath))
		bn=''
		if bname != '00':
			bn=bname[:-4]
		if filepath.endswith(".xc0"):
			outname = bn+".xci"
			ender=".xc"
		elif filepath.endswith(".ns0"):
			outname = bn+".nsp"
			ender=".ns"
		elif filepath[-2:]=="00":
			outname = "output.nsp"
			ender="0"
		else:
			print ("Not valid file")
		ruta=os.path.dirname(os.path.abspath(filepath))
		# print(ruta)
		for dirpath, dnames, fnames in os.walk(ruta):
			for f in fnames:
				check=f[-4:-1]
				# print(check)
				# print(ender)
				# print(bname[:-1])
				# print(f[:-1])
				if check==ender and bname[:-1]==f[:-1]:
					n=bname[-1];n=int(n)
					# print(bname)
					try:
						n=f[-1];n=int(n)
						n+=1
						fp = os.path.join(ruta, f)
						size=os.path.getsize(fp)
						file_list.append([fp,size])
					except BaseException as e:
						# Print.error('Exception: ' + str(e))
						continue
		file_list.sort()
		# print(file_list)
		return file_list
	except BaseException as e:
		Print.error('Exception: ' + str(e))

##################
#DB DATA
##################

def return_DBdict(filepath):
	cnmtfiles=file_location(filepath,'.cnmt.nca',Printdata=False)
	content_number=len(cnmtfiles)
	memoryload(cnmtfiles,target=False,ender='.cnmt.nca')
	if content_number>1:
		file,mcstring,mGame=self.choosecnmt(cnmtnames)
		DBdict=self.getDBdict(file,content_number=content_number,mcstring=mcstring,mGame=mGame)
	else:
		DBdict=self.getDBdict(cnmtnames[0],content_number=content_number)
	print(DBdict)
	return DBdict

def memoryload(filelist,target=False,ender=False):
	for i in range(len(filelist)):
		entry=filelist[i]
		file=entry[0];size=entry[1]
		initpath=entry[2];off1=entry[3]
		endpath=entry[4];off2=entry[5]
		if file.lower()==str(target).lower():
			if initpath==endpath:
				with open(initpath, 'rb') as f:
					f.seek(off1)
					inmemoryfile = io.BytesIO(f.read(size))
					inmemoryfile.seek(0)
					nca = Fs.Nca()
					nca.open(inmemoryfile)
					nca.read_cnmt()
		elif target==False and ender!=False:
			if str(file.lower()).endswith(ender):
				if initpath==endpath:
					with open(initpath, 'rb') as f:
						f.seek(off1)
						inmemoryfile = io.BytesIO(f.read(size))
						inmemoryfile.seek(0)
						ncaHeader = NcaHeader()
						f.seek(off1)
						ncaHeader.open(MemoryFile(f.read(size), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
						# ncaHeader.seek(0x400)
					try:
						nca3=NCA3(inmemoryfile,0,file,ncaHeader.titleKeyDec)
						for _, sec in enumerate(nca3.sections):
							if sec.fs_type == 'RomFS':
								continue
							for buf in sec.decrypt_raw():
								DAT=buf
								Hex.dump(buf)
								# print(d)
								# if file.endswith('.cnmt'):
									# DAT=sec.fs.open(file)
									# for test in DAT:
										# Hex.dump(test)
									# print(DAT)
					except Exception as e:
						print('%s: %s' % (e.__class__.__name__, e))
						# for i in range(4):
							# fs = GetSectionFilesystem(ncaHeader.read(0x200), cryptoKey = ncaHeader.titleKeyDec)
							# Print.info('fs type = ' + hex(fs.fsType))
							# Print.info('fs crypto = ' + hex(fs.cryptoType))
							# Print.info('st end offset = ' + str(ncaHeader.sectionTables[i].endOffset - ncaHeader.sectionTables[i].offset))
							# Print.info('fs offset = ' + hex(ncaHeader.sectionTables[i].offset))
							# Print.info('fs section start = ' + hex(fs.sectionStart))
							# Print.info('titleKey = ' + str(hx(ncaHeader.titleKeyDec)))
							# break
						# pfs0=fs
						# sectionHeaderBlock = fs.buffer
						# ncaHeader.seek(fs.offset)
						# pfs0Offset=fs.offset
						# pfs0Header = f.read(0x100)
						# Hex.dump(pfs0Header)
						# mem = MemoryFile(pfs0Header, Type.Crypto.CTR, ncaHeader.titleKeyDec, pfs0.cryptoCounter, offset = pfs0Offset)
						# data=mem.read();
						# data=ncaHeader.read()
						# Hex.dump(data)
						# nca = Fs.Nca()
						# f.seek(off1)
						# nca.open(MemoryFile(f.read(size), Type.Crypto.None, uhx(Keys.get('header_key'))))
						# nca.read_cnmt()
					break

def open_cnmt(nca):
	# Find the cnmt inside an NCA, and return a file handle
	for _, sec in enumerate(nca.sections):
		if sec.fs_type == 'RomFS':
			continue
		for file in sec.fs.files:
			if file.endswith('.cnmt'):
				return sec.fs.open(file)
	raise FileNotFoundError('No CNMT was not found')

def print_cnmt(cnmt):
	print('%016x v%d:' % (cnmt.tid, cnmt.ver))
	if cnmt.title_type == 'SystemUpdate':
		print('  Titles:')
		for tid, d in cnmt.data.items():
			print('	%016x:' % tid)
			print('	  Type:	%s' % d['Type'])
			print('	  Version: %d' % d['Version'])
	else:
		print('  Total title size: %s' % bytes2human(cnmt.title_size))
		print('  Files:')
		for _, ncas in cnmt.data.items():
			if ncas:
				for nca_id, d in ncas.items():
					print('	%032x.nca:' % nca_id)
					print('	  Size:   %s' % bytes2human(d['Size']))
					print('	  SHA256: %s' % hx(d['Hash']).decode())

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
