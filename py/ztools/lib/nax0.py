import aes128
import Print
import os
import shutil
import json
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs import Nca
import sq_tools
import hmac
import hashlib

import Keys
from binascii import hexlify as hx, unhexlify as uhx
import subprocess
import sys
from mtp.wpd import is_switch_connected
from python_pick import pick
from python_pick import Picker
import csv
from tqdm import tqdm
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
import Fs.Type
from Fs import Type
from listmanager import folder_to_list
import io
from hashlib import sha256,sha1

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed as completedfuture


# SET ENVIRONMENT
squirrel_dir=os.path.abspath(os.curdir)
NSCB_dir=os.path.abspath('../'+(os.curdir))

if os.path.exists(os.path.join(squirrel_dir,'ztools')):
	NSCB_dir=squirrel_dir
	zconfig_dir=os.path.join(NSCB_dir, 'zconfig')
	ztools_dir=os.path.join(NSCB_dir,'ztools')
	squirrel_dir=ztools_dir
elif os.path.exists(os.path.join(NSCB_dir,'ztools')):
	squirrel_dir=squirrel_dir
	ztools_dir=os.path.join(NSCB_dir, 'ztools')
	zconfig_dir=os.path.join(NSCB_dir, 'zconfig')
else:
	ztools_dir=os.path.join(NSCB_dir, 'ztools')
	zconfig_dir=os.path.join(NSCB_dir, 'zconfig')
	
testroute1=os.path.join(squirrel_dir, "squirrel.py")
testroute2=os.path.join(squirrel_dir, "squirrel.exe")
urlconfig=os.path.join(zconfig_dir,'NUT_DB_URL.txt')
isExe=False
if os.path.exists(testroute1):
	squirrel=testroute1
	isExe=False
elif os.path.exists(testroute2):
	squirrel=testroute2
	isExe=True

DB_folder=os.path.join(zconfig_dir,'DB')
if not os.path.exists(DB_folder):
	os.makedirs(DB_folder)
title_keys=os.path.join(DB_folder,'title.keys')
nax0_db=os.path.join(DB_folder,'nax0_db.json')

def readInt8(f_, byteorder='little', signed = False):
	return f_.read(1)[0]
	
def readInt16(f_, byteorder='little', signed = False):
	return int.from_bytes(f_.read(2), byteorder=byteorder, signed=signed)
	
def readInt32(f_, byteorder='little', signed = False):
	return int.from_bytes(f_.read(4), byteorder=byteorder, signed=signed)

def readInt48(f_, byteorder='little', signed = False):
	return int.from_bytes(f_.read(6), byteorder=byteorder, signed=signed)
	
def readInt64(f_, byteorder='little', signed = False):
	return int.from_bytes(f_.read(8), byteorder=byteorder, signed=signed)

def readInt128(f_, byteorder='little', signed = False):
	return int.from_bytes(f_.read(16), byteorder=byteorder, signed=signed)

def readInt(f_, size, byteorder='little', signed = False):
	return int.from_bytes(f_.read(size), byteorder=byteorder, signed=signed)
	
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
	cnmt_dict={
				'titleid':titleid,
				'titleversion':titleversion,
				'base_ID':base_ID,
				'keygeneration':keygeneration,
				'rightsId':rightsId,
				'RSV':RSV,
				'RGV':RGV,
				'ctype':ctype,
				'metasdkversion':metasdkversion,
				'exesdkversion':exesdkversion,
				'hasHtmlManual':hasHtmlManual,
				'Installedsize':Installedsize,
				'DeltaSize':DeltaSize,
				'ncadata':ncadata	
	}
	return cnmt_dict	
	
def get_SD_SEED():
	try:
		key= Keys.get('sd_seed')
		key= bytes.fromhex(key)
		return key
	except:
		return False
		
def get_sd_card_kek_source():
	try:
		key= Keys.get('sd_card_kek_source')
		key= bytes.fromhex(key)
		return key
	except:
		return False		
		
def get_sd_card_nca_key_source():
	try:
		key= Keys.get('sd_card_nca_key_source')
		key= bytes.fromhex(key)
		return key
	except:
		return False	
		
def get_relative_path(input):	
	p=os.path.abspath(input)
	if not p.endswith('nca'):
		z=(p.split('/'))[:-1]
		for x in z:
			p+='/'+x
		z=(p.split('\\'))[:-1]	
		for x in z:
			p+='/'+x		
		p=(p.split('Contents'))[-1]
		p.replace('\\','/')	
	else:
		z=(p.split('/'))
		for x in z:
			p+='/'+x
		z=(p.split('\\'))	
		for x in z:
			p+='/'+x	
		p=(p.split('Contents'))[-1]			
	return p

def get_decryption_keys(input,relative_PATH=False):
	if relative_PATH==False:
		r_path=get_relative_path(input)
	else:
		r_path=relative_PATH
	
	with open(input, 'rb') as f:
		HEADER_HMAC = f.read(0x20)
		header=f.read(0x60)
		f.seek(0x20)		
		MAGIC = f.read(0x4)		
		magic_pad =  f.read(0x4)
		CRYPTED_AES_KEYS = f.read(0x20)
		NCA_SIZE = readInt64(f)		
		PADDING = f.read(0x30)	
		
		if MAGIC not in [b'NAX0']:
			raise Exception('NOT A NAX0 CRYPTED FILE. MAGIC: ' + str(MAGIC))		
		
		sd_seed=get_SD_SEED()
		sd_card_kek_source = get_sd_card_kek_source()
		sd_card_nca_key_source = get_sd_card_nca_key_source()

		if 	sd_seed==False:
			raise Exception('MISSING SD_SEED')
			
		if 	sd_card_kek_source==False:
			raise Exception('MISSING sd_card_kek_source')		
		
		from Crypto.Cipher import AES
		crypto = AES.new(bytes.fromhex(Keys.get('master_key_00')), AES.MODE_ECB)
		kek = crypto.decrypt(bytes.fromhex(Keys.get('aes_kek_generation_source')))

		crypto = AES.new(kek, AES.MODE_ECB)
		Source = crypto.decrypt(sd_card_kek_source)
		
		crypto = AES.new(Source, AES.MODE_ECB)
		SDKEKTrue = crypto.decrypt(bytes.fromhex(Keys.get('aes_key_generation_source')))

		crypto = AES.new(SDKEKTrue, AES.MODE_ECB)
		SDKeySrc= bytearray(0x20)
		
		for i in range(0x20):
			SDKeySrc[i] = (sd_card_nca_key_source[i] ^ sd_seed[i & 0xF])
			
		aes = crypto.decrypt(SDKeySrc)
		SpecificKey0=aes[:0x10]
		SpecificKey1=aes[0x10:]
		
		from Crypto.Hash import HMAC, SHA256
		h = HMAC.new(SpecificKey0, digestmod=SHA256)
		ascii_rpath = bytes(r_path, 'ascii')
		h.update(ascii_rpath)
		MAC=h.hexdigest()
		MAC= bytes.fromhex(MAC)
		
		NAXKek0 = MAC[:0X10]
		NAXKek1 = MAC[0X10:]
		
		EncryptedKey0 = CRYPTED_AES_KEYS[:0X10]
		EncryptedKey1 = CRYPTED_AES_KEYS[0X10:]	
		
		crypto = AES.new(NAXKek0, AES.MODE_ECB)		
		NAXKey0 = crypto.decrypt(EncryptedKey0)
		
		crypto = AES.new(NAXKek1, AES.MODE_ECB)	
		NAXKey1 = crypto.decrypt(EncryptedKey1)
		
		HashedData=bytearray(header[:0x8]+NAXKey0+NAXKey1+header[0x28:])

		h = HMAC.new(HashedData, digestmod=SHA256)
		h.update(SpecificKey1)	
		
		calc_hash=h.hexdigest()
		calc_hash= bytes.fromhex(calc_hash)
		
		if not HEADER_HMAC == calc_hash:
			raise Exception("Invalid HMAC. IS RELATIVE PATH CORRECT?")		
			
		return	NAXKey0,NAXKey1,r_path

def get_nsx_name(dic=None,filepath=None):	
	if dic==None:
		NAXKey0,NAXKey1,r_path=get_decryption_keys(filepath)	
	elif dic!=None:
		NAXKey0=dic['NAXKey0']
		NAXKey1==dic['NAXKey1']
		r_path=dic['r_path']
		filepath=dic['filepath']		
	else: 
		return False
	nca_name=(r_path.split('/'))[-1]=(r_path.split('/'))[-1]		
	with open(filepath, 'rb') as f:	
		f.seek(0x4000)
		data=f.read()
	crypto = aes128.AESXTS(NAXKey0+NAXKey1,sector_size=0x4000)
	nca = Nca()
	nca.open(MemoryFile(crypto.decrypt(data)))
	nca.rewind()
	nca._path=nca_name
	result=nca.get_langueblock(roman=False)
	title_name=result[0]
	return title_name

def get_cnmt_data(dic=None,filepath=None):	
	if dic==None:
		NAXKey0,NAXKey1,r_path=get_decryption_keys(filepath)	
	elif dic!=None:
		NAXKey0=dic['NAXKey0']
		NAXKey1=dic['NAXKey1']
		r_path=dic['r_path']
		filepath=dic['filepath']
	else: 
		return False
	nca_name=(r_path.split('/'))[-1]=(r_path.split('/'))[-1]		
	with open(filepath, 'rb') as f:	
		f.seek(0x4000)
		data=f.read()
	crypto = aes128.AESXTS(NAXKey0+NAXKey1,sector_size=0x4000)
	nca = Nca()
	nca.open(MemoryFile(crypto.decrypt(data)))
	nca.rewind()
	nca_name=nca_name.replace('.nca','.cnmt.nca')
	nca._path=nca_name
	cnmt=io.BytesIO(nca.return_cnmt())
	cnmt_dict=cnmt_data(cnmt,nca,nca_name)
	return cnmt_dict	
	
	
def decrypt_nax0(input,output=None,ofolder=None,relative_PATH=False):
	if output==None and ofolder==None:
		raise Exception("User didn't set output")			
	NAXKey0,NAXKey1,r_path=get_decryption_keys(input,relative_PATH)		
	filename=(r_path.split('/'))[-1]
	with open(input, 'rb') as f:	
		f.seek(0x4000)
		data=f.read(0x4000)
	crypto = aes128.AESXTS(NAXKey0+NAXKey1,sector_size=0x4000)
	first_chunk=crypto.decrypt(data)
	ncaHeader = NcaHeader()
	ncaHeader.open(MemoryFile(first_chunk, Type.Crypto.XTS, uhx(Keys.get('header_key'))))
	if ncaHeader.magic not in [b'NCA3', b'NCA2']:
		raise Exception('Failed to decrypt NCA header: ' + str(self.magic))	
	else:
		sz=ncaHeader.size
		print(f'* {r_path} - Decryption Correct')
		print(f'* NCA Type is {str(ncaHeader.contentType).replace("Content.","")}')		
		print(f'* NCA TitleID is {str(ncaHeader.titleId)}')	
		print(f'* NCA size is {str(sq_tools.getSize(sz))}')					
		if not str(ncaHeader.contentType)=='Content.META':		
			print(f'* Filename is {filename}')	
		else:
			filename=filename.replace('.nca','.cnmt.nca')
	if output==None:
		output=os.path.join(ofolder,filename)
	t = tqdm(total=sz, unit='B', unit_scale=True, leave=False)
	t.write(f'\n- Decrypting to {output}')
	buffer=0x4000
	sect=0
	with open(output,'wb') as o:
		with open(input, 'rb') as f:	
			f.seek(0x4000)
			for data in iter(lambda: f.read(0x4000), ""):
				crypto = aes128.AESXTS(NAXKey0+NAXKey1,sector=sect,sector_size=0x4000)
				o.write(crypto.decrypt(data))
				o.flush()
				if not data:
					t.close()
					break
				sect+=1	

def dump_title(input_folder,output=None,ofolder=None,root_r_PATH=False):
	# if output==None and ofolder==None:
		# raise Exception("User didn't set output")	
	file_list=folder_to_list(input_folder,'all',filter='00')
	# print(file_list)
	meta_filepath,meta_filename,File_DB=return_meta_file(file_list)	
	if meta_filename==False:
		print("- Can't find a meta file")
	else:
		print(f"- Meta file is {meta_filename} in {meta_filepath}")
	title_name=None	
	for e in File_DB:
		dic=File_DB[e]
		if dic['content_type']=='Content.CONTROL':
			title_name=get_nsx_name(dic)
			break		
	cnmt_dict=get_cnmt_data(File_DB[meta_filename])
	titleid=cnmt_dict['titleid']	
	version=cnmt_dict['titleversion']		
	if title_name==None:
		import nutdb
		title_name=nutdb.get_dlcname(titleid)			
	nsx_name=f"{title_name} [{titleid}][v{version}].nsx"
	print(nsx_name)
	
def return_nca_data(file_list):
	File_DB={};meta_filename=False;meta_filepath=False
	end=len(file_list);c=1
	for filepath in file_list:
		try:
			NAXKey0,NAXKey1,r_path=get_decryption_keys(filepath)
			filename=(r_path.split('/'))[-1]
			with open(filepath, 'rb') as f:	
				f.seek(0x4000)
				data=f.read(0x4000)
			crypto = aes128.AESXTS(NAXKey0+NAXKey1,sector_size=0x4000)
			first_chunk=crypto.decrypt(data)
			ncaHeader = NcaHeader()
			ncaHeader.open(MemoryFile(first_chunk, Type.Crypto.XTS, uhx(Keys.get('header_key'))))
			# print(str(ncaHeader.contentType))
			if ncaHeader.magic not in [b'NCA3', b'NCA2']:		
				pass
			elif str(ncaHeader.contentType)=='Content.META':
				if str(ncaHeader.contentType)=='Content.META':		
					filename=filename.replace('.nca','.cnmt.nca')		
					# meta_filename=filename
					# meta_filepath=filepath
			File_DB[filename]={
				'filepath':filepath,
				'NAXKey0':NAXKey0,
				'NAXKey1':NAXKey1,
				'r_path':r_path,
				'content_type':ncaHeader.contentType,
				'titleid':ncaHeader.titleId,
				'size':ncaHeader.size,
				'titlerights':ncaHeader.rightsId,
				'crypto1':ncaHeader.getCryptoType(),
				'crypto2':ncaHeader.getCryptoType2()
				}
			print(f"{filename} - {ncaHeader.titleId} - {str(ncaHeader.contentType)} ({c}/{end})")	
			c+=1
			ncaHeader.close()	
		except:pass	
	# return meta_filepath,meta_filename,File_DB
	return File_DB	

def scrape(reg_folder):
	meta_filepaths=[]
	file_list=folder_to_list(reg_folder,'all',filter='00')
	# print(file_list)
	File_DB=return_nca_data(file_list)	
	# print(File_DB.keys())
	for e in File_DB:
		dic=File_DB[e]
		if str(dic['content_type'])=='Content.META':
			get_cnmt_data	
			cnmt_dict=get_cnmt_data(dic)			
			ncadata=cnmt_dict['ncadata']
			complete=True
			for d in ncadata:
				if d['NCAtype']=="DeltaFragment":
					continue
				ncid=d['NcaId']
				# print(f"{ncid}")
				if not (f"{str(ncid).lower()}.nca" in File_DB.keys()) and not(f"{str(ncid).lower()}.cnmt.nca" in File_DB.keys()):
					complete=False	
			print(f"{dic['titleid']} - {e} - complete:{complete}")
			