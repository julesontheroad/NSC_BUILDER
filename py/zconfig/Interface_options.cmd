::--------------------------------------------------------------
::SET CUSTOM COLOR FOR THE BATCH FILES
::--------------------------------------------------------------
rem color 1F
::--------------------------------------------------------------
::OPTION 1: PROGRAM ROUTES
::--------------------------------------------------------------
set "nut=ztools\squirrel.py"
::python command
set "pycommand=py -3"
::--------------------------------------------------------------
::INTERFACE OPTIONS
::--------------------------------------------------------------
::**************************************************************
::START console minimized with GUI yes\no
::**************************************************************
set "start_minimized=no"
::**************************************************************
::PATH TO BROWSER. USE AUTO, DEFAULT, ADD A PATH
::**************************************************************
::Auto preference order
::1. Chromium portable
::2. Slimjet portable
::3. Chrome or Chromium installed on system
::4. Microsoft Edge
::Default: USes default system brwoser (low compatibility)
::Path: Replace auto to the path to your browser, ending by exe
::Path: Replace auto to the path to an .lnk file(shortcut)
::Path: Add name to .lnk file in ztools\chromium.
::For example "brave.lnk" will redirect to the exe path of brave browser
set "browserpath=auto"
::**************************************************************
::ENABLE VIDEO PLAYBACK
::**************************************************************
set "videoplayback=true"