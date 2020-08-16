@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"

REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM ADVANCE MODE
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:normalmode
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo ADVANCE MODE ACTIVATED
echo -------------------------------------------------
echo *******************************************************
echo WHAT DO YOU WNAT TO DO?
echo *******************************************************
echo Input "1" to extract all files from nsp\xci
echo Input "2" for raw extraction (Use in case an nca gives magic error)
echo Input "3" to extract all nca files as plaintext
echo Input "4" to extract all nca files with titlerights removed
echo Input "5" to extract nca contents from nsp\xci
echo Input "6" to patch a linked account requirement
echo.
ECHO ******************************************
echo Or Input "0" to return to the main program
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" call "%cmdfolder%\6_1_extraction.bat"
if /i "%bs%"=="2" call "%cmdfolder%\6_2_raw_extraction.bat"
if /i "%bs%"=="3" call "%cmdfolder%\6_3_plaintext.bat"
if /i "%bs%"=="4" call "%cmdfolder%\6_4_extract_contents.bat"
if /i "%bs%"=="5" call "%cmdfolder%\6_5_extract_withoutrights.bat"
if /i "%bs%"=="6" call "%cmdfolder%\6_6_patch_link_account.bat"
goto normalmode
call "%main_program%