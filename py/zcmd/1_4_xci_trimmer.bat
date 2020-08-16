REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM XCI TRIMMER/SUPERTRIMMER/UNTRIMMER
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo XCI TRIMMER/SUPERTRIMMER/UNTRIMMER
echo -----------------------------------------------
if exist "%list_folder%\1_4list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (lists/1_4list.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (lists/1_4list.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del "%list_folder%\1_4list.txt" )
endlocal
if not exist "%list_folder%\1_4list.txt" goto manual_INIT
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
if /i "%bs%"=="1" goto s_trimmer_selection
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo BAD CHOICE
goto prevlist0
:delist
del "%list_folder%\1_4list.txt" 2>&1>NUL
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
%pycommand% "%squirrel%" -t xci -tfile "%list_folder%\1_4list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%list_folder%\1_4list.txt" mode=folder ext="xci" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%list_folder%\1_4list.txt" mode=file ext="xci" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\1_4list.txt" "extlist=xci" )
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\1_4list.txt" "extlist=xci" )
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
%pycommand% "%squirrel%" -t xci -tfile "%list_folder%\1_4list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" goto s_trimmer_selection
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg  "%list_folder%\1_4list.txt" mode=folder ext="xci" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg  "%list_folder%\1_4list.txt" mode=file ext="xci" )  2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\1_4list.txt" "extlist=xci" )
if /i "%eval%"=="5" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\1_4list.txt" "extlist=xci" )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del ("%list_folder%\1_4list.txt") 2>&1>NUL

goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (lists/1_4list.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:update_list1
if !pos1! GTR !pos2! ( goto :update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :update_list1
:update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<lists/1_4list.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>lists/1_4list.txt.new
endlocal
move /y "lists/1_4list.txt.new" "lists/1_4list.txt" >nul
endlocal

:showlist
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                 FILES TO PROCESS
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (lists/1_4list.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (lists/1_4list.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

goto checkagain

:s_cl_wrongchoice
echo wrong choice
echo ............

:s_trimmer_selection
echo *******************************************************
echo SUPERTRIMMING\TRIMMING\UNTRIMMING
echo *******************************************************
echo DESCRYPTION:
echo - Supetrimming
echo   Removes System Firmware update, empties update partition,
echo   removes final and middle padding, removes logo partition
echo   removes game update, keeps game certificate if exists
echo   (Perfect for installation)
echo - Supetrimming  keeping game updates
echo   Same as before but keeps game updates
echo - Trimming
echo   Removes final padding (empty data)
echo - UnTrimming
echo   Undoes the trimming of a normal trimming operation
echo.
echo Input "1" Supertrimm
echo Input "2" Supertrimm keeping game updates
echo Input "3" Trimm
echo Input "4" UnTrimm
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "vrepack=none"
if /i "%bs%"=="1" set "vrepack=xci_supertrimmer"
if /i "%bs%"=="2" set "vrepack=xci_supertrimmer_keep_upd"
if /i "%bs%"=="3" set "vrepack=xci_trimmer"
if /i "%bs%"=="4" set "vrepack=xci_untrimmer"
if /i "%vrepack%"=="none" echo WRONG CHOICE
if /i "%vrepack%"=="none" goto s_trimmer_selection
goto s_KeyChange_skip

:s_KeyChange_skip
cls
call "%nscb_logos%" "program_logo"

for /f "tokens=*" %%f in (lists/1_4list.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"

if "%%~nxf"=="%%~nf.xci" call :xci_manual
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/1_4list.txt" "1" "true"
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:xci_manual
rem if "%fatype%" EQU "-fat fat32" goto xci_manual_fat32
::FOR XCI FILES
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"

set "filename=%name%"
set "showname=%orinput%"

if "%vrepack%" EQU "xci_supertrimmer" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" -xci_st "%orinput%")
if "%vrepack%" EQU "xci_supertrimmer_keep_upd" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -t "xci" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt" )
if "%vrepack%" EQU "xci_trimmer" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" -xci_tr "%orinput%")
if "%vrepack%" EQU "xci_untrimmer" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" -xci_untr "%orinput%" )

if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo DONE
call :thumbup
call :delay
goto end_xci_manual

:xci_manual_fat32
CD /d "%prog_dir%"
::FOR XCI FILES
cls
if "%vrepack%" EQU "zip" ( goto end_xci_manual )
set "filename=%name%"
call "%nscb_logos%" "program_logo"
set "showname=%orinput%"
call "%nscb_tools%" "processing_message" "%showname%"
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
if "%vrename%" EQU "true" call :addtags_from_xci
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xc*"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo DONE
call :thumbup
call :delay
goto end_xci_manual

:end_xci_manual
exit /B

:s_exit_choice
call "%nscb_tools%" "delete_if_empty" "1_4list.txt"
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
goto s_exit_choice

:salida
::pause
exit