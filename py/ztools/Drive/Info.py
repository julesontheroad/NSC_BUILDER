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
from Fs.File import MemoryFile
from hashlib import sha256,sha1
from Drive import Public
from Drive import Private
from Drive import DriveTools

import Keys
from Fs import Type
from Fs.Nacp import Nacp
from Fs.pyNPDM import NPDM
import nutdb
import textwrap
from secondary import clear_Screen
from python_pick import pick
from python_pick import Picker
from Interface import About
import os
import csv

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

remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
download_lib_file = os.path.join(zconfig_dir, 'download_libraries.txt')

def libraries(tfile):
	db={}
	try:
		with open(tfile,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')
			i=0
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
				else:
					dict_={}
					for j in range(len(csvheader)):
						try:
							if row[j]==None or row[j]=='':
								dict_[csvheader[j]]=None
							else:
								dict_[csvheader[j]]=row[j]
						except:
							dict_[csvheader[j]]=None
					db[row[0]]=dict_
		# print(db)
		return db
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		return False

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

def pick_libraries():
	title = 'Select libraries to search: '
	db=libraries(remote_lib_file)
	if db==False:
		return False,False
	options = [x for x in db.keys()]
	selected = pick(options, title,multi_select=True,min_selection_count=1)
	# print(selected)
	paths=list();TDs=list()
	for entry in selected:
		paths.append((db[entry[0]])['path'])
		try:
			TDs.append((db[entry[0]])['TD_name'])
		except:
			TDs.append(None)
	# for p in range(len(paths)):
		# print(paths[p])
		# print(TDs[p])
	return paths,TDs


def Interface():
	clear_Screen()
	About()
	response=False
	print('\n********************************************************')
	print('FILE - INFORMATION')
	print('********************************************************')
	while True:
		print('Input "1" to select folder and file via file-picker')
		if os.path.exists(remote_lib_file):
			print('Input "2" to select from libraries')
		print('')
		print('Input "0" to go back to the MAIN PROGRAM')
		print('')
		print('--- Or INPUT GDRIVE Route OR PUBLIC_LINK ---')
		print('')
		ck=input('Input your answer: ')
		if ck=="0":
			break
		elif ck=="1":
			while True:
				folder,TD=Private.folder_walker()
				print(folder)
				response=interface_file(folder,TD)
				if response==False:
					return False
		elif ck=="2" and os.path.exists(remote_lib_file):
			while True:
				paths,TDs=pick_libraries()
				if paths==False:
					return False
				response=interface_file(paths,TDs)
				if response==False:
					return False
		elif ck=="0":
			break
		elif ck.startswith('http'):
			url=ck
			response=interface_menu(url,None,True)
		elif ck.endswith('/') or ck.endswith('\\'):
			response=interface_file(ck,"pick")
		elif (ck[:-1]).endswith('.xc') or (ck[:-1]).endswith('.ns'):
			TD=Private.TD_picker(ck)
			response=interface_menu(ck,TD,True)
		if 	response==False:
			break

def interface_file(path,TD):
	if TD=="pick":
		TD=Private.TD_picker(path)
	folder=path;TeamDrive=TD
	response=False
	while True:
		filter=interface_filter(path)
		file=Private.search_folder(folder,TD=TeamDrive,pickmode="single",filter=filter)
		if file==False:
			print("Query returned no files")
			input('\nPress any key to continue...')
			clear_Screen()
			About()
			return True
		else:
			response=interface_menu(file,TeamDrive)
			if str(response)=="False":
				return response
			elif str(response)=="CHANGE":
				return True

def interface_filter(path=None):
	title = 'Add a search filter?: '
	options = ['Yes','No']
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	if response=='No':
		return None
	else:
		clear_Screen()
		About()
		if path != None:
			print("Filepath {}\n".format(str(path)))
		ck=input('INPUT SEARCH FILTER: ')
		return ck

def interface_menu(path,TD,hide_f_op=False):
	initialpath=path;initial_TD=TD
	try:
		while True:
			clear_Screen()
			About()
			newload=False
			try:
				if isinstance(path, list):
					path=path[0]
				if isinstance(TD, list):
					TD=TD[0]
			except:pass
			print('Loaded: {}'.format(path))
			print('\n********************************************************')
			print('FILE - INFORMATION')
			print('********************************************************')
			print('Input "1" to get FILE LIST of the xci/nsp')
			print('Input "2" to get GAME-INFO and FW requirements')
			print('Input "3" to READ the CNMT from the xci/nsp')
			print('Input "4" to READ the NACP from the xci/nsp')
			print('')
			print('Input "L" to SELECT another file')
			if hide_f_op==False:
				print('Input "F" to CHANGE folder')
			print('Input "0" to go back to the MAIN PROGRAM')
			print('')
			print('--- Or INPUT GDRIVE Route OR PUBLIC_LINK ---')
			print('')
			ck=input('Input your answer: ')
			clear_Screen()
			About()
			if ck=="1":
				adv_file_list(path,TD)
			elif ck=="2":
				print_fw_req(path,TD)
			elif ck=="3":
				read_cnmt(path,TD)
			elif ck=="4":
				read_nacp(path,TD)
			elif ck=="0":
				return False
			elif str(ck).upper()=="L":
				return True
			elif str(ck).upper()=="F" and hide_f_op==False:
				return "CHANGE"
			elif ck.startswith('http'):
				TD=None
				path=ck
				newload=True
			elif len(ck)>=2:
				path=ck
				TD=Private.TD_picker(path)
				remote=Private.location(route=path,TD_Name=TD)
				if remote.ID==None:
					print("\nBad filepth. File wasn't loaded")
					input(' -- Press any key to continue... --')
					path=initialpath;TD=initial_TD
				else:
					newload=True
			else:
				return False
			if newload==False:
				input('\nPress any key to continue...')
	except:pass

def read_cnmt(path=None,TD=None,filter=None,file=None):
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
		Private.folderpicker(path,TD=TD,filter=filter,mode='read_cnmt')
		return
	else:
		print("- Parsing header...")
		files_list=DriveTools.get_files_from_head(remote,remote.name)
		# print(files_list)
		for i in range(len(files_list)):
			if (files_list[i][0]).endswith('.cnmt.nca'):
				nca_name=files_list[i][0]
				off1=files_list[i][1]
				off2=files_list[i][2]
				sz=files_list[i][3]
				# print(nca_name)
				remote.seek(off1,off2)
				buf=int(sz)
				try:
					nca=Nca()
					nca.open(MemoryFile(remote.read(buf)))
					nca.rewind()
					nca._path=nca_name
					nca.read_cnmt()
				except IOError as e:
					print(e, file=sys.stderr)

def read_nacp(path=None,TD=None,filter=None,file=None,feed='',roma=True):
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
		Private.folderpicker(path,TD=TD,filter=filter,mode='read_nacp')
		return
	else:
		print("- Parsing header...")
		count=0
		files_list=DriveTools.get_files_from_head(remote,remote.name)
		for i in range(len(files_list)):
			nca_name=files_list[i][0]
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			if nca_name.endswith('.ncz') or nca_name.endswith('.nca'):
				ncaHeader = NcaHeader()
				ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
				if 	str(ncaHeader.contentType) == 'Content.CONTROL':
					if count==0:
						count+=1
					else:
						print("")
					print("- Reading "+nca_name+":\n")
					nca=Nca()
					nca.open(MemoryFile(remote.read_at(off1,sz)))
					offset=nca.get_nacp_offset()
					for f in nca:
						f.seek(offset)
						nacp = Nacp()
						feed=nacp.par_getNameandPub(f.read(0x300*15),feed,False,roma)
						message='...............................';print(message);feed+=message+'\n'
						message='NACP FLAGS';print(message);feed+=message+'\n'
						message='...............................';print(message);feed+=message+'\n'
						f.seek(offset+0x3000)
						feed=nacp.par_Isbn(f.read(0x24),feed)
						f.seek(offset+0x3025)
						feed=nacp.par_getStartupUserAccount(f.readInt8('little'),feed)
						feed=nacp.par_getUserAccountSwitchLock(f.readInt8('little'),feed)
						feed=nacp.par_getAddOnContentRegistrationType(f.readInt8('little'),feed)
						feed=nacp.par_getContentType(f.readInt8('little'),feed)
						f.seek(offset+0x3030)
						feed=nacp.par_getParentalControl(f.readInt8('little'),feed)
						f.seek(offset+0x3034)
						feed=nacp.par_getScreenshot(f.readInt8('little'),feed)
						feed=nacp.par_getVideoCapture(f.readInt8('little'),feed)
						feed=nacp.par_dataLossConfirmation(f.readInt8('little'),feed)
						feed=nacp.par_getPlayLogPolicy(f.readInt8('little'),feed)
						f.seek(offset+0x3038)
						feed=nacp.par_getPresenceGroupId(f.readInt64('little'),feed)
						f.seek(offset+0x3040)
						listages=list()
						message='...............................';print(message);feed+=message+'\n'
						message='Age Ratings';print(message);feed+=message+'\n'
						message='...............................';print(message);feed+=message+'\n'
						for i in range(12):
							feed=nacp.par_getRatingAge(f.readInt8('little'),i,feed)
						f.seek(offset+0x3060)
						message='...............................';print(message);feed+=message+'\n'
						message='NACP ATTRIBUTES';print(message);feed+=message+'\n'
						message='...............................';print(message);feed+=message+'\n'
						try:
							feed=html_feed(feed,2,message=str("Nacp Atributes:"))
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							feed=nacp.par_getDisplayVersion(f.read(0xF),feed)
							f.seek(offset+0x3070)
							feed=nacp.par_getAddOnContentBaseId(f.readInt64('little'),feed)
							f.seek(offset+0x3078)
							feed=nacp.par_getSaveDataOwnerId(f.readInt64('little'),feed)
							f.seek(offset+0x3080)
							feed=nacp.par_getUserAccountSaveDataSize(f.readInt64('little'),feed)
							f.seek(offset+0x3088)
							feed=nacp.par_getUserAccountSaveDataJournalSize(f.readInt64('little'),feed)
							f.seek(offset+0x3090)
							feed=nacp.par_getDeviceSaveDataSize(f.readInt64('little'),feed)
							f.seek(offset+0x3098)
							feed=nacp.par_getDeviceSaveDataJournalSize(f.readInt64('little'),feed)
							f.seek(offset+0x30A0)
							feed=nacp.par_getBcatDeliveryCacheStorageSize(f.readInt64('little'),feed)
							f.seek(offset+0x30A8)
							feed=nacp.par_getApplicationErrorCodeCategory(f.read(0x07),feed)
							f.seek(offset+0x30B0)
							feed=nacp.par_getLocalCommunicationId(f.readInt64('little'),feed)
							f.seek(offset+0x30F0)
							feed=nacp.par_getLogoType(f.readInt8('little'),feed)
							feed=nacp.par_getLogoHandling(f.readInt8('little'),feed)
							feed=nacp.par_getRuntimeAddOnContentInstall(f.readInt8('little'),feed)
							f.seek(offset+0x30F6)
							feed=nacp.par_getCrashReport(f.readInt8('little'),feed)
							feed=nacp.par_getHdcp(f.readInt8('little'),feed)
							feed=nacp.par_getSeedForPseudoDeviceId(f.readInt64('little'),feed)
							f.seek(offset+0x3100)
							feed=nacp.par_getBcatPassphrase(f.read(0x40),feed)
							f.seek(offset+0x3148)
							feed=nacp.par_UserAccountSaveDataSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3150)
							feed=nacp.par_UserAccountSaveDataJournalSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3158)
							feed=nacp.par_getDeviceSaveDataSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3160)
							feed=nacp.par_getDeviceSaveDataJournalSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3168)
							feed=nacp.par_getTemporaryStorageSize(f.readInt64('little'),feed)
							feed=nacp.par_getCacheStorageSize(f.readInt64('little'),feed)
							f.seek(offset+0x3178)
							feed=nacp.par_getCacheStorageJournalSize(f.readInt64('little'),feed)
							feed=nacp.par_getCacheStorageDataAndJournalSizeMax(f.readInt64('little'),feed)
							f.seek(offset+0x3188)
							feed=nacp.par_getCacheStorageIndexMax(f.readInt64('little'),feed)
							f.seek(offset+0x3188)
							feed=nacp.par_getPlayLogQueryableApplicationId(f.readInt64('little'),feed)
							f.seek(offset+0x3210)
							feed=nacp.par_getPlayLogQueryCapability(f.readInt8('little'),feed)
							feed=nacp.par_getRepair(f.readInt8('little'),feed)
							feed=nacp.par_getProgramIndex(f.readInt8('little'),feed)
							feed=nacp.par_getRequiredNetworkServiceLicenseOnLaunch(f.readInt8('little'),feed)
						except:continue
	return feed


def adv_file_list(path=None,TD=None,filter=None,file=None):
	contentlist=list()
	feed=''
	size1=0;size2=0;size3=0;
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
		Private.folderpicker(path,TD=TD,filter=filter,mode='read_nacp')
		return
	else:
		print("- Parsing header...")
		count=0
		files_list=DriveTools.get_files_from_head(remote,remote.name)
		for i in range(len(files_list)):
			nca_name=files_list[i][0]
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			if nca_name.endswith('.cnmt.nca'):
				if count==0:
					count+=1
				else:
					print("")
				print("- Reading "+nca_name+":\n")
				nca=Nca()
				nca.open(MemoryFile(remote.read_at(off1,sz)))
				nca._path=nca_name
				for f in nca:
					for cnmt in f:
						nca.rewind();f.rewind();cnmt.rewind()
						titleid=cnmt.readInt64()
						titleversion = cnmt.read(0x4)
						cnmt.rewind()
						cnmt.seek(0xE)
						offset=cnmt.readInt16()
						content_entries=cnmt.readInt16()
						meta_entries=cnmt.readInt16()
						cnmt.rewind()
						cnmt.seek(0x20)
						original_ID=cnmt.readInt64()
						min_sversion=cnmt.readInt32()
						length_of_emeta=cnmt.readInt32()
						content_type_cnmt=str(cnmt._path)
						content_type_cnmt=content_type_cnmt[:-22]
						if content_type_cnmt == 'Patch':
							content_type='Update'
							reqtag='- RequiredSystemVersion: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list)
							if tit_name=='DLC':
								tit_name='-'
								editor='-'
							if isdemo == 1:
								content_type='Demo Update'
							if isdemo == 2:
								content_type='RetailInteractiveDisplay Update'
						if content_type_cnmt == 'AddOnContent':
							content_type='DLC'
							reqtag='- RequiredUpdateNumber: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list)
						if content_type_cnmt == 'Application':
							content_type='Game or Application'
							reqtag='- RequiredSystemVersion: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list)
							if tit_name=='DLC':
								tit_name='-'
								editor='-'
							if isdemo == 1:
								content_type='Demo'
							if isdemo == 2:
								content_type='RetailInteractiveDisplay'
						cnmt.rewind()
						cnmt.seek(0x20+offset)
						titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
						titleid2 = titleid2[2:-1]
						version=str(int.from_bytes(titleversion, byteorder='little'))
						v_number=int(int(version)/65536)
						RS_number=int(min_sversion/65536)
						nca.rewind()
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto1 == 2:
							if crypto1 > crypto2:
								keygen=nca.header.getCryptoType()
							else:
								keygen=nca.header.getCryptoType2()
						else:
							keygen=nca.header.getCryptoType2()
						programSDKversion,dataSDKversion=getsdkvertit(titleid2,remote,files_list)
						nca.rewind()
						sdkversion=nca.get_sdkversion()
						MinRSV=sq_tools.getMinRSV(keygen,min_sversion)
						FW_rq=sq_tools.getFWRangeKG(keygen)
						RSV_rq=sq_tools.getFWRangeRSV(min_sversion)
						RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)
						message=('-----------------------------');print(message);feed+=message+'\n'
						message=('CONTENT ID: ' + str(titleid2));print(message);feed+=message+'\n'
						message=('-----------------------------');print(message);feed+=message+'\n'
						if content_type_cnmt != 'AddOnContent':
							message=("Titleinfo:");print(message);feed+=message+'\n'
							message=("- Name: " + tit_name);print(message);feed+=message+'\n'
							message=("- Editor: " + editor);print(message);feed+=message+'\n'
							message=("- Display Version: " + str(ediver));print(message);feed+=message+'\n'
							message=("- Meta SDK version: " + sdkversion);print(message);feed+=message+'\n'
							message=("- Program SDK version: " + programSDKversion);print(message);feed+=message+'\n'
							suplangue=str((', '.join(SupLg)))
							message=("- Supported Languages: "+suplangue);print(message);feed+=message+'\n'
							message=("- Content type: "+content_type);print(message);feed+=message+'\n'
							message=("- Version: " + version+' -> '+content_type_cnmt+' ('+str(v_number)+')');print(message);feed+=message+'\n'
						if content_type_cnmt == 'AddOnContent':
							if tit_name != "DLC":
								message=("- Name: " + tit_name);print(message);feed+=message+'\n'
								message=("- Editor: " + editor);print(message);feed+=message+'\n'
							message=("- Content type: "+"DLC");print(message);feed+=message+'\n'
							DLCnumb=str(titleid2)
							DLCnumb="0000000000000"+DLCnumb[-3:]
							DLCnumb=bytes.fromhex(DLCnumb)
							DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
							DLCnumb=int(DLCnumb)
							message=("- DLC number: "+str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')');print(message);feed+=message+'\n'
							message=("- DLC version Number: " + version+' -> '+"Version"+' ('+str(v_number)+')');print(message);feed+=message+'\n'
							message=("- Meta SDK version: " + sdkversion);print(message);feed+=message+'\n'
							message=("- Data SDK version: " + dataSDKversion);print(message);feed+=message+'\n'
							if SupLg !='':
								suplangue=str((', '.join(SupLg)))
								message=("- Supported Languages: "+suplangue);print(message);feed+=message+'\n'
						message=("\nRequired Firmware:");print(message);feed+=message+'\n'
						if content_type_cnmt == 'AddOnContent':
							if v_number == 0:
								message=("- Required game version: " + str(min_sversion)+' -> '+"Application"+' ('+str(RS_number)+')');print(message);feed+=message+'\n'
							if v_number > 0:
								message=("- Required game version: " + str(min_sversion)+' -> '+"Patch"+' ('+str(RS_number)+')');print(message);feed+=message+'\n'
						else:
							message=(reqtag + str(min_sversion)+" -> " +RSV_rq);print(message);feed+=message+'\n'
						message=('- Encryption (keygeneration): ' + str(keygen)+" -> " +FW_rq);print(message);feed+=message+'\n'
						if content_type_cnmt != 'AddOnContent':
							message=('- Patchable to: ' + str(MinRSV)+" -> " + RSV_rq_min);print(message);feed+=message+'\n'
						else:
							message=('- Patchable to: DLC -> no RSV to patch\n');print(message);feed+=message+'\n'
						ncalist = list()
						ncasize = 0
						message=('......................');print(message);feed+=message+'\n'
						message=('NCA FILES (NON DELTAS)');print(message);feed+=message+'\n'
						message=('......................');print(message);feed+=message+'\n'
						for i in range(content_entries):
							vhash = cnmt.read(0x20)
							NcaId = cnmt.read(0x10)
							size = cnmt.read(0x6)
							ncatype = cnmt.read(0x1)
							ncatype = int.from_bytes(ncatype, byteorder='little')
							unknown = cnmt.read(0x1)
							#Print.info(str(ncatype))
							if ncatype != 6:
								nca_name=str(hx(NcaId))
								nca_name=nca_name[2:-1]+'.nca'
								s1=0;s1,feed=print_nca_by_title(nca_name,ncatype,remote,files_list,feed)
								ncasize=ncasize+s1
								ncalist.append(nca_name[:-4])
								contentlist.append(nca_name)
							if ncatype == 6:
								nca_name=str(hx(NcaId))
								nca_name=nca_name[2:-1]+'.nca'
								ncalist.append(nca_name[:-4])
								contentlist.append(nca_name)
						nca_meta=str(nca._path)
						ncalist.append(nca_meta[:-4])
						contentlist.append(nca_meta)
						s1=0;s1,feed=print_nca_by_title(nca_meta,0,remote,files_list,feed)
						ncasize=ncasize+s1
						size1=ncasize
						size_pr=sq_tools.getSize(ncasize)
						bigtab="\t"*7
						message=(bigtab+"  --------------------");print(message);feed+=message+'\n'
						message=(bigtab+'  TOTAL SIZE: '+size_pr);print(message);feed+=message+'\n'
						if actually_has_deltas(ncalist,remote,files_list)=="true":
							cnmt.rewind()
							cnmt.seek(0x20+offset)
							for i in range(content_entries):
								vhash = cnmt.read(0x20)
								NcaId = cnmt.read(0x10)
								size = cnmt.read(0x6)
								ncatype = cnmt.read(0x1)
								ncatype = int.from_bytes(ncatype, byteorder='little')
								unknown = cnmt.read(0x1)
								if ncatype == 6:
									message=('......................');print(message);feed+=message+'\n'
									message=('NCA FILES (DELTAS)');print(message);feed+=message+'\n'
									message=('......................');print(message);feed+=message+'\n'
									break
							cnmt.rewind()
							cnmt.seek(0x20+offset)
							ncasize = 0
							for i in range(content_entries):
								vhash = cnmt.read(0x20)
								NcaId = cnmt.read(0x10)
								size = cnmt.read(0x6)
								ncatype = cnmt.read(0x1)
								ncatype = int.from_bytes(ncatype, byteorder='little')
								unknown = cnmt.read(0x1)
								if ncatype == 6:
									nca_name=str(hx(NcaId))
									nca_name=nca_name[2:-1]+'.nca'
									s1=0;s1,feed=print_nca_by_title(nca_name,ncatype,remote,files_list,feed)
									ncasize=ncasize+s1
							size2=ncasize
							size_pr=sq_tools.getSize(ncasize)
							bigtab="\t"*7
							message=(bigtab+"  --------------------");print(message);feed+=message+'\n'
							message=(bigtab+'  TOTAL SIZE: '+size_pr);print(message);feed+=message+'\n'
						if actually_has_other(titleid2,ncalist,files_list)=="true":
							message=('......................');print(message);feed+=message+'\n'
							message=('OTHER TYPES OF FILES');print(message);feed+=message+'\n'
							message=('......................');print(message);feed+=message+'\n'
							othersize=0;os1=0;os2=0;os3=0
							os1,feed=print_xml_by_title(ncalist,contentlist,files_list,feed)
							os2,feed=print_tac_by_title(titleid2,contentlist,files_list,feed)
							os3,feed=print_jpg_by_title(ncalist,contentlist,files_list,feed)
							othersize=othersize+os1+os2+os3
							size3=othersize
							size_pr=sq_tools.getSize(othersize)
							bigtab="\t"*7
							message=(bigtab+"  --------------------");print(message);feed+=message+'\n'
							message=(bigtab+'  TOTAL SIZE: '+size_pr);print(message);feed+=message+'\n'
				finalsize=size1+size2+size3
				size_pr=sq_tools.getSize(finalsize)
				message=("/////////////////////////////////////");print(message);feed+=message+'\n'
				message=('   FULL CONTENT TOTAL SIZE: '+size_pr+"   ");print(message);feed+=message+'\n'
				message=("/////////////////////////////////////");print(message);feed+=message+'\n'
	printnonlisted(contentlist,files_list,feed)
	return feed

def print_fw_req(path=None,TD=None,filter=None,file=None,trans=True,roma=True):
	feed=''
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
		Private.folderpicker(path,TD=TD,filter=filter,mode='read_nacp')
		return
	else:
		print("- Parsing header...")
		count=0
		files_list=DriveTools.get_files_from_head(remote,remote.name)
		for i in range(len(files_list)):
			nca_name=files_list[i][0]
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			if nca_name.endswith('.cnmt.nca'):
				if count==0:
					count+=1
				else:
					print("")
				print("- Reading "+nca_name+":\n")
				nca=Nca()
				nca.open(MemoryFile(remote.read_at(off1,sz)))
				nca._path=nca_name
				for f in nca:
					for cnmt in f:
						nca.rewind();f.rewind();cnmt.rewind()
						titleid=cnmt.readInt64()
						titleversion = cnmt.read(0x4)
						cnmt.rewind()
						cnmt.seek(0xE)
						offset=cnmt.readInt16()
						content_entries=cnmt.readInt16()
						meta_entries=cnmt.readInt16()
						cnmt.rewind()
						cnmt.seek(0x20)
						original_ID=cnmt.readInt64()
						RSversion=cnmt.readInt32()
						Emeta=cnmt.readInt32()
						content_type_cnmt=str(cnmt._path)
						content_type_cnmt=content_type_cnmt[:-22]
						if content_type_cnmt == 'Patch':
							content_type='Update'
							reqtag='- RequiredSystemVersion: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list,roman=roma)
							if tit_name=='DLC':
								tit_name='-'
								editor='-'
							if isdemo == 1:
								content_type='Demo Update'
							if isdemo == 2:
								content_type='RetailInteractiveDisplay Update'
						if content_type_cnmt == 'AddOnContent':
							content_type='DLC'
							reqtag='- RequiredUpdateNumber: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list,roman=roma)
						if content_type_cnmt == 'Application':
							content_type='Base Game or Application'
							reqtag='- RequiredSystemVersion: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list,roman=roma)
							if tit_name=='DLC':
								tit_name='-'
								editor='-'
							if isdemo == 1:
								content_type='Demo'
							if isdemo == 2:
								content_type='RetailInteractiveDisplay'
						cnmt.rewind()
						cnmt.seek(0x20+offset)
						titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
						titleid2 = titleid2[2:-1]
						version=str(int.from_bytes(titleversion, byteorder='little'))
						v_number=int(int(version)/65536)
						RS_number=int(RSversion/65536)
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto1 == 2:
							if crypto1 > crypto2:
								keygen=nca.header.getCryptoType()
							else:
								keygen=nca.header.getCryptoType2()
						else:
							keygen=nca.header.getCryptoType2()
						MinRSV=sq_tools.getMinRSV(keygen,RSversion)
						FW_rq=sq_tools.getFWRangeKG(keygen)
						RSV_rq=sq_tools.getFWRangeRSV(RSversion)
						RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)
						content_type_cnmt=str(cnmt._path)
						content_type_cnmt=content_type_cnmt[:-22]
						if content_type_cnmt == 'Patch':
							content_type='Update'
							reqtag='- RequiredSystemVersion: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list)
							if tit_name=='DLC':
								tit_name='-'
								editor='-'
							if isdemo == 1:
								content_type='Demo Update'
							if isdemo == 2:
								content_type='RetailInteractiveDisplay Update'
						if content_type_cnmt == 'AddOnContent':
							content_type='DLC'
							reqtag='- RequiredUpdateNumber: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list)
						if content_type_cnmt == 'Application':
							content_type='Base Game or Application'
							reqtag='- RequiredSystemVersion: '
							tit_name,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(nca,offset,content_entries,original_ID,remote,files_list)
							if tit_name=='DLC':
								tit_name='-'
								editor='-'
							if isdemo == 1:
								content_type='Demo'
							if isdemo == 2:
								content_type='RetailInteractiveDisplay'
						programSDKversion,dataSDKversion=getsdkvertit(titleid2,remote,files_list)
						nsuId,releaseDate,category,ratingContent,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(titleid2,trans)
						sdkversion=nca.get_sdkversion()
						message=('-----------------------------');print(message);feed+=message+'\n'
						message=('CONTENT ID: ' + str(titleid2));print(message);feed+=message+'\n'
						message=('-----------------------------');print(message);feed+=message+'\n'
						if content_type_cnmt != 'AddOnContent':
							message=("Titleinfo:");print(message);feed+=message+'\n'
							message=("- Name: " + tit_name);print(message);feed+=message+'\n'
							message=("- Editor: " + editor);print(message);feed+=message+'\n'
							message=("- Display Version: " + str(ediver));print(message);feed+=message+'\n'
							message=("- Meta SDK version: " + sdkversion);print(message);feed+=message+'\n'
							message=("- Program SDK version: " + programSDKversion);print(message);feed+=message+'\n'
							suplangue=str((', '.join(SupLg)))
							message=("- Supported Languages: "+suplangue);
							par = textwrap.dedent(message).strip()
							message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
							message=("- Content type: "+content_type);print(message);feed+=message+'\n'
							message=("- Version: " + version+' -> '+content_type_cnmt+' ('+str(v_number)+')');print(message);feed+=message+'\n'
						if content_type_cnmt == 'AddOnContent':
							nsuId=nutdb.get_dlcnsuId(titleid2)
							message=("Titleinfo:");print(message);feed+=message+'\n'
							if tit_name != "DLC":
								message=("- Name: " + tit_name);print(message);feed+=message+'\n'
								message=("- Editor: " + editor);print(message);feed+=message+'\n'
							message=("- Content type: "+"DLC");print(message);feed+=message+'\n'
							DLCnumb=str(titleid2)
							DLCnumb="0000000000000"+DLCnumb[-3:]
							DLCnumb=bytes.fromhex(DLCnumb)
							DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
							DLCnumb=int(DLCnumb)
							message=("- DLC number: "+str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')');print(message);feed+=message+'\n'
							message=("- DLC version Number: " + version+' -> '+"Version"+' ('+str(v_number)+')');print(message);feed+=message+'\n'
							message=("- Meta SDK version: " + sdkversion);print(message);feed+=message+'\n'
							message=("- Data SDK version: " + dataSDKversion);print(message);feed+=message+'\n'
							if SupLg !='':
								suplangue=str((', '.join(SupLg)))
								message=("- Supported Languages: "+suplangue);
								par = textwrap.dedent(message).strip()
								message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
						message=("\nRequired Firmware:");print(message);feed+=message+'\n'
						if content_type_cnmt == 'AddOnContent':
							if v_number == 0:
								message=("- Required game version: " + str(RSversion)+' -> '+"Application"+' ('+str(RS_number)+')');print(message);feed+=message+'\n'
							if v_number > 0:
								message=("- Required game version: " + str(RSversion)+' -> '+"Patch"+' ('+str(RS_number)+')');print(message);feed+=message+'\n'
						else:
							message=(reqtag + str(RSversion)+" -> " +RSV_rq);print(message);feed+=message+'\n'
						message=('- Encryption (keygeneration): ' + str(keygen)+" -> " +FW_rq);print(message);feed+=message+'\n'
						if content_type_cnmt != 'AddOnContent':
							message=('- Patchable to: ' + str(MinRSV)+" -> " + RSV_rq_min+'\n');print(message);feed+=message+'\n'
						else:
							message=('- Patchable to: DLC -> no RSV to patch\n');print(message);feed+=message+'\n'
						# try:
							# if content_type_cnmt != 'AddOnContent' and not str(remote.name).endswith('.nsz'):
								# message=('ExeFS Data:');print(message);feed+=message+'\n'
								# ModuleId,BuildID8,BuildID16=self.read_buildid()
								# message=('- BuildID8: '+ BuildID8);print(message);feed+=message+'\n'
								# message=('- BuildID:  '+ sq_tools.trimm_module_id(ModuleId));print(message);feed+=message+'\n'
						# except:pass
						if nsuId!=False or numberOfPlayers!=False or releaseDate!=False or category!=False or ratingContent!=False:
							message=('Eshop Data:');print(message);feed+=message+'\n'
						if nsuId!=False:
							message=("- nsuId: " + nsuId);print(message);feed+=message+'\n'
						if region!=False:
							message=('- Data from Region: ' + region);print(message);feed+=message+'\n'
						if numberOfPlayers!=False:
							message=("- Number of Players: " + numberOfPlayers);print(message);feed+=message+'\n'
						if releaseDate!=False:
							message=("- Release Date: " + releaseDate);print(message);feed+=message+'\n'
						if category!=False:
							category=str((', '.join(category)))
							message=("- Genres: " + category);
							par = textwrap.dedent(message).strip()
							message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
						if rating!=False:
							message=("- AgeRating: " + rating);print(message);feed+=message+'\n'
						if ratingContent!=False:
							ratingContent=str((', '.join(ratingContent)))
							message=("- Rating tags: " + ratingContent);
							par = textwrap.dedent(message).strip()
							message=(textwrap.fill(par,width=80,initial_indent='', subsequent_indent='  ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
						if intro!=False or description!=False:
							message=('\nDescription:');print(message);feed+=message+'\n'
						if intro!=False:
							par = textwrap.dedent(intro).strip().upper()
							message=('-----------------------------------------------------------------------------');print(message);feed+=message+'\n'
							message=(textwrap.fill(par,width=80,initial_indent=' ', subsequent_indent=' ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
							message=('-----------------------------------------------------------------------------');print(message);feed+=message+'\n'
						if description!=False:
							if "•" in description:
								data=description.split("• ")
								token='• '
							elif "★" in description:
								data=description.split("★ ")
								token='* '
							elif "*" in description:
								data=description.split("* ")
								token='* '
							elif "■" in description:
								data=description.split("* ")
								token='• '
							elif "●" in description:
								data=description.split("● ")
								token='• '
							elif "-" in description:
								data=description.split("- ")
								token='- '
							else:
								data=description.split("  ")
								token=''
							i=0
							for d in data:
								if i>0:
									d=token+d
								i+=1
								par = textwrap.dedent(d).strip()
								message=(textwrap.fill(par,width=80,initial_indent=' ', subsequent_indent=' ',replace_whitespace=True,fix_sentence_endings=True));print(message);feed+=message+'\n'
	return feed

def inf_get_title(cnmt_nca,offset,content_entries,original_ID,remote,files_list,roman=True):
	content_type=''
	cnmt_nca.rewind()
	for f in cnmt_nca:
		for cnmt in f:
			cnmt_nca.rewind()
			f.rewind()
			cnmt.rewind()
			titleid=cnmt.readInt64()
			titleid2 = str(hx(titleid.to_bytes(8, byteorder='big')))
			titleid2 = titleid2[2:-1]
			cnmt.rewind()
			cnmt.seek(0x20+offset)
			nca_name='false'
			for i in range(content_entries):
				vhash = cnmt.read(0x20)
				NcaId = cnmt.read(0x10)
				size = cnmt.read(0x6)
				ncatype = cnmt.read(0x1)
				unknown = cnmt.read(0x1)
				ncatype2 = int.from_bytes(ncatype, byteorder='little')
				if ncatype2 == 3:
					nca_name=str(hx(NcaId))
					nca_name=nca_name[2:-1]+'.nca'
	if nca_name=='false':
		title = 'DLC'
		title,editor=nutdb.get_dlcData(titleid2)
		if editor==False:
			editor=""
		if title==False:
			title = 'DLC'
		else:
			SupLg=nutdb.get_content_langue(titleid2)
			if SupLg==False:
				SupLg=""
			#return(title,editor,ediver,SupLg,regionstr,isdemo)
			regionstr="0|0|0|0|0|0|0|0|0|0|0|0|0|0"
			return(title,editor,"",SupLg,regionstr,"")
	if nca_name=='false' and title == 'DLC'	:
		cnmt_nca.rewind()
		for f in cnmt_nca:
			for cnmt in f:
				cnmt.rewind()
				testID=cnmt.readInt64()
				if 	testID == original_ID:
					cnmt_nca.rewind()
					f.rewind()
					titleid=cnmt.readInt64()
					titleversion = cnmt.read(0x4)
					cnmt.rewind()
					cnmt.seek(0xE)
					offset=cnmt.readInt16()
					content_entries=cnmt.readInt16()
					meta_entries=cnmt.readInt16()
					cnmt.rewind()
					cnmt.seek(0x20)
					original_ID=cnmt.readInt64()
					min_sversion=cnmt.readInt32()
					end_of_emeta=cnmt.readInt32()
					contentname,editor,ediver,SupLg,regionstr,isdemo = inf_get_title(cnmt_nca,offset,content_entries,original_ID,remote,files_list)
					DLCnumb=str(titleid2)
					DLCnumb="0000000000000"+DLCnumb[-3:]
					DLCnumb=bytes.fromhex(DLCnumb)
					DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
					DLCnumb=int(DLCnumb)
					name = contentname+' '+'['+str(DLCnumb)+']'
					return name,editor,"","",regionstr,""
	title = 'DLC'
	for i in range(len(files_list)):
		file_name=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if nca_name == file_name:
			nca=Nca()
			nca.open(MemoryFile(remote.read_at(off1,sz)))
			nca._path=nca_name
			title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock(title,roman)
			return(title,editor,ediver,SupLg,regionstr,isdemo)
	regionstr="0|0|0|0|0|0|0|0|0|0|0|0|0|0"
	return(title,"","","",regionstr,"")

def print_nca_by_title(nca_name,ncatype,remote,files_list,feed=''):
	tab="\t";
	size=0
	ncz_name=nca_name[:-1]+'z'
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename == nca_name or filename == ncz_name:
			ncaHeader = NcaHeader()
			ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
			ncaHeader.rewind()
			size=ncaHeader.size
			size_pr=sq_tools.getSize(size)
			content=str(ncaHeader.contentType)
			content=content[8:]+": "
			ncatype=sq_tools.getTypeFromCNMT(ncatype)
			if ncatype != "Meta: ":
				message=("- "+ncatype+tab+str(filename)+tab+tab+"Size: "+size_pr);print(message);feed+=message+'\n'
			else:
				message=("- "+ncatype+tab+str(filename)+tab+"Size: "+size_pr);print(message);feed+=message+'\n'
			return size,feed
	return size,feed

def actually_has_deltas(ncalist,remote,files_list):
	vfragment="false"
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename.endswith('.nca'):
			ncaHeader = NcaHeader()
			ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
			ncaHeader.rewind()
			if 	str(ncaHeader.contentType) == 'Content.DATA':
				if 	filename in ncalist:
					vfragment="true"
					break
	return vfragment

def actually_has_other(titleid,ncalist,files_list):
	vother="false"
	for i in range(len(files_list)):
		filename=files_list[i][0]
		if filename.endswith('.xml'):
			xml=filename[:-4]
			if xml in ncalist:
				vother="true"
				break
		if filename.endswith('.tik'):
			tik=filename[:-20]
			if tik == titleid:
				vother="true"
				break
		if filename.endswith('.cert'):
			cert_id =filename[:-21]
			if cert_id == titleid:
				vother="true"
				break
		if filename.endswith('.jpg'):
			jpg=filename[:32]
			if jpg in ncalist:
				vother="true"
				break
	return vother

def print_xml_by_title(ncalist,contentlist,files_list,feed=''):
	tab="\t";
	size2return=0
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename.endswith('.xml'):
			size=sz
			size_pr=sq_tools.getSize(size)
			xml=filename[:-4]
			if xml in ncalist:
				message=("- XML: "+tab*2+str(filename)+tab+"Size: "+size_pr);print(message);feed+=message+'\n'
				contentlist.append(filename)
				size2return=size+size2return
	return size2return,feed

def print_tac_by_title(titleid,contentlist,files_list,feed=''):
	tab="\t";
	size2return=0
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename.endswith('.tik'):
			size=sz
			size_pr=sq_tools.getSize(size)
			tik=filename[:-20]
			if tik == titleid:
				message=("- Ticket: "+tab+str(filename)+tab*2+"Size: "+size_pr);print(message);feed+=message+'\n'
				contentlist.append(filename)
				size2return=size+size2return
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename.endswith('.cert'):
			size=sz
			size_pr=sq_tools.getSize(size)
			cert_id =filename[:-21]
			if cert_id == titleid:
				message=("- Cert: "+tab+str(filename)+tab*2+"Size: "+size_pr);print(message);feed+=message+'\n'
				contentlist.append(filename)
				size2return=size+size2return
	return size2return,feed

def print_jpg_by_title(ncalist,contentlist,files_list,feed=''):
	size2return=0
	tab="\t";
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename.endswith('.jpg'):
			size=sz
			size_pr=sq_tools.getSize(size)
			jpg=filename[:32]
			if jpg in ncalist:
				message=("- JPG: "+tab*2+"..."+str(filename[-38:])+tab+"Size: "+size_pr);print(message);feed+=message+'\n'
				contentlist.append(filename)
				size2return=size+size2return
		return size2return,feed

def printnonlisted(contentlist,files_list,feed=''):
	tab="\t";
	list_nonlisted="false"
	for i in range(len(files_list)):
		filename=files_list[i][0]
		if not filename in contentlist:
			list_nonlisted="true"
	if list_nonlisted == "true":
		message=('-----------------------------------');print(message);feed+=message+'\n'
		message=('FILES NOT LINKED TO CONTENT IN NSP');print(message);feed+=message+'\n'
		message=('-----------------------------------');print(message);feed+=message+'\n'
		totsnl=0
		for i in range(len(files_list)):
			filename=files_list[i][0]
			off1=files_list[i][1]
			off2=files_list[i][2]
			sz=files_list[i][3]
			nczname= str(filename)[:-1]+'z'
			if not filename in contentlist and not nczname in contentlist:
				totsnl=totsnl+sz
				size_pr=sq_tools.getSize(sz)
				message=(str(filename)+3*tab+"Size: "+size_pr);print(message);feed+=message+'\n'
		bigtab="\t"*7
		size_pr=sq_tools.getSize(totsnl)
		message=(bigtab+"  --------------------");print(message);feed+=message+'\n'
		message=(bigtab+'  TOTAL SIZE: '+size_pr);print(message);feed+=message+'\n'
	return feed

def getsdkvertit(titid,remote,files_list):
	programSDKversion=''
	controlSDKversion=''
	dataSDKversion=''
	for i in range(len(files_list)):
		filename=files_list[i][0]
		off1=files_list[i][1]
		off2=files_list[i][2]
		sz=files_list[i][3]
		if filename.endswith('.nca') or filename.endswith('.ncz'):
			ncaHeader = NcaHeader()
			ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), Type.Crypto.XTS, uhx(Keys.get('header_key'))))
			ncaHeader.rewind()
			nca_id=ncaHeader.titleId
			if str(titid[:-3]).upper() == str(nca_id[:-3]).upper():
				if 	str(ncaHeader.contentType) == 'Content.PROGRAM':
					programSDKversion=str(ncaHeader.sdkVersion4)+'.'+str(ncaHeader.sdkVersion3)+'.'+str(ncaHeader.sdkVersion2)+'.'+str(ncaHeader.sdkVersion1)
					break
				elif str(ncaHeader.contentType) == 'Content.CONTROL' and controlSDKversion=='':
					controlSDKversion=str(ncaHeader.sdkVersion4)+'.'+str(ncaHeader.sdkVersion3)+'.'+str(ncaHeader.sdkVersion2)+'.'+str(ncaHeader.sdkVersion1)
				elif str(ncaHeader.contentType) == 'Content.PUBLIC_DATA' and dataSDKversion=='':
					dataSDKversion=str(ncaHeader.sdkVersion4)+'.'+str(ncaHeader.sdkVersion3)+'.'+str(ncaHeader.sdkVersion2)+'.'+str(ncaHeader.sdkVersion1)
	if 	programSDKversion=='':
		programSDKversion=controlSDKversion
	return 	programSDKversion,dataSDKversion
