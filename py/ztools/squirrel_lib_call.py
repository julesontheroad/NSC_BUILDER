# -*- coding: utf-8 -*-

'''
   _____			 _				__
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

import argparse
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'lib')
try:
	sys.path.insert(0, 'private')
except:pass	

# SET ENVIRONMENT
squirrel_dir=os.path.abspath(os.curdir)
NSCB_dir=os.path.abspath('../'+(os.curdir))

if os.path.exists(os.path.join(squirrel_dir,'ztools')):
	NSCB_dir=squirrel_dir
	zconfig_dir=os.path.join(NSCB_dir, 'zconfig')
	ztools_dir=os.path.join(NSCB_dir,'ztools')
	squirrel_dir=ztools_dir
elif os.path.exists(os.path.join(NSCB_dir,'ztools')):
	squirrel_dir=squirrel_dir
	ztools_dir=os.path.join(NSCB_dir, 'ztools')
	zconfig_dir=os.path.join(NSCB_dir, 'zconfig')
else:
	ztools_dir=os.path.join(NSCB_dir, 'ztools')
	zconfig_dir=os.path.join(NSCB_dir, 'zconfig')

if __name__ == '__main__':
	try:
		parser = argparse.ArgumentParser()
		parser.add_argument('file',nargs='*')		
		parser.add_argument('-lib_call','--library_call', nargs='+',  help="Call a library function within squirrel")
		parser.add_argument('-xarg','--explicit_argument', nargs='+', help=argparse.SUPPRESS)
		parser.add_argument('-mtpeval','--mtp_eval_link', nargs='+', help=argparse.SUPPRESS)
		
		args = parser.parse_args()

		if args.file==list():
			args.file=None
			
		if args.library_call:
			if (args.library_call[0]).startswith('Drive.'):
				sys.path.insert(0, 'Drive')
				args.library_call[0]=str(args.library_call[0]).replace("Drive.", "")
			if (args.library_call[0]).startswith('mtp.'):
				sys.path.insert(0, 'mtp')
				args.library_call[0]=str(args.library_call[0]).replace("mtp.", "")		
			if (args.library_call[0]).startswith('cmd.'):
				sys.path.insert(0, 'cmd')
				args.library_call[0]=str(args.library_call[0]).replace("cmd.", "")					
			import secondary
			if args.explicit_argument:
				vret=secondary.call_library(args.library_call,args.explicit_argument)
			else:
				vret=secondary.call_library(args.library_call)
				
		if args.mtp_eval_link:
			tfile=args.mtp_eval_link[0]
			userfile=args.mtp_eval_link[1]			
			link=input("Enter your choice: ")
			link=link.strip()
			if '&' in link:
				varout='999'
			elif len(link)<2:
				varout=link
			else:
				varout='999'
			with open(userfile,"w", encoding='utf8') as userinput:
				userinput.write(varout)		
			if link.startswith('https://1fichier.com'):
				with open(tfile,"a", encoding='utf8') as textfile:
					textfile.write(link+'\n')				
			elif link.startswith('https://drive.google.com'):
				with open(tfile,"a", encoding='utf8') as textfile:
					textfile.write(link+'\n')	
					
	except BaseException as e:
		print(e)