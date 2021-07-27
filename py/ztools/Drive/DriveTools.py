# -*- coding: utf-8 -*-
import sys
from binascii import hexlify as hx, unhexlify as uhx
import Hex
import io
import sq_tools
import Fs.Nca as Nca
from Fs.Nca import NcaHeader
import Fs.Nsp as Nsp
import Fs.Nacp as Nacp
from Fs.Pfs0 import Pfs0
from Fs.Ticket import Ticket
from Fs.pyNCA3 import NCA3
from Fs.pyNPDM import NPDM
from Fs.File import MemoryFile
from hashlib import sha256,sha1
from Drive import Public
from Drive import Private

import Keys
from Fs import Type
import nutFs
from nutFs.BaseFs import BaseFs
from nutFs.Rom import Rom
import Print

def readInt8(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(1), byteorder=byteorder, signed=signed)

def readInt16(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(2), byteorder=byteorder, signed=signed)

def readInt32(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(4), byteorder=byteorder, signed=signed)

def readInt64(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(8), byteorder=byteorder, signed=signed)

def readInt128(f, byteorder='little', signed = False):
	return int.from_bytes(f.read(16), byteorder=byteorder, signed=signed)

def GetSectionFilesystem(buffer, cryptoKey):
	fsType = buffer[0x3]
	if fsType == nutFs.Type.nutFs.PFS0:
		return Pfs0(buffer, cryptoKey = cryptoKey)

	if fsType == nutFs.Type.nutFs.ROMFS:
		return Rom(buffer, cryptoKey = cryptoKey)

	return BaseFs(buffer, cryptoKey = cryptoKey)

def get_files_from_head_nsp(file,kbsize=8):
	kbsize=int(kbsize);buf=int(kbsize*1024)
	file.rewind();res=file.response
	try:
		for data in res.iter_content(chunk_size=buf):
			data=data
			#print(hx(data))
			break
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
	except IOError as e:
		print(e, file=sys.stderr)
	if 	headerSize>buf:
		data2=file.read_at(buf,headerSize)
		data=data+data2
	#print(head)
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
		off1=offset+headerSize
		off2=off1+size
		files_list.append([name,off1,off2,size])
	files_list.reverse()
	return files_list

def get_files_from_head_xci(file,kbsize=8):
	kbsize=int(kbsize);buf=int(8*1024)
	files_list=list();file.rewind()
	try:
		rawhead = io.BytesIO(file.read(int(0x200)))
		data=rawhead.read()
		try:
			rawhead.seek(0x100)
			magic=rawhead.read(0x4)
			# print(magic)
			if magic==b'HEAD':
				# print(magic)
				secureOffset=int.from_bytes(rawhead.read(4), byteorder='little')
				secureOffset=secureOffset*0x200
				data=file.read_at(secureOffset,int(kbsize*1024))
				rawhead = io.BytesIO(data)
				rmagic=rawhead.read(0x4)
				# print(rmagic)
				if rmagic==b'HFS0':
					head=data[0:4]
					n_files=(data[4:8])
					n_files=int.from_bytes(n_files, byteorder='little')
					st_size=(data[8:12])
					st_size=int.from_bytes(st_size, byteorder='little')
					junk=(data[12:16])
					offset=(0x10 + n_files * 0x40)
					stringTable=(data[offset:offset+st_size])
					stringEndOffset = st_size
					headerSize = 0x10 + 0x40 * n_files + st_size
					# print(head)
					# print(str(n_files))
					# print(str(st_size))
					# print(str((stringTable)))
					for i in range(n_files):
						i = n_files - i - 1
						pos=0x10 + i * 0x40
						offset = data[pos:pos+8]
						offset=int.from_bytes(offset, byteorder='little')
						size = data[pos+8:pos+16]
						size=int.from_bytes(size, byteorder='little')
						nameOffset = data[pos+16:pos+20] # just the offset
						nameOffset=int.from_bytes(nameOffset, byteorder='little')
						name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
						stringEndOffset = nameOffset
						junk2 = data[pos+20:pos+24] # junk data
						# print(name)
						# print(offset)
						# print(size)
						off1=offset+headerSize+secureOffset
						off2=off1+size
						files_list.append([name,off1,off2,size])
					files_list.reverse()
					# print(files_list)
		except IOError as e:
			print(e, file=sys.stderr)
	except IOError as e:
		print(e, file=sys.stderr)
	return files_list

def get_files_from_head_xci_fw(file,partition='update',kbsize=32):
	kbsize=int(kbsize);buf=int(8*1024)
	files_list=list();file.rewind()
	try:
		rawhead = io.BytesIO(file.read(int(0x200)))
		data=rawhead.read()
		try:
			rawhead.seek(0x100)
			magic=rawhead.read(0x4)
			# print(magic)
			if magic==b'HEAD':
				HFS0_offset=0xF000
				data=file.read_at(HFS0_offset,int(kbsize*1024))
				rawhead = io.BytesIO(data)
				rmagic=rawhead.read(0x4)
				# print(rmagic)
				if rmagic==b'HFS0':
					head=data[0:4]
					n_files=(data[4:8])
					n_files=int.from_bytes(n_files, byteorder='little')
					st_size=(data[8:12])
					st_size=int.from_bytes(st_size, byteorder='little')
					junk=(data[12:16])
					offset=(0x10 + n_files * 0x40)
					stringTable=(data[offset:offset+st_size])
					stringEndOffset = st_size
					headerSize = 0x10 + 0x40 * n_files + st_size
					# print(head)
					# print(str(n_files))
					# print(str(st_size))
					# print(str((stringTable)))
					for i in range(n_files):
						i = n_files - i - 1
						pos=0x10 + i * 0x40
						offset = data[pos:pos+8]
						offset=int.from_bytes(offset, byteorder='little')
						size = data[pos+8:pos+16]
						size=int.from_bytes(size, byteorder='little')
						nameOffset = data[pos+16:pos+20] # just the offset
						nameOffset=int.from_bytes(nameOffset, byteorder='little')
						name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
						stringEndOffset = nameOffset
						junk2 = data[pos+20:pos+24] # junk data
						# print(name)
						# print(offset)
						# print(size)
						off1=offset+headerSize+HFS0_offset
						off2=off1+size
						files_list.append([name,off1,off2,size])
					files_list.reverse()
					# print(files_list)
					updoffset=False
					for f in files_list:
						if f[0]==str(partition).lower():
							updoffset=f[1]
							break
					files_list=list()
					if updoffset!=False:
						data=file.read_at(updoffset,int(kbsize*1024))
						rawhead = io.BytesIO(data)
						a=rawhead.read()
						rawhead.seek(0)
						rmagic=rawhead.read(0x4)
						if rmagic==b'HFS0':
							#print(rmagic)
							head=data[0:4]
							n_files=(data[4:8])
							n_files=int.from_bytes(n_files, byteorder='little')
							st_size=(data[8:12])
							st_size=int.from_bytes(st_size, byteorder='little')
							junk=(data[12:16])
							offset=(0x10 + n_files * 0x40)
							stringTable=(data[offset:offset+st_size])
							stringEndOffset = st_size
							headerSize = 0x10 + 0x40 * n_files + st_size
							# print(head)
							# print(str(n_files))
							# print(str(st_size))
							# print(str((stringTable)))
							for i in range(n_files):
								i = n_files - i - 1
								pos=0x10 + i * 0x40
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
								off1=offset+headerSize+HFS0_offset
								off2=off1+size
								files_list.append([name,off1,off2,size])
								# with open(filename, 'r+b') as f:
									# f.seek(off1)
									# print(f.read(0x4))
							files_list.reverse()
							# print(files_list)
		except IOError as e:
			print(e, fi=sys.stderr)
	except IOError as e:
		print(e, fi=sys.stderr)
	return files_list

def get_files_from_head(file,output):
	if output.endswith('.nsp') or output.endswith('.nsz') or output.endswith('.nsx'):
		files_list=get_files_from_head_nsp(file)
	elif output.endswith('.xci') or  output.endswith('.xcz'):
		files_list=get_files_from_head_xci(file)
	return 	files_list

def get_key(url):
	file=location(url)
	res=file.response;readable=file.readable;output=file.name

	if not readable:
		return False
	else:
		clean_name=untag(output)

	files_list=get_files_from_head(file,output)

	for i in range(len(files_list)):
		if (files_list[i][0]).endswith('.tik'):
			#print(files_list[i][0])
			#print(files_list[i][1])
			#print(files_list[i][2])
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			trights=((files_list[i][0])[:-4]).upper()
			#print(trights)
	file.rewind()
	file.seek(off1,sz)
	buf=int(sz)
	try:
		data=file.read(buf)
		tk=str(hx(data[0x180:0x190]))
		tk=tk.upper();tk=tk[2:-1]
		#print(tk)
		print('TRIGHTS STRING: ')
		print(trights+'|'+tk+'|'+clean_name)
	except IOError as e:
		print(e, file=sys.stderr)

def get_cnmt_data(path=None,TD=None,filter=None,target=None,file=None):
	if path==None and file==None:
		return False
	if file != None:
		remote=file
		type='file'
		remote.rewind()
	elif path.startswith('http'):
		url=path
		remote=Public.location(url);readable=remote.readable
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
		Private.folderpicker(path,TD=TD,filter=filter,mode='get_cnmt_data')
		return
	else:
		files_list=get_files_from_head(remote,remote.name)
		# print(files_list)
		for i in range(len(files_list)):
			if (files_list[i][0]).endswith('.cnmt.nca'):
				nca_name=files_list[i][0]
				off1=files_list[i][1]
				off2=files_list[i][2]
				sz=files_list[i][3]
				if target==None:
					break
				# print(nca_name)
				# print(target)
				if str(nca_name).lower()==str(target).lower():
					break
		remote.seek(off1,off2)
		buf=int(sz)
		try:
			nca=Nca()
			nca.open(MemoryFile(remote.read(buf)))
			nca.rewind()
			cnmt=io.BytesIO(nca.return_cnmt())
			titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=cnmt_data(cnmt,nca,nca_name)
			d={}
			d['titleid']=titleid;d['version']=titleversion;d['baseid']=base_ID;d['keygeneration']=keygeneration;d['rightsId']=rightsId;
			d['rsv']=RSV;d['rgv']=RGV;d['ctype']=ctype;d['metasdkversion']=metasdkversion;d['exesdkversion']=exesdkversion;
			d['hasHtmlManual']=hasHtmlManual;d['Installedsize']=Installedsize;d['DeltaSize']=DeltaSize;d['ncadata']=ncadata;
			# print(d)
			return d,files_list,remote
		except IOError as e:
			print(e, file=sys.stderr)

def get_nacp_data(path=None,TD=None,filter=None,file=None):
	cnmtdict,files_list,remote=get_cnmt_data(path,TD,filter)
	print(cnmtdict)
	ctype=cnmtdict['ctype']
	nacpdict=nacp_data(remote,cnmtdict['ncadata'],files_list,ctype)
	print(nacpdict)
	return nacpdict

def cnmt_data(cnmt,nca,nca_name):
	crypto1=nca.header.getCryptoType()
	crypto2=nca.header.getCryptoType2()
	if crypto2>crypto1:
		keygeneration=crypto2
	if crypto2<=crypto1:
		keygeneration=crypto1
	cnmt.seek(0)
	titleid=readInt64(cnmt)
	titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
	titleid2 = titleid2[2:-1]
	titleid=(str(hx(titleid.to_bytes(8, byteorder='big')))[2:-1]).upper()
	titleversion = cnmt.read(0x4)
	titleversion=str(int.from_bytes(titleversion, byteorder='little'))
	type_n = cnmt.read(0x1)
	cnmt.seek(0xE)
	offset=readInt16(cnmt)
	content_entries=readInt16(cnmt)
	meta_entries=readInt16(cnmt)
	cnmt.seek(0x20)
	base_ID=readInt64(cnmt)
	base_ID=(str(hx(base_ID.to_bytes(8, byteorder='big')))[2:-1]).upper()
	cnmt.seek(0x28)
	min_sversion=readInt32(cnmt)
	length_of_emeta=readInt32(cnmt)
	content_type_cnmt=None
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
	programSDKversion=None
	dataSDKversion=None
	if content_type_cnmt == 'AddOnContent':
		exesdkversion=dataSDKversion
	if content_type_cnmt != 'AddOnContent':
		exesdkversion=programSDKversion
	ncadata=list()
	hasHtmlManual=False
	Installedsize=int(nca.header.size);DeltaSize=0
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
		unknown = cnmt.read(0x1)
		data['NcaId']=NcaId[2:-1]
		data['NCAtype']=ncatype
		data['Size']=size
		data['Hash']=vhash[2:-1]
		if ncatype != "DeltaFragment":
			Installedsize=Installedsize+int(size)
		else:
			DeltaSize=DeltaSize+int(size)
		if ncatype == "HtmlDocument":
			hasHtmlManual=True
		ncadata.append(data)
	cnmtdata={}
	metaname=str(nca_name);metaname =  metaname[:-9]
	nca.rewind();block = nca.read();nsha=sha256(block).hexdigest()
	cnmtdata['NcaId']=metaname
	cnmtdata['NCAtype']='Meta'
	cnmtdata['Size']=str(nca.header.size)
	cnmtdata['Hash']=str(nsha)
	ncadata.append(cnmtdata)
	if int(crypto2)>9:
		kg_=str(hex(int(str(crypto2))))[2:]
	else:
		kg_=str(crypto2)
	if len(str(kg_))==1:
		rightsId=str(titleid2).lower()+'000000000000000'+kg_
	elif len(str(kg_))==2:
		rightsId=str(titleid2)+'00000000000000'+kg_
	return 	titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata

def get_titlekey(remote,rightsId,keygeneration,files_list=None):
	if files_list==None:
		files_list=get_files_from_head(remote,remote.name)
	hasticket=False
	for i in range(len(files_list)):
		if (files_list[i][0]).endswith('.tik'):
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			trights=((files_list[i][0])[:-4]).upper()
			if str(trights).upper()==str(rightsId).upper():
				hasticket=True
				break
	if hasticket==False:
		return False
	remote.rewind()
	remote.seek(off1,sz)
	buf=int(sz)
	try:
		data=remote.read(buf)
		tk=str(hx(data[0x180:0x190]))
		tk=tk[2:-1]
		encKey=bytes.fromhex(tk)
		titleKeyDec = Keys.decryptTitleKey(encKey, Keys.getMasterKeyIndex(keygeneration))
		return titleKeyDec
	except IOError as e:
		print(e, file=sys.stderr)
		return False

def nacp_data(file,ncadata,files_list,ctype):
	ncaname=None;dict={}
	for entry in ncadata:
		if str(entry['NCAtype']).lower()=='control':
			ncaname=entry['NcaId']+'.nca'
			break
	if ncaname!=None:
		for i in range(len(files_list)):
			if files_list[i][0]==ncaname:
				nca_name=files_list[i][0]
				off1=files_list[i][1]
				off2=files_list[i][2]
				sz=files_list[i][3]
				break
		file.seek(off1,off2)
		buf=int(sz)
		nca=Nca()
		nca.open(MemoryFile(file.read(buf)))
		nca.rewind()
		f=io.BytesIO(nca.ret_nacp());f.seek(0)
		nacp = Nacp()
		dict['RegionalNames'],dict['RegionalEditors']=nacp.get_NameandPub(f.read(0x300*15))
		f.seek(0x3000)
		dict['ISBN']=nacp.get_Isbn(f.read(0x24))
		f.seek(0x3025)
		dict['StartupUserAccount']=nacp.get_StartupUserAccount(readInt8(f,'little'))
		dict['UserAccountSwitchLock']=nacp.get_UserAccountSwitchLock(readInt8(f,'little'))
		dict['AddOnContentRegistrationType']=nacp.get_AddOnContentRegistrationType(readInt8(f,'little'))
		dict['ctype']=nacp.get_ContentType(readInt8(f,'little'))
		dict['ParentalControl']=nacp.get_ParentalControl(readInt8(f,'little'))
		dict['ScreenshotsEnabled']=nacp.get_Screenshot(readInt8(f,'little'))
		dict['VideocaptureEnabled']=nacp.get_VideoCapture(readInt8(f,'little'))
		dict['dataLossConfirmation']=nacp.get_dataLossConfirmation(readInt8(f,'little'))
		dict['PlayLogPolicy']=nacp.get_PlayLogPolicy(readInt8(f,'little'))
		dict['PresenceGroupId']=nacp.get_PresenceGroupId(readInt64(f,'little'))
		f.seek(0x3040)
		dict['AgeRatings']=nacp.get_RatingAge(f.read(0x20))
		f.seek(0x3060)
		try:
			dict['BuildNumber']=nacp.get_DisplayVersion(f.read(0xF))
			f.seek(0x3070)
			dict['AddOnContentBaseId']=nacp.get_AddOnContentBaseId(readInt64(f,'little'))
			f.seek(0x3078)
			dict['SaveDataOwnerId']=nacp.get_SaveDataOwnerId(readInt64(f,'little'))
			f.seek(0x3080)
			dict['UserAccountSaveDataSize']=nacp.get_UserAccountSaveDataSize(readInt64(f,'little'))
			f.seek(0x3088)
			dict['UserAccountSaveDataJournalSize']=nacp.get_UserAccountSaveDataJournalSize(readInt64(f,'little'))
			f.seek(0x3090)
			dict['DeviceSaveDataSize']=nacp.get_DeviceSaveDataSize(readInt64(f,'little'))
			f.seek(0x3098)
			dict['DeviceSaveDataJournalSize']=nacp.get_DeviceSaveDataJournalSize(readInt64(f,'little'))
			f.seek(0x30A0)
			dict['BcatDeliveryCacheStorageSize']=nacp.get_BcatDeliveryCacheStorageSize(readInt64(f,'little'))
			f.seek(0x30A8)
			dict['ApplicationErrorCodeCategory']=nacp.get_ApplicationErrorCodeCategory(f.read(0x07))
			f.seek(0x30B0)
			dict['LocalCommunicationId']=nacp.get_LocalCommunicationId(readInt64(f,'little'))
			f.seek(0x30F0)
			dict['LogoType']=nacp.get_LogoType(readInt8(f,'little'))
			dict['LogoHandling']=nacp.get_LogoHandling(readInt8(f,'little'))
			dict['RuntimeAddOnContentInstall']=nacp.get_RuntimeAddOnContentInstall(readInt8(f,'little'))
			dict['CrashReport']=nacp.get_CrashReport(readInt8(f,'little'))
			dict['Hdcp']=nacp.get_Hdcp(readInt8(f,'little'))
			dict['SeedForPseudoDeviceId']=nacp.get_SeedForPseudoDeviceId(readInt64(f,'little'))
			f.seek(0x3100)
			dict['BcatPassphrase']=nacp.get_BcatPassphrase(f.read(0x40))
			f.seek(0x3148)
			dict['UserAccountSaveDataSizeMax']=nacp.par_UserAccountSaveDataSizeMax(readInt64(f,'little'))
			f.seek(0x3150)
			dict['UserAccountSaveDataJournalSizeMax']=nacp.par_UserAccountSaveDataJournalSizeMax(readInt64(f,'little'))
			f.seek(0x3158)
			dict['DeviceSaveDataSizeMax']=nacp.get_DeviceSaveDataSizeMax(readInt64(f,'little'))
			f.seek(0x3160)
			dict['DeviceSaveDataJournalSizeMax']=nacp.get_DeviceSaveDataJournalSizeMax(readInt64(f,'little'))
			f.seek(0x3168)
			dict['TemporaryStorageSize']=nacp.get_TemporaryStorageSize(readInt64(f,'little'))
			dict['CacheStorageSize']=nacp.get_CacheStorageSize(readInt64(f,'little'))
			f.seek(0x3178)
			dict['CacheStorageJournalSize']=nacp.get_CacheStorageJournalSize(readInt64(f,'little'))
			dict['CacheStorageDataAndJournalSizeMax']=nacp.get_CacheStorageDataAndJournalSizeMax(readInt64(f,'little'))
			f.seek(0x3188)
			dict['CacheStorageIndexMax']=nacp.get_CacheStorageIndexMax(readInt64(f,'little'))
			dict['PlayLogQueryableApplicationId']=nacp.get_PlayLogQueryableApplicationId(readInt64(f,'little'))
			f.seek(0x3210)
			dict['PlayLogQueryCapability']=nacp.get_PlayLogQueryCapability(readInt8(f,'little'))
			dict['Repair']=nacp.get_Repair(readInt8(f,'little'))
			dict['ProgramIndex']=nacp.get_ProgramIndex(readInt8(f,'little'))
			dict['RequiredNetworkServiceLicenseOnLaunch']=nacp.get_RequiredNetworkServiceLicenseOnLaunch(readInt8(f,'little'))
		except:pass
		nca.rewind()
		title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock('DLC',roman=True)
		dict['title']=title
		dict['editor']=editor
		dict['SupLg']=SupLg
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
		dict['ctype']=ctype
	return dict

def get_xci_rom_size(remote):
	files_list=get_files_from_head(remote,remote.name)
	lastfile=files_list[-1]
	endfile=int(lastfile[2])
	return endfile

def file_hash(remote,target,files_list=None):
	if files_list==None:
		files_list=get_files_from_head(remote,remote.name)
	else:
		files_list=files_list
	target2=target[:-1]+'z'
	indent = 1
	gamecard = False
	tabs = '\t' * indent
	sha=False;sizef=False
	for i in range(len(files_list)):
		if str(files_list[i][0]).lower()==str(target).lower() or str(files_list[i][0]).lower()==str(target2).lower():
			nca_name=files_list[i][0]
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			break
	hblock=remote.read_at(off1,0x200)
	sha=sha256(hblock).hexdigest()
	if nca_name.endswith('.ncz') or nca_name.endswith('.nca'):
		ncaHeader = NcaHeader()
		ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
	if nca_name.endswith('.ncz'):
		sizef=ncaHeader.size
	else:
		sizef=sz
	if nca_name.endswith('.ncz'):
		if	ncaHeader.getgamecard() == 1:
			gamecard=True
		else:
			nca_id=ncaHeader.titleId
			if nca_id.endswith('000') or nca_id.endswith('800'):
				if 	str(ncaHeader.contentType) == 'Content.PROGRAM':
					docheck=True
			else:
				if 	str(ncaHeader.contentType) == 'Content.DATA':
					docheck=True
			if docheck == True:
				crypto1=ncaHeader.getCryptoType()
				crypto2=ncaHeader.getCryptoType2()
				if crypto2>crypto1:
					masterKeyRev=crypto2
				if crypto2<=crypto1:
					masterKeyRev=crypto1
				crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), ncaHeader.keyIndex))
				KB1L=ncaHeader.getKB1L()
				KB1L = crypto.decrypt(KB1L)
				if sum(KB1L) == 0:
					gamecard=True
	return sha,sizef,gamecard

def read_buildid(path=None,TD=None,filter=None,file=None,cnmtdict=None,files_list=None,dectkey=None):
	ModuleId='';BuildID8='';BuildID16='';iscorrect=False;sdkversion='-'
	sectionFilesystems=[]
	if file !=None and cnmtdict!=None and files_list!=None:
		remote=file
	else:
		cnmtdict,files_list,remote=get_cnmt_data(path,TD,filter)
	ctype=cnmtdict['ctype']
	if ctype != 'DLC':
		ncadata=cnmtdict['ncadata']
		for entry in ncadata:
			if str(entry['NCAtype']).lower()=='program':
				ncaname=entry['NcaId']+'.nca'
				break
		for i in range(len(files_list)):
			if (files_list[i][0])==ncaname:
				name=files_list[i][0]
				off1=files_list[i][1]
				off2=files_list[i][2]
				sz=files_list[i][3]
				break
		remote.seek(off1,off2)
		ncaHeader = NcaHeader()
		ncaHeader.open(MemoryFile(remote.read(0xC00), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
		ncaHeader.rewind()
		if ncaHeader.getRightsId() == 0:
			decKey=ncaHeader.titleKeyDec
		elif dectkey!=None:
			# print(dectkey)
			decKey=bytes.fromhex(dectkey)
		try:
			sdkversion=get_sdkversion_from_head(ncaHeader)
		except:
			sdkversion='-'
		try:
			ncaHeader.seek(0x400)
			for i in range(4):
				hdr = ncaHeader.read(0x200)
				section = BaseFs(hdr, cryptoKey = ncaHeader.titleKeyDec)
				fs = GetSectionFilesystem(hdr, cryptoKey = -1)
				if fs.fsType:
					fs.offset=ncaHeader.sectionTables[i].offset
					sectionFilesystems.append(fs)
					# Print.info('fs type = ' + hex(fs.fsType))
					# Print.info('fs crypto = ' + hex(fs.cryptoType))
					# Print.info('fs cryptocounter = ' + str(fs.cryptoCounter))
					# Print.info('st end offset = ' + str(ncaHeader.sectionTables[i].endOffset - ncaHeader.sectionTables[i].offset))
					# Print.info('fs offset = ' + hex(ncaHeader.sectionTables[i].offset))
					# Print.info('fs section start = ' + hex(fs.sectionStart))
					# Print.info('titleKey = ' + str(hx(ncaHeader.titleKeyDec)))
			for fs in sectionFilesystems:
				if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
					# print(fs.fsType)
					# print(fs.cryptoType)
					# print(fs.buffer)
					pfs0=fs
					sectionHeaderBlock = fs.buffer
					pfs0Offset=fs.offset+fs.sectionStart
					skoff=off1+pfs0Offset
					# pfs0Offset=off1+fs.offset+0xC00+ncaHeader.get_htable_offset()
					remote.seek(skoff,off2)
					# print(str(fs.cryptoCounter))
					pfs0Header = remote.read(0x10*30)
					# print(hex(pfs0Offset))
					# print(hex(fs.sectionStart))
					# Hex.dump(pfs0Header)
					off=fs.offset+fs.sectionStart
					mem = MemoryFile(pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = pfs0Offset)
					data = mem.read();
					# Hex.dump(data)
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
					# print(head)
					# print(str(n_files))
					# print(str(st_size))
					# print(str((stringTable)))
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
						# junk2 = data[pos+20:pos+24] # junk data
						# print(name)
						# print(offset)
						# print(size)
						files_list.append([name,offset,size])
					files_list.reverse()
					# print(files_list)
					for i in range(len(files_list)):
						if files_list[i][0] == 'main':
							foff=files_list[i][1]+pfs0Offset+headerSize
							skoff2=files_list[i][1]+skoff+headerSize
							remote.seek(skoff2,off2)
							np=remote.read(0x60)
							mem = MemoryFile(np, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = foff)
							magic=mem.read(0x4)
							# print(magic)
							if magic==b'NSO0':
								mem.seek(0x40)
								data = mem.read(0x20);
								ModuleId=(str(hx(data)).upper())[2:-1]
								BuildID8=(str(hx(data[:8])).upper())[2:-1]
								BuildID16=(str(hx(data[:16])).upper())[2:-1]
								iscorrect=True;
							break
				break
		except:pass
	if iscorrect==False:
		ModuleId='';BuildID8='';BuildID16='';
	# print(ModuleId);print(BuildID8);print(BuildID16)
	return ModuleId,BuildID8,BuildID16,sdkversion

def get_sdkversion_from_head(ncaHeader):
	ncaHeader.rewind()
	sdkversion=str(ncaHeader.sdkVersion4)+'.'+str(ncaHeader.sdkVersion3)+'.'+str(ncaHeader.sdkVersion2)+'.'+str(ncaHeader.sdkVersion1)
	return sdkversion
