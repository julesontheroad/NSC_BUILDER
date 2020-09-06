@ECHO OFF
CD /d "%prog_dir%"
set "bat_name=%~n0"
Title NSC_Builder v1.00d -- Profile: %ofile_name% -- by JulesOnTheRoad

:MAIN
cls
call "%nscb_logos%" "program_logo"
ECHO .......................................................
echo Input "1" to enter into DOWNLOAD mode
echo Input "2" to enter into FILE-INFO mode
echo Input "0"  to enter into CONFIGURATION mode
echo.
echo Input "N" to go to STANDARD MODES
echo Input "M" to enter MTP MODE
echo Input "D" to enter GOOGLE DRIVE MODES
echo Input "L" to go to LEGACY MODES
echo .......................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto DOWNLOADMODE
if /i "%bs%"=="2" goto INFMODE
if /i "%bs%"=="N" call "%main_program%"
if /i "%bs%"=="L" call "%cmdfolder%\L_0_LEGACY.bat"
if /i "%bs%"=="M" call "%cmdfolder%\M_0_MtpMode.bat"
if /i "%bs%"=="0" call "%cmdfolder%\nscb_config.bat"
goto MAIN

:DOWNLOADMODE
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%sq_lc%" -lib_call Drive.Download Interface
goto MAIN

:INFMODE
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%sq_lc%" -lib_call Drive.Info Interface
goto MAIN
