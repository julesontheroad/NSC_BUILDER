:sc1
set "info_dir=%~1INFO"
cls
call :logo
echo ********************************************************
echo FILE - INFORMATION
echo ********************************************************
echo.
echo -- Input "0" to go back to the MAIN PROGRAM --
echo.
set /p bs="OR DRAG A XCI OR NSP FILE AND PRESS ENTER: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto salida
set "targt=%bs%"
for /f "delims=" %%a in ("%bs%") do set "Extension=%%~xa"
for /f "delims=" %%a in ("%bs%") do set "Name=%%~na"
if "%Extension%" EQU ".nsp" ( goto sc2 )
if "%Extension%" EQU ".xci" ( goto sc2 )
echo WRONG TYPE OF FILE
pause
goto sc1
:sc2
cls
call :logo
echo .......................................................
echo Input "1" to get CONTENT of the xci\nsp
echo Input "2" to get NUT-INFO of the xci\nsp
echo Input "3" to get FIRMWARE REQUIREMENTS of the xci\nsp
echo Input "4" to READ the CNMT of the xci\nsp
echo.
echo Input "b" to go back to FILE LOADING
echo Input "0" to go back to the MAIN PROGRAM
echo .......................................................
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto g_content
if /i "%bs%"=="2" goto n_info
if /i "%bs%"=="3" goto f_info
if /i "%bs%"=="4" goto r_cnmt

if /i "%bs%"=="b" goto sc1
if /i "%bs%"=="0" goto salida
echo WRONG CHOICE
echo.
goto sc2

:g_content
cls
call :logo
echo ********************************************************
echo SHOW NSP CONTENT OR XCI SECURE PARTITION CONTENT
echo ********************************************************
%pycommand% "%nut%" --filelist "%targt%"
echo.
ECHO ********************************************************
echo Do you want to print the information to a text file?
ECHO ********************************************************
:g_content_wrong
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto g_content_print
if /i "%bs%"=="2" goto sc2
echo WRONG CHOICE
echo.
goto g_content_wrong
:g_content_print
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%-content.txt"
%pycommand% "%nut%" --filelist "%targt%">"%i_file%"
ECHO DONE
goto sc2

:n_info
cls
call :logo
echo ********************************************************
echo NUT - INFO BY BLAWAR
echo ********************************************************
%pycommand% "%nut%" -i "%targt%"
echo.
ECHO ********************************************************
echo Do you want to print the information to a text file?
ECHO ********************************************************
:n_info_wrong
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto n_info_print
if /i "%bs%"=="2" goto sc2
echo WRONG CHOICE
echo.
goto n_info_wrong
:n_info_print
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%-info.txt"
%pycommand% "%nut%" -i "%targt%">"%i_file%"
more +2 "%i_file%">"%i_file%.new"
move /y "%i_file%.new" "%i_file%" >nul
ECHO DONE
goto sc2

:f_info
cls
call :logo
echo ********************************************************
echo SHOW INFORMATION ABOUT REQUIRED FIRMWARE
echo ********************************************************
%pycommand% "%nut%" --fw_req "%targt%"
echo.
ECHO ********************************************************
echo Do you want to print the information to a text file?
ECHO ********************************************************
:f_info_wrong
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto f_info_print
if /i "%bs%"=="2" goto sc2
echo WRONG CHOICE
echo.
goto f_info_wrong
:f_info_print
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%-fwinfo.txt"
%pycommand% "%nut%" --fw_req "%targt%">"%i_file%"
ECHO DONE
goto sc2

:r_cnmt
cls
call :logo
echo ********************************************************
echo SHOW NSP CONTENT OR XCI SECURE PARTITION CONTENT
echo ********************************************************
%pycommand% "%nut%" --Read_cnmt "%targt%"
echo.
ECHO ********************************************************
echo Do you want to print the information to a text file?
ECHO ********************************************************
:r_cnmt_wrong
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto r_cnmt_print
if /i "%bs%"=="2" goto sc2
echo WRONG CHOICE
echo.
goto r_cnmt_wrong
:r_cnmt_print
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%-meta.txt"
%pycommand% "%nut%" --Read_cnmt "%targt%">"%i_file%"
more +1 "%i_file%">"%i_file%.new"
move /y "%i_file%.new" "%i_file%" >nul
ECHO DONE
goto sc2

:salida
exit /B

:logo
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
ECHO                                     VERSION 0.75                                     	
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Revised hacbuild: https://github.com/julesontheroad/hacbuild
ECHO Blawar's NUT    : https://github.com/blawar/nut 
ECHO SciresM hactool : https://github.com/SciresM/hactool
ECHO -------------------------------------------------------------------------------------
exit /B
