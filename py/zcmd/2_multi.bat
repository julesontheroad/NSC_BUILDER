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
if exist "%list_folder%\2_0list.txt" del "%list_folder%\2_0list.txt"
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
%pycommand% "%sq_lc%" -lib_call cmd.cmd_tools userinput -xarg "%list_folder%\2_0list.txt" ext="nsp xci nsz xcz" userfile="%uinput%"    
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" call "%main_program%"
if /i "%eval%"=="1" set skip_list_split="true"
if /i "%eval%"=="1" goto multi_start_cleaning
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\2_0list.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\2_0list.txt" mode=file ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\2_0list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="5" ( %pycommand% "%sq_lc%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\2_0list.txt" "extlist=nsp xci nsz xcz" )

goto checkagain
echo.
:checkagain
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
%pycommand% "%sq_lc%" -lib_call cmd.cmd_tools userinput -xarg "%list_folder%\2_0list.txt" ext="nsp xci nsz xcz" userfile="%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" call "%main_program%"
if /i "%eval%"=="1" set "mlistfol=%list_folder%\a_multi"
if /i "%eval%"=="1" goto multi_start_cleaning
if /i "%eval%"=="2" set "mlistfol=%list_folder%\m_multi"
if /i "%eval%"=="2" goto multi_start_cleaning
if /i "%eval%"=="3" set "mlistfol=%list_folder%\m_multi"
if /i "%eval%"=="3" goto multi_saved_for_later
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\2_0list.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="5" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\2_0list.txt" mode=file ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="6" ( %pycommand% "%sq_lc%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\2_0list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="7" ( %pycommand% "%sq_lc%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\2_0list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" ( del "%prog_dir%lists\2_0list.txt" )

goto checkagain

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
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" goto multi_saved_for_later1
if /i "%bs%"=="2" ( %pycommand% "%squirrel%" -splid "%mlistfol%" -tfile "%list_folder%\2_0list.txt" )
if /i "%bs%"=="2" del "%list_folder%\2_0list.txt"
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
move /y "%list_folder%\2_0list.txt" "%mlistfol%\%lname%.txt" >nul
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
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" echo.
if /i "%bs%"=="1" echo CREATE ANOTHER JOB
if /i "%bs%"=="1" goto multi_manual_INIT
if /i "%bs%"=="1" goto salida
goto multi_saved_for_later2

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
%pycommand% "%sq_lc%" -lib_call listmanager remove_from_botton -xarg  "%list_folder%\2_0list.txt" "%bs%"

:showlist
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%sq_lc%" -lib_call listmanager printcurrent -xarg  "%list_folder%\1_1list.txt" "all" "counter=True"
goto checkagain

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
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" set "vrepack=cnsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=cboth"

if /i "%bs%"=="4" set "vrepack=nsp"
if /i "%bs%"=="4" set "skipRSVprompt=true"
if /i "%bs%"=="5" set "vrepack=both"

if %vrepack%=="none" goto m_cl_wrongchoice
:m_RSV_wrongchoice
if /i "%skipRSVprompt%"=="true" set "patchRSV=false"
if /i "%skipRSVprompt%"=="true" set "vkey=false"
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
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="0" set "patchRSV=false"
if /i "%bs%"=="0" set "vkey=false"
if /i "%bs%"=="1" set "patchRSV=true"
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
echo Input "11" to change top keygeneration to 11 (FW 9.1.0-10.1.1)
echo.
ECHO *****************************************
echo Or Input "b" to return to the option list
ECHO *****************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "vkey=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="f" set "vkey=false"
if /i "%bs%"=="0" set "vkey=0"
if /i "%bs%"=="0" set "capRSV=0"
if /i "%bs%"=="1" set "vkey=1"
if /i "%bs%"=="1" set "capRSV=65796"
if /i "%bs%"=="2" set "vkey=2"
if /i "%bs%"=="2" set "capRSV=201327002"
if /i "%bs%"=="3" set "vkey=3"
if /i "%bs%"=="3" set "capRSV=201392178"
if /i "%bs%"=="4" set "vkey=4"
if /i "%bs%"=="4" set "capRSV=268435656"
if /i "%bs%"=="5" set "vkey=5"
if /i "%bs%"=="5" set "capRSV=335544750"
if /i "%bs%"=="6" set "vkey=6"
if /i "%bs%"=="6" set "capRSV=402653494"
if /i "%bs%"=="7" set "vkey=7"
if /i "%bs%"=="7" set "capRSV=404750336"
if /i "%bs%"=="8" set "vkey=8"
if /i "%bs%"=="8" set "capRSV=469762048"
if /i "%bs%"=="9" set "vkey=9"
if /i "%bs%"=="9" set "capRSV=537919488"
if /i "%bs%"=="10" set "vkey=10"
if /i "%bs%"=="10" set "capRSV=603979776"
if /i "%bs%"=="11" set "vkey=11"
if /i "%bs%"=="11" set "capRSV=605028352"
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
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" move /y "%list_folder%\2_0list.txt" "%mlistfol%\mlist.txt" >nul
if /i "%bs%"=="1" goto m_process_jobs
if /i "%bs%"=="2" goto m_split_merge
goto m_KeyChange_skip

:m_split_merge
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%sq_lc%" -lib_call listmanager filter_list "%list_folder%\2_0list.txt","ext=nsp nsx xci","token=False",Print="False" )
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%squirrel%" -splid "%mlistfol%" -tfile "%list_folder%\2_0list.txt"
goto m_process_jobs2
:m_process_jobs
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%sq_lc%" -lib_call listmanager filter_list "%list_folder%\2_0list.txt","ext=nsp nsx xci","token=False",Print="False" )
cls
:m_process_jobs2
dir "%mlistfol%\*.txt" /b  > "%list_folder%\2_0list.txt"
rem if "%fatype%" EQU "-fat fat32" goto m_process_jobs_fat32
for /f "tokens=*" %%f in ( lists/2_0list.txt ) do (
set "listname=%%f"
if "%vrepack%" EQU "cnsp" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cnsp" call :m_split_merge_list_name
if "%vrepack%" EQU "cnsp" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t cnsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "xci" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "xci" call :m_split_merge_list_name
if "%vrepack%" EQU "xci" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "nsp" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "nsp" call :m_split_merge_list_name
if "%vrepack%" EQU "nsp" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t nsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "cboth" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cboth" call :m_split_merge_list_name
if "%vrepack%" EQU "cboth" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "cboth" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "cboth" call :m_split_merge_list_name
if "%vrepack%" EQU "cboth" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t cnsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "both" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "both" call :m_split_merge_list_name
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t nsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" call "%nscb_logos%" "program_logo"
if "%vrepack%" EQU "both" call :m_split_merge_list_name
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" -b "%buffer%" -pv "%patchRSV%" -kp "%vkey%" --RSVcap "%capRSV%" -fat "%fatype%" -fx "%fexport%" -ND "%skdelta%" -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
%pycommand% "%squirrel%" --strip_lines "%list_folder%\2_0list.txt" "1" "true"
if exist "%mlistfol%\%%f" del "%mlistfol%\%%f"
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
if exist "%prog_dir%lists\2_0list.txt" del "%prog_dir%lists\2_0list.txt"
goto m_exit_choice

:m_split_merge_list_name
echo *******************************************************
echo Processing list %listname%
echo *******************************************************
exit /B

:m_exit_choice
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
if exist "%prog_dir%lists\2_0list.txt" del "%prog_dir%lists\2_0list.txt"
if /i "%va_exit%"=="true" echo PROGRAM WILL CLOSE NOW
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" goto salida
goto m_exit_choice