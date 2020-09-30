import os
import string
from shutil import disk_usage
from python_pick import pick
from python_pick import Picker
import listmanager
import os
import shutil
from secondary import clear_Screen
import csv
try:
	import ujson as json
except:
	import json
	
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
local_libraries=os.path.join(zconfig_dir,'local_libraries.txt')
remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
remote_lib_cache=os.path.join(zconfig_dir, 'remote_lib_cache')	
cache_lib_file= os.path.join(zconfig_dir, 'remote_cache_location.txt')

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
		return db			
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		return False	
		
def get_library_from_path(tfile=None,filename=None):
	if tfile==None:
		db=libraries(remote_lib_file)
	else:
		db=libraries(tfile)		
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

def get_disks():
	available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
	for d in available_drives:
		dsktotal, dskused, dskfree=disk_usage(str(d))	
		if int(dsktotal)==0:
			available_drives.remove(d)
	title = 'Pick drive: \n + Press enter or intro to select \n + Press E to scape back to menu'
	options = available_drives
	picker = Picker(options, title, min_selection_count=1)	
	def end_selection(picker):
		return False,-1	
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)		
	selected = picker.start()	
	if selected[0]==False:
		return False
	drive=selected[0]
	return drive	
		
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

def pick_folder(folders,previous):
	Recursive=False
	title = 'Pick folder:\n + Press space or right to select content \n + Press E to move to file selection phase (Shows files in current folder) \n + Press R to move to file selection phase (Shows files recursevely including subfolders) \n + Press X to exit selection'
	options = folders
	picker = Picker(options, title, min_selection_count=1)	
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)	
	def end_selection_recursive(picker):
		return True,-1
	picker.register_custom_handler(ord('r'),  end_selection_recursive)
	picker.register_custom_handler(ord('R'),  end_selection_recursive)	
	def exit_selection(picker):
		return "EXIT",-1
	picker.register_custom_handler(ord('x'),  exit_selection)
	picker.register_custom_handler(ord('X'),  exit_selection)		
	selected=picker.start()	
	if selected[0]==False:
		return False,False
	if selected[0]=="EXIT":		
		return "EXIT",False
	if selected[0]==True:		
		return False,True		
	folder=os.path.join(previous,selected[0])		
	return 	folder,Recursive
	
def folder_walker():
	Recursive=False
	folder=get_disks()
	if folder==False:
		return	False,False			
	while True:
		folders=next(os.walk(folder))[1]	
		if not folders:
			break
		choice,Recursive=pick_folder(folders,folder)
		if choice==False:
			break
		if choice=="EXIT":
			return False,False	
		folder=choice
	return folder,Recursive	

def get_files_from_walk(tfile=None,extlist=['nsp','nsz','xci','xcz'],filter=False,recursive=False,doPrint=False):
	if not isinstance(extlist, list): 
		if str(extlist).lower()!='all':
			ext=extlist.split()
			extlist=[]			
			for x in ext:
				extlist.append(x)			
	folder,rec=folder_walker()
	if folder==False:
		return False	
	if rec==True:
		recursive=True
	print("Parsing files. Please wait...")
	title = 'Add a search filter?: '
	options = ['Yes','No']	
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	if response=='No':
		pass
	else:
		clear_Screen()
		About()
		filter=input('INPUT SEARCH FILTER: ')	
	if recursive==False:	
		files=listmanager.nextfolder_to_list(folder,extlist=extlist,filter=filter)
	else:
		files=listmanager.folder_to_list(folder,extlist=extlist,filter=filter)		
	if not files:
		sys.exit("Query didn't return any files")
	order=pick_order()
	if order==False:
		return False	
	filedata={}
	for file in files:
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
	title = 'Select content: \n + Press space or right to select entries \n + Press Enter to confirm selection \n + Press E to exit selection \n + Press A to select all entries'				
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
		print("User didn't select any files")
		return False					
	newgpaths=[]
	if selected[0]=="ALL":	
		for game in options:	
			newgpaths.append(os.path.join(folder,game))		
	else:	
		for game in selected:
			newgpaths.append(os.path.join(folder,game[0]))
	if tfile!=None:		
		with open(tfile,'w', encoding='utf8') as textfile:
			for i in newgpaths:
				textfile.write((i).strip()+"\n")		
	if doPrint!=False:
		for i in newgpaths:
			print(i)
	return newgpaths
	
def get_libs(lib="local"):
	libraries={}
	if lib=="local":
		libtfile=local_libraries
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
	
def search_with_filter(folder_paths,extlist=['nsp','nsz','xci','xcz']):
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
	
def select_from_local_libraries(tfile=None,extlist=['nsp','nsz','xci','xcz']):				
	if not os.path.exists(local_libraries):
		sys.exit("Missing local_libraries.txt")	
	if not isinstance(extlist, list): 
		if str(extlist).lower()!='all':
			ext=extlist.split()
			extlist=[]			
			for x in ext:
				extlist.append(x)		
	db=get_libs()
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
	filepaths=search_with_filter(folder_paths,extlist)
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
	if tfile!=None:	
		with open(tfile,'a') as  textfile:		
			for f in selected:
				fpath=(filedata[f[0]])['filepath']		
				textfile.write(fpath+'\n')	
	else:
		filespaths=[]
		for f in selected:
			fpath=(filedata[f[0]])['filepath']		
			filespaths.append(fpath)		
		return filespaths	
		
def remote_interface_filter(path=None):
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
		
def remote_interface_filter_local(filelist):
	title = 'Add a search filter?: '
	options = ['Yes','No']	
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	if response=='No':
		return filelist
	else:
		clear_Screen()
		About()
		ck=input('INPUT SEARCH FILTER: ')
		filelist=listmanager.filter_vlist(filelist,token=ck,Print=False)
	return filelist		

def eval_link(tfile,userfile):
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
			
def drive_pick_libraries():
	title = 'Select libraries to search:  \n + Press space or right to select content \n + Press E to finish selection'
	db=libraries(remote_lib_file)
	if db==False:
		return False,False
	options = [x for x in db.keys()]
	picker = Picker(options, title,multi_select=True,min_selection_count=1)	
	def end_selection(picker):
		return False,-1		
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)
	selected = picker.start()	
	if selected[0]==False:
		return False,False	
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
			
def remote_select_from_libraries(tfile):	
	from workers import concurrent_scrapper
	db=libraries(remote_lib_file)
	if db==False:
		sys.exit(f"Missing {remote_lib_file}")
	paths,TDs=drive_pick_libraries()
	if paths==False:
		return False	
	order=pick_order()
	if order==False:
		return False		
	filter=remote_interface_filter()	
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
	title = 'Select content to install or transfer: \n + Press space or right to select content \n + Press Enter to confirm selection \n + Press E to exit selection'
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
			fpath=(files[f[1]])[2]+'/'+(files[f[1]])[0]
			lib,TD,libpath=get_library_from_path(remote_lib_file,fpath)		
			try:
				ID=(files[f[1]])[4]
				textfile.write(f"{fpath}|{TD}|{ID}\n")
			except:	
				textfile.write(f"{fpath}|{TD}\n")

def remote_select_from_cache(tfile):	
	from workers import concurrent_scrapper
	cache_is_setup=False
	if not os.path.exists(remote_lib_cache):
		os.makedirs(remote_lib_cache)
	jsonlist=listmanager.folder_to_list(remote_lib_cache,extlist=['json'])	
	if not jsonlist:
		print("Cache wasn't found. Generating cache up...")
		from workers import concurrent_cache
		concurrent_cache()
	jsonlist=listmanager.folder_to_list(remote_lib_cache,extlist=['json'])			
	if not jsonlist:
		sys.exit("Can't setup remote cache. Are libraries set up?")
	libnames=[]
	for j in jsonlist:
		bname=os.path.basename(j) 
		bname=bname.replace('.json','')
		libnames.append(bname)
	title = 'Select libraries to search:  \n + Press space or right to select content \n + Press Enter to confirm selection \n + Press E to exit selection \n + Press A to select all libraries'
	db=libraries(remote_lib_file)
	options = libnames
	picker = Picker(options, title,multi_select=True,min_selection_count=1)	
	def end_selection(picker):
		return False,-1	
	def select_all(picker):
		return True,libnames
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)	
	picker.register_custom_handler(ord('a'),  select_all)
	picker.register_custom_handler(ord('A'),  select_all)	
	selected = picker.start()	
	if selected[0]==False:
		print("User didn't select any libraries")
		return False,False		
	if selected[0]==True:	
		cachefiles=jsonlist
	else:
		cachefiles=[]
		for entry in selected:
			fname=entry[0]+'.json'
			fpath=os.path.join(remote_lib_cache,fname)
			cachefiles.append(fpath)
	cachedict={}
	for cach in cachefiles:
		with open(cach) as json_file:					
			data = json.load(json_file)		
		for entry in data:
			if not entry in cachedict:
				cachedict[entry]=data[entry]
	# for k in cachedict.keys():
		# print(k)
	order=pick_order()
	if order==False:
		return False	
	options=[]	
	if order=='name_ascending':
		options=sorted(cachedict,key=lambda x:cachedict[x]['filepath'])
	elif order=='name_descending':	
		options=sorted(cachedict,key=lambda x:cachedict[x]['filepath'])
		options.reverse()
	elif order=='size_ascending':
		options=sorted(cachedict,key=lambda x:cachedict[x]['size'])
	elif order=='size_descending':	
		options=sorted(cachedict,key=lambda x:cachedict[x]['size'])
		options.reverse()	
	elif order=='date_ascending':
		options=sorted(cachedict,key=lambda x:cachedict[x]['date'])
	elif order=='date_descending':	
		options=sorted(cachedict,key=lambda x:cachedict[x]['date'])
		options.reverse()	
	options=remote_interface_filter_local(options)	
	print("  * Entering File Picker")	
	title = 'Select content to install or transfer: \n + Press space or right to select content \n + Press Enter to confirm selection \n + Press E to exit selection'
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
			fpath=(cachedict[f[0]])['filepath']
			TD=(cachedict[f[0]])['TD']
			try:
				ID=(cachedict[f[0]])['id']
				textfile.write(f"{fpath}|{TD}|{ID}\n")		
			except:
				textfile.write(f"{fpath}|{TD}\n")				

def remote_select_from_walker(tfile,types='all'):	
	from workers import concurrent_scrapper	
	from Drive import Private as DrivePrivate
	ext=[]
	if types!='all':
		items=types.split(' ')
		for x in items:
			ext.append(str(x).lower())	
	folder,TeamDrive=DrivePrivate.folder_walker()	
	if TeamDrive=="" or TeamDrive==False:
		TeamDrive=None
	if folder==False:
		return False
	filt=remote_interface_filter()			
	order=pick_order()
	if order==False:
		return False	
	print(f"- Checking {folder}")
	print("  * Parsing files from Google Drive. Please Wait...")		
	db={}
	db[folder]={'path':folder,'TD_name':TeamDrive}			
	files=concurrent_scrapper(filter=filt,order=order,remotelib='all',db=db)			
	if files==False:
		return False			
	print("  * Entering File Picker")	
	title = 'Select content to install or transfer: \n + Press space or right to select content \n + Press Enter to confirm selection \n + Press E to exit selection'
	filenames=[]
	for f in files:
		if types=='all':	
			filenames.append(f[0])
		else:
			for x in ext:
				if (str(f[0]).lower()).endswith(x):
					filenames.append(f[0])
					break
	if filenames==[]:
		print("  * Request didn't retrieve any files")
		return False
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
			fpath=(files[f[1]])[2]+'/'+(files[f[1]])[0]
			TD=str(TeamDrive)
			try:
				ID=(files[f[1]])[4]
				textfile.write(f"{fpath}|{TD}|{ID}\n")
			except:	
				textfile.write(f"{fpath}|{TD}\n")