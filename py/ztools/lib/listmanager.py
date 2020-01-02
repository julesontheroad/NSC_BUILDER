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

def striplines(textfile,number=1,counter=False):
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
		print('...................................................')
		print('STILL '+str(c)+' FILES TO PROCESS')
		print('...................................................')
			
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
	number=int(number)
	with open(textfile,'r', encoding='utf8') as f:
		i=0
		for line in f:
			i+=1
			print(line.strip())
			if i==number:
				break
			
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
		if len(tid1)>=len(tid2):
			lentlist=len(tid1)					
		elif len(tid1)<len(tid2):
			lentlist=len(tid2)				
		for i in range(lentlist):	
			try:
				i1=tid1[i]
				i2=tid2[i]+1					
				t=filepath[i1:i2]
				#print(t)
				if 'G+' in t or 'G)' in t:
					x_= t.find('G')-1
					nG=t[x_]
					for i in range(len(t)):
						try:
							index=x_-i
							test=t[index:x_]
							int(test)
							nG=test
						except:pass	
				else:
					nG=1
				if 'U+' in t or 'U)' in t:					
					y_= t.find('U')-1
					nU=t[y_]
					for i in range(len(t)):
						try:
							index=y_-i
							test=t[index:y_]
							int(test)
							nU=test
						except:pass						
				if 'D)' in t:			
					z_= t.find('D')-1
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
	return str(fileid),str(fileversion),cctag,int(nG),int(nU),int(nD),baseid
	
def folder_to_list(ifolder,extlist=['nsp'],filter=False):	
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
			#print (ext)
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
	except BaseException as e:
		nutPrint.error('Exception: ' + str(e))													
	return filelist


def selector2list(textfile,mode='folder',ext=False,filter=False,Print=False):	
	root = tk.Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	if mode=='file':
		filepath = filedialog.askopenfilename()		
	else:
		filepath = filedialog.askdirectory()
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
							
		with open(textfile,"a", encoding='utf8') as tfile:
			for line in filelist:
				try:
					tfile.write(line+"\n")
				except:
					continue							
	except BaseException as e:
		nutPrint.error('Exception: ' + str(e))													
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