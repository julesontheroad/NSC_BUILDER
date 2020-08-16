::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:: DB-MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:DBMODE
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo DATABASE GENERATION MODE ACTIVATED
echo -----------------------------------------------
if exist "DBL.txt" goto DBprevlist
goto DBmanual_INIT
:DBprevlist
set conta=0
for /f "tokens=*" %%f in (DBL.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del DBL.txt )
endlocal
if not exist "DBL.txt" goto DBmanual_INIT
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
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo BAD CHOICE
goto DBprevlist0
:DBdelist
del DBL.txt
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
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
set /p bs="PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
set "targt=%bs%"
dir "%bs%\" >nul 2>nul
if not errorlevel 1 goto DBcheckfolder
if exist "%bs%\" goto DBcheckfolder
goto DBcheckfile
:DBcheckfolder
%pycommand% "%squirrel%" -t nsp xci nsx nsz xcz -tfile "%prog_dir%DBL.txt" -ff "%targt%"
goto DBcheckagain
:DBcheckfile
%pycommand% "%squirrel%" -t nsp xci nsx nsz xcz -tfile "%prog_dir%DBL.txt" -ff "%targt%"
goto DBcheckagain
echo.
:DBcheckagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Input "1" to start processing
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
echo ......................................................................
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
set /p bs="Drag file/folder or set option: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto DBstart_cleaning
if /i "%bs%"=="e" goto DBsalida
if /i "%bs%"=="i" goto DBshowlist
if /i "%bs%"=="r" goto DBr_files
if /i "%bs%"=="z" del DBL.txt
set "targt=%bs%"
dir "%bs%\" >nul 2>nul
if not errorlevel 1 goto DBcheckfolder
if exist "%bs%\" goto DBcheckfolder
goto DBcheckfile
goto DBsalida

:DBr_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:DBupdate_list1
if !pos1! GTR !pos2! ( goto :DBupdate_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :DBupdate_list1
:DBupdate_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<DBL.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>DBL.txt.new
endlocal
move /y "DBL.txt.new" "DBL.txt" >nul
endlocal

:DBshowlist
cls
call "%nscb_logos%" "program_logo"
echo -------------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                 FILES TO PROCESS
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (DBL.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

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
echo Input "Z" TO MAKE ZIP FILES
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="0" goto DBcheckagain
if /i "%bs%"=="Z" set "vrepack=zip"
if /i "%bs%"=="Z" goto DBs_start
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
for /f "tokens=*" %%f in (DBL.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
set "ziptarget=%%f"
if "%vrepack%" EQU "zip" ( set "zip_restore=true" )
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
%pycommand% "%squirrel%" --strip_lines "%prog_dir%DBL.txt" "1" "true"
rem call :DBcontador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
:DBs_exit_choice
if exist DBL.txt del DBL.txt
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

:DBnsp_manual
set "filename=%name%"
set "showname=%orinput%"
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
call :squirrell

if "%vrepack%" EQU "zip" ( goto nsp_just_zip )

:DBnsp_just_zip
if "%zip_restore%" EQU "true" ( call :makezip )
rem call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp
if "%zip_restore%" EQU "true" ( goto :nsp_just_zip2 )

:DBnsp_just_zip2

if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
RD /S /Q "%w_folder%" >NUL 2>&1

echo DONE
call :thumbup
call :delay

:DBend_nsp_manual
exit /B

:DBs_GENDB
set "db_file=%prog_dir%INFO\%dbformat%_DB.txt"
set "dbdir=%prog_dir%INFO\"
if exist "%dbdir%temp" ( RD /S /Q "%dbdir%temp" ) >NUL 2>&1
rem echo %dbdir%temp

for /f "tokens=*" %%f in (DBL.txt) do (
set "orinput=%%f"
if exist "%dbdir%temp" ( RD /S /Q "%dbdir%temp" ) >NUL 2>&1
call :DBGeneration
if "%workers%" EQU "-threads 1" ( %pycommand% "%squirrel%" --strip_lines "%prog_dir%DBL.txt" "1" "true")
if "%workers%" NEQ "-threads 1" ( call :DBcheck )
rem if "%workers%" NEQ "-threads 1" ( call :DBcontador_NF )
)
:DBs_fin
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
if exist "%dbdir%temp" ( RD /S /Q "%dbdir%temp" ) >NUL 2>&1
goto DBs_exit_choice

:DBGeneration
if not exist "%dbdir%" MD "%dbdir%">NUL 2>&1
%pycommand% "%squirrel%" --dbformat "%dbformat%" -dbfile "%db_file%" -tfile "%prog_dir%DBL.txt" -nscdb "%orinput%" %workers%
exit /B

:DBcheck
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)
if !conta! LEQ 0 ( del DBL.txt )
endlocal
if not exist "DBL.txt" goto DBs_fin
exit /B

:DBcontador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo STILL !conta! FILES TO PROCESS
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B