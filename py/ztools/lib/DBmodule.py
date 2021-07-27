'''
Based on Pysos with modifications to handle switch added clases to handle NSCB library
Pydbm - Library Data:
* Name: Pysos
* Author: dagnelies
* License: Apache 2.0 -> https://github.com/dagnelies/pysos
* Modifications by julesontheroad:
https://github.com/julesontheroad/NSC_BUILDER/
'''

import io
import os.path
import bisect
try:
	import ujson as json
except:
	import json
from binascii import hexlify as hx, unhexlify as uhx
import ast
import textwrap

indent = 1
tabs = '\t' * indent	

def parseLine(line):
	#print(line)
	(left, sep, right) = line.partition(b'\t')
	key = json.loads( left.decode('utf8') )
	value = json.loads( right.decode('utf8') )
	return ( key, value )
	
def parseKey(line):
	(left, sep, right) = line.partition(b'\t')
	key = json.loads( left.decode('utf8') )
	return key
	
def parseValue(line):
	(left, sep, right) = line.partition(b'\t')
	value = json.loads( right.decode('utf8') )
	return value

def _int2bytes(i,n):
	return i.to_bytes(n, byteorder='little', signed=False)

def _bytes2int(b):
	return int.from_bytes(b, byteorder='little', signed=False)
	
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
	
if os.path.exists(zconfig_dir):
	DATABASE_folder=os.path.join(zconfig_dir, 'DB')
	exchangefile=os.path.join(DATABASE_folder,'exchange.txt')
	urlconfig=os.path.join(zconfig_dir,'NUT_DB_URL.txt')
else:
	DATABASE_folder=squirrel_dir	
	exchangefile=os.path.join(DATABASE_folder,'titlekeys.txt')
	urlconfig=os.path.join(squirrel_dir,'NUT_DB_URL.txt')

if not os.path.exists(DATABASE_folder):
	os.makedirs(DATABASE_folder)		
	
fwdb=os.path.join(DATABASE_folder,'fw.json')	

class Exchange():	
	def add(titlerights,titlekey):
		dbstr=str()
		dbstr+=str(titlerights).upper()+'|'
		if len(titlekey)==30:
			titlekey='00'+str(titlekey).upper()
		if len(titlekey)==31:
			titlekey='0'+str(titlekey).upper()
		dbstr+=str(titlekey).upper()
		with open(exchangefile, 'a') as dbfile:			
			dbfile.write(dbstr+ '\n')		
			
	def retrievekey(titlerights):
		with open(exchangefile,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')		
			for row in readCSV:
				if row[0]==titlerights.upper():
					tk=row[1]
					tk.strip()
					return tk
		return None			
		
	def deletefile():
		try:os.remove(exchangefile)
		except:pass		

class FWDB():
	def add(FW,filepath):
		import sq_tools	
		dump={};newdict={};fwfiles=list()
		if os.path.exists(fwdb):
			with open(fwdb) as json_file:	
				data = json.load(json_file)		
				for i in data:	
					dict=data[i]
					if len(dict.items())>0:
						dump[i]=dict
					else: return False		
		if not FW in dump.items():				
			if filepath.endswith('nsp'):
				files_list=sq_tools.ret_nsp_offsets(filepath,32)
			elif filepath.endswith('xci') or filepath.endswith('xc0'):
				files_list=sq_tools.ret_xci_offsets_fw(filepath)
			else:
				return False
			# print(files_list)
			# print(len(files_list))
			for i in range(len(files_list)):
				f=files_list[i]
				file=f[0]
				# print(file)
				fwfiles.append(file)
			newdict['files']=fwfiles
			dump[FW]=newdict
			app_json = json.dumps(dump, indent=4)
			with open(fwdb, 'w') as json_file:
			  json_file.write(app_json)	
			print('Added firmware {}'.format(FW))	
		else:
			print('Firmware {} is already in json'.format(FW))			

	def add_specific():	
		dump={};files=list()
		if os.path.exists(fwdb):
			with open(fwdb) as json_file:	
				data = json.load(json_file)		
				for i in data:	
					dict=data[i]
					if len(dict.items())>0:
						dump[i]=dict
					else: return False	
		else: return False			
		for i in dump:
			entry=dump[i]
			files=entry['files']
			for j in dump:
				if j==i:
					pass
				else:
					entry2=dump[j]
					files2=entry2['files']
					aux=list()
					for k in files:
						if k not in files2:
							aux.append(k)
					files=aux
			entry['specific']=files
			dump[i]=entry
		app_json = json.dumps(dump, indent=4)
		with open(fwdb, 'w') as json_file:
		  json_file.write(app_json)	
		print('Updated firmware json')

	def add_real_number(k,filepath):	
		dump={};files=list()
		if os.path.exists(fwdb):
			with open(fwdb) as json_file:	
				data = json.load(json_file)		
				for i in data:	
					dict=data[i]
					if len(dict.items())>0:
						dump[i]=dict
					else: return False	
		else: return False	
		if k in dump.keys():
			FW,fwver,unique=FWDB.read_fw(filepath,add=False,doprint=True)	
			entry=dump[k]
			entry['RSV']=fwver
			entry['ExactFirm']=FW
			entry['RSVcnmt']=unique			
			dump[k]=entry			
		app_json = json.dumps(dump, indent=4)
		with open(fwdb, 'w') as json_file:
		  json_file.write(app_json)	
		print('Updated firmware json')			
		
	def detect_xci_fw(filepath,doprint=True,remote=False):
		import sq_tools	
		import nutdb
		nutdb.check_other_file(urlconfig,'fw',nutdb=False)
		FW=None;dump={}
		if remote==False:
			xcifw=sq_tools.ret_xci_offsets_fw(filepath)
		else:
			from Drive import DriveTools
			xcifw=DriveTools.get_files_from_head_xci_fw(filepath)
		# print(xcifw)
		fwfiles=list()
		if len(xcifw)>0:
			for i in xcifw:
				entry=i
				fwfiles.append(entry[0])
		else: 
			if doprint==True:
				print('- Firmware was deleted from file')		
			return 'Deleted'
		# print(fwfiles)
		if os.path.exists(fwdb):
			with open(fwdb) as json_file:	
				data = json.load(json_file)	
				for i in data:	
					dict=data[i]
					if len(dict.items())>0:
						dump[i]=dict
					else: return False	
		for i in fwfiles:
			for j in dump:
				entry=dump[j]
				try:
					files=entry['specific']
					if i in files:
						FW=j
						if doprint==True:
							print('- Xci includes firmware: '+FW)
						return FW
				except:
					try:
						RSVcnmt=entry['RSVcnmt']
						if str(RSVcnmt).lower()==str(i).lower():
							FW=j
							if doprint==True:
								print('- Xci includes firmware: '+FW)
							return FW
					except:pass		
		fwfiles.sort()
		for j in dump:
			entry=dump[j]
			files=entry['files']
			files.sort()
			if fwfiles==files:
				FW=j
				if doprint==True:
					print('- Xci includes firmware: '+FW)
				return FW
		try:
			FW,fwver,unique=FWDB.read_fw(filepath,add=True,doprint=False)
			if doprint==True:
				print('- Xci includes firmware: '+FW)
			return FWnumber
		except:pass
		if doprint==True:
			print('- Unknown firmware')
		return 'UNKNOWN'	
			
	def read_fw(filepath,add=False,doprint=True):
		if filepath.endswith('.xci'):
			from Fs import uXci as fwFS
			f=fwFS(filepath)
			FWnumber,fwver,unique=f.get_FW_number()
			f.close()
			if doprint==True:
				print(str(fwver)+" ({})".format(FWnumber))
			if add==True:
				FWDB.add(FWnumber,filepath)
				FWDB.add_real_number(FWnumber,filepath)					
				FWDB.add_specific()
		elif filepath.endswith('.nsp'):
			from Fs import Nsp as fwFS	
			f=fwFS(filepath)			
			FWnumber,fwver,unique=f.get_FW_number()
			f.close()
			if doprint==True:
				print(str(fwver)+" ({})".format(FWnumber))
			if add==True:
				FWDB.add(FWnumber,filepath)
				FWDB.add_real_number(FWnumber,filepath)		
				FWDB.add_specific()			
		return FWnumber,fwver,unique
	
class Dict(dict):
	START_FLAG = b'# FILE-DICT v1\n'

	def __init__(self, path):
		self.path = path
		
		if os.path.exists(path):
			file = io.open(path, 'r+b')
		else:
			file = io.open(path, 'w+b')
			file.write( self.START_FLAG )
			file.flush()
		
		self._file = file
		self._offsets = {}   # the (size, offset) of the lines, where size is in bytes, including the trailing \n
		self._free_lines = []
		self._observers = []
		
		offset = 0
		while True:
			line = file.readline()
			if line == b'': # end of file
				break
			
			# ignore empty lines
			if line == b'\n':
				offset += len(line) 
				continue
			
			if line.startswith(b'#'):	# skip comments but add to free list
				if len(line) > 5:
					self._free_lines.append( (len(line), offset) )
			else:
				# let's parse the value as well to be sure the data is ok
				key = parseKey(line)
				self._offsets[key] = offset
			
			offset += len(line) 
		
		self._free_lines.sort()
		#print("free lines: " + str(len(self._free_lines)))
		
	def _freeLine(self, offset):
		self._file.seek(offset)
		self._file.write(b'#')
		self._file.flush()
		
		line = self._file.readline()
		size = len(line) + 1   # one character was written beforehand
		
		if size > 5:
			bisect.insort(self._free_lines, (len(line)+1, offset) )
		
	def _findLine(self, size):
		index = bisect.bisect( self._free_lines, (size,0) )
		if index >= len( self._free_lines ):
			return None
		else:
			return self._free_lines.pop(index)
		
	def _isWorthIt(self, size):
		# determines if it's worth to add the free line to the list
		# we don't want to clutter this list with a large amount of tiny gaps
		return (size > 5 + len(self._free_lines))
		
	def __getitem__(self, key):
		offset = self._offsets[key]
		self._file.seek(offset)
		line = self._file.readline()
		value = parseValue(line)
		return value
		
	def __setitem__(self, key, value):
		# trigger observers
		if self._observers:
			old_value = self[key] if key in self else None
			for callback in self._observers:
				callback(key, value, old_value)
		
		if key in self._offsets:
			# to be removed once the new value has been written
			old_offset = self._offsets[key]
		else:
			old_offset = None
			
		
		line = json.dumps(key,ensure_ascii=False) + '\t' + json.dumps(value,ensure_ascii=False) + '\n'
		line = line.encode('UTF-8')
		size = len(line)
		
		found = self._findLine(size)

		if found:
			# great, we can recycle a commented line
			(place, offset) = found
			self._file.seek(offset)
			diff = place - size
			# if diff is 0, we'll override the line perfectly:		XXXX\n -> YYYY\n
			# if diff is 1, we'll leave an empty line after:		  XXXX\n -> YYY\n\n
			# if diff is > 1, we'll need to comment out the rest:	 XXXX\n -> Y\n#X\n (diff == 3)
			if diff > 1:
				line += b'#'
				if diff > 5:
					# it's worth to reuse that space
					bisect.insort(self._free_lines, (diff, offset + size) )
				
		else:
			# go to end of file
			self._file.seek(0, os.SEEK_END)
			offset = self._file.tell()
		
		# if it's a really big line, it won't be written at once on the disk
		# so until it's done, let's consider it a comment
		self._file.write(b'#' + line[1:])
		if line[-1] == 35:
			# if it ends with a "comment" (bytes to recycle),
			# let's be clean and avoid cutting unicode chars in the middle
			while self._file.peek(1)[0] & 0x80 == 0x80: # it's a continuation byte
				self._file.write(b'.')
		self._file.flush()
		# now that everything has been written...
		self._file.seek(offset)
		self._file.write(line[0:1])
		self._file.flush()
	
		# and now remove the previous entry
		if old_offset:
			self._freeLine(old_offset)
		
		self._offsets[key] = offset
		
		
			
		
	def __delitem__(self, key):
		# trigger observers
		if self._observers:
			old_value = self[key]
			for callback in self._observers:
				callback(key, None, old_value)
				
		offset = self._offsets[key]
		self._freeLine(offset)
		del self._offsets[key]
		
		
	def __contains__(self, key):
		return (key in self._offsets)
	
	def observe(self, callback):
		self._observers.append(callback)
		
	
	def keys(self):
		return self._offsets.keys()
	
	def clear(self):
		self._file.truncate(0)
		self._file.flush()
		self._offsets = {}
		self._free_lines = []
		
	def items(self):
		offset = 0
		while True:
			# if somethig was read/written while iterating, the stream might be positioned elsewhere
			if self._file.tell() != offset:
				self._file.seek(offset) #put it back on track
			
			line = self._file.readline()
			if line == b'': # end of file
				break
			
			offset += len(line)
			# ignore empty and commented lines
			if line == b'\n' or line[0] == 35:
				continue
			yield parseLine(line)
	
	def __iter__(self):
		return self.keys()
	
	def values(self):
		for item in self.items():
			yield item[1]
			
	def __len__(self):
		return len(self._offsets)

	def size(self):
		self._file.size()
		
		
	def close(self):
		self._file.close()
		#print("free lines: " + str(len(self._free_lines)))

class List(list):
	START_FLAG = b'# FILE-LIST v1\n'
	
	def __init__(self, path):
		self._dict = Dict(path)
		self._indexes = sorted( self._dict.keys() )
		self._observers = []
	
	def __getitem__(self, i):
		key = self._indexes[i]
		return self._dict[key]
		
	def __setitem__(self, i, value):
		# trigger observers
		if self._observers:
			old_value = self[i]
			for callback in self._observers:
				callback(i, value, old_value)
				
		key = self._indexes[i]
		self._dict[key] = value
	
	def append(self, value):
		# trigger observers
		if self._observers:
			for callback in self._observers:
				callback(len(self._indexes), value, None)
				
		if len(self._indexes) == 0:
			key = 0
		else:
			key = self._indexes[-1] + 1
				
		self._dict[key] = value
		self._indexes.append(key)
		
	def __delitem__(self, i):
		# trigger observers
		if self._observers:
			old_value = self[i]
			for callback in self._observers:
				callback(i, None, old_value)
				
		key = self._indexes[i]
		del self._dict[key]
		del self._indexes[i]
	
	def __len__(self):
		return len(self._indexes)
		
	def __contains__(self, key):
		raise Exception('Operation not supported for lists')
	
	# this must be overriden in order to provide the correct order
	def __iter__(self):
		for i in range(len(self)):
			yield self[i]
	
	def observe(self, callback):
		self._observers.append(callback)
		
	def clear(self):
		self._dict.clear()
		self._indexes = []
	
	
	def size(self):
		self._dict.size()
		
	def close(self):
		self._dict.close()	

def load(path):
	file = open(path, 'rb')
	first = file.readline()
	
	if first == Dict.START_FLAG:
		file.close()
		return Dict(path)
	if first == List.START_FLAG:
		file.close()
		return List(path)
		
	for line in file:
		if line[0] == 0x23:
			continue
		key = parseKey(line)
		if isinstance(key, int):
			file.close()
			return List(path)
		else:
			file.close()
			return Dict(path)
	raise Exception("Empty collection without header. Cannot determine whether it is a list or a dict.")
	
import csv
import chardet
#from chardet.universaldetector import UniversalDetector
#import cchardet as chardet

def detectEncoding(path):
	with open(path, 'rb') as f:
		res = chardet.detect( f.read(10*1024*1024) )
	print(res)
	return res['encoding']
	
	detector = UniversalDetector()
	for line in open(path, 'rb'):
		detector.feed(line)
		if detector.done: break
	detector.close()
	print(detector.result)
	return detector.result.encoding
	
def csv2sos(path, keys=None, encoding=None, dialect=None):
	
	if not encoding:
		encoding = detectEncoding(path)
		print('Detected encoding: %s' % encoding)
	
	csvfile = open(path, 'rt', encoding=encoding)
	sosfile = open(path + '.sos', 'wt', encoding='utf8')

	if not dialect:
		dialect = csv.Sniffer().sniff(csvfile.read(1024*1024), delimiters=[';','\t',','])
		print('Detected csv dialect: %s' % dialect)
	
	csvfile.seek(0)
	reader = csv.DictReader(csvfile, dialect=dialect)
	i = 0
	for row in reader:
		sosfile.write(str(i) + '\t' + json.dumps(row, ensure_ascii=False) + '\n')
		i += 1
		if i % 100000 == 0:
			print("%10d items converted" % i)

	csvfile.close()	
	sosfile.close()

class MainDB:		

	def clone(dbfile,dbfile2):
		Datashelve = Dict(dbfile)
		Datashelve2 = Dict(dbfile2)
		Datashelve2['fields']=Datashelve['fields']
		for k in sorted(Datashelve.keys()):	
			if k!='fields':
				Datashelve2[k]=Datashelve[k]
		Datashelve.close()
		Datashelve2.close()		
		
	def initializeDB(dbfile):
		Datashelve = Dict(dbfile)
		incorporate=list()
		incorporate.append('id')
		incorporate.append('baseid')	
		incorporate.append('nsuId')	
		incorporate.append('rightsId')	
		incorporate.append('keygeneration')		
		incorporate.append('RSV')		
		incorporate.append('RGV')	
		incorporate.append('FWoncard')				
		incorporate.append('key')
		incorporate.append('deckey')		
		incorporate.append('ContentType')
		incorporate.append('distEshop')			
		incorporate.append('distCard')		
		incorporate.append('baseName')
		incorporate.append('multigameCard')				
		incorporate.append('contentname')	
		incorporate.append('editor')	
		incorporate.append('version')		
		incorporate.append('cversion')	
		incorporate.append('metasdkversion')		
		incorporate.append('exesdkversion')		
		incorporate.append('languages')			
		incorporate.append('genretags')	
		incorporate.append('ratingtags')	
		incorporate.append('worldreleasedate')		
		incorporate.append('numberOfPlayers')	
		incorporate.append('InstalledSize')
		incorporate.append('deltasize')			
		incorporate.append('GCSize')	
		incorporate.append('TrimmedSize')				
		incorporate.append('HtmlManual')		
		incorporate.append('isbn')	
		incorporate.append('ratingage')	
		incorporate.append('accrequired')	
		incorporate.append('UserAccountSwitchLock')	
		incorporate.append('AddOnContentRegistrationType')		
		incorporate.append('ParentalControl')	
		incorporate.append('ScreenshotsEnabled')	
		incorporate.append('VideocaptureEnabled')		
		incorporate.append('DataLossConfirmation')		
		incorporate.append('PlayLogPolicy')			
		incorporate.append('PresenceGroupId')		
		incorporate.append('AddOnContentBaseId')		
		incorporate.append('SaveDataOwnerId')	
		incorporate.append('UserAccountSaveDataSize')	
		incorporate.append('UserAccountSaveDataJournalSize')	
		incorporate.append('DeviceSaveDataSize')		
		incorporate.append('DeviceSaveDataJournalSize')			
		incorporate.append('BcatDeliveryCacheStorageSize')	
		incorporate.append('ApplicationErrorCodeCategory')	
		incorporate.append('LocalCommunicationId')	
		incorporate.append('LogoType')	
		incorporate.append('LogoHandling')	
		incorporate.append('RuntimeAddOnContentInstall')	
		incorporate.append('CrashReport')	
		incorporate.append('Hdcp')		
		incorporate.append('SeedForPseudoDeviceId')		
		incorporate.append('BcatPassphrase')		
		incorporate.append('UserAccountSaveDataSizeMax')		
		incorporate.append('UserAccountSaveDataJournalSizeMax')		
		incorporate.append('DeviceSaveDataSizeMax')			
		incorporate.append('DeviceSaveDataJournalSizeMax')	
		incorporate.append('TemporaryStorageSize')	
		incorporate.append('CacheStorageSize')	
		incorporate.append('CacheStorageJournalSize')	
		incorporate.append('CacheStorageDataAndJournalSizeMax')	
		incorporate.append('CacheStorageIndexMax')	
		incorporate.append('PlayLogQueryableApplicationId')	
		incorporate.append('PlayLogQueryCapability')	
		incorporate.append('Repair')	
		incorporate.append('ProgramIndex')
		incorporate.append('RequiredNetworkServiceLicenseOnLaunch')	
		incorporate.append('iconUrl')		
		incorporate.append('screenshots')		
		incorporate.append('bannerUrl')	
		incorporate.append('intro')		
		incorporate.append('description')	
		incorporate.append('ncasizes')		
		Datashelve['fields']=(incorporate)
		#for i in Datashelve['fields']:
		#	print(str(i))
		Datashelve.close()	

	def addkey(dbfile,key):	
		Datashelve = Dict(dbfile)
		if not key in Datashelve:
			print('Adding entry: '+key)
			fields=Datashelve['fields']
			nf=len(fields)
			#print(str(nf))
			#print(fields)
			incorporatate=dict()
			for i in range(nf):
				incorporatate[str(fields[i])]='-'
			Datashelve[key]=incorporatate
			#print(Datashelve['fields'])
			#print(Datashelve[key])
			Datashelve.close()
		else:
			print(key+' Already in dB. Skipping')		
			Datashelve.close()
		
	def expandkeyfields(dbfile):	
		fields=MainDB.getfields(dbfile)
		nf=len(fields)	
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():
			#for a,b in Datashelve[k].items():
			try:
				op=len(Datashelve[k].items())
				if op<nf:
					#print(len(Datashelve[k].items()))
					entry=Datashelve[k]
					for i in fields:
						if i in entry:
							pass
						else:
							entry[str(i)]='-'
				Datashelve[k]=entry
				print('Expanded entry: '+k)
			except:pass		
		Datashelve.close()		

	def rearrangedfields(dbfile):	
		fields=MainDB.getfields(dbfile)
		nf=len(fields)	
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():
			#for a,b in Datashelve[k].items():
			try:
				op=len(Datashelve[k].items())
				entry=Datashelve[k]
				incorporatate=dict()
				for i in fields:
					if i in entry:
						incorporatate[i]=entry[i]
					else:
						incorporatate[i]='-'
				Datashelve[k]=incorporatate
				print('Rearranged entry: '+k)
			except:pass		
		Datashelve.close()	

	def changefieldname(dbfile,fname,newfname):	
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():
			#for a,b in Datashelve[k].items():
			try:
				op=len(Datashelve[k].items())
				entry=Datashelve[k]
				incorporatate=dict()
				for i in entry:
					if i == fname:
						incorporatate[newfname]=entry[fname]
					else:
						incorporatate[i]=entry[i]						
				else:
					incorporatate[i]='-'
				Datashelve[k]=incorporatate
				print('Changed entry: '+k)
			except:pass		
		Datashelve.close()			


	def getfields(dbfile):	
		Datashelve = Dict(dbfile)
		fields=Datashelve['fields']
		Datashelve.close()		
		return fields
		

	def init_keys_from_csv(dbfile,csvfile):	
		fields=MainDB.getfields(dbfile)
		nf=len(fields)
		with open(csvfile,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0	
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
				else:	
					if 'id' and 'version' in csvheader:
						id=csvheader.index('id')
						version=csvheader.index('version')
						dbkey=(str(row[id])+'_v'+str(row[version])).lower()
						MainDB.addkey(dbfile,dbkey)

	def append_data_from_csv(dbfile,csvfile):							
		fields=MainDB.getfields(dbfile)
		nf=len(fields)
		with open(csvfile,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0	
			Datashelve = Dict(dbfile)
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
				else:
					if 'id' and 'version' in csvheader:	
						id=csvheader.index('id')
						version=csvheader.index('version')
						dbkey=(str(row[id])+'_v'+str(row[version])).lower()						
						entry=Datashelve[dbkey]
						for x in csvheader:
							if x in fields:
								if entry[x]=='-':
									entry[x]=row[csvheader.index(str(x))]
						Datashelve[dbkey]=entry
						print(Datashelve[dbkey])
			Datashelve.close()	

	def ow_lan_from_csv(dbfile,csvfile):							
		fields=MainDB.getfields(dbfile)
		nf=len(fields)
		langues=['us','uk','jp','fr','de','lat','es','it','nl','cad','por','ru','kor','tw','ch']
		with open(csvfile,'rt',encoding='utf8') as csvfile:
			readCSV = csv.reader(csvfile, delimiter='|')	
			i=0	
			Datashelve = Dict(dbfile)
			for row in readCSV:
				if i==0:
					csvheader=row
					i=1
				else:
					if 'id' and 'version' in csvheader:	
						languestring=list();haslang=False;check='0'
						id=csvheader.index('id')
						version=csvheader.index('version')
						content=csvheader.index('ContentType')
						if str(row[content])!='DLC':
							try:
								for l in langues:
									if l in csvheader:
										#print(l)
										lg=csvheader.index(l)
										#print(str(row[lg]))
										check=row[lg]
										if check=='1':
											haslang=True
											languestring.append(l)
											check='0'
							except:continue
						#print(languestring)		
						#print(haslang)
						if haslang==True:			
							dbkey=(str(row[id])+'_v'+str(row[version])).lower()		
							try:
								entry=Datashelve[dbkey]
								entry['languages']=languestring
								Datashelve[dbkey]=entry
								print(dbkey+': '+str(entry['languages']))
							except:pass
			Datashelve.close()	
		fields=MainDB.getfields(dbfile)
		nf=len(fields)		
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():	
			try:
				added=False
				entry=Datashelve[k]	
				if 	entry['id']!='-' and (str(entry['id'])[-3:])!='000' and (str(entry['id'])[-3:])!='800':
					include=['languages']				
					baseid=entry['baseid']
					dbkey=(baseid+'_v0').lower()	
					baseentry=Datashelve[dbkey]					
					for fld in fields:
						if fld in include:
							entry[fld]=baseentry[fld]	
							added=True
				Datashelve[k]=entry		
				if added==True:
					print(dbkey+': '+str(entry['languages']))
			except:pass		
		Datashelve.close()			
								
	def add_baseid(dbfile):
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():	
			try:
				entry=Datashelve[k]	
				if 	entry['id']!='-' and entry['baseid'] =='-':
					if 	str(entry['id'])[-3:]=='000':
						entry['baseid']=entry['id']
					elif str(entry['id'])[-3:]=='800':
						entry['baseid']=str(entry['id'])[:-3]+'000'
					else:
						fileid=str(entry['id'])
						DLCnumb=fileid
						token=int(hx(bytes.fromhex('0'+DLCnumb[-4:-3])),16)-int('1',16)
						token=str(hex(token))[-1]
						token=token.upper()
						fileid=fileid[:-4]+token+'000'
						entry['baseid']=fileid
				Datashelve[k]=entry		
				print('- Added baseid: '+entry['baseid'])	
			except:pass		
		Datashelve.close()	
		
								
	def fix_baseid(dbfile):
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():	
			try:
				entry=Datashelve[k]	
				if 	entry['id']!='-':
					if 	str(entry['id'])[-3:]=='000':
						entry['baseid']=entry['id']
					elif str(entry['id'])[-3:]=='800':
						entry['baseid']=str(entry['id'])[:-3]+'000'
						#print(entry['id'])
						#print(entry['baseid'])
					else:
						fileid=str(entry['id'])
						DLCnumb=fileid
						token=int(hx(bytes.fromhex('0'+DLCnumb[-4:-3])),16)-int('1',16)
						token=str(hex(token))[-1]
						token=token.upper()
						fileid=fileid[:-4]+token+'000'
						entry['baseid']=fileid
				Datashelve[k]=entry		
				print('- Added baseid: '+entry['baseid'])	
			except:pass		
		Datashelve.close()			

	def fix_basenames(dbfile):
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():	
			try:
				entry=Datashelve[k]	
				if 	entry['id']!='-':	
					if 	(str(entry['id'])[-3:])!='000' and (str(entry['id'])[-3:])!='800':				
						if 	(entry['contentname']=='-' and entry['baseName'] !='-'):	
							entry['contentname'] = entry['baseName']
							baseid=entry['baseid']
							#version=entry['version']
							dbkey=(baseid+'_v0').lower()	
							baseentry=Datashelve[dbkey]
							basename=baseentry['baseName']
							entry['baseName'] = basename	
						elif entry['baseName']=='-':	
							baseid=entry['baseid']
							#version=entry['version']
							dbkey=(baseid+'_v0').lower()	
							baseentry=Datashelve[dbkey]
							basename=baseentry['baseName']
							entry['baseName'] = basename
						else:
							baseid=entry['baseid']
							#version=entry['version']
							dbkey=(baseid+'_v0').lower()	
							#print(dbkey)
							baseentry=Datashelve[dbkey]
							basename=baseentry['baseName']
							entry['baseName'] = basename						
				Datashelve[k]=entry		
				print('- Added basename: '+entry['baseName'])	
			except:pass		
		Datashelve.close()

	def fix_RGV(dbfile):
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():	
			try:
				entry=Datashelve[k]	
				if 	entry['id']!='-':	
					if 	(str(entry['id'])[-3:])!='000': 
						entry['RGV']='-'
					if (str(entry['id'])[-3:])!='800':		
						entry['RGV']='-'
					else:
						RGV=entry['RGV']
						if int(RGV)<65536:
							RGV=int(int(RGV)*65536)
							entry['RGV']=str(RGV)				
				Datashelve[k]=entry		
				print('- Modified: '+entry['id'])	
			except:pass		
		Datashelve.close()			
		
	def expand_data_from_baseid(dbfile):
		fields=MainDB.getfields(dbfile)
		nf=len(fields)		
		Datashelve = Dict(dbfile)
		for k in Datashelve.keys():	
			try:
				added=False
				entry=Datashelve[k]	
				if 	entry['id']!='-' and (str(entry['id'])[-3:])!='000':	
					if (str(entry['id'])[-3:])=='800':
						include=['nsuId','editor','languages','genretags','ratingtags','numberOfPlayers','iconUrl','screenshots','bannerUrl','intro','description']
						#print(entry['id'])
						#print(entry['baseid'])
					else:
						include=['editor','languages','genretags','ratingtags','numberOfPlayers']				
					baseid=entry['baseid']
					dbkey=(baseid+'_v0').lower()	
					baseentry=Datashelve[dbkey]					
					for fld in fields:
						if fld in include and entry[fld]=='-':
							entry[fld]=baseentry[fld]	
							added=True
				Datashelve[k]=entry		
				if added==True:
					print('- Added data for: '+entry['id'])	
			except:pass		
		Datashelve.close()				
			
	
	def append_data_from_json(dbfile,jsonfile):			
		fields=MainDB.getfields(dbfile)
		nf=len(fields)	
		with open(jsonfile) as json_file:	
			Datashelve = Dict(dbfile)		
			data = json.load(json_file)	
			for i in data:
				print(i)
				id='';version='';dbkey=''
				for j,k in data[i].items():
					if str(j) == 'id':
						id=str(k)
					if str(j) == 'version':	
						version=str(k)
						if version.lower()=='null' or version.lower()=='none':
							version='0'						
						#print(version)
					if 	id !='' and version != '':
						dbkey=(str(id)+'_v'+str(version).lower())	
						break
				if 	dbkey != '':
					if dbkey in Datashelve:
						entry=Datashelve[dbkey]	
						for j,k in data[i].items():
							field=MainDB.correspondanceinDB(str(j))
							if field == 'name':
								if id[-3:] != '000' and id[-3:] != '800':
									field='contentname'
							if field in fields:
								if entry[field]=='-' and str(k).lower() != 'none':	
									entry[field]=str(k)		
								if str(entry[field]).lower()=='none':
									entry[field]='-'
						Datashelve[dbkey]=entry				
						#print(Datashelve[dbkey])					
			Datashelve.close()		

	def correspondanceinDB(field):
		if field=='category':
			field='genretags'
		if field=='ratingContent':
			field='ratingtags'	
		if field=='releaseDate':			
			field='worldreleasedate'
		if field=='publisher':			
			field='editor'			
		return field
			
def getSize(bytes):
	if bytes>(1024*1024*1024):
		Gbytes=bytes/(1024*1024*1024)
		Gbytes=round(Gbytes,2)
		Gbytes=str(Gbytes)+"GB"
		return Gbytes
	if bytes>(1024*1024):
		Mbytes=bytes/(1024*1024)
		Mbytes=round(Mbytes,2)
		Mbytes=str(Mbytes)+"MB"
		return Mbytes		
	if bytes>(1024):
		Kbytes=bytes/(1024)
		Kbytes=round(Kbytes,2)
		Kbytes=str(Kbytes)+"KB"	
		return Kbytes		
	else:
		bytes=str(bytes)+"B"	
		return bytes		
		
def searchgenre(dbfile,genre):
	Datashelve = Dict(dbfile)
	for k in Datashelve.keys():
		showdata=False		
		try:
			entry=Datashelve[k]		
			for a,b in Datashelve[k].items():
				if a=='ContentType':
					if b.upper()=='GAME':
						showdata=True
						break
					else:
						break		
			if showdata==True:	
				for a,b in Datashelve[k].items():			
					if a=='genretags':
						genreslist=ast.literal_eval(b)	
						#print(genreslist)
						if genre in	genreslist:
							print(entry['id'])
							print('  - '+entry['baseName'])
							print('  - '+entry['editor'])		
							print('  - '+entry['genretags'])	
							print('  - '+entry['ratingtags'])						
							print('\n')	
						break
		except BaseException as e:
			#print('Exception: ' + str(e))
			continue			
	Datashelve.close()				

def printlatestversions(dbfile):	
	Datashelve = Dict(dbfile)
	titleid='';
	for k in sorted(Datashelve.keys()):
		try:
			if k!='fields':
				#print(k[13:16])
				#print(k[:13])			
				if titleid=='':
					if k[13:16]=='800':
						titleid=k[:13]+'000'
					else:
						titleid=k[:16]				
					version=k[18:]
				else:
					if k[13:16]=='800':
						if titleid==(k[:13]+'000'):				
							if int(version)<int(k[18:]):
								version=k[18:]
						else:
							#if int(version)>0:
							print(titleid+' v'+version)
							titleid=k[:16]
							version=k[18:]							
					else:
						if titleid==(k[:16]):	
							if int(version)<int(k[18:]):
								version=k[18:]
						else:
							if int(version)>0 and titleid[-3:]=='000':
								baseid=titleid
								titleid=titleid[:13]+'800'
								print(baseid+':')
								print('  * UPD: '+titleid+' v'+version)			
							else:	
								print('  * DLC: '+titleid+' v'+version)
							titleid=k[:16]
							version=k[18:]		
		except:pass		
	try:		
		if int(version)>0 and titleid[-3:]=='000':
			baseid=titleid
			titleid=titleid[:13]+'800'
			print(baseid+':')
			print('  * UPD: '+titleid+' v'+version)			
		else:	
			print('  * DLC: '+titleid+' v'+version)
	except:pass				
	Datashelve.close()		
	
class Reader():			
	def __init__(self, dbfile,titleid=False,version=0,arg=False,name=False):
		self._dict = Dict(dbfile)	
		if arg != False:
			self._arg=arg
			self._titleid=arg[:16]
			self._version=int(arg[18:])
		elif titleid != False:
			self._titleid = titleid	
			self._version = int(version)
			self._arg = str(titleid)+'_v'+str(version)
		elif name != False:		
			arg=self.trackname(name)
			self._arg=arg			
			self._titleid=arg[:16]
			self._version=int(arg[18:])		

	def close(self):
		self._dict.close()				

	def fields(self):
		Datashelve = self._dict
		dict2=Datashelve[self._arg].items()
		fields=list()
		for a,b in dict2:
			fields.append(a)
		return fields

	def query(self,field):
		Datashelve = self._dict
		dict2=Datashelve[self._arg].items()
		answer=None
		for a,b in dict2:
			if a.upper()==field.upper():
				answer=b
		return answer				
			
	def trackname(self,name):	
		name=name.lower()
		Datashelve = self._dict
		for k in Datashelve.keys():
			try:
				for a,b in Datashelve[k].items():
					if a=='ContentType' and b=='GAME':
						if a=='baseName' or a=='contentname':
							if name in b.lower():
								return k
				for a,b in Datashelve[k].items():
					if a=='ContentType'and b!='GAME' and (b=='UPD' or b=='DLC'):
						if a=='baseName' or a=='contentname':
							if name in b.lower():
								return k		
				for a,b in Datashelve[k].items():
					if a=='ContentType' and (b!='UPD' and b!='DLC' and b!='GAME'):
						if a=='baseName' or a=='contentname':
							if name in b.lower():
								return k								
			except:pass					

	def tracknames(self,name,onlygames=False):	
		name=name.lower()
		Datashelve = self._dict
		keys=list()
		for k in Datashelve.keys():
			try:
				if k[13:16]!='000' and onlygames==True:
					pass
				else:				
					for a,b in Datashelve[k].items():
						if a=='baseName' or a=='contentname':
							if name in b.lower():
								keys.append(k)
								break
			except:pass		
		return(keys)

	def trackgenres(self,genre):	
		genre=genre.lower()
		Datashelve = self._dict
		keys=list()
		for k in Datashelve.keys():
			try:
				for a,b in Datashelve[k].items():
					if a=='genretags':
						if genre in b.lower():
							keys.append(k)
							break							
			except:pass		
		return(keys)		
				
	def tracktags(self,tag):	
		tag=tag.lower()
		Datashelve = self._dict
		keys=list()
		for k in Datashelve.keys():
			try:
				for a,b in Datashelve[k].items():
					if a=='genretags' or a=='ratingtags':
						if tag in b.lower():
							keys.append(k)
							break
			except:pass		
		return(keys)				

	def tracklanguages(self,lan):	
		lan=lan.lower()
		Datashelve = self._dict
		keys=list()
		for k in Datashelve.keys():
			try:
				for a,b in Datashelve[k].items():
					if a=='languages':
						if lan in str(b).lower():
							keys.append(k)
							break							
			except:pass		
		return(keys)	

	def trackeditor(self,edit,onlygames=False):	
		edit=edit.lower()
		Datashelve = self._dict
		keys=list()
		for k in Datashelve.keys():
			try:
				if k[13:16]!='000' and onlygames==True:
					pass
				else:	
					for a,b in Datashelve[k].items():
						if a=='editor':
							if edit in str(b).lower():
								keys.append(k)
								break							
			except:pass		
		return(keys)		
		
	def track(self,field,value,onlygames=False,filter=True):	
		if not isinstance(filter, list):
			if filter !=True and filter != False:
				filter=True
		if not isinstance(value, list) and not isinstance(field, list):
			value=value.lower()
			Datashelve = self._dict
			keys=list()
			for k in Datashelve.keys():
				try:
					if k[13:16]!='000' and onlygames==True:
						pass
					else:	
						for a,b in Datashelve[k].items():
							if a.lower()==field.lower():
								if value in str(b).lower():
									keys.append(k)
									break							
				except:pass		
			return(keys)				
		elif filter == False:
			Datashelve = self._dict
			keys=list()			
			for i in range(len(field)):
				in_field=str(field[i]).lower()
				in_value=str(value[i]).lower()
				#print(in_field)
				#print(in_value)				
				for k in Datashelve.keys():
					try:
						if k[13:16]!='000' and onlygames==True:
							pass
						else:	
							for a,b in Datashelve[k].items():
								if a.lower()==in_field.lower():
									if in_value in str(b).lower():
										keys.append(k)
										break		
					except:pass				
			return(keys)
		elif filter == True:
			Datashelve = self._dict
			keys=list()			
			for i in range(len(field)):
				if i==0:
					in_field=str(field[i]).lower()
					in_value=str(value[i]).lower()
					#print(in_field)
					#print(in_value)				
					for k in Datashelve.keys():
						try:
							if k[13:16]!='000' and onlygames==True:
								pass
							else:	
								for a,b in Datashelve[k].items():
									if a.lower()==in_field.lower():
										if in_value in str(b).lower():
											keys.append(k)
											break	
						except:pass		
				else:
					auxlist=list()				
					in_field=str(field[i]).lower();
					in_value=str(value[i]).lower();
					for k in keys:
						try:
							for a,b in Datashelve[k].items():
								if a.lower()==in_field.lower():
									if in_value in str(b).lower():
										auxlist.append(k)
										break								
						except BaseException as e:
							print('Exception: ' + str(e))
							continue
					keys=auxlist	
					del auxlist									
			return(keys)		
		elif isinstance(filter, list):
			Datashelve = self._dict
			keys=list()					
			for i in range(len(field)):
				in_field=str(field[i]).lower()
				in_value=str(value[i]).lower()
				in_filter=str(filter[i]).lower()	
				if in_filter=='false':
					for k in Datashelve.keys():
						try:
							if k[13:16]!='000' and onlygames==True:
								pass
							else:	
								for a,b in Datashelve[k].items():
									if a.lower()==in_field.lower():
										if in_value in str(b).lower():
											keys.append(k)
											break	
						except:pass	
				else: pass	
			for i in range(len(field)):
				auxlist=list()	
				in_field=str(field[i]).lower()
				in_value=str(value[i]).lower()
				in_filter=str(filter[i]).lower()				
				if in_filter=='true':
					for k in keys:
						try:
							for a,b in Datashelve[k].items():
								if a.lower()==in_field.lower():
									if in_value in str(b).lower():
										auxlist.append(k)
										break								
						except BaseException as e:
							print('Exception: ' + str(e))
							continue
					keys=auxlist	
					del auxlist	
				else: pass
			return(keys)
