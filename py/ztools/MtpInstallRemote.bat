@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"
set "bat_name=%~n0"
Title NSC_Builder v1.00c -- Profile: %ofile_name% -- by JulesOnTheRoad

:MAIN
if exist "MTP1GD.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (MTP1GD.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (MTP1GD.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del MTP1GD.txt )
endlocal
if not exist "MTP1GD.txt" goto manual_INIT
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
call :program_logo
echo -------------------------------------------------
echo MTP - INSTALL FROM GOOGLE DRIVE
echo -------------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................

:manual_INIT
endlocal
cls
call :program_logo
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
%pycommand% "%squirrel%" --mtp_eval_link "%prog_dir%MTP1GD.txt" "%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto MAIN
if /i "%eval%"=="1" ( %pycommand% "%squirrel%" -lib_call picker_walker remote_select_from_cache -xarg "%prog_dir%MTP1GD.txt" )
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call picker_walker remote_select_from_libraries -xarg "%prog_dir%MTP1GD.txt" )
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call picker_walker remote_select_from_walker -xarg "%prog_dir%MTP1GD.txt" "nsp nsz" )
if /i "%eval%"=="c" ( %pycommand% "%squirrel%" -lib_call workers concurrent_cache )
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
%pycommand% "%squirrel%" --mtp_eval_link "%prog_dir%MTP1GD.txt" "%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto MAIN
if /i "%eval%"=="1" goto select_medium
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call picker_walker remote_select_from_cache -xarg "%prog_dir%MTP1GD.txt" )
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call picker_walker remote_select_from_libraries -xarg "%prog_dir%MTP1GD.txt" )
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker remote_select_from_walker -xarg "%prog_dir%MTP1GD.txt" "nsp nsz" )
if /i "%eval%"=="c" ( %pycommand% "%squirrel%" -lib_call workers concurrent_cache )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del "%prog_dir%MTP1GD.txt"
echo.
goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (MTP1GD.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:update_list1
if !pos1! GTR !pos2! ( goto :update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :update_list1
:update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<MTP1GD.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>MTP1GD.txt.new
endlocal
move /y "MTP1GD.txt.new" "MTP1GD.txt" >nul
endlocal
:showlist
cls
call :program_logo
echo -------------------------------------------------
echo MTP - INSTALL FROM GOOGLE DRIVE
echo -------------------------------------------------
ECHO FILES TO PROCESS:
for /f "tokens=*" %%f in (MTP1GD.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (MTP1GD.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal
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
call :program_logo
CD /d "%prog_dir%"
%pycommand% "%squirrel%" -lib_call mtp.mtp_gdrive loop_install -xarg "%prog_dir%MTP1GD.txt" "destiny=%medium%" "%w_folder%" "ch_medium=%MTP_aut_ch_medium%" "check_fw=%MTP_chk_fw%" "patch_keygen=%MTP_prepatch_kg%" "ch_base=%MTP_prechk_Base%" "ch_other=%MTP_prechk_Upd%" "truecopy=%MTP_pdrive_truecopy%"
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if exist MTP1GD.txt del MTP1GD.txt
if /i "%va_exit%"=="true" echo PROGRAM WILL CLOSE NOW
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto s_exit_choice


::///////////////////////////////////////////////////
::SUBROUTINES
::///////////////////////////////////////////////////

:squirrell
echo                    ,;:;;,
echo                   ;;;;;
echo           .=',    ;:;;:,
echo          /_', "=. ';:;:;
echo          @=:__,  \,;:;:'
echo            _(\.=  ;:;;'
echo           `"_(  _/="`
echo            `"'
exit /B

:program_logo

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
ECHO "                         A MTP MANAGER FOR DBI INSTALLER                           "
ECHO                                  VERSION 1.00c (MTP)
ECHO -------------------------------------------------------------------------------------
ECHO DBI by DUCKBILL: https://github.com/rashevskyv/switch/releases
ECHO Latest DBI: https://github.com/rashevskyv/switch/releases/tag/462
ECHO -------------------------------------------------------------------------------------
exit /B

:delay
PING -n 2 127.0.0.1 >NUL 2>&1
exit /B

:thumbup
echo.
echo    /@
echo    \ \
echo  ___\ \
echo (__O)  \
echo (____@) \
echo (____@)  \
echo (__o)_    \
echo       \    \
echo.
echo HOPE YOU HAVE A FUN TIME
exit /B

:MAIN
call "%prog_dir%\MtpMode.bat"
exit /B

:salida
::pause
exit
