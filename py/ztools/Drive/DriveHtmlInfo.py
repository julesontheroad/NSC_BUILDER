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
from Fs.pyNCA3 import NCA3
from Fs.Ticket import Ticket
import nutdb
import textwrap
from secondary import clear_Screen
from python_pick import pick
from python_pick import Picker
from Interface import About
import os
import csv
import Print
import DBmodule
from Fs.ChromeNca import Nca as ChromeNca
from Fs.ChromeNacp import ChromeNacp
import nutFs
from nutFs.BaseFs import BaseFs
from nutFs.Rom import Rom

squirrel_dir=os.path.abspath(os.curdir)
NSCB_dir=os.path.abspath('../'+(os.curdir))
buffer = 65536

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

def html_feed(feed='',style=1,message=''):
	if style==1:
		feed+='<p style="font-size: 14px; justify;text-justify: inter-word;"><strong>{}</strong></p>'.format(message)
		return feed
	if style==2:
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 2vh"><strong>{}</strong></p>'.format(message)
		return feed
	if style==3:
		feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>{} </strong><span>{}</span></li>'.format(message[0],message[1])
		return feed
	if style==4:
		feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>{} </strong><span>{}. </span><strong>{} </strong><strong>{}</strong></li>'.format(message[0],message[1],message[2],message[3])
		return feed
	if style==5:
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 2vh;text-indent:5vh";><strong style="text-indent:5vh;">{}</strong></p>'.format(message)
		return feed
	if style==6:
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;";><strong>{}</strong></p>'.format(message)
		return feed
	if style==7:
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;";><strong>{}</strong>{}</p>'.format(message[0],message[1])
		return feed

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
		feed=''
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
					nca=ChromeNca()
					nca.open(MemoryFile(remote.read(buf)))
					nca.rewind()
					nca._path=nca_name
					feed+=nca.read_cnmt()
				except IOError as e:
					print(e, file=sys.stderr)
		return feed

def icon_info(path=None,TD=None,filter=None,file=None,feed='',roma=True):
	if path==None and file==None:
		return False
	if file != None:
		remote=file
		type='file'
		remote.rewind()
	elif path.startswith('http'):
		url=path
		remote=Public.location(url)
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
					nca.rewind()
					tk=nca.header.titleKeyDec
					checksums = list()
					nca.rewind()
					nca3=NCA3(io.BytesIO(nca.read()),int(0),str(nca._path),tk,buffer)
					for dat in open_all_dat(nca3):
						checksum = sha1(dat.read()).digest()
						if checksum not in checksums:
							checksums.append(checksum)
							a=print_dat(dat)
							return a
							break

def open_all_dat(nca):
	# Iterators that yields all the icon file handles inside an NCA
	for _, sec in enumerate(nca.sections):
		if sec.fs_type == 'PFS0':
			continue
		cur_file = sec.fs.first_file
		while cur_file is not None:
			if cur_file.name.endswith('.dat'):
				yield sec.fs.open(cur_file)
			cur_file = cur_file.next

def print_dat(dat):
	dat.seek(0)
	a=dat.read()
	# print(a)
	# img = Image.open(dat)
	# img.show()
	return a

def getDBdict(path=None,TD=None,filter=None,file=None,feed='',roma=True):
	if path==None and file==None:
		return False
	if file != None:
		remote=file
		type='file'
		remote.rewind()
	elif path.startswith('http'):
		url=path
		remote=Public.location(url)
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
		cnmtdata,files_list,remote=DriveTools.get_cnmt_data(file=remote)
		ctype=cnmtdata['ctype']
		DBdict={}
		if ctype!='DLC':
			nacpdata=DriveTools.nacp_data(remote,cnmtdata['ncadata'],files_list,ctype)
			sqname=nacpdata['title']
			sqeditor=nacpdata['editor']
			SupLg=nacpdata['SupLg']
			ctype=nacpdata['ctype']
			nacpdict=nacpdata
		else:
			sqname,sqeditor,SupLg=DB_get_names_from_nutdb(cnmtdata['titleid'])
		titlekey='';dectkey='';sdkversion='-'
		try:
			titlekey,dectkey=db_get_titlekey(cnmtdata,files_list,remote)
		except:
			titlekey='';dectkey=''
		if ctype!='DLC':
			ModuleId,BuildID8,BuildID16,sdkversion=DriveTools.read_buildid(file=remote,cnmtdict=cnmtdata,files_list=files_list,dectkey=dectkey)
		else:
			ModuleId='-';BuildID8='-';BuildID16='-'

		#cnmt flags
		DBdict['id']=cnmtdata['titleid']
		DBdict['baseid']=cnmtdata['baseid']
		DBdict['rightsId']=cnmtdata['rightsId']
		DBdict['Type']=ctype
		DBdict['version']=cnmtdata['version']
		DBdict['keygeneration']=cnmtdata['keygeneration']
		DBdict['RSV']=(cnmtdata['rsv'])[1:-1]
		DBdict['RGV']=cnmtdata['rgv']
		DBdict['metasdkversion']=cnmtdata['metasdkversion']
		DBdict['exesdkversion']=sdkversion
		DBdict['InstalledSize']=cnmtdata['Installedsize']
		DBdict['deltasize']=cnmtdata['DeltaSize']
		DBdict['HtmlManual']=cnmtdata['hasHtmlManual']
		DBdict['ncasizes']=cnmtdata['ncadata']
		DBdict['ModuleId']=ModuleId
		DBdict['BuildID8']=BuildID8
		DBdict['BuildID16']=BuildID16

		#nacpt flags
		if ctype != 'DLC':
			DBdict['baseName']=sqname
			DBdict['contentname']='-'
		else:
			DBdict['baseName']='-'
			DBdict['contentname']=sqname
		DBdict['editor']=sqeditor
		DBdict['languages']=SupLg
		if ctype != 'DLC':
			try:
				if nacpdict['StartupUserAccount']=='RequiredWithNetworkServiceAccountAvailable' or nacpdict['RequiredNetworkServiceLicenseOnLaunch']!='None':
					DBdict['linkedAccRequired']='True'
				else:
					DBdict['linkedAccRequired']='False'
				DBdict['dispversion']=nacpdict['BuildNumber']
				DBdict['RegionalBaseNames']=nacpdict['RegionalNames']
				DBdict['RegionalContentNames']='-'
				DBdict['RegionalEditors']=nacpdict['RegionalEditors']
				DBdict['AgeRatings']=nacpdict['AgeRatings']
				DBdict['isbn']=nacpdict['ISBN']
				DBdict['StartupUserAccount']=nacpdict['StartupUserAccount']
				DBdict['UserAccountSwitchLock']=nacpdict['UserAccountSwitchLock']
				DBdict['AddOnContentRegistrationType']=nacpdict['AddOnContentRegistrationType']
				DBdict['ctype']=nacpdict['ctype']
				DBdict['ParentalControl']=nacpdict['ParentalControl']
				DBdict['ScreenshotsEnabled']=nacpdict['ScreenshotsEnabled']
				DBdict['VideocaptureEnabled']=nacpdict['VideocaptureEnabled']
				DBdict['DataLossConfirmation']=nacpdict['dataLossConfirmation']
				DBdict['PlayLogPolicy']=nacpdict['PlayLogPolicy']
				DBdict['PresenceGroupId']=nacpdict['PresenceGroupId']
				DBdict['AddOnContentBaseId']=nacpdict['AddOnContentBaseId']
				DBdict['SaveDataOwnerId']=nacpdict['SaveDataOwnerId']
				DBdict['UserAccountSaveDataSize']=nacpdict['UserAccountSaveDataSize']
				DBdict['UserAccountSaveDataJournalSize']=nacpdict['UserAccountSaveDataJournalSize']
				DBdict['DeviceSaveDataSize']=nacpdict['DeviceSaveDataSize']
				DBdict['DeviceSaveDataJournalSize']=nacpdict['DeviceSaveDataJournalSize']
				DBdict['BcatDeliveryCacheStorageSize']=nacpdict['BcatDeliveryCacheStorageSize']
				DBdict['ApplicationErrorCodeCategory']=nacpdict['ApplicationErrorCodeCategory']
				DBdict['LocalCommunicationId']=nacpdict['LocalCommunicationId']
				DBdict['LogoType']=nacpdict['LogoType']
				DBdict['LogoHandling']=nacpdict['LogoHandling']
				DBdict['RuntimeAddOnContentInstall']=nacpdict['RuntimeAddOnContentInstall']
				DBdict['CrashReport']=nacpdict['CrashReport']
				DBdict['Hdcp']=nacpdict['Hdcp']
				DBdict['SeedForPseudoDeviceId']=nacpdict['SeedForPseudoDeviceId']
				DBdict['BcatPassphrase']=nacpdict['BcatPassphrase']
				DBdict['UserAccountSaveDataSizeMax']=nacpdict['UserAccountSaveDataSizeMax']
				DBdict['UserAccountSaveDataJournalSizeMax']=nacpdict['UserAccountSaveDataJournalSizeMax']
				DBdict['DeviceSaveDataSizeMax']=nacpdict['DeviceSaveDataSizeMax']
				DBdict['DeviceSaveDataJournalSizeMax']=nacpdict['DeviceSaveDataJournalSizeMax']
				DBdict['TemporaryStorageSize']=nacpdict['TemporaryStorageSize']
				DBdict['CacheStorageSize']=nacpdict['CacheStorageSize']
				DBdict['CacheStorageJournalSize']=nacpdict['CacheStorageJournalSize']
				DBdict['CacheStorageDataAndJournalSizeMax']=nacpdict['CacheStorageDataAndJournalSizeMax']
				DBdict['CacheStorageIndexMax']=nacpdict['CacheStorageIndexMax']
				DBdict['PlayLogQueryableApplicationId']=nacpdict['PlayLogQueryableApplicationId']
				DBdict['PlayLogQueryCapability']=nacpdict['PlayLogQueryCapability']
				DBdict['Repair']=nacpdict['Repair']
				DBdict['ProgramIndex']=nacpdict['ProgramIndex']
				DBdict['RequiredNetworkServiceLicenseOnLaunch']=nacpdict['RequiredNetworkServiceLicenseOnLaunch']
			except:pass

		#ticket flags
		if titlekey==False:
			titlekey='-'
			dectkey='-'
		DBdict['key']=titlekey
		DBdict['deckey']=dectkey

		#Distribution type flags
		if ctype=='GAME':
			DBdict['DistEshop']='-'
			DBdict['DistCard']='True'
		else:
			DBdict['DistEshop']='-'
			DBdict['DistCard']='True'

		#xci flags
		DBdict['FWoncard']='-'
		if remote.name.endswith('.xci') or  remote.name.endswith('.xcz'):
			try:
				DBdict['FWoncard']=DBmodule.FWDB.detect_xci_fw(remote,remote=True)
			except BaseException as e:
				Print.error('Exception: ' + str(e))

		if remote.name.endswith('.xci') or  remote.name.endswith('.xcz'):
			gamecardSize=remote.read_at(0x10D,0x1)
			validDataEndOffset=remote.seek(0x118)
			validDataEndOffset=readInt64(remote)
			GCFlag=(str(hx(gamecardSize))[2:-1]).upper()
			valid_data=int(((validDataEndOffset+0x1)*0x200))
			GCSize=sq_tools.getGCsizeinbytes(GCFlag)
			GCSize=int(GCSize)
			DBdict['GCSize']=GCSize
			DBdict['TrimmedSize']=valid_data

		#Check if multicontent
		content_number=0
		for i in range(len(files_list)):
			if (files_list[i][0]).endswith('cnmt.nca'):
				content_number+=1
		DBdict['ContentNumber']=str(content_number)
		maincnmt,mcstring,mGame,mcontent=db_multicontent_data(cnmtdata,files_list,remote,content_number)
		if mcstring !=False:
			DBdict['ContentString']=mcstring
		if content_number!=False and content_number>1:
			if mGame==True:
				DBdict['Type']="MULTIGAME"
			else:
				DBdict['Type']="MULTICONTENT"
			DBdict['InstalledSize']=sq_tools.get_mc_isize(files_list=files_list)

		DBdict['nsuId']='-'
		DBdict['genretags']='-'
		DBdict['ratingtags']='-'
		DBdict['worldreleasedate']='-'
		DBdict['numberOfPlayers']='-'
		DBdict['iconUrl']='-'
		DBdict['screenshots']='-'
		DBdict['bannerUrl']='-'
		DBdict['intro']='-'
		DBdict['description']='-'
		if ctype=='GAME' or ctype=='DLC' or ctype=='DEMO':
			nsuId,worldreleasedate,genretags,ratingtags,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(cnmtdata['titleid'])
			regions=nutdb.get_contenregions(cnmtdata['titleid'])
		else:
			nsuId,worldreleasedate,genretags,ratingtags,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(cnmtdata['titleid'])
			regions=nutdb.get_contenregions(cnmtdata['titleid'])
		if 	nsuId!=False:
			DBdict['nsuId']=nsuId
		if 	genretags!=False:
			DBdict['genretags']=genretags
		if 	ratingtags!=False:
			DBdict['ratingtags']=ratingtags
		if 	worldreleasedate!=False:
			DBdict['worldreleasedate']=worldreleasedate
		if 	numberOfPlayers!=False:
			DBdict['numberOfPlayers']=numberOfPlayers
		if 	iconUrl!=False:
			DBdict['iconUrl']=iconUrl
		if 	screenshots!=False:
			DBdict['screenshots']=screenshots
		if 	bannerUrl!=False:
			DBdict['bannerUrl']=bannerUrl
		if 	intro!=False:
			DBdict['intro']=intro
		if 	description!=False:
			DBdict['description']=description
		if 	rating!=False:
			DBdict['eshoprating']=rating
		if 	developer!=False:
			DBdict['developer']=developer
		if 	productCode!=False:
			DBdict['productCode']=productCode
		if 	OnlinePlay!=False:
			DBdict['OnlinePlay']=OnlinePlay
		if 	SaveDataCloud!=False:
			DBdict['SaveDataCloud']=SaveDataCloud
		if 	playmodes!=False:
			DBdict['playmodes']=playmodes
		if 	video!=False:
			DBdict['video']=video
		if 	shopurl!=False:
			DBdict['shopurl']=shopurl
		if 	len(regions)>0:
			DBdict['regions']=regions
		metascore,userscore,openscore=nutdb.get_metascores(cnmtdata['titleid'])
		DBdict['metascore']='-'
		DBdict['userscore']='-'
		DBdict['openscore']='-'
		if 	metascore!=False:
			DBdict['metascore']=metascore
		if 	userscore!=False:
			DBdict['userscore']=userscore
		if 	openscore!=False:
			DBdict['openscore']=openscore
		return DBdict

def DB_get_names_from_nutdb(titleid):
	try:
		sqname,sqeditor=nutdb.get_dlcData(titleid)
		SupLg=nutdb.get_content_langue(titleid)
		return sqname,sqeditor,SupLg
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		return "-","-","-"

def db_get_titlekey(cnmtdata,files_list,remote):
	titleKey=False;deckey=False
	rightsId=cnmtdata['rightsId'];
	keygeneration=cnmtdata['keygeneration']
	hasrights=True;tkname=None
	try:
		if int(rightsId,16)==0:
			hasrights=False
	except:pass
	try:
		if rightsId != None and hasrights==True:
			tkname=str(rightsId.lower())+'.tik'
			for i in range(len(files_list)):
				if (files_list[i][0])==tkname:
					tkname=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					sz=files_list[i][3]
					break
			remote.seek(off1,off2)
			buf=int(sz)
			tk=Ticket()
			tk.open(MemoryFile(remote.read(buf)))
			tk.rewind()
			titleKey = tk.getTitleKeyBlock()
			titleKey=str(hx(titleKey.to_bytes(16, byteorder='big')))
			titleKey=titleKey[2:-1].upper()
			deckey = Keys.decryptTitleKey(tk.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(int(keygeneration)))
			deckey=(str(hx(deckey))[2:-1]).upper()
	except BaseException as e:
		# Print.error('Exception: ' + str(e))
		pass
	return titleKey,deckey

def db_multicontent_data(cnmtdata,files_list,remote,content_number):
	file=False;titleid=False;nG=0;nU=0;nD=0;mcstring="";mGame=False;mcontent=False
	if content_number>1:
		mcontent=True
		for i in range(len(files_list)):
			if (files_list[i][0]).endswith('.cnmt.nca'):
				name=files_list[i][0]
				off1=files_list[i][1]
				off2=files_list[i][2]
				sz=files_list[i][3]
				break
		remote.seek(off1,off2)
		buf=int(sz)
		nca=Nca()
		nca.open(MemoryFile(remote.read(buf)))
		if titleid==False:
			file=name
		titleid=str(nca.header.titleId)
		if str(nca.header.titleId).endswith('000'):
			nG+=1
		elif str(nca.header.titleId).endswith('800'):
			if nU==0 and nG<2:
				file=str(nca._path)
			nU+=1
		else:
			nD+=1
	else:
		for i in range(len(files_list)):
			if (files_list[i][0]).endswith('.cnmt.nca'):
				name=files_list[i][0]
				off1=files_list[i][1]
				off2=files_list[i][2]
				sz=files_list[i][3]
				break
		file=name
		titleid=cnmtdata['titleid']
		if str(titleid).endswith('000'):
			nG+=1
		elif str(titleid).endswith('800'):
			nU+=1
		else:
			nD+=1
		mGame=False;mcontent=False
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
	return file,mcstring,mGame,mcontent

def read_nacp(path=None,TD=None,filter=None,file=None,feed='',roma=True,gui=True):
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
		count=0;feed=''
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
					# print("- Reading "+nca_name+":\n")
					nca=Nca()
					nca.open(MemoryFile(remote.read_at(off1,sz)))
					nca.rewind()
					titleid2=nca.header.titleId
					feed+=html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
					nca.rewind()
					offset=nca.get_nacp_offset()
					for f in nca:
						f.seek(offset)
						nacp = ChromeNacp()
						feed=nacp.par_getNameandPub(f.read(0x300*15),feed,gui)
						feed=html_feed(feed,2,message=str("Nacp Flags:"))
						feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
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
						feed+='</ul>'
						f.seek(offset+0x3040)
						listages=list()
						feed=html_feed(feed,2,message=str("Age Ratings:"))
						feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
						for i in range(12):
							feed=nacp.par_getRatingAge(f.readInt8('little'),i,feed)
						feed+='</ul>'
						f.seek(offset+0x3060)
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
							feed+='</ul>'
						except:
							feed+='</ul>'
							continue
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
						feed=html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
						feed=html_feed(feed,2,message=str("- Titleinfo:"))
						feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
						if content_type_cnmt != 'AddOnContent':

							message=["Name:",tit_name];feed=html_feed(feed,3,message)
							message=["Editor:",editor];feed=html_feed(feed,3,message)
							message=["Display Version:",str(ediver)];feed=html_feed(feed,3,message)
							message=["Meta SDK version:",sdkversion];feed=html_feed(feed,3,message)
							message=["Program SDK version:",programSDKversion];feed=html_feed(feed,3,message)
							suplangue=str((', '.join(SupLg)))
							message=["Supported Languages:",suplangue];feed=html_feed(feed,3,message)
							message=["Content type:",content_type];feed=html_feed(feed,3,message)
							v_number=str(v_number)
							data='{} -> {} ({})'.format(version,content_type_cnmt,v_number)
							message=["Version:",data];feed=html_feed(feed,3,message=message);
						if content_type_cnmt == 'AddOnContent':
							if tit_name != "DLC":
								message=["Name:",tit_name];feed=html_feed(feed,3,message)
								message=["Editor:",editor];feed=html_feed(feed,3,message)
							message=["Content type:","DLC"];feed=html_feed(feed,3,message)
							DLCnumb=str(titleid2)
							DLCnumb="0000000000000"+DLCnumb[-3:]
							DLCnumb=bytes.fromhex(DLCnumb)
							DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))
							DLCnumb=int(DLCnumb)
							message=["DLC number:",str(str(DLCnumb)+' -> '+"AddOnContent"+' ('+str(DLCnumb)+')')];feed=html_feed(feed,3,message)
							message=["DLC version Number:",str( version+' -> '+"Version"+' ('+str(v_number)+')')];feed=html_feed(feed,3,message)
							message=["Meta SDK version:",sdkversion];feed=html_feed(feed,3,message)
							message=["Data SDK version:",dataSDKversion];feed=html_feed(feed,3,message)
							if SupLg !='':
								suplangue=str((', '.join(SupLg)))
								message=["Supported Languages:",suplangue];feed=html_feed(feed,3,message)
						feed+='</ul>'
						feed=html_feed(feed,2,message=str("- Required Firmware:"))
						if remote.name.endswith('.xci'):
							incl_Firm=DBmodule.FWDB.detect_xci_fw(remote,doprint=False,remote=True)
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							message=["Included Firmware:",str(str(incl_Firm))];feed=html_feed(feed,3,message)
						if content_type_cnmt == 'AddOnContent':
							if v_number == 0:
								message=["Required game version:",str(str(min_sversion)+' -> '+"Application"+' ('+str(RS_number)+')')];feed=html_feed(feed,3,message)
								message=["Required game version:",str(str(min_sversion)+' -> '+"Application"+' ('+str(RS_number)+')')];feed=html_feed(feed,3,message)
							if v_number > 0:
								message=["Required game version:",str(str(min_sversion)+' -> '+"Patch"+' ('+str(RS_number)+')')];feed=html_feed(feed,3,message)
						else:
							message=[reqtag,(str(min_sversion)+" -> " +RSV_rq)];feed=html_feed(feed,3,message)
						message=['Encryption (keygeneration):',(str(keygen)+" -> " +FW_rq)];feed=html_feed(feed,3,message)
						if content_type_cnmt != 'AddOnContent':
							message=['Patchable to:',(str(MinRSV)+" -> " + RSV_rq_min)];feed=html_feed(feed,3,message)
						else:
							message=['Patchable to:',('DLC -> no RSV to patch')];feed=html_feed(feed,3,message)
						feed+='</ul>'
						ncalist = list()
						ncasize = 0
						feed=html_feed(feed,2,message=str("- Nca files (Non Deltas):"))
						feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
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
						feed+='</ul>'
						feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
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
									feed=html_feed(feed,2,message=('- Nca files (Deltas):'))
									feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
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
							feed+='</ul>'
							feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
						if actually_has_other(titleid2,ncalist,files_list)=="true":
							feed=html_feed(feed,2,message=('- Other types of files:'))
							feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
							othersize=0;os1=0;os2=0;os3=0
							os1,feed=print_xml_by_title(ncalist,contentlist,files_list,feed)
							os2,feed=print_tac_by_title(titleid2,contentlist,files_list,feed)
							os3,feed=print_jpg_by_title(ncalist,contentlist,files_list,feed)
							othersize=othersize+os1+os2+os3
							size3=othersize
							size_pr=sq_tools.getSize(othersize)
							feed+='</ul>'
							feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
				finalsize=size1+size2+size3
				size_pr=sq_tools.getSize(finalsize)
				feed=html_feed(feed,2,message=('FULL CONTENT TOTAL SIZE: '+size_pr))
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
							reqtag='RequiredSystemVersion: '
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
				message=[ncatype,str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
			else:
				message=[ncatype,str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
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
				message=['XML:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
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
				message=['Ticket:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
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
				message=['Cert:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
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
				message=['JPG:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
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
		feed=html_feed(feed,2,'Files not linked to content:')
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
				message=['OTHER:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
		size_pr=sq_tools.getSize(totsnl)
		feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
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

def read_npdm(path=None,TD=None,filter=None,file=None):
	feed=''
	sectionFilesystems=[]
	if file !=None:
		remote=file
		cnmtdict,files_list,remote=DriveTools.get_cnmt_data(file=remote)
		try:
			titlekey,dectkey=db_get_titlekey(cnmtdict,files_list,remote)
		except:
			titlekey='';dectkey=''
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
			decKey=bytes.fromhex(dectkey)
		# print(decKey)
		try:
			titleid2=ncaHeader.titleId
			feed=html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))
			feed+='<p style="font-size: 1.86vh;text-align: left;white-space: pre-line;margin-top:0.2vh;"><strong><span">'
			ncaHeader.seek(0x400)
			for i in range(4):
				hdr = ncaHeader.read(0x200)
				section = BaseFs(hdr, cryptoKey = ncaHeader.titleKeyDec)
				fs = DriveTools.GetSectionFilesystem(hdr, cryptoKey = -1)
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
							skoff1=files_list[i][1]+skoff+headerSize
							sz1=files_list[i][2]
							break
					for i in range(len(files_list)):
						if files_list[i][0] == 'main.npdm':
							skoff2=files_list[i][1]+skoff+headerSize
							remote.seek(skoff1,off2)
							sz2=files_list[i][2]
							np=remote.read(sz1+sz2)
							mem = MemoryFile(np, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = foff)
							mem.seek(sz1);
							data=mem.read(sz2)
							inmemoryfile = io.BytesIO(data)
							npdm = NPDM(inmemoryfile)
							n=npdm.__str__()
							feed+=n
							feed+='</span></strong></p>'
							return feed
				break
			return feed
		except IOError as e:
			print(e, file=sys.stderr)
			feed=html_feed(feed,2,message=str('- Error decrypting npdm'))


def verify(path=None,TD=None,filter=None,file=None):
	contentlist=list();validfiles=list();listed_files=list()
	contentlist=list();	feed='';delta = False;verdict = True
	checktik=False
	sectionFilesystems=[]
	if file !=None:
		remote=file
		cnmtdict,files_list,remote=DriveTools.get_cnmt_data(file=remote)
		try:
			titlekey,dectkey=db_get_titlekey(cnmtdict,files_list,remote)
		except:
			titlekey='';dectkey=''
	else:
		cnmtdict,files_list,remote=get_cnmt_data(path,TD,filter)
	ctype=cnmtdict['ctype']
	# for f in files_list:


	feed=self.html_feed(feed,2,message=('DECRYPTION TEST:'))
