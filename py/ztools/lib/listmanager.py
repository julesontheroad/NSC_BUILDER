indent = 1
tabs = '\t' * indent	
from binascii import hexlify as hx, unhexlify as uhx
import Print as nutPrint
import os
import ast
try:
	import tkinter as tk
	from tkinter import filedialog
except:pass	

def striplines(textfile,number=1,counter=False,jump_line=False):
	#print(textfile)
	number=int(number)
	filelist=list()
	c=0;i=0
	with open(textfile,'r', encoding='utf8') as f:
		for line in f:		
			if i>(number-1):
				fp=line.strip()
				filelist.append(fp)	
				c+=1	
			else:
				i+=1	

	with open(textfile,"w", encoding='utf8') as f:
		for ln in filelist:
			f.write(ln+'\n')
	if counter == True:
		if jump_line==True:
			print("")
		print('...................................................')
		print('STILL '+str(c)+' FILES TO PROCESS')
		print('...................................................')
		
def remove_from_botton(textfile,number=1):
	#print(textfile)
	number=int(number)
	filelist=list()
	c=0;
	with open(textfile,'r', encoding='utf8') as f:
		for line in f:		
			fp=line.strip()
			filelist.append(fp)	
			c+=1
	c=c-number
	if c<0:
		c=0
	with open(textfile,"w", encoding='utf8') as f:
		for ln in filelist:
			while c>0:
				f.write(ln+'\n')
				c-=1	
			
def counter(textfile,doprint=False):	
	counter=0
	with open(textfile,'r', encoding='utf8') as f:
		for line in f:
			counter+=1
	if doprint!=False:			
		print('...................................................')
		print('STILL '+str(counter)+' FILES TO PROCESS')
		print('...................................................') 		
	return counter

def printcurrent(textfile,number=1,counter=False):
	currentline=''
	if number!='all':
		number=int(number)
	with open(textfile,'r', encoding='utf8') as f:
		i=0
		for line in f:
			i+=1
			print(line.strip())
			if str(number)!='all':
				if i==number:
					break
	c=i				
	if counter!=False:			
		print('...................................................')
		print(f'{c} FILES ADDED TO LIST')
		print('...................................................') 		
	return c				
			
def read_lines_to_list(textfile,number=1,all=False):
	#print(textfile)
	number=int(number)
	filelist=list()
	i=0
	if all==False:
		with open(textfile,'r', encoding='utf8') as f:
			for line in f:		
				if i>(number-1):
					break
				else:
					fp=line.strip()
					filelist.append(fp)					
					i+=1
	else:
		with open(textfile,'r', encoding='utf8') as f:
			for line in f:			
				fp=line.strip()	
				filelist.append(fp)		
	return 	filelist		
	
def filter_list(textfile,ext=False,token=False,Print=True):
	try:
		ext=ext.split(' ')	
	except:pass
	if ext==False and token==False and not textfile.endswith('.txt'):
		if Print==True:
			print("List wasn't filtered")
		return None
	extlist=list()		
	if ext!=False:
		if isinstance(ext, list):	
			extlist=ext
		else:
			try:
				ext=ast.literal_eval(str(ext))
				if isinstance(ext, list):	
					extlist=ext
				else:
					extlist.append(ext)
			except:		
				extlist.append(ext)
	filelist=list()
	i=0
	if Print==True:		
		print("Filtering list {}".format(textfile))			
	if ext!=False:	
		with open(textfile,'r', encoding='utf8') as f:
			for line in f:			
				fp=line.strip()	
				for xt in extlist:
					if (fp.lower()).endswith(xt.lower()):
						filelist.append(fp)	
		for xt in extlist:
			if Print==True:				
				print(" - Added items matching extension {}".format(xt))					
	if token!=False:	
		with open(textfile,'r', encoding='utf8') as f:
			for line in f:			
				fp=line.strip()	
				if token.lower() in fp.lower():
					filelist.append(fp)		
			if Print==True:								
				print(" - Added items matching search {}".format(token))				
	if ext!=False or token!=False:	
		if Print==True:			
			print(" - Writing list")		
		with open(textfile,"w", encoding='utf8') as tfile:
			for line in filelist:
				try:
					tfile.write(line+"\n")
				except:
					continue	
		if Print==True:							
			print("List was filtered")		
			
def filter_vlist(inputlist,ext=False,token=False,Print=True):
	filelist=list()
	i=0	
	if ext!=False:	
		for line in inputlist:			
			fp=line.strip()	
			for xt in extlist:
				if (fp.lower()).endswith(xt.lower()):
					filelist.append(fp)	
		if Print==True:									
			for xt in extlist:
				print(" - Added items matching extension {}".format(xt))					
	if token!=False:	
		for line in inputlist:			
			fp=line.strip()	
			if token.lower() in fp.lower():
				filelist.append(fp)		
		if Print==True:								
			print(" - Added items matching search {}".format(token))				
	return filelist				
			
	
def remove_from_list(textfile,ext=False,token=False,Print=True):
	ext=ext.split(' ')
	if ext==False and token==False and not textfile.endswith('.txt'):
		if Print==True:
			print("List wasn't filtered")
		return None
	extlist=list()	
	if ext!=False:
		if isinstance(ext, list):	
			extlist=ext
		else:
			try:
				ext=ast.literal_eval(str(ext))
				if isinstance(ext, list):	
					extlist=ext
				else:
					extlist.append(ext)
			except:		
				extlist.append(ext)
	filelist=list()
	i=0
	if Print==True:		
		print("Filtering list {}".format(textfile))			
	if ext!=False:	
		with open(textfile,'r', encoding='utf8') as f:
			for line in f:			
				fp=line.strip()	
				for xt in extlist:
					if not (fp.lower()).endswith(xt.lower()):
						filelist.append(fp)	
		for xt in extlist:
			if Print==True:				
				print(" - Added items matching extension {}".format(xt))					
	if token!=False:	
		with open(textfile,'r', encoding='utf8') as f:
			for line in f:			
				fp=line.strip()	
				if not token.lower() in fp.lower():
					filelist.append(fp)		
			if Print==True:								
				print(" - Added items matching search {}".format(token))				
	if ext!=False or token!=False:	
		if Print==True:			
			print(" - Writing list")		
		with open(textfile,"w", encoding='utf8') as tfile:
			for line in filelist:
				try:
					tfile.write(line+"\n")
				except:
					continue	
		if Print==True:							
			print("List was filtered")				
		
def parsetags(filepath):	
	fileid='unknown';fileversion='unknown';cctag='unknown';nG=0;nU=0;nD=0;
	baseid=None
	tid1=list()
	tid2=list()
	tid1=[pos for pos, char in enumerate(filepath) if char == '[']
	tid2=[pos for pos, char in enumerate(filepath) if char == ']']
	if len(tid1)>=len(tid2):
		lentlist=len(tid1)					
	elif len(tid1)<len(tid2):
		lentlist=len(tid2)						
	for i in range(lentlist):	
		try:
			i1=tid1[i]+1
			i2=tid2[i]					
			t=filepath[i1:i2]
			#print(t)
			if len(t)==16: 
				try:
					test1=filepath[i1:i2]
					int(filepath[i1:i2], 16)
					fileid=str(filepath[i1:i2]).upper()
					if fileid !='unknown':
						if int(fileid[-3:])==800:
							cctag='UPD'
							baseid=str(fileid[:-3])+'000'
						elif int(fileid[-3:])==000:
							cctag='BASE'
							baseid=str(fileid)
						else:
							try:
								int(fileid[-3:])
								cctag='DLC'											
							except:pass
						break
				except:
					try:
						fileid=str(filepath[i1:i2]).upper()
						if str(fileid[-3:])!='800' or str(fileid[-3:])!='000':
							DLCnumb=str(fileid)
							DLCnumb="0000000000000"+DLCnumb[-3:]									
							DLCnumb=bytes.fromhex(DLCnumb)
							DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
							DLCnumb=int(DLCnumb)
							cctag='DLC'
					except:continue
		except:pass	
	if cctag=='DLC':
		baseid=str(fileid)
		token=int(hx(bytes.fromhex('0'+baseid[-4:-3])),16)-int('1',16)
		token=str(hex(token))[-1]
		token=token.upper()
		baseid=baseid[:-4]+token+'000'				
	for i in range(lentlist):	
		try:
			i1=tid1[i]+1
			i2=tid2[i]
		except:pass									
		if (str(filepath[(i1)]).upper())=='V':
			try:
				test2=filepath[(i1+1):i2]
				fileversion=int(filepath[(i1+1):i2])
				if fileversion !='unknown':
					break
			except:
				continue
	if fileversion == 'unknown':
		fileversion=0
	if fileid !='unknown':
		tid1=list()
		tid2=list()
		tid1=[pos for pos, char in enumerate(filepath) if char == '(']
		tid2=[pos for pos, char in enumerate(filepath) if char == ')']
		if not tid1 or not tid2:
			lentlist=0
		elif len(tid1)>=len(tid2):
			lentlist=len(tid1)					
		elif len(tid1)<len(tid2):
			lentlist=len(tid2)				
		for i in range(lentlist):	
			try:
				try:
					i1=tid1[i]
				except:
					i1=tid1[-1]
				try:					
					i2=tid2[i]+1	
				except:
					i2=tid2[-1]+1				
				t=filepath[i1:i2]		
				endertest=''
				try:
					endertest=t[-2:]
				except:
					pass			
				if 'G+' in t or 'G)' in t or 'G)'==endertest:
					x_= t.find('G')-1
					nG=t[x_]
					for i in range(len(t)):
						try:
							index=x_-i
							test=t[index:x_]
							int(test)
							nG=test
						except:pass	
				if 'U+' in t or 'U)' in t or 'U)'==endertest:					
					y_= t.find('U')-1
					nU=t[y_]
					for i in range(len(t)):
						try:
							index=y_-i
							test=t[index:y_]
							int(test)
							nU=test
						except:pass						
				if 'D)' in t or 'D)'==endertest:			
					z_= t.find('D')
					nD=t[z_]	
					for i in range(len(t)):
						try:
							index=z_-i
							test=t[index:z_]						
							int(test)
							nD=test
						except:pass							
			except:pass		
		# if int(nG)>0 or int(nU)>0 or int(nD)>0:
			# print(fileid+' '+str(fileversion)+' '+cctag+' '+str(nG)+'G+'+str(nU)+'U+'+str(nD)+'D')			
		# else:
			# print(fileid+' '+str(fileversion)+' '+cctag)	
	try:
		int(nG)
	except:
		nG=0
	try:
		int(nU)
	except:
		nU=0
	try:
		int(nD)
	except:
		nD=0		
	if int(nG)==0 and int(nU)==0 and int(nD)==0:
		nG=1
	return str(fileid),str(fileversion),cctag,int(nG),int(nU),int(nD),baseid

def folder_to_list(ifolder,extlist=['nsp'],filter=False,alfanumeric=False):	
	ruta=ifolder
	filelist=list()
	if str(extlist)=='all' and os.path.isdir(ruta):
		fname=""
		binbin='RECYCLE.BIN'
		for dirpath, dirnames, filenames in os.walk(ruta):
			for filename in [f for f in filenames]:
				fname=""
				if filter != False:
					if filter.lower() in filename.lower():
						fname=filename
				else:
					fname=filename
				if fname != "":
					if binbin.lower() not in filename.lower():
						filelist.append(os.path.join(dirpath, filename))		
	try:
		fname=""
		binbin='RECYCLE.BIN'
		for ext in extlist:
			# print (ext)
			if os.path.isdir(ruta):
				for dirpath, dirnames, filenames in os.walk(ruta):
					try:
						for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:
							try:
								fname=""
								if filter != False:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(os.path.join(dirpath, filename))
							except BaseException as e:
								# nutPrint.error('Exception: ' + str(e))					
								pass	
					except BaseException as e:
						# nutPrint.error('Exception: ' + str(e))					
						pass							
			else:
				try:
					if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
						filename = ruta
						fname=""
						if filter != False:
							if filter.lower() in filename.lower():
								fname=filename
						else:
							fname=filename
						if fname != "":
							if binbin.lower() not in filename.lower():
								filelist.append(filename)							
				except BaseException as e:
					# nutPrint.error('Exception: ' + str(e))					
					pass
		if alfanumeric==True:
			nl=list([val for val in filelist if not val.isalnum()])
			filelist=nl	
	except BaseException as e:
		nutPrint.error('Exception: ' + str(e))	
	return filelist

def nextfolder_to_list(ifolder,extlist=['nsp'],filter=False,alfanumeric=False):	
	ruta=ifolder
	filelist=list()
	if str(extlist)=='all' and os.path.isdir(ruta):
		fname=""
		binbin='RECYCLE.BIN'
		dirpath=ruta
		for filename in next(os.walk(ruta))[2]:			
			fname=""
			if filter != False:
				if filter.lower() in filename.lower():
					fname=filename
			else:
				fname=filename
			if fname != "":
				if binbin.lower() not in filename.lower():
					filelist.append(os.path.join(dirpath, filename))		
	try:
		fname=""
		binbin='RECYCLE.BIN'
		for ext in extlist:
			#print (ext)
			if os.path.isdir(ruta):
				dirpath=ruta
				for filename in next(os.walk(ruta))[2]:	
					try:				
						if filename.endswith(ext.lower()) or filename.endswith(ext.upper()) or filename[:-1].endswith(ext.lower()) or filename[:-1].endswith(ext.lower()):
							fname=""
							if filter != False:
								if filter.lower() in filename.lower():
									fname=filename
							else:
								fname=filename
							if fname != "":
								if binbin.lower() not in filename.lower():
									filelist.append(os.path.join(dirpath, filename))
					except:pass			
			else:
				try:
					if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
						filename = ruta
						fname=""
						if filter != False:
							if filter.lower() in filename.lower():
								fname=filename
						else:
							fname=filename
						if fname != "":
							if binbin.lower() not in filename.lower():
								filelist.append(filename)
				except:pass			
		if alfanumeric==True:
			nl=list([val for val in filelist if not val.isalnum()])
			filelist=nl	
	except BaseException as e:
		nutPrint.error('Exception: ' + str(e))													
	return filelist

def selector2list(textfile,mode='folder',ext=False,filter=False,Print=False,multiselect=False):
	root = tk.Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	extlist=list()
	if ext!=False:
		if isinstance(ext, list):	
			extlist=ext
		else:
			try:
				if not ',' in ext:
					ext=ext.split(' ')
				else:
					ext=ext.split(',')			
				ext=ast.literal_eval(str(ext))
				if isinstance(ext, list):	
					extlist=ext
				else:
					extlist=ext.split(' ')
			except:		
				extlist.append(ext)	
	else:
		extlist=['nsp','xci','nsx','xcz','nsz']	
	if mode=='file':
		filetypes=[]
		if not 'all' in extlist:
			for x in extlist:
				if not x.startswith('.'):
					x='.'+x
				entry=("Filetypes",f"*{x}")	
				filetypes.append(entry)
			if multiselect==False:
				filepath = filedialog.askopenfilename(filetypes=filetypes)				
			else:	
				filepath = filedialog.askopenfilenames(filetypes=filetypes)	
		else:
			if multiselect==False:	
				filepath = filedialog.askopenfilename()					
			else:				
				filepath = filedialog.askopenfilenames()		
		if multiselect==False:					
			filelist=[]
			filelist.append(filepath)
		else:
			filelist=list(filepath)
	else:
		filepath = filedialog.askdirectory()
	if mode!='file':		
		ruta=filepath
		filelist=list()
		try:
			fname=""
			binbin='RECYCLE.BIN'
			if ext!=False:
				for ext in extlist:
					ext=ext.strip()
					# print (ext)
					if os.path.isdir(ruta):
						for dirpath, dirnames, filenames in os.walk(ruta):
							for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:
								fname=""
								if filter != False:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(os.path.join(dirpath, filename))
					else:
						if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
							filename = ruta
							fname=""
							if filter != False:
								if filter.lower() in filename.lower():
									fname=filename
							else:
								fname=filename
							if fname != "":
								if binbin.lower() not in filename.lower():
									filelist.append(filename)
			elif os.path.isdir(ruta):
				for dirpath, dirnames, filenames in os.walk(ruta):
					for filename in [f for f in filenames]:
						fname=""
						if filter != False:
							if filter.lower() in filename.lower():
								fname=filename
						else:
							fname=filename
						if fname != "":
							if binbin.lower() not in filename.lower():
								filelist.append(os.path.join(dirpath, filename))
			elif not os.path.isdir(ruta):	
				filename = ruta
				fname=""
				if filter != False:
					if filter.lower() in filename.lower():
						fname=filename
				else:
					fname=filename
				if fname != "":
					if binbin.lower() not in filename.lower():
						filelist.append(filename)						
		except BaseException as e:
			nutPrint.error('Exception: ' + str(e))	
	if filelist:		
		with open(textfile,"a", encoding='utf8') as tfile:
			for line in filelist:
				try:
					tfile.write(line+"\n")
				except:
					continue				
	return filelist

def size_sorted_from_json(jsonfile,tfile,first='small'):
	dump={}
	try:
		import ujson as json
	except:
		import json
	with open(jsonfile,'rt',encoding='utf8') as json_file:	
		data = json.load(json_file)		
		for dict in data:	
			if 'Name' in dict and 'Size' in dict:
				try:
					dump[dict['Name']]=dict['Size']
				except:pass		
	if first=='big':
		sortedlist = sorted(dump.items(), key=lambda x: x[1],reverse=True)
	else:
		sortedlist = sorted(dump.items(), key=lambda x: x[1],reverse=False)
	with open(tfile,'wt',encoding='utf8') as tfile:	
		for i in sortedlist:
			tfile.write(i[0]+"\n")
	print('- List was ordered by size')
		
def size_sorted_from_folder(ifolder,tfile,extlist=['nsp'],first='small'):	
	filelist=folder_to_list(ifolder,extlist)
	dump={}
	for file in filelist:
		size=os.path.getsize(file)
		dump[file]=size
	if first=='big':
		sortedlist = sorted(dump.items(), key=lambda x: x[1],reverse=True)
	else:
		sortedlist = sorted(dump.items(), key=lambda x: x[1],reverse=False)	
	with open(tfile,'wt',encoding='utf8') as tfile:	
		for i in sortedlist:
			tfile.write(i[0]+"\n")
	print('- List ordered by size was created')
	
def size_sorted_from_tfile(itfile,otfile=None,first='small'):	
	filelist=read_lines_to_list(itfile,all=True)
	dump={}
	for file in filelist:
		size=os.path.getsize(file)
		dump[file]=size
	if first=='big':
		sortedlist = sorted(dump.items(), key=lambda x: x[1],reverse=True)
	else:
		sortedlist = sorted(dump.items(), key=lambda x: x[1],reverse=False)
	if otfile == None:
		tfile=itfile
	else:
		tfile=otfile
		ofolder=os.path.dirname(os.path.abspath(tfile))
		if not os.path.exists(ofolder):
			os.makedirs(ofolder)
	with open(tfile,'wt',encoding='utf8') as tfile:	
		for i in sortedlist:
			tfile.write(i[0]+"\n")
	print('- List was ordered by size')
	
def move_all_ext_to_folder(ifolder,ofolder,extensions=['nca']):
	import shutil
	filelist=folder_to_list(ifolder,extlist=extensions)
	for file in filelist:
		destiny=os.path.join(ofolder, str(os.path.basename(os.path.abspath(file))))
		shutil.move(file,destiny) 
		
def calculate_name(filelist,romanize=True,ext='.xci'):	
	from Fs import Nsp as squirrelNSP
	from Fs import Xci as squirrelXCI
	import re
	prlist=list()	
	for filepath in filelist:
		if filepath.endswith('.nsp'):
			try:
				c=list()
				f = squirrelNSP(filepath)
				contentlist=f.get_content(False,False,True)
				f.flush()
				f.close()
				if len(prlist)==0:
					for i in contentlist:
						prlist.append(i)
				else:
					for j in range(len(contentlist)):
						notinlist=False
						for i in range(len(prlist)):
							if contentlist[j][1] == prlist[i][1]:
								if contentlist[j][6] > prlist[i][6]:
									del prlist[i]
									prlist.append(contentlist[j])
									notinlist=False
								elif contentlist[j][6] == prlist[i][6]:
									notinlist=False
							else:
								notinlist=True
						if notinlist == True:
							prlist.append(contentlist[j])
			except BaseException as e:
				nutPrint.error('Exception: ' + str(e))
		if filepath.endswith('.xci'):
			try:
				c=list()
				f = squirrelXCI(filepath)
				contentlist=f.get_content(False,False,True)
				f.flush()
				f.close()
				if len(prlist)==0:
					for i in contentlist:
						prlist.append(i)
				else:
					for j in range(len(contentlist)):
						notinlist=False
						for i in range(len(prlist)):
							if contentlist[j][1] == prlist[i][1]:
								if contentlist[j][6] > prlist[i][6]:
									del prlist[i]
									prlist.append(contentlist[j])
									notinlist=False
								elif contentlist[j][6] == prlist[i][6]:
									notinlist=False
							else:
								notinlist=True
						if notinlist == True:
							prlist.append(contentlist[j])
			except BaseException as e:
				nutPrint.error('Exception: ' + str(e))
	basecount=0; basename='';basever='';baseid='';basefile=''
	updcount=0; updname='';updver='';updid='';updfile=''
	dlccount=0; dlcname='';dlcver='';dlcid='';dlcfile=''
	ccount='';bctag='';updtag='';dctag=''
	for i in range(len(prlist)):
		if prlist[i][5] == 'BASE':
			basecount+=1
			if baseid == "":
				basefile=str(prlist[i][0])
				baseid=str(prlist[i][1])
				basever='[v'+str(prlist[i][6])+']'
		if prlist[i][5] == 'UPDATE':
			updcount+=1
			endver=str(prlist[i][6])
			if updid == "":
				updfile=str(prlist[i][0])
				updid=str(prlist[i][1])
				updver='[v'+str(prlist[i][6])+']'
		if prlist[i][5] == 'DLC':
			dlccount+=1
			if dlcid == "":
				dlcfile=str(prlist[i][0])
				dlcid=str(prlist[i][1])
				dlcver='[v'+str(prlist[i][6])+']'
		if 	basecount !=0:
			bctag=str(basecount)+'G'
		else:
			bctag=''
		if 	updcount !=0:
			if bctag != '':
				updtag='+'+str(updcount)+'U'
			else:
				updtag=str(updcount)+'U'
		else:
			updtag=''
		if 	dlccount !=0:
			if bctag != '' or updtag != '':
				dctag='+'+str(dlccount)+'D'
			else:
				dctag=str(dlccount)+'D'
		else:
			dctag=''
		ccount='('+bctag+updtag+dctag+')'
	if baseid != "":
		if basefile.endswith('.xci'):
			f =squirrelXCI(basefile)
		elif basefile.endswith('.nsp'):
			f = squirrelNSP(basefile)
		ctitl=f.get_title(baseid)
		f.flush()
		f.close()
		if ctitl=='DLC' or ctitl=='-':
			ctitl=''
	elif updid !="":
		if updfile.endswith('.xci'):
			f = squirrelXCI(updfile)
		elif updfile.endswith('.nsp'):
			f = squirrelNSP(updfile)
		ctitl=f.get_title(updid)
		f.flush()
		f.close()
		if ctitl=='DLC' or ctitl=='-':
			ctitl=''
	elif dlcid !="":
		ctitl=get_title
		if dlcfile.endswith('.xci'):
			f = squirrelXCI(dlcfile)
		elif dlcfile.endswith('.nsp'):
			f = squirrelNSP(dlcfile)
		ctitl=f.get_title(dlcid)
		f.flush()
		f.close()
	else:
		ctitl='UNKNOWN'
	baseid='['+baseid.upper()+']'
	updid='['+updid.upper()+']'
	dlcid='['+dlcid.upper()+']'
	if ccount == '(1G)' or ccount == '(1U)' or ccount == '(1D)':
		ccount=''
	if baseid != "[]":
		if updver != "":
			endname=ctitl+' '+baseid+' '+updver+' '+ccount
		else:
			endname=ctitl+' '+baseid+' '+basever+' '+ccount
	elif updid != "[]":
		endname=ctitl+' '+updid+' '+updver+' '+ccount
	else:
		endname=ctitl+' '+dlcid+' '+dlcver+' '+ccount
	if romanize == True:
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
		endname=converter.do(endname)
		endname=endname[0].upper()+endname[1:]
	endname = (re.sub(r'[\/\\\:\*\?]+', '', endname))
	endname = re.sub(r'[™©®`~^´ªº¢#£€¥$ƒ±¬½¼♡«»±•²‰œæÆ³☆<<>>|]', '', endname)
	endname = re.sub(r'[Ⅰ]', 'I', endname);endname = re.sub(r'[Ⅱ]', 'II', endname)
	endname = re.sub(r'[Ⅲ]', 'III', endname);endname = re.sub(r'[Ⅳ]', 'IV', endname)
	endname = re.sub(r'[Ⅴ]', 'V', endname);endname = re.sub(r'[Ⅵ]', 'VI', endname)
	endname = re.sub(r'[Ⅶ]', 'VII', endname);endname = re.sub(r'[Ⅷ]', 'VIII', endname)
	endname = re.sub(r'[Ⅸ]', 'IX', endname);endname = re.sub(r'[Ⅹ]', 'X', endname)
	endname = re.sub(r'[Ⅺ]', 'XI', endname);endname = re.sub(r'[Ⅻ]', 'XII', endname)
	endname = re.sub(r'[Ⅼ]', 'L', endname);endname = re.sub(r'[Ⅽ]', 'C', endname)
	endname = re.sub(r'[Ⅾ]', 'D', endname);endname = re.sub(r'[Ⅿ]', 'M', endname)
	endname = re.sub(r'[—]', '-', endname);endname = re.sub(r'[√]', 'Root', endname)
	endname = re.sub(r'[àâá@äå]', 'a', endname);endname = re.sub(r'[ÀÂÁÄÅ]', 'A', endname)
	endname = re.sub(r'[èêéë]', 'e', endname);endname = re.sub(r'[ÈÊÉË]', 'E', endname)
	endname = re.sub(r'[ìîíï]', 'i', endname);endname = re.sub(r'[ÌÎÍÏ]', 'I', endname)
	endname = re.sub(r'[òôóöø]', 'o', endname);endname = re.sub(r'[ÒÔÓÖØ]', 'O', endname)
	endname = re.sub(r'[ùûúü]', 'u', endname);endname = re.sub(r'[ÙÛÚÜ]', 'U', endname)
	endname = re.sub(r'[’]', "'", endname);endname = re.sub(r'[“”]', '"', endname)
	endname = re.sub(' {3,}', ' ',endname);re.sub(' {2,}', ' ',endname);
	try:
		endname = endname.replace("( ", "(");endname = endname.replace(" )", ")")
		endname = endname.replace("[ ", "[");endname = endname.replace(" ]", "]")
		endname = endname.replace("[ (", "[(");endname = endname.replace(") ]", ")]")
		endname = endname.replace("[]", "");endname = endname.replace("()", "")
		endname = endname.replace('" ','"');endname = endname.replace(' "','"')
		endname = endname.replace(" !", "!");endname = endname.replace(" ?", "?")
		endname = endname.replace("  ", " ");endname = endname.replace("  ", " ")
		endname = endname.replace('"', '');
		endname = endname.replace(')', ') ');endname = endname.replace(']', '] ')
		endname = endname.replace("[ (", "[(");endname = endname.replace(") ]", ")]")
		endname = endname.replace("  ", " ")
	except:pass
	if endname[-1]==' ':
		endname=endname[:-1]
	endname=endname+ext
	return endname,prlist

def blk_txt_fromtxt(textfile1,textfile2,Print=True):
	filelist=[]
	with open(textfile1,'r', encoding='utf8') as f:
		for line in f:			
			fp=line.strip()	
			filelist.append(fp)	
	filelist2=[]
	with open(textfile2,'r', encoding='utf8') as f:
		for line in f:			
			fp=line.strip()	
			filelist2.append(fp)	
	newitems=[]		
	for item in filelist:
		delete_it=False
		for k in filelist2:	
			if os.path.splitext(item)[0]==os.path.splitext(k)[0]:
				delete_it=True
		if delete_it==False:
			newitems.append(item)
	with open(textfile1,'w', encoding='utf8') as f:			
		for it in newitems:
			f.write(it+'\n')	
			
def check_tfile_4missing(tfile1,tfile2,output,compare='right',include_parsed=False,errorfile=False):
	file_list1=read_lines_to_list(tfile1,all=True)
	file_list2=read_lines_to_list(tfile2,all=True)	
	if os.path.exists(output):
		try:
			os.remove(output)
		except:pass			
	titledb1={};titledb2={}
	for file in file_list1:
		try:
			print(f"Parsing {file}")
			fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)
			ky=f"{str(fileid).upper()}|{str(fileversion)}|{str(nG)}|{str(nU)}|{str(nD)}"
			ky=ky.strip()		
			print(ky)
			if not str(ky) in titledb1.keys():
				titledb1[str(ky)]=file	
		except:
			print("Exception: "+file)
			pass
	for file in file_list2:
		try:
			print(f"Parsing {file}")	
			fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)
			ky=f"{str(fileid).upper()}|{str(fileversion)}|{str(nG)}|{str(nU)}|{str(nD)}"
			ky=ky.strip()
			print(ky)			
			if not str(ky) in titledb2.keys():
				titledb2[str(ky)]=file			
		except:
			print("Exception: "+file)
			pass			
	counter=0			
	if compare=='right':
		for entry in titledb1.keys():
			try:
				if not entry in titledb2.keys():
					with open(output,'a', encoding='utf8') as f: 
						if include_parsed==False:				
							f.write(titledb1[entry]+'\n')	
						else:
							f.write(entry+'|'+titledb1[entry]+'\n')							
						counter+=1
			except:
				print("Exception: "+entry)
				pass					
	else:
		for entry in titledb2.keys():	
			try:
				if not entry in titledb1.keys():
					with open(output,'a', encoding='utf8') as f: 
						if include_parsed==False:					
							f.write(titledb2[entry]+'\n')
						else:
							f.write(entry+'|'+titledb2[entry]+'\n')								
						counter+=1	
			except:
				print("Exception: "+entry)
				pass							
	print("Done")		
	print(f"Detected {counter} files missing")

def append_parsed_to_tfile(tfile1,output):
	file_list1=read_lines_to_list(tfile1,all=True)
	if os.path.exists(output):
		try:
			os.remove(output)
		except:pass			
	titledb1={};
	for file in file_list1:
		print(f"Parsing {file}")
		fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)
		ky=f"{str(fileid).upper()}|{str(fileversion)}|{str(nG)}|{str(nU)}|{str(nD)}"
		ky=ky.strip()		
		print(ky)
		if not str(ky) in titledb1.keys():
			titledb1[str(ky)]=file	
	for entry in titledb1.keys():
		with open(output,'a', encoding='utf8') as f: 
			f.write(entry+'|'+titledb1[entry]+'\n')									
	print("Done")		
	
def check_cxci_dlc_number(cxci_text,dlc_text,outdated_cxci):
	cxci_list=read_lines_to_list(cxci_text,all=True)
	dlc_list=read_lines_to_list(dlc_text,all=True)	
	if os.path.exists(outdated_cxci):
		try:
			os.remove(outdated_cxci)
		except:pass			
	cxci_db={};dlc_db={};dlc_number={}
	print("Parsing files")
	for file in cxci_list:
		# print(f"Parsing {file}")
		fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)
		ky=f"{str(fileid).upper()}|{str(fileversion)}|{str(nG)}|{str(nU)}|{str(nD)}"
		ky=ky.strip()		
		# print(ky)
		if not str(ky) in cxci_db.keys():
			cxci_db[str(ky)]=[file,baseid,nG,nU,nD]	
	for file in dlc_list:
		# print(f"Parsing {file}")	
		fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)
		ky=f"{str(fileid).upper()}|{str(fileversion)}|{str(nG)}|{str(nU)}|{str(nD)}"
		ky=ky.strip()
		# print(ky)			
		if not str(ky) in dlc_db.keys():
			dlc_db[str(ky)]=file
		if not baseid in dlc_number.keys():
			dlc_number[baseid]=1
		else:
			num_d=dlc_number[baseid]
			dlc_number[baseid]=num_d+1
	counter=0		
	# print(dlc_number)
	for entry in cxci_db.keys():
		try:
			file=(cxci_db[entry])[0]	
			baseid=(cxci_db[entry])[1]
			dlc_n=int((cxci_db[entry])[4])
			available_dlc=0
			if baseid in dlc_number.keys():
				available_dlc=int(dlc_number[baseid])
				print(f"{baseid}:{available_dlc}")
			if available_dlc>dlc_n:	
				with open(outdated_cxci,'a', encoding='utf8') as f: 			
					print(f"Outdated {baseid}")
					f.write(file+'\n')		
					counter+=1	
		except BaseException as e:
			print('Exception: ' + str(e))
			pass	
	print("Done")		
	print(f"Detected {counter} files missing")	
	
def get_common_tid_files_ftxt(tfile1,tfile2,output,compare='right'):
	file_list1=read_lines_to_list(tfile1,all=True)
	file_list2=read_lines_to_list(tfile2,all=True)	
	if os.path.exists(output):
		try:
			os.remove(output)
		except:pass			
	titledb1={};titledb2={}
	for file in file_list1:
		# print(f"Parsing {file}")
		fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)	
		if not str(fileid) in titledb1.keys():
			titledb1[str(fileid)]=file	
	for file in file_list2:
		# print(f"Parsing {file}")	
		fileid,fileversion,cctag,nG,nU,nD,baseid=parsetags(file)
		if not str(fileid) in titledb2.keys():
			titledb2[str(fileid)]=file						
	if compare=='right':
		for entry in titledb1.keys():
			if entry in titledb2.keys():
				with open(output,'a', encoding='utf8') as f: 				
					f.write(titledb1[entry]+'\n')		
					print(entry)	
	else:
		for entry in titledb2.keys():	
			if entry in titledb1.keys():
				with open(output,'a', encoding='utf8') as f: 				
					f.write(titledb2[entry]+'\n')
					print(entry)		