endlocal
CD /d "%~2"
CD /d ".."
if "%~1" EQU "repack" call :nsp_repack
if "%~1" EQU "convert" call :nsp_convert
if "%~1" EQU "sp_convert" call :sp_nsp_convert
goto end

:nsp_repack
ECHO -----------------
echo Repacking as nsp 
ECHO -----------------
if exist "%w_folder%\secure\*.dat" del "%w_folder%\secure\*.dat" >NUL 2>&1

dir "%w_folder%\secure\*.cnmt.nca" /b  > "%w_folder%\cnmt_fileslist.txt"
setlocal enabledelayedexpansion
set row=
for /f "usebackq" %%x in ("%w_folder%\cnmt_fileslist.txt") do set row="%w_folder%\secure\%%x" !row!
%pycommand% "%nut%" -o "%w_folder%\secure" --xml_gen %row% >NUL 2>&1
endlocal
del "%w_folder%\cnmt_fileslist.txt" >NUL 2>&1

%pycommand% "%nut%" %buffer% %fatype% %fexport% -ifo "%w_folder%\secure" -c "%w_folder%\%filename%.nsp"
if exist "%w_folder%\*.ns*" ren "%w_folder%\*.ns*" "%filename%.ns*" >NUL 2>&1

exit /B

:nsp_convert
ECHO -----------------
echo Repacking as nsp 
ECHO -----------------
if exist "%w_folder%\secure\*.dat" del "%w_folder%\secure\*.dat" >NUL 2>&1

dir "%w_folder%\secure\*.cnmt.nca" /b  > "%w_folder%\cnmt_fileslist.txt"
setlocal enabledelayedexpansion
set row=
for /f "usebackq" %%x in ("%w_folder%\cnmt_fileslist.txt") do set row="%w_folder%\secure\%%x" !row!
%pycommand% "%nut%" -o "%w_folder%\secure" --xml_gen %row% >NUL 2>&1
endlocal
del "%w_folder%\cnmt_fileslist.txt" >NUL 2>&1

%pycommand% "%nut%" %buffer% %fatype% %fexport% -ifo "%w_folder%\secure" -c "%w_folder%\%filename%.nsp"
if exist "%w_folder%\*.ns*" ren "%w_folder%\*.ns*" "%filename%.ns*" >NUL 2>&1

exit /B

:sp_nsp_convert
ECHO -----------------
echo Repacking as nsp 
ECHO -----------------
if exist "!tfolder!\secure\*.dat" del "!tfolder!\secure\*.dat" >NUL 2>&1

dir "!tfolder!\secure\*.cnmt.nca" /b  > "!tfolder!\cnmt_fileslist.txt"
set row=
for /f "usebackq" %%x in ("!tfolder!\cnmt_fileslist.txt") do set row="!tfolder!\secure\%%x" !row!
%pycommand% "%nut%" -o "!tfolder!\secure" --xml_gen %row% >NUL 2>&1
del "!tfolder!\cnmt_fileslist.txt"

%pycommand% "%nut%" %buffer% %fatype% %fexport% -ifo "!tfolder!\secure" -c "%w_folder%\!fname!.nsp"
if exist "%w_folder%\*.ns*" ren "%w_folder%\*.ns*" "!fname!.ns*" >NUL 2>&1

exit /B

:end
PING -n 3 127.0.0.1 >NUL 2>&1

