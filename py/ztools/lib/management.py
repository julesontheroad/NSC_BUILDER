import sys
import os
import Fs.Nsp as Nsp
import Fs.Xci as Xci
import sq_tools
import Hex
from binascii import hexlify as hx, unhexlify as uhx
import listmanager

def get_key_fromdict(fp):
	if fp.endswith('.nsp') or fp.endswith('.nsx'):
		files_list=sq_tools.ret_nsp_offsets(fp)
		files=list();filesizes=list()
		fplist=list()
		for k in range(len(files_list)):
			entry=files_list[k]
			fplist.append(entry[0])
		for i in range(len(files_list)):
			entry=files_list[i]
			filepath=entry[0]
			if filepath.endswith('.cnmt.nca'):
				f=Nsp(fp,'rb')
				titleid,titleversion,base_ID,keygeneration,rightsId,RSV,RGV,ctype,metasdkversion,exesdkversion,hasHtmlManual,Installedsize,DeltaSize,ncadata=f.get_data_from_cnmt(filepath)
				titlekey,dectkey=f.db_get_titlekey(rightsId,keygeneration)
				f.flush()
				f.close()
				# print(titlekey);print(rightsId)				
				return titlekey
				
def rename_nsx(fp):
	if  fp.endswith('.txt'): 
		filelist=listmanager.read_lines_to_list(fp,all=True)
		for file in filelist:
			if file[0]=='"':
				file=file[1:]
			if file[-1]=='"':
				file=file[:-1]			
			file=os.path.abspath(file)
			test_ifnsx(file)	
			listmanager.striplines(fp,number=1,counter=True)				
	else:
		test_ifnsx(fp)
	try:
		os.remove(fp) 	
	except:
		pass			
		
def test_ifnsx(fp):
	if fp.endswith('.nsp') or fp.endswith('.nsx'):
		print('Checking file {}'.format(fp))	
		titlekey=get_key_fromdict(fp)
		if titlekey != False:
			check=bytes.fromhex(titlekey)
			if sum(check)==0:
				print(' - File is nsx')			
				newpath =fp[:-1]+'x'
				if newpath==fp:
					print('   > Current name is correct')	
				else:	
					os.rename(fp, newpath)
					print('   > Renamed to {}'.format(os.path.basename(newpath)))						
			else:	
				print(' - File is nsp')			
				newpath =fp[:-1]+'p'
				if newpath==fp:
					print('   > Current name is correct')	
				else:	
					os.rename(fp, newpath)
					print('   > Renamed to {}'.format(os.path.basename(newpath)))		
		else:
			print(' - File is standard crypto. Skipping...')
	else:		
		print(" - File isn't nsp or nsx. Skipping...")
		
def verify_ticket(fp):		
	if fp.endswith('.nsp') or fp.endswith('.nsz'):
		files_list=sq_tools.ret_nsp_offsets(fp)	
		for i in range(len(files_list)):
			entry=files_list[i]
			filepath=entry[0]
			if filepath.endswith('.tick'):		
				pass
		# f=Nsp(fp,'rb')
		# f.flush()
		# f.close()	
	elif fp.endswith('.xci') or fp.endswith('.xcz'):
		files_list=sq_tools.ret_xci_offsets(fp)		
		pass	
		# f=Xci(fp)
		# f.flush()
		# f.close()		