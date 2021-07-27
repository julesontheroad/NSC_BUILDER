import aes128
import Print
import os
import shutil
import json
import listmanager
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs import factory
from Fs import Nca
import sq_tools
import io

import Keys
from binascii import hexlify as hx, unhexlify as uhx
import math
import subprocess
import sys
from mtp.wpd import is_switch_connected
from python_pick import pick
from python_pick import Picker
import csv
from tqdm import tqdm

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

def pick_transfer_folder():
	if not os.path.exists(mtp_internal_lib):
		return "SD"
	title = 'Select transfer folder: '
	db=libraries(mtp_internal_lib)
	if db==False:
		return "SD"
	options = [x for x in db.keys()]
	selected = pick(options, title,min_selection_count=1)
	path=(db[selected[0]])['path']
	return path

def file_verification(filename,hash=False):
	if not os.path.exists(cachefolder):
		os.makedirs(cachefolder)
	tempfolder=os.path.join(cachefolder, 'temp')
	if not os.path.exists(tempfolder):
		os.makedirs(tempfolder)
	verdict=False;isrestored=False;cnmt_is_patched=False
	if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz') or filename.endswith('.xcz') or filename.endswith('.xci'):
		try:
			if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz'):
				f = squirrelNSP(filename, 'rb')
			elif filename.endswith('.xci') or filename.endswith('.xcz'):
				f = factory(filename)
				f.open(filename, 'rb')
			check,feed=f.verify()
			if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.nsz'):
				verdict,headerlist,feed=f.verify_sig(feed,tempfolder,cnmt='nocheck')
			else:
				verdict,headerlist,feed=f.verify_sig(feed,tempfolder)
			output_type='nsp';multi=False;cnmtcount=0
			if verdict == True:
				isrestored=True
				for i in range(len(headerlist)):
					entry=headerlist[i]
					if str(entry[0]).endswith('.cnmt.nca'):
						cnmtcount+=1
						if cnmt_is_patched==False:
							status=entry[2]
							if status=='patched':
								cnmt_is_patched=True
					if entry[1]!=False:
						if int(entry[-1])==1:
							output_type='xci'
						isrestored=False
					else:
						pass
				if	isrestored == False:
					if cnmt_is_patched !=True:
						print('\nFILE VERIFICATION CORRECT.\n -> FILE WAS MODIFIED BUT ORIGIN IS CONFIRMED AS LEGIT\n')
					else:
						print('\nFILE VERIFICATION CORRECT. \n -> FILE WAS MODIFIED AND CNMT PATCHED\n')
				else:
					print("\nFILE VERIFICATION CORRECT. FILE IS SAFE.\n")
			if verdict == False:
				print("\nFILE VERIFICATION INCORRECT. \n -> UNCONFIRMED ORIGIN FILE HAS BEEN TAMPERED WITH\n")
			if 	hash==True and verdict==True:
				if filename.endswith('.nsp') or filename.endswith('.nsx') or filename.endswith('.xci'):
					verdict,feed=f.verify_hash_nca(65536,headerlist,verdict,feed)
				elif filename.endswith('.nsz'):
					verdict,feed=f.nsz_hasher(65536,headerlist,verdict,feed)
				elif filename.endswith('.xcz'):
					verdict,feed=f.xcz_hasher(65536,headerlist,verdict,feed)
			f.flush()
			f.close()
		except BaseException as e:
			Print.error('Exception: ' + str(e))
	return verdict,isrestored,cnmt_is_patched

def generate_and_transfer_st1(filepath,outfolder,keypatch='false'):
	tname=str(os.path.basename(filepath))[:-3]+'xci'
	tmpfile=os.path.join(outfolder,tname)
	if filepath.endswith('xci') or filepath.endswith('xcz'):
		f = factory(filepath)
		f.open(filepath, 'rb')
	elif filepath.endswith('nsp') or filepath.endswith('nsz'):
		f = squirrelNSP(filepath, 'rb')
	f.c_xci_direct(65536,tmpfile,outfolder,metapatch='true',keypatch=keypatch)
	f.flush()
	f.close()

def generate_xci_and_transfer(filepath=None,outfolder=None,destiny="SD",kgpatch=False,verification=False):
	check_connection()
	if destiny=="SD":
		destiny="1: External SD Card\\"
	from mtpinstaller import get_storage_info,get_DB_dict
	tgkg=0;kgwarning=False
	if filepath=="":
		filepath=None
	if filepath==None:
		print("File input = null")
		return False
	if outfolder=="":
		outfolder=None
	if outfolder==None:
		outfolder=cachefolder
		if not os.path.exists(cachefolder):
			os.makedirs(cachefolder)
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	for f in os.listdir(outfolder):
		fp = os.path.join(outfolder, f)
		try:
			shutil.rmtree(fp)
		except OSError:
			os.remove(fp)
	if verification==True or str(verification).upper()=="HASH":
		if str(verification).upper()=="HASH":
			verdict,isrestored,cnmt_is_patched=file_verification(filepath,hash=True)
		else:
			verdict,isrestored,cnmt_is_patched=file_verification(filepath)
		if verdict==False:
			print("File didn't pass verification. Skipping...")
			return False
	dopatch=False
	print("- Retrieving Space on device")
	SD_ds,SD_fs,NAND_ds,NAND_fs,FW,device=get_storage_info()
	print("- Calculating Size")
	head_xci_size,keygeneration,sz=get_header_size(filepath)
	installedsize=head_xci_size+sz
	print(f"  * SD free space: {SD_fs} ({sq_tools.getSize(SD_fs)})")
	print(f"  * File installed size: {installedsize} ({sq_tools.getSize(installedsize)})")
	if installedsize>SD_fs:
		sys.exit("   NOT ENOUGH SPACE SD STORAGE")
	if kgpatch==True:
		if FW!='unknown':
			try:
				FW_RSV,RRSV=sq_tools.transform_fw_string(FW)
				FW_kg=sq_tools.kg_by_RSV(FW_RSV)
			except BaseException as e:
				Print.error('Exception: ' + str(e))
				FW='unknown'
				FW_kg='unknown'
				pass
		if FW!='unknown' and FW_kg!='unknown':
			if int(keygeneration)>int(FW_kg):
				kgwarning=True
				tgkg=int(FW_kg)
			else:
				tgkg=keygeneration
		else:
			tgkg=keygeneration
		print(f"- Console Firmware: {FW} ({FW_RSV}) - keygen {FW_kg})")
		print(f"- File keygeneration: {keygeneration}")
	else:
		tgkg=keygeneration
	if kgwarning==True:
		print("File requires a higher firmware. It'll will be prepatch")
		dopatch=True
	keypatch=int(tgkg)
	tname=str(os.path.basename(filepath))[:-3]+'xci'
	tmpfile=os.path.join(outfolder,tname)
	if filepath.endswith('xcz') or filepath.endswith('nsz'):
		if isExe==False:
			process0=subprocess.Popen([sys.executable,squirrel,"-lib_call","mtp.mtpxci","generate_and_transfer_st1","-xarg",filepath,outfolder,str(keypatch)])
		else:
			process0=subprocess.Popen([squirrel,"-lib_call","mtp.mtpxci","generate_and_transfer_st1","-xarg",filepath,outfolder,str(keypatch)])
		while process0.poll()==None:
			if process0.poll()!=None:
				process0.terminate();
		if isExe==False:
			process1=subprocess.Popen([sys.executable,squirrel,"-renf",tmpfile,"-t","xci","-renm","force","-nover","xci_no_v0","-addl","false","-roma","TRUE"])
		else:
			process1=subprocess.Popen([sys.executable,squirrel,"-renf",tmpfile,"-t","xci","-renm","force","-nover","xci_no_v0","-addl","false","-roma","TRUE"])
		while process1.poll()==None:
			if process1.poll()!=None:
				process1.terminate();
		files2transfer=listmanager.folder_to_list(outfolder,['xci'])
		for f in files2transfer:
			bname=str(os.path.basename(f))
			destinypath=os.path.join(destiny,bname)
			process=subprocess.Popen([nscb_mtp,"Transfer","-ori",f,"-dst",destinypath])
			while process.poll()==None:
				if process.poll()!=None:
					process.terminate();
		try:
			for f in os.listdir(outfolder):
				fp = os.path.join(outfolder, f)
				try:
					shutil.rmtree(fp)
				except OSError:
					os.remove(fp)
		except:pass
	elif filepath.endswith('xci') or filepath.endswith('nsp'):
		from mtpxci_gen import transfer_xci_csv
		transfer_xci_csv(filepath,destiny,cachefolder=outfolder,keypatch=keypatch)

def generate_multixci_and_transfer(tfile=None,outfolder=None,destiny="SD",kgpatch=False,verification=False):
	check_connection()
	if destiny==False or destiny=="pick" or destiny=="":
		destiny=pick_transfer_folder()
	if destiny=="SD":
		destiny="1: External SD Card\\"
	from mtpinstaller import get_storage_info,get_DB_dict
	tgkg=0;kgwarning=False
	if tfile=="":
		tfile=None
	if tfile==None:
		print("File input = null")
		return False
	if not os.path.exists(tfile):
		sys.exit(f"Couldn't find {tfile}")
	if outfolder=="":
		outfolder=None
	if outfolder==None:
		outfolder=cachefolder
		if not os.path.exists(cachefolder):
			os.makedirs(cachefolder)
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	for f in os.listdir(outfolder):
		fp = os.path.join(outfolder, f)
		try:
			shutil.rmtree(fp)
		except OSError:
			os.remove(fp)
	file_list=listmanager.read_lines_to_list(tfile,all=True)
	if verification==True or str(verification).upper()=="HASH":
		verdict=False
		for fp in file_list:
			if str(verification).upper()=="HASH":
				verdict,isrestored,cnmt_is_patched=file_verification(fp,hash=True)
			else:
				verdict,isrestored,cnmt_is_patched=file_verification(fp)
			if verdict==False:
				print(f"{fp} didn't pass verification. Skipping {tfile}")
				return False
	dopatch=False
	print("- Retrieving Space on device")
	SD_ds,SD_fs,NAND_ds,NAND_fs,FW,device=get_storage_info()
	print("- Calculating Size")
	fullxcisize=0;maxkg=0
	for fp in file_list:
		head_xci_size,keygeneration,sz=get_header_size(fp)
		installedsize=head_xci_size+sz
		fullxcisize+=installedsize
		if int(maxkg)<int(keygeneration):
			maxkg=keygeneration
	print(f"  * SD free space: {SD_fs} ({sq_tools.getSize(SD_fs)})")
	print(f"  * File installed size: {installedsize} ({sq_tools.getSize(installedsize)})")
	if installedsize>SD_fs:
		sys.exit("   NOT ENOUGH SPACE SD STORAGE")
	if kgpatch==True:
		if FW!='unknown':
			try:
				FW_RSV,RRSV=sq_tools.transform_fw_string(FW)
				FW_kg=sq_tools.kg_by_RSV(FW_RSV)
			except BaseException as e:
				Print.error('Exception: ' + str(e))
				FW='unknown'
				FW_kg='unknown'
				pass
		if FW!='unknown' and FW_kg!='unknown':
			if int(keygeneration)>int(FW_kg):
				kgwarning=True
				tgkg=int(FW_kg)
			else:
				tgkg=keygeneration
		else:
			tgkg=keygeneration
		print(f"- Console Firmware: {FW} ({FW_RSV}) - keygen {FW_kg})")
		print(f"- File keygeneration: {keygeneration}")
	else:
		tgkg=keygeneration
	if kgwarning==True:
		print("File requires a higher firmware. It'll will be prepatch")
		dopatch=True
	keypatch=int(tgkg)
	input_files=listmanager.read_lines_to_list(tfile,all=True)
	has_compressed=False
	for fi in input_files:
		if fi.endswith('xcz') or fi.endswith('nsz'):
			has_compressed=True
			break
	if has_compressed==True:
		if isExe==False:
			process0=subprocess.Popen([sys.executable,squirrel,"-b","65536","-pv","true","-kp",str(keypatch),"--RSVcap","268435656","-fat","exfat","-fx","files","-ND","true","-t","xci","-o",outfolder,"-tfile",tfile,"-roma","TRUE","-dmul","calculate"])
		else:
			process0=subprocess.Popen([squirrel,"-b","65536","-pv","true","-kp",str(keypatch),"--RSVcap","268435656","-fat","exfat","-fx","files","-ND","true","-t","xci","-o",outfolder,"-tfile",tfile,"-roma","TRUE","-dmul","calculate"])
		while process0.poll()==None:
			if process0.poll()!=None:
				process0.terminate();
		files2transfer=listmanager.folder_to_list(outfolder,['xci'])
		for f in files2transfer:
			bname=str(os.path.basename(f))
			destinypath=os.path.join(destiny,bname)
			process=subprocess.Popen([nscb_mtp,"Transfer","-ori",f,"-dst",destinypath])
			while process.poll()==None:
				if process.poll()!=None:
					process.terminate();
		try:
			for f in os.listdir(outfolder):
				fp = os.path.join(outfolder, f)
				try:
					shutil.rmtree(fp)
				except OSError:
					os.remove(fp)
		except:pass
	elif has_compressed==False:
		from mtpxci_gen import transfer_mxci_csv
		transfer_mxci_csv(tfile=tfile,destiny=destiny,cachefolder=outfolder,keypatch=keypatch,input_files=input_files)

def loop_xci_transfer(tfile,destiny=False,verification=True,outfolder=None,patch_keygen=False,mode="single"):
	check_connection()
	if destiny==False or destiny=="pick" or destiny=="":
		destiny=pick_transfer_folder()
	if not os.path.exists(tfile):
		sys.exit(f"Couldn't find {tfile}")
	file_list=listmanager.read_lines_to_list(tfile,all=True)
	for item in file_list:
		if mode=="single":
			generate_xci_and_transfer(filepath=item,destiny=destiny,verification=verification,outfolder=outfolder,kgpatch=patch_keygen)
			print("")
			listmanager.striplines(tfile,counter=True)
		elif mode=="multi":
			continue

def get_header_size(filepath):
	properheadsize=0;sz=0
	if filepath.endswith('xci') or filepath.endswith('xcz'):
		files_list=sq_tools.ret_xci_offsets(filepath)
		files=list();filesizes=list()
		fplist=list()
		for k in range(len(files_list)):
			entry=files_list[k]
			fplist.append(entry[0])
		for i in range(len(files_list)):
			entry=files_list[i]
			cnmtfile=entry[0]
			if cnmtfile.endswith('.cnmt.nca'):
				f=squirrelXCI(filepath)
				titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']!='Meta':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist or test2 in fplist:
							# print(str(row['NcaId'])+'.nca')
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
							sz+=int(row['Size'])
					elif row['NCAtype']=='Meta':
						# print(str(row['NcaId'])+'.cnmt.nca')
						files.append(str(row['NcaId'])+'.cnmt.nca')
						filesizes.append(int(row['Size']))
						sz+=int(row['Size'])
		sec_hashlist=list()
		try:
			for file in files:
				sha,size,gamecard=f.file_hash(file)
				# print(sha)
				if sha != False:
					sec_hashlist.append(sha)
		except BaseException as e:
			Print.error('Exception: ' + str(e))
		f.flush()
		f.close()
		xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=sq_tools.get_xciheader(files,filesizes,sec_hashlist)
		outheader=xci_header
		outheader+=game_info
		outheader+=sig_padding
		outheader+=xci_certificate
		outheader+=root_header
		outheader+=upd_header
		outheader+=norm_header
		outheader+=sec_header
	elif filepath.endswith('nsp') or filepath.endswith('nsz'):
		files_list=sq_tools.ret_nsp_offsets(filepath)
		files=list();filesizes=list()
		fplist=list()
		for k in range(len(files_list)):
			entry=files_list[k]
			fplist.append(entry[0])
		for i in range(len(files_list)):
			entry=files_list[i]
			cnmtfile=entry[0]
			if cnmtfile.endswith('.cnmt.nca'):
				f=squirrelNSP(filepath)
				titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
				f.flush()
				f.close()
				for j in range(len(ncadata)):
					row=ncadata[j]
					# print(row)
					if row['NCAtype']!='Meta':
						test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
						if test1 in fplist or test2 in fplist:
							# print(str(row['NcaId'])+'.nca')
							files.append(str(row['NcaId'])+'.nca')
							filesizes.append(int(row['Size']))
							sz+=int(row['Size'])
					elif row['NCAtype']=='Meta':
						# print(str(row['NcaId'])+'.cnmt.nca')
						files.append(str(row['NcaId'])+'.cnmt.nca')
						filesizes.append(int(row['Size']))
						sz+=int(row['Size'])
		f.flush()
		f.close()
		outheader = sq_tools.gen_nsp_header(files,filesizes)
	properheadsize=len(outheader)
	return properheadsize,keygeneration,sz

def install_xci_csv(filepath,destiny="SD",cachefolder=None,override=False,keypatch=False):
	check_connection()
	if cachefolder==None:
		cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
	files_list=sq_tools.ret_xci_offsets(filepath)
	print(f"Installing {filepath} by content")
	counter=0
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
			counter+=1
	print(f"- Detected {counter} content ids")
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
			target_cnmt=cnmtfile
			nspname=gen_xci_parts_spec1(filepath,target_cnmt=target_cnmt,cachefolder=cachefolder,keypatch=keypatch)
			if filepath.endswith('xcz'):
				nspname=nspname[:-1]+'z'
			files_csv=os.path.join(cachefolder, 'files.csv')
			process=subprocess.Popen([nscb_mtp,"InstallfromCSV","-cs",files_csv,"-nm",nspname,"-dst",destiny])
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

def gen_xci_parts_spec0(filepath,target_cnmt=None,cachefolder=None,keypatch=False,export_type='csv'):
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
	program_name=None
	files_list=sq_tools.ret_xci_offsets(filepath)
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
			f=squirrelXCI(filepath)
			titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
			f.flush()
			f.close()
			for j in range(len(ncadata)):
				row=ncadata[j]
				# print(row)
				if row['NCAtype']!='Meta' and row['NCAtype']!='Program':
					test1=str(row['NcaId'])+'.nca';test2=str(row['NcaId'])+'.ncz'
					if test1 in fplist or test2 in fplist:
						# print(str(row['NcaId'])+'.nca')
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
					if test1 in fplist or test2 in fplist:
						# print(str(row['NcaId'])+'.nca')
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
	f.flush()
	f.close()
	outheader = sq_tools.gen_nsp_header(files,filesizes)
	properheadsize=len(outheader)
	# print(properheadsize)
	# print(bucketsize)
	i=0;sum=properheadsize;
	for file in files:
		# print(file)
		# print(filesizes[i])
		if i<(len(files)-1):
			sum+=filesizes[i]
		i+=1
	# print(sum)
	# print(sum/bucketsize)
	multiplier=math.ceil(sum/bucketsize)
	# print(multiplier)
	remainder = bucketsize*multiplier - sum
	# print(bucketsize*multiplier)
	xci=squirrelXCI(filepath)
	outfile=os.path.join(cachefolder, "0")
	written=0;
	outf = open(outfile, 'w+b')
	outf.write(outheader)
	written+=len(outheader)
	movoffset=0
	for fi in files:
		for nspF in xci.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if nca._path==fi:
						nca=Nca(nca)
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:
							masterKeyRev=crypto1
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))
						gc_flag='00'*0x01
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if nca.header.getRightsId() != 0:
							nca.rewind()
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:
								masterKeyRev=crypto1
							from mtp_tools import get_nca_ticket
							check,titleKey=get_nca_ticket(filepath,fi)
							if check==False:
								sys.exit("Can't verify titleckey")
							titleKeyDec = Keys.decryptTitleKey(titleKey, Keys.getMasterKeyIndex(int(masterKeyRev)))
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
							if str(keypatch) != "False":
								t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=squirrelXCI.get_new_cryptoblock(squirrelXCI,nca, keypatch,encKeyBlock,t)
								t.close()
						if nca.header.getRightsId() == 0:
							nca.rewind()
							encKeyBlock = nca.header.getKeyBlock()
							if str(keypatch) != "False":
								t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=squirrelXCI.get_new_cryptoblock(squirrelXCI,nca,keypatch,encKeyBlock,t)
								t.close()
						nca.rewind()
						i=0
						newheader=xci.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)
						outf.write(newheader)
						written+=len(newheader)
						nca.seek(0xC00)
						movoffset+=0xC00
						if (str(nca.header.contentType) != 'Content.PROGRAM'):
							data=nca.read()
							nca.close()
							outf.write(data)
							written+=len(data)
						break
					else:pass
	xci.flush()
	xci.close()
	outf.close()
	if export_type=='json':
		files_json=os.path.join(cachefolder, "files.json")
		d={}
		d['0']={"step": 0,
		  "filepath":outfile ,
		  "size":( written) ,
		  "targetsize":( written) ,
		  "off1":0,
		  "off2":( written)
		}
		for j in files_list:
			if j[0]==files[-1]:
				off1=j[1]+0xC00
				off2=j[2]
				targetsize=j[3]-0xC00
		d['1']={"step": 1,
		  "filepath":filepath ,
		  "size":( os.path.getsize(filepath)) ,
		  "targetsize":targetsize,
		  "off1":off1,
		  "off2":off2
		}
		app_json = json.dumps(d, indent=1)
		with open(files_json, 'w') as json_file:
		  json_file.write(app_json)
		# print(os.path.getsize(filepath))
	else:
		for j in files_list:
			if j[0]==files[-1]:
				off1=j[1]+0xC00
				off2=j[2]
				targetsize=j[3]-0xC00
		tfile=os.path.join(cachefolder, "files.csv")
		i=0;
		while True:
			with open(tfile,'w') as csvfile:
				if i==0:
					csvfile.write("{}|{}|{}|{}|{}|{}\n".format("step","filepath","size","targetsize","off1","off2"))
					i+=1
				if i==1:
					csvfile.write("{}|{}|{}|{}|{}|{}\n".format(0,outfile,os.path.getsize(outfile),os.path.getsize(outfile),0,os.path.getsize(outfile)))
					i+=1
				if i==2:
					csvfile.write("{}|{}|{}|{}|{}|{}".format(1,filepath,( os.path.getsize(filepath)),targetsize,off1,off2))
					i+=1
					break
	nspname="test.nsp"
	try:
		g=os.path.basename(filepath)
		g0=[pos for pos, char in enumerate(g) if char == '[']
		g0=(g[0:g0[0]]).strip()
		nspname=f"{g0} [{titleid}] [v{titleversion}] [{ctype}].nsp"
	except:pass
	return nspname

def gen_xci_parts_spec1(filepath,target_cnmt=None,cachefolder=None,keypatch=False):
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
	files_list=sq_tools.ret_xci_offsets(filepath)
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
			f=squirrelXCI(filepath)
			titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(cnmtfile)
			f.flush()
			f.close()
			for j in range(len(ncadata)):
				row=ncadata[j]
				# print(row)
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
	f.flush()
	f.close()
	outheader = sq_tools.gen_nsp_header(files,filesizes)
	properheadsize=len(outheader)
	# print(properheadsize)
	# print(bucketsize)
	i=0;sum=properheadsize;
	xci=squirrelXCI(filepath)
	outfile=os.path.join(cachefolder, "0")
	outf = open(outfile, 'w+b')
	outf.write(outheader)
	written=0
	for fi in files:
		for nspF in xci.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:
					if nca._path==fi:
						nca=Nca(nca)
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if crypto2>crypto1:
							masterKeyRev=crypto2
						if crypto2<=crypto1:
							masterKeyRev=crypto1
						crypto = aes128.AESECB(Keys.keyAreaKey(Keys.getMasterKeyIndex(masterKeyRev), nca.header.keyIndex))
						hcrypto = aes128.AESXTS(uhx(Keys.get('header_key')))
						gc_flag='00'*0x01
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()
						if nca.header.getRightsId() != 0:
							nca.rewind()
							if crypto2>crypto1:
								masterKeyRev=crypto2
							if crypto2<=crypto1:
								masterKeyRev=crypto1
							from mtp_tools import get_nca_ticket
							check,titleKey=get_nca_ticket(filepath,fi)
							if check==False:
								sys.exit("Can't verify titleckey")
							titleKeyDec = Keys.decryptTitleKey(titleKey, Keys.getMasterKeyIndex(int(masterKeyRev)))
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
							if str(keypatch) != "False":
								t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=squirrelXCI.get_new_cryptoblock(squirrelXCI,nca,keypatch,encKeyBlock,t)
								t.close()
						if nca.header.getRightsId() == 0:
							nca.rewind()
							encKeyBlock = nca.header.getKeyBlock()
							if str(keypatch) != "False":
								t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=squirrelXCI.get_new_cryptoblock(squirrelXCI,nca,keypatch,encKeyBlock,t)
								t.close()
						nca.rewind()
						i=0
						newheader=xci.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)
						outf.write(newheader)
						written+=len(newheader)
						nca.seek(0xC00)
						break
					else:pass
	xci.flush()
	xci.close()
	outf.flush()
	outf.close()
	tfile=os.path.join(cachefolder, "files.csv")
	with open(tfile,'w') as csvfile:
		csvfile.write("{}|{}|{}|{}|{}|{}\n".format("step","filepath","size","targetsize","off1","off2"))
		csvfile.write("{}|{}|{}|{}|{}|{}\n".format(0,outfile,properheadsize+written,properheadsize,0,properheadsize))
		k=0;l=0
		for fi in files:
			for j in files_list:
				if j[0]==fi:
					csvfile.write("{}|{}|{}|{}|{}|{}\n".format(k+1,outfile,properheadsize+written,0xC00,(properheadsize+l*0xC00),(properheadsize+(l*0xC00)+0xC00)))
					off1=j[1]+0xC00
					off2=j[2]
					targetsize=j[3]-0xC00
					csvfile.write("{}|{}|{}|{}|{}|{}\n".format(k+2,filepath,(os.path.getsize(filepath)),targetsize,off1,off2))
					break
			k+=2;l+=1
	nspname="test.nsp"
	try:
		g=os.path.basename(filepath)
		g0=[pos for pos, char in enumerate(g) if char == '[']
		g0=(g[0:g0[0]]).strip()
		nspname=f"{g0} [{titleid}] [v{titleversion}] [{ctype}].nsp"
	except:pass
	return nspname
