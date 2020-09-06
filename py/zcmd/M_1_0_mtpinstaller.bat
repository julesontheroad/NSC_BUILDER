@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM MTP INSTALLER MODE
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:MAIN
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MTP - GAME INSTALLATION MODE ACTIVATED
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" call "%cmdfolder%\M_1_1_mtpinst_local.bat"
if /i "%bs%"=="2" call "%cmdfolder%\M_1_2_mtpinst_remote.bat"
goto MAIN
call "%main_program%"