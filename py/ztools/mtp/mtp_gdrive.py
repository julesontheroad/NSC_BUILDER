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
import requests

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