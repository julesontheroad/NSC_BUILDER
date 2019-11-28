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
		
def add_signed_footer(message=None,ifolder=None,tfile=None,ext='all',rewrite=False):
	from sq_tools import add_signed_footer as sign
	from ast import literal_eval  as eval
	if ext=='all':
		ext=['nsp','nsx','nsz','xci','xcz']
	else:
		if isinstance(ext, list):
			ext=ext
		else:
			try:
				ext=eval(ext)
			except:pass
			ext=ext.split(',')	
	if ifolder!=None:
		try:
			ifolder=eval(ifolder)
		except:pass
		files=listmanager.folder_to_list(ifolder,ext)
	elif tfile!=None:
		try:
			tfile=eval(tfile)
		except:pass	
		files=read_lines_to_list(tfile,all=True)
	else:
		return False
	for filepath in files:
		try:
			sign(filepath,message,rewrite)
		except:
			print('Error in '+filepath)
		
def delete_footer(ifolder=None,tfile=None,ext='all'):
	from sq_tools import delete_footer
	from ast import literal_eval  as eval
	if ext=='all':
		ext=['nsp','nsx','nsz','xci','xcz']
	else:
		if isinstance(ext, list):
			ext=ext
		else:
			try:
				ext=eval(ext)
			except:pass
			ext=ext.split(',')	
	if ifolder!=None:
		files=listmanager.folder_to_list(ifolder,ext)
	elif tfile!=None:
		files=read_lines_to_list(tfile,all=True)
	else:
		return False
	for filepath in files:	
		delete_footer(filepath)	
		
def read_footer(ifolder=None,tfile=None,ext='all'):
	from sq_tools import read_footer
	from ast import literal_eval  as eval
	if ext=='all':
		ext=['nsp','nsx','nsz','xci','xcz']
	else:
		if isinstance(ext, list):
			ext=ext
		else:
			try:
				ext=eval(ext)
			except:pass
			ext=ext.split(',')	
	if ifolder!=None:
		files=listmanager.folder_to_list(ifolder,ext)
	elif tfile!=None:
		files=read_lines_to_list(tfile,all=True)
	else:
		return False
	for filepath in files:	
		read_footer(filepath)	