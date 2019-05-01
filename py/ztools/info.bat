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
echo Input "1" to get FILE LIST of the xci\nsp
echo Input "2" to get CONTENT LIST of the xci\nsp
echo Input "3" to get NUT-INFO of the xci\nsp
echo Input "4" to get GAME-INFO and FW requirements
echo Input "5" to READ the CNMT of the xci\nsp
echo.
echo Input "b" to go back to FILE LOADING
echo Input "0" to go back to the MAIN PROGRAM
echo.
echo --- Or DRAG a New File to change the current target ---
echo .......................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
for /f "delims=" %%a in ("%bs%") do set "Extension=%%~xa"
if "%Extension%" EQU ".*" ( goto wch )
if "%Extension%" EQU ".nsp" ( goto snfi )
if "%Extension%" EQU ".xci" ( goto snfi )

if /i "%bs%"=="1" goto g_file_content
if /i "%bs%"=="2" goto g_content_list
if /i "%bs%"=="3" goto n_info
if /i "%bs%"=="4" goto f_info
if /i "%bs%"=="5" goto r_cnmt

if /i "%bs%"=="b" goto sc1
if /i "%bs%"=="0" goto salida
goto wch

:snfi
for /f "delims=" %%a in ("%bs%") do set "Name=%%~na"
set "targt=%bs%"
goto sc2
:wch
echo WRONG CHOICE
pause
goto sc2

:g_file_content
cls
call :logo
echo ********************************************************
echo SHOW NSP FILE CONTENT OR XCI SECURE PARTITION CONTENT
echo ********************************************************
%pycommand% "%nut%" --ADVfilelist "%targt%"
echo.
ECHO ********************************************************
echo Do you want to print the information to a text file?
ECHO ********************************************************
:g_file_contentwrong
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto g_file_content_print
if /i "%bs%"=="2" goto sc2
echo WRONG CHOICE
echo.
goto g_file_contentwrong
:g_file_content_print
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%-Fcontent.txt"
%pycommand% "%nut%" --ADVfilelist "%targt%">"%i_file%"
ECHO DONE
goto sc2

:g_content_list
cls
call :logo
echo ********************************************************
echo SHOW NSP OR XCI CONTENT ARRANGED BY ID
echo ********************************************************
%pycommand% "%nut%" --ADVcontentlist "%targt%"
echo.
ECHO ********************************************************
echo Do you want to print the information to a text file?
ECHO ********************************************************
:g_content_list_wrong
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto g_content_list_print
if /i "%bs%"=="2" goto sc2
echo WRONG CHOICE
echo.
goto g_content_list_wrong
:g_content_list_print
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%_ID_content.txt"
%pycommand% "%nut%" --ADVcontentlist "%targt%">"%i_file%"
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
echo SHOW INFORMATION AND DATA ABOUT THE REQUIRED FIRMWARE
echo ********************************************************
%pycommand% "%nut%" --fw_req "%targt%"

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
ECHO                      (THE XCI MULTI CONTENT BUILDER AND MORE)
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                                POWERED BY SQUIRREL                                "
ECHO "                    BASED IN THE WORK OF BLAWAR AND LUCA FRAGA                     "
ECHO                                     VERSION 0.83
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Blawar's github:  https://github.com/blawar
ECHO Blawar's tinfoil: https://github.com/digableinc/tinfoil
ECHO Luca Fraga's github: https://github.com/LucaFraga
ECHO -------------------------------------------------------------------------------------
exit /B
