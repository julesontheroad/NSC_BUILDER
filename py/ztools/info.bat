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
set /p bs="OR DRAG A XCI\NSP\NSX\NCA FILE AND PRESS ENTER: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto salida
set "targt=%bs%"
for /f "delims=" %%a in ("%bs%") do set "Extension=%%~xa"
for /f "delims=" %%a in ("%bs%") do set "Name=%%~na"
if "%Extension%" EQU ".nsp" ( goto sc2 )
if "%Extension%" EQU ".nsx" ( goto sc2 )
if "%Extension%" EQU ".xci" ( goto sc2 )
if "%Extension%" EQU ".nca" ( goto sc3 )
if "%Extension%" EQU ".nsz" ( goto sc2_1 )
if "%Extension%" EQU ".xcz" ( goto sc2_1 )
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
echo Input "5" to READ the CNMT from the xci\nsp
echo Input "6" to READ the NACP from the xci\nsp
echo Input "7" to READ the main.NPDM from the xci\nsp
echo Input "8" to VERIFY file (xci\nsp\nsx\nca)
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
if "%Extension%" EQU ".nsx" ( goto snfi )
if "%Extension%" EQU ".xci" ( goto snfi )
if "%Extension%" EQU ".nsz" ( goto snfi2 )
if "%Extension%" EQU ".xcz" ( goto snfi2 )
if "%Extension%" EQU ".nca" ( goto snfi_nca ) 

if /i "%bs%"=="1" goto g_file_content
if /i "%bs%"=="2" goto g_content_list
if /i "%bs%"=="3" goto n_info
if /i "%bs%"=="4" goto f_info
if /i "%bs%"=="5" goto r_cnmt
if /i "%bs%"=="6" goto r_nacp
if /i "%bs%"=="7" goto r_npdm
if /i "%bs%"=="8" goto verify

if /i "%bs%"=="b" goto sc1
if /i "%bs%"=="0" goto salida
goto wch

:sc2_1
cls
call :logo
echo .......................................................
echo Input "1" to get FILE LIST of the xci\nsp
echo Input "2" to get CONTENT LIST of the xci\nsp
echo Input "3" to get GAME-INFO and FW requirements
echo Input "4" to READ the CNMT from the xci\nsp
echo Input "5" to READ the NACP from the xci\nsp
echo Input "6" to VERIFY file
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
if "%Extension%" EQU ".nsx" ( goto snfi )
if "%Extension%" EQU ".xci" ( goto snfi )
if "%Extension%" EQU ".nsz" ( goto snfi2 )
if "%Extension%" EQU ".xcz" ( goto snfi2 )
if "%Extension%" EQU ".nca" ( goto snfi_nca ) 

if /i "%bs%"=="1" goto g_file_content2
if /i "%bs%"=="2" goto g_content_list2
if /i "%bs%"=="3" goto f_info2
if /i "%bs%"=="4" goto r_cnmt2
if /i "%bs%"=="5" goto r_nacp2
if /i "%bs%"=="6" goto verify2

if /i "%bs%"=="b" goto sc1
if /i "%bs%"=="0" goto salida
goto wch2

:snfi
for /f "delims=" %%a in ("%bs%") do set "Name=%%~na"
set "targt=%bs%"
goto sc2
:snfi2
for /f "delims=" %%a in ("%bs%") do set "Name=%%~na"
set "targt=%bs%"
goto sc2_1
:wch
echo WRONG CHOICE
pause
goto sc2

:wch2
echo WRONG CHOICE
pause
goto sc2_1

:g_file_content
cls
call :logo
echo ********************************************************
echo SHOW NSP FILE CONTENT OR XCI SECURE PARTITION CONTENT
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --ADVfilelist "%targt%"
goto sc2

:g_file_content2
cls
call :logo
echo ********************************************************
echo SHOW NSZ FILE CONTENT OR XCZ SECURE PARTITION CONTENT
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --ADVfilelist "%targt%"
goto sc2_1

:g_content_list
cls
call :logo
echo ********************************************************
echo SHOW NSP OR XCI CONTENT ARRANGED BY ID
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --ADVcontentlist "%targt%"
goto sc2

:g_content_list2
cls
call :logo
echo ********************************************************
echo SHOW NSP OR XCI CONTENT ARRANGED BY ID
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --ADVcontentlist "%targt%"
goto sc2_1

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
%pycommand% "%nut%" --strip_lines "%i_file%" "2"
ECHO DONE
goto sc2

:f_info
cls
call :logo
echo ********************************************************
echo SHOW INFORMATION AND DATA ABOUT THE REQUIRED FIRMWARE
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --translate %transnutdb% --fw_req "%targt%"
goto sc2

:f_info2
cls
call :logo
echo ********************************************************
echo SHOW INFORMATION AND DATA ABOUT THE REQUIRED FIRMWARE
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --translate %transnutdb% --fw_req "%targt%"

goto sc2_1

:r_cnmt
cls
call :logo
echo ********************************************************
echo SHOW CMT DATA FROM META NCA IN NSP\XCI
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --Read_cnmt "%targt%"
if "%Extension%" EQU ".nsz" ( goto sc2_1 )
if "%Extension%" EQU ".xcz" ( goto sc2_1 )
goto sc2

:r_cnmt2
cls
call :logo
echo ********************************************************
echo SHOW CMT DATA FROM META NCA IN NSP\XCI
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --Read_cnmt "%targt%"
if "%Extension%" EQU ".nsz" ( goto sc2_1 )
if "%Extension%" EQU ".xcz" ( goto sc2_1 )
goto sc2_1

:r_nacp
cls
call :logo
echo ********************************************************
echo SHOW NACP DATA FROM CONTROL NCA IN NSP\XCI
echo ********************************************************
echo IMPLEMENTATION OF 0LIAM'S NACP LIBRARY
%pycommand% "%nut%" -o "%info_dir%" --Read_nacp "%targt%"
if "%Extension%" EQU ".nsz" ( goto sc2_1 )
if "%Extension%" EQU ".xcz" ( goto sc2_1 )
goto sc2

:r_nacp2
cls
call :logo
echo ********************************************************
echo SHOW NACP DATA FROM CONTROL NCA IN NSP\XCI
echo ********************************************************
echo IMPLEMENTATION OF 0LIAM'S NACP LIBRARY
%pycommand% "%nut%" -o "%info_dir%" --Read_nacp "%targt%"
if "%Extension%" EQU ".nsz" ( goto sc2_1 )
if "%Extension%" EQU ".xcz" ( goto sc2_1 )
goto sc2_1

:r_npdm
cls
call :logo
echo ********************************************************
echo SHOW MAIN.NPDM DATA FROM PROGRAM NCA IN NSP\XCI
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --Read_npdm "%targt%"
goto sc2


:verify
cls
call :logo
echo ********************************************************
echo VERIFY A NSP\XCI\NCA
echo ********************************************************
%pycommand% "%nut%" %buffer% -o "%info_dir%" -v "%targt%" 

goto sc2

:verify2
cls
call :logo
echo ********************************************************
echo VERIFY A NSZ\XCZ FILE
echo ********************************************************
%pycommand% "%nut%" %buffer% -o "%info_dir%" -v "%targt%" 

goto sc2_1

:sc3
cls
call :logo
echo .......................................................
echo Input "1" to get NUT-INFO of the NCA
echo Input "2" to READ the CNMT of a meta NCA
echo Input "3" to READ the NACP of a control NCA
echo Input "4" to READ the NPDM of a program NCA
echo Input "5" to VERIFY the NCA
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
if "%Extension%" EQU ".*" ( goto wch_nca )
if "%Extension%" EQU ".nca" ( goto snfi_nca )
if "%Extension%" EQU ".nsp" ( goto snfi )
if "%Extension%" EQU ".nsx" ( goto snfi )
if "%Extension%" EQU ".xci" ( goto snfi )

if /i "%bs%"=="1" goto n_info_nca
if /i "%bs%"=="2" goto r_cnmt_nca
if /i "%bs%"=="3" goto r_nacp_nca
if /i "%bs%"=="4" goto r_npdm_nca
if /i "%bs%"=="5" goto verify_nca

if /i "%bs%"=="b" goto sc1
if /i "%bs%"=="0" goto salida
goto wch

:snfi_nca
for /f "delims=" %%a in ("%bs%") do set "Name=%%~na"
set "targt=%bs%"
goto sc3
:wch_nca
echo WRONG CHOICE
pause
goto sc3

:n_info_nca
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
:n_info_wrong_nca
echo Input "1" to print to text file
echo Input "2" to NOT print to text file
echo.
set /p bs="Enter your choice: "
if /i "%bs%"=="1" goto n_info_print_nca
if /i "%bs%"=="2" goto sc3
echo WRONG CHOICE
echo.
goto n_info_wrong_nca
:n_info_print_nca
if not exist "%info_dir%" MD "%info_dir%">NUL 2>&1
set "i_file=%info_dir%\%Name%-info.txt"
%pycommand% "%nut%" -i "%targt%">"%i_file%"
%pycommand% "%nut%" -i "%targt%">"%i_file%"
%pycommand% "%nut%" --strip_lines "%i_file%" "2"
ECHO DONE
goto sc3

:r_cnmt_nca
cls
call :logo
echo ********************************************************
echo SHOW CMT DATA FROM META NCA IN NSP\XCI
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --Read_cnmt "%targt%"
goto sc3

:r_nacp_nca
cls
call :logo
echo ********************************************************
echo SHOW NACP DATA FROM CONTROL NCA IN NSP\XCI
echo ********************************************************
echo IMPLEMENTATION OF 0LIAM'S NACP LIBRARY
%pycommand% "%nut%" -o "%info_dir%" --Read_nacp "%targt%"
goto sc3

:r_npdm_nca
cls
call :logo
echo ********************************************************
echo SHOW MAIN.NPDM DATA FROM PROGRAM NCA IN NSP\XCI
echo ********************************************************
%pycommand% "%nut%" -o "%info_dir%" --Read_npdm "%targt%"
goto sc3

:verify_nca
cls
call :logo
echo ********************************************************
echo VERIFY A NSP\XCI\NCA
echo ********************************************************
%pycommand% "%nut%" %buffer% -o "%info_dir%" -v "%targt%" 
goto sc3


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
ECHO "                    BASED ON THE WORK OF BLAWAR AND LUCA FRAGA                     "
ECHO                                    VERSION 0.97
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Blawar's github:  https://github.com/blawar
ECHO Blawar's tinfoil: https://github.com/digableinc/tinfoil
ECHO Luca Fraga's github: https://github.com/LucaFraga
ECHO -------------------------------------------------------------------------------------
exit /B
