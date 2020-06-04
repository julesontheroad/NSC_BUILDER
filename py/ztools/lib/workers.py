def back_check_files():
	import os
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
	
	import sys	
	sys.stdout = open(os.path.join(debug_folder,'temp.txt'), 'w')
	sys.stderr = sys.stdout
	import nutdb
	nutdb.check_files()