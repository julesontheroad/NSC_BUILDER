@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"
set "bat_name=%~n0"
Title NSC_Builder v1.01 -- Profile: %ofile_name% -- by JulesOnTheRoad

:MAIN
cls
call :program_logo
ECHO .............................................................
echo Input "1" to enter into GAME INSTALLATION mode
echo Input "2" to enter into FILE TRANSFER mode
echo Input "3" to enter into AUTOUPDATE DEVICE FROM LIBRARY mode
echo Input "4" to enter into DUMP OR UNINSTALL GAMES
echo Input "5" to enter into BACKUP SAVES mode
echo Input "6" to enter into DEVICE INFORMATION mode
echo Input "7" to enter into GENERATE SX AUTOLOADER FILES mode
echo Input "0" to enter into CONFIGURATION mode
echo.
echo Input "N" to go to STANDARD MODES
echo Input "D" to enter GOOGLE DRIVE MODES
echo Input "L" to go to LEGACY MODES
echo .............................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto G_INST
if /i "%bs%"=="2" goto F_TR
if /i "%bs%"=="3" goto AUTOUPDATE
if /i "%bs%"=="4" goto INSTALLED
if /i "%bs%"=="5" goto SAVES
if /i "%bs%"=="6" goto DEV_INF
if /i "%bs%"=="7" goto SX_AUTOLOADER
if /i "%bs%"=="N" goto call_main
if /i "%bs%"=="L" goto LegacyMode
if /i "%bs%"=="D" goto GDMode
if /i "%bs%"=="0" goto OPT_CONFIG
goto MAIN

:LegacyMode
call "%prog_dir%ztools\LEGACY.bat"
exit /B

:GDMode
call "%prog_dir%ztools\DriveMode.bat"
exit /B

:G_INST
cls
call :program_logo
echo -------------------------------------------------
echo MTP - FILE TRANFER MODE ACTIVATED
echo -------------------------------------------------
echo *******************************************************
echo SELECT FUNCTION
echo *******************************************************
echo.
echo 1. GAME INSTALLATION FROM LOCAL FILES
echo 2. GAME INSTALLATION FROM REMOTE LIBRARIES (GDRIVE)
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" goto G_INST_LOCAL
if /i "%bs%"=="2" goto G_INST_GDRIVE
goto G_INST

:G_INST_GDRIVE
call "%prog_dir%ztools\MtpInstallRemote.bat"
goto MAIN

:G_INST_LOCAL
cls
call :program_logo
echo -------------------------------------------------
echo MTP - INSTALLATION MODE ACTIVATED
echo -------------------------------------------------
if exist "MTP1.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (MTP1.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (MTP1.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del MTP1.txt )
endlocal
if not exist "MTP1.txt" goto manual_INIT
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
if /i "%bs%"=="1" goto start_1install
if /i "%bs%"=="0" goto MAIN
echo.
echo BAD CHOICE
goto prevlist0
:delist
del MTP1.txt
cls
call :program_logo
echo -------------------------------------------------
echo MTP - INSTALLATION MODE ACTIVATED
echo -------------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................

:manual_INIT
endlocal
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "3" to select files from local libraries
echo Input "4" to select files via folder-walker
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%squirrel%" -t nsp nsz xci xcz -tfile "%prog_dir%MTP1.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto MAIN
if /i "%eval%"=="1" ( %pycommand% "%squirrel_lb%" -lib_call listmanager selector2list -xarg "%prog_dir%MTP1.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%squirrel_lb%" -lib_call listmanager selector2list -xarg "%prog_dir%MTP1.txt" mode=file ext="nsp xci nsz xcz" False False True )  2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller select_from_local_libraries -xarg "%prog_dir%MTP1.txt" )
if /i "%eval%"=="4" ( %pycommand% "%squirrel_lb%" -lib_call picker_walker get_files_from_walk -xarg "%prog_dir%MTP1.txt" "extlist=nsp xci nsz xcz" )

goto checkagain
echo.
:checkagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Input "1" to start processing
echo Input "2" to add another folder to list via selector
echo Input "3" to add another file to list via selector
echo Input "4" to select files from local libraries
echo Input "5" to select files via folder-walker
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
echo ......................................................................
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%squirrel%" -t nsp nsz xci xcz -tfile "%prog_dir%MTP1.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto MAIN
if /i "%eval%"=="1" goto start_1install
if /i "%eval%"=="2" ( %pycommand% "%squirrel_lb%" -lib_call listmanager selector2list -xarg "%prog_dir%MTP1.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel_lb%" -lib_call listmanager selector2list -xarg "%prog_dir%MTP1.txt" mode=file ext="nsp xci nsz xcz" False False True )  2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller select_from_local_libraries -xarg "%prog_dir%MTP1.txt" )
if /i "%eval%"=="5" ( %pycommand% "%squirrel_lb%" -lib_call picker_walker get_files_from_walk -xarg "%prog_dir%MTP1.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del MTP1.txt

goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (MTP1.txt) do (
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
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<MTP1.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>MTP1.txt.new
endlocal
move /y "MTP1.txt.new" "MTP1.txt" >nul
endlocal

:showlist
cls
call :program_logo
echo -------------------------------------------------
echo MTP - INSTALLATION MODE ACTIVATED
echo -------------------------------------------------
ECHO FILES TO PROCESS:
for /f "tokens=*" %%f in (MTP1.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (MTP1.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

goto checkagain

:s_mtp1_wrongchoice
echo wrong choice
echo ............
:start_1install
echo *******************************************************
echo CHOOSE HOW TO PROCESS THE FILES
echo *******************************************************
echo Input "1" to install games
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" goto select_medium
if %choice%=="none" goto s_mtp1_wrongchoice

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
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set medium=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" set "medium=SD"
if /i "%bs%"=="2" set "medium=EMMC"

if %medium%=="none" goto select_medium_wrongchoice

:start_installing
cls
call :program_logo
CD /d "%prog_dir%"

%pycommand% "%squirrel_lb%" -lib_call listmanager filter_list "%prog_dir%MTP1.txt","ext=nsp xci nsz","token=False",Print="False"
%pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller loop_install -xarg "%prog_dir%MTP1.txt" "destiny=%medium%" "verification=%MTP_verification%" "%w_folder%" "ch_medium=%MTP_aut_ch_medium%" "check_fw=%MTP_chk_fw%" "patch_keygen=%MTP_prepatch_kg%" "ch_base=%MTP_prechk_Base%" "ch_other=%MTP_prechk_Upd%" "install_mode=%MTP_ptch_inst_spec%" "st_crypto=%MTP_stc_installs%"

ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:F_TR
cls
call :program_logo
echo -------------------------------------------------
echo MTP - FILE TRANFER MODE ACTIVATED
echo -------------------------------------------------
echo *******************************************************
echo SELECT FUNCTION
echo *******************************************************
echo.
echo 1. FILE TRANSFER FROM LOCAL FILES
echo 2. FILE TRANSFER FROM REMOTE LIBRARIES (GDRIVE)
echo 3. CREATE XCI AND TRANSFER (LOCAL)
echo 4. CREATE MULTI-XCI AND TRANSFER (LOCAL)
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" goto F_TR_LOCAL
if /i "%bs%"=="2" goto F_TR_GD
if /i "%bs%"=="3" goto F_TR_C_xci_Transfer
if /i "%bs%"=="4" goto F_TR_C_mxci_Transfer
goto F_TR

:F_TR_LOCAL
call "%prog_dir%ztools\MtpFTLocal.bat"
goto MAIN
:F_TR_GD
call "%prog_dir%ztools\MtpTransferRemote.bat"
goto MAIN
:F_TR_C_xci_Transfer
call "%prog_dir%ztools\MtpCxciFTLocal.bat"
goto MAIN
:F_TR_C_mxci_Transfer
call "%prog_dir%ztools\MtpCmxciFTLocal.bat"
goto MAIN

:AUTOUPDATE
cls
call :program_logo
:select_medium_AUTOUPDATE
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

if %medium%=="none" goto select_medium_AUTOUPDATE
:set_auto_AUTOUPDATE
echo *******************************************************
echo AUTOSTART INSTALLATION?
echo *******************************************************
echo.
echo 1. START INSTALLATION AFTER DETECTING NEW CONTENT (CHECKS INSTALLED)
echo 2. SELECT CONTENT TO INSTALL (CHECKS INSTALLED)
echo 3. SELECT CONTENT TO INSTALL (USE REGISTRY, INCL. ARCHIVED AND REG. XCI)
echo.
ECHO ******************************************
echo Input "0" to return to the list options
echo Input "b" to go to the previous menu
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set autoupd_aut=none
set "use_archived=False"
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" set "autoupd_aut=True"
if /i "%bs%"=="2" set "autoupd_aut=False"
if /i "%bs%"=="3" set "autoupd_aut=False"
if /i "%bs%"=="3" set "use_archived=True"
if /i "%bs%"=="b" goto select_medium_AUTOUPDATE

if %autoupd_aut%=="none" goto set_auto_AUTOUPDATE

:set_source_AUTOUPDATE
echo *******************************************************
echo SOURCE FOR AUTOUPDATE
echo *******************************************************
echo.
echo 1. AUTOUPDATE FROM LOCAL LIBRARIES
echo 2. AUTOUPDATE FROM REMOTE LIBRARIES (GOOGLE DRIVE)
echo.
ECHO ******************************************
echo Input "0" to return to the list options
echo Input "b" to go to the previous menu
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" goto AUTOUPDATE_LOCAL
if /i "%bs%"=="2" goto AUTOUPDATE_GD
if /i "%bs%"=="b" goto set_auto_AUTOUPDATE

if %autoupd_aut%=="none" goto set_auto_AUTOUPDATE

:AUTOUPDATE_GD
CD /d "%prog_dir%"
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtp_gdrive update_console_from_gd -xarg "libraries=update" "destiny=%medium%" "exclude_xci=%MTP_exclude_xci_autinst%" "prioritize_nsz=%MTP_prioritize_NSZ%" "%prog_dir%MTP1GD.txt" "verification=%MTP_verification%" "ch_medium=%MTP_aut_ch_medium%" "ch_other=%MTP_prechk_Upd%" "autoupd_aut=%autoupd_aut%" "archived=%use_archived%"
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:AUTOUPDATE_LOCAL
CD /d "%prog_dir%"
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller update_console -xarg "libraries=all" "destiny=%medium%" "exclude_xci=%MTP_exclude_xci_autinst%" "prioritize_nsz=%MTP_prioritize_NSZ%" "%prog_dir%MTP1.txt" "verification=%MTP_verification%" "ch_medium=%MTP_aut_ch_medium%" "ch_other=%MTP_prechk_Upd%" "autoupd_aut=%autoupd_aut%" "archived=%use_archived%"

echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:INSTALLED
cls
call :program_logo
echo.
echo 1. DUMP INSTALLED CONTENT
echo 2. UNINSTALL CONTENT
echo 3. DELETE ARCHIVED GAMES
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" goto dump_games
if /i "%bs%"=="2" goto uninstall_games
if /i "%bs%"=="3" goto delete_archived
goto INSTALLED

:dump_games
echo.
ECHO ******************************************
echo CONTENT DUMPER
ECHO ******************************************
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtp_game_manager dump_content
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:uninstall_games
echo.
ECHO ******************************************
echo CONTENT UNINSTALLER
ECHO ******************************************
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtp_game_manager uninstall_content
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:delete_archived
echo.
ECHO ******************************************
echo DELETE ARCHIVED_GAMES
ECHO ******************************************
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtp_game_manager delete_archived
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:SAVES_wrongchoice
echo wrong choice
echo ............
:SAVES
cls
call :program_logo
echo.
ECHO ******************************************
echo SAVEGAMES DUMPER
ECHO ******************************************
echo.
echo 1. DUMP ALL SAVES
echo 2. SELECT WHAT SAVES TO DUMP
echo 3. BACKUP ONLY CURRENTLY INSTALLED (DBI 155 or newer)
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set backup_all=none
set onlyinstalled=none
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" set "backup_all=True"
if /i "%bs%"=="1" set "onlyinstalled=False"
if /i "%bs%"=="2" set "backup_all=False"
if /i "%bs%"=="2" set "onlyinstalled=False"
if /i "%bs%"=="3" set "backup_all=True"
if /i "%bs%"=="3" set "onlyinstalled=True"
if %backup_all%=="none" goto SAVES_wrongchoice

%pycommand% "%squirrel_lb%" -lib_call mtp.mtp_game_manager back_up_saves -xarg  %backup_all% %MTP_saves_Inline% %MTP_saves_AddTIDandVer% %romaji% "" %onlyinstalled%
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:SX_AUTOLOADER
cls
call :program_logo
echo.
ECHO ******************************************
echo SX AUTOLOADER OPTIONS
ECHO ******************************************
echo.
echo 1. GENERATE SX AUTOLOADER FILES FOR SD GAMES
echo 2. GENERATE SX AUTOLOADER FILES FOR HDD GAMES
echo 3. PUSH SX AUTOLOADER FILES TO CONSOLE
echo 4. CHECK AND CLEAN AUTOLOADER FILES (MEANT TO AVOID COLLISION BETWEEN SD AND HDD)
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set backup_all=none
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" ( %pycommand% "%squirrel_lb%" -lib_call mtp.mtp_game_manager gen_sx_autoloader_sd_files )
if /i "%bs%"=="1" goto s_exit_choice
if /i "%bs%"=="2" ( %pycommand% "%squirrel_lb%" -lib_call mtp.mtp_tools gen_sx_autoloader_files_menu )
if /i "%bs%"=="2" goto s_exit_choice
if /i "%bs%"=="3" ( %pycommand% "%squirrel_lb%" -lib_call mtp.mtp_tools push_sx_autoloader_libraries )
if /i "%bs%"=="3" goto s_exit_choice
if /i "%bs%"=="4" ( %pycommand% "%squirrel_lb%" -lib_call mtp.mtp_tools cleanup_sx_autoloader_files )
if /i "%bs%"=="4" goto s_exit_choice
goto SX_AUTOLOADER

:s_exit_choice
if exist MTP1.txt del MTP1.txt
if /i "%va_exit%"=="true" echo PROGRAM WILL CLOSE NOW
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto MAIN
if /i "%bs%"=="1" goto salida
goto s_exit_choice

:DEV_INF_wrongchoice
echo wrong choice
echo ............
:DEV_INF
cls
call :program_logo
ECHO ******************************************
echo INFORMATION
ECHO ******************************************
echo Input "1" to show device information
echo Input "2" to show installed and xci games on device
echo Input "3" to show list of new available updates or dlcs for PLAY-READY GAMES
echo Input "4" to show archived games
echo Input "5" to show list of new available updates or dlcs for ARCHIVED GAMES
echo.
ECHO ******************************************
echo Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto DEV_INF2
if /i "%bs%"=="2" goto GAMES_INSTALLED_INFO
if /i "%bs%"=="3" goto NC_AVAILABLE_INFO
if /i "%bs%"=="4" goto ARCHIVED_GAMES_INFO
if /i "%bs%"=="5" goto NC_ARCHIVED_GAMES_INFO
if /i "%bs%"=="0" goto MAIN
goto DEV_INF_wrongchoice

:DEV_INF2
cls
call :program_logo
echo.
"%MTP%" ShowInfo
echo.
PAUSE
goto DEV_INF

:GAMES_INSTALLED_INFO
cls
call :program_logo
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller get_installed_info -xarg "" False "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

:NC_AVAILABLE_INFO
cls
call :program_logo
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller get_installed_info -xarg "" True "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

:ARCHIVED_GAMES_INFO
cls
call :program_logo
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller get_archived_info -xarg False "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

:NC_ARCHIVED_GAMES_INFO
cls
call :program_logo
echo.
%pycommand% "%squirrel_lb%" -lib_call mtp.mtpinstaller get_archived_info -xarg True "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

::///////////////////////////////////////////////////
::NSCB_options.cmd configuration script
::///////////////////////////////////////////////////
:OPT_CONFIG
call "%batconfig%" "%op_file%" "%listmanager%" "%batdepend%"
cls
goto TOP_INIT

:contador_MTP1
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (MTP1.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo STILL !conta! FILES TO PROCESS
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

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
ECHO                                  VERSION 1.01 (MTP)
ECHO -------------------------------------------------------------------------------------
ECHO DBI by DUCKBILL: https://github.com/rashevskyv/switch/releases
ECHO Latest DBI: https://github.com/rashevskyv/switch/releases
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

:call_main
call "%prog_dir%\NSCB.bat"
exit /B

:salida
::pause
exit
