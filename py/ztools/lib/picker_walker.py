import os
import string
from shutil import disk_usage
from python_pick import pick
from python_pick import Picker
import listmanager
import os
import shutil
from secondary import clear_Screen
from Interface import About
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
	title = 'Pick folder:\n + Press space or right to select content \n + Press E to move to file selection fase (Shows files in current folder) \n + Press R to move to file selection fase (Shows files recursevely including subfolders) \n + Press X to exit selection'
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