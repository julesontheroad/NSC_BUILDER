import aes128
import Print
import os
import shutil
import json
import listmanager
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs import Nca
import sq_tools

import Keys
from binascii import hexlify as hx, unhexlify as uhx
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


def install_nsp_csv(filepath,destiny="SD",cachefolder=None,override=False,keypatch=False):
	check_connection()
	if cachefolder==None:
		cachefolder=os.path.join(ztools_dir, '_mtp_cache_')
	files_list=sq_tools.ret_nsp_offsets(filepath)
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
			nspname=gen_nsp_parts_spec1(filepath,target_cnmt=target_cnmt,cachefolder=cachefolder,keypatch=keypatch)
			if filepath.endswith('nsz'):
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

def gen_nsp_parts_spec1(filepath,target_cnmt=None,cachefolder=None,keypatch=False):
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
	files_list=sq_tools.ret_nsp_offsets(filepath)
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
			f=squirrelNSP(filepath)
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
	nsp=squirrelNSP(filepath)
	outfile=os.path.join(cachefolder, "0")
	outf = open(outfile, 'w+b')
	outf.write(outheader)
	written=0
	for fi in files:
		for nca in nsp:
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
							encKeyBlock,crypto1,crypto2=squirrelNSP.get_new_cryptoblock(squirrelNSP,nca,keypatch,encKeyBlock,t)
						t.close()
				if nca.header.getRightsId() == 0:
					nca.rewind()
					encKeyBlock = nca.header.getKeyBlock()
					if str(keypatch) != "False":
						t = tqdm(total=False, unit='B', unit_scale=False, leave=False)
						if keypatch < nca.header.getCryptoType2():
							encKeyBlock,crypto1,crypto2=squirrelNSP.get_new_cryptoblock(squirrelNSP,nca,keypatch,encKeyBlock,t)
						t.close()
				nca.rewind()
				i=0
				newheader=nsp.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)
				outf.write(newheader)
				written+=len(newheader)
				nca.seek(0xC00)
				break
			else:pass
	nsp.flush()
	nsp.close()
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
