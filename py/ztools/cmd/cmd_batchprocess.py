import subprocess
import os
import sys
import listmanager
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs import factory
import Print
from secondary import clear_Screen

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
	
default_output=os.path.join(NSCB_dir,'NSCB_output')

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

def create_nsp_direct(filepath,outfolder,buffer=65536,fat="exfat",fx="files",delta=False,metapatch='false',RSV_cap=268435656,keypatch='false'):
	tname=str(os.path.basename(filepath))[:-3]+'nsp'
	tempfolder=os.path.join(outfolder,'temp')
	tmpfile=os.path.join(tempfolder,tname)
	if not os.path.exists(tempfolder):
		os.makedirs(tempfolder)		
	if filepath.endswith('xci'):
		f = factory(filepath)
		f.open(filepath, 'rb')
	elif filepath.endswith('nsp'):	
		f = squirrelNSP(filepath, 'rb')		
	f.c_nsp_direct(buffer,tmpfile,outfolder,fat,fx,delta,metapatch,RSV_cap,keypatch)
	f.flush()
	f.close()	
	
def create_xci_direct(filepath,outfolder,buffer=65536,fat="exfat",fx="files",delta=False,metapatch='false',RSV_cap=268435656,keypatch='false'):
	tname=str(os.path.basename(filepath))[:-3]+'xci'
	tempfolder=os.path.join(outfolder,'temp')
	tmpfile=os.path.join(tempfolder,tname)
	if not os.path.exists(tempfolder):
		os.makedirs(tempfolder)			
	if filepath.endswith('xci'):
		f = factory(filepath)
		f.open(filepath, 'rb')
	elif filepath.endswith('nsp'):	
		f = squirrelNSP(filepath, 'rb')	

	temp=f.c_xci_direct(buffer,tmpfile,outfolder,fat,fx,delta,metapatch,RSV_cap,keypatch)
	
def loop_repack(tfile=None,buffer=65536,pv='false',kp='false',RSVcap=268435656,fat="exfat",fx='files',skdelta="true",ofolder=default_output,type="both",verify=False):
	if tfile==None:
		sys.exit("Didn't get a text file input")	
	if not os.path.exists(tfile):
		sys.exit(f"Can't locate {tfile}")
	file_list=listmanager.read_lines_to_list(tfile,all=True)
	if not file_list:
		sys.exit(f"{tfile} doesn't have entries")		
	if not os.path.exists(ofolder):
		os.makedirs(ofolder)	
	try:
		buffer=int(buffer)
	except:
		buffer=65536
	pv=str(pv).lower()	
	kp=str(kp).lower()	
	try:
		RSV_cap=int(RSV_cap)
	except:
		RSV_cap=268435656
	if str(skdelta).upper()=="FALSE":
		delta=False
	else:
		delta=True
	c=0	
	for fp in file_list:
		if c==0:
			clear_Screen()
			c+=1
		About()
		processing(fp)
		if type=='nsp' or type=='both':
			try:
				create_nsp_direct(fp,ofolder,buffer=buffer,fat=fat,fx=fx,delta=delta,metapatch=pv,RSV_cap=RSV_cap,keypatch=kp)
				print("")				
			except BaseException as e:
				Print.error('Exception: ' + str(e))	
		if type=='xci' or type=='both':
			try:
				create_xci_direct(fp,ofolder,buffer=buffer,fat=fat,fx=fx,delta=delta,metapatch=pv,RSV_cap=RSV_cap,keypatch=kp)
				print("")
			except BaseException as e:
				Print.error('Exception: ' + str(e))	
		listmanager.striplines(tfile,number=1,counter=True)	
		
def processing(input):
	name=os.path.basename(input)
	print('------------------------------------------------------------------------------------- ')
	print(f'Processing: {name}')
	print('------------------------------------------------------------------------------------- ')


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