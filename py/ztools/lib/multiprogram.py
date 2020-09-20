import aes128
import Print
import os
import shutil
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs import Nca
from Fs import factory
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
from Fs import Ticket
import sq_tools
from tqdm import tqdm
from binascii import hexlify as hx, unhexlify as uhx
import sys
import re
import copy 


def groupncabyid_and_idoffset(filepath,ofolder,export,buffer=65536,fat='exfat',fx='files',nodecompress=False):
	if filepath.endswith('.nsp') or filepath.endswith('.nsx') or filepath.endswith('.nsz'):		
		container = squirrelNSP(filepath, 'rb')
	elif filepath.endswith('.xci') or filepath.endswith('.xcz'):	
		container = factory(filepath)		
		container.open(filepath, 'rb')	
	contentlist=list()
	ncalist=list()
	completefilelist=list()
	for nspF in container.hfs0:
		if str(nspF._path)=="secure":
			for file in nspF:		
				completefilelist.append(str(file._path))
	for nspF in container.hfs0:
		if str(nspF._path)=="secure":
			for nca in nspF:					
				if type(nca) == Nca:
					if 	str(nca.header.contentType) == 'Content.META':
						crypto1=nca.header.getCryptoType()
						crypto2=nca.header.getCryptoType2()	
						if crypto1 == 2:
							if crypto1 > crypto2:								
								keygen=nca.header.getCryptoType()
							else:			
								keygen=nca.header.getCryptoType2()	
						else:			
							keygen=nca.header.getCryptoType2()				
						ncalist=list()
						for f in nca:
							for cnmt in f:
								nca.rewind()
								f.rewind()
								cnmt.rewind()						
								titleid=cnmt.readInt64()
								titleversion = cnmt.read(0x4)
								cnmt.rewind()
								cnmt.seek(0xE)
								offset=cnmt.readInt16()
								content_entries=cnmt.readInt16()
								meta_entries=cnmt.readInt16()
								content_type=str(cnmt._path)
								content_type=content_type[:-22]	
								titleid2 = str(hx(titleid.to_bytes(8, byteorder='big'))) 	
								titleid2 = titleid2[2:-1]	
								cnmt.seek(0x20)
								if content_type=='Application':
									original_ID=titleid2
									cnmt.readInt64()
									ttag=''
									CTYPE='BASE'
								elif content_type=='Patch':
									original_ID=cnmt.readInt64()	
									original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
									original_ID = original_ID[2:-1]	
									ttag=' [UPD]'
									CTYPE='UPDATE'
								elif content_type=='AddOnContent':
									original_ID=cnmt.readInt64()	
									original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
									original_ID = original_ID[2:-1]	
									ttag=' [DLC]'
									CTYPE='DLC'								
								else: 
									original_ID=cnmt.readInt64()	
									original_ID=str(hx(original_ID.to_bytes(8, byteorder='big')))
									original_ID = original_ID[2:-1]							
								cnmt.seek(0x20+offset)			
								for i in range(content_entries):
									vhash = cnmt.read(0x20)
									NcaId = cnmt.read(0x10)
									size = cnmt.read(0x6)
									ncatype = cnmt.read(0x1)
									idoffset = cnmt.read(0x1)	
									idoffset=int.from_bytes(idoffset, byteorder='little', signed=True)
								#**************************************************************	
									version=str(int.from_bytes(titleversion, byteorder='little'))
									version='[v'+version+']'
									titleid3 ='['+ titleid2+']'
									nca_name=str(hx(NcaId))
									nca_name=nca_name[2:-1]+'.nca'
									ncz_name=nca_name[:-1]+'z'
									if nca_name in completefilelist or ncz_name in completefilelist:
										ncalist.append([nca_name,idoffset])				
								nca_meta=str(nca._path)
								if nca_meta in completefilelist:	
									ncalist.append([nca_meta,0])
								target=str(nca._path)
								tit_name,editor,ediver,SupLg,regionstr,isdemo = container.inf_get_title(target,offset,content_entries,original_ID)
								tit_name = (re.sub(r'[\/\\\:\*\?\!\"\<\>\|\.\s™©®()\~]+', ' ', tit_name))
								tit_name = tit_name.strip()
								if tit_name=='DLC' and (str(titleid2).endswith('000') or str(titleid2).endswith('800')):
									tit_name='-'
									editor='-'										
								tid='['+titleid2+']'
								filename=tit_name+' '+tid+' '+version
								titlerights=titleid2+str('0'*15)+str(crypto2)
								contentlist.append([filename,titleid2,titlerights,keygen,ncalist,CTYPE,tit_name,tid,version])
	'''		
	for i in contentlist:
		print("")
		print('Filename: '+i[0])
		print('TitleID: '+i[1])
		print('TitleRights: '+i[2])
		print('Keygen: '+str(i[3]))			
		for j in i[4]:
			print (j)	
	'''						
	newcontentlist=[];counter=0
	for i in contentlist:
		idoffsets=[]
		files=i[4]
		metafile=None
		for j in files:
			if j[0].endswith('.cnmt'):
				metafile=j[0]
				break
		for j in files:
			if j[-1] not in idoffsets:
				idoffsets.append(j[-1])	
		for j in idoffsets:
			entry=copy.deepcopy(contentlist[counter])
			newfiles=[]
			for k in files:
				if k[-1]==j:
					newfiles.append(k[0])
			if not metafile in newfiles:
				newfiles.append(metafile)	
			filename=entry[-3]+' '+(entry[-2])[:-2]+str(j)+' '+version
			entry[0]=filename
			entry[4]=newfiles	
			newcontentlist.append(entry)	
		counter+=1			
			
	for nspF in container.hfs0:
		if str(nspF._path)=="secure":
			for file in nspF:									
				if type(file) == Ticket or file._path.endswith('.cert'):	
					test=file._path
					test=test[0:32]
					for i in newcontentlist:
						if i[2]==test:
							i[4].append(file._path)
				elif file._path.endswith('.xml'):	
					test=file._path
					test=test[0:-4]+'.nca'
					for i in newcontentlist:
						if test in i[4]:
							i[4].append(file._path)			
			
	for i in newcontentlist:
		if export == 'nsp':
			container.cd_spl_nsp(buffer,i[0],ofolder,i[4],fat,fx,nodecompress)
		if export == 'xci':		
			if  i[5] != 'BASE':
				container.cd_spl_nsp(buffer,i[0],ofolder,i[4],fat,fx,nodecompress)	
			else:		
				container.cd_spl_xci(buffer,i[0],ofolder,i[4],fat,fx,nodecompress)
		if export == 'both':	
			if  i[5] != 'BASE':
				container.cd_spl_nsp(buffer,i[0],ofolder,i[4],fat,fx,nodecompress)					
			else:
				container.cd_spl_nsp(buffer,i[0],ofolder,i[4],fat,fx,nodecompress)			
				container.cd_spl_xci(buffer,i[0],ofolder,i[4],fat,fx,nodecompress)						

# def exchange_id_offset(filepath,original_idoffset,new_idoffset):

# def split_multiprogram_by_id(filepath,ofolder,output_format):


# write_cnmt_titleid
# write_cnmt_updateid