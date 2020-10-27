import zstandard
import sq_tools
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Drive import DriveTools
from Drive import Public
from Drive import Private
import Print
from tqdm import tqdm
import Hex
import io
from binascii import hexlify as hx, unhexlify as uhx
from Fs.Nca import NcaHeader
from Fs.Nca import Nca
from Fs.File import MemoryFile

import Keys
from Fs import Type
import os
import time

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

def decompress(path,ofolder,TD=None,filter=None,file=None):
	buf=64*1024;buffer=buf
	if path.startswith('http'):
		url=path
		if file==None:
			remote=Public.location(url);readable=remote.readable
		else:
			remote=file;readable=remote.readable
		if not readable:
			return False
		type='file'
	else:
		if path=='pick':
			account=Private.token_picker()
			TD=Private.TD_picker(account)
			return
		test=path.split(".+")
		if TD=='pick':
			TD=Private.TD_picker(path)
		if len(test)>1 or path.endswith('/') or path.endswith('\\'):
			type="folder"
		else:
			ID,name,type,size,md5,remote=Private.get_Data(path,TD=TD,Print=False)
	if type!='file':
		# print('Path is a folder')
		Private.folderpicker(path,TD=TD,filter=filter,mode='decompress')
		return
	else:
		if remote.name.endswith(".xcz"):
			decompress_xcz(remote,ofolder)
		elif remote.name.endswith(".nsz"):
			decompress_nsz(remote,ofolder)

def decompress_nsz(remote,ofolder):
	buf=64*1024;buffer=buf
	endname=remote.name[:-1]+'p'
	output=os.path.join(ofolder, endname)
	files_list=DriveTools.get_files_from_head(remote,remote.name)
	remote.rewind()
	print('Decompressing {}'.format(remote.name))
	print('- Parsing headers...')
	files=list();filesizes=list()
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0];metadict={}
		if cnmtfile.endswith('.cnmt.nca'):
			metadict,d1,d2=DriveTools.get_cnmt_data(target=cnmtfile,file=remote)
			ncadata=metadict['ncadata']
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
	# Hex.dump(nspheader)
	# print(totsize)
	print(files)
	t = tqdm(total=totsize, unit='B', unit_scale=True, leave=False)
	with open(output, 'wb') as o:
		o.write(nspheader)
		t.update(len(nspheader))
	for file in files:
		if file.endswith('cnmt.nca'):
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(file).lower():
					nca_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					nca_size=files_list[i][3]
					break
			t.write('- Appending {}'.format(nca_name))
			data=remote.read_at(off1,nca_size)
			with open(output, 'ab') as o:
				o.write(data)
				t.update(len(data))
		elif file.endswith('.nca'):
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(file).lower():
					nca_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					nca_size=files_list[i][3]
					t.write('- Appending {}'.format(nca_name))
					o = open(output, 'ab+')
					remote.seek(off1,off2)
					for data in remote.response.iter_content(chunk_size=buf):
						o.write(data)
						t.update(len(data))
						o.flush()
						if not data:
							o.close()
							break
				elif (str(files_list[i][0]).lower())[:-1] == (str(file).lower())[:-1] and str(files_list[i][0]).endswith('ncz'):
					ncz_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					sz=files_list[i][3]
					t.write('- Calculating compressed sections for: '+ncz_name)
					remote.seek(off1,off2)
					header=remote.read(0x4000)
					magic = readInt64(remote)
					sectionCount =  readInt64(remote)
					sections = []
					for i in range(sectionCount):
						sections.append(Section(remote))
					t.write('  Detected {} sections'.format(str(sectionCount)))
					with open(output, 'rb+') as o:
						o.seek(0, os.SEEK_END)
						curr_off= o.tell()
						t.write('- Appending decompressed {}'.format(ncz_name))
						t.write('  Writing nca header')
						o.write(header)
						t.update(len(header))
						timestamp = time.time()
						t.write('  Writing decompressed body in plaintext')
						count=0;checkstarter=0
						dctx = zstandard.ZstdDecompressor()
						hd=Private.get_html_header(remote.access_token,remote.position,off2)
						remote.get_session(hd)
						reader = dctx.stream_reader(remote.response.raw, read_size=buffer)
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
							c+=1
						elapsed = time.time() - timestamp
						minutes = elapsed / 60
						seconds = elapsed % 60

						speed = 0 if elapsed == 0 else (spsize / elapsed)
						t.write('\n    Decompressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))
		else:
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(file).lower():
					file_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					file_size=files_list[i][3]
					break
			t.write('- Appending {}'.format(file_name))
			data=remote.read_at(off1,file_size)
			with open(output, 'ab') as o:
				o.write(data)
				t.update(len(data))
	t.close()

def decompress_xcz(remote,ofolder):
	buf=64*1024;buffer=buf
	endname=remote.name[:-1]+'i'
	output=os.path.join(ofolder, endname)
	files_list=DriveTools.get_files_from_head(remote,remote.name)
	remote.rewind()
	# print(files_list)
	print('Decompressing {}'.format(remote.name))
	print('- Parsing headers...')
	files=list();filesizes=list()
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0];metadict={}
		if cnmtfile.endswith('.cnmt.nca'):
			metadict,d1,d2=DriveTools.get_cnmt_data(target=cnmtfile,file=remote)
			ncadata=metadict['ncadata']
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
	sec_hashlist=list()
	try:
		for target in files:
			sha,size,gamecard=DriveTools.file_hash(remote,target,files_list)
			# print(sha)
			if sha != False:
				sec_hashlist.append(sha)
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	# print(sec_hashlist)
	xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=sq_tools.get_xciheader(files,filesizes,sec_hashlist)
	outheader=xci_header
	outheader+=game_info
	outheader+=sig_padding
	outheader+=xci_certificate
	outheader+=root_header
	outheader+=upd_header
	outheader+=norm_header
	outheader+=sec_header
	properheadsize=len(outheader)
	totsize=properheadsize
	for s in filesizes:
		totsize+=s
	# Hex.dump(outheader)
	# print(totsize)
	print(files)
	t = tqdm(total=totsize, unit='B', unit_scale=True, leave=False)
	with open(output, 'wb') as o:
		o.write(outheader)
		t.update(len(outheader))
	for file in files:
		if file.endswith('cnmt.nca'):
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(file).lower():
					nca_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					nca_size=files_list[i][3]
					break
			t.write('- Appending {}'.format(nca_name))
			data=remote.read_at(off1,nca_size)
			with open(output, 'ab') as o:
				o.write(data)
				t.update(len(data))
		elif file.endswith('.nca'):
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(file).lower():
					nca_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					nca_size=files_list[i][3]
					t.write('- Appending {}'.format(nca_name))
					o = open(output, 'ab+')
					remote.seek(off1,off2)
					for data in remote.response.iter_content(chunk_size=buf):
						o.write(data)
						t.update(len(data))
						o.flush()
						if not data:
							o.close()
							break
				elif (str(files_list[i][0]).lower())[:-1] == (str(file).lower())[:-1] and str(files_list[i][0]).endswith('ncz'):
					ncz_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					sz=files_list[i][3]
					t.write('- Calculating compressed sections for: '+ncz_name)
					remote.seek(off1,off2)
					header=remote.read(0x4000)
					magic = readInt64(remote)
					sectionCount =  readInt64(remote)
					sections = []
					for i in range(sectionCount):
						sections.append(Section(remote))
					t.write('  Detected {} sections'.format(str(sectionCount)))
					with open(output, 'rb+') as o:
						o.seek(0, os.SEEK_END)
						curr_off= o.tell()
						t.write('- Appending decompressed {}'.format(ncz_name))
						t.write('  Writing nca header')
						o.write(header)
						t.update(len(header))
						timestamp = time.time()
						t.write('  Writing decompressed body in plaintext')
						count=0;checkstarter=0
						dctx = zstandard.ZstdDecompressor()
						hd=Private.get_html_header(remote.access_token,remote.position,off2)
						remote.get_session(hd)
						reader = dctx.stream_reader(remote.response.raw, read_size=buffer)
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
							c+=1
						elapsed = time.time() - timestamp
						minutes = elapsed / 60
						seconds = elapsed % 60

						speed = 0 if elapsed == 0 else (spsize / elapsed)
						t.write('\n    Decompressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))
		else:
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(file).lower():
					file_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					file_size=files_list[i][3]
					break
			t.write('- Appending {}'.format(file_name))
			data=remote.read_at(off1,file_size)
			with open(output, 'ab') as o:
				o.write(data)
				t.update(len(data))
	t.close()
