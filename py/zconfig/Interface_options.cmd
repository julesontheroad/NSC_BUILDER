::--------------------------------------------------------------
::SET CUSTOM COLOR FOR THE BATCH FILES
::--------------------------------------------------------------
rem color 1F
::--------------------------------------------------------------
::OPTION 1: PROGRAM ROUTES
::--------------------------------------------------------------
set "nut=ztools\squirrel.py"
::--------------------------------------------------------------
::OPTION 2: INTERFACE OPTIONS
::--------------------------------------------------------------
::python command
set "pycommand=py -3"
::START console minimized with GUI yes\no
set "start_minimized=no"
::Path to browser. Use auto, default or add a path
::Auto preference order
::1. Chromium portable
::2. Slimjet portable
::3. Chrome or Chromium installed on system
::4. Microsoft Edge
::Default: USes default system brwoser (low compatibility)
::Path: Replace auto to the path to your browser, ending by exe
set "browserpath=auto"