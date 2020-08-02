REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM MANUAL MODE. INDIVIDUAL PROCESSING
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:main
cls
call "%nscb_logos%" "program_logo"
echo -----------------------------------------------
echo INDIVIDUAL PROCESSING ACTIVATED
echo -----------------------------------------------
echo *******************************************************
echo WHAT DO YOU WNAT TO DO?
echo *******************************************************
echo Input "1" to repack CONVERT\REPACK files as XCI\NSP without titlerights
echo Input "2" to remove DELTAS from nsp update files
echo Input "3" to RENAME xci\nsp\nsz\xcz\nsx files
echo Input "4" to use xci SUPERTRIMMER\TRIMMER\UNTRIMMER
echo Input "5" to REBUILD nsp by cnmt order
echo Input "6" to VERIFY files
echo.
ECHO ******************************************
echo Or Input "0" to return to the main program
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set choice=none
if /i "%bs%"=="0" call "%main_program%"
if /i "%bs%"=="1" call "%cmdfolder%\1_1_repack.bat"
if /i "%bs%"=="2" call "%cmdfolder%\1_2_rem_deltas.bat"
if /i "%bs%"=="3" call "%cmdfolder%\1_3_renamer.bat"
if /i "%bs%"=="4" call "%cmdfolder%\1_4_xci_trimmer.bat"
if /i "%bs%"=="5" call "%cmdfolder%\1_5_rebuild_by_cnmt.bat"
if /i "%bs%"=="6" call "%cmdfolder%\1_6_verification.bat"
goto main





























echo *******************************************************
echo CHOOSE WHAT TO DO AFTER PROCESSING THE SELECTED FILES
echo *******************************************************
echo Input "1" to repack list as nsp
echo Input "2" to repack list as xci
echo Input "3" to repack list as both
echo.
echo SPECIAL OPTIONS:
echo Input "4" to erase deltas from nsp files
echo Input "5" to rename xci or nsp files
echo Input "6" to xci supertrimmer\trimmer\untrimmer
echo Input "7" to rebuild nsp by cnmt order
echo Input "8" to verify files
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
if /i "%bs%"=="4" set "vrepack=nodelta"
if /i "%bs%"=="4" goto s_KeyChange_skip
if /i "%bs%"=="5" set "vrepack=renamef"
if /i "%bs%"=="5" goto rename
if /i "%bs%"=="6" goto s_trimmer_selection
if /i "%bs%"=="7" set "vrepack=rebuild"
if /i "%bs%"=="7" goto s_KeyChange_skip
if /i "%bs%"=="8" set "vrepack=verify"
if /i "%bs%"=="8" goto s_vertype
if %vrepack%=="none" goto s_cl_wrongchoice
:s_RSV_wrongchoice
if /i "%skipRSVprompt%"=="true" set "patchRSV=-pv false"
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
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
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
if /i "%bs%"=="f" set "vkey=-kp false"
if /i "%bs%"=="0" set "vkey=-kp 0"
if /i "%bs%"=="0" set "capRSV=--RSVcap 0"
if /i "%bs%"=="1" set "vkey=-kp 1"
if /i "%bs%"=="1" set "capRSV=--RSVcap 65796"
if /i "%bs%"=="2" set "vkey=-kp 2"
if /i "%bs%"=="2" set "capRSV=--RSVcap 201327002"
if /i "%bs%"=="3" set "vkey=-kp 3"
if /i "%bs%"=="3" set "capRSV=--RSVcap 201392178"
if /i "%bs%"=="4" set "vkey=-kp 4"
if /i "%bs%"=="4" set "capRSV=--RSVcap 268435656"
if /i "%bs%"=="5" set "vkey=-kp 5"
if /i "%bs%"=="5" set "capRSV=--RSVcap 335544750"
if /i "%bs%"=="6" set "vkey=-kp 6"
if /i "%bs%"=="6" set "capRSV=--RSVcap 402653494"
if /i "%bs%"=="7" set "vkey=-kp 7"
if /i "%bs%"=="7" set "capRSV=--RSVcap 404750336"
if /i "%bs%"=="8" set "vkey=-kp 8"
if /i "%bs%"=="8" set "capRSV=--RSVcap 469762048"
if /i "%bs%"=="9" set "vkey=-kp 9"
if /i "%bs%"=="9" set "capRSV=--RSVcap 537919488"
if /i "%bs%"=="10" set "vkey=-kp 10"
if /i "%bs%"=="10" set "capRSV=--RSVcap 603979776"
if /i "%bs%"=="11" set "vkey=-kp 11"
if /i "%bs%"=="11" set "capRSV=--RSVcap 605028352"
if /i "%vkey%"=="none" echo WRONG CHOICE
if /i "%vkey%"=="none" goto s_KeyChange_wrongchoice
goto s_KeyChange_skip

:s_trimmer_selection
echo *******************************************************
echo SUPERTRIMMING\TRIMMING\UNTRIMMING
echo *******************************************************
echo DESCRYPTION:
echo - Supetrimming
echo   Removes System Firmware update, empties update partition,
echo   removes final and middle padding, removes logo partition
echo   removes game update, keeps game certificate if exists
echo   (Perfect for installation)
echo - Supetrimming  keeping game updates
echo   Same as before but keeps game updates
echo - Trimming
echo   Removes final padding (empty data)
echo - UnTrimming
echo   Undoes the trimming of a normal trimming operation
echo.
echo Input "1" Supertrimm
echo Input "2" Supertrimm keeping game updates
echo Input "3" Trimm
echo Input "4" UnTrimm
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "vrepack=none"
if /i "%bs%"=="1" set "vrepack=xci_supertrimmer"
if /i "%bs%"=="2" set "vrepack=xci_supertrimmer_keep_upd"
if /i "%bs%"=="3" set "vrepack=xci_trimmer"
if /i "%bs%"=="4" set "vrepack=xci_untrimmer"
if /i "%vrepack%"=="none" echo WRONG CHOICE
if /i "%vrepack%"=="none" goto s_trimmer_selection
goto s_KeyChange_skip

:s_vertype
echo *******************************************************
echo TYPE OF VERIFICATION
echo *******************************************************
echo This chooses the level of verification.
echo DECRYPTION - Files ar readable, ticket's correct
echo              No file is missing
echo SIGNATURE  - Check's header against Nintendo Sig1
echo              Calculates original header for NSCB modifications
echo HASH       - Check's current and original hash of files and
echo              matches them against name of the file
echo.
echo NOTE: If you read files on a remote service via a filestream
echo method decryption or signature are the recommended methods
echo.
echo Input "1" to use DECRYPTION verification (fast)
echo Input "2" to use decryption + SIGNATURE verification (fast)
echo Input "3" to use decryption + signature + HASH verification (slow)
echo.
ECHO ******************************************
echo Or Input "b" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "verif=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" set "verif=lv1"
if /i "%bs%"=="2" set "verif=lv2"
if /i "%bs%"=="3" set "verif=lv3"
if /i "%verif%"=="none" echo WRONG CHOICE
if /i "%verif%"=="none" echo.
if /i "%verif%"=="none" goto s_vertype

:s_KeyChange_skip
echo Filtering extensions from list according to options chosen
if "%vrepack%" EQU "xci_supertrimmer" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=xci","token=False",Print="False" )
if "%vrepack%" EQU "xci_supertrimmer_keep_upd" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=xci","token=False",Print="False" )
if "%vrepack%" EQU "xci_trimmer" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=xci","token=False",Print="False" )
if "%vrepack%" EQU "xci_untrimmer" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=xci","token=False",Print="False" )
if "%vrepack%" EQU "rebuild" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=nsp nsz","token=False",Print="False" )
if "%vrepack%" EQU "nodelta" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=nsp nsz","token=False",Print="False" )
if "%fatype%" EQU "-fat fat32" echo Fat32 selected, removing nsz and xcz from input list
if "%fatype%" EQU "-fat fat32" ( %pycommand% "%squirrel%" -lib_call listmanager filter_list "%prog_dir%lists/list.txt","ext=nsp nsx xci","token=False",Print="False" )
cls
call "%nscb_logos%" "program_logo"

for /f "tokens=*" %%f in (lists/list.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
set "ziptarget=%%f"

if "%%~nxf"=="%%~nf.nsp" call :nsp_manual
if "%%~nxf"=="%%~nf.nsz" call :nsp_manual
if "%%~nxf"=="%%~nf.xci" call :xci_manual
if "%%~nxf"=="%%~nf.xcz" call :xci_manual
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:rename
:s_rename_wrongchoice1
echo.
echo *******************************************************
echo TYPE OF RENAME
echo *******************************************************
echo Normal modes:
echo Input "1" to ALWAYS rename
echo Input "2" to NOT RENAME IF [TITLEID] is present
echo Input "3" to NOT RENAME IF [TITLEID] is equal to the one calculated
echo Input "4" to ONLY ADD ID
echo Input "5" to ADD ID + TAGS AND KEEP NAME TILL [
echo.
echo Sanitize:
echo Input "6" to REMOVE BAD characters from the file name
echo Input "7" to convert japanese\chinese to ROMAJI
echo.
echo Clean tags:
echo Input "8" to REMOVE [] tags from the filename
echo Input "9" to REMOVE () tags from the filename
echo Input "10" to REMOVE [] and () tags from the filename
echo Input "11" to REMOVE TITLE FROM FIRST [
echo Input "12" to REMOVE TITLE FROM FIRST (
echo.
ECHO ******************************************
echo Or Input "0" to return to the list options
ECHO ******************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "renmode=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="1" set "renmode=force"
if /i "%bs%"=="1" set "oaid=false"
if /i "%bs%"=="2" set "renmode=skip_corr_tid"
if /i "%bs%"=="2" set "oaid=false"
if /i "%bs%"=="3" set "renmode=skip_if_tid"
if /i "%bs%"=="3" set "oaid=false"
if /i "%bs%"=="4" set "renmode=skip_corr_tid"
if /i "%bs%"=="4" set "oaid=true"
if /i "%bs%"=="5" set "renmode=skip_corr_tid"
if /i "%bs%"=="5" set "oaid=idtag"
if /i "%bs%"=="6" goto sanitize
if /i "%bs%"=="7" goto romaji

if /i "%bs%"=="8" set "tagtype=[]"
if /i "%bs%"=="8" goto filecleantags
if /i "%bs%"=="9" set "tagtype=()"
if /i "%bs%"=="9" goto filecleantags
if /i "%bs%"=="10" set "tagtype=false"
if /i "%bs%"=="10" goto filecleantags
if /i "%bs%"=="11" set "tagtype=["
if /i "%bs%"=="11" goto filecleantags
if /i "%bs%"=="12" set "tagtype=("
if /i "%bs%"=="12" goto filecleantags

if /i "%renmode%"=="none" echo WRONG CHOICE
if /i "%renmode%"=="none" goto s_rename_wrongchoice1
echo.
:s_rename_wrongchoice2
echo *******************************************************
echo ADD VERSION NUMBER
echo *******************************************************
echo Adds content version number to filename
echo.
echo Input "1" to ADD version number
echo Input "2" to NOT ADD version number
echo Input "3" to NOT ADD version in xci if VERSION=0
echo.
ECHO *********************************************
echo Or Input "b" to return to TYPE OF RENAME
echo Or Input "0" to return to the list options
ECHO *********************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "nover=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice1
if /i "%bs%"=="1" set "nover=false"
if /i "%bs%"=="2" set "nover=true"
if /i "%bs%"=="3" set "nover=xci_no_v0"
if /i "%nover%"=="none" echo WRONG CHOICE
if /i "%nover%"=="none" goto s_rename_wrongchoice2
echo.
:s_rename_wrongchoice3
echo *******************************************************
echo ADD LANGUAGE STRING
echo *******************************************************
echo Adds language tags for games and updates
echo.
echo Input "1" to NOT ADD language string
echo Input "2" to ADD language string
echo.
echo Note: Language can't be read from dlcs so this option
echo won't affect them
echo.
ECHO *********************************************
echo Or Input "b" to return to ADD VERSION NUMBER
echo Or Input "0" to return to the list options
ECHO *********************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "addlangue=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice2
if /i "%bs%"=="1" set "addlangue=false"
if /i "%bs%"=="2" set "addlangue=true"
if /i "%addlangue%"=="none" echo WRONG CHOICE
if /i "%addlangue%"=="none" goto s_rename_wrongchoice3
echo.
:s_rename_wrongchoice4
echo *******************************************************
echo DLC NAMES FALLBACK
echo *******************************************************
echo Current version request dlc names to nutdb, this option
echo states the fallback system to employ in case the name
echo can't be retrieved.
echo.
echo Normal format basename [contentname]
echo Option 3 format basename [contentname] [DLC Number]
echo.
echo Input "1" to KEEP basename
echo Input "2" to RENAME as DLC Number
echo Input "3" to keep basename and ADD DLC NUMBER AS TAG
echo.
ECHO *********************************************
echo Or Input "b" to return to ADD  KEEP DLC NAMES
echo Or Input "0" to return to the list options
ECHO *********************************************
echo.
set /p bs="Enter your choice: "
set bs=%bs:"=%
set "dlcrname=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice3
if /i "%bs%"=="1" set "dlcrname=false"
if /i "%bs%"=="2" set "dlcrname=true"
if /i "%bs%"=="3" set "dlcrname=tag"
if /i "%dlcrname%"=="none" echo WRONG CHOICE
if /i "%dlcrname%"=="none" goto s_rename_wrongchoice4
echo.
cls
call "%nscb_logos%" "program_logo"
set "workers=-threads 1"
for /f "tokens=*" %%f in (lists/list.txt) do (
%pycommand% "%squirrel%" -renf "single" -tfile "%prog_dir%lists/list.txt" -t nsp xci nsx nsz xcz -renm %renmode% -nover %nover% -oaid %oaid% -addl %addlangue% -roma %romaji% -dlcrn %dlcrname% %workers%
if "%workers%" EQU "-threads 1" ( %pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/list.txt" "1" "true" )
if "%workers%" NEQ "-threads 1" ( call :renamecheck )
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:renamecheck
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (lists/list.txt) do (
set /a conta=!conta! + 1
)
if !conta! LEQ 0 ( del lists/list.txt )
endlocal
if not exist "lists/list.txt" goto s_exit_choice
exit /B

:sanitize
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (lists/list.txt) do (
%pycommand% "%squirrel%" -snz "single" -tfile "%prog_dir%lists/list.txt" -t nsp xci nsx nsz xcz
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:romaji
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (lists/list.txt) do (
%pycommand% "%squirrel%" -roma "single" -tfile "%prog_dir%lists/list.txt" -t nsp xci nsx nsz xcz
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice


:filecleantags
cls
call "%nscb_logos%" "program_logo"
for /f "tokens=*" %%f in (lists/list.txt) do (
%pycommand% "%squirrel%" -cltg "single" -tfile "%prog_dir%lists/list.txt" -t nsp xci nsx nsz xcz -tgtype "%tagtype%"
%pycommand% "%squirrel%" --strip_lines "%prog_dir%lists/list.txt" "1" "true"
rem call :contador_NF
)
ECHO ---------------------------------------------------
ECHO *********** ALL FILES WERE PROCESSED! *************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if exist lists/list.txt del lists/list.txt
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

:nsp_manual
rem if "%fatype%" EQU "-fat fat32" goto nsp_manual_fat32
rem set "filename=%name%"
rem set "showname=%orinput%"
if "%zip_restore%" EQU "true" ( call :makezip )
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
call :squirrell

if "%vrename%" EQU "true" call :addtags_from_nsp

if "%vrepack%" EQU "nsp" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt")
if "%vrepack%" EQU "xci" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt")
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt")
if "%vrepack%" EQU "nodelta" ( %pycommand% "%squirrel%" %buffer% --xml_gen "true" -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" --erase_deltas "")
if "%vrepack%" EQU "rebuild" ( %pycommand% "%squirrel%" %buffer% %skdelta% --xml_gen "true" -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" --rebuild_nsp "")
if "%vrepack%" EQU "verify" ( %pycommand% "%squirrel%" %buffer% -vt "%verif%" -tfile "%prog_dir%lists/list.txt" -v "")
if "%vrepack%" EQU "verify" ( goto end_nsp_manual )

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo DONE
call :thumbup
call :delay
goto end_nsp_manual

:nsp_manual_fat32
CD /d "%prog_dir%"
set "filename=%name%"
set "showname=%orinput%"
call :processing_message

if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell

if "%vrepack%" EQU "zip" ( goto nsp_just_zip )

%pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"

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
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo DONE
call :thumbup
call :delay
goto end_nsp_manual

:end_nsp_manual
exit /B

:xci_manual
rem if "%fatype%" EQU "-fat fat32" goto xci_manual_fat32
::FOR XCI FILES
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"

set "filename=%name%"
set "showname=%orinput%"

if "%vrepack%" EQU "nsp" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt")
if "%vrepack%" EQU "xci" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt")
if "%vrepack%" EQU "both" ( %pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt")
if "%vrepack%" EQU "xci_supertrimmer" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" -xci_st "%orinput%")
if "%vrepack%" EQU "xci_supertrimmer_keep_upd" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -t "xci" -dc "%orinput%" -tfile "%prog_dir%lists/list.txt" )
if "%vrepack%" EQU "xci_trimmer" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" -xci_tr "%orinput%")
if "%vrepack%" EQU "xci_untrimmer" ( %pycommand% "%squirrel%" %buffer% -o "%w_folder%" -tfile "%prog_dir%lists/list.txt" -xci_untr "%orinput%" )
if "%vrepack%" EQU "verify" ( %pycommand% "%squirrel%" %buffer% -vt "%verif%" -tfile "%prog_dir%lists/list.txt" -v "")
if "%vrepack%" EQU "verify" ( goto end_xci_manual )

if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo DONE
call :thumbup
call :delay
goto end_xci_manual

:xci_manual_fat32
CD /d "%prog_dir%"
::FOR XCI FILES
cls
if "%vrepack%" EQU "zip" ( goto end_xci_manual )
set "filename=%name%"
call "%nscb_logos%" "program_logo"
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo ------------------------------------
echo Extracting secure partition from xci
echo ------------------------------------
%pycommand% "%squirrel%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
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
move  "%w_folder%\*.xc*"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%squirrel%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo DONE
call :thumbup
call :delay
goto end_xci_manual

:end_xci_manual
exit /B

:contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (lists/list.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo STILL !conta! FILES TO PROCESS
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B