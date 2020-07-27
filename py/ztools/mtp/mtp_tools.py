import os
from listmanager import folder_to_list
from listmanager import parsetags
from pathlib import Path
import Print
import shutil
from mtp.wpd import is_switch_connected
import sys
import subprocess
from python_pick import pick
from python_pick import Picker

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
autoloader_files_cache=os.path.join(cachefolder, 'autoloader_files.txt')
sd_xci_cache=os.path.join(cachefolder, 'sd_xci.txt')
valid_saves_cache=os.path.join(cachefolder, 'valid_saves.txt')
mtp_source_lib=os.path.join(zconfig_dir,'mtp_source_libraries.txt')
mtp_internal_lib=os.path.join(zconfig_dir,'mtp_SD_libraries.txt')
storage_info=os.path.join(cachefolder, 'storage.csv')
download_lib_file = os.path.join(zconfig_dir, 'mtp_download_libraries.txt')
sx_autoloader_db=os.path.join(zconfig_dir, 'sx_autoloader_db')

def gen_sx_autoloader_files_menu():
	print('***********************************************')
	print('SX AUTOLOADER GENERATE FILES FROM HDD OR FOLDER')
	print('***********************************************')
	print('')
	folder=input("Input a drive path: ")
	if not os.path.exists(folder):
		sys.exit("Can't find location")
	title = 'Target for autoloader files: '	
	options = ['HDD','SD']		
	selected = pick(options, title, min_selection_count=1)
	if selected[0]=='HDD':
		type='hdd'
	else:
		type='sd'
	title = 'Push files after generation?: '		
	options = ['YES','NO']			
	selected = pick(options, title, min_selection_count=1)
	if selected[0]=='YES':
		push=True
	else:
		push=False
	title = "Ensure files can't colide after transfer?: "		
	options = ['YES','NO']			
	selected = pick(options, title, min_selection_count=1)		
	if selected[0]=='YES':
		no_colide=True
	else:
		no_colide=False
	gen_sx_autoloader_files(folder,type=type,push=push,no_colide=no_colide)	
		
def gen_sx_autoloader_files(folder,type='hdd',push=False,no_colide=False):
	gamelist=folder_to_list(folder,['xci','xc0'])
	if type=='hdd':
		SD_folder=os.path.join(sx_autoloader_db, 'hdd')
	else:
		SD_folder=os.path.join(sx_autoloader_db, 'sd')
	if not os.path.exists(sx_autoloader_db):
		os.makedirs(sx_autoloader_db)		
	if not os.path.exists(SD_folder):
		os.makedirs(SD_folder)		
	for f in os.listdir(SD_folder):
		fp = os.path.join(SD_folder, f)
		try:
			shutil.rmtree(fp)
		except OSError:
			os.remove(fp)	
	print('  * Generating autoloader files')
	try:
		for g in gamelist:	
			try:
				fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(g)	
				if fileid=='unknown':
					continue
				tfile=os.path.join(SD_folder,fileid)
				fileparts=Path(g).parts
				if type=='hdd':
					new_path=g.replace(fileparts[0],'"usbhdd:/')
				else:
					new_path=g.replace(fileparts[0],'"sdmc:/')
				new_path=new_path.replace('\\','/')
				with open(tfile,'w') as text_file:
					text_file.write(new_path)
			except:pass		
		print('    DONE')
		if push==True:	
			if not is_switch_connected():
				sys.exit("Can't push files. Switch device isn't connected.\nCheck if mtp responder is running!!!")		
			print('  * Pushing autoloader files')	
			if type=='hdd':			
				destiny="1: External SD Card\\sxos\\titles\\00FF0012656180FF\\cach\\hdd"
			else:
				destiny="1: External SD Card\\sxos\\titles\\00FF0012656180FF\\cach\\sd"
			process=subprocess.Popen([nscb_mtp,"TransferFolder","-ori",SD_folder,"-dst",destiny,"-fbf","true"])
			while process.poll()==None:
				if process.poll()!=None:
					process.terminate();	
		if no_colide==True:
			cleanup_sx_autoloader_files()
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		pass

def cleanup_sx_autoloader_files():
	from mtp_game_manager import retrieve_xci_paths
	from mtp_game_manager import get_gamelist	
	try:			
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)	
	except:pass		
	if not is_switch_connected():
		sys.exit("Can't push files. Switch device isn't connected.\nCheck if mtp responder is running!!!")			
	retrieve_xci_paths()			
	print("  * Retriving autoloader files in device. Please Wait...")			
	process=subprocess.Popen([nscb_mtp,"Retrieve_autoloader_files","-tfile",autoloader_files_cache,"-show","false"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();	
	if os.path.exists(autoloader_files_cache):	
		print("    Success")
	else:
		sys.exit("Autoloader files weren't retrieved properly")
	gamelist=get_gamelist(file=sd_xci_cache)		
	autoloader_list=get_gamelist(file=autoloader_files_cache)	
	sd_xci_ids=[]
	for g in gamelist:
		try:
			fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(g)	
			sd_xci_ids.append(fileid)	
		except:pass	
	files_to_remove=[]
	for f in autoloader_list:
		fileparts=Path(f).parts
		if 'sdd' in fileparts and not (fileparts[-1] in sd_xci_ids): 	
			files_to_remove.append(f)		
		elif 'hdd' in fileparts and (fileparts[-1] in sd_xci_ids):
			files_to_remove.append(f)
	print("  * The following files will be removed")		
	for f in files_to_remove:
		print("    - "+f)
	for f in files_to_remove:			
		process=subprocess.Popen([nscb_mtp,"DeleteFile","-fp",f])
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();	
				
def push_sx_autoloader_libraries():
	if not is_switch_connected():
		sys.exit("Can't push files. Switch device isn't connected.\nCheck if mtp responder is running!!!")		
	title = "Ensure files can't colide after transfer?: "		
	options = ['YES','NO']				
	selected = pick(options, title, min_selection_count=1)		
	if selected[0]=='YES':
		no_colide=True
	else:
		no_colide=False				
	print('  * Pushing autoloader files in hdd folder')			
	HDD_folder=os.path.join(sx_autoloader_db, 'hdd')
	destiny="1: External SD Card\\sxos\\titles\\00FF0012656180FF\\cach\\hdd"
	process=subprocess.Popen([nscb_mtp,"TransferFolder","-ori",HDD_folder,"-dst",destiny,"-fbf","true"])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();		
	print('  * Pushing autoloader files in SD folder')					
	SD_folder=os.path.join(sx_autoloader_db, 'sd')		
	destiny="1: External SD Card\\sxos\\titles\\00FF0012656180FF\\cach\\sd"
	process=subprocess.Popen([nscb_mtp,"TransferFolder","-ori",SD_folder,"-dst",destiny,"-fbf","true"])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
	if no_colide==True:
		cleanup_sx_autoloader_files()	
						
def get_nca_ticket(filepath,nca):
	import Fs
	from binascii import hexlify as hx, unhexlify as uhx
	if filepath.endswith('xci') or filepath.endswith('xcz'):
		f = Fs.Xci(filepath)
		check=False;titleKey=0
		for nspF in f.hfs0:
			if str(nspF._path)=="secure":
				for file in nspF:	
					if (file._path).endswith('.tik'):
						titleKey = file.getTitleKeyBlock().to_bytes(16, byteorder='big')
						check=f.verify_key(nca,str(file._path))
						if check==True:
							break
		return check,titleKey		
	elif filepath.endswith('nsp') or filepath.endswith('nsz'):
		f = Fs.Nsp(filepath)	
		check=False;titleKey=0
		for file in f:	
			if (file._path).endswith('.tik'):
				titleKey = file.getTitleKeyBlock().to_bytes(16, byteorder='big')
				check=f.verify_key(nca,str(file._path))
				if check==True:
					break
	return check,titleKey		