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

def retrieve_installed():	
	try:			
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)	
	except:pass		
	print("  * Parsing games in device. Please Wait...")			
	process=subprocess.Popen([nscb_mtp,"ShowInstalled","-tfile",games_installed_cache,"-show","false","-exci","true"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	
	if os.path.exists(games_installed_cache):	
		print("    Success")		
			
def parsedinstalled():
	installed={}	
	if os.path.exists(games_installed_cache):	
		gamelist=listmanager.read_lines_to_list(games_installed_cache,all=True)	
		for g in gamelist:
			entry=listmanager.parsetags(g)
			entry=list(entry)		
			entry.append(g)
			installed[entry[0]]=entry
	return installed
	
def get_gamelist(dosort=True):	
	if os.path.exists(games_installed_cache):	
		gamelist=listmanager.read_lines_to_list(games_installed_cache,all=True)	
		gamelist.sort()
	return gamelist
	
def pick_download_folder():
	title = 'Select download folder: '
	db=libraries(download_lib_file)
	if db==False:
		return False,False
	options = [x for x in db.keys()]
	selected = pick(options, title,min_selection_count=1)	
	path=(db[selected[0]])['path']
	return path		
	
def pick_transfer_folder():
	if not os.path.exists(mtp_internal_lib):
		return "SD"
	title = 'Select transfer folder: '
	db=libraries(mtp_internal_lib)
	if db==False:
		return False,False
	options = [x for x in db.keys()]
	selected = pick(options, title,min_selection_count=1)	
	path=(db[selected[0]])['path']
	return path			
	
def transfer(filepath=None,destiny="SD",):	
	if filepath=="":
		filepath=None
	if filepath==None:
		print("File input = null")
		return False
	print("- Retrieving Space on device")
	from mtp.mtpinstaller import get_storage_info
	SD_ds,SD_fs,NAND_ds,NAND_fs,FW,device=get_storage_info()
	print("- Calculating File size")	
	file_size=os.path.getsize(filepath)
	print(f"  * SD free space: {SD_fs} ({sq_tools.getSize(SD_fs)})")	
	print(f"  * File installed size: {file_size} ({sq_tools.getSize(file_size)})")		
	if file_size>SD_fs:
		print("  Not enough space on SD. Changing target to EMMC")
		print(f"  * EMMC free space: {NAND_fs} ({sq_tools.getSize(NAND_fs)})")						
		sys.exit("   NOT ENOUGH SPACE SD STORAGE")
	if destiny=="SD":
		destiny="1: External SD Card/"
	basename=os.path.basename(filepath)		
	destiny=os.path.join(destiny, basename)
	process=subprocess.Popen([nscb_mtp,"Transfer","-ori",filepath,"-dst",destiny])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	
	
def loop_transfer(tfile):		
	if not os.path.exists(tfile):
		sys.exit(f"Couldn't find {tfile}")			
	destiny=pick_transfer_folder()	
	file_list=listmanager.read_lines_to_list(tfile,all=True)
	for item in file_list:			
		transfer(filepath=item,destiny=destiny)
		print("")
		listmanager.striplines(tfile,counter=True)	
	
def dump_content():
	retrieve_installed()
	installed=get_gamelist()
	print("  * Entering File Picker")	
	title = 'Select content to uninstall: \n + Press space or right to select content \n + Press E to finish selection'
	options=installed
	picker = Picker(options, title, multi_select=True, min_selection_count=1)
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection)
	selected=picker.start()
	if selected[0]==False:
		print("    User didn't select any files")
		return False
	outfolder=pick_download_folder()
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	print("  * Starting dumping process...")
	counter=len(selected)	
	for file in selected:	
		outputfile=os.path.join(outfolder, file[0])
		process=subprocess.Popen([nscb_mtp,"Dump","-sch",file[0],"-dst",outputfile])
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();
		counter-=1		
		print('...................................................')
		print('STILL '+str(counter)+' FILES TO PROCESS')
		print('...................................................') 						
		
def uninstall_content():	
	retrieve_installed()
	installed=get_gamelist()
	print("  * Entering File Picker")
	title = 'Select content to uninstall: \n + Press space or right to select content \n + Press E to finish selection'
	options=installed
	picker = Picker(options, title, multi_select=True, min_selection_count=1)
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection)
	selected=picker.start()
	if selected[0]==False:
		print("    User didn't select any files")
		return False	
	print("  * Starting uninstalling process...")
	counter=len(selected)	
	for file in selected:	
		process=subprocess.Popen([nscb_mtp,"DeleteID","-ID",file[0]])	
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();				
		counter-=1		
		print('...................................................')
		print('STILL '+str(counter)+' FILES TO PROCESS')
		print('...................................................') 		
	