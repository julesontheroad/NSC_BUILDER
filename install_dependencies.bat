@ECHO OFF
call "zconfig/nsp_cleaner_options.cmd"
set pycommand=%pycommand:"=%
ECHO.
ECHO Installing dependencies 
ECHO.
%pycommand% -m pip install urllib3 unidecode tqdm bs4 tqdm requests image
ECHO.
PAUSE