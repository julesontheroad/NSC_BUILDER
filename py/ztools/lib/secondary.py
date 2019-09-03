import subprocess
import os
import argparse
import listmanager

sqdir=os.path.abspath(os.curdir)
squirrel=os.path.join(sqdir, "squirrel.py")
allowedlist=['--renamef','--addtodb','--addtodb_new']
	
def route(args,workers):
	arguments,tfile=getargs(args)
	#print(arguments)
	if tfile==False:
		process=subprocess.Popen(arguments)	
		while process.poll()==None and process2.poll()==None:
			if process.poll()!=None:
				process.terminate();
			if process2.poll()!=None:	
				process2.terminate();	
		#op,oe=process.communicate();#print (op);print (oe)
		#process.terminate();process2.terminate()
	else:
		filelist=listmanager.read_lines_to_list(tfile,number=workers)		
		commands=list();i=0
		#print(filelist)
		for allw in allowedlist:
			if allw in arguments:
				ind=arguments.index(allw)
				ind+=1	
				break
		process=list()		
		for f in filelist:				
			arguments[ind]=f			
			process.append(subprocess.Popen(arguments))		
			#print(f)		
		#print(len(process))	
		for p in process: 	
			p.wait()
			while p.poll()==None:
				if p.poll()!=None:
					p.terminate();	
		listmanager.striplines(tfile,number=workers,counter=True)							

	
	
def getargs(args):
	tfile=False
	args=str(args)
	args=args.split(', ')
	arguments=list()
	arguments.append("python")
	arguments.append(squirrel)
	for a in args:
		if not 'None' in a and a != 'file=[]' and not 'threads' in a:
			a=a.split('=')
			#print(a)
			try:
				b=str(a[1])[1:-1]
			except:
				b=None
				pass
			if a[0]=='text_file':
				tfile=b
			else:
				if b!=None:			
					a='--'+a[0]
					arguments.append(a)
					arguments.append(b)
				else:
					a=a[0]
					arguments.append(a)					
	return arguments,tfile		
			