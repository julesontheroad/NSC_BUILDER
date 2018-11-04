#!/usr/bin/python3
# -*- coding: utf-8 -*-
# place this file in your CDNSP directory
# add the following line to the top of your CDNSP.py file:
# from tqdm import tqdm

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


if __name__ == '__main__':
	try:
		urllib3.disable_warnings()
		parser = argparse.ArgumentParser()
		parser.add_argument('file',nargs='*')
		
		# INFORMATION
		parser.add_argument('-i', '--info', help='show info about title or file')
		parser.add_argument('--NSP_filelist', nargs='+', help='Prints file list in an nsp')

		# REPACK
		parser.add_argument('-c', '--create', help='create / pack a NSP')
		
		# nca/nsp identification
		parser.add_argument('--ncatitleid', nargs='+', help='Returns titleid from a nca input')
		parser.add_argument('--ncatype', nargs='+', help='Returns type of a nca file')	
		parser.add_argument('--nsptitleid', nargs='+', help='Returns titleid for a nsp file')
		parser.add_argument('--nsptype', nargs='+', help='Returns type for a nsp file')			
		parser.add_argument('--nsp_htrights', nargs='+', help='Returns true if nsp has titlerights')
		parser.add_argument('--nsp_hticket', nargs='+', help='Returns true if nsp has ticket')
		
		# Remove titlerights functions
		parser.add_argument('--remove-title-rights', nargs='+', help='Removes title rights encryption from all NCA\'s in the NSP.')
		parser.add_argument('--RTRNCA_h_nsp', nargs='+', help='Removes title rights encryption from a single nca reading from original nsp')		
		parser.add_argument('--RTRNCA_h_tick', nargs='+', help='Removes title rights encryption from a single nca reading from extracted ticket')
		
		# Gamecard flag functions
		parser.add_argument('--seteshop', nargs='+', help='Set all nca in an nsp as eshop')
		parser.add_argument('--setcgame', nargs='+', help='Set all nca in an nsp card')	
		parser.add_argument('--seteshop_nca', nargs='+', help='Set a single nca in an nsp as eshop')
		parser.add_argument('--setcgame_nca', nargs='+', help='Set a single nca in an nsp card')	
		parser.add_argument('--cardstate', nargs='+', help='Returns value for isgamecard flag from an nca')	
		
		# Copy functions
		parser.add_argument('--NSP_copy_ticket', nargs='+', help='Extracts ticket from target nsp')
		parser.add_argument('--NSP_copy_nca', nargs='+', help='Extracts all nca files from target nsp')	
		parser.add_argument('--NSP_copy_other', nargs='+', help='Extracts all kinds of files different from nca or ticket from target nsp')
		parser.add_argument('--NSP_copy_xml', nargs='+', help='Extracts xml files from target nsp')
		parser.add_argument('--NSP_copy_cert', nargs='+', help='Extracts cert files from target nsp')
		parser.add_argument('--NSP_copy_jpg', nargs='+', help='Extracts jpg files from target nsp')	
		parser.add_argument('--NSP_copy_cnmt', nargs='+', help='Extracts cnmt files from target nsp')
		parser.add_argument('--NSP_copy_ncap', nargs='+', help='Extracts ncap files from target nsp')			

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
		parser.add_argument('--NSP_c_clean', nargs='+', help='Extracts nca files and removes it.s titlerights from target nsp')
		parser.add_argument('--NSP_c_KeyBlock', nargs='+', help='Extracts keyblock from nsca files with titlerigths  from target nsp')				

		# Combinations	
		parser.add_argument('--placeholder_combo', nargs='+', help='Extracts nca files for placeholder nsp')
		parser.add_argument('--license_combo', nargs='+', help='Extracts nca files for license nsp')
		parser.add_argument('--mlicense_combo', nargs='+', help='Extracts nca files for tinfoil license nsp')
		parser.add_argument('--zip_combo', nargs='+', help='Extracts and generate files to make a restore zip')
		
		# Auxiliary
		parser.add_argument('-o', '--ofolder', nargs='+', help='Set output folder for copy instructions')
		parser.add_argument('-b', '--buffer', nargs='+', help='Set buffer for copy instructions')
		parser.add_argument('-ext', '--external', nargs='+', help='Set original nsp or ticket for remove nca titlerights functions')

		
		args = parser.parse_args()

		Status.start()
		

# NCA/NSP IDENTIFICATION
		# ..................................................
		# Get titleid from nca file
		# ..................................................
		if args.ncatitleid:
			for fileName in args.ncatitleid:		
				try:
					f = Fs.Nca(fileName, 'r+b')
					f.printtitleId()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ..................................................
		# Get type from nca file	
		# ..................................................		
		if args.ncatype:
			for fileName in args.ncatype:		
				try:
					f = Fs.Nca(fileName, 'r+b')
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
		# Identify type of nsp	
		# ..................................................
		if args.nsptype:
			for fileName in args.nsptype:		
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for fileName in args.nsp_htrights:		
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for fileName in args.nsp_hticket:		
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for fileName in args.remove_title_rights:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.removeTitleRights()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ..................................................................			
		# Remove titlerights from an NSP using information from original NSP
		# ..................................................................		
		if args.RTRNCA_h_nsp:
			for fileName in args.external:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					masterKeyRev=f.nspmasterkey()
					titleKeyDec=f.nsptitlekeydec()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
			for fileName in args.RTRNCA_h_nsp:
				try:
					f = Fs.Nca(fileName, 'r+b')
					f.removeTitleRightsnca(masterKeyRev,titleKeyDec)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# .........................................................................						
		# Remove titlerights from an NCA using information from an extracted TICKET
		# .........................................................................			
		if args.RTRNCA_h_tick:
			for fileName in args.external:
				try:
					f = Fs.Ticket(fileName, 'r+b')
					f.open(fileName, 'r+b')
					masterKeyRev=f.getMasterKeyRevision()
					titleKeyDec=f.get_titlekeydec()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
			for fileName in args.RTRNCA_h_tick:
				try:
					f = Fs.Nca(fileName, 'r+b')
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
			for fileName in args.seteshop:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.seteshop()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Set isgamecard flag from all nca in an NSP as CARD
		# ...................................................					
		if args.setcgame:
			for fileName in args.setcgame:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.setcgame()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
		# ...................................................						
		# Get isgamecard flag from a NCA file
		# ...................................................		
		if args.cardstate:
			for fileName in args.cardstate:		
				try:
					f = Fs.Nca(fileName, 'r+b')
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
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.NSP_copy_ticket:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_ticket(ofolder)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Copy all NCA from NSP file
		# ...................................................							
		if args.NSP_copy_nca:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
			for fileName in args.NSP_copy_nca:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ...................................................						
		# Copy OTHER KIND OF FILES from NSP file
		# ...................................................							
		if args.NSP_copy_other:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_other:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_other(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))

		# ...................................................						
		# Copy XML from NSP file
		# ...................................................	
		if args.NSP_copy_xml:		
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))			
			for fileName in args.NSP_copy_xml:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_xml(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ...................................................						
		# Copy CERT from NSP file
		# ...................................................	
		if args.NSP_copy_cert:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_cert:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nsp_cert(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		# ...................................................						
		# Copy JPG from NSP file
		# ...................................................	
		if args.NSP_copy_jpg:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_jpg:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_jpg(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	

		# ...................................................						
		# Copy meta cnmt files from NSP file
		# ...................................................	
		if args.NSP_copy_cnmt:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_cnmt:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_cnmt(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
					
		# ...................................................						
		# Copy control ncap files from NSP file
		# ...................................................	
		if args.NSP_copy_ncap:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_ncap:
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_nca_meta:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca_meta(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Copy all CONTROL NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_control:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_nca_control:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca_control(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))					
		# ...................................................						
		# Copy all MANUAL NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_manual:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))						
			for fileName in args.NSP_copy_nca_manual:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca_manual(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
		# ...................................................						
		# Copy all PROGRAM NCA from NSP file
		# ...................................................						
		if args.NSP_copy_nca_program:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_nca_program:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca_program(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		# ...................................................						
		# Copy all DATA NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_data:	
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_nca_data:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca_data(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))						
		# ...................................................						
		# Copy all PUBLIC DATA NCA from NSP file
		# ...................................................	
		if args.NSP_copy_nca_pdata:
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_nca_pdata:
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
			for fileName in args.NSP_copy_tr_nca:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_tr_nca(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ...................................................						
		# Copy all NCA WITHOUT TITLERIGHTS from target NSP
		# ...................................................						
		if args.NSP_copy_ntr_nca:		
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.NSP_copy_ntr_nca:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_ntr_nca(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		
		# ...................................................						
		# Copy ALL NCA AND CLEAN TITLERIGHTS
		# ...................................................					
		if args.NSP_c_clean:		
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.NSP_c_clean:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					if f.trights_set() == 'FALSE':
						Print.info("NSP DOESN'T HAVE TITLERIGHTS")
						f.copy_nca(ofolder,buffer)	
					if f.trights_set() == 'TRUE':
						if f.exist_ticket() == 'TRUE':
							Print.info("NSP HAS TITLERIGHTS AND TICKET EXISTS")
							f.copyandremove_tr_nca(ofolder,buffer)
						if f.exist_ticket() == 'FALSE':
							Print.error('NSP FILE HAS TITLERIGHTS BUT NO TICKET')		
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
					
		# ........................................................						
		# Copy keyblock from nca files with titlerights from a nsp
		# ........................................................						
		if args.NSP_c_KeyBlock:	
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.NSP_c_KeyBlock:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_KeyBlock(ofolder)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
					
		# ..................................................
		# Identify if nsp has titlerights
		# ..................................................
#		if args.nsp_htrights:
#			for fileName in args.nsp_htrights:		
#				try:
#					f = Fs.Nsp(fileName, 'r+b')
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
#			for fileName in args.nsp_hticket:		
#				try:
#					f = Fs.Nsp(fileName, 'r+b')
#					if f.exist_ticket() == 'TRUE':
#						Print.info('TRUE')
#					if f.exist_ticket() == 'FALSE':
#						Print.info('FALSE')
#				except BaseException as e:
#					Print.error('Exception: ' + str(e))						
	
# COMBINATIONS
		# ............................................................						
		# Get nca files to make a placeholder in eshop format from NSP
		# ............................................................		
		if args.placeholder_combo:		
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.placeholder_combo:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.copy_nca_control(ofolder,buffer)
					f.copy_nca_meta(ofolder,buffer)
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		# ............................................................						
		# Get files to make a [lc].nsp from NSP
		# ............................................................		
		if args.license_combo:		
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.license_combo:
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.mlicense_combo:
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
			for input in args.ofolder:
				try:
					ofolder = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for input in args.buffer:
				try:
					buffer = input
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
			for fileName in args.zip_combo:
				try:
					f = Fs.Nsp(fileName, 'r+b')
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
		if args.NSP_filelist:
			for fileName in args.NSP_filelist:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.print_file_list()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
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
		
		Status.close()
	
	except KeyboardInterrupt:
		Config.isRunning = False
		Status.close()
	except BaseException as e:
		Config.isRunning = False
		Status.close()
		raise



