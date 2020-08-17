@ECHO OFF
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM RENAME TO NSX
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
CD /d "%prog_dir%"
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MANAGEMENT MODE ACTIVATED
echo -------------------------------------------------
call "%cmdfolder%\10_1_rename_to_nsx.bat"
call "%main_program%
