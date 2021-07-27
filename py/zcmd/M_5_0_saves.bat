:SAVES
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - SAVEGAMES DUMPER MODE ACTIVATED
echo -------------------------------------------------
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" set "backup_all=True"
if /i "%bs%"=="1" set "onlyinstalled=False"
if /i "%bs%"=="2" set "backup_all=False"
if /i "%bs%"=="2" set "onlyinstalled=False"
if /i "%bs%"=="3" set "backup_all=True"
if /i "%bs%"=="3" set "onlyinstalled=True"
if %backup_all%=="none" goto SAVES_wrongchoice

%pycommand% "%sq_lc%" -lib_call mtp.mtp_game_manager back_up_saves -xarg  %backup_all% %MTP_saves_Inline% %MTP_saves_AddTIDandVer% %romaji% "" %onlyinstalled%
echo.
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
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