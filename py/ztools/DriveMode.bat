@ECHO OFF
:TOP_INIT
CD /d "%prog_dir%"
set "bat_name=%~n0"
Title NSC_Builder v0.98 -- Profile: %ofile_name% -- by JulesOnTheRoad

:MAIN
cls
call :program_logo
ECHO .......................................................
echo Input "1" to enter into DOWNLOAD mode
echo Input "2" to enter into FILE-INFO mode
echo.
echo Input "N" to go to NEW MODES
echo Input "L" to go to LEGACY MODES
echo .......................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto DOWNLOADMODE
if /i "%bs%"=="2" goto INFMODE
if /i "%bs%"=="N" exit /B
if /i "%bs%"=="L" goto LegacyMode
goto MAIN

:LegacyMode
call "%prog_dir%ztools\LEGACY.bat"
exit /B

:DOWNLOADMODE
cls
call :program_logo
%pycommand% "%nut%" -lib_call Drive.Download Interface
goto MAIN

:INFMODE
cls
call :program_logo
%pycommand% "%nut%" -lib_call Drive.Info Interface
goto MAIN

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
ECHO                                  VERSION 0.98 (GDRIVE)
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
::pause
exit



