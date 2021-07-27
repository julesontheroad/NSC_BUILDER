import aes128
import Print
import os
import json
import nutFs
import nutFs.Pfs0
import nutFs.Type
import nutFs.Nca
from nutFs.Nca import Nca
import subprocess
from contextlib import closing
import zstandard
import listmanager
from tqdm import tqdm
import time
from nutFs.Xci import Xci
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
import sq_tools
import io
from Fs import Type as FsType

import Keys
from binascii import hexlify as hx, unhexlify as uhx
from DBmodule import Exchange as exchangefile
import copy

ncaHeaderSize = 0x4000

def sortedFs(nca):
	fs = []
	for i in nca.sections:
		fs.append(i)
	fs.sort(key=lambda x: x.offset)
	return fs

def get_sections(nca):
	sections0 = []
	for fs in sortedFs(nca):
		sections0 += fs.getEncryptionSections()
	check_padding=(((sortedFs(nca))[0]).offset)-ncaHeaderSize
	if check_padding>0:
		sections = []
		fs=copy.deepcopy(sections0[0])
		sections.append(fs)
		for fs in sections0:
			sections.append(fs)
		(sections[0]).offset=int(ncaHeaderSize)
		(sections[0]).size=(sections[1]).offset-int(ncaHeaderSize)
		(sections[0]).cryptoType=nutFs.Type.Crypto.NONE
		(sections[0]).cryptoKey=(sections[1]).cryptoKey
		(sections[0]).cryptoCounter=(sections[1]).cryptoCounter
	else:
		sections=sections0
	return sections

def isNcaPacked(nca):
	fs = get_sections(nca)

	if len(fs) == 0:
		return True

	next = ncaHeaderSize

	for i in range(len(fs)):
		if fs[i].offset != next:
			return False

		next = fs[i].offset + fs[i].size

	if next != nca.size:
		return False

	return True

def foldercompress(ifolder, ofolder = None, level = 17, threads = 0, t=['nsp']):
	mylist=listmanager.folder_to_list(ifolder,t)
	counter=len(mylist)
	for item in mylist:
		print(item)
		if ofolder is None:
			nszPath = item[0:-1] + 'z'
		else:
			nszPath = os.path.join(ofolder, os.path.basename(item[0:-1] + 'z'))
		compress(item,ofolder=None,level=level,threads=threads,ofile=nszPath)
		counter-=1
		print('\nStill %d files to compress\n'%(counter))

def check_sections(filepath):
	if filepath.endswith(".xci"):
		xcicontainer = Xci(filepath)
		files2=list();filesizes2=list()
		for nspF in xcicontainer.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if isinstance(nca, nutFs.Nca.Nca) and (nca.header.contentType == nutFs.Type.Content.PROGRAM or nca.header.contentType == nutFs.Type.Content.PUBLIC_DATA):
						sections=get_sections(nca)
						for fs in sections:
							print(hx(fs.offset.to_bytes(8, 'little')))
							print(hx(fs.size.to_bytes(8, 'little')))
							print(hx(fs.cryptoType.to_bytes(8, 'little')))
							print(hx(b'\x00' * 8))
							print(hx(fs.cryptoKey))
							print(hx(fs.cryptoCounter))
							print("")
	elif filepath.endswith(".nsp"):
		nspcontainer = Nsp(filepath,'rb')
		for nca in nspcontainer:
			if isinstance(nca, nutFs.Nca.Nca) and (nca.header.contentType == nutFs.Type.Content.PROGRAM or nca.header.contentType == nutFs.Type.Content.PUBLIC_DATA):
				sections = []
				sections=get_sections(nca)
				for fs in sections:
					print(hx(fs.offset.to_bytes(8, 'little')))
					print(hx(fs.size.to_bytes(8, 'little')))
					print(hx(fs.cryptoType.to_bytes(8, 'little')))
					print(hx(b'\x00' * 8))
					print(hx(fs.cryptoKey))
					print(hx(fs.cryptoCounter))
					print("")

def supertrim_xci(filepath,buffer=65536,outfile=None,keepupd=False, level = 17,  threads = 0, pos=False, nthreads=False):
	isthreaded=False
	if pos!=False:
		isthreaded=True
	elif str(pos)=='0':
		isthreaded=True
	else:
		pos=0
	pos=int(pos)
	if isthreaded==False:
		try:
			exchangefile.deletefile()
		except:pass
	f=squirrelXCI(filepath)
	t = tqdm(total=0, unit='B', unit_scale=True, leave=False,position=0)
	for nspF in f.hfs0:
		if str(nspF._path)=="secure":
			for ticket in nspF:
				if str(ticket._path).endswith('.tik'):
					if isthreaded==False:
						t.write('- Titlerights: '+ticket.rightsId)
					tk=(str(hex(ticket.getTitleKeyBlock()))[2:]).upper()
					if isthreaded==False:
						if len(tk)==30:
							tk='00'+str(tk).upper()
						if len(tk)==31:
							tk='0'+str(tk).upper()
						t.write('- Titlekey: '+tk)
					exchangefile.add(ticket.rightsId,tk)
	f.flush()
	f.close()
	t.close()
	files_list=sq_tools.ret_xci_offsets(filepath)
	files=list();filesizes=list()
	if isthreaded==True and nthreads!=False:
		tqlist=list()
		for i in range(nthreads):
			tq = tqdm(total=0, unit='B', unit_scale=True, leave=False,position=i)
			tqlist.append(tq)
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
			f=squirrelXCI(filepath)
			titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
			f.flush()
			f.close()
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
	f=squirrelXCI(filepath)
	try:
		for file in files:
			sha,size,gamecard=f.file_hash(file)
			# print(sha)
			if sha != False:
				sec_hashlist.append(sha)
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	f.flush()
	f.close()
	xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=sq_tools.get_xciheader(files,filesizes,sec_hashlist)
	compressionLevel=int(level)
	CHUNK_SZ = buffer
	if outfile==None:
		ofile = filepath[0:-1] + 'z'
	else:
		ofile=outfile
	ofile = os.path.abspath(ofile)
	outheader=xci_header
	outheader+=game_info
	outheader+=sig_padding
	outheader+=xci_certificate
	outheader+=root_header
	outheader+=upd_header
	outheader+=norm_header
	outheader+=sec_header
	properheadsize=len(outheader)

	compressionLevel=int(level)
	CHUNK_SZ = buffer
	if outfile==None:
		nszPath = filepath[0:-1] + 'z'
	else:
		nszPath=outfile
	nszPath = os.path.abspath(nszPath)

	tsize=properheadsize
	for sz in filesizes:
		tsize+=sz
	if isthreaded==True:
		from colorama import Fore
		colors=Fore.__dict__
		k=0;l=pos
		for col in colors:
			if l>len(colors):
				l=l-len(colors)
			color=colors[col]
			if k==(l+1):
				break
			else:
				k+=1
		t = tqdm(total=tsize, unit='B', unit_scale=True, leave=False,position=pos,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, Fore.RESET))
	else:
		t = tqdm(total=tsize, unit='B', unit_scale=True, leave=False,position=0)

	if isthreaded==False:
		t.write('Compressing with level %d and %d threads' % (compressionLevel, threads))
		t.write('\n  %s -> %s \n' % (filepath, nszPath))

	newNsp = nutFs.Pfs0.Pfs0Stream(nszPath,headsize=properheadsize,mode='wb+')

	xcicontainer = Xci(filepath)
	# f.compressed_supertrim(buffer,outfile,keepupd,level,threads)
	files2=list();filesizes2=list()
	for file in files:
		for nspF in xcicontainer.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if nca._path==file:
						if isinstance(nca, nutFs.Nca.Nca) and (nca.header.contentType == nutFs.Type.Content.PROGRAM or nca.header.contentType == nutFs.Type.Content.PUBLIC_DATA):
							if isNcaPacked(nca):
								skip=0
							else:
								skip=int(ncaHeaderSize-(((sortedFs(nca))[0]).offset))
							cctx = zstandard.ZstdCompressor(level=compressionLevel, threads = threads)

							newFileName = nca._path[0:-1] + 'z'

							f = newNsp.add(newFileName, nca.size,t,isthreaded)

							start = f.tell()

							nca.seek(0)
							data=nca.read(ncaHeaderSize)
							f.write(data)
							nca.seek(ncaHeaderSize)

							written = ncaHeaderSize

							compressor = cctx.stream_writer(f)

							sections = get_sections(nca)

							header = b'NCZSECTN'
							header += len(sections).to_bytes(8, 'little')

							i = 0
							for fs in sections:
								i += 1
								if skip>0:
									header += (fs.offset+skip).to_bytes(8, 'little')
									header += (fs.size-skip).to_bytes(8, 'little')
									header += fs.cryptoType.to_bytes(8, 'little')
									header += b'\x00' * 8
									header += fs.cryptoKey
									header += fs.cryptoCounter
								else:
									header += fs.offset.to_bytes(8, 'little')
									header += fs.size.to_bytes(8, 'little')
									header += fs.cryptoType.to_bytes(8, 'little')
									header += b'\x00' * 8
									header += fs.cryptoKey
									header += fs.cryptoCounter

							f.write(header)
							t.update(len(header))
							written += len(header)
							timestamp = time.time()
							decompressedBytes = ncaHeaderSize
							totsize=0
							for fs in sections:
								totsize+=fs.size

							c0=0
							for section in sections:
								#print('offset: %x\t\tsize: %x\t\ttype: %d\t\tiv%s' % (section.offset, section.size, section.cryptoType, str(hx(section.cryptoCounter))))
								o = nca.partition(offset = section.offset, size = section.size, n = None, cryptoType = section.cryptoType, cryptoKey = section.cryptoKey, cryptoCounter = bytearray(section.cryptoCounter), autoOpen = True)
								if c0==0 and skip>0:
									o.seek(skip)
								while not o.eof():
									buffer = o.read(CHUNK_SZ)
									t.update(len(buffer))
									if len(buffer) == 0:
										raise IOError('read failed')

									written += compressor.write(buffer)

									decompressedBytes += len(buffer)
								c0+=1
							compressor.flush(zstandard.FLUSH_FRAME)

							elapsed = time.time() - timestamp
							minutes = elapsed / 60
							seconds = elapsed % 60

							speed = 0 if elapsed == 0 else (nca.size / elapsed)

							written = f.tell() - start
							if isthreaded==False:
								t.write('\n  * Compressed at %d%% from %s to %s  - %s' % (int(written * 100 / nca.size), str(sq_tools.getSize(decompressedBytes)), str(sq_tools.getSize(written)), nca._path))
								t.write('  * Compressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))
							newNsp.resize(newFileName, written)
							files2.append(newFileName)
							filesizes2.append(written)
							continue

						f = newNsp.add(nca._path, nca.size,t,isthreaded)
						files2.append(nca._path)
						filesizes2.append(nca.size)
						nca.seek(0)

						while not nca.eof():
							buffer = nca.read(CHUNK_SZ)
							t.update(len(buffer))
							f.write(buffer)

	t.close()
	newNsp.close()

	xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=sq_tools.get_xciheader(files2,filesizes2,sec_hashlist)
	outheader=xci_header
	outheader+=game_info
	outheader+=sig_padding
	outheader+=xci_certificate
	outheader+=root_header
	outheader+=upd_header
	outheader+=norm_header
	outheader+=sec_header
	with open(nszPath, 'rb+') as o:
		o.seek(0)
		o.write(outheader)
	try:
		exchangefile.deletefile()
	except:pass
	if isthreaded==True and nthreads!=False:
		for i in range(nthreads):
			tqlist[i].close()
	return nszPath



def xci_to_nsz(filepath,buffer=65536,outfile=None,keepupd=False, level = 17,  threads = 0, pos=False, nthreads=False):
	isthreaded=False
	if pos!=False:
		isthreaded=True
	elif str(pos)=='0':
		isthreaded=True
	else:
		pos=0
	pos=int(pos)
	try:
		exchangefile.deletefile()
	except:pass
	f=squirrelXCI(filepath)
	for nspF in f.hfs0:
		if str(nspF._path)=="secure":
			for ticket in nspF:
				if str(ticket._path).endswith('.tik'):
					if isthreaded==False:
						print('- Titlerights: '+ticket.rightsId)
					tk=(str(hex(ticket.getTitleKeyBlock()))[2:]).upper()
					if isthreaded==False:
						print('- Titlekey: '+tk)
					exchangefile.add(ticket.rightsId,tk)
	f.flush()
	f.close()
	files_list=sq_tools.ret_xci_offsets(filepath)
	files=list();filesizes=list()
	if isthreaded==True and nthreads!=False:
		tqlist=list()
		for i in range(nthreads):
			tq = tqdm(total=0, unit='B', unit_scale=True, leave=False,position=i)
			tqlist.append(tq)
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
			f=squirrelXCI(filepath)
			titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
			f.flush()
			f.close()
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
	properheadsize=len(nspheader)

	compressionLevel=int(level)
	CHUNK_SZ = buffer
	if outfile==None:
		nszPath = filepath[0:-1] + 'z'
	else:
		nszPath=outfile
	nszPath = os.path.abspath(nszPath)

	tsize=properheadsize
	for sz in filesizes:
		tsize+=sz
	if isthreaded==True:
		from colorama import Fore
		colors=Fore.__dict__
		k=0;l=pos
		for col in colors:
			if l>len(colors):
				l=l-len(colors)
			color=colors[col]
			if k==(l+1):
				break
			else:
				k+=1
		t = tqdm(total=tsize, unit='B', unit_scale=True, leave=False,position=pos,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, Fore.RESET))
	else:
		t = tqdm(total=tsize, unit='B', unit_scale=True, leave=False,position=0)

	if isthreaded==False:
		t.write('Compressing with level %d and %d threads' % (compressionLevel, threads))
		t.write('\n  %s -> %s \n' % (filepath, nszPath))

	newNsp = nutFs.Pfs0.Pfs0Stream(nszPath,headsize=properheadsize,mode='wb+')

	xcicontainer = Xci(filepath)
	# f.compressed_supertrim(buffer,outfile,keepupd,level,threads)
	for nspF in xcicontainer.hfs0:
		if str(nspF._path)=="secure":
			for nca in nspF:
				if isinstance(nca, nutFs.Nca.Nca) and (nca.header.contentType == nutFs.Type.Content.PROGRAM or nca.header.contentType == nutFs.Type.Content.PUBLIC_DATA):
					if isNcaPacked(nca):
						skip=0
					else:
						skip=int(ncaHeaderSize-(((sortedFs(nca))[0]).offset))
					cctx = zstandard.ZstdCompressor(level=compressionLevel, threads = threads)

					newFileName = nca._path[0:-1] + 'z'

					f = newNsp.add(newFileName, nca.size,t,isthreaded)

					start = f.tell()

					nca.seek(0)
					data=nca.read(ncaHeaderSize)
					f.write(data)
					nca.seek(ncaHeaderSize)

					written = ncaHeaderSize

					compressor = cctx.stream_writer(f)

					sections = get_sections(nca)

					header = b'NCZSECTN'
					header += len(sections).to_bytes(8, 'little')

					i = 0
					for fs in sections:
						i += 1
						if skip>0:
							header += (fs.offset+skip).to_bytes(8, 'little')
							header += (fs.size-skip).to_bytes(8, 'little')
							header += fs.cryptoType.to_bytes(8, 'little')
							header += b'\x00' * 8
							header += fs.cryptoKey
							header += fs.cryptoCounter
						else:
							header += fs.offset.to_bytes(8, 'little')
							header += fs.size.to_bytes(8, 'little')
							header += fs.cryptoType.to_bytes(8, 'little')
							header += b'\x00' * 8
							header += fs.cryptoKey
							header += fs.cryptoCounter

					f.write(header)
					written += len(header)
					timestamp = time.time()
					decompressedBytes = ncaHeaderSize
					totsize=0
					for fs in sections:
						totsize+=fs.size
					c0=0
					for section in sections:
						#print('offset: %x\t\tsize: %x\t\ttype: %d\t\tiv%s' % (section.offset, section.size, section.cryptoType, str(hx(section.cryptoCounter))))
						o = nca.partition(offset = section.offset, size = section.size, n = None, cryptoType = section.cryptoType, cryptoKey = section.cryptoKey, cryptoCounter = bytearray(section.cryptoCounter), autoOpen = True)
						if c0==0 and skip>0:
							o.seek(skip)
						while not o.eof():
							buffer = o.read(CHUNK_SZ)
							t.update(len(buffer))
							if len(buffer) == 0:
								raise IOError('read failed')

							written += compressor.write(buffer)

							decompressedBytes += len(buffer)
						c0+=1
					compressor.flush(zstandard.FLUSH_FRAME)

					elapsed = time.time() - timestamp
					minutes = elapsed / 60
					seconds = elapsed % 60

					speed = 0 if elapsed == 0 else (nca.size / elapsed)

					written = f.tell() - start
					if isthreaded==False:
						t.write('\n  * Compressed at %d%% from %s to %s  - %s' % (int(written * 100 / nca.size), str(sq_tools.getSize(decompressedBytes)), str(sq_tools.getSize(written)), nca._path))
						t.write('  * Compressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))
					newNsp.resize(newFileName, written)
					continue

				f = newNsp.add(nca._path, nca.size,t,isthreaded)

				nca.seek(0)
				while not nca.eof():
					buffer = nca.read(CHUNK_SZ)
					t.update(len(buffer))
					f.write(buffer)
	t.close()
	newNsp.close()
	try:
		exchangefile.deletefile()
	except:pass
	if isthreaded==True and nthreads!=False:
		for i in range(nthreads):
			tqlist[i].close()
	return nszPath

def compress(filePath,ofolder = None, level = 17,  threads = 0, delta=False, ofile= None, buffer=65536,pos=False, nthreads=False):
	isthreaded=False
	if pos!=False:
		isthreaded=True
	elif str(pos)=='0':
		isthreaded=True
	else:
		pos=0
	pos=int(pos)
	files_list=sq_tools.ret_nsp_offsets(filePath)
	files=list();filesizes=list()
	if isthreaded==True and nthreads!=False:
		tqlist=list()
		for i in range(nthreads):
			tq = tqdm(total=0, unit='B', unit_scale=True, leave=False,position=i)
			tqlist.append(tq)
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
			f=squirrelNSP(filePath,'rb')
			titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
			f.flush()
			f.close()
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
	properheadsize=len(nspheader)

	compressionLevel=int(level)
	container = nutFs.factory(filePath)

	container.open(filePath, 'rb')

	CHUNK_SZ = buffer

	if ofolder is None and ofile is None:
		nszPath = filePath[0:-1] + 'z'
	elif ofolder is not None:
		nszPath = os.path.join(ofolder, os.path.basename(filePath[0:-1] + 'z'))
	elif ofile is not None:
		nszPath = ofile

	tsize=properheadsize
	for sz in filesizes:
		tsize+=sz
	if isthreaded==True:
		from colorama import Fore
		colors=Fore.__dict__
		k=0;l=pos
		for col in colors:
			if l>len(colors):
				l=l-len(colors)
			color=colors[col]
			if k==(l+1):
				break
			else:
				k+=1
		t = tqdm(total=tsize, unit='B', unit_scale=True, leave=False,position=pos,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, Fore.RESET))
	else:
		t = tqdm(total=tsize, unit='B', unit_scale=True, leave=False,position=0)
	nszPath = os.path.abspath(nszPath)
	if isthreaded==False:
		t.write('\n Compressing with level %d and %d threads' % (compressionLevel, threads))
		t.write('%s -> %s \n' % (filePath, nszPath))
	newNsp = nutFs.Pfs0.Pfs0Stream(nszPath,headsize=properheadsize)

	for file in files:
		for nspf in container:
			if nspf._path==file:
				if isinstance(nspf, nutFs.Nca.Nca) and nspf.header.contentType == nutFs.Type.Content.DATA and delta==False:
					if isthreaded==False:
						t.write('-> Skipping delta fragment')
					continue

				if isinstance(nspf, nutFs.Nca.Nca) and (nspf.header.contentType == nutFs.Type.Content.PROGRAM or nspf.header.contentType == nutFs.Type.Content.PUBLIC_DATA):
					if isNcaPacked(nspf):
						skip=0
					else:
						skip=int(ncaHeaderSize-(((sortedFs(nspf))[0]).offset))
					cctx = zstandard.ZstdCompressor(level=compressionLevel, threads = threads)

					newFileName = nspf._path[0:-1] + 'z'

					f = newNsp.add(newFileName, nspf.size,t,isthreaded)

					start = f.tell()

					nspf.seek(0)
					f.write(nspf.read(ncaHeaderSize))
					written = ncaHeaderSize

					compressor = cctx.stream_writer(f)

					sections = get_sections(nspf)

					header = b'NCZSECTN'
					header += len(sections).to_bytes(8, 'little')

					i = 0
					for fs in sections:
						i += 1
						if skip>0:
							header += (fs.offset+skip).to_bytes(8, 'little')
							header += (fs.size-skip).to_bytes(8, 'little')
							header += fs.cryptoType.to_bytes(8, 'little')
							header += b'\x00' * 8
							header += fs.cryptoKey
							header += fs.cryptoCounter
						else:
							header += fs.offset.to_bytes(8, 'little')
							header += fs.size.to_bytes(8, 'little')
							header += fs.cryptoType.to_bytes(8, 'little')
							header += b'\x00' * 8
							header += fs.cryptoKey
							header += fs.cryptoCounter

					f.write(header)
					written += len(header)
					timestamp = time.time()
					decompressedBytes = ncaHeaderSize
					totsize=0
					for fs in sections:
						totsize+=fs.size
					c0=0
					for section in sections:
						#print('offset: %x\t\tsize: %x\t\ttype: %d\t\tiv%s' % (section.offset, section.size, section.cryptoType, str(hx(section.cryptoCounter))))
						o = nspf.partition(offset = section.offset, size = section.size, n = None, cryptoType = section.cryptoType, cryptoKey = section.cryptoKey, cryptoCounter = bytearray(section.cryptoCounter), autoOpen = True)
						if c0==0 and skip>0:
							o.seek(skip)

						while not o.eof():
							buffer = o.read(CHUNK_SZ)
							t.update(len(buffer))
							if len(buffer) == 0:
								raise IOError('read failed')

							written += compressor.write(buffer)

							decompressedBytes += len(buffer)
						c0+=1
					compressor.flush(zstandard.FLUSH_FRAME)

					elapsed = time.time() - timestamp
					minutes = elapsed / 60
					seconds = elapsed % 60

					speed = 0 if elapsed == 0 else (nspf.size / elapsed)

					written = f.tell() - start
					if isthreaded==False:
						t.write('\n  * Compressed at %d%% from %s to %s  - %s' % (int(written * 100 / nspf.size), str(sq_tools.getSize(decompressedBytes)), str(sq_tools.getSize(written)), nspf._path))
						t.write('  * Compressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))
					newNsp.resize(newFileName, written)
					continue

				f = newNsp.add(nspf._path, nspf.size,t,isthreaded)
				nspf.seek(0)
				while not nspf.eof():
					buffer = nspf.read(CHUNK_SZ)
					t.update(len(buffer))
					f.write(buffer)
	t.close()
	newNsp.close()
	if isthreaded==True and nthreads!=False:
		for i in range(nthreads):
			tqlist[i].close()
