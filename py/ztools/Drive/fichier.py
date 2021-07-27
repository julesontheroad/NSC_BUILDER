import Print
import os
import shutil
import sq_tools
import io
import sys
import listmanager
import csv
import requests
try:
	import ujson as json
except:
	import json
from tqdm import tqdm

# SET ENVIRONMENT
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
_1fichier_token=os.path.join((os.path.join(zconfig_dir, 'credentials')),'_1fichier_token.tk')	
	
def download(url,ofolder):
	if not os.path.exists(_1fichier_token):
		sys.exit("No 1fichier token setup")
	with open(_1fichier_token,'rt',encoding='utf8') as tfile:
		token=(tfile.readline().strip())
	if token==None:
		sys.exit("Missing 1fichier token")		
	APIkey=token
	auth={'Authorization':f'Bearer {APIkey}','Content-Type':'application/json'}
	session = requests.session()
	download_params = {
		'url' : url,
		'inline' : 0,
		'cdn' : 0,
		'restrict_ip':  0,
		'no_ssl' : 0,
	}			
	info_params={
		'url' : url	
	}
	r=session.post('https://api.1fichier.com/v1/file/info.cgi',json=info_params,headers=auth)
	info_dict=r.json()
	# print(info_dict)
	sz=info_dict['size']
	name=info_dict['filename']
	r=session.post('https://api.1fichier.com/v1/download/get_token.cgi',json=download_params,headers=auth)
	dict_=r.json()
	# print(dict_)
	if not dict_['status']=="OK":
		sys.exit(f"API call returned {dict_['status']}")			
	URL=dict_['url']
	sess = requests.session()
	response=sess.get(URL, stream=True)	
	buf=int(64*1024)
	output=os.path.join(ofolder,name)	
	print("- Downloading file to {}".format(output))
	t = tqdm(total=int(sz), unit='B', unit_scale=True, leave=False)	
	with open(output,"wb") as o:
		for data in response.iter_content(chunk_size=buf):
			o.write(data)
			t.update(len(data))
			if not data:
				break	
	t.close()		
	print("  *Finished*")	