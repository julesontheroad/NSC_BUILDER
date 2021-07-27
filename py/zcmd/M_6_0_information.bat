:SX_AUTOLOADER
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - INFORMATION MODE ACTIVATED
echo -------------------------------------------------
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
if /i "%bs%"=="0" call "%main_program%"
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
%pycommand% "%sq_lc%" -lib_call mtp.mtpinstaller get_installed_info -xarg "" False "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

:NC_AVAILABLE_INFO
cls
call :program_logo
echo.
%pycommand% "%sq_lc%" -lib_call mtp.mtpinstaller get_installed_info -xarg "" True "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

:ARCHIVED_GAMES_INFO
cls
call :program_logo
echo.
%pycommand% "%sq_lc%" -lib_call mtp.mtpinstaller get_archived_info -xarg False "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

:NC_ARCHIVED_GAMES_INFO
cls
call :program_logo
echo.
%pycommand% "%sq_lc%" -lib_call mtp.mtpinstaller get_archived_info -xarg True "exclude_homebrew=True" "exclude_xci=False"
echo.
PAUSE
goto DEV_INF

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