@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM FILE RESTORATION
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
CD /d "%prog_dir%"
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo FILE RESTORATION ACTIVATED
echo -------------------------------------------------
call "%cmdfolder%\9_1_restore.bat"
call "%main_program%
