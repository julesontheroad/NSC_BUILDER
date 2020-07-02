import aes128
import Print
import os
import shutil
import json
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
import sq_tools
import io
from Fs import Type as FsType
from Fs import factory
import Keys
from binascii import hexlify as hx, unhexlify as uhx
from DBmodule import Exchange as exchangefile
import math
import sys
import subprocess
from mtp.wpd import is_switch_connected
import listmanager
import csv
from colorama import Fore, Back, Style
import time
from secondary import clear_Screen
from python_pick import pick
from python_pick import Picker
from Drive import Private as DrivePrivate
from Drive import Public as DrivePublic
from Drive import DriveTools
import requests
from Drive import Download as Drv
from Interface import About
from workers import concurrent_scrapper

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
download_lib_file = os.path.join(zconfig_dir, 'mtp_download_libraries.txt')
remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
cache_lib_file= os.path.join(zconfig_dir, 'remote_cache_location.txt')
_1fichier_token=os.path.join((os.path.join(zconfig_dir, 'credentials')),'_1fichier_token.tk')

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
					dict={}
					for j in range(len(csvheader)):
						try:
							dict[csvheader[j]]=row[j]
						except:
							dict[csvheader[j]]=None
					db[row[0]]=dict
		# print(db)			
		return db
	except: return False
	
def get_cache_lib():
	db=libraries(cache_lib_file)
	TD=None;lib=None;path="null";libpath=None
	for entry in db:
		path=db[entry]['path']
		TD=db[entry]['TD_name']
		lib=entry
		libpath=path
		break
	if TD=='':
		TD=None
	return lib,TD,libpath		
	
def addtodrive(filename):
	if os.path.exists(cache_lib_file):
		lib,TD,libpath=get_cache_lib()
		if lib!=None:
			file_id, is_download_link=DrivePublic.parse_url(filename)		
			if is_download_link:
				remote=DrivePrivate.location(route=libpath,TD_Name=TD)		
				result=remote.drive_service.files().get(fileId=file_id, fields="name,mimeType").execute()		
				name=result['name']	
				testpath=('{}/{}').format(libpath,name)
				remote=DrivePrivate.location(route=testpath,TD_Name=TD)	
				if remote.name==None:			
					name=DrivePrivate.add_to_drive(url=filename,filepath=libpath,makecopy=True,TD=TD)
					filename=('{}/{}').format(libpath,name)
					ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
				else:
					filename=testpath
				globalremote=remote
		return filename	

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

def pick_order():
	title = 'Select order to list the files: '
	db=libraries(download_lib_file)
	options = ['name_ascending','name_descending','size_ascending','size_descending','date_ascending','date_descending']
	selected = pick(options, title,min_selection_count=1)	
	order=selected[0]
	return order			
	
def eval_link(link,tfile,userfile):	
	link=input("Enter your choice: ")
	link=link.strip()
	if '&' in link:
		varout='999'
	elif len(link)<2:
		varout=link
	else:
		varout='999'
	with open(userfile,"w", encoding='utf8') as userinput:
		userinput.write(varout)		
	if link.startswith('https://1fichier.com'):
		with open(tfile,"a", encoding='utf8') as textfile:
			textfile.write(link+'\n')				
	elif link.startswith('https://drive.google.com'):
		with open(tfile,"a", encoding='utf8') as textfile:
			textfile.write(link+'\n')	

def select_from_libraries(tfile):	
	db=libraries(remote_lib_file)
	if db==False:
		sys.exit(f"Missing {remote_lib_file}")
	paths,TDs=Drv.pick_libraries()
	filter=interface_filter()	
	order=pick_order()
	print("  * Parsing files from Google Drive. Please Wait...")		
	if isinstance(paths, list):
		db={}
		for i in range(len(paths)):
			db[paths[i]]={'path':paths[i],'TD_name':TDs[i]}				
		files=concurrent_scrapper(filter=filter,order=order,remotelib='all',db=db)
	else:
		db={}
		db[paths]={'path':paths,'TD_name':TDs}			
		files=concurrent_scrapper(filter=filter,order=order,remotelib='all',db=db)	
	print("  * Entering File Picker")	
	title = 'Select content to install: \n + Press space or right to select content \n + Press E to finish selection'
	filenames=[]
	for f in files:
		filenames.append(f[0])
	options=filenames
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
			textfile.write((files[f[1]])[2]+'/'+(files[f[1]])[0]+'\n')

		
def loop_install(tfile,destiny="SD",outfolder=None,ch_medium=True,check_fw=True,patch_keygen=False,ch_base=False,ch_other=False,checked=False):	
	if not os.path.exists(tfile):
		sys.exit(f"Couldn't find {tfile}")		
	if (ch_base==True or ch_other==True) and checked==False:		
		print("Content check activated")			
		retrieve_installed()
		installed=parsedinstalled()		
	elif (ch_base==True or ch_other==True) and checked==True:	
		print("Content check activated. Games are preparsed")		
		installed=parsedinstalled()		
	file_list=listmanager.read_lines_to_list(tfile,all=True)	
	for item in file_list:
		if item.startswith('https://1fichier.com'):
			print("Item is 1fichier link. Redirecting...")
			fichier_install(item,destiny)			
		elif item.startswith('https://drive.google.com'):
			print("Item is google drive public link. Redirecting...")
			public_gdrive_install(item,destiny)			
		elif os.path.exists(item):
			print("Item is a local link. Skipping...")	
		else:
			test=item.split('|')
			item=test[0]
			lib,TD,libpath=get_library_from_path(remote_lib_file,item)			
			if lib!=None:
				print("Item item remote library link. Redirecting...")
				gdrive_install(item,destiny)
	
def get_library_from_path(tfile,filename):
	db=libraries(remote_lib_file)
	TD=None;lib=None;path="null"
	for entry in db:
		path=db[entry]['path']
		# print(path)
		if filename.startswith(path):
			TD=db[entry]['TD_name']
			lib=entry
			libpath=path
			break
		else:
			pass
	if lib==None:
		db=libraries(cache_lib_file)
		TD=None;lib=None;path="null"
		for entry in db:
			path=db[entry]['path']
			if filename.startswith(path):
				TD=db[entry]['TD_name']
				lib=entry
				libpath=path
				break
			else:
				pass		
	if TD=='':
		TD=None			
	return lib,TD,libpath	
	
def gdrive_install(filename,destiny="SD"):
	lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
	ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
	# header=DrivePrivate.get_html_header(remote.access_token)
	token=remote.access_token
	name=remote.name
	sz=remote.size
	URL='https://www.googleapis.com/drive/v3/files/'+remote.ID+'?alt=media'	
	ext=name.split('.')
	ext=ext[-1]
	if not name.endswith('nsp') and not name.endswith('nsz'):
		sys.exit(f"Extension not supported for direct instalation {ext} in {name}")			
	process=subprocess.Popen([nscb_mtp,"DriveInstall","-ori",URL,"-dst",destiny,"-name",name,"-size",sz,"-tk",token])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	

def public_gdrive_install(filepath,destiny="SD"):
	lib,TD,libpath=get_cache_lib()
	if lib==None:
		sys.exit(f"Google Drive Public Links are only supported via cache folder")	
	filename=addtodrive(filepath)
	ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)	
	token=remote.access_token
	name=remote.name
	sz=remote.size
	URL='https://www.googleapis.com/drive/v3/files/'+remote.ID+'?alt=media'	
	ext=name.split('.')
	ext=ext[-1]
	if not name.endswith('nsp') and not name.endswith('nsz'):
		sys.exit(f"Extension not supported for direct instalation {ext} in {name}")			
	process=subprocess.Popen([nscb_mtp,"DriveInstall","-ori",URL,"-dst",destiny,"-name",name,"-size",sz,"-tk",token])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();		
	
def fichier_install(url,destiny="SD"):
	if not os.path.exists(_1fichier_token):
		sys.exit("No 1fichier token setup")
	with open(_1fichier_token,'rt',encoding='utf8') as tfile:
		token=(tfile.readline().strip())
	if token==None:
		sys.exit("Missing 1fichier token")		
	APIkey=token
	auth={'Authorization':f'Bearer {APIkey}','Content-Type':'application/json'}
	session = requests.session()
	download_params = {
		'url' : url,
		'inline' : 0,
		'cdn' : 0,
		'restrict_ip':  0,
		'no_ssl' : 0,
	}			
	info_params={
		'url' : url	
	}
	r=session.post('https://api.1fichier.com/v1/file/info.cgi',json=info_params,headers=auth)
	info_dict=r.json()
	# print(info_dict)
	sz=info_dict['size']
	name=info_dict['filename']
	r=session.post('https://api.1fichier.com/v1/download/get_token.cgi',json=download_params,headers=auth)
	dict=r.json()
	# print(dict)
	ext=name.split('.')
	ext=ext[-1]
	if not name.endswith('nsp') and not name.endswith('nsz'):
		sys.exit(f"Extension not supported for direct instalation {ext} in {name}")			
	if not dict['status']=="OK":
		sys.exit(f"API call returned {dict['status']}")			
	URL=dict['url']
	process=subprocess.Popen([nscb_mtp,"fichierInstall","-ori",URL,"-dst",destiny,"-name",name,"-size",str(sz)])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();		
			
			
def Interface_Installer():
	clear_Screen()
	About()
	response=False	
	print('\n********************************************************')
	print('REMOTE INSTALLER')
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
				folder,TD=DrivePrivate.folder_walker()		
				print(folder)
				response=interface_file(folder,TD)
				if response==False:
					return False
		elif ck=="2" and os.path.exists(remote_lib_file):
			while True:
				paths,TDs=Drv.pick_libraries()
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
			TD=DrivePrivate.TD_picker(ck)		
			response=interface_menu(ck,TD,True)
		if 	response==False:
			break	

def interface_menu(path,TD):
	xcipr=False;nxzpr=False;xcimode="Untrimmed";zmode="Compressed"
	if isinstance(path, list):
		if not isinstance(path[0], list):	
			for file in path:
				if file.endswith('.xci'):
					xcipr=True
				elif file.endswith('.xcz') or file.endswith('.nsz'):
					nxzpr=True	
				if xcipr==True and nxzpr==True:
					break
				print(file)
			return False
	else:
		return False	
			# if xcipr==True:
				# xcimode=interface_xci_mode()
			# if nxzpr==True:	
				# zmode=interface_compressedf_mode()
			# ofolder=ask_download_folder()	
			# clear_Screen()
			# About()						
			# counter=len(path)	
			# for file in path:	
				# route_download(file,TD,ofolder,xcimode=xcimode,zmode=zmode)	
				# counter-=1
				# if counter>0:
					# print("Still {} files to download".format(str(counter)))	
			# input('\nPress any key to continue...')					
			# return False	
		# else:
			# counter=0;files=list()
			# for i in path:
				# counter+=len(i[0])
				# files+=i[0]
			# for file in files:
				# if file.endswith('.xci'):
					# xcipr=True
				# elif file.endswith('.xcz') or file.endswith('.nsz'):
					# nxzpr=True	
				# if xcipr==True and nxzpr==True:
					# break
			# if xcipr==True:
				# xcimode=interface_xci_mode()
			# if nxzpr==True:	
				# zmode=interface_compressedf_mode()
			# ofolder=ask_download_folder()	
			# clear_Screen()
			# About()			
			# for k in path:
				# TD=k[1];files=k[0]
				# for file in files:	
					# route_download(file,TD,ofolder,xcimode=xcimode,zmode=zmode)	
					# counter-=1
					# if counter>0:
						# print("Still {} files to download".format(str(counter)))	
			# input('\nPress any key to continue...')					
			# return False				
	# elif path.startswith('http'):
		# file=DrivePublic.return_remote(path)		
		# if file.name.endswith('.xci'):
			# xcipr=True
		# elif file.name.endswith('.xcz') or file.name.endswith('.nsz'):
			# nxzpr=True
		# elif file.name==None:
			# print("File overpassed quota or is unreadable")
			# input('\nPress any key to continue...')	
			# clear_Screen()
			# About()		
		# if xcipr==True:
			# xcimode=interface_xci_mode()
		# if nxzpr==True:	
			# zmode=interface_compressedf_mode()
		# ofolder=ask_download_folder()		
		# route_download_public(path,ofolder,file.name,xcimode=xcimode,zmode=zmode,file=file)	
		# input('\nPress any key to continue...')					
		# return False
	# elif path !=None:
		# if path.endswith('.xci'):
			# xcipr=True
		# elif path.endswith('.xcz') or path.endswith('.nsz'):
			# nxzpr=True	
		# if xcipr==True:
			# xcimode=interface_xci_mode()
		# if nxzpr==True:	
			# zmode=interface_compressedf_mode()
		# ofolder=ask_download_folder()	
		# route_download(path,TD,ofolder,xcimode=xcimode,zmode=zmode)	
		# input('\nPress any key to continue...')					
		# return False	
	# else:
		# return False		
def interface_file(path,TD):
	if TD=="pick":
		TD=DrivePrivate.TD_picker(path)
	folder=path;TeamDrive=TD
	response=False	
	files=list()
	filter=interface_filter(path)	
	if isinstance(path, list):
		db={}
		for i in range(len(path)):
			db[path[i]]={'path':path[i],'TD_name':TD[i]}	
		files=concurrent_scrapper(filter='',order='name_ascending',remotelib='all',db=db)
	else:
		db={}
		db[path]={'path':path,'TD_name':TD}	
		files=concurrent_scrapper(filter='',order='name_ascending',remotelib='all',db=db)		
		if files==False:
			print("Query returned no files")
			input('\nPress any key to continue...')	
			clear_Screen()
			About()
			return False			
		else:	
			response=interface_menu(files,TeamDrive)
			if str(response)=="False":
				return response
			elif str(response)=="CHANGE": 
				return True

	