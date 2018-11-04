endlocal
CD /d "%~2"
CD /d ".."

if "%~1" EQU "repack" call :nsp_repack
if "%~1" EQU "convert" call :nsp_convert
goto end

:nsp_repack
ECHO -----------------
echo Repacking as nsp 
ECHO -----------------
dir "%w_folder%\secure" /b  > "%w_folder%\nsp_fileslist.txt"
set ruta_nspb=ztools\nspBuild.py
setlocal enabledelayedexpansion
set row=
for /f %%x in (%w_folder%\nsp_fileslist.txt) do set row="%w_folder%\secure\%%x" !row!
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
set ruta_nspb=ztools\nspBuild.py
setlocal enabledelayedexpansion
set row=
for /f %%x in (%w_folder%\nsp_fileslist.txt) do set row="%w_folder%\secure\%%x" !row!
%pycommand% "%nut%" -c "%w_folder%\output.nsp" %row% >NUL 2>&1
endlocal
%pycommand% "%nut%" --seteshop "%w_folder%\output.nsp"
ren "%w_folder%\output.nsp" "%filename%[nap].nsp"
del "%w_folder%\nsp_fileslist.txt"
echo DONE 
exit /B

:end
PING -n 3 127.0.0.1 >NUL 2>&1

