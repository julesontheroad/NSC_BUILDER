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

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'lib')

import Titles
import Fs
import Config
import Print
import Status
import Nsps
from hashlib import sha256
from pathlib import Path
from binascii import hexlify as hx, unhexlify as uhx


if __name__ == '__main__':
	try:
		urllib3.disable_warnings()
		parser = argparse.ArgumentParser()
		parser.add_argument('file',nargs='*')
		
		# INFORMATION
		parser.add_argument('-i', '--info', help='show info about title or file')
		parser.add_argument('--filelist', nargs='+', help='Prints file list from NSP\XCI secure partition')
		parser.add_argument('--ADVfilelist', nargs='+', help='Prints ADVANCED file list from NSP\XCI secure partition')		
		parser.add_argument('--Read_cnmt', nargs='+', help='Read cnmt file inside NSP\XCI')
		parser.add_argument('--fw_req', nargs='+', help='Get information about fw requirements for NSP\XCI')		

		# CNMT Flag funtions		
		parser.add_argument('--set_cnmt_version', nargs='+', help='Changes cnmt.nca version number')	
		parser.add_argument('--set_cnmt_RSV', nargs='+', help='Changes cnmt.nca RSV')	
		parser.add_argument('--update_hash', nargs='+', help='Updates cnmt.nca hashes')	
		parser.add_argument('--xml_gen', nargs='+', help='Generates cnmt.xml')				
		
		# REPACK
		parser.add_argument('-c', '--create', help='create / pack a NSP')
		
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
		parser.add_argument('--updbase', nargs='+', help='Prepare base file to update it')

		# Combinations	
		parser.add_argument('--placeholder_combo', nargs='+', help='Extracts nca files for placeholder nsp')
		parser.add_argument('--license_combo', nargs='+', help='Extracts nca files for license nsp')
		parser.add_argument('--mlicense_combo', nargs='+', help='Extracts nca files for tinfoil license nsp')
		parser.add_argument('--zip_combo', nargs='+', help='Extracts and generate files to make a restore zip')
		
		# Auxiliary
		parser.add_argument('-o', '--ofolder', nargs='+', help='Set output folder for copy instructions')
		parser.add_argument('-b', '--buffer', nargs='+', help='Set buffer for copy instructions')
		parser.add_argument('-ext', '--external', nargs='+', help='Set original nsp or ticket for remove nca titlerights functions')
		parser.add_argument('-pv', '--patchversion', nargs='+', help='Number fot patch Required system version or program, patch or addcontent version')
		parser.add_argument('-kp', '--keypatch', nargs='+', help='patch masterkey to input number')	
		parser.add_argument('-rsvc', '--RSVcap', nargs='+', help='RSV cap when patching. Default is FW4.0')			
		parser.add_argument('-pe', '--pathend', nargs='+', help='Output to subfolder')		
		parser.add_argument('-cskip', nargs='+', help='Skip dlc or update')				

		
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
					titleid=f.getnspid()
					if titleid[-3:] == '000':
						if f.exist_control() == 'TRUE':
							Print.info('BASE')
					if titleid[-3:] == '800':
						Print.info('UPDATE')
					if titleid[-3:] != '800':
						if f.exist_control() == 'FALSE':
							Print.info('DLC')
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
					ofolder = dir+ '/'+ 'output'
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768			
			for filePath in args.XCI_copy_nca_secure:
				f = Fs.factory(filePath)
				f.open(filePath, 'rb')
				f.copy_nca(ofolder,buffer,'secure')
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
					ofolder = dir+ '/'+ 'output'
					
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
				for filename in args.C_clean:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '/'+ 'output'
					
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
			for filename in args.C_clean:
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
				for filename in args.C_clean_ND:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '/'+ 'output'		
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
			for filename in args.C_clean_ND:
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
					ofolder = dir+ '/'+ 'output'
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
				for filename in args.splitter:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '/'+ 'output'		
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
			for filename in args.splitter:
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
					ofolder = dir+ '/'+ 'output'		
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
			for filename in args.updbase:
				if filename.endswith('.nsp'):
					try:
						f = Fs.Nsp(filename, 'rb')
						f.updbase_read(ofolder,buffer,cskip)
						f.flush()
						f.close()	
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
				if filename.endswith('.xci'):
					try:
						f = Fs.factory(filename)
						f.open(filename, 'rb')
						f.updbase_read(ofolder,buffer,cskip)
						f.flush()
						f.close()
					except BaseException as e:
						Print.error('Exception: ' + str(e))
												
# COMBINATIONS
		# ............................................................						
		# Get nca files to make a placeholder in eshop format from NSP
		# ............................................................		
		if args.placeholder_combo:		
			if args.ofolder:		
				for input in args.ofolder:
					try:
						ofolder = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))	
			else:
				for filename in args.placeholder_combo:
					dir=os.path.dirname(os.path.abspath(filename))
					ofolder = dir+ '/'+ 'output'
			if args.buffer:		
				for input in args.buffer:
					try:
						buffer = input
					except BaseException as e:
						Print.error('Exception: ' + str(e))
			else:
				buffer = 32768
			for filename in args.placeholder_combo:
				try:
					f = Fs.Nsp(filename, 'rb')
					f.copy_nca_control(ofolder,buffer)
					f.copy_nca_meta(ofolder,buffer)
					f.flush()
					f.close()
					'''
					#TEST CODE 
					f = Fs.Nsp(filename, 'rb')
					lcontrol=f.copy_nca_control(ofolder,buffer)
					lmeta=f.copy_nca_meta(ofolder,buffer)
					files=lcontrol+lmeta
					f.flush()
					f.close()
					nsp = Fs.Nsp(None, None)
					nsp.path = "placeholder.nsp"
					nsp.pack(files)'''
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
					ofolder = dir+ '/'+ 'output'
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
					ofolder = dir+ '/'+ 'output'
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
					ofolder = dir+ '/'+ 'output'
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
			Print.info('creating ' + args.create)
			nsp = Fs.Nsp(None, None)
			nsp.path = args.create
			nsp.pack(args.file)
			#for filePath in args.file:
			#	Print.info(filePath)

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
						newpath=dir+ '/' + newname
						os.rename(filename, newpath)
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
						newpath=dir+ '/' + newname
						os.rename(filename, newpath)
					except BaseException as e:
						Print.error('Exception: ' + str(e))
		Status.close()
									
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
						newpath=dir+ '/' + newname
						os.rename(filename, newpath)
					except BaseException as e:
						Print.error('Exception: ' + str(e))
		Status.close()	
		
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
					ofolder = dir+ '/'+ 'output'					
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
		
	
	except KeyboardInterrupt:
		Config.isRunning = False
		Status.close()
	except BaseException as e:
		Config.isRunning = False
		Status.close()
		raise

		


