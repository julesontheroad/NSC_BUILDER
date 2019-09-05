import subprocess
import os
import argparse
import listmanager
import Print

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
			process.append(subprocess.Popen(arguments))		
			#print(f)		
		#print(len(process))	
		for p in process: 	
			p.wait()
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

	
def getargs(args):
	tfile=False
	args=str(args)
	args=args.split(', ')
	arguments=list()
	if not isExe==True:
		arguments.append("python")
	arguments.append(squirrel)
	for a in args:
		if not 'None' in a and a != 'file=[]' and not 'threads' in a:
			a=a.split('=')
			#print(a)
			try:
				b=a[1]
				b=b[1:-1]
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