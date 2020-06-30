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

# def create serviceDB:
	# import DBModule

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
	def __init__(self,SCOPES=None,token='drive',SCOPES_type='default',headless=True,apiver='v2',json_file=None):
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
					json.load(jfile)	
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
			self.access_token = creds.token_uri		
				
def add_to_drive(token=None,parent=None,ID=None,makecopy=False,json_file=None):
	# print(url);print(ID);print(filepath);print(makecopy);print(TD);
	if json_file==None:
		remote=auth(token=token)
	else:
		remote=auth(token=json_file)		
	if parent==None:
		parent='root'
	try:
		file_id=ID
		FolderID=parent
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
	
def show_files(token=None,mime='files',parent='root',filter='',Print=True,json_file=None):
	# print(url);print(ID);print(filepath);print(makecopy);print(TD);
	if json_file==None:
		remote=auth(token=token)
	else:
		remote=auth(token=json_file)
	drive_service=remote.drive_service
	file_list=list()
	if filter==None or filter=="":
		filter=""
	else:
		filter=" and name contains '{}'".format(filter)	
	try:
		if mime=='files' or mime=='all':
			page_token = None;pagesize=1000
			while True:		
				if parent!= 'root':
					results = drive_service.files().list(
					q="mimeType!='application/vnd.google-apps.folder' and '{}' in parents{}".format(parent,filter),
					pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name, size)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute() 		
				else:
					results = drive_service.files().list(
					q="mimeType!='application/vnd.google-apps.folder' and '{}' in parents{}".format('root',filter),
					pageSize=100,fields="nextPageToken, files(id, name, size)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute() 
				items = results.get('files', [])
				try:
					page_token = results.get('nextPageToken', None)	
				except:pass
				for file in items:
					try:
						file_list.append([file['name'],file['size'],file['id'],"file"])
					except:
						file_list.append([file['name'],file['id'],"folder"])
					pass	
				if Print==True:
					print('- Total Retrieved '+str(len(file_list)))	
				if page_token == None:
					break	
		if mime=='folders' or mime=='all':		
			page_token = None;pagesize=100
			while True:
				if parent != 'root':
					results = drive_service.files().list(
					q="mimeType='application/vnd.google-apps.folder' and '{}' in parents{}".format(parent,filter),
					pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name)",includeItemsFromAllDrives = True,supportsAllDrives = True).execute() 
				else:
					results = drive_service.files().list(
					q="mimeType='application/vnd.google-apps.folder' and '{}' in parents{}".format(parent,filter),
					pageSize=pagesize,pageToken=page_token,fields="nextPageToken, files(id, name)").execute() 
				items = results.get('files', [])
				try:
					page_token = results.get('nextPageToken', None)	
				except:pass
				for file in items:
					try:
						file_list.append([file['name'],file['size'],file['id'],"file"])
					except:
						file_list.append([file['name'],file['id'],"folder"])
					pass	
				if Print==True:
					print('- Total Retrieved '+str(len(file_list)))	
				if page_token == None:
					break					
		for f in file_list:
			print(f)		
	except IOError as e:
		print(e, file=sys.stderr)	
		
def add_file_to_all_SA(SAfolder=None,ID=None,parent='root'):
	if os.path.exists(SAfolder):
		from listmanager import folder_to_list
		jfiles=folder_to_list(SAfolder,['json'])
		for j in jfiles:
			add_to_drive(json_file=j,parent=parent,ID=ID,makecopy=False)
			print('{} Added to {}'.format(ID,j))