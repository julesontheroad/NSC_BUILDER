import subprocess
import os
import argparse

sqdir=os.path.abspath(os.curdir)
squirrel=os.path.join(sqdir, "squirrel.py")
	
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
		pass
	
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
			b=(a[1])[1:-1]
			if a[0]=='text_file':
				tfile=b
			else:	
				a='--'+a[0]
				arguments.append(a)
				arguments.append(b)
	return arguments,tfile		
			