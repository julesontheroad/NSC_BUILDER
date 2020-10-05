import subprocess
import os
import sys
import argparse
import listmanager
import Print
import inspect
from tqdm import tqdm

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

testroute1=os.path.join(squirrel_dir, "squirrel.py")
testroute2=os.path.join(squirrel_dir, "squirrel.exe")
isExe=False
if os.path.exists(testroute1):
	squirrel=testroute1
	isExe=False
elif os.path.exists(testroute2):	
	squirrel=testroute2
	isExe=True
allowedlist=['--renamef','--addtodb','--addtodb_new','--verify','--compress']

#print (squirrel)
	
def call_library(args,xarg=None):	
	vret=None
	try:
		if args[0]:
			components = args[0].split('.')
			if len(components)>1:
				vret=call_class(args,xarg)
				try:
					if str(args[2]).lower() == 'print' or str(args[3]).lower() == 'print':
						print(str(vret))
					else:
						print(str(vret))		
				except:	
					return 	vret				
			else:
				library=args[0]
				lib=__import__(library)
	except:pass	
	
	if len(args)>1:	
		if xarg==None:
			try:	
				if args[2]:		
					var=args[2]
					try:
						var=var.split(',')	
						for i in range(len(var)):
							if str(var[i]).lower()=='true':
								var[i]=True
							elif str(var[i]).lower()=='false':
								var[i]=False
							elif str(var[i]).lower()=='none':
								var[i]=None									
							elif '=' in var[i]:
								try:
									asignation=var[i].split("=")
									if str(asignation[1]).lower()=='true':
										var[i]=True
									elif str(asignation[1]).lower()=='false':	
										var[i]=False
									elif str(asignation[1]).lower()=='none':
										var[i]=None												
									else:
										toks=list()
										toks=[pos for pos, char in enumerate(var[i]) if char == '=']
										indx=toks[0]+1
										var[i]=(var[i])[indx:]
								except:pass
							else:pass
					except:pass
			except:	
				var=None
		else:
			var=xarg
			for i in range(len(var)):
				try:
					if str(var[i]).lower()=='true':
						var[i]=True
					elif str(var[i]).lower()=='false':
						var[i]=False
					elif str(var[i]).lower()=='none':
						var[i]=None									
					elif '=' in var[i]:
						try:
							asignation=var[i].split("=")
							if str(asignation[1]).lower()=='true':
								var[i]=True
							elif str(asignation[1]).lower()=='false':	
								var[i]=False
							elif str(asignation[1]).lower()=='none':
								var[i]=None			
							else:
								toks=list()
								toks=[pos for pos, char in enumerate(var[i]) if char == '=']
								indx=toks[0]+1
								var[i]=(var[i])[indx:]
						except:pass
					else:pass
				except:pass	
		try:	
			if args[1]:
				fimport=args[1]
				if library=='Interface' and fimport=='start':
					try:
						if str(var[6]).lower()=='true':
							debug_write(True)
					except:
						debug_write(False)
				if library=='Interface' and fimport=='server':
					try:
						if str(var[4]).lower()=='true':
							debug_write(True)
					except:
						debug_write(False)						
				function = getattr(__import__(library,fromlist=[fimport]), fimport)	
				if var==None:
					vret=function()
				else:
					vret=function(*var)					
		except BaseException as e:
			Print.error('Exception: ' + str(e))	
		try:
			if str(args[2]).lower() == 'print' or str(args[3]).lower() == 'print':
				print(str(vret))
			else:
				print(str(vret))		
		except:	
			return 	vret
			
def call_class(args,xarg=None):			
	vret=None
	try:
		if args[0]:
			components = args[0].split('.')
			library=components[0]
			lib = __import__(library)
			importedclass = getattr(lib, components[1])		
	except:pass	

	if len(args)>1:	
		if xarg==None:
			try:	
				if args[2]:		
					var=args[2]
					try:
						var=var.split(',')	
						for i in range(len(var)):
							if str(var[i]).lower()=='true':
								var[i]=True
							elif str(var[i]).lower()=='false':
								var[i]=False
							elif str(var[i]).lower()=='none':
								var[i]=None									
							elif '=' in var[i]:
								try:
									asignation=var[i].split("=")
									if str(asignation[1]).lower()=='true':
										var[i]=True
									elif str(asignation[1]).lower()=='false':	
										var[i]=False
									elif str(asignation[1]).lower()=='none':
										var[i]=None												
									else:
										var[i]=asignation[1]
								except:pass
							else:pass
					except:pass
			except:	
				var=None
		else:
			var=xarg
			for i in range(len(var)):
				try:
					if str(var[i]).lower()=='true':
						var[i]=True
					elif str(var[i]).lower()=='false':
						var[i]=False
					elif str(var[i]).lower()=='none':
						var[i]=None									
					elif '=' in var[i]:
						try:
							asignation=var[i].split("=")
							if str(asignation[1]).lower()=='true':
								var[i]=True
							elif str(asignation[1]).lower()=='false':	
								var[i]=False
							elif str(asignation[1]).lower()=='none':
								var[i]=None			
							else:
								var[i]=asignation[1]
						except:pass
					else:pass
				except:pass	
		try:	
			if args[1]:
				fimport=args[1]
				function = getattr(importedclass, fimport)
				if var==None:
					vret=function()
				else:
					vret=function(*var)					
		except BaseException as e:
			Print.error('Exception: ' + str(e))	
		try:
			if str(args[2]).lower() == 'print' or str(args[3]).lower() == 'print':
				print(str(vret))
			else:
				print(str(vret))		
		except:	
			return 	vret
			
def debug_write(state):
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
	web_folder=os.path.join(ztools_dir,'web')
	debug_folder=os.path.join(web_folder,'_debug_')
	flag_file=os.path.join(debug_folder,'flag')		
	with open(flag_file,'wt') as tfile:	
		tfile.write(str(state))	
		
def route(args,workers,silence=False):
	arguments,tfile=getargs(args)
	#print(arguments)
	# print(tfile)
	if tfile==False:
		if silence==False:
			process=subprocess.Popen(arguments)	
		else:
			process=subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)				
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
		ind2=False		
		try:
			ind2=arguments.index('--db_file')
			ind2+=1	
			sub_r=arguments[ind2]
		except:pass					
		process=list();sub_r=arguments[ind2];c=0	
		if ind2 !=False:
			if not os.path.isdir(sub_r) and not str(sub_r).endswith('all_DB.txt'):  
				folder=os.path.dirname(os.path.abspath(sub_r))
				ruta=os.path.abspath(os.path.join(folder, "temp"))		
			else:	
				folder=os.path.dirname(os.path.abspath(sub_r))			
				ruta=os.path.abspath(os.path.join(folder, "temp"))	
			if not os.path.exists(ruta):
				os.makedirs(ruta)				
		for f in filelist:	
			arguments[ind]=f
			#print (arguments)
			if ind2 !=False:
				if not os.path.isdir(sub_r) and not str(sub_r).endswith('all_DB.txt'):  			
					fi=str(os.path.basename(os.path.abspath(sub_r)))+'_'+str(c)	
					ruta2=os.path.abspath(os.path.join(ruta,fi))
					arguments[ind2]=ruta2
					#print(ruta2)
				else:
					ruta2=os.path.abspath(os.path.join(ruta,str(c)))	
					if not os.path.exists(ruta2):
						os.makedirs(ruta2)		
					fi=os.path.join(ruta2,'all_DB.txt')
					arguments[ind2]=fi
					#print(arguments)
				c+=1	
			if silence==False:
				process.append(subprocess.Popen(arguments))	
			else:
				process.append(subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE))	
			#print(process)
			#print(f)		
		#print(len(process))	
		for p in process: 	
			p.wait()
			# print(str(p.poll()))
			while p.poll()==None:
				if p.poll()!=None:
					p.terminate();	
					
		if ind2 !=False:			
			if not os.path.isdir(sub_r) and not str(sub_r).endswith('all_DB.txt'): 			
				for i in range(int(workers-1)): 
					fi=str(os.path.basename(os.path.abspath(sub_r)))+'_'+str(i)	
					t=os.path.join(ruta,fi)		
					if os.path.exists(t):		
						with open(t,"r+", encoding='utf8') as filelist:
							if not os.path.exists(sub_r):						
								with open(sub_r,"w", encoding='utf8') as dbt: 
									for line in filelist:
										dbt.write(line)		
							else:
								c=0
								with open(sub_r,"a", encoding='utf8') as dbt: 
									for line in filelist:
										if not c==0:
											dbt.write(line)										
										c+=1						
					i+=1
				try:
					os.remove(ruta) 	
				except BaseException as e:
					Print.error('Exception: ' + str(e))
					pass
			else:
				include=['extended_DB.txt','nutdb_DB.txt','keyless_DB.txt','simple_DB.txt']
				for i in range(int(workers-1)): 
					for input in include:
						ruta2=os.path.abspath(os.path.join(ruta,str(i)))	
						t=os.path.join(ruta2,input)	
						t2=os.path.join(folder,input)	
						# print(t)
						# print(t2)
						if os.path.exists(t):		
							with open(t,"r+", encoding='utf8') as filelist:
								if not os.path.exists(t2):						
									with open(t2,"w", encoding='utf8') as dbt: 
										for line in filelist:
											dbt.write(line)		
								else:
									c=0
									with open(t2,"a", encoding='utf8') as dbt: 
										for line in filelist:
											if not c==0:
												dbt.write(line)										
											c+=1		
						i+=1	
					try:
						os.remove(t) 	
					except:pass	
					try:
						os.remove(ruta2) 	
					except:pass													
		try:
			os.remove(ruta) 	
		except:pass	
			
		listmanager.striplines(tfile,number=workers,counter=True)							

	
def getargs(args,separate_list=True,current=False,pos=0,tothreads=1):

	tfile=False
	# args=str(args)
	# args=args.split(', ')
	arguments=list()
	if not isExe==True:
		arguments.append(sys.executable)
	arguments.append(squirrel)
	
	if args.compress!=None and current!=False:
		nargs=list()
		args.text_file=None
		f=None
		f=current
		nargs.append(f)		
		nargs.append(args.compress[-1])	
		args.compress=nargs
		args.position=str(pos)
		try:
			tothreads=int(tothreads)
			if tothreads>1:
				args.n_instances=str(tothreads)
		except:pass
			
	for a in vars(args):
		if not 'None' in str(a) and str(a) != 'file=[]' and not 'threads' in str(a) and not 'pararell' in str(a):
			# a=a.split('=')
			# print(a)
			# try:
				# b=a[1]
				# b=b[1:-1]
			# except:
				# b=None
				# pass
			b=getattr(args, a)
			if isinstance(b, list):
				c=0
				for x in b:
					if x=="" and c==0:
						b=""
						c+=1
						break
			# print(a)
			# if a == 'type':
				# print(b)
			if a=='text_file' and separate_list==True:
				tfile=b
			else:
				if b!=None:			
					a='--'+a
					arguments.append(a)
					if isinstance(b, list):
						for x in b:
							if x!='':
								arguments.append(x)	
						# narg=narg[:-1]
						# arguments.append(narg)	
						# print(narg)
					else:
						arguments.append(b)
	return arguments,tfile		
	
def pass_command(args,silence=False):	
	c=0
	if not args.findfile:
		items=listmanager.counter(args.text_file)
		process=list()
		while items!=0:
			if c==0:
				c+=1
			else:
				print("")			
			listmanager.printcurrent(args.text_file)
			arguments,nonevar=getargs(args,separate_list=False)
			# print(arguments)
			if silence==False:
				process.append(subprocess.Popen(arguments))
			else:
				process.append(subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE))	
			for p in process: 	
				p.wait()
				# print(str(p.poll()))
				while p.poll()==None:
					if p.poll()!=None:
						p.terminate();		
			listmanager.striplines(args.text_file,number=1,counter=True)	
			items-=1	
		return items
	else:
		arguments,nonevar=getargs(args,separate_list=False)
		# print(arguments)
		process=list()
		if silence==False:
			process.append(subprocess.Popen(arguments))
		else:
			process.append(subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE))			
		for p in process: 	
			p.wait()
			# print(str(p.poll()))
			while p.poll()==None:
				if p.poll()!=None:
					p.terminate();				
		return 0	

def pararell(args,workers,silence=False,nocls=False):	
	from subprocess import call
	from time import sleep
	c=0;workers=int(workers);tfile=args.text_file;args0=args;f=False
	filelist=listmanager.read_lines_to_list(tfile,all=True)
	if not args.findfile:
		items=listmanager.counter(args.text_file);index=0
		process=list()
		while items!=0:
			if c==0:
				c+=1
			else:
				#print("")
				pass

			from colorama import Fore	
			colors=Fore.__dict__
			p=0;threads=0			
			for r in range(workers):
				if index != items:
					k=0;l=p
					for col in colors:
						if l>len(colors):
							l=l-len(colors)			
						color=colors[col]
						if k==(l+1):
							break
						else:
							k+=1 	 					
					#listmanager.printcurrent(tfile)
					try:
						f=filelist[index]
					except:break
					tq = tqdm(leave=False,position=0)
					#tq = tqdm(leave=False,position=0,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, color))
					tq.write('Opening thread for '+f)
					threads+=1
					tq.close() 	
					tq = tqdm(total=1, unit='|', leave=True,position=0,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, Fore.RESET))
					tq.update(1)
					tq.close()  
					opworkers=workers
					if items<workers:
						opworkers=items
					arguments,nonevar=getargs(args,separate_list=False,current=f,pos=p,tothreads=opworkers)	
					#print(arguments)				
					f=False
					args=args0
					#print(arguments)
					if silence==False:
						process.append(subprocess.Popen(arguments))
					else:
						process.append(subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
					index+=1
					p+=1
			
			pr_n=0
			for pr in process: 	
				#pr.wait()
				#call('clear' if os.name =='posix' else 'cls') 				
				# print(str(p.poll()))
				while pr.poll()==None:
					sleep(3)
					if nocls==False:
						if os.name =='posix':
							call('clear')#linux
						else:
							try:
								call('cls')#macos
							except:
								print ("\n" * 100)
								os.system('cls')#windows
						listmanager.counter(tfile,doprint=True)	
					p=0;index2=index-workers
					for r in range(workers):
						if index2 != items:
							k=0;l=p
							for col in colors:
								if l>len(colors):
									l=l-len(colors)			
								color=colors[col]
								if k==(l+1):
									break
								else:
									k+=1 	 					
							#listmanager.printcurrent(tfile)
							try:
								f=filelist[index2]
							except:break
							if nocls==False:
								tq = tqdm(leave=False,position=0)
								# tq = tqdm(leave=False,position=0,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, color))
								tq.write('Opening thread for '+f)
								tq.close() 	
								tq = tqdm(total=1, unit='|', leave=True,position=0,bar_format="{l_bar}%s{bar}%s{r_bar}" % (color, Fore.RESET))
								tq.update(1)
								tq.close()  
								index2+=1;p+=1
					if pr.poll()!=None:
						pr.terminate();						
					pr_n+=1	
			if nocls==False:			
				clear_Screen()
			if nocls==False:	
				listmanager.striplines(tfile,number=threads,counter=False)		
			else:
				listmanager.striplines(tfile,number=threads,counter=True,jump_line=True)					
			items-=threads	
			if items<0:
				items=0	
		return items		 		


def clear_Screen():
	from subprocess import call
	from time import sleep
	if os.name =='posix':
		call('clear')#linux
	else:
		try:
			call('cls')#macos
		except:
			print ("\n" * 100)
			os.system('cls')#windows