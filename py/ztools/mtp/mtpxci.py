import aes128
import Print
import os
import shutil
import json
# import listmanager
# from tqdm import tqdm
from Fs import Nsp as squirrelNSP
from Fs import Xci as squirrelXCI
from Fs.Nca import NcaHeader
from Fs.File import MemoryFile
import sq_tools
import io
from Fs import Type as FsType
import Keys
from binascii import hexlify as hx, unhexlify as uhx
from DBmodule import Exchange as exchangefile
import math

bucketsize = 81920


def gen_xci_parts(filepath,cachefolder=None,keepupd=False,id_target=False,keypatch=False,export_type='csv'):
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
	for i in range(len(files_list)):
		entry=files_list[i]
		cnmtfile=entry[0]
		if cnmtfile.endswith('.cnmt.nca'):
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
						files.append(str(row['NcaId'])+'.nca')
						filesizes.append(int(row['Size']))					
				elif row['NCAtype']=='Meta':
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
						files.append(str(row['NcaId'])+'.nca')
						filesizes.append(int(row['Size']))				
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
	for fi in files:
		for nspF in xci.hfs0:
			if str(nspF._path)=="secure":
				for nca in nspF:	
					if nca._path==fi:
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
							encKeyBlock = crypto.encrypt(titleKeyDec * 4)
							if str(keypatch) != "False":
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=squirrelXCI.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)	
						if nca.header.getRightsId() == 0:
							nca.rewind()				
							encKeyBlock = nca.header.getKeyBlock()	
							if str(keypatch) != "False":
								if keypatch < nca.header.getCryptoType2():
									encKeyBlock,crypto1,crypto2=squirrelXCI.get_new_cryptoblock(nca, keypatch,encKeyBlock,t)					
						nca.rewind()					
						i=0				
						newheader=xci.get_newheader(nca,encKeyBlock,crypto1,crypto2,hcrypto,gc_flag)		
						outf.write(newheader)
						written+=len(newheader)
						nca.seek(0xC00)	
						if (str(nca.header.contentType) != 'Content.PROGRAM'):
							data=nca.read()	
							nca.close()
							outf.write(data)
							written+=len(data)
						else:
							remainder = bucketsize*multiplier - written
							data=nca.read(remainder)
							nca.close()
							outf.write(data)
							written+=len(data)						
						break					
					else:pass
	outf.close()		
	if export_type=='json':
		files_json=os.path.join(cachefolder, "files.json")	
		d={}
		d['0']={"step": 0,
		  "filepath":outfile ,
		  "size":( bucketsize*multiplier) ,
		  "targetsize":( bucketsize*multiplier) ,
		  "off1":0,
		  "off2":( bucketsize*multiplier)
		}
		for j in files_list:
			if j[0]==files[-1]:
				off1=j[1]
				off2=j[2]
				targetsize=j[3]
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
				off1=j[1]
				off2=j[2]
				targetsize=j[3]	
		tfile=os.path.join(cachefolder, "files.csv")
		i=0;
		with open(tfile,'w') as csvfile:
			if i==0:
				csvfile.write("{}|{}|{}|{}|{}|{}\n".format("step","filepath","size","targetsize","off1","off2"))
				i+=1
			if i==1:	
				csvfile.write("{}|{}|{}|{}|{}|{}\n".format(0,outfile,( bucketsize*multiplier),( bucketsize*multiplier),0,( bucketsize*multiplier)))		
				i+=1				
			if i==2:	
				csvfile.write("{}|{}|{}|{}|{}|{}".format(1,filepath,( os.path.getsize(filepath)),targetsize,off1,off2))		
				i+=1			
					
