endlocal
CD /d "%~2"
CD /d ".."
::echo %~1"
if "%~1" EQU "repack" call :xci_repack
if "%~1" EQU "sp_repack" call :sp_xci_repack
goto end

:xci_repack
if not exist "%w_folder%\normal" MD "%w_folder%\normal"
if not exist "%w_folder%\update" MD "%w_folder%\update"

dir /b "%w_folder%\secure\*.nca">"%w_folder%\lisfiles.txt"
FINDSTR /I ".nca" "%w_folder%\lisfiles.txt">"%w_folder%\nca_list.txt"
del "%w_folder%\lisfiles.txt"

setlocal enabledelayedexpansion
set nca_number=
for /f "usebackq tokens=*" %%f in ("%w_folder%\nca_list.txt") do (
set /a nca_number=!nca_number! + 1
)
del "%w_folder%\nca_list.txt"
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
echo Repacking as xci
echo -------------------------------
if exist "%w_folder%\secure\*.dat" del "%w_folder%\secure\*.dat" >NUL 2>&1
if exist "%w_folder%\secure\*.xml" del "%w_folder%\secure\*.xml" >NUL 2>&1
%pycommand% "%nut%" %buffer% -ifo "%w_folder%" %fatype% --create_xci "%w_folder%\%filename%.xci"
exit /B

:sp_xci_repack
if not exist "!tfolder!\normal" MD "!tfolder!\normal"
if not exist "!tfolder!\update" MD "!tfolder!\update"

dir /b "!tfolder!\secure\*.nca">"!tfolder!\lisfiles.txt"
FINDSTR /I ".nca" "!tfolder!\lisfiles.txt">"!tfolder!\nca_list.txt"

del "!tfolder!\lisfiles.txt"

set nca_number=
for /f "usebackq tokens=*" %%f in ("!tfolder!\nca_list.txt") do (
set /a nca_number=!nca_number! + 1
)
::echo !nca_number!

if !nca_number! LEQ 3 goto sp_c1dummy
if !nca_number! LEQ 2 goto sp_c2dummy
if !nca_number! LEQ 1 goto sp_c3dummy
goto sp_nodummy
:sp_c3dummy
type nul>testfile>"!tfolder!\secure\000"
:sp_c2dummy
type nul>testfile>"!tfolder!\secure\00"
:sp_c1dummy
type nul>testfile>"!tfolder!\secure\0"
:sp_nodummy

::Enable old license nsp method if necessary
if not exist "!tfolder!\secure\*.tik" goto sp_build
MD "!tfolder!\lc
echo f | xcopy /f /y "!tfolder!\secure\*.cnmt.nca" "!tfolder!\lc\"  >NUL 2>&1
move  "!tfolder!\secure\*.tik"  "!tfolder!\lc" >NUL 2>&1
move  "!tfolder!\secure\*.cert"  "!tfolder!\lc" >NUL 2>&1
for /f "usebackq tokens=*" %%f in ("!tfolder!\nca_list.txt") do (
%pycommand% "%nut%" --ncatype "!tfolder!\secure\%%f">"!tfolder!\nca_type.txt"
set /p nca_type=<"!tfolder!\nca_type.txt"
del "!tfolder!\nca_type.txt"
if "!nca_type!" EQU "Content.CONTROL" ( set "ctrl_nca=%%f" )
)
echo f | xcopy /f /y "!tfolder!\secure\!ctrl_nca!" "!tfolder!\lc\"  >NUL 2>&1
del "!tfolder!\nca_list.txt"
dir "!tfolder!\lc" /b  > "!tfolder!\lc_list.txt"
set row=
for /f "usebackq" %%x in ("!tfolder!\lc_list.txt") do set row="!tfolder!\lc\%%x" !row!
%pycommand% "%nut%" -c "%w_folder%\output.nsp" %row% >NUL 2>&1
ren "%w_folder%\output.nsp" "!fname![lc].nsp"
del "!tfolder!\lc_list.txt"

:sp_build
echo -------------------------------
echo Repacking as xci
echo -------------------------------
if exist "!tfolder!\secure\*.dat" del "!tfolder!\secure\*.dat" >NUL 2>&1
if exist "!tfolder!\secure\*.xml" del "!tfolder!\secure\*.xml" >NUL 2>&1
%pycommand% "%nut%" %buffer% -ifo "!tfolder!" %fatype% --create_xci "%w_folder%\!fname!.xci"
RD /S /Q  "!tfolder!" >NUL 2>&1
exit /B

:end
PING -n 3 127.0.0.1 >NUL 2>&1