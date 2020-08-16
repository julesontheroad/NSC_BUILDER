import os
def userinput(text_file,type=False,userinput=False,filter=False):
	if type!=False:
		type=type.split(' ')
	else:
		type=[]
	raised_error=False
	ruta=input("PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: ")
	if '&' in ruta:
		varout='999'
	elif len(ruta)<2:
		varout=ruta
	else:
		varout='999'

	if userinput:
		userfile=userinput
	else:
		userfile='uinput'

	with open(userfile,"w", encoding='utf8') as userinput:
		userinput.write(varout)

		try:	
			if ruta[-1]=='"':
				ruta=ruta[:-1]
			if ruta[0]=='"':
				ruta=ruta[1:]
		except:
			raised_error=True
		if not os.path.exists(ruta):
			raised_error=True
		if raised_error==False:
			extlist=list()
			if type:
				for t in type:
					if t=="all":
						extlist.append('all')
						continue
					x='.'+t
					extlist.append(x)
					if x[-1]=='*':
						x=x[:-1]
						extlist.append(x)
					elif x==".00":
						extlist.append('00')
			#print(extlist)
			if filter:
				for f in filter:
					filter=f

			filelist=list()
			try:
				fname=""
				binbin='RECYCLE.BIN'
				if not 'all' in extlist:
					for ext in extlist:
						#print (ext)
						if os.path.isdir(ruta):
							for dirpath, dirnames, filenames in os.walk(ruta):
								for filename in [f for f in filenames if f.endswith(ext.lower()) or f.endswith(ext.upper()) or f[:-1].endswith(ext.lower()) or f[:-1].endswith(ext.lower())]:
									fname=""
									if filter:
										if filter.lower() in filename.lower():
											fname=filename
									else:
										fname=filename
									if fname != "":
										if binbin.lower() not in filename.lower():
											filelist.append(os.path.join(dirpath, filename))
						else:
							if ruta.endswith(ext.lower()) or ruta.endswith(ext.upper()) or ruta[:-1].endswith(ext.lower()) or ruta[:-1].endswith(ext.upper()):
								filename = ruta
								fname=""
								if filter:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(filename)
				else:
					# print(ruta)
					if os.path.isdir(ruta):
						for dirpath, dirnames, filenames in os.walk(ruta):
							for filename in [f for f in filenames]:
								fname=""
								if filter:
									if filter.lower() in filename.lower():
										fname=filename
								else:
									fname=filename
								if fname != "":
									if binbin.lower() not in filename.lower():
										filelist.append(os.path.join(dirpath, filename))
					else:
						filename = ruta
						fname=""
						if filter:
							if filter.lower() in filename.lower():
								fname=filename
						else:
							fname=filename
						if fname != "":
							if binbin.lower() not in filename.lower():
								filelist.append(filename)
				with open(text_file,"a", encoding='utf8') as tfile:
					for line in filelist:
						try:
							tfile.write(line+"\n")
						except:
							continue
			except BaseException as e:
				print('Exception: ' + str(e))