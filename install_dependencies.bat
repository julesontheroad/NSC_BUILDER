@ECHO OFF
set "pycommand=py -3"
set "op_file=%~dp0zconfig/NSCB_options.cmd"
setlocal
if exist "%op_file%" call "%op_file%" 	  
endlocal & ( 
set "pycommand=%pycommand%"
)

call :program_logo
ECHO.
ECHO Installing dependencies 
ECHO.
%pycommand% -m pip install urllib3 unidecode tqdm bs4 tqdm requests image
ECHO.
ECHO. Check if dependencies were installed correctly before exiting the .bat file.
PAUSE
exit

:program_logo

ECHO                                        __          _ __    __         
ECHO                  ____  _____ ____     / /_  __  __(_) /___/ /__  _____
ECHO                 / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/
ECHO                / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /    
ECHO               /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/     
ECHO                              /_____/                                  
ECHO -------------------------------------------------------------------------------------
ECHO                         NINTENDO SWITCH CLEANER AND BUILDER
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                             POWERED WITH NUT BY BLAWAR                            "
ECHO "                             AND LUCA FRAGA'S HACBUILD                             "
ECHO                                     VERSION 0.65                                     	
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Revised hacbuild: https://github.com/julesontheroad/hacbuild
ECHO Blawar's NUT    : https://github.com/blawar/nut 
ECHO SciresM hactool : https://github.com/SciresM/hactool
ECHO -------------------------------------------------------------------------------------
exit /B