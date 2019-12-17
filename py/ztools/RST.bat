@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"

REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM FILE RESTORATION
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:normalmode
cls
call :program_logo
echo -------------------------------------------------
echo FILE RESTORATION ACTIVATED
echo -------------------------------------------------
if exist "rstlist.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (rstlist.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (rstlist.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del rstlist.txt )
endlocal
if not exist "rstlist.txt" goto manual_INIT
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
if /i "%bs%"=="1" goto start_cleaning
if /i "%bs%"=="0" exit /B
echo.
echo BAD CHOICE
goto prevlist0
:delist
del rstlist.txt
cls
call :program_logo
echo -------------------------------------------------
echo FILE RESTORATION ACTIVATED
echo -------------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................

:manual_INIT
endlocal
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%rstlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" exit /B
if /i "%eval%"=="1" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%rstlist.txt" mode=folder ext="nsp xci" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%rstlist.txt" mode=file ext="nsp xci" ) 2>&1>NUL
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
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
echo ......................................................................
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%rstlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" exit /B
if /i "%eval%"=="1" goto start_cleaning
if /i "%eval%"=="2" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%rstlist.txt" mode=folder ext="nsp xci" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%rstlist.txt" mode=file ext="nsp xci" ) 2>&1>NUL
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del rstlist.txt

goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (rstlist.txt) do (
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
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<rstlist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>rstlist.txt.new
endlocal
move /y "rstlist.txt.new" "rstlist.txt" >nul
endlocal

:showlist
cls
call :program_logo
echo -------------------------------------------------
echo FILE RESTORATION ACTIVATED
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                 FILES TO PROCESS 
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (rstlist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (rstlist.txt) do (
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
:start_cleaning
echo *******************************************************
echo CHOOSE HOW TO PROCESS THE FILES
echo *******************************************************
echo If the files where modified with NSCB from legit sources
echo their nca files are restorable, if not you're not in luck
echo.
echo This mode will restore:
echo   - Conversions between xci\nsp (done by NSCB)
echo   - Titlerights removal operations
echo   - Keygeneration and RSV changes
echo.
echo + Restoration of the link account patcher is not supported yet
echo + Multicontent files need to be processed by the multicontent
echo   splitter first in this first implementation.
echo.
echo ------------------------------------------
echo Input "1" to process the files
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" goto restorefiles
if %vrepack%=="none" goto s_cl_wrongchoice

:restorefiles
cls
call :program_logo
CD /d "%prog_dir%"
MD "%fold_output%" >NUL 2>&1
for /f "tokens=*" %%f in (rstlist.txt) do (
MD "%w_folder%" >NUL 2>&1

%pycommand% "%nut%" %buffer% -o "%w_folder%" %buffer% -tfile "%prog_dir%rstlist.txt" --restore ""
%pycommand% "%nut%" --strip_lines "%prog_dir%rstlist.txt"

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1

RD /S /Q "%w_folder%" >NUL 2>&1
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if exist rstlist.txt del rstlist.txt
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

:contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (rstlist.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo STILL !conta! FILES TO PROCESS
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B


::///////////////////////////////////////////////////
::SUBROUTINES
::///////////////////////////////////////////////////

:squirrell
echo                    ,;:;;,
echo                   ;;;;;
echo           .=',    ;:;;:,
echo          /_', "=. ';:;:;
echo          @=:__,  \,;:;:'
echo            _(\.=  ;:;;'
echo           `"_(  _/="`
echo            `"'		
exit /B

:program_logo

ECHO                                        __          _ __    __         
ECHO                  ____  _____ ____     / /_  __  __(_) /___/ /__  _____
ECHO                 / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/
ECHO                / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /    
ECHO               /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/     
ECHO                              /_____/                                  
ECHO -------------------------------------------------------------------------------------
ECHO                         NINTENDO SWITCH CLEANER AND BUILDER
ECHO                      (THE XCI MULTI CONTENT BUILDER AND MORE)
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                                POWERED BY SQUIRREL                                "
ECHO "                    BASED ON THE WORK OF BLAWAR AND LUCA FRAGA                     "
ECHO                                    VERSION 0.97
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Blawar's github:  https://github.com/blawar
ECHO Blawar's tinfoil: https://github.com/digableinc/tinfoil
ECHO Luca Fraga's github: https://github.com/LucaFraga
ECHO -------------------------------------------------------------------------------------
exit /B

:delay
PING -n 2 127.0.0.1 >NUL 2>&1
exit /B

:thumbup
echo.
echo    /@
echo    \ \
echo  ___\ \
echo (__O)  \
echo (____@) \
echo (____@)  \
echo (__o)_    \
echo       \    \
echo.
echo HOPE YOU HAVE A FUN TIME
exit /B


:salida
exit /B


