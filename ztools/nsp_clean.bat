@echo off
setlocal enabledelayedexpansion
color 03

CD /d "%~dp0"
if not exist "ztools" goto iztools
::check for keys.txt
if not exist "ztools\keys.txt" echo Missing file "KEYS.txt" or "keys.txt!"
echo.
if not exist "ztools\keys.txt" pause
if not exist "ztools\keys.txt" exit
goto set_options1

:iztools
CD /d ".."
if not exist "ztools\keys.txt" echo Missing file "KEYS.txt" or "keys.txt!"
echo.
if not exist "ztools\keys.txt" pause
if not exist "ztools\keys.txt" exit
goto set_options1

::Set PRESETS
::For now only nut.py route
:set_options1
if exist "zconfig\nsp_cleaner_options.txt" goto set_options2
set NUT_ROUTE=ztools/nut_RTR.py
if exist %NUT_ROUTE% goto startpr
exit

:set_options2

set crlt=0
for /f "tokens=2 delims=|" %%a in (zconfig\nsp_cleaner_options.txt) do (
    set /a crlt=!crlt! + 1
    set opt!crlt!=%%a
)
set NUT_ROUTE=%opt1%
if exist %NUT_ROUTE% goto startpr
set NUT_ROUTE=ztools/nut_RTR.py
if exist %NUT_ROUTE% goto startpr
exit

:startpr
::Set working folder and file
set file=%~n1
FOR %%i IN ("%file%") DO (
set filename=%%~ni
)
::set filename=%filename:_= %
cls

if "%~x1"==".nsp" (goto nsp)
if "%~x1"==".xci" (goto end)
goto end 
ECHO                               __           __                          
ECHO                  ____  __  __/ /_    _____/ /__  ____ _____  ___  _____
ECHO                 / __ \/ / / / __/   / ___/ / _ \/ __ `/ __ \/ _ \/ ___/
ECHO                / / / / /_/ / /_    / /__/ /  __/ /_/ / / / /  __/ /    
ECHO               /_/ /_/\__,_/\__/____\___/_/\___/\__,_/_/ /_/\___/_/     
ECHO                              /_____/              
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                              POWERED WITH NUT BY BLAWAR                           "
ECHO                                      VERSION 0.1               
ECHO -------------------------------------------------------------------------------------                   
ECHO check xci_batch_builder at: https://github.com/julesontheroad/
ECHO and check blawar's NUT at:  https://github.com/blawar/nut 
ECHO -------------------------------------------------------------------------------------
echo.
ECHO ............
ECHO INSTRUCTIONS
ECHO ............
echo.
echo This program works dragging an nsp file over it's bat file
echo.
echo It also works with nsp_clean.bat "filename.nsp" over the command line
echo.
echo It's function is to convert clean nsp files from tickets and titlekey encryption
echo.
echo.This batch makes use of nut.py libraries
echo.
pause
exit

:nsp
@echo off
setlocal enabledelayedexpansion
ECHO                               __           __                          
ECHO                  ____  __  __/ /_    _____/ /__  ____ _____  ___  _____
ECHO                 / __ \/ / / / __/   / ___/ / _ \/ __ `/ __ \/ _ \/ ___/
ECHO                / / / / /_/ / /_    / /__/ /  __/ /_/ / / / /  __/ /    
ECHO               /_/ /_/\__,_/\__/____\___/_/\___/\__,_/_/ /_/\___/_/     
ECHO                              /_____/              
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                              POWERED WITH NUT BY BLAWAR                           "
ECHO                                      VERSION 0.1               
ECHO -------------------------------------------------------------------------------------                   
ECHO check xci_batch_builder at: https://github.com/julesontheroad/
ECHO and check blawar's NUT at:  https://github.com/blawar/nut 
ECHO -------------------------------------------------------------------------------------

if exist "nspDecrypted\" rmdir /s /q "nspDecrypted\"  >NUL 2>&1
if exist "o_clean_nsp\!filename!.nsp" del "o_clean_nsp\!filename!.nsp"  >NUL 2>&1
set myfile=%~dp0\nspDecrypted\%filename%.nsp
MD nspDecrypted

ECHO -------------------------------------------------------------------------------------
echo Copy %filename% to nspDecrypted
ECHO -------------------------------------------------------------------------------------
echo f | xcopy /f /y "%~1" "nspDecrypted\"   >NUL 2>&1
echo DONE

ECHO -------------------------------------------------------------------------------------
echo Cleaning nsp with nut.py
ECHO -------------------------------------------------------------------------------------
set p_folder=%~dp0 
set p_folder=%p_folder:ztools\ =%
"%NUT_ROUTE%" --remove-title-rights "%p_folder%nspDecrypted\%filename%.nsp" >nspDecrypted\assist.txt
FINDSTR /N "Mismatched" nspDecrypted\assist.txt > nspDecrypted\l_check.txt
FINDSTR /N "name needs to contain [titleId]" nspDecrypted\assist.txt >> nspDecrypted\l_check.txt
for /f "tokens=1* delims=:" %%a in (nspDecrypted\l_check.txt) do set l_check=%%a
del nspDecrypted\l_check.txt >NUL 2>&1
if !l_check! GTR 0 goto an_error
more +8 "nspDecrypted\assist.txt" >"nspDecrypted\assist.txt.new"
move /y "nspDecrypted\assist.txt.new" "nspDecrypted\assist.txt" >nul

echo                    ,;:;;,
echo                   ;;;;;
echo           .=',    ;:;;:,
echo          /_', "=. ';:;:;
echo          @=:__,  \,;:;:'
echo            _(\.=  ;:;;'
echo           `"_(  _/="`
echo            `"'		
for /f "tokens=*" %%n in (nspDecrypted\assist.txt) do echo %%n 
del nspDecrypted\assist.txt >NUL 2>&1
echo .......
echo DONE  
ECHO -------------------------------------------------------------------------------------
echo Extracting nsp file with hactool by SciresM
ECHO -------------------------------------------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t pfs0 --pfs0dir=nspDecrypted\rawnsp "nspDecrypted\%filename%.nsp" >NUL 2>&1
echo DONE  
ECHO -------------------------------------------------------------------------------------
echo Removing ticket and cert
ECHO -------------------------------------------------------------------------------------
del "nspDecrypted\%filename%.nsp"
del "nspDecrypted\rawnsp\*.tik"
del "nspDecrypted\rawnsp\*.cert"
if exist nspDecrypted\rawnsp\*.jpg del nspDecrypted\*.jpg
echo DONE  
ECHO -------------------------------------------------------------------------------------
echo Repacking nsp with nspbuild by CVFireDragon
ECHO -------------------------------------------------------------------------------------
set ruta_nspb=ztools\nspBuild.py
dir "nspDecrypted\rawnsp\*" /b  > "nspDecrypted\nsp_fileslist.txt"
set row=
for /f %%x in (nspDecrypted\nsp_fileslist.txt) do set row="nspDecrypted\rawnsp\%%x" !row!
%ruta_nspb% "nspDecrypted\%filename%[nt].nsp" %row% >NUL 2>&1
echo DONE 
goto final

:an_error
echo Couldn't Remove title rights from file %filename%
echo %DATE%. %TIME%>>log.txt
echo Error removing title rights from %filename%>>log.txt
RD /S /Q nspDecrypted\
goto end

:final
RD /S /Q nspDecrypted\rawnsp\
if not exist o_clean_nsp MD o_clean_nsp
move  "nspDecrypted\*.nsp"  "o_clean_nsp"  >NUL 2>&1
RD /S /Q nspDecrypted\

echo Cleaned !filename!.nsp
echo.
echo Your files should be in the o_clean_nsp folder
echo.
echo    /@
echo    \ \
echo  ___\ \
echo (__O)  \
echo (____@)  \
echo (____@)   \
echo (__o)_    \
echo       \    \
echo.
echo HOPE YOU HAVE A FUN TIME




:end
PING -n 3 127.0.0.1 >NUL 2>&1
cls

