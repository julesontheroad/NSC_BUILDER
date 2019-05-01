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
REM echo Input "4" to INSTALL DEPENDENCIES
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
rem if /i "%bs%"=="4" goto idepend

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
echo Input "8" to change top keygeneration to 8 (FW 7.0.0-7.0.1)
echo.
echo Input "b" to return to AUTO-MODE - CONFIGURATION
echo Input "c" to return to CONFIG MENU
echo Input "e" to go back to the MAIN PROGRAM
echo ...........................................................................
echo.
set /p bs="Enter your choice: "
set "v_KGEN=none"
if /i "%bs%"=="f" set "v_KGEN=-kp false"
if /i "%bs%"=="0" set "v_KGEN=-kp 0"
if /i "%bs%"=="1" set "v_KGEN=-kp 1"
if /i "%bs%"=="2" set "v_KGEN=-kp 2"
if /i "%bs%"=="3" set "v_KGEN=-kp 3"
if /i "%bs%"=="4" set "v_KGEN=-kp 4"
if /i "%bs%"=="5" set "v_KGEN=-kp 5"
if /i "%bs%"=="6" set "v_KGEN=-kp 6"
if /i "%bs%"=="7" set "v_KGEN=-kp 7"
if /i "%bs%"=="7" set "v_KGEN=-kp 8"

if /i "%bs%"=="b" goto sc2
if /i "%bs%"=="c" goto sc1
if /i "%bs%"=="e" goto salida

if "%v_RSV%"=="none" echo WRONG CHOICE
if "%v_RSV%"=="none" echo.
if "%v_RSV%"=="none" goto op_RSV

set v_KGEN="vkey=%v_KGEN%"
set v_KGEN="%v_KGEN%"
%pycommand% "%listmanager%" -cl "%op_file%" -ln "95" -nl "set %v_KGEN%" 
echo.
%pycommand% "%listmanager%" -rl "%op_file%" -ln "95" -nl "Line in config was changed to: "
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
echo Input "5" to change ZIP configuration
echo Input "6" to change AUTO-EXIT configuration
echo Input "7" to skip KEY-GENERATION PROMPT
echo Input "8" to set file stream BUFFER
echo Input "9" to set file FAT32\EXFAT options
echo Input "10" to how to ORGANIZE output files
echo Input "11" to set NEW MODE OR LEGACY MODE
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
set "v_buffer=buffer=-b 65536"
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
ECHO                                     VERSION 0.83
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