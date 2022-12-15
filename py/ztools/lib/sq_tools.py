import random
import os, codecs
import Hex
from binascii import hexlify as hx, unhexlify as uhx

import Keys
import re
from hashlib import sha256
from struct import pack as pk, unpack as upk
import Fs
import aes128
import sq_tools
import io
import Print
indent = 1
tabs = '\t' * indent
'''
versions =
    0:           "1.0.0",       ->   keygeneration = 0
    450:         "1.0.0",       ->   keygeneration = 0
    65536:       "2.0.0",       ->   keygeneration = 1
    131072:      "2.1.0",       ->   keygeneration = 1
    196608:      "2.2.0",       ->   keygeneration = 1
    262144:      "2.3.0",       ->   keygeneration = 1
    201326592:   "3.0.0",       ->   keygeneration = 2
    201392128:   "3.0.1",       ->   keygeneration = 3
    201457664:   "3.0.2",       ->   keygeneration = 3
    268435456:   "4.0.0",       ->   keygeneration = 4
    268500992:   "4.0.1",       ->   keygeneration = 4
    269484032:   "4.1.0",       ->   keygeneration = 4
    335544320:   "5.0.0",       ->   keygeneration = 5
    335609856:   "5.0.1",       ->   keygeneration = 5
    335675392:   "5.0.2",       ->   keygeneration = 5
    336592896:   "5.1.0",       ->   keygeneration = 5
    402653184:   "6.0.0",       ->   keygeneration = 6
    402718720:   "6.0.1",       ->   keygeneration = 6
    403701760:   "6.1.0",       ->   keygeneration = 6
	404750336:   "6.2.0"        ->   keygeneration = 7
	469762048:   "7.0.0"        ->   keygeneration = 8
	469827584:   "7.0.1"        ->   keygeneration = 8
	536870912:   "8.0.0"        ->   keygeneration = 8
	536936448:   "8.0.1"        ->   keygeneration = 8
	537919488:   "8.1.0"        ->   keygeneration = 9
	603979776:   "9.0.0"        ->   keygeneration = 10
	604045312:   "9.0.1"        ->   keygeneration = 10
	605028352:   "9.1.0"        ->   keygeneration = 11
	606076928:   "9.2.0"        ->   keygeneration = 11
	671088640:   "10.0.0"       ->   keygeneration = 11
	671154176:   "10.0.1"       ->   keygeneration = 11
	671219712:   "10.0.2"       ->   keygeneration = 11
	671285248:   "10.0.3"       ->   keygeneration = 11
	671350784:   "10.0.4"       ->   keygeneration = 11
	672137216:   "10.1.0"       ->   keygeneration = 11
	672202752:   "10.1.1"       ->   keygeneration = 11
	673185792:   "10.2.0"       ->   keygeneration = 11
	738197504:   "11.0.0"       ->   keygeneration = 11
	738263040:   "11.0.1"       ->   keygeneration = 11
	805306368:   "12.0.0"       ->   keygeneration = 11
	805371904:   "12.0.1"       ->   keygeneration = 11
	805437440:   "12.0.2"       ->   keygeneration = 11
	805502976:   "12.0.3"       ->   keygeneration = 11
	806354944:   "12.1.0"		->   keygeneration = 12
	872415232:   "13.0.0"	    ->   keygeneration = 13
	873463808:   "13.1.0"	    ->   keygeneration = 13
	874512404:   "13.2.0"	    ->   keygeneration = 13
	874578000:   "13.2.1"	    ->   keygeneration = 13
	939524096:   "14.0.0"	    ->   keygeneration = 14
	940572672:   "14.1.0"	    ->   keygeneration = 14
	940638208:   "14.1.1"	    ->   keygeneration = 14
	940703744:   "14.1.2"	    ->   keygeneration = 14
	1006632960:  "15.0.0"	    ->   keygeneration = 15
	1006698496:  "15.0.1"	    ->   keygeneration = 15
'''
def kgstring():
	kg=list()
	kg15=[1006632960,1006698496];kg.append(kg15)
	kg14=[939524096,940572672,940638208,940703744];kg.append(kg14)
	kg13=[872415232,873463808,874512404,874578000];kg.append(kg13)	
	kg12=[806354944];kg.append(kg12)
	kg11=[605028352,606076928,671088640,671154176,671219712,671285248,671350784,672137216,672202752,673185792,738197504,738263040,805306368,805371904,805437440,805502976];kg.append(kg11)
	kg10=[603979776,604045312];kg.append(kg10)
	kg9=[537919488];kg.append(kg9)
	kg8=[536936448,536870912,469827584,469762048];kg.append(kg8)
	kg7=[404750336];kg.append(kg7)
	kg6=[403701760,402718720,402653184];kg.append(kg6)
	kg5=[336592896,335675392,335609856,335544320];kg.append(kg5)
	kg4=[269484032,268500992,268435456];kg.append(kg4)
	kg3=[201457664,201392128];kg.append(kg3)
	kg2=[201326592];kg.append(kg2)
	kg1=[262144,196608,131072,65536];kg.append(kg1)
	kg0=[450,0];kg.append(kg0)
	return kg

def kg_by_RSV(RSV):
	kgs=kgstring();keygen=len(kgs)-1;topkg=len(kgs)
	for k in range(len(kgs)):
		if not RSV in kgs[k]:
			keygen-=1
		if RSV in kgs[k]:	
			break
	if keygen<0:
		return 'unknown'
	return keygen

def transform_fw_string(FW):
	FW=FW.split('-');rem=0;RRSV=0
	if len(FW)>1:
		rem=FW[1]
	else:
		rem=0
	FW=FW[0]
	FW=FW.split('.')
	RSV=0
	for i in range(len(FW)):
		n=int(FW[i])
		if i==0:
			if n>=3:
				RSV+=67108864*n
			elif n==2:
				RSV+=65536
		elif i==1 and int(FW[0])>3:
			RSV+=1048576*n
		elif i==1 and int(FW[0])==2:
			RSV+=1*n
		elif i==2 and int(FW[0])>3:
			RSV+=65536*n
			RRSV=RSV+rem
	return RSV,RRSV

def kg2masterkey(kg):
	if kg == 1:
		return 1
	else:
		return kg-1

def getTopRSV(keygeneration, RSV):
	if keygeneration == 0:
		return 450
	if keygeneration == 1:
		return 262164
	if keygeneration == 2:
		return 201327002
	if keygeneration == 3:
		return 201457684
	if keygeneration == 4:
		return 269484082
	if keygeneration == 5:
		return 336592976
	if keygeneration == 6:
		return 403701850
	if keygeneration == 7:
		return 404750376
	if keygeneration == 8:
		return 536936448
	if keygeneration == 9:
		return 537919488
	if keygeneration == 10:
		return 603979776
	if keygeneration == 11:
		return 605028352
	if keygeneration == 12:
		return 806354944		
	if keygeneration == 13:
		return 872415232
	if keygeneration == 14:
		return 939524096
	if keygeneration == 15:
		return 1006632960			
	else:
		return RSV

def getMinRSV(keygeneration, RSV):
	if keygeneration == 0:
		return 0
	if keygeneration == 1:
		return 65796
	if keygeneration == 2:
		RSV=3*67108864
		return RSV
	if keygeneration == 3:
		RSV=3*67108864+1*65536
		return RSV
	if keygeneration == 4:
		RSV=4*67108864
		return RSV
	if keygeneration == 5:
		RSV=5*67108864
		return RSV
	if keygeneration == 6:
		RSV=6*67108864
		return RSV
	if keygeneration == 7:
		RSV=6*67108864+2*1048576
		return RSV
	if keygeneration == 8:
		RSV=7*67108864
		return RSV
	if keygeneration == 9:
		RSV=8*67108864+1*1048576
		return RSV
	if keygeneration == 10:
		RSV=9*67108864
		return RSV
	if keygeneration == 11:
		RSV=9*67108864+1*1048576+0*65796+0*1
		return RSV
	if keygeneration == 12:
		RSV=12*67108864+1*1048576+0*65796+0*1
		return RSV
	if keygeneration == 13:
		RSV=13*67108864+0*1048576+0*65796+0*1
		return RSV
	if keygeneration == 14:
		RSV=14*67108864+0*1048576+0*65796+0*1
		return RSV
	if keygeneration == 15:
		RSV=15*67108864+0*1048576+0*65796+0*1
		return RSV
	else:
		return RSV

def getFWRangeKG(keygeneration):
	if keygeneration == 0:
		return "(1.0.0)"
	if keygeneration == 1:
		return "(2.0.0 - 2.3.0)"
	if keygeneration == 2:
		return "(3.0.0)"
	if keygeneration == 3:
		return "(3.0.1 - 3.0.2)"
	if keygeneration == 4:
		return "(4.0.0 - 4.1.0)"
	if keygeneration == 5:
		return "(5.0.0 - 5.1.0)"
	if keygeneration == 6:
		return "(6.0.0 - 6.1.0)"
	if keygeneration == 7:
		return "(6.2.0)"
	if keygeneration == 8:
		return "(7.0.0 - 8.0.1)"
	if keygeneration == 9:
		return "(8.1.0)"
	if keygeneration == 10:
		return "(9.0.0 - 9.0.1)"
	if keygeneration == 11:
		return "(9.1.0 - 12.0.3)"
	if keygeneration == 12:
		return "(12.1.0)"	
	if keygeneration == 13:
		return "(13.0.0 - 13.2.1)"	
	if keygeneration == 14:
		return "(14.0.0 - 14.1.2)"	
	if keygeneration == 15:
		return "(>= 15.0.0)"		
	else:
		return "UNKNOWN"

def getmetacontenttype(ncatypenumber):
	ncatypenumber=int(ncatypenumber)
	if ncatypenumber==0:
		return "Meta"
	elif ncatypenumber==1:
		return "Program"
	elif ncatypenumber==2:
		return "Data"
	elif ncatypenumber==3:
		return "Control"
	elif ncatypenumber==4:
		return "HtmlDocument"
	elif ncatypenumber==5:
		return "LegalInformation"
	elif ncatypenumber==6:
		return "DeltaFragment"

def getFWRangeRSV(RSV):
	if RSV >= (3*67108864):
		RSV=int(RSV)
		frst_num=str(int(RSV/67108864))
		remainder=RSV%67108864
		sec_num=str(int(remainder/1048576))
		remainder=remainder%1048576
		thd_num=str(int(remainder/65536))
		remainder=remainder%65536
		fth_num=remainder
		version=str(frst_num)
		version+='.'
		version+=str(sec_num)
		version+='.'
		version+=str(thd_num)
		if fth_num > 0:
			version+='-'
			version+=str(fth_num)
		version="("+version+")"
		return version
	elif RSV >= 65536:
		RSV=int(RSV)
		frst_num=2
		sec_num=str(int(RSV/65536))
		remainder=RSV%65536
		thd_num=0
		fth_num=remainder
		version=str(frst_num)
		version+='.'
		version+=str(sec_num)
		version+='.'
		version+=str(thd_num)
		if fth_num > 0:
			version+='-'
			version+=str(fth_num)
		version="("+version+")"
		return version
	elif RSV > 0:
		RSV=int(RSV)
		frst_num=1
		sec_num=0
		thd_num=0
		remainder=RSV%65536
		fth_num=remainder
		version=str(frst_num)
		version+='.'
		version+=str(sec_num)
		version+='.'
		version+=str(thd_num)
		if fth_num > 0:
			version+='-'
			version+=str(fth_num)
		version="("+version+")"
		return version
	elif RSV == 0:
		return "(1.0.0)"
	else:
		return "(-)"

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

def getGCsize(bytes):
	Gbytes=bytes/(1024*1024*1024)
	Gbytes=round(Gbytes,2)
	if Gbytes>=32:
		card=0xE3
		firm_ver='1000a100'
		return card,firm_ver
	if Gbytes>=16:
		card=0xE2
		firm_ver='1000a100'
		return card,firm_ver
	if Gbytes>=8:
		card=0xE1
		firm_ver='1000a100'
		return card,firm_ver
	if Gbytes>=4:
		card=0xE0
		firm_ver='1000a100'
		return card,firm_ver
	if Gbytes>=2:
		card=0xF0
		firm_ver='1100a100'
		return card,firm_ver
	if Gbytes>=1:
		card=0xF8
		firm_ver='1100a100'
		return card,firm_ver
	if Gbytes<1:
		card=0xFA
		firm_ver='1100a100'
		return card,firm_ver


def getGCsizeinbytes(GCflag):
	bytes=''
	if GCflag=='E3':
		size=64
	if GCflag=='E2':
		size=32
	if GCflag=='E1':
		size=16
	if GCflag=='E0':
		size=8
	if GCflag=='F0':
		size=4
	if GCflag=='F8':
		size=2
	if GCflag=='FA':
		size=1
	bytes=size*998244352
	return bytes

def getTypeFromCNMT(number):
	if number == 0:
		return "Meta: "
	if number == 1:
		return "Program: "
	if number == 2:
		return "Data: "
	if number == 3:
		return "Control: "
	if number == 4:
		return "HtmlDoc: "
	if number == 5:
		return "LegalInf: "
	if number == 6:
		return "Delta: "


def randhex(size):
	hexdigits = "0123456789ABCDEF"
	random_digits = "".join([ hexdigits[random.randint(0,0xF)] for _ in range(size*2) ])
	return random_digits

def get_enc_gameinfo(bytes):
	Gbytes=bytes/(1024*1024*1024)
	Gbytes=round(Gbytes,2)
	if Gbytes>=32 or Gbytes>=16 or Gbytes>=8 or Gbytes>=4:
		firm_ver= 0x9298F35088F09F7D
		access_freq= 0xa89a60d4
		Read_Wait_Time= 0xcba6f96f
		Read_Wait_Time2= 0xa45bb6ac
		Write_Wait_Time= 0xabc751f9
		Write_Wait_Time2= 0x5d398742
		Firmware_Mode = 0x6b38c3f2
		CUP_Version = 0x10da0b70
		Empty1 = 0x0e5ece29
		Upd_Hash= 0xa13cbe1da6d052cb
		CUP_Id = 0xf2087ce9af590538
		Empty2= 0x570d78b9cdd27fbeb4a0ac2adff9ba77754dd6675ac76223506b3bdabcb2e212fa465111ab7d51afc8b5b2b21c4b3f40654598620282add6
	else:
		firm_ver= 0x9109FF82971EE993
		access_freq=0x5011ca06
		Read_Wait_Time=0x3f3c4d87
		Read_Wait_Time2=0xa13d28a9
		Write_Wait_Time=0x928d74f1
		Write_Wait_Time2=0x49919eb7
		Firmware_Mode =0x82e1f0cf
		CUP_Version = 0xe4a5a3bd
		Empty1 = 0xf978295c
		Upd_Hash= 0xd52639a4991bdb1f
		CUP_Id = 0xed841779a3f85d23
		Empty2= 0xaa4242135616f5187c03cf0d97e5d218fdb245381fd1cf8dfb796fbeda4bf7f7d6b128ce89bc9eaa8552d42f597c5db866c67bb0dd8eea11

	firm_ver=firm_ver.to_bytes(8, byteorder='big')
	access_freq=access_freq.to_bytes(4, byteorder='big')
	Read_Wait_Time=Read_Wait_Time.to_bytes(4, byteorder='big')
	Read_Wait_Time2=Read_Wait_Time2.to_bytes(4, byteorder='big')
	Write_Wait_Time=Write_Wait_Time.to_bytes(4, byteorder='big')
	Write_Wait_Time2=Write_Wait_Time2.to_bytes(4, byteorder='big')
	Firmware_Mode=Firmware_Mode.to_bytes(4, byteorder='big')
	CUP_Version=CUP_Version.to_bytes(4, byteorder='big')
	Empty1=Empty1.to_bytes(4, byteorder='big')
	Upd_Hash=Upd_Hash.to_bytes(8, byteorder='big')
	CUP_Id=CUP_Id.to_bytes(8, byteorder='big')
	Empty2=Empty2.to_bytes(56, byteorder='big')

	Game_info =  b''
	Game_info += firm_ver
	Game_info += access_freq
	Game_info += Read_Wait_Time
	Game_info += Read_Wait_Time2
	Game_info += Write_Wait_Time
	Game_info += Write_Wait_Time2
	Game_info += Firmware_Mode
	Game_info += CUP_Version
	Game_info += Empty1
	Game_info += Upd_Hash
	Game_info += CUP_Id
	Game_info += Empty2

	#print(Game_info)
	return Game_info

def get_krypto_block(keygeneration):
	if keygeneration == 0:
		return 'f3cbc0052cac528adf9129210f0a02e4'
	if keygeneration == 1:
		return 'f3cbc0052cac528adf9129210f0a02e4'
	if keygeneration == 2:
		return '789800b9e78b860eec2f7862ef05545e'
	if keygeneration == 3:
		return '99776e03a21f56232d056b8683d9c681'
	if keygeneration == 4:
		return '48df2c73957fa1b73b8e33fb2d052512'
	if keygeneration == 5:
		return '91dea3589a56e4fa1ce60a444009e7d8'
	if keygeneration == 6:
		return 'cd5b0d1abcf6450f37b8a3b68a15d5e9'
	if keygeneration == 7:
		return 'e7ae8f7303809fd63cbd1f500b31d5b9'
	else:
		return "UNKNOWN"

def verify_nkeys(fileName):
	indent = 1
	tabs = '     ' * indent
	checkkeys = {}
	with open(fileName, encoding="utf8") as f:
		for line in f.readlines():
			r = re.match('\s*([a-z0-9_]+)\s*=\s*([A-F0-9]+)\s*', line, re.I)
			if r:
				checkkeys[r.group(1)] = r.group(2)
	print("")

	if 'aes_kek_generation_source' not in checkkeys:
		print("aes_kek_generation_source is Missing")
	if 'aes_key_generation_source' not in checkkeys:
		print("aes_key_generation_source is Missing")
	if 'titlekek_source' not in checkkeys:
		print("titlekek_source is Missing")
	if 'key_area_key_application_source' not in checkkeys:
		print("key_area_key_application_source is Missing")
	if 'key_area_key_ocean_source' not in checkkeys:
		print("key_area_key_ocean_source is Missing")
	if 'key_area_key_system_source' not in checkkeys:
		print("key_area_key_system_source is Missing")
	counter=0
	if 'master_key_00' not in checkkeys:
		print("master_key_00 is Missing")
	else:
		counter+=1
	if 'master_key_01' not in checkkeys:
		print("master_key_01 is Missing")
	else:
		counter+=1
	if 'master_key_02' not in checkkeys:
		print("master_key_02 is Missing")
	else:
		counter+=1
	if 'master_key_03' not in checkkeys:
		print("master_key_03 is Missing")
	else:
		counter+=1
	if 'master_key_04' not in checkkeys:
		print("master_key_04 is Missing")
	else:
		counter+=1
	if 'master_key_05' not in checkkeys:
		print("master_key_05 is Missing")
	else:
		counter+=1
	if 'master_key_06' not in checkkeys:
		print("master_key_06 is Missing")
	else:
		counter+=1
	if 'master_key_07' not in checkkeys:
		print("master_key_07 is Missing")
	else:
		counter+=1
	if 'master_key_08' not in checkkeys:
		print("master_key_08 is Missing")
	else:
		counter+=1
	if 'master_key_09' not in checkkeys:
		print("master_key_09 is Missing")
	else:
		counter+=1
	if 'master_key_10' not in checkkeys and 'master_key_0a' not in checkkeys:
		print("master_key_10|master_key_0a is Missing")
	else:
		counter+=1

	if 'header_key' not in checkkeys:
		print("header_key is Missing")
	if 'xci_header_key' not in checkkeys:
		print('OPTIONAL KEY "xci_header_key" is Missing')

	while counter<len(checkkeys):
		if len(str(counter))<2:
			mkverifier='master_key_0'+str(counter)
		else:
			mkverifier='master_key'+str(counter)
		if mkverifier in checkkeys:
			print(mkverifier+" is present but program doesn't have the hash to verify the key")
			for i in checkkeys:
				if i==mkverifier:
					mk =checkkeys[i][:]
					sha=sha256(uhx(mk)).hexdigest()
					print('  > HEX SHA256: '+sha)
					print('')
		counter+=1

	for i in checkkeys:

		if i == 'aes_kek_generation_source':
			aes_kek_generation_source =checkkeys[i][:]
			print('aes_kek_generation_source : '+aes_kek_generation_source )
			sha=sha256(uhx(aes_kek_generation_source)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == 'fc02b9d37b42d7a1452e71444f1f700311d1132e301a83b16062e72a78175085':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'aes_key_generation_source':
			aes_key_generation_source =checkkeys[i][:]
			print('aes_key_generation_source : '+aes_key_generation_source )
			sha=sha256(uhx(aes_key_generation_source)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == 'fbd10056999edc7acdb96098e47e2c3606230270d23281e671f0f389fc5bc585':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'titlekek_source':
			titlekek_source=checkkeys[i][:]
			print('titlekek_source: '+titlekek_source)
			sha=sha256(uhx(titlekek_source)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == 'c48b619827986c7f4e3081d59db2b460c84312650e9a8e6b458e53e8cbca4e87':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'key_area_key_application_source':
			key_area_key_application_source=checkkeys[i][:]
			print('key_area_key_application_source: '+key_area_key_application_source)
			sha=sha256(uhx(key_area_key_application_source)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '04ad66143c726b2a139fb6b21128b46f56c553b2b3887110304298d8d0092d9e':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'key_area_key_ocean_source':
			key_area_key_ocean_source=checkkeys[i][:]
			print('key_area_key_ocean_source: '+key_area_key_ocean_source)
			sha=sha256(uhx(key_area_key_ocean_source)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == 'fd434000c8ff2b26f8e9a9d2d2c12f6be5773cbb9dc86300e1bd99f8ea33a417':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'key_area_key_system_source':
			key_area_key_system_source=checkkeys[i][:]
			print('key_area_key_system_source: '+key_area_key_system_source)
			sha=sha256(uhx(key_area_key_system_source)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '1f17b1fd51ad1c2379b58f152ca4912ec2106441e51722f38700d5937a1162f7':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_00':
			master_key_00=checkkeys[i][:]
			print('master_key_00: '+master_key_00)
			sha=sha256(uhx(master_key_00)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '0ee359be3c864bb0782e1d70a718a0342c551eed28c369754f9c4f691becf7ca':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_01':
			master_key_01=checkkeys[i][:]
			print('master_key_01: '+master_key_01)
			sha=sha256(uhx(master_key_01)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '4fe707b7e4abdaf727c894aaf13b1351bfe2ac90d875f73b2e20fa94b9cc661e':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_02':
			master_key_02=checkkeys[i][:]
			print('master_key_02: '+master_key_02)
			sha=sha256(uhx(master_key_02)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '79277c0237a2252ec3dfac1f7c359c2b3d121e9db15bb9ab4c2b4408d2f3ae09':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_03':
			master_key_03=checkkeys[i][:]
			print('master_key_03: '+master_key_03)
			sha=sha256(uhx(master_key_03)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '4f36c565d13325f65ee134073c6a578ffcb0008e02d69400836844eab7432754':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_04':
			master_key_04=checkkeys[i][:]
			print('master_key_04: '+master_key_04)
			sha=sha256(uhx(master_key_04)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '75ff1d95d26113550ee6fcc20acb58e97edeb3a2ff52543ed5aec63bdcc3da50':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_05':
			master_key_05=checkkeys[i][:]
			print('master_key_05: '+master_key_05)
			sha=sha256(uhx(master_key_05)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == 'ebe2bcd6704673ec0f88a187bb2ad9f1cc82b718c389425941bdc194dc46b0dd':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_06':
			master_key_06=checkkeys[i][:]
			print('master_key_06: '+master_key_06)
			sha=sha256(uhx(master_key_06)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '9497e6779f5d840f2bba1de4e95ba1d6f21efc94717d5ae5ca37d7ec5bd37a19':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_07':
			master_key_07=checkkeys[i][:]
			print('master_key_07: '+master_key_07)
			sha=sha256(uhx(master_key_07)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '4ec96b8cb01b8dce382149443430b2b6ebcb2983348afa04a25e53609dabedf6':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_08':
			master_key_08=checkkeys[i][:]
			print('master_key_08: '+master_key_08)
			sha=sha256(uhx(master_key_08)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '2998e2e23609bc2675ff062a2d64af5b1b78dff463b24119d64a1b64f01b2d51':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_09':
			master_key_09=checkkeys[i][:]
			print('master_key_09: '+master_key_09)
			sha=sha256(uhx(master_key_09)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '9d486a98067c44b37cf173d3bf577891eb6081ff6b4a166347d9dbbf7025076b':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'master_key_10' or i == 'master_key_0a':
			master_key_10=checkkeys[i][:]
			print('master_key_10|master_key_0a: '+master_key_10)
			sha=sha256(uhx(master_key_10)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '4ec5a237a75a083a9c5f6cf615601522a7f822d06bd4ba32612c9cebbb29bd45':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'header_key':
			header_key=checkkeys[i][:]
			print('header_key: '+header_key)
			sha=sha256(uhx(header_key)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '8e03de24818d96ce4f2a09b43af979e679974f7570713a61eed8b314864a11d5':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

		if i == 'xci_header_key':
			xci_header_key=checkkeys[i][:]
			print('xci_header_key: '+xci_header_key)
			sha=sha256(uhx(xci_header_key)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha == '2e36cc55157a351090a73e7ae77cf581f69b0b6e48fb066c984879a6ed7d2e96':
				print(tabs+'> Key is valid!!!')
			else:
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
			print('')

def verify_nkeys_startup(fileName):
	indent = 1
	tabs = '     ' * indent
	checkkeys = {}
	startup=False
	with open(fileName, encoding="utf8") as f:
		for line in f.readlines():
			r = re.match('\s*([a-z0-9_]+)\s*=\s*([A-F0-9]+)\s*', line, re.I)
			if r:
				checkkeys[r.group(1)] = r.group(2)
	print("")

	if 'aes_kek_generation_source' not in checkkeys:
		print("aes_kek_generation_source is Missing")
		print("This is a needed key!!!")
		startup=True
	if 'aes_key_generation_source' not in checkkeys:
		print("aes_key_generation_source is Missing")
		print("This is a needed key!!!")
		startup=True
	if 'titlekek_source' not in checkkeys:
		print("titlekek_source is Missing")
		print("This is a needed key!!!")
		startup=True
	if 'key_area_key_application_source' not in checkkeys:
		print("key_area_key_application_source is Missing")
		print("This is a needed key!!!")
		startup=True
	if 'key_area_key_ocean_source' not in checkkeys:
		print("key_area_key_ocean_source is Missing")
		print("This is a needed key!!!")
		startup=True
	if 'key_area_key_system_source' not in checkkeys:
		print("key_area_key_system_source is Missing")
		print("This is a needed key!!!")
		startup=True
	counter=0
	if 'master_key_00' not in checkkeys:
		print("master_key_00 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 1.0.0-2.3.0 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_01' not in checkkeys:
		print("master_key_01 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 3.0.0 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_02' not in checkkeys:
		print("master_key_02 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 3.0.1-3.0.2 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_03' not in checkkeys:
		print("master_key_03 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 4.0.0-4.0.1 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_04' not in checkkeys:
		print("master_key_04 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 5.0.0-5.1.0 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_05' not in checkkeys:
		print("master_key_05 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 6.0.0-6.1.0 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_06' not in checkkeys:
		print("master_key_06 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 6.2.0 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_07' not in checkkeys:
		print("master_key_07 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 7.0.0-8.0.1 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_08' not in checkkeys:
		print("master_key_08 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 8.1 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_09' not in checkkeys:
		print("master_key_09 is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 9.0 requirement")
		startup=True
	else:
		counter+=1
	if 'master_key_10' not in checkkeys and 'master_key_0a' not in checkkeys:
		print("master_key_10|master_key_0a is Missing!!!")
		print("The program won't be able to decrypt games content that uses this key")
		print("This key represents FW 9.1-10.04 requirement")
		startup=True
	else:
		counter+=1

	if 'header_key' not in checkkeys:
		print("header_key is Missing")
	if 'xci_header_key' not in checkkeys:
		print('OPTIONAL KEY "xci_header_key" is Missing')

	while counter<len(checkkeys):
		if len(str(counter))<2:
			mkverifier='master_key_0'+str(counter)
		else:
			mkverifier='master_key'+str(counter)
		if mkverifier in checkkeys:
			print(mkverifier+" is present but program doesn't have the hash to verify the key")
			for i in checkkeys:
				if i==mkverifier:
					mk =checkkeys[i][:]
					sha=sha256(uhx(mk)).hexdigest()
					print('  > HEX SHA256: '+sha)
					print('')
		counter+=1

	for i in checkkeys:

		if i == 'aes_kek_generation_source':
			aes_kek_generation_source =checkkeys[i][:]
			sha=sha256(uhx(aes_kek_generation_source)).hexdigest()
			if sha != 'fc02b9d37b42d7a1452e71444f1f700311d1132e301a83b16062e72a78175085':
				print('aes_kek_generation_source : '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'aes_key_generation_source':
			aes_key_generation_source =checkkeys[i][:]
			sha=sha256(uhx(aes_key_generation_source)).hexdigest()
			if sha != 'fbd10056999edc7acdb96098e47e2c3606230270d23281e671f0f389fc5bc585':
				print('aes_key_generation_source : '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'titlekek_source':
			titlekek_source=checkkeys[i][:]
			sha=sha256(uhx(titlekek_source)).hexdigest()
			if sha != 'c48b619827986c7f4e3081d59db2b460c84312650e9a8e6b458e53e8cbca4e87':
				print('titlekek_source : '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'key_area_key_application_source':
			key_area_key_application_source=checkkeys[i][:]
			sha=sha256(uhx(key_area_key_application_source)).hexdigest()
			if sha != '04ad66143c726b2a139fb6b21128b46f56c553b2b3887110304298d8d0092d9e':
				print('key_area_key_application_source: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'key_area_key_ocean_source':
			key_area_key_ocean_source=checkkeys[i][:]
			sha=sha256(uhx(key_area_key_ocean_source)).hexdigest()
			if sha != 'fd434000c8ff2b26f8e9a9d2d2c12f6be5773cbb9dc86300e1bd99f8ea33a417':
				print('key_area_key_ocean_source: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'key_area_key_system_source':
			key_area_key_system_source=checkkeys[i][:]
			sha=sha256(uhx(key_area_key_system_source)).hexdigest()
			if sha != '1f17b1fd51ad1c2379b58f152ca4912ec2106441e51722f38700d5937a1162f7':
				print('key_area_key_system_source: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_00':
			master_key_00=checkkeys[i][:]
			sha=sha256(uhx(master_key_00)).hexdigest()
			if sha != '0ee359be3c864bb0782e1d70a718a0342c551eed28c369754f9c4f691becf7ca':
				print('master_key_00: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_01':
			master_key_01=checkkeys[i][:]
			sha=sha256(uhx(master_key_01)).hexdigest()
			if sha != '4fe707b7e4abdaf727c894aaf13b1351bfe2ac90d875f73b2e20fa94b9cc661e':
				print('master_key_01: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_02':
			master_key_02=checkkeys[i][:]
			sha=sha256(uhx(master_key_02)).hexdigest()
			if sha != '79277c0237a2252ec3dfac1f7c359c2b3d121e9db15bb9ab4c2b4408d2f3ae09':
				print('master_key_02: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_03':
			master_key_03=checkkeys[i][:]
			sha=sha256(uhx(master_key_03)).hexdigest()
			if sha != '4f36c565d13325f65ee134073c6a578ffcb0008e02d69400836844eab7432754':
				print('master_key_03: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_04':
			master_key_04=checkkeys[i][:]
			sha=sha256(uhx(master_key_04)).hexdigest()
			if sha != '75ff1d95d26113550ee6fcc20acb58e97edeb3a2ff52543ed5aec63bdcc3da50':
				print('master_key_04: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_05':
			master_key_05=checkkeys[i][:]
			sha=sha256(uhx(master_key_05)).hexdigest()
			if sha != 'ebe2bcd6704673ec0f88a187bb2ad9f1cc82b718c389425941bdc194dc46b0dd':
				print('master_key_05: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_06':
			master_key_06=checkkeys[i][:]
			print('master_key_06: '+master_key_06)
			sha=sha256(uhx(master_key_06)).hexdigest()
			print('  > HEX SHA256: '+sha)
			if sha != '9497e6779f5d840f2bba1de4e95ba1d6f21efc94717d5ae5ca37d7ec5bd37a19':
				print('master_key_06: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_07':
			master_key_07=checkkeys[i][:]
			sha=sha256(uhx(master_key_07)).hexdigest()
			if sha != '4ec96b8cb01b8dce382149443430b2b6ebcb2983348afa04a25e53609dabedf6':
				print('master_key_07: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_08':
			master_key_08=checkkeys[i][:]
			sha=sha256(uhx(master_key_08)).hexdigest()
			if sha != '2998e2e23609bc2675ff062a2d64af5b1b78dff463b24119d64a1b64f01b2d51':
				print('master_key_08: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'master_key_09':
			master_key_09=checkkeys[i][:]
			sha=sha256(uhx(master_key_09)).hexdigest()
			if sha != '9d486a98067c44b37cf173d3bf577891eb6081ff6b4a166347d9dbbf7025076b':
				print('master_key_09: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if (i == 'master_key_10' or i=='master_key_0a'):
			master_key_10=checkkeys[i][:]
			sha=sha256(uhx(master_key_10)).hexdigest()
			if sha != '4ec5a237a75a083a9c5f6cf615601522a7f822d06bd4ba32612c9cebbb29bd45':
				print('master_key_10|master_key_0a: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'header_key':
			header_key=checkkeys[i][:]
			sha=sha256(uhx(header_key)).hexdigest()
			if sha != '8e03de24818d96ce4f2a09b43af979e679974f7570713a61eed8b314864a11d5':
				print('header_key: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

		if i == 'xci_header_key':
			xci_header_key=checkkeys[i][:]
			sha=sha256(uhx(xci_header_key)).hexdigest()
			if sha != '2e36cc55157a351090a73e7ae77cf581f69b0b6e48fb066c984879a6ed7d2e96':
				print('xci_header_key: '+aes_kek_generation_source )
				print('  > HEX SHA256: '+sha)
				print(tabs+'> Key is invalid!!! -> PLEASE CHECK YOUR KEYS.TXT!!!')
				startup=True
			print('')

	return startup


def gen_nsp_header(files,fileSizes):
	'''
	for i in range(len(files)):
		print (files[i])
		print (fileSizes[i])
	'''
	filesNb = len(files)
	stringTable = '\x00'.join(str(nca) for nca in files)
	headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
	remainder = 0x10 - headerSize%0x10
	headerSize += remainder
	fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
	fileNamesLengths = [len(str(nca))+1 for nca in files] # +1 for the \x00
	stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]

	header =  b''
	header += b'PFS0'
	header += pk('<I', filesNb)
	header += pk('<I', len(stringTable)+remainder)
	header += b'\x00\x00\x00\x00'
	for n in range(filesNb):
		header += pk('<Q', fileOffsets[n])
		header += pk('<Q', fileSizes[n])
		header += pk('<I', stringTableOffsets[n])
		header += b'\x00\x00\x00\x00'
	header += stringTable.encode()
	header += remainder * b'\x00'

	return header


def get_xciheader(oflist,osizelist,sec_hashlist):
	upd_list=list()
	upd_fileSizes = list()
	norm_list=list()
	norm_fileSizes = list()
	sec_list=oflist
	sec_fileSizes = osizelist
	sec_shalist = sec_hashlist

	hfs0 = Fs.Hfs0(None, None)
	root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=hfs0.gen_rhfs0_head(upd_list,norm_list,sec_list,sec_fileSizes,sec_shalist)
	#print (hx(root_header))
	tot_size=0xF000+rootSize

	signature=sq_tools.randhex(0x100)
	signature= bytes.fromhex(signature)

	sec_offset=root_header[0x90:0x90+0x8]
	sec_offset=int.from_bytes(sec_offset, byteorder='little')
	sec_offset=int((sec_offset+0xF000+0x200)/0x200)
	sec_offset=sec_offset.to_bytes(4, byteorder='little')
	back_offset=(0xFFFFFFFF).to_bytes(4, byteorder='little')
	kek=(0x00).to_bytes(1, byteorder='big')
	cardsize,access_freq=sq_tools.getGCsize(tot_size)
	cardsize=cardsize.to_bytes(1, byteorder='big')
	GC_ver=(0x00).to_bytes(1, byteorder='big')
	GC_flag=(0x00).to_bytes(1, byteorder='big')
	pack_id=(0x8750F4C0A9C5A966).to_bytes(8, byteorder='big')
	valid_data=int(((tot_size-0x1)/0x200))
	valid_data=valid_data.to_bytes(8, byteorder='little')

	try:
		Keys.get('xci_header_key')
		key= Keys.get('xci_header_key')
		key= bytes.fromhex(key)
		IV=sq_tools.randhex(0x10)
		IV= bytes.fromhex(IV)
		xkey=True
		#print(hx(IV))

	except:
		IV=(0x5B408B145E277E81E5BF677C94888D7B).to_bytes(16, byteorder='big')
		xkey=False


	HFS0_offset=(0xF000).to_bytes(8, byteorder='little')
	len_rHFS0=(len(root_header)).to_bytes(8, byteorder='little')
	sha_rheader=sha256(root_header[0x00:0x200]).hexdigest()
	sha_rheader=bytes.fromhex(sha_rheader)
	sha_ini_data=bytes.fromhex('1AB7C7B263E74E44CD3C68E40F7EF4A4D6571551D043FCA8ECF5C489F2C66E7E')
	SM_flag=(0x01).to_bytes(4, byteorder='little')
	TK_flag=(0x02).to_bytes(4, byteorder='little')
	K_flag=(0x0).to_bytes(4, byteorder='little')
	end_norm = sec_offset

	header =  b''
	header += signature
	header += b'HEAD'
	header += sec_offset
	header += back_offset
	header += kek
	header += cardsize
	header += GC_ver
	header += GC_flag
	header += pack_id
	header += valid_data
	header += IV
	header += HFS0_offset
	header += len_rHFS0
	header += sha_rheader
	header += sha_ini_data
	header += SM_flag
	header += TK_flag
	header += K_flag
	header += end_norm

	#Game_info
	if xkey==True:
		firm_ver='0100000000000000'
		access_freq=access_freq
		Read_Wait_Time='88130000'
		Read_Wait_Time2='00000000'
		Write_Wait_Time='00000000'
		Write_Wait_Time2='00000000'
		Firmware_Mode='00110C00'
		CUP_Version='5a000200'
		Empty1='00000000'
		Upd_Hash='9bfb03ddbb7c5fca'
		CUP_Id='1608000000000001'
		Empty2='00'*0x38
		#print(hx(Empty2))

		firm_ver=bytes.fromhex(firm_ver)
		access_freq=bytes.fromhex(access_freq)
		Read_Wait_Time=bytes.fromhex(Read_Wait_Time)
		Read_Wait_Time2=bytes.fromhex(Read_Wait_Time2)
		Write_Wait_Time=bytes.fromhex(Write_Wait_Time)
		Write_Wait_Time2=bytes.fromhex(Write_Wait_Time2)
		Firmware_Mode=bytes.fromhex(Firmware_Mode)
		CUP_Version=bytes.fromhex(CUP_Version)
		Empty1=bytes.fromhex(Empty1)
		Upd_Hash=bytes.fromhex(Upd_Hash)
		CUP_Id=bytes.fromhex(CUP_Id)
		Empty2=bytes.fromhex(Empty2)

		Game_info =  b''
		Game_info += firm_ver
		Game_info += access_freq
		Game_info += Read_Wait_Time
		Game_info += Read_Wait_Time2
		Game_info += Write_Wait_Time
		Game_info += Write_Wait_Time2
		Game_info += Firmware_Mode
		Game_info += CUP_Version
		Game_info += Empty1
		Game_info += Upd_Hash
		Game_info += CUP_Id
		Game_info += Empty2

		gamecardInfoIV=IV[::-1]
		crypto = aes128.AESCBC(key, gamecardInfoIV)
		enc_info=crypto.encrypt(Game_info)
	if xkey==False:
		enc_info=sq_tools.get_enc_gameinfo(tot_size)

	#print (hx(enc_info))

	#Padding
	sig_padding='00'*0x6E00
	sig_padding=bytes.fromhex(sig_padding)
	#print (hx(sig_padding))

	#CERT
	fake_CERT='FF'*0x8000
	fake_CERT=bytes.fromhex(fake_CERT)
	#print (hx(fake_CERT))


	return header,enc_info,sig_padding,fake_CERT,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier

def ret_nsp_offsets(filepath,kbsize=8):
	kbsize=int(kbsize)
	files_list=list()
	try:
		with open(filepath, 'r+b') as f:
			data=f.read(int(kbsize*1024))
		try:
			head=data[0:4]
			n_files=(data[4:8])
			n_files=int.from_bytes(n_files, byteorder='little')
			st_size=(data[8:12])
			st_size=int.from_bytes(st_size, byteorder='little')
			junk=(data[12:16])
			offset=(0x10 + n_files * 0x18)
			stringTable=(data[offset:offset+st_size])
			stringEndOffset = st_size
			headerSize = 0x10 + 0x18 * n_files + st_size
			#print(head)
			#print(str(n_files))
			#print(str(st_size))
			#print(str((stringTable)))
			for i in range(n_files):
				i = n_files - i - 1
				pos=0x10 + i * 0x18
				offset = data[pos:pos+8]
				offset=int.from_bytes(offset, byteorder='little')
				size = data[pos+8:pos+16]
				size=int.from_bytes(size, byteorder='little')
				nameOffset = data[pos+16:pos+20] # just the offset
				nameOffset=int.from_bytes(nameOffset, byteorder='little')
				name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
				stringEndOffset = nameOffset
				junk2 = data[pos+20:pos+24] # junk data
				#print(name)
				#print(offset)
				#print(size)
				off1=offset+headerSize
				off2=off1+size
				files_list.append([name,off1,off2,size])
			files_list.reverse()
			#print(files_list)
		except BaseException as e:
			Print.error('Exception: ' + str(e))
		#print(files_list)
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	return	files_list
	
def update_tik_and_cert(filepath,old_tk_name,new_tk_name,kbsize=8):
	old_cert_name=old_tk_name.replace('.tik','.cert')
	new_cert_name=new_tk_name.replace('.tik','.cert')	
	files=[];fileOffsets=[];fileSizes=[]
	kbsize=int(kbsize)
	try:
		with open(filepath, 'r+b') as f:
			data=f.read(int(kbsize*1024))
		try:
			head=data[0:4]
			n_files=(data[4:8])
			n_files=int.from_bytes(n_files, byteorder='little')
			st_size=(data[8:12])
			st_size=int.from_bytes(st_size, byteorder='little')
			junk=(data[12:16])
			offset=(0x10 + n_files * 0x18)
			stringTable=(data[offset:offset+st_size])
			stringEndOffset = st_size
			headerSize = 0x10 + 0x18 * n_files + st_size
			for i in range(n_files):
				i = n_files - i - 1
				pos=0x10 + i * 0x18
				offset = data[pos:pos+8]
				offset=int.from_bytes(offset, byteorder='little')
				size = data[pos+8:pos+16]
				size=int.from_bytes(size, byteorder='little')
				nameOffset = data[pos+16:pos+20] # just the offset
				nameOffset=int.from_bytes(nameOffset, byteorder='little')
				name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
				stringEndOffset = nameOffset
				junk2 = data[pos+20:pos+24] # junk data
				if name==old_tk_name:
					files.append(new_tk_name)
				elif name==old_cert_name:
					files.append(new_cert_name)
				else:
					files.append(name)
				fileOffsets.append(offset)
				fileSizes.append(size)
			files.reverse()
			fileOffsets.reverse()
			fileSizes.reverse()
		except BaseException as e:
			Print.error('Exception: ' + str(e))
	except BaseException as e:
		Print.error('Exception: ' + str(e))	
	filesNb = len(files)
	stringTable = '\x00'.join(str(nca) for nca in files)
	remainder = 0x10 - headerSize%0x10
	fileNamesLengths = [len(str(nca))+1 for nca in files] # +1 for the \x00
	stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
	header =  b''
	header += b'PFS0'
	header += pk('<I', filesNb)
	header += pk('<I', st_size)
	header += b'\x00\x00\x00\x00'
	for n in range(filesNb):
		header += pk('<Q', fileOffsets[n])
		header += pk('<Q', fileSizes[n])
		header += pk('<I', stringTableOffsets[n])
		header += b'\x00\x00\x00\x00'
	header += stringTable.encode()	
	with open(filepath, 'r+b') as f:	
		f.seek(0)
		f.write(header)	

def ret_xci_offsets(filepath,kbsize=8):
	kbsize=int(kbsize)
	files_list=list()
	try:
		with open(filepath, 'r+b') as f:
			rawhead = io.BytesIO(f.read(int(0x200)))
			data=rawhead.read()
			#print(hx(data))
		try:
			rawhead.seek(0x100)
			magic=rawhead.read(0x4)
			if magic==b'HEAD':
				#print(magic)
				secureOffset=int.from_bytes(rawhead.read(4), byteorder='little')
				secureOffset=secureOffset*0x200
				with open(filepath, 'r+b') as f:
					f.seek(secureOffset)
					data=f.read(int(kbsize*1024))
					rawhead = io.BytesIO(data)
				rmagic=rawhead.read(0x4)
				if rmagic==b'HFS0':
					#print(rmagic)
					head=data[0:4]
					n_files=(data[4:8])
					n_files=int.from_bytes(n_files, byteorder='little')
					st_size=(data[8:12])
					st_size=int.from_bytes(st_size, byteorder='little')
					junk=(data[12:16])
					offset=(0x10 + n_files * 0x40)
					stringTable=(data[offset:offset+st_size])
					stringEndOffset = st_size
					headerSize = 0x10 + 0x40 * n_files + st_size
					#print(head)
					#print(str(n_files))
					#print(str(st_size))
					#print(str((stringTable)))
					for i in range(n_files):
						i = n_files - i - 1
						pos=0x10 + i * 0x40
						offset = data[pos:pos+8]
						offset=int.from_bytes(offset, byteorder='little')
						size = data[pos+8:pos+16]
						size=int.from_bytes(size, byteorder='little')
						nameOffset = data[pos+16:pos+20] # just the offset
						nameOffset=int.from_bytes(nameOffset, byteorder='little')
						name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
						stringEndOffset = nameOffset
						junk2 = data[pos+20:pos+24] # junk data
						#print(name)
						#print(offset)
						#print(size)
						off1=offset+headerSize+secureOffset
						off2=off1+size
						files_list.append([name,off1,off2,size])
						# with open(filename, 'r+b') as f:
							# f.seek(off1)
							# print(f.read(0x4))
					files_list.reverse()
					#print(files_list)
		except BaseException as e:
			Print.error('Exception: ' + str(e))
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	return files_list

def ret_xci_offsets_fw(filepath,partition='update',kbsize=32):
	kbsize=int(kbsize)
	files_list=list()
	try:
		with open(filepath, 'r+b') as f:
			rawhead = io.BytesIO(f.read(int(0x200)))
			data=rawhead.read()
			#print(hx(data))
		try:
			rawhead.seek(0x100)
			magic=rawhead.read(0x4)
			if magic==b'HEAD':
				#print(magic)
				HFS0_offset=0xF000
				with open(filepath, 'r+b') as f:
					f.seek(HFS0_offset)
					data=f.read(int(8*1024))
					rawhead = io.BytesIO(data)
				rmagic=rawhead.read(0x4)
				if rmagic==b'HFS0':
					#print(rmagic)
					head=data[0:4]
					n_files=(data[4:8])
					n_files=int.from_bytes(n_files, byteorder='little')
					st_size=(data[8:12])
					st_size=int.from_bytes(st_size, byteorder='little')
					junk=(data[12:16])
					offset=(0x10 + n_files * 0x40)
					stringTable=(data[offset:offset+st_size])
					stringEndOffset = st_size
					headerSize = 0x10 + 0x40 * n_files + st_size
					# print(head)
					# print(str(n_files))
					# print(str(st_size))
					# print(str((stringTable)))
					for i in range(n_files):
						i = n_files - i - 1
						pos=0x10 + i * 0x40
						offset = data[pos:pos+8]
						offset=int.from_bytes(offset, byteorder='little')
						size = data[pos+8:pos+16]
						size=int.from_bytes(size, byteorder='little')
						nameOffset = data[pos+16:pos+20] # just the offset
						nameOffset=int.from_bytes(nameOffset, byteorder='little')
						name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
						stringEndOffset = nameOffset
						junk2 = data[pos+20:pos+24] # junk data
						#print(name)
						#print(offset)
						#print(size)
						off1=offset+headerSize+HFS0_offset
						off2=off1+size
						files_list.append([name,off1,off2,size])
						# with open(filename, 'r+b') as f:
							# f.seek(off1)
							# print(f.read(0x4))
					files_list.reverse()
					# print(files_list)
					updoffset=False
					for file in files_list:
						if file[0]==str(partition).lower():
							updoffset=file[1]
							break
					files_list=list()
					if updoffset!=False:
						with open(filepath, 'r+b') as f:
							f.seek(updoffset)
							data=f.read(int(kbsize*1024))
							rawhead = io.BytesIO(data)
						a=rawhead.read()
						# Hex.dump(a)
						rawhead.seek(0)
						rmagic=rawhead.read(0x4)
						if rmagic==b'HFS0':
							#print(rmagic)
							head=data[0:4]
							n_files=(data[4:8])
							n_files=int.from_bytes(n_files, byteorder='little')
							st_size=(data[8:12])
							st_size=int.from_bytes(st_size, byteorder='little')
							junk=(data[12:16])
							offset=(0x10 + n_files * 0x40)
							stringTable=(data[offset:offset+st_size])
							stringEndOffset = st_size
							headerSize = 0x10 + 0x40 * n_files + st_size
							# print(head)
							# print(str(n_files))
							# print(str(st_size))
							# print(str((stringTable)))
							for i in range(n_files):
								i = n_files - i - 1
								pos=0x10 + i * 0x40
								offset = data[pos:pos+8]
								offset=int.from_bytes(offset, byteorder='little')
								size = data[pos+8:pos+16]
								size=int.from_bytes(size, byteorder='little')
								nameOffset = data[pos+16:pos+20] # just the offset
								nameOffset=int.from_bytes(nameOffset, byteorder='little')
								name = stringTable[nameOffset:stringEndOffset].decode('utf-8').rstrip(' \t\r\n\0')
								stringEndOffset = nameOffset
								junk2 = data[pos+20:pos+24] # junk data
								#print(name)
								#print(offset)
								#print(size)
								off1=offset+headerSize+HFS0_offset
								off2=off1+size
								files_list.append([name,off1,off2,size])
								# with open(filename, 'r+b') as f:
									# f.seek(off1)
									# print(f.read(0x4))
							files_list.reverse()
							# print(files_list)
		except BaseException as e:
			Print.error('Exception: ' + str(e))
	except BaseException as e:
		Print.error('Exception: ' + str(e))
	return files_list

def count_content(filepath,filelist=None):
	counter=0
	if files_list==None:
		if filepath.endswith('.nsp')or filepath.endswith('.nsx') or filepath.endswith('.nsz') or filepath.endswith('.ns0'):
			files_list=ret_nsp_offsets(filepath)
		elif filepath.endswith('.xci') or filepath.endswith('.xcz') or filepath.endswith('.xc0'):
			files_list=ret_xci_offsets(filepath)
	for i in range(len(files_list)):
		entry=files_list[i]
		if str(entry[0]).endswith('cnmt.nca'):
			counter+=1
	return counter

def trimm_module_id(moduleid):
	moduleid=str(moduleid)
	while moduleid[-2:]=='00':
		moduleid=moduleid[:-2]
	return moduleid

def get_mc_isize(filepath=None,files_list=None):
	counter=0;size=0
	if files_list==None:
		files_list=[]
		if filepath.endswith('.nsp')or filepath.endswith('.nsx') or filepath.endswith('.nsz') or filepath.endswith('.ns0'):
			files_list=ret_nsp_offsets(filepath)
		elif filepath.endswith('.xci') or filepath.endswith('.xcz') or filepath.endswith('.xc0'):
			files_list=ret_xci_offsets(filepath)
	if files_list!=None:
		for i in range(len(files_list)):
			entry=files_list[i]
			size+=int(entry[3])
	return size

def cnmt_type(type_n):
	if str(hx(type_n)) == "b'1'":
		ctype='SystemProgram'
	if str(hx(type_n)) == "b'2'":
		ctype='SystemData'
	if str(hx(type_n)) == "b'3'":
		ctype='SystemUpdate'
	if str(hx(type_n)) == "b'4'":
		ctype='BootImagePackage'
	if str(hx(type_n)) == "b'5'":
		ctype='BootImagePackageSafe'
	if str(hx(type_n)) == "b'80'":
		ctype='GAME'
	if str(hx(type_n)) == "b'81'":
		ctype='UPDATE'
	if str(hx(type_n)) == "b'82'":
		ctype='DLC'
	if str(hx(type_n)) == "b'83'":
		ctype='Delta'
	return ctype

def file_real_size(filepath):
	if filepath.endswith('.nsp')or filepath.endswith('.nsx') or filepath.endswith('.nsz'):
		files_list=ret_nsp_offsets(filepath)
	elif filepath.endswith('.xci') or filepath.endswith('.xcz'):
		files_list=ret_xci_offsets(filepath)
	last_file=files_list[-1]
	realsize=last_file[2]
	return realsize

def check_if_trimmed(filepath):
	realsize=file_real_size(filepath)
	size=os.path.getsize(filepath)
	if size==realsize:
		return True,realsize
	else:
		return False,realsize

def check_if_foot_signed(filepath,realsize,cryptokey=None):
	with open(filepath, 'rb') as o:
		o.seek(realsize)
		if o.read(6)==b'FOOTER':
			return True
		else:
			return False

def add_signed_footer(filepath,message=None,rewrite=False,encrypted=None,cryptokey=None):
	result,realsize=check_if_trimmed(filepath)
	if result==False and rewrite==False:
		result2=check_if_foot_signed(filepath,realsize)
		if result2==True:
			print(filepath+' is already signed')
			return True
	if message==None:
		message='Made with NSCB'
	if encrypted==None:
		crypto=(0x0).to_bytes(4, byteorder='little')
	else:
		crypto=(0x1).to_bytes(4, byteorder='little')
	mss=message.encode(encoding='UTF-8')
	footer =  b''
	footer += b'FOOTER'
	footer += crypto
	footer += (len(mss)).to_bytes(4, byteorder='little')
	footer += mss
	with open(filepath, 'rb+') as o:
		o.seek(realsize)
		o.write(footer)
		o.seek(0, os.SEEK_END)
		curr_off= o.tell()
		remainder=curr_off%0x10
		if remainder!=0:
			while remainder!=0:
				padd = b''
				padd += (0x00).to_bytes(1, byteorder='little')
				o.write(padd)
				o.seek(0, os.SEEK_END)
				curr_off= o.tell()
				remainder=curr_off%0x10
		print('Added message: "{}" to {}'.format(message,filepath))

def read_footer(filepath,cryptokey=None):
	result,realsize=check_if_trimmed(filepath)
	if result==True:
		print(filepath+" doesn't have a footer")
	else:
		with open(filepath, 'rb') as o:
			o.seek(realsize)
			if o.read(0x6)==b'FOOTER':
				crypto=o.read(0x4)
				footsize=int.from_bytes(o.read(0x4), byteorder='little', signed=False)
				print(filepath)
				print(' -> '+((o.read(footsize)).decode(encoding='UTF-8')))
			else:
				print(filepath)
				print(" -> doesn't have a footer")

def delete_footer(filepath,cryptokey=None):
	result,realsize=check_if_trimmed(filepath)
	if result==True:
		print(filepath+" doesn't have a footer")
	else:
		with open(filepath, 'rb+') as o:
			o.seek(realsize)
			if o.read(0x6)==b'FOOTER':
				o.seek(realsize)
				o.truncate()
				print("Footer has been deleted from "+filepath)
			else:
				print(filepath+" doesn't have a footer")

def decompress_zip(filepath,ofolder,delete_after=False):
	import zipfile
	if not os.path.isdir(filepath):
		with zipfile.ZipFile(filepath, 'r') as zipf:
			zipf.extractall(ofolder)
		if delete_after==True:
			try:
				os.remove(filepath)
			except:pass
	else:
		from listmanager import folder_to_list
		file_list=folder_to_list(filepath,['zip'])
		for filepath in file_list:
			with zipfile.ZipFile(filepath, 'r') as zipf:
				zipf.extractall(ofolder)
			if delete_after==True:
				try:
					os.remove(filepath)
				except:pass
