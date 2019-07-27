#!/usr/bin/python3
# -*- coding: utf-8 -*-

from binascii import hexlify as hx, unhexlify as uhx
from Utils import pk_u8
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5, PKCS1_PSS

def sha256(data):
	return SHA256.new(data).digest()

def sha256_file(fp):
	hash = SHA256.new()
	fp.seek(0)
	while True:
		buf = fp.read(0x10000)
		if not buf:
			break
		hash.update(buf)
	return hash.digest()
	
def validate_rsa2048_pkcs1_sig(n, e, msg, sig):
	cipher = PKCS1_v1_5.new(RSA.RsaKey(n=n, e=e))
	digest = SHA256.new(msg) # DRM'd to use their impl
	return cipher.verify(digest, sig)

def validate_rsa2048_pss_sig(n, e, msg, sig):
	cipher = PKCS1_PSS.new(RSA.RsaKey(n=n, e=e))
	digest = SHA256.new(msg)
	return cipher.verify(digest, sig)

def sxor(s1, s2):
	assert len(s1) == len(s2), 'Strings need to be of the same size'
	return b''.join(pk_u8(x ^ y) for x, y in zip(s1, s2))

def gen_aes_kek(src, mkey, kek_seed, key_seed):
	key = AES.new(mkey, AES.MODE_ECB).decrypt(kek_seed)
	kek = AES.new(key, AES.MODE_ECB).decrypt(src)
	return AES.new(kek, AES.MODE_ECB).decrypt(key_seed)

def hex2ctr(x):
	return Counter.new(128, initial_value=int(x, 16))

def b2ctr(x):
	return hex2ctr(hx(x))

# From: https://gist.github.com/SciresM/a4b9ae50a9ae89e6119c4de9def22435
# Pure python AES128 implementation
# SciresM, 2017
# Ported to Python 3, and modded to use the pycryptodome module for AES-ECB operations
class AESXTSN:
	def __init__(self, keys, sector=0):
		if not (type(keys) is tuple and len(keys) == 2):
			raise ValueError('Key must be 32 bytes long')
		self.K1 = AES.new(keys[0], mode=AES.MODE_ECB)
		self.K2 = AES.new(keys[1], mode=AES.MODE_ECB)
		self.keys = keys
		self.sector = sector
		self.sector_size = 0x200
		self.block_size = 0x10

	def encrypt(self, data, sector=None):
		if sector is None:
			sector = self.sector
		if len(data) % self.block_size:
			raise ValueError('Data is not aligned to block size!')
		out = b''
		while data:
			tweak = self.get_tweak(sector)
			out += self.encrypt_sector(data[:self.sector_size], tweak)
			data = data[self.sector_size:]
			sector += 1
		return out

	def encrypt_sector(self, data, tweak):
		if len(data) % self.block_size:
			raise ValueError('Data is not aligned to block size!')
		out = b''
		tweak = self.K2.encrypt(uhx('%032X' % tweak))
		while data:
			out += sxor(tweak, self.K1.encrypt(sxor(data[:0x10], tweak)))
			_t = int(hx(tweak[::-1]), 16)
			_t <<= 1
			if _t & (1 << 128):
				_t ^= ((1 << 128) | (0x87))
			tweak = uhx('%032X' % _t)[::-1]
			data = data[0x10:]
		return out

	def decrypt(self, data, sector=None):
		if sector is None:
			sector = self.sector
		if len(data) % self.block_size:
			raise ValueError('Data is not aligned to block size!')
		out = b''
		while data:
			tweak = self.get_tweak(sector)
			out += self.decrypt_sector(data[:self.sector_size], tweak)
			data = data[self.sector_size:]
			sector += 1
		return out

	def decrypt_sector(self, data, tweak):
		if len(data) % self.block_size:
			raise ValueError('Data is not aligned to block size!')
		out = b''
		tweak = self.K2.encrypt(uhx('%032X' % tweak))
		while data:
			a = self.K1.decrypt(sxor(data[:0x10], tweak))
			out += sxor(tweak, a)
			_t = int(hx(tweak[::-1]), 16)
			_t <<= 1
			if _t & (1 << 128):
				_t ^= ((1 << 128) | (0x87))
			tweak = uhx('%032X' % _t)[::-1]
			data = data[0x10:]
		return out

	def get_tweak(self, sector=None):
		if sector is None:
			sector = self.sector
		tweak = 0
		for i in range(self.block_size):
			tweak |= (sector & 0xFF) << (i * 8)
			sector >>= 8
		return tweak
		