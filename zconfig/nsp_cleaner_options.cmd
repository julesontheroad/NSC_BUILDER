::--------------------------------------------------------------
::OPTION 1
::Route of nut.py. If you have full nut in your pc
::you can choose it's route and erase nut_RTR.py, 
::FS folder and lib folder from ztools
::--------------------------------------------------------------

set NUT_ROUTE=ztools/nut_RTR.py

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

set f_replace="false"

::--------------------------------------------------------------
::OPTION 10
::clean trimmed xci output folder
::--------------------------------------------------------------



::--------------------------------------------------------------
::OPTION 11
::clean trimmed xci output folder
::--------------------------------------------------------------



::--------------------------------------------------------------
::OPTION 12
::Types of tags to erase in output xci
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 13
::Types of tags to erase in output nsp
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 14
::Types of tags to ADD in output xci
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 15
::Types of tags to ADD in output nsp
::--------------------------------------------------------------


::--------------------------------------------------------------
::OPTION 16
::Repack nsp as base + update [PROPOSED]
::--------------------------------------------------------------




