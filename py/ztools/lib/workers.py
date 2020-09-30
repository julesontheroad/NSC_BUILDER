import os
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed as completedfuture
from ast import literal_eval
try:
	import ujson as json
except:
	import json
import subprocess
import Print


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
	
local_lib_file = os.path.join(zconfig_dir, 'local_libraries.txt')
remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
download_lib_file = os.path.join(zconfig_dir, 'download_libraries.txt')
web_folder=os.path.join(ztools_dir,'web')
debug_folder=os.path.join(web_folder,'_debug_')
if not os.path.exists(debug_folder):
	os.makedirs(debug_folder)
cache_folder=os.path.join(web_folder,'_cache_')
if not os.path.exists(cache_folder):
	os.makedirs(cache_folder)
local_cache_folder=os.path.join(cache_folder,'_locallib_')
if not os.path.exists(local_cache_folder):
	os.makedirs(local_cache_folder)
remote_cache_folder=os.path.join(cache_folder,'_remotelib_')
if not os.path.exists(remote_cache_folder):
	os.makedirs(remote_cache_folder)

remote_lib_cache=os.path.join(zconfig_dir, 'remote_lib_cache')	
if not os.path.exists(remote_lib_cache):
	os.makedirs(remote_lib_cache)

	
def back_check_files():		
	templog=os.path.join(debug_folder,'temp.txt')
	import sys	
	sys.stdout = open(templog, 'w')
	sys.stderr = sys.stdout
	import nutdb
	nutdb.check_files()
	sys.stdout=open(os.devnull, 'w')
	sys.stderr=sys.stdout
	os.remove(templog)
	
def libraries(tfile):
	import csv
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
		
def sortbyname(files):
	results={};
	for f in files:
		k=str(os.path.basename(os.path.abspath(f)))
		results[k]=f
	return results		
	
def scrape_local_libs(): 
	from listmanager import folder_to_list
	db=libraries(local_lib_file)	
	if db==False:	
		return
	results=[]	
	for entry in db:
		path=db[entry]['path']	
		res=folder_to_list(path,'all')	
		results+=res	
		local_lib_2html(entry,res)
	local_lib_2html('all',results)	
		
def local_lib_2html(entry,results):		
	sr=sortbyname(results)	
	html='<ul style="margin-bottom: 2px;margin-top: 3px; list-style-type: none;">'	
	i=0		
	for it in sorted(sr.keys()):
		i+=1;type=''
		item=sr[it]
		item2='&nbsp'+it
		if item2.endswith('.nsp'):
			type='<span class="bg-darkBlue fg-white">&nbspnsp&nbsp</span>'	
		elif item2.endswith('.xci'):
			type='<span class="bg-darkRed fg-white">&nbspxci&nbsp&nbsp</span>'					
		var='local_res_'+str(i)
		html+='<li style="margin-bottom: 2px;margin-top: 3px" onclick="start_from_library({})"><span id="{}" style="display:none">{}</span>{}<strong>{}</strong></li>'.format(var,var,item,type,item2)
	html+='</ul>'			
	cachefile=os.path.join(local_cache_folder,entry)
	with open(cachefile,'wt',encoding='utf8') as file:
		file.write(html)
	

def scrape_remote_libs(): 
	db=libraries(remote_lib_file)	
	if db==False:	
		return
	results=[];		
	for entry in db:	
		path=db[entry]['path']
		TD=db[entry]['TD_name']	
		from Drive import Private as DrivePrivate
		response=DrivePrivate.search_folder(path,TD=TD,filter="",Pick=False)
		if response!=False:
			results+=response	
			remote_lib_2html(entry,response)
	remote_lib_2html('all',results)				
	
def remote_lib_2html(libname,results):			
	send_results=[]
	try:
		for entry in results:
			send_results.append('{}/{}'.format(entry[2],entry[0]))
		sr=sortbyname(send_results)
	except:pass		
	html='<ul style="margin-bottom: 2px;margin-top: 3px; list-style-type: none;">'	
	i=0
	for it in sorted(sr.keys()):
		i+=1;type=''
		item=sr[it]
		item2='&nbsp'+it
		if item2.endswith('.nsp'):
			type='<span class="bg-darkBlue fg-white">&nbspnsp&nbsp</span>'
		elif item2.endswith('.xci'):
			type='<span class="bg-darkRed fg-white">&nbspxci&nbsp&nbsp</span>'
		var='remote_res_'+str(i)
		html+='<li style="margin-bottom: 2px;margin-top: 3px" onclick="start_from_remote_library({})"><span id="{}" style="display:none">{}</span>{}<strong>{}</strong></li>'.format(var,var,item,type,item2)
	html+='</ul>'		
	cachefile=os.path.join(remote_cache_folder,libname)
	with open(cachefile,'wt',encoding='utf8') as file:
		file.write(html)	

def scrape_lib_worker(db,entry,filter=''): 
	results=[];		
	path=db[entry]['path']
	TD=db[entry]['TD_name']	
	from Drive import Private as DrivePrivate
	response=DrivePrivate.search_folder(path,TD=TD,filter=filter,Pick=False)
	if response!=False:
		results+=response	
	return results
		
def concurrent_scrapper(filter='',order='name_ascending',remotelib='all',db=False):
	if db==False:
		db=libraries(remote_lib_file)	
	else:
		db=db
	checks=[]
	if db==False:	
		return	
	if isinstance(remotelib, list):
		for item in remotelib:
			if item in db.keys():
				checks.append(item)		
	elif remotelib=='all':
		checks=db.keys()
	else:
		if remotelib in db.keys():
			checks.append(remotelib)
	# elif literal_eval(remotelib)	
	with ThreadPoolExecutor(max_workers=8) as executor:
		# future = executor.map(scrape_lib_worker,db.keys())
		futures = {executor.submit(scrape_lib_worker,db,entry,filter): entry for entry in checks}
	items=[]		
	for future in completedfuture(futures):
		for res in future.result():
			items.append(res)		
	if order=='name_ascending':
		items.sort(key=lambda x: x[0])
	elif order=='name_descending':	
		(items.sort(key=lambda x: x[0]))
		items.reverse()
	elif order=='size_ascending':
		items.sort(key=lambda x: x[1])		
	elif order=='size_descending':	
		(items.sort(key=lambda x: x[1]))
		items.reverse()	
	elif order=='date_ascending':
		items.sort(key=lambda x: x[3])		
	elif order=='date_descending':	
		(items.sort(key=lambda x: x[3]))
		items.reverse()				
	# for item in items:
		# print(item[0])
	return items

def concurrent_cache():
	filter='';jlib=None
	db=libraries(remote_lib_file)	
	checks=db.keys()
	with ThreadPoolExecutor(max_workers=8) as executor:
		# future = executor.map(scrape_lib_worker,db.keys())
		futures = {executor.submit(scrape_lib_worker,db,entry,filter): entry for entry in checks}
		for future in completedfuture(futures):
			c=0;jdict={}
			for res in future.result():
				if c==0:
					lib,TD,libpath=get_library_from_path(filename=res[2])
					jname=f"{lib}.json"
					jlib=os.path.join(remote_lib_cache,jname)
					c+=1	
					print(f"- Writing {lib} to {jlib}")
				filepath=f"{res[2]}/{res[0]}"
				entry={'library':lib,'TD':TD,'library_path':res[2],'filepath':filepath,'size':res[1],'date':res[3],'id':res[4]}	
				jdict[res[0]]=entry	
			if jlib!=None:	
				app_json = json.dumps(jdict, indent=2)					
				with open(jlib, 'w') as json_file:
				  json_file.write(app_json)	

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

def romaji(filename):	
	converter = kakashi_conv()
	filename=converter.do(filename)	
	return filename
	
def concurrent_romaji(filenames,workers=20):
	with ThreadPoolExecutor(max_workers=workers) as executor:
		future = executor.map(romaji,filenames)
	return future	
	
	
def get_library_from_path(tfile=None,filename=None):
	if tfile==None:
		db=libraries(remote_lib_file)
	else:
		db=libraries(tfile)		
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
	
	