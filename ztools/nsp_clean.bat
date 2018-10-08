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
::OPT1 set nut.py route
::OPT2 Set auto mode output format from option 2 of option file
::     nsp > output as nsp
::     xci > output as xci
::     both > output as both nsp and xci
:set_options1
set i_folder=%~dp0 
set i_folder=%i_folder:ztools\ =%
::echo %i_folder%>i_folder.txt
set zip=ztools/7za.exe
if exist "%i_folder%zconfig\nsp_cleaner_options.cmd" goto set_options2
set NUT_ROUTE=ztools\nut_RTR.py
set z_preserve="true"
set vrepack="nsp"
if exist %NUT_ROUTE% goto startpr
exit

:set_options2
call "zconfig/nsp_cleaner_options.cmd"
set pycommand=%pycommand:"=%
if exist %NUT_ROUTE% goto startpr
set NUT_ROUTE=ztools\nut_RTR.py
if exist %NUT_ROUTE% goto startpr
exit


:startpr
::Set working folder and file
set file=%~n1
if %f_replace%=="true" ( set org_out="folder")
if %fold_clnsp%=="false" ( set root_outf=o_clean_nsp)
if not %fold_clnsp%=="false" ( set root_outf=%fold_clnsp%)
set root_outf=%root_outf:"=%

FOR %%i IN ("%file%") DO (
set filename=%%~ni
)
::set filename=%filename:_= %
cls
::Included other variable for manual to fix issues
if %2=="manual" set vrepack=%3

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
ECHO                                      VERSION 0.41               
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
ECHO                                      VERSION 0.41               
ECHO -------------------------------------------------------------------------------------                   
ECHO check xci_batch_builder at: https://github.com/julesontheroad/
ECHO and check blawar's NUT at:  https://github.com/blawar/nut 
ECHO -------------------------------------------------------------------------------------

if exist "nspDecrypted\" rmdir /s /q "nspDecrypted\"  >NUL 2>&1
if exist "%root_outf%\!filename!.nsp" del "%root_outf%\!filename!.nsp"  >NUL 2>&1
set myfile=%~dp0\nspDecrypted\%filename%.nsp
MD nspDecrypted

%pycommand% "%NUT_ROUTE%" --nsptitleid "%~1" >nspDecrypted\nsptitleid.txt
set /p titleid=<nspDecrypted\nsptitleid.txt
echo [%titleid%]>nspDecrypted\nsptitleid.txt

FINDSTR /L 000] nspDecrypted\nsptitleid.txt >nspDecrypted\isbasef.txt
set /p base_nsp=<nspDecrypted\isbasef.txt

FINDSTR /L 800] nspDecrypted\nsptitleid.txt >nspDecrypted\isupdatef.txt
set /p update_nsp=<nspDecrypted\isupdatef.txt

del nspDecrypted\isupdatef.txt
del nspDecrypted\isbasef.txt

if [%titleid%] EQU !base_nsp! goto allgood
if [%titleid%] EQU !update_nsp! goto itwasupdate1

:itwasupdate1
if %vrepack%=="xci" goto itwasupdate2
if %vrepack%=="both" ( set vrepack=nsp )
goto allgood
::echo %vrepack% > vrepack.txt
:itwasupdate2
if %xnsp_ifnotgame%=="true" ( set vrepack=nsp )
if %xnsp_ifnotgame%=="false" ( goto itwasupdate3 )

:allgood

ECHO -------------------------------------------------------------------------------------
echo Copy %originalname% to nspDecrypted
ECHO -------------------------------------------------------------------------------------
echo f | xcopy /f /y "%~1" "nspDecrypted\"   >NUL 2>&1
echo DONE
if exist "%myinput%" ren "%myinput%" "%originalname%"
set ofolder=%filename%
::In case these tags are at the beginning of the file
set ofolder=%ofolder:[DLC]=%
set ofolder=%ofolder:[UPD]=%
echo %ofolder%>nspDecrypted\fname.txt
::deletebrackets
for /f "tokens=1* delims=[" %%a in (nspDecrypted\fname.txt) do (
    set ofolder=%%a)
echo %ofolder%>nspDecrypted\fname.txt
::deleteparenthesis
for /f "tokens=1* delims=(" %%a in (nspDecrypted\fname.txt) do (
    set ofolder=%%a)
echo %ofolder%>nspDecrypted\fname.txt
::I also wanted to remove_(
set ofolder=%ofolder:_= %
set onlyinfo_name=%ofolder%
if exist nspDecrypted\fname.txt del nspDecrypted\fname.txt

ECHO -------------------------------------------------------------------------------------
echo Cleaning nsp with nut.py
ECHO -------------------------------------------------------------------------------------
set p_folder=%~dp0 
set p_folder=%p_folder:ztools\ =%

::NAME REFORMING SCRIPT
%pycommand% "%NUT_ROUTE%" --nsptitleid "%p_folder%nspDecrypted\%filename%.nsp" >nspDecrypted\nsptitleid.txt
set /p titleid=<nspDecrypted\nsptitleid.txt
echo [%titleid%]>nspDecrypted\nsptitleid.txt

FINDSTR /L 000] nspDecrypted\nsptitleid.txt >nspDecrypted\isbasef.txt
set /p base_nsp=<nspDecrypted\isbasef.txt

FINDSTR /L 800] nspDecrypted\nsptitleid.txt >nspDecrypted\isupdatef.txt
set /p update_nsp=<nspDecrypted\isupdatef.txt
del nspDecrypted\nsptitleid.txt
set ttag=[DLC]
if [%titleid%] EQU !base_nsp! set ttag=[V0]
if [%titleid%] EQU !update_nsp! set ttag=[UPD]
del nspDecrypted\isupdatef.txt
del nspDecrypted\isbasef.txt

ren "%p_folder%nspDecrypted\%filename%.nsp" "%ofolder% [%titleid%] %ttag%.nsp"
set filenametemp=%ofolder% [%titleid%] %ttag%

%pycommand% "%NUT_ROUTE%" --remove-title-rights "%p_folder%nspDecrypted\%filenametemp%.nsp" >nspDecrypted\assist.txt
FINDSTR /N "Mismatched" nspDecrypted\assist.txt > nspDecrypted\l_check.txt
FINDSTR /N "name needs to contain [titleId]" nspDecrypted\assist.txt >> nspDecrypted\l_check.txt
for /f "tokens=1* delims=:" %%a in (nspDecrypted\l_check.txt) do set l_check=%%a
del nspDecrypted\l_check.txt >NUL 2>&1
if !l_check! GTR 0 goto an_error
::more +8 "nspDecrypted\assist.txt" >"nspDecrypted\assist.txt.new"
::move /y "nspDecrypted\assist.txt.new" "nspDecrypted\assist.txt" >nul

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
::set filename=%filenametemp%
ren "%p_folder%nspDecrypted\%filenametemp%.nsp" "%filename%.nsp"
ECHO -------------------------------------------------------------------------------------
echo Extracting nsp file with hactool by SciresM
ECHO -------------------------------------------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t pfs0 --pfs0dir=nspDecrypted\rawnsp "nspDecrypted\%filename%.nsp" >NUL 2>&1
echo DONE  
ECHO -------------------------------------------------------------------------------------
if not %z_preserve%=="true" echo Removing ticket and cert
if %z_preserve%=="true"  echo Removing ticket and cert and ziping them
ECHO -------------------------------------------------------------------------------------
del "nspDecrypted\%filename%.nsp"

if %safe_var% EQU "agro" call :get_nsp_data
if not %safe_var% EQU "agro" ( if %ncap_rname% EQU "true" call :get_nsp_data )
if not %safe_var% EQU "agro" ( if %ncap_rname% EQU "oinfo" call :get_nsp_data )

::echo %filename%>nspDecrypted\filename.txt
::echo %ofolder%>nspDecrypted\ofolder.txt


if %z_preserve%=="true" ( "%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawnsp\*.tik" ) >NUL 2>&1
del "nspDecrypted\rawnsp\*.tik"
if %z_preserve%=="true" ( "%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawnsp\*.cert" ) >NUL 2>&1
del "nspDecrypted\rawnsp\*.cert"
if %z_preserve%=="true" ( "%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawnsp\*.jpg" ) >NUL 2>&1
if exist nspDecrypted\rawnsp\*.jpg del nspDecrypted\*.jpg


echo DONE  

if %vrepack%=="nsp" ( goto nsp_repack )
if %vrepack%=="xci" ( goto xci_repack )

:nsp_repack
ECHO -------------------------------------------------------------------------------------
echo Repacking as nsp with nspbuild by CVFireDragon
ECHO -------------------------------------------------------------------------------------
set ruta_nspb=ztools\nspBuild.py
dir "nspDecrypted\rawnsp\*" /b  > "nspDecrypted\nsp_fileslist.txt"
set row=
for /f %%x in (nspDecrypted\nsp_fileslist.txt) do set row="nspDecrypted\rawnsp\%%x" !row!
%pycommand% %ruta_nspb% "nspDecrypted\%filename%[rr].nsp" %row% >NUL 2>&1
echo DONE 
if not exist %root_outf% MD %root_outf%

if %org_out%=="folder" goto org_nsp_f
move  "nspDecrypted\*.nsp"  "%root_outf%"  >NUL 2>&1
echo f | xcopy /f /y "nspDecrypted\*.zip" "%root_outf%" >NUL 2>&1
if %vrepack%=="both" ( goto xci_repack )
goto final

:org_nsp_f
MD "%root_outf%\!ofolder!" >NUL 2>&1
move  "nspDecrypted\*.nsp"  "%root_outf%\!ofolder!"  >NUL 2>&1
echo f | xcopy /f /y "nspDecrypted\*.zip" "%root_outf%\!ofolder!" >NUL 2>&1
if %vrepack%=="both" ( goto xci_repack )
goto final

:xci_repack
del nspDecrypted\*.txt >NUL 2>&1
MD nspDecrypted\rawsecure\ >NUL 2>&1
move  "nspDecrypted\rawnsp\*"  "nspDecrypted\rawsecure\" >NUL 2>&1
RD /S /Q nspDecrypted\rawnsp\
set rutaXCIB=XCI_Builder.bat
if not exist XCI_Builder.bat ( set rutaXCIB=ztools\XCI_Builder.bat )
set op=startbuilding
set z_preserve=%z_preserve:"=%
set org_out=%org_out:"=%
if exist "%orinput%" ( call %rutaXCIB% "%orinput%" "%op%" "%z_preserve%" "%org_out%" )
if not exist "%orinput%" ( call %rutaXCIB% "%~1" "%op%" "%z_preserve%" "%org_out%" )
goto final

:an_error
ren "%p_folder%nspDecrypted\%filenametemp%.nsp" "%filename%.nsp"
echo Couldn't Remove title rights from file %filename%
echo %DATE%. %TIME%>>log.txt
echo Error removing title rights from %filename%>>log.txt
echo Initiating fallback alternative
if %vrepack%=="xci" ( goto fallback )
RD /S /Q nspDecrypted\ >NUL 2>&1
goto final

:fallback
set rutaXCIB=XCI_Builder.bat
if not exist XCI_Builder.bat ( set rutaXCIB=ztools\XCI_Builder.bat )
set op=fallback
if exist "%orinput%" ( call %rutaXCIB% "%orinput%" "%op%" )
if not exist "%orinput%" (  call %rutaXCIB% "%~1" "%op%" )
goto final

:final
RD /S /Q nspDecrypted\rawnsp\ >NUL 2>&1
RD /S /Q nspDecrypted\ >NUL 2>&1
echo Cleaned !filename!.nsp
if %vrepack%=="nsp" echo and repacked it as nsp
if %vrepack%=="xci" echo and repacked it as xci
if %vrepack%=="both" echo and repacked it as nsp and xci
if %f_replace%=="true" goto replace_orig
goto thumbup
:replace_orig
del "%orinput%" >NUL 2>&1
set ofolder=%ofolder%\
set ofolder=%ofolder: \=\%
move  "%root_outf%\!ofolder!*.*"  "%~dp1"  >NUL 2>&1
RD /S /Q "%root_outf%\!ofolder!" >NUL 2>&1

:thumbup
echo.
echo Your files should be in the respective output folders
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
goto end

::SUBROUTINES

:get_nsp_data
ECHO -------------------------------------------------------------------------------------
echo Getting data from control and meta nca files
ECHO -------------------------------------------------------------------------------------
dir "nspDecrypted\rawnsp\*.nca" /b  > "nspDecrypted\nca_list.txt"

set p_folder=%~dp0 
set p_folder=%p_folder:ztools\ =%

for /f "tokens=*" %%f in ( nspDecrypted\nca_list.txt ) do (
%pycommand% "%p_folder%%NUT_ROUTE%" --ncatype "%p_folder%nspDecrypted\rawnsp\%%f" >nspDecrypted\ncatype.txt
set /p nca_type=<nspDecrypted\ncatype.txt 
if "!nca_type!" EQU "Content.CONTROL" set cont_nca=%%f 
if "!nca_type!" EQU "Content.META" set meta_nca=%%f 
)

del nspDecrypted\nca_list.txt
del nspDecrypted\ncatype.txt 
MD nspDecrypted\control
::echo %cont_nca%>nspDecrypted\control.txt
::echo %meta_nca%>nspDecrypted\meta.txt

"ztools\hactool.exe" -k "ztools\keys.txt" -t nca --exefsdir=nspDecrypted\control --romfsdir=nspDecrypted\control "nspDecrypted\rawnsp\%cont_nca%" >NUL 2>&1
del nspDecrypted\control\*.dat >NUL 2>&1
"ztools\nstool.exe" -k "ztools\keys.txt" --listfs "nspDecrypted\control\control.nacp" >nspDecrypted\nacp.txt
FINDSTR /L Name "nspDecrypted\nacp.txt" >nspDecrypted\gamename.txt
del nspDecrypted\nacp.txt
set crlt=0
for /f "tokens=1* delims=: " %%a in ( nspDecrypted\gamename.txt ) do (
    set /a crlt=!crlt! + 1
    set gamename!crlt!=%%b
)
set gamename=!gamename1!
del nspDecrypted\gamename.txt
::echo !gamename!>nspDecrypted\gamename2.txt

call "ztools/safename.bat" "!gamename!" "control_name"

set gamename=%mygamename%
::echo %mygamename%>nspDecrypted\mygamename.txt

set filename=%gamename% [%titleid%] %ttag%
set ofolder=%mygamename%
RD /S /Q nspDecrypted\control

::echo %filename%>nspDecrypted\filename.txt
::echo %ofolder%>nspDecrypted\ofolder.txt

if "%ttag%" EQU "[UPD]" goto check_upd_ver
if "%ttag%" EQU "[DLC]" goto check_upd_ver
goto data_end_check

:check_upd_ver
MD nspDecrypted\meta
"ztools\nstool.exe" -k "ztools\keys.txt" -t nca --part0 "nspDecrypted\meta" "nspDecrypted\rawnsp\%meta_nca%" >NUL 2>&1
dir "nspDecrypted\meta\*.cnmt" /b  > "nspDecrypted\cnmt.txt"
set /p cnmt_file=<nspDecrypted\cnmt.txt 
del nspDecrypted\cnmt.txt
"ztools\nstool.exe" -k "ztools\keys.txt" --listfs "nspDecrypted\meta\%cnmt_file%" >nspDecrypted\metadata.txt
FINDSTR /L " Version:" "nspDecrypted\metadata.txt" >nspDecrypted\gameversion.txt
del nspDecrypted\metadata.txt 
set crlt=0
for /f "tokens=1* delims=: " %%a in ( nspDecrypted\gameversion.txt ) do (
    set /a crlt=!crlt! + 1
    set gameversion!crlt!=%%b
)
del nspDecrypted\gameversion.txt
echo !gameversion1!>nspDecrypted\checkversion.txt
::deleteparenthesis
for /f "tokens=1* delims=(" %%a in (nspDecrypted\checkversion.txt) do (
    set gameversion=%%a)
set gameversion=%gameversion: =%
del nspDecrypted\checkversion.txt
::echo %gameversion%>nspDecrypted\gameversion.txt
RD /S /Q nspDecrypted\meta
set filename=%gamename% [%titleid%] %ttag% [%gameversion%]
::echo %filename%>nspDecrypted\filename.txt


:data_end_check

if not %safe_var% EQU "agro" ( if %ncap_rname% EQU "oinfo" goto only_info )
if %ncap_rname% EQU "true" ( if "%ttag%" EQU "[DLC]" goto only_info )
goto not_oinfo

:only_info
if "%ttag%" EQU "[UPD]" ( set filename=%onlyinfo_name% [%titleid%] %ttag% [%gameversion%] )
if "%ttag%" EQU "[DLC]" ( set filename=%onlyinfo_name% [%titleid%] %ttag% [%gameversion%] )
if "%ttag%" EQU "[V0]" ( set filename=%onlyinfo_name% [%titleid%] %ttag% )
set ofolder=%onlyinfo_name%
exit /B

:not_oinfo
if %safe_var% EQU "agro" ( if "%ttag%" EQU "[DLC]" ( set filename=[%titleid%] %ttag% [%gameversion%] ) )
if %safe_var% EQU "agro" ( if "%ttag%" EQU "[DLC]" ( set ofolder=[%titleid%] ) )
exit /B

::END OF PROGRAM

:itwasupdate3
RD /S /Q nspDecrypted\rawnsp\
RD /S /Q nspDecrypted\
echo **************************************************
echo FILE WASN'T REPACKED AS XCI DUE TO BEING AN UPDATE
echo **************************************************
echo **************************************************
echo if chosen to also repack as nsp the resulting file
echo should be in o_folder.
echo **************************************************

:end
if exist nspDecrypted\ RD /S /Q nspDecrypted\ >NUL 2>&1
PING -n 3 127.0.0.1 >NUL 2>&1
endlocal



