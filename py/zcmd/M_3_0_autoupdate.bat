@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM MTP AUTO-UPDATE MODE
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:INSTALLED
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - AUTO-UPDATE MODE ACTIVATED
echo -------------------------------------------------
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
if /i "%bs%"=="0" call "%main_program%"
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
if /i "%bs%"=="0" call "%main_program%"
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" goto AUTOUPDATE_LOCAL
if /i "%bs%"=="2" goto AUTOUPDATE_GD
if /i "%bs%"=="b" goto set_auto_AUTOUPDATE

if %autoupd_aut%=="none" goto set_auto_AUTOUPDATE

:AUTOUPDATE_GD
CD /d "%prog_dir%"
echo.
%pycommand% "%sq_lc%" -lib_call mtp.mtp_gdrive update_console_from_gd -xarg "libraries=update" "destiny=%medium%" "exclude_xci=%MTP_exclude_xci_autinst%" "prioritize_nsz=%MTP_prioritize_NSZ%" "%prog_dir%M3_1list.txt" "verification=%MTP_verification%" "ch_medium=%MTP_aut_ch_medium%" "ch_other=%MTP_prechk_Upd%" "autoupd_aut=%autoupd_aut%" "archived=%use_archived%"
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:AUTOUPDATE_LOCAL
CD /d "%prog_dir%"
echo.
%pycommand% "%sq_lc%" -lib_call mtp.mtpinstaller update_console -xarg "libraries=all" "destiny=%medium%" "exclude_xci=%MTP_exclude_xci_autinst%" "prioritize_nsz=%MTP_prioritize_NSZ%" "%list_folder%\M3_2list.txt" "verification=%MTP_verification%" "ch_medium=%MTP_aut_ch_medium%" "ch_other=%MTP_prechk_Upd%" "autoupd_aut=%autoupd_aut%" "archived=%use_archived%"

echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice


:s_exit_choice
if exist "%list_folder%\M3_1list.txt" ( call "%nscb_tools%" "delete_if_empty" "M3_1list.txt" )
if exist "%list_folder%\M3_2list.txt" ( call "%nscb_tools%" "delete_if_empty" "M3_2list.txt" )
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