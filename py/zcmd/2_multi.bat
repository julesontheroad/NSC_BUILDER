::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:: MULTI-MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////

:multimode
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1
if exist "%list_folder%\a_multi" RD /S /Q "%list_folder%\a_multi" >NUL 2>&1
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo MULTI-REPACK MODE ACTIVATED
echo -----------------------------------------------
if exist "mlist.txt" del "mlist.txt"
:multi_manual_INIT
endlocal
set skip_list_split="false"
set "mlistfol=%list_folder%\m_multi"
echo Drag files or folders to create a list
echo Note: Remember to press enter after each file\folder dragged
echo.
ECHO ***********************************************
echo Input "1" to process PREVIOUSLY SAVED JOBS
echo Input "2" to add another folder to list via selector
echo Input "3" to add another file to list via selector
echo Input "4" to add files to list via local libraries
echo Input "5" to add files to list via folder-walker
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%squirrel%" -t nsp xci nsz xcz -tfile "%prog_dir%mlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" set skip_list_split="true"
if /i "%eval%"=="1" goto multi_start_cleaning
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%prog_dir%mlist.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%prog_dir%mlist.txt" mode=file ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%prog_dir%mlist.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="5" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%prog_dir%mlist.txt" "extlist=nsp xci nsz xcz" )

goto multi_checkagain
echo.
:multi_checkagain
set "mlistfol=%list_folder%\a_multi"
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Input "1" to start processing current list
echo Input "2" to add to saved lists and process them
echo Input "3" to save list for later
echo Input "4" to add another folder to list via selector
echo Input "5" to add another file to list via selector
echo Input "6" to add files to list via local libraries
echo Input "7" to add files to list via folder-walker
echo.
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
echo ......................................................................
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%squirrel%" -t nsp xci nsz xcz -tfile "%prog_dir%mlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" set "mlistfol=%list_folder%\a_multi"
if /i "%eval%"=="1" goto multi_start_cleaning
if /i "%eval%"=="2" set "mlistfol=%list_folder%\m_multi"
if /i "%eval%"=="2" goto multi_start_cleaning
if /i "%eval%"=="3" set "mlistfol=%list_folder%\m_multi"
if /i "%eval%"=="3" goto multi_saved_for_later
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%prog_dir%mlist.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="5" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%prog_dir%mlist.txt" mode=file ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="6" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%prog_dir%mlist.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="7" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%prog_dir%mlist.txt" "extlist=nsp xci nsz xcz" )
REM if /i "%eval%"=="2" goto multi_set_clogo
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto multi_showlist
if /i "%eval%"=="r" goto multi_r_files
if /i "%eval%"=="z" del mlist.txt

goto multi_checkagain

:multi_saved_for_later
if not exist "%list_folder%" MD "%list_folder%" >NUL 2>&1
if not exist "%mlistfol%" MD "%mlistfol%" >NUL 2>&1
echo SAVE LIST JOB FOR ANOTHER TIME
echo ......................................................................
echo Input "1" to SAVE the list as a MERGE job (single multifile list)
echo Input "2" to SAVE the list as a MULTIPLE jobs by baseid of files
echo.
ECHO *******************************************
echo Input "b" to keep building the list
echo Input "0" to go back to the selection menu
ECHO *******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto multi_saved_for_later1
if /i "%bs%"=="2" ( %pycommand% "%squirrel%" -splid "%mlistfol%" -tfile "%prog_dir%mlist.txt" )
if /i "%bs%"=="2" del "%prog_dir%mlist.txt"
if /i "%bs%"=="2" goto multi_saved_for_later2
echo WRONG CHOICE!!
goto multi_saved_for_later
:multi_saved_for_later1
echo.
echo CHOOSE NAME FOR THE JOB
echo ......................................................................
echo The list will be saved under the name of your choosing in the list's
echo folder ( Route is "program's folder\list\m_multi")
echo.
set /p lname="Input name for the list job: "
set lname=%lname:"=%
move /y "%prog_dir%mlist.txt" "%mlistfol%\%lname%.txt" >nul
echo.
echo JOB SAVED!!!
:multi_saved_for_later2
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to create other job
echo Input "2" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" echo.
if /i "%bs%"=="1" echo CREATE ANOTHER JOB
if /i "%bs%"=="1" goto multi_manual_INIT
if /i "%bs%"=="1" goto salida
goto multi_saved_for_later2

:multi_r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:multi_update_list1
if !pos1! GTR !pos2! ( goto :multi_update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :multi_update_list1
:multi_update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<mlist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>mlist.txt.new
endlocal
move /y "mlist.txt.new" "mlist.txt" >nul
endlocal

:multi_showlist
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo MULTI-REPACK MODE ACTIVATED
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                FILES TO PROCESS
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (mlist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

goto multi_checkagain

:m_cl_wrongchoice
echo wrong choice
echo ............
:multi_start_cleaning
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo STANDARD CRYPTO OPTIONS:
echo Input "1" to repack list as Ticketless NSP
echo Input "2" to repack list as XCI
echo Input "3" to repack list as both T-NSP and XCI
echo.
echo SPECIAL OPTIONS:
echo Input "4" to as NSP with only Unmodified eshop nca files
echo Input "5" to repack list as both NSP-U and XCI
echo.
ECHO *****************************************
echo Or Input "b" to return to the option list
ECHO *****************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="1" set "vrepack=cnsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=cboth"

if /i "%bs%"=="4" set "vrepack=nsp"
if /i "%bs%"=="4" set "skipRSVprompt=true"
if /i "%bs%"=="5" set "vrepack=both"

if %vrepack%=="none" goto m_cl_wrongchoice
:m_RSV_wrongchoice
if /i "%skipRSVprompt%"=="true" set "patchRSV=-pv false"
if /i "%skipRSVprompt%"=="true" set "vkey=-kp false"
if /i "%skipRSVprompt%"=="true" goto m_KeyChange_skip
echo *******************************************************
echo DO YOU WANT TO PATCH THE REQUIRED-SYSTEM-VERSION
echo *******************************************************
echo If you choose to patch it will be set to match the
echo nca crypto so it'll only ask to update your system
echo in the case it's necessary
echo.
echo Input "0" to don't patch the Required System Version
echo Input "1" to "PATCH" the Required System Version
echo.
ECHO *****************************************
echo Or Input "b" to return to the option list
ECHO *****************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set patchRSV=none
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="0" set "vkey=-kp false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto m_RSV_wrongchoice
if /i "%bs%"=="0" goto m_KeyChange_skip

:m_KeyChange_wrongchoice
echo *******************************************************
echo SET MAXIMUM KEYGENERATION\RSV ALOWED
echo *******************************************************
echo Depending on your choice keygeneration and RSV will be
echo lowered to the corresponding keygeneration range in case
echo read keygeneration value is bigger than the one specified
echo in the program.
echo THIS WON'T ALWAYS WORK TO LOWER THE FIRMWARE REQUIREMENT.
echo.
echo Input "f" to not change the keygeneration
echo Input "0" to change top keygeneration to 0 (FW 1.0)
echo Input "1" to change top keygeneration to 1 (FW 2.0-2.3)
echo Input "2" to change top keygeneration to 2 (FW 3.0)
echo Input "3" to change top keygeneration to 3 (FW 3.0.1-3.02)
echo Input "4" to change top keygeneration to 4 (FW 4.0.0-4.1.0)
echo Input "5" to change top keygeneration to 5 (FW 5.0.0-5.1.0)
echo Input "6" to change top keygeneration to 6 (FW 6.0.0-6.1.0)
echo Input "7" to change top keygeneration to 7 (FW 6.2.0)
echo Input "8" to change top keygeneration to 8 (FW 7.0.0-8.0.1)
echo Input "9" to change top keygeneration to 9 (FW 8.1.0)
echo Input "10" to change top keygeneration to 10 (FW 9.0.0-9.01)
echo Input "11" to change top keygeneration to 11 (FW 9.1.0)
echo.
ECHO *****************************************
echo Or Input "b" to return to the option list
ECHO *****************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "vkey=none"
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="f" set "vkey=-kp false"
if /i "%bs%"=="0" set "vkey=-kp 0"
if /i "%bs%"=="0" set "capRSV=--RSVcap 0"
if /i "%bs%"=="1" set "vkey=-kp 1"
if /i "%bs%"=="1" set "capRSV=--RSVcap 65796"
if /i "%bs%"=="2" set "vkey=-kp 2"
if /i "%bs%"=="2" set "capRSV=--RSVcap 201327002"
if /i "%bs%"=="3" set "vkey=-kp 3"
if /i "%bs%"=="3" set "capRSV=--RSVcap 201392178"
if /i "%bs%"=="4" set "vkey=-kp 4"
if /i "%bs%"=="4" set "capRSV=--RSVcap 268435656"
if /i "%bs%"=="5" set "vkey=-kp 5"
if /i "%bs%"=="5" set "capRSV=--RSVcap 335544750"
if /i "%bs%"=="6" set "vkey=-kp 6"
if /i "%bs%"=="6" set "capRSV=--RSVcap 402653494"
if /i "%bs%"=="7" set "vkey=-kp 7"
if /i "%bs%"=="7" set "capRSV=--RSVcap 404750336"
if /i "%bs%"=="8" set "vkey=-kp 8"
if /i "%bs%"=="8" set "capRSV=--RSVcap 469762048"
if /i "%bs%"=="9" set "vkey=-kp 9"
if /i "%bs%"=="9" set "capRSV=--RSVcap 537919488"
if /i "%bs%"=="10" set "vkey=-kp 10"
if /i "%bs%"=="10" set "capRSV=--RSVcap 603979776"
if /i "%bs%"=="11" set "vkey=-kp 11"
if /i "%bs%"=="11" set "capRSV=--RSVcap 605028352"
if /i "%vkey%"=="none" echo WRONG CHOICE
if /i "%vkey%"=="none" goto m_KeyChange_wrongchoice

:m_KeyChange_skip
if not exist "%list_folder%" MD "%list_folder%" >NUL 2>&1
if not exist "%mlistfol%" MD "%mlistfol%" >NUL 2>&1
if %skip_list_split% EQU "true" goto m_process_jobs
echo *******************************************************
echo HOW DO YOU WANT TO PROCESS THE FILES?
echo *******************************************************
echo The separate by base id mode is capable to identify the
echo content that corresponds to each game and create multiple
echo multi-xci or multi-nsp from the same list file
echo.
echo Input "1" to MERGE all files into a single file
echo Input "2" to SEPARATE into multifiles by baseid
echo.
ECHO *****************************************
echo Or Input "b" to return to the option list
ECHO *****************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="1" move /y "%prog_dir%mlist.txt" "%mlistfol%\mlist.txt" >nul
if /i "%bs%"=="1" goto m_process_jobs
if /i "%bs%"=="2" goto m_split_merge
goto m_KeyChange_skip

:m_split_merge
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%mlist.txt","ext=nsp nsx xci","token=False",Print="False" )
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%squirrel%" -splid "%mlistfol%" -tfile "%prog_dir%mlist.txt"
goto m_process_jobs2
:m_process_jobs
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%mlist.txt","ext=nsp nsx xci","token=False",Print="False" )
cls
:m_process_jobs2
dir "%mlistfol%\*.txt" /b  > "%prog_dir%mlist.txt"
rem if "%fatype%" EQU "-fat fat32" goto m_process_jobs_fat32
for /f "tokens=*" %%f in (mlist.txt) do (
set "listname=%%f"
if "%vrepack%" EQU "cnsp" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cnsp" call :m_split_merge_list_name
if "%vrepack%" EQU "cnsp" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "xci" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "xci" call :m_split_merge_list_name
if "%vrepack%" EQU "xci" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "nsp" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "nsp" call :m_split_merge_list_name
if "%vrepack%" EQU "nsp" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "cboth" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cboth" call :m_split_merge_list_name
if "%vrepack%" EQU "cboth" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "cboth" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cboth" call :m_split_merge_list_name
if "%vrepack%" EQU "cboth" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "both" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "both" call :m_split_merge_list_name
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "both" call :m_split_merge_list_name
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
%pycommand% "%squirrel%" --strip_lines "%prog_dir%mlist.txt" "1" "true"
if exist "%mlistfol%\%%f" del "%mlistfol%\%%f"
rem call :multi_contador_NF
)

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%"
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -tfile "%w_folder%\filename.txt" -ifo "%w_folder%\archfolder" -archive "%gefolder%" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
if exist "%mlistfol%" RD /S /Q "%mlistfol%" >NUL 2>&1
if exist mlist.txt del mlist.txt
goto m_exit_choice

:m_process_jobs_fat32
CD /d "%prog_dir%"
set "finalname=tempname"
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (mlist.txt) do (
set "listname=%%f"
set "list=%mlistfol%\%%f"
call :m_split_merge_list_name
call :m_process_jobs_fat32_2
%pycommand% "%squirrel%" --strip_lines "%prog_dir%mlist.txt" "1" "true"
if exist "%mlistfol%\%%f" del "%mlistfol%\%%f"
rem call :multi_contador_NF
)
goto m_exit_choice
:m_process_jobs_fat32_2
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
copy "%list%" "%w_folder%\list.txt" >NUL 2>&1
for /f "usebackq tokens=*" %%f in ("%w_folder%\list.txt") do (
echo %%f
set "name=%%~nf"
set "filename=tempname"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :multi_nsp_manual
if "%%~nxf"=="%%~nf.xci" call :multi_xci_manual
)
if exist "%w_folder%\list.txt" del "%w_folder%\list.txt"
if "%vrepack%" EQU "cnsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "cboth" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "cboth" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
RD /S /Q "%w_folder%\secure" >NUL 2>&1
RD /S /Q "%w_folder%\normal" >NUL 2>&1
if exist "%w_folder%\archfolder" goto m_process_jobs_fat32_3
if exist "%w_folder%\*.xc*" goto m_process_jobs_fat32_4
if exist "%w_folder%\*.ns*" goto m_process_jobs_fat32_4
if exist "%w_folder%\tempname.*" goto m_process_jobs_fat32_4
:m_process_jobs_fat32_3
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\tempname.nsp" )
endlocal
dir "%fold_output%\tempname.*" /b  > "%w_folder%\templist.txt"
for /f "usebackq tokens=*" %%f in ("%w_folder%\templist.txt") do (
%pycommand% "%squirrel%" -roma %romaji% --renameftxt "%fold_output%\%%f" -tfile "%list%"
if exist "%w_folder%\templist.txt" del "%w_folder%\templist.txt"
)

if exist "%w_folder%\*.xc*" goto m_process_jobs_fat32_4
if exist "%w_folder%\*.ns*" goto m_process_jobs_fat32_4
RD /S /Q "%w_folder%" >NUL 2>&1
exit /B

:m_process_jobs_fat32_4
dir "%w_folder%\tempname.*" /b  > "%w_folder%\templist.txt"
for /f "usebackq tokens=*" %%f in ("%w_folder%\templist.txt") do (
%pycommand% "%squirrel%" -roma %romaji% --renameftxt "%w_folder%\%%f" -tfile "%list%"
)
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
exit /B

:m_split_merge_list_name
echo *******************************************************
echo Processing list %listname%
echo *******************************************************
exit /B

:m_normal_merge
rem if "%fatype%" EQU "-fat fat32" goto m_KeyChange_skip_fat32
REM For the current beta the filenames are calculted. This code remains commented for future reintegration
rem echo *******************************************************
rem echo ENTER FINAL FILENAME FOR THE OUTPUT FILE
rem echo *******************************************************
rem echo.
rem echo Or Input "b" to return to the option list
rem echo.
rem set /p bs="Please type the name without extension: "
rem set finalname=%bs:"=%
rem if /i "%finalname%"=="b" goto multi_checkagain

cls
if "%vrepack%" EQU "cnsp" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cnsp" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "xci" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "xci" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "nsp" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "nsp" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "cboth" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cboth" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "cboth" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cboth" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "both" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -tfile "%w_folder%\filename.txt" -ifo "%w_folder%\archfolder" -archive "%gefolder%" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
goto m_exit_choice

:m_KeyChange_skip_fat32
CD /d "%prog_dir%"
echo *******************************************************
echo ENTER FINAL FILENAME FOR THE OUTPUT FILE
echo *******************************************************
echo.
echo Or Input "b" to return to the option list
echo.
set /p bs="Please type the name without extension: "
set finalname=%bs:"=%
if /i "%finalname%"=="b" goto multi_checkagain

cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (mlist.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :multi_nsp_manual
if "%%~nxf"=="%%~nf.xci" call :multi_xci_manual
%pycommand% "%squirrel%" --strip_lines "%prog_dir%mlist.txt" "1" "true"
rem call :multi_contador_NF
)
set "filename=%finalname%"
set "end_folder=%finalname%"
set "filename=%finalname%[multi]"
::pause
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
goto m_exit_choice

:m_exit_choice
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
if exist mlist.txt del mlist.txt
if /i "%va_exit%"=="true" echo PROGRAM WILL CLOSE NOW
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto m_exit_choice


:multi_nsp_manual
set "showname=%orinput%"
call :processing_message
call :squirrell
%pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
call :thumbup
call :delay
exit /B

:multi_xci_manual
::FOR XCI FILES
set "showname=%orinput%"
call :processing_message
MD "%w_folder%" >NUL 2>&1
MD "%w_folder%\secure" >NUL 2>&1
MD "%w_folder%\normal" >NUL 2>&1
MD "%w_folder%\update" >NUL 2>&1
call :getname
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
call :thumbup
call :delay
exit /B

:multi_contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo STILL !conta! FILES TO PROCESS
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

REM the logo function has been disabled temporarly for the current beta, the code remains here
REM unaccessed for future modification and reintegration
:multi_set_clogo
cls
call "%nscb_logos%" "program_logo"
echo ------------------------------------------
echo Set custom logo or predominant game
echo ------------------------------------------
echo Indicated for multi-game xci.
echo Currently custom logos and names are set dragging a nsp or control nca
echo That way the program will copy the control nca in the normal partition
echo If you don't add a custom logo the logo will be set from one of your games
echo ..........................................
echo Input "b" to go back to the list builder
echo ..........................................
set /p bs="OR DRAG A NSP OR NCA FILE OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if /i "%bs%"=="b" ( goto multi_checkagain )
if exist "%bs%" ( goto multi_checklogo )
goto multi_set_clogo

:multi_checklogo
if exist "%~dp0logo.txt" del "%~dp0logo.txt" >NUL 2>&1
echo %bs%>"%~dp0hlogo.txt"
FINDSTR /L ".nsp" "%~dp0hlogo.txt" >"%~dp0logo.txt"
FINDSTR /L ".nca" "%~dp0hlogo.txt" >>"%~dp0logo.txt"
set /p custlogo=<"%~dp0logo.txt"
del "%~dp0hlogo.txt"
::echo %custlogo%
for /f "usebackq tokens=*" %%f in ( "%~dp0logo.txt" ) do (
set "logoname=%%~nxf"
if "%%~nxf"=="%%~nf.nsp" goto ext_log
if "%%~nxf"=="%%~nf.nca" goto check_log
)

:ext_log
del "%~dp0logo.txt"
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
if exist "%w_folder%\normal" RD /S /Q "%w_folder%\normal" >NUL 2>&1

%pycommand% "%squirrel%" --nsptype "%custlogo%">"%w_folder%\nsptype.txt"
set /p nsptype=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt"
if "%nsptype%" EQU "DLC" echo.
if "%nsptype%" EQU "DLC" echo ---NSP DOESN'T HAVE A CONTROL NCA---
if "%nsptype%" EQU "DLC" echo.
if "%nsptype%" EQU "DLC" ( goto multi_set_clogo )
MD "%w_folder%\normal" >NUL 2>&1
%pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\normal" --NSP_copy_nca_control "%custlogo%"
echo ................
echo "EXTRACTED LOGO"
echo ................
echo.
goto multi_checkagain

:check_log
del "%~dp0logo.txt"
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
if exist "%w_folder%\normal" RD /S /Q "%w_folder%\normal" >NUL 2>&1
%pycommand% "%squirrel%" --ncatype "%custlogo%">"%w_folder%\ncatype.txt"
set /p ncatype=<"%w_folder%\ncatype.txt"
del "%w_folder%\ncatype.txt"
if "%ncatype%" NEQ "Content.CONTROL" echo.
if "%ncatype%" NEQ "Content.CONTROL" echo ---NCA IS NOT A CONTROL TYPE---
if "%ncatype%" NEQ "Content.CONTROL" echo.
if "%ncatype%" NEQ "Content.CONTROL" ( goto multi_set_clogo )
MD "%w_folder%\normal" >NUL 2>&1
copy "%custlogo%" "%w_folder%\normal\%logoname%"
echo.
goto multi_checkagain
exit