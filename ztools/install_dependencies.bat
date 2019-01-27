@ECHO OFF
set "pycommand=py -3"
set "op_file=%~dp0zconfig/NSCB_options.cmd"
setlocal
if exist "%op_file%" call "%op_file%" 	  
endlocal & ( 
set "pycommand=%pycommand%"
)

ECHO.
ECHO Installing dependencies 
ECHO.
%pycommand% -m pip install urllib3 unidecode tqdm bs4 tqdm requests image pywin32
ECHO.
ECHO **********************************************************************************
ECHO ---IMPORTANT: Check if dependencies were installed correctly before continuing---
ECHO **********************************************************************************
ECHO.
PAUSE
exit /B
