@echo off
setlocal enabledelayedexpansion
color 03

::XCI_Builder v0.7 by julesontheroad::
::A batch file made to automate nsp to xci files conversion via hacbuild
::XCI_Builder serves as a workflow helper for hacbuild, hactool and nspbuild
::Just drag and drop. Drag a nsp file into XCI_Builder .bat and it'll take care of everything
::hacbuild made by LucaFraga https://github.com/LucaFraga/hacbuild
::hactool made by SciresM https://github.com/SciresM/hactool
::nspBuild made by CVFireDragon https://github.com/CVFireDragon/nspBuild

::Requirements at least NETFramework=v4.5.2
::hacbuild  needs python 2/3 installed in the system 
::nspBuild needs python 2/3 installed in the system 

::Thx to my friends from elotrolado.net and gbatemp

::Set options preset
::OPTION 1 - "preservemanual"
::In case the nsp have a manual nca it will be saved to output folder
::Don't install it as it will cause issues in your switch, it's meant for and
::xci debuilder that will be able to restore nsp to original conditions
::by default=0
::OPTION 2 - "delete_brack_tags"
::Delete bracket tags like [trimmed] by default 1
::OPTION 3 - "delete_pa_tags"
::Delete parenthesis tags like (USA) by default 0, if activated it may also erase [] tags
set /a preservemanual=0
set /a delete_brack_tags=1
set /a delete_pa_tags=0


CD /d "%~dp0"
if not exist "ztools" goto iztools
::check for keys.txt
if not exist "ztools\keys.txt" echo Missing file "KEYS.txt" or "keys.txt!"
echo.
if not exist "ztools\keys.txt" pause
if not exist "ztools\keys.txt" exit
goto startpr

:iztools
CD /d ".."
if not exist "ztools\keys.txt" echo Missing file "KEYS.txt" or "keys.txt!"
echo.
if not exist "ztools\keys.txt" pause
if not exist "ztools\keys.txt" exit
goto startpr

:startpr
if %f_replace%=="true" ( set org_out="folder")
if %fold_xcib%=="false" ( set root_outxf=output_xcib)
if not %fold_xcib%=="false" ( set root_outxf=%fold_xcib%)
set root_outxf=%root_outxf:"=%

set zip=ztools/7za.exe
set opsb=%2
set z_preserve=%3
set org_out=%4
::echo %zpreserve% >zpreserve.txt
::echo %opsb% >opsb.txt
if %opsb%=="startbuilding" ( goto startbuilding )

::Set working folder and file
set file=%~n1
FOR %%i IN ("%file%") DO (
set filename=%%~ni
)
cls

if "%~x1"==".nsp" (goto nsp)
if "%~x1"==".xci" (goto end)
goto end 
ECHO -------------------------------------------
ECHO ====== XCI_BUILDER BY JULESONTHEROAD ====== 
ECHO -------------------------------------------
ECHO "             VERSION 0.7                 "
ECHO more in: https://github.com/julesontheroad/
echo.
ECHO ............
ECHO INSTRUCTIONS
ECHO ............
echo.
echo This program works dragging an nsp file over it's bat file
echo.
echo It also works with XCI_Builder.bat "filename.nsp" over the command line
echo.
echo It's function is to convert nsp files to xci files
echo.
echo.Remember, you'll need to install the small [lc].nsp to get your .xci working in SX OS
echo.
echo.You can install this less than 1mb file with SX OS custom installer
echo.
echo.XCI_Builder's author it's not responsibleof any problems it may derive in your system
echo.
pause
exit

:nsp
@echo off
setlocal enabledelayedexpansion
if exist "nspDecrypted\" rmdir /s /q "nspDecrypted\"
MD nspDecrypted

:: If activated remove identifiers [] or () in filename.
if exist nspDecrypted\*.txt del nspDecrypted\*.txt
echo %filename%>nspDecrypted\fname.txt

if !delete_brack_tags! EQU 1 goto deletebrackets
goto notdeletebrackets
:deletebrackets
for /f "tokens=1* delims=[" %%a in (nspDecrypted\fname.txt) do (
    set filename=%%a)
echo %filename%>nspDecrypted\fname.txt
:notdeletebrackets
if !delete_pa_tags! EQU 1 goto deleteparenthesis
goto notdeleteparenthesis
:deleteparenthesis
for /f "tokens=1* delims=(" %%a in (nspDecrypted\fname.txt) do (
    set filename=%%a)
echo %filename%>nspDecrypted\fname.txt
:notdeleteparenthesis
if exist nspDecrypted\fname.txt del nspDecrypted\fname.txt

::I also wanted to remove_(
set filename=%filename:_= %

ECHO -------------------------------------------
ECHO ====== XCI_BUILDER BY JULESONTHEROAD ====== 
ECHO -------------------------------------------
ECHO "             VERSION 0.7                 "
ECHO more in: https://github.com/julesontheroad/
PING -n 2 127.0.0.1 >NUL 2>&1
echo STARTING PROCESS... 
echo PROCESSING  !filename!
echo Please wait till window closes
echo Depending on file size it can take a little
PING -n 2 127.0.0.1 >NUL 2>&1

if exist "%root_outxf%\!filename!" RD /s /q "%root_outxf%\!filename!" >NUL 2>&1
set ofolder=%filename%
::Extract nsp to rawsecure
echo ----------------------------------------------------
echo Extracting nsp file with hactool by SciresM
echo ----------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t pfs0 --pfs0dir=nspDecrypted\rawsecure "%~1" >NUL 2>&1
echo DONE
:startbuilding
set ofolder=%filename%
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
if exist nspDecrypted\fname.txt del nspDecrypted\fname.txt

set p_folder=%~dp0 
set p_folder=%p_folder:ztools\ =%

if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawsecure\*.jpg" ) >NUL 2>&1
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawsecure\*.tik" ) >NUL 2>&1
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawsecure\*.xml" ) >NUL 2>&1
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawsecure\*.cert" ) >NUL 2>&1
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawsecure\*.jpg" ) >NUL 2>&1

::Delete .jpg files if BBB dump
if exist nspDecrypted\rawsecure\*.jpg del nspDecrypted\rawsecure\*.jpg >NUL 2>&1
::List .nca files in directory
dir nspDecrypted\rawsecure\*.nca > nspDecrypted\lisfiles.txt
FINDSTR /I ".nca" "nspDecrypted\lisfiles.txt">nspDecrypted\nca_list.txt
del nspDecrypted\lisfiles.txt
set /a nca_number=0
for /f %%a in (nspDecrypted\nca_list.txt) do (
    set /a nca_number=!nca_number! + 1
)
::echo !nca_number!>nspDecrypted\nca_number.txt
::a nsp doesn't need .xml files to work. If it have them it will make our life easier
if exist "nspDecrypted\rawsecure\*.cnmt.xml" goto nsp_proper
goto nsp_notproper

:nsp_proper
::If we only have 4 nca files we don't have a manual
if !nca_number! LEQ 4 goto nsp_proper_nm
::Process for nsp with manual
set meta_xml=nspDecrypted\rawsecure\*.cnmt.xml

::Get a list of id's
FINDSTR /N /I "<id>" %meta_xml%>nspDecrypted\id.txt

::Find the html document (manual)
FINDSTR /N "HtmlDocument" %meta_xml%>nspDecrypted\ishtmldoc.txt
for /f "tokens=2* delims=: " %%a in (nspDecrypted\ishtmldoc.txt) do (
set html_pos=%%a)
::echo !html_pos!>nspDecrypted\html_pos.txt
set /a html_id_pos=!html_pos!+1
::echo %html_id_pos%>nspDecrypted\html_nca_id__pos.txt

::Set the filename for the manual nca
FINDSTR /N "%html_id_pos%:" nspDecrypted\id.txt>nspDecrypted\ishtml_id.txt
for /f "tokens=3* delims=<>" %%a in (nspDecrypted\ishtml_id.txt) do (
set myhtmlnca=%%a.nca)

::If we don't want to preserve the manual erase it
::If we want to preserve it move it out of rawsecure
::echo %myhtmlnca%>nspDecrypted\myhtmlnca.txt
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%nspDecrypted\rawsecure\%myhtmlnca%" ) >NUL 2>&1
del "nspDecrypted\rawsecure\%myhtmlnca%"
::echo %myhtmlnca%>nspDecrypted\myhtmlnca.txt
set filename=!filename![nm]

:nsp_proper_nm
::Process for nsp without manual or next step if we have a manual
set meta_xml=nspDecrypted\rawsecure\*.cnmt.xml
if exist nspDecrypted\id.txt del nspDecrypted\id.txt

FINDSTR /N /I "<id>" %meta_xml%>nspDecrypted\id.txt

::Identify the control nca and set it in a variable for next steps

FINDSTR /N "Control" %meta_xml%>nspDecrypted\iscontrolnca.txt
for /f "tokens=2* delims=: " %%a in (nspDecrypted\iscontrolnca.txt) do (
set control_pos=%%a)
echo !control_pos!>nspDecrypted\control_pos.txt
set /a control_id_pos=!control_pos!+1
::echo %control_id_pos%>nspDecrypted\control_id_pos.txt
FINDSTR /N "%control_id_pos%:" nspDecrypted\id.txt>nspDecrypted\iscrl_id.txt
for /f "tokens=3* delims=<>" %%a in (nspDecrypted\iscrl_id.txt) do (
set myctrlnca=%%a.nca)
echo %myctrlnca%>nspDecrypted\myctrlnca.txt

::Go and make a license .nsp
goto :lcnsp

::If the nsp doesn't have a .xml file follow a guessing approach
::In this portion we'll identify the manual nca files via hactool
::Hactool will recognize 2 of them as manual when one is actually legal
::We'll do a supposition to identify each
:nsp_notproper
set /a c_gamenca=1
set mycheck=Manual
set mycheck2=Control

for /f "tokens=4* delims= " %%a in (nspDecrypted\nca_list.txt) do (
echo %%a>>nspDecrypted\nca_list_helper.txt)
del nspDecrypted\nca_list.txt

if !nca_number! LEQ 4 goto nsp_notproper_nm

:nsp_notproper_man
set gstring=
if !c_gamenca! EQU 6 ( goto nsp_notproper_man2 )
if !c_gamenca! EQU 1 ( set gstring=,2,3,4,5, )
if !c_gamenca! EQU 2 ( set gstring=,1,3,4,5, )
if !c_gamenca! EQU 3 ( set gstring=,1,2,4,5, )
if !c_gamenca! EQU 4 ( set gstring=,1,2,3,5, )
if !c_gamenca! EQU 5 ( set gstring=,1,2,3,4, )

Set "skip=%gstring%"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<nspDecrypted\nca_list_helper.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>nspDecrypted\ncatocheck.txt

for /f %%a in (nspDecrypted\ncatocheck.txt) do (
    set ncatocheck=%%a
)
"ztools\hactool.exe" -k "ztools\keys.txt" -t nca -i "nspDecrypted\rawsecure\%ncatocheck%" >"nspDecrypted\nca_data.txt"

FINDSTR "Type" nspDecrypted\nca_data.txt >nspDecrypted\nca_helper.txt
for /f "tokens=3* delims=: " %%a in (nspDecrypted\nca_helper.txt) do (
echo %%a>>nspDecrypted\nca_helper2.txt)
Set "skip=,2,3,"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<nspDecrypted\nca_helper2.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>nspDecrypted\nca_type.txt
for /f %%a in (nspDecrypted\nca_type.txt) do (
    set nca_type=%%a
)
if %nca_type% EQU %mycheck% ( echo %ncatocheck%>>nspDecrypted\manual_list.txt )
if %nca_type% EQU %mycheck2% ( set myctrlnca=%ncatocheck% )
::echo %myctrlnca%> nspDecrypted\myctrlnca.txt
set /a c_gamenca+=1
del nspDecrypted\ncatocheck.txt
del nspDecrypted\nca_data.txt
del nspDecrypted\nca_helper.txt
del nspDecrypted\nca_helper2.txt
del nspDecrypted\nca_type.txt
goto nsp_notproper_man

:nsp_notproper_man2
::We'll get the route of the alleged "manual nca" 
set crlt=0
for /f %%a in (nspDecrypted\manual_list.txt) do (
    set /a crlt=!crlt! + 1
    set tmanual!crlt!=%%a
)

::del manual_list.txt

::Set complete route
set f_tmanual1="nspDecrypted\rawsecure\%tmanual1%"
set f_tmanual2="nspDecrypted\rawsecure\%tmanual2%"

::Get size of both nca
for /f "usebackq" %%A in ('%f_tmanual1%') do set size_tm1=%%~zA
for /f "usebackq" %%A in ('%f_tmanual2%') do set size_tm2=%%~zA

echo !size_tm1!>nspDecrypted\size_tm1.txt
echo !size_tm2!>nspDecrypted\size_tm2.txt

::Ok, here's some technical explanation
::Normaly legas is like 130-190kb
::Manual can be some mb (offline manual) or less size than legal (online manual)
::I'm assuming the limit for legal sise is a little over 300kb. Can be altered if needed

if !size_tm1! GTR 3400000 ( goto case1 )
if !size_tm1! GTR 3400000 ( goto case2 )
if !size_tm1! GTR !size_tm2! ( goto case3 )
if !size_tm2! GTR !size_tm1!( goto case4 )
goto nomanual

:case1
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%%f_tmanual1%" ) >NUL 2>&1
del "%f_tmanual1%"
set filename=!filename![nm]
goto lcnsp
:case2
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%%f_tmanual2%" ) >NUL 2>&1
del "%f_tmanual2%"
set filename=!filename![nm]
goto lcnsp
:case3
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%%f_tmanual2%" ) >NUL 2>&1
del "%f_tmanual2%"
set filename=!filename![nm]
goto lcnsp
:case4
if %z_preserve%=="true" ( "%p_folder%%zip%" a "%p_folder%nspDecrypted\%filename%[del].zip" "%p_folder%%f_tmanual1%" ) >NUL 2>&1
del "%f_tmanual1%"
set filename=!filename![nm]
goto lcnsp

::Same aproach as before but only to identify the control .nca to make the license
:nsp_notproper_nm
set gstring=
if !c_gamenca! EQU 5 ( goto lcnsp )
if !c_gamenca! EQU 1 ( set gstring=,2,3,4, )
if !c_gamenca! EQU 2 ( set gstring=,1,3,4, )
if !c_gamenca! EQU 3 ( set gstring=,1,2,4, )
if !c_gamenca! EQU 4 ( set gstring=,1,2,3, )

Set "skip=%gstring%"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<nspDecrypted\nca_list_helper.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>nspDecrypted\ncatocheck.txt

for /f %%a in (nspDecrypted\ncatocheck.txt) do (
    set ncatocheck=%%a
)
"ztools\hactool.exe" -k "ztools\keys.txt" -t nca -i "nspDecrypted\rawsecure\%ncatocheck%" >"nspDecrypted\nca_data.txt"
FINDSTR "Type" nspDecrypted\nca_data.txt >nspDecrypted\nca_helper.txt
for /f "tokens=3* delims=: " %%a in (nspDecrypted\nca_helper.txt) do (
echo %%a>>nspDecrypted\nca_helper2.txt)
Set "skip=,2,3,"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<nspDecrypted\nca_helper2.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>nspDecrypted\nca_type.txt
for /f %%a in (nspDecrypted\nca_type.txt) do (
    set nca_type=%%a
)

if %nca_type% EQU %mycheck2% ( set myctrlnca=%ncatocheck% )
::echo %myctrlnca%> nspDecrypted\myctrlnca.txt
set /a c_gamenca+=1
del nspDecrypted\ncatocheck.txt
del nspDecrypted\nca_data.txt
del nspDecrypted\nca_helper.txt
del nspDecrypted\nca_helper2.txt
del nspDecrypted\nca_type.txt
goto nsp_notproper_nm

:lcnsp
del nspDecrypted\*.txt
if exist "nspDecrypted\licencia" RD /S /Q "nspDecrypted\licencia" >NUL 2>&1
MD nspDecrypted\licencia
echo f | xcopy /f /y "nspDecrypted\rawsecure\%myctrlnca%" "nspDecrypted\licencia\"  >NUL 2>&1
move "nspDecrypted\rawsecure\*.cnmt.xml"  "nspDecrypted\licencia"  >NUL 2>&1
move "nspDecrypted\rawsecure\*.tik"  "nspDecrypted\licencia"  >NUL 2>&1
move "nspDecrypted\rawsecure\*.cert"  "nspDecrypted\licencia"  >NUL 2>&1

dir "nspDecrypted\licencia" /b  > "nspDecrypted\fileslist.txt"
set list=0
for /F "tokens=*" %%A in (nspDecrypted\fileslist.txt) do (
    SET /A list=!list! + 1
    set varlist!list!=%%A
) >NUL 2>&1
set varlist >NUL 2>&1

if exist nspDecrypted\licencia\*.cnmt.xml goto nspwithxml
if exist nspDecrypted\licencia\*.tik goto nspwithoutxml
goto createxci
:nspwithxml
if not exist nspDecrypted\licencia\*.tik goto createxci
echo ----------------------------------------------------
echo Building license nsp with "nspbuild" by CVFireDragon
echo ----------------------------------------------------
py -3 "ztools\nspbuild.py" "nspDecrypted\!ofolder![lc].nsp" "nspDecrypted\licencia\%varlist1%" "nspDecrypted\licencia\%varlist2%" "nspDecrypted\licencia\%varlist3%" "nspDecrypted\licencia\%varlist4%"  >NUL 2>&1
echo DONE
del nspDecrypted\fileslist.txt
rmdir /s /q "nspDecrypted\licencia"
goto createxci
:nspwithoutxml
echo ----------------------------------------------------
echo Building license nsp with "nspbuild" by CVFireDragon
echo ----------------------------------------------------
py -3 "ztools\nspbuild.py" "nspDecrypted\!ofolder![lc].nsp" "nspDecrypted\licencia\%varlist1%" "nspDecrypted\licencia\%varlist2%" "nspDecrypted\licencia\%varlist3%"  >NUL 2>&1
echo DONE
del nspDecrypted\fileslist.txt
rmdir /s /q "nspDecrypted\licencia"
goto createxci

::Pass everything to hacbuild
:createxci
if exist nspDecrypted\rawsecure\*.tik del nspDecrypted\rawsecure\*.tik >NUL 2>&1
if exist nspDecrypted\rawsecure\*.xml del nspDecrypted\rawsecure\*.xml >NUL 2>&1
if exist nspDecrypted\rawsecure\*.cert del nspDecrypted\rawsecure\*.cert >NUL 2>&1
if exist nspDecrypted\*.txt del nspDecrypted\*.txt >NUL 2>&1
if exist nspDecrypted\rawsecure\*.jpg del nspDecrypted\rawsecure\*.jpg >NUL 2>&1
if exist nspDecrypted\secure RD /S /Q nspDecrypted\secure\ >NUL 2>&1
MD nspDecrypted\secure
echo f | xcopy /f /y "zconfig\game_info_preset.ini" "nspDecrypted\"  >NUL 2>&1
RENAME "nspDecrypted\game_info_preset.ini" "game_info.ini"
move  "nspDecrypted\rawsecure\*.nca"  "nspDecrypted\secure\"  >NUL 2>&1
RD /S /Q nspDecrypted\rawsecure\
MD nspDecrypted\normal
MD nspDecrypted\update
echo ----------------------------------------------
echo Building xci file with hacbuild by LucaFraga
echo ----------------------------------------------
ECHO NOTE:
echo With files bigger than 4Gb it'll take more time proportionally than with smaller files.
echo Also you'll need to have at least double the amount of free disk space than file's size.
echo IF YOU DON'T SEE "DONE" HACBUILD IS STILL AT WORK.
ECHO ........................................................................................
"ztools\hacbuild.exe" xci_auto "nspDecrypted"  "nspDecrypted\!filename![xcib].xci"  >NUL 2>&1
echo DONE
RD /S /Q "nspDecrypted\secure"
RD /S /Q "nspDecrypted\normal"
RD /S /Q "nspDecrypted\update"
del "nspDecrypted\game_info.ini"
if not exist "%root_outxf%" MD "%root_outxf%" >NUL 2>&1
if %org_out%=="folder" goto org_xci_f
move  "nspDecrypted\*.*"  "%root_outxf%\"  >NUL 2>&1
RD /S /Q "nspDecrypted"
if %opsb%=="startbuilding" ( goto end )
if %opsb%=="fallback" ( goto end )

:org_xci_f
MD "%root_outxf%\!ofolder!" >NUL 2>&1
move  "nspDecrypted\*.*"  "%root_outxf%\!ofolder!"  >NUL 2>&1
RD /S /Q "nspDecrypted"
if %opsb%=="startbuilding" ( goto end )
if %opsb%=="fallback" ( goto end )

echo ----------------------------------------------
echo Processed !filename!
echo Your files should be in the %root_outxf% folder
echo ----------------------------------------------
PING -n 4 127.0.0.1 >NUL 2>&1
echo    /@
echo    \ \
echo  ___\ \
echo (__O)  \
echo (____@)  \
echo (____@)   \
echo (__o)_    \
echo       \    \

:end
PING -n 2 127.0.0.1 >NUL 2>&1

















