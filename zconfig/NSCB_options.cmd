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
set "nut=ztools\nut_RTR.py"
set "xci_lib=ztools\XCI.bat"
set "nsp_lib=ztools\NSP.bat"
set "zip=ztools\7za.exe"
set "hactool=ztools\hactool.exe
set "hacbuild=ztools\hacbuild.exe"
::--------------------------------------------------------------
::OPTION 3: NUT OPTIONS
::--------------------------------------------------------------
::python command
set "pycommand=py -3"
::Buffer for the copy functions. 
::Change the number for the number of bytes that works best for you
::30720bytes=30kB
set "buffer=-b 30720"
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




















::--------------------------------------------------------------
::OPTION 3
::In case of update or dlc while exporting as xci export as nsp
::true->export as nsp
::false->skip file
::--------------------------------------------------------------

set xnsp_ifnotgame="true"

::--------------------------------------------------------------
::OPTION 4
::Organizing exported items
::line->all files go to output folder
::folder->all files go to separate folders
::--------------------------------------------------------------

set org_out="folder"

::--------------------------------------------------------------
::OPTION 5
::nsp>xci output folder
::"false"-> Use default folder
::Or input route. 
::Example 1: Absolute route
::set fold_xcib=C:\xcib
::Example 2: Relative route
::set fold_xcib=output_xcib
::--------------------------------------------------------------

set fold_xcib=BC_output
::--------------------------------------------------------------
::OPTION 6
::clean nsp output folder
::"false"-> Use default folder
::Or input route. 
::Example 1: Absolute route
::set fold_clnsp=C:\clnsp
::Example 2: Relative route
::set fold_clnsp=o_clean_nsp
::--------------------------------------------------------------

set fold_clnsp=BC_output

::--------------------------------------------------------------
::OPTION 7
::Preserve stripped items (instead of deleting them) as zip file
::--------------------------------------------------------------
::true->preserve files as .zip instead of deleting them
::false->delete stripped files

set z_preserve="true"

::--------------------------------------------------------------
::OPTION 8
::Replace original file
::--------------------------------------------------------------
::true->replace original file
::false->don't replace original file
::ADVICE. TO BE USE ONLY IN MANUAL MODE OR WITH INDIVIDUAL FILES
::DO NOT USE WITH FOLDERS IN AUTO MODE

set f_replace="false"

::--------------------------------------------------------------
::OPTION 9
::Process files by temporarly renaming them to a safe name
::--------------------------------------------------------------
::false->don't rename files
::true->use safename.bat
::agro->rename temporarly to tempname and output as name set in nacp file
::DLCS DON'T HAVE NACP FILE SO AGRO WILL OUTPUT THEM AS [titleid]
set safe_var="true"

::--------------------------------------------------------------
::OPTION 10
::Output final file as game real name looking at control nca
::(If option 9 is set as "agro" it will allways output to the
::real name.
::--------------------------------------------------------------
::false->output as original name/or original name corrected with safe characters
::true->output as "real" name, stored in control nca.
::oinfo->"Only info"-> Use either original filename or safename and add only titleid, version, content tag ...
::DLCS DON'T HAVE NACP FILE SO "true" IN THIS CASE WILL BE REPLACED BY THE "oinfo" OPTION

set ncap_rname="oinfo"

::--------------------------------------------------------------
::OPTION 11
::Remove all xml from nsp file. (NOT YET IMPLEMENTED)
::--------------------------------------------------------------
::false->keep xml files inside the nsp
::true->erase or zip xml files

::--------------------------------------------------------------
::OPTION 12
::Tag skipping (NOT YET IMPLEMENTED)
::--------------------------------------------------------------
::false->keep xml files inside the nsp
::true->erase or zip xml files
::set total_tags=3
::set tag_to_skip1=[rr]
::set tag_to_skip2=[xcib]
::set tag_to_skip3=[nxt]

::--------------------------------------------------------------
::OPTION 12
::clean trimmed xci output folder (NOT YET IMPLEMENTED)
::--------------------------------------------------------------



::--------------------------------------------------------------
::OPTION 13
::clean trimmed xci output folder (NOT YET IMPLEMENTED)
::--------------------------------------------------------------



::--------------------------------------------------------------
::OPTION 14
::Types of tags to erase in output xci (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 15
::Types of tags to erase in output nsp (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 16
::Types of tags to ADD in output xci (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 17
::Types of tags to ADD in output nsp (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 18
::Repack nsp as base + update (NOT YET IMPLEMENTED)
::--------------------------------------------------------------




