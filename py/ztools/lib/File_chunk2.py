import sq_tools

class chunk():
	def __init__(self,firstchunk,type='all',locations=None,files=None,fileopen=None):
		self.locations=file_locations(firstchunk,type)
	
	def file_locations(filepath,t='all',Printdata=False):		
		filenames=retchunks(filepath)
		# print(filenames)
		locations=list()
		if filepath.endswith('.xc0'):
			files_list=sq_tools.ret_xci_offsets(filepath)	
		elif filepath.endswith('.ns0'):
			files_list=sq_tools.ret_nsp_offsets(filepath)		
		for file in files_list:
			if not t.lower()=='all':
				# print(file)
				if (str(file[0]).lower()).endswith(t.lower()):
					location1,tgoffset1=get_file_and_offset(filenames,file[1])
					location2,tgoffset2=get_file_and_offset(filenames,file[2])		
					locations.append([file[0],file[3],location1,tgoffset1,location2,tgoffset2])
					if Printdata==True:
						print('{}'.format(file[0]))		
						print('- Starts in file {} at offset {}'.format(location1[-4:],tgoffset1))
						print('- Ends in file {} at offset {}'.format(location2[-4:],tgoffset2))
						print('')			
				else:pass
			else:	
				location1,tgoffset1=get_file_and_offset(filenames,file[1])
				location2,tgoffset2=get_file_and_offset(filenames,file[2])		
				locations.append([file[0],file[3],location1,tgoffset1,location2,tgoffset2])
				if Printdata==True:
					print('{}'.format(file[0]))		
					print('- Starts in file {} at offset {}'.format(location1[-4:],tgoffset1))
					print('- Ends in file {} at offset {}'.format(location2[-4:],tgoffset2))
					print('')
		return locations		
		
	def get_file_and_offset(filelist,targetoffset):
		startoffset=0;endoffset=0
		# print(targetoffset)
		# print(filelist)
		for i in range(len(filelist)):
			entry=filelist[i]
			filepath=entry[0];size=entry[1]
			startoffset=endoffset
			endoffset+=size
			# print(endoffset)
			if targetoffset>endoffset:
				pass
			else:
				partialoffset=targetoffset-startoffset
				return filepath,partialoffset
		return False,False	
		
	def read_start(filepath):		
		filenames=retchunks(filepath)
		f = chain_streams(generate_open_file_streams(filenames))
		if filepath.endswith('.xc0'):
			files_list=sq_tools.ret_xci_offsets(filepath)	
		elif filepath.endswith('.ns0'):
			files_list=sq_tools.ret_nsp_offsets(filepath)		
		print(files_list)

		# feed=f.read(0x500)
		# Hex.dump(feed)
		f.flush()
		f.close()	
