import re
import aes128
from binascii import hexlify as hx, unhexlify as uhx
import Print
from pathlib import Path
import sq_settings

keys = {}
titleKeks = []
keyAreaKeys = []


def _master_key_name(index):
	return 'master_key_%02d' % int(index)


def _parse_master_key_suffix(suffix, force_hex=False):
	# Support both legacy hex-like names (e.g. 0a) and decimal names (e.g. 10).
	suffix = suffix.strip().lower()
	if force_hex and re.fullmatch('[0-9a-f]+', suffix):
		return int(suffix, 16)
	if re.search('[a-f]', suffix):
		return int(suffix, 16)
	if len(suffix) == 2 and suffix.startswith('0'):
		return int(suffix, 16)
	return int(suffix, 10)

def getMasterKeyIndex(i):
	if i > 0:
		return i-1
	else:
		return 0

def keyAreaKey(cryptoType, i):
	if cryptoType < 0 or cryptoType >= len(keyAreaKeys):
		raise IOError('missing key area key generation %d in keys.txt' % cryptoType)
	key = keyAreaKeys[cryptoType][i]
	if key is None:
		raise IOError('missing key area key generation %d/%d in keys.txt' % (cryptoType, i))
	return key

def get(key):
	return keys[key]
	
def getTitleKek(i):
	if i < 0 or i >= len(titleKeks) or titleKeks[i] is None:
		raise IOError('missing titlekek generation %d in keys.txt' % i)
	return titleKeks[i]
	
def decryptTitleKey(key, i):
	kek = getTitleKek(i)
	
	crypto = aes128.AESECB(uhx(kek))
	return crypto.decrypt(key)
	
def encryptTitleKey(key, i):
	kek = getTitleKek(i)
	
	crypto = aes128.AESECB(uhx(kek))
	return crypto.encrypt(key)
	
def changeTitleKeyMasterKey(key, currentMasterKeyIndex, newMasterKeyIndex):
	return encryptTitleKey(decryptTitleKey(key, currentMasterKeyIndex), newMasterKeyIndex)

def generateKek(src, masterKey, kek_seed, key_seed):
	kek = []
	src_kek = []

	crypto = aes128.AESECB(masterKey)
	kek = crypto.decrypt(kek_seed)

	crypto = aes128.AESECB(kek)
	src_kek = crypto.decrypt(src)

	if key_seed != None:
		crypto = aes128.AESECB(src_kek)
		return crypto.decrypt(key_seed)
	else:
		return src_kek
		
def unwrapAesWrappedTitlekey(wrappedKey, keyGeneration):
	aes_kek_generation_source = uhx(keys['aes_kek_generation_source'])
	aes_key_generation_source = uhx(keys['aes_key_generation_source'])
	
	if keyGeneration<10:
		mk = 'master_key_0'
	else:
		mk = 'master_key_'	

	kek = generateKek(uhx(keys['key_area_key_application_source']), uhx(keys[mk + str(keyGeneration)]), aes_kek_generation_source, aes_key_generation_source)

	crypto = aes128.AESECB(kek)
	return crypto.decrypt(wrappedKey)		
	
def getKey(key):
	if key not in keys:
		raise IOError('%s missing from keys.txt' % key)
	return uhx(keys[key])

def masterKey(masterKeyIndex):
	return getKey(_master_key_name(masterKeyIndex))

def load(fileName):
	global keyAreaKeys
	global titleKeks

	entries = []
	master_suffixes = []
	with open(fileName, encoding="utf8") as f:
		for line in f.readlines():
			r = re.match(r'\s*([a-z0-9_]+)\s*=\s*([A-F0-9]+)\s*', line, re.I)
			if r:
				keyname = r.group(1)
				keyvalue = r.group(2)
				entries.append((keyname, keyvalue))
				if keyname.startswith('master_key_'):
					suffix = keyname.split('master_key_', 1)[1]
					if re.fullmatch('[0-9a-f]+', suffix, re.I):
						master_suffixes.append(suffix.lower())

	hex_series = any(re.search('[a-f]', s) for s in master_suffixes)

	for keyname, keyvalue in entries:
		if keyname.startswith('master_key_'):
			suffix = keyname.split('master_key_', 1)[1]
			if re.fullmatch('[0-9a-f]+', suffix, re.I):
				num = _parse_master_key_suffix(suffix, force_hex=hex_series)
				keyname = _master_key_name(num)
		keys[keyname] = keyvalue
		# for k in keys.keys():
			# print(k)
	
	#crypto = aes128.AESCTR(uhx(key), uhx('00000000000000000000000000000010'))
	aes_kek_generation_source = uhx(keys['aes_kek_generation_source'])
	aes_key_generation_source = uhx(keys['aes_key_generation_source'])

	master_indices = []
	for keyname in keys.keys():
		if keyname.startswith('master_key_'):
			try:
				master_indices.append(int(keyname.split('master_key_', 1)[1], 10))
			except Exception:
				pass

	max_generation = max(master_indices) if master_indices else 0

	titleKeks = [None] * (max_generation + 1)
	keyAreaKeys = [[None, None, None] for _ in range(max_generation + 1)]

	for i in range(max_generation + 1):
		masterKeyName = _master_key_name(i)
		if masterKeyName in keys.keys():
			# aes_decrypt(master_ctx, &keyset->titlekeks[i], keyset->titlekek_source, 0x10);
			masterKey = uhx(keys[masterKeyName])
			crypto = aes128.AESECB(masterKey)
			titleKeks[i] = crypto.decrypt(uhx(keys['titlekek_source'])).hex()
			keyAreaKeys[i][0] = generateKek(uhx(keys['key_area_key_application_source']), masterKey, aes_kek_generation_source, aes_key_generation_source)
			keyAreaKeys[i][1] = generateKek(uhx(keys['key_area_key_ocean_source']), masterKey, aes_kek_generation_source, aes_key_generation_source)
			keyAreaKeys[i][2] = generateKek(uhx(keys['key_area_key_system_source']), masterKey, aes_kek_generation_source, aes_key_generation_source)
		else:
			pass

if sq_settings.key_system =="production":
	raw_keys_file = Path('keys.txt')
	raw_keys_file2 = Path('ztools\\keys.txt')
	raw_keys_file3 = Path('ztools/keys.txt')
else:
	raw_keys_file = Path('dev_keys.txt')
	raw_keys_file2 = Path('ztools\\dev_keys.txt')
	raw_keys_file3 = Path('ztools/keys.txt')	
	
if raw_keys_file.is_file():
	load(raw_keys_file)
elif raw_keys_file2.is_file():
	load(raw_keys_file2)
elif raw_keys_file3.is_file():
	load(raw_keys_file3)	
	
if not raw_keys_file.is_file() and not raw_keys_file2.is_file() and not raw_keys_file3.is_file():
	print('keys.txt missing')
		
#for k in titleKeks:
#	Print.info('titleKek = ' + k)

#for k in keyAreaKeys:
#	Print.info('%s, %s, %s' % (hex(k[0]), hex(k[1]), hex(k[2])))