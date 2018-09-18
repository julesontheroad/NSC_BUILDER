@ECHO OFF
color 03
setlocal enabledelayedexpansion

::Set checks
set /a Enclean=0

::Checks if cleaner exist
if exist "%~dp0nsp_clean.bat" set /a Enclean=1
if exist "%~dp0ztools\nsp_clean.bat" set /a Enclean=1

::If no program exist go to exit
if %Enclean% EQU 0 ( goto noprograms )

::Set route for programs depending on it's location
set rutaNCLEAN=%~dp0nsp_clean.bat

if not exist "%~dp0nsp_clean.bat" ( set rutaNCLEAN=%~dp0ztools\nsp_clean.bat ) 

::Check if user is dragging a folder or a file

if exist "%~dp1%~n1\*.nsp" goto folder
goto file

:folder
ECHO                 __       __          __       __             __                          
ECHO    ____  __  __/ /_     / /_  ____ _/ /______/ /_      _____/ /__  ____ _____  ___  _____
ECHO   / __ \/ / / / __/    / __ \/ __ `/ __/ ___/ __ \    / ___/ / _ \/ __ `/ __ \/ _ \/ ___/
ECHO  / / / / /_/ / /_     / /_/ / /_/ / /_/ /__/ / / /   / /__/ /  __/ /_/ / / / /  __/ /    
ECHO /_/ /_/\__,_/\__/____/_.___/\__,_/\__/\___/_/ /_/____\___/_/\___/\__,_/_/ /_/\___/_/     
ECHO                /_____/                         /_____/       
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                              POWERED WITH NUT BY BLAWAR                           "
ECHO                                      VERSION 0.15               
ECHO -------------------------------------------------------------------------------------                   
ECHO check xci_batch_builder at: https://github.com/julesontheroad/
ECHO and check blawar's NUT at:  https://github.com/blawar/nut 
ECHO -------------------------------------------------------------------------------------
PING -n 2 127.0.0.1 >NUL 2>&1

for /r "%~1" %%f in (*.nsp) do (
if %Enclean% EQU 1 ( call "%rutaNCLEAN%" "%%f" )
)
ECHO ---------------------------------------------------
ECHO ************ ALL FILES WERE CLEANED! ************** 
ECHO ---------------------------------------------------
PING -n 2 127.0.0.1 >NUL 2>&1
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
exit

:file
if "%~x1"==".nsp" ( goto nsp )
if "%~x1"==".*" ( goto other )
goto manual

:nsp

call "%rutaNCLEAN%" "%~1"
exit

:noprograms
ECHO ....................................................
echo nsp_clean.bat wasn't found
ECHO ....................................................
echo you can download it from: 
ECHO -----------------------------------
echo https://github.com/julesontheroad/
ECHO -----------------------------------
echo Then install them either in ztools or in BatchBuilder
echo root directory.
pause
exit


:manual
setlocal enabledelayedexpansion
::Set checks
set /a Enclean=0

::Checks if cleaner exist
if exist "%~dp0nsp_clean.bat" set /a Enclean=1
if exist "%~dp0ztools\nsp_clean.bat" set /a Enclean=1

::If no program exist go to exit
if %Enclean% EQU 0 ( goto noprograms )

::Set route for programs depending on it's location
set rutaNCLEAN=%~dp0nsp_clean.bat

if not exist "%~dp0nsp_clean.bat" ( set rutaNCLEAN=%~dp0ztools\nsp_clean.bat ) 


ECHO                 __       __          __       __             __                          
ECHO    ____  __  __/ /_     / /_  ____ _/ /______/ /_      _____/ /__  ____ _____  ___  _____
ECHO   / __ \/ / / / __/    / __ \/ __ `/ __/ ___/ __ \    / ___/ / _ \/ __ `/ __ \/ _ \/ ___/
ECHO  / / / / /_/ / /_     / /_/ / /_/ / /_/ /__/ / / /   / /__/ /  __/ /_/ / / / /  __/ /    
ECHO /_/ /_/\__,_/\__/____/_.___/\__,_/\__/\___/_/ /_/____\___/_/\___/\__,_/_/ /_/\___/_/     
ECHO                /_____/                         /_____/       
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                                POWERED NY NUT BY BLAWAR                           "
ECHO                                        VERSION 0.1               
ECHO -------------------------------------------------------------------------------------                   
ECHO check xci_batch_builder at: https://github.com/julesontheroad/
ECHO and check blawar's NUT at:  https://github.com/blawar/nut 
ECHO -------------------------------------------------------------------------------------
echo.
echo ********************************
echo YOU'VE ENTERED INTO MANUAL MODE
echo ********************************
if exist "list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del list.txt )
if not exist "list.txt" goto manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WHAS FOUND. WHAT DO YOU WANT TO DO?
:prevlist0
ECHO .......................................................
echo Press "0" to auto-start cleaning from the previous list
echo Press "1" to erase list and make a new one.
echo Press "2" to continue building the previous list
echo .......................................................
echo NOTE: By pressing 2 you'll see the previous list 
echo before starting the cleaning process and you will 
echo be able to add and delete items to the list
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="2" goto showlist
if /i "%bs%"=="1" goto delist
if /i "%bs%"=="0" goto start_cleaning
echo.
echo BAD CHOICE
goto prevlist0
:delist
del list.txt
echo YOU'VE DECIDED TO START A NEW LIST
echo ...................................................................
:manual_INIT
set /p bs="PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if exist "%bs%\" goto checkfolder
goto checkfile
:checkfolder
DIR /B /S "%bs%\*.nsp" >hlist.txt
FINDSTR ".nsp" hlist.txt >>list.txt
del hlist.txt
goto checkagain
:checkfile
echo %bs% >>hlist.txt
FINDSTR ".nsp" hlist.txt >>list.txt
del hlist.txt
goto checkagain
echo.
:checkagain
echo What do you want to do?
echo.
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Press "1" to start cleaning
echo Press "e" to exit
echo Press "i" to see list of files to clean
echo Press "r" to remove some files (counting from bottom)
echo ......................................................................
set /p bs="Drag file/folder or set option: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto start_cleaning
if /i "%bs%"=="e" goto salida
if /i "%bs%"=="i" goto showlist
if /i "%bs%"=="r" goto r_files
if exist "%bs%\" goto checkfolder
goto checkfile
goto salida
pause

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
set conta=
for /f "tokens=*" %%f in (list.txt) do (
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
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<list.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>list.txt.new
move /y "list.txt.new" "list.txt" >nul

:showlist
ECHO -------------------------------------------------
ECHO                 FILES TO CLEAN 
ECHO -------------------------------------------------
set conta=
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO CLEAN
echo .................................................
goto checkagain

:s_cl_wrongchoice
echo wrong choice
echo ............
:start_cleaning
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER CLEANING TITLERIGHTS ENCRYPTION
echo *******************************************************
echo Press "1" to repack list as nsp
echo Press "2" to repack list as xci
echo Press "3" to repack list as both
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="1" set vrepack=nsp
if /i "%bs%"=="2" set vrepack=xci
if /i "%bs%"=="3" set vrepack=both
if %vrepack%=="none" goto s_cl_wrongchoice

set conta=
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
set /a conta=!conta! + 1
)
for /f "tokens=*" %%f in (list.txt) do (
call "%rutaNCLEAN%" "%%f" "%vrepack%"
more +1 "list.txt" >"list.txt.new"
move /y "list.txt.new" "list.txt" >nul
set /a conta=!conta! - 1
echo .................................................
echo STILL !conta! FILES TO CLEAN
echo .................................................
)
ECHO -------------------------------------------------
ECHO *********** ALL FILES WERE CLEANED! *************
ECHO -------------------------------------------------
PING -n 2 127.0.0.1 >NUL 2>&1
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
:salida

exit
