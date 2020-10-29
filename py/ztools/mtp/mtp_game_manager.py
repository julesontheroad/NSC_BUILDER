import Print
import os
import shutil
import json
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
import sq_tools

import Keys
import sys
import subprocess
from mtp.wpd import is_switch_connected
import listmanager
import csv
import time
from secondary import clear_Screen
from python_pick import pick
from python_pick import Picker

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
sd_xci_cache=os.path.join(cachefolder, 'sd_xci.txt')
valid_saves_cache=os.path.join(cachefolder, 'valid_saves.txt')
mtp_source_lib=os.path.join(zconfig_dir,'mtp_source_libraries.txt')
mtp_internal_lib=os.path.join(zconfig_dir,'mtp_SD_libraries.txt')
storage_info=os.path.join(cachefolder, 'storage.csv')
download_lib_file = os.path.join(zconfig_dir, 'mtp_download_libraries.txt')
sx_autoloader_db=os.path.join(zconfig_dir, 'sx_autoloader_db')
xci_locations=os.path.join(zconfig_dir, 'mtp_xci_locations.txt')

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

def retrieve_installed():
	check_connection()
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

def retrieve_registered():
	check_connection()
	try:
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)
	except:pass
	print("1. Retrieving registered...")
	dbicsv=os.path.join(cachefolder,"registered.csv")
	process=subprocess.Popen([nscb_mtp,"Download","-ori","4: Installed gamesInstalledApplications.csv","-dst",dbicsv],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
	if os.path.exists(dbicsv):
		print("   Success")
	else:
		sys.exit("Couldn't retrieved Game Registry")
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
	return dbi_dict

def retrieve_xci_paths():
	check_connection()
	try:
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)
	except:pass
	print("  * Parsing games in device. Please Wait...")
	process=subprocess.Popen([nscb_mtp,"Retrieve_XCI_paths","-tfile",sd_xci_cache,"-show","false","-exci","false","-xci_lc",xci_locations],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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
			try:
				entry=listmanager.parsetags(g)
				entry=list(entry)
				entry.append(g)
				installed[entry[0]]=entry
			except:pass
	return installed

def get_gamelist(dosort=True,file=games_installed_cache):
	gamelist=[]
	if os.path.exists(file):
		gamelist=listmanager.read_lines_to_list(file,all=True)
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
		return "SD"
	options = [x for x in db.keys()]
	selected = pick(options, title,min_selection_count=1)
	path=(db[selected[0]])['path']
	return path

def transfer(filepath=None,destiny="SD",):
	check_connection()
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
	check_connection()
	if not os.path.exists(tfile):
		sys.exit(f"Couldn't find {tfile}")
	destiny=pick_transfer_folder()
	file_list=listmanager.read_lines_to_list(tfile,all=True)
	for item in file_list:
		transfer(filepath=item,destiny=destiny)
		print("")
		listmanager.striplines(tfile,counter=True)

def gen_sx_autoloader_sd_files():
	check_connection()
	retrieve_xci_paths()
	gamelist=get_gamelist(file=sd_xci_cache)
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
	print('  * Genereting autoloader files')
	for g in gamelist:
		try:
			fileid,fileversion,cctag,nG,nU,nD,baseid=listmanager.parsetags(g)
			tfile=os.path.join(SD_folder,fileid)
			new_path=g.replace('\\1: External SD Card\\','sdmc:/')
			new_path=new_path.replace('\\','/')
			with open(tfile,'w') as text_file:
				text_file.write(new_path)
		except:pass
	print('  * Pushing autoloader files')
	destiny="1: External SD Card\\sxos\\titles\\00FF0012656180FF\\cach\\sd"
	process=subprocess.Popen([nscb_mtp,"TransferFolder","-ori",SD_folder,"-dst",destiny,"-fbf","true"])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();


def dump_content():
	check_connection()
	retrieve_installed()
	installed=get_gamelist()
	print("  * Entering File Picker")
	title = 'Select content to dump: \n + Press space or right to select content \n + Press Enter or Intro to accept selection \n + Press E to exit selection'
	options=installed
	picker = Picker(options, title, multi_select=True, min_selection_count=1)
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection);picker.register_custom_handler(ord('E'),  end_selection)
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
	check_connection()
	retrieve_installed()
	installed=get_gamelist()
	print("  * Entering File Picker")
	title = 'Select content to uninstall: \n + Press space or right to select content \n + Press E to finish selection'
	options=installed
	picker = Picker(options, title, multi_select=True, min_selection_count=1)
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection);picker.register_custom_handler(ord('E'),  end_selection)
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

def delete_archived():
	check_connection()
	retrieve_installed()
	installed=get_gamelist()
	registered=retrieve_registered()
	for game in installed:
		try:
			fileid,fileversion,cctag,nG,nU,nD,baseid=listmanager.parsetags(game)
			try:
				del registered[fileid]
			except:pass
		except:pass
	games=[]
	# Name [version][title]
	for k in registered.keys():
		games.append(f"{(registered[k])[2]} [{(registered[k])[0]}][{(registered[k])[1]}]")
	print("  * Entering File Picker")
	if not games:
		sys.exit("There isn't any archived games or placeholder on the device")
	title = 'Select registries to delete: \n + Press space or right to select entries \n + Press E to finish selection \n + Press A to select all entries'
	options=games
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
	print("  * Starting uninstalling process...")
	arch2delete=[]
	if selected[0]=="ALL":
		for k in registered:
			g0=(registered[k])[2]
			arch2delete.append(g0)
	else:
		for game in selected:
			g=game[0]
			g0=[pos for pos, char in enumerate(g) if char == '[']
			g0=(g[0:g0[0]]).strip()
			arch2delete.append(g0)
	counter=len(arch2delete)
	for file in arch2delete:
		process=subprocess.Popen([nscb_mtp,"DeleteRegistry","-ID",file])
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();
		counter-=1
		print('...................................................')
		print('STILL '+str(counter)+' FILES TO PROCESS')
		print('...................................................')

def back_up_saves(backup_all=False,inline=False,tidandver=True,romaji=True,outfolder=None,onlyInstalled=False):
	check_connection()
	import zipfile
	from datetime import datetime
	if outfolder=="":
		outfolder=None
	try:
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)
	except:pass
	if outfolder==None:
		outfolder=pick_download_folder()
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	if onlyInstalled==True:
		process=subprocess.Popen([nscb_mtp,"ShowSaveGames","-saves",valid_saves_cache,"-show","False","-oinst","True"])
	else:
		process=subprocess.Popen([nscb_mtp,"ShowSaveGames","-saves",valid_saves_cache,"-show","False","-oinst","False"])
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
	if not os.path.exists(valid_saves_cache):
		sys.exit("Savegames couldn't be retrieved")
	valid_saves=[];options=[]
	with open(valid_saves_cache,'rt',encoding='utf8') as tfile:
		for line in tfile:
			valid_saves.append(line.strip())
			if line.startswith("Installed games\\"):
				line=line.replace("Installed games\\","")
				options.append(line.strip())
			elif line.startswith("Uninstalled games\\"):
				line=line.replace("Uninstalled games\\","")
				options.append(line.strip())
	if backup_all==False:
		title = 'Select saves to backup: \n + Press space or right to select content \n + Press E to finish selection'
		picker = Picker(options, title, multi_select=True, min_selection_count=1)
		def end_selection(picker):
			return False,-1
		picker.register_custom_handler(ord('e'),  end_selection);picker.register_custom_handler(ord('E'),  end_selection)
		selected=picker.start()
		if selected[0]==False:
			print("    User didn't select any games")
			return False
	else:
		selected=[]
		for i in range(len(valid_saves)):
			selected.append([valid_saves[i],i])
	print("- Retrieving registered to get TitleIDs...")
	dbicsv=os.path.join(cachefolder,"registered.csv")
	process=subprocess.Popen([nscb_mtp,"Download","-ori","4: Installed gamesInstalledApplications.csv","-dst",dbicsv],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while process.poll()==None:
		if process.poll()!=None:
			process.terminate();
	if os.path.exists(dbicsv):
		print("   Success")
	if tidandver==True:
		dbi_dict={}
		with open(dbicsv,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			id=0;ver=1;tname=2;
			for row in readCSV:
				version=0;
				try:
					tid=(str(row[id]).upper())[2:]
					tid=tid[:-3]+'000'
					version=int(row[ver])
					name=str(row[tname])
					if name in dbi_dict:
						if version<((dbi_dict[name])['version']):
							continue
					dbi_dict[name]={'tid':tid,'version':version,'name':name}
				except BaseException as e:
					Print.error('Exception: ' + str(e))
					return False
	counter=len(selected)
	for file in selected:
		if tidandver==True:
			print(f'- Searching "{file[0]}" in registered data')
			titleid="";version=""
			name=file[0]
			if name.startswith("Installed games\\"):
				name=name.replace("Installed games\\","")
			elif name.startswith("Uninstalled games\\"):
				name=name.replace("Uninstalled games\\","")
			try:
				titleid=((dbi_dict[name])['tid'])
				titleid=f'[{titleid}]'
				version=str((dbi_dict[file[0]])['version'])
				version=f'[v{version}]'
			except:
				pass
			game=f"{name} {titleid}{version}"
		else:
			name=file[0]
			if name.startswith("Installed games\\"):
				name=name.replace("Installed games\\","")
			elif name.startswith("Uninstalled games\\"):
				name=name.replace("Uninstalled games\\","")
			game=f"{name}"
		game=sanitize(game,romaji)
		if inline==False:
			dmpfolder=os.path.join(outfolder,game)
		else:
			dmpfolder=outfolder
		tmpfolder=os.path.join(dmpfolder,'tmp')
		if not os.path.exists(dmpfolder):
			os.makedirs(dmpfolder)
		if not os.path.exists(tmpfolder):
			os.makedirs(tmpfolder)
		process=subprocess.Popen([nscb_mtp,"BackSaves","-sch",file[0],"-dst",tmpfolder])
		while process.poll()==None:
			if process.poll()!=None:
				process.terminate();
		counter-=1
		subfolders = [ f.path for f in os.scandir(tmpfolder) if f.is_dir() ]
		for folder in subfolders:
			dname=os.path.basename(folder)
			timedate = datetime.now()
			timedate = timedate.strftime("[%Y.%m.%d @ %H.%M.%S]")
			zipname=f"{game}{timedate}[{dname}].zip"
			output=os.path.join(dmpfolder,zipname)
			print(f"- Zipping {folder} to {output}")
			file_list=listmanager.folder_to_list(folder,extlist='all')
			if not file_list:
				continue
			z = zipfile.ZipFile(output, "w",zipfile.ZIP_DEFLATED)
			basedir=os.path.dirname(folder)
			for dirpath, dirnames, filenames in os.walk(folder):
				for filename in filenames:
					filePath = os.path.join(dirpath, filename)
					dirname = filePath.replace(folder,'')
					dirname=dirname[0:]
					if os.path.isfile(filePath):
						z.write(filePath, dirname)
			z.close()
		try:
			shutil.rmtree(tmpfolder, ignore_errors=True)
		except: pass
		print('...................................................')
		print('STILL '+str(counter)+' FILES TO PROCESS')
		print('...................................................')

def sanitize(filename,roma=True):
	import re
	filename = (re.sub(r'[\/\\\:\*\?]+', '', filename))
	filename = re.sub(r'[™©®`~^´ªº¢#£€¥$ƒ±¬½¼♡«»±•²‰œæÆ³☆<<>>|]', '', filename)
	filename = re.sub(r'[Ⅰ]', 'I', filename);filename = re.sub(r'[Ⅱ]', 'II', filename)
	filename = re.sub(r'[Ⅲ]', 'III', filename);filename = re.sub(r'[Ⅳ]', 'IV', filename)
	filename = re.sub(r'[Ⅴ]', 'V', filename);filename = re.sub(r'[Ⅵ]', 'VI', filename)
	filename = re.sub(r'[Ⅶ]', 'VII', filename);filename = re.sub(r'[Ⅷ]', 'VIII', filename)
	filename = re.sub(r'[Ⅸ]', 'IX', filename);filename = re.sub(r'[Ⅹ]', 'X', filename)
	filename = re.sub(r'[Ⅺ]', 'XI', filename);filename = re.sub(r'[Ⅻ]', 'XII', filename)
	filename = re.sub(r'[Ⅼ]', 'L', filename);filename = re.sub(r'[Ⅽ]', 'C', filename)
	filename = re.sub(r'[Ⅾ]', 'D', filename);filename = re.sub(r'[Ⅿ]', 'M', filename)
	filename = re.sub(r'[—]', '-', filename);filename = re.sub(r'[√]', 'Root', filename)
	filename = re.sub(r'[àâá@äå]', 'a', filename);filename = re.sub(r'[ÀÂÁÄÅ]', 'A', filename)
	filename = re.sub(r'[èêéë]', 'e', filename);filename = re.sub(r'[ÈÊÉË]', 'E', filename)
	filename = re.sub(r'[ìîíï]', 'i', filename);filename = re.sub(r'[ÌÎÍÏ]', 'I', filename)
	filename = re.sub(r'[òôóöø]', 'o', filename);filename = re.sub(r'[ÒÔÓÖØ]', 'O', filename)
	filename = re.sub(r'[ùûúü]', 'u', filename);filename = re.sub(r'[ÙÛÚÜ]', 'U', filename)
	filename = re.sub(r'[’]', "'", filename);filename = re.sub(r'[“”]', '"', filename)
	filename = re.sub(' {3,}', ' ',filename);re.sub(' {2,}', ' ',filename);
	filename = filename.replace("( ", "(");filename = filename.replace(" )", ")")
	filename = filename.replace("[ ", "[");filename = filename.replace(" ]", "]")
	filename = filename.replace("[ (", "[(");filename = filename.replace(") ]", ")]")
	filename = filename.replace("[]", "");filename = filename.replace("()", "")
	filename = filename.replace('" ','"');filename = filename.replace(' "','"')
	filename = filename.replace(" !", "!");filename = filename.replace(" ?", "?")
	filename = filename.replace("  ", " ");filename = filename.replace("  ", " ")
	filename = filename.replace('"', '');
	filename = filename.replace(')', ') ');filename = filename.replace(']', '] ')
	filename = filename.replace("[ (", "[(");filename = filename.replace(") ]", ")]")
	filename = filename.replace("  ", " ")
	if roma==True:
		converter = kakashi_conv()
		filename=converter.do(filename)
	filename.strip()
	return filename

def kakashi_conv():
	import pykakasi
	kakasi = pykakasi.kakasi()
	kakasi.setMode("H", "a")
	kakasi.setMode("K", "a")
	kakasi.setMode("J", "a")
	kakasi.setMode("s", True)
	kakasi.setMode("E", "a")
	kakasi.setMode("a", None)
	kakasi.setMode("C", False)
	converter = kakasi.getConverter()
	return converter
