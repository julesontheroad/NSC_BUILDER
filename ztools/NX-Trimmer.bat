@echo off
color 03

::NX-Trimmer v0.4 by julesontheroad::
::A batch file made to automate system updates trimming, game updates trimming and padding reduction via hacbuild
::NX-Trimmer serves as a workflow helper for hacbuild, hactool and nspbuild
::Just drag and drop. Drag a xci file into NX-Trimmer .bat and it'll take care of everything
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
set /a preservemanual=1
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

::Set working folder and file
set file=%~n1
FOR %%i IN ("%file%") DO (
set filename=%%~ni
)

if exist "xciDecrypted" RD /s /q "xciDecrypted"
cls

if "%~x1"==".xci" ( goto xci )
if "%~x1"==".nsp" ( goto end )
goto end 

ECHO ------------------------------------------
ECHO ====== NX-TRIMMER BY JULESONTHEROAD ====== 
ECHO ------------------------------------------
ECHO "            VERSION 0.4                 "
ECHO more in: https://github.com/julesontheroad/
echo.
ECHO ............
ECHO INSTRUCTIONS
ECHO ............
echo.
echo This program works dragging an xci file over it's bat file
echo.
echo It also works with NX-Trimmer.bat "filename.xci" over the command line
echo.
echo It's function is to automate update partition removal and padding reduction via hacbuild
echo.
echo.NX-Trimmer's author it's not responsible of any problems it may derive in your system
echo.
pause
exit

:xci
@echo off
setlocal enabledelayedexpansion

if exist "xciDecrypted" RD /s /q "xciDecrypted" >NUL 2>&1
if not exist game_info MD game_info
if not exist output_nxt MD output_nxt
MD xciDecrypted

if exist "game_info\!filename!.ini" del "game_info\!filename!.ini" >NUL 2>&1

"ztools\hacbuild.exe" read xci "%~f1" >NUL 2>&1


move  "%~dp1\*.ini"  "xciDecrypted\" 
echo f | xcopy /f /y "xciDecrypted\*.ini" "game_info\"
rename xciDecrypted\*.ini ""game_info.ini"

:: If activated remove identifiers [] or () in filename.
if exist xciDecrypted\*.txt del xciDecrypted\*.txt
echo %filename%>xciDecrypted\fname.txt

if !delete_brack_tags! EQU 1 goto deletebrackets
goto notdeletebrackets
:deletebrackets
for /f "tokens=1* delims=[" %%a in (xciDecrypted\fname.txt) do (
    set filename=%%a)
echo %filename%>xciDecrypted\fname.txt
:notdeletebrackets
if !delete_pa_tags! EQU 1 goto deleteparenthesis
goto notdeleteparenthesis
:deleteparenthesis
for /f "tokens=1* delims=(" %%a in (xciDecrypted\fname.txt) do (
    set filename=%%a)
echo %filename%>xciDecrypted\fname.txt
:notdeleteparenthesis
if exist xciDecrypted\fname.txt del xciDecrypted\fname.txt

::I also wanted to remove_(
set filename=%filename:_= %
cls

ECHO ------------------------------------------
ECHO ====== NX-TRIMMER BY JULESONTHEROAD ====== 
ECHO ------------------------------------------
ECHO "            VERSION 0.4                 "
ECHO more in: https://github.com/julesontheroad/
PING -n 2 127.0.0.1 >NUL 2>&1
echo STARTING PROCESS... 
echo PROCESSING  !filename!
echo Please wait till window closes
echo Depending on file size it can take a little
PING -n 2 127.0.0.1 >NUL 2>&1

if exist "output_nxt\!filename!" RD /s /q "output_nxt\!filename!" >NUL 2>&1
::Get partitions table from hactool and format it to get the secure partitions nca in correct order
echo -----------------------------------------------------
echo Getting partition information with hactool by SciresM
echo -----------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t xci -i  "%~1" >xciDecrypted\partitions.txt 
echo DONE

for /f "tokens=2* delims= " %%a in (xciDecrypted\partitions.txt) do (
echo %%a>>xciDecrypted\helper1.txt
)
FINDSTR "secure:/" xciDecrypted\helper1.txt >xciDecrypted\s_order.txt

for /f "tokens=1* delims= " %%a in (xciDecrypted\partitions.txt) do (
echo %%a>>xciDecrypted\helper2.txt
)
FINDSTR "secure:/" xciDecrypted\helper2.txt >>xciDecrypted\s_order.txt

::Secu order is the order of the secure partitions nca
for /f "tokens=2* delims=/ " %%a in (xciDecrypted\s_order.txt) do (
echo %%a>>xciDecrypted\secu_order.txt)

FINDSTR "Number of files:" xciDecrypted\partitions.txt >xciDecrypted\helper3.txt
for /f "tokens=4* delims= " %%a in (xciDecrypted\helper3.txt) do (
echo %%a>>xciDecrypted\helper4.txt
)

Set "skip=,1,2,3,5,"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<xciDecrypted\helper4.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>xciDecrypted\secu_number.txt

::Secu number is the number of the secure partitions nca
for /f %%a in (xciDecrypted\secu_number.txt) do (
    set secu_number=%%a
)
::echo !secu_number!>xciDecrypted\secn.txt

::Clean the folder
del xciDecrypted\helper1.txt
del xciDecrypted\helper2.txt
del xciDecrypted\helper3.txt
del xciDecrypted\helper4.txt
del xciDecrypted\partitions.txt
del xciDecrypted\s_order.txt

::If only 4 nca there's no game and no manual
:: Skip the next steps
if !secu_number! LSS 5 ( goto ognm )

::Get positions of cnmt.nca
FINDSTR  /N "cnmt.nca" xciDecrypted\secu_order.txt >>xciDecrypted\helper1.txt
for /f "tokens=1* delims=:" %%a in (xciDecrypted\helper1.txt) do (
echo %%a>>xciDecrypted\positions.txt)

del xciDecrypted\helper1.txt

::Get position of cnmt.nca in variables
set crlt=0
for /f %%a in (xciDecrypted\positions.txt) do (
    set /a crlt=!crlt! + 1
    set vet!crlt!=%%a
)

::check with echos
::echo !vet1!>xciDecrypted\vet1.txt
::echo !vet2!>xciDecrypted\vet2.txt
::echo !vet3!>xciDecrypted\vet3.txt
::echo !secu_number!>xciDecrypted\secu_number.txt


::Strip game content from rawsecure to move into secure
::Step 1. Get skiplist

set pos1=!vet1!
set pos2=!secu_number!
set string=
:stripgame1 
if !pos1! GTR !pos2! ( goto :stripgame2 ) else (set /a pos1+=1)
set string=%string%,%pos1%
goto :stripgame1 

:stripgame2
set string=%string%,
set skiplist=%string%

::echo %skiplist%>xciDecrypted\skiplist.txt

::Step 2. Strip no game content and save game nca in txt
Set "skip=%skiplist%"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<xciDecrypted\secu_order.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>xciDecrypted\game_nca.txt

::Step 4. Extract secure partition with hactool
echo ------------------------------------------------------------
echo Extracting secure partition from xci with hactool by SciresM
echo ------------------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t xci --securedir=xciDecrypted\rawsecure\ "%~1" >NUL 2>&1
echo DONE
MD "xciDecrypted\secure"

::Step 5. Move game nca to secure
set game_nca_number=0
for /f %%a in (xciDecrypted\game_nca.txt) do (
move  "xciDecrypted\rawsecure\%%a"  "xciDecrypted\secure" >NUL 2>&1
set /a game_nca_number+=1
)
::echo !game_nca_number!>xciDecrypted\game_nca_number.txt

echo f | xcopy /f /y "xciDecrypted\secu_order.txt" "xciDecrypted\content_helper.txt" >NUL 2>&1
set a/ contador=0
set /a pos2=!vet1!-1
::echo %pos2%>xciDecrypted\pos2.txt
set /a pos1=0
set string=
:update_list1
if !pos1! GTR !pos2! ( goto :update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :update_list1 
:update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<xciDecrypted\content_helper.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>xciDecrypted\other_content.txt
::del xciDecrypted\content_helper.txt
::echo %skiplist%>xciDecrypted\skiplist.txt
setlocal EnableDelayedExpansion

::Get number of other content
FINDSTR /R /N "^.*" xciDecrypted\other_content.txt | FIND /C ":">xciDecrypted\ocont_number.txt
for /f %%a in (xciDecrypted\ocont_number.txt) do (
    set ocont_number=%%a
)
::echo !ocont_number!>xciDecrypted\ocont_number2.txt

if %ocont_number% EQU 0 ( goto nocontent )


del xciDecrypted\positions.txt
::Get positions of cnmt.nca
FINDSTR  /N "cnmt.nca" xciDecrypted\other_content.txt >>xciDecrypted\helper1.txt
for /f "tokens=1* delims=:" %%a in (xciDecrypted\helper1.txt) do (
echo %%a>>xciDecrypted\positions.txt)

del xciDecrypted\helper1.txt

::Get position of cnmt.nca in variables
set crlt=0
for /f %%a in (xciDecrypted\positions.txt) do (
    set /a crlt=!crlt! + 1
    set vet!crlt!=%%a
)

::Get position of .cert
FINDSTR  /N ".cert" xciDecrypted\other_content.txt >>xciDecrypted\helper2.txt
for /f "tokens=1* delims=:" %%a in (xciDecrypted\helper2.txt) do (
echo %%a>>xciDecrypted\cert_pos.txt)
del xciDecrypted\helper2.txt

for /f %%a in (xciDecrypted\cert_pos.txt) do (
    set cert_pos=%%a
)

if cert_pos GTR 0 ( goto update_exist )
goto not_update 

:update_exist
set /a test=!cert_pos!-!vet1!
if !test! LSS 3 ( goto isupdate )

goto not_update
 
:not_update
set /a pos1=!vet1!
set /a pos2=!ocont_number!
set string=
if !vet1! EQU !ocont_number! ( goto endofcontent )

goto contentstrip1

:isupdate
if !cert_pos! EQU !ocont_number! ( goto endofcontent )


:contentstrip1
if !pos1! GTR !pos2! ( goto :contentstrip2 ) else (set /a pos1+=1)
set string=%string%,%pos1%
goto :contentstrip1 

:contentstrip2


set string=%string%,
set skiplist=%string%
echo %skiplist%>xciDecrypted\skiplist.txt
set /a contador+=1
set "skip=%skiplist%"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<xciDecrypted\other_content.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>xciDecrypted\content!contador!.txt
MD "xciDecrypted\content!contador!"
for /f %%a in (xciDecrypted\content!contador!.txt) do (
move  "xciDecrypted\rawsecure\%%a"  "xciDecrypted\content!contador!" 
) >NUL 2>&1

set /a pos2=!vet1!
set /a pos1=1
set string=
echo f | xcopy /f /y "xciDecrypted\other_content.txt" "xciDecrypted\content_helper.txt" >NUL 2>&1
del xciDecrypted\other_content.txt

goto :update_list1 

:endofcontent
set /a contador+=1
MD "xciDecrypted\content!contador!"
move  "xciDecrypted\rawsecure\*"  "xciDecrypted\content!contador!" >NUL 2>&1

:nocontent

::If we only have 4 nca we have no manual
if !game_nca_number! LSS 5 ( goto nomanual )

::In this portion we'll identify the manual nca files via hactool
::Hactool will recognize 2 of them as manual when one is actually legal
::We'll do a supposition to identify each

set /a c_gamenca=1
set mycheck=Manual
:getmeinfo1
::In normal conditions we'll only have 5 nca files "tops" with a proper release
::If not proper it could be a big pain in the ass depending the conditions
::We'll iterate to identify the two manual nca files

set gstring=
if !c_gamenca! EQU 6 ( goto getmeinfo2 )
if !c_gamenca! EQU 1 ( set gstring=,2,3,4,5, )
if !c_gamenca! EQU 2 ( set gstring=,1,3,4,5, )
if !c_gamenca! EQU 3 ( set gstring=,1,2,4,5, )
if !c_gamenca! EQU 4 ( set gstring=,1,2,3,5, )
if !c_gamenca! EQU 5 ( set gstring=,1,2,3,4, )

Set "skip=%gstring%"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<xciDecrypted\game_nca.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>xciDecrypted\ncatocheck.txt
for /f %%a in (xciDecrypted\ncatocheck.txt) do (
    set ncatocheck=%%a
)
echo -------------------------------------------------
echo Analyzing nca !c_gamenca! with hactool by SciresM
echo -------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t nca -i "xciDecrypted\secure\%ncatocheck%" >"xciDecrypted\nca_data.txt"
FINDSTR "Type" xciDecrypted\nca_data.txt >xciDecrypted\nca_helper.txt
for /f "tokens=3* delims=: " %%a in (xciDecrypted\nca_helper.txt) do (
echo %%a>>xciDecrypted\nca_helper2.txt)
Set "skip=,2,3,"
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<xciDecrypted\nca_helper2.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>xciDecrypted\nca_type.txt
for /f %%a in (xciDecrypted\nca_type.txt) do (
    set nca_type=%%a
) >NUL 2>&1

if %nca_type% EQU %mycheck% ( echo %ncatocheck%>>xciDecrypted\manual_list.txt )
set /a c_gamenca+=1
del xciDecrypted\ncatocheck.txt
del xciDecrypted\nca_data.txt
del xciDecrypted\nca_helper.txt
del xciDecrypted\nca_helper2.txt
del xciDecrypted\nca_type.txt
echo is %nca_type%. DONE
goto getmeinfo1

:getmeinfo2
::We'll get the route of the alleged "manual nca" 
set crlt=0
for /f %%a in (xciDecrypted\manual_list.txt) do (
    set /a crlt=!crlt! + 1
    set tmanual!crlt!=%%a
)

::del manual_list.txt

::Set complete route
set f_tmanual1="xciDecrypted\secure\%tmanual1%"
set f_tmanual2="xciDecrypted\secure\%tmanual2%"

::Get size of both nca
for /f "usebackq" %%A in ('%f_tmanual1%') do set size_tm1=%%~zA
for /f "usebackq" %%A in ('%f_tmanual2%') do set size_tm2=%%~zA

::echo !size_tm1!>xciDecrypted\size_tm1.txt
::echo !size_tm2!>xciDecrypted\size_tm2.txt

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
if !preservemanual! EQU 1 ( move "%f_tmanual1%"  "xciDecrypted\" ) 
if !preservemanual! NEQ 1 ( del "%f_tmanual1%" ) 
set filename=!filename![nm]
goto nomanual
:case2
if !preservemanual! EQU 1 ( move "%f_tmanual2%"  "xciDecrypted\" ) 
if !preservemanual! NEQ 1 ( del "%f_tmanual2%" ) 
set filename=!filename![nm]
goto nomanual
:case3
if !preservemanual! EQU 1 ( move "%f_tmanual2%"  "xciDecrypted\" ) 
if !preservemanual! NEQ 1 ( del "%f_tmanual2%" ) 
set filename=!filename![nm]
goto nomanual
:case4
if !preservemanual! EQU 1 ( move "%f_tmanual1%"  "xciDecrypted\" ) 
if !preservemanual! NEQ 1 ( del "%f_tmanual1%" ) 
set filename=!filename![nm]
goto nomanual

:ognm
::If only 4 nca just extract secure partition to secure
echo ------------------------------------------------------------
echo Extracting secure partition from xci with hactool by SciresM
echo ------------------------------------------------------------
"ztools\hactool.exe" -k "ztools\keys.txt" -t xci --securedir=xciDecrypted\secure\ "%~1" >NUL 2>&1
echo DONE
goto nomanual

::In case we have no manual to proccess less code
:nomanual
RD /s /q "xciDecrypted\rawsecure" >NUL 2>&1
::We don't need to preserve normal and update
MD "xciDecrypted\update"
MD "xciDecrypted\normal"
::We can clean the txt files
del xciDecrypted\*.txt
::Call hacbuild to build the xci
::To do->Force hacbuild to build secure in correct order in all cases
::To do->Option to preserve padding in secure header for future compatibility to dlc and update reforming
echo ------------------------------------------------------
echo Rebuilding trimmed xci file with hacbuild by LucaFraga
echo ------------------------------------------------------
ECHO NOTE:
echo With files bigger than 4Gb it'll take more time proportionally than with smaller files.
echo Also you'll need to have at least double the amount of free disk space than file's size.
echo IF YOU DON'T SEE "DONE" HACBUILD IS STILL AT WORK.
ECHO ........................................................................................
"ztools\hacbuild.exe" xci_auto "xciDecrypted" "xciDecrypted\!filename![nxt].xci" >NUL 2>&1
echo DONE

::Create output folder and move trimmed file
echo %filename%>xciDecrypted\fname.txt
for /f "tokens=1* delims=[" %%a in (xciDecrypted\fname.txt) do (
    set ofolder=%%a)
del xciDecrypted\fname.txt
MD "output_nxt\!ofolder!" >NUL 2>&1
move  "xciDecrypted\*.xci"  "output_nxt\!ofolder!" >NUL 2>&1
move  "xciDecrypted\*.nca" "output_nxt\!ofolder!" >NUL 2>&1
RD /s /q "xciDecrypted\normal"
RD /s /q "xciDecrypted\secure"
RD /s /q "xciDecrypted\update"
del xciDecrypted\*.ini

::Create content nsp
set a/ c_aux=0
if !contador! GTR 0 ( goto create_nsp ) 
goto :final

:create_nsp
if !contador! LEQ !c_aux! ( goto :final ) else ( set /a c_aux+=1 )

dir "xciDecrypted\content!c_aux!" /b  > "xciDecrypted\fileslist.txt"
FINDSTR /R /N "^.*" xciDecrypted\fileslist.txt | FIND /C ":">xciDecrypted\fileslist_helper.txt
for /f %%a in (xciDecrypted\fileslist_helper.txt) do (
    set fileslist=%%a
)

set list=0
for /F "tokens=*" %%A in (xciDecrypted\fileslist.txt) do (
    SET /A list=!list! + 1
    set varlist!list!=%%A
) >NUL 2>&1
set varlist >NUL 2>&1

::echo %string%>xciDecrypted\teststring.txt
echo --------------------------------------------------------------------------
echo Rebuilding dlc or update [c!c_aux!] as nsp with "nspbuild" by CVFireDragon
echo --------------------------------------------------------------------------
if !fileslist! EQU 0 ( goto :final)
if !fileslist! EQU 1 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" ) >NUL 2>&1
if !fileslist! EQU 2 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" ) >NUL 2>&1
if !fileslist! EQU 3 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" "xciDecrypted\content!c_aux!\%varlist3%" ) >NUL 2>&1
if !fileslist! EQU 4 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" "xciDecrypted\content!c_aux!\%varlist3%" "xciDecrypted\content!c_aux!\%varlist4%" ) >NUL 2>&1
if !fileslist! EQU 5 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" "xciDecrypted\content!c_aux!\%varlist3%" "xciDecrypted\content!c_aux!\%varlist4%" "xciDecrypted\content!c_aux!\%varlist5%" ) >NUL 2>&1
if !fileslist! EQU 6 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" "xciDecrypted\content!c_aux!\%varlist3%" "xciDecrypted\content!c_aux!\%varlist4%" "xciDecrypted\content!c_aux!\%varlist5%" "xciDecrypted\content!c_aux!\%varlist6%") >NUL 2>&1
if !fileslist! EQU 7 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" "xciDecrypted\content!c_aux!\%varlist3%" "xciDecrypted\content!c_aux!\%varlist4%" "xciDecrypted\content!c_aux!\%varlist5%" "xciDecrypted\content!c_aux!\%varlist6%" "xciDecrypted\content!c_aux!\%varlist7%") >NUL 2>&1
if !fileslist! EQU 8 ( "ztools\nspbuild.py" "xciDecrypted\content!c_aux!.nsp" "xciDecrypted\content!c_aux!\%varlist1%" "xciDecrypted\content!c_aux!\%varlist2%" "xciDecrypted\content!c_aux!\%varlist3%" "xciDecrypted\content!c_aux!\%varlist4%" "xciDecrypted\content!c_aux!\%varlist5%" "xciDecrypted\content!c_aux!\%varlist6%" "xciDecrypted\content!c_aux!\%varlist7%" "xciDecrypted\content!c_aux!\%varlist8%") >NUL 2>&1
echo DONE
set fileslist=0
del xciDecrypted\fileslist.txt
del xciDecrypted\fileslist_helper.txt
echo %filename%>xciDecrypted\fname.txt
for /f "tokens=1* delims=[" %%a in (xciDecrypted\fname.txt) do (
    set onsp=%%a)
del xciDecrypted\fname.txt
if exist "xciDecrypted\content!c_aux!\*.tik" ( rename "xciDecrypted\content!c_aux!.nsp" "!onsp![c!c_aux!][upd].nsp") else ( rename "xciDecrypted\content!c_aux!.nsp" "!onsp![c!c_aux!][dlc].nsp")
RD /s /q "xciDecrypted\content!c_aux!"
goto create_nsp

:final
move  "xciDecrypted\*.nsp" "output_nxt\!ofolder!" >NUL 2>&1 

::Delete work folder
RD /s /q "xciDecrypted"

echo Processed !filename!
echo Your files should be in the output_nxt folder
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
cls






