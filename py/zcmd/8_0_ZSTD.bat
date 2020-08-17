@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM COMPRESSION
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
CD /d "%prog_dir%"
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo COMPRESS\DECOMPRESS MODE ACTIVATED
echo -------------------------------------------------
echo *******************************************************
echo WHAT DO YOU WNAT TO DO?
echo *******************************************************
echo Input "1" to compress nsp\xci to nsz\xcz
echo Input "2" for  pararell compression
echo Input "3" for decompress nsz\xcz
echo.
ECHO ******************************************
echo Or Input "0" to return to the main program
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" call "%cmdfolder%\8_1_compression.bat"
if /i "%bs%"=="2" call "%cmdfolder%\8_2_decompression.bat"
goto main
call "%main_program%"
