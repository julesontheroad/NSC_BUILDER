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
set "pycommandw=pyw -3"
::--------------------------------------------------------------
::INTERFACE OPTIONS
::--------------------------------------------------------------
::**************************************************************
::START console minimized with GUI yes\no
::**************************************************************
set "start_minimized=yes"
::**************************************************************
::PATH TO BROWSER. USE AUTO, DEFAULT, ADD A PATH
::**************************************************************
::Auto preference order
::1. Chromium portable
::2. Slimjet portable
::3. Chrome or Chromium installed on system
::4. Microsoft Edge
::Default: Uses default system brwoser (low compatibility)
::Path: Replace auto to the path to your browser, ending by exe
::Path: Replace auto to the path to an .lnk file(shortcut)
::Path: Add name to .lnk file in ztools\chromium.
::For example "brave.lnk" will redirect to the exe path launching brave browser
set "browserpath=chrome"
::**************************************************************
::ENABLE VIDEO PLAYBACK
::**************************************************************
set "videoplayback=true"
::**************************************************************
::Initial Height and Width
::**************************************************************
set "height=800"
set "width=740"
::**************************************************************
::Port
::**************************************************************
::auto -> any open port
::rg8000 -> any open port between 8000 and 8999
::Port number -> Fixed port (example 8000)
::Auto and rg8000 allow for multiwindows
set "port=rg8000"
::**************************************************************
::Host
::**************************************************************
::0.0.0.0 -> all hosts
::localhost -> default
::IP -> Some ip
set "host=localhost"
::**************************************************************
::Noconsole
::**************************************************************
::true -> Dettach gui from console
::false -> Attach gui to console
set "noconsole=true"