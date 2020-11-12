from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
import os
import pickle
try:
	import ujson as json
except:
	import json
import requests
from tqdm import tqdm

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
	elif type=='write':
		SCOPES = ['https://www.googleapis.com/auth/drive.file']			
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
		tk = os.path.join(credentials_dir, token)				
		if SCOPES!=None:
			if os.path.exists(tk):
				try: 
					os.remove(tk)
				except:pass	
		else:
			SCOPES = ['https://www.googleapis.com/auth/drive']				
		creds = None;json_auth=False		
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
			
				
def upload_file(filepath,remote=auth(),mimetype='application/octet-stream', parent="root",upload_filename=None, resumable=True, ck=80:
	try:
		chunksize=int(ck)*1024*1024
	except:
		chunksize=30*1024*1024
	print(chunksize)	
	if upload_filename==None:
		upload_filename=str(os.path.basename(os.path.abspath(filepath)))
	filesize=os.path.getsize(filepath)	
	headers = {"Authorization": "Bearer "+remote.access_token, "Content-Type": "application/json"}
	params = {
		"name": upload_filename,
		"mimeType": mimetype,
		"parents": parent
	}
	r = requests.post(
		"https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
		headers=headers,
		data=json.dumps(params)
	)
	location = r.headers['Location']
	print(f"Retrieved location: {location}")
	if filesize > chunksize:
		ini=0;end=chunksize;written=0
		t = tqdm(total=(filesize-1), unit='B', unit_scale=True, leave=False)
		with open(filepath, 'rb') as fp:
			while written<(filesize-1):
				headers = {"Content-Range": "bytes "+str(ini)+"-" + str(end) + "/" + str(filesize)}
				# t.write(str(headers))
				fp.seek(ini)
				dt=fp.read(int(end-ini+1))
				r = requests.put(
					location,
					headers=headers,
					data=dt
				)		
				lg=(int(end-ini))	
				written+=lg
				if lg==0:
					break
				t.update(lg)
				ini=written
				if written+chunksize<(filesize-1):
					end=end+chunksize
				else:
					end=filesize-1
		t.close()		
		print(r.text)					
	else:
		headers = {"Content-Range": "bytes 0-" + str(filesize - 1) + "/" + str(filesize)}
		print(headers)
		print(filepath)	
		r = requests.put(
			location,
			headers=headers,
			data=open(filepath, 'rb')
		)
		print(r.text)
	
	
	