# -*- coding: utf-8 -*-
import sys
from binascii import hexlify as hx, unhexlify as uhx
import Hex
import io
import sq_tools
import Fs.Nca as Nca
from Fs.Nca import NcaHeader
import Fs.Nsp as Nsp
import Fs.Nacp as Nacp
from Fs.File import MemoryFile
from hashlib import sha256,sha1
from Drive import Public
from Drive import Private
from Drive import DriveTools

import Keys
from Fs import Type
from Fs.Nacp import Nacp
from Fs.pyNPDM import NPDM
import nutdb
from secondary import clear_Screen
from Drive.XciTools import supertrimm
from Drive.Decompress import decompress
import os
import csv

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

remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
download_lib_file = os.path.join(zconfig_dir, 'download_libraries.txt')

def About():
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

def readInt64(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(8), byteorder=byteorder, signed=signed)

def readInt128(f, byteorder='little', signed = False):
	return int.from_bytes(f.read(16), byteorder=byteorder, signed=signed)

class AESCTR:
	def __init__(self, key, nonce, offset = 0):
		self.key = key
		self.nonce = nonce
		self.seek(offset)

	def encrypt(self, data, ctr=None):
		if ctr is None:
			ctr = self.ctr
		return self.aes.encrypt(data)

	def decrypt(self, data, ctr=None):
		return self.encrypt(data, ctr)

	def seek(self, offset):
		self.ctr = Counter.new(64, prefix=self.nonce[0:8], initial_value=(offset >> 4))
		self.aes = AES.new(self.key, AES.MODE_CTR, counter=self.ctr)

class Section:
	def __init__(self, f):
		self.f = f
		self.offset = readInt64(f)
		self.size = readInt64(f)
		self.cryptoType = readInt64(f)
		readInt64(f) # padding
		self.cryptoKey = f.read(16)
		self.cryptoCounter = f.read(16)

def pick_libraries():
	from python_pick import Picker
	title = 'Select libraries to search:  \n + Press space or right to select content \n + Press E to finish selection'
	db=libraries(remote_lib_file)
	if db==False:
		return False,False
	options = [x for x in db.keys()]
	picker = Picker(options, title,multi_select=True,min_selection_count=1)
	def end_selection(picker):
		return False,-1
	picker.register_custom_handler(ord('e'),  end_selection)
	picker.register_custom_handler(ord('E'),  end_selection)
	selected = picker.start()
	if selected[0]==False:
		return False,False
	# print(selected)
	paths=list();TDs=list()
	for entry in selected:
		paths.append((db[entry[0]])['path'])
		try:
			TDs.append((db[entry[0]])['TD_name'])
		except:
			TDs.append(None)
	# for p in range(len(paths)):
		# print(paths[p])
		# print(TDs[p])
	return paths,TDs

def pick_download_folder():
	from python_pick import pick
	title = 'Select download folder: '
	db=libraries(download_lib_file)
	if db==False:
		return False,False
	options = [x for x in db.keys()]
	selected = pick(options, title,min_selection_count=1)
	path=selected[0]
	return path

def Interface():
	clear_Screen()
	About()
	response=False
	print('\n********************************************************')
	print('DOWNLOAD SYSTEM')
	print('********************************************************')
	while True:
		print('Input "1" to select folder and file via file-picker')
		if os.path.exists(remote_lib_file):
			print('Input "2" to select from libraries')
		print('')
		print('Input "0" to go back to the MAIN PROGRAM')
		print('')
		print('--- Or INPUT GDRIVE Route OR PUBLIC_LINK ---')
		print('')
		ck=input('Input your answer: ')
		if ck=="0":
			break
		elif ck=="1":
			while True:
				folder,TD=Private.folder_walker()
				if folder==False:
					return False
				print(folder)
				response=interface_file(folder,TD)
				if response==False:
					return False
		elif ck=="2" and os.path.exists(remote_lib_file):
			while True:
				paths,TDs=pick_libraries()
				if paths==False:
					return False
				response=interface_file(paths,TDs)
				if response==False:
					return False
		elif ck=="0":
			break
		elif ck.startswith('http'):
			url=ck
			response=interface_menu(url,None,True)
		elif ck.endswith('/') or ck.endswith('\\'):
			response=interface_file(ck,"pick")
		elif (ck[:-1]).endswith('.xc') or (ck[:-1]).endswith('.ns'):
			TD=Private.TD_picker(ck)
			response=interface_menu(ck,TD,True)
		if 	response==False:
			break

def interface_file(path,TD):
	if TD=="pick":
		TD=Private.TD_picker(path)
	folder=path;TeamDrive=TD
	response=False
	files=list()
	while True:
		filter=interface_filter(path)
		files=Private.search_folder(folder,TD=TeamDrive,pickmode="multi",filter=filter,Print=False)
		if files==False:
			print("Query returned no files")
			input('\nPress any key to continue...')
			clear_Screen()
			About()
			return True
		else:
			response=interface_menu(files,TeamDrive)
			if str(response)=="False":
				return response
			elif str(response)=="CHANGE":
				return True

def interface_filter(path=None):
	from python_pick import pick
	title = 'Add a search filter?: '
	options = ['Yes','No']
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	if response=='No':
		return None
	else:
		clear_Screen()
		About()
		if path != None:
			print("Filepath {}\n".format(str(path)))
		ck=input('INPUT SEARCH FILTER: ')
		return ck

def interface_xci_mode():
	from python_pick import pick
	title = 'Xci files detected. Input download mode'
	options = ['Untrimmed','Trimmed','Supertrimmed']
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	return response

def interface_compressedf_mode():
	from python_pick import pick
	title = 'Compressed files detected. Input download mode'
	options = ['Compressed','Uncompressed']
	selected = pick(options, title, min_selection_count=1)
	response=selected[0]
	return response

def ask_download_folder():
	clear_Screen()
	About()
	if not os.path.exists(download_lib_file):
		while True:
			ofolder=input('Input Download Folder: ')
			if os.path.exists(ofolder):
				return ofolder
			if not os.path.exists(ofolder):
				try:
					os.makedirs(ofolder)
					return ofolder
				except:
					print("\nCan't create folder. Please Try again\n")
	else:
		while True:
			print('Input "1" to Download folder from libraries')
			print('')
			print('--- Or Input Download Folder Route ---')
			print('')
			ck=input('Input your answer: ')
			if ck=="1":
				ofolder=pick_download_folder()
			else:
				ofolder=ck
			if os.path.exists(ofolder):
				return ofolder
			if not os.path.exists(ofolder):
				try:
					os.makedirs(ofolder)
					return ofolder
				except:
					print("\nCan't create folder. Please Try again\n")

def interface_menu(path,TD,hide_f_op=False):
	xcipr=False;nxzpr=False;xcimode="Untrimmed";zmode="Compressed"
	if isinstance(path, list):
		if not isinstance(path[0], list):
			for file in path:
				if file.endswith('.xci'):
					xcipr=True
				elif file.endswith('.xcz') or file.endswith('.nsz'):
					nxzpr=True
				if xcipr==True and nxzpr==True:
					break
			if xcipr==True:
				xcimode=interface_xci_mode()
			if nxzpr==True:
				zmode=interface_compressedf_mode()
			ofolder=ask_download_folder()
			clear_Screen()
			About()
			counter=len(path)
			for file in path:
				route_download(file,TD,ofolder,xcimode=xcimode,zmode=zmode)
				counter-=1
				if counter>0:
					print("Still {} files to download".format(str(counter)))
			input('\nPress any key to continue...')
			return False
		else:
			counter=0;files=list()
			for i in path:
				counter+=len(i[0])
				files+=i[0]
			for file in files:
				if file.endswith('.xci'):
					xcipr=True
				elif file.endswith('.xcz') or file.endswith('.nsz'):
					nxzpr=True
				if xcipr==True and nxzpr==True:
					break
			if xcipr==True:
				xcimode=interface_xci_mode()
			if nxzpr==True:
				zmode=interface_compressedf_mode()
			ofolder=ask_download_folder()
			clear_Screen()
			About()
			for k in path:
				TD=k[1];files=k[0]
				for file in files:
					route_download(file,TD,ofolder,xcimode=xcimode,zmode=zmode)
					counter-=1
					if counter>0:
						print("Still {} files to download".format(str(counter)))
			input('\nPress any key to continue...')
			return False
	elif path.startswith('http'):
		file=Public.return_remote(path)
		if file.name.endswith('.xci'):
			xcipr=True
		elif file.name.endswith('.xcz') or file.name.endswith('.nsz'):
			nxzpr=True
		elif file.name==None:
			print("File overpassed quota or is unreadable")
			input('\nPress any key to continue...')
			clear_Screen()
			About()
		if xcipr==True:
			xcimode=interface_xci_mode()
		if nxzpr==True:
			zmode=interface_compressedf_mode()
		ofolder=ask_download_folder()
		route_download_public(path,ofolder,file.name,xcimode=xcimode,zmode=zmode,file=file)
		input('\nPress any key to continue...')
		return False
	elif path !=None:
		if path.endswith('.xci'):
			xcipr=True
		elif path.endswith('.xcz') or path.endswith('.nsz'):
			nxzpr=True
		if xcipr==True:
			xcimode=interface_xci_mode()
		if nxzpr==True:
			zmode=interface_compressedf_mode()
		ofolder=ask_download_folder()
		route_download(path,TD,ofolder,xcimode=xcimode,zmode=zmode)
		input('\nPress any key to continue...')
		return False
	else:
		return False

def route_download(path,TD,ofolder,xcimode="Untrimmed",zmode="Compressed"):
	if (path.endswith('.xcz') or path.endswith('.nsz')) and zmode=="Uncompressed":
		decompress(path,ofolder,TD=TD)
	if path.endswith('.xci') and xcimode=="Trimmed":
		Private.download(path,ofolder,TD=TD,trimm=True)
	elif path.endswith('.xci') and xcimode=="Supertrimmed":
		supertrimm(path,ofolder,TD=TD)
	else:
		Private.download(path,ofolder,TD=TD,trimm=False)

def route_download_public(url,ofolder,fname,xcimode="Untrimmed",zmode="Compressed",file=None):
	if (fname.endswith('.xcz') or fname.endswith('.nsz')) and zmode=="Uncompressed":
		decompress(url,ofolder,file=file)
	if fname.endswith('.xci') and xcimode=="Trimmed":
		Public.download(url,ofolder,trimm=True,file=file)
	elif fname.endswith('.xci') and xcimode=="Supertrimmed":
		supertrimm(url,ofolder,file=file)
	else:
		Public.download(url,ofolder,trimm=False,file=file)
