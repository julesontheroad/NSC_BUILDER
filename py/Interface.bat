@ECHO OFF
:TOP_INIT
set "prog_dir=%~dp0"
set "bat_name=%~n0"
set "ofile_name=%bat_name%_options.cmd"
Title NSC_Builder v0.90 -- Profile: %ofile_name% -- by JulesOnTheRoad
set "list_folder=%prog_dir%lists"
::-----------------------------------------------------
::EDIT THIS VARIABLE TO LINK OTHER OPTION FILE
::-----------------------------------------------------
set "op_file=%~dp0zconfig\%ofile_name%"

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
REM set "trn_skip=%trn_skip%"
REM set "updx_skip=%updx_skip%"
REM set "ngx_skip=%ngx_skip%"

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
set "nut=%nut%"
set "squirrel=%nut%"
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
set "zip_fold=%~dp0%zip_fold%"
)
::-----------------------------------------------------
::SET ABSOLUTE ROUTES
::-----------------------------------------------------
::Program full route
if exist "%~dp0%nut%" set "nut=%~dp0%nut%"
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


%pycommand% "%squirrel%" -lib_call Interface start

