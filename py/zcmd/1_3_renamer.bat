REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM FILE RENAMER
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo FILE RENAMER
echo -----------------------------------------------
if exist "%list_folder%\1_3list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del "%list_folder%\1_3list.txt" )
endlocal
if not exist "%list_folder%\1_3list.txt" goto manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:prevlist0
ECHO .......................................................
echo Input "1" to auto-start processing from the previous list
echo Input "2" to erase list and make a new one.
echo Input "3" to continue building the previous list
echo .......................................................
echo NOTE: By pressing 3 you'll see the previous list
echo before starting the processing the files and you will
echo be able to add and delete items from the list
echo.
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="3" goto showlist
if /i "%bs%"=="2" goto delist
if /i "%bs%"=="1" goto rename
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo BAD CHOICE
goto prevlist0
:delist
del "%list_folder%\1_3list.txt" 2>&1>NUL
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -----------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................
:manual_INIT
endlocal
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "3" to add files to list via local libraries
echo Input "4" to add files to list via folder-walker
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%squirrel%" -t nsp nsz -tfile "%list_folder%\1_3list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%list_folder%\1_3list.txt" mode=folder ext="nsp xci nsx nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%list_folder%\1_3list.txt" mode=file ext="nsp xci nsx nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\1_3list.txt" "extlist=nsp xci nsx nsz xcz" )
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\1_3list.txt" "extlist=nsp xci nsx nsz xcz" )
goto checkagain
echo.
:checkagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Input "1" to start processing
echo Input "2" to add another folder to list via selector
echo Input "3" to add another file to list via selector
echo Input "4" to add files to list via local libraries
echo Input "5" to add files to list via folder-walker
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
echo ......................................................................
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%squirrel%" -t nsp nsz -tfile "%list_folder%\1_3list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" goto rename
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg  "%list_folder%\1_3list.txt" mode=folder ext="nsp xci nsx nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg  "%list_folder%\1_3list.txt" mode=file ext="nsp xci nsx nsz xcz" )  2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\1_3list.txt" "extlist=nsp xci nsx nsz xcz" )
if /i "%eval%"=="5" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\1_3list.txt" "extlist=nsp xci nsx nsz xcz" )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" ( del "%list_folder%\1_3list.txt" ) 2>&1>NUL

goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
%pycommand% "%squirrel%" -lib_call listmanager remove_from_botton -xarg  "%list_folder%\1_1list.txt" "%bs%"

:showlist
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%squirrel%" -lib_call listmanager printcurrent -xarg  "%list_folder%\1_1list.txt" "all" "counter=True"
goto checkagain

:rename
:s_rename_wrongchoice1
echo.
echo *******************************************************
echo TYPE OF RENAME
echo *******************************************************
echo Normal modes:
echo Input "1" to ALWAYS rename
echo Input "2" to NOT RENAME IF [TITLEID] is present
echo Input "3" to NOT RENAME IF [TITLEID] is equal to the one calculated
echo Input "4" to ONLY ADD ID
echo Input "5" to ADD ID + TAGS AND KEEP NAME TILL [
echo.
echo Sanitize:
echo Input "6" to REMOVE BAD characters from the file name
echo Input "7" to convert japanese\chinese to ROMAJI
echo.
echo Clean tags:
echo Input "8" to REMOVE [] tags from the filename
echo Input "9" to REMOVE () tags from the filename
echo Input "10" to REMOVE [] and () tags from the filename
echo Input "11" to REMOVE TITLE FROM FIRST [
echo Input "12" to REMOVE TITLE FROM FIRST (
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "renmode=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="1" set "renmode=force"
if /i "%bs%"=="1" set "oaid=false"
if /i "%bs%"=="2" set "renmode=skip_corr_tid"
if /i "%bs%"=="2" set "oaid=false"
if /i "%bs%"=="3" set "renmode=skip_if_tid"
if /i "%bs%"=="3" set "oaid=false"
if /i "%bs%"=="4" set "renmode=skip_corr_tid"
if /i "%bs%"=="4" set "oaid=true"
if /i "%bs%"=="5" set "renmode=skip_corr_tid"
if /i "%bs%"=="5" set "oaid=idtag"
if /i "%bs%"=="6" goto sanitize
if /i "%bs%"=="7" goto romaji

if /i "%bs%"=="8" set "tagtype=[]"
if /i "%bs%"=="8" goto filecleantags
if /i "%bs%"=="9" set "tagtype=()"
if /i "%bs%"=="9" goto filecleantags
if /i "%bs%"=="10" set "tagtype=false"
if /i "%bs%"=="10" goto filecleantags
if /i "%bs%"=="11" set "tagtype=["
if /i "%bs%"=="11" goto filecleantags
if /i "%bs%"=="12" set "tagtype=("
if /i "%bs%"=="12" goto filecleantags

if /i "%renmode%"=="none" echo WRONG CHOICE
if /i "%renmode%"=="none" goto s_rename_wrongchoice1
echo.
:s_rename_wrongchoice2
echo *******************************************************
echo ADD VERSION NUMBER
echo *******************************************************
echo Adds content version number to filename
echo.
echo Input "1" to ADD version number
echo Input "2" to NOT ADD version number
echo Input "3" to NOT ADD version in xci if VERSION=0
echo.
ECHO *********************************************
echo Or Input "b" to return to TYPE OF RENAME
echo Or Input "0" to return to the list options
ECHO *********************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "nover=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice1
if /i "%bs%"=="1" set "nover=false"
if /i "%bs%"=="2" set "nover=true"
if /i "%bs%"=="3" set "nover=xci_no_v0"
if /i "%nover%"=="none" echo WRONG CHOICE
if /i "%nover%"=="none" goto s_rename_wrongchoice2
echo.
:s_rename_wrongchoice3
echo *******************************************************
echo ADD LANGUAGE STRING
echo *******************************************************
echo Adds language tags for games and updates
echo.
echo Input "1" to NOT ADD language string
echo Input "2" to ADD language string
echo.
echo Note: Language can't be read from dlcs so this option
echo won't affect them
echo.
ECHO *********************************************
echo Or Input "b" to return to ADD VERSION NUMBER
echo Or Input "0" to return to the list options
ECHO *********************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "addlangue=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice2
if /i "%bs%"=="1" set "addlangue=false"
if /i "%bs%"=="2" set "addlangue=true"
if /i "%addlangue%"=="none" echo WRONG CHOICE
if /i "%addlangue%"=="none" goto s_rename_wrongchoice3
echo.
:s_rename_wrongchoice4
echo *******************************************************
echo DLC NAMES FALLBACK
echo *******************************************************
echo Current version request dlc names to nutdb, this option
echo states the fallback system to employ in case the name
echo can't be retrieved.
echo.
echo Normal format basename [contentname]
echo Option 3 format basename [contentname] [DLC Number]
echo.
echo Input "1" to KEEP basename
echo Input "2" to RENAME as DLC Number
echo Input "3" to keep basename and ADD DLC NUMBER AS TAG
echo.
ECHO *********************************************
echo Or Input "b" to return to ADD  KEEP DLC NAMES
echo Or Input "0" to return to the list options
ECHO *********************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "dlcrname=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice3
if /i "%bs%"=="1" set "dlcrname=false"
if /i "%bs%"=="2" set "dlcrname=true"
if /i "%bs%"=="3" set "dlcrname=tag"
if /i "%dlcrname%"=="none" echo WRONG CHOICE
if /i "%dlcrname%"=="none" goto s_rename_wrongchoice4
echo.
cls
call "%nscb_logos%" "program_logo"
set "workers=-threads 1"
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
%pycommand% "%squirrel%" -renf "single" -tfile "%prog_dir%lists/1_3list.txt" -t nsp xci nsx nsz xcz -renm %renmode% -nover %nover% -oaid %oaid% -addl %addlangue% -roma %romaji% -dlcrn %dlcrname% %workers%
if "%workers%" EQU "-threads 1" ( %pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/1_3list.txt" "1" "true" )
if "%workers%" NEQ "-threads 1" ( call :renamecheck )
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:renamecheck
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
set /a conta=!conta! + 1
)
if !conta! LEQ 0 ( del lists/1_3list.txt )
endlocal
if not exist "lists/1_3list.txt" goto s_exit_choice
exit /B

:sanitize
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
%pycommand% "%squirrel%" -snz "single" -tfile "%prog_dir%lists/1_3list.txt" -t nsp xci nsx nsz xcz
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/1_3list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:romaji
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
%pycommand% "%squirrel%" -roma "single" -tfile "%prog_dir%lists/1_3list.txt" -t nsp xci nsx nsz xcz
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/1_3list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:filecleantags
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (lists/1_3list.txt) do (
%pycommand% "%squirrel%" -cltg "single" -tfile "%prog_dir%lists/1_3list.txt" -t nsp xci nsx nsz xcz -tgtype "%tagtype%"
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/1_3list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
call "%nscb_tools%" "delete_if_empty" "1_3list.txt"
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
goto s_exit_choice
