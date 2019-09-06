::--------------------------------------------------------------
::SET CUSTOM COLOR FOR THE BATCH FILES
::--------------------------------------------------------------
color 1F
::--------------------------------------------------------------
::OPTION 1: FOLDERS
::--------------------------------------------------------------
::work folder
set "w_folder=NSCB_temp"
::output folder
set "fold_output=NSCB_output"
::zip folder
set "zip_fold=NSCB_zips"
::--------------------------------------------------------------
::OPTION 2: PROGRAM ROUTES
::--------------------------------------------------------------
set "nut=ztools\squirrel.py"
set "xci_lib=ztools\XCI.bat"
set "nsp_lib=ztools\NSP.bat"
set "zip=ztools\squirrel.py"
set "listmanager=ztools\squirrel.py"
set "batconfig=ztools\NSCB_config.bat"
set "batdepend=ztools\install_dependencies.bat"
set "infobat=ztools\info.bat"
::--------------------------------------------------------------
::OPTION 3: SQUIRREL OPTIONS
::--------------------------------------------------------------
::python command
set "pycommand=py -3"
::Buffer for the copy functions. 
::Change the number for the number of bytes that works best for you
::32768=32kB ; 65536=64kB
set "buffer=-b 65536"
::Copy function with or without deltas
::--C_clean -> Copy and remove titlerights. Don't skips deltas
::--C_clean_ND-> Copy and remove titlerights skipping deltas
set "nf_cleaner=--C_clean_ND"
set "skdelta=-ND true"
::than the required FW to decypher the crypto
::true -> Patch required system version in the meta nca
::false-> Don't patch required system version in the meta nca
set "patchRSV=-pv false"
set "capRSV=--RSVcap 268435656"
::--------------------------------------------------------------
::OPTION 4: IMPORTANT FILES
::--------------------------------------------------------------
::
set "uinput=ztools\uinput"
::Route for keys.txt 
set "dec_keys=ztools\keys.txt"
::--------------------------------------------------------------
::OPTION 5: REPACK OPTIONS
::--------------------------------------------------------------
::Repack option for auto-mode
::nsp->repack as nsp-
::xci->repack as xci-
::both->repack as both
set "vrepack=both"
::Type of repack for folders
::indiv->repack multiple input files as multiple output file. INDIVIDUAL MODE
::multi->repack multiple input files as single output file. MULTI-MODE
set "fi_rep=multi"
::--------------------------------------------------------------
::OPTION 6: MANUAL MODE INTRO
::--------------------------------------------------------------
::Repack mode that is shown first in manual mode
::indiv->individual packing of files
::multi->multi-pack mode
::split->splitter mode
::update->update mode
::choose->prompt to choose the mode to enter
set "manual_intro=choose"
::--------------------------------------------------------------
::OPTION 7: Zip files
::--------------------------------------------------------------
::ZIP FILES FOR UPCOMING RESTORE MODE
::true->zip the needed files
::false->don't zip the files
set "zip_restore=false"

::--------------------------------------------------------------
::OPTION 8: PATCH IF KEYGENERATION IS BIGGER THAN
::--------------------------------------------------------------
:: CHANGE ENCRYPTION TO THE SET KEYGENERATION IN AUTO-MODE
:: Don't change encryption -> vkey = false
:: "1.0.0"			  	   -> vkey = 0
:: "2.0.0 - 2.3.0"         -> vkey = 1
:: "3.0.0" 		   	 	   -> vkey = 2
:: "3.0.1 - 3.0.2" 		   -> vkey = 3
:: "4.0.0 - 4.1.0"		   -> vkey = 4
:: "5.0.0 - 5.1.0" 		   -> vkey = 5
:: "6.0.0-4 - 6.1.0" 	   -> vkey = 6 
:: "6.2.0"	    	 	   -> vkey = 7
:: "7.0.0 - 8.01"	  	   -> vkey = 8
:: "6.2.0 - ?"	  	 	   -> vkey = 9
set "vkey=-kp false"

::--------------------------------------------------------------
::OPTION 10: AUTO-EXIT
::--------------------------------------------------------------
:: If set at true the program will auto-exit in manual mode
set "va_exit=false"

::--------------------------------------------------------------
::OPTION 11: SKIP RSV AND KEYGENERATION CHANGE PROPMT
::--------------------------------------------------------------
:: Skip RequiredSystemVersion and keygeneration prompts while
:: in manual mode
set "skipRSVprompt=false"

::--------------------------------------------------------------
::OPTION 12: SD FORMAT
::--------------------------------------------------------------
:: Choose to pack xci or for exfat cards or fat32 cards
::fatype can be fat32 or exfat
::fexport pack split nsp as files (sxos rommenu) or as folder (other installers)
set "fatype=-fat exfat"
set "fexport=-fx files"

::--------------------------------------------------------------
::OPTION 13: END FOLDER ORGANIZATION
::--------------------------------------------------------------
::Organization in the output folder.
::inline -> All files go to root folder
::subfolder -> Files go to folder named by game
set "oforg=inline"

::--------------------------------------------------------------
::OPTION 14: NEW OR LEGACY
::--------------------------------------------------------------
::SETS THE PROGRAM STARTUP FOR NEW MODES OR LEGACY MODES
::value is new or legacy
set "NSBMODE=new"

::--------------------------------------------------------------
::OPTION 15: ROMANIZE JAPANESE AND CHINESE TITLES
::--------------------------------------------------------------
::romanice ->TRUE
::don't romanize -> FALSE
set "romaji=TRUE"