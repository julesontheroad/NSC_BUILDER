#from nutFs.Pfs0 import Pfs0Stream
import Print
import os
import json
import nutFs
import nutFs.Pfs0
import nutFs.Type
import nutFs.Nca
import nutFs.Type
import subprocess
from contextlib import closing
import zstandard
import listmanager
from tqdm import tqdm
import time

def sortednutFs(nca):
	fs = []
	for i in nca.sections:
		fs.append(i)
	fs.sort(key=lambda x: x.offset)
	return fs

def isNcaPacked(nca):
	fs = sortednutFs(nca)

	if len(fs) == 0:
		return True

	next = 0x4000
	for i in range(len(fs)):
		if fs[i].offset != next:
			return False

		next = fs[i].offset + fs[i].size

	if next != nca.size:
		return False

	return True
	
def foldercompress(ifolder, ofolder = None, level = 17, threads = 0, t=['nsp']):
	mylist=listmanager.folder_to_list(ifolder,t)
	counter=len(mylist)
	for item in mylist:
		print(item)
		if ofolder is None:
			nszPath = item[0:-1] + 'z'		
		else:
			nszPath = os.path.join(ofolder, os.path.basename(item[0:-1] + 'z'))
		compress(item,ofolder=None,level=level,threads=threads,ofile=nszPath)
		counter-=1
		print('\nStill %d files to compress\n'%(counter))


def compress(filePath,ofolder = None, level = 17,  threads = 0, ofile= None):
	compressionLevel=int(level)
	container = nutFs.factory(filePath)

	container.open(filePath, 'rb')

	CHUNK_SZ = 0x1000000
	
	if ofolder is None and ofile is None:
		nszPath = filePath[0:-1] + 'z'
	elif ofolder is not None:
		nszPath = os.path.join(ofolder, os.path.basename(filePath[0:-1] + 'z'))
	elif ofile is not None:
		nszPath = ofile	
		
	nszPath = os.path.abspath(nszPath)
	
	Print.info('Compressing with level %d and %d threads' % (compressionLevel, threads))	
	Print.info('\n  %s -> %s \n' % (filePath, nszPath))	

	newNsp = nutFs.Pfs0.Pfs0Stream(nszPath)

	for nspf in container:
		if isinstance(nspf, nutFs.Nca.Nca) and (nspf.header.contentType == nutFs.Type.Content.PROGRAM or nspf.header.contentType == nutFs.Type.Content.PUBLICDATA):
			if isNcaPacked(nspf):
				cctx = zstandard.ZstdCompressor(level=compressionLevel, threads = threads)

				newFileName = nspf._path[0:-1] + 'z'

				f = newNsp.add(newFileName, nspf.size)
				
				start = f.tell()

				nspf.seek(0)
				f.write(nspf.read(0x4000))
				written = 0x4000

				compressor = cctx.stream_writer(f)
				
				header = b'NCZSECTN'
				header += len(sortednutFs(nspf)).to_bytes(8, 'little')
				
				i = 0
				for fs in sortednutFs(nspf):
					i += 1
					header += fs.realOffset().to_bytes(8, 'little')
					header += fs.size.to_bytes(8, 'little')
					header += fs.cryptoType.to_bytes(8, 'little')
					header += b'\x00' * 8
					header += fs.cryptoKey
					header += fs.cryptoCounter
					
				f.write(header)
				written += len(header)
				timestamp = time.time()
				decompressedBytes = 0x4000
				totsize=0
				for fs in sortednutFs(nspf):
					totsize+=fs.size
				t = tqdm(total=totsize, unit='B', unit_scale=True, leave=False)
				
				for fs in sortednutFs(nspf):
					fs.seek(0)			
					while not fs.eof():
						buffer = fs.read(CHUNK_SZ)
						t.update(len(buffer))
						if len(buffer) == 0:
							raise IOError('read failed')

						written += compressor.write(buffer)
						
						decompressedBytes += len(buffer)
				t.close()	
				compressor.flush(zstandard.FLUSH_FRAME)

				elapsed = time.time() - timestamp
				minutes = elapsed / 60
				seconds = elapsed % 60
				
				speed = 0 if elapsed == 0 else (nspf.size / elapsed)				
				
				print('\n  * %d written vs %d tell' % (written, f.tell() - start))
				written = f.tell() - start
				print('  * Compressed %d%% %d -> %d  - %s' % (int(written * 100 / nspf.size), decompressedBytes, written, nspf._path))
				print('  * Compressed in %02d:%02d at speed: %.1f MB/s\n' % (minutes, seconds, speed / 1000000.0))				
				newNsp.resize(newFileName, written)
				continue
			else:
				print('not packed!')

		f = newNsp.add(nspf._path, nspf.size)
		nspf.seek(0)
		t = tqdm(total=nspf.size, unit='B', unit_scale=True, leave=False)
		while not nspf.eof():
			buffer = nspf.read(CHUNK_SZ)
			t.update(len(buffer))
			f.write(buffer)
		t.close()	


	newNsp.close()
