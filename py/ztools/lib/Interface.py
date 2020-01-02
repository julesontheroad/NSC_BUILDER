import io
import eel
import sq_tools
import Fs
import sys
import platform
import win32com.client 
from base64 import b64encode
import tkinter as tk
from tkinter import filedialog
import sq_tools
import os
import ast
import Print
import nutdb
from subprocess import call 

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
slimjet='slimjet.exe'
slimpath=os.path.join(chromiumpath,slimjet)
slimpath_alt=os.path.join(chromiumpath_alt,slimjet)
chrom='chrlauncher.exe'
chromiumpath=os.path.join(chromiumpath,chrom)
chromiumpath_alt=os.path.join(chromiumpath_alt,chrom)

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
		ret='<div class="grid"><div class="row"><div class="img-container thumbnail" style="width: auto;max-height:auto; margin-left: auto; margin-right: auto; display: block;"><img src="{}" id="mainpicture" style="width: auto;max-height:63vh;"></div></div></div><div class="row">'.format(banner)
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
	except:return "Not available"

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
		

@eel.expose
def getfname():
	root = tk.Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	filename = filedialog.askopenfilename()	
	print('\nLoaded: '+filename)
	return str(filename)

@eel.expose
def showicon(filename):
	print('* Seeking icon')
	try:
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			files_list=sq_tools.ret_nsp_offsets(filename)	
			f = Fs.Nsp(filename, 'rb')
		elif filename.endswith('.xci') or filename.endswith('.xcz'):	
			files_list=sq_tools.ret_xci_offsets(filename)		
			f = Fs.Xci(filename)	
		else: return ""
		a=f.icon_info(files_list)
		f.flush()
		f.close()	
		encoded = b64encode(a).decode("ascii")
		return "data:image/png;base64, " + encoded	
	except BaseException as e:
		# Print.error('Exception: ' + str(e))
		iconurl=retrieve_icon_from_server(filename)
		if iconurl!=False:
			return iconurl
		else:return ""	
		
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
	
@eel.expose	
def getinfo(filename):
	print('* Retrieving Game Information')
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)		
	else: return []		
	dict=f.return_DBdict()
	try:
		ModuleId,BuildID8,BuildID16=f.read_buildid()	
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
	if 'regions' in dict:
		reg=str((', '.join(dict['regions'])))
		send_.append(reg)
	else:
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
		if str(dict['Type']).upper()!='DLC':
			try:
				send_.append(dict['baseName'])	
			except:send_.append('-')	
		else:
			try:
				send_.append(dict['contentname'])
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
	try:	
		if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
			send_.append("Eshop")	
		elif filename.endswith('.xci') or filename.endswith('.xcz'):
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
	f.flush()
	f.close()			
	return send_
	
@eel.expose	
def getfiletree(ID):
	print('* Generating BaseID FileTree from DB')
	feed=''
	message,baselist,updlist,dlclist=nutdb.BaseID_tree(ID,printinfo=False)	
	feed=format_file_tree(baselist,updlist,dlclist,ID)
	return	feed	
	
@eel.expose	
def getcheats(ID):
	print('* Seeking cheats from DB')
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
	return feed

@eel.expose	
def getfiledata(filename):
	print('* Generating Titles File Data')
	if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)	
	else: return ""		
	feed=f.adv_file_list()
	f.flush()
	f.close()		
	return	feed

@eel.expose	
def getnacpdata(filename):
	print('* Reading Data from Nacp')
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)		
	else: return ""		
	feed=f.read_nacp(gui=True)
	f.flush()
	f.close()			
	if feed=='':
		feed=html_feed(feed,2,message=str('No nacp in the file'))		
	return	feed
	
@eel.expose	
def getnpdmdata(filename):
	print('* Reading Data from Npdm')
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
		files_list=sq_tools.ret_nsp_offsets(filename)			
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)			
		files_list=sq_tools.ret_xci_offsets(filename)	
	else: return ""			
	feed=f.read_npdm(files_list)
	f.flush()
	f.close()
	if feed=='':
		feed=html_feed(feed,2,message=str('No npdm in the file'))		
	return	feed
	
@eel.expose	
def getcnmtdata(filename):
	print('* Reading Data from Cnmt')
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)	
	else: return ""			
	feed=f.read_cnmt()
	f.flush()
	f.close()			
	return	feed	
	
@eel.expose	
def getverificationdata(filename):
	print('* Verifying files')
	if filename.endswith('.nsp')or filename.endswith('.nsx') or filename.endswith('.nsz'):
		f = Fs.ChromeNsp(filename, 'rb')
	elif filename.endswith('.xci') or filename.endswith('.xcz'):	
		f = Fs.ChromeXci(filename)		
	else: return ""			
	check,feed=f.verify()
	if not os.path.exists(tmpfolder):
		os.makedirs(tmpfolder)		
	verdict,headerlist,feed=f.verify_sig(feed,tmpfolder)
	f.flush()
	f.close()			
	try:
		os.remove(tmpfolder) 	
	except:pass			
	return	feed		
	
def About():	
	print('                                       __          _ __    __                         ')
	print('                 ____  _____ ____     / /_  __  __(_) /___/ /__  _____                ')
	print('                / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/                ')
	print('               / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /                    ')
	print('              /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/                     ')
	print('                             /_____/                                                  ')
	print('------------------------------------------------------------------------------------- ')
	print('                        NINTENDO SWITCH CLEANER AND BUILDER                           ')
	print('                               FILE_INFO ALPHA GUI                                    ')
	print('------------------------------------------------------------------------------------- ')
	print('=============================     BY JULESONTHEROAD     ============================= ')
	print('------------------------------------------------------------------------------------- ')
	print('"                                POWERED BY SQUIRREL                                " ')
	print('"                    BASED ON THE WORK OF BLAWAR AND LUCA FRAGA                     " ')
	print('------------------------------------------------------------------------------------- ')                   
	print("Program's github: https://github.com/julesontheroad/NSC_BUILDER                       ")
	print('Cheats and Eshop information from nutdb and http://tinfoil.io                         ')
	print('------------------------------------------------------------------------------------- ')

def start(browserpath='auto',videoplayback=True,height=800,width=740):
	global enablevideoplayback
	enablevideoplayback=videoplayback
	try:
		if browserpath == 'default':
			print("Launched using default system browser")
			eel.start('main.html', mode='default', size=(height, width))				
		elif browserpath != 'auto' and os.path.exists(browserpath) and not browserpath.endswith('.ink'):
			eel.browsers.set_path('chrome', browserpath)
			About()
			print("Launched using: "+browserpath)
			eel.start('main.html', mode='chrome', size=(height, width))
		elif browserpath != 'auto' and browserpath.endswith('.lnk') and sys.platform in ['win32', 'win64']:
			chrpath=os.path.join(ztools_dir,'chromium')
			chrpath_alt=os.path.join(squirrel_dir,'chromium')
			if not os.path.exists(browserpath) and os.path.exists(chrpath):
				browserpath=os.path.join(chrpath,browserpath)
			elif not os.path.exists(browserpath) and os.path.exists(chrpath_alt):
				browserpath=os.path.join(chrpath_alt,browserpath)
			elif not os.path.exists(browserpath):
				print(".lnk file doesn't exist")
				return False
			shell = win32com.client.Dispatch("WScript.Shell")
			browserpath = shell.CreateShortCut(browserpath)
			browserpath=browserpath.Targetpath	
			eel.browsers.set_path('chrome', browserpath)
			About()
			print("Launched using: "+browserpath)
			eel.start('main.html', mode='chrome', size=(height, width))			
		elif os.path.exists(chromiumpath):
			eel.browsers.set_path('chrome', chromiumpath)
			About()
			print("Launched using: "+chromiumpath)
			eel.start('main.html', mode='chrome', size=(height, width))		
		elif os.path.exists(chromiumpath_alt):	
			eel.browsers.set_path('chrome', chromiumpath_alt)
			About()
			print("Launched using: "+chromiumpath_alt)
			eel.start('main.html', mode='chrome', size=(height, width))		
		elif os.path.exists(slimpath):
			eel.browsers.set_path('chrome', slimpath)
			About()
			print("Launched using: "+slimpath)
			eel.start('main.html', mode='chrome', size=(height, width))		
		elif os.path.exists(slimpath_alt):	
			eel.browsers.set_path('chrome', slimpath_alt)
			About()
			print("Launched using: "+slimpath_alt)
			eel.start('main.html', mode='chrome', size=(height, width))						
		else:
			try:
				About()
				print("Launched using Chrome Installation")
				eel.start('main.html', mode='chrome', size=(height, width))
			except EnvironmentError:
				print("Chrome wasn't detected. Launched using Windows Edge with limited compatibility")	
				if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
					# print(platform.release())
					eel.start('main.html', mode='edge', size=(height, width))
				else:
					raise				
	except (SystemExit, MemoryError, KeyboardInterrupt):	
		try:
			print("User closed the program")
			sys.exit()
		except:pass		