::--------------------------------------------------------------
::OPTION 1
::Route of nut.py. If you have full nut in your pc
::you can choose it's route and erase nut_RTR.py, 
::FS folder and lib folder from ztools
::--------------------------------------------------------------

set NUT_ROUTE=ztools\nut_RTR.py

::--------------------------------------------------------------
::OPTION 2
::Repack option for auto-mode
::nsp->repack as nsp-
::xci->repack as xci-
::both->repack as both
::--------------------------------------------------------------

set vrepack="both"

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

set ncap_rname="false"

::--------------------------------------------------------------------
::OPTION 11
::Python 3 command function
::Set py, python, py -3, python -3, conda ... depending on your system
::--------------------------------------------------------------------

set pycommand="py -3"

::--------------------------------------------------------------
::OPTION 12
::Remove all xml from nsp file. (NOT YET IMPLEMENTED)
::--------------------------------------------------------------
::false->keep xml files inside the nsp
::true->erase or zip xml files

::--------------------------------------------------------------
::OPTION 13
::Tag skipping (NOT YET IMPLEMENTED)
::--------------------------------------------------------------
::false->keep xml files inside the nsp
::true->erase or zip xml files
::set total_tags=3
::set tag_to_skip1=[rr]
::set tag_to_skip2=[xcib]
::set tag_to_skip3=[nxt]

::--------------------------------------------------------------
::OPTION 14
::clean trimmed xci output folder (NOT YET IMPLEMENTED)
::--------------------------------------------------------------



::--------------------------------------------------------------
::OPTION 15
::clean trimmed xci output folder (NOT YET IMPLEMENTED)
::--------------------------------------------------------------



::--------------------------------------------------------------
::OPTION 16
::Types of tags to erase in output xci (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 17
::Types of tags to erase in output nsp (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 18
::Types of tags to ADD in output xci (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 19
::Types of tags to ADD in output nsp (NOT YET IMPLEMENTED)
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 20
::Repack nsp as base + update (NOT YET IMPLEMENTED)
::--------------------------------------------------------------




