import listmanager
import os

def decompress_nsz(ifolder,ofolder,buffer = 65536,delta=False,xml_gen=False):
	extlist=['nsz']
	files=listmanager.folder_to_list(ifolder,extlist)
	import decompressor		
	for filepath in files:
		basename=os.path.basename(os.path.abspath(filepath))
		endname=basename[:-1]+'p'
		endname =os.path.join(ofolder,endname)
		decompressor.decompress_nsz(filepath,endname,buffer,delta,xml_gen)	
		
def rebuild_nsp(ifolder,ofolder,buffer = 65536,delta=False,xml_gen=False,export='nsp'):
	extlist=['nsp','nsz']
	files=listmanager.folder_to_list(ifolder,extlist)
	from Fs import Nsp
	import decompressor		
	total=len(files)
	for filepath in files:	
		if filepath.endswith('nsp'):
			basename=os.path.basename(os.path.abspath(filepath))
			endfile =os.path.join(ofolder,basename)
			print('Processing: '+filepath)
			f = Nsp(filepath)
			f.rebuild(buffer,endfile,delta,False,xml_gen)
			f.flush()
			f.close()
		elif filepath.endswith('nsz'):			
			basename=os.path.basename(os.path.abspath(filepath))
			endname=basename[:-1]+'p'
			endname =os.path.join(ofolder,endname)
			decompressor.decompress_nsz(filepath,endname,buffer,delta,xml_gen)
		total-=1
		print("**********************************************************")
		print(('Still {} files to process').format(str(total)))
		print("**********************************************************")