REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM CREATE STANDARD CRYPTO XCI OR NSP
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo CONVERT\REPACK AS STANDARD CRYPTO NSP\XCI
echo -----------------------------------------------
if exist "%list_folder%\1_1list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (lists/1_1list.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (lists/1_1list.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del "%list_folder%\1_1list.txt" )
endlocal
if not exist "%list_folder%\1_1list.txt" goto manual_INIT
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
if /i "%bs%"=="1" goto dostart
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo BAD CHOICE
goto prevlist0
:delist
del "%list_folder%\1_1list.txt" 2>&1>NUL
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -----------------------------------------------
echo ..................................
echo YOU'VE DECIDED TO START A NEW LIST
echo ..................................
:manual_INIT
endlocal
ECHO ***********************************************
echo Input "1" to add folder to list via selector
echo Input "2" to add file to list via selector
echo Input "3" to add files to list via local libraries
echo Input "4" to add files to list via folder-walker
echo Input "0" to return to the MODE SELECTION MENU
ECHO ***********************************************
echo.
%pycommand% "%squirrel%" -t nsp xci nsz xcz -tfile "%list_folder%\1_1list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%list_folder%\1_1list.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg "%list_folder%\1_1list.txt" mode=file ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\1_1list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\1_1list.txt" "extlist=nsp xci nsz xcz" )
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
echo Input "4" to add files to list via local libraries
echo Input "5" to add files to list via folder-walker
echo Input "e" to exit
echo Input "i" to see list of files to process
echo Input "r" to remove some files (counting from bottom)
echo Input "z" to remove the whole list
echo ......................................................................
ECHO *************************************************
echo Or Input "0" to return to the MODE SELECTION MENU
ECHO *************************************************
echo.
%pycommand% "%squirrel%" -t nsp xci nsz xcz -tfile "%list_folder%\1_1list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" goto dostart
if /i "%eval%"=="2" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg  "%list_folder%\1_1list.txt" mode=folder ext="nsp xci nsz xcz" ) 2>&1>NUL
if /i "%eval%"=="3" ( %pycommand% "%squirrel%" -lib_call listmanager selector2list -xarg  "%list_folder%\1_1list.txt" mode=file ext="nsp xci nsz xcz" )  2>&1>NUL
if /i "%eval%"=="4" ( %pycommand% "%squirrel%" -lib_call picker_walker select_from_local_libraries -xarg "%list_folder%\1_1list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="5" ( %pycommand% "%squirrel%" -lib_call picker_walker get_files_from_walk -xarg "%list_folder%\1_1list.txt" "extlist=nsp xci nsz xcz" )
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" ( del "%list_folder%\1_1list.txt" ) 2>&1>NUL

goto checkagain

:r_files
set /p bs="Input the number of files you want to remove (from bottom): "
set bs=%bs:"=%
%pycommand% "%squirrel%" -lib_call listmanager remove_from_botton -xarg  "%list_folder%\1_1list.txt" "%bs%"

:showlist
cls
call "%nscb_logos%" "program_logo"
%pycommand% "%squirrel%" -lib_call listmanager printcurrent -xarg  "%list_folder%\1_1list.txt" "all" "counter=True"
goto checkagain

:dostart
echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Input "1" to repack list as nsp
echo Input "2" to repack list as xci
echo Input "3" to repack list as both
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto s_cl_wrongchoice

:s_RSV_wrongchoice
if /i "%skipRSVprompt%"=="true" set "patchRSV=false"
if /i "%skipRSVprompt%"=="true" goto s_KeyChange_skip
echo *******************************************************
echo DO YOU WANT TO PATCH THE REQUIRED-SYSTEM-VERSION
echo *******************************************************
echo If you choose to patch it will be set to match the
echo nca crypto so it'll only ask to update your system
echo in the case it's necessary
echo.
echo Input "0" to don't patch the Required System Version
echo Input "1" to "PATCH" the Required System Version
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "patchRSV=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="0" set "patchRSV=false"
if /i "%bs%"=="1" set "patchRSV=true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto s_RSV_wrongchoice
if /i "%bs%"=="0" goto s_KeyChange_skip

:s_KeyChange_wrongchoice
echo *******************************************************
echo SET MAXIMUM KEYGENERATION\RSV ALOWED
echo *******************************************************
echo Depending on your choice keygeneration and RSV will be
echo lowered to the corresponding keygeneration range in case
echo read keygeneration value is bigger than the one specified
echo in the program.
echo THIS WON'T ALWAYS WORK TO LOWER THE FIRMWARE REQUIREMENT.
echo.
echo Input "f" to not change the keygeneration
echo Input "0" to change top keygeneration to 0 (FW 1.0)
echo Input "1" to change top keygeneration to 1 (FW 2.0-2.3)
echo Input "2" to change top keygeneration to 2 (FW 3.0)
echo Input "3" to change top keygeneration to 3 (FW 3.0.1-3.02)
echo Input "4" to change top keygeneration to 4 (FW 4.0.0-4.1.0)
echo Input "5" to change top keygeneration to 5 (FW 5.0.0-5.1.0)
echo Input "6" to change top keygeneration to 6 (FW 6.0.0-6.1.0)
echo Input "7" to change top keygeneration to 7 (FW 6.2.0)
echo Input "8" to change top keygeneration to 8 (FW 7.0.0-8.0.1)
echo Input "9" to change top keygeneration to 9 (FW 8.1.0)
echo Input "10" to change top keygeneration to 10 (FW 9.0.0-9.01)
echo Input "11" to change top keygeneration to 11 (FW 9.1.0)
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "vkey=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="f" set "vkey=false"
if /i "%bs%"=="0" set "vkey=0"
if /i "%bs%"=="0" set "capRSV=0"
if /i "%bs%"=="1" set "vkey=1"
if /i "%bs%"=="1" set "capRSV=65796"
if /i "%bs%"=="2" set "vkey=2"
if /i "%bs%"=="2" set "capRSV=201327002"
if /i "%bs%"=="3" set "vkey=3"
if /i "%bs%"=="3" set "capRSV=201392178"
if /i "%bs%"=="4" set "vkey=4"
if /i "%bs%"=="4" set "capRSV=268435656"
if /i "%bs%"=="5" set "vkey=5"
if /i "%bs%"=="5" set "capRSV=335544750"
if /i "%bs%"=="6" set "vkey=6"
if /i "%bs%"=="6" set "capRSV=402653494"
if /i "%bs%"=="7" set "vkey=7"
if /i "%bs%"=="7" set "capRSV=404750336"
if /i "%bs%"=="8" set "vkey=8"
if /i "%bs%"=="8" set "capRSV=469762048"
if /i "%bs%"=="9" set "vkey=9"
if /i "%bs%"=="9" set "capRSV=537919488"
if /i "%bs%"=="10" set "vkey=10"
if /i "%bs%"=="10" set "capRSV=603979776"
if /i "%bs%"=="11" set "vkey=11"
if /i "%bs%"=="11" set "capRSV=605028352"
if /i "%vkey%"=="none" echo WRONG CHOICE
if /i "%vkey%"=="none" goto s_KeyChange_wrongchoice
goto s_KeyChange_skip

:s_KeyChange_skip
echo Filtering extensions from list according to options chosen
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%list_folder%\1_1list.txt","ext=nsp nsx xci","token=False",Print="False" )

%pycommand% "%squirrel%" -lib_call cmd.cmd_batchprocess loop_repack -xarg "%list_folder%\1_1list.txt" "%buffer%" "%patchRSV%" "%vkey%" "%capRSV%" "%fatype%" "%fexport%" "%skdelta%" "%fold_output%" "%vrepack%"

ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if /i "%va_exit%"=="true" echo PROGRAM WILL CLOSE NOW
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo Input "0" to go back to the mode selection
echo Input "1" to exit the program
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" goto salida
goto s_exit_choice

:salida
::pause
exit