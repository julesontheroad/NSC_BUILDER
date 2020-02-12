import sq_tools
from Fs.File import MemoryFile

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
from tqdm import tqdm
from Fs.Pfs0 import Pfs0
from Fs.Ticket import Ticket
from Fs.Nca import Nca
from Fs.ChromeNca import Nca as ChromeNca
from Fs.Nacp import Nacp
from Fs.Nca import NcaHeader
from Fs.pyNCA3 import NCA3
from Fs.pyNPDM import NPDM
from Fs.BaseFs import BaseFs
from Fs.ChromeNacp import ChromeNacp
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

MEDIA_SIZE = 0x200
buffer = 65536
indent = 1
tabs = '\t' * indent

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

def file_location(filepath,t='all',name=None,Printdata=False):		
	filenames=retchunks(filepath)
	# print(filenames)
	locations=list()
	if filepath.endswith('.xc0'):
		files_list=sq_tools.ret_xci_offsets(filepath)	
	elif filepath.endswith('.ns0'):
		files_list=sq_tools.ret_nsp_offsets(filepath)		
	for file in files_list:
		if name!=None:
			if (str(file[0]).lower())==str(name).lower():		
				location1,tgoffset1=get_file_and_offset(filenames,file[1])
				location2,tgoffset2=get_file_and_offset(filenames,file[2])		
				locations.append([file[0],file[3],location1,tgoffset1,location2,tgoffset2])
				if Printdata==True:
					print('{}'.format(file[0]))		
					print('- Starts in file {} at offset {}'.format(location1[-4:],tgoffset1))
					print('- Ends in file {} at offset {}'.format(location2[-4:],tgoffset2))
					print('')			
			else:pass			
		elif not t.lower()=='all':
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
	rightsId=titleid+'000000000000000'+str(crypto2)	
	return 	titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata						

def nacp_data(nca):
	dict={}
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
	return dict							

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
		

class chunk():
	def __init__(self,filepath,type='all',locations=None,files=None,fileopen=None):
		self.maincontrol=None;self.nacpdata=None;self.cmtdata=None;self.maintitleKey=False;self.maindeckey=False
		self.firstchunk=filepath
		self.chunklist=retchunks(filepath)		
		self.cnmtfiles=file_location(filepath,t='.cnmt.nca',Printdata=False)	
		self.maincnmt=self.choosecnmt()
		self.get_cnmt_data()
		self.ctype=self.cnmtdata['ctype']
		self.maintitleid=self.cnmtdata['titleid'];self.mainbaseid=self.cnmtdata['baseid']
		self.db_get_titlekey()
		if self.ctype != 'DLC':
			self.get_main_control_nca()
			self.get_nacp_data()
		
	def choosecnmt(self):		
		file=False;titleid=False;nG=0;nU=0;nD=0;mcstring="";mGame=False
		if len(self.cnmtfiles)<2:
			return self.cnmtfiles[0]
		# for nca in self:
			# if str(nca._path) in cnmtnames:
				# if type(nca) == Nca:
					# if titleid==False:
						# file=str(nca._path)
					# titleid=str(nca.header.titleId)								
					# if str(nca.header.titleId).endswith('000'):	
						# nG+=1
					# elif str(nca.header.titleId).endswith('800'):
						# if nU==0 and nG<2:
							# file=str(nca._path)
						# nU+=1
					# else:
						# nD+=1
		# if nG>0:
			# mcstring+='{} Game'.format(str(nG))
			# if nG>1:
				# mcstring+='s'
				# mGame=True
		# if nU>0:
			# if nG>0:
				# mcstring+=', '
			# mcstring+='{} Update'.format(str(nU))	
			# if nU>1:
				# mcstring+='s'			
		# if nD>0:
			# if nG>0 or nU>0: 
				# mcstring+=', '		
			# mcstring+='{} DLC'.format(str(nD))	
			# if nD>1:
				# mcstring+='s'			
		# return file,mcstring,mGame	

	def get_cnmt_data(self):
		nca=Nca()
		nca.open(MemoryFile(self.memoryload(self.maincnmt).read()))
		nca.rewind()	
		cnmt=io.BytesIO(nca.return_cnmt())
		nca_name=self.maincnmt[0]
		titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=cnmt_data(cnmt,nca,nca_name)
		d={}
		d['titleid']=titleid;d['version']=titleversion;d['baseid']=base_ID;d['keygeneration']=keygeneration;d['rightsId']=rightsId;
		d['rsv']=RSV;d['rgv']=RGV;d['ctype']=ctype;d['metasdkversion']=metasdkversion;d['exesdkversion']=exesdkversion;
		d['hasHtmlManual']=hasHtmlManual;d['Installedsize']=Installedsize;d['DeltaSize']=DeltaSize;d['ncadata']=ncadata;
		# print(d)
		self.cnmtdata=d
		
	def read_cnmt(self):
		feed=''
		for entry in self.cnmtfiles:
			nca=Nca()
			nca.open(MemoryFile(self.memoryload(entry).read()))
			nca._path=entry[0]
			feed+=nca.read_cnmt()
		return feed				

	def send_html_cnmt_data(self):
		feed=''
		for entry in self.cnmtfiles:
			nca=ChromeNca()
			nca.open(MemoryFile(self.memoryload(entry).read()))
			nca._path=entry[0]
			feed+=nca.read_cnmt()	
		return feed	
			

	def get_main_control_nca(self):
		ncadata=self.cnmtdata['ncadata']
		for entry in ncadata:
			if str(entry['NCAtype']).lower()=='control':
				ncaname=entry['NcaId']+'.nca'
				break		
		results=file_location(self.firstchunk,name=ncaname,Printdata=False)			
		self.maincontrol=results[0]		

	def get_nacp_data(self):		
		nca=Nca()
		nca.open(MemoryFile(self.memoryload(self.maincontrol).read()))
		nca.rewind()	
		self.nacpdata=nacp_data(nca)
		nca.rewind()
		title,editor,SupLg,ctype=self.DB_get_names(nca)
		self.nacpdata['title']=title
		self.nacpdata['editor']=editor
		self.nacpdata['SupLg']=SupLg
		self.ctype=ctype
		# print(nacpdict)

	def memoryload(self,filedata):
		if filedata[2]==filedata[4]:
			with open(filedata[2], 'rb') as f:	
				f.seek(int(filedata[3]))
				inmemoryfile = io.BytesIO(f.read(int(filedata[5])-int(filedata[3])))
				return inmemoryfile
				
	def DB_get_names(self,nca):	
		ctype=self.ctype
		title,editor,ediver,SupLg,regionstr,isdemo=nca.get_langueblock('DLC',roman=True)
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
		return 	title,editor,SupLg,ctype		

	def DB_get_names_from_nutdb(self):
		titleid=self.maintitleid
		try:
			sqname,sqeditor=nutdb.get_dlcData(titleid)
			SupLg=nutdb.get_content_langue(titleid)		
			return sqname,sqeditor,SupLg
		except BaseException as e:
			Print.error('Exception: ' + str(e))	
			return "-","-","-"	

	def db_get_titlekey(self):	
		titleKey=False;deckey=False
		rightsId=self.cnmtdata['rightsId'];ticket=None
		keygeneration=self.cnmtdata['keygeneration']
		try:
			if rightsId != None and sum(rightsId)!=0:
				tkname=str(rightsId.lower)+'.tik'
				tickets=file_location(filepath,name=tkname,Printdata=False)
				# print(tickets)
				if tickets:
					ticket=tickets[0]							
					tk=Ticket()
					tk.open(MemoryFile(self.memoryload(ticket).read()))
					tk.rewind()	
					titleKey = ticket.getTitleKeyBlock()	
					titleKey=str(hx(titleKey.to_bytes(16, byteorder='big')))
					titleKey=titleKey[2:-1].upper()
					deckey = Keys.decryptTitleKey(ticket.getTitleKeyBlock().to_bytes(16, byteorder='big'), Keys.getMasterKeyIndex(int(keygeneration)))						
					deckey=(str(hx(deckey))[2:-1]).upper()	
					# print(titleKey)	
					# print(deckey)	
		except:
			pass
		self.maintitleKey=titleKey
		self.maindeckey=deckey					
				
	def getDBdict(self):
		ctype=self.ctype
		DBdict={}
		if ctype!='DLC':
			sqname=self.nacpdata['title']
			sqeditor=self.nacpdata['editor']
			SupLg=self.nacpdata['SupLg']
			nacpdict=self.nacpdata
		else:	
			sqname,sqeditor,SupLg=self.DB_get_names_from_nutdb()
	
		titlekey=self.maintitleKey
		dectkey=self.maindeckey
		
		#cnmt flags	
		DBdict['id']=self.cnmtdata['titleid']
		DBdict['baseid']=self.cnmtdata['baseid']
		DBdict['rightsId']=self.cnmtdata['rightsId']	
		DBdict['Type']=ctype					
		DBdict['version']=self.cnmtdata['version']		
		DBdict['keygeneration']=self.cnmtdata['keygeneration']			
		DBdict['RSV']=(self.cnmtdata['rsv'])[1:-1]		
		DBdict['RGV']=self.cnmtdata['rgv']			
		DBdict['metasdkversion']=self.cnmtdata['metasdkversion']	
		DBdict['exesdkversion']=self.cnmtdata['exesdkversion']
		DBdict['InstalledSize']=self.cnmtdata['Installedsize']		
		DBdict['deltasize']=self.cnmtdata['DeltaSize']		
		DBdict['HtmlManual']=self.cnmtdata['hasHtmlManual']			
		DBdict['ncasizes']=self.cnmtdata['ncadata']		
		
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
		try:
			DBdict['FWoncard']=DBmodule.FWDB.detect_xci_fw(self.firstchunk)
		except:pass	
		
		if self.firstchunk.endswith('.xc0'):
			with open(self.firstchunk, 'rb') as f:	
				f.seek(0x10D)
				gamecardSize=f.read(0x1)
				f.seek(0x118)
				validDataEndOffset=readInt64(f)
			GCFlag=(str(hx(gamecardSize))[2:-1]).upper()
			valid_data=int(((validDataEndOffset+0x1)*0x200))
			GCSize=sq_tools.getGCsizeinbytes(GCFlag)
			GCSize=int(GCSize)	
			DBdict['GCSize']=GCSize	
			DBdict['TrimmedSize']=valid_data	

		# #Check if multicontent
		content_number=len(self.cnmtfiles)
		# print(str(content_number))
		DBdict['ContentNumber']=str(content_number)
		# if mcstring !=False:
			# DBdict['ContentString']=mcstring
		if content_number!=False and content_number>1:
			if mGame==True:
				DBdict['Type']="MULTIGAME"			
			else:
				DBdict['Type']="MULTICONTENT"
			DBdict['InstalledSize']=sq_tools.get_mc_isize(self.firstchunk)
			
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
			nsuId,worldreleasedate,genretags,ratingtags,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(self.maintitleid)
			regions=nutdb.get_contenregions(self.maintitleid)
		else:
			nsuId,worldreleasedate,genretags,ratingtags,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,shopurl=nutdb.get_content_data(self.mainbaseid)
			regions=nutdb.get_contenregions(self.mainbaseid)		
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
		metascore,userscore,openscore=nutdb.get_metascores(self.maintitleid)	
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

	def send_html_nacp_data(self,gui=True):
		feed=''
		ncadata=self.cnmtdata['ncadata']
		for entry in ncadata:
			if str(entry['NCAtype']).lower()=='control':
				ncaname=entry['NcaId']+'.nca'
				results=file_location(self.firstchunk,name=ncaname,Printdata=False)			
				control=results[0]
				nca=Nca()				
				nca.open(MemoryFile(self.memoryload(control).read()))
				nca.rewind()	
				titleid2=nca.header.titleId
				feed=html_feed(feed,1,message=str('TITLEID: ' + str(titleid2).upper()))									
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
					feed=nacp.par_getParentalControl(f.readInt8('little'),feed)
					feed=nacp.par_getScreenshot(f.readInt8('little'),feed)
					feed=nacp.par_getVideoCapture(f.readInt8('little'),feed)
					feed=nacp.par_dataLossConfirmation(f.readInt8('little'),feed)
					feed=nacp.par_getPlayLogPolicy(f.readInt8('little'),feed)
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

	def send_html_adv_file_list(self):				
		contentlist=list()	
		feed=''
		for entry in self.cnmtfiles:
			nca=Nca()
			nca.open(MemoryFile(self.memoryload(entry).read()))
			nca._path=entry[0]
			nca.rewind()	
			cnmt=io.BytesIO(nca.return_cnmt())
			nca.rewind()
			cnmt.seek(0)
			titleid=readInt64(cnmt)
			titleversion = cnmt.read(0x4)
			cnmt.seek(0xE)
			offset=readInt16(cnmt)
			content_entries=readInt16(cnmt)
			meta_entries=readInt16(cnmt)
			cnmt.seek(0x20)
			original_ID=readInt64(cnmt)								
			min_sversion=readInt32(cnmt)
			length_of_emeta=readInt32(cnmt)	
			target=str(nca._path)
			content_type_cnmt=str(cnmt._path)
			content_type_cnmt=content_type_cnmt[:-22]		
			if content_type_cnmt == 'Patch':
				content_type='Update'
				reqtag='RequiredSystemVersion: '
				tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)							
				if tit_name=='DLC':
					tit_name='-'
					editor='-'									
				if isdemo == 1:
					content_type='Demo Update'
				if isdemo == 2:
					content_type='RetailInteractiveDisplay Update'									
			if content_type_cnmt == 'AddOnContent':
				content_type='DLC'
				reqtag='RequiredUpdateNumber: '
				tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
			if content_type_cnmt == 'Application':
				content_type='Game or Application'
				reqtag='RequiredSystemVersion: '	
				tit_name,editor,ediver,SupLg,regionstr,isdemo = self.inf_get_title(target,offset,content_entries,original_ID)	
				if tit_name=='DLC':
					tit_name='-'
					editor='-'									
				if isdemo == 1:
					content_type='Demo'
				if isdemo == 2:
					content_type='RetailInteractiveDisplay'														
			cnmt.seek(0x20+offset)
			titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
			titleid2 = titleid2[2:-1]
			version=str(int.from_bytes(titleversion, byteorder='little'))
			v_number=int(int(version)/65536)
			RS_number=int(min_sversion/65536)
			crypto1=nca.header.getCryptoType()
			crypto2=nca.header.getCryptoType2()	
			if crypto1 == 2:
				if crypto1 > crypto2:								
					keygen=nca.header.getCryptoType()
				else:			
					keygen=nca.header.getCryptoType2()	
			else:			
				keygen=nca.header.getCryptoType2()		
			programSDKversion,dataSDKversion=self.getsdkvertit(titleid2)									
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
			incl_Firm=DBmodule.FWDB.detect_xci_fw(self._path,False)									
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
					s1=0;s1,feed=self.print_nca_by_title(nca_name,ncatype,feed)
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
			s1=0;s1,feed=self.print_nca_by_title(nca_meta,0,feed)							
			ncasize=ncasize+s1
			size1=ncasize
			size_pr=sq_tools.getSize(ncasize)		
			feed+='</ul>'	
			feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))								
			if self.actually_has_deltas(ncalist)=="true":
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
						s1=0;s1,feed=self.print_nca_by_title(nca_name,ncatype,feed)
						ncasize=ncasize+s1
				size2=ncasize
				size_pr=sq_tools.getSize(ncasize)		
				feed+='</ul>'
				feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))
			if self.actually_has_other(titleid2,ncalist)=="true":	
				feed=html_feed(feed,2,message=('- Other types of files:'))	
				feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'	
				othersize=0;os1=0;os2=0;os3=0
				os1,feed=self.print_xml_by_title(ncalist,contentlist,feed)
				os2,feed=self.print_tac_by_title(titleid2,contentlist,feed)
				os3,feed=self.print_jpg_by_title(ncalist,contentlist,feed)
				othersize=othersize+os1+os2+os3	
				size3=othersize								
				size_pr=sq_tools.getSize(othersize)							
				feed+='</ul>'
				feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))										
		finalsize=size1+size2+size3	
		size_pr=sq_tools.getSize(finalsize)	
		feed=html_feed(feed,2,message=('FULL CONTENT TOTAL SIZE: '+size_pr))	
		self.printnonlisted(contentlist,feed)
		return feed			
																				
	def html_print_nca_by_title(self,nca_name,ncatype,feed):	
		tab="\t"
		size=0
		ncz_name=nca_name[:-1]+'z'			
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					filename = str(nca._path)				
					if type(nca) == Nca:
						if filename == nca_name:
							size=nca.header.size
							size_pr=sq_tools.getSize(size)
							content=str(nca.header.contentType)
							content=content[8:]+": "
							ncatype=sq_tools.getTypeFromCNMT(ncatype)	
							if ncatype != "Meta: ":
								message=[ncatype,str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)						
							else:
								message=[ncatype,str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)					
							return size,feed		
					elif filename == ncz_name:
						ncztype=Nca(nca)
						ncztype._path=nca._path							
						size=ncztype.header.size
						size_pr=sq_tools.getSize(size)
						content=str(ncztype.header.contentType)
						content=content[8:]+": "
						ncatype=sq_tools.getTypeFromCNMT(ncatype)	
						if ncatype != "Meta: ":
							message=[ncatype,str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)						
						else:
							message=[ncatype,str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)					
						return size,feed		
		return size,feed							
	def html_print_xml_by_title(self,ncalist,contentlist,feed):	
		tab="\t"
		size2return=0
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:		
					if file._path.endswith('.xml'):
						size=file.size
						size_pr=sq_tools.getSize(size)			
						filename =  str(file._path)	
						xml=filename[:-4]
						if xml in ncalist:
							message=['XML:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
							contentlist.append(filename)	
							size2return=size+size2return			
		return size2return,feed									
	def html_print_tac_by_title(self,titleid,contentlist,feed):		
		tab="\t"	
		size2return=0	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for ticket in nspF:			
					if type(ticket) == Ticket:
						size=ticket.size			
						size_pr=sq_tools.getSize(size)			
						filename =  str(ticket._path)
						tik=filename[:-20]
						if tik == titleid:
							message=['Ticket:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
							contentlist.append(filename)					
							size2return=size+size2return													
				for cert in nspF:						
					if cert._path.endswith('.cert'):
						size=cert.size		
						size_pr=sq_tools.getSize(size)
						filename = str(cert._path)
						cert_id =filename[:-21]
						if cert_id == titleid:
							message=['Cert:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)						
							contentlist.append(filename)					
							size2return=size+size2return
		return size2return,feed						
	def html_print_jpg_by_title(self,ncalist,contentlist,feed):	
		size2return=0
		tab="\t"
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":		
				for file in nspF:
					if file._path.endswith('.jpg'):
						size=file.size
						size_pr=sq_tools.getSize(size)			
						filename =  str(file._path)	
						jpg=filename[:32]
						if jpg in ncalist:
							message=['JPG:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
							contentlist.append(filename)					
							size2return=size+size2return
		return size2return,feed		
	def html_actually_has_deltas(self,ncalist):	
		vfragment="false"	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if type(nca) == Nca:
						if 	str(nca.header.contentType) == 'Content.DATA':
							for f in nca:
									for file in f:
										filename = str(file._path)
										if filename=="fragment":
											if 	nca._path[:-4] in ncalist:	
												vfragment="true"
												break
		return vfragment
	def html_actually_has_other(self,titleid,ncalist):
		vother="false"	
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":		
				for file in nspF:
					if file._path.endswith('.xml'):
						filename =  str(file._path)	
						xml=filename[:-4]
						if xml in ncalist:
							vother="true"	
							break		
					if type(file) == Ticket:		
						filename =  str(file._path)
						tik=filename[:-20]
						if tik == titleid:
							vother="true"	
							break																
					if file._path.endswith('.cert'):
						filename = str(file._path)
						cert_id =filename[:-21]
						if cert_id == titleid:
							vother="true"	
							break		
					if file._path.endswith('.jpg'):
						filename =  str(file._path)	
						jpg=filename[:32]
						if jpg in ncalist:
							vother="true"	
							break	
		return vother					
	def html_printnonlisted(self,contentlist,feed=''):
		tab="\t"	
		list_nonlisted="false"
		for nspF in self.hfs0:
			if str(nspF._path)=="secure":		
				for file in nspF:		
					filename =  str(file._path)
					if not filename in contentlist:
						list_nonlisted="true"
		if list_nonlisted == "true":
			feed=html_feed(feed,2,'Files not linked to content in xci:')
			totsnl=0
			for nspF in self.hfs0:
				if str(nspF._path)=="secure":		
					for file in nspF:				
						filename =  str(file._path)
						nczname= str(file._path)[:-1]+'z'
						if not filename in contentlist and not nczname in contentlist:
							totsnl=totsnl+file.size
							size_pr=sq_tools.getSize(file.size)						
							message=['OTHER:',str(filename),'Size:',size_pr];feed=html_feed(feed,4,message)
			bigtab="\t"*7
			size_pr=sq_tools.getSize(totsnl)					
			feed=html_feed(feed,5,message=('TOTAL SIZE: '+size_pr))	
		return feed		
		
def get_cnmt_files(path):
	ck=chunk(path)
	# print(ck.cnmtdata)
	# print(ck.nacpdata)	
	print(ck.maintitleKey)
	print(ck.maindeckey)	
	
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
	
def icon_info(path):
	ck=chunk(path)
	if ck.maincontrol != None:
		inmemoryfile=ck.memoryload(ck.maincontrol)
		nca=Nca()
		nca.open(MemoryFile(inmemoryfile.read()))
		nca.rewind()	
		if 	str(nca.header.contentType) == 'Content.CONTROL':
			tk=nca.header.titleKeyDec	
			checksums = list()		
			inmemoryfile.seek(0)
			nca3=NCA3(inmemoryfile,int(0),str(nca._path),tk,buffer)
			for dat in open_all_dat(nca3):
				checksum = sha1(dat.read()).digest()
				if checksum not in checksums:
					checksums.append(checksum)
					a=print_dat(dat)	
					return a
					break								
								