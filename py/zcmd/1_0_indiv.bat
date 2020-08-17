@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM MANUAL MODE. INDIVIDUAL PROCESSING
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
CD /d "%prog_dir%"
:main
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -----------------------------------------------
echo *******************************************************
echo WHAT DO YOU WNAT TO DO?
echo *******************************************************
echo Input "1" to repack CONVERT\REPACK files as XCI\NSP without titlerights
echo Input "2" to remove DELTAS from nsp update files
echo Input "3" to RENAME xci\nsp\nsz\xcz\nsx files
echo Input "4" to use xci SUPERTRIMMER\TRIMMER\UNTRIMMER
echo Input "5" to REBUILD nsp by cnmt order
echo Input "6" to VERIFY files
echo.
ECHO ******************************************
echo Or Input "0" to return to the main program
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" call "%cmdfolder%\1_1_repack.bat"
if /i "%bs%"=="2" call "%cmdfolder%\1_2_rem_deltas.bat"
if /i "%bs%"=="3" call "%cmdfolder%\1_3_renamer.bat"
if /i "%bs%"=="4" call "%cmdfolder%\1_4_xci_trimmer.bat"
if /i "%bs%"=="5" call "%cmdfolder%\1_5_rebuild_by_cnmt.bat"
if /i "%bs%"=="6" call "%cmdfolder%\1_6_verification.bat"
goto main
call "%main_program%"