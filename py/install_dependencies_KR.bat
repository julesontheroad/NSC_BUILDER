@ECHO OFF
set "pycommand=py -3"
set "op_file=%~dp0zconfig/NSCB_options.cmd"
call :program_logo
setlocal
if exist "%op_file%" call "%op_file%" 	  
endlocal & ( 
set "pycommand=%pycommand%"
)

ECHO.
ECHO 종속성 설치
ECHO.
%pycommand% -m pip install urllib3 unidecode tqdm bs4 tqdm requests image pywin32 pycryptodome pykakasi googletrans chardet textwrap
ECHO.
ECHO **********************************************************************************
ECHO ---중요 : 계속하기 전에 종속성이 올바르게 설치되었는지 확인하십시오.---
ECHO **********************************************************************************
ECHO.
PAUSE
exit /B

:program_logo

ECHO                                        __          _ __    __         
ECHO                  ____  _____ ____     / /_  __  __(_) /___/ /__  _____
ECHO                 / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/
ECHO                / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /    
ECHO               /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/     
ECHO                              /_____/                                  
ECHO -------------------------------------------------------------------------------------
ECHO                              닌텐도 스위치 클리너 및 빌더
ECHO                             (XCI 다중 콘텐츠 빌더 및 기타)
ECHO -------------------------------------------------------------------------------------
ECHO =============================    JULESONTHEROAD 제작    =============================
ECHO -------------------------------------------------------------------------------------
exit /B
