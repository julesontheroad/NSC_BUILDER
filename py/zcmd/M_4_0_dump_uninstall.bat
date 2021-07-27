:INSTALLED
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - DUMP OR UNINSTALL MODE ACTIVATED
echo -------------------------------------------------
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" goto dump_games
if /i "%bs%"=="2" goto uninstall_games
if /i "%bs%"=="3" goto delete_archived
goto INSTALLED

:dump_games
echo.
ECHO ******************************************
echo MTP - CONTENT DUMPER
ECHO ******************************************
echo.
%pycommand% "%sq_lc%" -lib_call mtp.mtp_game_manager dump_content
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
%pycommand% "%sq_lc%" -lib_call mtp.mtp_game_manager uninstall_content
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
%pycommand% "%sq_lc%" -lib_call mtp.mtp_game_manager delete_archived
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