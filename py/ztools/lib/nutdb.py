from urllib.request import urlopen
import requests
try:
	import ujson as json
except:
	import json
import Hex
from binascii import hexlify as hx, unhexlify as uhx
import pykakasi
import os
import Print
from tqdm import tqdm
import time
import csv
import chardet
from googletrans import Translator
import ast
from difflib import SequenceMatcher
import re
import listmanager
import DBmodule as dbmodule
from datetime import date

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

def get_titlesurl(tfile):
	with open(tfile,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'URL' in csvheader:
					weburl=csvheader.index('URL')	
				else:break	
			else:	
				url=str(row[weburl])
				return url	
				
def get_otherurl(tfile,dbname):
	with open(tfile,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'URL' and 'NAME' in csvheader:
					weburl=csvheader.index('URL')
					name=csvheader.index('NAME')
				else:break	
			else:
				if dbname.lower() == str(row[name]).lower():
					url=str(row[weburl])
					return url

if os.path.exists(zconfig_dir):
	DATABASE_folder=os.path.join(zconfig_dir, 'DB')
	nutdbfile=os.path.join(DATABASE_folder,'nutdb.json')	
	urlconfig=os.path.join(zconfig_dir,'NUT_DB_URL.txt')
	urlregions=os.path.join(zconfig_dir,'NUT_DB_REGIONS_URL.txt')
	urlconfig_mirror=os.path.join(zconfig_dir,'NUT_DB_URL_mirror.txt')
	urlregions_mirror=os.path.join(zconfig_dir,'NUT_DB_REGIONS_URL_mirror.txt')		
	if os.path.exists(urlconfig):
		json_url = get_titlesurl(urlconfig)	
		json_url_mirror = get_titlesurl(urlconfig_mirror)	
	else:
		urlconfig=os.path.join(squirrel_dir,'NUT_DB_URL.txt')
		urlregions=os.path.join(squirrel_dir,'NUT_DB_REGIONS_URL.txt')	
		urlconfig_mirror=os.path.join(squirrel_dir,'NUT_DB_URL_mirror.txt')
		urlregions_mirror=os.path.join(squirrel_dir,'NUT_DB_REGIONS_URL_mirror.txt')			
		DATABASE_folder=squirrel_dir
		try:
			if os.path.exists(urlconfig):	
				json_url = get_titlesurl(urlconfig)		
				json_url_mirror = get_titlesurl(urlconfig_mirror)	
			else:	
				json_url='http://tinfoil.media/repo/db/titles.US.en.json'
				json_url_mirror='https://raw.githubusercontent.com/julesontheroad/titledb/master/titles.US.en.json'				
		except:
			if os.path.exists(urlconfig_mirror):	
				json_url = get_titlesurl(urlconfig_mirror)		
			else:	
				json_url='https://raw.githubusercontent.com/julesontheroad/titledb/master/titles.US.en.json'			
else:
	nutdbfile='nutdb.json'
	urlconfig=os.path.join(squirrel_dir,'NUT_DB_URL.txt')
	urlregions=os.path.join(squirrel_dir,'NUT_DB_REGIONS_URL.txt')
	urlconfig_mirror=os.path.join(squirrel_dir,'NUT_DB_URL_mirror.txt')
	urlregions_mirror=os.path.join(squirrel_dir,'NUT_DB_REGIONS_URL_mirror.txt')		
	DATABASE_folder=squirrel_dir	
	try:
		if os.path.exists(urlconfig):	
			json_url = get_titlesurl(urlconfig)		
		else:	
			json_url='http://tinfoil.media/repo/db/titles.US.en.json'
	except:
		if os.path.exists(urlconfig_mirror):	
			json_url = get_titlesurl(urlconfig_mirror)		
		else:	
			json_url='https://raw.githubusercontent.com/julesontheroad/titledb/master/titles.US.en.json'
			
if not os.path.exists(DATABASE_folder):
	os.makedirs(DATABASE_folder)	
	
apivjson=os.path.join(DATABASE_folder,'apiv.json')	

def get_apivjson():
	try:
		response = requests.get('http://tinfoil.io/Api/patches/get', stream=True)
	except BaseException as e:
		Print.error('Exception: ' + str(e))		
	if '<Response [404]>'!=str(response):
		tempfile=apivjson[:-4]+'2.json'		
		try:
			with open(tempfile,'wb') as nutfile:
				print('Getting apiv json')
				for data in response:
					nutfile.write(data)
					if not data:
						break	
			with open(tempfile) as json_file:					
				data = json.load(json_file)	
			app_json = json.dumps(data, indent=4)		
			with open(apivjson, 'w') as json_file:
			  json_file.write(app_json)			
			try:os.remove(tempfile)
			except:pass	
		except BaseException as e:
			Print.error('Exception: ' + str(e))	
			pass			

def get_DBfolder():
	return DATABASE_folder
	
def getnutdb():
	try:
		response = requests.get(json_url, stream=True)
	except BaseException as e:
		Print.error('Exception: ' + str(e))	
	if '<Response [404]>'!=str(response):
		tempfile=nutdbfile[:-4]+'2.json'		
		try:
			with open(tempfile,'wb') as nutfile:
				print('Getting NUTDB json')
				for data in response.iter_content(65536):
					nutfile.write(data)
					if not data:
						break
			with open(tempfile) as json_file:					
				data = json.load(json_file)	
			app_json = json.dumps(data, indent=4)		
			with open(nutdbfile, 'w') as json_file:
			  json_file.write(app_json)			
			try:os.remove(tempfile)
			except:pass	
		except:
			try:
				response = requests.get(json_url_mirror, stream=True)
			except BaseException as e:
				Print.error('Exception: ' + str(e))					
			if '<Response [404]>'!=str(response):
				tempfile=nutdbfile[:-4]+'2.json'
				try:
					with open(tempfile,'wb') as nutfile:
						print('Error in nutdb origin -> Getting NUTDB json using mirror')
						for data in response.iter_content(65536):
							nutfile.write(data)
							if not data:
								break
					with open(tempfile) as json_file:					
						data = json.load(json_file)				
					app_json = json.dumps(data, indent=4)		
					with open(nutdbfile, 'w') as json_file:
					  json_file.write(app_json)			
					try:os.remove(tempfile)
					except:pass
					return True	
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
					try:os.remove(tempfile)
					except:pass	
					os.utime(nutdbfile,(time.time(),time.time()))	
					print('DB origin is corrupt. Old Files were preserved.')
					print('The program will retry in the next refresh cicle')
					return False
			else:
				print(json_url)
				print("Response 404. Old Files weren't removed")
				os.utime(nutdbfile,(time.time(),time.time()))			
				return False	
	else:
		try:
			response = requests.get(json_url_mirror, stream=True)
		except BaseException as e:
			Print.error('Exception: ' + str(e))	
		if '<Response [404]>'!=str(response):
			tempfile=nutdbfile[:-4]+'2.json'			
			try:
				with open(tempfile,'wb') as nutfile:
					print('Error in nutdb origin -> Getting NUTDB json using mirror')
					for data in response.iter_content(65536):
						nutfile.write(data)
						if not data:
							break
				with open(tempfile) as json_file:					
					data = json.load(json_file)				
				app_json = json.dumps(data, indent=4)		
				with open(nutdbfile, 'w') as json_file:
				  json_file.write(app_json)			
				try:os.remove(tempfile)
				except:pass
				return False
			except BaseException as e:
				Print.error('Exception: ' + str(e))		
				try:os.remove(tempfile)
				except:pass	
				os.utime(nutdbfile,(time.time(),time.time()))	
				print('DB origin is corrupt. Old Files were preserved.')
				print('The program will retry in the next refresh cicle')
				return True			
		else:
			print(json_url)
			print("Response 404. Old Files weren't removed")
			os.utime(nutdbfile,(time.time(),time.time()))			
			return False			

def regionurl(region):	
	with open(urlregions,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'REGION' and 'URL' in csvheader:
					reg=csvheader.index('REGION')
					weburl=csvheader.index('URL')	
				else:break	
			else:	
				if str(region).lower()==str(row[reg]).lower():
					url=str(row[weburl])
					break
	try:
		response = requests.get(url, stream=True)
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	if '<Response [404]>'!=str(response):
		return url
	else:
		with open(urlregions_mirror,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0	
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
					if 'REGION' and 'URL' in csvheader:
						reg=csvheader.index('REGION')
						weburl=csvheader.index('URL')	
					else:break	
				else:	
					if str(region).lower()==str(row[reg]).lower():
						url=str(row[weburl])
						return url	
					
def region_refresh_time(region):	
	th=24;tm=0;ts=0
	with open(urlregions,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'REGION'in csvheader:
					reg=csvheader.index('REGION')
				else:break	
				if 'REFRESH(h)'in csvheader:
					indexh=csvheader.index('REFRESH(h)')
				else:break		
				if 'REFRESH(m)'in csvheader:
					indexm=csvheader.index('REFRESH(m)')
				else:break	
				if 'REFRESH(s)'in csvheader:
					indexs=csvheader.index('REFRESH(s)')
				else:break								
			else:	
				if str(region).lower()==str(row[reg]).lower():
					try:
						th=int(str(row[indexh]))
					except:	pass
					try:
						tm=int(str(row[indexm]))
					except:	pass
					try:
						ts=int(str(row[indexs]))
					except:	pass		
					break
	return th,tm,ts		
	
def others_refresh_time(tfile,dbname):	
	th=24;tm=0;ts=0
	with open(tfile,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'NAME'in csvheader:
					name=csvheader.index('NAME')
				else:break	
				if 'REFRESH(h)'in csvheader:
					indexh=csvheader.index('REFRESH(h)')
				else:break		
				if 'REFRESH(m)'in csvheader:
					indexm=csvheader.index('REFRESH(m)')
				else:break	
				if 'REFRESH(s)'in csvheader:
					indexs=csvheader.index('REFRESH(s)')
				else:break								
			else:	
				if str(dbname).lower()==str(row[name]).lower():
					try:
						th=int(str(row[indexh]))
					except:	pass
					try:
						tm=int(str(row[indexm]))
					except:	pass
					try:
						ts=int(str(row[indexs]))
					except:	pass		
					break
	return th,tm,ts		

def titles_refresh_time():	
	th=24;tm=0;ts=0
	with open(urlconfig,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'REFRESH(h)'in csvheader:
					indexh=csvheader.index('REFRESH(h)')
				else:break		
				if 'REFRESH(m)'in csvheader:
					indexm=csvheader.index('REFRESH(m)')
				else:break	
				if 'REFRESH(s)'in csvheader:
					indexs=csvheader.index('REFRESH(s)')
				else:break								
			else:	
				try:
					th=int(str(row[indexh]))
				except:	pass
				try:
					tm=int(str(row[indexm]))
				except:	pass
				try:
					ts=int(str(row[indexs]))
				except:	pass		
				break
	return th,tm,ts			
					
def check_region_file(region,nutdb=True):	
	try:
		th,tm,ts=region_refresh_time(region)
	except:
		th=24;tm=0;ts=0
	f='nutdb_'+region+'.json'
	if nutdb==False:
		f=region+'.json'		
	regionfile=os.path.join(DATABASE_folder,f)		
	if not os.path.exists(regionfile):
		try:
			get_regionDB(region)
			return True		
		except:
			return False
	elif (th*60*60+tm*60+ts)>=(9999*60*60):
		return True			
	elif (time.time() - os.path.getmtime(regionfile)) > (th*60*60+tm*60+ts):
		try:
			get_regionDB(region)	
			return True	
		except:
			return False
	else:
		try:
			with open(regionfile) as json_file:
				pass
				return 'Refresh time limit not reached'
		except:
			try:
				get_regionDB(region)	
				return True
			except:
				return False
	return	False							
			
def check_other_file(dbfile,dbname,nutdb=True):	
	if str(dbname.lower()).endswith('_txt'):
		ext='.txt'
		enderf=dbname[:-4]
	else:
		ext='.json'	
		enderf=dbname
	try:
		th,tm,ts=others_refresh_time(dbfile,dbname)
	except:
		th=24;tm=0;ts=0
	f='nutdb_'+enderf+ext
	if nutdb==False:
		f=enderf+ext
	_dbfile_=os.path.join(DATABASE_folder,f)		
	if not os.path.exists(_dbfile_):
		try:
			get_otherDB(dbfile,dbname,f)
			return True
		except:
			return False
	elif (th*60*60+tm*60+ts)>=(9999*60*60):
		return True						
	elif (time.time() - os.path.getmtime(_dbfile_)) > (th*60*60+tm*60+ts):
		try:
			get_otherDB(dbfile,dbname,f)	
			return True	
		except:
			return False
	else:
		try:
			with open(_dbfile_) as json_file:
				pass
				return 'Refresh time limit not reached'
		except:
			try:
				get_otherDB(dbfile,dbname,f)
				return True
			except:
				return False
	return	False

def get_otherDB(dbfile,dbname,f,URL=None):
	if URL==None:
		url=get_otherurl(dbfile,dbname)
		URL=url
	else:
		url=URL
	_dbfile_=os.path.join(DATABASE_folder,f)
	try:
		response = requests.get(url, stream=True)
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	if '<Response [404]>'!=str(response):	
		if os.path.exists(_dbfile_):
			try:os.remove(_dbfile_)
			except:pass		
		try:
			with open(_dbfile_,'wb') as nutfile:
				print('Getting NUTDB json "'+dbname+'"')
				for data in response.iter_content(65536):
					nutfile.write(data)
					if not data:
						break
		except BaseException as e:
			Print.error('Exception: ' + str(e))		
			try:os.remove(_dbfile_)
			except:pass	
		if 	dbname=='versions_txt' and URL==None:	
			check_ver_not_missing(_dbfile_)
		if dbname=='HC_VLIST':
			format_hac_versionlist()
		return True				
	else:
		dbfile_mirror=dbfile[:-4]+'_mirror.txt'
		url=get_otherurl(dbfile_mirror,dbname)
		URL=url
		_dbfile_=os.path.join(DATABASE_folder,f)
		try:
			response = requests.get(url, stream=True)
		except BaseException as e:
			Print.error('Exception: ' + str(e))
		if '<Response [404]>'!=str(response):	
			if os.path.exists(_dbfile_):
				try:os.remove(_dbfile_)
				except:pass		
			try:
				with open(_dbfile_,'wb') as nutfile:
					print('Getting NUTDB json "'+dbname+'"')
					for data in response.iter_content(65536):
						nutfile.write(data)
						if not data:
							break
			except BaseException as e:
				Print.error('Exception: ' + str(e))		
				try:os.remove(_dbfile_)
				except:pass	
			if 	dbname=='versions_txt' and URL==None:	
				check_ver_not_missing(_dbfile_)				
			return True			
		else:	
			URL=None
			if 	dbname=='versions_txt' and URL==None:
				check_ver_not_missing(_dbfile_,force=True)	
			else:	
				print(dbname)
				print("Response 404. Old Files weren't removed")	
				return False	

def check_ver_not_missing(_dbfile_,force=False):
	if force==True:
		get_otherDB(urlconfig,'versions_txt','nutdb_versions.txt',URL='http://tinfoil.media/repo/db/versions.txt')	
		get_otherDB(urlconfig,'versions','nutdb_versions.json')			
		return
	try:	
		with open(_dbfile_,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0	
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
					if 'id' and 'version' in csvheader:
						id=csvheader.index('id')
						ver=csvheader.index('version')	
				else:	
					try:
						tid=str(row[id]).upper() 
						v_=str(row[ver])
						if v_=='':
							print("Version numbers missing falling back to tinfoil media")
							get_otherDB(urlconfig,'versions_txt','nutdb_versions.txt',URL='http://tinfoil.media/repo/db/versions.txt')
							get_otherDB(urlconfig,'versions','nutdb_versions.json')								
					except:
						get_otherDB(urlconfig,'versions_txt','nutdb_versions.txt',URL='http://tinfoil.media/repo/db/versions.txt')
						get_otherDB(urlconfig,'versions','nutdb_versions.json',URL='http://tinfoil.media/repo/db/versions.json')
					break	
	except:
		get_otherDB(urlconfig,'versions_txt','nutdb_versions.txt',URL='http://tinfoil.media/repo/db/versions.txt')	
		get_otherDB(urlconfig,'versions','nutdb_versions.json')			
	consolidate_versiondb()

def consolidate_versiondb():
	ver_txt=os.path.join(DATABASE_folder, 'nutdb_versions.txt')
	ver_JSON=os.path.join(DATABASE_folder, 'nutdb_versions.json')
	titles_JSON=os.path.join(DATABASE_folder, 'nutdb.json')	
	hcvfile=os.path.join(DATABASE_folder,'HC_VLIST.json')
	ver_txt_dict={};data={}
	if os.path.exists(ver_txt):	
		with open(ver_txt,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0			
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
					if 'id' and 'version' in csvheader:
						id=csvheader.index('id')
						ver=csvheader.index('version')	
					else:break	
				else:	
					tid=str(row[id]).upper() 
					v_=str(row[ver])
					if v_=="" and tid.endswith('800'):
						continue
						# v_=65536
					elif v_=="":
						v_=0					
					if tid.endswith('800'):
						tid=tid[:-3]+'000'					
					if not tid in ver_txt_dict:
						ver_txt_dict[tid]=v_			
					else:
						if int(v_)>int(ver_txt_dict[tid]):
							ver_txt_dict[tid]=v_
	if os.path.exists(ver_JSON):	
		with open(ver_JSON, 'r') as json_file:	
			data = json.load(json_file)	
			for i in data:
				c=0;tid=str(i).upper()
				if tid.endswith('800'):
					tid=tid[:-3]+'000'
				for j in (data[i]).keys():
					if j=="" and i.endswith('800'):
						continue
						# j=65536
					elif j=="":
						j=0							
					try:
						if not tid in ver_txt_dict:
							ver_txt_dict[tid]=j
						else:
							if int(j)>int(ver_txt_dict[tid]):
								ver_txt_dict[tid]=j
					except BaseException as e:
						Print.error('Exception: ' + str(e))
	if os.path.exists(titles_JSON):	
		with open(titles_JSON, 'r') as json_file:	
			data2 = json.load(json_file)	
			for i in data2:
				c=0;tid=str(i).upper()
				if tid.endswith('800'):
					tid=tid[:-3]+'000'
				entry=data2[i]	
				if i.endswith('800'):
					try:
						j=entry['version']
					except:
						continue
						# j=65536
				else:
					try:
						j=entry['version']
					except:
						j=0	
				try:
					if j is None:
						continue
					if not tid in ver_txt_dict:
						ver_txt_dict[tid]=j
					else:
						if int(j)>int(ver_txt_dict[tid]):
							ver_txt_dict[tid]=j
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
	if os.path.exists(hcvfile):	
		with open(hcvfile, 'r') as json_file:	
			data3 = json.load(json_file)	
			for i in data3:
				c=0;tid=str(i).upper()
				if tid.endswith('800'):
					tid=tid[:-3]+'000'
				version=data3[i]	
				if i.endswith('800'):
					try:
						j=version
					except:
						continue
						# j=65536
				else:
					try:
						j=version
					except:
						j=0	
				try:
					if not tid in ver_txt_dict:
						ver_txt_dict[tid]=j
					else:
						if int(j)>int(ver_txt_dict[tid]):
							ver_txt_dict[tid]=j
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
	from copy import deepcopy
	newdict= deepcopy(ver_txt_dict)				
	for i in ver_txt_dict:
		v_=ver_txt_dict[i]
		if int(v_)<65536:
			pass
		elif i.endswith('000'):
			updid=i[:-3]+'800'
			if not updid in newdict:
				newdict[i]='0'
				newdict[updid]=v_	
	ver_txt_dict=newdict
	for i in data:
		tid=i.upper()
		if i.endswith('000'):
			for j in (data[i]).keys():
				if not j=="":
					if int(j)>0 and int(j)<65536:
						ver_txt_dict[tid]=str(j)
						
	with open(ver_txt,'wt',encoding='utf8') as csvfile:			
		csvfile.write('id|version\n')
		for i in sorted(ver_txt_dict.keys()):
			if str(i).upper()=='UNKNOWN':
				continue
			csvfile.write(f"{i}|{ver_txt_dict[i]}\n")
			
def return_versiondb():
	ver_txt=os.path.join(DATABASE_folder, 'nutdb_versions.txt')
	ver_txt_dict={};data={}
	if os.path.exists(ver_txt):	
		with open(ver_txt,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0			
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
					if 'id' and 'version' in csvheader:
						id=csvheader.index('id')
						ver=csvheader.index('version')	
					else:break	
				else:	
					tid=str(row[id]).upper() 
					v_=str(row[ver])
					if v_=="" and tid.endswith('800'):
						v_=65536
					elif v_=="":
						v_=0					
					ver_txt_dict[tid]=v_
	return ver_txt_dict,ver_txt
	
def get_libs_remote_source(lib):
	libraries={}
	libtfile=lib
	with open(libtfile,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0;up=False;tdn=False;	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'library_name' and 'path' and 'TD_name' and 'Update' in csvheader:
					lb=csvheader.index('library_name')
					pth=csvheader.index('path')	
					tdn=csvheader.index('TD_name')	
					up=csvheader.index('Update')	
				else:
					if 'library_name' and 'path' and 'TD_name' in csvheader:
						lb=csvheader.index('library_name')
						tdn=csvheader.index('TD_name')
						pth=csvheader.index('path')				
					else:break	
			else:	
				try:
					update=False
					library=str(row[lb])
					route=str(row[pth])		
					if tdn!=False:
						try:
							TD=str(row[tdn])
							if TD=='':
								TD=None
						except:
							TD=None
					else:	
						TD=None					
					if up!=False:
						try:
							update=str(row[up])
							if update.upper()=="TRUE":
								update=True
							else:
								update=False
						except:	
							update=True
					else:
						update=False
					libraries[library]=[route,TD,update]
				except BaseException as e:
					Print.error('Exception: ' + str(e))			
					pass
		if not libraries:
			return False
	return libraries					
	
def update_version_db_from_gd():	
	from workers import concurrent_scrapper
	remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')		
	ver_txt_dict,ver_txt=return_versiondb()
	libdict=get_libs_remote_source(remote_lib_file)
	if libdict==False:
		sys.exit("No libraries set up")
	pths={};TDs={};
	for entry in libdict.keys():
		pths[entry]=((libdict[entry])[0])
		TDs[entry]=((libdict[entry])[1])
	# print(pths);print(TDs);
	print("1. Parsing files from Google Drive. Please Wait...")		
	# print(pths)
	if isinstance(pths, dict):
		db={}
		for i in pths.keys():
			db[i]={'path':pths[i],'TD_name':TDs[i]}	
		files=concurrent_scrapper(filter='',order='name_ascending',remotelib='all',db=db)
	else:
		db={}
		db[pths]={'path':pths,'TD_name':TDs}			
		files=concurrent_scrapper(filter=filter,order='name_ascending',remotelib='all',db=db)
	remotelist=[]		
	for f in files:
		remotelist.append(f[0])
	remotelist.reverse()
	# for f in remotelist:
		# print(f)
	remotegames={}		
	for g in remotelist:
		entry=listmanager.parsetags(g)
		entry=list(entry)
		entry.append(g)		
		if not entry[0] in remotegames:
			remotegames[entry[0]]=entry
		else:
			v=(remotegames[entry[0]])[1]
			if int(entry[1])>int(v):
				remotegames[entry[0]]=entry		
	print("2. Consolidating DB...")						
	for tid in remotegames.keys():
		if not tid in ver_txt_dict:				
			ver_txt_dict[tid]=int((remotegames[tid])[1])
		else:
			# print(tid)		
			# print((remotegames[tid])[1])
			# print(ver_txt_dict[tid])			
			if int((remotegames[tid])[1])>int(ver_txt_dict[tid]):
				ver_txt_dict[tid]=int((remotegames[tid])[1])
	with open(ver_txt,'wt',encoding='utf8') as csvfile:			
		csvfile.write('id|version\n')
		for i in sorted(ver_txt_dict.keys()):
			csvfile.write(f"{i}|{ver_txt_dict[i]}\n")	
	consolidate_versiondb()			
	
def get_regionDB(region):
	url=regionurl(region)
	f='nutdb_'+region+'.json'
	regionfile=os.path.join(DATABASE_folder,f)
	try:
		response = requests.get(url, stream=True)
	except BaseException as e:
		Print.error('Exception: ' + str(e))			
	if '<Response [404]>'!=str(response):	
		tempfile=regionfile[:-4]+'2.json'			
		try:
			with open(tempfile,'wb') as nutfile:
				print('Getting NUTDB json "'+region+'"')
				for data in response.iter_content(65536):
					nutfile.write(data)
					if not data:
						break
			with open(tempfile) as json_file:					
				data = json.load(json_file)					
			app_json = json.dumps(data, indent=4)		
			with open(regionfile, 'w') as json_file:
			  json_file.write(app_json)				  
			try:os.remove(tempfile)
			except:pass							
		except:
			url.replace("blawar","julesontheroad")
			try:
				response = requests.get(url, stream=True)
			except BaseException as e:
				Print.error('Exception: ' + str(e))	
			if '<Response [404]>'!=str(response):	
				tempfile=regionfile[:-4]+'2.json'			
				try:
					with open(tempfile,'wb') as nutfile:
						print('Getting NUTDB json "'+region+'"')
						for data in response.iter_content(65536):
							nutfile.write(data)
							if not data:
								break
					with open(tempfile) as json_file:					
						data = json.load(json_file)					
					app_json = json.dumps(data, indent=4)		
					with open(regionfile, 'w') as json_file:
					  json_file.write(app_json)				  
					try:os.remove(tempfile)
					except:pass							
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
					try:os.remove(tempfile)
					except:pass	
					os.utime(regionfile,(time.time(),time.time()))
					print('DB origin is corrupt. Old Files were preserved.')
					print('The program will retry in the next refresh cicle')			
				return True	
	else:
		print(json_url)
		print("Response 404. Old Files weren't removed")
		os.utime(regionfile,(time.time(),time.time()))
		return False		

def format_hac_versionlist():	
	try:
		hcvfile=os.path.join(DATABASE_folder,'HC_VLIST.json')
		versionlist={}
		if os.path.exists(hcvfile):
			with open(hcvfile) as json_file:
				data = json.load(json_file)	
			titles=data['titles']
			for entry in titles:
				try:
					tid=entry['id']
					v=entry['version']
					versionlist[tid]=v
				except:pass
		app_json = json.dumps(versionlist, indent=1)		
		with open(hcvfile, 'w') as json_file:
		  json_file.write(app_json)		
	except:pass
	
def force_refresh():
	try:
		getnutdb()
		get_regionDB('America')	
		get_regionDB('Europe')	
		get_regionDB('Japan')	
		get_regionDB('Asia')		
		get_otherDB(urlconfig,'versions_txt','nutdb_versions.txt')
		get_otherDB(urlconfig,'versions','nutdb_versions.json')	
		get_otherDB(urlconfig,'HC_VLIST','HC_VLIST.json')			
		get_otherDB(urlconfig,'cheats','nutdb_cheats.json')	
		get_otherDB(urlconfig,'ninshop','ninshop.json')
		get_otherDB(urlconfig,'metacritic_id','metacritic_id.json')	
		get_otherDB(urlconfig,'fw','fw.json')
		consolidate_versiondb()
		return True
	except BaseException as e:
		Print.error('Exception: ' + str(e))		
		return False
					
def check_current():	
	try:
		th,tm,ts=titles_refresh_time()
	except:
		th=24;tm=0;ts=0	
	if not os.path.exists(nutdbfile):
		getnutdb()
		return True		
	elif (th*60*60+tm*60+ts)>=(9999*60*60):
		return True					
	elif (time.time() - os.path.getmtime(nutdbfile)) > (th*60*60+tm*60+ts):
		try:
			getnutdb()		
			return True		
		except:
			return False
	else:
		try:
			with open(nutdbfile) as json_file:
				pass
				return 'Refresh time limit not reached'
		except:
			try:
				getnutdb()	
				return True
			except:
				return False
	return	False	
	
def force_update():	
	try:
		getnutdb()
		return True
	except:
		return False
try:	
	check_current()
except:pass	
	
def get_contentname(titleid,roman=True,format='tabs'):
	cname=False
	with open(nutdbfile) as json_file:	
		data = json.load(json_file)		
		titleid=str(titleid).lower()
		for i in data:
			check=False
			for j,k in data[i].items():
				if str(j) == 'id':
					if str(k).lower()==titleid:
						check=True	
				if str(j) == 'name' and check==True:
					cname=str(k)
					break
		if cname != False and roman == True:
			converter = kakashi_conv()
			cname=converter.do(cname)	
			if cname[0] == ' ':
				basename=basename[1:]			
			cname=cname[0].upper()+cname[1:]
			cname=set_roma_uppercases(cname)
		else:pass						
		if cname==False:
			return False
	return 	cname		

def get_metascores(titleid):
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid[:-3]+'000'
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()
	check_other_file(urlconfig,'metacritic_id',nutdb=False)
	f='metacritic_id.json'
	metacritic_json=os.path.join(DATABASE_folder,f)	
	metascore=False;userscore=False;openscore=False	
	try:
		with open(metacritic_json) as json_file:	
			data = json.load(json_file)		
			for i in data:
				try:
					if str(i).lower()==str(baseid).lower() or str(i).lower()==str(titleid).lower():			
						for j,k in data[i].items():
							if str(j) == 'metascore':
								metascore=k
							if str(j) == 'userscore':
								userscore=k			
							if str(j) == 'openscore':
								openscore=k											
						break
				except:pass			
	except:pass				
	if metascore==None:
		metascore=False
	else:
		metascore=str(metascore)
	if userscore==None:
		userscore=False
	else:
		userscore=str(userscore)	
	if openscore==None:
		openscore=False
	else:
		openscore=str(openscore)		
	return 	metascore,userscore,openscore			

def get_contenregions(titleid):
	baseid=get_baseid(titleid);baseid=baseid.lower()	
	langue=False
	rglist=['America','Europe','Japan','Asia']
	regions=list()
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()	
	for region in rglist:
		f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		check_region_file(region)
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict and not region in regions:
					if str(dict['id']).lower()==baseid:
						regions.append(region)
						break
	return regions
	
def get_icon(titleid):
	baseid=get_baseid(titleid);baseid=baseid.lower()	
	iconUrl=False
	rglist=['America','Europe','Japan','Asia']
	regions=list()
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()	
	for region in rglist:
		f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		check_region_file(region)
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict and not region in regions:
					if str(dict['id']).lower()==titleid:
						if 'iconUrl' in dict:
							iconUrl=str(dict['iconUrl'])	
							if iconUrl=='None' or iconUrl=='':
								iconUrl=False	
							else:	
								return iconUrl	
	for region in rglist:
		f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		check_region_file(region)
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict and not region in regions:
					if str(dict['id']).lower()==baseid:
						if 'iconUrl' in dict:
							iconUrl=str(dict['iconUrl'])	
							if iconUrl=='None' or iconUrl=='':
								iconUrl=False	
							else:	
								return iconUrl						
	return regions	


def get_dlcname(titleid,roman=True,format='tabs'):
	cname=False;basename=False;name=False
	with open(nutdbfile) as json_file:			
		data = json.load(json_file)	
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()
		for i in data:
			check=False
			for j,k in data[i].items():
				if str(j) == 'id':
					if str(k).lower()==titleid:
						check=True	
				if str(j) == 'name' and check==True:
					cname=str(k)
					break
		for i in data:
			check=False
			for j,k in data[i].items():
				if str(j) == 'id':
					if str(k).lower()==baseid:
						check=True	
				if str(j) == 'name' and check==True:
					basename=str(k)
					break	
		if basename != False and roman == True:
			converter = kakashi_conv()
			basename=converter.do(basename)	
			if basename[0] == ' ':
				basename=basename[1:]
			basename=basename[0].upper()+basename[1:]
			basename=set_roma_uppercases(basename)		
		else:pass		
		if cname != False and roman == True:
			converter = kakashi_conv()
			cname=converter.do(cname)	
			if cname[0] == ' ':
				basename=basename[1:]			
			cname=cname[0].upper()+cname[1:]
			cname=set_roma_uppercases(cname)
		else:pass						
		if cname==False:
			return False
		else:
			if (cname=='None' and basename=='None') or (cname=='None' and basename==False):
				return False
			if basename==False or basename=='None':	
				name=cname
			elif cname!='None':
				name=basename+' '+'['+cname+']'
			else:
				DLCnumb=str(titleid)
				DLCnumb="0000000000000"+DLCnumb[-3:]									
				DLCnumb=bytes.fromhex(DLCnumb)
				DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
				DLCnumb=int(DLCnumb)	
				name = basename+' '+'['+str(DLCnumb)+']'
		if format!='tabs':
			name=name.replace("[", "- ")
			name=name.replace("]", "")
		name=name.replace("\n", "")	
	return 	name			
				

def get_dlcData(titleid,roman=True,format='tabs'):
	cname=False;basename=False;name=False;editor=False		
	with open(nutdbfile) as json_file:			
		data = json.load(json_file)		
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()
		for i in data:
			dict=data[i]
			if 'id' in dict:
				if str(dict['id']).lower()==titleid:
					if 'name' in dict:
						cname=str(dict['name'])
					break
		for i in data:
			dict=data[i]
			if 'id' in dict:
				if str(dict['id']).lower()==baseid:
					if 'name' in dict:
						basename=str(dict['name'])
					if 'publisher' in dict:
						editor=str(dict['publisher'])
					break					
		if basename != False and roman == True and basename != 'None':
			converter = kakashi_conv()
			basename=converter.do(basename)	
			basename=basename[0].upper()+basename[1:]
			basename=set_roma_uppercases(basename)		
		else:pass	
		if editor != False and roman == True and editor != 'None':
			converter = kakashi_conv()
			editor=converter.do(editor)	
			editor=editor[0].upper()+editor[1:]
			editor=set_roma_uppercases(editor)		
		else:pass			
		if cname != False and roman == True and cname != 'None':
			converter = kakashi_conv()
			cname=converter.do(cname)	
			cname=cname[0].upper()+cname[1:]
			cname=set_roma_uppercases(cname)
		else:pass						
		if cname==False:
			return False,False
		else:
			if (cname=='None' and basename=='None') or (cname=='None' and basename==False):
				return False,False
			if basename==False or basename=='None':	
				name=cname
			elif cname!='None':
				name=basename+' '+'['+cname+']'
			else:
				DLCnumb=str(titleid)
				DLCnumb="0000000000000"+DLCnumb[-3:]									
				DLCnumb=bytes.fromhex(DLCnumb)
				DLCnumb=str(int.from_bytes(DLCnumb, byteorder='big'))									
				DLCnumb=int(DLCnumb)	
				name = basename+' '+'['+str(DLCnumb)+']'
		if editor=='None':
			editor=False
		if format!='tabs':
			name=name.replace("[", "- ")
			name=name.replace("]", "")	
		name=name.replace("\n", "")				
	return 	name,editor	
	
def get_content_langue(titleid):	
	langue=False
	rglist=['America','Europe','Japan','Asia']
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()	
	for region in rglist:
		f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		check_region_file(region)
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict:
					if str(dict['id']).lower()==baseid:
						if 'languages' in dict:
							langue=str(dict['languages'])
							if langue=='None':
								langue=False
						break
		if langue != False:
			try:
				langue=convertlangue(langue,region)
			except BaseException as e:
				Print.error('Exception: ' + str(e))	
				pass	
			break
	return langue
	
def get_list_match(token,roma=True,show=False,Print=False):	
	token=token.lower()
	tokenlist=list();
	include_tk=list();exclude_tk=list();filter_tk=list()
	include_val=list();exclude_val=list();filter_val=list()
	langue='';match=''
	if '{' in token or '}' in token:
		var_=token[1:-1]
		tokenlist=var_.split(".")
		for v in tokenlist:
			if v[0]=='+':
				par=v[1:]
				p_=par.split(":")
				include_tk.append(p_[0])
				include_val.append(p_[1])				
			elif v[0]=='-':
				par=v[1:]
				p_=par.split(":")
				exclude_tk.append(p_[0])
				exclude_val.append(p_[1])					
			elif v[0]=='*':
				par=v[1:]
				p_=par.split(":")
				filter_tk.append(p_[0])
				filter_val.append(p_[1])	
			else:			
				par=v
				p_=par.split(":")
				include_tk.append(p_[0])
				include_val.append(p_[1])			
	# print(include_tk)			
	# print(include_val)
	# print(exclude_tk)			
	# print(exclude_val)
	# print(filter_tk)			
	# print(filter_val)	
	# print(roma)
	# print(show)
	# print(Print)	

	matchdict={};
	rglist=['America','Europe','Japan','Asia']
	for region in rglist:
		f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		check_region_file(region)
		titleid=False;basename=False;version=0
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict:
					titleid=str(dict['id']).upper()
					if titleid=='NONE':
						break		
					else:	
						baseid=get_baseid(titleid)
				if titleid !=baseid:
					basename=get_dlcname(titleid,roman=rome)	
				if 'version' in dict:
					version=str(dict['version'])
					if version=='None':
						version=0
				if 'name' in dict:
					contentname=str(dict['name'])
					if contentname=='None':				
						contentname=''
					if (contentname != '' or contentname != None) and roma == True:
						converter = kakashi_conv()
						contentname=converter.do(contentname)
						contentname=contentname[0].upper()+contentname[1:]
				if 'languages' in dict:
					langue=dict['languages']
					langue=ast.literal_eval(str(langue))
					if isinstance(langue, list):
						langue=','.join(langue)		
				ismatch=False						
				for j,k in data[i].items():
					for i in range(len(include_tk)):
						token=include_tk[i];value=include_val[i]
						if j.lower()==token:
							entry=ast.literal_eval(str(k))
							if isinstance(entry, list):
								for val in entry:
									if str(val).lower()==value:
										ismatch=True
										match=','.join(entry)											
							else:
								entry=str(entry).lower()
								if value in entry:
									ismatch=True
									match=entry
					if ismatch==True:
						for i in range(len(exclude_tk)):					
							token=exclude_tk[i];value=exclude_val[i]		
							if j.lower()==token:
								entry=ast.literal_eval(str(k))
								if isinstance(entry, list):
									for val in entry:
										if str(val).lower()==value:
											ismatch=False	
					if ismatch==True:
						for i in range(len(filter_tk)):					
							token=filter_tk[i];value=filter_val[i]		
							if j.lower()==token:
								entry=ast.literal_eval(str(k))
								if isinstance(entry, list):
									for val in entry:
										if str(val).lower()!=value:
											ismatch=False	
											
				if 	not titleid in matchdict.keys() and titleid != False and ismatch==True:
					if basename==False:
						cname= "{} ({})[{}][v{}].nsp".format(contentname,langue,titleid,version)
					else:
						cname= "{} [{}]({})[{}][v{}].nsp".format(contentname,basename,langue,titleid,version)					
					matchdict[titleid]=cname

	if show==True:
		showlist=list()
		for key in matchdict.keys():
			entry=matchdict[key]
			showlist.append(entry)
		showlist.sort()	
		for entry in showlist:	
			print(entry)
	if Print!=False:
		try:
			dir=os.path.dirname(os.path.abspath(Print))
			if not os.path.exists(dir):
				os.makedirs(dir)	
			printlist=list()
			for key in matchdict.keys():
				entry=matchdict[key]
				printlist.append(entry)
			printlist.sort()	
			with open(Print,"a", encoding='utf8') as tfile: 
				for entry in printlist:	
					tfile.write(entry+'\n')	
		except BaseException as e:
			Print.error('Exception: ' + str(e))	
			pass				
	return 	matchdict
	
def get_baseid(titleid):
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid)
	return baseid.upper()	
		
def get_content_data(titleid,trans=True):	
	releaseDate=False;nsuId=False;category=False;ratingContent=False;
	numberOfPlayers=False;iconUrl=False;screenshots=False;bannerUrl=False
	intro=False;description=False;rating=False;developer=False;
	productCode=False;OnlinePlay=False;SaveDataCloud=False;playmodes=False;
	video=False;url=False;
	rglist=['ninshop','America','Europe','Japan','Asia']
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()	
	for region in rglist:
		if region=='ninshop':
			f=region+'.json'
		else:
			f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		if region=='ninshop':
			check_other_file(urlconfig,region,nutdb=False)
		else:	
			check_region_file(region,nutdb=True)
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict:
					if str(dict['id']).lower()==baseid:
						if 'releaseDate' in dict:
							releaseDate=str(dict['releaseDate'])
							if releaseDate=='None':
								releaseDate=False
							else:
								b=releaseDate
								releaseDate=b[6:]+'/'+b[4:6]+'/'+b[:4]
						if 'nsuId' in dict:
							nsuId=str(dict['nsuId'])
							if nsuId=='None' or nsuId=='':
								nsuId=False
						if 'developer' in dict:
							developer=str(dict['developer'])
							if developer=='None' or developer=='':
								developer=False	
						else:developer=False		
						if 'productCode' in dict:
							productCode=str(dict['productCode'])
							if productCode=='None' or productCode=='':
								productCode=False
						else:
							productCode=False
						if 'OnlinePlay' in dict:
							OnlinePlay=str(dict['OnlinePlay'])
							if OnlinePlay==True:
								OnlinePlay='Yes'
							elif OnlinePlay==False:
								OnlinePlay='No'							
							if OnlinePlay=='None' or OnlinePlay=='':
								OnlinePlay=False
						else:
							OnlinePlay=False							
						if 'SaveDataCloud' in dict:
							SaveDataCloud=str(dict['SaveDataCloud'])
							if SaveDataCloud==True:
								SaveDataCloud='Yes'
							elif SaveDataCloud==False:
								SaveDataCloud='No'							
							if SaveDataCloud=='None' or SaveDataCloud=='':
								SaveDataCloud=False
						else:
							SaveDataCloud=False								
						if 'category' in dict:
							category=str(dict['category'])
							try:	
								x = [x.strip() for x in eval(category)]							
								category=x
							except:pass	
							if category=='None' or str((', '.join(category)))=='':
								category=False		
							elif region=='Japan' or region=='Asia':
								converter = kakashi_conv()
								romalist=list()
								for item in category:										
									item=converter.do(item)	
									item=item[0].upper()+item[1:]
									romalist.append(item)
								category=romalist	
						if 'ratingContent' in dict:
							ratingContent=str(dict['ratingContent'])							
							try:									
								x = [x.strip() for x in eval(ratingContent)]							
								ratingContent=x
							except:pass	
							if ratingContent=='None' or str((', '.join(ratingContent)))=='':
								ratingContent=False	
							elif region=='Japan' or region=='Asia':
								converter = kakashi_conv()
								romalist=list()
								for item in ratingContent:										
									item=converter.do(item)	
									item=item[0].upper()+item[1:]
									romalist.append(item)
								ratingContent=romalist	
						if 'playmodes' in dict:
							playmodes=str(dict['playmodes'])
							try:	
								x = [x.strip() for x in eval(playmodes)]							
								playmodes=x
							except:pass	
							if playmodes=='None' or str((', '.join(playmodes)))=='':
								playmodes=False		
						else:playmodes=False	
						if 'numberOfPlayers' in dict:
							numberOfPlayers=str(dict['numberOfPlayers'])
							if numberOfPlayers=='None' or numberOfPlayers=='':
								numberOfPlayers=False	
						if 'rating' in dict:
							rating=str(dict['rating'])
							if rating=='None' or rating=='':
								rating=False									
						if 'iconUrl' in dict:
							iconUrl=str(dict['iconUrl'])	
							if iconUrl=='None' or iconUrl=='':
								iconUrl=False									
						if 'video' in dict:
							video=str(dict['video'])	
							if video=='None' or video=='':
								video=False	
						else:video=False		
						if 'screenshots' in dict:
							screenshots=str(dict['screenshots'])	
							if screenshots=='None' or screenshots=='':
								screenshots=False									
						if 'url' in dict:
							url=str(dict['url'])
							if url=='None' or url=='':
								url=False
						else:url=False		
						if 'bannerUrl' in dict:
							bannerUrl=str(dict['bannerUrl'])
							if bannerUrl=='None' or bannerUrl=='':
								bannerUrl=False									
						if 'intro' in dict:
							intro=str(dict['intro'])
							if intro=='None' or intro=='':
								intro=False			
							elif region=='Japan' or region=='Asia':			
								if trans==False:
									intro=False	
								else:
									try:
										# converter = kakashi_conv()							
										# intro=converter.do(intro)	
										# intro=intro[0].upper()+intro[1:]												
										translator = Translator()
										if region=='Asia':
											translation=translator.translate(intro,dest='en')	
										if region=='Japan':
											translation=translator.translate(intro,src='ja',dest='en')	
										intro=translation.text								
									except: pass																		
						if 'description' in dict:
							description=str(dict['description'])	
							if description=='None' or description=='':
								description=False		
							elif region=='Japan' or region=='Asia':		
								if trans==False:
									description=False	
								else:
									try:
										# converter = kakashi_conv()						
										# description=converter.do(description)	
										# description=description[0].upper()+description[1:]												
										translator = Translator()
										if region=='Asia':
											translation=translator.translate(description,dest='en')	
										if region=='Japan':
											translation=translator.translate(description,src='ja',dest='en')												
										description=translation.text								
									except: pass														
						break
		if nsuId != False or releaseDate != False or category != False:
			break
		if 	nsuId == False and releaseDate == False and category == False:
			region=False
	return nsuId,releaseDate,category,ratingContent,numberOfPlayers,intro,description,iconUrl,screenshots,bannerUrl,region,rating,developer,productCode,OnlinePlay,SaveDataCloud,playmodes,video,url
			
def get_dlcnsuId(titleid):
	nsuId=False
	rglist=['America','Europe','Japan','Asia']
	titleid=str(titleid).lower()	
	for region in rglist:	
		f='nutdb_'+region+'.json'
		regionfile=os.path.join(DATABASE_folder,f)	
		check_region_file(region)
		with open(regionfile) as json_file:	
			data = json.load(json_file)		
			for i in data:
				dict=data[i]
				if 'id' in dict:
					if str(dict['id']).lower()==titleid:
						if 'releaseDate' in dict:
							releaseDate=str(dict['releaseDate'])
						if 'nsuId' in dict:
							nsuId=str(dict['nsuId'])
							if nsuId=='None':
								nsuId=False	
						break
		if nsuId != False:
			break						
	return 	nsuId

def convertlangue(langue,region):
	SupLg=list()
	x = [x.strip() for x in eval(langue)]
	langue=x
	for i in langue:
		if i=='en' and region=='America':
			SupLg.append("US (eng)")
		if i=='en' and region=='Europe':
			SupLg.append("UK (eng)")				
		if i=='ja':
			SupLg.append("JP")				
		if i=='fr':
			SupLg.append("FR")				
		if i=='de':
			SupLg.append("DE")						
		if i=='es':
			SupLg.append("SPA")				
		if i=='it':
			SupLg.append("IT")						
		if i=='nl':
			SupLg.append("DU")									
		if i=='pt':
			SupLg.append("POR")						
		if i=='ru':
			SupLg.append("RU")						
		if i=='ko':
			SupLg.append("KOR")				
		if i=='zh':
			SupLg.append("CH")	
	return SupLg


def get_dlc_baseid(titleid):
	baseid=str(titleid)
	token=int(hx(bytes.fromhex('0'+baseid[-4:-3])),16)-int('1',16)
	token=str(hex(token))[-1]
	token=token.upper()
	baseid=baseid[:-4]+token+'000'	
	return baseid


def get_content_cheats(titleid,version=False,buildId=False):	
	cheatID_list=list();
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()	
	f='nutdb_'+'cheats'+'.json'
	_dbfile_=os.path.join(DATABASE_folder,f)	
	check_other_file(urlconfig,'cheats')
	with open(_dbfile_) as json_file:	
		data = json.load(json_file)		
		for i in data:
			if i.lower()==baseid.lower():
				dict=data[i]
				for j in dict:
					jsonbID=j
					datalv2=dict[j]
					if 'version' in datalv2:
						titleid=str(i).upper()
						version=str(datalv2['version'])
						BuildID=str(j).upper()
						# print (titleid+' v'+version)
						# print('BuildID: '+str(j))
						cheats=list()
						for k in datalv2:
							if k!='version':
								datalv3=datalv2[k]
								if 'title' in datalv3:
									cheat_title=datalv3['title']
									# print("Title: "+datalv3['title'])
								if 'source' in datalv3:
									cheat_source=datalv3['source']
									# print(datalv3['source'])	
									if not 'title' in datalv3:
										cheat_title=''
									cheats.append([cheat_title,cheat_source])
						cheatID_list.append([titleid,version,BuildID,cheats])			
				break
	return cheatID_list
	
def BaseID_tree(titleid,printinfo=True):	
	feed=''
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()		
	f='nutdb_'+'versions'+'.txt'
	_dbfile_=os.path.join(DATABASE_folder,f)	
	check_other_file(urlconfig,'versions_txt')
	baselist=list();updlist=list();dlclist=list()
	with open(_dbfile_,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'id' and 'version' in csvheader:
					id=csvheader.index('id')
					ver=csvheader.index('version')	
				else:break	
			else:	
				tid=str(row[id]).lower() 
				if str(tid).endswith('000'):
					bid=tid
				elif str(tid).endswith('800'):	
					bid=tid[:-3]+'000'
				else:
					tid=tid.lower()
					bid=get_dlc_baseid(tid);bid=bid.lower()				
				if baseid==bid:
					v_=str(row[ver])
					if v_=='':
						v_='0'
					if tid.endswith('000'):
						baselist.append([tid,v_])
						if printinfo==True:
							message=('Base:   '+tid.upper()+' v'+str(v_));print(message);feed+=message+'\n'
					elif tid.endswith('800'):
						updlist.append([tid,v_])
						if printinfo==True:
							message=('Update: '+tid.upper()+' v'+str(v_));print(message);feed+=message+'\n'		
					else:
						dlclist.append([tid,v_])
						if printinfo==True:
							message=('DLC:    '+tid.upper()+' v'+str(v_));print(message);feed+=message+'\n'
				else:pass
	return feed,baselist,updlist,dlclist			

def checkfolder(ofolder,roman=True,printinfo=True):	
	today = date.today()
	today=int(today.strftime("%Y%m%d"))
	# print(str(today))
	feed=''
	rglist=['America','Europe','Japan','Asia']
	
	filelist=listmanager.folder_to_list(ofolder,extlist=['nsp','nsz','xci','xcz'])
  
	# for f in filelist:
		# print(f)
	test2="";test=""
	Datashelve = dbmodule.Dict('File01.dshlv');c=0		
	for filepath in filelist:
		try:
			fileid,fileversion,cctag,nG,nU,nD,baseid=listmanager.parsetags(filepath)
			# print('[{}] [v{}] [{}]'.format(fileid,fileversion,cctag))
			if c==0:
				c+=1
				try:
					Datashelve[str(fileid)]=[filepath,fileid,fileversion,cctag,nG,nU,nD,baseid]				
				except BaseException as e:
					Print.error('Exception: ' + str(e))							
			else:
				try:
					if str(fileid) in Datashelve:
						shelvedfile=Datashelve[str(fileid)]
						#print(shelvedfile[2])
						if shelvedfile[1]==fileid:
							if int(shelvedfile[2])>int(fileversion):							
								Datashelve[str(fileid)]=shelvedfile								
							elif int(shelvedfile[2])== int(fileversion):								
								Datashelve[str(fileid)]=shelvedfile	
							else:										
								Datashelve[str(fileid)]=[filepath,fileid,fileversion,cctag,nG,nU,nD,baseid]									
						else:		
							pass	
					else:
						Datashelve[str(fileid)]=[filepath,fileid,fileversion,cctag,nG,nU,nD,baseid]						
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		except:pass			
	del filelist	

	f='nutdb_'+'versions'+'.txt'
	_dbfile_=os.path.join(DATABASE_folder,f)	
	check_other_file(urlconfig,'versions_txt')
	missID=list()
	with open(_dbfile_,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'id' and 'version' in csvheader:
					id=csvheader.index('id')
					ver=csvheader.index('version')	
				else:break	
			else:	
				tid=str(row[id]).upper() 
				if not tid in Datashelve.keys() and tid.endswith('000'):
					# print(tid)
					missID.append(tid)
				# if updid==tid:
					# v_=str(row[ver])				
					# return ('v'+str(v_))						
	counter=len(missID);c=0
	namedfiles=list();excludefiles=list()
	with open(nutdbfile) as json_file:	
		data = json.load(json_file)		
		for i in data:
			if c >= counter:
				break
			try:	
				check=False
				region='unknown'
				for j,k in data[i].items():
					if str(j) == 'id':
						if str(k).upper() in missID and not str(k).upper() in namedfiles:
							id=str(k).upper()
							check=True	
					if str(j) == 'name' and check==True:
						cname=str(k)
						if roman == True:
							converter = kakashi_conv()
							cname=converter.do(cname)	
							if cname[0] == ' ':
								basename=basename[1:]			
							cname=cname[0].upper()+cname[1:]
							cname=set_roma_uppercases(cname)		
							if cname=='None':
								cname=''
					if str(j) == 'region' :
						region=str(k)
					if str(j) == 'releaseDate' and check==True:
						rdate=int(k)
						if rdate<today:
							b=str(rdate)						
							releaseDate=b[6:]+'/'+b[4:6]+'/'+b[:4]
							print('{}|{}|{}[{}][v{}]'.format(releaseDate,region,cname,id,'0'))						
							c+=1	
							namedfiles.append(id)
							break
						else:
							excludefiles.append(id)
							c+=1						
							break				
			except:
				c+=1
				pass
	for x in missID:
		if x not in namedfiles and x not in excludefiles:
			print('[{}][v{}]'.format(x,'0'))

	Datashelve.close()		
	try:os.remove('File01.dshlv')
	except:pass			
	
def checkfolder_updates(ofolder,roman=True,printinfo=True):	
	today = date.today()
	today=int(today.strftime("%Y%m%d"))
	# print(str(today))
	feed=''
	rglist=['America','Europe','Japan','Asia']
	

	filelist=listmanager.folder_to_list(ofolder,extlist=['nsp','nsz','xci','xcz'])

	# for f in filelist:
		# print(f)
	test2="";test=""
	Datashelve = dbmodule.Dict('File01.dshlv');c=0		
	for filepath in filelist:
		try:
			fileid,fileversion,cctag,nG,nU,nD,baseid=listmanager.parsetags(filepath)
			# print('[{}] [v{}] [{}]'.format(fileid,fileversion,cctag))
			if c==0:
				c+=1
				try:
					Datashelve[str(fileid)]=[filepath,fileid,fileversion,cctag,nG,nU,nD,baseid]				
				except BaseException as e:
					Print.error('Exception: ' + str(e))							
			else:
				try:
					if str(fileid) in Datashelve:
						shelvedfile=Datashelve[str(fileid)]
						#print(shelvedfile[2])
						if shelvedfile[1]==fileid:
							if int(shelvedfile[2])>int(fileversion):							
								Datashelve[str(fileid)]=shelvedfile								
							elif int(shelvedfile[2])== int(fileversion):								
								Datashelve[str(fileid)]=shelvedfile	
							else:										
								Datashelve[str(fileid)]=[filepath,fileid,fileversion,cctag,nG,nU,nD,baseid]									
						else:		
							pass	
					else:
						Datashelve[str(fileid)]=[filepath,fileid,fileversion,cctag,nG,nU,nD,baseid]						
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		except:pass			
	del filelist	

	# print(Datashelve.keys())

	f='nutdb_'+'versions'+'.txt'
	_dbfile_=os.path.join(DATABASE_folder,f)	
	check_other_file(urlconfig,'versions_txt')
	missID=list()
	with open(_dbfile_,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'id' and 'version' in csvheader:
					id=csvheader.index('id')
					ver=csvheader.index('version')	
				else:break	
			else:	
				try:
					tid=str(row[id]).upper() 
					if tid.endswith('800'):
						btid=tid[:-3]+'000'
					else:
						btid=tid
					if (tid in Datashelve.keys() or btid in Datashelve.keys()) and tid.endswith('800'):
						# print(tid)
						try:
							data=Datashelve[tid]
						except:
							data=Datashelve[btid]
						v_=str(row[ver])
						# print(v_)
						# print(data[2])
						# print('..')
						if int(v_)>int(data[2]):		

							missID.append([tid,v_])				

				except:pass
	# print(missID)
	for t,v in missID:
		print('[{}][v{}]'.format(t,v))
	# counter=len(missID);c=0
	# namedfiles=list();excludefiles=list()
	# with open(nutdbfile) as json_file:	
		# data = json.load(json_file)		
		# for i in data:
			# if c >= counter:
				# break
			# try:	
				# check=False
				# for j,k in data[i].items():
					# if str(j) == 'id':
						# if str(k).upper() in missID and not str(k).upper() in namedfiles:
							# id=str(k).upper()
							# check=True	
					# if str(j) == 'name' and check==True:
						# cname=str(k)
						# if roman == True:
							# converter = kakashi_conv()
							# cname=converter.do(cname)	
							# if cname[0] == ' ':
								# basename=basename[1:]			
							# cname=cname[0].upper()+cname[1:]
							# cname=set_roma_uppercases(cname)		
							# if cname=='None':
								# cname=''
					# if str(j) == 'releaseDate' and check==True:
						# rdate=int(k)
						# if rdate<today:
							# print('{}[{}][v{}]'.format(cname,id,'0'))
							# c+=1	
							# namedfiles.append(id)
							# break
						# else:
							# excludefiles.append(id)
							# c+=1						
							# break				
			# except:
				# c+=1
				# pass
	# for x in missID:
		# if x not in namedfiles and x not in excludefiles:
			# print('[{}][v{}]'.format(x,'0'))

	Datashelve.close()		
	try:os.remove('File01.dshlv')
	except:pass			

def getupcoming(roman=True,printinfo=True):	
	today = date.today()
	today=int(today.strftime("%Y%m%d"))
	# print(str(today))
	namedfiles=list();
	with open(nutdbfile) as json_file:	
		data = json.load(json_file)		
		for i in data:
			try:	
				check=False
				for j,k in data[i].items():
					if str(j) == 'id':
						if str(k).upper() not in namedfiles:
							id=str(k).upper()
							check=True	
					if str(j) == 'name' and check==True:
						cname=str(k)
						if roman == True:
							converter = kakashi_conv()
							cname=converter.do(cname)	
							if cname[0] == ' ':
								basename=basename[1:]			
							cname=cname[0].upper()+cname[1:]
							cname=set_roma_uppercases(cname)		
							if cname=='None':
								cname=''
					if str(j) == 'releaseDate' and check==True:
						rdate=int(k)
						if rdate>today:
							b=str(rdate)
							releaseDate=b[6:]+'/'+b[4:6]+'/'+b[:4]
							print('{}: {}[{}][v{}]'.format(releaseDate,cname,id,'0'))
							namedfiles.append(id)
							break
						else:				
							break				
			except:
				pass

def latest_upd(titleid):	
	titleid=str(titleid).lower()	
	if str(titleid).endswith('000'):
		baseid=titleid[:-3]+'000'
	elif str(titleid).endswith('800'):	
		baseid=titleid[:-3]+'000'
	else:
		titleid=str(titleid).lower()
		baseid=get_dlc_baseid(titleid);baseid=baseid.lower()
	updid=baseid[:-3]+'800'
	f='nutdb_'+'versions'+'.txt'
	_dbfile_=os.path.join(DATABASE_folder,f)	
	check_other_file(urlconfig,'versions_txt')
	feed=list()
	with open(_dbfile_,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'id' and 'version' in csvheader:
					id=csvheader.index('id')
					ver=csvheader.index('version')	
				else:break	
			else:	
				tid=str(row[id]).lower() 		
				if updid==tid:
					v_=str(row[ver])				
					return ('v'+str(v_))

def latest_ver(titleid):	
	titleid=str(titleid).lower()	
	f='nutdb_'+'versions'+'.txt'
	_dbfile_=os.path.join(DATABASE_folder,f)	
	check_other_file(urlconfig,'versions_txt')
	feed=list()
	with open(_dbfile_,'rt',encoding='utf8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter='|')	
		i=0	
		for row in readCSV:
			if i==0:
				csvheader=row
				i=1
				if 'id' and 'version' in csvheader:
					id=csvheader.index('id')
					ver=csvheader.index('version')	
				else:break	
			else:	
				tid=str(row[id]).lower() 		
				if titleid==tid:
					v_=str(row[ver])				
					return ('v'+str(v_))					

def set_roma_uppercases(input):
	if '(' in str(input):
		input = input.replace("( ", "(");input = input.replace(" )", ")")	
		tid1=list()
		tid2=list()
		tid1=[pos for pos, char in enumerate(input) if char == '(']
		tid2=[pos for pos, char in enumerate(input) if char == ')']
		if len(tid1)>=len(tid2):
			lentlist=len(tid1)					
		elif len(tid1)<len(tid2):
			lentlist=len(tid2)				
		for i in range(lentlist):	
			try:
				i1=tid1[i]
				i2=tid2[i]+1					
				t=input[i1:i2]
				t=t[0]+t[1].upper()+t[2:]
				input=input[:i1]+t+input[i2:]
			except:pass		
	elif '[' in str(input):
		input = input.replace("[", "(");input = input.replace("]", ")")
		tid1=list()
		tid2=list()
		tid1=[pos for pos, char in enumerate(input) if char == '(']
		tid2=[pos for pos, char in enumerate(input) if char == ')']
		if len(tid1)>=len(tid2):
			lentlist=len(tid1)					
		elif len(tid1)<len(tid2):
			lentlist=len(tid2)				
		for i in range(lentlist):	
			try:
				i1=tid1[i]
				i2=tid2[i]+1					
				t=input[i1:i2]
				t=t[0]+t[1].upper()+t[2:]
				input=input[:i1]+t+input[i2:]
			except:pass		
	else:
		pass
	return 	input

def kakashi_conv():
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
	
def check_files():
	# check_current()	
	rglist=['ninshop','America','Europe','Japan','Asia']
	for region in rglist:
		if region=='ninshop':
			check_other_file(urlconfig,region,nutdb=False)
		else:	
			check_region_file(region,nutdb=True)	
	check_other_file(urlconfig,'metacritic_id',nutdb=False)
	check_other_file(urlconfig,'fw',nutdb=False)	
	check_other_file(urlconfig,'versions_txt')
	check_other_file(urlconfig,'versions')		
	check_other_file(urlconfig,'HC_VLIST')	
	check_other_file(urlconfig,'cheats')
	consolidate_versiondb()	