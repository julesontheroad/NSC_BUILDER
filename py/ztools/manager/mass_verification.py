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
	
def check_xci_certs(ifolder,tfile,tfile2):
	from listmanager import folder_to_list,striplines,read_lines_to_list
	from Fs import Xci
	import os
	if not os.path.exists(tfile):		
		xci_files=folder_to_list(ifolder,['xci'])
		with open(tfile,"w", encoding='utf8') as t:
			for file in xci_files:
				t.write(file+'\n')
	else:
		xci_files=read_lines_to_list(tfile,all=True)
	counter=len(xci_files)
	for file in xci_files:
		try:
			xci=Xci(file)
			if not xci.gamecardCert.Cert_is_fake:
				print(f"{file} has personalized certificate")
				with open(tfile2,"a", encoding='utf8') as t:
					t.write(file+'\n')
			else:
				print(f"{file} has a wiped certificate")			
			xci.close()
			counter-=1
			striplines(tfile,1,True)
		except:
			try:
				with open(tfile2,"a", encoding='utf8') as t:
					t.write("Error:"+file+'\n')			
			except:pass
			counter-=1
			striplines(tfile,1,True)	
	try:			
		os.remove(tfile)
	except:pass		
	