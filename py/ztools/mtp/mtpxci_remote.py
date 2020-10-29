import aes128
import Print
import os
import shutil
import json
import listmanager
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs.Nca import NcaHeader
from Fs import Nca
from Fs.File import MemoryFile
import sq_tools
from Fs import Type as FsType

import Keys
from binascii import hexlify as hx, unhexlify as uhx
import subprocess
import sys
from mtp.wpd import is_switch_connected
from python_pick import pick
from python_pick import Picker
import csv
from tqdm import tqdm
from Drive import Private as DrivePrivate
from Drive import DriveTools

def check_connection():
	if not is_switch_connected():
		sys.exit("Switch device isn't connected.\nCheck if mtp responder is running!!!")

bucketsize = 81920

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

testroute1=os.path.join(squirrel_dir, "squirrel.py")
testroute2=os.path.join(squirrel_dir, "squirrel.exe")
urlconfig=os.path.join(zconfig_dir,'NUT_DB_URL.txt')
isExe=False
if os.path.exists(testroute1):
	squirrel=testroute1
	isExe=False
elif os.path.exists(testroute2):
	squirrel=testroute2
	isExe=True
bin_folder=os.path.join(ztools_dir, 'bin')
nscb_mtp=os.path.join(bin_folder, 'nscb_mtp.exe')
cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
if not os.path.exists(cachefolder):
	os.makedirs(cachefolder)
games_installed_cache=os.path.join(cachefolder, 'games_installed.txt')
valid_saves_cache=os.path.join(cachefolder, 'valid_saves.txt')
mtp_source_lib=os.path.join(zconfig_dir,'mtp_source_libraries.txt')
mtp_internal_lib=os.path.join(zconfig_dir,'mtp_SD_libraries.txt')
storage_info=os.path.join(cachefolder, 'storage.csv')
download_lib_file = os.path.join(zconfig_dir, 'mtp_download_libraries.txt')
remote_lib_file = os.path.join(zconfig_dir, 'remote_libraries.txt')
cache_lib_file= os.path.join(zconfig_dir, 'remote_cache_location.txt')
_1fichier_token=os.path.join((os.path.join(zconfig_dir, 'credentials')),'_1fichier_token.tk')
remote_lib_cache=os.path.join(zconfig_dir, 'remote_lib_cache')

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
		return db
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		return False

def get_library_from_path(tfile=None,filename=None):
	if tfile==None:
		db=libraries(remote_lib_file)
	else:
		db=libraries(tfile)
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

def install_xci_csv(filepath=None,remote=None,destiny="SD",cachefolder=None,override=False,keypatch=False):
	if filepath=="":
		filepath=None
	if remote=="":
		remote=None
	if remote==None:
		test=filepath.split('|');TD=None
		if len(test)<2:
			filepath=test[0]
			lib,TD,libpath=get_library_from_path(remote_lib_file,filepath)
		else:
			filepath=test[0]
			TD=test[1]
			if str(TD).upper()=="NONE":
				TD=None
		ID,name,type,size,md5,remote=DrivePrivate.get_Data(filepath,TD=TD,Print=False)
	check_connection()
	if cachefolder==None:
		cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
	files_list=DriveTools.get_files_from_head(remote,remote.name)
	remote.rewind()
	print(f"Installing {remote.name} by content")
	print('- Parsing headers...')
	files=list();filesizes=list()
	fplist=list()
	counter=0
	for k in range(len(files_list)):
		entry=files_list[k]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
			counter+=1
	print(f"- Detected {counter} content ids")
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0];
		if cnmtfile.endswith('.cnmt.nca'):
			target_cnmt=cnmtfile
			nspname=gen_xci_parts_spec0(remote=remote,target_cnmt=target_cnmt,cachefolder=cachefolder,keypatch=keypatch)
			if (remote.name).endswith('xcz'):
				nspname=nspname[:-1]+'z'
			files_csv=os.path.join(cachefolder, 'remote_files.csv')
			process=subprocess.Popen([nscb_mtp,"GDInstallfromCSV","-cs",files_csv,"-nm",nspname,"-dst",destiny])
			while process.poll()==None:
				if process.poll()!=None:
					process.terminate();
			counter-=1
			print('\n- Still '+str(counter)+' subitems to process')
			if counter>0:
				print("")
	if os.path.exists(cachefolder):
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)

def gen_xci_parts_spec0(filepath=None,remote=None,target_cnmt=None,cachefolder=None,keypatch=False,files_list=None):
	if filepath=="":
		filepath=None
	if remote=="":
		remote=None
	if remote==None:
		test=filepath.split('|');TD=None
		if len(test)<2:
			filepath=test[0]
			lib,TD,libpath=get_library_from_path(remote_lib_file,filepath)
		else:
			filepath=test[0]
			TD=test[1]
			if str(TD).upper()=="NONE":
				TD=None
		ID,name,type,size,md5,remote=DrivePrivate.get_Data(filepath,TD=TD,Print=False)
	if keypatch!=False:
		try:
			keypatch=int(keypatch)
		except:	keypatch=False
	if cachefolder==None:
		cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)
	else:
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)
	if files_list==None:
		files_list=DriveTools.get_files_from_head(remote,remote.name)
	files=list();filesizes=list()
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	if target_cnmt==None:
		for i in range(len(files_list)):
			entry=files_list[i]
			cnmtfile=entry[0]
			if cnmtfile.endswith('.cnmt.nca'):
				target_cnmt=cnmtfile
				break
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca') and target_cnmt==cnmtfile:
			metadict,d1,d2=DriveTools.get_cnmt_data(target=cnmtfile,file=remote)
			ncadata=metadict['ncadata']
			content_type=metadict['ctype']
			if content_type!="DLC":
				for j in range(len(ncadata)):
					row=ncadata[j]
					if row['NCAtype']!='Meta' and row['NCAtype']!='Program' and row['NCAtype']!='DeltaFragment':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist:
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
						elif test2 in fplist:
							files.append(str(row['NcaId'])+'.ncz')
							for k in range(len(files_list)):
								entry=files_list[k]
								if entry[0]==test2:
									filesizes.append(int(entry[3]))
									break
				for j in range(len(ncadata)):
					row=ncadata[j]
					if row['NCAtype']=='Meta':
						# print(str(row['NcaId'])+'.cnmt.nca')
						files.append(str(row['NcaId'])+'.cnmt.nca')
						filesizes.append(int(row['Size']))
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']=='Program':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist:
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
						elif test2 in fplist:
							files.append(str(row['NcaId'])+'.ncz')
							for k in range(len(files_list)):
								entry=files_list[k]
								if entry[0]==test2:
									filesizes.append(int(entry[3]))
									break
			else:
				for j in range(len(ncadata)):
					row=ncadata[j]
					if row['NCAtype']!='Meta' and row['NCAtype']!='Data':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist:
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
						elif test2 in fplist:
							files.append(str(row['NcaId'])+'.ncz')
							for k in range(len(files_list)):
								entry=files_list[k]
								if entry[0]==test2:
									filesizes.append(int(entry[3]))
									break
				for j in range(len(ncadata)):
					row=ncadata[j]
					if row['NCAtype']=='Meta':
						# print(str(row['NcaId'])+'.cnmt.nca')
						files.append(str(row['NcaId'])+'.cnmt.nca')
						filesizes.append(int(row['Size']))
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']=='Data':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist:
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
						elif test2 in fplist:
							files.append(str(row['NcaId'])+'.ncz')
							for k in range(len(files_list)):
								entry=files_list[k]
								if entry[0]==test2:
									filesizes.append(int(entry[3]))
									break
			break
	remote.rewind()
	outheader = sq_tools.gen_nsp_header(files,filesizes)
	properheadsize=len(outheader)
	# print(properheadsize)
	# print(bucketsize)
	i=0;sum=properheadsize;
	outfile=os.path.join(cachefolder, "0")
	outf = open(outfile, 'w+b')
	outf.write(outheader)
	written=0
	nca_program=''
	for fi in files:
		if fi.endswith('nca') or fi.endswith('ncz') :
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(fi).lower():
					nca_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					nca_size=files_list[i][3]
					break
			ncaHeader = NcaHeader()
			ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), FsType.Crypto.XTS, uhx(Keys.get('header_key'))))
			crypto1=ncaHeader.getCryptoType()
			crypto2=ncaHeader.getCryptoType2()
			if crypto2>crypto1:
				masterKeyRev=crypto2
			if crypto2<=crypto1:
				masterKeyRev=crypto1
			crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), ncaHeader.keyIndex))
			hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))
			gc_flag='00'*0x01
			crypto1=ncaHeader.getCryptoType()
			crypto2=ncaHeader.getCryptoType2()
			if ncaHeader.getRightsId() != 0:
				ncaHeader.rewind()
				if crypto2>crypto1:
					masterKeyRev=crypto2
				if crypto2<=crypto1:
					masterKeyRev=crypto1
				rightsId=metadict['rightsId']
				titleKeyDec = DriveTools.get_titlekey(remote,rightsId,masterKeyRev,files_list=files_list)
				encKeyBlock = crypto.encrypt(titleKeyDec * 4)
				if str(keypatch) != "False":
					t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
					if keypatch < ncaHeader.getCryptoType2():
						encKeyBlock,crypto1,crypto2=get_new_cryptoblock(ncaHeader,keypatch,encKeyBlock,t)
					t.close()
			if ncaHeader.getRightsId() == 0:
				ncaHeader.rewind()
				encKeyBlock = ncaHeader.getKeyBlock()
				if str(keypatch) != "False":
					t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
					if keypatch < ncaHeader.getCryptoType2():
						encKeyBlock,crypto1,crypto2=get_new_cryptoblock(ncaHeader,keypatch,encKeyBlock,t)
					t.close()
			ncaHeader.rewind()
			i=0
			newheader=get_newheader(MemoryFile(remote.read_at(off1,0xC00)),encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)
			outf.write(newheader)
			written+=len(newheader)
			if content_type!="DLC":
				if (str(ncaHeader.contentType) != 'Content.PROGRAM'):
					nca = Nca()
					nca.open(MemoryFile(remote.read_at(off1,nca_size)))
					nca.seek(0xC00)
					data=nca.read()
					outf.write(data)
					written+=len(data)
					# print(nca_name)
					# print(len(newheader)+len(data))
				else:
					nca_program=nca_name
					# print(nca_name)
					# print(len(newheader))
			else:
				if (str(ncaHeader.contentType) != 'Content.PUBLIC_DATA'):
					nca = Nca()
					nca.open(MemoryFile(remote.read_at(off1,nca_size)))
					nca.seek(0xC00)
					data=nca.read()
					outf.write(data)
					written+=len(data)
					# print(nca_name)
					# print(len(newheader)+len(data))
				else:
					nca_program=nca_name
					# print(nca_name)
					# print(len(newheader))
		else:pass
	outf.flush()
	outf.close()
	tfile=os.path.join(cachefolder, "remote_files.csv")
	with open(tfile,'w') as csvfile:
		csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format("step","filepath","size","targetsize","off1","off2","token"))
		csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format(0,outfile,os.path.getsize(outfile),os.path.getsize(outfile),0,os.path.getsize(outfile),"False"))
		k=0;
		for j in files_list:
			if j[0]==nca_program:
				# print(j[0])
				off1=j[1]+0xC00
				off2=j[2]
				targetsize=j[3]-0xC00
				URL='https://www.googleapis.com/drive/v3/files/'+remote.ID+'?alt=media'
				token=remote.access_token
				csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format(k+1,URL,remote.size,targetsize,off1,off2,token))
				k+=1
				break
	nspname="test.nsp"
	try:
		g=remote.name
		g0=[pos for pos, char in enumerate(g) if char == '[']
		g0=(g[0:g0[0]]).strip()
		titleid=metadict['titleid']
		titleversion=metadict['version']
		ctype=metadict['ctype']
		nspname=f"{g0} [{titleid}] [v{titleversion}] [{ctype}].nsp"
	except BaseException as e:
		Print.error('Exception: ' + str(e))
		pass
	return nspname

def gen_xci_parts_spec1(filepath=None,remote=None,target_cnmt=None,cachefolder=None,keypatch=False,files_list=None):
	if filepath=="":
		filepath=None
	if remote=="":
		remote=None
	if remote==None:
		test=filepath.split('|');TD=None
		if len(test)<2:
			filepath=test[0]
			lib,TD,libpath=get_library_from_path(remote_lib_file,filepath)
		else:
			filepath=test[0]
			TD=test[1]
			if str(TD).upper()=="NONE":
				TD=None
		ID,name,type,size,md5,remote=DrivePrivate.get_Data(filepath,TD=TD,Print=False)
	if keypatch!=False:
		try:
			keypatch=int(keypatch)
		except:	keypatch=False
	if cachefolder==None:
		cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)
	else:
		for f in os.listdir(cachefolder):
			fp = os.path.join(cachefolder, f)
			try:
				shutil.rmtree(fp)
			except OSError:
				os.remove(fp)
	if files_list==None:
		files_list=DriveTools.get_files_from_head(remote,remote.name)
	files=list();filesizes=list()
	fplist=list()
	for k in range(len(files_list)):
		entry=files_list[k]
		fplist.append(entry[0])
	if target_cnmt==None:
		for i in range(len(files_list)):
			entry=files_list[i]
			cnmtfile=entry[0]
			if cnmtfile.endswith('.cnmt.nca'):
				target_cnmt=cnmtfile
				break
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca') and target_cnmt==cnmtfile:
			metadict,d1,d2=DriveTools.get_cnmt_data(target=cnmtfile,file=remote)
			ncadata=metadict['ncadata']
			for j in range(len(ncadata)):
				row=ncadata[j]
				if row['NCAtype']!='Meta' and row['NCAtype']!='Program':
					test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
					if test1 in fplist:
						files.append(str(row['NcaId'])+'.nca')
						filesizes.append(int(row['Size']))
					elif test2 in fplist:
						files.append(str(row['NcaId'])+'.ncz')
						for k in range(len(files_list)):
							entry=files_list[k]
							if entry[0]==test2:
								filesizes.append(int(entry[3]))
								break
			for j in range(len(ncadata)):
				row=ncadata[j]
				if row['NCAtype']=='Meta':
					# print(str(row['NcaId'])+'.cnmt.nca')
					files.append(str(row['NcaId'])+'.cnmt.nca')
					filesizes.append(int(row['Size']))
			for j in range(len(ncadata)):
				row=ncadata[j]
				# print(row)
				if row['NCAtype']=='Program':
					test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
					if test1 in fplist:
						files.append(str(row['NcaId'])+'.nca')
						filesizes.append(int(row['Size']))
					elif test2 in fplist:
						files.append(str(row['NcaId'])+'.ncz')
						for k in range(len(files_list)):
							entry=files_list[k]
							if entry[0]==test2:
								filesizes.append(int(entry[3]))
								break
			break
	remote.rewind()
	outheader = sq_tools.gen_nsp_header(files,filesizes)
	properheadsize=len(outheader)
	# print(properheadsize)
	# print(bucketsize)
	i=0;sum=properheadsize;
	outfile=os.path.join(cachefolder, "0")
	outf = open(outfile, 'w+b')
	outf.write(outheader)
	written=0
	for fi in files:
		if fi.endswith('nca') or fi.endswith('ncz') :
			for i in range(len(files_list)):
				if str(files_list[i][0]).lower() == str(fi).lower():
					nca_name=files_list[i][0]
					off1=files_list[i][1]
					off2=files_list[i][2]
					nca_size=files_list[i][3]
					break
			data=remote.read_at(off1,nca_size)
			ncaHeader = NcaHeader()
			ncaHeader.open(MemoryFile(remote.read_at(off1,0x400), FsType.Crypto.XTS, uhx(Keys.get('header_key'))))
			crypto1=ncaHeader.getCryptoType()
			crypto2=ncaHeader.getCryptoType2()
			if crypto2>crypto1:
				masterKeyRev=crypto2
			if crypto2<=crypto1:
				masterKeyRev=crypto1
			crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), ncaHeader.keyIndex))
			hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))
			gc_flag='00'*0x01
			crypto1=ncaHeader.getCryptoType()
			crypto2=ncaHeader.getCryptoType2()
			if ncaHeader.getRightsId() != 0:
				ncaHeader.rewind()
				if crypto2>crypto1:
					masterKeyRev=crypto2
				if crypto2<=crypto1:
					masterKeyRev=crypto1
				titleKeyDec = Keys.decryptTitleKey(titleKey, Keys.getMasterKeyIndex(int(masterKeyRev)))
				encKeyBlock = crypto.encrypt(titleKeyDec * 4)
				if str(keypatch) != "False":
					t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
					if keypatch < ncaHeader.getCryptoType2():
						encKeyBlock,crypto1,crypto2=get_new_cryptoblock(ncaHeader,keypatch,encKeyBlock,t)
					t.close()
			if ncaHeader.getRightsId() == 0:
				ncaHeader.rewind()
				encKeyBlock = ncaHeader.getKeyBlock()
				if str(keypatch) != "False":
					t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
					if keypatch < ncaHeader.getCryptoType2():
						encKeyBlock,crypto1,crypto2=get_new_cryptoblock(ncaHeader,keypatch,encKeyBlock,t)
					t.close()
			ncaHeader.rewind()
			i=0
			newheader=get_newheader(MemoryFile(remote.read_at(off1,0xC00)),encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)
			outf.write(newheader)
			written+=len(newheader)
			break
		else:pass
	outf.flush()
	outf.close()
	tfile=os.path.join(cachefolder, "remote_files.csv")
	with open(tfile,'w') as csvfile:
		csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format("step","filepath","size","targetsize","off1","off2","token"))
		csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format(0,outfile,properheadsize+written,properheadsize,0,properheadsize,"False"))
		k=0;l=0
		for fi in files:
			for j in files_list:
				if j[0]==fi:
					csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format(k+1,outfile,properheadsize+written,0xC00,(properheadsize+l*0xC00),(properheadsize+(l*0xC00)+0xC00),"False"))
					off1=j[1]+0xC00
					off2=j[2]
					targetsize=j[3]-0xC00
					URL='https://www.googleapis.com/drive/v3/files/'+remote.ID+'?alt=media'
					token=remote.access_token
					csvfile.write("{}|{}|{}|{}|{}|{}|{}\n".format(k+2,URL,remote.size,targetsize,off1,off2,token))
					break
			k+=2;l+=1
	nspname="test.nsp"
	try:
		g=remote.name
		g0=[pos for pos, char in enumerate(g) if char == '[']
		g0=(g[0:g0[0]]).strip()
		titleid=metadict['titleid']
		titleversion=metadict['version']
		ctype=metadict['ctype']
		nspname=f"{g0} [{titleid}] [v{titleversion}] [{ctype}].nsp"
	except:pass
	return nspname

def get_new_cryptoblock(ncaHeader, newMasterKeyRev,encKeyBlock,t):
	indent = 1
	tabs = '\t' * indent
	indent2 = 2
	tabs2 = '\t' * indent2

	masterKeyRev = ncaHeader.getCryptoType2()

	if type(ncaHeader) == NcaHeader():
		if ncaHeader.getCryptoType2() != newMasterKeyRev:
			t.write(tabs + '-----------------------------------')
			t.write(tabs + 'Changing keygeneration from %d to %s' % ( ncaHeader.getCryptoType2(), str(newMasterKeyRev)))
			t.write(tabs + '-----------------------------------')
			if sum(encKeyBlock) != 0:
				key = Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev),ncaHeader.keyIndex)
				t.write(tabs2 + '+ decrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(masterKeyRev), ncaHeader.keyIndex))
				crypto = aes128.AESECB(key)
				decKeyBlock = crypto.decrypt(encKeyBlock)
				key = Keys.keyAreaKey(Keys.getMasterKeyIndex(newMasterKeyRev),ncaHeader.keyIndex)
				t.write(tabs2 + '+ encrypting with %s (%d, %d)' % (str(hx(key)), Keys.getMasterKeyIndex(newMasterKeyRev), ncaHeader.keyIndex))
				crypto = aes128.AESECB(key)
				reEncKeyBlock = crypto.encrypt(decKeyBlock)
				encKeyBlock = reEncKeyBlock
			if newMasterKeyRev >= 3:
				crypto1=2
				crypto2=newMasterKeyRev
			if newMasterKeyRev == 2:
				crypto1=2
				crypto2=0
			if newMasterKeyRev < 2:
				crypto1=newMasterKeyRev
				crypto2=0
			return encKeyBlock,crypto1,crypto2
	return encKeyBlock,ncaHeader.getCryptoType(),ncaHeader.getCryptoType2()

def get_newheader(ncaHeader,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag):
	ncaHeader.rewind()
	rawhead=ncaHeader.read(0xC00)
	rawhead=hcrypto.decrypt(rawhead)
	header = b''
	header += rawhead[0x00:0x00+0x204]
	#isgamecard 0x204
	GC=bytes.fromhex(gc_flag)
	header += GC
	#contentType 0x205
	header += rawhead[0x205:0x206]
	#crypto 1 0x206
	c1=crypto1.to_bytes(1, byteorder='big')
	header += c1
	#########
	header += rawhead[0x207:0x220]
	#crypto 1 0x220
	c2=crypto2.to_bytes(1, byteorder='big')
	header += c2
	#########
	header += rawhead[0x221:0x230]
	tr='00'*0x10
	tr=bytes.fromhex(tr)
	header += tr
	header += rawhead[0x240:0x240+0xC0]
	header += encKeyBlock
	header += rawhead[0x340:]
	newheader=hcrypto.encrypt(header)
	return newheader
