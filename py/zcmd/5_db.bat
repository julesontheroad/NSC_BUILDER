::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:: DB-MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
CD /d "%prog_dir%"
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo DATABASE GENERATION MODE ACTIVATED
echo -----------------------------------------------
if exist "%list_folder%\5_0list.txt" goto DBprevlist
goto DBmanual_INIT
:DBprevlist
set conta=0
for /f "tokens=*" %%f in ( lists/5_0list.txt ) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in ( lists/5_0list.txt ) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del "%list_folder%\5_0list.txt" )
endlocal
if not exist "%list_folder%\5_0list.txt" goto DBmanual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:DBprevlist0
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
if /i "%bs%"=="3" goto DBshowlist
if /i "%bs%"=="2" goto DBdelist
if /i "%bs%"=="1" goto DBstart_cleaning
if /i "%bs%"=="0" call "%main_program%"
echo.
echo BAD CHOICE
goto DBprevlist0
:DBdelist
del "%list_folder%\5_0list.txt"
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -----------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................
:DBmanual_INIT
endlocal
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "3" to add files to list via local libraries
echo Input "4" to add files to list via folder-walker
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%sq_lc%" -lib_call cmd.cmd_tools userinput -xarg "%list_folder%\5_0list.txt" ext="nsp xci nsz xcz nsx" userfile="%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" call "%main_program%"
if /i "%eval%"=="1" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\5_0list.txt" mode=folder ext="nsp xci nsz xcz nsx" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\5_0list.txt" mode=file ext="nsp xci nsz xcz nsx" )  2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\5_0list.txt" "extlist=nsp xci nsz xcz nsx" )
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\5_0list.txt" "extlist=nsp xci nsz xcz nsx" )

echo.
:DBcheckagain
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
%pycommand% "%sq_lc%" -lib_call cmd.cmd_tools userinput -xarg "%list_folder%\5_0list.txt" ext="nsp xci nsz xcz nsx" userfile="%uinput%"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" call "%main_program%"
if /i "%eval%"=="1" goto DBstart_cleaning
if /i "%eval%"=="2" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\5_0list.txt" mode=folder ext="nsp xci nsz xcz nsx" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%sq_lc%" -lib_call listmanager selector2list -xarg "%list_folder%\5_0list.txt" mode=file ext="nsp xci nsz xcz nsx" )  2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%sq_lc%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\5_0list.txt" "extlist=nsp xci nsz xcz nsx" )
if /i "%eval%"=="5" ( %pycommand% "%sq_lc%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\5_0list.txt" "extlist=nsp xci nsz xcz nsx" )

if /i "%eval%"=="e" goto DBsalida
if /i "%eval%"=="i" goto DBshowlist
if /i "%eval%"=="r" goto DBr_files
if /i "%eval%"=="z" ( del "%list_folder%\5_0list.txt" )

goto DBcheckagain

:DBr_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
%pycommand% "%sq_lc%" -lib_call listmanager remove_from_botton -xarg  "%list_folder%\5_0list.txt" "%bs%"

:DBshowlist
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%sq_lc%" -lib_call listmanager printcurrent -xarg  "%list_folder%\5_0list.txt" "all" "counter=True"
goto DBcheckagain

:DBs_cl_wrongchoice
echo wrong choice
echo ............
:DBstart_cleaning
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Input "1" TO GENERATE nutdb DATABASE
echo Input "2" TO GENERATE EXTENDED DATABASE
echo Input "3" TO GENERATE KEYLESS DATABASE (EXTENDED)
echo Input "4" TO GENERATE SIMPLE DATABASE
echo Input "5" TO GENERATE ALL 4 ABOVE DATABASES
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="0" goto DBcheckagain
if /i "%bs%"=="1" set "dbformat=nutdb"
if /i "%bs%"=="1" goto DBs_GENDB
if /i "%bs%"=="2" set "dbformat=extended"
if /i "%bs%"=="2" goto DBs_GENDB
if /i "%bs%"=="3" set "dbformat=keyless"
if /i "%bs%"=="3" goto DBs_GENDB
if /i "%bs%"=="4" set "dbformat=simple"
if /i "%bs%"=="4" goto DBs_GENDB
if /i "%bs%"=="5" set "dbformat=all"
if /i "%bs%"=="5" goto DBs_GENDB
if %vrepack%=="none" goto DBs_cl_wrongchoice

:DBs_start
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in ( lists/5_0list.txt ) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
set "ziptarget=%%f"
if "%%~nxf"=="%%~nf.nsp" call :DBnsp_manual
if "%%~nxf"=="%%~nf.nsx" call :DBnsp_manual
if "%%~nxf"=="%%~nf.nsz" call :DBnsp_manual
if "%%~nxf"=="%%~nf.NSP" call :DBnsp_manual
if "%%~nxf"=="%%~nf.NSX" call :DBnsp_manual
if "%%~nxf"=="%%~nf.NSZ" call :DBnsp_manual
if "%%~nxf"=="%%~nf.xci" call :DBnsp_manual
if "%%~nxf"=="%%~nf.XCI" call :DBnsp_manual
if "%%~nxf"=="%%~nf.xcz" call :DBnsp_manual
if "%%~nxf"=="%%~nf.XCZ" call :DBnsp_manual
%pycommand% "%squirrel%" --strip_lines "%list_folder%\5_0list.txt" "1" "true"
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
:DBs_exit_choice
if exist "%list_folder%\5_0list.txt" del "%list_folder%\5_0list.txt"
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

:DBnsp_manual
set "filename=%name%"
set "showname=%orinput%"
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
call "%nscb_logos%" "squirrell"

:DBend_nsp_manual
exit /B

:DBs_GENDB
set "db_file=%prog_dir%INFO\%dbformat%_DB.txt"
set "dbdir=%prog_dir%INFO\"
if exist "%dbdir%temp" ( RD /S /Q "%dbdir%temp" ) >NUL 2>&1

for /f "tokens=*" %%f in ( lists/5_0list.txt ) do (
set "orinput=%%f"
if exist "%dbdir%temp" ( RD /S /Q "%dbdir%temp" ) >NUL 2>&1
call :DBGeneration
if "%workers%" EQU "-threads 1" ( %pycommand% "%squirrel%" --strip_lines "%list_folder%\5_0list.txt" "1" "true")
if "%workers%" NEQ "-threads 1" ( call :DBcheck )
)
:DBs_fin
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
if exist "%dbdir%temp" ( RD /S /Q "%dbdir%temp" ) >NUL 2>&1
goto DBs_exit_choice

:DBGeneration
if not exist "%dbdir%" MD "%dbdir%">NUL 2>&1
%pycommand% "%squirrel%" --dbformat "%dbformat%" -dbfile "%db_file%" -tfile "%list_folder%\5_0list.txt" -nscdb "%orinput%" %workers%
exit /B

:DBcheck
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in ( lists/5_0list.txt ) do (
set /a conta=!conta! + 1
)
if !conta! LEQ 0 ( del "%list_folder%\5_0list.txt" )
endlocal
if not exist "%list_folder%\5_0list.txt" goto DBs_fin
exit /B
