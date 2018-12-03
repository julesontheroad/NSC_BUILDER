::--------------------------------------------------------------
::SET CUSTOM COLOR FOR THE BATCH FILES
::--------------------------------------------------------------
color 03
::--------------------------------------------------------------
::OPTION 1: FOLDERS
::--------------------------------------------------------------
::work folder
set "w_folder=NSCB_temp"
::output folder
set "fold_output=NSCB_output"
::--------------------------------------------------------------
::OPTION 2: PROGRAM ROUTES
::--------------------------------------------------------------
set "nut=ztools\squirrel.py"
set "xci_lib=ztools\XCI.bat"
set "nsp_lib=ztools\NSP.bat"
set "zip=ztools\7za.exe"
set "hactool=ztools\hactool.exe"
set "hacbuild=ztools\hacbuild.exe"
::--------------------------------------------------------------
::OPTION 3: SQUIRREL OPTIONS
::--------------------------------------------------------------
::python command
set "pycommand=py -3"
::Buffer for the copy functions. 
::Change the number for the number of bytes that works best for you
::32768bytes=32kB
set "buffer=-b 32768"
::Copy function with or without deltas
::--C_clean -> Copy and remove titlerights. Don't skips deltas
::--C_clean_ND-> Copy and remove titlerights skipping deltas
set "nf_cleaner=--C_clean_ND"
::Patch the RequiredSystemVersion so console doesn't ask for updates bigger
::than the required FW to decypher the crypto
::true -> Patch required system version in the meta nca
::false-> Don't patch required system version in the meta nca
set "patchRSV=-pv false"

::--------------------------------------------------------------
::OPTION 4: IMPORTANT FILES
::--------------------------------------------------------------
::Route for game_info file 
set "game_info=zconfig\game_info_preset.ini"
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
set "zip_restore=true"

::--------------------------------------------------------------
::OPTION 8: RENAMING OPTIONS
::--------------------------------------------------------------
REM -> Requires some more work to work as intended without nstool
set "vrename=false"

::--------------------------------------------------------------
::OPTION 9: SKIPS FOR INDIVIDUAL MODE 
::--------------------------------------------------------------
REM -> Not enabled yet. They're here as a reminder for me.
REM -> You can erase option's 9 block.

::Skip NSP repack if input NSP doesn't have titlerights
::true-> skip repacking
::false-> don't skip repacking
REM set "trn_skip=true"
::Skip XCI repack if input XCI have empty update partition
::true-> skip repacking
::false-> don't skip repacking
REM "updx_skip=true"
::Repack as NSP updates and dlc 
::true-> repack as nsp
::false-> repack as xci either way
REM "ngx_skip=true"


