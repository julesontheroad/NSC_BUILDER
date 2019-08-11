indent = 1
tabs = '\t' * indent	

def striplines(textfile,number=1,counter=False):
	#print(textfile)
	number=int(number)
	filelist=list()
	c=0;i=0
	with open(textfile,'r', encoding='utf8') as f:
		for line in f:		
			if i>(number-1):
				fp=line.strip()
				filelist.append(fp)	
				c+=1	
			else:
				i+=1	

	with open(textfile,"w", encoding='utf8') as f:
		for ln in filelist:
			f.write(ln+'\n')
	if counter == True:
		print('...................................................')
		print('STILL '+str(c)+' FILES TO PROCESS')
		print('...................................................')
			
def counter(textfile):
	counter=0
	with open(textfile,'r', encoding='utf8') as f:
		for line in f:
			counter+=1	
	return counter

def printcurrent(textfile,number=1,counter=False):
	currentline=''
	with open(textfile,'r', encoding='utf8') as f:
		i=0
		for line in f:
			print(line)
			break