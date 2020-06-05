import os
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
					dict={}
					for j in range(len(csvheader)):
						try:
							dict[csvheader[j]]=row[j]
						except:
							dict[csvheader[j]]=None
					db[row[0]]=dict
		# print(db)			
		return db
	except: 
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
	
	
	
	
	
	
	
	
	