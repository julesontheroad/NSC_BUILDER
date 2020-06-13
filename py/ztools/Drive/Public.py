# -*- coding: utf-8 -*-
import re
import warnings
from six.moves import urllib_parse
import os
import os.path as osp
import re
import shutil
import sys
import tempfile
import requests
import six
from tqdm import tqdm
import argparse
import pkg_resources
from binascii import hexlify as hx, unhexlify as uhx
import Hex
import io
import sq_tools
import Fs.Nca as Nca
import Fs.Nsp as Nsp
import Fs.Nacp as Nacp
from Fs.File import MemoryFile
from hashlib import sha256,sha1
from Drive import DriveTools

CHUNK_SIZE = 512 * 1024  # 512KB

def readInt8(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(1), byteorder=byteorder, signed=signed)

def readInt16(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(2), byteorder=byteorder, signed=signed)

def readInt32(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(4), byteorder=byteorder, signed=signed)

def readInt64(f, byteorder='little', signed = False):
		return int.from_bytes(f.read(8), byteorder=byteorder, signed=signed)

def readInt128(f, byteorder='little', signed = False):
	return int.from_bytes(f.read(16), byteorder=byteorder, signed=signed)

def parse_url(url, warning=True):
	"""Parse URLs especially for Google Drive links.
	file_id: ID of file on Google Drive.  
	is_download_link: Flag if it is download link of Google Drive.
	"""
	# test=url.split('drive')
	# print(test)
	# if len(test)>1:
		# url='https://drive.{}'.format(test[1])
	# print(url)	
	parsed = urllib_parse.urlparse(url)
	query = urllib_parse.parse_qs(parsed.query)
	is_gdrive = parsed.hostname == 'drive.google.com'
	is_download_link = parsed.path.endswith('/uc')
	if is_download_link == False:
		is_download_link = parsed.path.endswith('/view')
	if is_download_link == False:
		is_download_link = parsed.path.endswith('/edit')
	if is_download_link == False:
		is_download_link = parsed.path.endswith('/view?usp=drivesdk')
		
	file_id = None
	if is_gdrive and 'id' in query:
		file_ids = query['id']
		if len(file_ids) == 1:
			file_id = file_ids[0]
	match = re.match(r'^/file/d/(.*?)/view$', parsed.path)
	if not match:
		match = re.match(r'^/file/d/(.*?)/edit$', parsed.path)	
	if match:
		file_id = match.groups()[0]
		
	if is_gdrive and not is_download_link:
		if url.startswith('https://drive.google.com/open?id='):
			url=url.replace('https://drive.google.com/open?id=','')	
		if '/' in url:
			url=url.split('/')
			file_id=url[0]
		else:
			file_id=url
		is_download_link=True
	
	if is_gdrive and not is_download_link:
		warnings.warn(
			'You specified Google Drive Link but it is not the correct link '
			"to download the file. Maybe you should try: {url}".format(url='https://drive.google.com/uc?id={}'.format(file_id))
		)
	return file_id, is_download_link
	
def get_url_from_gdrive_confirmation(contents):
    url = ''
    for line in contents.splitlines():
        m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
        if m:
            url = 'https://docs.google.com' + m.groups()[0]
            url = url.replace('&amp;', '&')
            return url
        m = re.search('confirm=([^;&]+)', line)
        if m:
            confirm = m.groups()[0]
            url = re.sub(
                r'confirm=([^;&]+)',
                r'confirm={}'.format(confirm),
                url,
            )
            return url
        m = re.search('"downloadUrl":"([^"]+)', line)
        if m:
            url = m.groups()[0]
            url = url.replace('\\u003d', '=')
            url = url.replace('\\u0026', '&')
            return url	
			
def is_readable(url,file_id,is_download_link,sess):
	url_origin=url
	readable=False
	output=""
	while True:
		res = sess.get(url, stream=True)
		if 'Content-Disposition' in res.headers:
			# This is the file
			break

			# Need to redirect with confiramtion
		url = get_url_from_gdrive_confirmation(res.text)

		if url is None:
			print('Permission denied: %s' % url_origin, file=sys.stderr)
			print("Maybe you need to change permission over, 'Anyone with the link'?", file=sys.stderr)
			break
		else:
			readable=True
			
	if readable==True:		
		try:
			if file_id and is_download_link:
				m = re.search('filename="(.*)"',res.headers['Content-Disposition'])
				#print(m)
				output = m.groups()[0]
			else:
				output = osp.basename(url)
			print('FILENAME:         '+output)		
		except:
			print("File download quota reached or temporarly restricted")
	return readable,output,url,res,sess	
	
def untag(output):
	tid1=list()
	tid2=list()
	tid1=[pos for pos, char in enumerate(output) if char == '[']
	clean_name=output[0:tid1[0]]
	if clean_name[-1] == ' ':
		clean_name=clean_name[:-1]
	return clean_name	
	
class location():
	def __init__(self,url_origin=None,ID=None,url=None,doPrint=True):
		self.url=None;self.requesturl=None;self.readable=None;self.name=None
		self.response=None;self.sess=None;self.position=0;self.size=None
		self.ftype=None
		self.sess = requests.session()
		self.sess.headers.update({"Range" : 'bytes=%s-%s' % (0,8*1024)})
		file_id, is_download_link=parse_url(url_origin)
		if is_download_link == False:
			print('Bad url')
			return False	
		elif file_id==None:
			print("Can't get ID")
			return False			
		else:
			self.ID=file_id
			self.url='https://drive.google.com/uc?id={id}'.format(id=self.ID)
			if doPrint==True:
				print('\nFILE ID:          '+self.ID)
				print('DOWNLOAD URL:     '+self.url)		
		self.readable,self.name,self.url,self.response,self.sess=is_readable(self.url,self.ID,is_download_link,self.sess)
		self.get_size()
		self.rewind()
		if (self.name.lower()).endswith('.nsp') or (self.name.lower()).endswith('.nsx') or (self.name.lower()).endswith('.nsz'): 
			self.ftype='nsp'
		elif (self.name.lower()).endswith('.xci') or (self.name.lower()).endswith('.xcz'): 
			self.ftype='xci'
			
	def get_size(self):
		self.sess.headers.update = {'Range':'bytes=0-'}
		r = self.sess.get(self.url, stream=True).headers['Content-Range']
		try:
			contleng=r.partition('/')
			contleng=contleng[-1]
			self.size=int(contleng)
		except:
			contrange=re.split('\W+',r)
			contrange=contrange[-2]
			self.size=int(contrange)
		
	def rewind(self):
		hd={"Range" : 'bytes=%s-%s' % (0,int(self.size))}
		self.sess.headers=hd
		self.response = self.sess.get(self.url, stream=True)	
		self.position=0
		return self.response
		
	def seek(self,p,off2=None):
		if off2==None:
			off2=self.size
		p=int(p);off2=int(off2)-0x01
		hd={"Range" : 'bytes=%s-%s' % (p,off2)}
		self.sess.headers=hd			
		self.response = self.sess.get(self.url, stream=True)	
		self.position=p
		return self.response

	def read(self,sz=None):
		if sz==None:
			sz=self.size-self.position
		sz=int(sz)
		buf=64*1024
		end=self.position+sz-0x01
		hd={"Range" : 'bytes=%s-%s' % (self.position,end)}
		self.sess.headers=hd	
		self.response = self.sess.get(self.url, stream=True)	
		data=b''
		for dump in self.response.iter_content(chunk_size=buf):
			data=data+dump
			self.position=self.position+len(dump)
		return data	

	def read_at(self,pos,sz):
		pos=int(pos);off2=int(sz)
		self.position=pos
		buf=64*1024
		end=self.position+sz-0x01
		hd={"Range" : 'bytes=%s-%s' % (self.position,end)}
		self.sess.headers=hd			
		self.response = self.sess.get(self.url, stream=True)	
		data=b''
		for dump in self.response.iter_content(chunk_size=buf):
			data=data+dump
			self.position=self.position+len(dump)
		return data	
	
def download(url,ofolder,sz=64,trimm=True,file=None,name=None,readable=None):
	if file==None:
		file=location(url)
	res=file.response;
	if readable==None:
		readable=file.readable;
	else:
		readable=True
	if name==None:
		fname=file.name
	else:
		fname=name
	file_id=file.ID;
	# print(file_id)
	if not readable:
		return False
	totsize=file.size
	output=os.path.join(ofolder,fname)
	buf=int(sz*1024)
	if fname.endswith(".xci") and trimm==True:
		end=DriveTools.get_xci_rom_size(file)
		hd={"Range" : 'bytes=%s-%s' % (0,end)}
		file.sess.headers=hd	
		file.response = file.sess.get(file.url, stream=True)	
		totsize=end
	else:
		res = file.rewind()
	print("Downloading file to {}".format(output))
	t = tqdm(total=totsize, unit='B', unit_scale=True, leave=False)	
	with open(output,"wb") as o:
		for data in res.iter_content(chunk_size=buf):
			o.write(data)
			p=file.position
			t.update(len(data));file.position=p+len(data)
			if not data:
				break	
	t.close()
	# print(output)
	return output
	
def return_remote(url):
	file=location(url)
	return file