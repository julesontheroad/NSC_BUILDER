if "%~1" EQU "delete_if_empty" call :delete_if_empty
if "%~1" EQU "contador" call :contador
if "%~1" EQU "processing_message" call :processing_message
exit /B

:check_if_empty
set conta=0
for /f "tokens=*" %%f in (lists/%~2) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (lists/%~2) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del "%list_folder%\%~2" )
endlocal
exit /B

:contador
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (lists/%~2) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo STILL !conta! FILES TO PROCESS
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

:processing_message
echo Processing %~2
echo.
exit /B
