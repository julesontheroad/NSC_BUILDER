import io
import _EEL_ as eel
import sq_tools
import Fs
import sys

import platform
if sys.platform in ['win32', 'win64']:
	import win32com.client 
from base64 import b64encode
try:
	import tkinter as tk
	from tkinter import filedialog
except:pass	
import sq_tools
import os
import ast
import Print
import nutdb
from subprocess import call 
import File_chunk2 as file_chunk
import csv
from listmanager import folder_to_list
import html

def About(noconsole=False):	
	if noconsole==True:
		print('NSC_Builder by JulesOnTheRoad')
		sys.stdout.flush()
		return
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
eel.init('web')

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
	
tmpfolder =os.path.join(NSCB_dir,'tmp')
chromiumpath=os.path.join(ztools_dir,'chromium')
chromiumpath_alt=os.path.join(squirrel_dir,'chromium')
if sys.platform in ['win32', 'win64']:
	slimjet='slimjet.exe'
	slimpath=os.path.join(chromiumpath,slimjet)
	slimpath_alt=os.path.join(chromiumpath_alt,slimjet)
	chrom='chrlauncher.exe'
	chromiumpath=os.path.join(chromiumpath,chrom)
	chromiumpath_alt=os.path.join(chromiumpath_alt,chrom)
else:
	chromiumdir=os.path.join(ztools_dir, 'chromium')
	chromiumpath=os.path.join(chromiumdir, 'chrome')	


local_lib_file = os.path.join(zconfig_dir, 'local_libraries.txt')
remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
cache_lib_file= os.path.join(zconfig_dir, 'remote_cache_location.txt')
download_lib_file = os.path.join(zconfig_dir, 'download_libraries.txt')
ssl_cert= os.path.join(zconfig_dir, 'certificate.pem')
ssl_key= os.path.join(zconfig_dir, 'key.pem')
web_folder=os.path.join(ztools_dir,'web')
debug_folder=os.path.join(web_folder,'_debug_')
flag_file=os.path.join(debug_folder,'flag')	
debug_log=os.path.join(debug_folder,'log')	
if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
	pass
else:
	ssl_cert=False;ssl_key=False

globalpath=None;globalTD=None;globalremote=None
globalocalpath=None
gl_current_local_lib='all';gl_current_remote_lib='all'
threads=[]
from Drive import Private as DrivePrivate
from Drive import DriveHtmlInfo
from Drive import Public as DrivePublic

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

def get_library_from_path(tfile,filename):
	db=libraries(remote_lib_file)
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
	
	
def deepcheck_path(path1,path2,accuracy=0.9):	
	path1=path1.lower()	
	path1 = list([val for val in path1 if val.isalnum()]) 
	path1 = "".join(path1) 			
	path2=path2.lower()	
	path2 = list([val for val in path2 if val.isalnum()]) 
	path2 = "".join(path2) 	
	ratio=SequenceMatcher(None, path1, path2).ratio()
	if ratio>=accuracy:
		return True
	else:
		return False
										
def  html_feed(feed='',style=1,message=''):	
	if style==1:
		feed+='<p style="font-size: 14px; justify;text-justify: inter-word;"><strong>{}</strong></p>'.format(message)	
		return feed
	if style==2:			
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 2vh"><strong>{}</strong></p>'.format(message)	
		return feed
	if style==3:				
		feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>{} </strong><span>{}</span></li>'.format(message[0],message[1])				
		return feed				
	if style==4:				
		feed+='<li style="margin-bottom: 2px;margin-top: 3px"><strong>{} </strong><span>{}. </span><strong>{} </strong><strong>{}</strong></li>'.format(message[0],message[1],message[2],message[3])				
		return feed	
	if style==5:			
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 2vh;text-indent:5vh";><strong style="text-indent:5vh;">{}</strong></p>'.format(message)	
		return feed	
	if style==6:			
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;";><strong>{}</strong></p>'.format(message)	
		return feed		
	if style==7:			
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;";><strong>{}</strong>{}</p>'.format(message[0],message[1])
		return feed		
	if style==8:			
		feed+='<p style="margin-bottom: 2px;margin-top: 2px;font-size: 1.8vh;">{}</p>'.format(message)
		return feed		
	if style==9:				
		feed+='<li style="margin-bottom: 2px;margin-top: 3px;list-style-type:none;"><strong>{} </strong><span>{}</span></li>'.format(message[0],message[1])	
		return feed					
	if style==10:				
		feed+='<li style="margin-bottom: 2px;margin-top: 3px;list-style-type:none;"><strong style=border-style: solid;>{} </strong><span>{}</span></li>'.format(message[0],message[1])	
		return feed				

def get_screen_gallery(banner,screenlist):
	try:	
		ret='<div class="grid"><div class="row"><div class="img-container thumbnail" style="width: auto;max-height:auto; margin-left: auto; margin-right: auto; display: block;" onclick="showimg()"><img src="{}" id="mainpicture" style="width: auto;max-height:63vh;"></div></div></div><div class="row">'.format(banner)
		banner1="'{}'".format(banner)
		ret+='<div class="cell" style="width: auto;max-height:5vh;"><div class="img-container thumbnail" onclick="setmainimage({})"><img src="{}"></div></div>'.format(banner1,banner)
		screenlist=ast.literal_eval(str(screenlist))
		if isinstance(screenlist, list):
			i=0
			for x in screenlist:
				x1="'{}'".format(x)
				ret+='<div class="cell"><div class="img-container thumbnail"  onclick="setmainimage({})"><img src="{}" id="gallerypicture{}"></div></div>'.format(x1,x,i)
				i+=1
		if 	len(screenlist)<5:
			number=5-len(screenlist)
			for x in range(number):
				x="img/placeholder3.jpg"
				ret+='<div class="cell"><div class="img-container thumbnail"><img src="{}"></div></div>'.format(x)				
			
		ret+='</div>'
		return ret
	except:
		return "Not available"
# @eel.expose	
# def show_picture(img):	
	# eel.show(img)

def format_file_tree(baselist,updlist,dlclist,titleid):
	feed=''
	feed=html_feed(feed,1,message=str('CURRENT GAME FILE TREE: '))
	feed=html_feed(feed,2,message=str('- Games: '))	
	feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'
	if len(baselist)==0:
		message=['TitleID:',(titleid.upper()+' <strong>Version:</strong> '+'0')];feed=html_feed(feed,3,message)	
	else:
		for i in range(len(baselist)):
			p_=baselist[i]
			message=['TitleID: ',(p_[0].upper()+' <strong>Version:</strong> '+p_[1])];feed=html_feed(feed,3,message)	
	feed+='</ul>'		
	
	# feed=html_feed(feed,2,message=str('- Updates: '))		
	if len(updlist)==0:
		# feed+='<ul style="margin-bottom: 2px;margin-top: 3px;list-style-type: none;">'
		# message=['None.',''];feed=html_feed(feed,3,message)	
		# feed+='</ul>'
		pass
	else:	
		feed=html_feed(feed,2,message=str('- Updates: '))		
		feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'	
		for i in range(len(updlist)):
			p_=updlist[i]
			message=['TitleID: ',(p_[0].upper()+' <strong>Version:</strong> '+p_[1])];feed=html_feed(feed,3,message)	
		feed+='</ul>'	
	
	# feed=html_feed(feed,2,message=str('- DLCs: '))				
	if len(dlclist)==0:
		# feed+='<ul style="margin-bottom: 2px;margin-top: 3px;list-style-type: none;">'	
		# message=['None.',''];feed=html_feed(feed,3,message)	
		# feed+='</ul>'		
		pass
	else:		
		feed=html_feed(feed,2,message=str('- DLCs: '))	
		feed+='<ul style="margin-bottom: 2px;margin-top: 3px">'		
		for i in range(len(dlclist)):
			p_=dlclist[i]
			message=['TitleID: ',(p_[0].upper()+' <strong>Version:</strong> '+p_[1])];feed=html_feed(feed,3,message)	
		feed+='</ul>'		
	return feed			

@eel.expose
def clear(): 
	try:
		call('cls')
	except:	
		try:
			call('clear') 
		except:pass
	
def search_local_lib(value,library): 
	if library=='None':
		html='<p style="margin-bottom: 2px;margin-top: 3px"><strong style="margin-left: 12px">You need to create a library config file first</strong></p>'	
		eel.load_local_results(html)	
		return
	try:	
		db=libraries(local_lib_file)	
		if db==False:
			eel.load_local_results(False)	
			return
		if not library.lower()=='all':
			path=db[library]['path']
			print("* Searching library {}".format(library))
			sys.stdout.flush()
			results=folder_to_list(path,'all',value)	
			sr=sortbyname(results)	
			html='<ul style="margin-bottom: 2px;margin-top: 3px; list-style-type: none;">'
			i=0
			print("  - Retrieved {} files".format(str(len(results))))
			sys.stdout.flush()
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
		else:
			results=[]	
			for entry in db:
				path=db[entry]['path']
				print("* Searching library {}".format(entry))
				sys.stdout.flush()
				res=folder_to_list(path,'all',value)	
				print("  - Retrieved {} files".format(str(len(res))))
				sys.stdout.flush()
				results+=res	
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
				# print(item)	
			html+='</ul>'	
		eel.load_local_results(html)	
		return
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		sys.stdout.flush()	
		
@eel.expose
def get_libraries(): 
	try:	
		htmlcode='<select class="bg-cobalt fg-white" data-role="select" style="width:25vw" id="_local_lib_select_">'
		htmlcode+='<option value="All" selected="selected">All</option>'
		db=libraries(local_lib_file)	
		if db==False:
			htmlcode='<select class="bg-cobalt fg-white" data-role="select" style="width:25vw" id="_local_lib_select_">'
			htmlcode+='<option value="{}">{}</option>'.format('None','Missing libraries')
			htmlcode+='</select>'
			# print(db[item])			
			return htmlcode			
		for item in db:
			htmlcode+='<option value="{}">{}</option>'.format(item,item)
			# print(db[item])
		htmlcode+='</select>'		
		return htmlcode
	except BaseException as e:
		Print.error('Exception: ' + str(e))	
		sys.stdout.flush()		
		
@eel.expose
def get_drive_libraries(): 
	try:	
		htmlcode='<select class="bg-cobalt fg-white" data-role="select" style="width:25vw" id="_remote_lib_select_">'
		htmlcode+='<option value="All" selected="selected">All</option>'
		db=libraries(remote_lib_file)	
		if db==False:
			htmlcode='<select class="bg-cobalt fg-white" data-role="select" style="width:25vw" id="_remote_lib_select_">'
			htmlcode+='<option value="{}">{}</option>'.format('None','Missing libraries')
			htmlcode+='</select>'	
			return htmlcode
		for item in db:
			htmlcode+='<option value="{}">{}</option>'.format(item,item)
			# print(db[item])
		htmlcode+='</select>'		
		return htmlcode
	except BaseException as e:
		Print.error('Exception: ' + str(e))		
		sys.stdout.flush()		
		
def search_remote_lib(value,library): 
	if library=='None':
		html='<p style="margin-bottom: 2px;margin-top: 3px"><strong style="margin-left: 12px">You need to create a library config file first</strong></p>'	
		eel.load_remote_results(html)	
		return
	try:	
		db=libraries(remote_lib_file)	
		if db==False:
			eel.load_remote_results(False)	
			return
		if not library.lower()=='all':
			results=[]	
			path=db[library]['path']
			TD=db[library]['TD_name']
			print("* Searching library {}".format(library))
			sys.stdout.flush()			
			response=DrivePrivate.search_folder(path,TD=TD,filter=value,Pick=False)
			if response!=False:
				results+=response			
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
		else:
			results=[]	
			for entry in db:
				path=db[entry]['path']
				TD=db[entry]['TD_name']
				print("* Searching library {}".format(entry))
				sys.stdout.flush()				
				response=DrivePrivate.search_folder(path,TD=TD,filter=value,Pick=False)
				if response!=False:
					results+=response
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
		eel.load_remote_results(html)
		return	
	except BaseException as e:
		Print.error('Exception: ' + str(e))		
		sys.stdout.flush()		
def sortbyname(files):
	results={};
	for f in files:
		k=str(os.path.basename(os.path.abspath(f)))
		results[k]=f
	return results
	
@eel.expose
def getfname():
	try:
		global threads
		for t in threads:
			# print(t)
			t.kill()
		treads=[]	
	except BaseException as e:
		# Print.error('Exception: ' + str(e))
		pass		
	root = tk.Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	filename = filedialog.askopenfilename(
	filetypes=[
				("All Filetypes","*.xci"),("All Filetypes","*.xcz"),("All Filetypes","*.xc0"),("All Filetypes","*.nsp"),("All Filetypes","*.nsz"),("All Filetypes","*.ns0"),("All Filetypes","*.nsx"),("All Filetypes","00"),	
				("xci","*.xci"),("xci","*.xcz"),("xci","*.xc0"),
				("nsp","*.nsp"),("nsp","*.nsz"),("nsp","*.ns0"),("nsp","*.nsx"),
				("Compressed files","*.nsz"),("Compressed files","*.xcz"),
				("Uncompressed files","*.nsp"),("Uncompressed files","*.nsx"),("Uncompressed files","*.xci"),("Uncompressed files","*.xc0"),("Uncompressed files","*.ns0"),("Uncompressed files","00"),		
				("Split Files","*.ns0"),("Split Files","*.xc0"),("Split Files","00")	
			]
	)	
	print('\nLoaded: '+filename)
	sys.stdout.flush()	
	return str(filename)
	
@eel.expose
def call_search_remote_lib(value,selected):
	global threads
	threads.append(eel.spawn(search_remote_lib,value,selected))	
	return
	
@eel.expose
def call_search_local_lib(value,selected):
	global threads
	threads.append(eel.spawn(search_local_lib,value,selected))	
	return	
	
@eel.expose
def call_showicon(filename):
	global threads
	threads.append(eel.spawn(showicon,filename))
	return
	
@eel.expose
def call_showicon_remote(filename):
	global threads
	threads.append(eel.spawn(showicon_remote,filename))	
	return
	
@eel.expose	
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

@eel.expose
def call_getinfo(filename,remotelocation=False):
	global threads
	threads.append(eel.spawn(getinfo,filename,remotelocation))
	return

@eel.expose
def call_get_adv_filelist(filename,remotelocation=False):
	global threads
	threads.append(eel.spawn(getfiledata,filename,remotelocation))
	return

@eel.expose
def call_get_nacp_data(filename,remotelocation=False):
	global threads
	threads.append(eel.spawn(getnacpdata,filename,remotelocation))
	return

@eel.expose
def call_get_npdm_data(filename,remotelocation=False):
	global threads
	threads.append(eel.spawn(getnpdmdata,filename,remotelocation))
	return

@eel.expose
def call_get_cnmt_data(filename,remotelocation=False):
	global threads
	threads.append(eel.spawn(getcnmtdata,filename,remotelocation))
	return	
	
@eel.expose
def call_get_verification_data(filename,remotelocation=False):
	global threads
	threads.append(eel.spawn(getverificationdata,filename,remotelocation))	
	return	
	
@eel.expose
def download(filename,remotelocation=False):
	filename=html.unescape(filename)
	lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
	ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
	# header=DrivePrivate.get_html_header(remote.access_token)
	token=remote.access_token
	URL='https://www.googleapis.com/drive/v3/files/'+remote.ID+'?alt=media'		
	eel.browser_download(URL,token)
	
def showicon(filename):
	filename=html.unescape(filename)
	# global globalocalpath;
	# if globalocalpath!=filename:
		# result=deepcheck_path(globalocalpath,filename)	
		# if result==False:
			# globalocalpath=filename
		# else:
			# filename=globalocalpath
	print('* Seeking icon')
	sys.stdout.flush()	
	# print(filename)
	try:
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			files_list=sq_tools.ret_nsp_offsets(filename)	
			f = Fs.Nsp(filename, 'rb')
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			files_list=sq_tools.ret_xci_offsets(filename)		
			f = Fs.Xci(filename)	
		elif filename.endswith('.xc0') or filename.endswith('.ns0') or filename.endswith('00'): 
			a=file_chunk.icon_info(filename)	
			encoded = b64encode(a).decode("ascii")
			data= "data:image/png;base64, " + encoded
			eel.setImage(data)	
			return
		else:
			eel.setImage("")	
			return
		a=f.icon_info(files_list)
		f.flush()
		f.close()	
		encoded = b64encode(a).decode("ascii")
		data= "data:image/png;base64, " + encoded	
		eel.setImage(data)	
		return
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		sys.stdout.flush()		
		iconurl=retrieve_icon_from_server(filename)
		if iconurl!=False:
			eel.setImage(iconurl)
			return
		else:
			eel.setImage("")
			return
		
def retrieve_icon_from_server(filename):
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):	
		f = Fs.Nsp(filename, 'rb')
		titleid=f.getnspid()		
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.Xci(filename)	
		titleid=f.getxciid()		
	else:	
		return False	
	iconurl=nutdb.get_icon(titleid)
	return iconurl
	
def showicon_remote(filename):
	filename=html.unescape(filename)
	global globalpath; global globalremote
	if globalpath!=filename:
		if not filename.startswith('http'):
			globalpath=filename
			lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
			ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
			globalremote=remote
		else:
			globalpath=filename
			remote=DrivePublic.location(filename);readable=remote.readable
			globalremote=remote
			if not readable:
				eel.setImage("")
				return
	try:				
		a=DriveHtmlInfo.icon_info(file=globalremote)		
		# a=DriveHtmlInfo.icon_info(path=filename,TD=TD)
		encoded = b64encode(a).decode("ascii")
		data="data:image/png;base64, " + encoded	
		eel.setImage(data)	
		return
	except:
		iconurl=nutdb.get_icon(remote.id)
		if iconurl!=False:
			eel.setImage(iconurl)
			return
		else:
			eel.setImage("")	
			return
		
def getinfo(filename,remotelocation=False):
	filename=html.unescape(filename)
	print('* Retrieving Game Information')
	sys.stdout.flush()	
	if remotelocation == False:
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			f = Fs.ChromeNsp(filename, 'rb')
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			f = Fs.ChromeXci(filename)	
		elif filename.endswith('.xc0') or filename.endswith('.ns0') or filename.endswith('00'):
			f=file_chunk.chunk(filename)
		else: return []		
		if not filename.endswith('0'):
			dict=f.return_DBdict()
		else:
			dict=f.getDBdict()		
			# print(dict)
	else:
		global globalpath; global globalremote
		if globalpath!=filename:
			globalpath=filename
			lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
			ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
			globalremote=remote
		dict=DriveHtmlInfo.getDBdict(file=globalremote)
	if remotelocation == False:		
		try:
			ModuleId,BuildID8,BuildID16=f.read_buildid()
			ModuleId=sq_tools.trimm_module_id(ModuleId)
		except BaseException as e:
			Print.error("Can't read buildID: " + str(e))
			ModuleId="-";BuildID8="-";BuildID16="-";
	else:
		try:	
			ModuleId=dict['ModuleId']
			BuildID8=dict['BuildID8']
			BuildID16=dict['BuildID16']
			ModuleId=sq_tools.trimm_module_id(ModuleId)
		except:
			ModuleId="-";BuildID8="-";BuildID16="-";
	try:	
		MinRSV=sq_tools.getMinRSV(dict['keygeneration'],dict['RSV'])
		RSV_rq_min=sq_tools.getFWRangeRSV(MinRSV)
		FW_rq=sq_tools.getFWRangeKG(dict['keygeneration'])	
	except:
		MinRSV="-";RSV_rq_min="-";FW_rq="-"
	try:	
		RGV=dict['RGV']
		RS_number=int(int(RGV)/65536)
	except:
		RGV="0";RS_number="0";	
	send_=list()
	try:
		if str(dict['Type']).upper()=='DLC':
			send_.append(dict['contentname'])			
		else:
			send_.append(dict['baseName'])
	except:send_.append('-')
	try:
		send_.append(dict['editor'])
	except:send_.append('-')
	try:		
		send_.append(dict['id'])
	except:send_.append('-')
	try:			
		send_.append(dict['version'])	
	except:send_.append('-')
	try:			
		send_.append(dict['Type'])	
	except:send_.append('-')
	try:			
		send_.append(dict['dispversion'])	
	except:send_.append('-')
	try:
		send_.append(dict['metasdkversion'])
	except:send_.append('-')
	try:			
		send_.append(dict['exesdkversion'])	
	except:send_.append('-')
	try:			
		lang=str((', '.join(dict['languages'])))
		send_.append(lang)	
	except:send_.append('-')
	try:			
		send_.append(dict['RSV'])
	except:send_.append('-')
	try:			
		send_.append(str(dict['keygeneration'])+" -> " +FW_rq)				
	except:send_.append('-')
	try:	
		send_.append(dict['nsuId'])		
	except:send_.append('-')
	try:			
		genres=str((', '.join(dict['genretags'])))
		send_.append(genres)	
	except:send_.append('-')
	try:			
		ratags=str((', '.join(dict['ratingtags'])))
		send_.append(ratags)				
	except:send_.append('-')
	try:			
		send_.append(dict['worldreleasedate'])	
	except:send_.append('-')
	try:			
		send_.append(dict['numberOfPlayers'])	
	except:send_.append('-')
	try:			
		send_.append(str(dict['eshoprating']))	
	except:send_.append('-')
	try:			
		send_.append(sq_tools.getSize(dict['InstalledSize']))	
	except:send_.append('-')
	try:			
		send_.append(BuildID8)	
	except:send_.append('-')
	try:			
		send_.append(ModuleId)	
	except:send_.append('-')
	try:			
		send_.append(dict['key'])		
	except:send_.append('-')
	try:			
		send_.append(RSV_rq_min[1:-1])	
	except:send_.append('-')	
	try:
		if 'regions' in dict:
			reg=str((', '.join(dict['regions'])))
			send_.append(reg)
		else:
			send_.append('-')
	except:
		send_.append('-')
	try:	
		if dict["intro"] !='-' and dict["intro"] !=None and dict["intro"] !='':
			if str(dict['Type']).upper()!='DLC':
				send_.append(dict['baseName']+". "+dict["intro"])	
			else:
				send_.append(dict['contentname']+". "+dict["intro"])
		else:
			if str(dict['Type']).upper()!='DLC':
				send_.append(dict['baseName'])	
			else:
				send_.append(dict['contentname'])				
	except:	
		try:
			if str(dict['Type']).upper()!='DLC':
				try:
					send_.append(dict['baseName'])	
				except:send_.append('-')	
			else:
				try:
					send_.append(dict['contentname'])
				except:send_.append('-')	
		except:send_.append('-')		
	try:	
		if dict["description"] !='-':		
			send_.append(dict["description"])
		else:
			send_.append("Not available")	
	except:send_.append("Not available")	
	try:			
		if str(dict['HtmlManual']).lower()=="true":
			send_.append("Yes")	
		else:
			send_.append("No")						
	except:send_.append('-')	
	try:			
		# print(str(dict['linkedAccRequired']))
		if str(dict['linkedAccRequired']).lower()=="true":
			send_.append("Yes")	
		else:
			send_.append("No")	
	except:send_.append('-')
	try:	
		if dict["ContentNumber"] !='-':		
			if int(dict["ContentNumber"])>1:
				if 'ContentString' in dict:
					send_.append(dict["ContentString"])
				else:
					send_.append("Yes ({})".format(dict["ContentNumber"]))
			else:	
				send_.append("No")			
		else:
			send_.append("-")	
	except:send_.append("-")		
	if remotelocation == False:	
		try:	
			if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
				send_.append("Eshop")	
			elif filename.endswith('.xci') or filename.endswith('.xcz'):
				send_.append("Gamecard")	
			else:		
				send_.append("-")			
		except:send_.append("-")
	else:
		remotename=globalremote.name
		try:	
			if remotename.endswith('.nsp')or remotename.endswith('.nsx') or remotename.endswith('.nsz'):
				send_.append("Eshop")	
			elif remotename.endswith('.xci') or remotename.endswith('.xcz'):
				send_.append("Gamecard")	
			else:		
				send_.append("-")			
		except:send_.append("-")	
	try:
		send_.append(sq_tools.getSize(dict['GCSize']))	
	except:send_.append('-')	
	try:#data[30]
		x=get_screen_gallery(dict["bannerUrl"],dict["screenshots"])
		send_.append(x)			
	except:send_.append("Not available")
	try:#data[31]
		RQversion=0
		if str(dict['Type']).upper()=='DLC':
			if int(RGV)>0:
				RQversion=str(RGV)+" -> Patch ({})".format(str(RS_number))
			else:
				RQversion=str(RGV)+" -> Application ({})".format(str(RS_number))
		send_.append(RQversion)		
	except:send_.append('-')
	###NEW JSON STUFF###
	try:#data[32]			
		send_.append(dict['developer'])	
	except:send_.append('-')
	try:#data[33]			
		send_.append(dict['productCode'])	
	except:send_.append('-')
	try:#data[34]
		if str(dict['OnlinePlay']).lower()=="true":
			send_.append("Yes")	
		else:
			send_.append("No")						
	except:send_.append('No')
	try:#data[35]			
		if str(dict['SaveDataCloud']).lower()=="true":
			send_.append("Yes")	
		else:
			send_.append("No")						
	except:send_.append('No')
	try:#data[36]			
		playmodes=str((', '.join(dict['playmodes'])))
		send_.append(playmodes)	
	except:send_.append('-')
	try:#data[37]	
		if str(dict['metascore']).lower()=='false':
			send_.append('-')
		else:	
			send_.append(dict['metascore'])	
	except:send_.append('-')
	try:#data[38]			
		if str(dict['userscore']).lower()=='false':
			send_.append('-')
		else:		
			send_.append(dict['userscore'])	
	except:send_.append('-')
	try:#data[39]
		FWoncard=dict['FWoncard']
		FWoncard=str(FWoncard).strip("'")
		send_.append(FWoncard)	
	except:send_.append('-')
	try:#data[40]		
		if str(enablevideoplayback).lower() == 'true':
			video=dict['video']	
			video=ast.literal_eval(str(video))
			video=video[0]
			send_.append(str(video))	
		else:
			send_.append('-')
	except:send_.append('-')	
	try:#data[41]			
		if str(dict['openscore']).lower()=='false':
			send_.append('-')
		else:
			if dict['openscore'] != dict['metascore']:
				send_.append(dict['openscore'])	
			else:
				send_.append('-')
	except:send_.append('-')	
	try:
		f.flush()
		f.close()			
	except:pass	
	eel.setInfo(send_)
	return
	
@eel.expose	
def getfiletree(ID):
	print('* Generating BaseID FileTree from DB')
	sys.stdout.flush()
	feed=''
	try:
		message,baselist,updlist,dlclist=nutdb.BaseID_tree(ID,printinfo=False)	
		feed=format_file_tree(baselist,updlist,dlclist,ID)
	except:pass	
	return	feed	
	
@eel.expose	
def getcheats(ID):
	print('* Seeking cheats from DB')
	sys.stdout.flush()	
	feed=''
	try:
		cheatID_list=nutdb.get_content_cheats(ID)	
		feed=html_feed(feed,1,message=str('LIST OF CHEATS: '))	
		if len(cheatID_list)==0:
			feed=html_feed(feed,2,message=str('- Cheats not found'))			
		for i in range(len(cheatID_list)):
			data=cheatID_list[i]
			titleid=data[0];version=data[1];buildid=data[2]
			message=[str(titleid+' v'+version+'. '+'BuildID: '+buildid),''];feed=html_feed(feed,3,message)		
			cheats=data[3]
			feed+='<div style="margin-left:2.6vh">'
			for j in range(len(cheats)):
				entry=cheats[j]
				cheat_title=entry[0]
				cheat_source=entry[1]
				message=[cheat_title,""];feed=html_feed(feed,9,message)
				feed=html_feed(feed,8,message=(cheat_source))
			feed+='</div>'
	except:
			feed=html_feed(feed,1,message=str('LIST OF CHEATS: '))		
			feed=html_feed(feed,2,message=str('- Cheats not found'))			
	print('  DONE')	
	sys.stdout.flush()	
	return feed

def getfiledata(filename,remotelocation=False):
	filename=html.unescape(filename)
	print('* Generating Titles File Data')
	sys.stdout.flush()	
	if remotelocation != False:
		global globalpath; global globalremote
		if globalpath!=filename:
			globalpath=filename
			lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
			ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
			globalremote=remote
		feed=DriveHtmlInfo.adv_file_list(file=globalremote)
		eel.set_adv_filelist(feed)		
		return
	else:
		if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz'):
			f = Fs.ChromeNsp(filename, 'rb')
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			f = Fs.ChromeXci(filename)	
		elif filename.endswith('.xc0') or filename.endswith('.ns0') or filename.endswith('00'): 
			ck=file_chunk.chunk(filename)	
			feed=ck.send_html_adv_file_list()
			eel.set_adv_filelist(feed)	
			return
		else: eel.set_adv_filelist("")		
		feed=f.adv_file_list()
		f.flush()
		f.close()		
		eel.set_adv_filelist(feed)
		return

def getnacpdata(filename,remotelocation=False):
	filename=html.unescape(filename)
	print('* Reading Data from Nacp')
	sys.stdout.flush()	
	if remotelocation != False:
		global globalpath; global globalremote
		if globalpath!=filename:
			globalpath=filename
			lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
			ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
			globalremote=remote
		feed=DriveHtmlInfo.read_nacp(file=globalremote)		
		if feed=='':
			feed=html_feed(feed,2,message=str('No nacp in the file'))		
		eel.set_nacp_data(feed)
		return
	else:
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			f = Fs.ChromeNsp(filename, 'rb')
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			f = Fs.ChromeXci(filename)	
		elif filename.endswith('.xc0') or filename.endswith('.ns0') or filename.endswith('00'): 
			ck=file_chunk.chunk(filename)	
			feed=ck.send_html_nacp_data()
			if feed=='':
				feed=html_feed(feed,2,message=str('No nacp in the file'))	
			eel.set_nacp_data(feed)		
			return
		else: 
			eel.set_nacp_data("")	
			return
		feed=f.read_nacp(gui=True)
		f.flush()
		f.close()			
		if feed=='':
			feed=html_feed(feed,2,message=str('No nacp in the file'))		
		eel.set_nacp_data(feed)
		return
	
def getnpdmdata(filename,remotelocation=False):
	filename=html.unescape(filename)
	print('* Reading Data from Npdm')
	sys.stdout.flush()	
	if remotelocation != False:
		global globalpath; global globalremote
		if globalpath!=filename:
			globalpath=filename
			lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
			ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
			globalremote=remote
		feed=DriveHtmlInfo.read_npdm(file=globalremote)	
		if feed=='':
			feed=html_feed(feed,2,message=str('No npdm in the file'))	
		eel.set_npdm_data(feed)
		return
	else:
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			f = Fs.ChromeNsp(filename, 'rb')
			files_list=sq_tools.ret_nsp_offsets(filename)			
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			f = Fs.ChromeXci(filename)			
			files_list=sq_tools.ret_xci_offsets(filename)	
		else: 
			eel.set_npdm_data("")	
			return		
		feed=f.read_npdm(files_list)
		f.flush()
		f.close()
		if feed=='':
			feed=html_feed(feed,2,message=str('No npdm in the file'))		
	eel.set_npdm_data(feed)
	return
	
def getcnmtdata(filename,remotelocation=False):
	filename=html.unescape(filename)
	print('* Reading Data from Cnmt')
	sys.stdout.flush()	
	if remotelocation != False:
		global globalpath; global globalremote
		if globalpath!=filename:
			globalpath=filename
			lib,TD,libpath=get_library_from_path(remote_lib_file,filename)
			ID,name,type,size,md5,remote=DrivePrivate.get_Data(filename,TD=TD,Print=False)
			globalremote=remote
		feed=DriveHtmlInfo.read_cnmt(file=globalremote)	
		eel.set_cnmt_data(feed)
		return
	else:
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			f = Fs.ChromeNsp(filename, 'rb')
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			f = Fs.ChromeXci(filename)	
		elif filename.endswith('.xc0') or filename.endswith('.ns0') or filename.endswith('00'): 
			ck=file_chunk.chunk(filename)	
			feed=ck.send_html_cnmt_data()
			eel.set_cnmt_data(feed)
			return	
		else: 
			eel.set_cnmt_data("")	
			return	
		feed=f.read_cnmt()
		f.flush()
		f.close()			
		eel.set_cnmt_data(feed)
		return
	
def getverificationdata(filename,remotelocation=False):
	filename=html.unescape(filename)
	print('* Verifying files')
	sys.stdout.flush()	
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)		
	else: 
		eel.set_ver_data("")
		return	
	check,feed=f.verify()
	if not os.path.exists(tmpfolder):
		os.makedirs(tmpfolder)		
	verdict,headerlist,feed=f.verify_sig(feed,tmpfolder)
	f.flush()
	f.close()			
	try:
		os.remove(tmpfolder) 	
	except:pass			
	eel.set_ver_data(feed)
	return	

def server(port=8000,host='localhost',videoplayback=True,ssl=False,noconsole=False,overwrite=False):
	ssl_cert= os.path.join(zconfig_dir, 'certificate.pem')
	ssl_key= os.path.join(zconfig_dir, 'key.pem')
	web_folder=os.path.join(ztools_dir,'web')
	debug_folder=os.path.join(web_folder,'_debug_')
	flag_file=os.path.join(debug_folder,'flag')	
	debug_log=os.path.join(debug_folder,'log')	
	if ssl==False:
		ssl_cert=False
		ssl_key=False
	else:
		if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
			pass
		else:
			ssl_cert=False;ssl_key=False	
	with open(flag_file,'wt') as tfile:
		if noconsole==True:	
			tfile.write('True')
		else:	
			tfile.write('False')	
	global enablevideoplayback
	enablevideoplayback=videoplayback
	host=str(host)
	if port=='auto':
		port=0
	elif port=='rg8000':
		import socket, errno
		for p in range(8000,8999):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
			try:
				s.bind(("localhost", p))
				port=p
				s.close()
				break
			except socket.error as e:
				# print(e)
				pass
			s.close()			
	else:
		try:
			port=int(port)
		except:
			port=8000
	if noconsole==True:	
		sys.stdout = open(os.path.join(debug_folder,'log_{}.txt'.format(str(port))), 'w')
		sys.stderr = sys.stdout		
	else:
		with open(os.path.join(debug_folder,'log_{}.txt'.format(str(port))), 'w') as tfile:
			tfile.write("")		
	About(noconsole)
	if host=='0.0.0.0':
		h_='serverdomain'
	else:
		h_=str(host)
	if overwrite!=False:
		print("Launched in {}/nscb.html".format(overwrite))	
		sys.stdout.flush()				
	elif ssl_cert!=False and ssl_key!=False:
		print("Server launched in https://{}:{}/nscb.html".format(h_,port))	
		print("Local Interface launched in https://{}:{}/main.html".format(h_,port))			
		sys.stdout.flush()		
	else:
		print("Server launched in http://{}:{}/nscb.html".format(h_,port))
		print("Local Interface in http://{}:{}/main.html".format(h_,port))			
		sys.stdout.flush()		
	while True:
		try:
			eel.start('nscb.html', mode=False,port=port,host=host,ssl_cert=ssl_cert,ssl_key=ssl_key)			
		except:pass
			
def start(browserpath='auto',videoplayback=True,height=800,width=740,port=8000,host='localhost',noconsole=False):
	if not (sys.platform in ['win32', 'win64']) and browserpath=='auto':
		browserpath='default'
	flag_file=os.path.join(debug_folder,'flag')	
	with open(flag_file,'wt') as tfile:
		if noconsole==True:	
			tfile.write('True')
		else:	
			tfile.write('False')			
	global enablevideoplayback
	enablevideoplayback=videoplayback
	host=str(host)
	if port=='auto':
		port=0
	elif port=='rg8000':
		import socket, errno
		for p in range(8000,8999):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
			try:
				s.bind(("localhost", p))
				port=p
				s.close()
				break
			except socket.error as e:
				# print(e)
				pass
			s.close()			
	else:
		try:
			port=int(port)
		except:
			port=8000
	if noconsole==True:	
		sys.stdout = open(os.path.join(debug_folder,'log_{}.txt'.format(str(port))), 'w')
		sys.stderr = sys.stdout			
	else:
		with open(os.path.join(debug_folder,'log_{}.txt'.format(str(port))), 'w') as tfile:
			tfile.write("")			
	try:
		if browserpath == 'default':
			print("Launched using default system browser")
			sys.stdout.flush()			
			eel.start('main.html', mode='default', size=(height, width),port=port,host=host)		
		elif str(browserpath).lower() == 'false' or str(browserpath).lower() == 'none':
			About(noconsole)
			if host=='0.0.0.0':
				print("Launched in http://{}:{}/main.html".format('localhost',port))
				print("Launched in http://{}:{}/main.html".format('127.0.0.1',port))
				sys.stdout.flush()				
			else:
				print("Launched in http://{}:{}/main.html".format(host,port))
				sys.stdout.flush()				
			if permanent==True:
				while True:
					try:
						eel.start('main.html', mode=False, size=(height, width),port=port,host=host)			
					except:pass
		elif browserpath != 'auto' and os.path.exists(browserpath) and not browserpath.endswith('.ink'):
			eel.browsers.set_path('chrome', browserpath)
			About(noconsole)
			print("Launched using: "+browserpath)
			sys.stdout.flush()			
			eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)
		elif browserpath != 'auto' and browserpath.endswith('.lnk') and sys.platform in ['win32', 'win64']:
			chrpath=os.path.join(ztools_dir,'chromium')
			chrpath_alt=os.path.join(squirrel_dir,'chromium')
			if not os.path.exists(browserpath) and os.path.exists(chrpath):
				browserpath=os.path.join(chrpath,browserpath)
			elif not os.path.exists(browserpath) and os.path.exists(chrpath_alt):
				browserpath=os.path.join(chrpath_alt,browserpath)
			elif not os.path.exists(browserpath) and sys.platform == 'win32':
				print(".lnk file doesn't exist")
				sys.stdout.flush()				
				return False
			shell = win32com.client.Dispatch("WScript.Shell")
			browserpath = shell.CreateShortCut(browserpath)
			browserpath=browserpath.Targetpath	
			eel.browsers.set_path('chrome', browserpath)
			About(noconsole)
			print("Launched using: "+browserpath)
			sys.stdout.flush()			
			eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)			
		elif os.path.exists(chromiumpath):
			eel.browsers.set_path('chrome', chromiumpath)
			About(noconsole)
			print("Launched using: "+chromiumpath)
			sys.stdout.flush()			
			eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)		
		elif os.path.exists(chromiumpath_alt):	
			eel.browsers.set_path('chrome', chromiumpath_alt)
			About(noconsole)
			print("Launched using: "+chromiumpath_alt)
			sys.stdout.flush()			
			eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)		
		elif os.path.exists(slimpath):
			eel.browsers.set_path('chrome', slimpath)
			About(noconsole)
			print("Launched using: "+slimpath)
			sys.stdout.flush()			
			eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)		
		elif os.path.exists(slimpath_alt):	
			eel.browsers.set_path('chrome', slimpath_alt)
			About(noconsole)
			print("Launched using: "+slimpath_alt)
			sys.stdout.flush()			
			eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)						
		else:
			try:
				About(noconsole)
				print("Launched using Chrome Installation")
				sys.stdout.flush()				
				eel.start('main.html', mode='chrome', size=(height, width),port=port,host=host)
			except EnvironmentError:
				print("Chrome wasn't detected. Launched using Windows Edge with limited compatibility")	
				sys.stdout.flush()				
				if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
					# print(platform.release())
					eel.start('main.html', mode='edge', size=(height, width),port=port,host=host)
				else:
					raise				
	except (SystemExit, MemoryError, KeyboardInterrupt):	
		try:
			try:
				global threads
				for t in threads:
					# print(t)
					t.kill()
				treads=[]	
			except BaseException as e:
				# Print.error('Exception: ' + str(e))
				pass
			print("User closed the program")
			sys.stdout.flush()			
			sys.exit()
		except:pass