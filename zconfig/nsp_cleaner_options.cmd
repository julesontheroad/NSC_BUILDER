::OPTION 1
::Route of nut.py. If you have full nut in your pc
::you can choose it's route and erase nut_RTR.py, 
::FS folder and lib folder from ztools
set NUT_ROUTE=ztools/nut_RTR.py

::OPTION 2
::Repack option for auto-mode
::nsp->repack as nsp-
::xci->repack as xci-
::both->repack as both
set vrepack="both"

::OPTION 3
::In case of update or dlc while exporting as xci export as nsp
::true->export as nsp
::false->skip file
set xnsp_ifnotgame="true"