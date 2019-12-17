@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"

REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM COMPRESSION
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:normalmode
cls
call :program_logo
echo -------------------------------------------------
echo COMPRESS\DECOMPRESS MODE ACTIVATED
echo -------------------------------------------------
if exist "zzlist.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (zzlist.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (zzlist.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del zzlist.txt )
endlocal
if not exist "zzlist.txt" goto manual_INIT
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
if /i "%bs%"=="1" goto start
if /i "%bs%"=="0" exit /B
echo.
echo BAD CHOICE
goto prevlist0
:delist
del zzlist.txt
cls
call :program_logo
echo -------------------------------------------------
echo COMPRESS\DECOMPRESS MODE ACTIVATED
echo -------------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................

:manual_INIT
endlocal
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%nut%" -t nsp xci nsz xcz -tfile "%prog_dir%zzlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" exit /B
if /i "%eval%"=="1" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%zzlist.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%zzlist.txt" mode=file ext="nsp xci nsz xcz" )  2>&1>NUL

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
%pycommand% "%nut%" -t nsp xci nsz xcz -tfile "%prog_dir%zzlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" exit /B
if /i "%eval%"=="1" goto start
if /i "%eval%"=="2" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%zzlist.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%nut%" -lib_call listmanager selector2list -xarg "%prog_dir%zzlist.txt" mode=file ext="nsp xci nsz xcz" )  2>&1>NUL
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del zzlist.txt

goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (zzlist.txt) do (
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
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<zzlist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>zzlist.txt.new
endlocal
move /y "zzlist.txt.new" "zzlist.txt" >nul
endlocal

:showlist
cls
call :program_logo
echo -------------------------------------------------
echo COMPRESS\DECOMPRESS MODE ACTIVATED
echo -------------------------------------------------
ECHO FILES TO PROCESS: 
for /f "tokens=*" %%f in (zzlist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (zzlist.txt) do (
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
:start
echo *******************************************************
echo CHOOSE HOW TO PROCESS THE FILES
echo *******************************************************
echo Input "1" to compress nsp\xci to nsz\xcz
echo Input "2" for  pararell compression
echo Input "3" for decompress nsz\xcz
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" goto compression_presets_menu
if /i "%bs%"=="2" goto pararell_compress
if /i "%bs%"=="3" goto decompress
if %choice%=="none" goto s_cl_wrongchoice


:compression_presets_wrongchoice
echo wrong choice
echo ............
:compression_presets_menu
echo *******************************************************
echo COMPRESSION PRESETS
echo *******************************************************
echo Compression presets for ease of use
echo.
echo 0. MANUAL SETUP
echo 1. FAST (THREADED)           - LEVEL 1  _ 4   threads
echo 2. FAST (UNTHREADED)         - LEVEL 1  _ no  threads
echo 3. INTERMEDIATE (THREADED)   - LEVEL 10 _ 4   threads
echo 4. INTERMEDIATE (UNTHREADED) - LEVEL 10 _ no  threads
echo 5. AVERAGE (THREADED)        - LEVEL 17 _ 2   threads
echo 6. AVERAGE (UNTHREADED)      - LEVEL 17 _ no  threads
echo 7. HARD    (UNTHREADED)      - LEVEL 22 _ no  threads
echo 8. HARD    (THREADED)        - LEVEL 22 _ 1   threads
echo 9. USER VALUE (SETUP IN CONFIG)
echo. 
ECHO ******************************************
echo Input "d" for default (level 17_no threads)
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Input level number: "
set bs=%bs:"=%
set level=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="d" set "level=17"
if /i "%bs%"=="d" set "workers=0"

if /i "%bs%"=="0" goto levels
if /i "%bs%"=="1" set "level=1"
if /i "%bs%"=="1" set "workers=4"
if /i "%bs%"=="2" set "level=1"
if /i "%bs%"=="2" set "workers=0"
if /i "%bs%"=="3" set "level=10"
if /i "%bs%"=="3" set "workers=4"
if /i "%bs%"=="4" set "level=10"
if /i "%bs%"=="4" set "workers=0"
if /i "%bs%"=="5" set "level=17"
if /i "%bs%"=="5" set "workers=2"
if /i "%bs%"=="6" set "level=17"
if /i "%bs%"=="6" set "workers=0"
if /i "%bs%"=="7" set "level=22"
if /i "%bs%"=="7" set "workers=0"
if /i "%bs%"=="8" set "level=22"
if /i "%bs%"=="8" set "workers=1"
if /i "%bs%"=="9" set "level=%compression_lv%"
if /i "%bs%"=="9" set "workers=%compression_threads%"

if "%level%"=="none" goto compression_presets_wrongchoice
goto compress


:levels_wrongchoice
echo wrong choice
echo ............
:levels
echo *******************************************************
echo INPUT COMPRESSION LEVEL
echo *******************************************************
echo Input a compression level between 1 and 22
echo Notes:
echo  + Level 1 - Fast and smaller compression ratio
echo  + Level 22 - Slow but better compression ratio
echo  Levels 10-17 are recommended in the spec
echo.
ECHO ******************************************
echo Input "d" for default (level 17)
echo Or Input "b" to return to the previous option
echo Or Input "x" to return to the list options
ECHO ******************************************
echo.
set /p bs="Input level number [1-22]: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="x" goto checkagain
if /i "%bs%"=="b" goto compression_presets_menu
if /i "%bs%"=="d" set "bs=17"
set "level=%bs%"
if %choice%=="none" goto levels_wrongchoice
goto threads
:threads_wrongchoice
echo wrong choice
echo ............
:threads
echo *******************************************************
echo INPUT NUMBER OF THREADS TO USE
echo *******************************************************
echo Input a number of threads to use between 0 and 4
echo Notes:
echo  + By using threads you may gain a little speed bump 
echo    but you'll loose compression ratio
echo  + Level 22 and 4 threads may run you out of memory
echo  + For maximum threads level 17 compression is advised
echo    but you'll loose compression ratio
echo  + -1 will set it to your number of logical threads
echo.
ECHO *********************************************
echo Input "d" for default (0 threads)
echo Or Input "b" to return to the previous option
echo Or Input "x" to return to the list options
ECHO *********************************************
echo.
set /p bs="Input number of threads [-1;0-4]: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="x" goto checkagain
if /i "%bs%"=="b" goto levels
if /i "%bs%"=="d" set "bs=0"
set "workers=%bs%"
if %choice%=="none" goto threads_wrongchoice

:compress
cls
call :program_logo
echo *******************************
echo COMPRESS A NSP\XCI
echo *******************************
CD /d "%prog_dir%"
%pycommand% "%nut%" -lib_call listmanager filter_list "%prog_dir%zzlist.txt","ext=nsp xci","token=False",Print="False"
for /f "tokens=*" %%f in (zzlist.txt) do (

%pycommand% "%nut%" %buffer% -o "%fold_output%" -tfile "%prog_dir%zzlist.txt" --compress "%level%" --threads "%workers%" --nodelta "%skdelta%" --fexport "%xci_export%"
REM %pycommand% "%nut%" %buffer% -o "%fold_output%" -tfile "%prog_dir%zzlist.txt" --compress "%level%" --threads "%workers%" --nodelta "%skdelta%" --pararell "true" 

%pycommand% "%nut%" --strip_lines "%prog_dir%zzlist.txt"
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:pararell_compress_wrongchoice
echo wrong choice
echo ............
:pararell_compress
echo *******************************************************
echo INPUT NUMBER OF INSTANCES TO USE
echo *******************************************************
echo Input a number of instances to use bigger than 0
echo Wrong values are converted to 2. 0 is converted to 1
echo Notes:
echo  + You'll create a number of compressed file equal to
echo    the number of instances
echo  + If you have enough disk space instances are more 
echo    efective than threads and have a lower compute power 
echo    fingerprint 
echo  + If you have enough disk space and compute power 
echo    don't be afraid to try using 10-20 instances
echo  + tqdm is a little wonky when printing pararell bars
echo    with threads some so the screen will refresh 
echo    each 3s in pararell mode to clear bad prints.
echo.
ECHO *********************************************
echo Input "d" for default (4 instances)
echo Or Input "b" to return to the previous option
echo Or Input "x" to return to the list options
ECHO *********************************************
echo.
set /p bs="Input number of instances [>1]: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="x" goto checkagain
if /i "%bs%"=="b" goto start
if /i "%bs%"=="d" set "bs=4"
set "workers=%bs%"
if %choice%=="none" goto pararell_compress_wrongchoice

:pararell_levels_wrongchoice
echo wrong choice
echo ............
:pararell_levels
echo *******************************************************
echo INPUT COMPRESSION LEVEL
echo *******************************************************
echo Input a compression level between 1 and 22
echo Notes:
echo  + Level 1 - Fast and smaller compression ratio
echo  + Level 22 - Slow but better compression ratio
echo  Levels 10-17 are recommended in the spec
echo.
ECHO ******************************************
echo Input "d" for default (level 17)
echo Or Input "b" to return to the previous option
echo Or Input "x" to return to the list options
ECHO ******************************************
echo.
set /p bs="Input level number [1-22]: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="x" goto checkagain
if /i "%bs%"=="b" goto pararell_compress
if /i "%bs%"=="d" set "bs=17"
set "level=%bs%"
if %choice%=="none" goto pararell_levels_wrongchoice
goto pcompress
:pcompress
cls
call :program_logo
echo *******************************
echo NSP\XCI PARARELL COMPRESSION 
echo *******************************
CD /d "%prog_dir%"
echo Filter extensions from list
%pycommand% "%nut%" -lib_call listmanager filter_list "%prog_dir%zzlist.txt","ext=nsp xci","token=False",Print="False"
echo Arrange list by filesizes
%pycommand% "%nut%" -lib_call listmanager size_sorted_from_tfile -xarg "%prog_dir%zzlist.txt"
echo Start compression by batches of "%workers%"
%pycommand% "%nut%" %buffer% -o "%fold_output%" -tfile "%prog_dir%zzlist.txt" --compress "%level%" --threads "%workers%" --nodelta "%skdelta%" --fexport "%xci_export%" --pararell "true"

ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:decompress
cls
call :program_logo
echo **************************
echo DECOMPRESS A NSZ\XCZ
echo **************************
CD /d "%prog_dir%"
%pycommand% "%nut%" -lib_call listmanager filter_list "%prog_dir%zzlist.txt","ext=nsz xcz","token=False",Print="False"
for /f "tokens=*" %%f in (zzlist.txt) do (

%pycommand% "%nut%" -o "%fold_output%" -tfile "%prog_dir%zzlist.txt" --decompress "auto"

%pycommand% "%nut%" --strip_lines "%prog_dir%zzlist.txt"
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if exist zzlist.txt del zzlist.txt
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
for /f "tokens=*" %%f in (zzlist.txt) do (
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


