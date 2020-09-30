# -*- coding: utf-8 -*-
import re
import warnings
from six.moves import urllib_parse
import os
import os.path as osp
import re
import shutil
import sys
import tempfile
import requests
import six
from tqdm import tqdm
import argparse
import pkg_resources
from binascii import hexlify as hx, unhexlify as uhx
try:
	import ujson as json
except:
	import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials
import Hex
import sq_tools
from Drive import Public
from Drive import DriveTools
import io
import Fs.Nca as Nca
import Fs.Nsp as Nsp
import Fs.Nacp as Nacp
from Fs.File import MemoryFile
from hashlib import sha256,sha1
from python_pick import pick
from python_pick import Picker
from listmanager import folder_to_list

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

credentials_dir=os.path.join(zconfig_dir, 'credentials')	
if not os.path.exists(credentials_dir):
	os.makedirs(credentials_dir)
	
credentials_json = os.path.join(credentials_dir, 'credentials.json')

def get_scopes(type):
	if type=='default':
		SCOPES = ['https://www.googleapis.com/auth/drive']	
	elif type=='read':
		SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly']
	return	SCOPES
	
def get_path_parameters(route):
	param=route.split(":")
	folder_list=list()
	if len(param)>1:
		token_name=param[0]
		route=param[1]
	else:	
		try:
			token_name=param[0]
			# print(token_name)
			route='root'
		except:
			token_name='drive'
			route='root'
	if route=='drive':
		pass
	else:
		tid1=list();tid1=[pos for pos, char in enumerate(route) if char == '/']
		tid2=list();tid2=[pos for pos, char in enumerate(route) if char == '\\']
		positions= list(set(tid1 + tid2));positions.sort()
		for i in range(len(positions)):
			if i==0:
				j=positions[i];folder=route[:j]
			else:
				j=positions[i-1];k=positions[i]
				folder=route[j+1:k]
			if folder != "":	
				folder_list.append(folder)				
			if i==(len(positions)-1):
				j=positions[i]+1;folder=route[j:]
				if folder != "":
					folder_list.append(folder)		
	return token_name,folder_list

def get_html_header(access_token,off1=None,off2=None):
	tokenTotal = 'Bearer ' + str(access_token)	
	if off1==None or off2==None:
		header={
		'Authorization':tokenTotal, 
		'token_type':'Bearer',
		'accept' : '*/*',
		'accept-encoding': 'none',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
		'x-goog-api-client': 'gdcl/1.7.11 gl-python/3.7.3'}	
	else:
		header={
		'Range': 'bytes=%s-%s' % (off1,off2), 
		'Authorization':tokenTotal, 
		'token_type':'Bearer',
		'accept' : '*/*',
		'accept-encoding': 'none',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
		'x-goog-api-client': 'gdcl/1.7.11 gl-python/3.7.3'}
	return header
	
class auth():
	def __init__(self,SCOPES=None,token='drive',SCOPES_type='default',headless=True,apiver='v3',json_file=None):
		if SCOPES_type!='default':
			SCOPES=get_scopes(SCOPES_type)	
		if SCOPES!=None:
			if os.path.exists(tk):
				try: 
					os.remove(tk)
				except:pass	
		else:
			SCOPES = ['https://www.googleapis.com/auth/drive']				
		creds = None;json_auth=False		
		tk = os.path.join(credentials_dir, token)	
		alt_json=os.path.join(credentials_dir, (token+".json"))		
		if os.path.exists(alt_json):
			credentials_json=alt_json
		else:	
			credentials_json=os.path.join(credentials_dir, 'credentials.json')			
		if json_file!=None:		
			tk=json_file			
		if os.path.exists(tk):
			try:
				with open(tk) as jfile:						
					test=json.load(jfile)	
				json_auth=True
				apiver='v3'
			except:
				with open(tk, 'rb') as tok:
					creds = pickle.load(tok)							
		# If there are no (valid) credentials available, let the user log in.
		if json_auth==False:		
			if not creds or not creds.valid:
				if creds and creds.expired and creds.refresh_token:
					creds.refresh(Request())
				else:
					flow = InstalledAppFlow.from_client_secrets_file(
						credentials_json, SCOPES)
					if headless==False:	
						creds = flow.run_local_server(port=0)
					else:
						creds = flow.run_console()
				# Save the credentials for the next run
				with open(tk, 'wb') as tok:
					pickle.dump(creds, tok)
			self.drive_service = build('drive', apiver, credentials=creds)
			self.access_token = creds.token
		else:		
			if os.path.exists(token):				
				creds = ServiceAccountCredentials.from_json_keyfile_name(token, scopes=SCOPES)
			elif os.path.exists(tk):		
				creds = ServiceAccountCredentials.from_json_keyfile_name(tk, scopes=SCOPES)					
			self.drive_service = build('drive', apiver, credentials=creds)
			self.access_token = None

class location():
	def __init__(self,ID=None,route=None,TD_ID=None,TD_Name=None,token_name=None):
		self.ID=ID;self.name=None;self.token_name=token_name;drive_service=None
		self.root='root';self.filetype=None;self.md5hash=None;self.access_token = None
		self.size=None;self.session=None;self.position=0;self.drivename=None
		self.drivename=self.token_name;self.response=None
		if TD_ID==None and TD_Name==None:
			self.isinTD=False
		else:
			self.isinTD=True
		if self.ID!=None and self.name==None:
			self.name,mimetype=self.get_name()
			if mimetype=='application/vnd.google-apps.folder':
				self.filetype='folder'
			else:
				self.filetype='file'
		if self.ID==None and route==None:
			raise("Can't get route to location")
		elif ID != None:
			self.ID=ID
		else:
			self.ID,self.name=self.get_location_ID(route,TD_ID,TD_Name)
		if self.ID==None and route!=None:
			tk,flist=get_path_parameters(route)
			if not flist and tk==self.token_name:
				self.ID=self.root			
			
	def get_name(self,ID=None,token_name=None):
		if ID==None:
			ID=self.ID
		if token_name==None:
			remote=auth()
			self.access_token = remote.access_token
		else:
			remote=auth(token=token_name)
			self.access_token = remote.access_token
		drive_service=remote.drive_service	
		self.drive_service=drive_service
		# print(self.isinTD)
		if self.isinTD==False:
			result=drive_service.files().get(fileId=ID, fields="name,mimeType").execute()
		else:
			result=drive_service.files().get(fileId=ID, fields="name,mimeType",supportsAllDrives = True).execute()			
		name=result['name']
		mimetype=result['mimeType']
		return name,mimetype

	def get_hash(self,ID=None,token_name=None):		
		if ID==None:
			ID=self.ID
		if token_name==None:
			remote=auth()
			self.access_token = remote.access_token
		else:
			remote=auth(token=token_name)
			self.access_token = remote.access_token
		drive_service=remote.drive_service	
		self.drive_service=drive_service		
		if self.isinTD==False:
			result=drive_service.files().get(fileId=ID, fields="md5Checksum").execute()
		else:
			result=drive_service.files().get(fileId=ID, fields="md5Checksum",supportsAllDrives = True).execute()			
		md5=result['md5Checksum']
		self.md5hash=md5
		return md5

	def get_size(self,ID=None,token_name=None):		
		if ID==None:
			ID=self.ID
		if token_name==None:
			remote=auth()
			self.access_token = remote.access_token
		else:
			remote=auth(token=token_name)
			self.access_token = remote.access_token
		drive_service=remote.drive_service	
		self.drive_service=drive_service
		try:	
			if self.isinTD==False:
				result=drive_service.files().get(fileId=ID, fields="size").execute()
			else:
				result=drive_service.files().get(fileId=ID, fields="size",supportsAllDrives = True).execute()			
			size=result['size']
			self.size=size
		except:pass	
		return self.size		
		
	def get_location_ID(self,route,TD_ID=None,TD_Name=None):
		token_name,folder_list=get_path_parameters(route)
		self.token_name=token_name
		self.drivename=self.token_name
		remote=auth(token=token_name)
		self.access_token = remote.access_token
		drive_service=remote.drive_service
		self.drive_service=drive_service
		parent='root';endID=None;endName=None
		if TD_ID !=None:
			parent=TD_ID
			self.root=parent
		elif TD_Name != None:
			parent=self.get_TD(TD_Name)
			self.root=parent
		for i in range(len(folder_list)):		
			# if i==0:
				# j=folder_list[i]
				# if self.root != 'root':
					# results = drive_service.files().list(
					# q="mimeType='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
					# pageSize=100, fields="nextPageToken, files(id, name)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute()
				# else:
					# results = drive_service.files().list(
					# q="mimeType='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
					# pageSize=100, fields="nextPageToken, files(id, name)").execute()					
				# items = results.get('files', [])
				# if not items:
					# return 	None,None					
				# parent=items[0]['id']
				# endID=parent;endName=items[0]['name']
			if i == (len(folder_list)-1):	
				j=folder_list[i]
				if self.root != 'root':
					results = drive_service.files().list(
					q="mimeType='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
					pageSize=100, fields="nextPageToken, files(id, name)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute() 			
				else:
					results = drive_service.files().list(
					q="mimeType='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
					pageSize=100, fields="nextPageToken, files(id, name)").execute() 
				items = results.get('files', [])	
				if not items:
					if self.root != 'root':
						results = drive_service.files().list(
						q="mimeType!='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
						pageSize=100, fields="nextPageToken, files(id, name)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute()					
					else:
						results = drive_service.files().list(
						q="mimeType!='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
						pageSize=100, fields="nextPageToken, files(id, name)").execute()
					self.filetype='file'
				else:
					self.filetype='folder'
				items = results.get('files', [])	
				if not items:
					self.filetype=None
					return 	None,None
				parent=items[0]['id']	
				endID=parent;endName=items[0]['name']													
			else:	
				j=folder_list[i]
				if self.root != 'root':
					results = drive_service.files().list(
					q="mimeType='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
					pageSize=100, fields="nextPageToken, files(id, name)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute()
				else:
					results = drive_service.files().list(
					q="mimeType='application/vnd.google-apps.folder' and name='{}' and '{}' in parents".format(j,parent),
					pageSize=100, fields="nextPageToken, files(id, name)").execute()				
				items = results.get('files', [])
				if not items:
					return 	None,None					
				parent=items[0]['id']	
				endID=parent;endName=items[0]['name']
		return 	endID,endName
	
	def get_TD(self,TD_Name=None):
		drive_service=self.drive_service;root='root'
		results = drive_service.drives().list(pageSize=100).execute()
		if TD_Name=='None' or TD_Name==None:
			return results['drives']
		else:	
			TDlist= results['drives']
			for drive in results['drives']:
				if str(TD_Name).lower() == str(drive['name']).lower():
					root=drive['id']
					break
		if root != 'root':
			return root

	def get_session(self,hd=None):
		if self.filetype=='file':
			if self.session==None:
				self.session = requests.session()
			if hd==None:
				header=get_html_header(self.access_token)
			else:
				header=hd
			self.session.headers=header
			URL='https://www.googleapis.com/drive/v3/files/'+self.ID+'?alt=media'
			res = self.session.get(URL, stream=True)
			self.response=res
		else:
			self.session=None
			self.response=None

	def rewind(self):
		hd=get_html_header(self.access_token,0,int(self.size))
		self.get_session(hd)
		self.position=0

	def seek(self,p,off2=None):
		if off2==None:
			off2=self.size
		p=int(p);off2=int(off2)-0x01
		hd=get_html_header(self.access_token,p,off2)
		self.get_session(hd)	
		self.position=p
		
	def read(self,sz=None,buffer=None):
		if buffer==None:
			buf=64*1024
		else:
			buf=int(buffer)
		if sz==None:
			sz=self.size-self.position
		sz=int(sz)
		if buf>sz:
			buf=sz
		end=self.position+sz-0x01
		hd=get_html_header(self.access_token,self.position,end)
		self.get_session(hd)	
		data=b''
		for dump in self.response.iter_content(chunk_size=buf):
			data=data+dump
			self.position=self.position+len(dump)
			if not dump:
				break
		return data	

	def read_at(self,pos,sz,buffer=None):
		if buffer==None:
			buf=64*1024
		else:
			buf=int(buffer)
		pos=int(pos);off2=int(sz)
		self.position=pos
		sz=int(sz)
		if buf>sz:
			buf=sz
		end=self.position+sz-0x01
		hd=get_html_header(self.access_token,self.position,end)
		self.get_session(hd)	
		data=b''
		for dump in self.response.iter_content(chunk_size=buf):
			data=data+dump
			self.position=self.position+len(dump)
			if not dump:
				break			
		return data	
		
	def readInt8(self, byteorder='little', signed = False):
			return int.from_bytes(self.read(1), byteorder=byteorder, signed=signed)

	def readInt16(self, byteorder='little', signed = False):
			return int.from_bytes(self.read(2), byteorder=byteorder, signed=signed)

	def readInt32(self, byteorder='little', signed = False):
			return int.from_bytes(self.read(4), byteorder=byteorder, signed=signed)

	def readInt64(self, byteorder='little', signed = False):
			return int.from_bytes(self.read(8), byteorder=byteorder, signed=signed)

	def readInt128(self, byteorder='little', signed = False):
		return int.from_bytes(self.read(16), byteorder=byteorder, signed=signed)
	
def create_token(name,headless=True,SCOPES='default'):
	tk = os.path.join(credentials_dir, name)	
	if os.path.exists(tk):
		os.remove(tk)
	auth(token=name,SCOPES_type=SCOPES,headless=headless)
	if os.path.exists(tk):
		print("\nSUCCESS!!!\n")
	else:
		print("\FAILURE!!!\n")	
		
def token_picker():	
	files=folder_to_list(credentials_dir,"all")	
	# print(files)	
	tokens=list();names=list()
	for file in files:
		bname=os.path.basename(os.path.abspath(file))
		test=bname.split(".")
		if len(test)==1 and file not in tokens:
			tokens.append(file)
			names.append(str(os.path.basename(os.path.abspath(file))))
	if len(names)>1:
		title = 'Pick an account (press SPACE\RIGHT to mark\\unmark, ENTER to continue): '
		options = names	
		selected = pick(options, title, min_selection_count=1)
		tok=names[selected[1]]
	elif len(names)==1:
		tok=names[0]
	else:
		tok=False
	return tok

def folder_walker(showfiles=False,Print=False):
	account=token_picker()
	path=account+':'
	TD=TD_picker(path)
	while True:
		folder=search_folder(path,TD=TD,mime='folders',pickmode='single',Print=False)
		if folder==False:
			break
		if folder=="EXIT":
			return False,False
		path=folder
	if Print==True:
		print(path)
	if showfiles==False:
		return path,TD
	else:
		files=search_folder(path,TD=TD)
		
def search_folder(path,TD=None,ext=None,filter=None,order=None,mime='files',Pick=True,Print=True,pickmode='multi'):
	file_list=list();userfilter=filter;isroot=False;TDlist=False;file_listv2=list()
	if isinstance(path, list):
		paths=path
	else:
		paths=path.split('.+')
	if isinstance(TD, list):
		TDlist=TD	
	index=0	
	for path in paths:
		# print(path)
		try:
			if userfilter==None or filter=="":
				filter=""
			else:
				filter=" and name contains '{}'".format(userfilter)
			if TDlist!=False:
				TD=TDlist[index]
				index+=1
			if TD=="pick":
				TD=TD_picker(path)
			if 	TD!= None:
				remote=location(route=path,TD_Name=TD)
			else:
				remote=location(route=path)
			drive_service=remote.drive_service
			if drive_service==None:
				if remote.token_name==None:
					auth=auth()
				else:
					auth=auth(token=token_name)
				drive_service=auth.drive_service
			tk,fl=get_path_parameters(path)
			if not fl and TD==None:
				root='root';remote.root=root;remote.ID=root
			elif not fl:
				root=remote.ID
				remote.root=root
				remote.ID=root
			else:
				root=remote.root
			# print(remote.ID)	
			if mime=='files':
				page_token = None;pagesize=1000
				while True:
					if root != 'root':
						results = drive_service.files().list(
						q="mimeType!='application/vnd.google-apps.folder' and '{}' in parents{}".format(remote.ID,filter),
						pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name, size, createdTime)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute() 
					else:
						results = drive_service.files().list(
						q="mimeType!='application/vnd.google-apps.folder' and '{}' in parents{}".format(remote.ID,filter),
						pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name, size, createdTime)").execute()	
					items = results.get('files', [])
					try:
						page_token = results.get('nextPageToken', None)	
					except:pass
					for file in items:
						try:
							file_list.append([file['name'],file['size'],path,file['createdTime'],file['id']])
						except:pass	
					if Print==True:
						print(f'- {path}: Total Retrieved '+str(len(file_list)))	
					if page_token == None:
						break		
			elif mime=='folders':	
				page_token = None;pagesize=100
				while True:
					if root != 'root':
						results = drive_service.files().list(
						q="mimeType='application/vnd.google-apps.folder' and '{}' in parents{}".format(remote.ID,filter),
						pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute() 
					else:
						results = drive_service.files().list(
						q="mimeType='application/vnd.google-apps.folder' and '{}' in parents{}".format(remote.ID,filter),
						pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name)").execute() 
					items = results.get('files', [])			
					try:
						page_token = results.get('nextPageToken', None)	
					except:pass
					for file in items:
						try:
							file_list.append([file['name'],path])
						except:pass							
					if Print==True:
						print(f'- {path}: Total Retrieved '+str(len(file_list)))	
					if page_token == None:
						break	
		except:
			print(f'- {path}: Retrieved 0')
			return False	
	if not file_list:
		return False
	file_list.sort(key=lambda x: x[0])
	if Pick==True:
		if pickmode!='single':
			title = 'Select results (press SPACE\RIGHT to mark\\unmark, ENTER to continue): '
		elif mime=="files":
			title = 'Select result:'
		else:
			title = 'Select result:\n + Press space or right to select content \n + Press E to move to file selection phase \n + Press X to exit selection'
		oplist=list();cleanlist=list()
		if mime=='folders':
			for item in file_list:
				oplist.append(item[0])
				cleanlist.append(clean_name(item[0]))
		else:
			for item in file_list:
				sz=str(sq_tools.getSize(int(item[1])))
				oplist.append(item[0]+' | '+sz)
				cleanlist.append(clean_name(item[0])+' | '+sz)				
		options = cleanlist	
		if pickmode!='single':
			selected = pick(options, title, multi_select=True, min_selection_count=0)
		elif mime=="files":	
			selected = pick(options, title, min_selection_count=1)	
			if selected[0]==False:
				return False			
		else:
			picker = Picker(options, title, min_selection_count=1)
			def end_selection(picker):
				return False,-1
			picker.register_custom_handler(ord('e'),  end_selection)
			picker.register_custom_handler(ord('E'),  end_selection)		
			if mime!="files":		
				def exit_selection(picker):
					return "EXIT",-1
				picker.register_custom_handler(ord('x'),  exit_selection)
				picker.register_custom_handler(ord('X'),  exit_selection)			
			selected=picker.start()
			if selected[0]==False:
				return False
			if selected[0]=="EXIT":		
				return "EXIT"
		# print (selected)		
		oplist=file_list;file_list=list()
		if pickmode=='single':
			if mime=='folders':
				basepath=oplist[selected[1]][1]
				if basepath[-1]!="/" and basepath[-1]!="\\":	
					basepath=basepath+'/'
				pth=basepath+oplist[selected[1]][0]	
			else:
				basepath=oplist[selected[1]][2]
				if basepath[-1]!="/" and basepath[-1]!="\\":	
					basepath=basepath+'/'
				pth=basepath+oplist[selected[1]][0]					
			return pth
		if mime=='folders':
			for file in selected:
				basepath=oplist[file[1]][1]
				if basepath[-1]!="/" and basepath[-1]!="\\":	
					basepath=basepath+'/'
				pth=basepath+oplist[file[1]][0]	
				file_list.append(pth)
		else:
			for file in selected:
				basepath=oplist[file[1]][2]
				if basepath[-1]!="/" and basepath[-1]!="\\":	
					basepath=basepath+'/'
				pth=basepath+oplist[file[1]][0]		
				file_list.append(pth)
		if not file_list:
			return False
		if Print==True:	
			print("\n- User selected the following results: ")
			for file in file_list:
				print(file)
		else:
			print("- User selected {} files".format(str(len(file_list))))
		if TDlist!=False and file_list:
			file_listv2.append([file_list,TD])
	if TDlist!=False:			
		return file_listv2
	return file_list
	
def get_TeamDrives(token='drive:',Print=False):
	remote=location(route=token)
	TD_list=remote.get_TD()
	names=list();ids=list()
	names.append('None');ids.append('root')
	for drive in TD_list:
		names.append(drive['name']);ids.append(drive['id'])		
		if Print!=False:  
			print(drive['name']+' id: '+drive['id'])
	return names,ids
	# print(remote.ID)
	# print(remote.name)
	
def get_Data(path,TD=None,get_hash=False,Print=True,ID=None):
	if ID==None:
		if 	TD!= None:
			remote=location(route=path,TD_Name=TD)
		else:
			remote=location(route=path)
	else:
		if 	TD!= None:
			remote=location(route=path,TD_Name=TD,ID=ID)
		else:
			remote=location(route=path,ID=ID)	
	ID=remote.ID
	type=remote.filetype
	name=remote.name
	if Print==True:
		print('- ID: '+ID);print('- Name: '+name);print('- Type: '+type)
	if type!='folder':
		size=remote.get_size(remote.ID,remote.token_name)
		if Print==True:
			print('- Size: '+size)
	else:
		size=None
	if get_hash==True:
		md5=remote.get_hash(remote.ID,remote.token_name)	
		if Print==True:
			print('- MD5Hash: '+md5)	
	else:
		md5=None
	return ID,name,type,size,md5,remote
	
def download(path,ofolder,TD=None,filter=None,trimm=True):
	if path=='pick':
		account=token_picker()
		TD=TD_picker(account)
		return
	test=path.split(".+")
	if TD=='pick':
		TD=TD_picker(path)		
	if len(test)>1 or path.endswith('/') or path.endswith('\\'):
		type="folder"
	else:	
		ID,name,type,size,md5,remote=get_Data(path,TD=TD,Print=False)
		output=os.path.join(ofolder,name)
	if type!='file':
		# print('Path is a folder')
		folderpicker(path,ofolder,TD,filter)
		return
	else:
		if name.endswith(".xci") and trimm==True:
			end=DriveTools.get_xci_rom_size(remote)
			hd=get_html_header(remote.access_token,off1=0,off2=end)
			remote.get_session(hd)
			size=end
		else:
			remote.get_session()
		buf=int(64*1024)
		print("- Downloading file to {}".format(output))
		t = tqdm(total=int(size), unit='B', unit_scale=True, leave=False)	
		with open(output,"wb") as o:
			for data in remote.response.iter_content(chunk_size=buf):
				o.write(data)
				t.update(len(data))
				if not data:
					break	
		t.close()		
		print("  *Finished*")		

def TD_picker(path):		
	remote=location(route=path)
	names,ids=get_TeamDrives(remote.token_name)
	if names:
		title = 'Select Teamdrive (press SPACE\RIGHT to mark\\unmark, ENTER to continue): \n"None" will return the My-Drive section of the account'
		options = names	
		selected = pick(options, title, min_selection_count=1)
		TD=selected[0]
		if TD=='None':
			TD=None
	else:
		TD=None
	return TD

def folderpicker(path,ofolder=None,TD=None,filter=None,mode='download'):
	pathlist=search_folder(path,TD,pick=True,Print=False,filter=filter)
	counter=len(pathlist)
	for path in pathlist:
		if mode=='download':
			download(path,ofolder,TD)
		elif mode=='get_cnmt_data':
			DriveTools.get_cnmt_data(path,TD)
		elif mode=='decompress':
			from Drive.Decompress import decompress
			decompress(path,ofolder,TD)		
		elif mode=='supertrimm':
			from Drive.XciTools import supertrimm
			supertrimm(path,ofolder,TD)		
		elif mode=='read_cnmt':
			from Drive.Info import read_cnmt
			read_cnmt(path,TD)				
		counter-=1
		if counter>0:
			print("Still {} files to download".format(str(counter)))
			
def add_to_drive(url=None,ID=None,filepath=None,makecopy=False,TD=None):
	# print(url);print(ID);print(filepath);print(makecopy);print(TD);
	try:
		if ID==None and url==None:
			return False
		if filepath==None:
			return False			
		if ID!=None:
			file_id=ID
		else:	
			file_id, is_download_link=Public.parse_url(url)
		if TD==None:	
			remote=location(route=filepath)				
		else:
			remote=location(route=filepath,TD_Name=TD)		
		# remote=location(route=filepath)
		drive=remote.drivename
		FolderID=remote.ID
		if makecopy!=True:
			file = remote.drive_service.files().update(fileId=file_id,
											addParents=FolderID,
											fields='id,parents,name').execute()
			name=file.get('name')
		else:
			result=remote.drive_service.files().get(fileId=file_id, fields="name,mimeType").execute()	
			name=result['name']	
			newfile = {'name': name, 'parents' : [FolderID]}

			file = remote.drive_service.files().copy(fileId=file_id, 
											body=newfile,
											fields='id, parents').execute()	
		print("{} was added to drive".format(name))												
	except IOError as e:
		print(e, file=sys.stderr)	
	return name		
	
# def get_plink_data(url=None,ID=None,filepath=None,TD=None):
	# try:
		# if ID==None and url==None:
			# return False
		# if filepath==None:
			# return False			
		# if ID!=None:
			# file_id=ID
		# else:	
			# file_id, is_download_link=Public.parse_url(url)
		# if TD==None:	
			# remote=location(route=filepath)				
		# else:
			# remote=location(route=filepath,TD_Name=TD)		
		# remote=location(route=filepath)
		# drive=remote.drivename
		# FolderID=remote.ID
		# result=remote.drive_service.files().get(fileId=file_id, fields="name,mimeType").execute()	
		# name=result['name']	
		# id=file_id									
	# except IOError as e:
		# print(e, file=sys.stderr)	
	# return name,id		

def delete_from_drive(filepath=None,url=None,lkID=None,TD=None):
	try:
		if filepath==None and url==None and lkID==None:
			return False
		if TD==None:	
			remote=location(route=filepath)				
		else:
			remote=location(route=filepath,TD_Name=TD)	
		if lkID != None:
			file_id=lkID	
		elif url != None:
			file_id, is_download_link=Public.parse_url(url)
		elif filepath != None:
			file_id=remote.ID
			
		file = remote.drive_service.files().get(fileId=file_id,
										 fields='parents').execute()
		# print(file.get('parents'))										 
		previous_parents = ",".join(file.get('parents'))
		file = remote.drive_service.files().update(fileId=file_id,
											removeParents=previous_parents,
											fields='name,id,parents').execute()
		print("{} was removed from drive".format(file['name']))									
	except IOError as e:
		print(e, file=sys.stderr)											
		

def move(origin,destiny,originTD,destinyTD):		
	if originTD==None:	
		Oremote=location(route=origin)				
	else:
		Oremote=location(route=origin,TD_Name=originTD)		
	fileId=Oremote.ID
	# print(fileId)
	# print(Oremote.name)
	if destinyTD==None:	
		Dremote=location(route=destiny)				
	else:
		Dremote=location(route=destiny,TD_Name=destinyTD)		
	folderID=Dremote.ID
	# print(folderID)
	file = Oremote.drive_service.files().get(fileId=fileId,
									 fields='parents').execute()	
	previous_parents = ",".join(file.get('parents'))									 
	file = Dremote.drive_service.files().update(fileId=fileId,
										removeParents=previous_parents,
										addParents=folderID,
										fields='id, parents').execute()		

def rename(filepath=None,newname=None,TD=None,remote=None):	
	if remote==None:
		if 	TD!= None:
			remote=location(route=filepath,TD_Name=TD)
		else:
			remote=location(route=filepath)
	fileId=remote.ID
	name=remote.name
	file = remote.drive_service.files().update(fileId=fileId,
										supportsAllDrives='true',
										body={'name': newname},
										fields='id, name').execute()		
	finalname=file.get('name')
	print("{} renamed to {}".format(name,finalname))

def create_folder(filepath):
	c=0;parent='root';endID=False
	try:
		remote=location(route=filepath)
		if remote.ID!=None:
			print("- Folder already exists")
			return True,remote.ID	
		else:
			token_name,folder_list=get_path_parameters(filepath)
			remote=location(route=token_name)	
			if remote.ID==None:
				print("Bad token")
				return False,False	
			folder="{}:".format(token_name)
			for j in folder_list:
				folder+=('/'+j)
				remote=location(route=folder)
				if remote.ID==None:
					try:
						file_metadata = {
							'name': j,
							'mimeType': 'application/vnd.google-apps.folder',
							'parents': [parent]
						}
						# print(file_metadata)
						file = remote.drive_service.files().create(body=file_metadata,
															fields='id').execute()
						parent=file.get('id')
						endID=parent						
						print("Created {} with ID: {}".format(folder,parent))
					except:	
						return False,False
				else:
					parent=remote.ID		
	except:
			token_name,folder_list=get_path_parameters(filepath)
			remote=location(route=token_name)	
			if remote.ID==None:
				print("Bad token")
				return False,False	
			folder="{}:".format(token_name)
			for j in folder_list:
				folder+=('/'+j)
				remote=location(route=folder)
				if remote.ID==None:
					try:
						file_metadata = {
							'name': j,
							'mimeType': 'application/vnd.google-apps.folder',
							'parents': [parent]
						}
						print(file_metadata)
						file = remote.drive_service.files().create(body=file_metadata,
															fields='id').execute()
						parent=file.get('id')
						endID=parent						
						print("Created {} with ID: {}".format(folder,parent))
					except:	
						return False,False
				else:
					parent=remote.ID
	return True,endID
			
def get_parents(path,ID=None,url=None):
	file_id=ID
	remote=location(route=path)		
	if ID !=None:
		file = remote.drive_service.files().get(fileId=file_id,
					 fields='parents').execute()
		return file.get('parents')			 
	elif url !=None:
		file_id, is_download_link=Public.parse_url(url)
		file = remote.drive_service.files().get(fileId=file_id,
					 fields='parents').execute()
		return file.get('parents')				
	else: 
		return False

def clean_name(name):
	import nutdb
	name = re.sub(r'[àâá@äå]', 'a', name);name = re.sub(r'[ÀÂÁÄÅ]', 'A', name)
	name = re.sub(r'[èêéë]', 'e', name);name = re.sub(r'[ÈÊÉË]', 'E', name)
	name = re.sub(r'[ìîíï]', 'i', name);name = re.sub(r'[ÌÎÍÏ]', 'I', name)
	name = re.sub(r'[òôóöø]', 'o', name);name = re.sub(r'[ÒÔÓÖØ]', 'O', name)
	name = re.sub(r'[ùûúü]', 'u', name);name = re.sub(r'[ÙÛÚÜ]', 'U', name)
	converter = nutdb.kakashi_conv()
	name=converter.do(name)	
	if name[0] == ' ':
		name=name[1:]			
	name=name[0].upper()+name[1:]
	name=nutdb.set_roma_uppercases(name)
	return name

		