import subprocess
import os
import argparse
import listmanager
import _thread as thread

sqdir=os.path.abspath(os.curdir)
squirrel=os.path.join(sqdir, "squirrel.py")
allowedlist=['--renamef','--rebuild_nsp']
	
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
		listmanager.striplines(tfile,number=workers)		
		commands=list();i=0
		for allw in allowedlist:
			if allw in arguments:
				ind=arguments.index(allw)
				ind+=1	
				break
		ind2=False		
		try:
			ind2=arguments.index('--ofolder')
			ind2+=1	
		except:pass	
		c=0;outf=arguments[ind2]
		for f in filelist:				
			arguments[ind]=f
			if ind2 !=False:
				arguments[ind2]=outf+'_'+str(c)
				commands.append(arguments)
		processlist = [Popen(process, shell=True) for process in commands]				
		for p in processlist: 
			p.communicate()
	
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
			