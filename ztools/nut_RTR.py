#!/usr/bin/python3
# -*- coding: utf-8 -*-
# place this file in your CDNSP directory
# add the following line to the top of your CDNSP.py file:
# from tqdm import tqdm

import argparse
import sys
import os
import urllib3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'lib')

import Titles
import Fs
import Config
import Print
import Status

def submitKeys():
	try:
		import blockchain
	except:
		pass
	for id, t in Titles.items():
		if t.key: #and not t.isUpdate:
			try:
				blockchain.blockchain.suggest(t.id, t.key)
			except BaseException as e:
				Print.info(str(e))

if __name__ == '__main__':
	try:
		urllib3.disable_warnings()
		parser = argparse.ArgumentParser()
		parser.add_argument('file',nargs='*')
		parser.add_argument('--remove-title-rights', nargs='+', help='Removes title rights encryption from all NCA\'s in the NSP.')
		parser.add_argument('--seteshop', nargs='+', help='Set a nca as eshop')
		parser.add_argument('--setcgame', nargs='+', help='Set a nca as card')		
		parser.add_argument('--ncatitleid', nargs='+', help='Returns titleid from a nca input')
		parser.add_argument('--ncatype', nargs='+', help='Returns type of a nca file')	
		parser.add_argument('--cardstate', nargs='+', help='Returns value for isgamecard flag')	
		parser.add_argument('--nsptitleid', nargs='+', help='Returns titleid for a nsp file flag')	
		
		args = parser.parse_args()

		Status.start()
		if args.remove_title_rights:
			for fileName in args.remove_title_rights:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.removeTitleRights()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		Status.close()
		
		if args.seteshop:
			for fileName in args.seteshop:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.seteshop()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))
		if args.setcgame:
			for fileName in args.setcgame:
				try:
					f = Fs.Nsp(fileName, 'r+b')
					f.setcgame()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))				
		if args.ncatitleid:
			for fileName in args.ncatitleid:		
				try:
					f = Fs.Nca(fileName, 'r+b')
					f.printtitleId()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
					
		if args.ncatype:
			for fileName in args.ncatype:		
				try:
					f = Fs.Nca(fileName, 'r+b')
					f.print_nca_type()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))	
					
		if args.cardstate:
			for fileName in args.cardstate:		
				try:
					f = Fs.Nca(fileName, 'r+b')
					f.cardstate()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))		

		if args.nsptitleid:
			for fileName in args.nsptitleid:		
				try:
					f = Fs.Nsp(fileName, 'r+b')
					titleid=f.getnspid()
					f.flush()
					f.close()
				except BaseException as e:
					Print.error('Exception: ' + str(e))							
		
	
	except KeyboardInterrupt:
		Config.isRunning = False
		Status.close()
	except BaseException as e:
		Config.isRunning = False
		Status.close()
		raise



