@ECHO OFF
:TOP_INIT
set "prog_dir=%~dp0"
set "bat_name=%~n0"
set "ofile_name=%bat_name%_options.cmd"
Title NSC_Builder v1.01-b -- Profile: %ofile_name% -- by JulesOnTheRoad
set "list_folder=%prog_dir%lists"
::-----------------------------------------------------
::EDIT THIS VARIABLE TO LINK OTHER OPTION FILE
::-----------------------------------------------------
set "op_file=%~dp0zconfig\%ofile_name%"

::-----------------------------------------------------
::COPY OPTIONS FROM OPTION FILE
::-----------------------------------------------------
setlocal
if exist "%op_file%" call "%op_file%"
endlocal & (
REM environment
set "pycommand=%pycommand%"
set "start_minimized=%start_minimized%"
set "videoplayback=%videoplayback%"
set "port=%port%"
set "host=%host%"
set "noconsole=%noconsole%"
set "pycommandw=%pycommandw%"
set "ssl=%ssl%"
REM PROGRAMS
set "squirrel=%nut%"
REM FILES
set "dec_keys=%dec_keys%"
)
::-----------------------------------------------------
::SET ABSOLUTE ROUTES
::-----------------------------------------------------
::Program full route
if exist "%~dp0%squirrel%" set "squirrel=%~dp0%squirrel%"

::Important files full route
if exist "%~dp0%dec_keys%"  set "dec_keys=%~dp0%dec_keys%"
::Folder output
CD /d "%~dp0"
if not exist "%dec_keys%" ( goto missing_things )

if "%start_minimized%" EQU "yes" ( goto minimize )
goto start
:minimize
if not "%1" == "min" start /MIN cmd /c %0 min & exit/b >nul 2>&1
:start
%pycommand% "%squirrel%" -lib_call nutdb  check_files
if "%noconsole%" == "false" (%pycommand% "%squirrel%" -lib_call Interface server -xarg "%port%" "%host%" "%videoplayback%" "%ssl%" )
if "%noconsole%" == "false" goto salida
start %pycommandw% "%squirrel%" -lib_call Interface server -xarg "%port%" "%host%" "%videoplayback%" "%ssl%" "%noconsole%"
goto salida

:missing_things
echo ....................................
echo You're missing the following things:
echo ....................................
echo.
::File full route
if not exist "%dec_keys%" echo - "keys.txt" is not correctly pointed or is missing.
echo.
pause
echo Program will exit now
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida
:salida
REM pause
exit
