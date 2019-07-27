#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
import io
import re
from binascii import hexlify as hx, unhexlify as uhx
from struct import pack as pk, unpack as upk

def memdump(data, length=16, message=''):
	assert data, 'Nothing to dump'
	dump = []
	first = True
	while data:
		dump.append(message + ' '.join('%02x' % data[n] for n in range(min(length, len(data)))))
		data = data[length:]
		if first:
			message = len(message) * ' '
			first = False
	return '\n'.join(dump)

def check_tkey(tkey):
	return re.match('[a-fA-F0-9]{32}', tkey)

def check_tid(tid):
	return re.match('0100[a-fA-F0-9]{12}', tid)

def read_at(fp, off, len):
	fp.seek(off)
	return fp.read(len)

def read_u8(fp, off):
	return upk('<B', read_at(fp, off, 1))[0]

def read_u16(fp, off):
	return upk('<H', read_at(fp, off, 2))[0]

def read_u32(fp, off):
	return upk('<I', read_at(fp, off, 4))[0]

def read_u48(fp, off):
	s = upk('<HI', read_at(fp, off, 6))
	return s[1] << 16 | s[0]

def read_u64(fp, off):
	return upk('<Q', read_at(fp, off, 8))[0]

def pk_u8(nb, endianness='<'):
	return pk(endianness+'B', nb)

def pk_u16(nb, endianness='<'):
	return pk(endianness+'H', nb)

def pk_u32(nb, endianness='<'):
	return pk(endianness+'I', nb)

def pk_u48(nb, endianness='<'):
	return pk_u64(nb, endianness=endianness)[:6]

def pk_u64(nb, endianness='<'):
	return pk(endianness+'Q', nb)

def pad_to(string, length=0, multiple=0, char=b'\x00'):
	if type(string) is str:
		string = string.encode()
	if length:
		if len(string) == length:
			return string
		assert len(string) < length, 'String is longer than specified length'
		return bytes(string) + (length - len(string)) * char
	elif multiple:
		if len(string) % multiple == 0:
			return string
		return bytes(string) + (multiple - (len(string) % multiple)) * char
	else:
		raise Exception('Nothing to pad string to')

def align_to(nb, alignment):
	return (nb + (alignment - 1)) & ~(alignment - 1)

def bytes2human(n, f='%(value).1f %(symbol)s'):
	n = int(n)
	assert n >= 0, 'Can\'t convert negative input to byte units'
	symbols = ('B', 'KB', 'MB', 'GB', 'TB')
	prefix = {}
	for i, s in enumerate(symbols[1:]):
		prefix[s] = 10**(3 * i) * 1000
	for symbol in reversed(symbols[1:]):
		if n >= prefix[symbol]:
			value = float(n) / prefix[symbol]
			return f % locals()
	return f % dict(symbol=symbols[0], value=n)

class FileInContainer(io.BufferedReader):
	'''Hacky class to redirect read operations to the container, instead of loading everything in memory'''	 
	def __init__(self, fp, offset_in_container, size):
		super(FileInContainer, self).__init__(fp)
		self.f = fp
		self.offset_in_cont = offset_in_container
		self.size = size
		self.seek(0) # Doesn't default there

	def seek(self, offset, whence=0):
		if whence == 0:
			self._pos = offset
			self.f.seek(self.offset_in_cont + offset)
		elif whence == 1:
			self._pos += offset
			self.f.seek(self.offset_in_cont + self._pos + offset)
		elif whence == 2:
			if offset > 0:
				offset *= -1
			self._pos = self.size + offset
			self.f.seek(self.offset_in_cont + self.size + offset, whence)

	def tell(self):
		return self._pos

	def read(self, size=None):
		if self.offset_in_cont + self._pos != self.f.tell():
			self.seek(self._pos)
		if self.tell() > self.size:
			data = b''
		elif size is None or size + self.tell() > self.size:
			data = self.f.read(self.size - self.tell())
			self._pos = self.size
		else:
			data = self.f.read(size)
			self._pos += size
		return data

	def write(self, data):
		raise NotImplementedError

	def close(self):
		# File of container is closed along with this object
		return
