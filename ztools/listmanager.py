
# -*- coding: utf-8 -*-
import argparse
import sys
import os
import re
import pathlib
import urllib3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'lib')
import Config
import Print
import Status

if __name__ == '__main__':
	try:
		urllib3.disable_warnings()
		parser = argparse.ArgumentParser()
		parser.add_argument('file',nargs='*')
		
		# INFORMATION
		parser.add_argument('-cl', '--change_line', help='Change line in text file')
		parser.add_argument('-rl', '--read_line', help='Read line in text file')		
		parser.add_argument('-ln', '--line_number', help='line number')
		parser.add_argument('-nl', '--new_line', help='new line')
	
		args = parser.parse_args()

		Status.start()		
									
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

		Status.close()	
	
	
	except KeyboardInterrupt:
		Config.isRunning = False
		Status.close()
	except BaseException as e:
		Config.isRunning = False
		Status.close()
		raise

		


