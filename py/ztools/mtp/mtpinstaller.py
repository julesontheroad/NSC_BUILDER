import Print
import os
import shutil
import json
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
import sq_tools
from Fs import factory
from binascii import hexlify as hx, unhexlify as uhx
import sys
import subprocess
from mtp.wpd import is_switch_connected
import listmanager
import csv
import copy
from colorama import Fore, Back, Style
from python_pick import pick
from python_pick import Picker
from secondary import clear_Screen

def check_connection():
	if not is_switch_connected():
		sys.exit("Switch device isn't connected.\nCheck if mtp responder is running!!!")	
	
bucketsize = 81920

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
bin_folder=os.path.join(ztools_dir, 'bin')
nscb_mtp=os.path.join(bin_folder, 'nscb_mtp.exe')
cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
if not os.path.exists(cachefolder):
	os.makedirs(cachefolder)
games_installed_cache=os.path.join(cachefolder, 'games_installed.txt')
mtp_source_lib=os.path.join(zconfig_dir,'mtp_source_libraries.txt')
mtp_internal_lib=os.path.join(zconfig_dir,'mtp_SD_libraries.txt')
storage_info=os.path.join(cachefolder, 'storage.csv')
xci_locations=os.path.join(zconfig_dir, 'mtp_xci_locations.txt')

def About():	
	print('                                       __          _ __    __                         ')
	print('                 ____  _____ ____     / /_  __  __(_) /___/ /__  _____                ')
	print('                / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/                ')
	print('               / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /                    ')
	print('              /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/                     ')
	print('                             /_____/                                                  ')
	print('------------------------------------------------------------------------------------- ')
	print('                        NINTENDO SWITCH CLEANER AND BUILDER                           ')
	print('------------------------------------------------------------------------------------- ')
	print('=============================     BY JULESONTHEROAD     ============================= ')
	print('------------------------------------------------------------------------------------- ')
	print('"                                POWERED BY SQUIRREL                                " ')
	print('"                    BASED ON THE WORK OF BLAWAR AND LUCA FRAGA                     " ')
	print('------------------------------------------------------------------------------------- ')                   
	print("Program's github: https://github.com/julesontheroad/NSC_BUILDER                       ")
	print('Cheats and Eshop information from nutdb and http://tinfoil.io                         ')
	print('------------------------------------------------------------------------------------- ')	

#One CJK character is 2 English characters wide when printed
def display_len(s:str):
	cnt=0
	for c in s:
		if len(c.encode('utf-8'))>=3: # CJK character take >=3 bytes in utf-8 
			cnt+=2
		else:
			cnt+=1
	return cnt

def pretty_str(name:str,name_length=40):
	g0=copy.copy(name)
	if display_len(g0)>name_length+3:
		cnt=0
		short_g0=''
		for i in range(len(g0)):
			if cnt+display_len(g0[i])<=name_length:
				cnt+=display_len(g0[i])
				short_g0+=g0[i]
			else:
				break
		g0=short_g0
		if cnt<name_length:
			g0+=' '
		g0+='...'	
	else:
		g0=g0+((name_length+3-display_len(g0))*' ')
	return g0

def search_with_filter(folder_paths,mode='installer'):
	if mode=='installer':
		extlist=['nsp','nsz','xci','xcz']
	else:
		extlist='all'
	filepaths=[]
	title = 'Add a search filter?: '
	options = ['Yes','No']	
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	if response=='No':
		for fo in folder_paths:
			rlist=listmanager.folder_to_list(fo,extlist)
			filepaths=[*filepaths,*rlist]
		return filepaths
	else:
		clear_Screen()
		About()
		ck=input('INPUT SEARCH FILTER: ')
		for fo in folder_paths:
			rlist=listmanager.folder_to_list(fo,extlist,ck)
			filepaths=[*filepaths,*rlist]		
		return filepaths
		
def pick_order():
	title = 'Select order to list the files: \n + Press enter or intro to select \n + Press E to scape back to menu'
	options = ['name_ascending','name_descending','size_ascending','size_descending','date_ascending','date_descending']
	picker = Picker(options, title, min_selection_count=1)	
	def end_selection(picker):
		return False,-1	
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)		
	selected = picker.start()	
	if selected[0]==False:
		return False
	order=selected[0]
	return order			

def select_from_local_libraries(tfile,mode='installer'):	
	if not os.path.exists(mtp_source_lib):
		sys.exit("mtp_source_libraries.txt")
	db=get_libs("source")
	title = 'Select libraries to search:  \n + Press space or right to select content \n + Press E to finish selection \n + Press A to select all libraries'
	folder_paths= []
	options=[]
	for k in db:
		options.append(k)
	picker = Picker(options, title,multi_select=True,min_selection_count=1)	
	def end_selection(picker):
		return False,-1	
	def select_all(picker):
		return True,options
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)	
	picker.register_custom_handler(ord('a'),  select_all)
	picker.register_custom_handler(ord('A'),  select_all)	
	selected = picker.start()	
	if selected[0]==False:
		print("User didn't select any libraries")
		return False,False		
	if selected[0]==True:	
		for k in db.keys():
			folder_paths.append((db[k])[0])
	else:
		for entry in selected:
			folder_paths.append((db[entry[0]])[0])
	order=pick_order()
	if order==False:
		return False				
	filepaths=search_with_filter(folder_paths,mode)
	filedata={}
	for file in filepaths:
		try:
			fname=os.path.basename(file)
			fsize=os.path.getsize(file)
			fdate=os.path.getctime(file)
			entry={'filepath':file,'filename':fname,'size':fsize,'date':fdate}
			if not fname in filedata:
				filedata[fname]=entry
		except:pass		
	options=[]	
	if order=='name_ascending':
		options=sorted(filedata,key=lambda x:filedata[x]['filename'])
	elif order=='name_descending':	
		options=sorted(filedata,key=lambda x:filedata[x]['filename'])
		options.reverse()
	elif order=='size_ascending':
		options=sorted(filedata,key=lambda x:filedata[x]['size'])
	elif order=='size_descending':	
		options=sorted(filedata,key=lambda x:filedata[x]['size'])
		options.reverse()	
	elif order=='date_ascending':
		options=sorted(filedata,key=lambda x:filedata[x]['date'])
	elif order=='date_descending':	
		options=sorted(filedata,key=lambda x:filedata[x]['date'])
		options.reverse()	
	print("  * Entering File Picker")	
	title = 'Select content to install or transfer: \n + Press space or right to select content \n + Press E to finish selection'
	picker = Picker(options, title, multi_select=True, min_selection_count=1)
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection);picker.register_custom_handler(ord('E'),  end_selection)
	selected=picker.start()
	if selected[0]==False:
		print("    User didn't select any files")
		return False
	with open(tfile,'a') as  textfile:		
		for f in selected:
			fpath=(filedata[f[0]])['filepath']		
			textfile.write(fpath+'\n')

def file_verification(filename,hash=False):
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)
	tempfolder=os.path.join(cachefolder, 'temp')	
	if not os.path.exists(tempfolder):
		os.makedirs(tempfolder)	
	verdict=False;isrestored=False;cnmt_is_patched=False
	if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz') or filename.endswith('.xcz') or filename.endswith('.xci'):
		try:
			if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz'):		
				f = squirrelNSP(filename, 'rb')
			elif filename.endswith('.xci') or filename.endswith('.xcz'):	
				f = factory(filename)		
				f.open(filename, 'rb')	
			check,feed=f.verify()
			if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz'):					
				verdict,headerlist,feed=f.verify_sig(feed,tempfolder,cnmt='nocheck')
			else:
				verdict,headerlist,feed=f.verify_sig(feed,tempfolder)
			output_type='nsp';multi=False;cnmtcount=0
			if verdict == True:
				isrestored=True
				for i in range(len(headerlist)):
					entry=headerlist[i]
					if str(entry[0]).endswith('.cnmt.nca'):
						cnmtcount+=1
						if cnmt_is_patched==False:
							status=entry[2]
							if status=='patched':
								cnmt_is_patched=True
					if entry[1]!=False:
						if int(entry[-1])==1:
							output_type='xci'
						isrestored=False	
					else:
						pass
				if	isrestored == False:	
					if cnmt_is_patched !=True:
						print('\nFILE VERIFICATION CORRECT.\n -> FILE WAS MODIFIED BUT ORIGIN IS CONFIRMED AS LEGIT\n')
					else:
						print('\nFILE VERIFICATION CORRECT. \n -> FILE WAS MODIFIED AND CNMT PATCHED\n')
				else:
					print("\nFILE VERIFICATION CORRECT. FILE IS SAFE.\n")
			if verdict == False:		
				print("\nFILE VERIFICATION INCORRECT. \n -> UNCONFIRMED ORIGIN FILE HAS BEEN TAMPERED WITH\n")	
			if 	hash==True and verdict==True:
				if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.xci'):
					verdict,feed=f.verify_hash_nca(65536,headerlist,verdict,feed)
				elif filename.endswith('.nsz'):
					verdict,feed=f.nsz_hasher(65536,headerlist,verdict,feed)
				elif filename.endswith('.xcz'):	
					verdict,feed=f.xcz_hasher(65536,headerlist,verdict,feed)
			f.flush()
			f.close()					
		except BaseException as e:
			Print.error('Exception: ' + str(e))
	return verdict,isrestored,cnmt_is_patched
		
def install(filepath=None,destiny="SD",verification=True,outfolder=None,ch_medium=True,check_fw=True,patch_keygen=False,install_mode="spec1",st_crypto=False):	
	print(check_fw)
	check_connection()
	if install_mode!="legacy":
		from mtpnsp import install_nsp_csv
	kgwarning=False;dopatch=False;keygeneration=0;tgkg=0
	if filepath=="":
		filepath=None
	if filepath==None:
		print("File input = null")
		return False
	if verification==True or str(verification).upper()=="HASH":	
		if str(verification).upper()=="HASH":
			verdict,isrestored,cnmt_is_patched=file_verification(filepath,hash=True)		
		else:
			verdict,isrestored,cnmt_is_patched=file_verification(filepath)
		if verdict==False:
			print("File didn't pass verification. Skipping...")
			return False
	print("- Retrieving Space on device")
	SD_ds,SD_fs,NAND_ds,NAND_fs,FW,device=get_storage_info()
	print("- Calculating Installed size")	
	dbDict=get_DB_dict(filepath)
	installedsize=dbDict['InstalledSize']	
	if destiny=="SD":
		print(f"  * SD free space: {SD_fs} ({sq_tools.getSize(SD_fs)})")	
		print(f"  * File installed size: {installedsize} ({sq_tools.getSize(installedsize)})")		
		if installedsize>SD_fs:
			if installedsize<NAND_fs and ch_medium==True:
				print("  Not enough space on SD. Changing target to EMMC")
				print(f"  * EMMC free space: {NAND_fs} ({sq_tools.getSize(NAND_fs)})")						
				destiny="NAND"
			elif  ch_medium==False:	
				sys.exit("   NOT ENOUGH SPACE SD STORAGE")				
			else:
				sys.exit("   NOT ENOUGH SPACE ON DEVICE")				
	else:
		print(f"  * EMMC free space: {NAND_fs} ({sq_tools.getSize(NAND_fs)})")	
		print(f"  * File installed size: {installedsize} ({sq_tools.getSize(installedsize)})")		
		if installedsize>NAND_fs:		
			if installedsize<SD_fs and ch_medium==True:
				print("  Not enough space on EMMC. Changing target to SD")			
				print(f"  * SD free space: {SD_fs} ({sq_tools.getSize(SD_fs)})")					
				destiny="SD"
			elif  ch_medium==False:	
				sys.exit("   NOT ENOUGH SPACE EMMC STORAGE")							
			else:
				sys.exit("   NOT ENOUGH SPACE ON DEVICE")	
	if check_fw==True:	
		keygeneration=dbDict['keygeneration']
		if FW!='unknown':	
			try:
				FW_RSV,RRSV=sq_tools.transform_fw_string(FW)
				FW_kg=sq_tools.kg_by_RSV(FW_RSV)
			except BaseException as e:
				Print.error('Exception: ' + str(e))
				FW='unknown'
				FW_kg='unknown'
				pass
		if FW!='unknown' and FW_kg!='unknown':			
			if int(keygeneration)>int(FW_kg):
				kgwarning=True
				tgkg=int(FW_kg)
			else:
				tgkg=keygeneration
		else:
			tgkg=keygeneration
		print(f"- Console Firmware: {FW} ({FW_RSV}) - keygen {FW_kg})")		
		print(f"- File keygeneration: {keygeneration}")				
	if kgwarning==True and patch_keygen==False:
		print("File requires a higher firmware. Skipping...")
		return False		
	elif kgwarning==True and patch_keygen==True: 	
		print("File requires a higher firmware. It'll will be prepatch")
		dopatch=True
	if (filepath.endswith('nsp') or filepath.endswith('nsz')) and st_crypto==True:	
		if install_mode=="legacy":	
			install_converted(filepath=filepath,outfolder=outfolder,destiny=destiny,kgpatch=dopatch,tgkg=tgkg)	
		else:
			if dopatch==False:
				tgkg=False		
			install_nsp_csv(filepath,destiny=destiny,cachefolder=outfolder,keypatch=tgkg)	
		return					
	if (filepath.endswith('nsp') or filepath.endswith('nsz')) and dopatch==True:	
		if install_mode=="legacy":	
			install_converted(filepath=filepath,outfolder=outfolder,destiny=destiny,kgpatch=dopatch,tgkg=tgkg)	
		else:
			install_nsp_csv(filepath,destiny=destiny,cachefolder=outfolder,keypatch=tgkg)		
		return			
	if filepath.endswith('xci') or filepath.endswith('xcz'):
		if install_mode=="legacy":
			install_converted(filepath=filepath,outfolder=outfolder,destiny=destiny,kgpatch=dopatch,tgkg=tgkg)
		else:
			from mtpxci import install_xci_csv
			if dopatch==False:
				tgkg=False			
			install_xci_csv(filepath,destiny=destiny,cachefolder=outfolder,keypatch=tgkg)
		return	
	process=subprocess.Popen([nscb_mtp,"Install","-ori",filepath,"-dst",destiny])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
			
def install_conv_st1(filepath,outfolder,keypatch='false'):
	tname=str(os.path.basename(filepath))[:-3]+'nsp'
	tmpfile=os.path.join(outfolder,tname)
	if filepath.endswith('xci') or filepath.endswith('xcz'):
		f = factory(filepath)
		f.open(filepath, 'rb')
	elif filepath.endswith('nsp') or filepath.endswith('nsz'):	
		f = squirrelNSP(filepath, 'rb')	
	f.c_nsp_direct(65536,tmpfile,outfolder,keypatch=keypatch)
	f.flush()
	f.close()	
			
def install_converted(filepath=None,outfolder=None,destiny="SD",kgpatch=False,tgkg=0):		
	check_connection()
	if filepath=="":
		filepath=None	
	if outfolder=="":
		filepath=None	
	if outfolder==None:
		outfolder=cachefolder
		if not os.path.exists(cachefolder):
			os.makedirs(cachefolder)	
	if kgpatch==False:
		keypatch='false'
	else:
		keypatch=int(tgkg)
	if filepath==None:
		print("File input = null")
		return False
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)		
	for f in os.listdir(outfolder):
		fp = os.path.join(outfolder, f)
		try:
			shutil.rmtree(fp)
		except OSError:
			os.remove(fp)		
	tname=str(os.path.basename(filepath))[:-3]+'nsp'
	tmpfile=os.path.join(outfolder,tname)	
	if isExe==False:
		process0=subprocess.Popen([sys.executable,squirrel,"-lib_call","mtp.mtpinstaller","install_conv_st1","-xarg",filepath,outfolder,keypatch])	
	else:
		process0=subprocess.Popen([squirrel,"-lib_call","mtp.mtpinstaller","install_conv_st1","-xarg",filepath,outfolder,keypatch])		
	while process0.poll()==None:
		if process0.poll()!=None:
			process0.terminate();
	process=subprocess.Popen([nscb_mtp,"Install","-ori",tmpfile,"-dst",destiny])		
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	
	try:			
		for f in os.listdir(outfolder):
			fp = os.path.join(outfolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)	
	except:pass				
		
def loop_install(tfile,destiny="SD",verification=True,outfolder=None,ch_medium=True,check_fw=True,patch_keygen=False,ch_base=False,ch_other=False,install_mode="spec1",st_crypto=False,checked=False):
	check_connection()		
	if not os.path.exists(tfile):
		sys.exit(f"Couldn't find {tfile}")		
	if ch_base==True or ch_other==True:
		if checked==False:		
			print("Content check activated")			
			retrieve_installed()
			installed=parsedinstalled()
		elif checked==True:	
			print("Content check activated. Games are preparsed")		
			installed=parsedinstalled()	
	file_list=listmanager.read_lines_to_list(tfile,all=True)
	for item in file_list:
		try:
			if ch_base==True or ch_other==True:
				fileid,fileversion,cctag,nG,nU,nD,baseid=listmanager.parsetags(item)
				if fileid.endswith('000') and fileversion==0 and fileid in installed.keys() and ch_base==True:
					print("Base game already installed. Skipping...")
					listmanager.striplines(tfile,counter=True)
					continue
				elif fileid.endswith('000') and fileid in installed.keys() and ch_other==True:
					updid=fileid[:-3]+'800'
					if fileversion>((installed[fileid])[2]):
						print("Asking DBI to delete previous content")
						process=subprocess.Popen([nscb_mtp,"DeleteID","-ID",fileid])	
						while process.poll()==None:
							if process.poll()!=None:
								process.terminate();					
						process=subprocess.Popen([nscb_mtp,"DeleteID","-ID",updid])		
						while process.poll()==None:
							if process.poll()!=None:
								process.terminate();					
					else:
						print("The update is a previous version than the installed on device.Skipping..")
						listmanager.striplines(tfile,counter=True)
						continue				
				elif ch_other==True	and fileid in installed.keys():
					if fileversion>((installed[fileid])[2]):
						print("Asking DBI to delete previous update")
						process=subprocess.Popen([nscb_mtp,"DeleteID","-ID",fileid])					
						while process.poll()==None:
							if process.poll()!=None:
								process.terminate();
					else:
						print("The update is a previous version than the installed on device.Skipping..")
						listmanager.striplines(tfile,counter=True)
						continue	
		except:pass				
		install(filepath=item,destiny=destiny,verification=verification,outfolder=outfolder,ch_medium=ch_medium,check_fw=check_fw,patch_keygen=patch_keygen,install_mode=install_mode,st_crypto=st_crypto)
		print("")
		listmanager.striplines(tfile,counter=True)
		
def retrieve_installed():	
	check_connection()
	print("  * Parsing games in device. Please Wait...")			
	process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","true"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	
	if os.path.exists(games_installed_cache):	
		print("   Success")		
			
def parsedinstalled(exclude_xci=True):
	installed={}	
	if os.path.exists(games_installed_cache):	
		gamelist=listmanager.read_lines_to_list(games_installed_cache,all=True)	
		for g in gamelist:
			try:
				if exclude_xci==True:
					if g.endswith('xci') or g.endswith('xc0'):
						continue		
				entry=listmanager.parsetags(g)
				entry=list(entry)		
				entry.append(g)
				installed[entry[0]]=entry
			except:pass				
	return installed	
	
		
def get_installed_info(tfile=None,search_new=True,excludehb=True,exclude_xci=False):
	check_connection()
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)
	forecombo=Style.BRIGHT+Back.GREEN+Fore.WHITE
	if tfile=="":
		tfile=None
	if os.path.exists(games_installed_cache):
		try:
			os.remove(games_installed_cache)
		except:pass
	if tfile==None:
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)	
		if exclude_xci==True:
			process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","true"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		else:	
			process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","false","-xci_lc",xci_locations],stdout=subprocess.PIPE,stderr=subprocess.PIPE)					
		print("Parsing games in device. Please Wait...")
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();	
	if os.path.exists(games_installed_cache):	
		gamelist=listmanager.read_lines_to_list(games_installed_cache,all=True)
		gamelist.sort()
		print("..........................................................")
		print("CONTENT FOUND ON DEVICE")
		print("..........................................................")		
		installed={}
		for g in gamelist:
			try:
				fileid,fileversion,cctag,nG,nU,nD,baseid=listmanager.parsetags(g)
				g0=[pos for pos, char in enumerate(g) if char == '[']
				g0=(g[0:g0[0]]).strip()
				installed[fileid]=[fileid,fileversion,cctag,nG,nU,nD,baseid,g0,g]
				g0=pretty_str(g0)
				verprint=str(fileversion)
				if len(verprint)<9:
					verprint=verprint+((9-len(verprint))*' ')					
				if excludehb==True:
					if not fileid.startswith('05') and not fileid.startswith('04')  and not str(fileid).lower()=='unknown':
						if g.endswith('.xci') or g.endswith('.xc0'):
							print(f"{g0} |{fileid}|{verprint}|XCI|{nG}G|{nU}U|{nD}D")
						else:
							print(f"{g0} |{fileid}|{verprint}|{cctag}")
				else:
					if g.endswith('.xci') or g.endswith('.xc0'):
						print(f"{g0} |{fileid}|{verprint}|XCI|{nG}G|{nU}U|{nD}D")	
					else:	
						print(f"{g0} |{fileid}|{verprint}|{cctag}")
			except:pass
		if search_new==True:			
			import nutdb
			nutdb.check_other_file(urlconfig,'versions_txt')
			f='nutdb_'+'versions'+'.txt'
			DATABASE_folder=nutdb.get_DBfolder()
			_dbfile_=os.path.join(DATABASE_folder,f)
			versiondict={}
			with open(_dbfile_,'rt',encoding='utf8') as csvfile:
				readCSV = csv.reader(csvfile, delimiter='|')	
				i=0			
				for row in readCSV:
					if i==0:
						csvheader=row
						i=1
						if 'id' and 'version' in csvheader:
							id=csvheader.index('id')
							ver=csvheader.index('version')	
						else:break	
					else:	
						try:
							tid=str(row[id]).upper() 
							version=str(row[ver]).upper() 
							if tid.endswith('800'):
								keyid=tid[:-3]+'000'
							else:
								keyid=tid
							if keyid in versiondict.keys():
								v=versiondict[keyid]
								if v<int(version):
									versiondict[keyid]=int(version)
							else:
								versiondict[keyid]=int(version)
						except:pass
			print("..........................................................")
			print("NEW UPDATES")
			print("..........................................................")			
			for k in installed.keys():	
				fileid,fileversion,cctag,nG,nU,nD,baseid,g0,g=installed[k]
				g0=pretty_str(g0)
				verprint=str(fileversion)
				fillver=''
				if len(verprint)<6:
					fillver=(6-len(verprint))*' '					
				v=0;
				updateid=fileid[:-3]+'800'
				if updateid in installed.keys() and fileid.endswith('000'):				
					continue
				if	fileid.endswith('800'):
					try:			
						v=versiondict[baseid]
					except:pass						
				else:	
					try:
						v=versiondict[fileid]
					except:pass			
				if int(v)>int(fileversion):
					if fileid.endswith('000') or fileid.endswith('800'):
						updid=fileid[:-3]+'800'
						print(f"{g0} [{baseid}][{verprint}]{fillver} -> "+forecombo+  f"[{updid}] [v{v}]"+Style.RESET_ALL)
					else:
						print(f"{g0} [{fileid}][{verprint}]{fillver} -> "+forecombo+  f"[{fileid}] [v{v}]"+Style.RESET_ALL)	
			check_xcis=False;xci_dlcs={}			
			print("..........................................................")
			print("NEW DLCS")
			print("..........................................................")	
			for k in versiondict.keys():
				if k in installed.keys() or k.endswith('000') or k.endswith('800'):
					continue
				else:
					try:
						baseid=get_dlc_baseid(k)
					except:
						baseid=k
					updid=baseid[:-3]+'800'
					if baseid in installed.keys() or updid in installed.keys():
						fileid,fileversion,cctag,nG,nU,nD,baseid,g0,g=installed[baseid]
						if nD>0:
							if check_xcis==False:
								check_xcis=True
							if not baseid in xci_dlcs.keys():
								entry=list()
								entry.append(k)
								xci_dlcs[baseid]=entry
							else:
								entry=xci_dlcs[baseid]
								entry.append(k)
								xci_dlcs[baseid]=entry
							continue
						g0=pretty_str(g0)									
						print(f"{g0} [{baseid}] -> "+forecombo+ f"[{k}] [v{versiondict[k]}]"+Style.RESET_ALL)
			t=0			
			if check_xcis==True:
				for bid in xci_dlcs.keys():
					fileid,fileversion,cctag,nG,nU,nD,baseid,g0,g=installed[bid]
					entry=xci_dlcs[bid]
					test=len(entry)
					if test>nD:
						if t==0:
								print("..........................................................")
								print("XCI MAY HAVE NEW DLCS. LISTING AVAILABLE")
								print("..........................................................")	
								t+=1
						g0=pretty_str(g0)
						for k in xci_dlcs[baseid]:	
							print(f"{g0} [{baseid}] -> "+forecombo+ f"[{k}] [v{versiondict[k]}]"+Style.RESET_ALL)						
					

def get_archived_info(search_new=True,excludehb=True,exclude_xci=False):	
	check_connection()
	forecombo=Style.BRIGHT+Back.GREEN+Fore.WHITE
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)	
	for f in os.listdir(cachefolder):
		fp = os.path.join(cachefolder, f)
		try:
			shutil.rmtree(fp)
		except OSError:
			os.remove(fp)	
	print("1. Retrieving registered...")			
	dbicsv=os.path.join(cachefolder,"registered.csv")
	process=subprocess.Popen([nscb_mtp,"Download","-ori","4: Installed games\\InstalledApplications.csv","-dst",dbicsv],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
	if os.path.exists(dbicsv):	
		print("   Success")			
	print("2. Checking Installed...")
	if exclude_xci==True:
		process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","true"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	else:	
		process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","false","-xci_lc",xci_locations],stdout=subprocess.PIPE,stderr=subprocess.PIPE)		
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	
	if os.path.exists(games_installed_cache):	
		print("   Success")
	gamelist=listmanager.read_lines_to_list(games_installed_cache,all=True)	
	dbi_dict={}
	with open(dbicsv,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		id=0;ver=1;tname=2;
		for row in readCSV:		
			try:
				tid=(str(row[id]).upper())[2:]
				version=int(row[ver])
				name=str(row[tname])
				dbi_dict[tid]=[tid,version,name]
			except:pass
	installed={}		
	for g in gamelist:
		entry=listmanager.parsetags(g)
		installed[entry[0]]=entry
	print("..........................................................")
	print("ARCHIVED|REGISTERED GAMES")
	print("..........................................................")	
	for g in dbi_dict.keys():
		if not g in installed.keys():
			tid,version,g0=dbi_dict[g]
			g0=pretty_str(g0)			
			print(f"{g0} [{tid}][{version}]")
	if search_new==True:			
		import nutdb
		nutdb.check_other_file(urlconfig,'versions_txt')
		f='nutdb_'+'versions'+'.txt'
		DATABASE_folder=nutdb.get_DBfolder()
		_dbfile_=os.path.join(DATABASE_folder,f)
		versiondict={}
		with open(_dbfile_,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0			
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
					if 'id' and 'version' in csvheader:
						id=csvheader.index('id')
						ver=csvheader.index('version')	
					else:break	
				else:	
					try:
						tid=str(row[id]).upper() 
						version=str(row[ver]).upper() 
						if tid.endswith('800'):
							keyid=tid[:-3]+'000'
						else:
							keyid=tid
						if keyid in versiondict.keys():
							v=versiondict[keyid]
							if v<int(version):
								versiondict[keyid]=int(version)
						else:
							versiondict[keyid]=int(version)
					except:pass		
		print("..........................................................")
		print("NEW UPDATES")
		print("..........................................................")			
		for k in dbi_dict.keys():	
			fileid,fileversion,g0=dbi_dict[k]
			g0=pretty_str(g0)
			verprint=str(fileversion)
			fillver=''
			if len(verprint)<6:
				fillver=(6-len(verprint))*' '						
			v=0;
			updateid=fileid[:-3]+'800'
			if updateid in dbi_dict.keys() and fileid.endswith('000'):				
				continue
			if	fileid.endswith('800'):
				try:
					baseid=fileid[:-3]+'000'
					v=versiondict[baseid]
				except:pass						
			else:	
				try:
					v=versiondict[fileid]
				except:pass			
			if int(v)>int(fileversion):
				if fileid.endswith('000') or fileid.endswith('800'):
					baseid=fileid[:-3]+'000'
					updid=fileid[:-3]+'800'
					print(f"{g0} [{baseid}][{verprint}]{fillver} -> "+forecombo+  f"[{updid}] [v{v}]"+Style.RESET_ALL)
				else:
					print(f"{g0} [{fileid}][{verprint}]{fillver} -> "+forecombo+  f"[{fileid}] [v{v}]"+Style.RESET_ALL)	
		print("..........................................................")
		print("NEW DLCS")
		print("..........................................................")	
		for k in versiondict.keys():
			if k in dbi_dict.keys() or k.endswith('000') or k.endswith('800'):
				continue
			else:
				try:
					baseid=get_dlc_baseid(k)
				except:
					baseid=k
				updid=baseid[:-3]+'800'
				if baseid in dbi_dict.keys() or updid in dbi_dict.keys():
					fileid,fileversion,g0=dbi_dict[baseid]
					g0=pretty_str(g0)			
					print(f"{g0} [{baseid}] -> "+forecombo+ f"[{k}] [v{versiondict[k]}]"+Style.RESET_ALL)	
		
			
def update_console(libraries="all",destiny="SD",exclude_xci=True,prioritize_nsz=True,tfile=None,verification=True,ch_medium=True,ch_other=False,autoupd_aut=True,use_archived=False):	
	check_connection()
	if use_archived==True:
		autoupd_aut=False
	if tfile==None:
		tfile=os.path.join(NSCB_dir, 'MTP1.txt')
	if os.path.exists(tfile):
		try:
			os.remove(tfile)
		except: pass			
	libdict=get_libs("source");
	pths={}	
	if libraries=="all":
		for entry in libdict.keys():
			pths[entry]=((libdict[entry])[0])
	else:
		for entry in libdict.keys():
			if (libdict[entry])[1]==True:
				pths[entry]=((libdict[entry])[0])	
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)				
	for f in os.listdir(cachefolder):
		fp = os.path.join(cachefolder, f)
		try:
			shutil.rmtree(fp)
		except OSError:
			os.remove(fp)	
	if use_archived!=True:		
		print("1. Parsing games in device. Please Wait...")			
		if exclude_xci==True:
			process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","true"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		else:	
			process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","false","-xci_lc",xci_locations],stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();	
		if os.path.exists(games_installed_cache):	
			print("   Success")
		gamelist=listmanager.read_lines_to_list(games_installed_cache,all=True)
		installed={}		
		for g in gamelist:
			try:
				if exclude_xci==True:
					if g.endswith('xci') or g.endswith('xc0'):
						continue
				entry=listmanager.parsetags(g)
				entry=list(entry)		
				entry.append(g)
				installed[entry[0]]=entry	
			except:pass
	else:
		print("1. Retrieving registered...")			
		dbicsv=os.path.join(cachefolder,"registered.csv")
		process=subprocess.Popen([nscb_mtp,"Download","-ori","4: Installed games\\InstalledApplications.csv","-dst",dbicsv],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();
		if os.path.exists(dbicsv):	
			print("   Success")					
			installed={}
			with open(dbicsv,'rt',encoding='utf8') as csvfile:
				readCSV = csv.reader(csvfile, delimiter=',')
				id=0;ver=1;tname=2;
				for row in readCSV:		
					try:
						tid=(str(row[id]).upper())[2:]
						version=int(row[ver])
						if version>0 and tid.endswith('000'):
							tid=tid[:-3]+'800'
						name=str(row[tname])
						g=f"{name} [{tid}][v{version}].nsp"
						entry=listmanager.parsetags(g)
						entry=list(entry)		
						entry.append(g)
						if entry[0] in installed.keys():
							if int((intalled[entry[0]])[1])<version:
								installed[entry[0]]=entry
						else:
							installed[entry[0]]=entry							
					except:pass						
	print("2. Parsing local libraries. Please Wait...")				
	locallist=[]
	for p in pths.keys():
		locallist+=listmanager.folder_to_list(pths[p],['nsp','nsz'])
		print(f'   Parsed Library: "{str(p).upper()}"')		
	if prioritize_nsz==True:
		locallist=sorted(locallist, key=lambda x: x[-1])
		locallist.reverse()
	localgames={}		
	for g in locallist:
		try:
			entry=listmanager.parsetags(g)
			entry=list(entry)
			entry.append(g)		
			if not entry[0] in localgames:
				localgames[entry[0]]=entry
			else:
				v=(localgames[entry[0]])[1]
				if int(entry[1])>int(v):
					localgames[entry[0]]=entry		
		except:pass	
	print("3. Searching new updates. Please Wait...")						
	gamestosend={}		
	for g in installed.keys():
		if g.endswith('000') or g.endswith('800'): 
			try:
				updid=g[:-3]+'800'
				if updid in localgames:
					if updid in installed:
						if int((installed[updid])[1])<int((localgames[updid])[1]):
							if not updid in gamestosend:
								gamestosend[updid]=localgames[updid]
							else:
								if int((gamestosend[updid])[1])<int((localgames[updid])[1]):
									gamestosend[updid]=localgames[updid]
					else:
						if not updid in gamestosend:
							gamestosend[updid]=localgames[updid]
						else:
							if int((gamestosend[updid])[1])<int((localgames[updid])[1]):
								gamestosend[updid]=localgames[updid]				
			except:pass
		else:
			try:		
				if g in localgames:
					if int((installed[g])[1])<int((localgames[g])[1]):
						if not g in gamestosend:
							gamestosend[g]=localgames[g]
						else:
							if int((gamestosend[g])[1])<int((localgames[g])[1]):
								gamestosend[g]=localgames[g]
			except:pass
	print("4. Searching new dlcs. Please Wait...")	
	for g in installed.keys():	
		try:
			if g.endswith('000') or g.endswith('800'): 
				baseid=g[:-3]+'000'
			else:
				baseid=(installed[g])[6]
			for k in localgames.keys():
				try:				
					if not (k.endswith('000') or k.endswith('800')) and not k in installed:
						test=get_dlc_baseid(k)
						if baseid ==test:
							if not k in gamestosend:
								gamestosend[k]=localgames[k]
							else:
								if int((gamestosend[k])[1])<int((localgames[k])[1]):
									gamestosend[k]=localgames[k]	
				except BaseException as e:
					# Print.error('Exception: ' + str(e))			
					pass								
		except BaseException as e:
			# Print.error('Exception: ' + str(e))			
			pass
	print("5. List of content that will get installed...")	
	gamepaths=[]
	if len(gamestosend.keys())>0:
		if autoupd_aut==True:		
			for i in sorted(gamestosend.keys()):
				fileid,fileversion,cctag,nG,nU,nD,baseid,path=gamestosend[i]
				bname=os.path.basename(path) 
				gamepaths.append(path)
				g0=[pos for pos, char in enumerate(bname) if char == '[']	
				g0=(bname[0:g0[0]]).strip()
				print(f"   * {g0} [{fileid}][{fileversion}] [{cctag}] - {(bname[-3:]).upper()}")
		else:				
			options=[]
			for i in sorted(gamestosend.keys()):
				fileid,fileversion,cctag,nG,nU,nD,baseid,path=gamestosend[i]
				bname=os.path.basename(path) 
				gamepaths.append(path)
				g0=[pos for pos, char in enumerate(bname) if char == '[']	
				g0=(bname[0:g0[0]]).strip()
				cstring=f"{g0} [{fileid}][{fileversion}] [{cctag}] - {(bname[-3:]).upper()}"
				options.append(cstring)
			if options:
				title = 'Select content to install: \n + Press space or right to select entries \n + Press E to finish selection \n + Press A to select all entries'				
				picker = Picker(options, title, multi_select=True, min_selection_count=1)
				def end_selection(picker):
					return False,-1
				def select_all(picker):
					return "ALL",-1			
				picker.register_custom_handler(ord('e'),  end_selection)
				picker.register_custom_handler(ord('E'),  end_selection)
				picker.register_custom_handler(ord('a'),  select_all)
				picker.register_custom_handler(ord('A'),  select_all)	
				selected=picker.start()					
				if selected[0]==False:
					print("    User didn't select any files")
					return False					
				if selected[0]=="ALL":		
					pass
				else:
					newgpaths=[]
					for game in selected:
						g=game[1]
						g0=gamepaths[g]
						newgpaths.append(g0)
					gamepaths=newgpaths	
		print("6. Generating text file...")		
		with open(tfile,'w', encoding='utf8') as textfile:
			for i in gamepaths:
				textfile.write((i).strip()+"\n")
		print("7. Triggering installer on loop mode.")
		print("   Note:If you interrupt the list use normal install mode to continue list")				
		loop_install(tfile,destiny=destiny,verification=verification,ch_medium=ch_medium,ch_other=ch_other,checked=True)
	else:
		print("\n   --- DEVICE IS UP TO DATE ---")		
	
def get_libs(lib="source"):
	libraries={}
	if lib=="source":
		libtfile=mtp_source_lib
	elif lib=="internal":		
		libtfile=mtp_internal_lib		
	else:
		libtfile=lib	
	with open(libtfile,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0;up=False	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'library_name' and 'path' and 'Update' in csvheader:
					lb=csvheader.index('library_name')
					pth=csvheader.index('path')	
					up=csvheader.index('Update')	
				else:
					if 'library_name' and 'path' in csvheader:
						lb=csvheader.index('library_name')
						pth=csvheader.index('path')				
					else:break	
			else:	
				try:
					update=False
					library=str(row[lb])
					route=str(row[pth])			
					if up!=False:
						update=str(row[up])
						if update.upper()=="TRUE":
							update=True
						else:
							update=False
					else:
						update=False
					libraries[library]=[route,update]
				except:pass	
	return libraries		
			
def get_dlc_baseid(titleid):
	baseid=str(titleid)
	token=int(hx(bytes.fromhex('0'+baseid[-4:-3])),16)-int('1',16)
	token=str(hex(token))[-1]
	token=token.upper()
	baseid=baseid[:-4]+token+'000'	
	return baseid	

def get_storage_info():
	check_connection()
	SD_ds=0;SD_fs=0;NAND_ds=0;NAND_fs=0;device='unknown';FW='unknown'
	if os.path.exists(storage_info):
		try:
			os.remove(storage_info)
		except:pass	
	process=subprocess.Popen([nscb_mtp,"ReportStorage","-tfile",storage_info],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
	if os.path.exists(storage_info):
		with open(storage_info,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0			
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
					if 'device' and 'disk_name' and 'capacity' and 'freespace' and 'FW' in csvheader:
						idev=csvheader.index('device')
						idn=csvheader.index('disk_name')
						idc=csvheader.index('capacity')
						ifs=csvheader.index('freespace')
						ifw=csvheader.index('FW')						
					else:break		
				else:
					if i==1:
						try:
							device=str(row[idev])
							FW=str(row[ifw])
						except:pass	
						i+1;
					if 'SD CARD' in str(row[idn]).upper() or 'SD' in str(row[idn]).upper():
						# print(str(row[idn]));print(str(row[idc]));print(str(row[ifs]));
						SD_ds=int(row[idc])
						SD_fs=int(row[ifs])
					if 'USER' in str(row[idn]).upper():							
						# print(str(row[idn]));print(str(row[idc]));print(str(row[ifs]));
						NAND_ds=int(row[idc])
						NAND_fs=int(row[ifs])
					if str(row[idev]).upper()=="TINFOIL":
						SD_ds=int(row[idc])
						SD_fs=int(row[ifs])
						NAND_ds=0
						NAND_fs=0
	return SD_ds,SD_fs,NAND_ds,NAND_fs,FW,device
	
def get_DB_dict(filepath):
	installedsize=0
	if filepath.endswith('xci') or filepath.endswith('xcz'):
		f = factory(filepath)		
		f.open(filepath, 'rb')		
		dict=f.return_DBdict()			
		f.flush()
		f.close()
	elif filepath.endswith('nsp') or filepath.endswith('nsz') or filepath.endswith('nsx'):
		f = squirrelNSP(filepath)			
		dict=f.return_DBdict()		
		f.flush()
		f.close()		
	return dict
	
def get_files_from_walk(tfile=None,extlist=['nsp','nsz','xci','xcz'],filter=False):
	from picker_walker import get_files_from_walk
	files=get_files_from_walk(tfile=tfile,extlist=extlist,filter=filter)
	if files==False:
		return False
	elif tfile==None:
		return files
