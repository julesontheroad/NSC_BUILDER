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
dir "%w_folder%\secure" /b  > "%w_folder%\nsp_fileslist.txt"
if exist "%w_folder%\secure\*.dat" del "%w_folder%\secure\*.dat" >NUL 2>&1
setlocal enabledelayedexpansion
set row=
for /f "usebackq" %%x in ("%w_folder%\nsp_fileslist.txt") do set row="%w_folder%\secure\%%x" !row!
%pycommand% "%nut%" -c "%w_folder%\output.nsp" %row% >NUL 2>&1
endlocal
ren "%w_folder%\output.nsp" "%filename%[rr].nsp"
del "%w_folder%\nsp_fileslist.txt"
echo DONE 
exit /B

:nsp_convert
ECHO -----------------
echo Repacking as nsp 
ECHO -----------------
dir "%w_folder%\secure" /b  > "%w_folder%\nsp_fileslist.txt"
if exist "%w_folder%\secure\*.dat" del "%w_folder%\secure\*.dat" >NUL 2>&1
setlocal enabledelayedexpansion
set row=
for /f "usebackq" %%x in ("%w_folder%\nsp_fileslist.txt") do set row="%w_folder%\secure\%%x" !row!
%pycommand% "%nut%" -c "%w_folder%\output.nsp" %row% >NUL 2>&1
endlocal
%pycommand% "%nut%" --seteshop "%w_folder%\output.nsp"
ren "%w_folder%\output.nsp" "%filename%[nap].nsp"
del "%w_folder%\nsp_fileslist.txt"
echo DONE 
exit /B

:sp_nsp_convert
ECHO -----------------
echo Repacking as nsp 
ECHO -----------------
if exist "%w_folder%\secure\*.dat" del "%w_folder%\secure\*.dat" >NUL 2>&1
dir "!tfolder!\secure" /b  > "!tfolder!\nsp_fileslist.txt"
set row=
for /f "usebackq" %%x in ("!tfolder!\nsp_fileslist.txt") do set row="!tfolder!\secure\%%x" !row!
%pycommand% "%nut%" -c "%w_folder%\output.nsp" %row% >NUL 2>&1
%pycommand% "%nut%" --seteshop "%w_folder%\output.nsp"
ren "%w_folder%\output.nsp" "!fname!.nsp"
del "!tfolder!\nsp_fileslist.txt"
echo DONE 
exit /B

:end
PING -n 3 127.0.0.1 >NUL 2>&1

