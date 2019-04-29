'''
   _____             _                __
  / ___/____ ___  __(_)____________  / /
  \__ \/ __ `/ / / / / ___/ ___/ _ \/ / 
 ___/ / /_/ / /_/ / / /  / /  /  __/ /  
/____/\__, /\__,_/_/_/  /_/   \___/_/   
        /_/                             

By julesontheroad:
https://github.com/julesontheroad/
Squirrel is a fork of NUT made to support NSC Builder		
https://github.com/julesontheroad/NSC_BUILDER		

The original NUT is made and actively supported by blawar
https://github.com/blawar/nut

This fork doesn't follow NUT's main line and strips many features from nut
(like CDNSP support) while adds several functions based in new code.
This program specialices in content building and file management for several
Nintendo Switch formats.

Squirrel original's purpose is to support NSC_Builder though it serves as a 
standalone program with many functions, some of them not being used currently in NSC_Builder.						
'''		

# -*- coding: utf-8 -*-
import argparse
import sys
import os
import re
import pathlib
import urllib3
import json
from zipfile import ZipFile

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'lib')
import sq_tools
import Keys
import Titles
import Fs
import Config
import Print
import Status
import Nsps
from hashlib import sha256
from pathlib import Path
from binascii import hexlify as hx, unhexlify as uhx

if sys.platform == 'win32':
	import win32con, win32api
import shutil
from tqdm import tqdm
from datetime import datetime
import math  


if __name__ == '__main__':
	try:
		urllib3.disable_warnings()
		parser = argparse.ArgumentParser()
		parser.add_argument('file',nargs='*')
		
		# INFORMATION
		parser.add_argument('-i', '--info', help='show info about title or file')
		parser.add_argument('--filelist', nargs='+', help='Prints file list from NSP\XCI secure partition')
		parser.add_argument('--ADVfilelist', nargs='+', help='Prints ADVANCED file list from NSP\XCI secure partition')		
		parser.add_argument('--ADVcontentlist', nargs='+', help='Prints ADVANCED content list from NSP\XCI arranged by base titleid')			
		parser.add_argument('--Read_cnmt', nargs='+', help='Read cnmt file inside NSP\XCI')
		parser.add_argument('--Read_hfs0', nargs='+', help='Read hfs0')		
		parser.add_argument('--fw_req', nargs='+', help='Get information about fw requirements for NSP\XCI')		
		parser.add_argument('--Read_xci_head', nargs='+', help='Get information about xci header and cert')				
		parser.add_argument('-nscdb', '--addtodb', nargs='+', help='Adds content to database')	

		# CNMT Flag funtions		
		parser.add_argument('--set_cnmt_version', nargs='+', help='Changes cnmt.nca version number')	
		parser.add_argument('--set_cnmt_RSV', nargs='+', help='Changes cnmt.nca RSV')	
		parser.add_argument('--update_hash', nargs='+', help='Updates cnmt.nca hashes')	
		parser.add_argument('--xml_gen', nargs='+', help='Generates cnmt.xml')				
		
		# REPACK
		parser.add_argument('-c', '--create', help='create / pack a NSP')
		parser.add_argument('--create_hfs0', help='create / pack a hfs0')
		parser.add_argument('--create_rhfs0', help='create / pack a root hfs0')		
		parser.add_argument('--create_xci', help='create / pack a xci')		
		parser.add_argument('--xci_super_trim', nargs='+', help='Supertrim xci')	
		parser.add_argument('-dc', '--direct_creation', nargs='+', help='Create directly a nsp or xci')		
		parser.add_argument('-dmul', '--direct_multi', nargs='+', help='Create directly a multi nsp or xci')		
		parser.add_argument('-ed', '--erase_deltas', nargs='+', help='Take of deltas from updates')			
	
		# nca/nsp identification
		parser.add_argument('--ncatitleid', nargs='+', help='Returns titleid from a nca input')
		parser.add_argument('--ncatype', nargs='+', help='Returns type of a nca file')	
		parser.add_argument('--nsptitleid', nargs='+', help='Returns titleid for a nsp file')
		parser.add_argument('--nsptype', nargs='+', help='Returns type for a nsp file')			
		parser.add_argument('--ReadversionID', nargs='+', help='Returns version number for nsp Oorxci')				
		parser.add_argument('--nsp_htrights', nargs='+', help='Returns true if nsp has titlerights')
		parser.add_argument('--nsp_hticket', nargs='+', help='Returns true if nsp has ticket')
		
		# Remove titlerights functions
		parser.add_argument('--remove-title-rights', nargs='+', help='Removes title rights encryption from all NCA\'s in the NSP.')
		parser.add_argument('--RTRNCA_h_nsp', nargs='+', help='Removes title rights encryption from a single nca reading from original nsp')		
		parser.add_argument('--RTRNCA_h_tick', nargs='+', help='Removes title rights encryption from a single nca reading from extracted ticket')
		parser.add_argument('--set-masterkey1', help='Changes the master key encryption for NSP.')
		parser.add_argument('--set-masterkey2', help='Changes the master key encryption for NSP.')
		parser.add_argument('--set-masterkey3', help='Changes the master key encryption for NSP.')
		parser.add_argument('--set-masterkey4', help='Changes the master key encryption for NSP.')
		parser.add_argument('--set-masterkey5', help='Changes the master key encryption for NSP.')
		parser.add_argument('--set-masterkey6', help='Changes the master key encryption for NSP.')
		parser.add_argument('--set-masterkey7', help='Changes the master key encryption for NSP.')		
		
		# Gamecard flag functions
		parser.add_argument('--seteshop', nargs='+', help='Set all nca in an nsp as eshop')
		parser.add_argument('--setcgame', nargs='+', help='Set all nca in an nsp card')	
		parser.add_argument('--seteshop_nca', nargs='+', help='Set a single nca as eshop')
		parser.add_argument('--setcgame_nca', nargs='+', help='Set a single nca as card')	
		parser.add_argument('--cardstate', nargs='+', help='Returns value for isgamecard flag from an nca')	
		
		# NSP Copy functions
		parser.add_argument('--NSP_copy_ticket', nargs='+', help='Extracts ticket from target nsp')
		parser.add_argument('--NSP_copy_nca', nargs='+', help='Extracts all nca files from target nsp')	
		parser.add_argument('--NSP_copy_other', nargs='+', help='Extracts all kinds of files different from nca or ticket from target nsp')
		parser.add_argument('--NSP_copy_xml', nargs='+', help='Extracts xml files from target nsp')
		parser.add_argument('--NSP_copy_cert', nargs='+', help='Extracts cert files from target nsp')
		parser.add_argument('--NSP_copy_jpg', nargs='+', help='Extracts jpg files from target nsp')	
		parser.add_argument('--NSP_copy_cnmt', nargs='+', help='Extracts cnmt files from target nsp')
		parser.add_argument('--copy_pfs0_meta', nargs='+', help='Extracts meta pfs0 from target nsp')
		parser.add_argument('--NSP_copy_ncap', nargs='+', help='Extracts ncap files from target nsp')
		
		# XCI Copy functions
		parser.add_argument('--XCI_copy_hfs0', nargs='+', help='Extracts hfs0 partition files from target xci')
		parser.add_argument('--XCI_c_hfs0_secure', nargs='+', help='Extracts secure hfs0 partition files from target xci')
		parser.add_argument('--XCI_c_hfs0_normal', nargs='+', help='Extracts normal hfs0 partition files from target xci')
		parser.add_argument('--XCI_c_hfs0_update', nargs='+', help='Extracts update hfs0 partition files from target xci')
		parser.add_argument('--XCI_copy_nca_secure', nargs='+', help='Extracts nca from secure partition')
		parser.add_argument('--XCI_copy_nca_normal', nargs='+', help='Extracts nca from normal partition')
		parser.add_argument('--XCI_copy_nca_update', nargs='+', help='Extracts nca from update partition')
		parser.add_argument('--XCI_copy_rhfs0', nargs='+', help='Extracts root.hfs0')

		# Dedicated copy functions. NCA Types. 
		parser.add_argument('--NSP_copy_nca_meta', nargs='+', help='Extracts nca files with type meta from target nsp')
		parser.add_argument('--NSP_copy_nca_control', nargs='+', help='Extracts nca files with type control from target nsp')
		parser.add_argument('--NSP_copy_nca_manual', nargs='+', help='Extracts nca files with type manual from target nsp')		
		parser.add_argument('--NSP_copy_nca_program', nargs='+', help='Extracts nca files with type program from target nsp')
		parser.add_argument('--NSP_copy_nca_data', nargs='+', help='Extracts nca files with type data from target nsp')
		parser.add_argument('--NSP_copy_nca_pdata', nargs='+', help='Extracts nca fles with type public data from target nsp')
		
		# Dedicated copy functions. TITLERIGHTS. 
		parser.add_argument('--NSP_copy_tr_nca', nargs='+', help='Extracts nca files with titlerights from target nsp')
		parser.add_argument('--NSP_copy_ntr_nca', nargs='+', help='Extracts nca files without titlerights from target nsp')
		parser.add_argument('--NSP_c_KeyBlock', nargs='+', help='Extracts keyblock from nsca files with titlerigths  from target nsp')	
		parser.add_argument('--C_clean', nargs='+', help='Extracts nca files and removes it.s titlerights from target NSP OR XCI')			
		parser.add_argument('--C_clean_ND', nargs='+', help='Extracts nca files and removes it.s titlerights from target NSP OR XCI without deltas')
		
		# Dedicated copy functions. SPLIT OR UPDATE. 
		parser.add_argument('--splitter', nargs='+', help='Split content by titleid according to cnmt files')
		parser.add_argument('-dspl', '--direct_splitter', nargs='+', help='Split content by titleid according to cnmt files')		
		parser.add_argument('--updbase', nargs='+', help='Prepare base file to update it')

		# Combinations	
		parser.add_argument('--gen_placeholder', help='Creates nsp or xci placeholder')		
		parser.add_argument('--placeholder_combo', nargs='+', help='Extracts nca files for placeholder nsp')
		parser.add_argument('--license_combo', nargs='+', help='Extracts nca files for license nsp')
		parser.add_argument('--mlicense_combo', nargs='+', help='Extracts nca files for tinfoil license nsp')
		parser.add_argument('--zip_combo', nargs='+', help='Extracts and generate files to make a restore zip')
		
		# Auxiliary
		parser.add_argument('-o', '--ofolder', nargs='+', help='Set output folder for copy instructions')
		parser.add_argument('-ifo', '--ifolder', help='Input folder')		
		parser.add_argument('-ifo_s', '--ifolder_secure', help='Input secure folder')	
		parser.add_argument('-ifo_n', '--ifolder_normal', help='Input normal folder')		
		parser.add_argument('-ifo_u', '--ifolder_update', help='Input update folder')		
		parser.add_argument('-tfile', '--text_file', help='Output text file')
		parser.add_argument('-dbfile', '--db_file', help='Output text file for database')			
		parser.add_argument('-b', '--buffer', nargs='+', help='Set buffer for copy instructions')
		parser.add_argument('-ext', '--external', nargs='+', help='Set original nsp or ticket for remove nca titlerights functions')
		parser.add_argument('-pv', '--patchversion', nargs='+', help='Number fot patch Required system version or program, patch or addcontent version')
		parser.add_argument('-kp', '--keypatch', nargs='+', help='patch masterkey to input number')	
		parser.add_argument('-rsvc', '--RSVcap', nargs='+', help='RSV cap when patching. Default is FW4.0')			
		parser.add_argument('-pe', '--pathend', nargs='+', help='Output to subfolder')		
		parser.add_argument('-cskip', '--cskip', nargs='+', help='Skip dlc or update')		
		parser.add_argument('-fat', '--fat', nargs='+', help='Split xci for fat32 or exfat')	
		parser.add_argument('-fx', '--fexport', nargs='+', help='Export splitted nsp to files or folder')
		parser.add_argument('-t', '--type', nargs='+', help='Type of file')			
		parser.add_argument('-tid', '--titleid', nargs='+', help='Filter with titleid')			
		parser.add_argument('-bid', '--baseid', nargs='+', help='Filter with base titleid')		
		parser.add_argument('-ND', '--nodelta', nargs='+', help='Exclude deltas')	
		parser.add_argument('-dbformat', '--dbformat', nargs='+', help='Database format extended, nutdb or keyless-extended')		
		parser.add_argument('-rn', '--rename', nargs='+', help='Filter with base titleid')		
		parser.add_argument('-uin', '--userinput', help='Reads a user input')				
		# LISTMANAGER
		parser.add_argument('-cl', '--change_line', help='Change line in text file')
		parser.add_argument('-rl', '--read_line', help='Read line in text file')		
		parser.add_argument('-ln', '--line_number', help='line number')
		parser.add_argument('-nl', '--new_line', help='new line')
		parser.add_argument('-ff', '--findfile', help='find different types of files')	
		parser.add_argument('-fil', '--filter', nargs='+', help='filter using strings')			
		# Archive		
		parser.add_argument('-archive','--archive', help='Archive to folder')		
		parser.add_argument('-zippy','--zippy', help='Zip a file')			
		parser.add_argument('-joinfile','--joinfile', help='Join split file')
		# OTHER		
		parser.add_argument('-nint_keys','--nint_keys', help='Verify NS keys')			
		parser.add_argument('-renf','--renamef', help='Rename file with proper name')	
		parser.add_argument('-oaid','--onlyaddid', help='Rename file with proper name')		

		args = parser.parse_args()

		Status.start()
		
# NCA/NSP IDENTIFICATION
		# ..................................................
		# Get titleid from nca file
		# ..................................................
		if args.ncatitleid:
			for filename in args.ncatitleid:		
				try:
					f = Fs.Nca(filename, 'rb')
					f.printtitleId()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ..................................................
		# Get type from nca file	
		# ..................................................		
		if args.ncatype:
			for filename in args.ncatype:		
				try:
					f = Fs.Nca(filename, 'rb')
					f.print_nca_type()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ..................................................
		# Get titleid from nsp file		
		# ..................................................		
		if args.nsptitleid:
			for fileName in args.nsptitleid:		
				try:
					f = Fs.Nsp(fileName, 'r+b')
					titleid=f.getnspid()
					Print.info(titleid)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))										
		# ..................................................
		# Read version number from nsp or xci	
		# ..................................................		
		if args.ReadversionID:
			for filename in args.ReadversionID:		
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.get_cnmt_verID()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.get_cnmt_verID()
						f.flush()
						f.close()														
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			
		# ..................................................
		# Identify type of nsp	
		# ..................................................
		if args.nsptype:
			for filename in args.nsptype:		
				try:
					f = Fs.Nsp(filename, 'rb')
					TYPE=f.nsptype()
					print(TYPE)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		

		# ..................................................
		# Identify if nsp has titlerights
		# ..................................................
		if args.nsp_htrights:
			for filename in args.nsp_htrights:		
				try:
					f = Fs.Nsp(filename, 'rb')
					if f.trights_set() == 'TRUE':
						Print.info('TRUE')
					if f.trights_set() == 'FALSE':
						Print.info('FALSE')
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
	
		# ..................................................
		# Identify if nsp has ticket
		# ..................................................	
		if args.nsp_hticket:
			for filename in args.nsp_hticket:		
				try:
					f = Fs.Nsp(filename, 'rb')
					if f.exist_ticket() == 'TRUE':
						Print.info('TRUE')
					if f.exist_ticket() == 'FALSE':
						Print.info('FALSE')
				except BaseException as e:
					Print.error('Exception: ' + str(e))	

		# ..................................................
		# Identify if nsp has ticket
		# ..................................................	
		if args.nsp_hticket:
			for filename in args.nsp_hticket:		
				try:
					f = Fs.Nsp(filename, 'rb')
					if f.exist_ticket() == 'TRUE':
						Print.info('TRUE')
					if f.exist_ticket() == 'FALSE':
						Print.info('FALSE')
				except BaseException as e:
					Print.error('Exception: ' + str(e))							

# REMOVE TITLERIGHTS FUNCTIONS
		# ..................................................
		# Remove titlerights from input NSP
		# ..................................................
		if args.remove_title_rights:
			for filename in args.remove_title_rights:
				try:
					f = Fs.Nsp(filename, 'r+b')
					f.removeTitleRights()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ..................................................
		# Change Master keys
		# ..................................................					

		if args.set_masterkey1:
			f = Fs.Nsp(args.set_masterkey1, 'r+b')
			f.setMasterKeyRev(0)
			f.flush()
			f.close()
			pass

		if args.set_masterkey2:
			f = Fs.Nsp(args.set_masterkey2, 'r+b')
			f.setMasterKeyRev(2)
			f.flush()
			f.close()
			pass

		if args.set_masterkey3:
			f = Fs.Nsp(args.set_masterkey3, 'r+b')
			f.setMasterKeyRev(3)
			f.flush()
			f.close()
			pass

		if args.set_masterkey4:
			f = Fs.Nsp(args.set_masterkey4, 'r+b')
			f.setMasterKeyRev(4)
			f.flush()
			f.close()
			pass

		if args.set_masterkey5:
			f = Fs.Nsp(args.set_masterkey5, 'r+b')
			f.setMasterKeyRev(5)
			f.flush()
			f.close()
			pass

		if args.set_masterkey6:
			f = Fs.Nsp(args.set_masterkey6, 'r+b')
			f.setMasterKeyRev(6)
			f.flush()
			f.close()
			pass			
			
		if args.set_masterkey7:
			f = Fs.Nsp(args.set_masterkey7, 'r+b')
			f.setMasterKeyRev(7)
			f.flush()
			f.close()
			pass								
		# ..................................................................			
		# Remove titlerights from an NSP using information from original NSP
		# ..................................................................		
		if args.RTRNCA_h_nsp:
			for filename in args.external:
				try:
					f = Fs.Nsp(filename, 'r+b')
					masterKeyRev=f.nspmasterkey()
					titleKeyDec=f.nsptitlekeydec()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
			for filename in args.RTRNCA_h_nsp:
				try:
					f = Fs.Nca(filename, 'r+b')
					f.removeTitleRightsnca(masterKeyRev,titleKeyDec)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# .........................................................................						
		# Remove titlerights from an NCA using information from an extracted TICKET
		# .........................................................................			
		if args.RTRNCA_h_tick:
			for filename in args.external:
				try:
					f = Fs.Ticket(filename, 'r+b')
					f.open(filename, 'r+b')
					masterKeyRev=f.getMasterKeyRevision()
					titleKeyDec=f.get_titlekeydec()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
			for filename in args.RTRNCA_h_tick:
				try:
					f = Fs.Nca(filename, 'r+b')
					f.removeTitleRightsnca(masterKeyRev,titleKeyDec)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))			
				
# GAMECARD FLAG FUNCTIONS
		# ...................................................						
		# Set isgamecard flag from all nca in an NSP as ESHOP
		# ...................................................
		if args.seteshop:
			for filename in args.seteshop:
				try:
					f = Fs.Nsp(filename, 'r+b')
					f.seteshop()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Set isgamecard flag from all nca in an NSP as CARD
		# ...................................................					
		if args.setcgame:
			for filename in args.setcgame:
				try:
					f = Fs.Nsp(filename, 'r+b')
					f.setcgame()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ...................................................						
		# Set isgamecard flag for one nca as ESHOP
		# ...................................................
		if args.seteshop_nca:
			for filename in args.seteshop_nca:
				try:
					f = Fs.Nca(filename, 'r+b')
					f.header.setgamecard(0)
					Print.info('IsGameCard flag is now set as: ' + str(f.header.getgamecard()))	
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Set isgamecard flag for one nca as CARD
		# ...................................................
		if args.setcgame_nca:
			for filename in args.setcgame_nca:
				try:
					f = Fs.Nca(filename, 'r+b')
					f.header.setgamecard(1)
					Print.info('IsGameCard flag is now set as: ' + str(f.header.getgamecard()))	
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
					
		# ...................................................						
		# Get isgamecard flag from a NCA file
		# ...................................................		
		if args.cardstate:
			for filename in args.cardstate:		
				try:
					f = Fs.Nca(filename, 'rb')
					f.cardstate()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		

# COPY FUNCTIONS
		# ...................................................						
		# Copy TICKET from NSP file
		# ...................................................		
		if args.NSP_copy_ticket:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_ticket:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
			for filename in args.NSP_copy_ticket:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_ticket(ofolder)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Copy all NCA from NSP file
		# ...................................................							
		if args.NSP_copy_nca:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'					
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656		
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'					
			for filename in args.NSP_copy_nca:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
					
		# ...................................................................						
		# Copy all hfs0 partitions (update, normal,secure,logo) from XCI file
		# ...................................................................	
		if args.XCI_copy_hfs0:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.XCI_copy_hfs0:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			for filePath in args.XCI_copy_hfs0:
				f = Fs.factory(filePath)
				f.open(filePath, 'rb')
				f.copy_hfs0(ofolder,buffer,"all")
				f.close()

		# ...........................................						
		# Copy update partition from XCI file as hfs0
		# ...........................................	
		if args.XCI_c_hfs0_update:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.XCI_c_hfs0_update:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768			
			for filePath in args.XCI_c_hfs0_update:
				f = Fs.factory(filePath)
				f.open(filePath, 'rb')
				f.copy_hfs0(ofolder,buffer,"update")
				f.close()		
				
		# ...........................................						
		# Copy normal partition from XCI file as hfs0
		# ...........................................	
		if args.XCI_c_hfs0_normal:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.XCI_c_hfs0_normal:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768			
			for filePath in args.XCI_c_hfs0_normal:
				f = Fs.factory(filePath)
				f.open(filePath, 'rb')
				f.copy_hfs0(ofolder,buffer,"normal")
				f.close()	

		# ...........................................						
		# Copy secure partition from XCI file as hfs0
		# ...........................................	
		if args.XCI_c_hfs0_secure:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.XCI_c_hfs0_secure:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768		
			for filePath in args.XCI_c_hfs0_secure:
				f = Fs.factory(filePath)
				f.open(filePath, 'rb')
				f.copy_hfs0(ofolder,buffer,'secure')
				f.close()						
				
		# ...........................................						
		# Copy nca from secure partition from XCI 
		# ...........................................	
		if args.XCI_copy_nca_secure:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.XCI_copy_nca_secure:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656					
			for filePath in args.XCI_copy_nca_secure:
				f = Fs.Xci(filePath)
				f.open(filePath, 'rb')
				f.copy_nca(ofolder,buffer,'secure',metapatch,vkeypatch,int(RSV_cap))
				f.close()						

		# ...........................................						
		# Copy nca from secure partition from XCI 
		# ...........................................	
		if args.XCI_copy_nca_normal:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.C_clean:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656					
			for filePath in args.XCI_copy_nca_normal:
				f = Fs.nXci(filePath)
				f.open(filePath, 'rb')
				f.copy_nca(ofolder,buffer,'normal',metapatch,vkeypatch,int(RSV_cap))
				f.close()					

		# ...........................................						
		# Copy nca from secure partition from XCI 
		# ...........................................	
		if args.XCI_copy_nca_update:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.C_clean:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656					
			for filePath in args.XCI_copy_nca_update:
				f = Fs.uXci(filePath)
				f.open(filePath, 'rb')
				f.copy_nca(ofolder,buffer,'update',metapatch,vkeypatch,int(RSV_cap))
				f.close()					
		
		
		# ...........................................						
		# Copy root.hfs0 from XCI 
		# ...........................................	
		if args.XCI_copy_rhfs0:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.XCI_copy_rhfs0:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768		
			for filePath in args.XCI_copy_rhfs0:
				f = Fs.factory(filePath)
				f.open(filePath, 'rb')
				f.copy_root_hfs0(ofolder,buffer)
				f.close()			


					
		# ...................................................						
		# Copy OTHER KIND OF FILES from NSP file
		# ...................................................							
		if args.NSP_copy_other:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_other:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768						
			for filename in args.NSP_copy_other:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_other(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))

		# ...................................................						
		# Copy XML from NSP file
		# ...................................................	
		if args.NSP_copy_xml:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_xml:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			for filename in args.NSP_copy_xml:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_xml(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ...................................................						
		# Copy CERT from NSP file
		# ...................................................	
		if args.NSP_copy_cert:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_cert:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768					
			for filename in args.NSP_copy_cert:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nsp_cert(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		# ...................................................						
		# Copy JPG from NSP file
		# ...................................................	
		if args.NSP_copy_jpg:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_jpg:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768			
			for filename in args.NSP_copy_jpg:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_jpg(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	

		# ...................................................						
		# Copy meta cnmt files from NSP file
		# ...................................................	
		if args.NSP_copy_cnmt:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_cnmt:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768			
			for filename in args.NSP_copy_cnmt:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.copy_cnmt(ofolder,buffer)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))		
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.copy_cnmt(ofolder,buffer)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))								
					
		# ...................................................						
		# Copy pfs0 from NSP file
		# ...................................................	
		if args.copy_pfs0_meta:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.copy_pfs0_meta:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			for filename in args.copy_pfs0_meta:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_pfs0_meta(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))											
					
		# ...................................................						
		# Copy control ncap files from NSP file
		# ...................................................	
		if args.NSP_copy_ncap:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_ncap:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			for filename in args.NSP_copy_ncap:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_ncap(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))							

# DEDICATED COPY FUNCTIONS. NCA TYPES. 
		# ...................................................						
		# Copy all META NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_meta:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca_meta:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			for filename in args.NSP_copy_nca_meta:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_meta(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Copy all CONTROL NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_control:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca_control:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			for filename in args.NSP_copy_nca_control:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_control(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))					
		# ...................................................						
		# Copy all MANUAL NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_manual:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca_manual:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768						
			for filename in args.NSP_copy_nca_manual:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_manual(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ...................................................						
		# Copy all PROGRAM NCA from NSP file
		# ...................................................						
		if args.NSP_copy_nca_program:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca_program:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768											
			for filename in args.NSP_copy_nca_program:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_program(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		# ...................................................						
		# Copy all DATA NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_data:	
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca_data:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
											
			for filename in args.NSP_copy_nca_data:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_data(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))						
		# ...................................................						
		# Copy all PUBLIC DATA NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_pdata:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_nca_pdata:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
								
			for filename in args.NSP_copy_nca_pdata:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_pdata(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))								
		
# DEDICATED COPY FUNCTIONS. TITLERIGHTS. 
		# ...................................................						
		# Copy all NCA WITH TITLERIGHTS from target NSP
		# ...................................................			
		if args.NSP_copy_tr_nca:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_tr_nca:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
					
			for filename in args.NSP_copy_tr_nca:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_tr_nca(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Copy all NCA WITHOUT TITLERIGHTS from target NSP
		# ...................................................						
		if args.NSP_copy_ntr_nca:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_copy_ntr_nca:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
				
			for filename in args.NSP_copy_ntr_nca:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_ntr_nca(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	

		# ..................................						
		# Copy ALL NCA AND CLEAN TITLERIGHTS 
		# ..................................					
		if args.C_clean:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))		
						dir=os.path.dirname(os.path.abspath(filename))
						ofolder = dir+ '\\'+ 'output'
				else:		
					for filename in args.C_clean:
						dir=os.path.dirname(os.path.abspath(filename))
						ofolder = dir+ '\\'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'true'
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656		
			if args.C_clean:					
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))				
				else:
					for filename in args.C_clean:
						filename=filename
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						if f.trights_set() == 'FALSE':
							Print.info("NSP DOESN'T HAVE TITLERIGHTS")
							f.copy_nca(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))	
						if f.trights_set() == 'TRUE':
							if f.exist_ticket() == 'TRUE':
								Print.info("NSP HAS TITLERIGHTS AND TICKET EXISTS")
								f.cr_tr_nca(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))
							if f.exist_ticket() == 'FALSE':
								Print.error('NSP FILE HAS TITLERIGHTS BUT NO TICKET')		
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						if f.trights_set() == 'FALSE':
							Print.info("XCI DOESN'T HAVE TITLERIGHTS")
							f.copy_nca(ofolder,buffer,'secure',metapatch,vkeypatch,int(RSV_cap))
						if f.trights_set() == 'TRUE':
							if f.exist_ticket() == 'TRUE':
								Print.info("XCI HAS TITLERIGHTS AND TICKET EXISTS")
								f.cr_tr_nca(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))
							if f.exist_ticket() == 'FALSE':
								Print.error('XCI FILE HAS TITLERIGHTS BUT NO TICKET')		
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			
		# ...................................................						
		# Copy ALL NCA AND CLEAN TITLERIGHTS WITHOUT DELTAS
		# ...................................................				
		if args.C_clean_ND:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))		
						dir=os.path.dirname(os.path.abspath(filename))
						ofolder = dir+ '\\'+ 'output'
				else:			
					for filename in args.C_clean_ND:
						dir=os.path.dirname(os.path.abspath(filename))
						ofolder = dir+ '\\'+ 'output'		
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'	
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'		
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input							
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656		
			
			if args.C_clean_ND:			
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))		
				else:			
					for filename in args.C_clean_ND:
						filename=filename	
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						if f.trights_set() == 'FALSE':
							Print.info("NSP DOESN'T HAVE TITLERIGHTS")
							f.copy_nca_nd(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))	
						if f.trights_set() == 'TRUE':
							if f.exist_ticket() == 'TRUE':
								Print.info("NSP HAS TITLERIGHTS AND TICKET EXISTS")
								f.cr_tr_nca_nd(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))
							if f.exist_ticket() == 'FALSE':
								Print.error('NSP FILE HAS TITLERIGHTS BUT NO TICKET')		
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						if f.trights_set() == 'FALSE':
							Print.info("XCI DOESN'T HAVE TITLERIGHTS")
							f.copy_nca_nd(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))	
						if f.trights_set() == 'TRUE':
							if f.exist_ticket() == 'TRUE':
								Print.info("XCI HAS TITLERIGHTS AND TICKET EXISTS")
								f.cr_tr_nca_nd(ofolder,buffer,metapatch,vkeypatch,int(RSV_cap))
							if f.exist_ticket() == 'FALSE':
								Print.error('XCI FILE HAS TITLERIGHTS BUT NO TICKET')		
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))	

	
		# ........................................................						
		# Copy keyblock from nca files with titlerights from a nsp
		# ........................................................						
		if args.NSP_c_KeyBlock:	
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.NSP_c_KeyBlock:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
			for filename in args.NSP_c_KeyBlock:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_KeyBlock(ofolder)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
					
		# ..................................................
		# Identify if nsp has titlerights
		# ..................................................
#		if args.nsp_htrights:
#			for filename in args.nsp_htrights:		
#				try:
#					f = Fs.Nsp(filename, 'r+b')
#					if f.trights_set() == 'TRUE':
#						Print.info('TRUE')
#					if f.trights_set() == 'FALSE':
#						Print.info('FALSE')
#				except BaseException as e:
#					Print.error('Exception: ' + str(e))				
	
		# ..................................................
		# Identify if nsp has ticket
		# ..................................................	
#		if args.nsp_hticket:
#			for filename in args.nsp_hticket:		
#				try:
#					f = Fs.Nsp(filename, 'r+b')
#					if f.exist_ticket() == 'TRUE':
#						Print.info('TRUE')
#					if f.exist_ticket() == 'FALSE':
#						Print.info('FALSE')
#				except BaseException as e:
#					Print.error('Exception: ' + str(e))						



# DEDICATED COPY FUNCTIONS. SPLIT OR UPDATE. 
		# ............................................................						
		# Split content by titleid according to cnmt files
		# ............................................................	
		if args.splitter:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:				
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))	
						dir=os.path.dirname(os.path.abspath(filename))
						ofolder = dir+ '\\'+ 'output'	
				else:			
					for filename in args.splitter:
						dir=os.path.dirname(os.path.abspath(filename))
						ofolder = dir+ '\\'+ 'output'		
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			if args.pathend:
				for input in args.pathend:
					try:
						pathend = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				pathend = ''
			if args.splitter:					
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))	
				else:		
					for filename in args.splitter:
						filename=filename
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.splitter_read(ofolder,buffer,pathend)
						f.flush()
						f.close()	
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.splitter_read(ofolder,buffer,pathend)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
						
		# ............................................................						
		# Prepare base content to get it updated
		# ............................................................	
		if args.updbase:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.updbase:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'		
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768				
			if args.cskip:
				for input in args.cskip:
					try:
						cskip = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				pathend = 'false'			
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'					
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656		
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
				
			for filename in args.updbase:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.updbase_read(ofolder,buffer,cskip,metapatch,vkeypatch,RSV_cap)
						f.flush()
						f.close()	
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.updbase_read(ofolder,buffer,cskip,metapatch,vkeypatch,RSV_cap)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
												
# COMBINATIONS
		# ............................................................						
		# Get nca files to make a placeholder in eshop format from NSP
		# ............................................................
		'''
		parser.add_argument('--gen_placeholder', nargs='+', help='Creates nsp or xci placeholder')	
		'''
		if args.gen_placeholder:	
			indent = 1
			tabs = '\t' * indent							
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
	
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				folder = args.gen_placeholder
				dir=os.path.abspath(folder)
				ofolder = os.path.join(dir, 'output')
			if not os.path.exists(ofolder):
				os.makedirs(ofolder)		
			ruta=args.gen_placeholder
			indent = 1
			tabs = '\t' * indent	
			if ruta[-1]=='"':
				ruta=ruta[:-1]
			if ruta[0]=='"':
				ruta=ruta[1:]		
			extlist=list()
			if args.type:
				for t in args.type:
					x='.'+t
					extlist.append(x)
					if x[-1]=='*':
						x=x[:-1]
						extlist.append(x)
			#print(extlist)			
			if args.filter:
				for f in args.filter:
					filter=f	
			if args.type:
				for input in args.type:		
					if input == "xci" or input == "XCI": 
						export='xci'						
					elif input == "nsp" or input == "NSP": 	
						export='nsp'
					elif input == "both" or input == "BOTH": 
						export='both'													
					else:
						print ("Wrong Type!!!")							
			
			filelist=list()				
			ruta=str(ruta)
			#print(ruta)
			try:
				fname=""
				binbin='RECYCLE.BIN'
				for ext in extlist:
					#print (ext)
					if os.path.isdir(ruta):
						for dirpath, dirnames, filenames in os.walk(ruta):
							for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:
								fname=""
								if args.filter:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(os.path.join(dirpath, filename))
					else:		
						if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
							filename = ruta
							fname=""
							if args.filter:
								if filter.lower() in filename.lower():
									fname=filename
							else:
								fname=filename		
							if fname != "":
								if binbin.lower() not in filename.lower():					
									filelist.append(filename)								
				'''					
				for f in filelist:
					print(f)
				'''
				print(len(filelist))
				counter=len(filelist)
				for filepath in filelist:
					if filepath.endswith('.nsp'):
						try:
							prlist=list()
							f = Fs.Nsp(filepath)										
							contentlist=f.get_content_placeholder()
							#print(contentlist)
							f.flush()
							f.close()		
							if len(prlist)==0:
								for i in contentlist:
									prlist.append(i)
								#print (prlist)
							else:
								for j in range(len(contentlist)):
									notinlist=False
									for i in range(len(prlist)):
										#print (contentlist[j][1])
										#print (contentlist[j][6])
										#pass
										if contentlist[j][1] == prlist[i][1]:
											if contentlist[j][6] > prlist[i][6]:
												del prlist[i]
												prlist.append(contentlist[j])
										else:
											notinlist=True
									if notinlist == True:
										prlist.append(contentlist[j])		
						except BaseException as e:
							counter=int(counter)
							counter-=1						
							Print.error('Exception: ' + str(e))		
							continue					
					if export=='nsp' or export=='both':
						oflist=list()
						osizelist=list()
						totSize=0
						#print(prlist)
						for i in range(len(prlist)):
							for j in prlist[i][4]:
								oflist.append(j[0])
								osizelist.append(j[1])
								totSize = totSize+j[1]	
								filelist			
						basename=str(os.path.basename(os.path.abspath(filepath)))		
						endname=basename[:-4]+'[PLH].nsp'							
						endfile = os.path.join(ofolder, endname)
						#print(str(filepath))	
						#print(str(endfile))	
						nspheader=sq_tools.gen_nsp_header(oflist,osizelist)					
						#print(endfile)						
						#print(hx(nspheader))
						totSize = len(nspheader) + totSize
						#print(str(totSize))
						vskip=False	
						print('Processing: '+str(filepath))						
						if os.path.exists(endfile) and os.path.getsize(endfile) == totSize:
							print('- Placeholder file already exists, skipping...')
							vskip=True			
						if vskip==False:				
							t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)			
							outf = open(endfile, 'w+b')		
							t.write(tabs+'- Writing NSP header...')							
							outf.write(nspheader)		
							t.update(len(nspheader))				
							outf.close()
							if filepath.endswith('.nsp'):
								try:
									f = Fs.Nsp(filepath)
									for file in oflist:									
										f.append_content(endfile,file,buffer,t)
									f.flush()
									f.close()	
									t.close()			
									counter=int(counter)
									counter-=1									
									print(tabs+'> Placeholder was created')						
									print(tabs+'> Still '+str(counter)+' to go')									
								except BaseException as e:
									counter=int(counter)
									counter-=1								
									Print.error('Exception: ' + str(e))			
			except BaseException as e:
				Print.error('Exception: ' + str(e))		
								
		# ............................................................						
		# Get files to make a [lc].nsp from NSP
		# ............................................................		
		if args.license_combo:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.license_combo:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			for filename in args.license_combo:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_control(ofolder,buffer)
					f.copy_ticket(ofolder)
					f.copy_nsp_cert(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ............................................................						
		# Get files to make a placeholder+license nsp from a NSP
		# ............................................................		
		if args.mlicense_combo:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.mlicense_combo:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			for filename in args.mlicense_combo:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_control(ofolder,buffer)
					f.copy_nca_meta(ofolder,buffer)
					f.copy_ticket(ofolder)
					f.copy_nsp_cert(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ............................................................						
		# Get files to make zip to restore nsp to original state
		# ............................................................
		if args.zip_combo:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.zip_combo:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
				
			for filename in args.zip_combo:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_meta(ofolder,buffer)
					f.copy_ticket(ofolder)
					f.copy_other(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))

# REPACK
		# ...................................................						
		# Repack NCA files to NSP
		# ...................................................	
		if args.create:
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"		
			if args.fexport:		
				for input in args.fexport:
					try:
						if input == "files":
							fx="files"
						else:
							fx="folder"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fx="files"	
			if args.ifolder:
				ruta = args.ifolder				
				f_list = list()
				ncalist = list()
				orderlist = list()
				for dirpath, dnames, fnames in os.walk(ruta):
					for f in fnames:
						if f.endswith('.cnmt.nca'):	
							try:
								filepath = os.path.join(ruta, f)							
								nca = Fs.Nca(filepath, 'r+b')
								ncalist=ncalist+nca.ncalist_bycnmt()
							except BaseException as e:
								Print.error('Exception: ' + str(e))								
					for f in fnames:
						filepath = os.path.join(ruta, f)
						f_list.append(filepath)
					for f in ncalist:
						fpath= os.path.join(ruta, f)						
						if fpath in f_list:			
							orderlist.append(fpath)	
					for f in fnames:
						if f.endswith('.cnmt'):
							fpath= os.path.join(ruta, f)								
							orderlist.append(fpath)	
					for f in fnames:
						if f.endswith('.jpg'):						
							fpath= os.path.join(ruta, f)								
							orderlist.append(fpath)							
					for f in fnames:
						if f.endswith('.tik') or f.endswith('.cert'):							
							fpath= os.path.join(ruta, f)								
							orderlist.append(fpath)	
					nsp = Fs.Nsp(None, None)
					nsp.path = args.create
					nsp.pack(orderlist,buffer,fat,fx)	
					#print (f_list)
					#print (fnames)
					#print (ncalist)
					#print (orderlist)
			else:
				nsp = Fs.Nsp(None, None)
				nsp.path = args.create
				nsp.pack(args.file,buffer,fat,fx)
			#for filePath in args.file:
			#	Print.info(filePath)
		# ...................................................						
		# Repack NCA files to partition hfs0
		# ...................................................	
		if args.create_hfs0:
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			hfs0 = Fs.Hfs0(None, None)
			hfs0.path = args.create_hfs0
			if args.ifolder:
				ruta = args.ifolder				
				f_list = list()
				for dirpath, dnames, fnames in os.walk(ruta):
					for f in fnames:
						filepath = os.path.join(ruta, f)
						f_list.append(filepath)
				hfs0.pack(f_list,buffer)
			else:
				hfs0.pack(args.file,buffer)	
		# ...................................................						
		# Repack NCA files to root_hfs0
		# ...................................................	
		if args.create_rhfs0:
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.ifolder:
				ruta = args.ifolder
				ruta_update=os.path.join(ruta, "update")
				ruta_normal=os.path.join(ruta, "normal")
				ruta_secure=os.path.join(ruta, "secure")
				if os.path.isdir(ruta_update) == True:
					upd_list = list()	
					for dirpath, dnames, fnames in os.walk(ruta_update):
						for f in fnames:
							filepath = os.path.join(ruta_update, f)
							upd_list.append(filepath)
				else:			
					upd_list = list()				
				if os.path.isdir(ruta_normal) == True:
					norm_list = list()	
					for dirpath, dnames, fnames in os.walk(ruta_normal):
						for f in fnames:
							filepath = os.path.join(ruta_normal, f)
							norm_list.append(filepath)
				else:			
					norm_list = list()		
				if os.path.isdir(ruta_secure) == True:
					sec_list = list()	
					for dirpath, dnames, fnames in os.walk(ruta_secure):
						for f in fnames:
							filepath = os.path.join(ruta_secure, f)
							sec_list.append(filepath)
				else:			
					sec_list = list()							
			else:				
				if args.ifolder_update:
					ruta = args.ifolder_update				
					upd_list = list()
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							upd_list.append(filepath)
				else:			
					upd_list = list()
				if args.ifolder_normal:
					ruta = args.ifolder_normal				
					norm_list = list()
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							norm_list.append(filepath)
				else:			
					norm_list = list()
				if args.ifolder_secure:
					ruta = args.ifolder_secure				
					sec_list = list()
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							sec_list.append(filepath)
				else:			
					sec_list = list()				
					
			#print (upd_list)
			#print (norm_list)
			#print (sec_list)
			hfs0 = Fs.Hfs0(None, None)
			hfs0.path = args.create_rhfs0
			hfs0.pack_root(upd_list,norm_list,sec_list,buffer)
		# ...................................................						
		# Repack NCA files to xci
		# ...................................................	
		if args.create_xci:
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"								
			if args.ifolder:
				ruta = args.ifolder
				ruta_update=os.path.join(ruta, "update")
				ruta_normal=os.path.join(ruta, "normal")
				ruta_secure=os.path.join(ruta, "secure")
				if os.path.isdir(ruta_update) == True:
					upd_list = list()	
					for dirpath, dnames, fnames in os.walk(ruta_update):
						for f in fnames:
							filepath = os.path.join(ruta_update, f)
							upd_list.append(filepath)
				else:			
					upd_list = list()				
				if os.path.isdir(ruta_normal) == True:
					norm_list = list()	
					for dirpath, dnames, fnames in os.walk(ruta_normal):
						for f in fnames:
							filepath = os.path.join(ruta_normal, f)
							norm_list.append(filepath)
				else:			
					norm_list = list()		
				if os.path.isdir(ruta_secure) == True:
					sec_list = list()	
					for dirpath, dnames, fnames in os.walk(ruta_secure):
						for f in fnames:
							filepath = os.path.join(ruta_secure, f)
							sec_list.append(filepath)
				else:			
					sec_list = list()		
			else:				
				if args.ifolder_update:
					ruta = args.ifolder_update				
					upd_list = list()
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							upd_list.append(filepath)
				else:			
					upd_list = list()
				if args.ifolder_normal:
					ruta = args.ifolder_normal				
					norm_list = list()
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							norm_list.append(filepath)
				else:			
					norm_list = list()
				if args.ifolder_secure:
					ruta = args.ifolder_secure				
					sec_list = list()
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							sec_list.append(filepath)
				else:			
					sec_list = list()		
				
			#print (upd_list)
			#print (norm_list)
			#print (sec_list)
			xci = Fs.Xci(None)
			xci.path = args.create_xci
			xci.pack(upd_list,norm_list,sec_list,buffer,fat)			
		# ...................................................						
		# Supertrimm a xci
		# ...................................................				
		if args.xci_super_trim:			
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filepath in args.xci_super_trim:
					dir=os.path.dirname(os.path.abspath(filepath))
					ofolder = dir+ '\\'+ 'output'
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"								
			for filepath in args.xci_super_trim:
				if filepath.endswith('.xci'):
					try:
						f = Fs.factory(filepath)
						filename=os.path.basename(os.path.abspath(filepath))
						#print(filename)
						outfile = os.path.join(ofolder, filename)
						#print(f.path)
						f.open(filepath, 'rb')
						f.supertrim(buffer,outfile,ofolder,fat)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))				

				
		# ...................................................						
		# Take off deltas
		# ...................................................						
		if args.erase_deltas:	
						
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
	
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filepath in args.erase_deltas:
					dir=os.path.dirname(os.path.abspath(filepath))
					ofolder = os.path.join(dir, 'output')						
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"		
			if args.fexport:		
				for input in args.fexport:
					try:
						if input == "files":
							fx="files"
						else:
							fx="folder"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fx="files"		
				
			if args.erase_deltas:
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filepath = filelist.readline()
						filepath=os.path.abspath(filepath.rstrip('\n'))						
				else:
					for filepath in args.erase_deltas:
						filepath=filepath
				if args.type:
					for input in args.type:							
						if input == "nsp" or input == "NSP": 	
							export='nsp'										
						else:
							print ("Wrong Type!!!")					
				else:
					if filepath.endswith('.nsp'):
						export='nsp'
					else:
						print ("Wrong Type!!!")
				if args.rename:
					for newname in args.rename:
						newname=newname+'.xxx'
						endfile = os.path.join(ofolder, newname)
				else:
					endfile=os.path.basename(os.path.abspath(filepath))					
				if args.cskip=='False':
					cskip=False
				else:
					cskip=True						

				if filepath.endswith(".nsp"):
					try:				
						f = Fs.Nsp(filepath)					
						f.sp_groupncabyid_ND(buffer,ofolder,fat,fx)
						f.flush()
						f.close()		
					except BaseException as e:
						Print.error('Exception: ' + str(e))						
						
		# ...................................................						
		# Direct NSP OR XCI
		# ...................................................				
		if args.direct_creation:	
						
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			if args.nodelta:		
				for input in args.nodelta:
					try:
						if input == "true" or input == "True" or input == "TRUE":
							delta=False
						elif input == "false" or input == "False" or input == "FALSE":
							delta=True		
						else:
							delta=False									
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				delta=True					
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filepath in args.direct_creation:
					dir=os.path.dirname(os.path.abspath(filepath))
					ofolder = dir+ '\\'+ 'output'		
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"		
			if args.fexport:		
				for input in args.fexport:
					try:
						if input == "files":
							fx="files"
						else:
							fx="folder"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fx="files"		
			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'					
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656		
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
				
			if args.direct_creation:
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filepath = filelist.readline()
						filepath=os.path.abspath(filepath.rstrip('\n'))						
				else:
					for filepath in args.direct_creation:
						filepath=filepath
				if args.type:
					for input in args.type:		
						if input == "xci" or input == "XCI": 
							export='xci'						
						elif input == "nsp" or input == "NSP": 	
							export='nsp'
						elif input == "both" or input == "BOTH": 
							export='both'													
						else:
							print ("Wrong Type!!!")					
				else:
					if filepath.endswith('.nsp'):
						export='nsp'
					elif filepath.endswith('.xci'):
						export='xci'
					else:
						print ("Wrong Type!!!")
				if args.rename:
					for newname in args.rename:
						newname=newname+'.xxx'
						endfile = os.path.join(ofolder, newname)
				else:
					endfile=os.path.basename(os.path.abspath(filepath))					
				if args.cskip=='False':
					cskip=False
				else:
					cskip=True						

				if filepath.endswith(".nsp"):	
					f = Fs.Nsp(filepath)					
					TYPE=f.nsptype()
					f.flush()
					f.close()
					
					if cskip==True:
						if TYPE=='DLC' or TYPE=='UPDATE':	
							export='nsp'
					if export=='nsp':							
						try:
							print("Processing: " + filepath)
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'nsp'								
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_nsp_direct(buffer,outfile,ofolder,fat,fx,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()
						except BaseException as e:
							Print.error('Exception: ' + str(e))	
					if export=='xci':						
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'xci'
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_xci_direct(buffer,outfile,ofolder,fat,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()						
						except BaseException as e:
							Print.error('Exception: ' + str(e))		
					if export=='both':	
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'nsp'	
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_nsp_direct(buffer,outfile,ofolder,fat,fx,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()						
						except BaseException as e:
							Print.error('Exception: ' + str(e))						
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'xci'
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_xci_direct(buffer,outfile,ofolder,fat,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()						
						except BaseException as e:
							Print.error('Exception: ' + str(e))								
		
				if filepath.endswith(".xci"):	
					if export=='nsp':					
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'nsp'								
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_nsp_direct(buffer,outfile,ofolder,fat,fx,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()						
						except BaseException as e:
							Print.error('Exception: ' + str(e))	
					if export=='xci':						
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'xci'
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							temp=f.c_xci_direct(buffer,outfile,ofolder,fat,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()							
						except BaseException as e:
							Print.error('Exception: ' + str(e))			
					if export=='both':	
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'nsp'							
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_nsp_direct(buffer,outfile,ofolder,fat,fx,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()						
						except BaseException as e:
							Print.error('Exception: ' + str(e))						
						try:
							print("Processing: " + filepath)						
							f = Fs.factory(filepath)
							filename=endfile[:-3]+'xci'
							#print(filename)
							outfile = os.path.join(ofolder, filename)
							#print(f.path)
							f.open(filepath, 'rb')
							f.c_xci_direct(buffer,outfile,ofolder,fat,delta,metapatch,RSV_cap,vkeypatch)
							f.flush()
							f.close()						
						except BaseException as e:
							Print.error('Exception: ' + str(e))	

		# ...................................................						
		# Direct MULTI NSP OR XCI
		# ...................................................		
		if args.direct_multi:
			indent = 1
			index = 0
			tabs = '\t' * indent							
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
	
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
						if not os.path.exists(ofolder):
							os.makedirs(ofolder)								
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filepath in args.direct_multi:
					dir=os.path.dirname(os.path.abspath(filepath))
					ofolder = os.path.join(dir, 'output')
					if not os.path.exists(ofolder):
						os.makedirs(ofolder)						
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"		
			if args.fexport:		
				for input in args.fexport:
					try:
						if input == "files":
							fx="files"
						else:
							fx="folder"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fx="files"					
			if args.nodelta:		
				for input in args.nodelta:
					try:
						if input == "true" or input == "True" or input == "TRUE":
							delta=False
						elif input == "false" or input == "False" or input == "FALSE":
							delta=True		
						else:
							delta=False									
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				delta=True				

			if args.patchversion:
				for input in args.patchversion:
					try:
						metapatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				metapatch = 'false'					
			if args.RSVcap:
				for input in args.RSVcap:
					try:
						RSV_cap = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				RSV_cap = 268435656		
			if args.keypatch:
				for input in args.keypatch:
					try:
						vkeypatch = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				vkeypatch = 'false'	
			export=list()
			if args.type:
				for input in args.type:		
					if input == "xci" or input == "XCI": 
						export.append('xci')
					elif input == "nsp" or input == "NSP": 	
						export.append('nsp')
					elif input == "cnsp" or input == "CNSP": 	
						export.append('cnsp')												
					else:
						print ("Wrong Type!!!")			

			if args.direct_multi:
				if args.text_file:
					tfile=args.text_file
					filelist=list()
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as f: 	
						for line in f:
							fp=line.strip()
							filelist.append(fp)	
					'''		
					for file in filelist:		
						print(file)
						pass
					'''
					prlist=list()	
					print ('Calculating final content:')
					for filepath in filelist:
						if filepath.endswith('.nsp'):
							#print(filepath)
							try:
								c=list()
								f = Fs.Nsp(filepath)	
								if 'nsp' in export or 'cnsp' in export:	
									afolder=False
									if fat=="fat32" and fx=="folder":
										afolder=os.path.join(ofolder,"archfolder")
										if not os.path.exists(afolder):
											os.makedirs(afolder)			
										contentlist=f.get_content(afolder,vkeypatch,delta)
									else:
										contentlist=f.get_content(ofolder,vkeypatch,delta)									
								else:	
									contentlist=f.get_content(False,False,delta)									
								f.flush()
								f.close()		
								if len(prlist)==0:
									for i in contentlist:
										prlist.append(i)
									#print (prlist)
								else:
									for j in range(len(contentlist)):
										notinlist=False
										for i in range(len(prlist)):
											#print (contentlist[j][1])
											#print (contentlist[j][6])
											#pass
											if contentlist[j][1] == prlist[i][1]:
												if contentlist[j][6] > prlist[i][6]:
													del prlist[i]
													prlist.append(contentlist[j])
											else:
												notinlist=True
										if notinlist == True:
											prlist.append(contentlist[j])	
							except BaseException as e:
								Print.error('Exception: ' + str(e))	

						if filepath.endswith('.xci'):
							#print(filepath)
							try:
								c=list()
								f = Fs.Xci(filepath)					
								if 'nsp' in export or 'cnsp' in export:
									contentlist=f.get_content(ofolder,vkeypatch,delta)
								else:	
									contentlist=f.get_content(False,False,delta)									
								f.flush()
								f.close()		
								if len(prlist)==0:
									for i in contentlist:
										prlist.append(i)
									#print (prlist)
								else:
									for j in range(len(contentlist)):
										notinlist=False
										for i in range(len(prlist)):
											#print (contentlist[j][1])
											#print (contentlist[j][6])
											#pass
											if contentlist[j][1] == prlist[i][1]:
												if contentlist[j][6] > prlist[i][6]:
													del prlist[i]
													prlist.append(contentlist[j])
											else:
												notinlist=True
										if notinlist == True:
											prlist.append(contentlist[j])	
							except BaseException as e:
								Print.error('Exception: ' + str(e))											
					'''
					for i in range(len(prlist)):
						print (prlist[i][0])									
						print (prlist[i][1]+' v'+prlist[i][6])	
						for j in prlist[i][4]:
							print (j[0])
							print (j[1])		
						print('////////////////////////////////////////////////////////////')
					'''
					for f in args.direct_multi:
						if f == 'calculate':
							#BASE
							basecount=0; basename='';basever='';baseid='';basefile=''
							updcount=0; updname='';updver='';updid='';updfile=''
							dlccount=0; dlcname='';dlcver='';dlcid='';dlcfile=''
							for i in range(len(prlist)):
								if prlist[i][5] == 'BASE':
									basecount+=1
									if baseid == "":
										basefile=str(prlist[i][0])
										baseid=str(prlist[i][1])
										basever='[v'+str(prlist[i][6])+']'
								if prlist[i][5] == 'UPDATE':
									updcount+=1
									endver=str(prlist[i][6])
									if updid == "":		
										updfile=str(prlist[i][0])									
										updid=str(prlist[i][1])		
										updver='[v'+str(prlist[i][6])+']'										
								if prlist[i][5] == 'DLC':
									dlccount+=1
									if dlcid == "":		
										dlcfile=str(prlist[i][0])								
										dlcid=str(prlist[i][1])	
										dlcver='[v'+str(prlist[i][6])+']'
								if 	basecount !=0:
									bctag=str(basecount)+'G'
								else:
									bctag=''								
								if 	updcount !=0:
									if bctag != '':
										updtag='+'+str(updcount)+'U'									
									else:
										updtag=str(updcount)+'U'
								else:
									updtag=''										
								if 	dlccount !=0:
									if bctag != '' or updtag != '':
										dctag='+'+str(dlccount)+'D'	
									else:										
										dctag=str(dlccount)+'D'	
								else:
									dctag=''									
								ccount='('+bctag+updtag+dctag+')'
							if baseid != "":
								if basefile.endswith('.xci'):							
									f = Fs.Xci(basefile)
								elif basefile.endswith('.nsp'):	
									f = Fs.Nsp(basefile)								
								ctitl=f.get_title(baseid)
								f.flush()
								f.close()										
							elif updid !="":
								if updfile.endswith('.xci'):								
									f = Fs.Xci(updfile)	
								elif updfile.endswith('.nsp'):	
									f = Fs.Nsp(updfile)							
								ctitl=f.get_title(updid)
								f.flush()
								f.close()									
							elif dlcid !="":
								ctitl=get_title	
								if dlcfile.endswith('.xci'):								
									f = Fs.Xci(dlcfile)	
								elif dlcfile.endswith('.nsp'):	
									f = Fs.Nsp(dlcfile)							
								ctitl=f.get_title(dlcid)
								f.flush()
								f.close()									
							else:
								ctitl='UNKNOWN'							
							baseid='['+baseid.upper()+']'
							updid='['+updid.upper()+']'
							dlcid='['+dlcid.upper()+']'	
							if ccount == '(1G)' or ccount == '(1U)' or ccount == '(1D)':
								ccount=''							
							if baseid != "[]":
								if updver != "":							
									endname=ctitl+' '+baseid+' '+updver+' '+ccount
								else:	
									endname=ctitl+' '+baseid+' '+basever+' '+ccount
							elif updid != "[]":
								endname=ctitl+' '+updid+' '+updver+' '+ccount							
							else:
								endname=ctitl+' '+dlcid+' '+dlcver+' '+ccount	
							#print('Filename: '+endname)
						else:
							endname=str(f)

				endname = (re.sub(r'[\/\\\:\*\?]+', '', endname))
				if endname[-1]==' ':
					endname=endname[:-1]
				if fat=="fat32" and fx=="folder":			
					tfname='filename.txt'		
					tfname = os.path.join(ofolder, tfname)			
					with open(tfname,"w", encoding='utf8') as tfile: 	
						tfile.write(endname)				
				if 'nsp' in export:
					oflist=list()
					osizelist=list()
					totSize=0
					c=0
					for i in range(len(prlist)):
						for j in prlist[i][4]:
							oflist.append(j[0])
							osizelist.append(j[1])
							totSize = totSize+j[1]				
					nspheader=sq_tools.gen_nsp_header(oflist,osizelist)						
					endname_x=endname+'.nsp'								
					endfile = os.path.join(ofolder, str(endname_x))	
					print('Filename: '+endname_x)					
					#print(hx(nspheader))
					totSize = len(nspheader) + totSize
					#print(str(totSize))
					if totSize <= 4294901760:
						fat="exfat"			
					if fat=="fat32":
						splitnumb=math.ceil(totSize/4294901760)
						index=0
						endfile=endfile[:-1]+str(index)
					if fx=="folder" and fat=="fat32":
						output_folder = os.path.join(ofolder, "archfolder")			
						endfile = os.path.join(output_folder, "00")	
						if not os.path.exists(output_folder):
							os.makedirs(output_folder)	
					elif fx=="folder" and fat=="exfat":
						ext='.xml'
						if os.path.exists(afolder) and os.path.isdir(afolder):
							for dirpath, dirnames, filenames in os.walk(afolder):				
								for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:				
									filename= os.path.join(afolder,filename)	
									shutil.move(filename,ofolder)	
						shutil.rmtree(afolder, ignore_errors=True)				

					t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)			
					outf = open(endfile, 'w+b')		
					t.write(tabs+'- Writing NSP header...')							
					outf.write(nspheader)		
					t.update(len(nspheader))	
					c=c+len(nspheader)						
					outf.close()
					for filepath in filelist:
						if filepath.endswith('.nsp'):
							try:
								f = Fs.Nsp(filepath)
								for file in oflist:		
									if not file.endswith('xml'):
										outf,index,c = f.append_content(endfile,file,buffer,t,fat,fx,c,index)
								f.flush()
								f.close()		
							except BaseException as e:
								Print.error('Exception: ' + str(e))	
					t.close()								
				if 'xci' in export:
					endname_x=endname+'[nscb].xci'		
					print('Filename: '+endname_x)						
					endfile = os.path.join(ofolder, endname_x)					
					oflist=list()
					osizelist=list()
					ototlist=list()
					totSize=0
					for i in range(len(prlist)):
						for j in prlist[i][4]:
							el=j[0]
							if el.endswith('.nca'):
								oflist.append(j[0])
								#print(j[0])
								totSize = totSize+j[1]	
								#print(j[1])
							ototlist.append(j[0])
					sec_hashlist=list()
					GClist=list()					
					for filepath in filelist:
						if filepath.endswith('.nsp'):
							try:
								f = Fs.Nsp(filepath)
								for file in oflist:
									sha,size,gamecard=f.file_hash(file)
									if sha != False:
										sec_hashlist.append(sha)	
										osizelist.append(size)
										GClist.append([file,gamecard])								
								f.flush()
								f.close()	
							except BaseException as e:
								Print.error('Exception: ' + str(e))										
						if filepath.endswith('.xci'):
							try:
								f = Fs.Xci(filepath)
								for file in oflist:
									sha,size,gamecard=f.file_hash(file)
									if sha != False:
										sec_hashlist.append(sha)	
										osizelist.append(size)	
										GClist.append([file,gamecard])											
								f.flush()
								f.close()	
							except BaseException as e:
								Print.error('Exception: ' + str(e))		
					#print(oflist)
					#print(osizelist)
					#print(sec_hashlist)
					if totSize <= 4294901760:
						fat="exfat"			
					if fat=="fat32":
						splitnumb=math.ceil(totSize/4294901760)
						index=0
						endfile=endfile[:-1]+str(index)
						
					xci_header,game_info,sig_padding,xci_certificate,root_header,upd_header,norm_header,sec_header,rootSize,upd_multiplier,norm_multiplier,sec_multiplier=sq_tools.get_xciheader(oflist,osizelist,sec_hashlist)	 						
					totSize=len(xci_header)+len(game_info)+len(sig_padding)+len(xci_certificate)+rootSize
					#print(hx(xci_header))
					#print(str(totSize))
					c=0
					t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
					t.write(tabs+'- Writing XCI header...')
					outf = open(endfile, 'w+b')
					outf.write(xci_header)
					t.update(len(xci_header))		
					c=c+len(xci_header)
					t.write(tabs+'- Writing XCI game info...')		
					outf.write(game_info)	
					t.update(len(game_info))	
					c=c+len(game_info)
					t.write(tabs+'- Generating padding...')
					outf.write(sig_padding)	
					t.update(len(sig_padding))		
					c=c+len(sig_padding)		
					t.write(tabs+'- Writing XCI certificate...')
					outf.write(xci_certificate)	
					t.update(len(xci_certificate))	
					c=c+len(xci_certificate)		
					t.write(tabs+'- Writing ROOT HFS0 header...')		
					outf.write(root_header)
					t.update(len(root_header))
					c=c+len(root_header)
					t.write(tabs+'- Writing UPDATE partition header...')
					t.write(tabs+'  Calculated multiplier: '+str(upd_multiplier))	
					outf.write(upd_header)
					t.update(len(upd_header))
					c=c+len(upd_header)
					t.write(tabs+'- Writing NORMAL partition header...')
					t.write(tabs+'  Calculated multiplier: '+str(norm_multiplier))			
					outf.write(norm_header)
					t.update(len(norm_header))
					c=c+len(norm_header)
					t.write(tabs+'- Writing SECURE partition header...')
					t.write(tabs+'  Calculated multiplier: '+str(sec_multiplier))		
					outf.write(sec_header)
					t.update(len(sec_header))
					c=c+len(sec_header)	
					outf.close()			
				
					for filepath in filelist:
						if filepath.endswith('.nsp'):
							try:
								GC=False
								f = Fs.Nsp(filepath)
								for file in oflist:			
									if not file.endswith('xml'):		
										for i in range(len(GClist)):
											if GClist[i][0] == file:
												GC=GClist[i][1]
										outf,index,c = f.append_clean_content(endfile,file,buffer,t,GC,vkeypatch,metapatch,RSV_cap,fat,fx,c,index)
								f.flush()
								f.close()		
							except BaseException as e:
								Print.error('Exception: ' + str(e))	
						if filepath.endswith('.xci'):
							try:
								GC=False							
								f = Fs.Xci(filepath)
								for file in oflist:	
									if not file.endswith('xml'):
										for i in range(len(GClist)):
											if GClist[i][0] == file:
												GC=GClist[i][1]									
										outf,index,c = f.append_clean_content(endfile,file,buffer,t,GC,vkeypatch,metapatch,RSV_cap,fat,fx,c,index)
								f.flush()
								f.close()		
							except BaseException as e:
								Print.error('Exception: ' + str(e))	
					t.close()								
				if 'cnsp' in export:
					oflist=list()
					osizelist=list()
					ototlist=list()					
					totSize=0
					c=0
					for i in range(len(prlist)):
						for j in prlist[i][4]:
							el=j[0]
							if el.endswith('.nca') or el.endswith('.xml'):
								oflist.append(j[0])
								#print(j[0])
								osizelist.append(j[1])
								totSize = totSize+j[1]	
								#print(j[1])
							ototlist.append(j[0])	
					nspheader=sq_tools.gen_nsp_header(oflist,osizelist)					
					endname_x=endname+'[rr][nscb].nsp'		
					print('Filename: '+endname_x)						
					endfile = os.path.join(ofolder, endname_x)	
					#print(endfile)						
					#print(hx(nspheader))
					totSize = len(nspheader) + totSize
					if totSize <= 4294901760:
						fat="exfat"			
					if fat=="fat32":
						splitnumb=math.ceil(totSize/4294901760)
						index=0
						endfile=endfile[:-1]+str(index)
					if fx=="folder" and fat=="fat32":
						output_folder = os.path.join(ofolder, "archfolder")			
						endfile = os.path.join(output_folder, "00")	
						if not os.path.exists(output_folder):
							os.makedirs(output_folder)		
					elif fx=="folder" and fat=="exfat":
						ext='.xml'
						if os.path.exists(afolder) and os.path.isdir(afolder):
							for dirpath, dirnames, filenames in os.walk(afolder):				
								for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:				
									filename= os.path.join(afolder,filename)	
									shutil.move(filename,ofolder)	
						shutil.rmtree(afolder, ignore_errors=True)										
					#print(str(totSize))
					t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)			
					outf = open(endfile, 'w+b')		
					t.write(tabs+'- Writing NSP header...')							
					outf.write(nspheader)		
					t.update(len(nspheader))	
					c=c+len(nspheader)						
					outf.close()
					for filepath in filelist:
						if filepath.endswith('.nsp'):
							try:
								f = Fs.Nsp(filepath)
								for file in oflist:			
									if not file.endswith('xml'):					
										outf,index,c = f.append_clean_content(endfile,file,buffer,t,False,vkeypatch,metapatch,RSV_cap,fat,fx,c,index)
								f.flush()
								f.close()		
							except BaseException as e:
								Print.error('Exception: ' + str(e))	
						if filepath.endswith('.xci'):
							try:
								f = Fs.Xci(filepath)
								for file in oflist:						
									if not file.endswith('xml'):									
										outf,index,c = f.append_clean_content(endfile,file,buffer,t,False,vkeypatch,metapatch,RSV_cap,fat,fx,c,index)
								f.flush()
								f.close()		
							except BaseException as e:
								Print.error('Exception: ' + str(e))	
					t.close()								

		# ...................................................						
		# Direct Splitter
		# ...................................................			
		
		if args.direct_splitter:	
						
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
	
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filepath in args.direct_splitter:
					dir=os.path.dirname(os.path.abspath(filepath))
					ofolder = os.path.join(dir, 'output')						
			if args.fat:		
				for input in args.fat:
					try:
						if input == "fat32":
							fat="fat32"
						else:
							fat="exfat"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fat="exfat"		
			if args.fexport:		
				for input in args.fexport:
					try:
						if input == "files":
							fx="files"
						else:
							fx="folder"
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				fx="files"		
				
			if args.direct_splitter:
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filepath = filelist.readline()
						filepath=os.path.abspath(filepath.rstrip('\n'))						
				else:
					for filepath in args.direct_splitter:
						filepath=filepath
				if args.type:
					for input in args.type:		
						if input == "xci" or input == "XCI": 
							export='xci'						
						elif input == "nsp" or input == "NSP": 	
							export='nsp'
						elif input == "both" or input == "BOTH": 
							export='both'													
						else:
							print ("Wrong Type!!!")					
				else:
					if filepath.endswith('.nsp'):
						export='nsp'
					elif filepath.endswith('.xci'):
						export='xci'
					else:
						print ("Wrong Type!!!")
				if args.rename:
					for newname in args.rename:
						newname=newname+'.xxx'
						endfile = os.path.join(ofolder, newname)
				else:
					endfile=os.path.basename(os.path.abspath(filepath))					
				if args.cskip=='False':
					cskip=False
				else:
					cskip=True						

				if filepath.endswith(".nsp"):
					try:				
						f = Fs.Nsp(filepath)					
						f.sp_groupncabyid(buffer,ofolder,fat,fx,export)
						f.flush()
						f.close()		
					except BaseException as e:
						Print.error('Exception: ' + str(e))						
				if filepath.endswith(".xci"):	
					try:				
						f = Fs.Xci(filepath)					
						f.sp_groupncabyid(buffer,ofolder,fat,fx,export)		
						f.flush()
						f.close()				
					except BaseException as e:
						Print.error('Exception: ' + str(e))						

		# ...................................................						
		# Archive to nsp
		# ...................................................						
		if args.archive and args.ifolder:		
			indent = 1
			tabs = '\t' * indent	
			if args.text_file:			
				tfile=args.text_file
				with open(tfile,"r+", encoding='utf8') as tname: 	
					name = tname.readline()			
					name=name+'.nsp'
				endfolder=args.archive	
				endfolder = os.path.join(endfolder, name)
			else:
				endfolder=args.archive				
			try:		
				ruta = args.ifolder
				if not os.path.exists(endfolder):
					os.makedirs(endfolder)		
				#print (ruta)	
				#print (os.path.isdir(ruta))
				print (tabs+"Archiving to output folder...")		
				if os.path.isdir(ruta) == True:
					for dirpath, dnames, fnames in os.walk(ruta):
						#print (fnames)
						for f in fnames:
							filepath = os.path.join(ruta, f)
							#print (f)
							#win32api.SetFileAttributes(filepath,win32con.FILE_ATTRIBUTE_NORMAL)							
							shutil.move(filepath,endfolder)	
				if sys.platform == 'win32':
					win32api.SetFileAttributes(endfolder,win32con.FILE_ATTRIBUTE_ARCHIVE)							
			except BaseException as e:
				Print.error('Exception: ' + str(e))				
		# ...................................................						
		# Join split files
		# ...................................................						
		if args.joinfile:
			indent = 1
			tabs = '\t' * indent			
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				filepath = args.joinfile
				dir=os.path.dirname(os.path.abspath(filepath))
				ofolder = os.path.join(dir, 'output')
			if not os.path.exists(ofolder):
				os.makedirs(ofolder)						
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			filepath = args.joinfile
			file_list=list()
			#print (filepath)
			try:
				if filepath.endswith(".xc0"):
					outname = "output.xci"
					ender=".xc"
				elif filepath.endswith(".ns0"):
					outname = "output.nsp"
					ender=".ns"
				elif filepath[-2:]=="00":				
					outname = "output.nsp"
					ender="0"
				else:
					print ("Not valid file")
				outfile = os.path.join(ofolder, outname)
				#print (outfile)
				ruta=os.path.dirname(os.path.abspath(args.joinfile))			
				for dirpath, dnames, fnames in os.walk(ruta):
					for f in fnames:
						check=f[-3:-1]			
						if check==ender:
							fp = os.path.join(ruta, f)
							file_list.append(fp)
			except BaseException as e:
				Print.error('Exception: ' + str(e))
			totSize = sum(os.path.getsize(file) for file in file_list)
			t = tqdm(total=totSize, unit='B', unit_scale=True, leave=False)
			t.write(tabs+'- Joining files...')			
			index=0				
			outf = open(outfile, 'wb')			
			#print(file_list)
			for file in file_list:
				t.write(tabs+'- Appending: '+ file)
				outfile=file[:-1]+str(index)
				with open(outfile, 'rb') as inf:
					while True:
						data = inf.read(int(buffer))
						outf.write(data)
						t.update(len(data))	
						outf.flush()
						if not data:
							break
				index+=1
			t.close()				
			outf.close()				

		# ...................................................						
		# ZIP
		# ...................................................						
		if args.zippy and args.ifolder:		
			indent = 1
			tabs = '\t' * indent	
			try:		
				outfile=args.zippy
				ruta = args.ifolder				
				endfolder=os.path.dirname(os.path.abspath(outfile))
				if not os.path.exists(endfolder):
					os.makedirs(endfolder)		
				print (tabs+"Packing zip...")		
				if os.path.isdir(ruta) == True:
					for dirpath, dnames, fnames in os.walk(ruta):
						for f in fnames:
							filepath = os.path.join(ruta, f)
							with ZipFile(outfile, 'a') as zippy:
								fp = os.path.join(ruta, f)							
								zippy.write(fp,f)						
			except BaseException as e:
				Print.error('Exception: ' + str(e))				
			
# INFORMATION
		# ...................................................						
		# Show file filelist
		# ...................................................	
		if args.filelist:
			for filename in args.filelist:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.print_file_list()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.print_file_list()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))		
		# ...................................................						
		# Show advance filelist
		# ...................................................	
		if args.ADVfilelist:
			for filename in args.ADVfilelist:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.adv_file_list()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.adv_file_list()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))		

		# ...................................................						
		# Show advance filelist
		# ...................................................	
		if args.ADVcontentlist:
			for filename in args.ADVcontentlist:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.adv_content_list()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.adv_content_list()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))								
								
		# ...................................................						
		# FW REQ INFO
		# ...................................................	
		if args.fw_req:
			for filename in args.fw_req:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.print_fw_req()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.print_fw_req()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))									
		# ...................................................						
		# XCI HEADER
		# ...................................................	
		if args.Read_xci_head:
			for filename in args.Read_xci_head:
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.print_head()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))		
		# ...................................................						
		# ADD CONTENT TO DATABASE
		# ...................................................	
		if args.addtodb:
			if args.db_file:	
				outfile=args.db_file
				dir=os.path.dirname(os.path.abspath(outfile))
				err='errorlog.txt'				
				errfile = os.path.join(dir, err)						
			else:
				for filename in args.addtodb:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = os.path.join(dir, 'output')	
					outname='nutdb.txt'
					outfile = os.path.join(ofolder, outname)		
					err='errorlog.txt'			
					errfile = os.path.join(ofolder, outname)		
					if not os.path.exists(ofolder):
						os.makedirs(ofolder)	
			if args.dbformat:	
				for input in args.dbformat:
					if input == "nutdb":
						outdb = "nutdb"
					elif input == "keyless":
						outdb = "keyless"	
					elif input == "all":
						outdb = "all"								
					else:
						outdb = "extended"	
			else:
				outdb = "extended"	
			if args.addtodb:
				if args.text_file:
					tfile=args.text_file
					with open(tfile,"r+", encoding='utf8') as filelist: 	
						filename = filelist.readline()
						filename=os.path.abspath(filename.rstrip('\n'))
				else:				
					for filename in args.addtodb:
						filename=filename
				if (filename.lower()).endswith('.nsp') or (filename.lower()).endswith('.nsx'):
					try:
						infile=r''
						infile+=filename
						f = Fs.Nsp(filename, 'rb')
						f.addtodb(outfile,outdb)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
						with open(errfile, 'a') as errfile:	
							now=datetime.now()
							date=now.strftime("%x")+". "+now.strftime("%X")								
							errfile.write(date+' Error in "ADD TO DATABASE" function:'+'\n')	
							errfile.write("Route "+str(filename)+'\n')							
							errfile.write('- Exception: ' + str(e)+ '\n')
							
		# ...................................................						
		# Show info
		# ...................................................					
		if args.info:
			print(str(len(args.info)))
			if re.search(r'^[A-Fa-f0-9]+$', args.info.strip(), re.I | re.M | re.S):
				Print.info('%s version = %s' % (args.info.upper(), CDNSP.get_version(args.info.lower())))
			else:
				f = Fs.factory(args.info)
				f.open(args.info, 'r+b')
				f.printInfo()
				'''
				for i in f.cnmt():
					for j in i:
						Print.info(j._path)
						j.rewind()
						buf = j.read()
						Hex.dump(buf)
						j.seek(0x28)
						#j.writeInt64(0)
						Print.info('min: ' + str(j.readInt64()))
				#f.flush()
				#f.close()
				'''				
		# ...................................................						
		# Read cnmt inside nsp or xci
		# ...................................................					

		if args.Read_cnmt:
			for filename in args.Read_cnmt:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.read_cnmt()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.read_cnmt()
						f.flush()
						f.close()														
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.nca'):
					try:
						f = Fs.Nca(filename, 'rb')
						f.read_cnmt()
						f.flush()
						f.close()												
					except BaseException as e:
						Print.error('Exception: ' + str(e))						
						
		# ...................................................						
		# Change Required System Version in a nca file
		# ...................................................									
		if args.patchversion:		
			for input in args.patchversion:
				try:
					number = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))
			else:
				number = 336592896
		if args.set_cnmt_RSV:
			for filename in args.set_cnmt_RSV:
				if filename.endswith('.nca'):
					try:
						f = Fs.Nca(filename, 'r+b')
						f.write_req_system(number)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha=f.calc_pfs0_hash()
						f.flush()
						f.close()
						f = Fs.Nca(filename, 'r+b')
						f.set_pfs0_hash(sha)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha2=f.calc_htable_hash()
						f.flush()
						f.close()						
						f = Fs.Nca(filename, 'r+b')
						f.header.set_htable_hash(sha2)
						f.flush()
						f.close()
						########################
						f = Fs.Nca(filename, 'r+b')
						sha3=f.header.calculate_hblock_hash()
						f.flush()
						f.close()						
						f = Fs.Nca(filename, 'r+b')
						f.header.set_hblock_hash(sha3)
						f.flush()
						f.close()
						########################
						with open(filename, 'r+b') as file:			
							nsha=sha256(file.read()).hexdigest()
						newname=nsha[:32] + '.cnmt.nca'				
						Print.info('New name: ' + newname )
						dir=os.path.dirname(os.path.abspath(filename))
						newpath=dir+ '\\' + newname
						os.rename(filename, newpath)
					except BaseException as e:
						Print.error('Exception: ' + str(e))
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'r+b')
						f.metapatcher(number)					
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))				
		Status.close()
	
		# ...................................................						
		# Change version number from nca
		# ...................................................									

		if args.patchversion:		
			for input in args.patchversion:
				try:
					number = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		else:
			number = 65536
		if args.set_cnmt_version:
			for filename in args.set_cnmt_version:
				if filename.endswith('.nca'):
					try:
						f = Fs.Nca(filename, 'r+b')
						f.write_version(number)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha=f.calc_pfs0_hash()
						f.flush()
						f.close()
						f = Fs.Nca(filename, 'r+b')
						f.set_pfs0_hash(sha)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha2=f.calc_htable_hash()
						f.flush()
						f.close()						
						f = Fs.Nca(filename, 'r+b')
						f.header.set_htable_hash(sha2)
						f.flush()
						f.close()
						########################
						f = Fs.Nca(filename, 'r+b')
						sha3=f.header.calculate_hblock_hash()
						f.flush()
						f.close()						
						f = Fs.Nca(filename, 'r+b')
						f.header.set_hblock_hash(sha3)
						f.flush()
						f.close()
						########################
						with open(filename, 'r+b') as file:			
							nsha=sha256(file.read()).hexdigest()
						newname=nsha[:32] + '.cnmt.nca'				
						Print.info('New name: ' + newname )
						dir=os.path.dirname(os.path.abspath(filename))
						newpath=dir+ '\\' + newname
						os.rename(filename, newpath)
					except BaseException as e:
						Print.error('Exception: ' + str(e))
		Status.close()

		# ..................						
		# Read hfs0
		# ..................									
		if args.Read_hfs0:
			for filename in args.Read_hfs0:
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.readhfs0()
						#f.printInfo()
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
						
		# ...................................................						
		# Update hashes in cnmt file
		# ...................................................									
		if args.update_hash:
			for filename in args.update_hash:
				if filename.endswith('.nca'):
					try:				
						f = Fs.Nca(filename, 'r+b')			
						pfs0_size,block_size,multiplier=f.get_pfs0_hash_data()
						Print.info('block size in bytes: ' + str(hx(block_size.to_bytes(8, byteorder='big'))))
						Print.info('Pfs0 size: ' +  str(hx(pfs0_size.to_bytes(8, byteorder='big'))))
						Print.info('Multiplier: ' +  str(multiplier))			
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha=f.calc_pfs0_hash()
						f.flush()
						f.close()
						f = Fs.Nca(filename, 'r+b')
						f.set_pfs0_hash(sha)
						f.flush()
						f.close()
						############################
						f = Fs.Nca(filename, 'r+b')
						sha2=f.calc_htable_hash()
						f.flush()
						f.close()						
						f = Fs.Nca(filename, 'r+b')
						f.header.set_htable_hash(sha2)
						f.flush()
						f.close()
						########################
						f = Fs.Nca(filename, 'r+b')
						sha3=f.header.calculate_hblock_hash()
						f.flush()
						f.close()						
						f = Fs.Nca(filename, 'r+b')
						f.header.set_hblock_hash(sha3)
						f.flush()
						f.close()
						########################
						with open(filename, 'r+b') as file:			
							nsha=sha256(file.read()).hexdigest()
						newname=nsha[:32] + '.cnmt.nca'				
						Print.info('New name: ' + newname )
						dir=os.path.dirname(os.path.abspath(filename))
						newpath=dir+ '\\' + newname
						os.rename(filename, newpath)
					except BaseException as e:
						Print.error('Exception: ' + str(e))
		Status.close()	
	
								
		# LISTMANAGER

		# ..................						
		# Generate cnmt.xml
		# ..................									
		if args.xml_gen:
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.xml_gen:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '\\'+ 'output'					
			for filename in args.xml_gen:
				if filename.endswith('.nca'):
					try:
						with open(filename, 'r+b') as file:			
							nsha=sha256(file.read()).hexdigest()			
						f = Fs.Nca(filename, 'r+b')	
						f.xml_gen(ofolder,nsha)					
					except BaseException as e:
						Print.error('Exception: ' + str(e))
		Status.close()		
	
									
		# ...................................................						
		# Change line in text file
		# ...................................................									

		if args.change_line:		
			if args.line_number:
				try:
					line_number = int(args.line_number)
				except BaseException as e:
					Print.error('Exception: ' + str(e))
			if args.new_line:
				try:
					new_line = str(args.new_line)
				except BaseException as e:
					Print.error('Exception: ' + str(e))					
			if args.change_line:
				try:
					config_file=os.path.abspath(str(args.change_line))
					lines = open(str(config_file)).read().splitlines()
					lines[line_number] = str(new_line)						
					open(str(config_file),'w').write('\n'.join(lines))
				except BaseException as e:
					Print.error('Exception: ' + str(e))
					
		# ...................................................						
		# Read line in text file
		# ...................................................									

		if args.read_line:	
			if args.new_line:
				try:
					write_line = str(args.new_line)
				except BaseException as e:
					Print.error('Exception: ' + str(e))			
			if args.line_number:
				try:
					line_number = int(args.line_number)
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			if args.read_line:
				try:
					indent = 4
					tabs = '\t' * indent
					config_file=os.path.abspath(str(args.read_line))
					lines = open(str(config_file)).read().splitlines()
					line2read= str(lines[line_number])
					Print.info(write_line + line2read)	
				except BaseException as e:
					Print.error('Exception: ' + str(e))					

		# ...................................................						
		# Generate list of files
		# ...................................................
		#parser.add_argument('-tid', '--titleid', nargs='+', help='Filter with titleid')			
		#parser.add_argument('-bid', '--baseid', nargs='+', help='Filter with base titleid')				
		
		if args.findfile:
			if args.findfile  == 'uinput':
				ruta=input("PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: ")
				if '&' in ruta:
					varout='999'				
				elif len(ruta)<2:
					varout=ruta
				else:
					varout='999'
		
				if args.userinput:
					userfile=args.userinput
				else:	
					userfile='uinput'					

				with open(userfile,"w", encoding='utf8') as userinput: 	
					userinput.write(varout)
			else:
				ruta=args.findfile			
			if ruta[-1]=='"':
				ruta=ruta[:-1]
			if ruta[0]=='"':
				ruta=ruta[1:]	
		
			extlist=list()
			if args.type:
				for t in args.type:
					x='.'+t
					extlist.append(x)
					if x[-1]=='*':
						x=x[:-1]
						extlist.append(x)
			#print(extlist)			
			if args.filter:
				for f in args.filter:
					filter=f	
					
			filelist=list()						
			try:
				fname=""
				binbin='RECYCLE.BIN'
				for ext in extlist:
					#print (ext)
					if os.path.isdir(ruta):
						for dirpath, dirnames, filenames in os.walk(ruta):
							for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:
								fname=""
								if args.filter:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(os.path.join(dirpath, filename))
					else:		
						if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
							filename = ruta
							fname=""
							if args.filter:
								if filter.lower() in filename.lower():
									fname=filename
							else:
								fname=filename		
							if fname != "":
								if binbin.lower() not in filename.lower():					
									filelist.append(filename)	
								
				if args.text_file:	
					tfile=args.text_file
					with open(tfile,"a", encoding='utf8') as tfile: 	
						for line in filelist:
							try:
								tfile.write(line+"\n")
							except:
								continue
				else:			
					for line in filelist:	
						try:					
							print (line)
						except:
							continue							
			except BaseException as e:
				Print.error('Exception: ' + str(e))	

		if args.nint_keys:
			try:	
				sq_tools.verify_nkeys(args.nint_keys)				
			except BaseException as e:
				Print.error('Exception: ' + str(e))					

				
				
				
		#parser.add_argument('-renf','--renamef', help='Rename file with proper name')	

		if args.renamef:
			if args.onlyaddid:
				if args.onlyaddid=="true" or args.onlyaddid == "True" or args.onlyaddid == "TRUE":
					onaddid=True
				else:					
					onaddid=False
			else:
				onaddid=False		
			ruta=args.renamef
			indent = 1
			tabs = '\t' * indent	
			if ruta[-1]=='"':
				ruta=ruta[:-1]
			if ruta[0]=='"':
				ruta=ruta[1:]		
			extlist=list()
			if args.type:
				for t in args.type:
					x='.'+t
					extlist.append(x)
					if x[-1]=='*':
						x=x[:-1]
						extlist.append(x)
			#print(extlist)			
			if args.filter:
				for f in args.filter:
					filter=f	
					
			filelist=list()						
			try:
				fname=""
				binbin='RECYCLE.BIN'
				for ext in extlist:
					#print (ext)
					if os.path.isdir(ruta):
						for dirpath, dirnames, filenames in os.walk(ruta):
							for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:
								fname=""
								if args.filter:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(os.path.join(dirpath, filename))
					else:		
						if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
							filename = ruta
							fname=""
							if args.filter:
								if filter.lower() in filename.lower():
									fname=filename
							else:
								fname=filename		
							if fname != "":
								if binbin.lower() not in filename.lower():					
									filelist.append(filename)	
				'''					
				for f in filelist:
					print(f)
				'''
				print(len(filelist))
				counter=len(filelist)
				for filepath in filelist:
					if filepath.endswith('.nsp'):
						try:
							prlist=list()
							f = Fs.Nsp(filepath)					
							contentlist=f.get_content(False,False,True)
							#print(contentlist)
							f.flush()
							f.close()		
							if len(prlist)==0:
								for i in contentlist:
									prlist.append(i)
								#print (prlist)
							else:
								for j in range(len(contentlist)):
									notinlist=False
									for i in range(len(prlist)):
										#print (contentlist[j][1])
										#print (contentlist[j][6])
										#pass
										if contentlist[j][1] == prlist[i][1]:
											if contentlist[j][6] > prlist[i][6]:
												del prlist[i]
												prlist.append(contentlist[j])
										else:
											notinlist=True
									if notinlist == True:
										prlist.append(contentlist[j])		
						except BaseException as e:
							counter=int(counter)
							counter-=1						
							Print.error('Exception: ' + str(e))		
							continue
						#print(prlist)
					if filepath.endswith('.xci'):
						filepath.strip()
						print("Processing "+filepath)					
						#print(filepath)
						try:
							prlist=list()
							#f = Fs.Xci(filepath)
							f = Fs.factory(filepath)
							f.open(filepath, 'rb')														
							contentlist=f.get_content(False,False,True)
							f.flush()
							f.close()							
							if len(prlist)==0:
								for i in contentlist:
									prlist.append(i)
								#print (prlist)
							else:
								for j in range(len(contentlist)):
									notinlist=False
									for i in range(len(prlist)):
										#print (contentlist[j][1])
										#print (contentlist[j][6])
										#pass
										if contentlist[j][1] == prlist[i][1]:
											if contentlist[j][6] > prlist[i][6]:
												del prlist[i]
												prlist.append(contentlist[j])
										else:
											notinlist=True
									if notinlist == True:
										prlist.append(contentlist[j])		
						except BaseException as e:
							counter=int(counter)
							counter-=1						
							Print.error('Exception: ' + str(e))
							continue	
					if filepath.endswith('.xci') or filepath.endswith('.nsp'):							
						basecount=0; basename='';basever='';baseid='';basefile=''
						updcount=0; updname='';updver='';updid='';updfile=''
						dlccount=0; dlcname='';dlcver='';dlcid='';dlcfile=''
						endname=0; mgame=''
						for i in range(len(prlist)):
							#print(prlist[i][5])
							if prlist[i][5] == 'BASE':
								basecount+=1
								if baseid == "":
									basefile=str(prlist[i][0])
									baseid=str(prlist[i][1])
									basever='[v'+str(prlist[i][6])+']'
							if prlist[i][5] == 'UPDATE':
								updcount+=1
								endver=str(prlist[i][6])
								if updid == "":		
									#print(str(prlist))
									updfile=str(prlist[i][0])									
									updid=str(prlist[i][1])		
									updver='[v'+str(prlist[i][6])+']'										
							if prlist[i][5] == 'DLC':
								dlccount+=1
								if dlcid == "":		
									dlcfile=str(prlist[i][0])								
									dlcid=str(prlist[i][1])	
									dlcver='[v'+str(prlist[i][6])+']'							
							if 	basecount !=0:
								bctag=str(basecount)+'G'	
							else:
								bctag=''								
							if 	updcount !=0:
								if bctag != '':
									updtag='+'+str(updcount)+'U'									
								else:
									updtag=str(updcount)+'U'
							else:
								updtag=''										
							if 	dlccount !=0:
								if bctag != '' or updtag != '':
									dctag='+'+str(dlccount)+'D'	
								else:										
									dctag=str(dlccount)+'D'	
							else:
								dctag=''									
							ccount='('+bctag+updtag+dctag+')'		
						if baseid != "":						
							basename=str(os.path.basename(os.path.abspath(filepath)))
							basename2=basename.upper()							
							check=str('['+baseid+']').upper()	
							#print(basename)	
							#print(check)
							if basename2.find(check) is not -1:				
								print('Filename: '+basename)										
								print(tabs+"> File already has id")
								counter=int(counter)
								counter-=1
								print(tabs+'> Still '+str(counter)+' to go')										
								continue
							if filepath.endswith('.xci'):							
								f = Fs.Xci(basefile)
							elif filepath.endswith('.nsp'):	
								f = Fs.Nsp(basefile)						
							ctitl=f.get_title(baseid)
							#print(ctitl)
							#print(baseid)	
							f.flush()
							f.close()										
						elif updid !="":
							basename=str(os.path.basename(os.path.abspath(filepath)))
							basename2=basename.upper()		
							check=str('['+updid+']').upper()
							if basename2.find(check) is not -1:						
								basename=os.path.basename(os.path.abspath(filepath))	
								print('Filename: '+basename)										
								print(tabs+"> File already has id")	
								counter=int(counter)
								counter-=1
								print(tabs+'> Still '+str(counter)+' to go')										
								continue		
							if filepath.endswith('.xci'):								
								f = Fs.Xci(updfile)	
							elif filepath.endswith('.nsp'):	
								f = Fs.Nsp(updfile)						
							ctitl=f.get_title(updid)
							#print(ctitl)
							#print(updid)	
							f.flush()
							f.close()									
						elif dlcid !="":
							basename=str(os.path.basename(os.path.abspath(filepath)))
							basename2=basename.upper()		
							check=str('['+dlcid+']').upper()							
							if basename2.find(check) is not -1:	
								print('Filename: '+basename)										
								print(tabs+"> File already has id")		
								counter=int(counter)
								counter-=1
								print(tabs+'> Still '+str(counter)+' to go')										
								continue
							if filepath.endswith('.xci'):								
								f = Fs.Xci(dlcfile)	
							elif filepath.endswith('.nsp'):	
								f = Fs.Nsp(dlcfile)						
							ctitl=f.get_title(dlcid)
							f.flush()
							f.close()									
						else:
							ctitl='UNKNOWN'		
						baseid='['+baseid.upper()+']'
						updid='['+updid.upper()+']'
						dlcid='['+dlcid.upper()+']'
						if basecount>1:
							mgame='(mgame)'
						if ccount == '(1G)' or ccount == '(1U)' or ccount == '(1D)':
							ccount=''
						basename=str(os.path.basename(os.path.abspath(filepath)))							
						if baseid != "" and baseid != "[]":
							if updver != "":	
								if onaddid==True:
									endname=basename[:-4]+' '+baseid	
								else:		
									endname=ctitl+' '+baseid+' '+updver+' '+ccount+' '+mgame
							else:
								if onaddid==True:
									endname=basename[:-4]+' '+baseid	
								else:							
									endname=ctitl+' '+baseid+' '+basever+' '+ccount+' '+mgame
						elif updid !="" and updid != "[]":
							if onaddid==True:
								endname=basename[:-4]+' '+updid	
							else:						
								endname=ctitl+' '+updid+' '+updver+' '+ccount+' '+mgame							
						else:
							if onaddid==True:
								endname=basename[:-4]+' '+dlcid	
							else:											
								endname=ctitl+' '+dlcid+' '+dlcver+' '+ccount+' '+mgame	
					while endname[-1]==' ':
						endname=endname[:-1]					
					#endname = re.sub(r'[\/\\\:\*\?\"\<\>\|\.\s™©®()\~]+', ' ', endname)							
					endname = (re.sub(r'[\/\\\:\*\?]+', '', endname))	
					if filepath.endswith('.xci'):								
						endname=endname+'.xci'
					elif filepath.endswith('.nsp'):						
						endname=endname+'.nsp'
					basename=str(os.path.basename(os.path.abspath(filepath)))			
					dir=os.path.dirname(os.path.abspath(filepath))
					newpath=os.path.join(dir,endname)
					if os.path.exists(newpath):
						endname=basename[:-4]+' (needscheck)'+'.xci'
						newpath=os.path.join(dir,endname)	
					if 	ctitl=='UNKNOWN':
						endname=basename[:-4]+' (needscheck)'+'.xci'
						newpath=os.path.join(dir,endname)						
					print('Old Filename: '+basename)						
					print('Filename: '+endname)								
					os.rename(filepath, newpath)	
					counter=int(counter)
					counter-=1
					print(tabs+'File was renamed')						
					print(tabs+'> Still '+str(counter)+' to go')				
			except BaseException as e:
				counter=int(counter)
				counter-=1
				Print.error('Exception: ' + str(e))	
					


		Status.close()		
	
		

	except KeyboardInterrupt:
		Config.isRunning = False
		Status.close()
	except BaseException as e:
		Config.isRunning = False
		Status.close()
		raise

		


