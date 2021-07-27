@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM MTP FILE TRANSFER MODE
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:MAIN
cls
call "%nscb_logos%" "program_logo"
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" call "%cmdfolder%\M_2_1_mtptr_local.bat"
if /i "%bs%"=="2" call "%cmdfolder%\M_2_2_mtptr_remote.bat"
if /i "%bs%"=="3" call "%cmdfolder%\M_2_3_mtptr_CXciTr.bat"
if /i "%bs%"=="4" call "%cmdfolder%\M_2_4_mtptr_CMXciTr.bat"
goto MAIN
call "%main_program%"