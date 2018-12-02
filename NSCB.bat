@ECHO OFF
::-----------------------------------------------------
::EDIT THIS VARIABLE TO LINK OTHER OPTION FILE
::-----------------------------------------------------
set "op_file=%~dp0zconfig/NSCB_options.cmd"

::-----------------------------------------------------
::COPY OPTIONS FROM OPTION FILE
::-----------------------------------------------------
setlocal
if exist "%op_file%" call "%op_file%" 	  
endlocal & ( 
REM VARIABLES
set "safe_var=%safe_var%"
set "vrepack=%vrepack%"
set "vrename=%vrename%"
set "fi_rep=%fi_rep%"
set "zip_restore=%zip_restore%"
set "manual_intro=%manual_intro%"
REM set "trn_skip=%trn_skip%"
REM set "updx_skip=%updx_skip%"
REM set "ngx_skip=%ngx_skip%"

REM Copy function
set "pycommand=%pycommand%"
set "buffer=%buffer%"
set "nf_cleaner=%nf_cleaner%"
set "patchRSV=%patchRSV%"

REM PROGRAMS
set "nut=%nut%"
set "xci_lib=%xci_lib%"
set "nsp_lib=%nsp_lib%"
set "zip=%zip%"
set "hactool=%hactool%"
set "hacbuild=%hacbuild%"
REM FILES
set "game_info=%game_info%"
set "dec_keys=%dec_keys%"
REM FOLDERS
set "w_folder=%~dp0%w_folder%"
set "fold_output=%fold_output%"
)
::-----------------------------------------------------
::SET ABSOLUTE ROUTES
::-----------------------------------------------------
::Program full route
if exist "%~dp0%nut%" set "nut=%~dp0%nut%"
if exist "%~dp0%xci_lib%"  set "xci_lib=%~dp0%xci_lib%"
if exist "%~dp0%nsp_lib%"  set "nsp_lib=%~dp0%nsp_lib%"
if exist "%~dp0%zip%"  set "zip=%~dp0%zip%"
if exist "%~dp0%hactool%"  set "hactool=%~dp0%hactool%
if exist "%~dp0%hacbuild%"  set "hacbuild=%~dp0%hacbuild%"
::Important files full route
if exist "%~dp0%game_info%"  set "game_info=%~dp0%game_info%"
if exist "%~dp0%dec_keys%"  set "dec_keys=%~dp0%dec_keys%"
::Folder output
CD /d "%~dp0"
if not exist "%fold_output%" MD "%fold_output%"
if not exist "%fold_output%" MD "%~dp0%fold_output%"
if exist "%~dp0%fold_output%"  set "fold_output=%~dp0%fold_output%"
::-----------------------------------------------------
::A LOT OF CHECKS
::-----------------------------------------------------
::Option file check
if not exist "%op_file%" ( goto missing_things )
::Program checks
if not exist "%nut%" ( goto missing_things )
if not exist "%xci_lib%" ( goto missing_things )
if not exist "%nsp_lib%" ( goto missing_things )
if not exist "%zip%" ( goto missing_things )
if not exist "%hactool%" ( goto missing_things )
if not exist "%hacbuild%" ( goto missing_things )
::Important files check
if not exist "%game_info%" ( goto missing_things )
if not exist "%dec_keys%" ( goto missing_things )
::-----------------------------------------------------


::Check if user is dragging a folder or a file
if "%~1"=="" goto manual
if exist "%~1\" goto folder
goto file

:folder
if "%fi_rep%" EQU "multi" goto folder_mult_mode
goto folder_ind_mode

::AUTO MODE. INDIVIDUAL REPACK PROCESSING OPTION.
:folder_ind_mode
::*************
::FOR NSP FILES
::*************
for /r "%~1" %%f in (*.nsp) do (
set "target=%%f"
if exist "%w_folder%" RD /s /q "%w_folder%" >NUL 2>&1

MD "%w_folder%"
MD "%w_folder%\secure"

cls
call :program_logo
echo --------------------------------------
echo Auto-Mode. Individual repacking is set
echo --------------------------------------
echo.
set "filename=%%~nf"
set "orinput=%%f"
set "showname=%orinput%"
call :processing_message
REM echo %safe_var%>safe.txt
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
REM setlocal enabledelayedexpansion
REM set vpack=!vrepack!
REM endlocal & ( set "vpack=!vrepack!" )

REM if "%trn_skip%" EQU "true" ( call :check_titlerights )
if "%vrename%" EQU "true" ( call :addtags_from_nsp )

if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
MD "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.zip" "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
)

::FOR XCI FILES
for /r "%~1" %%f in (*.xci) do (
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
cls
call :program_logo
set "filename=%%~nf"
set "orinput=%%f"
set "showname=%orinput%"
call :processing_message
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo -------------------------------------
echo Extracting secure partition from xci 
echo -------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
echo DONE
if "%vrename%" EQU "true" ( call :addtags_from_xci )
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
MD "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
call :delay
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! ************* 
ECHO ---------------------------------------------------
PING -n 2 127.0.0.1 >NUL 2>&1
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
::pause
exit

::AUTO MODE. MULTIREPACK PROCESSING OPTION.
:folder_mult_mode
set "filename=%~n1"
set "orinput=%~f1"
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
set "end_folder=%filename%"
set "filename=%filename%[multi]"
::FOR NSP FILES
for /r "%~1" %%f in (*.nsp) do (
cls
call :program_logo
echo --------------------------------------
echo Auto-Mode. Multi-repacking is set
echo --------------------------------------
echo.
set "showname=%orinput%"
call :processing_message
::echo %safe_var%>safe.txt
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
)

::FOR XCI FILES
for /r "%~1" %%f in (*.xci) do (
cls
call :program_logo
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
echo DONE
)
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.zip"  "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
call :delay
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! ************* 
ECHO ---------------------------------------------------
PING -n 2 127.0.0.1 >NUL 2>&1
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
::pause
exit

:file
call :program_logo
if "%~x1"==".nsp" ( goto nsp )
if "%~x1"==".xci" ( goto xci )
if "%~x1"==".*" ( goto other )
:other
echo No valid file was dragged. The program only accepts xci or nsp files.
echo You'll be redirected to manual mode.
pause
goto manual

:nsp
set "orinput=%~f1"
set "filename=%~n1"
set "target=%~1"
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%~1"
if "%zip_restore%" EQU "true" ( set "ziptarget=%~1" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp
::echo "%vrepack%"
::echo "%nsp_lib%"
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.zip" "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
call :delay
::pause
exit

:xci
set "filename=%~n1"
set "orinput=%~f1"
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo ------------------------------------
echo Extracting secure partition from xci 
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%~1"
echo DONE
if "%vrename%" EQU "true" call :addtags_from_xci
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
call :delay
::pause
exit

:manual
endlocal


call :program_logo
echo ********************************
echo YOU'VE ENTERED INTO MANUAL MODE
echo ********************************
if "%manual_intro%" EQU "indiv" ( goto normalmode ) 
if "%manual_intro%" EQU "multi" ( goto multimode )
if "%manual_intro%" EQU "split" ( goto SPLMODE )
if "%manual_intro%" EQU "update" ( goto UPDMODE )
goto manual_Reentry

:manual_Reentry
ECHO .......................................................
echo Press "1" to process files individually
echo Press "2" to enter in multi-pack mode
echo Press "3" to enter in splitter mode
echo Press "4" to enter in update mode
echo .......................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto normalmode
if /i "%bs%"=="2" goto multimode
if /i "%bs%"=="3" goto SPLMODE
if /i "%bs%"=="4" goto UPDMODE
goto manual_Reentry

REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM START OF MANUAL MODE. INDIVIDUAL PROCESSING
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////

:normalmode
echo -------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -------------------------------
if exist "list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del list.txt )
endlocal
if not exist "list.txt" goto manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:prevlist0
ECHO .......................................................
echo Press "0" to auto-start processing from the previous list
echo Press "1" to erase list and make a new one.
echo Press "2" to continue building the previous list
echo .......................................................
echo NOTE: By pressing 2 you'll see the previous list 
echo before starting the processing the files and you will 
echo be able to add and delete items from the list
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
endlocal
set /p bs="PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if exist "%bs%\" goto checkfolder
goto checkfile
:checkfolder
DIR /B /S "%bs%\*.nsp">hlist.txt
FINDSTR /L ".nsp" hlist.txt>>list.txt
del hlist.txt
DIR /B /S "%bs%\*.xci">hlist2.txt
FINDSTR /L ".xci" hlist2.txt>>list.txt
del hlist2.txt
goto checkagain
:checkfile
echo %bs%>>hlist.txt
FINDSTR /L ".nsp" hlist.txt>>list.txt
del hlist.txt
echo %bs%>>hlist2.txt
FINDSTR /L ".xci" hlist2.txt>>list.txt
del hlist2.txt
goto checkagain
echo.
:checkagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Press "1" to start processing
echo Press "e" to exit
echo Press "i" to see list of files to process
echo Press "r" to remove some files (counting from bottom)
echo Press "z" to remove the whole list
echo ......................................................................
set /p bs="Drag file/folder or set option: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto start_cleaning
if /i "%bs%"=="e" goto salida
if /i "%bs%"=="i" goto showlist
if /i "%bs%"=="r" goto r_files
if /i "%bs%"=="z" del list.txt
if exist "%bs%\" goto checkfolder
goto checkfile
goto salida

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
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
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<list.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>list.txt.new
endlocal
move /y "list.txt.new" "list.txt" >nul
endlocal

:showlist
ECHO -------------------------------------------------
ECHO                 FILES TO PROCESS 
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (list.txt) do (
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
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Press "1" to repack list as nsp
echo Press "2" to repack list as xci
echo Press "3" to repack list as both
echo Press "0" TO JUST MAKE ZIP FILES!!!!
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="0" set "vrepack=zip"
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto s_cl_wrongchoice
: s_RSV_wrongchoice
echo *******************************************************
echo DO YOU WANT TO PATCH THE REQUIRED-SYSTEM-VERSION
echo *******************************************************
echo If you choose to patch it will be set to match the 
echo nca crypto so it'll only ask to update your system
echo in the case it's necessary
echo.
echo Press "0" to don't patch the Required System Version
echo Press "1" to "PATCH" the Required System Version
set /p bs="Enter your choice: "
set bs=%bs:"=%
set patchRSV=none
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto s_RSV_wrongchoice

for /f "tokens=*" %%f in (list.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"

if "%vrepack%" EQU "zip" ( set "zip_restore=true" )
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%%~nxf"=="%%~nf.nsp" call :nsp_manual
if "%%~nxf"=="%%~nf.xci" call :xci_manual
more +1 "list.txt">"list.txt.new"
move /y "list.txt.new" "list.txt" >nul
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
PING -n 2 127.0.0.1 >NUL 2>&1
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida


:nsp_manual
cls
set "filename=%name%"
call :program_logo
set "showname=%orinput%"
call :processing_message

if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell

if "%vrepack%" EQU "zip" ( goto nsp_just_zip )

%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"

:nsp_just_zip
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" "%%f")
setlocal enabledelayedexpansion
if "%zip_restore%" EQU "true" ( goto :nsp_just_zip2 )
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
:nsp_just_zip2
if not exist "%fold_output%\!end_folder!" MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.zip"  "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
call :delay

:end_nsp_manual
exit /B

:xci_manual
::FOR XCI FILES
cls
if "%vrepack%" EQU "zip" ( goto end_xci_manual )
set "filename=%name%"
call :program_logo
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
if "%vrename%" EQU "true" call :addtags_from_xci
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
call :thumbup
call :delay
:end_xci_manual
exit /B

:contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo STILL !conta! FILES TO PROCESS
echo .................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::RESERVED SPACE FOR MULTI-MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:multimode
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1

echo -------------------------------
echo MULTI-REPACK MODE ACTIVATED
echo -------------------------------
if exist "mlist.txt" goto multi_prevlist
goto multi_manual_INIT
:multi_prevlist
set conta=0
for /f "tokens=*" %%f in (mlist.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del mlist.txt )
endlocal
if not exist "mlist.txt" goto multi_manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:multi_prevlist0
ECHO .......................................................
echo Press "0" to auto-start processing from the previous list
echo Press "1" to erase list and make a new one.
echo Press "2" to continue building the previous list
echo .......................................................
echo NOTE: By pressing 2 you'll see the previous list 
echo before starting processing the files you will 
echo be able to add and delete items to the list
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="2" goto multi_showlist
if /i "%bs%"=="1" goto multi_delist
if /i "%bs%"=="0" goto multi_start_cleaning
echo.
echo BAD CHOICE
goto multi_prevlist0
:multi_delist
del mlist.txt
echo YOU'VE DECIDED TO START A NEW LIST
echo ...................................................................
:multi_manual_INIT
endlocal
set /p bs="PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if exist "%bs%\" goto multi_checkfolder
goto multi_checkfile
:multi_checkfolder
DIR /B /S "%bs%\*.nsp">hmlist.txt
FINDSTR /L ".nsp" hmlist.txt>>mlist.txt
del hmlist.txt
DIR /B /S "%bs%\*.xci">hmlist2.txt
FINDSTR /L ".xci" hmlist2.txt>>mlist.txt
del hmlist2.txt
goto multi_checkagain
:multi_checkfile
echo %bs%>>hmlist.txt
FINDSTR /L ".nsp" hmlist.txt>>mlist.txt
del hmlist.txt
echo %bs%>>hmlist2.txt
FINDSTR /L ".xci" hmlist2.txt>>mlist.txt
del hmlist2.txt
goto multi_checkagain
echo.
:multi_checkagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Press "1" to start processing
echo Press "2" to set a custom logo from a nsp/nca
echo Press "e" to exit
echo Press "i" to see list of files to process
echo Press "r" to remove some files (counting from bottom)
echo Press "z" to remove the whole list
echo ......................................................................
set /p bs="Drag file/folder or set option: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto multi_start_cleaning
if /i "%bs%"=="2" goto multi_set_clogo
if /i "%bs%"=="e" goto salida
if /i "%bs%"=="i" goto multi_showlist
if /i "%bs%"=="r" goto multi_r_files
if /i "%bs%"=="z" del mlist.txt
if exist "%bs%\" goto multi_checkfolder
goto multi_checkfile
goto salida


:multi_r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:multi_update_list1
if !pos1! GTR !pos2! ( goto :multi_update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :multi_update_list1 
:multi_update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<mlist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>mlist.txt.new
endlocal
move /y "mlist.txt.new" "mlist.txt" >nul
endlocal

:multi_showlist
ECHO -------------------------------------------------
ECHO                FILES TO PROCESS 
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (mlist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

goto multi_checkagain

:m_cl_wrongchoice
echo wrong choice
echo ............
:multi_start_cleaning
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Press "1" to repack list as nsp
echo Press "2" to repack list as xci
echo Press "3" to repack list as both
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto m_cl_wrongchoice
: m_RSV_wrongchoice
echo *******************************************************
echo DO YOU WANT TO PATCH THE REQUIRED-SYSTEM-VERSION
echo *******************************************************
echo If you choose to patch it will be set to match the 
echo nca crypto so it'll only ask to update your system
echo in the case it's necessary
echo.
echo Press "0" to don't patch the Required System Version
echo Press "1" to "PATCH" the Required System Version
set /p bs="Enter your choice: "
set bs=%bs:"=%
set patchRSV=none
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto m_RSV_wrongchoice
echo *******************************************************
echo ENTER FINAL FILENAME FOR THE OUTPUT FILE
echo *******************************************************
set /p bs="Please type the name without extension: "
set finalname=%bs:"=%
for /f "tokens=*" %%f in (mlist.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :multi_nsp_manual
if "%%~nxf"=="%%~nf.xci" call :multi_xci_manual
more +1 "mlist.txt">"mlist.txt.new"
move /y "mlist.txt.new" "mlist.txt" >nul
call :multi_contador_NF
)
set "filename=%finalname%"
set "end_folder=%finalname%"
set "filename=%finalname%[multi]"
::pause
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )

setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.zip"  "%fold_output%\!end_folder!" >NUL 2>&1
RD /S /Q "%w_folder%" >NUL 2>&1
endlocal
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida


:multi_nsp_manual
cls
call :program_logo
set "showname=%orinput%"
call :processing_message
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
if "%zip_restore%" EQU "true" ( set "ziptarget=%orinput%" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :thumbup
call :delay
exit /B

:multi_xci_manual
::FOR XCI FILES
cls
call :program_logo
set "showname=%orinput%"
call :processing_message
MD "%w_folder%" >NUL 2>&1
MD "%w_folder%\secure" >NUL 2>&1
MD "%w_folder%\normal" >NUL 2>&1
MD "%w_folder%\update" >NUL 2>&1
call :getname
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
call :thumbup
call :delay
exit /B

:multi_contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo STILL !conta! FILES TO PROCESS
echo .................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B


:multi_set_clogo
echo ------------------------------------------
echo Set custom logo or predominant game
echo ------------------------------------------
echo Indicated for multi-game xci. 
echo Currently custom logos and names are set dragging a nsp or control nca
echo That way the program will copy the control nca in the normal partition
echo If you don't add a custom logo the logo will be set from one of your games
echo ..........................................
echo Press "b" to go back to the list builder
echo ..........................................
set /p bs="OR DRAG A NSP OR NCA FILE OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if /i "%bs%"=="b" ( goto multi_checkagain )
if exist "%bs%" ( goto multi_checklogo )
goto multi_set_clogo

:multi_checklogo
if exist "%~dp0logo.txt" del "%~dp0logo.txt" >NUL 2>&1
echo %bs%>"%~dp0hlogo.txt"
FINDSTR /L ".nsp" "%~dp0hlogo.txt" >"%~dp0logo.txt"
FINDSTR /L ".nca" "%~dp0hlogo.txt" >>"%~dp0logo.txt"
del "%~dp0hlogo.txt"
set /p custlogo=<"%~dp0logo.txt"
::echo %custlogo%
for /f "usebackq tokens=*" %%f in ( "%~dp0logo.txt" ) do (
set "logoname=%%~nxf"
if "%%~nxf"=="%%~nf.nsp" goto ext_log
if "%%~nxf"=="%%~nf.nca" goto check_log
)

:ext_log
del "%~dp0logo.txt"
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
if exist "%w_folder%\normal" RD /S /Q "%w_folder%\normal" >NUL 2>&1

%pycommand% "%nut%" --nsptype "%custlogo%">"%w_folder%\nsptype.txt"
set /p nsptype=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt"
if "%nsptype%" EQU "DLC" echo.
if "%nsptype%" EQU "DLC" echo ---NSP DOESN'T HAVE A CONTROL NCA---
if "%nsptype%" EQU "DLC" echo.
if "%nsptype%" EQU "DLC" ( goto multi_set_clogo )
MD "%w_folder%\normal" >NUL 2>&1
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\normal" --NSP_copy_nca_control "%custlogo%"
echo ................
echo "EXTRACTED LOGO"
echo ................
echo.
goto multi_checkagain

:check_log
del "%~dp0logo.txt"
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
if exist "%w_folder%\normal" RD /S /Q "%w_folder%\normal" >NUL 2>&1
%pycommand% "%nut%" --ncatype "%custlogo%">"%w_folder%\ncatype.txt"
set /p ncatype=<"%w_folder%\ncatype.txt"
del "%w_folder%\ncatype.txt"
if "%ncatype%" NEQ "Content.CONTROL" echo.
if "%ncatype%" NEQ "Content.CONTROL" echo ---NCA IS NOT A CONTROL TYPE---
if "%ncatype%" NEQ "Content.CONTROL" echo.
if "%ncatype%" NEQ "Content.CONTROL" ( goto multi_set_clogo )
MD "%w_folder%\normal" >NUL 2>&1
copy "%custlogo%" "%w_folder%\normal\%logoname%"
echo.
goto multi_checkagain
exit


::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::SPLITTER MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////

:SPLMODE
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1
echo -------------------------------
echo SPLITTER MODE ACTIVATED
echo -------------------------------
if exist "splist.txt" goto sp_prevlist
goto sp_manual_INIT
:sp_prevlist
set conta=0
for /f "tokens=*" %%f in (splist.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del splist.txt )
endlocal
if not exist "splist.txt" goto sp_manual_INIT
ECHO .......................................................
ECHO A PREVIOUS LIST WAS FOUND. WHAT DO YOU WANT TO DO?
:sp_prevlist0
ECHO .......................................................
echo Press "0" to auto-start processing from the previous list
echo Press "1" to erase list and make a new one.
echo Press "2" to continue building the previous list
echo .......................................................
echo NOTE: By pressing 2 you'll see the previous list 
echo before starting processing the files you will 
echo be able to add and delete items to the list
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="2" goto sp_showlist
if /i "%bs%"=="1" goto sp_delist
if /i "%bs%"=="0" goto sp_start_cleaning
echo.
echo BAD CHOICE
goto sp_prevlist0
:sp_delist
del splist.txt
echo YOU'VE DECIDED TO START A NEW LIST
echo ...................................................................
:sp_manual_INIT
endlocal
set /p bs="PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if exist "%bs%\" goto sp_checkfolder
goto sp_checkfile
:sp_checkfolder
DIR /B /S "%bs%\*.nsp">hsplist.txt
FINDSTR /L ".nsp" hsplist.txt>>splist.txt
del hsplist.txt
DIR /B /S "%bs%\*.xci">hsplist2.txt
FINDSTR /L ".xci" hsplist2.txt>>splist.txt
del hsplist2.txt
goto sp_checkagain
:sp_checkfile
echo %bs%>>hsplist.txt
FINDSTR /L ".nsp" hsplist.txt>>splist.txt
del hsplist.txt
echo %bs%>>hsplist2.txt
FINDSTR /L ".xci" hsplist2.txt>>splist.txt
del hsplist2.txt
goto sp_checkagain
echo.
:sp_checkagain
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Press "1" to start processing
echo Press "e" to exit
echo Press "i" to see list of files to process
echo Press "r" to remove some files (counting from bottom)
echo Press "z" to remove the whole list
echo ......................................................................
set /p bs="Drag file/folder or set option: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto sp_start_cleaning
if /i "%bs%"=="e" goto salida
if /i "%bs%"=="i" goto sp_showlist
if /i "%bs%"=="r" goto sp_r_files
if /i "%bs%"=="z" del splist.txt
if exist "%bs%\" goto sp_checkfolder
goto sp_checkfile
goto salida


:sp_r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:sp_update_list1
if !pos1! GTR !pos2! ( goto :sp_update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :sp_update_list1 
:sp_update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<splist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>splist.txt.new
endlocal
move /y "splist.txt.new" "splist.txt" >nul
endlocal

:sp_showlist
ECHO -------------------------------------------------
ECHO                FILES TO PROCESS 
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (splist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

goto sp_checkagain

:sp_cl_wrongchoice
echo wrong choice
echo ............
:sp_start_cleaning
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Press "1" to repack list as nsp
echo Press "2" to repack list as xci
echo Press "3" to repack list as both
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto m_cl_wrongchoice
for /f "tokens=*" %%f in (splist.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "end_folder=%%~nf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :split_content
if "%%~nxf"=="%%~nf.xci" call :split_content
more +1 "splist.txt">"splist.txt.new"
move /y "splist.txt.new" "splist.txt" >nul
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
endlocal
call :sp_contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida


:split_content
cls
call :program_logo
set "showname=%orinput%"
set "sp_repack=%vrepack%"
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
call :processing_message
call :squirrell
%pycommand% "%nut%" %buffer% -o "%w_folder%" --splitter "%orinput%" -pe "secure"
for /f "usebackq tokens=*" %%f in ("%w_folder%\dirlist.txt") do (
setlocal enabledelayedexpansion
set "sp_repack=%vrepack%"
rem echo "!sp_repack!"
set "tfolder=%%f"
set "fname=%%~nf"
set "test=%%~nf"
set test=!test:[DLC]=!
rem echo !test!
rem echo "!test!"
rem echo "!fname!"
if "!test!" NEQ "!fname!" ( set "sp_repack=nsp" )
rem echo "!sp_repack!"
set "test=%%~nf"
set test=!test:[UPD]=!
rem echo !test!
rem echo "!test!"
rem echo "!fname!"
if "!test!" NEQ "!fname!" ( set "sp_repack=nsp" )
rem echo "!sp_repack!"
if "!sp_repack!" EQU "nsp" ( call "%nsp_lib%" "sp_convert" "%w_folder%" "!tfolder!" "!fname!" )
if "!sp_repack!" EQU "xci" ( call "%xci_lib%" "sp_repack" "%w_folder%" "!tfolder!" "!fname!" )
if "!sp_repack!" EQU "both" ( call "%nsp_lib%" "sp_convert" "%w_folder%" "!tfolder!" "!fname!" )
if "!sp_repack!" EQU "both" ( call "%xci_lib%" "sp_repack" "%w_folder%" "!tfolder!" "!fname!" )
endlocal
more +1 "%w_folder%\dirlist.txt">"%w_folder%\dirlist.txt.new"
move /y "%w_folder%\dirlist.txt.new" "%w_folder%\dirlist.txt" >nul
)
del "%w_folder%\dirlist.txt"

call :thumbup
call :delay
exit /B

:sp_contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo STILL !conta! FILES TO PROCESS
echo .................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::UPDATE MODE -> FIRST APPROACH
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////

:UPDMODE
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1
echo -------------------------------------------------------------------
echo                      UPDATE MODE ACTIVATED
echo -------------------------------------------------------------------
if exist "UPDlist.txt" goto upd_prevlist
goto upd_ADD_BASE
:upd_prevlist
set conta=0
for /f "tokens=*" %%f in (UPDlist.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (UPDlist.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del UPDlist.txt )
endlocal
:upd_ADD_BASE
ECHO *******************************************************************
ECHO                         ADD BASE CONTENT 
ECHO *******************************************************************
set /p bs="PLEASE DRAG THE FILE THAT YOU WANT TO UPDATE AND PRESS ENTER: "
set basefile=%bs:"=%
set "test=%basefile%"
set "basecheck=false" 
set test=%test:.xci=%
if "%test%" NEQ "%basefile%" ( set "basecheck=true" )
set "test=%basefile%"
set test=%test:.nsp=%
if "%test%" NEQ "%basefile%" ( set "basecheck=true" )
::echo %basecheck%
if "%basecheck%" EQU "false" ( 
echo. 
echo ---WRONG KIND OF FILE. TRY AGAIN---
echo. 
)
if "%basecheck%" EQU "false" ( goto upd_ADD_BASE)
if not exist "UPDlist.txt" goto upd_ADD_UPD_FILES
ECHO ..................................................................
ECHO A PREVIOUS LIST OF UPDATE FILES WAS FOUND. WHAT DO YOU WANT TO DO?
:upd_prevlist0
ECHO ..................................................................
echo Press "0" to start updating the base content
echo Press "1" to erase list and make a new one.
echo Press "2" to continue building the previous list
echo ..................................................................
echo NOTE: By pressing 2 you'll see the previous list 
echo before starting processing the files you will 
echo be able to add and delete items to the list
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="2" goto upd_showlist
if /i "%bs%"=="1" goto upd_delist
if /i "%bs%"=="0" goto upd_starts
echo.
echo BAD CHOICE
goto upd_prevlist0
:upd_delist
del UPDlist.txt
echo YOU'VE DECIDED TO START A NEW LIST
echo ...................................................................
:upd_ADD_UPD_FILES
ECHO.
ECHO *******************************************************************
ECHO PLEASE ADD THE FILES YOU WANT TO USE TO UPDATE THE BASE CONTENT
ECHO *******************************************************************
set /p bs="PLEASE DRAG A FILE OR FOLDER OVER THE WINDOW AND PRESS ENTER: "
set bs=%bs:"=%
if exist "%bs%\" goto upd_checkfolder
goto upd_checkfile
:upd_checkfolder
DIR /B /S "%bs%\*.nsp">hUPDlist.txt
FINDSTR /L ".nsp" hUPDlist.txt>>UPDlist.txt
del hUPDlist.txt
DIR /B /S "%bs%\*.xci">hUPDlist2.txt
FINDSTR /L ".xci" hUPDlist2.txt>>UPDlist.txt
del hUPDlist2.txt
goto upd_checkagain
:upd_checkfile
echo %bs%>>hUPDlist.txt
FINDSTR /L ".nsp" hUPDlist.txt>>UPDlist.txt
del hUPDlist.txt
echo %bs%>>hUPDlist2.txt
FINDSTR /L ".xci" hUPDlist2.txt>>UPDlist.txt
del hUPDlist2.txt
goto upd_checkagain
echo.
:upd_checkagain
echo.
echo WHAT DO YOU WANT TO DO?
echo ......................................................................
echo "DRAG ANOTHER FILE OR FOLDER AND PRESS ENTER TO ADD ITEMS TO THE LIST"
echo.
echo Press "1" to start processing
echo Press "2" to change basecontent
echo Press "i" to see list of files to process
echo Press "b" to see the current base content
echo Press "r" to remove some files (counting from bottom)
echo Press "z" to remove the whole list
echo Press "e" to exit
echo ......................................................................
set /p bs="Drag file/folder or set option: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto upd_starts
if /i "%bs%"=="2" goto upd_ADD_BASE
if /i "%bs%"=="e" goto salida
if /i "%bs%"=="i" goto upd_showlist
if /i "%bs%"=="b" goto upd_showbase
if /i "%bs%"=="r" goto upd_r_files
if /i "%bs%"=="z" del UPDlist.txt
if exist "%bs%\" goto upd_checkfolder
goto upd_checkfile
goto salida

:upd_showbase
echo.
ECHO -------------------------------------------------
ECHO                BASE CONTENT 
ECHO -------------------------------------------------
echo %basefile%
goto upd_checkagain

:upd_r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (UPDlist.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:upd_update_list1
if !pos1! GTR !pos2! ( goto :upd_update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :upd_update_list1 
:upd_update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<UPDlist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>UPDlist.txt.new
endlocal
move /y "UPDlist.txt.new" "UPDlist.txt" >nul
endlocal

:upd_showlist
ECHO.
ECHO -------------------------------------------------
ECHO                FILES TO PROCESS 
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (UPDlist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (UPDlist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo YOU'VE ADDED !conta! FILES TO PROCESS
echo .................................................
endlocal

goto upd_checkagain

:upd_wrongchoice1
echo wrong choice
echo ............
:upd_starts
echo *******************************************************
echo HOW DO YOU WANT TO PROCESS THE BASE FILE
echo *******************************************************
echo Press "1" to remove previous updates
echo Press "2" to remove previous dlcs
echo Press "3" to remove previous updates and dlcs
set /p bs="Enter your choice: "
set bs=%bs:"=%
set cskip=none
if /i "%bs%"=="1" set "cskip=upd"
if /i "%bs%"=="2" set "cskip=dlc"
if /i "%bs%"=="3" set "cskip=both"
if %cskip%=="none" goto upd_wrongchoice1
goto upd_pack_choice
:upd_wrongchoice2
echo wrong choice
echo ............
:upd_pack_choice
echo *******************************************************
echo CHOOSE HOW DO YOU WANT TO PACK THE RESULT
echo *******************************************************
echo Press "1" to repack list as nsp
echo Press "2" to repack list as xci
echo Press "3" to repack list as both
set /p bs="Enter your choice: "
set vrepack=none
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto upd_pack_choice
echo *******************************************************
echo DO YOU WANT TO PATCH THE REQUIRED-SYSTEM-VERSION
echo *******************************************************
echo If you choose to patch it will be set to match the 
echo nca crypto so it'll only ask to update your system
echo in the case it's necessary
echo.
echo Press "0" to don't patch the Required System Version
echo Press "1" to "PATCH" the Required System Version
set /p bs="Enter your choice: "
set bs=%bs:"=%
set patchRSV=none
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto m_RSV_wrongchoice
if exist "%w_folder%" RD /S /Q "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" -cskip "%cskip%" --updbase "%basefile%"

for %%i in ("%basefile%") do (
set "filename=%%~ni"
)
call :getname

for /f "tokens=*" %%f in (UPDlist.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :UPD_nsp_manual
if "%%~nxf"=="%%~nf.xci" call :UPD_xci_manual
more +1 "UPDlist.txt">"UPDlist.txt.new"
move /y "UPDlist.txt.new" "UPDlist.txt" >nul
call :UPD_contador_NF
)
set "filename=%end_folder%[multi]"
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )

setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.zip"  "%fold_output%\!end_folder!" >NUL 2>&1
RD /S /Q "%w_folder%" >NUL 2>&1
endlocal
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
ECHO PROGRAM WILL CLOSE NOW
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida


:UPD_nsp_manual
cls
call :program_logo
set "showname=%orinput%"
call :processing_message
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
if "%zip_restore%" EQU "true" ( set "ziptarget=%orinput%" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :thumbup
call :delay
exit /B

:UPD_xci_manual
::FOR XCI FILES
cls
call :program_logo
set "showname=%orinput%"
call :processing_message
MD "%w_folder%" >NUL 2>&1
MD "%w_folder%\secure" >NUL 2>&1
MD "%w_folder%\normal" >NUL 2>&1
MD "%w_folder%\update" >NUL 2>&1
call :getname
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
call :thumbup
call :delay
exit /B

:UPD_contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (UPDlist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo STILL !conta! FILES TO PROCESS
echo .................................................
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
ECHO -------------------------------------------------------------------------------------
ECHO =============================     BY JULESONTHEROAD     =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                             POWERED WITH NUT BY BLAWAR                            "
ECHO "                             AND LUCA FRAGA'S HACBUILD                             "
ECHO                                     VERSION 0.70                                     	
ECHO -------------------------------------------------------------------------------------                   
ECHO Program's github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Revised hacbuild: https://github.com/julesontheroad/hacbuild
ECHO Blawar's NUT    : https://github.com/blawar/nut 
ECHO SciresM hactool : https://github.com/SciresM/hactool
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

:getname

if not exist %w_folder% MD %w_folder% >NUL 2>&1

set filename=%filename:[NAP]=%
set filename=%filename:[rr]=%
set filename=%filename:[xcib]=%
set filename=%filename:[nxt]=%
set filename=%filename:[Trimmed]=%
echo %filename% >"%w_folder%\fname.txt"

::deletebrackets
for /f "usebackq tokens=1* delims=[" %%a in ("%w_folder%\fname.txt") do (
    set end_folder=%%a)
echo %end_folder%>"%w_folder%\fname.txt"
::deleteparenthesis
for /f "usebackq tokens=1* delims=(" %%a in ("%w_folder%\fname.txt") do (
    set end_folder=%%a)
echo %end_folder%>"%w_folder%\fname.txt"
::I also wanted to remove_(
set end_folder=%end_folder:_= %
set end_folder=%end_folder:~0,-1%
del "%w_folder%\fname.txt" >NUL 2>&1
if "%vrename%" EQU "true" ( set "filename=%end_folder%" )
exit /B

:makezip
echo.
echo Making zip for %ziptarget%
echo.
%pycommand% "%nut%" %buffer% %patchRSV% -o "%w_folder%\zip" --zip_combo "%ziptarget%"
%pycommand% "%nut%" -o "%w_folder%\zip" --NSP_c_KeyBlock "%ziptarget%"
%pycommand% "%nut%" --nsptitleid "%ziptarget%" >"%w_folder%\nsptitleid.txt"
if exist "%w_folder%\secure\*.dat" ( move "%w_folder%\secure\*.dat" "%w_folder%\zip" ) >NUL 2>&1

set /p titleid=<"%w_folder%\nsptitleid.txt"
del "%w_folder%\nsptitleid.txt" >NUL 2>&1
%pycommand% "%nut%" --nsptype "%ziptarget%" >"%w_folder%\nsptype.txt"
set /p type=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt" >NUL 2>&1
%pycommand% "%nut%" --ReadversionID "%ziptarget%">"%w_folder%\nspversion.txt"
set /p verID=<"%w_folder%\nspversion.txt"
set "verID=V%verID%"
del "%w_folder%\nspversion.txt" >NUL 2>&1
if "%type%" EQU "BASE" ( set "ctag=" )
if "%type%" EQU "UPDATE" ( set ctag=[UPD] )
if "%type%" EQU "DLC" ( set ctag=[DLC] )
%pycommand% "%nut%" -i "%ziptarget%">"%w_folder%\zip\fileinfo[%titleid%][%verID%]%ctag%.txt" 
%pycommand% "%nut%" --NSP_filelist "%ziptarget%">"%w_folder%\zip\ORIGINAL_filelist[%titleid%][%verID%]%ctag%.txt"
"%zip%" a "%w_folder%\%titleid%[%verID%]%ctag%.zip" "%w_folder%\zip\*.*" >NUL 2>&1
RD /S /Q "%w_folder%\zip" >NUL 2>&1
exit /B

:processing_message
echo Processing %showname%
echo.
exit /B

:check_titlerights
%pycommand% "%nut%" --nsp_htrights "%target%">"%w_folder%\trights.txt"
set /p trights=<"%w_folder%\trights.txt"
del "%w_folder%\trights.txt" >NUL 2>&1
if "%trights%" EQU "TRUE" ( goto ct_true )
if "%vrepack%" EQU "nsp" ( set "vpack=none" )
if "%vrepack%" EQU "both" ( set "vpack=xci" )
:ct_true
exit /B


:addtags_from_nsp
%pycommand% "%nut%" --nsptitleid "%orinput%" >"%w_folder%\nsptitleid.txt"
set /p titleid=<"%w_folder%\nsptitleid.txt"
del "%w_folder%\nsptitleid.txt" >NUL 2>&1
%pycommand% "%nut%" --nsptype "%orinput%" >"%w_folder%\nsptype.txt"
set /p type=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt" >NUL 2>&1
if "%type%" EQU "BASE" ( set filename=%filename%[%titleid%][v0] )
if "%type%" EQU "UPDATE" ( set filename=%filename%[%titleid%][UPD] )
if "%type%" EQU "DLC" ( set filename=%filename%[%titleid%][DLC] )

exit /B
:addtags_from_xci
dir "%w_folder%\secure\*.cnmt.nca" /b  >"%w_folder%\ncameta.txt"
set /p ncameta=<"%w_folder%\ncameta.txt"
del "%w_folder%\ncameta.txt" >NUL 2>&1 
set "ncameta=%w_folder%\secure\%ncameta%"
%pycommand% "%nut%" --ncatitleid "%ncameta%" >"%w_folder%\ncaid.txt"
set /p titleid=<"%w_folder%\ncaid.txt"
del "%w_folder%\ncaid.txt"
echo [%titleid%]>"%w_folder%\titleid.txt"

FINDSTR /L 000] "%w_folder%\titleid.txt">"%w_folder%\isbase.txt"
set /p c_base=<"%w_folder%\isbase.txt"
del "%w_folder%\isbase.txt"
FINDSTR /L 800] "%w_folder%\titleid.txt">"%w_folder%\isupdate.txt"
set /p c_update=<"%w_folder%\isupdate.txt"
del "%w_folder%\isupdate.txt"

set ttag=[DLC]

if [%titleid%] EQU %c_base% set ttag=[v0]
if [%titleid%] EQU %c_update% set ttag=[UPD]
 
set filename=%filename%[%titleid%][%ttag%] 
del "%w_folder%\titleid.txt"
exit /B

:missing_things
call :program_logo
echo ....................................
echo You're missing the following things:
echo ....................................
echo.
if not exist "%op_file%" echo - The config file is not correctly pointed or is missing.
if not exist "%nut%" echo - "nut_RTR.py" is not correctly pointed or is missing.
if not exist "%xci_lib%" echo - "XCI.bat" is not correctly pointed or is missing.
if not exist "%nsp_lib%" echo - "NSP.bat" is not correctly pointed or is missing.
if not exist "%zip%" echo - "7za.exe" is not correctly pointed or is missing.
if not exist "%hactool%" echo - "hactool.exe" is not correctly pointed or is missing.
if not exist "%hacbuild%" echo - "hacbuild.exe" is not correctly pointed or is missing.
::File full route
if not exist "%game_info%" echo - "game_info.ini" is not correctly pointed or is missing.
if not exist "%dec_keys%" echo - "keys.txt" is not correctly pointed or is missing.
echo.
pause
echo Program will exit now
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida
:salida
::pause
exit



