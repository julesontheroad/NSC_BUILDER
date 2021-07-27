:SX_AUTOLOADER
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - SX AUTOLOADER GENERATOR MODE ACTIVATED
echo -------------------------------------------------
ECHO ******************************************
echo SAVEGAMES DUMPER
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" ( %pycommand% "%sq_lc%" -lib_call mtp.mtp_game_manager gen_sx_autoloader_sd_files )
if /i "%bs%"=="1" goto s_exit_choice
if /i "%bs%"=="2" ( %pycommand% "%sq_lc%" -lib_call mtp.mtp_tools gen_sx_autoloader_files_menu )
if /i "%bs%"=="2" goto s_exit_choice
if /i "%bs%"=="3" ( %pycommand% ""%sq_lc%" -lib_call mtp.mtp_tools push_sx_autoloader_libraries )
if /i "%bs%"=="3" goto s_exit_choice
if /i "%bs%"=="4" ( %pycommand% "%sq_lc%" -lib_call mtp.mtp_tools cleanup_sx_autoloader_files )
if /i "%bs%"=="4" goto s_exit_choice
goto SX_AUTOLOADER

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