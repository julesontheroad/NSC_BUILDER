@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"
set "bat_name=%~n0"
Title NSC_Builder v1.00d -- Profile: %ofile_name% -- by JulesOnTheRoad

:MAIN
cls
call :program_logo
ECHO .............................................................
echo Input "1" to enter into GAME INSTALLATION mode
echo Input "2" to enter into FILE TRANSFER mode
echo Input "3" to enter into AUTOUPDATE DEVICE FROM LIBRARY mode
echo Input "4" to enter into DUMP OR UNINSTALL GAMES
echo Input "5" to enter into BACKUP SAVES mode
echo Input "6" to enter into DEVICE INFORMATION mode
echo Input "7" to enter into GENERATE SX AUTOLOADER FILES mode
echo Input "0" to enter into CONFIGURATION mode
echo.
echo Input "N" to go to STANDARD MODES
echo Input "D" to enter GOOGLE DRIVE MODES
echo Input "L" to go to LEGACY MODES
echo .............................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" call "%cmdfolder%\M_1_0_mtpinstaller.bat"
if /i "%bs%"=="2" call "%cmdfolder%\M_2_0_mtptransfer.bat"
if /i "%bs%"=="3" call "%cmdfolder%\M_3_0_autoupdate.bat.bat"
if /i "%bs%"=="4" call "%cmdfolder%\M_4_0_dump_uninstall.bat"
if /i "%bs%"=="5" call "%cmdfolder%\M_5_0_saves.bat"
if /i "%bs%"=="6" call "%cmdfolder%\M_6_0_information.bat"
if /i "%bs%"=="7" call "%cmdfolder%\M_7_0_sx_autoloader.bat"
if /i "%bs%"=="N" call "%main_program%"
if /i "%bs%"=="L" call "%cmdfolder%\L_0_LEGACY.bat"
if /i "%bs%"=="D" call "%cmdfolder%\D_0_DriveMode.bat"
if /i "%bs%"=="0" call "%cmdfolder%\nscb_config.bat"
goto MAIN