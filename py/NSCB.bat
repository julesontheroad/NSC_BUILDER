@ECHO OFF
:TOP_INIT
set "prog_dir=%~dp0"
set "bat_name=%~n0"
set "ofile_name=%bat_name%_options.cmd"
set "opt_interface=Interface_options.cmd"
set "opt_server=Server_options.cmd"
Title NSC_Builder v1.00d -- Profile: %ofile_name% -- by JulesOnTheRoad
set "cmdfolder=%prog_dir%zcmd"
set "nscb_logos=%cmdfolder%\nscb_logos"
set "nscb_tools=%cmdfolder%\nscb_tools"
set "main_program=%prog_dir%%bat_name%.bat"
::-----------------------------------------------------
::OPTION FILES
::-----------------------------------------------------
set "op_file=%~dp0zconfig\%ofile_name%"
set "opt_interface=%~dp0zconfig\%opt_interface%"
set "opt_server=%~dp0zconfig\%opt_server%"
::-----------------------------------------------------
::COPY OPTIONS FROM OPTION FILE
::-----------------------------------------------------
setlocal
if exist "%op_file%" call "%op_file%"
endlocal & (
REM VARIABLES
set "safe_var=%safe_var%"
set "vrepack=%vrepack%"
set "vrename=%vrename%"
set "fi_rep=%fi_rep%"
set "zip_restore=%zip_restore%"
set "manual_intro=%manual_intro%"
set "va_exit=%va_exit%"
set "skipRSVprompt=%skipRSVprompt%"
set "oforg=%oforg%"
set "NSBMODE=%NSBMODE%"
set "romaji=%romaji%"
set "transnutdb=%transnutdb%"
set "workers=%workers%"
set "compression_lv=%compression_lv%"
set "compression_threads=%compression_threads%"
set "xci_export=%xci_export%"
set "MTP_verification=%MTP_verification%"
set "MTP_prioritize_NSZ=%MTP_prioritize_NSZ%"
set "MTP_exclude_xci_autinst=%MTP_exclude_xci_autinst%"
set "MTP_aut_ch_medium=%MTP_aut_ch_medium%"
set "MTP_chk_fw=%MTP_chk_fw%"
set "MTP_prepatch_kg=%MTP_prepatch_kg%"
set "MTP_prechk_Base=%MTP_prechk_Base%"
set "MTP_prechk_Upd=%MTP_prechk_Upd%"
set "MTP_saves_Inline=%MTP_saves_Inline%"
set "MTP_saves_AddTIDandVer=%MTP_saves_AddTIDandVer%"
set "MTP_pdrive_truecopy=%MTP_pdrive_truecopy%"
set "MTP_stc_installs=%MTP_stc_installs%"
set "MTP_ptch_inst_spec=%MTP_ptch_inst_spec%"

REM Copy function
set "pycommand=%pycommand%"
set "buffer=%buffer%"
set "nf_cleaner=%nf_cleaner%"
set "patchRSV=%patchRSV%"
set "vkey=%vkey%"
set "capRSV=%capRSV%"
set "fatype=%fatype%"
set "fexport=%fexport%"
set "skdelta=%skdelta%"
REM PROGRAMS
set "squirrel=%squirrel%"
set "MTP=%MTP%"
set "xci_lib=%xci_lib%"
set "nsp_lib=%nsp_lib%"
set "zip=%zip%"
set "hacbuild=%hacbuild%"
set "listmanager=%listmanager%"
set "batconfig=%batconfig%"
set "batdepend=%batdepend%"
set "infobat=%infobat%"
REM FILES
set "uinput=%uinput%"
set "dec_keys=%dec_keys%"
REM FOLDERS
set "w_folder=%~dp0%w_folder%"
set "fold_output=%fold_output%"
set "list_folder=%prog_dir%lists"
)
::-----------------------------------------------------
::SET ABSOLUTE ROUTES
::-----------------------------------------------------
::Program full route
if exist "%~dp0%squirrel%" set "squirrel=%~dp0%squirrel%"
if exist "%~dp0%xci_lib%"  set "xci_lib=%~dp0%xci_lib%"
if exist "%~dp0%nsp_lib%"  set "nsp_lib=%~dp0%nsp_lib%"
if exist "%~dp0%zip%"  set "zip=%~dp0%zip%"

if exist "%~dp0%hacbuild%"  set "hacbuild=%~dp0%hacbuild%"
if exist "%~dp0%listmanager%"  set "listmanager=%~dp0%listmanager%"
if exist "%~dp0%batconfig%"  set "batconfig=%~dp0%batconfig%"
if exist "%~dp0%batdepend%"  set "batdepend=%~dp0%batdepend%"
if exist "%~dp0%infobat%"  set "infobat=%~dp0%infobat%"
::Important files full route
if exist "%~dp0%uinput%"  set "uinput=%~dp0%uinput%"
if exist "%~dp0%dec_keys%"  set "dec_keys=%~dp0%dec_keys%"
::Folder output
CD /d "%~dp0"
if not exist "%fold_output%" MD "%fold_output%"
if not exist "%fold_output%" MD "%~dp0%fold_output%"
if exist "%~dp0%fold_output%"  set "fold_output=%~dp0%fold_output%"
if not exist "%list_folder%" MD "%list_folder%"
::-----------------------------------------------------
::CHECKS
::-----------------------------------------------------
::Option file check
if not exist "%op_file%" ( goto missing_things )
::Program checks
if not exist "%squirrel%" ( goto missing_things )
::Important files check
if not exist "%dec_keys%" ( goto missing_things )
::-----------------------------------------------------
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1

::Check if user is dragging a folder or a file
if "%~1"=="" goto manual
call "%cmdfolder%\0_auto" %*

:manual
cls
if "%NSBMODE%" EQU "legacy" call "%cmdfolder%\L_0_LEGACY.bat"
call "%nscb_logos%" "program_logo"
ECHO .......................................................
echo Input "1"  to process files INDIVIDUALLY
echo Input "2"  to enter into MULTI-PACK mode
echo Input "3"  to enter into MULTI-CONTENT SPLITTER mode
echo Input "4"  to enter into FILE-INFO mode
echo Input "5"  to enter into DATABASE building mode
echo Input "6"  to enter into ADVANCED mode
echo Input "7"  to enter into FILE-JOINER mode
echo Input "8"  to enter into COMPRESSOR\DECOMPRESSOR mode
echo Input "9"  to enter into FILE-RESTORATION mode
REM echo Input "10" to enter into FILE-MANAGEMENT mode
echo Input "0"  to enter into CONFIGURATION mode
echo.
echo Input "D" to enter GOOGLE DRIVE MODES
echo Input "M" to enter MTP MODES
echo Input "L" to enter LEGACY MODES
echo Input "I" to open INTERFACE
echo Input "S" to open SERVER
echo .......................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto normalmode
if /i "%bs%"=="2" goto multimode
if /i "%bs%"=="3" goto SPLMODE
if /i "%bs%"=="4" goto INFMODE
if /i "%bs%"=="5" goto DBMODE
if /i "%bs%"=="6" goto ADVmode
if /i "%bs%"=="7" goto JOINmode
if /i "%bs%"=="8" goto ZSTDmode
if /i "%bs%"=="9" goto RSTmode
REM if /i "%bs%"=="10" goto MNGmode
if /i "%bs%"=="M" goto MTPMode
if /i "%bs%"=="D" goto DriveMode
if /i "%bs%"=="L" goto LegacyMode
if /i "%bs%"=="I" goto InterfaceTrigger
if /i "%bs%"=="S" goto ServerTrigger
if /i "%bs%"=="0" goto OPT_CONFIG
goto manual_Reentry

:normalmode
call "%cmdfolder%\1_0_indiv.bat"
goto manual_Reentry
:multimode
call "%cmdfolder%\2_multi.bat"
goto manual_Reentry
:SPLMODE
call "%cmdfolder%\3_c_splitter.bat"
goto manual_Reentry
:INFMODE
call "%cmdfolder%\4_info.bat"
goto manual_Reentry
:DBMODE
call "%cmdfolder%\5_db.bat"
goto manual_Reentry
:ADVmode
call "%cmdfolder%\6_0_ADV.bat"
goto manual_Reentry
:JOINmode
call "%cmdfolder%\7_0_JOINER.bat"
goto manual_Reentry
:ZSTDmode
call "%cmdfolder%\8_0_ZSTD.bat"
goto manual_Reentry
:RSTmode
call "%cmdfolder%\9_0_RST.bat"
goto manual_Reentry
:MNGmode
call "%cmdfolder%\10_0_MNG.bat"
goto manual_Reentry
:LegacyMode
call "%cmdfolder%\L_0_LEGACY.bat"
goto manual_Reentry
:MTPMode
call "%cmdfolder%\M_0_MtpMode.bat"
goto manual_Reentry
:DriveMode
call "%cmdfolder%\D_0_DriveMode.bat"
goto manual_Reentry
:InterfaceTrigger
call Interface.bat
goto manual_Reentry
:ServerTrigger
call Server.bat
goto manual_Reentry
:OPT_CONFIG
call "%cmdfolder%\nscb_config.bat"

:missing_things
call "%nscb_logos%" "program_logo"
echo ....................................
echo You're missing the following things:
echo ....................................
echo.
::File full route
if not exist "%op_file%" echo - The config file is not correctly pointed or is missing.
if not exist "%squirrel%" echo - "squirrel.py" is not correctly pointed or is missing.
if not exist "%dec_keys%" echo - "keys.txt" is not correctly pointed or is missing.
echo.
pause
echo Program will exit now
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida
:salida
::pause
exit
