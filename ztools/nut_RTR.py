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
		
		args = parser.parse_args()

		Status.start()
		Print.info('                        ,;:;;,')
		Print.info('                       ;;;;;')
		Print.info('               .=\',    ;:;;:,')
		Print.info('              /_\', "=. \';:;:;')
		Print.info('              @=:__,  \,;:;:\'')
		Print.info('                _(\.=  ;:;;\'')
		Print.info('               `"_(  _/="`')
		Print.info('                `"\'')

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
	
	except KeyboardInterrupt:
		Config.isRunning = False
		Status.close()
	except BaseException as e:
		Config.isRunning = False
		Status.close()
		raise

	Print.info('fin')

