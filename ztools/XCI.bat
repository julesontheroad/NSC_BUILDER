endlocal
CD /d "%~2"
CD /d ".."
::echo %~1"
if "%~1" EQU "repack" call :xci_repack

goto end


:xci_repack
if not exist "%w_folder%\normal" MD "%w_folder%\normal"
if not exist "%w_folder%\update" MD "%w_folder%\update"
echo f | xcopy /f /y "%game_info%" "%w_folder%\"  >NUL 2>&1
ren "%w_folder%\*.ini" "game_info.ini"

dir /b "%w_folder%\secure\*.nca">"%w_folder%\lisfiles.txt"
FINDSTR /I ".nca" "%w_folder%\lisfiles.txt">"%w_folder%\nca_list.txt"
del "%w_folder%\lisfiles.txt"

setlocal enabledelayedexpansion
FINDSTR /R /N "^.*" "%w_folder%\nca_list.txt" | FIND /C ":">"%w_folder%\nca_number.txt"
del "%w_folder%\nca_list.txt"
set /p nca_number=<"%w_folder%\nca_number.txt"
del "%w_folder%\nca_number.txt"
::echo !nca_number!
if !nca_number! LEQ 3 goto c1dummy
if !nca_number! LEQ 2 goto c2dummy
if !nca_number! LEQ 1 goto c3dummy
goto nodummy
:c3dummy
type nul>testfile>"%w_folder%\secure\000"
:c2dummy
type nul>testfile>"%w_folder%\secure\00"
:c1dummy
type nul>testfile>"%w_folder%\secure\0"
:nodummy
endlocal
echo -------------------------------
echo Building xci file with hacbuild 
echo -------------------------------
ECHO NOTE:
echo With files bigger than 4Gb it'll take more time proportionally than with smaller files.
echo Also you'll need to have at least double the amount of free disk space than file's size.
echo IF YOU DON'T SEE "DONE" HACBUILD IS STILL AT WORK.
ECHO ........................................................................................
"%hacbuild%" xci_auto_del "%w_folder%"  "%w_folder%\%filename%[xcib].xci"
exit /B

:end
PING -n 3 127.0.0.1 >NUL 2>&1