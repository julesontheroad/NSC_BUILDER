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
set "showname=%orinput%"
call :processing_message
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
REM echo %safe_var%>safe.txt
call :squirrell
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%%f"
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
set "filename=%%~nxf"
set "orinput=%%f"
set "showname=%orinput%"
call :processing_message
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo -------------------------------------
echo Extracting secure partition from xci 
echo -------------------------------------
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%%f"
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
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
::echo %safe_var%>safe.txt
call :squirrell
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%%f"
)

::FOR XCI FILES
for /r "%~1" %%f in (*.xci) do (
cls
call :program_logo
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%%f"
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
exit

:file
call :program_logo
if "%~x1"==".nsp" ( goto nsp )
if "%~x1"==".xci" ( goto xci )
if "%~x1"==".*" ( goto other )
goto manual

:nsp
set "orinput=%~f1"
set "filename=%~n1"
set "target=%~1"
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%~1"
call :getname
if "%zip_restore%" EQU "true" ( set "ziptarget=%~1" )
if "%zip_restore%" EQU "true" ( call :makezip )
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
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%~1"
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
exit

:manual
endlocal

call :program_logo
echo ********************************
echo YOU'VE ENTERED INTO MANUAL MODE
echo ********************************
if "%manual_intro%" EQU "indiv" ( goto normalmode ) 
if "%manual_intro%" EQU "multi" ( goto multimode )
goto manual_Reentry

:manual_Reentry
ECHO .......................................................
echo Press "1" to process files individually
echo Press "2" to enter in multi-pack mode
echo .......................................................
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto normalmode
if /i "%bs%"=="2" goto multimode
goto manual_Reentry

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
ECHO A PREVIOUS LIST WHAS FOUND. WHAT DO YOU WANT TO DO?
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
DIR /B /S "%bs%\*.nsp" >hlist.txt
FINDSTR /L ".nsp" hlist.txt >>list.txt
del hlist.txt
DIR /B /S "%bs%\*.xci" >hlist2.txt
FINDSTR /L ".xci" hlist2.txt >>list.txt
del hlist2.txt
goto checkagain
:checkfile
echo %bs% >>hlist.txt
FINDSTR /L ".nsp" hlist.txt >>list.txt
del hlist.txt
echo %bs% >>hlist2.txt
FINDSTR /L ".xci" hlist2.txt >>list.txt
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
pause

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
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto s_cl_wrongchoice
for /f "tokens=*" %%f in (list.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%%~nxf"=="%%~nf.nsp" call :nsp_manual
if "%%~nxf"=="%%~nf.xci" call :xci_manual
more +1 "list.txt" >"list.txt.new"
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
call :program_logo
set "showname=%orinput%"
call :processing_message

if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
call :getname

if "%zip_restore%" EQU "true" ( call :makezip )

if "%vrename%" EQU "true" call :addtags_from_nsp
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" "%%f")
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
:end_nsp_manual
exit /B

:xci_manual
::FOR XCI FILES
cls
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
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
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
set conta=
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo STILL !conta! FILES TO PROCESS
echo .................................................
PING -n 2 127.0.0.1 >NUL 2>&1
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
ECHO A PREVIOUS LIST WHAS FOUND. WHAT DO YOU WANT TO DO?
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
DIR /B /S "%bs%\*.nsp" >hmlist.txt
FINDSTR /L ".nsp" hmlist.txt >>mlist.txt
del hmlist.txt
DIR /B /S "%bs%\*.xci" >hmlist2.txt
FINDSTR /L ".xci" hmlist2.txt >>mlist.txt
del hmlist2.txt
goto multi_checkagain
:multi_checkfile
echo %bs% >>hmlist.txt
FINDSTR /L ".nsp" hmlist.txt >>mlist.txt
del hmlist.txt
echo %bs% >>hmlist2.txt
FINDSTR /L ".xci" hmlist2.txt >>mlist.txt
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
if /i "%bs%"=="z" del multi_mlist.txt
if exist "%bs%\" goto multi_checkfolder
goto multi_checkfile
goto salida
pause

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
more +1 "mlist.txt" >"mlist.txt.new"
move /y "mlist.txt.new" "mlist.txt" >nul
call :multi_contador_NF
)
set "filename=%finalname%"
set "end_folder=%finalname%"
set "filename=%finalname%[multi]"

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
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
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
%pycommand% "%nut%" %buffer% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo DONE
call :thumbup
call :delay
exit /B

:multi_contador_NF
setlocal enabledelayedexpansion
set "cmd=findstr /R /N "^^" "%~dp0mlist.txt" | find /C ":""
for /f %%a in ('!cmd!') do set number=%%a
echo .................................................
echo STILL %number% FILES TO PROCESS
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
for /f "tokens=*" %%f in ( %~dp0logo.txt ) do (
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
%pycommand% "%nut%" %buffer% -o "%w_folder%\normal" --NSP_copy_nca_control "%custlogo%"
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
ECHO                                     VERSION 0.60                                     	
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
set filename=%filename:[NAP]=%
set filename=%filename:[rr]=%
set filename=%filename:[xcib]=%
set filename=%filename:[nxt]=%
set filename=%filename:[Trimmed]=%
echo %filename%>"%w_folder%\fname.txt"

::deletebrackets
for /f "tokens=1* delims=[" %%a in (%w_folder%\fname.txt) do (
    set end_folder=%%a)
echo %end_folder%>"%w_folder%\fname.txt"
::deleteparenthesis
for /f "tokens=1* delims=(" %%a in (%w_folder%\fname.txt) do (
    set end_folder=%%a)
echo %end_folder%>"%w_folder%\fname.txt"
::I also wanted to remove_(
set end_folder=%end_folder:_= %
del "%w_folder%\fname.txt" >NUL 2>&1
if "%vrename%" EQU "true" ( set "filename=%end_folder%" )
exit /B

:makezip
echo Making zip for %ziptarget%
echo.
%pycommand% "%nut%" %buffer% -o "%w_folder%\zip" --zip_combo "%ziptarget%"
%pycommand% "%nut%" -o "%w_folder%\zip" --NSP_c_KeyBlock "%ziptarget%"
%pycommand% "%nut%" --nsptitleid "%ziptarget%" >"%w_folder%\nsptitleid.txt"
set /p titleid=<"%w_folder%\nsptitleid.txt"
del "%w_folder%\nsptitleid.txt" >NUL 2>&1
%pycommand% "%nut%" --nsptype "%ziptarget%" >"%w_folder%\nsptype.txt"
set /p type=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt" >NUL 2>&1
if "%type%" EQU "BASE" ( set ctag=[BASE] )
if "%type%" EQU "UPDATE" ( set ctag=[UPD] )
if "%type%" EQU "DLC" ( set ctag=[DLC] )
%pycommand% "%nut%" -i "%ziptarget%">"%w_folder%\zip\fileinfo[%titleid%]%ctag%.txt" 
%pycommand% "%nut%" --NSP_filelist "%ziptarget%">"%w_folder%\zip\filelist[%titleid%]%ctag%.txt"
"%zip%" a "%w_folder%\%titleid%%ctag%.zip" "%w_folder%\zip\*.*" >NUL 2>&1
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
exit



