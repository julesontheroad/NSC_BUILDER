@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM MTP INSTALLER REMOTE
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - INSTALL FROM GOOGLE DRIVE
echo -------------------------------------------------
if exist "%list_folder%\M1_2list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in ( lists/M1_2list.txt ) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in ( lists/M1_2list.txt ) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del MTP1GD.txt )
endlocal
if not exist "%list_folder%\M1_2list.txt" goto manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:prevlist0
ECHO .......................................................
echo Input "1" to auto-start processing from the previous list
echo Input "2" to erase list and make a new one.
echo Input "3" to continue building the previous list
echo .......................................................
echo NOTE: By pressing 3 you'll see the previous list
echo before starting the processing the files and you will
echo be able to add and delete items from the list
echo.
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="3" goto showlist
if /i "%bs%"=="2" goto delist
if /i "%bs%"=="1" goto select_medium
if /i "%bs%"=="0" call "%prog_dir%ztools\MtpMode.bat"
echo.
echo BAD CHOICE
goto prevlist0
:delist
del MTP1GD.txt
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - INSTALL FROM GOOGLE DRIVE
echo -------------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................

:manual_INIT
endlocal
cls
call "%nscb_logos%" "program_logo"
echo *******************************************************
echo SELECT FUNCTION
echo *******************************************************
echo.
echo Input "1" to PICK FILES FROM CACHE FILES
echo Input "2" to PICK FILES FROM LIBRARIES
echo Input "3" to PICK FILES FROM FOLDER WALKER
echo Input "c" to regenerate the cache for remote libraries
ECHO.
echo --- Or INPUT GDRIVE PUBLIC_LINK or 1FICHIER LINK ---
echo.
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%sq_lc%" --mtp_eval_link "%list_folder%\M1_2list.txt" "%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto MAIN
if /i "%eval%"=="1" ( %pycommand% "%sq_lc%" -lib_call picker_walker remote_select_from_cache -xarg"%list_folder%\M1_2list.txt" )
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call picker_walker remote_select_from_libraries -xarg"%list_folder%\M1_2list.txt" )
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call picker_walker remote_select_from_walker -xarg"%list_folder%\M1_2list.txt" "nsp nsz xci xcz" )
if /i "%eval%"=="c" ( %pycommand% "%sq_lc%" -lib_call workers concurrent_cache )
echo.
goto checkagain

:checkagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Input "1" to START INSTALLING
echo Input "2" to PICK FILES FROM CACHE FILES
echo Input "3" to PICK FILES FROM LIBRARIES
echo Input "4" to PICK FILES FROM FOLDER WALKER
echo Input "c" to regenerate the cache for remote libraries
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
ECHO.
echo --- Or INPUT GDRIVE PUBLIC_LINK or 1FICHIER LINK ---
echo.
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%sq_lc%" --mtp_eval_link "%list_folder%\M1_2list.txt" "%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto MAIN
if /i "%eval%"=="1" goto select_medium
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call picker_walker remote_select_from_cache -xarg"%list_folder%\M1_2list.txt" )
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call picker_walker remote_select_from_libraries -xarg"%list_folder%\M1_2list.txt" )
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call picker_walker remote_select_from_walker -xarg"%list_folder%\M1_2list.txt" "nsp nsz xci xcz" )
if /i "%eval%"=="c" ( %pycommand% "%sq_lc%" -lib_call workers concurrent_cache )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del"%list_folder%\M1_2list.txt"
echo.
goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
%pycommand% "%sq_lc%" -lib_call listmanager remove_from_botton -xarg  "%list_folder%\M1_2list.txt" "%bs%"

:showlist
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%sq_lc%" -lib_call listmanager printcurrent -xarg  "%list_folder%\M1_2list.txt" "all" "counter=True"
goto checkagain

:select_medium_wrongchoice
echo wrong choice
echo ............
:select_medium
echo *******************************************************
echo INSTALLATION MEDIUM
echo *******************************************************
echo.
echo 1. SD
echo 2. EMMC
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set medium=none
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" set "medium=SD"
if /i "%bs%"=="2" set "medium=EMMC"

if %medium%=="none" goto select_medium_wrongchoice

:START_INSTALLATION
cls
call "%nscb_logos%" "program_logo"
CD /d "%prog_dir%"
%pycommand% "%sq_lc%" -lib_call mtp.mtp_gdrive loop_install -xarg"%list_folder%\M1_2list.txt" "destiny=%medium%" "%w_folder%" "ch_medium=%MTP_aut_ch_medium%" "check_fw=%MTP_chk_fw%" "patch_keygen=%MTP_prepatch_kg%" "ch_base=%MTP_prechk_Base%" "ch_other=%MTP_prechk_Upd%" "truecopy=%MTP_pdrive_truecopy%"
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if exist "%list_folder%\M1_2list.txt" ( call "%nscb_tools%" "delete_if_empty" "M1_2list.txt" )
if /i "%va_exit%"=="true" echo PROGRAM WILL CLOSE NOW
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" call "%cmdfolder%\M_0_MtpMode.bat"
if /i "%bs%"=="1" goto salida
goto s_exit_choice

:salida
::pause
exit