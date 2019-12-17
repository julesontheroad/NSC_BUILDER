:sc1
set "op_file=%~1"
set "listmanager=%~2"
set "batdepend=%~3"
cls
call :logo
echo ********************************************************
echo OPTION - CONFIGURATION
echo ********************************************************
echo Input "1" for AUTO-MODE OPTIONS
echo Input "2" for GLOBAL AND MANUAL OPTIONS
echo Input "3" to VERIFY KEYS.TXT 
echo Input "4" to UPDATE NUTDB
echo Input "5" to INTERFACE OPTIONS
echo.
echo Input "c" to read CURRENT PROFILE
echo Input "d" to set DEFAULT SETTINGS
echo Input "0" to go back to the MAIN PROGRAM
echo .......................................................
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto sc2
if /i "%bs%"=="2" goto sc3
if /i "%bs%"=="3" goto verify_keys
if /i "%bs%"=="4" goto update_nutdb
if /i "%bs%"=="5" goto interface

if /i "%bs%"=="c" call :curr_set1
if /i "%bs%"=="c" call :curr_set2
if /i "%bs%"=="c" echo.
if /i "%bs%"=="c" pause

if /i "%bs%"=="d" call :def_set1
if /i "%bs%"=="d" call :def_set2
if /i "%bs%"=="d" echo.
if /i "%bs%"=="d" pause

if /i "%bs%"=="0" goto salida
echo WRONG CHOICE
echo.
goto sc1

:sc2
cls
call :logo
echo ********************************************************
echo AUTO-MODE - CONFIGURATION
echo ********************************************************
echo Input "1" to change REPACK configuration
echo Input "2" to change FOLDER'S TREATMENT 
echo Input "3" to change RSV patching configuration
echo Input "4" to change KEYGENERATION configuration
echo.
echo Input "c" to read CURRENT AUTO-MODE SETTINGS
echo Input "d" to set DEFAULT AUTO-MODE SETTINGS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo .......................................................
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto op_repack
if /i "%bs%"=="2" goto op_pfolder
if /i "%bs%"=="3" goto op_RSV
if /i "%bs%"=="4" goto op_KGEN

if /i "%bs%"=="c" call :curr_set1
if /i "%bs%"=="c" echo.
if /i "%bs%"=="c" pause

if /i "%bs%"=="d" call :def_set1
if /i "%bs%"=="d" echo.
if /i "%bs%"=="d" pause
if /i "%bs%"=="d" goto sc1

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida
echo WRONG CHOICE
echo.
goto sc2

:op_repack
cls
call :logo
echo *******************************************************
echo REPACK configuration
echo *******************************************************
echo REPACK OPTION FOR AUTO-MODE
echo .......................................................
echo Input "1" to repack as NSP
echo Input "2" to repack as XCI
echo Input "3" to repack as BOTH
echo Input "4" to remove DELTAS from updates
echo Input "5" to REBUILD NSPS by cnmt order
echo.
echo Input "b" to return to AUTO-MODE - CONFIGURATION
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo .......................................................
echo.
set /p bs="Enter your choice: "
set "v_rep=none"
if /i "%bs%"=="1" set "v_rep=nsp"
if /i "%bs%"=="2" set "v_rep=xci"
if /i "%bs%"=="3" set "v_rep=both"
if /i "%bs%"=="4" set "v_rep=nodelta"
if /i "%bs%"=="5" set "v_rep=rebuild"

if /i "%bs%"=="b" goto sc2
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_rep%"=="none" echo WRONG CHOICE
if "%v_rep%"=="none" echo.
if "%v_rep%"=="none" goto op_repack

set v_rep="vrepack=%v_rep%"
set v_rep="%v_rep%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "57" -nl "set %v_rep%"
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "57" -nl "Line in config was changed to: "
echo.
pause
goto sc2

:op_pfolder
cls
call :logo
echo **********************************************************************
echo FOLDER'S TREATMENT
echo **********************************************************************
echo HOW TO TREAT FOLDER'S IN AUTO-MODE
echo ......................................................................
echo Input "1" to repack folder's files individually (single-content file)
echo Input "2" to repack folder's files together (multi-content file)
echo Input "3" to repack folder's files by BASE ID
echo.
echo Input "b" to return to AUTO-MODE - CONFIGURATION
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ......................................................................
echo.
set /p bs="Enter your choice: "
set "v_fold=none"
if /i "%bs%"=="1" set "v_fold=indiv"
if /i "%bs%"=="2" set "v_fold=multi"
if /i "%bs%"=="3" set "v_fold=baseid"

if /i "%bs%"=="b" goto sc2
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_fold%"=="none" echo WRONG CHOICE
if "%v_fold%"=="none" echo.
if "%v_fold%"=="none" goto op_pfolder

set v_fold="fi_rep=%v_fold%"
set v_fold="%v_fold%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "61" -nl "set %v_fold%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "61" -nl "Line in config was changed to: "
echo.
pause
goto sc2

:op_RSV
cls
call :logo
echo ***************************************************************************
echo REQUIRED SYSTEM VERSION PATCHING
echo ***************************************************************************
echo PATCH REQUIRED_SYSTEM_VERSION IN THE META NCA (AUTO-MODE)
echo ...........................................................................
echo Patches the RequiredSystemVersion so console doesn't ask for updates bigger
echo the required FW to decypher the crypto
echo.
echo Input "1" to PATCH Required System Version in the meta nca
echo Input "2" to leave Required System Version UNCHANGED
echo.
echo Input "b" to return to AUTO-MODE - CONFIGURATION
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_RSV=none"
if /i "%bs%"=="1" set "v_RSV=-pv true"
if /i "%bs%"=="2" set "v_RSV=-pv false"

if /i "%bs%"=="b" goto sc2
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_RSV%"=="none" echo WRONG CHOICE
if "%v_RSV%"=="none" echo.
if "%v_RSV%"=="none" goto op_RSV

set v_RSV="patchRSV=%v_RSV%"
set v_RSV="%v_RSV%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "41" -nl "set %v_RSV%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "41" -nl "Line in config was changed to: "
echo.
pause
goto sc2

:op_KGEN
cls
call :logo
echo ***************************************************************************
echo PATCH IF KEYGENERATION IS BIGGER THAN
echo ***************************************************************************
echo CHANGE KEYGENERATION IF BIGGER THAN THE SET NUMBER(AUTO-MODE)
echo ...........................................................................
echo Changes the kegeneration and recalculates the keyblock to use a lower 
echo masterkey to decrypt the nca.
echo.
echo Input "f" to not change the keygeneration
echo Input "0" to change top keygeneration to 0 (FW 1.0)
echo Input "1" to change top keygeneration to 1 (FW 2.0-2.3)
echo Input "2" to change top keygeneration to 2 (FW 3.0)
echo Input "3" to change top keygeneration to 3 (FW 3.0.1-3.02)
echo Input "4" to change top keygeneration to 4 (FW 4.0.0-4.1.0)
echo Input "5" to change top keygeneration to 5 (FW 5.0.0-5.1.0)
echo Input "6" to change top keygeneration to 6 (FW 6.0.0-6.1.0)
echo Input "7" to change top keygeneration to 7 (FW 6.2.0)
echo Input "8" to change top keygeneration to 8 (FW 7.0.0-8.0.1)
echo Input "9" to change top keygeneration to 9 (FW 8.1.0)
echo Input "10" to change top keygeneration to 10 (FW 9.0.0-9.01)
echo Input "11" to change top keygeneration to 11 (FW 9.1.0)
echo.
echo Input "b" to return to AUTO-MODE - CONFIGURATION
echo Input "c" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_KGEN=none"
set "v_CAPRSV=0"
if /i "%bs%"=="f" set "v_KGEN=-kp false"
if /i "%bs%"=="0" set "v_KGEN=-kp 0"
if /i "%bs%"=="0" set "v_CAPRSV=--RSVcap 0"
if /i "%bs%"=="1" set "v_KGEN=-kp 1"
if /i "%bs%"=="1" set "v_CAPRSV=--RSVcap 65796"
if /i "%bs%"=="2" set "v_KGEN=-kp 2"
if /i "%bs%"=="2" set "v_CAPRSV=--RSVcap 201327002"
if /i "%bs%"=="3" set "v_KGEN=-kp 3"
if /i "%bs%"=="3" set "v_CAPRSV=--RSVcap 201392178"
if /i "%bs%"=="4" set "v_KGEN=-kp 4"
if /i "%bs%"=="4" set "v_CAPRSV=--RSVcap 268435656"
if /i "%bs%"=="5" set "v_KGEN=-kp 5"
if /i "%bs%"=="5" set "v_CAPRSV=--RSVcap 335544750"
if /i "%bs%"=="6" set "v_KGEN=-kp 6"
if /i "%bs%"=="6" set "v_CAPRSV=--RSVcap 402653494"
if /i "%bs%"=="7" set "v_KGEN=-kp 7"
if /i "%bs%"=="7" set "v_CAPRSV=--RSVcap 404750336"
if /i "%bs%"=="8" set "v_KGEN=-kp 8"
if /i "%bs%"=="8" set "v_CAPRSV=--RSVcap 469762048"
if /i "%bs%"=="9" set "v_KGEN=-kp 9"
if /i "%bs%"=="9" set "v_CAPRSV=--RSVcap 537919488"
if /i "%bs%"=="10" set "v_KGEN=-kp 10"
if /i "%bs%"=="10" set "v_CAPRSV=--RSVcap 603979776"
if /i "%bs%"=="11" set "v_KGEN=-kp 11"
if /i "%bs%"=="11" set "v_CAPRSV=--RSVcap 605028352"

if /i "%bs%"=="b" goto sc2
if /i "%bs%"=="c" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_RSV%"=="none" echo WRONG CHOICE
if "%v_RSV%"=="none" echo.
if "%v_RSV%"=="none" goto op_RSV

set v_KGEN="vkey=%v_KGEN%"
set v_KGEN="%v_KGEN%"
set v_CAPRSV="capRSV=%v_CAPRSV%"
set v_CAPRSV="%v_CAPRSV%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "95" -nl "set %v_KGEN%" 
%pycommand% "%listmanager%" -cl "%op_file%" -ln "42" -nl "set %v_CAPRSV%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "95" -nl "Line in config was changed to: "
%pycommand% "%listmanager%" -rl "%op_file%" -ln "42" -nl "Line in config was changed to: "
echo.
pause
goto sc2

:sc3
cls
call :logo
echo **********************************************
echo GLOBAL OPTIONS - CONFIGURATION
echo **********************************************
echo Input "1" to change text and background COLOR
echo Input "2" to change WORK FOLDER's name
echo Input "3" to change OUTPUT FOLDER's name
echo Input "4" to change DELTA files treatment
echo Input "5" to change ZIP configuration (LEGACY)
echo Input "6" to change AUTO-EXIT configuration
echo Input "7" to skip KEY-GENERATION PROMPT
echo Input "8" to set file stream BUFFER
echo Input "9" to set file FAT32\EXFAT options
echo Input "10" to how to ORGANIZE output files
echo Input "11" to set NEW MODE OR LEGACY MODE
echo Input "12" to ROMANIZE names when using direct-multi
echo Input "13" to TRANSLATE game description lines in file info
echo Input "14" to change number of WORKERS IN THREADED OPERATIONS (TEMPORARLY DISABLED) 
echo Input "15" to setup NSZ COMPRESSION USER PRESET
echo Input "16" to setup COMPRESSED XCI EXPORT FORMAT
echo.
echo Input "c" to read CURRENT GLOBAL SETTINGS
echo Input "d" to set DEFAULT GLOBAL SETTINGS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Enter your choice: "

if /i "%bs%"=="1" goto op_color
if /i "%bs%"=="2" goto op_wfolder
if /i "%bs%"=="3" goto op_ofolder
if /i "%bs%"=="4" goto op_delta
if /i "%bs%"=="5" goto op_zip
if /i "%bs%"=="6" goto op_aexit
if /i "%bs%"=="7" goto op_kgprompt
if /i "%bs%"=="8" goto op_buffer
if /i "%bs%"=="9" goto op_fat
if /i "%bs%"=="10" goto op_oforg
if /i "%bs%"=="11" goto op_nscbmode
if /i "%bs%"=="12" goto op_romanize
if /i "%bs%"=="13" goto op_translate
if /i "%bs%"=="14" goto op_threads
if /i "%bs%"=="15" goto op_NSZ1
if /i "%bs%"=="16" goto op_NSZ3

if /i "%bs%"=="c" call :curr_set2
if /i "%bs%"=="c" echo.
if /i "%bs%"=="c" pause

if /i "%bs%"=="d" call :def_set2
if /i "%bs%"=="d" echo.
if /i "%bs%"=="d" pause
if /i "%bs%"=="d" goto sc1

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

echo WRONG CHOICE
echo.
goto sc3

:op_color
cls
call :logo
echo ********************************************************
echo COLOR - CONFIGURATION                                
echo ********************************************************
echo --------------------------------------------------------
echo FOREGROUND COLOR (TEXT COLOR)                      
echo --------------------------------------------------------
echo Input "1" to change text color to BRIGHT WHITE (DEFAULT)
echo Input "2" to change text color to BLACK
echo Input "3" to change text color to BLUE
echo Input "4" to change text color to GREEN
echo Input "5" to change text color to AQUA
echo Input "6" to change text color to RED
echo Input "7" to change text color to PURPLE
echo Input "8" to change text color to YELLOW
echo Input "9" to change text color to WHITE
echo Input "10" to change text color to GRAY
echo Input "11" to change text color to LIGHT BLUE
echo Input "12" to change text color to LIGHT GREEN
echo Input "13" to change text color to LIGHT AQUA
echo Input "14" to change text color to LIGHT RED
echo Input "15" to change text color to LIGHT PURPLE
echo Input "16" to change text color to LIGHT YELLOW
echo.
echo Input "d" to set default color configuration
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bd="Enter your choice: "

set "v_colF=F"
if /i "%bd%"=="1" set "v_colF=F"
if /i "%bd%"=="2" set /a "v_colF=0"
if /i "%bd%"=="3" set /a "v_colF=3"
if /i "%bd%"=="4" set /a "v_colF=1"
if /i "%bd%"=="5" set /a "v_colF=2"
if /i "%bd%"=="6" set /a "v_colF=4"
if /i "%bd%"=="7" set /a "v_colF=5"
if /i "%bd%"=="8" set /a "v_colF=6"
if /i "%bd%"=="9" set /a "v_colF=7"
if /i "%bd%"=="10" set /a "v_colF=8"
if /i "%bd%"=="11" set /a "v_colF=9"
if /i "%bd%"=="12" set "v_colF=A"
if /i "%bd%"=="13" set "v_colF=B"
if /i "%bd%"=="14" set "v_colF=C"
if /i "%bd%"=="15" set "v_colF=D"
if /i "%bd%"=="16" set "v_colF=E"

if /i "%bd%"=="d" set "v_colF=F"
if /i "%bd%"=="d" set /a "v_colB=1"
if /i "%bd%"=="d" goto do_set_col

if /i "%bd%"=="b" goto sc3
if /i "%bd%"=="0" goto sc1
if /i "%bd%"=="e" goto salida

echo -----------------------------------------------------
echo BACKGROUND COLOR
echo -----------------------------------------------------
echo Input "1" to change background color to BLUE (DEFAULT)
echo Input "2" to change background color to BLACK
echo Input "3" to change background color to GREEN
echo Input "4" to change background color to AQUA
echo Input "5" to change background color to RED
echo Input "6" to change background color to PURPLE
echo Input "7" to change background color to YELLOW
echo Input "8" to change background color to WHITE
echo Input "9" to change background color to GRAY
echo Input "10" to change background color to BRIGHT WHITE
echo Input "11" to change background color to LIGHT BLUE
echo Input "12" to change background color to LIGHT GREEN
echo Input "13" to change background color to LIGHT AQUA
echo Input "14" to change background color to LIGHT RED
echo Input "15" to change background color to LIGHT PURPLE
echo Input "16" to change background color to LIGHT YELLOW
echo.
echo Input "d" to set default color configuration
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Enter your choice: "

set /a "v_colB=1"
if /i "%bs%"=="1" set /a "v_colB=1"
if /i "%bs%"=="2" set /a "v_colB=0"
if /i "%bs%"=="3" set /a "v_colB=2"
if /i "%bs%"=="4" set /a "v_colB=3"
if /i "%bs%"=="5" set /a "v_colB=4"
if /i "%bs%"=="6" set /a "v_colB=5"
if /i "%bs%"=="7" set /a "v_colB=6"
if /i "%bs%"=="8" set /a "v_colB=7"
if /i "%bs%"=="9" set /a "v_colB=8"
if /i "%bs%"=="10" set "v_colB=F"
if /i "%bs%"=="11" set /a "v_colB=9"
if /i "%bs%"=="12" set "v_colB=A"
if /i "%bs%"=="13" set "v_colB=B"
if /i "%bs%"=="14" set "v_colB=C"
if /i "%bs%"=="15" set "v_colB=D"
if /i "%bs%"=="16" set "v_colB=E"

if /i "%bs%"=="d" set "v_colF=F"
if /i "%bs%"=="d" set /a "v_colB=1"
if /i "%bs%"=="d" goto do_set_col

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

:do_set_col
setlocal enabledelayedexpansion
set "v_col=!v_colB!!v_colF!"
color !v_col!
%pycommand% "%listmanager%" -cl "%op_file%" -ln "3" -nl "color !v_col!"
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "3" -nl "Line in config was changed to: "
endlocal
echo.
pause
goto sc3

:op_wfolder
cls
call :logo
echo ***********************************
echo WORK FOLDER's name - CONFIGURATION
echo ***********************************
echo Input "1" to set default work folder's name
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Or type a new name: "
set "v_wf=%bs%"
if /i "%bs%"=="1" set "v_wf=NSCB_temp"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

set v_wf="w_folder=%v_wf%"
set v_wf="%v_wf%"

%pycommand% "%listmanager%" -cl "%op_file%" -ln "8" -nl "set %v_wf%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "8" -nl "Line in config was changed to: "
echo.
pause
goto sc3


:op_ofolder
cls
call :logo
echo *************************************
echo OUTPUT FOLDER's name - CONFIGURATION
echo *************************************
echo Input "1" to set default output folder's name
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Or type a new name: "
set "v_of=%bs%"
if /i "%bs%"=="1" set "v_of=NSCB_output"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

set v_of="fold_output=%v_of%"
set v_of="%v_of%"

%pycommand% "%listmanager%" -cl "%op_file%" -ln "10" -nl "set %v_of%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "10" -nl "Line in config was changed to: "
echo.
pause
goto sc3


:op_delta
cls
call :logo
echo ***************************************************************************
echo DELTA files treatment - CONFIGURATION
echo ***************************************************************************
echo SKIP DELTA NCA FILES WHEN EXTRACTING UPDATES
echo ...........................................................................
echo The deltas serve to convert previous updates into new ones, updates can
echo incorporate the full update + deltas. Deltas are nocive and innecessary
echo for xci, while they serve to install faster nsp and convert previous
echo updates to the new one. Without deltas your old update will stay in the
echo system and you'll need to uninstall it.
echo.
echo Input "1" to skip deltas (default configuration)
echo Input "2" to repack deltas
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_delta=none"
if /i "%bs%"=="1" set "v_delta=--C_clean_ND"
if /i "%bs%"=="1" set "v_delta2_=-ND true"
if /i "%bs%"=="2" set "v_delta=--C_clean"
if /i "%bs%"=="2" set "v_delta2_=-ND false"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_delta%"=="none" echo WRONG CHOICE
if "%v_delta%"=="none" echo.
if "%v_delta%"=="none" goto op_delta

set v_delta="nf_cleaner=%v_delta%"
set v_delta="%v_delta%"
set v_delta2_="skdelta=%v_delta2_%"
set v_delta2_="%v_delta2_%"

%pycommand% "%listmanager%" -cl "%op_file%" -ln "36" -nl "set %v_delta%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "36" -nl "Line in config was changed to: "
echo.
%pycommand% "%listmanager%" -cl "%op_file%" -ln "37" -nl "set %v_delta2_%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "37" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_zip
cls
call :logo
echo ***************************************************************************
echo ZIP FILES GENERATION
echo ***************************************************************************
echo GENERATE ZIP FILES WITH KEYBLOCK AND FILE INFORMATION
echo ...........................................................................
echo.
echo Input "1" to generate zip files
echo Input "2" to not generate zip files (default configuration) 
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_gzip=none"
if /i "%bs%"=="1" set "v_gzip=true"
if /i "%bs%"=="2" set "v_gzip=false"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_gzip%"=="none" echo WRONG CHOICE
if "%v_gzip%"=="none" echo.
if "%v_gzip%"=="none" goto op_zip

set v_gzip="zip_restore=%v_gzip%"
set v_gzip="%v_gzip%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "78" -nl "set %v_gzip%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "78" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_aexit
cls
call :logo
echo ***************************************************************************
echo AUTO-EXIT CONFIGURATION (MANUAL MODES)
echo ***************************************************************************
echo Auto exit after processing files or ask to process next.
echo ...........................................................................
echo.
echo Input "1" to set off auto-exit (default configuration)
echo Input "2" to to set on auto-exit
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_exit=none"
if /i "%bs%"=="1" set "v_exit=false"
if /i "%bs%"=="2" set "v_exit=true"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_exit%"=="none" echo WRONG CHOICE
if "%v_exit%"=="none" echo.
if "%v_exit%"=="none" goto op_aexit

set v_exit="va_exit=%v_exit%"
set v_exit="%v_exit%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "101" -nl "set %v_exit%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "101" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_kgprompt
cls
call :logo
echo ***************************************************************************
echo SHOW\SKIP REQUIRED_SYSTEM_VERSION AND KEYGENERATION CHANGE PROPMT
echo ***************************************************************************
echo.
echo Input "1" to show RSV prompt (default configuration)
echo Input "2" to not show RSV prompt
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "skipRSVprompt=none"
if /i "%bs%"=="1" set "skipRSVprompt=false"
if /i "%bs%"=="2" set "skipRSVprompt=true"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%skipRSVprompt%"=="none" echo WRONG CHOICE
if "%skipRSVprompt%"=="none" echo.
if "%skipRSVprompt%"=="none" goto op_kgprompt

set skipRSVprompt="skipRSVprompt=%skipRSVprompt%"
set skipRSVprompt="%skipRSVprompt%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "108" -nl "set %skipRSVprompt%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "108" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_buffer
cls
call :logo
echo ***************************************************************************
echo SET BUFFER FOR COPY AND APPENDING FILES FROM\TO NSP\XCI
echo ***************************************************************************
echo This option affects the speed of the process. The ideal buffer depends on
echo your system. Deffault is set at 64kB
echo.
echo Input "1"  to change BUFFER to 80kB
echo Input "2"  to change BUFFER to 72kB
echo Input "3"  to change BUFFER to 64kB (Default)
echo Input "4"  to change BUFFER to 56kB
echo Input "5"  to change BUFFER to 48kB
echo Input "6"  to change BUFFER to 40kB
echo Input "7"  to change BUFFER to 32kB
echo Input "8"  to change BUFFER to 24kB
echo Input "9"  to change BUFFER to 16kB
echo Input "10" to change BUFFER to  8kB

echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_buffer=none"
if /i "%bs%"=="1" set "v_buffer=-b 81920"
if /i "%bs%"=="2" set "v_buffer=-b 73728"
if /i "%bs%"=="3" set "v_buffer=-b 65536"
if /i "%bs%"=="4" set "v_buffer=-b 57344"
if /i "%bs%"=="5" set "v_buffer=-b 49152"
if /i "%bs%"=="6" set "v_buffer=-b 40960"
if /i "%bs%"=="7" set "v_buffer=-b 32768"
if /i "%bs%"=="8" set "v_buffer=-b 24576"
if /i "%bs%"=="9" set "v_buffer=-b 16384"
if /i "%bs%"=="10" set "v_buffer=-b 8192"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_buffer%"=="none" echo WRONG CHOICE
if "%v_buffer%"=="none" echo.
if "%v_buffer%"=="none" goto op_buffer

set v_buffer="buffer=%v_buffer%"
set v_buffer="%v_buffer%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "32" -nl "set %v_buffer%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "32" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_fat
cls
call :logo
echo ***************************************************************************
echo SET FAT32 FROM YOUR SD CARD TO GENERATE SPLIT FILES IF NEEDED
echo ***************************************************************************
echo SX OS rommenu supports ns0, ns1,.. files for splitted nsp files as well
echo as 00, 01 files in an archived folder, to reflect this 2 options are given.
echo.
echo Input "1" to change CARD FORMAT to exfat (Default)
echo Input "2" to change CARD FORMAT to fat32 for SX OS (xc0 and ns0 files)
echo Input "3" to change CARD FORMAT to fat32 for all CFW (archive folder)
echo.
echo Note: Archive folder option exports nsp files as folders and xci files 
echo splitted files.
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_fat1=none"
set "v_fat2=none"
if /i "%bs%"=="1" set "v_fat1=-fat exfat"
if /i "%bs%"=="1" set "v_fat2=-fx files"
if /i "%bs%"=="2" set "v_fat1=-fat fat32"
if /i "%bs%"=="2" set "v_fat2=-fx files"
if /i "%bs%"=="3" set "v_fat1=-fat fat32"
if /i "%bs%"=="3" set "v_fat2=-fx folder"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_fat1%"=="none" echo WRONG CHOICE
if "%v_fat1%"=="none" echo.
if "%v_fat1%"=="none" goto op_fat
if "%v_fat2%"=="none" echo WRONG CHOICE
if "%v_fat2%"=="none" echo.
if "%v_fat2%"=="none" goto op_fat

set v_fat1="fatype=%v_fat1%"
set v_fat1="%v_fat1%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "116" -nl "set %v_fat1%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "116" -nl "Line in config was changed to: "
echo.
set v_fat2="fexport=%v_fat2%"
set v_fat2="%v_fat2%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "117" -nl "set %v_fat2%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "117" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_oforg
cls
call :logo
echo ***************************************************************************
echo ORGANIZATION FORMAT FOR OUTPUT ITEMS IN OUTPUT FOLDER
echo ***************************************************************************
echo.
echo Input "1" to organize files separetely (default)
echo Input "2" to organize files in folders set by content
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_oforg=none"
if /i "%bs%"=="1" set "v_oforg=inline"
if /i "%bs%"=="2" set "v_oforg=subfolder"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_oforg%"=="none" echo WRONG CHOICE
if "%v_oforg%"=="none" echo.
if "%v_oforg%"=="none" goto op_oforg

set v_oforg="oforg=%v_oforg%"
set v_oforg="%v_oforg%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "125" -nl "set %v_oforg%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "125" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_nscbmode
cls
call :logo
echo ***************************************************************************
echo START PROGRAM WITH NEW MODE OR LEGACY MODE
echo ***************************************************************************
echo.
echo Input "1" to start with NEW MODE (default)
echo Input "2" to start with LEGACY MODE
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_nscbmode=none"
if /i "%bs%"=="1" set "v_nscbmode=new"
if /i "%bs%"=="2" set "v_nscbmode=legacy"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_nscbmode%"=="none" echo WRONG CHOICE
if "%v_nscbmode%"=="none" echo.
if "%v_nscbmode%"=="none" goto op_nscbmode

set v_nscbmode="NSBMODE=%v_nscbmode%"
set v_nscbmode="%v_nscbmode%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "132" -nl "set %v_nscbmode%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "132" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_romanize
cls
call :logo
echo ***************************************************************************
echo ROMANIZE RESULTING NAMES FOR DIRECT MULTI FUNCTION
echo ***************************************************************************
echo.
echo Input "1" to convert japanese\asian names to ROMAJI (default)
echo Input "2" to keep names as read on PREVALENT BASEFILE
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_roma=none"
if /i "%bs%"=="1" set "v_roma=TRUE"
if /i "%bs%"=="2" set "v_roma=FALSE"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_roma%"=="none" echo WRONG CHOICE
if "%v_roma%"=="none" echo.
if "%v_roma%"=="none" goto op_romanize

set v_roma="romaji=%v_roma%"
set v_roma="%v_roma%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "139" -nl "set %v_roma%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "139" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_translate
cls
call :logo
echo *****************************************************************************
echo TRANSLATE GAME DESCRIPTION LINES TO ENGLISH FROM JAPANESE, CHINES, KOREAN
echo *****************************************************************************
echo.
echo NOTE: Unlike romaji for translations NSCB makes API calls to GOOGLE TRANSLATE
echo.
echo Input "1" to translate descriptions (default)
echo Input "2" to keep descriptions as read on nutdb files
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_trans=none"
if /i "%bs%"=="1" set "v_trans=TRUE"
if /i "%bs%"=="2" set "v_trans=FALSE"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_trans%"=="none" echo WRONG CHOICE
if "%v_trans%"=="none" echo.
if "%v_trans%"=="none" goto op_translate

set v_trans="transnutdb=%v_trans%"
set v_trans="%v_trans%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "147" -nl "set %v_trans%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "147" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_threads
cls
call :logo
echo ***************************************************************************
echo SET NUMBER OF WORKERS FOR THREADED OPERATIONS
echo ***************************************************************************
echo Currently used in the renamer and database building modes
echo For more values edit NSCB_options.cmd with a text editor
echo.
echo Input "1"  to USE 1 worker (default\deactivated)
echo Input "2"  to USE 5 workers
echo Input "3"  to USE 10 workers
echo Input "4"  to USE 20 workers
echo Input "5"  to USE 30 workers
echo Input "6"  to USE 40 workers
echo Input "7"  to USE 50 workers
echo Input "8"  to USE 60 workers
echo Input "9"  to USE 70 workers
echo Input "10" to USE 80 workers
echo Input "11" to USE 90 workers
echo Input "12" to USE 100 workers
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_workers=none"
if /i "%bs%"=="1" set "v_workers=-threads 1"
if /i "%bs%"=="2" set "v_workers=-threads 5"
if /i "%bs%"=="3" set "v_workers=-threads 10"
if /i "%bs%"=="4" set "v_workers=-threads 20"
if /i "%bs%"=="5" set "v_workers=-threads 30"
if /i "%bs%"=="6" set "v_workers=-threads 40"
if /i "%bs%"=="7" set "v_workers=-threads 50"
if /i "%bs%"=="8" set "v_workers=-threads 60"
if /i "%bs%"=="9" set "v_workers=-threads 70"
if /i "%bs%"=="10" set "v_workers=-threads 80"
if /i "%bs%"=="11" set "v_workers=-threads 90"
if /i "%bs%"=="12" set "v_workers=-threads 100"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_workers%"=="none" echo WRONG CHOICE
if "%v_workers%"=="none" echo.
if "%v_workers%"=="none" goto op_threads

set v_workers="workers=%v_workers%"
set v_workers="%v_workers%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "153" -nl "set %v_workers%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "153" -nl "Line in config was changed to: "
echo.
pause
goto sc3

:op_NSZ1
cls
call :logo
echo ***************************************************************************
echo USER COMPRESSION OPTIONS
echo ***************************************************************************
echo ************************
echo INPUT COMPRESSION LEVEL
echo ************************
echo Input a compression level between 1 and 22
echo Notes:
echo  + Level 1 - Fast and smaller compression ratio
echo  + Level 22 - Slow but better compression ratio
echo  Levels 10-17 are recommended in the spec
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "x" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_nszlevels=none"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="x" goto sc1
if /i "%bs%"=="e" goto salida

set "v_nszlevels=%bs%"
set v_nszlevels="compression_lv=%v_nszlevels%"
set v_nszlevels="%v_nszlevels%"
if "%v_nszlevels%"=="none" echo WRONG CHOICE
if "%v_nszlevels%"=="none" echo.
if "%v_nszlevels%"=="none" goto op_NSZ1
%pycommand% "%listmanager%" -cl "%op_file%" -ln "158" -nl "set %v_nszlevels%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "158" -nl "Line in config was changed to: "
:op_NSZ2
echo.
echo *******************************************************
echo INPUT NUMBER OF THREADS TO USE
echo *******************************************************
echo Input a number of threads to use between 0 and 4
echo Notes:
echo  + By using threads you may gain a little speed bump 
echo    but you'll loose compression ratio
echo  + Level 22 and 4 threads may run you out of memory
echo  + For maximum threads level 17 compression is advised
echo    but you'll loose compression ratio
echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "x" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_nszthreads=none"

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="x" goto sc1
if /i "%bs%"=="e" goto salida

set "v_nszthreads=%bs%"
set v_nszthreads="compression_threads=%v_nszthreads%"
set v_nszthreads="%v_nszthreads%"
if "%v_nszthreads%"=="none" echo WRONG CHOICE
if "%v_nszthreads%"=="none" echo.
if "%v_nszthreads%"=="none" goto op_NSZ2
%pycommand% "%listmanager%" -cl "%op_file%" -ln "159" -nl "set %v_nszthreads%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "159" -nl "Line in config was changed to: "
pause
goto sc3
:op_NSZ3
echo.
echo *******************************************************
echo FORMAT TO EXPORT XCI
echo *******************************************************
echo.
echo Input "1"  to export as xcz -supertrimmed-(default)
echo Input "2"  to export as nsz
echo.
echo Remember, tinfoil can install both formats so is not
echo advised to export as nsz. If you really want to have
echo them as nsz please do it this way to make the nca
echo files from the game restorable.
echo Note: Currently this restoration needs to uncompressed
echo the file into nsp first a direct restoration will better
echo included soon.
echo.echo.
echo Input "b" to return to GLOBAL OPTIONS
echo Input "x" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set "v_xcz_export=none"
set /p bs="Enter your choice: "

if /i "%bs%"=="b" goto sc3
if /i "%bs%"=="x" goto sc1
if /i "%bs%"=="e" goto salida

if /i "%bs%"=="1" set "v_xcz_export=xcz"
if /i "%bs%"=="2" set "v_xcz_export=nsz"
set v_xcz_export="xci_export=%v_xcz_export%"
set v_xcz_export="%v_xcz_export%"
if "%v_xcz_export%"=="none" echo WRONG CHOICE
if "%v_xcz_export%"=="none" echo.
if "%v_xcz_export%"=="none" goto op_NSZ3
%pycommand% "%listmanager%" -cl "%op_file%" -ln "160" -nl "set %v_xcz_export%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "160" -nl "Line in config was changed to: "
pause
goto sc3

:def_set1
echo.
echo **AUTO-MODE OPTIONS**
REM vrepack
set "v_rep=both"
set v_rep="vrepack=%v_rep%"
set v_rep="%v_rep%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "57" -nl "set %v_rep%"
%pycommand% "%listmanager%" -rl "%op_file%" -ln "57" -nl "Line in config was changed to: "

REM fi_rep
set "v_fold=multi"
set v_fold="fi_rep=%v_fold%"
set v_fold="%v_fold%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "61" -nl "set %v_fold%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "61" -nl "Line in config was changed to: "

REM v_RSV
set "v_RSV=-pv false"
set v_RSV="patchRSV=%v_RSV%"
set v_RSV="%v_RSV%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "41" -nl "set %v_RSV%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "41" -nl "Line in config was changed to: "

REM vkey
set "v_KGEN=-kp false"
set v_KGEN="vkey=%v_KGEN%"
set v_KGEN="%v_KGEN%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "95" -nl "set %v_KGEN%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "95" -nl "Line in config was changed to: "

exit /B

:def_set2
echo.
echo **GLOBAL OPTIONS**
REM OP_COLOR
set "v_colF=F"
set /a "v_colB=1"
setlocal enabledelayedexpansion
set "v_col=!v_colB!!v_colF!"
color !v_col!
%pycommand% "%listmanager%" -cl "%op_file%" -ln "3" -nl "color !v_col!"
%pycommand% "%listmanager%" -rl "%op_file%" -ln "3" -nl "Line in config was changed to: "
endlocal

REM w_folder
set "v_wf=NSCB_temp"
set v_wf="w_folder=%v_wf%"
set v_wf="%v_wf%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "8" -nl "set %v_wf%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "8" -nl "Line in config was changed to: "

REM v_of
set "v_of=NSCB_output"
set v_of="fold_output=%v_of%"
set v_of="%v_of%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "10" -nl "set %v_of%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "10" -nl "Line in config was changed to: "

REM v_delta
set "v_delta=--C_clean_ND"
set v_delta="nf_cleaner=%v_delta%"
set v_delta="%v_delta%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "36" -nl "set %v_delta%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "36" -nl "Line in config was changed to: "

REM v_delta2
set "v_delta2_=-ND true"
set v_delta2_="skdelta=%v_delta2_%"
set v_delta2_="%v_delta2_%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "37" -nl "set %v_delta2_%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "37" -nl "Line in config was changed to: "

REM zip_restore
set "v_gzip=false"
set v_gzip="zip_restore=%v_gzip%"
set v_gzip="%v_gzip%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "78" -nl "set %v_gzip%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "78" -nl "Line in config was changed to: "

REM AUTO-EXIT
set "v_exit=false"
set v_exit="va_exit=%v_exit%"
set v_exit="%v_exit%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "101" -nl "set %v_exit%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "101" -nl "Line in config was changed to: "

REM skipRSVprompt
set "skipRSVprompt=false"
set skipRSVprompt="skipRSVprompt=%skipRSVprompt%"
set skipRSVprompt="%skipRSVprompt%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "108" -nl "set %skipRSVprompt%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "108" -nl "Line in config was changed to: "

REM buffer
set "v_buffer=-b 65536"
set v_buffer="buffer=%v_buffer%"
set v_buffer="%v_buffer%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "32" -nl "set %v_buffer%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "32" -nl "Line in config was changed to: "


REM FAT format
set "v_fat1=-fat exfat"
set v_fat1="fatype=%v_fat1%"
set v_fat1="%v_fat1%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "116" -nl "set %v_fat1%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "116" -nl "Line in config was changed to: "

set "v_fat2=-fx files"
set v_fat2="fexport=%v_fat2%"
set v_fat2="%v_fat2%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "117" -nl "set %v_fat2%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "117" -nl "Line in config was changed to: "

REM OUTPUT ORGANIZING format
set "v_oforg=inline"
set v_oforg="oforg=%v_oforg%"
set v_oforg="%v_oforg%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "125" -nl "set %v_oforg%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "125" -nl "Line in config was changed to: "

REM NSCB MODE
set "v_nscbmode=new"
set v_nscbmode="NSBMODE=%v_nscbmode%"
set v_nscbmode="%v_nscbmode%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "132" -nl "set %v_nscbmode%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "132" -nl "Line in config was changed to: "

REM ROMAJI
set "v_roma=TRUE"
set v_roma="romaji=%v_roma%"
set v_roma="%v_roma%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "139" -nl "set %v_roma%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "139" -nl "Line in config was changed to: "

REM TRANSLATE
set "v_trans=FALSE"
set v_trans="transnutdb=%v_trans%"
set v_trans="%v_trans%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "147" -nl "set %v_trans%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "147" -nl "Line in config was changed to: "

REM WORKERS
set v_workers="workers=-threads 1"
set v_workers="%v_workers%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "153" -nl "set %v_workers%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "153" -nl "Line in config was changed to: "

REM COMPRESSION
set "v_nszlevels=17"
set v_nszlevels="compression_lv=%v_nszlevels%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "158" -nl "set %v_nszlevels%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "158" -nl "Line in config was changed to: "
set "v_nszlevels=0"
set v_nszlevels="compression_threads=%v_nszlevels%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "159" -nl "set %v_nszlevels%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "159" -nl "Line in config was changed to: "
set "v_xcz_export=xcz"
set v_xcz_export="xci_export=%v_xcz_export%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "160" -nl "set %v_xcz_export%" 
%pycommand% "%listmanager%" -rl "%op_file%" -ln "160" -nl "Line in config was changed to: "

exit /B

:curr_set1
echo.
echo **CURRENT AUTO-MODE OPTIONS**
REM vrepack
%pycommand% "%listmanager%" -rl "%op_file%" -ln "57" -nl "File repack is set to: "

REM fi_rep
%pycommand% "%listmanager%" -rl "%op_file%" -ln "61" -nl "Folder processing is set to: "

REM v_RSV
%pycommand% "%listmanager%" -rl "%op_file%" -ln "41" -nl "RequiredSystemVersion patching is set to: "

REM vkey
%pycommand% "%listmanager%" -rl "%op_file%" -ln "95" -nl "Keygeneration variable is set to: "

exit /B

:curr_set2
echo.
echo **CURRENT GLOBAL OPTIONS**
REM OP_COLOR
%pycommand% "%listmanager%" -rl "%op_file%" -ln "3" -nl "Color is set to: "
endlocal

REM w_folder
%pycommand% "%listmanager%" -rl "%op_file%" -ln "8" -nl "Work Folder is set to: "

REM v_of
%pycommand% "%listmanager%" -rl "%op_file%" -ln "10" -nl "Output Folder is set to: "

REM v_delta
%pycommand% "%listmanager%" -rl "%op_file%" -ln "36" -nl "Delta Skipping is set to: "

REM v_delta2
%pycommand% "%listmanager%" -rl "%op_file%" -ln "37" -nl "Delta Skipping (direct functions) is set to: "

REM zip_restore
%pycommand% "%listmanager%" -rl "%op_file%" -ln "78" -nl "Zip generation is set to: "

REM AUTO-EXIT
%pycommand% "%listmanager%" -rl "%op_file%" -ln "101" -nl "Auto-exit is set to: "

REM skipRSVprompt
%pycommand% "%listmanager%" -rl "%op_file%" -ln "108" -nl "Skip RSV selection is set to: "

REM buffer
%pycommand% "%listmanager%" -rl "%op_file%" -ln "32" -nl "Buffer is set to: "

REM FAT format
%pycommand% "%listmanager%" -rl "%op_file%" -ln "116" -nl "SD File Format is set to: "
%pycommand% "%listmanager%" -rl "%op_file%" -ln "117" -nl "Split nsp format is set to: "
REM OUTPUT ORGANIZING format
%pycommand% "%listmanager%" -rl "%op_file%" -ln "125" -nl "Output organization is set to: "

REM NSCB MODE
%pycommand% "%listmanager%" -rl "%op_file%" -ln "132" -nl "NSCB mode is set to: "

REM ROMANIZE
%pycommand% "%listmanager%" -rl "%op_file%" -ln "139" -nl "ROMANIZE option is set to: "

REM TRANSLATE
%pycommand% "%listmanager%" -rl "%op_file%" -ln "147" -nl "TRANSLATE option is set to: "

REM WORKERS
%pycommand% "%listmanager%" -rl "%op_file%" -ln "153" -nl "WORKERS option is set to: "

REM COMPRESSION
%pycommand% "%listmanager%" -rl "%op_file%" -ln "158" -nl "COMPRESSION LEVELS option is set to: "
%pycommand% "%listmanager%" -rl "%op_file%" -ln "159" -nl "COMPRESSION THREADS option is set to: "
%pycommand% "%listmanager%" -rl "%op_file%" -ln "160" -nl "COMPRESSED XCIS EXPORT option is set to: "
exit /B

:verify_keys
cls
call :logo
echo ***************************************************************************
echo VERIFY KEYS IN KEYS.TXT AGAINST SHA256 HASHES FROM THE CORRECT KEYS
echo ***************************************************************************

%pycommand% "%nut%" -nint_keys "%dec_keys%"

echo ...........................................................................
echo Input "0" to return to CONFIG MENU
echo Input "1" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

:salida
exit /B

:update_nutdb
cls
call :logo
echo ***************************************************************************
echo FORCING NUT_DB UPDATE
echo ***************************************************************************

%pycommand% "%nut%" -lib_call nutdb force_refresh

echo ...........................................................................
echo Input "0" to return to CONFIG MENU
echo Input "1" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida

:interface
cls
call :logo
echo ********************************************************
echo AUTO-MODE - CONFIGURATION
echo ********************************************************
echo Input "1" to change STARTUP VISIBILITY configuration
echo Input "2" to choose a BROWSER for the interface 
echo Input "3" to deactivate VIDEO PLAYBACK
echo.
echo Input "d" to restore INTERFACE DEFAULTS
echo Input "0" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo .......................................................
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto op_interface_consolevisibility
if /i "%bs%"=="2" goto op_interface_browser
if /i "%bs%"=="3" goto op_interface_video_playback

if /i "%bs%"=="d" goto op_interface_defaults
if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="e" goto salida
echo WRONG CHOICE
echo.
goto interface

:op_interface_consolevisibility
cls
call :logo
echo ***************************************************************************
echo START INTERFACE.BAT MINIMIZED?
echo ***************************************************************************
echo Controls if the debugging console starts minimized together with the web
echo interface
echo.
echo Input "1"  to start MINIMIZED
echo Input "2"  to NOT start MINIMIZED
echo Input "D"  for default (NOT MINIMIZED)
echo.
echo Input "0" to return to CONFIG MENU
echo Input "b" to return to INTERFACE MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Enter your choice: "
set "v_interface=none"
if /i "%bs%"=="1" set "v_interface=yes"
if /i "%bs%"=="2" set "v_interface=no"
if /i "%bs%"=="d" set "v_interface=no"

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="b" goto interface
if /i "%bs%"=="e" goto salida

if "%v_interface%"=="none" echo WRONG CHOICE
if "%v_interface%"=="none" echo.
if "%v_interface%"=="none" goto op_interface_consolevisibility

set v_interface="start_minimized=%v_interface%"
set v_interface="%v_interface%"
%pycommand% "%listmanager%" -cl "%opt_interface%" -ln "16" -nl "set %v_interface%" 
echo.
%pycommand% "%listmanager%" -rl "%opt_interface%" -ln "16" -nl "Line in config was changed to: "
echo.
pause
goto interface

:op_interface_browser
cls
call :logo
echo ***************************************************************************
echo CHOOSE BROWSER TO STARTUP INTERFACE
echo ***************************************************************************
echo Selects the browser used to startup the interface:
echo Options:
echo 1. Auto. Order is set in base of ztools\chromium or browser installed in 
echo system. This is autoset by squirrel in the following order:
echo    I.   ztools\chromium (Chromium portable\Slimjet portable)
echo    II.  Chrome or Chromium installed on system
echo    III. Microsoft Edge (Not recommended)
echo 2. Sytem Default. USes default system brwoser (low compatibility)
echo 3. Set a raw path to a pure chromium browser by one of the following methods.
echo    I.   Absolute path to your browser, ending by .exe
echo    II.  Absolute path to a .lnk file (windows shortcut)
echo    III. Name of a .lnk file in ztools\chromium (ending by .lnk)
echo         Example: brave.lnk 
echo         This will read ztools\chromium\brave.lnk and redirect to the exe 
echo         path launching brave browser
echo.
echo Input "1" or "d" to set variable to AUTO
echo Input "2" to set variable to SYSTEM DEFAULT
echo Input shortcut.lnk name to 3.III methods
echo Input absolute route to browser or shortcut for 3.I or 3.II method
echo.
echo Input "0" to return to CONFIG MENU
echo Input "b" to return to INTERFACE MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Enter your choice: "
set "v_interface_browser=%bs%"
if /i "%bs%"=="1" set "v_interface_browser=auto"
if /i "%bs%"=="2" set "v_interface_browser=default"
if /i "%bs%"=="d" set "v_interface_browser=auto"

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="b" goto interface
if /i "%bs%"=="e" goto salida

set v_interface_browser="browserpath=%v_interface_browser%"
set v_interface_browser="%v_interface_browser%"

%pycommand% "%listmanager%" -cl "%opt_interface%" -ln "30" -nl "set %v_interface_browser%" 
echo.
%pycommand% "%listmanager%" -rl "%opt_interface%" -ln "30" -nl "Line in config was changed to: "
echo.
pause
goto interface

:op_interface_video_playback
cls
call :logo
echo ***************************************************************************
echo DEACTIVATE VIDEO PLAYBACK
echo ***************************************************************************
echo Deactivates HLS player for Nintendo.com videos.
echo This is meant for old computers that may freeze with the HLS javascript 
echo player
echo.
echo Input "1"  to ENABLE video playback
echo Input "2"  to DISABLE video playback
echo Input "D"  for default (NOT MINIMIZED)
echo.
echo Input "0" to return to CONFIG MENU
echo Input "b" to return to INTERFACE MENU
echo Input "e" to go back to the MAIN PROGRAM
echo.
set /p bs="Enter your choice: "
set "v_video_playback=none"
if /i "%bs%"=="1" set "v_video_playback=true"
if /i "%bs%"=="2" set "v_video_playback=false"
if /i "%bs%"=="d" set "v_video_playback=false"

if /i "%bs%"=="0" goto sc1
if /i "%bs%"=="b" goto interface
if /i "%bs%"=="e" goto salida

if "%v_video_playback%"=="none" echo WRONG CHOICE
if "%v_video_playback%"=="none" echo.
if "%v_video_playback%"=="none" goto op_interface_video_playback

set v_video_playback="videoplayback=%v_video_playback%"
set v_video_playback="%v_video_playback%"
%pycommand% "%listmanager%" -cl "%opt_interface%" -ln "34" -nl "set %v_video_playback%" 
echo.
%pycommand% "%listmanager%" -rl "%opt_interface%" -ln "34" -nl "Line in config was changed to: "
echo.
pause
goto interface

:op_interface_defaults
cls
call :logo
::Startup
set v_interface="start_minimized=no"
set v_interface="%v_interface%"
%pycommand% "%listmanager%" -cl "%opt_interface%" -ln "16" -nl "set %v_interface%" 
%pycommand% "%listmanager%" -rl "%opt_interface%" -ln "16" -nl "Line in config was changed to: "
echo.
::Browserpath
set v_interface_browser="browserpath=auto"
set v_interface_browser="%v_interface_browser%"
%pycommand% "%listmanager%" -cl "%opt_interface%" -ln "30" -nl "set %v_interface_browser%" 
%pycommand% "%listmanager%" -rl "%opt_interface%" -ln "30" -nl "Line in config was changed to: "
echo.
::Video playback
set v_video_playback="videoplayback=true"
set v_video_playback="%v_video_playback%"
%pycommand% "%listmanager%" -cl "%opt_interface%" -ln "34" -nl "set %v_video_playback%" 
%pycommand% "%listmanager%" -rl "%opt_interface%" -ln "34" -nl "Line in config was changed to: "
pause

goto sc1

:salida
exit /B

:logo
ECHO                                        __          _ __    __         
ECHO                  ____  _____ ____     / /_  __  __(_) /___/ /__  _____
ECHO                 / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/
ECHO                / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /    
ECHO               /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/     
ECHO                              /_____/                                  
ECHO -------------------------------------------------------------------------------------
ECHO                         NINTENDO SWITCH CLEANER AND BUILDER
ECHO                      (THE XCI MULTI CONTENT BUILDER AND MORE)
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                                POWERED BY SQUIRREL                                "
ECHO "                    BASED IN THE WORK OF BLAWAR AND LUCA FRAGA                     "
ECHO                                    VERSION 0.96e
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Blawar's github:  https://github.com/blawar
ECHO Blawar's tinfoil: https://github.com/digableinc/tinfoil
ECHO Luca Fraga's github: https://github.com/LucaFraga
ECHO -------------------------------------------------------------------------------------
exit /B

:idepend
cls
call :logo
call "%batdepend%"
goto sc1
