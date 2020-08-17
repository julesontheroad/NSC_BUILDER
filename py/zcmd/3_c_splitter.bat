::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::SPLITTER MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
CD /d "%prog_dir%"
cls
call "%nscb_logos%" "program_logo"
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1
echo -----------------------------------------------
echo SPLITTER MODE ACTIVATED
echo -----------------------------------------------
if exist "%list_folder%\3_0list.txt" goto sp_prevlist
goto sp_manual_INIT
:sp_prevlist
set conta=0
for /f "tokens=*" %%f in ( lists/3_0list.txt ) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in ( lists/3_0list.txt ) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del "%list_folder%\3_0list.txt" )
endlocal
if not exist "%list_folder%\3_0list.txt" goto sp_manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:sp_prevlist0
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
if /i "%bs%"=="3" goto sp_showlist
if /i "%bs%"=="2" goto sp_delist
if /i "%bs%"=="1" goto sp_start_cleaning
if /i "%bs%"=="0" call "%main_program%"
echo.
echo BAD CHOICE
goto sp_prevlist0
:sp_delist
del "%list_folder%\3_0list.txt" >NUL 2>&1
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo SPLITTER MODE ACTIVATED
echo -----------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................
:sp_manual_INIT
endlocal
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "3" to add files to list via local libraries
echo Input "4" to add files to list via folder-walker
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%sq_lc%" -lib_call cmd.cmd_tools userinput -xarg "%list_folder%\3_0list.txt" ext="nsp xci nsz xcz" userfile="%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" call "%main_program%"
if /i "%eval%"=="1" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\3_0list.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\3_0list.txt" mode=file ext="nsp xci nsz xcz" )  2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\3_0list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\3_0list.txt" "extlist=nsp xci nsz xcz" )

echo.
:sp_checkagain
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
%pycommand% "%sq_lc%" -lib_call cmd.cmd_tools userinput -xarg "%list_folder%\3_0list.txt" ext="nsp xci nsz xcz" userfile="%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" call "%main_program%"
if /i "%eval%"=="1" goto sp_start_cleaning
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\3_0list.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\3_0list.txt" mode=file ext="nsp xci nsz xcz" )  2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\3_0list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="5" ( %pycommand% "%sq_lc%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\3_0list.txt" "extlist=nsp xci nsz xcz" )

if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto sp_showlist
if /i "%eval%"=="r" goto sp_r_files
if /i "%eval%"=="z" ( del "%list_folder%\3_0list.txt" )

goto sp_checkagain

:sp_r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
%pycommand% "%sq_lc%" -lib_call listmanager remove_from_botton -xarg  "%list_folder%\3_0list.txt" "%bs%"

:sp_showlist
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%sq_lc%" -lib_call listmanager printcurrent -xarg  "%list_folder%\3_0list.txt" "all" "counter=True"
goto sp_checkagain

:sp_cl_wrongchoice
echo wrong choice
echo ............
:sp_start_cleaning
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Input "1" to repack list as nsp
echo Input "2" to repack list as xci
echo Input "3" to repack list as both
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto sp_checkagain
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto sp_cl_wrongchoice
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%sq_lc%" -lib_call listmanager filter_list "%list_folder%\3_0list.txt","ext=nsp nsx xci","token=False",Print="False" )
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in ( lists/3_0list.txt ) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "end_folder=%%~nf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :split_content
if "%%~nxf"=="%%~nf.NSP" call :split_content
if "%%~nxf"=="%%~nf.nsz" call :split_content
if "%%~nxf"=="%%~nf.NSZ" call :split_content
if "%%~nxf"=="%%~nf.xci" call :split_content
if "%%~nxf"=="%%~nf.XCI" call :split_content
if "%%~nxf"=="%%~nf.xcz" call :split_content
if "%%~nxf"=="%%~nf.XCZ" call :split_content
%pycommand% "%squirrel%" --strip_lines "%list_folder%\3_0list.txt" "1" "true"
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%\!end_folder!\" >NUL 2>&1
move "%w_folder%\*.xc*" "%fold_output%\!end_folder!\" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%\!end_folder!\" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!\" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
endlocal
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
:SPLIT_exit_choice
if exist "%list_folder%\3_0list.txt" del "%list_folder%\3_0list.txt"
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
goto SPLIT_exit_choice

:split_content
set "showname=%orinput%"
set "sp_repack=%vrepack%"
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
call "%nscb_tools%" "processing_message" "%showname%"
call "%nscb_logos%" "thumbup"
call "%nscb_logos%" "squirrell"
if "%vrepack%" EQU "nsp" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" %fatype% %fexport% -t "nsp" -dspl "%orinput%" -tfile "%list_folder%\3_0list.txt")
if "%vrepack%" EQU "xci" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" %fatype% %fexport% -t "xci" -dspl "%orinput%" -tfile "%list_folder%\3_0list.txt")
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" %fatype% %fexport% -t "both" -dspl "%orinput%" -tfile "%list_folder%\3_0list.txt")

call "%nscb_logos%" "thumbup"
call "%nscb_logos%" "delay"
exit /B


